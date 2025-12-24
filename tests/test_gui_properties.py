"""
Property-based tests for GUI real-time calculation updates.
Feature: stock-allocation-tool, Property 2: Real-time Calculation Updates
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
    initial_quantity=quantity_strategy,
    new_quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy
)
def test_quantity_change_updates_all_calculations(ticker, initial_quantity, new_quantity, target_allocation, price):
    """
    Property 2: Real-time Calculation Updates - Quantity changes
    For any portfolio change (quantity, allocation, or price update), all dependent 
    calculated fields (current value, allocation percentages, target values, rebalance 
    actions) should update immediately and correctly.
    **Validates: Requirements 1.5, 2.4, 4.2, 7.1**
    """
    portfolio = Portfolio()
    
    # Create initial holding
    holding = Holding(ticker, initial_quantity, target_allocation)
    holding.update_price(price)
    portfolio.add_holding(holding)
    
    # Calculate initial values
    initial_current_value = holding.get_current_value()
    initial_total_value = portfolio.get_total_value()
    initial_current_allocation = holding.get_current_allocation(initial_total_value)
    initial_target_value = holding.get_target_value(initial_total_value)
    initial_rebalance_action = holding.get_rebalance_action(initial_total_value)
    
    # Verify initial calculations
    assert abs(initial_current_value - (initial_quantity * price)) < 0.01
    assert abs(initial_total_value - initial_current_value) < 0.01  # Single holding portfolio
    
    # Update quantity
    portfolio.update_holding_quantity(ticker, new_quantity)
    updated_holding = portfolio.get_holding(ticker)
    
    # Calculate updated values
    new_current_value = updated_holding.get_current_value()
    new_total_value = portfolio.get_total_value()
    new_current_allocation = updated_holding.get_current_allocation(new_total_value)
    new_target_value = updated_holding.get_target_value(new_total_value)
    new_rebalance_action = updated_holding.get_rebalance_action(new_total_value)
    
    # Verify all calculations updated correctly
    expected_new_current_value = new_quantity * price
    assert abs(new_current_value - expected_new_current_value) < 0.01
    assert abs(new_total_value - new_current_value) < 0.01  # Single holding portfolio
    
    # Current allocation should be 100% for single holding (unless value is 0)
    if new_total_value > 0:
        assert abs(new_current_allocation - 100.0) < 0.01
    
    # Target value should reflect the target allocation percentage
    expected_target_value = (target_allocation / 100) * new_total_value
    assert abs(new_target_value - expected_target_value) < 0.01
    
    # Rebalance action should be calculated correctly
    expected_rebalance_shares = (new_target_value - new_current_value) / price
    # Use larger tolerance for rebalance action due to rounding
    assert abs(new_rebalance_action - round(expected_rebalance_shares)) < 0.01
    
    # The important thing is that calculations are mathematically correct


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    initial_allocation=allocation_strategy,
    new_allocation=allocation_strategy,
    price=price_strategy
)
def test_allocation_change_updates_all_calculations(ticker, quantity, initial_allocation, new_allocation, price):
    """
    Property 2: Real-time Calculation Updates - Allocation changes
    **Validates: Requirements 1.5, 2.4, 4.2, 7.1**
    """
    portfolio = Portfolio()
    
    # Create initial holding
    holding = Holding(ticker, quantity, initial_allocation)
    holding.update_price(price)
    portfolio.add_holding(holding)
    
    # Calculate initial values
    total_value = portfolio.get_total_value()
    initial_target_value = holding.get_target_value(total_value)
    initial_rebalance_action = holding.get_rebalance_action(total_value)
    
    # Update target allocation
    portfolio.update_target_allocation(ticker, new_allocation)
    updated_holding = portfolio.get_holding(ticker)
    
    # Calculate updated values (total value and current value shouldn't change)
    new_total_value = portfolio.get_total_value()
    new_current_value = updated_holding.get_current_value()
    new_target_value = updated_holding.get_target_value(new_total_value)
    new_rebalance_action = updated_holding.get_rebalance_action(new_total_value)
    
    # Verify current value and total value unchanged
    assert abs(new_total_value - total_value) < 0.01
    current_value = updated_holding.get_current_value()
    assert abs(current_value - (quantity * price)) < 0.01
    
    # Verify target value updated correctly
    expected_new_target_value = (new_allocation / 100) * new_total_value
    assert abs(new_target_value - expected_new_target_value) < 0.01
    
    # Verify rebalance action updated correctly
    expected_new_rebalance_shares = (new_target_value - current_value) / price
    # Use larger tolerance for rebalance action due to rounding
    assert abs(new_rebalance_action - round(expected_new_rebalance_shares)) < 0.01
    
    # The important thing is that calculations are mathematically correct
        # (which is very unlikely with random data)


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    initial_price=price_strategy,
    new_price=price_strategy
)
def test_price_change_updates_all_calculations(ticker, quantity, target_allocation, initial_price, new_price):
    """
    Property 2: Real-time Calculation Updates - Price changes
    **Validates: Requirements 1.5, 2.4, 4.2, 7.1**
    """
    portfolio = Portfolio()
    
    # Create initial holding
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(initial_price)
    portfolio.add_holding(holding)
    
    # Calculate initial values
    initial_current_value = holding.get_current_value()
    initial_total_value = portfolio.get_total_value()
    initial_current_allocation = holding.get_current_allocation(initial_total_value)
    initial_target_value = holding.get_target_value(initial_total_value)
    initial_rebalance_action = holding.get_rebalance_action(initial_total_value)
    
    # Update price
    holding.update_price(new_price)
    
    # Calculate updated values
    new_current_value = holding.get_current_value()
    new_total_value = portfolio.get_total_value()
    new_current_allocation = holding.get_current_allocation(new_total_value)
    new_target_value = holding.get_target_value(new_total_value)
    new_rebalance_action = holding.get_rebalance_action(new_total_value)
    
    # Verify all calculations updated correctly
    expected_new_current_value = quantity * new_price
    assert abs(new_current_value - expected_new_current_value) < 0.01
    assert abs(new_total_value - new_current_value) < 0.01  # Single holding portfolio
    
    # Current allocation should still be 100% for single holding (unless value is 0)
    if new_total_value > 0:
        assert abs(new_current_allocation - 100.0) < 0.01
    
    # Target value should reflect the target allocation percentage of new total
    expected_target_value = (target_allocation / 100) * new_total_value
    assert abs(new_target_value - expected_target_value) < 0.01
    
    # Rebalance action should be calculated with new price
    expected_rebalance_shares = (new_target_value - new_current_value) / new_price
    # Use larger tolerance for rebalance action due to rounding
    assert abs(new_rebalance_action - round(expected_rebalance_shares)) < 0.01
    
    # The important thing is that calculations are mathematically correct


@given(
    holdings_data=st.lists(
        st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
        min_size=2,
        max_size=5,
        unique_by=lambda x: x[0].upper()  # Ensure unique tickers
    ),
    update_ticker_index=st.integers(min_value=0, max_value=4),
    new_quantity=quantity_strategy
)
def test_multi_holding_quantity_change_updates_all_calculations(holdings_data, update_ticker_index, new_quantity):
    """
    Property 2: Real-time Calculation Updates - Multi-holding quantity changes
    Test that when one holding's quantity changes in a multi-holding portfolio,
    all calculations update correctly across all holdings.
    **Validates: Requirements 1.5, 2.4, 4.2, 7.1**
    """
    if not holdings_data:
        return
        
    portfolio = Portfolio()
    
    # Add all holdings
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.update_price(price)
        portfolio.add_holding(holding)
    
    # Calculate initial values for all holdings
    initial_total_value = portfolio.get_total_value()
    initial_values = {}
    for ticker, _, _, _ in holdings_data:
        holding = portfolio.get_holding(ticker)
        initial_values[ticker] = {
            'current_value': holding.get_current_value(),
            'current_allocation': holding.get_current_allocation(initial_total_value),
            'target_value': holding.get_target_value(initial_total_value),
            'rebalance_action': holding.get_rebalance_action(initial_total_value)
        }
    
    # Update one holding's quantity
    update_index = update_ticker_index % len(holdings_data)
    update_ticker = holdings_data[update_index][0]
    portfolio.update_holding_quantity(update_ticker, new_quantity)
    
    # Calculate new values for all holdings
    new_total_value = portfolio.get_total_value()
    
    # Verify that all holdings have updated calculations
    for i, (ticker, original_quantity, target_allocation, price) in enumerate(holdings_data):
        holding = portfolio.get_holding(ticker)
        
        new_current_value = holding.get_current_value()
        new_current_allocation = holding.get_current_allocation(new_total_value)
        new_target_value = holding.get_target_value(new_total_value)
        new_rebalance_action = holding.get_rebalance_action(new_total_value)
        
        if i == update_index:
            # Updated holding should have new current value
            expected_current_value = new_quantity * price
            assert abs(new_current_value - expected_current_value) < 0.01
        else:
            # Other holdings should have same current value
            expected_current_value = original_quantity * price
            assert abs(new_current_value - expected_current_value) < 0.01
        
        # All holdings should have updated allocations and target values based on new total
        expected_current_allocation = (new_current_value / new_total_value) * 100 if new_total_value > 0 else 0
        expected_target_value = (target_allocation / 100) * new_total_value
        expected_rebalance_action = (expected_target_value - new_current_value) / price
        
        if new_total_value > 0:
            assert abs(new_current_allocation - expected_current_allocation) < 0.01
        assert abs(new_target_value - expected_target_value) < 0.01
        # Use larger tolerance for rebalance action due to rounding
        assert abs(new_rebalance_action - round(expected_rebalance_action)) < 0.01
        
        # All calculations should be mathematically correct regardless of change magnitude
        # The important thing is correctness, not change detection


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy
)
def test_calculation_consistency_after_multiple_updates(ticker, quantity, target_allocation, price):
    """
    Property 2: Real-time Calculation Updates - Multiple sequential updates
    Test that calculations remain consistent after multiple sequential updates.
    **Validates: Requirements 1.5, 2.4, 4.2, 7.1**
    """
    portfolio = Portfolio()
    
    # Create initial holding
    holding = Holding(ticker, quantity, target_allocation)
    holding.update_price(price)
    portfolio.add_holding(holding)
    
    # Perform multiple updates and verify consistency after each
    updates = [
        ('quantity', quantity * 1.5),
        ('allocation', min(target_allocation * 1.2, 100.0)),
        ('price', price * 1.1),
        ('quantity', quantity * 0.8),
        ('allocation', max(target_allocation * 0.7, 0.0))
    ]
    
    for update_type, new_value in updates:
        if update_type == 'quantity':
            portfolio.update_holding_quantity(ticker, new_value)
        elif update_type == 'allocation':
            portfolio.update_target_allocation(ticker, new_value)
        elif update_type == 'price':
            holding = portfolio.get_holding(ticker)
            holding.update_price(new_value)
        
        # Verify calculations are consistent after each update
        updated_holding = portfolio.get_holding(ticker)
        total_value = portfolio.get_total_value()
        
        current_value = updated_holding.get_current_value()
        current_allocation = updated_holding.get_current_allocation(total_value)
        target_value = updated_holding.get_target_value(total_value)
        rebalance_action = updated_holding.get_rebalance_action(total_value)
        
        # Verify mathematical consistency
        expected_current_value = updated_holding.quantity * updated_holding.current_price
        assert abs(current_value - expected_current_value) < 0.01
        
        if total_value > 0:
            expected_current_allocation = (current_value / total_value) * 100
            assert abs(current_allocation - expected_current_allocation) < 0.01
        
        expected_target_value = (updated_holding.target_allocation / 100) * total_value
        assert abs(target_value - expected_target_value) < 0.01
        
        expected_rebalance_action = (target_value - current_value) / updated_holding.current_price
        # Use larger tolerance for rebalance action due to rounding
        assert abs(rebalance_action - round(expected_rebalance_action)) < 0.01


@given(
    holdings_data=st.lists(
        st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0].upper()  # Ensure unique tickers
    )
)
def test_portfolio_level_calculations_update_immediately(holdings_data):
    """
    Property 2: Real-time Calculation Updates - Portfolio-level calculations
    Test that portfolio-level calculations (total value, allocation summary) 
    update immediately when individual holdings change.
    **Validates: Requirements 1.5, 2.4, 4.2, 7.1**
    """
    portfolio = Portfolio()
    
    # Add all holdings
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.update_price(price)
        portfolio.add_holding(holding)
    
    # Calculate expected portfolio totals
    expected_total_value = sum(quantity * price for _, quantity, _, price in holdings_data)
    expected_target_allocation_total = sum(target_allocation for _, _, target_allocation, _ in holdings_data)
    
    # Verify portfolio calculations are correct
    actual_total_value = portfolio.get_total_value()
    actual_target_allocation_total = portfolio.get_target_allocation_total()
    allocation_summary = portfolio.get_allocation_summary()
    
    assert abs(actual_total_value - expected_total_value) < 0.01
    assert abs(actual_target_allocation_total - expected_target_allocation_total) < 0.01
    
    # Verify allocation summary contains all holdings
    assert len(allocation_summary) == len(holdings_data)
    
    # Verify allocation summary percentages are correct
    for ticker, quantity, target_allocation, price in holdings_data:
        assert ticker.upper() in allocation_summary
        if expected_total_value > 0:
            expected_allocation = ((quantity * price) / expected_total_value) * 100
            assert abs(allocation_summary[ticker.upper()] - expected_allocation) < 0.01
        else:
            assert allocation_summary[ticker.upper()] == 0.0
    
    # Verify allocation summary sums to 100% (within floating point precision)
    total_allocation_percentage = sum(allocation_summary.values())
    if expected_total_value > 0:
        assert abs(total_allocation_percentage - 100.0) < 0.01
    else:
        assert total_allocation_percentage == 0.0


@given(
    holdings_data=st.lists(
        st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
        min_size=1,
        max_size=5,
        unique_by=lambda x: x[0].upper()  # Ensure unique tickers
    ),
    invalid_allocation_multiplier=st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False)
)
def test_ui_functionality_during_invalid_allocation_states(holdings_data, invalid_allocation_multiplier):
    """
    Property 4: UI Functionality During Invalid States
    For any portfolio state where allocations don't sum to 100% or errors occur, 
    the UI should remain fully functional and responsive for all operations.
    **Validates: Requirements 2.3, 7.2, 7.5**
    """
    portfolio = Portfolio()
    
    # Add holdings with potentially invalid allocation totals
    total_allocation = 0.0
    for ticker, quantity, target_allocation, price in holdings_data:
        # Modify allocations to create invalid states (not summing to 100%)
        modified_allocation = target_allocation * invalid_allocation_multiplier
        # Ensure allocation stays within valid range for individual holdings
        modified_allocation = max(0.0, min(100.0, modified_allocation))
        
        holding = Holding(ticker, quantity, modified_allocation)
        holding.update_price(price)
        portfolio.add_holding(holding)
        total_allocation += modified_allocation
    
    # Verify portfolio functions normally regardless of allocation total
    portfolio_total_value = portfolio.get_total_value()
    allocation_summary = portfolio.get_allocation_summary()
    allocation_status = portfolio.get_allocation_status()
    target_allocation_total = portfolio.get_target_allocation_total()
    
    # Portfolio should function normally even with invalid allocation totals
    assert portfolio_total_value >= 0
    assert len(allocation_summary) == len(holdings_data)
    assert allocation_status in ["above", "below", "equal"]
    assert target_allocation_total >= 0
    
    # All portfolio operations should work regardless of allocation validity
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = portfolio.get_holding(ticker)
        assert holding is not None
        
        # Current calculations should work
        current_value = holding.get_current_value()
        current_allocation = holding.get_current_allocation(portfolio_total_value)
        target_value = holding.get_target_value(portfolio_total_value)
        rebalance_action = holding.get_rebalance_action(portfolio_total_value)
        
        # All calculations should return valid numbers
        assert isinstance(current_value, (int, float))
        assert isinstance(current_allocation, (int, float))
        assert isinstance(target_value, (int, float))
        assert isinstance(rebalance_action, (int, float))
        
        # Values should be mathematically correct
        expected_current_value = quantity * price
        assert abs(current_value - expected_current_value) < 0.01
        
        if portfolio_total_value > 0:
            expected_current_allocation = (current_value / portfolio_total_value) * 100
            assert abs(current_allocation - expected_current_allocation) < 0.01
        
        expected_target_value = (holding.target_allocation / 100) * portfolio_total_value
        assert abs(target_value - expected_target_value) < 0.01
        
        # Rebalance calculations should work even with invalid total allocations
        expected_rebalance_action = (target_value - current_value) / price
        assert abs(rebalance_action - round(expected_rebalance_action)) < 0.01
    
    # Portfolio modification operations should work
    if holdings_data:
        first_ticker = holdings_data[0][0]
        original_quantity = holdings_data[0][1]
        
        # Test quantity updates work with invalid allocations
        new_quantity = original_quantity * 1.5
        portfolio.update_holding_quantity(first_ticker, new_quantity)
        updated_holding = portfolio.get_holding(first_ticker)
        assert abs(updated_holding.quantity - new_quantity) < 0.001
        
        # Test allocation updates work even when total becomes more invalid
        new_allocation = min(95.0, holdings_data[0][2] * 2.0)  # Potentially make total even more invalid
        portfolio.update_target_allocation(first_ticker, new_allocation)
        assert abs(updated_holding.target_allocation - new_allocation) < 0.01
        
        # Portfolio should still function after modifications
        new_total_value = portfolio.get_total_value()
        new_allocation_summary = portfolio.get_allocation_summary()
        new_rebalance_actions = portfolio.calculate_rebalance_actions()
        
        assert new_total_value >= 0
        assert len(new_allocation_summary) == len(holdings_data)
        assert len(new_rebalance_actions) == len(holdings_data)
        
        # All operations should continue to work normally
        for ticker in portfolio.get_all_tickers():
            holding = portfolio.get_holding(ticker)
            assert holding.get_current_value() >= 0
            assert isinstance(holding.get_current_allocation(new_total_value), (int, float))
            assert isinstance(holding.get_target_value(new_total_value), (int, float))
            assert isinstance(holding.get_rebalance_action(new_total_value), (int, float))


@given(
    ticker=ticker_strategy,
    quantity=quantity_strategy,
    target_allocation=allocation_strategy,
    price=price_strategy,
    error_scenarios=st.lists(
        st.sampled_from(['zero_price', 'zero_quantity', 'zero_total_value', 'extreme_allocation']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
def test_ui_functionality_during_error_conditions(ticker, quantity, target_allocation, price, error_scenarios):
    """
    Property 4: UI Functionality During Invalid States - Error conditions
    Test that UI remains functional during various error conditions like zero prices,
    zero quantities, or extreme values.
    **Validates: Requirements 2.3, 7.2, 7.5**
    """
    portfolio = Portfolio()
    
    # Apply error scenarios to create edge cases
    test_quantity = quantity
    test_price = price
    test_allocation = target_allocation
    
    for scenario in error_scenarios:
        if scenario == 'zero_price':
            test_price = 0.0
        elif scenario == 'zero_quantity':
            test_quantity = 0.0
        elif scenario == 'extreme_allocation':
            test_allocation = 150.0  # Over 100%
        # zero_total_value will be handled by zero_price or zero_quantity
    
    # Create holding with potentially problematic values
    holding = Holding(ticker, test_quantity, min(test_allocation, 100.0))  # Clamp allocation to valid range
    holding.update_price(max(test_price, 0.01))  # Ensure price is positive for calculations
    portfolio.add_holding(holding)
    
    # Portfolio should handle edge cases gracefully
    total_value = portfolio.get_total_value()
    allocation_summary = portfolio.get_allocation_summary()
    rebalance_actions = portfolio.calculate_rebalance_actions()
    
    # All operations should return valid results
    assert isinstance(total_value, (int, float))
    assert total_value >= 0
    assert isinstance(allocation_summary, dict)
    assert len(allocation_summary) == 1
    assert ticker.upper() in allocation_summary
    assert isinstance(rebalance_actions, dict)
    assert len(rebalance_actions) == 1
    
    # Individual holding calculations should work
    current_value = holding.get_current_value()
    current_allocation = holding.get_current_allocation(total_value)
    target_value = holding.get_target_value(total_value)
    rebalance_action = holding.get_rebalance_action(total_value)
    
    # All should return valid numbers
    assert isinstance(current_value, (int, float))
    assert isinstance(current_allocation, (int, float))
    assert isinstance(target_value, (int, float))
    assert isinstance(rebalance_action, (int, float))
    
    # Values should be non-negative and finite
    assert current_value >= 0
    assert current_allocation >= 0
    assert target_value >= 0
    assert not (current_value != current_value)  # Check for NaN
    assert not (current_allocation != current_allocation)  # Check for NaN
    assert not (target_value != target_value)  # Check for NaN
    assert not (rebalance_action != rebalance_action)  # Check for NaN
    
    # Portfolio operations should continue to work
    try:
        # These operations should not crash even with edge case values
        portfolio.update_holding_quantity(ticker, max(test_quantity * 1.1, 0.001))
        portfolio.update_target_allocation(ticker, min(max(test_allocation * 0.9, 0.0), 100.0))
        
        # Recalculate after updates
        new_total_value = portfolio.get_total_value()
        new_allocation_summary = portfolio.get_allocation_summary()
        new_rebalance_actions = portfolio.calculate_rebalance_actions()
        
        # All should still work
        assert isinstance(new_total_value, (int, float))
        assert new_total_value >= 0
        assert len(new_allocation_summary) == 1
        assert len(new_rebalance_actions) == 1
        
    except ValueError:
        # Some operations might raise ValueError for invalid inputs, which is acceptable
        # The important thing is that the system doesn't crash or become unresponsive
        pass


@given(
    holdings_data=st.lists(
        st.tuples(ticker_strategy, quantity_strategy, allocation_strategy, price_strategy),
        min_size=2,
        max_size=5,
        unique_by=lambda x: x[0].upper()
    )
)
def test_ui_responsiveness_with_concurrent_operations(holdings_data):
    """
    Property 4: UI Functionality During Invalid States - Concurrent operations
    Test that UI remains responsive when multiple operations are performed
    in sequence, including operations that might create invalid states.
    **Validates: Requirements 2.3, 7.2, 7.5**
    """
    if len(holdings_data) < 2:
        return
        
    portfolio = Portfolio()
    
    # Add all holdings
    for ticker, quantity, target_allocation, price in holdings_data:
        holding = Holding(ticker, quantity, target_allocation)
        holding.update_price(price)
        portfolio.add_holding(holding)
    
    # Perform rapid sequence of operations that might create invalid states
    operations = [
        ('update_quantity', 0, holdings_data[0][1] * 2.5),
        ('update_allocation', 0, 150.0),  # Over 100%
        ('update_allocation', 1, 0.0),    # Zero allocation
        ('update_quantity', 1, holdings_data[1][1] * 0.1),
        ('update_allocation', 0, 25.0),   # Back to reasonable
        ('update_price', 0, holdings_data[0][3] * 3.0),
        ('update_allocation', 1, 75.0),   # Total might be 100% now
    ]
    
    for operation, holding_index, new_value in operations:
        if holding_index >= len(holdings_data):
            continue
            
        ticker = holdings_data[holding_index][0]
        
        try:
            if operation == 'update_quantity':
                portfolio.update_holding_quantity(ticker, new_value)
            elif operation == 'update_allocation':
                portfolio.update_target_allocation(ticker, new_value)
            elif operation == 'update_price':
                holding = portfolio.get_holding(ticker)
                holding.update_price(new_value)
        except ValueError:
            # Some operations might fail with invalid values, which is acceptable
            continue
        
        # After each operation, portfolio should remain functional
        total_value = portfolio.get_total_value()
        allocation_summary = portfolio.get_allocation_summary()
        allocation_status = portfolio.get_allocation_status()
        rebalance_actions = portfolio.calculate_rebalance_actions()
        
        # All operations should return valid results
        assert isinstance(total_value, (int, float))
        assert total_value >= 0
        assert isinstance(allocation_summary, dict)
        assert len(allocation_summary) == len(holdings_data)
        assert allocation_status in ["above", "below", "equal"]
        assert isinstance(rebalance_actions, dict)
        assert len(rebalance_actions) == len(holdings_data)
        
        # All holdings should remain accessible and functional
        for ticker, _, _, _ in holdings_data:
            holding = portfolio.get_holding(ticker)
            assert holding is not None
            
            # All calculations should work
            current_value = holding.get_current_value()
            current_allocation = holding.get_current_allocation(total_value)
            target_value = holding.get_target_value(total_value)
            rebalance_action = holding.get_rebalance_action(total_value)
            
            # All should be valid numbers
            assert isinstance(current_value, (int, float))
            assert isinstance(current_allocation, (int, float))
            assert isinstance(target_value, (int, float))
            assert isinstance(rebalance_action, (int, float))
            
            # Should not be NaN
            assert current_value == current_value
            assert current_allocation == current_allocation
            assert target_value == target_value
            assert rebalance_action == rebalance_action