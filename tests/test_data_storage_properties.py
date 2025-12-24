"""
Property-based tests for data persistence functionality.
Feature: stock-allocation-tool, Property 12: Data Persistence Round-trip
"""
import pytest
import os
import tempfile
import json
from datetime import datetime
from hypothesis import given, strategies as st
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.portfolio import Portfolio
from models.holding import Holding
from services.data_storage import DataStorage


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

# Strategy for generating portfolios with multiple holdings
portfolio_strategy = st.lists(
    st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
    min_size=0,
    max_size=10,
    unique_by=lambda x: x[0].upper()  # Ensure unique tickers
)


@given(portfolio_data=portfolio_strategy)
def test_data_persistence_round_trip(portfolio_data):
    """
    Property 12: Data Persistence Round-trip
    For any portfolio state, saving and then loading the portfolio should result in 
    identical data (holdings, quantities, allocations, and last known prices).
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Create original portfolio
        original_portfolio = Portfolio()
        
        # Add holdings to portfolio
        for ticker, quantity, target_allocation, price in portfolio_data:
            holding = Holding(ticker, quantity, target_allocation)
            holding.update_price(price)
            original_portfolio.add_holding(holding)
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Save portfolio (Requirement 9.1)
        storage.save_portfolio(original_portfolio)
        
        # Load portfolio (Requirement 9.2)
        loaded_portfolio = storage.load_portfolio()
        
        # Verify round-trip consistency (Requirements 9.3, 9.4)
        
        # Check portfolio structure
        assert len(loaded_portfolio) == len(original_portfolio)
        assert loaded_portfolio.get_all_tickers() == original_portfolio.get_all_tickers()
        
        # Check each holding's data integrity
        for ticker in original_portfolio.get_all_tickers():
            original_holding = original_portfolio.get_holding(ticker)
            loaded_holding = loaded_portfolio.get_holding(ticker)
            
            assert loaded_holding is not None
            assert loaded_holding.ticker == original_holding.ticker
            assert loaded_holding.quantity == original_holding.quantity
            assert loaded_holding.target_allocation == original_holding.target_allocation
            assert loaded_holding.current_price == original_holding.current_price
            
            # Check timestamp preservation (if it was set)
            if original_holding.last_updated is not None:
                assert loaded_holding.last_updated is not None
                # Allow for small differences due to serialization precision
                time_diff = abs((loaded_holding.last_updated - original_holding.last_updated).total_seconds())
                assert time_diff < 1.0  # Within 1 second
        
        # Check portfolio-level calculations remain consistent
        assert abs(loaded_portfolio.get_total_value() - original_portfolio.get_total_value()) < 0.01
        assert abs(loaded_portfolio.get_target_allocation_total() - original_portfolio.get_target_allocation_total()) < 0.01
        assert loaded_portfolio.get_allocation_status() == original_portfolio.get_allocation_status()
        
        # Check allocation summaries match
        original_allocations = original_portfolio.get_allocation_summary()
        loaded_allocations = loaded_portfolio.get_allocation_summary()
        
        for ticker in original_allocations:
            assert ticker in loaded_allocations
            assert abs(loaded_allocations[ticker] - original_allocations[ticker]) < 0.01
        
        # Check rebalance actions match
        original_rebalance = original_portfolio.calculate_rebalance_actions(rounded=True)
        loaded_rebalance = loaded_portfolio.calculate_rebalance_actions(rounded=True)
        
        for ticker in original_rebalance:
            assert ticker in loaded_rebalance
            assert loaded_rebalance[ticker] == original_rebalance[ticker]
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        backup_filename = f"{temp_filename}.backup"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy
)
def test_single_holding_persistence_round_trip(ticker, quantity, target_allocation, price):
    """
    Property 12: Data Persistence Round-trip - Single holding case
    Test round-trip persistence with a single holding to ensure basic functionality.
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Create original portfolio with single holding
        original_portfolio = Portfolio()
        holding = Holding(ticker, quantity, target_allocation)
        holding.update_price(price)
        original_portfolio.add_holding(holding)
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Save and load portfolio
        storage.save_portfolio(original_portfolio)
        loaded_portfolio = storage.load_portfolio()
        
        # Verify single holding round-trip
        assert len(loaded_portfolio) == 1
        
        loaded_holding = loaded_portfolio.get_holding(ticker)
        assert loaded_holding is not None
        assert loaded_holding.ticker == ticker.upper()
        assert loaded_holding.quantity == quantity
        assert loaded_holding.target_allocation == target_allocation
        assert loaded_holding.current_price == price
        assert loaded_holding.last_updated is not None
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        backup_filename = f"{temp_filename}.backup"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)


