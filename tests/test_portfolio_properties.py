"""
Property-based tests for portfolio state management.
Feature: stock-allocation-tool, Property 1: Portfolio State Management
"""
import pytest
from hypothesis import given, strategies as st
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy
)
def test_portfolio_add_holding_state_consistency(ticker, quantity, target_allocation, price):
    """
    Property 1: Portfolio State Management
    For any portfolio and any valid holding operation (add, update quantity, delete), 
    the portfolio should correctly reflect the change and maintain data consistency 
    across all holdings.
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    portfolio = Portfolio()
    initial_count = len(portfolio)
    
    # Create and add holding
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(price)
    
    portfolio.add_holding(holding)
    
    # Verify add operation
    assert len(portfolio) == initial_count + 1
    assert ticker.upper() in portfolio.holdings
    retrieved_holding = portfolio.get_holding(ticker)
    assert retrieved_holding is not None
    assert retrieved_holding.ticker == ticker.upper()
    assert retrieved_holding.quantity == quantity
    assert retrieved_holding.target_allocation == target_allocation
    assert retrieved_holding.current_price == price


@given(
    ticker=ticker_strategy,
    initial_quantity=quantity_strategy,
    new_quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy
)
def test_portfolio_update_quantity_state_consistency(ticker, initial_quantity, new_quantity, target_allocation, price):
    """
    Property 1: Portfolio State Management - Update quantity operation
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    portfolio = Portfolio()
    
    # Add initial holding
    holding = Holding(ticker, initial_quantity, target_allocation)
    holding.update_price(price)
    portfolio.add_holding(holding)
    
    # Update quantity
    portfolio.update_holding_quantity(ticker, new_quantity)
    
    # Verify update operation
    updated_holding = portfolio.get_holding(ticker)
    assert updated_holding is not None
    assert updated_holding.quantity == new_quantity
    assert updated_holding.ticker == ticker.upper()
    assert updated_holding.target_allocation == target_allocation
    assert updated_holding.current_price == price


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy
)
def test_portfolio_remove_holding_state_consistency(ticker, quantity, target_allocation, price):
    """
    Property 1: Portfolio State Management - Remove operation
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    portfolio = Portfolio()
    
    # Add holding
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(price)
    portfolio.add_holding(holding)
    
    initial_count = len(portfolio)
    assert initial_count == 1
    
    # Remove holding
    portfolio.remove_holding(ticker)
    
    # Verify remove operation
    assert len(portfolio) == initial_count - 1
    assert ticker.upper() not in portfolio.holdings
    assert portfolio.get_holding(ticker) is None


@given(
    holdings_data=st.lists(
        st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0].upper()  # Ensure unique tickers
    )
)
def test_portfolio_multiple_operations_state_consistency(holdings_data):
    """
    Property 1: Portfolio State Management - Multiple operations
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    portfolio = Portfolio()
    
    # Add all holdings
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.update_price(price)
        portfolio.add_holding(holding)
    
    # Verify all holdings were added correctly
    assert len(portfolio) == len(holdings_data)
    
    for ticker, quantity, target_allocation, price in holdings_data:
        retrieved_holding = portfolio.get_holding(ticker)
        assert retrieved_holding is not None
        assert retrieved_holding.ticker == ticker.upper()
        assert retrieved_holding.quantity == quantity
        assert retrieved_holding.target_allocation == target_allocation
        assert retrieved_holding.current_price == price
    
    # Test portfolio-level calculations maintain consistency
    total_value = portfolio.get_total_value()
    expected_total = sum(quantity * price for _, quantity, _, price in holdings_data)
    assert abs(total_value - expected_total) < 0.01  # Allow for floating point precision
    
    # Test allocation summary consistency
    allocation_summary = portfolio.get_allocation_summary()
    assert len(allocation_summary) == len(holdings_data)
    
    # Verify allocation percentages sum correctly (within floating point precision)
    total_allocation = sum(allocation_summary.values())
    assert abs(total_allocation - 100.0) < 0.01 or total_value == 0.0


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy,
    total_portfolio_value=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    rounded=st.booleans()
)
def test_rebalance_calculation_accuracy(ticker, quantity, target_allocation, price, total_portfolio_value, rounded):
    """
    Property 9: Rebalance Calculation Accuracy
    For any holding with current price and target allocation, the system should correctly 
    calculate target value, difference, and rebalance action with optional rounding to 
    whole shares based on user preference.
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
    """
    # Create holding with valid data
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(price)
    
    # Test target value calculation (Requirement 6.1)
    target_value = holding.get_target_value(total_portfolio_value)
    expected_target_value = (target_allocation / 100) * total_portfolio_value
    assert abs(target_value - expected_target_value) < 0.01
    
    # Test current value calculation
    current_value = holding.get_current_value()
    expected_current_value = quantity * price
    assert abs(current_value - expected_current_value) < 0.01
    
    # Test difference calculation (Requirement 6.2)
    difference = target_value - current_value
    
    # Test rebalance action calculation (Requirements 6.3, 6.4, 6.5)
    rebalance_action = holding.get_rebalance_action(total_portfolio_value, rounded)
    expected_shares_action = difference / price
    
    if rounded:
        # When rounding is enabled, result should be a whole number
        assert rebalance_action == round(expected_shares_action)
        assert rebalance_action == int(rebalance_action)
    else:
        # When rounding is disabled, result should be exact fractional shares
        assert abs(rebalance_action - expected_shares_action) < 0.0001
    
    # Test that rebalance action direction is correct
    if target_value > current_value:
        # Should recommend buying (positive action)
        assert rebalance_action >= 0
    elif target_value < current_value:
        # Should recommend selling (negative action)
        assert rebalance_action <= 0
    else:
        # Should recommend no action when target equals current
        assert abs(rebalance_action) < 0.0001


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    total_portfolio_value=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
def test_zero_target_allocation_sells_all_shares(ticker, quantity, total_portfolio_value):
    """
    Property 9: Rebalance Calculation Accuracy - Zero target allocation case
    When target allocation is zero, the system should recommend selling all shares.
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
    """
    # Create holding with zero target allocation
    holding = Holding(ticker, quantity, 0.0)
    holding.update_price(50.0)  # Use a reasonable price
    
    # Calculate rebalance action
    rebalance_action_rounded = holding.get_rebalance_action(total_portfolio_value, True)
    rebalance_action_exact = holding.get_rebalance_action(total_portfolio_value, False)
    
    # Should recommend selling all shares (negative quantity)
    assert rebalance_action_rounded == -round(quantity)
    assert abs(rebalance_action_exact - (-quantity)) < 0.0001


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy
)
def test_target_allocation_management(ticker, quantity, target_allocation):
    """
    Property 3: Target Allocation Management
    For any valid target allocation percentage (0-100%), the system should store the value 
    and correctly calculate allocation totals, regardless of whether the total equals 100%.
    **Validates: Requirements 2.1, 2.2, 2.5**
    """
    portfolio = Portfolio()
    
    # Test individual holding target allocation storage (Requirement 2.1)
    holding = Holding(ticker, quantity, target_allocation)
    portfolio.add_holding(holding)
    
    # Verify target allocation is stored correctly
    retrieved_holding = portfolio.get_holding(ticker)
    assert retrieved_holding is not None
    assert retrieved_holding.target_allocation == target_allocation
    
    # Test allocation total calculation (Requirement 2.2)
    total_allocation = portfolio.get_target_allocation_total()
    assert total_allocation == target_allocation
    
    # Test allocation status indication (Requirement 2.2)
    status = portfolio.get_allocation_status()
    if abs(target_allocation - 100.0) < 0.01:
        assert status == "equal"
    elif target_allocation > 100.0:
        assert status == "above"
    else:
        assert status == "below"
    
    # Test validation of target allocation range (Requirement 2.5)
    assert portfolio.validate_target_allocation_range(target_allocation) == True
    assert portfolio.validate_target_allocation_range(-1.0) == False
    assert portfolio.validate_target_allocation_range(101.0) == False


