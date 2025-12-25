#!/usr/bin/env python3
"""
Setup script for Stock Allocation Tool build environment.

This script helps users set up a proper virtual environment and install
all dependencies needed for building the standalone executable.

Usage:
    python setup_build_env.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Please install Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_venv_exists():
    """Check if virtual environment already exists."""
    venv_path = Path('venv')
    if venv_path.exists():
        print("✅ Virtual environment directory already exists")
        return True
    
    print("ℹ️  Virtual environment not found")
    return False


def create_virtual_environment():
    """Create a new virtual environment."""
    print("Creating virtual environment...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'venv', 'venv'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Virtual environment created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Python venv module not found")
        print("Please ensure Python is properly installed with venv support")
        return False


def get_activation_command():
    """Get the command to activate the virtual environment."""
    if platform.system() == 'Windows':
        return 'venv\\Scripts\\activate'
    else:
        return 'source venv/bin/activate'


def get_python_executable():
    """Get the path to Python executable in virtual environment."""
    if platform.system() == 'Windows':
        return Path('venv') / 'Scripts' / 'python.exe'
    else:
        return Path('venv') / 'bin' / 'python'


def install_dependencies():
    """Install dependencies in the virtual environment."""
    print("Installing dependencies...")
    
    python_exe = get_python_executable()
    
    if not python_exe.exists():
        print(f"❌ Python executable not found at {python_exe}")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([
            str(python_exe), '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True, text=True)
        
        # Install requirements
        result = subprocess.run([
            str(python_exe), '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("STDERR:", e.stderr)
        return False


def verify_installation():
    """Verify that all required packages are installed."""
    print("Verifying installation...")
    
    python_exe = get_python_executable()
    
    # Test imports
    test_script = """
import sys
try:
    import yfinance
    import PyInstaller
    import tkinter
    print("✅ All required packages imported successfully")
    print(f"yfinance version: {yfinance.__version__}")
    print(f"PyInstaller version: {PyInstaller.__version__}")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run([
            str(python_exe), '-c', test_script
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Package verification failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def print_next_steps():
    """Print instructions for next steps."""
    activation_cmd = get_activation_command()
    
    print("\n" + "="*50)
    print("🎉 Build environment setup complete!")
    print("="*50)
    print("\nNext steps:")
    print(f"1. Activate the virtual environment:")
    print(f"   {activation_cmd}")
    print("\n2. Build the executable:")
    print("   python build.py")
    print("\n3. Find your executable in the dist/ directory")
    print("\nNote: Always activate the virtual environment before building!")


def main():
    """Main setup function."""
    print("Stock Allocation Tool - Build Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Create virtual environment if needed
    if not check_venv_exists():
        if not create_virtual_environment():
            sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        print("You may need to manually fix dependency issues")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)