def test_empty_portfolio_persistence_round_trip():
    """
    Property 12: Data Persistence Round-trip - Empty portfolio case
    Test round-trip persistence with an empty portfolio.
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Create empty portfolio
        original_portfolio = Portfolio()
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Save and load empty portfolio
        storage.save_portfolio(original_portfolio)
        loaded_portfolio = storage.load_portfolio()
        
        # Verify empty portfolio round-trip
        assert len(loaded_portfolio) == 0
        assert loaded_portfolio.is_empty()
        assert loaded_portfolio.get_total_value() == 0.0
        assert loaded_portfolio.get_target_allocation_total() == 0.0
        assert loaded_portfolio.get_allocation_status() == "below"
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        backup_filename = f"{temp_filename}.backup"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)


def test_nonexistent_file_loads_empty_portfolio():
    """
    Property 12: Data Persistence Round-trip - Nonexistent file case
    Test that loading from a nonexistent file returns an empty portfolio.
    **Validates: Requirements 9.2**
    """
    # Use a filename that doesn't exist
    nonexistent_filename = "nonexistent_portfolio_test.json"
    
    # Ensure file doesn't exist
    if os.path.exists(nonexistent_filename):
        os.remove(nonexistent_filename)
    
    try:
        # Create data storage instance
        storage = DataStorage(nonexistent_filename)
        
        # Load from nonexistent file should return empty portfolio
        loaded_portfolio = storage.load_portfolio()
        
        # Verify empty portfolio is returned
        assert len(loaded_portfolio) == 0
        assert loaded_portfolio.is_empty()
        assert loaded_portfolio.get_total_value() == 0.0
        assert loaded_portfolio.get_target_allocation_total() == 0.0
    
    finally:
        # Clean up in case file was created
        if os.path.exists(nonexistent_filename):
            os.remove(nonexistent_filename)
        backup_filename = f"{nonexistent_filename}.backup"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)


@given(portfolio_data=portfolio_strategy)
def test_multiple_save_load_cycles(portfolio_data):
    """
    Property 12: Data Persistence Round-trip - Multiple cycles
    Test that multiple save/load cycles maintain data integrity.
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Create original portfolio
        original_portfolio = Portfolio()
        
        # Add holdings to portfolio
        for ticker, quantity, target_allocation, price in portfolio_data:
            holding = Holding(ticker, quantity, target_allocation)
            holding.update_price(price)
            original_portfolio.add_holding(holding)
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Perform multiple save/load cycles
        current_portfolio = original_portfolio
        for cycle in range(3):  # Test 3 cycles
            # Save current portfolio
            storage.save_portfolio(current_portfolio)
            
            # Load portfolio
            loaded_portfolio = storage.load_portfolio()
            
            # Verify consistency after each cycle
            assert len(loaded_portfolio) == len(original_portfolio)
            assert loaded_portfolio.get_all_tickers() == original_portfolio.get_all_tickers()
            
            # Check that values remain consistent across cycles
            assert abs(loaded_portfolio.get_total_value() - original_portfolio.get_total_value()) < 0.01
            assert abs(loaded_portfolio.get_target_allocation_total() - original_portfolio.get_target_allocation_total()) < 0.01
            
            # Use loaded portfolio for next cycle
            current_portfolio = loaded_portfolio
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        backup_filename = f"{temp_filename}.backup"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)


