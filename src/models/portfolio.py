"""
Portfolio class for managing a collection of stock holdings.
"""
from typing import Dict, List, Optional
from .holding import Holding


class Portfolio:
    """Manages a collection of stock holdings with portfolio-level calculations."""
    
    def __init__(self):
        """Initialize an empty portfolio."""
        self.holdings: Dict[str, Holding] = {}
    
    def add_holding(self, holding: Holding) -> None:
        """
        Add a new holding to the portfolio.
        
        Args:
            holding: Holding object to add
        """
        self.holdings[holding.ticker] = holding
    
    def remove_holding(self, ticker: str) -> None:
        """
        Remove a holding from the portfolio.
        
        Args:
            ticker: Stock ticker symbol to remove
        """
        ticker = ticker.upper()
        if ticker in self.holdings:
            del self.holdings[ticker]
    
    def get_holding(self, ticker: str) -> Optional[Holding]:
        """
        Get a specific holding by ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Holding object or None if not found
        """
        return self.holdings.get(ticker.upper())
    
    def update_holding_quantity(self, ticker: str, quantity: float) -> None:
        """
        Update the quantity of an existing holding.
        
        Args:
            ticker: Stock ticker symbol
            quantity: New quantity of shares
        """
        ticker = ticker.upper()
        if ticker in self.holdings:
            self.holdings[ticker].quantity = quantity
    
    def update_target_allocation(self, ticker: str, percentage: float) -> None:
        """
        Update the target allocation of an existing holding.
        
        Args:
            ticker: Stock ticker symbol
            percentage: New target allocation percentage (0-100)
            
        Raises:
            ValueError: If percentage is not between 0 and 100
        """
        # Validate target allocation range (Requirement 2.5)
        if not (0.0 <= percentage <= 100.0):
            raise ValueError(f"Target allocation must be between 0% and 100%, got {percentage}%")
            
        ticker = ticker.upper()
        if ticker in self.holdings:
            self.holdings[ticker].target_allocation = percentage
    
    def get_total_value(self) -> float:
        """Calculate total value of all holdings."""
        return sum(holding.get_current_value() for holding in self.holdings.values())
    
    def get_allocation_summary(self) -> Dict[str, float]:
        """
        Get current allocation percentages for all holdings.
        
        Returns:
            Dictionary mapping ticker to current allocation percentage
        """
        total_value = self.get_total_value()
        if total_value <= 0:
            return {ticker: 0.0 for ticker in self.holdings.keys()}
        
        return {
            ticker: holding.get_current_allocation(total_value)
            for ticker, holding in self.holdings.items()
        }
    
    def get_target_allocation_total(self) -> float:
        """Get sum of all target allocations."""
        return sum(holding.target_allocation for holding in self.holdings.values())
    
    def get_allocation_status(self) -> str:
        """
        Get status of target allocation total (Requirement 2.2).
        
        Returns:
            String indicating if allocations are "above", "below", or "equal" to 100%
        """
        total = self.get_target_allocation_total()
        if abs(total - 100.0) < 0.01:  # Allow for floating point precision
            return "equal"
        elif total > 100.0:
            return "above"
        else:
            return "below"
    
    def validate_target_allocation_range(self, percentage: float) -> bool:
        """
        Validate that target allocation is within valid range (Requirement 2.5).
        
        Args:
            percentage: Target allocation percentage to validate
            
        Returns:
            True if valid (0-100%), False otherwise
        """
        return 0.0 <= percentage <= 100.0
    
    def calculate_rebalance_actions(self, rounded: bool = True) -> Dict[str, float]:
        """
        Calculate rebalance actions for all holdings.
        
        Args:
            rounded: Whether to round to whole shares
            
        Returns:
            Dictionary mapping ticker to rebalance action (shares to buy/sell)
        """
        total_value = self.get_total_value()
        return {
            ticker: holding.get_rebalance_action(total_value, rounded)
            for ticker, holding in self.holdings.items()
        }
    
    def get_all_tickers(self) -> List[str]:
        """Get list of all ticker symbols in portfolio."""
        return list(self.holdings.keys())
    
    def is_empty(self) -> bool:
        """Check if portfolio has no holdings."""
        return len(self.holdings) == 0
    
    def __len__(self) -> int:
        """Return number of holdings in portfolio."""
        return len(self.holdings)
    
    def __repr__(self) -> str:
        return f"Portfolio(holdings={len(self.holdings)}, total_value=${self.get_total_value():.2f})"