@given(
    holdings_data=st.lists(
        st.tuples(ticker_strategy, quantity_strategy, allocation_strategy),
        min_size=2,
        max_size=5,
        unique_by=lambda x: x[0].upper()  # Ensure unique tickers
    )
)
def test_multiple_holdings_allocation_management(holdings_data):
    """
    Property 3: Target Allocation Management - Multiple holdings
    Test that allocation totals and status work correctly with multiple holdings.
    **Validates: Requirements 2.1, 2.2, 2.5**
    """
    portfolio = Portfolio()
    expected_total = 0.0
    
    # Add all holdings and calculate expected total
    for ticker, quantity, target_allocation in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        portfolio.add_holding(holding)
        expected_total += target_allocation
    
    # Test total allocation calculation (Requirement 2.2)
    actual_total = portfolio.get_target_allocation_total()
    assert abs(actual_total - expected_total) < 0.01
    
    # Test allocation status with multiple holdings (Requirement 2.2)
    status = portfolio.get_allocation_status()
    if abs(expected_total - 100.0) < 0.01:
        assert status == "equal"
    elif expected_total > 100.0:
        assert status == "above"
    else:
        assert status == "below"
    
    # Test that each individual holding maintains its allocation (Requirement 2.1)
    for ticker, quantity, target_allocation in holdings_data:
        retrieved_holding = portfolio.get_holding(ticker)
        assert retrieved_holding is not None
        assert retrieved_holding.target_allocation == target_allocation


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    initial_allocation=allocation_strategy,
    new_allocation=allocation_strategy
)
def test_target_allocation_update_management(ticker, quantity, initial_allocation, new_allocation):
    """
    Property 3: Target Allocation Management - Updates
    Test that target allocation updates work correctly and maintain system consistency.
    **Validates: Requirements 2.1, 2.2, 2.5**
    """
    portfolio = Portfolio()
    
    # Create holding with initial allocation
    holding = Holding(ticker, quantity, initial_allocation)
    portfolio.add_holding(holding)
    
    # Verify initial state
    assert portfolio.get_target_allocation_total() == initial_allocation
    
    # Update target allocation (Requirement 2.1)
    portfolio.update_target_allocation(ticker, new_allocation)
    
    # Verify update was applied correctly
    updated_holding = portfolio.get_holding(ticker)
    assert updated_holding is not None
    assert updated_holding.target_allocation == new_allocation
    
    # Verify total allocation updated correctly (Requirement 2.2)
    assert portfolio.get_target_allocation_total() == new_allocation
    
    # Verify allocation status reflects the change (Requirement 2.2)
    status = portfolio.get_allocation_status()
    if abs(new_allocation - 100.0) < 0.01:
        assert status == "equal"
    elif new_allocation > 100.0:
        assert status == "above"
    else:
        assert status == "below"


