"""
Desktop Application Lifecycle Manager & Server Wrapper
for Valve Workshop Management System.

Integrates:
- Dynamic localhost port binding
- Waitress multi-threaded production WSGI server
- Edge Chromium / WebView2 standalone native desktop shell
- Automatic database migrations on boot
- Non-blocking GFS backup background daemon
- Graceful pre-shutdown snapshot and thread termination
"""

import os
import sys
import time
import io
import socket
import logging
import threading
import urllib.request
from pathlib import Path

# Fix for PyInstaller --noconsole mode where sys.stdout and sys.stderr are None
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure Desktop Mode is set before Django settings are loaded
os.environ['DESKTOP_MODE'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valve_project.settings')

# Import desktop paths
from desktop_app.paths import init_desktop_environment, BUNDLE_DIR, DATA_DIR, DB_PATH, LOGS_DIR

logger = logging.getLogger("desktop_launcher")


def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Finds an unused TCP port on localhost."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port

    # Fallback to kernel-assigned free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_for_server(url: str, timeout_seconds: float = 15.0) -> bool:
    """Polls server URL until HTTP response is received."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ValveWorkshopDesktop/1.0'})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status in (200, 301, 302):
                    return True
        except urllib.error.HTTPError as e:
            # Any HTTP response code means server is listening
            if e.code in (200, 301, 302, 403, 404):
                return True
        except Exception:
            pass
        time.sleep(0.15)
    return False


def run_django_migrations():
    """Applies pending database migrations silently on boot."""
    logger.info("Checking and applying pending database migrations...")
    try:
        from django.core.management import call_command
        buf = io.StringIO()
        call_command('migrate', interactive=False, stdout=buf, stderr=buf)
        res_text = buf.getvalue().strip()
        logger.info(f"Database migrations applied successfully: {res_text or 'No pending migrations'}")
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)


def main(headless: bool = False):
    """
    Main Desktop Application Entry Point.
    """
    # 1. Initialize persistent data directories
    paths = init_desktop_environment()
    logger.info(f"Initialized desktop environment in: {paths['data_dir']}")

    # 2. Initialize Django
    import django
    django.setup()

    # 3. Apply pending migrations
    run_django_migrations()

    # 4. Start GFS Backup background scheduler
    import backup_manager
    backup_engine = backup_manager.get_backup_engine()
    backup_engine.start_background_scheduler(interval_seconds=3600)

    # 5. Determine dynamic port
    port = find_available_port(start_port=8000)
    server_url = f"http://127.0.0.1:{port}/"
    logger.info(f"Binding WSGI server to {server_url}")

    # 6. Start Waitress WSGI Server thread
    import waitress
    from valve_project.wsgi import application

    server_thread = threading.Thread(
        target=waitress.serve,
        args=(application,),
        kwargs={
            'host': '127.0.0.1',
            'port': port,
            'threads': 8,
            '_quiet': True,
        },
        daemon=True,
        name="WaitressWSGIServer",
    )
    server_thread.start()

    # 7. Wait for server readiness
    ready = wait_for_server(server_url, timeout_seconds=12.0)
    if not ready:
        logger.warning(f"Server did not respond within timeout, opening WebView anyway at {server_url}")
    else:
        logger.info(f"Server is live and responding at {server_url}")

    # 8. Headless mode (for automated testing / verification)
    if headless or os.environ.get('VALVE_HEADLESS_TEST') == 'True':
        logger.info("Running in headless test mode. Verifying operations...")
        time.sleep(1.0)
        # Execute pre-shutdown test
        backup_engine.trigger_pre_shutdown_backup()
        backup_engine.stop_scheduler()
        logger.info("Headless test completed successfully.")
        return 0

    # 9. Launch pywebview Desktop Window
    import webview

    icon_candidate = paths['bundle_dir'] / 'app_icon.ico'
    icon_path = str(icon_candidate) if icon_candidate.exists() else None

    window = webview.create_window(
        title="Valve Workshop Management System",
        url=server_url,
        width=1366,
        height=850,
        min_size=(1024, 700),
        text_select=True,
        zoomable=True,
    )

    def on_closing():
        logger.info("Application closing event received. Running pre-shutdown backup...")
        try:
            backup_engine.trigger_pre_shutdown_backup()
        except Exception as e:
            logger.error(f"Pre-shutdown backup failed: {e}")
        try:
            backup_engine.stop_scheduler()
        except Exception as e:
            logger.error(f"Stopping scheduler failed: {e}")
        logger.info("Shutdown sequence finalized.")

    window.events.closing += on_closing

    # Launch desktop UI
    webview.start(debug=False)

    return 0


if __name__ == '__main__':
    is_headless = '--headless' in sys.argv
    sys.exit(main(headless=is_headless))
