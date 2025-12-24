"""
Data persistence layer for portfolio management.
"""
import json
import os
import shutil
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.portfolio import Portfolio
from models.holding import Holding


class DataStorage:
    """Handles JSON serialization and persistence of Portfolio objects."""
    
    def __init__(self, filename: str = "portfolio.json"):
        """
        Initialize data storage with specified filename.
        
        Args:
            filename: Name of the JSON file to store portfolio data
        """
        self.filename = filename
        self.backup_filename = f"{filename}.backup"
        
    def save_portfolio(self, portfolio: Portfolio) -> None:
        """
        Save portfolio to JSON file with backup and error handling.
        
        Args:
            portfolio: Portfolio object to save
            
        Raises:
            PermissionError: If file cannot be written due to permissions
            OSError: If disk space is insufficient or other I/O error occurs
        """
        try:
            # Create backup of existing file if it exists and has content
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                self.backup_data()
            
            # Serialize portfolio to JSON format
            portfolio_data = self._serialize_portfolio(portfolio)
            
            # Write to temporary file first, then rename for atomic operation
            temp_filename = f"{self.filename}.tmp"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump(portfolio_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename to final filename
            os.rename(temp_filename, self.filename)
            
        except PermissionError:
            # Clean up temp file if it exists
            if os.path.exists(f"{self.filename}.tmp"):
                os.remove(f"{self.filename}.tmp")
            raise PermissionError("Cannot save portfolio, check file permissions")
        except OSError as e:
            # Clean up temp file if it exists
            if os.path.exists(f"{self.filename}.tmp"):
                os.remove(f"{self.filename}.tmp")
            if "No space left on device" in str(e):
                raise OSError("Insufficient disk space for saving portfolio")
            raise OSError(f"Error saving portfolio: {e}")
    
    def load_portfolio(self) -> Portfolio:
        """
        Load portfolio from JSON file with corruption detection and recovery.
        
        Returns:
            Portfolio object loaded from file, or empty portfolio if file doesn't exist
            
        Raises:
            ValueError: If data corruption is detected and cannot be recovered
        """
        # If main file doesn't exist, return empty portfolio
        if not os.path.exists(self.filename):
            return Portfolio()
        
        try:
            # Try to load main file
            with open(self.filename, 'r', encoding='utf-8') as f:
                portfolio_data = json.load(f)
            
            # Validate and deserialize
            return self._deserialize_portfolio(portfolio_data)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Main file is corrupted, try backup
            if os.path.exists(self.backup_filename):
                try:
                    with open(self.backup_filename, 'r', encoding='utf-8') as f:
                        portfolio_data = json.load(f)
                    
                    # Validate and deserialize backup
                    portfolio = self._deserialize_portfolio(portfolio_data)
                    
                    # Restore from backup by saving it as main file
                    self.save_portfolio(portfolio)
                    
                    return portfolio
                    
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Both files corrupted
                    raise ValueError("Portfolio data corrupted, starting fresh")
            else:
                # No backup available
                raise ValueError("Portfolio data corrupted, starting fresh")
        except OSError as e:
            raise OSError(f"Error loading portfolio: {e}")
    
    def backup_data(self) -> None:
        """
        Create backup copy of current portfolio file.
        
        Raises:
            OSError: If backup cannot be created
        """
        if os.path.exists(self.filename):
            try:
                shutil.copy2(self.filename, self.backup_filename)
            except OSError as e:
                raise OSError(f"Cannot create backup: {e}")
    
    def _serialize_portfolio(self, portfolio: Portfolio) -> Dict[str, Any]:
        """
        Convert Portfolio object to JSON-serializable dictionary.
        
        Args:
            portfolio: Portfolio object to serialize
            
        Returns:
            Dictionary representation of portfolio
        """
        holdings_data = []
        for ticker, holding in portfolio.holdings.items():
            holding_data = {
                "ticker": holding.ticker,
                "quantity": holding.quantity,
                "target_allocation": holding.target_allocation,
                "last_price": holding.current_price,
                "last_updated": holding.last_updated.isoformat() if holding.last_updated else None
            }
            holdings_data.append(holding_data)
        
        return {
            "version": "1.0",
            "last_saved": datetime.now().isoformat(),
            "holdings": holdings_data
        }
    
    def _deserialize_portfolio(self, data: Dict[str, Any]) -> Portfolio:
        """
        Convert JSON dictionary to Portfolio object.
        
        Args:
            data: Dictionary representation of portfolio
            
        Returns:
            Portfolio object
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If data format is invalid
        """
        # Validate required fields
        if "holdings" not in data:
            raise KeyError("Missing 'holdings' field in portfolio data")
        
        if not isinstance(data["holdings"], list):
            raise ValueError("'holdings' field must be a list")
        
        portfolio = Portfolio()
        
        for holding_data in data["holdings"]:
            # Validate required holding fields
            required_fields = ["ticker", "quantity", "target_allocation"]
            for field in required_fields:
                if field not in holding_data:
                    raise KeyError(f"Missing '{field}' field in holding data")
            
            # Create holding object
            holding = Holding(
                ticker=holding_data["ticker"],
                quantity=float(holding_data["quantity"]),
                target_allocation=float(holding_data["target_allocation"])
            )
            
            # Set price and timestamp if available
            if "last_price" in holding_data and holding_data["last_price"] is not None:
                holding.current_price = float(holding_data["last_price"])
            
            if "last_updated" in holding_data and holding_data["last_updated"] is not None:
                try:
                    holding.last_updated = datetime.fromisoformat(holding_data["last_updated"])
                except ValueError:
                    # Invalid timestamp format, leave as None
                    holding.last_updated = None
            
            portfolio.add_holding(holding)
        
        return portfolio
    
    def file_exists(self) -> bool:
        """Check if portfolio file exists."""
        return os.path.exists(self.filename)
    
    def backup_exists(self) -> bool:
        """Check if backup file exists."""
        return os.path.exists(self.backup_filename)
    
    def get_file_size(self) -> int:
        """
        Get size of portfolio file in bytes.
        
        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        if os.path.exists(self.filename):
            return os.path.getsize(self.filename)
        return 0
    
    def get_last_modified(self) -> Optional[datetime]:
        """
        Get last modification time of portfolio file.
        
        Returns:
            Datetime of last modification, or None if file doesn't exist
        """
        if os.path.exists(self.filename):
            timestamp = os.path.getmtime(self.filename)
            return datetime.fromtimestamp(timestamp)
        return None