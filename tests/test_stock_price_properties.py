"""
Property-based tests for stock price service integration.
Feature: stock-allocation-tool, Property 5: Stock Price Integration
Feature: stock-allocation-tool, Property 11: Error Handling with Graceful Degradation
"""
import pytest
from hypothesis import given, strategies as st, assume
import sys
import os
from unittest.mock import patch, MagicMock
import yfinance as yf

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.stock_price_service import StockPriceService


# Strategies for generating test data
valid_ticker_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu',)), 
    min_size=3, 
    max_size=5
)

price_strategy = st.floats(
    min_value=0.01, 
    max_value=10000.0, 
    allow_nan=False, 
    allow_infinity=False
)

# Strategy for generating realistic ticker lists
ticker_list_strategy = st.lists(
    valid_ticker_strategy,
    min_size=1,
    max_size=10,
    unique=True
)


@given(
    ticker=valid_ticker_strategy,
    mock_price=price_strategy
)
def test_stock_price_integration_single_ticker(ticker, mock_price):
    """
    Property 5: Stock Price Integration
    For any valid ticker symbol, the system should successfully fetch prices from the API 
    and update all price-dependent calculations correctly.
    **Validates: Requirements 3.1, 3.2**
    """
    service = StockPriceService()
    
    # Mock yfinance to return predictable data
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = MagicMock()
        mock_ticker.info = {'currentPrice': mock_price}
        mock_ticker_class.return_value = mock_ticker
        
        # Test single ticker price fetch (Requirement 3.1)
        result_price = service.get_current_price(ticker)
        
        # Verify price is returned correctly
        assert isinstance(result_price, float)
        assert result_price == mock_price
        
        # Verify ticker was called with correct symbol
        mock_ticker_class.assert_called_once_with(ticker.upper())
        
        # Verify price is cached (Requirement 3.2)
        cached_price = service.get_cached_price(ticker)
        assert cached_price == mock_price
        
        # Verify cache timestamp is set
        cache_timestamp = service.get_cache_timestamp(ticker)
        assert cache_timestamp is not None
        
        # Test that subsequent calls use cache efficiently
        # (This is implied by the caching mechanism)
        assert ticker.upper() in service.cache


@given(
    ticker_list=ticker_list_strategy,
    mock_prices=st.lists(
        price_strategy,
        min_size=1,
        max_size=10
    )
)
def test_stock_price_integration_multiple_tickers(ticker_list, mock_prices):
    """
    Property 5: Stock Price Integration - Multiple tickers
    For any list of valid ticker symbols, the system should successfully fetch prices 
    and handle partial failures gracefully.
    **Validates: Requirements 3.1, 3.2**
    """
    assume(len(ticker_list) <= len(mock_prices))
    
    service = StockPriceService()
    
    # Create mock responses for each ticker
    def mock_ticker_side_effect(ticker):
        mock_ticker = MagicMock()
        ticker_index = ticker_list.index(ticker) if ticker in ticker_list else 0
        price_index = min(ticker_index, len(mock_prices) - 1)
        mock_ticker.info = {'currentPrice': mock_prices[price_index]}
        return mock_ticker
    
    with patch('yfinance.Ticker', side_effect=mock_ticker_side_effect):
        # Test multiple ticker price fetch (Requirement 3.1)
        result_prices = service.get_multiple_prices(ticker_list)
        
        # Verify all tickers were processed
        assert isinstance(result_prices, dict)
        assert len(result_prices) == len(ticker_list)
        
        # Verify each ticker has correct price
        for i, ticker in enumerate(ticker_list):
            expected_price = mock_prices[min(i, len(mock_prices) - 1)]
            assert ticker.upper() in result_prices
            assert result_prices[ticker.upper()] == expected_price
        
        # Verify all prices are cached (Requirement 3.2)
        for ticker in ticker_list:
            cached_price = service.get_cached_price(ticker)
            assert cached_price is not None
            assert ticker.upper() in service.cache
        
        # Verify last_refresh timestamp is updated
        assert service.last_refresh is not None


