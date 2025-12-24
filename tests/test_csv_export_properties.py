"""
Property-based tests for CSV export functionality.
Feature: stock-allocation-tool, Property 14: CSV Export Accuracy
"""
import pytest
import csv
import os
import tempfile
from hypothesis import given, strategies as st
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.csv_exporter import CSVExporter
from models.portfolio import Portfolio
from models.holding import Holding


# Strategies for generating test data
ticker_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu',)), 
    min_size=3, 
    max_size=5
)

quantity_strategy = st.floats(
    min_value=0.001, 
    max_value=10000.0, 
    allow_nan=False, 
    allow_infinity=False
)

allocation_strategy = st.floats(
    min_value=0.0, 
    max_value=100.0, 
    allow_nan=False, 
    allow_infinity=False
)

price_strategy = st.floats(
    min_value=0.01, 
    max_value=10000.0, 
    allow_nan=False, 
    allow_infinity=False
)

holdings_strategy = st.lists(
    st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
    min_size=1,
    max_size=10,
    unique_by=lambda x: x[0].upper()  # Ensure unique tickers
)


@given(
    holdings_data=holdings_strategy,
    share_rounding=st.booleans()
)
def test_csv_export_accuracy_round_trip(holdings_data, share_rounding):
    """
    Property 14: CSV Export Accuracy
    For any portfolio state, exporting to CSV and parsing the resulting file should 
    contain all visible table data with correct formatting and no data loss.
    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    # Create portfolio with test data
    portfolio = Portfolio()
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.current_price = price
        holding.last_updated = None  # Set to None for consistent testing
        portfolio.add_holding(holding)
    
    # Create CSV exporter with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        exporter = CSVExporter(temp_dir)
        
        # Export portfolio to CSV
        filepath = exporter.export_portfolio(portfolio, share_rounding)
        
        # Verify file was created
        assert os.path.exists(filepath)
        assert filepath.endswith('.csv')
        
        # Read and parse the CSV file
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
        
        # Verify structure (Requirements 11.2, 11.3)
        assert len(rows) >= 1  # At least header row
        assert len(rows) == len(holdings_data) + 1  # Header + data rows
        
        # Verify header row contains all expected columns (Requirement 11.3)
        expected_headers = [
            "Ticker", "Price", "Quantity", "Target Allocation", 
            "Current Allocation", "Current Value", "Target Value", 
            "Difference", "Rebalance Action"
        ]
        assert rows[0] == expected_headers
        
        # Verify data accuracy by comparing with original portfolio data (Requirement 11.4)
        total_value = portfolio.get_total_value()
        allocations = portfolio.get_allocation_summary()
        rebalance_actions = portfolio.calculate_rebalance_actions(share_rounding)
        
        # Check each data row
        for i, (ticker, quantity, target_allocation, price) in enumerate(holdings_data, 1):
            row = rows[i]
            
            # Verify ticker
            assert row[0] == ticker.upper()
            
            # Verify price (formatted as currency)
            expected_price = f"${price:.2f}"
            assert row[1] == expected_price
            
            # Verify quantity (formatted to 3 decimal places)
            expected_quantity = f"{quantity:.3f}"
            assert row[2] == expected_quantity
            
            # Verify target allocation (formatted as percentage)
            expected_target_allocation = f"{target_allocation:.1f}%"
            assert row[3] == expected_target_allocation
            
            # Verify current allocation (calculated and formatted as percentage)
            current_allocation = allocations.get(ticker.upper(), 0.0)
            expected_current_allocation = f"{current_allocation:.1f}%"
            assert row[4] == expected_current_allocation
            
            # Verify current value (calculated and formatted as currency)
            current_value = quantity * price
            expected_current_value = f"${current_value:.2f}"
            assert row[5] == expected_current_value
            
            # Verify target value (calculated and formatted as currency)
            target_value = (target_allocation / 100) * total_value
            expected_target_value = f"${target_value:.2f}"
            assert row[6] == expected_target_value
            
            # Verify difference (calculated and formatted as currency)
            difference = target_value - current_value
            expected_difference = f"${difference:.2f}"
            assert row[7] == expected_difference
            
            # Verify rebalance action (calculated and formatted)
            rebalance_action = rebalance_actions.get(ticker.upper(), 0.0)
            if rebalance_action > 0:
                expected_rebalance = f"Buy {rebalance_action:.3f}"
            elif rebalance_action < 0:
                expected_rebalance = f"Sell {abs(rebalance_action):.3f}"
            else:
                expected_rebalance = "Hold"
            assert row[8] == expected_rebalance


@given(
    holdings_data=holdings_strategy
)
def test_csv_export_filename_generation(holdings_data):
    """
    Property 14: CSV Export Accuracy - Filename generation
    Test that CSV export generates proper timestamped filenames.
    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    # Create portfolio with test data
    portfolio = Portfolio()
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.current_price = price
        portfolio.add_holding(holding)
    
    # Create CSV exporter with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        exporter = CSVExporter(temp_dir)
        
        # Test filename generation
        filename = exporter.generate_filename()
        assert filename.startswith("portfolio_")
        assert filename.endswith(".csv")
        assert len(filename) == len("portfolio_YYYY-MM-DD_HH-MM-SS.csv")
        
        # Export portfolio and verify filename format
        filepath = exporter.export_portfolio(portfolio, True)
        actual_filename = os.path.basename(filepath)
        assert actual_filename.startswith("portfolio_")
        assert actual_filename.endswith(".csv")


