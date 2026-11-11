import os
import sys
import shutil
import secrets
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Determine if running within a bundled PyInstaller executable
IS_FROZEN = getattr(sys, 'frozen', False)

# Code / Bundle directory (read-only in Program Files or MEIPASS temp folder)
if IS_FROZEN:
    BUNDLE_DIR = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent)).resolve()
else:
    BUNDLE_DIR = Path(__file__).resolve().parent.parent

# Persistent User Data directory (%APPDATA%/ValveWorkshop or %LOCALAPPDATA%/ValveWorkshop)
def get_default_data_dir() -> Path:
    env_dir = os.environ.get('VALVE_DATA_DIR')
    if env_dir:
        return Path(env_dir).resolve()

    appdata = os.environ.get('APPDATA')
    if appdata:
        return Path(appdata) / 'ValveWorkshop'

    localappdata = os.environ.get('LOCALAPPDATA')
    if localappdata:
        return Path(localappdata) / 'ValveWorkshop'

    # Fallback to user home
    return Path.home() / 'AppData' / 'Roaming' / 'ValveWorkshop'

DATA_DIR = get_default_data_dir()

# Isolated Subpaths
DB_PATH = DATA_DIR / 'db.sqlite3'
MEDIA_DIR = DATA_DIR / 'media'
LOGS_DIR = DATA_DIR / 'logs'
BACKUP_DIR = DATA_DIR / 'backups'
SECRET_KEY_PATH = DATA_DIR / 'secret.key'

# Bundled Asset Paths (read-only)
BUNDLED_DB = BUNDLE_DIR / 'db.sqlite3'
BUNDLED_MEDIA = BUNDLE_DIR / 'media'
BUNDLED_STATIC = BUNDLE_DIR / 'static'
BUNDLED_STATICFILES = BUNDLE_DIR / 'staticfiles'
BUNDLED_TEMPLATES = BUNDLE_DIR / 'valve_project' / 'templates'
BUNDLED_LOCALE = BUNDLE_DIR / 'locale'
BUNDLED_ICON = BUNDLE_DIR / 'app_icon.ico'


def get_or_create_secret_key() -> str:
    """Retrieves or generates a persistent machine-specific secret key."""
    env_key = os.environ.get('SECRET_KEY')
    if env_key and len(env_key.strip()) >= 32:
        return env_key.strip()

    if SECRET_KEY_PATH.exists():
        try:
            stored = SECRET_KEY_PATH.read_text(encoding='utf-8').strip()
            if stored and len(stored) >= 32:
                return stored
        except Exception as e:
            logger.warning(f"Failed to read existing secret key from {SECRET_KEY_PATH}: {e}")

    # Generate new strong random key
    new_key = secrets.token_hex(32)
    try:
        SECRET_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        SECRET_KEY_PATH.write_text(new_key, encoding='utf-8')
    except Exception as e:
        logger.warning(f"Could not persist secret key to {SECRET_KEY_PATH}: {e}")
    return new_key


def init_desktop_environment():
    """
    Initializes persistent directories in %APPDATA%/ValveWorkshop.
    Preserves existing data and seeds defaults on initial execution.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Database Initialization
    if not DB_PATH.exists():
        if BUNDLED_DB.exists():
            logger.info(f"Seeding initial database from {BUNDLED_DB} -> {DB_PATH}")
            try:
                shutil.copy2(BUNDLED_DB, DB_PATH)
            except Exception as e:
                logger.error(f"Error copying bundled database: {e}")
        else:
            logger.info("No bundled database found. An empty database will be initialized via migrations.")

    # 2. Media Assets Initialization
    try:
        has_media = MEDIA_DIR.exists() and any(MEDIA_DIR.iterdir())
    except Exception:
        has_media = False

    if not has_media:
        source_media = None
        for candidate in [
            BUNDLED_MEDIA,
            BUNDLE_DIR.parent / 'media',
            Path(getattr(sys, '_MEIPASS', '')) / 'media' if getattr(sys, '_MEIPASS', '') else None,
            Path(r"D:\Projects\Valve_syste\valves_app\Valvesystem\Valvesystem\media"),
        ]:
            if candidate and candidate.exists() and candidate.is_dir():
                try:
                    if any(candidate.iterdir()):
                        source_media = candidate
                        break
                except Exception:
                    pass

        if source_media:
            logger.info(f"Initializing media assets from {source_media} -> {MEDIA_DIR}")
            try:
                # On Windows, try creating an instant, zero-footprint directory junction
                if sys.platform == 'win32':
                    try:
                        if MEDIA_DIR.exists() and not any(MEDIA_DIR.iterdir()):
                            MEDIA_DIR.rmdir()
                    except OSError:
                        pass
                    try:
                        import _winapi
                        _winapi.CreateJunction(str(source_media.resolve()), str(MEDIA_DIR.resolve()))
                        logger.info(f"Created instant directory junction to {source_media}")
                    except Exception as je:
                        logger.warning(f"Could not create junction: {je}; falling back to copy")

                # Fallback copy if junction was not created
                if not (MEDIA_DIR.exists() and any(MEDIA_DIR.iterdir())):
                    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
                    for item in source_media.iterdir():
                        dest = MEDIA_DIR / item.name
                        if not dest.exists():
                            if item.is_dir():
                                shutil.copytree(item, dest)
                            else:
                                shutil.copy2(item, dest)
            except Exception as e:
                logger.error(f"Error copying initial media files: {e}")

    # 3. Export environment variables for Django settings
    os.environ['VALVE_DATA_DIR'] = str(DATA_DIR)
    os.environ['VALVE_DB_PATH'] = str(DB_PATH)
    os.environ['VALVE_MEDIA_DIR'] = str(MEDIA_DIR)
    os.environ['VALVE_LOGS_DIR'] = str(LOGS_DIR)
    os.environ['VALVE_BACKUP_DIR'] = str(BACKUP_DIR)
    os.environ['SECRET_KEY'] = get_or_create_secret_key()

    return {
        'bundle_dir': BUNDLE_DIR,
        'data_dir': DATA_DIR,
        'db_path': DB_PATH,
        'media_dir': MEDIA_DIR,
        'logs_dir': LOGS_DIR,
        'backup_dir': BACKUP_DIR,
    }