@given(
    ticker=valid_ticker_strategy
)
def test_stock_price_integration_with_fallback_history(ticker):
    """
    Property 5: Stock Price Integration - Fallback to history data
    When currentPrice is not available, system should fall back to historical data.
    **Validates: Requirements 3.1, 3.2**
    """
    service = StockPriceService()
    mock_price = 123.45
    
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = MagicMock()
        # Simulate missing currentPrice in info
        mock_ticker.info = {'regularMarketPrice': None}
        
        # Mock history data as fallback
        import pandas as pd
        mock_history = pd.DataFrame({
            'Close': [mock_price]
        })
        mock_ticker.history.return_value = mock_history
        mock_ticker_class.return_value = mock_ticker
        
        # Test fallback mechanism (Requirement 3.1)
        result_price = service.get_current_price(ticker)
        
        # Verify fallback worked
        assert result_price == mock_price
        
        # Verify history was called when info didn't have price
        mock_ticker.history.assert_called_once_with(period="1d")
        
        # Verify price is still cached properly (Requirement 3.2)
        cached_price = service.get_cached_price(ticker)
        assert cached_price == mock_price


@given(
    ticker=valid_ticker_strategy
)
def test_ticker_validation_property(ticker):
    """
    Property 5: Stock Price Integration - Ticker validation
    The system should correctly validate ticker symbols.
    **Validates: Requirements 3.1, 3.2**
    """
    service = StockPriceService()
    
    # Test with valid ticker (mocked)
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = MagicMock()
        mock_ticker.info = {'currentPrice': 100.0}
        mock_ticker_class.return_value = mock_ticker
        
        # Valid ticker should return True
        is_valid = service.validate_ticker(ticker)
        assert is_valid == True
        
        # Should also cache the price during validation
        cached_price = service.get_cached_price(ticker)
        assert cached_price == 100.0


@given(
    invalid_ticker=st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
        st.just("INVALID_TICKER_THAT_DOES_NOT_EXIST"),  # Invalid ticker
        st.integers(),  # Non-string type
        st.none()  # None value
    )
)
def test_error_handling_invalid_ticker(invalid_ticker):
    """
    Property 11: Error Handling with Graceful Degradation - Invalid tickers
    For any invalid ticker, the system should display appropriate error messages 
    while maintaining existing data and functionality.
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
    """
    service = StockPriceService()
    
    if invalid_ticker is None or not isinstance(invalid_ticker, str):
        # Test non-string inputs (Requirement 8.1)
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            service.get_current_price(invalid_ticker)
        
        # Validation should return False for invalid types
        assert service.validate_ticker(invalid_ticker) == False
        
    elif not invalid_ticker.strip():
        # Test empty/whitespace strings (Requirement 8.1)
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            service.get_current_price(invalid_ticker)
        
        assert service.validate_ticker(invalid_ticker) == False
        
    else:
        # Test invalid ticker symbols (Requirement 8.1)
        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = {}  # Empty info indicates invalid ticker
            mock_ticker.history.return_value = pd.DataFrame()  # Empty history
            mock_ticker_class.return_value = mock_ticker
            
            # Should raise ValueError with specific message format
            with pytest.raises(ValueError, match=f"{invalid_ticker.upper().strip()} not found"):
                service.get_current_price(invalid_ticker)
            
            # Validation should return False
            assert service.validate_ticker(invalid_ticker) == False


@given(
    ticker=valid_ticker_strategy
)
def test_error_handling_api_failures(ticker):
    """
    Property 11: Error Handling with Graceful Degradation - API failures
    For any API failure condition, the system should handle errors gracefully 
    and maintain existing data and functionality.
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
    """
    service = StockPriceService()
    
    # Test network/connection errors (Requirement 8.2)
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker_class.side_effect = ConnectionError("Network error")
        
        with pytest.raises(ConnectionError, match="Yahoo Finance isn't working, try again later"):
            service.get_current_price(ticker)
        
        # Validation should handle the error gracefully
        assert service.validate_ticker(ticker) == False
    
    # Test timeout errors (Requirement 8.3)
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker_class.side_effect = TimeoutError("Request timeout")
        
        with pytest.raises(TimeoutError, match="Request timed out, retrying with cached data"):
            service.get_current_price(ticker)
    
    # Test generic API errors (Requirement 8.2)
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker_class.side_effect = Exception("Generic API error")
        
        with pytest.raises(ConnectionError, match="Yahoo Finance isn't working, try again later"):
            service.get_current_price(ticker)


