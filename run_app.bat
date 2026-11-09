@echo off
title Valve Workshop Desktop Application
echo Starting Valve Workshop Management System...

if exist "env_laptop\Scripts\python.exe" (
    "env_laptop\Scripts\python.exe" launcher.py
) else if exist "myenv\Scripts\python.exe" (
    "myenv\Scripts\python.exe" launcher.py
) else (
    python launcher.py
)

pause

