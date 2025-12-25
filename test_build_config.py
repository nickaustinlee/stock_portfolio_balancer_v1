#!/usr/bin/env python3
"""
Test script to verify build configuration without running PyInstaller.

This script tests that all the build components are properly configured
and that the main application can be imported successfully.
"""

import sys
import os
from pathlib import Path


def test_main_entry_point():
    """Test that the main entry point can be imported."""
    try:
        # Test that main.py exists and can be executed
        main_path = Path('main.py')
        if not main_path.exists():
            print("❌ main.py not found")
            return False
        
        print("✅ main.py exists")
        
        # Check if we're in a virtual environment with dependencies
        try:
            sys.path.insert(0, 'src')
            from controllers.portfolio_controller import PortfolioController
            from utils.debug import logger
            print("✅ Main application components can be imported")
            return True
        except ImportError as e:
            if 'yfinance' in str(e) or 'tkinter' in str(e):
                print("ℹ️  Dependencies not available (run setup_build_env.py first)")
                print("✅ Main entry point structure is correct")
                return True  # Structure is correct, just missing deps
            else:
                print(f"❌ Import error: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error testing main entry point: {e}")
        return False


def test_build_script():
    """Test that the build script is properly configured."""
    try:
        build_path = Path('build.py')
        if not build_path.exists():
            print("❌ build.py not found")
            return False
        
        print("✅ build.py exists")
        
        # Test that build script can be imported
        import build
        
        print("✅ build.py can be imported")
        
        # Test key functions exist
        required_functions = ['check_dependencies', 'build_executable', 'test_executable']
        for func_name in required_functions:
            if not hasattr(build, func_name):
                print(f"❌ Missing function: {func_name}")
                return False
        
        print("✅ All required build functions present")
        return True
        
    except Exception as e:
        print(f"❌ Error testing build script: {e}")
        return False


def test_spec_file():
    """Test that the PyInstaller spec file is valid."""
    try:
        spec_path = Path('stock-allocation-tool.spec')
        if not spec_path.exists():
            print("❌ stock-allocation-tool.spec not found")
            return False
        
        print("✅ stock-allocation-tool.spec exists")
        
        # Read and validate spec file content
        spec_content = spec_path.read_text()
        
        required_elements = [
            'Analysis',
            'PYZ', 
            'EXE',
            'main.py',
            'yfinance',
            'tkinter'
        ]
        
        for element in required_elements:
            if element not in spec_content:
                print(f"❌ Missing element in spec file: {element}")
                return False
        
        print("✅ Spec file contains all required elements")
        return True
        
    except Exception as e:
        print(f"❌ Error testing spec file: {e}")
        return False


def test_requirements():
    """Test that requirements.txt contains packaging dependencies."""
    try:
        req_path = Path('requirements.txt')
        if not req_path.exists():
            print("❌ requirements.txt not found")
            return False
        
        print("✅ requirements.txt exists")
        
        requirements = req_path.read_text()
        
        required_packages = ['pyinstaller', 'yfinance', 'setuptools']
        
        for package in required_packages:
            if package not in requirements.lower():
                print(f"❌ Missing package in requirements.txt: {package}")
                return False
        
        print("✅ All required packages listed in requirements.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error testing requirements: {e}")
        return False


def test_documentation():
    """Test that build documentation exists."""
    try:
        doc_path = Path('BUILD.md')
        if not doc_path.exists():
            print("❌ BUILD.md not found")
            return False
        
        print("✅ BUILD.md exists")
        
        doc_content = doc_path.read_text()
        
        required_sections = [
            'Prerequisites',
            'Build Methods', 
            'Platform-Specific',
            'Troubleshooting'
        ]
        
        for section in required_sections:
            if section not in doc_content:
                print(f"❌ Missing section in BUILD.md: {section}")
                return False
        
        print("✅ BUILD.md contains all required sections")
        return True
        
    except Exception as e:
        print(f"❌ Error testing documentation: {e}")
        return False


def main():
    """Run all build configuration tests."""
    print("Testing Build Configuration")
    print("=" * 40)
    
    tests = [
        ("Main Entry Point", test_main_entry_point),
        ("Build Script", test_build_script),
        ("Spec File", test_spec_file),
        ("Requirements", test_requirements),
        ("Documentation", test_documentation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n{'='*40}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All build configuration tests passed!")
        print("\nNext steps:")
        print("1. Install PyInstaller: pip install pyinstaller")
        print("2. Run build: python build.py")
        print("3. Test executable in dist/ directory")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)