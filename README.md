# Stock Portfolio Balancer

A desktop application for managing stock portfolios with target allocation percentages and rebalancing recommendations.

![Stock Portfolio Balancer Screenshot](product_screenshot.png)

## Features

- **Portfolio Management**: Add, edit, and remove stock holdings
- **Target Allocations**: Set target allocation percentages for each stock
- **Real-time Calculations**: Automatic calculation of current allocations, target values, and rebalancing actions
- **Stock Price Integration**: Fetch real-time prices from Yahoo Finance API
- **Manual & Auto Refresh**: Manual price refresh with optional 60-second auto-refresh
- **Rebalancing Recommendations**: Buy/sell recommendations with optional share rounding
- **Data Persistence**: Automatic saving and loading of portfolio data
- **CSV Export**: Export portfolio data with timestamped filenames
- **Dark Mode**: Toggle between light and dark themes
- **Error Handling**: Graceful error handling with user-friendly messages

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
- yfinance
- hypothesis (for testing)
- pytest (for testing)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:nickaustinlee/stock_portfolio_balancer_v1.git
cd stock_portfolio_balancer_v1
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

**Debug Mode:**
For troubleshooting and development, enable debug mode for verbose logging:
```bash
# Using command line flag
python src/main.py --debug
# or
python src/main.py -d

# Using environment variable
STOCK_TOOL_DEBUG=1 python src/main.py
```

### Troubleshooting

**If you get a "ModuleNotFoundError: No module named '_tkinter'" error:**

- **macOS**: `brew install python-tk` (if using Homebrew Python)
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Windows**: tkinter should be included with standard Python installation
- **Alternative**: Use the system Python instead of a virtual environment Python

### Basic Workflow

1. **Add Holdings**: Enter ticker symbol and quantity, click "Add"
2. **Set Target Allocations**: Double-click on target allocation cells to edit
3. **Refresh Prices**: Click "Refresh Prices" to get current market prices
4. **View Recommendations**: See buy/sell recommendations in the "Rebalance Action" column
5. **Export Data**: Click "Export to CSV" to save portfolio data

### Controls

- **Refresh Prices**: Manually fetch current stock prices
- **Auto-refresh (60s)**: Enable automatic price updates every 60 seconds
- **Round to whole shares**: Toggle between whole shares and fractional shares in recommendations
- **Dark mode**: Switch between light and dark themes
- **Export to CSV**: Export current portfolio data to timestamped CSV file

### New Features

- **Total Portfolio Value**: Displayed at the bottom of the interface showing the sum of all holdings
- **Column Sorting**: Click any numerical column header to sort (Price, Quantity, Target %, etc.). Click again to reverse sort direction. Headers show ↑/↓ arrows to indicate sort direction
- **Enhanced Input**: Target allocation accepts both "50" and "50%" formats
- **Debug Mode**: Enable verbose logging for troubleshooting with `--debug` flag or `STOCK_TOOL_DEBUG=1` environment variable

## Architecture

The application follows Model-View-Controller (MVC) architecture:

- **Models** (`src/models/`): Portfolio and Holding data models
- **Views** (`src/gui/`): Tkinter-based user interface components
- **Controllers** (`src/controllers/`): Application logic and coordination
- **Services** (`src/services/`): Stock price fetching and data persistence

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

The project includes comprehensive property-based tests using Hypothesis to ensure correctness across a wide range of inputs and edge cases.

## Development

### Project Structure

```
├── src/
│   ├── controllers/          # Application controllers
│   ├── gui/                  # GUI components
│   ├── models/               # Data models
│   ├── services/             # External services
│   └── main.py              # Application entry point
├── tests/                   # Test suite
├── .kiro/specs/            # Feature specifications
└── requirements.txt        # Python dependencies
```

### Specifications

The project was developed using specification-driven development. See `.kiro/specs/stock-allocation-tool/` for:
- `requirements.md`: Detailed requirements using EARS patterns
- `design.md`: System design and architecture
- `tasks.md`: Implementation task breakdown

## License

MIT License - see LICENSE file for details.