def test_file_metadata_preservation():
    """
    Property 12: Data Persistence Round-trip - Metadata preservation
    Test that file metadata like version and timestamps are properly handled.
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Create portfolio with holding
        portfolio = Portfolio()
        holding = Holding("AAPL", 10.0, 50.0)
        holding.update_price(150.0)
        portfolio.add_holding(holding)
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Save portfolio
        storage.save_portfolio(portfolio)
        
        # Verify file was created and has content
        assert storage.file_exists()
        assert storage.get_file_size() > 0
        assert storage.get_last_modified() is not None
        
        # Read raw JSON to verify structure
        with open(temp_filename, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Verify JSON structure includes metadata
        assert "version" in raw_data
        assert "last_saved" in raw_data
        assert "holdings" in raw_data
        assert raw_data["version"] == "1.0"
        
        # Verify holdings data structure
        assert len(raw_data["holdings"]) == 1
        holding_data = raw_data["holdings"][0]
        assert holding_data["ticker"] == "AAPL"
        assert holding_data["quantity"] == 10.0
        assert holding_data["target_allocation"] == 50.0
        assert holding_data["last_price"] == 150.0
        assert holding_data["last_updated"] is not None
        
        # Load and verify data integrity is maintained
        loaded_portfolio = storage.load_portfolio()
        assert len(loaded_portfolio) == 1
        loaded_holding = loaded_portfolio.get_holding("AAPL")
        assert loaded_holding is not None
        assert loaded_holding.ticker == "AAPL"
        assert loaded_holding.quantity == 10.0
        assert loaded_holding.target_allocation == 50.0
        assert loaded_holding.current_price == 150.0
        assert loaded_holding.last_updated is not None
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        backup_filename = f"{temp_filename}.backup"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)


@given(portfolio_data=st.lists(
    st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
    min_size=1,  # Ensure at least one holding for meaningful backup
    max_size=10,
    unique_by=lambda x: x[0].upper()
))
def test_data_corruption_recovery_with_backup(portfolio_data):
    """
    Property 15: Data Corruption Recovery - With valid backup
    Test corruption recovery when a valid backup exists.
    **Validates: Requirements 12.5**
    """
    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    backup_filename = f"{temp_filename}.backup"
    
    try:
        # Create original portfolio with at least one holding
        original_portfolio = Portfolio()
        
        # Add holdings to portfolio
        for ticker, quantity, target_allocation, price in portfolio_data:
            holding = Holding(ticker, quantity, target_allocation)
            holding.update_price(price)
            original_portfolio.add_holding(holding)
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Save portfolio first time (no backup created yet)
        storage.save_portfolio(original_portfolio)
        
        # Save portfolio second time (this creates backup from first save)
        storage.save_portfolio(original_portfolio)
        
        # Now we should have both main file and backup file
        assert storage.file_exists()
        assert storage.backup_exists()
        
        # Test Case 1: Corrupted main file with valid backup
        # Corrupt the main file with invalid JSON
        with open(temp_filename, 'w') as f:
            f.write('{"invalid": json content}')  # Invalid JSON syntax
        
        # Should recover from backup without crashing
        recovered_portfolio = storage.load_portfolio()
        
        # Verify recovery worked - should match original data
        assert len(recovered_portfolio) == len(original_portfolio)
        for ticker in original_portfolio.get_all_tickers():
            original_holding = original_portfolio.get_holding(ticker)
            recovered_holding = recovered_portfolio.get_holding(ticker)
            
            assert recovered_holding is not None
            assert recovered_holding.ticker == original_holding.ticker
            assert recovered_holding.quantity == original_holding.quantity
            assert recovered_holding.target_allocation == original_holding.target_allocation
            assert recovered_holding.current_price == original_holding.current_price
        
        # Test Case 2: Corrupted main file with missing required fields
        # Save again to create fresh backup
        storage.save_portfolio(original_portfolio)
        
        with open(temp_filename, 'w') as f:
            json.dump({"version": "1.0", "missing_holdings": []}, f)  # Missing 'holdings' field
        
        # Should recover from backup
        recovered_portfolio = storage.load_portfolio()
        assert len(recovered_portfolio) == len(original_portfolio)
    
    finally:
        # Clean up temporary files
        for filename in [temp_filename, backup_filename]:
            if os.path.exists(filename):
                os.remove(filename)


def test_data_corruption_recovery_no_backup():
    """
    Property 15: Data Corruption Recovery - No backup available
    Test corruption recovery when no backup exists.
    **Validates: Requirements 12.5**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    backup_filename = f"{temp_filename}.backup"
    
    try:
        storage = DataStorage(temp_filename)
        
        # Test Case 1: Corrupted main file with no backup
        with open(temp_filename, 'w') as f:
            f.write('invalid json')
        
        # Should handle gracefully and raise appropriate error
        try:
            corrupted_portfolio = storage.load_portfolio()
            # If it doesn't raise an exception, should return empty portfolio
            assert corrupted_portfolio.is_empty()
        except ValueError as e:
            # Should raise ValueError with appropriate message about corruption
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
        
        # Test Case 2: Invalid holding data structure with no backup
        invalid_holding_data = {
            "version": "1.0",
            "last_saved": datetime.now().isoformat(),
            "holdings": [
                {
                    "ticker": "AAPL",
                    # Missing required fields: quantity, target_allocation
                    "last_price": 150.0
                }
            ]
        }
        
        with open(temp_filename, 'w') as f:
            json.dump(invalid_holding_data, f)
        
        # Should handle missing required fields gracefully
        try:
            corrupted_holding_portfolio = storage.load_portfolio()
            # If it doesn't raise an exception, should return empty portfolio
            assert corrupted_holding_portfolio.is_empty()
        except (ValueError, KeyError) as e:
            # Should raise appropriate error about corruption
            assert "missing" in str(e).lower() or "corrupted" in str(e).lower()
    
    finally:
        # Clean up temporary files
        for filename in [temp_filename, backup_filename]:
            if os.path.exists(filename):
                os.remove(filename)


