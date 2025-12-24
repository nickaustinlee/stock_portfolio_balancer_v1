"""
Error dialog for displaying dismissible error messages with different types.
Provides user-friendly error reporting without blocking application functionality.
"""

import tkinter as tk
from tkinter import ttk
from enum import Enum
from typing import Optional, Callable


class ErrorType(Enum):
    """Types of errors that can be displayed."""
    INVALID_TICKER = "invalid_ticker"
    API_FAILURE = "api_failure"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    FILE_ERROR = "file_error"
    DATA_CORRUPTION = "data_corruption"
    GENERIC_ERROR = "generic_error"


class ErrorDialog:
    """Dismissible error dialog with different error types and appropriate messaging."""
    
    # Error type to message mapping
    ERROR_MESSAGES = {
        ErrorType.INVALID_TICKER: "{ticker} not found",
        ErrorType.API_FAILURE: "Yahoo Finance isn't working, try again later",
        ErrorType.RATE_LIMIT: "API rate limit exceeded, please use manual refresh",
        ErrorType.NETWORK_ERROR: "Network error, using cached prices",
        ErrorType.FILE_ERROR: "Cannot save portfolio, check file permissions",
        ErrorType.DATA_CORRUPTION: "Portfolio data corrupted, starting fresh",
        ErrorType.GENERIC_ERROR: "An unexpected error occurred: {details}"
    }
    
    # Error type to title mapping
    ERROR_TITLES = {
        ErrorType.INVALID_TICKER: "Invalid Ticker",
        ErrorType.API_FAILURE: "API Error",
        ErrorType.RATE_LIMIT: "Rate Limit Exceeded",
        ErrorType.NETWORK_ERROR: "Network Error",
        ErrorType.FILE_ERROR: "File Error",
        ErrorType.DATA_CORRUPTION: "Data Corruption",
        ErrorType.GENERIC_ERROR: "Error"
    }
    
    def __init__(self, parent: tk.Tk):
        """Initialize the error dialog.
        
        Args:
            parent: Parent window for the dialog
        """
        self.parent = parent
        self.dialog = None
        self.on_dismiss: Optional[Callable] = None
        
    def show_error(self, error_type: ErrorType, **kwargs) -> None:
        """Show an error dialog with the specified type and details.
        
        Args:
            error_type: Type of error to display
            **kwargs: Additional parameters for error message formatting
        """
        # Don't show multiple dialogs at once
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            return
            
        # Get error message and title
        message = self._format_error_message(error_type, **kwargs)
        title = self.ERROR_TITLES.get(error_type, "Error")
        
        # Create the dialog
        self._create_dialog(title, message, error_type)
        
    def _format_error_message(self, error_type: ErrorType, **kwargs) -> str:
        """Format the error message with provided parameters.
        
        Args:
            error_type: Type of error
            **kwargs: Parameters for message formatting
            
        Returns:
            Formatted error message
        """
        message_template = self.ERROR_MESSAGES.get(error_type, "Unknown error")
        
        try:
            return message_template.format(**kwargs)
        except KeyError:
            # If formatting fails, return the template as-is
            return message_template
            
    def _create_dialog(self, title: str, message: str, error_type: ErrorType) -> None:
        """Create and display the error dialog.
        
        Args:
            title: Dialog title
            message: Error message to display
            error_type: Type of error for styling
        """
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Center the dialog on parent
        self._center_dialog()
        
        # Make dialog modal but not blocking
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create icon and message frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add error icon
        icon_label = ttk.Label(content_frame, text="⚠️", font=("Arial", 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Add message
        message_label = ttk.Label(
            content_frame,
            text=message,
            wraplength=300,
            justify=tk.LEFT,
            font=("Arial", 10)
        )
        message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Add dismiss button
        dismiss_button = ttk.Button(
            button_frame,
            text="OK",
            command=self._dismiss_dialog,
            width=10
        )
        dismiss_button.pack(side=tk.RIGHT)
        
        # Handle window close event
        self.dialog.protocol("WM_DELETE_WINDOW", self._dismiss_dialog)
        
        # Focus the dismiss button
        dismiss_button.focus_set()
        
        # Bind Enter key to dismiss
        self.dialog.bind('<Return>', lambda e: self._dismiss_dialog())
        self.dialog.bind('<Escape>', lambda e: self._dismiss_dialog())
        
    def _center_dialog(self) -> None:
        """Center the dialog on the parent window."""
        # Update dialog to get actual size
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set dialog position
        self.dialog.geometry(f"+{x}+{y}")
        
    def _dismiss_dialog(self) -> None:
        """Dismiss the error dialog."""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None
            
        # Call dismiss callback if set
        if self.on_dismiss:
            self.on_dismiss()
            
    def is_showing(self) -> bool:
        """Check if an error dialog is currently showing.
        
        Returns:
            True if dialog is showing, False otherwise
        """
        return self.dialog is not None and self.dialog.winfo_exists()


class ErrorHandler:
    """Centralized error handler for the application."""
    
    def __init__(self, parent: tk.Tk):
        """Initialize the error handler.
        
        Args:
            parent: Parent window for error dialogs
        """
        self.error_dialog = ErrorDialog(parent)
        
    def handle_invalid_ticker(self, ticker: str) -> None:
        """Handle invalid ticker error.
        
        Args:
            ticker: The invalid ticker symbol
        """
        self.error_dialog.show_error(ErrorType.INVALID_TICKER, ticker=ticker)
        
    def handle_api_failure(self) -> None:
        """Handle Yahoo Finance API failure."""
        self.error_dialog.show_error(ErrorType.API_FAILURE)
        
    def handle_rate_limit(self) -> None:
        """Handle API rate limit exceeded."""
        self.error_dialog.show_error(ErrorType.RATE_LIMIT)
        
    def handle_network_error(self) -> None:
        """Handle network connectivity error."""
        self.error_dialog.show_error(ErrorType.NETWORK_ERROR)
        
    def handle_file_error(self, details: str = "") -> None:
        """Handle file system error.
        
        Args:
            details: Additional error details
        """
        if details:
            self.error_dialog.show_error(ErrorType.GENERIC_ERROR, details=details)
        else:
            self.error_dialog.show_error(ErrorType.FILE_ERROR)
            
    def handle_data_corruption(self) -> None:
        """Handle data corruption error."""
        self.error_dialog.show_error(ErrorType.DATA_CORRUPTION)
        
    def handle_generic_error(self, details: str) -> None:
        """Handle generic error with details.
        
        Args:
            details: Error details to display
        """
        self.error_dialog.show_error(ErrorType.GENERIC_ERROR, details=details)
        
    def is_showing_error(self) -> bool:
        """Check if an error dialog is currently showing.
        
        Returns:
            True if error dialog is showing, False otherwise
        """
        return self.error_dialog.is_showing()