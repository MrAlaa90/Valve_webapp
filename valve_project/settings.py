"""
Django settings for valve_project project.
Industrial Valve Maintenance Management System.
Supports both Web Server and Enterprise Standalone Desktop Executable.
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- تحميل متغيرات البيئة من ملف .env إن وجد ---
if (BASE_DIR / '.env').exists():
    load_dotenv(BASE_DIR / '.env')

# Detect execution context: Frozen executable (PyInstaller) or Desktop Mode
IS_FROZEN = getattr(sys, 'frozen', False)
DESKTOP_MODE = os.environ.get('DESKTOP_MODE', 'True' if IS_FROZEN else 'False') == 'True'

if DESKTOP_MODE:
    try:
        from desktop_app.paths import (
            init_desktop_environment,
            BUNDLE_DIR,
            DATA_DIR,
            DB_PATH,
            MEDIA_DIR,
            LOGS_DIR,
            BACKUP_DIR,
            get_or_create_secret_key,
        )
        desktop_env = init_desktop_environment()
        BUNDLE_DIR = desktop_env['bundle_dir']
        DATA_DIR = desktop_env['data_dir']
        DB_PATH = desktop_env['db_path']
        MEDIA_DIR = desktop_env['media_dir']
        LOGS_DIR = desktop_env['logs_dir']
        BACKUP_DIR = desktop_env['backup_dir']
        SECRET_KEY = get_or_create_secret_key()
    except Exception as e:
        # Fallback isolation in case desktop_app is not on path
        BUNDLE_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR)).resolve()
        appdata_base = os.environ.get('VALVE_DATA_DIR') or os.environ.get('APPDATA') or str(Path.home() / 'AppData' / 'Roaming')
        DATA_DIR = Path(appdata_base) if os.environ.get('VALVE_DATA_DIR') else Path(appdata_base) / 'ValveWorkshop'
        DB_PATH = DATA_DIR / 'db.sqlite3'
        MEDIA_DIR = DATA_DIR / 'media'
        LOGS_DIR = DATA_DIR / 'logs'
        BACKUP_DIR = DATA_DIR / 'backups'
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        SECRET_KEY = os.environ.get('SECRET_KEY', '901866ce8340bb820742ec60ffaaf183864bf59f2f6249e19504bb583e2562b6')
else:
    BUNDLE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR
    DB_PATH = BASE_DIR / 'db.sqlite3'
    MEDIA_DIR = BASE_DIR / 'media'
    LOGS_DIR = BASE_DIR / 'logs'
    BACKUP_DIR = BASE_DIR / 'backups'
    SECRET_KEY = os.environ.get('SECRET_KEY', '901866ce8340bb820742ec60ffaaf183864bf59f2f6249e19504bb583e2562b6')

# في وضع الديسكتوب، يتم تفعيل DEBUG لضمان عدم توقف السيرفر وإتاحة تتبع أي خطأ
if DESKTOP_MODE:
    DEBUG = True
else:
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://valvesworkshop.site',
    'https://www.valvesworkshop.site',
    'http://127.0.0.1',
    'http://localhost',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'valves',  # Core Valve Management App
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',  # Django REST Framework
    'rest_framework.authtoken',
    'djoser',
    'django_extensions',
    'django_filters',  # django-filter
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'valve_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BUNDLE_DIR / 'valve_project' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'valve_project.wsgi.application'

# Database Configuration
if DESKTOP_MODE or 'test' in sys.argv or os.environ.get('USE_SQLITE'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(DB_PATH),
            'OPTIONS': {
                'timeout': 30,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', 5432),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BUNDLE_DIR / 'locale',
]

TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BUNDLE_DIR / 'static',
]
STATIC_ROOT = BUNDLE_DIR / 'staticfiles'

# استخدام التخزين الآمن الذي لا ينهار إذا كان هناك ملف مفقود
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True

# Media files (Dynamic User Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR

# Authentication & Redirects
LOGIN_URL = 'valves:login'
LOGIN_REDIRECT_URL = 'valves:home'
LOGOUT_REDIRECT_URL = 'valves:home'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DESKTOP_MODE:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_PROXY_SSL_HEADER = None

# Logging Configuration
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'app.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
