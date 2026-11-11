"""
Desktop Application Lifecycle Manager & Server Wrapper
for Valve Workshop Management System.

Runs Django behind Waitress and opens the local application in an installed
Edge or Chrome app-mode window, without relying on WebView2 or pywebview.
"""

import io
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

# Fix for PyInstaller --noconsole mode where sys.stdout and sys.stderr are None.
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ['DESKTOP_MODE'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valve_project.settings')

from desktop_app.paths import init_desktop_environment

logger = logging.getLogger("desktop_launcher")


def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an unused TCP port on localhost."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('127.0.0.1', port)) != 0:
                return port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def wait_for_server(url: str, timeout_seconds: float = 15.0) -> bool:
    """Poll the local application until it responds or the timeout expires."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            request = urllib.request.Request(
                url, headers={'User-Agent': 'ValveWorkshopDesktop/1.0'}
            )
            with urllib.request.urlopen(request, timeout=1.0) as response:
                if response.status in (200, 301, 302):
                    return True
        except urllib.error.HTTPError as error:
            if error.code in (200, 301, 302, 403, 404):
                return True
        except Exception:
            pass
        time.sleep(0.15)
    return False


def run_django_migrations() -> None:
    """Apply pending database migrations before the server starts."""
    from django.core.management import call_command

    logger.info("Checking and applying pending database migrations...")
    output = io.StringIO()
    call_command('migrate', interactive=False, stdout=output, stderr=output)
    logger.info("Database migrations completed: %s", output.getvalue().strip() or "no changes")


def ensure_static_files(data_dir: Path) -> None:
    """Collect static assets if the build did not already provide them."""
    from django.conf import settings
    from django.core.management import call_command

    static_root = Path(settings.STATIC_ROOT)
    if static_root.is_dir() and any(static_root.iterdir()):
        logger.info("Static files are ready in %s", static_root)
        return

    if getattr(sys, 'frozen', False):
        static_root = data_dir / 'staticfiles'
        static_root.mkdir(parents=True, exist_ok=True)
        settings.STATIC_ROOT = str(static_root)

    logger.info("Collecting static files into %s", static_root)
    call_command('collectstatic', interactive=False, verbosity=0, clear=False)
    if not static_root.is_dir() or not any(static_root.iterdir()):
        raise RuntimeError(f"Static file collection did not populate {static_root}")


def browser_candidates() -> list[Path]:
    """Return supported Edge and Chrome executable paths in preference order."""
    program_files_x86 = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'))
    program_files = Path(os.environ.get('ProgramFiles', r'C:\Program Files'))
    local_app_data = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local')))
    return [
        program_files_x86 / 'Microsoft' / 'Edge' / 'Application' / 'msedge.exe',
        program_files / 'Microsoft' / 'Edge' / 'Application' / 'msedge.exe',
        program_files / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
        program_files_x86 / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
        local_app_data / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
    ]


def launch_browser(url: str) -> subprocess.Popen | None:
    """Open URL in Edge/Chrome app mode, falling back to the default browser."""
    for executable in browser_candidates():
        if executable.is_file():
            logger.info("Launching browser app window with %s", executable)
            try:
                return subprocess.Popen(
                    [str(executable), f'--app={url}', '--start-maximized'],
                    close_fds=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError:
                logger.exception("Could not launch %s; trying the next browser", executable)

    logger.warning("Edge and Chrome were not found; opening the default browser")
    try:
        webbrowser.open(url)
    except Exception:
        logger.exception("Could not open the default browser")
    return None


def shutdown(backup_engine, server) -> None:
    """Run application shutdown hooks and stop the Waitress server."""
    logger.info("Application closing; running pre-shutdown backup...")
    try:
        backup_engine.trigger_pre_shutdown_backup()
    except Exception:
        logger.exception("Pre-shutdown backup failed")
    try:
        backup_engine.stop_scheduler()
    except Exception:
        logger.exception("Stopping backup scheduler failed")
    try:
        server.close()
    except Exception:
        logger.exception("Stopping Waitress failed")
    logger.info("Shutdown sequence finalized.")


def main(headless: bool = False) -> int:
    """Initialize Django, serve the app, and manage its browser lifecycle."""
    paths = init_desktop_environment()
    logger.info("Initialized desktop environment in: %s", paths['data_dir'])

    import django
    django.setup()
    run_django_migrations()
    ensure_static_files(paths['data_dir'])

    import backup_manager
    backup_engine = backup_manager.get_backup_engine()
    backup_engine.start_background_scheduler(interval_seconds=3600)

    port = find_available_port(start_port=8000)
    server_url = f"http://127.0.0.1:{port}/"
    logger.info("Binding WSGI server to %s", server_url)

    from waitress import create_server
    from valve_project.wsgi import application

    server = create_server(
        application,
        host='127.0.0.1',
        port=port,
        threads=8,
    )
    server_thread = threading.Thread(
        target=server.run,
        daemon=True,
        name="WaitressWSGIServer",
    )
    server_thread.start()

    if not wait_for_server(server_url, timeout_seconds=12.0):
        shutdown(backup_engine, server)
        raise RuntimeError(f"Waitress did not respond at {server_url}")

    logger.info("Server is live at %s", server_url)

    if headless or os.environ.get('VALVE_HEADLESS_TEST') == 'True':
        logger.info("Running in headless test mode")
        shutdown(backup_engine, server)
        server_thread.join(timeout=5)
        return 0

    browser_process = launch_browser(server_url)
    if browser_process is None:
        server_thread.join()
        return 0

    try:
        browser_process.wait()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        shutdown(backup_engine, server)
        server_thread.join(timeout=5)

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == '__main__':
    sys.exit(main(headless='--headless' in sys.argv or '--headless-test' in sys.argv))