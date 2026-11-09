"""
Entry point for Valve Workshop Standalone Desktop Executable.
"""
import sys
import io
from pathlib import Path

# Fix for PyInstaller --noconsole mode
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from desktop_app.launcher import main

if __name__ == '__main__':
    is_headless = '--headless' in sys.argv or '--headless-test' in sys.argv
    sys.exit(main(headless=is_headless))
