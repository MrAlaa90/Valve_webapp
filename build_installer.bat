@echo off
title Build Valve Workshop Installer
echo ===================================================
echo Building Valve Workshop Standalone .exe & Installer
echo ===================================================

if exist "env_laptop\Scripts\python.exe" (
    "env_laptop\Scripts\python.exe" build_desktop.py
) else if exist "myenv\Scripts\python.exe" (
    "myenv\Scripts\python.exe" build_desktop.py
) else (
    python build_desktop.py
)

echo.
echo Build script finished. Press any key to exit.
pause
