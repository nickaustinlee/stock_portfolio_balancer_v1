# Stock Portfolio Balancer

A professional desktop application for managing your stock portfolio with target allocation percentages and automatic rebalancing recommendations. Available as both a Python application and standalone executable.

![Stock Portfolio Balancer Screenshot](./docs/product_screenshot.png)

## What It Does

This app helps you maintain your desired stock portfolio allocation by:
- Tracking your current stock holdings and their values
- Letting you set target allocation percentages for each stock
- Showing you exactly how many shares to buy or sell to reach your targets
- Fetching real-time stock prices automatically
- Exporting your portfolio data to spreadsheets

## Key Features

- **Easy Portfolio Management**: Add stocks by ticker symbol, enter your share quantities
- **Target Allocations**: Set what percentage of your portfolio each stock should represent
- **Smart Rebalancing**: Get precise buy/sell recommendations to reach your target allocations
- **Live Stock Prices**: Automatic price updates from Yahoo Finance
- **Auto-Refresh**: Optional 60-second price updates to keep data current
- **Portfolio Sorting**: Click column headers to sort by price, quantity, allocation, etc.
- **Total Value Display**: See your complete portfolio value at a glance
- **Data Export**: Save your portfolio to CSV files for spreadsheet analysis
- **Dark Mode**: Easy on the eyes with a sleek dark interface (default)
- **Data Persistence**: Your portfolio is automatically saved and restored
- **Professional Packaging**: Available as standalone executable (no Python required)

## System Requirements

### For Python Version
- **Python 3.8 or newer**
- **Internet connection** (for fetching stock prices)

### For Standalone Binary
- **Python only needed to build the binary**
- **End users need no Python installation**

## Installation & Usage

You have **two options** for running this application:

### Option 1: Python Application (Recommended for Development)

**Quick and easy - runs directly from source code**

#### Step 1: Download
```bash
git clone git@github.com:nickaustinlee/stock_portfolio_balancer_v1.git
cd stock_portfolio_balancer_v1
```

#### Step 2: Install Dependencies
```bash
# Create a clean environment for the app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required components
pip install -r requirements-user.txt
```

#### Step 3: Run
```bash
python src/main.py
```

**Advantages:**
- ⚡ Fast startup (no extraction overhead)
- 🔧 Easy to modify and customize
- 🐛 Better for debugging and development
- 📦 Smaller download size

### Option 2: Standalone Binary (Recommended for End Users)

**Self-contained executable - Python only needed to build**

#### Step 1: Download Source
```bash
git clone git@github.com:nickaustinlee/stock_portfolio_balancer_v1.git
cd stock_portfolio_balancer_v1
```

#### Step 2: Build Binary
```bash
# Automated setup (creates virtual environment and installs dependencies)
python packaging/setup_build_env.py

# Activate the build environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Build the standalone binary
python packaging/build.py
```

#### Step 3: Run the Binary
**macOS:**
```bash
# Double-click the binary (recommended)
open dist/StockAllocationTool.app

# Or run from terminal
./dist/StockAllocationTool/StockAllocationTool
```

**Windows:**
```bash
# Double-click the executable
dist\StockAllocationTool\StockAllocationTool.exe
```

**Linux:**
```bash
# Run the binary
./dist/StockAllocationTool/StockAllocationTool
```

**Advantages:**
- 🎨 Professional splash screen with loading animation
- 📱 No Python installation required for end users
- 🚀 Easy distribution to non-technical users
- 💼 Professional user experience

#### Build Documentation
For detailed build instructions, troubleshooting, and distribution guidance, see:
- **[packaging/BUILD.md](packaging/BUILD.md)** - Comprehensive build instructions
- **[packaging/PACKAGING.md](packaging/PACKAGING.md)** - Distribution and packaging summary

## How to Use

### Getting Started
1. **Add Your Stocks**: 
   - Enter a stock ticker (like AAPL, GOOGL, TSLA) 
   - Enter how many shares you own
   - Click "Add"

2. **Set Your Targets**: 
   - Double-click the "Target %" column for each stock
   - Enter what percentage of your portfolio it should be (like 25 for 25%)

