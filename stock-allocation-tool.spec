# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Stock Allocation Tool.

This spec file provides advanced configuration for building the standalone executable.
It can be used instead of command-line options for more control over the build process.

Usage:
    pyinstaller stock-allocation-tool.spec
"""

import sys
from pathlib import Path
import os

# Application metadata
APP_NAME = 'StockAllocationTool'
APP_VERSION = '1.0.0'
APP_DESCRIPTION = 'Portfolio management tool with stock price integration'

# Build configuration
block_cipher = None
debug = os.environ.get('PYINSTALLER_DEBUG', '').lower() in ('1', 'true', 'yes')

# Analysis phase - collect all Python files and dependencies
a = Analysis(
    ['main.py'],  # Entry point
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # Include source directory
    ],
    hiddenimports=[
        'yfinance',
        'yfinance.ticker',
        'yfinance.utils',
        'yfinance.scrapers.holders',
        'yfinance.scrapers.quote',
        'numpy',           # Required by yfinance
        'pandas',          # Required by yfinance
        'pandas.core',
        'pandas.core.arrays',
        'pandas.core.arrays.string_',
        'pandas.core.arrays.boolean',
        'pandas.core.arrays.integer',
        'pandas.core.arrays.floating',
        'pandas.core.arrays.categorical',
        'pandas.core.arrays.period',
        'pandas.core.arrays.datetimes',
        'pandas.core.arrays.timedeltas',
        'pandas.core.arrays.interval',
        'pandas.core.arrays.sparse',
        'pandas.core.arrays.numpy_',
        'requests',        # Required by yfinance
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'lxml',           # Required by yfinance for HTML parsing
        'html5lib',
        'bs4',            # BeautifulSoup4 - required by yfinance
        'soupsieve',
        'pytz',           # Timezone handling
        'dateutil',
        'six',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'json',
        'csv',
        'datetime',
        'threading',
        'pathlib',
        'hypothesis',
        'hypothesis.strategies',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Only exclude truly unused heavy dependencies
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],  # Don't bundle everything into one file - use onedir for faster startup
    exclude_binaries=True,  # Keep binaries separate for faster loading
    name=APP_NAME,
    debug=debug,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression for faster startup (trades size for speed)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=debug,  # Show console only in debug mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Create directory distribution (faster startup than onefile)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Disable compression for speed
    upx_exclude=[],
    name=APP_NAME,
)

# Platform-specific configurations
if sys.platform == 'darwin':
    # macOS app bundle - works with onedir distribution
    app = BUNDLE(
        coll,  # Use the COLLECT output instead of exe
        name=f'{APP_NAME}.app',
        icon=None,
        bundle_identifier='com.stocktool.app',
        version=APP_VERSION,
        info_plist={
            'CFBundleDisplayName': 'Stock Allocation Tool',  # Display name can have spaces
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleVersion': APP_VERSION,
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
        },
    )