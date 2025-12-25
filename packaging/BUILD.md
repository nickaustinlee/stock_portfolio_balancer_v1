# Build Instructions - Stock Allocation Tool

This document provides comprehensive instructions for building a standalone executable of the Stock Allocation Tool using PyInstaller.

## Quick Setup

### Automated Setup (Recommended)
```bash
# Run the setup script to create virtual environment and install dependencies
python setup_build_env.py

# Activate virtual environment (as instructed by setup script)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Build executable
python build.py
```

**Note**: The executable is named `StockAllocationTool` (no spaces) to avoid PyInstaller issues on macOS and other platforms. The display name in the app bundle will still show "Stock Allocation Tool" with proper spacing.

### Manual Setup
If you prefer to set up manually, follow the detailed instructions below.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Operating System: Windows 10+, macOS 10.13+, or Linux (Ubuntu 18.04+)
- At least 2GB free disk space for build process
- Internet connection (for downloading dependencies)

### Python Dependencies

**Important: Use a virtual environment to avoid conflicts with system packages.**

#### Setting up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Verify Virtual Environment
```bash
# Check that you're in the virtual environment
which python  # Should show path to venv/bin/python
pip list       # Should show only project dependencies
```

Key dependencies for building:
- `pyinstaller>=5.0.0` - Creates standalone executables
- `setuptools>=65.0.0` - Python packaging tools
- `yfinance>=0.2.18` - Stock price data API
- Application dependencies (tkinter is included with Python)

## Build Methods

### Method 1: Using Build Script (Recommended)

The `build.py` script provides an automated build process with error checking and testing.

#### Basic Build
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Build the executable
python build.py
```

#### Debug Build (with console window)
```bash
python build.py --debug
```

#### Clean Build (removes previous build files)
```bash
python build.py --clean
```

#### Build Script Features
- Automatic dependency checking
- Build directory cleanup
- Executable testing
- Platform-specific optimizations
- Detailed error reporting

### Method 2: Using PyInstaller Directly

#### Simple Command Line Build
```bash
pyinstaller --onefile --windowed --name "Stock Allocation Tool" main.py
```

#### Advanced Build with Spec File
```bash
pyinstaller stock-allocation-tool.spec
```

#### Manual Command with All Options
```bash
pyinstaller \
    --onefile \
    --windowed \
    --name "Stock Allocation Tool" \
    --add-data "src:src" \
    --hidden-import yfinance \
    --hidden-import tkinter \
    --collect-all yfinance \
    main.py
```

## Build Process Details

### What Happens During Build

1. **Dependency Analysis**: PyInstaller analyzes the Python code to find all imported modules
2. **Collection**: All required Python modules, libraries, and data files are collected
3. **Bundling**: Everything is packaged into a single executable file
4. **Optimization**: The executable is compressed and optimized for distribution
5. **Testing**: The build script tests that the executable can start successfully

### Build Output

After a successful build, you'll find the **runnable applications** in the `dist/` directory:

```
dist/
├── StockAllocationTool.exe    (Windows - double-click to run)
├── StockAllocationTool        (macOS/Linux - double-click or run from terminal)
└── StockAllocationTool.app/   (macOS app bundle - double-click to run)
```

**⚠️ Important**: Do NOT run files from the `build/` directory! These are intermediate build artifacts:
```
build/stock-allocation-tool/
└── StockAllocationTool/
    ├── StockAllocationTool.pkg  ❌ Don't run this - will cause installer errors
    ├── base_library.zip         ❌ Build artifact
    └── other build files...     ❌ Build artifacts
```

### Build Artifacts

Temporary files created during build (can be safely deleted):
```
build/                  # Temporary build files
├── stock-allocation-tool/  # Build files from spec file or build script
└── Stock Allocation Tool/  # Build files from command-line (if different naming)
*.spec                 # PyInstaller spec files (if auto-generated)
__pycache__/           # Python cache files
```

**Note**: You may see multiple build directories if you use both the build script and spec file methods. This is normal PyInstaller behavior - each build method creates its own working directory. Use `python build.py --clean` to remove all build artifacts.

## Best Practices

### Avoiding Multiple Build Directories

To keep your project clean and avoid confusion:

1. **Use one build method consistently**:
   - For most users: `python build.py` (recommended)
   - For advanced users: `pyinstaller stock-allocation-tool.spec`

2. **Clean between builds**:
   ```bash
   python build.py --clean  # Removes all build artifacts
   ```

3. **Understand the difference**:
   - `build.py` script: Uses consistent naming and includes testing
   - Spec file: Provides more advanced configuration options

### Recommended Workflow

```bash
# Clean start
python build.py --clean

# Build executable
python build.py

