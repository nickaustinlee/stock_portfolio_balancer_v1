"""
Stock Price Service for fetching real-time stock prices from Yahoo Finance.

This module provides the StockPriceService class that integrates with yfinance
to fetch current stock prices, validate ticker symbols, and handle API errors
gracefully according to requirements 3.1, 3.4, 8.1, and 8.2.
"""

import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime
import logging


class StockPriceService:
    """
    Service for fetching stock prices from Yahoo Finance API.
    
    Provides methods for single and multiple ticker price requests,
    ticker validation, price caching, and comprehensive error handling.
    """
    
    def __init__(self):
        """Initialize the stock price service with empty cache."""
        self.cache: Dict[str, Dict] = {}
        self.last_refresh: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)
    
    def get_current_price(self, ticker: str) -> float:
        """
        Get current price for a single ticker symbol.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Current stock price as float
            
        Raises:
            ValueError: If ticker is invalid or not found
            ConnectionError: If API is unavailable
            TimeoutError: If request times out
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        ticker = ticker.upper().strip()
        
        # Check if ticker is empty after stripping
        if not ticker:
            raise ValueError("Ticker must be a non-empty string")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if ticker is valid by looking for price data
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if current_price is None:
                # Try getting price from history as fallback
                hist = stock.history(period="1d")
                if hist.empty:
                    raise ValueError(f"{ticker} not found")
                current_price = float(hist['Close'].iloc[-1])
            
            # Update cache
            self.cache[ticker] = {
                'price': float(current_price),
                'last_updated': datetime.now(),
                'info': info
            }
            
            return float(current_price)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "empty ticker" in error_msg or "not found" in error_msg or "invalid" in error_msg:
                raise ValueError(f"{ticker} not found")
            elif "network" in error_msg or "connection" in error_msg:
                raise ConnectionError("Yahoo Finance isn't working, try again later")
            elif "timeout" in error_msg:
                raise TimeoutError("Request timed out, retrying with cached data")
            else:
                self.logger.error(f"Unexpected error fetching price for {ticker}: {e}")
                raise ConnectionError("Yahoo Finance isn't working, try again later")
    
    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Get current prices for multiple ticker symbols.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dictionary mapping ticker symbols to current prices
            
        Note:
            Invalid tickers are skipped and logged as warnings.
            Partial results are returned if some tickers fail.
        """
        if not tickers:
            return {}
        
        prices = {}
        failed_tickers = []
        
        # Clean and validate tickers
        clean_tickers = [t.upper().strip() for t in tickers if t and isinstance(t, str)]
        
        for ticker in clean_tickers:
            try:
                price = self.get_current_price(ticker)
                prices[ticker] = price
            except ValueError as e:
                self.logger.warning(f"Invalid ticker {ticker}: {e}")
                failed_tickers.append(ticker)
            except (ConnectionError, TimeoutError) as e:
                self.logger.warning(f"Failed to fetch price for {ticker}: {e}")
                failed_tickers.append(ticker)
        
        if failed_tickers:
            self.logger.info(f"Failed to fetch prices for: {failed_tickers}")
        
        self.last_refresh = datetime.now()
        return prices
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol exists and can be fetched.
        
        Args:
            ticker: Stock ticker symbol to validate
            
        Returns:
            True if ticker is valid, False otherwise
        """
        if not ticker or not isinstance(ticker, str):
            return False
        
        try:
            self.get_current_price(ticker)
            return True
        except (ValueError, ConnectionError, TimeoutError):
            return False
    
    def get_cached_price(self, ticker: str) -> Optional[float]:
        """
        Get cached price for a ticker if available.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Cached price if available, None otherwise
        """
        ticker = ticker.upper().strip()
        cached_data = self.cache.get(ticker)
        if cached_data:
            return cached_data['price']
        return None
    
    def get_cache_timestamp(self, ticker: str) -> Optional[datetime]:
        """
        Get the timestamp when a ticker was last updated in cache.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Timestamp of last update, None if not cached
        """
        ticker = ticker.upper().strip()
        cached_data = self.cache.get(ticker)
        if cached_data:
            return cached_data['last_updated']
        return None
    
    def clear_cache(self) -> None:
        """Clear all cached price data."""
        self.cache.clear()
        self.last_refresh = None