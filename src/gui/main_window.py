"""
Main window for the Stock Allocation Tool GUI.
Provides the primary interface with controls and portfolio table.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable


class MainWindow:
    """Main application window with controls and portfolio display."""
    
    def __init__(self, title: str = "Stock Allocation Tool"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1200x600")
        self.root.minsize(800, 400)
        
        # Callback functions (to be set by controller)
        self.on_refresh: Optional[Callable] = None
        self.on_auto_refresh_toggle: Optional[Callable[[bool], None]] = None
        self.on_share_rounding_toggle: Optional[Callable[[bool], None]] = None
        self.on_dark_mode_toggle: Optional[Callable[[bool], None]] = None
        self.on_csv_export: Optional[Callable] = None
        
        # State variables
        self.auto_refresh_var = tk.BooleanVar(value=False)
        self.share_rounding_var = tk.BooleanVar(value=True)
        self.dark_mode_var = tk.BooleanVar(value=False)
        
        # Portfolio table placeholder
        self.portfolio_table = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create control panel
        self._create_control_panel(main_frame)
        
        # Create portfolio table placeholder
        self._create_portfolio_table_placeholder(main_frame)
        
        # Create status bar
        self._create_status_bar(main_frame)
        
    def _create_control_panel(self, parent):
        """Create the control panel with buttons and toggles."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Refresh button
        self.refresh_button = ttk.Button(
            control_frame,
            text="Refresh Prices",
            command=self._on_refresh_clicked
        )
        self.refresh_button.grid(row=0, column=0, padx=(0, 10))
        
        # Auto-refresh toggle
        auto_refresh_check = ttk.Checkbutton(
            control_frame,
            text="Auto-refresh (60s)",
            variable=self.auto_refresh_var,
            command=self._on_auto_refresh_toggled
        )
        auto_refresh_check.grid(row=0, column=1, padx=(0, 10))
        
        # Share rounding toggle
        share_rounding_check = ttk.Checkbutton(
            control_frame,
            text="Round to whole shares",
            variable=self.share_rounding_var,
            command=self._on_share_rounding_toggled
        )
        share_rounding_check.grid(row=0, column=2, padx=(0, 10))
        
        # Dark mode toggle
        dark_mode_check = ttk.Checkbutton(
            control_frame,
            text="Dark mode",
            variable=self.dark_mode_var,
            command=self._on_dark_mode_toggled
        )
        dark_mode_check.grid(row=0, column=3, padx=(0, 10))
        
        # CSV export button
        self.export_button = ttk.Button(
            control_frame,
            text="Export to CSV",
            command=self._on_csv_export_clicked
        )
        self.export_button.grid(row=0, column=4, padx=(0, 10))
        
    def _create_portfolio_table_placeholder(self, parent):
        """Create placeholder for the portfolio table."""
        table_frame = ttk.LabelFrame(parent, text="Portfolio", padding="5")
        table_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Placeholder label (will be replaced by actual table)
        placeholder_label = ttk.Label(
            table_frame,
            text="Portfolio table will be displayed here",
            font=("Arial", 12),
            foreground="gray"
        )
        placeholder_label.grid(row=0, column=0, pady=50)
        
        # Store reference to table frame for later use
        self.table_frame = table_frame
        
    def _create_status_bar(self, parent):
        """Create status bar for displaying information."""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Last refresh timestamp
        self.last_refresh_label = ttk.Label(
            self.status_frame,
            text="Last refresh: Never",
            relief=tk.SUNKEN,
            anchor=tk.E
        )
        self.last_refresh_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Configure status bar grid
        self.status_frame.columnconfigure(0, weight=1)
        self.status_frame.columnconfigure(1, weight=1)
        
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        if self.on_refresh:
            self.on_refresh()
            
    def _on_auto_refresh_toggled(self):
        """Handle auto-refresh toggle."""
        if self.on_auto_refresh_toggle:
            self.on_auto_refresh_toggle(self.auto_refresh_var.get())
            
    def _on_share_rounding_toggled(self):
        """Handle share rounding toggle."""
        if self.on_share_rounding_toggle:
            self.on_share_rounding_toggle(self.share_rounding_var.get())
            
    def _on_dark_mode_toggled(self):
        """Handle dark mode toggle."""
        if self.on_dark_mode_toggle:
            self.on_dark_mode_toggle(self.dark_mode_var.get())
            
    def _on_csv_export_clicked(self):
        """Handle CSV export button click."""
        if self.on_csv_export:
            self.on_csv_export()
            
    def set_portfolio_table(self, table_widget):
        """Set the portfolio table widget."""
        # Remove placeholder if it exists
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        # Add the actual table
        self.portfolio_table = table_widget
        self.portfolio_table.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.config(text=message)
        
    def update_last_refresh(self, timestamp: str):
        """Update the last refresh timestamp."""
        self.last_refresh_label.config(text=f"Last refresh: {timestamp}")
        
    def show_error(self, title: str, message: str):
        """Show an error dialog."""
        messagebox.showerror(title, message)
        
    def show_info(self, title: str, message: str):
        """Show an info dialog."""
        messagebox.showinfo(title, message)
        
    def show_warning(self, title: str, message: str):
        """Show a warning dialog."""
        messagebox.showwarning(title, message)
        
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
        
    def destroy(self):
        """Destroy the window."""
        self.root.destroy()