3. **Get Recommendations**: 
   - Click "Refresh Prices" to get current stock prices
   - Look at the "Rebalance Action" column to see what to buy or sell

4. **Stay Updated**: 
   - Turn on "Auto-refresh (60s)" to keep prices current
   - Your portfolio value updates automatically

### Pro Tips
- **Sorting**: Click any column header to sort your stocks by that value
- **Exporting**: Use "Export to CSV" to analyze your data in Excel or Google Sheets
- **Themes**: Toggle between dark and light mode in the menu
- **Whole Shares**: Check "Round to whole shares" if you can't buy fractional shares

## Troubleshooting

### Python Version Issues
**"No module named '_tkinter'" error:**
- **Mac**: `brew install python-tk`
- **Ubuntu/Linux**: `sudo apt-get install python3-tk`  
- **Windows**: Should work automatically with standard Python

**App won't start:**
- Make sure you're using Python 3.8 or newer: `python --version`
- Try using `python3` instead of `python`

### Standalone Binary Issues
**macOS: "Binary can't be opened" security warning:**
- Right-click the binary → "Open" → Click "Open" in the dialog
- Or run: `xattr -d com.apple.quarantine StockAllocationTool.app`

**Windows: Antivirus blocking the binary:**
- This is common with PyInstaller binaries - add an exception for the executable
- The binary is safe - it's just not code-signed

**Slow startup on first run:**
- The standalone binary extracts dependencies on first run
- Subsequent runs will be faster

### Network Issues
**Can't connect to get stock prices:**
- Check your internet connection
- Some corporate networks block financial data - try from home

## Future Features

The following features are being considered for future releases:

- **📁 Multiple Portfolio Files**: Open and manage different portfolio JSON files
- **💾 File System Integration**: Native file dialogs for opening/saving portfolios
- **📊 Portfolio Comparison**: Compare performance across different portfolio files
- **🔄 Portfolio Templates**: Save and reuse allocation strategies
- **📈 Historical Tracking**: Track portfolio performance over time

## For Developers

### Development Setup
```bash
# Install all development dependencies (includes testing frameworks)
pip install -r requirements.txt
```

### Running Tests
```bash
# Run the complete test suite (78 tests)
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_portfolio_properties.py -v
```

### Debug Mode
For troubleshooting and development:
```bash
# Python version
python src/main.py --debug
# or
STOCK_TOOL_DEBUG=1 python src/main.py

# Standalone version (shows debug info in Console.app on macOS)
STOCK_TOOL_DEBUG=1 open dist/StockAllocationTool.app
```

### Build System
The project includes a comprehensive build system:

```bash
# Automated environment setup
python packaging/setup_build_env.py

# Build with verification
python packaging/build.py

# Test build configuration
python packaging/test_build_config.py

# Verify complete build
python packaging/verify_build_complete.py
```

### Project Structure
```
├── src/
│   ├── controllers/          # Application logic
│   ├── gui/                  # User interface components
│   │   └── splash_screen.py  # Professional loading screen
│   ├── models/               # Data models (Portfolio, Holding)
│   ├── services/             # External services (stock prices, storage)
│   └── main.py              # Development entry point
├── tests/                   # Comprehensive test suite (78 tests)
├── packaging/               # Build system and packaging
│   ├── build.py             # Automated build script
│   ├── setup_build_env.py   # Environment setup
│   ├── stock-allocation-tool.spec # PyInstaller configuration
│   ├── BUILD.md             # Detailed build instructions
│   └── PACKAGING.md         # Distribution guide
├── docs/                    # Documentation and assets
│   ├── product_screenshot.png
│   └── stock_tool.drawio.png
└── requirements.txt         # All dependencies
```

### Architecture
- **MVC Pattern**: Clean separation of concerns
- **Property-Based Testing**: Comprehensive validation using Hypothesis
- **Threaded UI**: Responsive interface during heavy operations
- **Cross-Platform**: Works on macOS, Windows, and Linux
- **Professional Packaging**: PyInstaller with optimized startup performance

## License

MIT License - see LICENSE file for details.

---

**Choose your preferred way to run the app and start managing your portfolio today!**