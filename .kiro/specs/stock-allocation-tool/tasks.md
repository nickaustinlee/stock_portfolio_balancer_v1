# Implementation Plan: Stock Allocation Tool

## Overview

This implementation plan converts the stock allocation tool design into discrete coding tasks. The approach follows an incremental development strategy, building core functionality first, then adding UI components, API integration, and finally advanced features like auto-refresh and error handling. Each task builds on previous work to ensure a working application at each checkpoint.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create Python project directory structure
  - Set up virtual environment and dependencies (yfinance, tkinter)
  - Implement Holding class with basic properties and calculations
  - Implement Portfolio class with holdings management
  - _Requirements: 1.1, 1.2, 1.3, 9.4_

- [x] 1.1 Write property test for portfolio state management
  - **Property 1: Portfolio State Management**
  - **Validates: Requirements 1.1, 1.2, 1.3**

- [x] 2. Implement core calculation engine
  - [x] 2.1 Add calculation methods to Holding class
    - Implement current_value, current_allocation, target_value calculations
    - Add rebalance_action calculation with optional rounding parameter
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 2.2 Write property test for rebalance calculation accuracy
    - **Property 9: Rebalance Calculation Accuracy**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

  - [x] 2.3 Add portfolio-level calculations
    - Implement total_value and allocation_summary methods
    - Add validation for target allocation ranges
    - _Requirements: 2.1, 2.2, 2.5_

  - [x] 2.4 Write property test for target allocation management
    - **Property 3: Target Allocation Management**
    - **Validates: Requirements 2.1, 2.2, 2.5**

- [x] 3. Create stock price service
  - [x] 3.1 Implement StockPriceService class
    - Create yfinance integration for single and multiple ticker requests
    - Add ticker validation and price caching
    - Implement error handling for invalid tickers and API failures
    - _Requirements: 3.1, 3.4, 8.1, 8.2_

  - [x] 3.2 Write property test for stock price integration
    - **Property 5: Stock Price Integration**
    - **Validates: Requirements 3.1, 3.2**

  - [x] 3.3 Write property test for error handling with graceful degradation
    - **Property 11: Error Handling with Graceful Degradation**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**

- [x] 4. Implement data persistence layer
  - [x] 4.1 Create DataStorage class
    - Implement JSON serialization and deserialization for Portfolio objects
    - Add file I/O with error handling for corruption and permissions
    - Create backup and recovery mechanisms
    - _Requirements: 9.1, 9.2, 9.3, 9.5_

  - [x] 4.2 Write property test for data persistence round-trip
    - **Property 12: Data Persistence Round-trip**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**

  - [x] 4.3 Write property test for data corruption recovery
    - **Property 15: Data Corruption Recovery**
    - **Validates: Requirements 12.5**

- [x] 5. Checkpoint - Core functionality complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Build basic GUI components
  - [x] 6.1 Create MainWindow class
    - Set up main Tkinter window with menu and layout
    - Add refresh button, auto-refresh toggle, share rounding toggle, dark mode toggle, and CSV export button
    - Create placeholder for portfolio table
    - _Requirements: 4.1, 5.1, 5.2, 6.6, 6.7, 10.1, 11.1_

  - [x] 6.2 Implement PortfolioTable widget
    - Create custom table widget for displaying portfolio data
    - Add columns in order: Ticker, Price, Quantity, Target Allocation, Current Allocation, Current Value, Target Value, Difference, Rebalance Action
    - Implement inline editing for quantities and target allocations
    - _Requirements: 1.4, 2.1_

  - [x] 6.3 Write property test for real-time calculation updates
    - **Property 2: Real-time Calculation Updates**
    - **Validates: Requirements 1.5, 2.4, 4.2, 7.1**

- [x] 7. Create application controller
  - [x] 7.1 Implement PortfolioController class
    - Connect GUI components to data models
    - Handle user input events (add, edit, delete holdings)
    - Implement manual refresh functionality, share rounding toggle, dark mode toggle, and CSV export
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.2, 6.6, 6.7, 10.3, 10.4, 10.7, 11.2, 11.4, 11.5_

  - [x] 7.2 Add real-time calculation updates
    - Connect model changes to GUI updates
    - Ensure calculations update immediately on data changes
    - _Requirements: 1.5, 7.1_

  - [x] 7.3 Write property test for UI functionality during invalid states
    - **Property 4: UI Functionality During Invalid States**
    - **Validates: Requirements 2.3, 7.2, 7.5**

