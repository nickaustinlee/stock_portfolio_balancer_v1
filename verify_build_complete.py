#!/usr/bin/env python3
"""
Verification script to demonstrate that PyInstaller configuration is complete.

This script verifies that all build components are working correctly
and demonstrates the complete build process.
"""

import os
import sys
import subprocess
from pathlib import Path


def verify_files_exist():
    """Verify all required build files exist."""
    required_files = [
        'setup_build_env.py',
        'build.py', 
        'stock-allocation-tool.spec',
        'test_build_config.py',
        'BUILD.md',
        'PACKAGING.md',
        'requirements.txt',
        'main.py'
    ]
    
    print("Checking required files...")
    all_exist = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist


def verify_venv_setup():
    """Verify virtual environment is properly set up."""
    venv_path = Path('venv')
    
    if not venv_path.exists():
        print("❌ Virtual environment not found")
        return False
    
    print("✅ Virtual environment exists")
    
    # Check for Python executable
    if sys.platform == 'win32':
        python_exe = venv_path / 'Scripts' / 'python.exe'
    else:
        python_exe = venv_path / 'bin' / 'python'
    
    if not python_exe.exists():
        print(f"❌ Python executable not found at {python_exe}")
        return False
    
    print(f"✅ Python executable found at {python_exe}")
    return True


def verify_dependencies():
    """Verify dependencies are installed in virtual environment."""
    if sys.platform == 'win32':
        python_exe = 'venv/Scripts/python.exe'
    else:
        python_exe = 'venv/bin/python'
    
    test_script = """
import sys
required_modules = ['yfinance', 'PyInstaller', 'tkinter', 'pytest', 'hypothesis']
missing = []

for module in required_modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        missing.append(module)

if missing:
    print(f'Missing modules: {missing}')
    sys.exit(1)
else:
    print('All required modules available')
    sys.exit(0)
"""
    
    try:
        result = subprocess.run([python_exe, '-c', test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Dependency check failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def verify_build_works():
    """Verify that the build process works."""
    if sys.platform == 'win32':
        python_exe = 'venv/Scripts/python.exe'
    else:
        python_exe = 'venv/bin/python'
    
    print("Testing build configuration...")
    
    try:
        result = subprocess.run([python_exe, 'test_build_config.py'], 
                              capture_output=True, text=True, check=True)
        print("✅ Build configuration test passed")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build configuration test failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def verify_executable_exists():
    """Check if executable was built successfully."""
    dist_path = Path('dist')
    
    if not dist_path.exists():
        print("ℹ️  No dist/ directory found (executable not built yet)")
        return None
    
    # Check for different executable types
    executables_found = []
    
    # Standalone executable
    executable_name = 'StockAllocationTool'
    if sys.platform == 'win32':
        executable_name += '.exe'
    
    executable_path = dist_path / executable_name
    if executable_path.exists():
        size_mb = executable_path.stat().st_size / (1024 * 1024)
        executables_found.append(f"Standalone: {executable_path} ({size_mb:.1f} MB)")
    
    # macOS app bundle
    if sys.platform == 'darwin':
        app_bundle_path = dist_path / 'StockAllocationTool.app'
        if app_bundle_path.exists():
            executables_found.append(f"App Bundle: {app_bundle_path}")
    
    if executables_found:
        print("✅ Executables found:")
        for exe in executables_found:
            print(f"   {exe}")
        print("\n💡 To run the application:")
        if sys.platform == 'darwin':
            print('   Double-click "StockAllocationTool.app" (recommended)')
            print('   Or run: open "dist/StockAllocationTool.app"')
            print('   Or run: ./dist/StockAllocationTool')
        elif sys.platform == 'win32':
            print('   Double-click "StockAllocationTool.exe"')
        else:
            print('   Double-click "StockAllocationTool"')
            print('   Or run: ./dist/StockAllocationTool')
        
        print("\n⚠️  Do NOT run .pkg files from build/ directory!")
        return True
    else:
        print("ℹ️  Executable not found (run build script to create)")
        return None


def main():
    """Main verification function."""
    print("PyInstaller Configuration Verification")
    print("=" * 50)
    
    checks = [
        ("Required Files", verify_files_exist),
        ("Virtual Environment", verify_venv_setup), 
        ("Dependencies", verify_dependencies),
        ("Build Configuration", verify_build_works),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            if check_func():
                passed += 1
            else:
                print(f"❌ {check_name} check failed")
        except Exception as e:
            print(f"❌ {check_name} check error: {e}")
    
    # Check executable (optional)
    print(f"\nExecutable Status:")
    verify_executable_exists()
    
    print(f"\n{'='*50}")
    print(f"Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 PyInstaller configuration is complete and working!")
        print("\nTo build the executable:")
        if sys.platform == 'win32':
            print("  venv\\Scripts\\python build.py")
        else:
            print("  venv/bin/python build.py")
        print("\nTo set up a new environment:")
        print("  python setup_build_env.py")
        return True
    else:
        print("❌ Some checks failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)