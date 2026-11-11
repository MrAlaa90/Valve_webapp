# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Valve Workshop Windows desktop application.
"""

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
BASE_DIR = Path.cwd()
import sys
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ['DESKTOP_MODE'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valve_project.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Warning during django.setup() in spec: {e}")

added_datas = []
for source, destination in (
    (BASE_DIR / 'valve_project' / 'templates', 'valve_project/templates'),
    (BASE_DIR / 'static', 'static'),
    (BASE_DIR / 'staticfiles', 'staticfiles'),
    (BASE_DIR / 'locale', 'locale'),
    (BASE_DIR / 'db.sqlite3', '.'),
    (BASE_DIR / 'app_icon.ico', '.'),
):
    if source.exists():
        added_datas.append((str(source), destination))

for package in ('crispy_forms', 'crispy_bootstrap5', 'rest_framework', 'djoser', 'widget_tweaks'):
    added_datas += collect_data_files(package)

hidden_imports = [
    'django.core.management',
    'django.core.management.commands.migrate',
    'django.core.management.commands.collectstatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.db.backends.sqlite3',
    'django.db.backends.sqlite3.base',
    'django.db.backends.postgresql',
    'django.template.loaders.filesystem',
    'django.template.loaders.app_directories',
    'whitenoise.middleware',
    'whitenoise.storage',
    'waitress',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework.urls',
    'rest_framework.routers',
    'rest_framework.views',
    'rest_framework.response',
    'rest_framework.request',
    'rest_framework.serializers',
    'rest_framework.permissions',
    'rest_framework.authentication',
    'rest_framework.parsers',
    'rest_framework.renderers',
    'rest_framework.negotiation',
    'rest_framework.metadata',
    'rest_framework.schemas',
    'djoser',
    'djoser.urls',
    'djoser.urls.authtoken',
    'djoser.urls.base',
    'djoser.urls.jwt',
    'djoser.views',
    'djoser.serializers',
    'djoser.conf',
    'djoser.constants',
    'djoser.email',
    'djoser.permissions',
    'djoser.signals',
    'djoser.compat',
    'djoser.auth_backends',
    'djoser.webauthn',
    'django.conf.urls.i18n',
    'django.views.i18n',
    'django.views.static',
    'django_extensions',
    'django_filters',
    'widget_tweaks',
    'widget_tweaks.templatetags',
    'widget_tweaks.templatetags.widget_tweaks',
    'psycopg2',
    'sqlite3',
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
    'et_xmlfile',
    'valves',
    'valves.apps',
    'valves.models',
    'valves.views',
    'valves.urls',
    'valves.forms',
    'valves.admin',
    'valves.serializers',
    'valves.filters',
    'valves.data_exchange',
    'valve_project',
    'desktop_app',
    'desktop_app.paths',
    'desktop_app.launcher',
    'backup_manager',
]

for package in (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.auth.migrations',
    'django.contrib.contenttypes.migrations',
    'django.contrib.sessions.migrations',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'djoser',
    'django_filters',
    'widget_tweaks',
    'openpyxl',
    'valves',
    'valve_project',
):
    hidden_imports += collect_submodules(package)

hidden_imports = list(dict.fromkeys(hidden_imports))

a = Analysis(
    ['launcher.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ValveWorkshop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(BASE_DIR / 'app_icon.ico') if (BASE_DIR / 'app_icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ValveWorkshop',
)
