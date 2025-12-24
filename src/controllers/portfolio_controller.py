"""
Portfolio Controller for the Stock Allocation Tool.

This module provides the PortfolioController class that acts as the main
application controller, connecting GUI components to data models and services.
Handles user input events, manages application state, and coordinates between
different components according to MVC architecture.
"""

import os
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any
import csv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.portfolio import Portfolio
from models.holding import Holding
from services.stock_price_service import StockPriceService
from services.data_storage import DataStorage
from gui.main_window import MainWindow
from gui.portfolio_table import PortfolioTable


class PortfolioController:
    """
    Main application controller that coordinates between GUI, models, and services.
    
    Implements the Controller component of the MVC architecture, handling:
    - User input events from GUI
    - Data model updates and persistence
    - Stock price service integration
    - Auto-refresh functionality
    - Theme management
    - CSV export functionality
    """
    
    def __init__(self):
        """Initialize the controller with default settings."""
        # Core components
        self.portfolio = Portfolio()
        self.stock_service = StockPriceService()
        self.storage = DataStorage()
        
        # GUI components
        self.main_window: Optional[MainWindow] = None
        self.portfolio_table: Optional[PortfolioTable] = None
        
        # Application state
        self.auto_refresh_timer: Optional[threading.Timer] = None
        self.share_rounding_enabled = True
        self.dark_mode_enabled = False
        self.auto_refresh_enabled = False
        
        # Theme colors
        self.light_colors = {
            "bg": "#ffffff",
            "fg": "#000000", 
            "table_bg": "#f8f9fa",
            "button_bg": "#e9ecef",
            "accent": "#007bff"
        }
        self.dark_colors = {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "table_bg": "#3c3c3c", 
            "button_bg": "#4a4a4a",
            "accent": "#0d6efd"
        }
        
    def initialize_gui(self):
        """Initialize and set up the GUI components."""
        # Create main window
        self.main_window = MainWindow("Stock Allocation Tool")
        
        # Create portfolio table
        self.portfolio_table = PortfolioTable(self.main_window.table_frame)
        self.main_window.set_portfolio_table(self.portfolio_table)
        
        # Connect GUI callbacks
        self._connect_gui_callbacks()
        
        # Load saved portfolio data
        self.load_portfolio()
        
        # Update GUI with initial data
        self._update_gui()
        
    def _connect_gui_callbacks(self):
        """Connect GUI event callbacks to controller methods."""
        if not self.main_window or not self.portfolio_table:
            return
            
        # Main window callbacks
        self.main_window.on_refresh = self.refresh_prices
        self.main_window.on_auto_refresh_toggle = self.toggle_auto_refresh
        self.main_window.on_share_rounding_toggle = self.toggle_share_rounding
        self.main_window.on_dark_mode_toggle = self.toggle_dark_mode
        self.main_window.on_csv_export = self.export_to_csv
        
        # Portfolio table callbacks
        self.portfolio_table.on_holding_added = self.add_holding
        self.portfolio_table.on_holding_removed = self.remove_holding
        self.portfolio_table.on_quantity_changed = self.update_holding_quantity
        self.portfolio_table.on_target_allocation_changed = self.update_target_allocation
        
    def add_holding(self, ticker: str, quantity: float) -> None:
        """
        Add a new holding to the portfolio.
        
        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
        """
        try:
            # Validate ticker by attempting to fetch price
            try:
                price = self.stock_service.get_current_price(ticker)
            except ValueError:
                self._show_error("Invalid Ticker", f"{ticker} not found")
                return
            except (ConnectionError, TimeoutError) as e:
                self._show_error("API Error", str(e))
                return
            
            # Create new holding
            holding = Holding(ticker=ticker, quantity=quantity)
            holding.current_price = price
            holding.last_updated = datetime.now()
            
            # Add to portfolio
            self.portfolio.add_holding(holding)
            
            # Save and update GUI
            self.save_portfolio()
            self._update_gui()
            
            self._update_status(f"Added {quantity} shares of {ticker}")
            
        except Exception as e:
            self._show_error("Error", f"Failed to add holding: {str(e)}")
            
    def remove_holding(self, ticker: str) -> None:
        """
        Remove a holding from the portfolio.
        
        Args:
            ticker: Stock ticker symbol to remove
        """
        try:
            self.portfolio.remove_holding(ticker)
            self.save_portfolio()
            self._update_gui()
            self._update_status(f"Removed {ticker} from portfolio")
            
        except Exception as e:
            self._show_error("Error", f"Failed to remove holding: {str(e)}")
            
    def update_holding_quantity(self, ticker: str, quantity: float) -> None:
        """
        Update the quantity of an existing holding.
        
        Args:
            ticker: Stock ticker symbol
            quantity: New quantity of shares
        """
        try:
            self.portfolio.update_holding_quantity(ticker, quantity)
            self.save_portfolio()
            self._update_gui()
            self._update_status(f"Updated {ticker} quantity to {quantity}")
            
        except Exception as e:
            self._show_error("Error", f"Failed to update quantity: {str(e)}")
            
    def update_target_allocation(self, ticker: str, percentage: float) -> None:
        """
        Update the target allocation of an existing holding.
        
        Args:
            ticker: Stock ticker symbol
            percentage: New target allocation percentage (0-100)
        """
        try:
            self.portfolio.update_target_allocation(ticker, percentage)
            self.save_portfolio()
            self._update_gui()
            self._update_status(f"Updated {ticker} target allocation to {percentage}%")
            
        except ValueError as e:
            self._show_error("Invalid Allocation", str(e))
        except Exception as e:
            self._show_error("Error", f"Failed to update allocation: {str(e)}")
            
    def refresh_prices(self) -> None:
        """Manually refresh stock prices for all holdings."""
        if self.portfolio.is_empty():
            self._update_status("No holdings to refresh")
            return
            
        self._update_status("Refreshing prices...")
        
        # Run price refresh in background thread to avoid blocking GUI
        def refresh_thread():
            try:
                tickers = self.portfolio.get_all_tickers()
                prices = self.stock_service.get_multiple_prices(tickers)
                
                # Update holdings with new prices
                for ticker, price in prices.items():
                    holding = self.portfolio.get_holding(ticker)
                    if holding:
                        holding.current_price = price
                        holding.last_updated = datetime.now()
                
                # Update GUI on main thread
                if self.main_window:
                    self.main_window.root.after(0, self._on_refresh_complete)
                    
            except Exception as e:
                if self.main_window:
                    self.main_window.root.after(0, lambda: self._show_error("Refresh Error", str(e)))
                    
        thread = threading.Thread(target=refresh_thread, daemon=True)
        thread.start()
        
    def _on_refresh_complete(self):
        """Handle completion of price refresh."""
        self.save_portfolio()
        self._update_gui()
        
        # Update last refresh timestamp
        if self.main_window and self.stock_service.last_refresh:
            timestamp = self.stock_service.last_refresh.strftime("%Y-%m-%d %H:%M:%S")
            self.main_window.update_last_refresh(timestamp)
            
        self._update_status("Prices refreshed successfully")
        
    def toggle_auto_refresh(self, enabled: bool) -> None:
        """
        Toggle auto-refresh functionality.
        
        Args:
            enabled: True to enable auto-refresh, False to disable
        """
        self.auto_refresh_enabled = enabled
        
        if enabled:
            self._start_auto_refresh()
            self._update_status("Auto-refresh enabled (60s intervals)")
        else:
            self._stop_auto_refresh()
            self._update_status("Auto-refresh disabled")
            
    def _start_auto_refresh(self):
        """Start the auto-refresh timer."""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.cancel()
            
        def auto_refresh_task():
            if self.auto_refresh_enabled and not self.portfolio.is_empty():
                self.refresh_prices()
            
            # Schedule next refresh
            if self.auto_refresh_enabled:
                self.auto_refresh_timer = threading.Timer(60.0, auto_refresh_task)
                self.auto_refresh_timer.daemon = True
                self.auto_refresh_timer.start()
                
        self.auto_refresh_timer = threading.Timer(60.0, auto_refresh_task)
        self.auto_refresh_timer.daemon = True
        self.auto_refresh_timer.start()
        
    def _stop_auto_refresh(self):
        """Stop the auto-refresh timer."""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.cancel()
            self.auto_refresh_timer = None
            
    def toggle_share_rounding(self, enabled: bool) -> None:
        """
        Toggle share rounding in rebalance calculations.
        
        Args:
            enabled: True to enable rounding, False for exact fractional shares
        """
        self.share_rounding_enabled = enabled
        self._update_gui()
        
        status = "enabled" if enabled else "disabled"
        self._update_status(f"Share rounding {status}")
        
    def toggle_dark_mode(self, enabled: bool) -> None:
        """
        Toggle dark mode theme.
        
        Args:
            enabled: True to enable dark mode, False for light mode
        """
        self.dark_mode_enabled = enabled
        self._apply_theme()
        
        mode = "dark" if enabled else "light"
        self._update_status(f"Switched to {mode} mode")
        
    def _apply_theme(self):
        """Apply the current theme to all GUI components."""
        if not self.main_window:
            return
            
        colors = self.dark_colors if self.dark_mode_enabled else self.light_colors
        
        # Apply theme to main window
        self.main_window.root.configure(bg=colors["bg"])
        
        # Note: Full theme implementation would require more extensive
        # styling of individual widgets. This is a basic implementation.
        
    def export_to_csv(self) -> None:
        """Export current portfolio data to CSV file."""
        try:
            if self.portfolio.is_empty():
                self._show_info("Export", "No portfolio data to export")
                return
                
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"portfolio_{timestamp}.csv"
            
            # Create exports directory if it doesn't exist
            os.makedirs("exports", exist_ok=True)
            filepath = os.path.join("exports", filename)
            
            # Prepare data for export
            holdings_data = self._get_portfolio_display_data()
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = [
                    "Ticker", "Price", "Quantity", "Target Allocation", 
                    "Current Allocation", "Current Value", "Target Value", 
                    "Difference", "Rebalance Action"
                ]
                writer.writerow(headers)
                
                # Write data rows
                for ticker, data in holdings_data.items():
                    row = [
                        ticker,
                        f"${data.get('price', 0):.2f}",
                        f"{data.get('quantity', 0):.3f}",
                        f"{data.get('target_allocation', 0):.1f}%",
                        f"{data.get('current_allocation', 0):.1f}%",
                        f"${data.get('current_value', 0):.2f}",
                        f"${data.get('target_value', 0):.2f}",
                        f"${data.get('difference', 0):.2f}",
                        self._format_rebalance_action(data.get('rebalance_action', 0))
                    ]
                    writer.writerow(row)
                    
            self._show_info("Export Successful", f"Portfolio exported to {filepath}")
            self._update_status(f"Exported to {filepath}")
            
        except Exception as e:
            self._show_error("Export Error", f"Failed to export portfolio: {str(e)}")
            
    def _format_rebalance_action(self, action: float) -> str:
        """Format rebalance action for display."""
        if action > 0:
            return f"Buy {action:.3f}"
        elif action < 0:
            return f"Sell {abs(action):.3f}"
        else:
            return "Hold"
            
    def save_portfolio(self) -> None:
        """Save the current portfolio to persistent storage."""
        try:
            self.storage.save_portfolio(self.portfolio)
        except Exception as e:
            self._show_error("Save Error", f"Failed to save portfolio: {str(e)}")
            
    def load_portfolio(self) -> None:
        """Load portfolio from persistent storage."""
        try:
            self.portfolio = self.storage.load_portfolio()
        except ValueError as e:
            # Data corruption detected
            self._show_warning("Data Corruption", str(e))
            self.portfolio = Portfolio()
        except Exception as e:
            self._show_error("Load Error", f"Failed to load portfolio: {str(e)}")
            self.portfolio = Portfolio()
            
    def _update_gui(self):
        """Update all GUI components with current portfolio data."""
        if not self.portfolio_table:
            return
            
        # Get portfolio display data
        holdings_data = self._get_portfolio_display_data()
        
        # Update portfolio table
        self.portfolio_table.update_holdings(holdings_data)
        
        # Update status with allocation summary
        self._update_allocation_status()
        
    def _get_portfolio_display_data(self) -> Dict[str, Dict[str, Any]]:
        """Get portfolio data formatted for display."""
        if self.portfolio.is_empty():
            return {}
            
        total_value = self.portfolio.get_total_value()
        allocations = self.portfolio.get_allocation_summary()
        rebalance_actions = self.portfolio.calculate_rebalance_actions(self.share_rounding_enabled)
        
        display_data = {}
        
        for ticker, holding in self.portfolio.holdings.items():
            target_value = holding.get_target_value(total_value)
            current_value = holding.get_current_value()
            difference = target_value - current_value
            
            display_data[ticker] = {
                'ticker': ticker,
                'price': holding.current_price,
                'quantity': holding.quantity,
                'target_allocation': holding.target_allocation,
                'current_allocation': allocations.get(ticker, 0.0),
                'current_value': current_value,
                'target_value': target_value,
                'difference': difference,
                'rebalance_action': rebalance_actions.get(ticker, 0.0)
            }
            
        return display_data
        
    def _update_allocation_status(self):
        """Update status bar with allocation summary."""
        if not self.main_window:
            return
            
        total_allocation = self.portfolio.get_target_allocation_total()
        status = self.portfolio.get_allocation_status()
        
        if status == "equal":
            message = f"Target allocations: {total_allocation:.1f}% (Balanced)"
        elif status == "above":
            message = f"Target allocations: {total_allocation:.1f}% (Over 100%)"
        else:
            message = f"Target allocations: {total_allocation:.1f}% (Under 100%)"
            
        self._update_status(message)
        
    def _update_status(self, message: str):
        """Update the status bar message."""
        if self.main_window:
            self.main_window.update_status(message)
            
    def _show_error(self, title: str, message: str):
        """Show an error dialog."""
        if self.main_window:
            self.main_window.show_error(title, message)
            
    def _show_info(self, title: str, message: str):
        """Show an info dialog."""
        if self.main_window:
            self.main_window.show_info(title, message)
            
    def _show_warning(self, title: str, message: str):
        """Show a warning dialog."""
        if self.main_window:
            self.main_window.show_warning(title, message)
            
    def run(self):
        """Start the application."""
        if not self.main_window:
            self.initialize_gui()
            
        self.main_window.run()
        
    def shutdown(self):
        """Clean shutdown of the application."""
        # Stop auto-refresh
        self._stop_auto_refresh()
        
        # Save portfolio
        self.save_portfolio()
        
        # Destroy GUI
        if self.main_window:
            self.main_window.destroy()