def test_data_corruption_recovery_both_files_corrupted():
    """
    Property 15: Data Corruption Recovery - Both files corrupted
    Test corruption recovery when both main file and backup are corrupted.
    **Validates: Requirements 12.5**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    backup_filename = f"{temp_filename}.backup"
    
    try:
        # Create portfolio with data
        portfolio = Portfolio()
        holding = Holding("AAPL", 10.0, 50.0)
        holding.update_price(150.0)
        portfolio.add_holding(holding)
        
        storage = DataStorage(temp_filename)
        
        # Save twice to create backup
        storage.save_portfolio(portfolio)
        storage.save_portfolio(portfolio)
        
        # Corrupt both files
        with open(temp_filename, 'w') as f:
            f.write('invalid json')
        with open(backup_filename, 'w') as f:
            f.write('also invalid json')
        
        # Should handle gracefully and raise appropriate error
        try:
            corrupted_recovery_portfolio = storage.load_portfolio()
            # If it doesn't raise an exception, it should return empty portfolio
            assert corrupted_recovery_portfolio.is_empty()
        except ValueError as e:
            # Should raise ValueError with appropriate message about corruption
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
    
    finally:
        # Clean up temporary files
        for filename in [temp_filename, backup_filename]:
            if os.path.exists(filename):
                os.remove(filename)


def test_empty_portfolio_corruption_recovery():
    """
    Property 15: Data Corruption Recovery - Empty portfolio case
    Test corruption recovery specifically for empty portfolios.
    **Validates: Requirements 12.5**
    """
    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    backup_filename = f"{temp_filename}.backup"
    
    try:
        # Create empty portfolio
        empty_portfolio = Portfolio()
        
        # Create data storage instance
        storage = DataStorage(temp_filename)
        
        # Save empty portfolio (no backup created for first save)
        storage.save_portfolio(empty_portfolio)
        
        # Corrupt the main file
        with open(temp_filename, 'w') as f:
            f.write('invalid json')
        
        # Should handle gracefully since no backup exists for empty portfolio
        try:
            recovered_portfolio = storage.load_portfolio()
            assert recovered_portfolio.is_empty()
        except ValueError as e:
            # Should raise ValueError about corruption
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
        
        # Test with empty portfolio that has backup
        # Save twice to create backup
        storage.save_portfolio(empty_portfolio)
        storage.save_portfolio(empty_portfolio)
        
        # Now corrupt main file
        with open(temp_filename, 'w') as f:
            f.write('invalid json')
        
        # Should recover from backup (which contains empty portfolio)
        recovered_portfolio = storage.load_portfolio()
        assert recovered_portfolio.is_empty()
        assert len(recovered_portfolio) == 0
        
        # Test both files corrupted with empty portfolio
        with open(temp_filename, 'w') as f:
            f.write('invalid json')
        with open(backup_filename, 'w') as f:
            f.write('also invalid json')
        
        # Should handle gracefully
        try:
            final_portfolio = storage.load_portfolio()
            assert final_portfolio.is_empty()
        except ValueError as e:
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
    
    finally:
        # Clean up temporary files
        for filename in [temp_filename, backup_filename]:
            if os.path.exists(filename):
                os.remove(filename)


def test_specific_corruption_scenarios():
    """
    Property 15: Data Corruption Recovery - Specific corruption scenarios
    Test specific types of data corruption that might occur in real usage.
    **Validates: Requirements 12.5**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    backup_filename = f"{temp_filename}.backup"
    
    try:
        storage = DataStorage(temp_filename)
        
        # Test Case 1: Empty file corruption
        with open(temp_filename, 'w') as f:
            f.write('')  # Empty file
        
        try:
            empty_file_portfolio = storage.load_portfolio()
            assert empty_file_portfolio.is_empty()
        except ValueError as e:
            # Acceptable to raise ValueError for empty file
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
        
        # Test Case 2: Non-JSON content
        with open(temp_filename, 'w') as f:
            f.write('This is not JSON content at all!')
        
        try:
            non_json_portfolio = storage.load_portfolio()
            assert non_json_portfolio.is_empty()
        except ValueError as e:
            # Acceptable to raise ValueError for non-JSON content
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
        
        # Test Case 3: Valid JSON but wrong structure
        with open(temp_filename, 'w') as f:
            json.dump({"completely": "different", "structure": True}, f)
        
        try:
            wrong_structure_portfolio = storage.load_portfolio()
            assert wrong_structure_portfolio.is_empty()
        except (ValueError, KeyError) as e:
            # Acceptable to raise error for wrong structure
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower() or "missing" in str(e).lower()
        
        # Test Case 4: Holdings field is not a list
        with open(temp_filename, 'w') as f:
            json.dump({
                "version": "1.0",
                "last_saved": datetime.now().isoformat(),
                "holdings": "not a list"
            }, f)
        
        try:
            non_list_holdings_portfolio = storage.load_portfolio()
            assert non_list_holdings_portfolio.is_empty()
        except ValueError as e:
            # Should handle type validation errors gracefully
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower() or "must be a list" in str(e)
        
        # Test Case 5: Invalid data types in holdings
        with open(temp_filename, 'w') as f:
            json.dump({
                "version": "1.0",
                "last_saved": datetime.now().isoformat(),
                "holdings": [
                    {
                        "ticker": "AAPL",
                        "quantity": "not a number",  # Invalid type
                        "target_allocation": 50.0,
                        "last_price": 150.0
                    }
                ]
            }, f)
        
        try:
            invalid_types_portfolio = storage.load_portfolio()
            assert invalid_types_portfolio.is_empty()
        except (ValueError, TypeError) as e:
            # Should handle type conversion errors
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower()
        
        # Test Case 6: Invalid target allocation values
        with open(temp_filename, 'w') as f:
            json.dump({
                "version": "1.0",
                "last_saved": datetime.now().isoformat(),
                "holdings": [
                    {
                        "ticker": "AAPL",
                        "quantity": 10.0,
                        "target_allocation": -50.0,  # Invalid allocation
                        "last_price": 150.0
                    }
                ]
            }, f)
        
        try:
            invalid_allocation_portfolio = storage.load_portfolio()
            assert invalid_allocation_portfolio.is_empty()
        except ValueError as e:
            # Should catch invalid target allocation
            assert "corrupted" in str(e).lower() or "starting fresh" in str(e).lower() or "target allocation" in str(e).lower()
    
    finally:
        # Clean up temporary files
        for filename in [temp_filename, backup_filename]:
            if os.path.exists(filename):
                os.remove(filename)


