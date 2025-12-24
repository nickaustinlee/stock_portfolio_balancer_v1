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

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.portfolio import Portfolio
from models.holding import Holding
from services.stock_price_service import StockPriceService
from services.data_storage import DataStorage
from services.theme_manager import ThemeManager
from services.csv_exporter import CSVExporter
from gui.main_window import MainWindow
from gui.portfolio_table import PortfolioTable
from gui.error_dialog import ErrorHandler


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
        self.theme_manager = ThemeManager()
        self.csv_exporter = CSVExporter()
        
        # GUI components
        self.main_window: Optional[MainWindow] = None
        self.portfolio_table: Optional[PortfolioTable] = None
        self.error_handler: Optional[ErrorHandler] = None
        
        # Application state
        self.auto_refresh_timer: Optional[threading.Timer] = None
        self.share_rounding_enabled = True
        self.auto_refresh_enabled = False
        
        # Initialize dark mode state from theme manager
        self.dark_mode_enabled = self.theme_manager.is_dark_mode()
        
    def initialize_gui(self):
        """Initialize and set up the GUI components."""
        try:
            # Create main window
            self.main_window = MainWindow("Stock Allocation Tool")
            
            # Create error handler
            self.error_handler = ErrorHandler(self.main_window.root)
            
            # Remove placeholder if it exists, then create portfolio table
            for widget in self.main_window.table_frame.winfo_children():
                widget.destroy()
            
            self.portfolio_table = PortfolioTable(self.main_window.table_frame, name="portfolio_table")
            self.main_window.set_portfolio_table(self.portfolio_table)
            
            # Connect GUI callbacks
            self._connect_gui_callbacks()
            
            # Load saved portfolio data on startup
            self.load_portfolio()
            
            # Set initial theme state in GUI
            self.main_window.dark_mode_var.set(self.dark_mode_enabled)
            
            # Apply initial theme
            self._apply_theme()
            
            # Update GUI with initial data
            self._update_gui()
            
            # Set up window close handler for clean shutdown
            self.main_window.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            self._update_status("Application initialized successfully")
            
        except Exception as e:
            # If GUI initialization fails, we need to handle it gracefully
            print(f"Failed to initialize GUI: {e}")
            raise
        
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
                if self.error_handler:
                    self.error_handler.handle_invalid_ticker(ticker)
                return
            except ConnectionError:
                if self.error_handler:
                    self.error_handler.handle_api_failure()
                return
            except TimeoutError:
                if self.error_handler:
                    self.error_handler.handle_network_error()
                return
            
            # Create new holding
            holding = Holding(ticker=ticker, quantity=quantity)
            holding.current_price = price
            holding.last_updated = datetime.now()
            
            # Add to portfolio
            self.portfolio.add_holding(holding)
            
            # Save immediately on data change
            self.save_portfolio()
            self._update_gui()
            
            self._update_status(f"Added {quantity} shares of {ticker}")
            
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to add holding: {str(e)}")
            else:
                self._show_error("Error", f"Failed to add holding: {str(e)}")
            
    def remove_holding(self, ticker: str) -> None:
        """
        Remove a holding from the portfolio.
        
        Args:
            ticker: Stock ticker symbol to remove
        """
        try:
            self.portfolio.remove_holding(ticker)
            # Save immediately on data change
            self.save_portfolio()
            self._update_gui()
            self._update_status(f"Removed {ticker} from portfolio")
            
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to remove holding: {str(e)}")
            else:
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
            # Save immediately on data change
            self.save_portfolio()
            self._update_gui()
            self._update_status(f"Updated {ticker} quantity to {quantity}")
            
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to update quantity: {str(e)}")
            else:
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
            # Save immediately on data change
            self.save_portfolio()
            self._update_gui()
            self._update_status(f"Updated {ticker} target allocation to {percentage}%")
            
        except ValueError as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Invalid allocation: {str(e)}")
            else:
                self._show_error("Invalid Allocation", str(e))
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to update allocation: {str(e)}")
            else:
                self._show_error("Error", f"Failed to update allocation: {str(e)}")
            
    def refresh_prices(self) -> None:
        """Manually refresh stock prices for all holdings."""
        if self.portfolio.is_empty():
            self._update_status("No holdings to refresh")
            return
            
        # Show loading indicator
        if self.main_window:
            self.main_window.show_loading("Refreshing prices...")
            
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
                    
            except ConnectionError:
                if self.main_window and self.error_handler:
                    self.main_window.root.after(0, lambda: self._on_refresh_error("API failure"))
            except TimeoutError:
                if self.main_window and self.error_handler:
                    self.main_window.root.after(0, lambda: self._on_refresh_error("Network timeout"))
            except Exception as e:
                if self.main_window and self.error_handler:
                    self.main_window.root.after(0, lambda: self._on_refresh_error(f"Refresh failed: {str(e)}"))
                    
        thread = threading.Thread(target=refresh_thread, daemon=True)
        thread.start()
        
    def _on_refresh_complete(self):
        """Handle completion of price refresh."""
        # Hide loading indicator
        if self.main_window:
            self.main_window.hide_loading()
            
        # Save portfolio after price updates
        self.save_portfolio()
        self._update_gui()
        
        # Update last refresh timestamp
        if self.main_window and self.stock_service.last_refresh:
            timestamp = self.stock_service.last_refresh.strftime("%Y-%m-%d %H:%M:%S")
            self.main_window.update_last_refresh(timestamp)
            
        self._update_status("Prices refreshed successfully")
        
    def _on_refresh_error(self, error_message: str):
        """Handle refresh error."""
        # Hide loading indicator
        if self.main_window:
            self.main_window.hide_loading()
            
        # Show appropriate error
        if "API failure" in error_message:
            if self.error_handler:
                self.error_handler.handle_api_failure()
        elif "Network timeout" in error_message:
            if self.error_handler:
                self.error_handler.handle_network_error()
        else:
            if self.error_handler:
                self.error_handler.handle_generic_error(error_message)
            elif self.main_window:
                self._show_error("Refresh Error", error_message)
                
        self._update_status("Refresh failed")
        
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
                try:
                    # Show subtle loading indicator for auto-refresh
                    if self.main_window:
                        self.main_window.show_loading("Auto-refreshing...")
                        
                    self.refresh_prices()
                except Exception as e:
                    # Log error but don't show dialog for auto-refresh failures
                    # to avoid interrupting user workflow
                    if self.error_handler:
                        # Just log the error, don't show dialog for auto-refresh
                        pass
                    # Hide loading indicator on error
                    if self.main_window:
                        self.main_window.hide_loading()
            
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
        
        # Update theme manager
        theme = "dark" if enabled else "light"
        self.theme_manager.set_theme(theme)
        
        # Apply theme to all UI components
        self._apply_theme()
        
        mode = "dark" if enabled else "light"
        self._update_status(f"Switched to {mode} mode")
        
    def _apply_theme(self):
        """Apply the current theme to all GUI components."""
        if not self.main_window:
            return
            
        # Apply theme to entire application starting from root window
        self.theme_manager.apply_theme_to_application(self.main_window.root)
        
    def export_to_csv(self) -> None:
        """Export current portfolio data to CSV file."""
        try:
            if self.portfolio.is_empty():
                self._show_info("Export", "No portfolio data to export")
                return
                
            # Use CSV exporter service
            filepath = self.csv_exporter.export_portfolio(self.portfolio, self.share_rounding_enabled)
                    
            self._show_info("Export Successful", f"Portfolio exported to {filepath}")
            self._update_status(f"Exported to {filepath}")
            
        except ValueError as e:
            # Empty portfolio
            self._show_info("Export", str(e))
        except PermissionError:
            if self.error_handler:
                self.error_handler.handle_file_error("Cannot save CSV file, check file permissions")
            else:
                self._show_error("Export Error", "Cannot save CSV file, check file permissions")
        except OSError as e:
            if self.error_handler:
                self.error_handler.handle_file_error(f"File system error: {str(e)}")
            else:
                self._show_error("Export Error", f"File system error: {str(e)}")
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to export portfolio: {str(e)}")
            else:
                self._show_error("Export Error", f"Failed to export portfolio: {str(e)}")
            
    def save_portfolio(self) -> None:
        """Save the current portfolio to persistent storage."""
        try:
            self.storage.save_portfolio(self.portfolio)
        except PermissionError:
            if self.error_handler:
                self.error_handler.handle_file_error()
            else:
                self._show_error("Save Error", "Cannot save portfolio, check file permissions")
        except OSError as e:
            if "No space left on device" in str(e):
                if self.error_handler:
                    self.error_handler.handle_file_error("Insufficient disk space for saving portfolio")
                else:
                    self._show_error("Save Error", "Insufficient disk space for saving portfolio")
            else:
                if self.error_handler:
                    self.error_handler.handle_file_error(f"Error saving portfolio: {str(e)}")
                else:
                    self._show_error("Save Error", f"Error saving portfolio: {str(e)}")
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to save portfolio: {str(e)}")
            else:
                self._show_error("Save Error", f"Failed to save portfolio: {str(e)}")
            
    def load_portfolio(self) -> None:
        """Load portfolio from persistent storage."""
        try:
            self.portfolio = self.storage.load_portfolio()
        except ValueError as e:
            # Data corruption detected
            if self.error_handler:
                self.error_handler.handle_data_corruption()
            else:
                self._show_warning("Data Corruption", str(e))
            self.portfolio = Portfolio()
        except OSError as e:
            if self.error_handler:
                self.error_handler.handle_file_error(f"Error loading portfolio: {str(e)}")
            else:
                self._show_error("Load Error", f"Error loading portfolio: {str(e)}")
            self.portfolio = Portfolio()
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_generic_error(f"Failed to load portfolio: {str(e)}")
            else:
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
        
        # Update total portfolio value
        total_value = self.portfolio.get_total_value()
        if self.main_window:
            self.main_window.update_total_portfolio_value(total_value)
        
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
        
        # Update allocation status indicator in GUI
        self.main_window.update_allocation_status(total_allocation, status)
        
        # Also update main status message
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
            
    def _on_window_close(self):
        """Handle window close event for clean shutdown."""
        try:
            # Save portfolio before closing
            self.save_portfolio()
            
            # Stop auto-refresh
            self._stop_auto_refresh()
            
            # Save theme preference
            self.theme_manager.save_theme_preference(self.theme_manager.current_theme)
            
            self._update_status("Shutting down...")
            
        except Exception as e:
            # Log error but don't prevent shutdown
            print(f"Error during shutdown: {e}")
        finally:
            # Always destroy the window
            self.main_window.root.destroy()
            
    def run(self):
        """Start the application."""
        if not self.main_window:
            self.initialize_gui()
            
        self.main_window.run()
        
    def shutdown(self):
        """Clean shutdown of the application."""
        try:
            # Stop auto-refresh
            self._stop_auto_refresh()
            
            # Save portfolio
            self.save_portfolio()
            
            # Save theme preference
            if self.theme_manager:
                self.theme_manager.save_theme_preference(self.theme_manager.current_theme)
            
            # Destroy GUI
            if self.main_window:
                self.main_window.destroy()
                
        except Exception as e:
            # Log error but continue shutdown
            print(f"Error during shutdown: {e}")
            if self.main_window:
                self.main_window.destroy()