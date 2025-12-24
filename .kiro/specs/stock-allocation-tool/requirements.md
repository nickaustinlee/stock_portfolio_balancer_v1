# Requirements Document

## Introduction

The Stock Allocation Tool is a portfolio management application that allows users to manage their stock holdings, set target allocations by percentage, and receive rebalancing recommendations. The system integrates with Yahoo Finance API to fetch real-time stock prices while providing manual and optional auto-refresh capabilities to avoid API rate limiting.

## Glossary

- **Portfolio**: A collection of stock holdings owned by the user
- **Holding**: A specific stock position including ticker symbol, quantity, and current value
- **Target_Allocation**: The desired percentage of total portfolio value for each stock
- **Current_Allocation**: The actual percentage of total portfolio value for each stock
- **Rebalance_Action**: The number of shares to buy (positive) or sell (negative) to achieve target allocation
- **Stock_API**: Yahoo Finance API service for retrieving current stock prices
- **Auto_Refresh**: Automated price updates that occur every minute when enabled
- **Share_Rounding_Toggle**: UI control for enabling/disabling whole share rounding in rebalance calculations
- **CSV_Export**: Feature to export current portfolio data to comma-separated values file format
- **Dark_Mode_Toggle**: UI control for switching between light and dark color themes

## Requirements

### Requirement 1: Portfolio Management

**User Story:** As a portfolio manager, I want to add and manage my stock holdings, so that I can track my current positions and make informed rebalancing decisions.

#### Acceptance Criteria

1. WHEN a user adds a new stock holding, THE System SHALL create a new portfolio entry with ticker symbol and quantity
2. WHEN a user modifies the quantity of an existing holding, THE System SHALL update the holding and recalculate all dependent values
3. WHEN a user deletes a holding, THE System SHALL remove it from the portfolio and recalculate remaining allocations
4. THE System SHALL display all holdings in a tabular format with ticker, price, quantity, target allocation, current allocation, current value, target value, difference, and rebalance action columns
5. WHEN portfolio changes are made, THE System SHALL immediately update all calculated fields without requiring a refresh

### Requirement 2: Target Allocation Management

**User Story:** As a portfolio manager, I want to set target allocation percentages for each stock, so that I can define my desired portfolio composition.

#### Acceptance Criteria

1. WHEN a user sets a target allocation percentage for a holding, THE System SHALL store the percentage and recalculate target values
2. THE System SHALL display the sum of all target allocations and indicate if the total is above, below, or equal to 100%
3. WHEN target allocations do not sum to 100%, THE System SHALL continue to function normally without locking the UI
4. WHEN target allocations are modified, THE System SHALL recalculate target values and rebalance actions for all holdings
5. THE System SHALL allow target allocation percentages between 0% and 100% for individual holdings

### Requirement 3: Stock Price Data Integration

**User Story:** As a portfolio manager, I want current stock price data, so that I can see accurate portfolio values and make informed decisions.

#### Acceptance Criteria

1. WHEN the system retrieves stock prices, THE Stock_API SHALL fetch current market prices from Yahoo Finance
2. WHEN a stock price is updated, THE System SHALL recalculate current values, allocations, and rebalance actions
3. WHEN API requests fail, THE System SHALL handle errors gracefully and maintain existing price data
4. THE System SHALL store the last successful price fetch timestamp for each stock
5. WHEN displaying stock data, THE System SHALL show current price information alongside holdings

### Requirement 4: Manual Refresh Functionality

**User Story:** As a portfolio manager, I want to manually refresh stock prices, so that I can get updated values when needed without automatic API calls.

#### Acceptance Criteria

1. WHEN a user clicks the refresh button, THE System SHALL fetch current prices for all holdings from the Stock_API
2. WHEN manual refresh is triggered, THE System SHALL update all price-dependent calculations immediately
3. WHEN refresh is in progress, THE System SHALL provide visual feedback to indicate the operation is running
4. WHEN refresh completes, THE System SHALL display updated values and timestamp of last refresh
5. THE System SHALL allow manual refresh at any time regardless of auto-refresh settings

### Requirement 5: Auto-Refresh Toggle

**User Story:** As a portfolio manager, I want optional automatic price updates, so that I can keep my portfolio current while controlling API usage.

#### Acceptance Criteria

1. THE System SHALL provide a toggle control for enabling/disabling auto-refresh functionality
2. THE System SHALL default auto-refresh to disabled state to prevent excessive API calls
3. WHEN auto-refresh is enabled, THE System SHALL fetch updated prices every 60 seconds
4. WHEN auto-refresh is disabled, THE System SHALL stop automatic price updates immediately
5. WHEN auto-refresh is running, THE System SHALL provide visual indication of the auto-refresh status

