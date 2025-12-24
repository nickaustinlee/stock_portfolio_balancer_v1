"""
CSV Export Service for the Stock Allocation Tool.

This module provides the CSVExporter class that handles exporting portfolio
data to CSV format with timestamped filenames and proper error handling.
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from models.portfolio import Portfolio


class CSVExporter:
    """
    Service for exporting portfolio data to CSV format.
    
    Provides functionality to:
    - Generate timestamped filenames
    - Format portfolio data for CSV export
    - Write CSV files with proper error handling
    - Handle file system issues gracefully
    """
    
    def __init__(self, default_directory: str = "exports"):
        """
        Initialize the CSV exporter.
        
        Args:
            default_directory: Directory to save CSV files (default: "exports")
        """
        self.default_directory = default_directory
        
    def export_portfolio(self, portfolio: Portfolio, share_rounding: bool = True) -> str:
        """
        Export portfolio data to a CSV file.
        
        Args:
            portfolio: Portfolio object to export
            share_rounding: Whether to use rounded share quantities in rebalance actions
            
        Returns:
            str: Full path to the created CSV file
            
        Raises:
            ValueError: If portfolio is empty
            PermissionError: If unable to write to file system
            OSError: If file system error occurs
        """
        if portfolio.is_empty():
            raise ValueError("Cannot export empty portfolio")
            
        # Generate timestamped filename
        filename = self.generate_filename()
        
        # Create exports directory if it doesn't exist
        os.makedirs(self.default_directory, exist_ok=True)
        filepath = os.path.join(self.default_directory, filename)
        
        # Format portfolio data
        data = self.format_portfolio_data(portfolio, share_rounding)
        
        # Write CSV file
        self.write_csv_file(filepath, data)
        
        return filepath
        
    def generate_filename(self) -> str:
        """
        Generate a timestamped filename for the CSV export.
        
        Returns:
            str: Filename in format "portfolio_YYYY-MM-DD_HH-MM-SS.csv"
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"portfolio_{timestamp}.csv"
        
    def format_portfolio_data(self, portfolio: Portfolio, share_rounding: bool = True) -> List[List[str]]:
        """
        Format portfolio data for CSV export.
        
        Args:
            portfolio: Portfolio object to format
            share_rounding: Whether to use rounded share quantities in rebalance actions
            
        Returns:
            List[List[str]]: List of rows, each row is a list of string values
        """
        if portfolio.is_empty():
            return []
            
        # Calculate portfolio metrics
        total_value = portfolio.get_total_value()
        allocations = portfolio.get_allocation_summary()
        rebalance_actions = portfolio.calculate_rebalance_actions(share_rounding)
        
        # Prepare data rows
        data = []
        
        # Header row
        headers = [
            "Ticker", "Price", "Quantity", "Target Allocation", 
            "Current Allocation", "Current Value", "Target Value", 
            "Difference", "Rebalance Action"
        ]
        data.append(headers)
        
        # Data rows for each holding
        for ticker, holding in portfolio.holdings.items():
            target_value = holding.get_target_value(total_value)
            current_value = holding.get_current_value()
            difference = target_value - current_value
            rebalance_action = rebalance_actions.get(ticker, 0.0)
            
            row = [
                ticker,
                f"${holding.current_price:.2f}",
                f"{holding.quantity:.3f}",
                f"{holding.target_allocation:.1f}%",
                f"{allocations.get(ticker, 0.0):.1f}%",
                f"${current_value:.2f}",
                f"${target_value:.2f}",
                f"${difference:.2f}",
                self._format_rebalance_action(rebalance_action)
            ]
            data.append(row)
            
        return data
        
    def write_csv_file(self, filepath: str, data: List[List[str]]) -> None:
        """
        Write data to a CSV file.
        
        Args:
            filepath: Full path to the CSV file
            data: List of rows to write
            
        Raises:
            PermissionError: If unable to write to the file
            OSError: If file system error occurs
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(data)
        except PermissionError:
            raise PermissionError(f"Cannot write to file {filepath}. Check file permissions.")
        except OSError as e:
            if "No space left on device" in str(e):
                raise OSError("Insufficient disk space for CSV export")
            else:
                raise OSError(f"File system error: {str(e)}")
                
    def _format_rebalance_action(self, action: float) -> str:
        """
        Format rebalance action for display.
        
        Args:
            action: Rebalance action value (positive = buy, negative = sell)
            
        Returns:
            str: Formatted rebalance action string
        """
        if action > 0:
            return f"Buy {action:.3f}"
        elif action < 0:
            return f"Sell {abs(action):.3f}"
        else:
            return "Hold"