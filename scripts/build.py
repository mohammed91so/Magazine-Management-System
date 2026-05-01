"""
Build script for packaging the Inventory System.

Usage: python scripts/build.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")
    
    # Clean Python cache
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))
    
    print("Clean complete.")


def build_executable():
    """Build executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=InventorySystem',
        '--add-data=.env:.',
        '--add-data=config:config',
        '--add-data=database:database',
        '--add-data=services:services',
        '--add-data=ui:ui',
        '--add-data=utils:utils',
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=dotenv',
        'main.py'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        sys.exit(1)
    
    print("Build successful!")
    print(f"Executable created at: dist/InventorySystem.exe")


def main():
    """Main build process."""
    print("=" * 50)
    print("Inventory System Build Script")
    print("=" * 50)
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    build_executable()
    
    print("\nBuild process complete!")


if __name__ == "__main__":
    main()
