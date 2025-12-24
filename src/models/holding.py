"""
Holding class for individual stock positions.
"""
from datetime import datetime
from typing import Optional


class Holding:
    """Represents a single stock holding with quantity and target allocation."""
    
    def __init__(self, ticker: str, quantity: float, target_allocation: float = 0.0):
        """
        Initialize a new holding.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            quantity: Number of shares owned
            target_allocation: Desired percentage of total portfolio (0-100)
            
        Raises:
            ValueError: If target_allocation is not between 0 and 100
        """
        # Validate target allocation range (Requirement 2.5)
        if not (0.0 <= target_allocation <= 100.0):
            raise ValueError(f"Target allocation must be between 0% and 100%, got {target_allocation}%")
            
        self.ticker = ticker.upper()
        self.quantity = quantity
        self.target_allocation = target_allocation
        self.current_price = 0.0
        self.last_updated: Optional[datetime] = None
    
    def get_current_value(self) -> float:
        """Calculate current value of this holding."""
        return self.quantity * self.current_price
    
    def get_current_allocation(self, total_portfolio_value: float) -> float:
        """
        Calculate current allocation percentage.
        
        Args:
            total_portfolio_value: Total value of entire portfolio
            
        Returns:
            Current allocation as percentage (0-100)
        """
        if total_portfolio_value <= 0:
            return 0.0
        return (self.get_current_value() / total_portfolio_value) * 100
    
    def get_target_value(self, total_portfolio_value: float) -> float:
        """
        Calculate target value based on target allocation.
        
        Args:
            total_portfolio_value: Total value of entire portfolio
            
        Returns:
            Target value in dollars
        """
        return (self.target_allocation / 100) * total_portfolio_value
    
    def get_rebalance_action(self, total_portfolio_value: float, rounded: bool = True) -> float:
        """
        Calculate rebalance action (shares to buy/sell).
        
        Args:
            total_portfolio_value: Total value of entire portfolio
            rounded: Whether to round to whole shares
            
        Returns:
            Number of shares to buy (positive) or sell (negative)
        """
        if self.current_price <= 0:
            return 0.0
            
        target_value = self.get_target_value(total_portfolio_value)
        current_value = self.get_current_value()
        difference = target_value - current_value
        shares_action = difference / self.current_price
        
        if rounded:
            return round(shares_action)
        return shares_action
    
    def update_price(self, price: float) -> None:
        """Update current price and timestamp."""
        self.current_price = price
        self.last_updated = datetime.now()
    
    def __repr__(self) -> str:
        return f"Holding(ticker='{self.ticker}', quantity={self.quantity}, target_allocation={self.target_allocation}%)"