# Test the result
./dist/StockAllocationTool  # macOS/Linux
# or double-click "StockAllocationTool.exe" on Windows
```

## Platform-Specific Instructions

### Windows

#### Prerequisites
- Windows 10 or later
- Python installed from python.org (not Microsoft Store version)
- Windows Defender exclusions may be needed for the build directory

#### Build Command
```cmd
python build.py
```

#### Output
- `dist/Stock Allocation Tool.exe` - Standalone executable
- File size: ~50-80 MB (includes Python runtime and all dependencies)
- No installation required - users can double-click to run

#### Distribution
- Distribute the `.exe` file to users
- No Python installation required on target machines
- Windows Defender may flag the executable initially (common with PyInstaller)

### macOS

#### Prerequisites
- macOS 10.13 (High Sierra) or later
- Python 3.8+ installed via Homebrew or python.org
- Xcode Command Line Tools: `xcode-select --install`

#### Build Command
```bash
python build.py
```

#### Output
- `dist/Stock Allocation Tool` - Standalone executable
- Optional: `dist/Stock Allocation Tool.app` - macOS app bundle (using spec file)

#### Code Signing (Optional)
For distribution outside the App Store:
```bash
codesign --force --deep --sign - "dist/Stock Allocation Tool"
```

#### Distribution
- Distribute the executable or app bundle
- **No installation required**: Users can run the app from anywhere (Downloads, Desktop, etc.)
- **Optional**: Move to Applications folder for permanent installation: `cp -r "StockAllocationTool.app" "/Applications/"`
- Users may need to allow the app in System Preferences > Security & Privacy on first run
- **First run**: Right-click → "Open" → "Open" to bypass security dialog
- Consider notarization for wider distribution

### Linux

#### Prerequisites
- Ubuntu 18.04+ or equivalent distribution
- Python 3.8+ installed
- Required system libraries: `sudo apt-get install python3-tk`

#### Build Command
```bash
python build.py
```

#### Output
- `dist/Stock Allocation Tool` - Standalone executable
- File size: ~40-60 MB

#### Distribution
- Distribute the executable file
- Make executable: `chmod +x "Stock Allocation Tool"`
- May require additional system libraries on some distributions

## Troubleshooting

### Common Build Issues

#### Virtual Environment Issues
```bash
# If you get "command not found" errors:
# Make sure virtual environment is activated:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Verify you're in the virtual environment:
which python  # Should show venv/bin/python or venv\Scripts\python.exe
```

#### "App runs but no window appears" on macOS
```bash
# Check if the app is actually running:
ps aux | grep -i stockallocation

# Try running from terminal to see error messages:
./dist/StockAllocationTool

# Check Console.app for crash logs or error messages
# Look for entries related to "StockAllocationTool"

# If window is hidden, try:
# - Cmd+Tab to cycle through applications
# - Check Activity Monitor for the process
# - Try running: open "dist/StockAllocationTool.app"
```

#### "com.apple.installer.pagecontroller error -1" on macOS
```bash
# This error occurs when trying to run .pkg files from build/ directory
# Solution: Run the correct executable from dist/ directory instead

# ❌ Wrong - don't run this:
# build/stock-allocation-tool/StockAllocationTool/StockAllocationTool.pkg

# ✅ Correct - run one of these:
open "dist/StockAllocationTool.app"           # App bundle (recommended)
./dist/StockAllocationTool                   # Standalone executable
```

#### "Module not found" errors
```bash
# Add missing modules to hiddenimports in spec file or use:
pyinstaller --hidden-import missing_module main.py
```

#### "Permission denied" errors
```bash
# On Windows, exclude build directory from antivirus
# On macOS/Linux, check file permissions:
chmod +x build.py
```

#### Large executable size
- Normal for PyInstaller (includes Python runtime)
- Use `--exclude-module` to remove unused dependencies
- Consider using `upx` compression (enabled in spec file)

#### Import errors in built executable
```bash
# Test imports in development first:
python -c "import yfinance; import tkinter; print('All imports OK')"
```

### Build Verification

#### Test the Executable
```bash
# The build script automatically tests the executable
# Manual testing:
cd dist
./Stock\ Allocation\ Tool  # macOS/Linux
# or double-click Stock Allocation Tool.exe on Windows
```

#### Verify Dependencies
```bash
# Check that all required modules are included:
python -c "
import sys
sys.path.insert(0, 'src')
from controllers.portfolio_controller import PortfolioController
print('All dependencies available')
"
```

## Advanced Configuration

### Customizing the Build

#### Modify the Spec File
Edit `stock-allocation-tool.spec` to:
- Add/remove hidden imports
- Include additional data files
- Exclude unnecessary modules
- Configure platform-specific options

#### Environment Variables
```bash
# Enable debug output during build
export PYINSTALLER_DEBUG=1

# Specify build directory
export PYINSTALLER_WORKPATH=/tmp/build
```

### Optimization Tips

#### Reduce Executable Size
1. Exclude unused modules in spec file
2. Use `--exclude-module` for large dependencies
3. Enable UPX compression
4. Remove debug symbols with `--strip`

#### Improve Startup Time
1. Use `--onedir` instead of `--onefile` (faster startup, multiple files)
2. Minimize hidden imports
3. Optimize Python code before building

## Distribution

### Preparing for Distribution

1. **Test thoroughly** on clean systems without Python
2. **Create installer** (optional) using tools like NSIS (Windows) or create-dmg (macOS)
3. **Document system requirements** for end users
4. **Provide troubleshooting guide** for common user issues

### User Instructions

Include these instructions for end users:

#### Windows Users
1. Download `Stock Allocation Tool.exe`
2. Double-click to run (no installation needed)
3. If Windows Defender blocks it, click "More info" → "Run anyway"
4. The application will create data files in the same directory

#### macOS Users
1. Download the application file (`StockAllocationTool.app`)
2. **No installation needed** - you can run it from anywhere (Downloads, Desktop, etc.)
3. **First run only**: Right-click → "Open" → Click "Open" in the security dialog
4. **Optional**: Drag to Applications folder if you want it permanently installed
5. The application will create data files in the same directory where it's located

#### Linux Users
1. Download the application file
2. Make executable: `chmod +x "Stock Allocation Tool"`
3. Run from terminal or file manager
4. Install tkinter if needed: `sudo apt-get install python3-tk`

## Support

### Getting Help

If you encounter build issues:

1. Check this documentation first
2. Verify all prerequisites are installed
3. Try a clean build: `python build.py --clean`
4. Check PyInstaller documentation: https://pyinstaller.readthedocs.io/
5. Review the build script output for specific error messages

### Reporting Issues

When reporting build problems, include:
- Operating system and version
- Python version (`python --version`)
- PyInstaller version (`pyinstaller --version`)
- Complete error output from build script
- Contents of any generated `.spec` files