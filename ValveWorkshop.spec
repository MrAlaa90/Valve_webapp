# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Valve Workshop Windows desktop application.
"""

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
BASE_DIR = Path.cwd()
os.environ['DESKTOP_MODE'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valve_project.settings')

try:
    import django
    django.setup()
except Exception:
    pass

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

for package in ('crispy_forms', 'crispy_bootstrap5', 'rest_framework', 'djoser'):
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
    'djoser',
    'django_extensions',
    'django_filters',
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