def test_backup_creation_and_recovery():
    """
    Property 15: Data Corruption Recovery - Backup creation and recovery
    Test that backup creation works correctly and recovery from backup is reliable.
    **Validates: Requirements 12.5**
    """
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    backup_filename = f"{temp_filename}.backup"
    
    try:
        # Create portfolio with data
        portfolio = Portfolio()
        holding = Holding("AAPL", 10.0, 50.0)
        holding.update_price(150.0)
        portfolio.add_holding(holding)
        
        storage = DataStorage(temp_filename)
        
        # Save portfolio (should create backup if file exists)
        storage.save_portfolio(portfolio)
        
        # Verify main file exists
        assert storage.file_exists()
        assert storage.get_file_size() > 0
        
        # Save again to create backup
        storage.save_portfolio(portfolio)
        
        # Verify backup was created
        assert storage.backup_exists()
        
        # Corrupt main file
        with open(temp_filename, 'w') as f:
            f.write('corrupted data')
        
        # Load should recover from backup
        recovered_portfolio = storage.load_portfolio()
        
        # Verify recovery worked
        assert len(recovered_portfolio) == 1
        recovered_holding = recovered_portfolio.get_holding("AAPL")
        assert recovered_holding is not None
        assert recovered_holding.ticker == "AAPL"
        assert recovered_holding.quantity == 10.0
        assert recovered_holding.target_allocation == 50.0
        assert recovered_holding.current_price == 150.0
        
        # Verify main file was restored from backup
        assert storage.file_exists()
        assert storage.get_file_size() > 0
        
        # Load again should work normally now
        restored_portfolio = storage.load_portfolio()
        assert len(restored_portfolio) == 1
    
    finally:
        # Clean up temporary files
        for filename in [temp_filename, backup_filename]:
            if os.path.exists(filename):
                os.remove(filename)