- [x] 8. Implement error handling and user feedback
  - [x] 8.1 Create ErrorDialog class
    - Implement dismissible error message dialogs
    - Add different error types with appropriate messaging
    - Ensure errors don't block other functionality
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 8.2 Integrate error handling throughout application
    - Add try-catch blocks around API calls and file operations
    - Connect error conditions to user-friendly messages
    - Implement graceful degradation for various error scenarios
    - _Requirements: 3.3, 8.6_

- [x] 9. Add auto-refresh functionality
  - [x] 9.1 Implement auto-refresh timer system
    - Create background timer for 60-second price updates
    - Add toggle functionality to enable/disable auto-refresh
    - Ensure auto-refresh defaults to disabled
    - _Requirements: 5.2, 5.3, 5.4_

  - [x] 9.2 Write property test for auto-refresh state management
    - **Property 8: Auto-refresh State Management**
    - **Validates: Requirements 5.4**

  - [x] 9.3 Write property test for manual refresh functionality
    - **Property 7: Manual Refresh Functionality**
    - **Validates: Requirements 4.1, 4.4, 4.5**

- [x] 10. Add dark mode theme support
  - [x] 10.1 Implement ThemeManager class
    - Create theme management service with light and dark color schemes
    - Add methods for applying themes to UI elements and persisting preferences
    - Implement immediate theme switching without restart
    - _Requirements: 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [x] 10.2 Write property test for dark mode theme consistency
    - **Property 13: Dark Mode Theme Consistency**
    - **Validates: Requirements 10.3, 10.4, 10.6, 10.7**

- [x] 11. Add CSV export functionality
  - [x] 11.1 Implement CSVExporter class
    - Create CSV export service with timestamped filename generation
    - Add methods for formatting portfolio data and writing CSV files
    - Implement error handling for file system issues
    - _Requirements: 11.2, 11.3, 11.4, 11.6, 11.7_

  - [x] 11.2 Write property test for CSV export accuracy
    - **Property 14: CSV Export Accuracy**
    - **Validates: Requirements 11.2, 11.3, 11.4**

- [x] 12. Final integration and polish
  - [x] 12.1 Wire all components together
    - Connect controller to GUI, data models, and services
    - Implement application startup and shutdown procedures
    - Add data loading on startup and saving on changes
    - _Requirements: 12.2, 1.5_

  - [x] 12.2 Add visual feedback and status indicators
    - Implement loading indicators for refresh operations
    - Add status bar with last refresh timestamp
    - Show allocation total and over/under 100% indicators
    - _Requirements: 4.3, 4.4, 2.2_

  - [x] 12.3 Write property test for price data persistence and display
    - **Property 6: Price Data Persistence and Display**
    - **Validates: Requirements 3.4, 3.5**

  - [x] 12.4 Write property test for rebalance action direction and rounding
    - **Property 10: Rebalance Action Direction and Rounding**
    - **Validates: Requirements 6.6, 6.7, 6.8, 6.9, 6.10**

- [x] 13. Add application packaging support
  - [x] 13.1 Create main.py entry point
    - Create standalone entry point for the application
    - Add proper path handling for packaged execution
    - Ensure all imports work correctly when packaged
    - _Requirements: Application packaging support_

  - [x] 13.2 Add PyInstaller configuration
    - Create build script for creating standalone executable
    - Add requirements.txt for packaging dependencies
    - Create build instructions and documentation
    - Test executable creation and functionality
    - _Requirements: Application packaging support_

- [x] 14. Final checkpoint - Complete application
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive validation from the start
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and working software at each stage
- Property tests validate universal correctness properties using Hypothesis framework
- Unit tests validate specific examples and edge cases
- The implementation follows MVC architecture with clear separation of concerns