@given(
    holdings_data=holdings_strategy
)
def test_csv_export_data_formatting_consistency(holdings_data):
    """
    Property 14: CSV Export Accuracy - Data formatting consistency
    Test that CSV export formats data consistently across different portfolio states.
    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    # Create portfolio with test data
    portfolio = Portfolio()
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.current_price = price
        portfolio.add_holding(holding)
    
    # Create CSV exporter
    exporter = CSVExporter()
    
    # Test data formatting without file I/O
    formatted_data = exporter.format_portfolio_data(portfolio, True)
    
    # Verify header consistency
    assert len(formatted_data) >= 1
    headers = formatted_data[0]
    expected_headers = [
        "Ticker", "Price", "Quantity", "Target Allocation", 
        "Current Allocation", "Current Value", "Target Value", 
        "Difference", "Rebalance Action"
    ]
    assert headers == expected_headers
    
    # Verify data row consistency
    assert len(formatted_data) == len(holdings_data) + 1  # Header + data rows
    
    for i, (ticker, quantity, target_allocation, price) in enumerate(holdings_data, 1):
        row = formatted_data[i]
        assert len(row) == len(headers)  # Same number of columns
        
        # Verify data types and formatting
        assert isinstance(row[0], str)  # Ticker
        assert row[1].startswith('$')   # Price formatted as currency
        assert '.' in row[2]            # Quantity has decimal places
        assert row[3].endswith('%')     # Target allocation as percentage
        assert row[4].endswith('%')     # Current allocation as percentage
        assert row[5].startswith('$')   # Current value as currency
        assert row[6].startswith('$')   # Target value as currency
        assert row[7].startswith('$') or row[7].startswith('-$')  # Difference as currency
        assert row[8] in ['Hold'] or row[8].startswith('Buy ') or row[8].startswith('Sell ')  # Rebalance action


@given(
    share_rounding=st.booleans()
)
def test_csv_export_empty_portfolio_handling(share_rounding):
    """
    Property 14: CSV Export Accuracy - Empty portfolio handling
    Test that CSV export properly handles empty portfolios.
    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    portfolio = Portfolio()
    exporter = CSVExporter()
    
    # Test that empty portfolio raises appropriate error
    with pytest.raises(ValueError, match="Cannot export empty portfolio"):
        exporter.export_portfolio(portfolio, share_rounding)
    
    # Test that format_portfolio_data returns empty list for empty portfolio
    formatted_data = exporter.format_portfolio_data(portfolio, share_rounding)
    assert formatted_data == []


@given(
    holdings_data=holdings_strategy
)
def test_csv_export_share_rounding_consistency(holdings_data):
    """
    Property 14: CSV Export Accuracy - Share rounding consistency
    Test that CSV export respects the share rounding setting consistently.
    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    # Create portfolio with test data
    portfolio = Portfolio()
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.current_price = price
        portfolio.add_holding(holding)
    
    exporter = CSVExporter()
    
    # Test with rounding enabled
    data_rounded = exporter.format_portfolio_data(portfolio, True)
    
    # Test with rounding disabled
    data_exact = exporter.format_portfolio_data(portfolio, False)
    
    # Both should have same structure
    assert len(data_rounded) == len(data_exact)
    assert data_rounded[0] == data_exact[0]  # Same headers
    
    # Compare rebalance actions (last column) for rounding differences
    for i in range(1, len(data_rounded)):
        rounded_action = data_rounded[i][8]  # Rebalance action column
        exact_action = data_exact[i][8]
        
        # Both should be valid rebalance action formats
        assert rounded_action in ['Hold'] or rounded_action.startswith('Buy ') or rounded_action.startswith('Sell ')
        assert exact_action in ['Hold'] or exact_action.startswith('Buy ') or exact_action.startswith('Sell ')
        
        # If not "Hold", the rounding setting should affect the precision
        if rounded_action != 'Hold' and exact_action != 'Hold':
            # Extract numeric values for comparison
            if rounded_action.startswith('Buy '):
                rounded_value = float(rounded_action.split()[1])
            else:  # Sell
                rounded_value = float(rounded_action.split()[1])
                
            if exact_action.startswith('Buy '):
                exact_value = float(exact_action.split()[1])
            else:  # Sell
                exact_value = float(exact_action.split()[1])
            
            # Rounded value should be close to exact value
            assert abs(rounded_value - exact_value) <= 0.5  # At most 0.5 difference due to rounding


def test_csv_export_file_system_error_handling():
    """
    Property 14: CSV Export Accuracy - File system error handling
    Test that CSV export properly handles file system errors.
    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    portfolio = Portfolio()
    holding = Holding("AAPL", 10.0, 50.0)
    holding.current_price = 150.0
    portfolio.add_holding(holding)
    
    # Test with invalid directory path
    exporter = CSVExporter("/invalid/path/that/does/not/exist")
    
    with pytest.raises(OSError):
        exporter.export_portfolio(portfolio, True)
    
    # Test write_csv_file with invalid path
    with pytest.raises(OSError):
        exporter.write_csv_file("/invalid/path/test.csv", [["header"], ["data"]])