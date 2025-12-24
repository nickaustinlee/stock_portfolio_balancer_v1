# Stock Portfolio Balancer

A simple desktop application for managing your stock portfolio with target allocation percentages and automatic rebalancing recommendations.

![Stock Portfolio Balancer Screenshot](product_screenshot.png)

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

## System Requirements

- **Python 3.8 or newer** (most computers have this already)
- **Internet connection** (for fetching stock prices)

## Quick Start

### Step 1: Download
```bash
git clone git@github.com:nickaustinlee/stock_portfolio_balancer_v1.git
cd stock_portfolio_balancer_v1
```

### Step 2: Install
```bash
# Create a clean environment for the app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required components (just one library!)
pip install -r requirements-user.txt
```

### Step 3: Run
```bash
python src/main.py
```

That's it! The app will open and you can start managing your portfolio.

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

**"No module named '_tkinter'" error:**
- **Mac**: `brew install python-tk`
- **Ubuntu/Linux**: `sudo apt-get install python3-tk`  
- **Windows**: Should work automatically with standard Python

**Can't connect to get stock prices:**
- Check your internet connection
- Some corporate networks block financial data - try from home

**App won't start:**
- Make sure you're using Python 3.8 or newer: `python --version`
- Try using `python3` instead of `python`

---

## For Developers

If you want to contribute to this project or run the test suite:

### Development Setup
```bash
# Install all development dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### Debug Mode
For troubleshooting and development:
```bash
python src/main.py --debug
# or
STOCK_TOOL_DEBUG=1 python src/main.py
```

### Project Structure
```
├── src/
│   ├── controllers/          # Application logic
│   ├── gui/                  # User interface
│   ├── models/               # Data models
│   ├── services/             # External services
│   └── main.py              # App entry point
├── tests/                   # Test suite
└── requirements.txt        # All dependencies
```

The project uses comprehensive property-based testing with Hypothesis and follows MVC architecture patterns.

## License

MIT License - see LICENSE file for details.