@given(
    ticker_list=ticker_list_strategy
)
def test_error_handling_partial_failures_multiple_tickers(ticker_list):
    """
    Property 11: Error Handling with Graceful Degradation - Partial failures
    For any mix of valid and invalid tickers, the system should return partial results 
    and handle failures gracefully without blocking successful operations.
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
    """
    assume(len(ticker_list) >= 2)  # Need at least 2 tickers for partial failure test
    
    service = StockPriceService()
    
    def mock_ticker_side_effect(ticker):
        mock_ticker = MagicMock()
        # Make every other ticker fail
        ticker_index = ticker_list.index(ticker) if ticker in ticker_list else 0
        if ticker_index % 2 == 0:
            # Success case
            mock_ticker.info = {'currentPrice': 100.0 + ticker_index}
            return mock_ticker
        else:
            # Failure case
            raise ConnectionError("API error for this ticker")
    
    with patch('yfinance.Ticker', side_effect=mock_ticker_side_effect):
        # Test partial failure handling (Requirements 8.4, 8.5, 8.6)
        result_prices = service.get_multiple_prices(ticker_list)
        
        # Should return partial results (successful tickers only)
        assert isinstance(result_prices, dict)
        
        # Count expected successful tickers (even indices)
        expected_successful = sum(1 for i in range(len(ticker_list)) if i % 2 == 0)
        assert len(result_prices) == expected_successful
        
        # Verify successful tickers have correct prices
        for i, ticker in enumerate(ticker_list):
            if i % 2 == 0:  # Should be successful
                assert ticker.upper() in result_prices
                assert result_prices[ticker.upper()] == 100.0 + i
            else:  # Should have failed
                assert ticker.upper() not in result_prices
        
        # Verify last_refresh is still updated despite partial failures
        assert service.last_refresh is not None


@given(
    ticker=valid_ticker_strategy,
    mock_price=price_strategy
)
def test_error_handling_maintains_cache_integrity(ticker, mock_price):
    """
    Property 11: Error Handling with Graceful Degradation - Cache integrity
    For any error condition, the system should maintain cache integrity and 
    existing cached data should remain accessible.
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
    """
    service = StockPriceService()
    
    # First, successfully cache a price
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = MagicMock()
        mock_ticker.info = {'currentPrice': mock_price}
        mock_ticker_class.return_value = mock_ticker
        
        service.get_current_price(ticker)
        
        # Verify price is cached
        assert service.get_cached_price(ticker) == mock_price
        original_cache_size = len(service.cache)
    
    # Now simulate an error condition for a different operation
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker_class.side_effect = ConnectionError("API error")
        
        # Try to fetch price for same ticker (should fail)
        with pytest.raises(ConnectionError):
            service.get_current_price(ticker)
        
        # Verify cached data is still intact (Requirement 8.6)
        assert service.get_cached_price(ticker) == mock_price
        assert len(service.cache) == original_cache_size
        assert ticker.upper() in service.cache
        
        # Verify cache timestamp is preserved
        cache_timestamp = service.get_cache_timestamp(ticker)
        assert cache_timestamp is not None


def test_error_handling_empty_ticker_list():
    """
    Property 11: Error Handling with Graceful Degradation - Edge cases
    The system should handle edge cases like empty ticker lists gracefully.
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
    """
    service = StockPriceService()
    
    # Empty list should return empty dict, not error
    result = service.get_multiple_prices([])
    assert result == {}
    
    # None list should return empty dict
    result = service.get_multiple_prices(None)
    assert result == {}
    
    # List with None/invalid elements should be filtered out
    result = service.get_multiple_prices([None, "", "   ", 123])
    assert result == {}


# Import pandas for the fallback history test
import pandas as pd