def test_invalid_target_allocation_validation():
    """
    Property 3: Target Allocation Management - Validation
    Test that invalid target allocations are properly rejected.
    **Validates: Requirements 2.5**
    """
    portfolio = Portfolio()
    
    # Test invalid allocations in Holding constructor
    with pytest.raises(ValueError, match="Target allocation must be between 0% and 100%"):
        Holding("AAPL", 10, -5.0)
    
    with pytest.raises(ValueError, match="Target allocation must be between 0% and 100%"):
        Holding("AAPL", 10, 150.0)
    
    # Test invalid allocations in portfolio update
    holding = Holding("AAPL", 10, 50.0)
    portfolio.add_holding(holding)
    
    with pytest.raises(ValueError, match="Target allocation must be between 0% and 100%"):
        portfolio.update_target_allocation("AAPL", -10.0)
    
    with pytest.raises(ValueError, match="Target allocation must be between 0% and 100%"):
        portfolio.update_target_allocation("AAPL", 200.0)
    
    # Test validation method
    assert portfolio.validate_target_allocation_range(0.0) == True
    assert portfolio.validate_target_allocation_range(50.0) == True
    assert portfolio.validate_target_allocation_range(100.0) == True
    assert portfolio.validate_target_allocation_range(-0.1) == False
    assert portfolio.validate_target_allocation_range(100.1) == False


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy,
    total_portfolio_value=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    share_rounding_enabled=st.booleans()
)
def test_rebalance_action_direction_and_rounding(ticker, quantity, target_allocation, price, total_portfolio_value, share_rounding_enabled):
    """
    Property 10: Rebalance Action Direction and Rounding
    For any calculated rebalance action, positive values should indicate buy recommendations, 
    negative values should indicate sell recommendations, zero target allocations should 
    recommend selling all shares, and the display should respect the share rounding toggle setting.
    **Validates: Requirements 6.6, 6.7, 6.8, 6.9, 6.10**
    """
    # Create holding
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(price)
    
    # Calculate values
    current_value = holding.get_current_value()
    target_value = holding.get_target_value(total_portfolio_value)
    difference = target_value - current_value
    
    # Get rebalance action
    rebalance_action = holding.get_rebalance_action(total_portfolio_value, share_rounding_enabled)
    
    # Test direction requirements (Requirements 6.8, 6.9)
    if target_value > current_value:
        # Should recommend buying shares (positive action) (Requirement 6.8)
        assert rebalance_action >= 0, f"Expected positive rebalance action for buy recommendation, got {rebalance_action}"
        
        # If difference is significant and will definitely round to positive, action should be clearly positive
        expected_shares = difference / price
        if share_rounding_enabled:
            if expected_shares > 0.5:  # Will round to at least 1 share (accounting for banker's rounding)
                assert rebalance_action > 0, f"Expected clearly positive action for significant buy recommendation"
        else:
            if difference > price * 0.01:  # More than 0.01 shares worth of difference
                assert rebalance_action > 0, f"Expected clearly positive action for significant buy recommendation"
            
    elif target_value < current_value:
        # Should recommend selling shares (negative action) (Requirement 6.9)
        assert rebalance_action <= 0, f"Expected negative rebalance action for sell recommendation, got {rebalance_action}"
        
        # If difference is significant and will definitely round to negative, action should be clearly negative
        expected_shares = difference / price
        if share_rounding_enabled:
            if expected_shares < -0.5:  # Will round to at least -1 share (accounting for banker's rounding)
                assert rebalance_action < 0, f"Expected clearly negative action for significant sell recommendation"
        else:
            if abs(difference) > price * 0.01:  # More than 0.01 shares worth of difference
                assert rebalance_action < 0, f"Expected clearly negative action for significant sell recommendation"
    
    # Test rounding behavior (Requirements 6.6, 6.7)
    if share_rounding_enabled:
        # When rounding is enabled, result should be whole shares (Requirement 6.6)
        assert rebalance_action == round(rebalance_action), f"Expected whole shares when rounding enabled, got {rebalance_action}"
        assert isinstance(rebalance_action, (int, float)) and rebalance_action == int(rebalance_action)
    else:
        # When rounding is disabled, result should be exact fractional shares (Requirement 6.7)
        expected_exact_action = difference / price
        assert abs(rebalance_action - expected_exact_action) < 0.0001, f"Expected exact fractional shares when rounding disabled"
    
    # Test mathematical consistency
    expected_shares_needed = difference / price
    if share_rounding_enabled:
        expected_rounded = round(expected_shares_needed)
        assert rebalance_action == expected_rounded
    else:
        assert abs(rebalance_action - expected_shares_needed) < 0.0001


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    price=price_strategy,
    total_portfolio_value=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    share_rounding_enabled=st.booleans()
)
def test_zero_target_allocation_sells_all_shares_property(ticker, quantity, price, total_portfolio_value, share_rounding_enabled):
    """
    Property 10: Rebalance Action Direction and Rounding - Zero target allocation
    When target allocation is zero, the system should recommend selling all shares.
    **Validates: Requirements 6.10**
    """
    # Create holding with zero target allocation
    holding = Holding(ticker, quantity, 0.0)  # Zero target allocation
    holding.update_price(price)
    
    # Calculate rebalance action
    rebalance_action = holding.get_rebalance_action(total_portfolio_value, share_rounding_enabled)
    
    # Should recommend selling all shares (Requirement 6.10)
    if share_rounding_enabled:
        # With rounding, should sell the rounded amount based on the calculation
        target_value = 0.0  # Zero target allocation
        current_value = quantity * price
        difference = target_value - current_value  # Will be negative
        expected_shares_action = difference / price  # Will be negative
        expected_action = round(expected_shares_action)
        assert rebalance_action == expected_action, f"Expected to sell {expected_action} shares (rounded), got {rebalance_action}"
    else:
        # Without rounding, should sell exactly the current quantity
        expected_action = -quantity
        assert abs(rebalance_action - expected_action) < 0.0001, f"Expected to sell {expected_action} shares (exact), got {rebalance_action}"
    
    # Action should always be negative or zero (selling)
    assert rebalance_action <= 0, f"Expected negative or zero action for zero target allocation, got {rebalance_action}"
    
    # If quantity is positive and rounding doesn't round to zero, action should be negative
    if quantity > 0:
        target_value = 0.0
        current_value = quantity * price
        difference = target_value - current_value
        expected_shares_action = difference / price
        
        if share_rounding_enabled:
            expected_rounded = round(expected_shares_action)
            if expected_rounded != 0:
                assert rebalance_action < 0, f"Expected negative action when rounded result is non-zero, got {rebalance_action}"
        else:
            assert rebalance_action < 0, f"Expected negative action when selling positive quantity (exact), got {rebalance_action}"


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    price=price_strategy,
    total_portfolio_value=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
