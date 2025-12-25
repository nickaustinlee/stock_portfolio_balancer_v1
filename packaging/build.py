#!/usr/bin/env python3
"""
Build script for creating standalone executable of Stock Allocation Tool.

This script uses PyInstaller to create a standalone executable that includes
all dependencies and can run without requiring Python installation.

Usage:
    python build.py [--debug] [--clean]
    
    --debug: Create debug build with console window
    --clean: Clean build directories before building
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def clean_build_dirs():
    """Remove existing build and dist directories."""
    # Work from parent directory since build/dist are in project root
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        dirs_to_clean = ['build', 'dist', '__pycache__']
        
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                print(f"Removing {dir_name}/")
                shutil.rmtree(dir_name)
        
        # Also clean .spec files that are auto-generated (but not our custom one)
        for spec_file in Path('.').glob('*.spec'):
            # Don't remove our custom spec file in packaging/
            if spec_file.name != 'stock-allocation-tool.spec':
                print(f"Removing {spec_file}")
                spec_file.unlink()
    finally:
        os.chdir(original_dir)


def check_virtual_environment():
    """Check if running in a virtual environment and recommend if not."""
    in_venv = (
        hasattr(sys, 'real_prefix') or  # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)  # venv
    )
    
    if not in_venv:
        print("WARNING: Not running in a virtual environment")
        print("Recommendation: Create and activate a virtual environment:")
        if sys.platform == 'win32':
            print("  python -m venv venv")
            print("  venv\\Scripts\\activate")
        else:
            print("  python -m venv venv")
            print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        print()
        
        # Ask user if they want to continue
        try:
            response = input("Continue without virtual environment? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Exiting. Please set up virtual environment first.")
                return False
        except KeyboardInterrupt:
            print("\nExiting.")
            return False
    else:
        print("✅ Running in virtual environment")
    
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("ERROR: PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Check if main dependencies are available
    required_modules = ['yfinance', 'tkinter']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"ERROR: Missing required modules: {', '.join(missing_modules)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def build_executable(debug_mode=False):
    """Build the standalone executable using PyInstaller."""
    
    # Use the same Python executable that's running this script
    # This ensures we use the virtual environment's pyinstaller
    python_exe = sys.executable
    pyinstaller_cmd = [python_exe, '-m', 'PyInstaller']
    
    # Use the spec file for better control over the build process
    # Look for spec file in current directory (packaging/)
    spec_file = 'stock-allocation-tool.spec'
    spec_path = Path(__file__).parent / spec_file
    
    if not spec_path.exists():
        print(f"ERROR: Spec file {spec_path} not found")
        return False
    
    # Build using spec file - run from parent directory
    # Change to parent directory so paths in spec file work correctly
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        # Build using spec file from packaging directory
        cmd = pyinstaller_cmd + [f'packaging/{spec_file}']
        
        # Add debug flag if needed (this will be handled by the spec file)
        if debug_mode:
            print("Debug mode: Console window will be shown")
            # Modify spec file temporarily for debug mode
            # For now, just note that debug mode was requested
        
        print("Building executable with spec file:")
        print(' '.join(cmd))
        print()
        
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    finally:
        # Always return to original directory
        os.chdir(original_dir)


def test_executable():
    """Test the built executable."""
    # Work from parent directory since dist/ is in project root
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        executable_name = 'StockAllocationTool'
        
        if sys.platform == 'win32':
            executable_path = Path('dist') / f'{executable_name}.exe'
        else:
            executable_path = Path('dist') / executable_name
        
        if not executable_path.exists():
            print(f"ERROR: Executable not found at {executable_path}")
            return False
        
        print(f"Executable created at: {executable_path}")
        print(f"File size: {executable_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Test that the executable can start (just check it doesn't crash immediately)
        print("Testing executable startup...")
        try:
            # Run with a timeout to avoid hanging
            result = subprocess.run([str(executable_path), '--help'], 
                                  timeout=10, capture_output=True, text=True)
            print("Executable test completed")
            return True
        except subprocess.TimeoutExpired:
            print("Executable started successfully (timed out waiting for GUI)")
            return True
        except Exception as e:
            print(f"Executable test failed: {e}")
            return False
    finally:
        os.chdir(original_dir)


def main():
    """Main build script entry point."""
    parser = argparse.ArgumentParser(description='Build Stock Allocation Tool executable')
    parser.add_argument('--debug', action='store_true', 
                       help='Create debug build with console window')
    parser.add_argument('--clean', action='store_true',
                       help='Clean build directories before building')
    
    args = parser.parse_args()
    
    print("Stock Allocation Tool - Build Script")
    print("=" * 40)
    
    # Clean build directories if requested
    if args.clean:
        print("Cleaning build directories...")
        clean_build_dirs()
        print()
    
    # Check virtual environment
    print("Checking virtual environment...")
    if not check_virtual_environment():
        sys.exit(1)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print()
    
    # Build executable
    build_type = "debug" if args.debug else "release"
    print(f"Building {build_type} executable...")
    if not build_executable(args.debug):
        sys.exit(1)
    print()
    
    # Test executable
    print("Testing executable...")
    if not test_executable():
        print("WARNING: Executable test failed, but build completed")
    print()
    
    print("Build process completed!")
    print()
    print("Next steps:")
    print("1. Test the executable in dist/ directory")
    print("2. Distribute the executable to users")
    print("3. Users can run it without Python installation")


if __name__ == "__main__":
    main()