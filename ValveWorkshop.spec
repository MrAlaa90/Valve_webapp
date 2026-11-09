# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec Configuration for Valve Workshop Desktop Executable.
Compiles the full Django runtime, Waitress WSGI server, and pywebview shell
into a standalone, production-grade Windows application.
"""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
BASE_DIR = Path.cwd()

# Configure Django settings before collecting hooks to eliminate ImproperlyConfigured warnings
os.environ['DESKTOP_MODE'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valve_project.settings')
try:
    import django
    django.setup()
except Exception:
    pass

# Collect third-party Django app templates and static assets
crispy_datas = collect_data_files('crispy_forms')
crispy_bs5_datas = collect_data_files('crispy_bootstrap5')
rest_datas = collect_data_files('rest_framework')
djoser_datas = collect_data_files('djoser')

# Application bundled assets
added_datas = [
    (str(BASE_DIR / 'valve_project' / 'templates'), 'valve_project/templates'),
    (str(BASE_DIR / 'static'), 'static'),
    (str(BASE_DIR / 'staticfiles'), 'staticfiles'),
    (str(BASE_DIR / 'locale'), 'locale'),
    (str(BASE_DIR / 'db.sqlite3'), '.'),
    (str(BASE_DIR / 'app_icon.ico'), '.'),
] + crispy_datas + crispy_bs5_datas + rest_datas + djoser_datas

# Hidden imports for dynamic Django components
hidden_imports = [
    # Django core & contrib
    'django',
    'django.core.management',
    'django.core.management.commands.migrate',
    'django.core.management.commands.collectstatic',
    'django.core.management.commands.showmigrations',
    'django.contrib.admin',
    'django.contrib.admin.apps',
    'django.contrib.auth',
    'django.contrib.auth.apps',
    'django.contrib.contenttypes',
    'django.contrib.contenttypes.apps',
    'django.contrib.sessions',
    'django.contrib.sessions.apps',
    'django.contrib.messages',
    'django.contrib.messages.apps',
    'django.contrib.staticfiles',
    'django.contrib.staticfiles.apps',
    'django.middleware.security',
    'django.middleware.locale',
    'django.middleware.common',
    'django.middleware.csrf',
    'django.middleware.clickjacking',
    'django.db.backends.sqlite3',
    'django.db.backends.sqlite3.base',
    'django.template.loaders.filesystem',
    'django.template.loaders.app_directories',

    # Third-party packages
    'whitenoise',
    'whitenoise.middleware',
    'whitenoise.storage',
    'waitress',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework.permissions',
    'rest_framework.parsers',
    'rest_framework.renderers',
    'rest_framework.views',
    'djoser',
    'djoser.urls',
    'djoser.urls.authtoken',
    'django_extensions',
    'django_filters',

    # GUI and system
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    'clr_loader',
    'pythonnet',
    'clr',
    'sqlite3',

    # Application modules
    'valves',
    'valves.apps',
    'valves.models',
    'valves.views',
    'valves.urls',
    'valves.forms',
    'valves.admin',
    'valves.serializers',
    'valves.filters',
    'desktop_app',
    'desktop_app.paths',
    'desktop_app.launcher',
    'backup_manager',
]

# Collect submodules
hidden_imports += collect_submodules('django.contrib.admin')
hidden_imports += collect_submodules('django.contrib.auth')
hidden_imports += collect_submodules('crispy_forms')
hidden_imports += collect_submodules('crispy_bootstrap5')
hidden_imports += collect_submodules('rest_framework')
hidden_imports += collect_submodules('djoser')

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

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

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
    icon=str(BASE_DIR / 'app_icon.ico'),
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
