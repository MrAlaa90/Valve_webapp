"""
Desktop Application Lifecycle Manager & Server Wrapper
for Valve Workshop Management System.

Runs Django behind Waitress and opens the local application in an installed
Edge or Chrome app-mode window, fully offline without relying on WebView2 or pywebview.
"""

import io
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import traceback
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


def run_django_migrations() -> None:
    """Apply pending database migrations before the server starts."""
    from django.core.management import call_command

    logger.info("Checking and applying pending database migrations...")
    output = io.StringIO()
    try:
        call_command('migrate', interactive=False, stdout=output, stderr=output)
        logger.info("Database migrations completed: %s", output.getvalue().strip() or "no changes")
    except Exception:
        logger.exception("Migration execution notice")


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
    try:
        call_command('collectstatic', interactive=False, verbosity=0, clear=False)
    except Exception:
        logger.exception("Static collection skipped in local environment")


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
                logger.exception("Could not launch %s; trying next candidate", executable)

    logger.warning("Edge and Chrome not found; opening default browser")
    try:
        webbrowser.open(url)
    except Exception:
        logger.exception("Could not open default browser")
    return None


def shutdown(backup_engine, server) -> None:
    """Run application shutdown hooks and stop the Waitress server."""
    logger.info("Application closing; running pre-shutdown tasks...")
    try:
        if backup_engine:
            backup_engine.trigger_pre_shutdown_backup()
    except Exception:
        logger.exception("Pre-shutdown backup notice")
    try:
        if backup_engine:
            backup_engine.stop_scheduler()
    except Exception:
        pass
    try:
        if server:
            server.close()
    except Exception:
        pass
    logger.info("Shutdown finalized.")


def main(headless: bool = False) -> int:
    """Initialize Django, serve the app, and manage its browser lifecycle."""
    paths = init_desktop_environment()
    logger.info("Initialized desktop environment in: %s", paths['data_dir'])

    import django
    django.setup()
    run_django_migrations()
    ensure_static_files(paths['data_dir'])

    backup_engine = None
    try:
        import backup_manager
        backup_engine = backup_manager.get_backup_engine()
        backup_engine.start_background_scheduler(interval_seconds=3600)
    except Exception:
        logger.exception("Backup engine could not be initialized")

    port = find_available_port(start_port=8000)
    server_url = f"http://127.0.0.1:{port}/"
    logger.info("Binding WSGI server to %s", server_url)

    from waitress import create_server
    from valve_project.wsgi import application as django_app

    def debug_application(environ, start_response):
        try:
            return django_app(environ, start_response)
        except Exception:
            err_trace = traceback.format_exc()
            logger.critical("Critical error handling WSGI request:\n%s", err_trace)
            body = (
                f"<html><head><title>System Error</title></head>"
                f"<body style='font-family:sans-serif;padding:30px;background:#1e1e1e;color:#f1f1f1;'>"
                f"<h2 style='color:#ff5555;'>Django Application Crash (Traceback)</h2>"
                f"<pre style='background:#111;padding:15px;border-radius:5px;overflow-x:auto;color:#ffb86c;font-size:13px;line-height:1.4;'>{err_trace}</pre>"
                f"</body></html>"
            ).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(body)))
            ])
            return [body]

    server = create_server(
        debug_application,
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

    time.sleep(1.5)

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