### Requirement 6: Rebalance Calculations

**User Story:** As a portfolio manager, I want to see recommended buy/sell actions, so that I can rebalance my portfolio to match target allocations.

#### Acceptance Criteria

1. WHEN target allocations and current prices are available, THE System SHALL calculate the target value for each holding
2. WHEN calculating rebalance actions, THE System SHALL determine the difference between current and target values
3. THE System SHALL convert value differences to share quantities with optional rounding to the nearest whole share
4. THE System SHALL provide a toggle control to enable/disable share rounding in rebalance actions
5. WHEN share rounding is enabled, THE System SHALL display whole share quantities for rebalance actions
6. WHEN share rounding is disabled, THE System SHALL display exact fractional share quantities for rebalance actions
7. THE System SHALL default share rounding to enabled state for user convenience
8. WHEN rebalance action is positive, THE System SHALL indicate shares to buy
9. WHEN rebalance action is negative, THE System SHALL indicate shares to sell
10. WHEN target allocation is zero, THE System SHALL recommend selling all shares of that holding

### Requirement 7: User Interface Responsiveness

**User Story:** As a portfolio manager, I want a responsive interface, so that I can efficiently manage my portfolio without UI delays or lockups.

#### Acceptance Criteria

1. WHEN users modify quantities or allocations, THE System SHALL update calculations in real-time
2. WHEN allocation percentages do not sum to 100%, THE System SHALL continue to allow all UI interactions
3. WHEN API calls are in progress, THE System SHALL maintain UI responsiveness for other operations
4. THE System SHALL provide immediate visual feedback for all user interactions
5. WHEN errors occur, THE System SHALL display error messages without blocking other functionality

### Requirement 8: Error Handling and User Feedback

**User Story:** As a portfolio manager, I want clear error messages when things go wrong, so that I can understand and resolve issues with my portfolio data.

#### Acceptance Criteria

1. WHEN an invalid ticker symbol is entered, THE System SHALL display a dismissible warning message stating "[ticker] not found"
2. WHEN Yahoo Finance API is unavailable or returns errors, THE System SHALL display a dismissible warning message stating "Yahoo Finance isn't working, try again later"
3. WHEN API rate limits are exceeded, THE System SHALL display an appropriate warning and suggest using manual refresh
4. WHEN network connectivity issues occur, THE System SHALL display a clear error message and maintain existing data
5. THE System SHALL allow users to dismiss error messages without affecting portfolio functionality
6. WHEN errors occur during auto-refresh, THE System SHALL log the error but continue normal operation with existing data

### Requirement 10: Dark Mode Theme Support

**User Story:** As a portfolio manager, I want to toggle between light and dark themes, so that I can use the application comfortably in different lighting conditions.

#### Acceptance Criteria

1. THE System SHALL provide a dark mode toggle control in the main interface
2. THE System SHALL default to light mode on first startup
3. WHEN dark mode is enabled, THE System SHALL apply dark color scheme to all UI elements (background, text, table, buttons)
4. WHEN light mode is enabled, THE System SHALL apply light color scheme to all UI elements
5. THE System SHALL persist the user's theme preference across application sessions
6. THE System SHALL maintain readability and contrast in both light and dark modes
7. WHEN theme is changed, THE System SHALL update all visible elements immediately without requiring restart

### Requirement 11: CSV Export Functionality

**User Story:** As a portfolio manager, I want to export my portfolio data to CSV format, so that I can analyze it in spreadsheet applications or keep historical records.

#### Acceptance Criteria

1. THE System SHALL provide an "Export to CSV" button in the main interface
2. WHEN the export button is clicked, THE System SHALL generate a CSV file containing all visible portfolio data
3. THE System SHALL include all table columns in the CSV export (ticker, price, quantity, target allocation, current allocation, current value, target value, difference, rebalance action)
4. THE System SHALL automatically generate timestamped filenames using format "portfolio_YYYY-MM-DD_HH-MM-SS.csv"
5. THE System SHALL save CSV files to a default location and notify the user of the file path
6. WHEN multiple exports are performed, THE System SHALL create separate files without overwriting previous exports
7. THE System SHALL handle file system errors gracefully and notify the user if export fails

### Requirement 12: Data Persistence

**User Story:** As a portfolio manager, I want my portfolio data saved, so that I can resume work without re-entering my holdings.

#### Acceptance Criteria

1. WHEN portfolio changes are made, THE System SHALL persist holdings data locally
2. WHEN the application starts, THE System SHALL load previously saved portfolio data
3. WHEN target allocations are modified, THE System SHALL save the updated allocations
4. THE System SHALL maintain data integrity across application sessions
5. WHEN data corruption is detected, THE System SHALL handle it gracefully and notify the user