def test_permission_and_io_error_handling():
    """
    Property 15: Data Corruption Recovery - Permission and I/O error handling
    Test that permission errors and I/O errors are handled gracefully.
    **Validates: Requirements 12.5**
    """
    # Create temporary directory that we can control permissions on
    temp_dir = tempfile.mkdtemp()
    temp_filename = os.path.join(temp_dir, 'portfolio.json')
    
    try:
        # Create portfolio with data
        portfolio = Portfolio()
        holding = Holding("AAPL", 10.0, 50.0)
        holding.update_price(150.0)
        portfolio.add_holding(holding)
        
        storage = DataStorage(temp_filename)
        
        # Test normal save first
        storage.save_portfolio(portfolio)
        assert storage.file_exists()
        
        # Test loading from existing file (should work)
        loaded_portfolio = storage.load_portfolio()
        assert len(loaded_portfolio) == 1
        
        # Test permission error by making directory read-only
        # This prevents backup creation and temp file operations
        os.chmod(temp_dir, 0o555)  # read and execute only, no write
        
        try:
            # Saving should raise OSError due to backup creation failure
            with pytest.raises(OSError, match="Cannot create backup"):
                storage.save_portfolio(portfolio)
        
        finally:
            # Restore directory permissions for cleanup
            os.chmod(temp_dir, 0o755)
        
        # Test with invalid directory path
        invalid_storage = DataStorage("/nonexistent/directory/portfolio.json")
        
        with pytest.raises(OSError):
            invalid_storage.save_portfolio(portfolio)
    
    finally:
        # Clean up temporary directory and files
        if os.path.exists(temp_dir):
            # Ensure directory is writable for cleanup
            os.chmod(temp_dir, 0o755)
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(temp_dir)