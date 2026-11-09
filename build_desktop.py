"""
Automated Desktop Build & Packaging Pipeline
Compiles the Django application into a standalone Windows executable
using PyInstaller and builds an Inno Setup installer.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def step(msg: str):
    print(f"\n{'='*70}\n[*] {msg}\n{'='*70}")


def run_cmd(cmd_list, desc: str):
    print(f"--> Executing: {' '.join(str(c) for c in cmd_list)}")
    res = subprocess.run(cmd_list, cwd=str(BASE_DIR))
    if res.returncode != 0:
        raise RuntimeError(f"Step failed ({desc}) with return code {res.returncode}")


def main():
    step("1. Preparing Application Assets & Icons")
    # Generate high-resolution multi-size icon if needed
    icon_path = BASE_DIR / 'app_icon.ico'
    logo_path = BASE_DIR / 'static' / 'images' / 'workshop-logo.png'
    if not icon_path.exists() and logo_path.exists():
        from PIL import Image
        img = Image.open(logo_path)
        img.save(icon_path, format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print(f"Generated {icon_path}")
    else:
        print(f"Application icon ready: {icon_path}")

    step("2. Collecting Static Files")
    python_exe = sys.executable
    run_cmd([python_exe, "manage.py", "collectstatic", "--noinput"], "Collect Static Files")

    step("3. Compiling Standalone Executable with PyInstaller")
    run_cmd([python_exe, "-m", "PyInstaller", "ValveWorkshop.spec", "--clean", "--noconfirm"], "PyInstaller Compilation")

    dist_dir = BASE_DIR / "dist" / "ValveWorkshop"
    exe_path = dist_dir / "ValveWorkshop.exe"
    if not exe_path.exists():
        raise FileNotFoundError(f"Expected executable not found at: {exe_path}")

    print(f"\n[+] Executable successfully generated at: {exe_path}")

    step("4. Checking for Inno Setup Compiler (ISCC)")
    iscc_candidates = [
        shutil.which("iscc"),
        shutil.which("iscc.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    iscc_path = next((c for c in iscc_candidates if c and os.path.exists(c)), None)

    if iscc_path:
        print(f"Found Inno Setup Compiler at: {iscc_path}")
        step("5. Compiling Inno Setup Windows Installer")
        run_cmd([iscc_path, str(BASE_DIR / "installer_setup.iss")], "Inno Setup Build")
        installer_path = BASE_DIR / "dist_installer" / "ValveWorkshop_Setup_v1.0.0.exe"
        if installer_path.exists():
            print(f"\n[+] Installer successfully created at: {installer_path}")
    else:
        print("\n[!] Inno Setup (ISCC.exe) not found on PATH or default directories.")
        print("    The 'installer_setup.iss' script is ready.")
        print("    To compile the setup installer, install Inno Setup 6 and run:")
        print(f'    "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" "{BASE_DIR / "installer_setup.iss"}"')

    step("BUILD PROCESS COMPLETE!")
    print(f"Standalone binaries: {dist_dir}")
    print(f"Main Executable:     {exe_path}")


if __name__ == "__main__":
    main()