def test_rounding_toggle_consistency(ticker, quantity, price, total_portfolio_value):
    """
    Property 10: Rebalance Action Direction and Rounding - Toggle consistency
    The same holding should produce different results based on rounding setting.
    **Validates: Requirements 6.6, 6.7**
    """
    # Use a target allocation that will likely produce fractional shares
    target_allocation = 33.33  # This often produces fractional results
    
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(price)
    
    # Get both rounded and exact results
    rounded_action = holding.get_rebalance_action(total_portfolio_value, True)
    exact_action = holding.get_rebalance_action(total_portfolio_value, False)
    
    # Rounded result should be a whole number (Requirement 6.6)
    assert rounded_action == round(rounded_action), f"Rounded action should be whole number, got {rounded_action}"
    
    # Exact result should match mathematical calculation (Requirement 6.7)
    target_value = holding.get_target_value(total_portfolio_value)
    current_value = holding.get_current_value()
    expected_exact = (target_value - current_value) / price
    assert abs(exact_action - expected_exact) < 0.0001, f"Exact action should match calculation, expected {expected_exact}, got {exact_action}"
    
    # If the exact calculation is not already a whole number, results should differ
    if abs(expected_exact - round(expected_exact)) > 0.001:
        assert rounded_action != exact_action, f"Rounded and exact actions should differ for fractional calculations"
        assert rounded_action == round(expected_exact), f"Rounded action should equal rounded exact calculation"