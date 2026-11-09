import logging
from django.apps import AppConfig
from django.db.backends.signals import connection_created

logger = logging.getLogger(__name__)


def set_sqlite_pragmas(sender, connection, **kwargs):
    """
    Applies enterprise reliability & performance pragmas to SQLite connections:
    - WAL journal mode: high concurrency (readers don't block writers, writers don't block readers).
    - synchronous = NORMAL: safe durability with drastically improved write speed.
    - foreign_keys = ON: strict relational integrity enforcement.
    - busy_timeout = 10000: wait up to 10 seconds on busy locks before timeout.
    """
    if connection.vendor == 'sqlite':
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA busy_timeout = 10000;")
            cursor.close()
        except Exception as e:
            logger.warning(f"Could not apply SQLite pragmas: {e}")


class ValvesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'valves'

    def ready(self):
        connection_created.connect(set_sqlite_pragmas)
