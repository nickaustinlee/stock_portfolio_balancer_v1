"""
Portfolio table widget for displaying and editing stock holdings.
Provides tabular view with inline editing capabilities.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Any
from decimal import Decimal, InvalidOperation
from utils.debug import logger


class PortfolioTable(ttk.Frame):
    """Custom table widget for portfolio data display and editing."""
    
    # Column definitions in display order
    COLUMNS = [
        ("ticker", "Ticker", 80, False),
        ("price", "Price", 100, False),
        ("quantity", "Quantity", 100, True),
        ("target_allocation", "Target %", 100, True),
        ("current_allocation", "Current %", 100, False),
        ("current_value", "Current Value", 120, False),
        ("target_value", "Target Value", 120, False),
        ("difference", "Difference", 120, False),
        ("rebalance_action", "Rebalance Action", 140, False)
    ]
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Callback functions
        self.on_quantity_changed: Optional[Callable[[str, float], None]] = None
        self.on_target_allocation_changed: Optional[Callable[[str, float], None]] = None
        self.on_holding_added: Optional[Callable[[str, float], None]] = None
        self.on_holding_removed: Optional[Callable[[str], None]] = None
        
        # Data storage
        self.holdings_data: Dict[str, Dict[str, Any]] = {}
        
        # Sorting state
        self.sort_column = None
        self.sort_reverse = False
        
        # UI components
        self.tree = None
        self.entry_popup = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the table UI components."""
        # Create main container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create add holding frame
        self._create_add_holding_frame(container)
        
        # Create treeview with scrollbars
        self._create_treeview(container)
        
    def _create_add_holding_frame(self, parent):
        """Create frame for adding new holdings."""
        add_frame = ttk.Frame(parent)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ticker entry
        ttk.Label(add_frame, text="Add Holding:").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(add_frame, text="Ticker:").pack(side=tk.LEFT, padx=(10, 5))
        self.ticker_entry = ttk.Entry(add_frame, width=10)
        self.ticker_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quantity entry
        ttk.Label(add_frame, text="Quantity:").pack(side=tk.LEFT, padx=(0, 5))
        self.quantity_entry = ttk.Entry(add_frame, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add button
        add_button = ttk.Button(
            add_frame,
            text="Add",
            command=self._on_add_holding
        )
        add_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Remove button
        remove_button = ttk.Button(
            add_frame,
            text="Remove Selected",
            command=self._on_remove_holding
        )
        remove_button.pack(side=tk.LEFT)
        
        # Bind Enter key to add holding
        self.ticker_entry.bind('<Return>', lambda e: self._on_add_holding())
        self.quantity_entry.bind('<Return>', lambda e: self._on_add_holding())
        
    def _create_treeview(self, parent):
        """Create the main treeview table."""
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = [col[0] for col in self.COLUMNS[1:]]  # Skip ticker (it's the tree column)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        for i, (col_id, col_name, col_width, editable) in enumerate(self.COLUMNS):
            if i == 0:  # Ticker column (tree column)
                self.tree.heading('#0', text=col_name, anchor=tk.W, command=lambda: self._sort_by_column('ticker'))
                self.tree.column('#0', width=col_width, minwidth=50)
            else:
                # Add sorting command to numerical/percentage columns
                if col_id in ['price', 'quantity', 'target_allocation', 'current_allocation', 'current_value', 'target_value', 'difference', 'rebalance_action']:
                    self.tree.heading(col_id, text=col_name, anchor=tk.CENTER, command=lambda c=col_id: self._sort_by_column(c))
                else:
                    self.tree.heading(col_id, text=col_name, anchor=tk.CENTER)
                self.tree.column(col_id, width=col_width, minwidth=80, anchor=tk.E)
        
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind double-click for editing
        self.tree.bind('<Double-1>', self._on_double_click)
        
    def _on_add_holding(self):
        """Handle adding a new holding."""
        ticker = self.ticker_entry.get().strip().upper()
        quantity_str = self.quantity_entry.get().strip()
        
        if not ticker or not quantity_str:
            return
            
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            return
            
        # Clear entries
        self.ticker_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        
        # Call callback
        if self.on_holding_added:
            self.on_holding_added(ticker, quantity)
            
    def _on_remove_holding(self):
        """Handle removing selected holding."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        ticker = self.tree.item(item, 'text')
        
        if self.on_holding_removed:
            self.on_holding_removed(ticker)
            
    def _on_double_click(self, event):
        """Handle double-click for inline editing."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        # Get clicked column
        column = self.tree.identify_column(event.x)
        
        # Check if column is editable
        if column == '#0':  # Ticker column
            return
            
        # Get column info
        col_index = int(column[1:])  # Remove '#' and convert to int
        if col_index > len(self.COLUMNS) - 1:
            return
            
        col_info = self.COLUMNS[col_index]
        col_id, col_name, col_width, editable = col_info
        
        if not editable:
            return
            
        # Get current value
        current_value = self.tree.set(item, col_id)
        ticker = self.tree.item(item, 'text')
        
        # Create inline editor
        self._create_inline_editor(item, col_id, current_value, ticker, event)
        
    def _create_inline_editor(self, item, column, current_value, ticker, event):
        """Create inline editor for cell editing."""
        # Get cell position
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
            
        x, y, width, height = bbox
        
        # Create entry widget
        self.entry_popup = tk.Entry(self.tree)
        self.entry_popup.place(x=x, y=y, width=width, height=height)
        self.entry_popup.insert(0, current_value)
        self.entry_popup.select_range(0, tk.END)
        self.entry_popup.focus()
        
        # Bind events
        def save_edit(event=None):
            new_value = self.entry_popup.get().strip()
            self.entry_popup.destroy()
            self.entry_popup = None
            
            if new_value != current_value:
                self._handle_cell_edit(ticker, column, new_value)
                
        def cancel_edit(event=None):
            self.entry_popup.destroy()
            self.entry_popup = None
            
        self.entry_popup.bind('<Return>', save_edit)
        self.entry_popup.bind('<Escape>', cancel_edit)
        self.entry_popup.bind('<FocusOut>', save_edit)
        
    def _handle_cell_edit(self, ticker: str, column: str, new_value: str):
        """Handle cell edit completion."""
        try:
            logger.debug("Editing %s for %s with value '%s'", column, ticker, new_value)
            
            if column == 'quantity':
                quantity = float(new_value)
                logger.debug("Parsed quantity: %s", quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
                if self.on_quantity_changed:
                    self.on_quantity_changed(ticker, quantity)
                    
            elif column == 'target_allocation':
                # Handle percentage input - remove % sign if present
                clean_value = new_value.strip().rstrip('%')
                logger.debug("Cleaned allocation value: '%s'", clean_value)
                allocation = float(clean_value)
                logger.debug("Parsed allocation: %s", allocation)
                if allocation < 0 or allocation > 100:
                    raise ValueError("Allocation must be between 0 and 100")
                if self.on_target_allocation_changed:
                    logger.debug("Calling on_target_allocation_changed(%s, %s)", ticker, allocation)
                    self.on_target_allocation_changed(ticker, allocation)
                    
        except ValueError as e:
            logger.debug("ValueError in _handle_cell_edit: %s", e)
            # Show error to user instead of silently ignoring
            import tkinter.messagebox as messagebox
            messagebox.showerror("Invalid Input", f"Error updating {column}: {str(e)}")
            # Refresh the display to revert the invalid change
            if hasattr(self, 'holdings_data'):
                self.update_holdings(self.holdings_data)
        except Exception as e:
            logger.error("Unexpected error in _handle_cell_edit: %s", e)
            import traceback
            traceback.print_exc()
            raise
    
    def _sort_by_column(self, column: str):
        """Sort the table by the specified column."""
        logger.debug("Sorting by column: %s", column)
        
        # Toggle sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Update column header to show sort direction
        self._update_sort_indicators()
        
        # Sort the data and refresh display
        self._sort_and_refresh()
    
    def _update_sort_indicators(self):
        """Update column headers to show sort direction."""
        for i, (col_id, col_name, _, _) in enumerate(self.COLUMNS):
            if i == 0:  # Ticker column
                header_text = col_name
                if self.sort_column == 'ticker':
                    header_text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading('#0', text=header_text)
            else:
                header_text = col_name
                if self.sort_column == col_id:
                    header_text += " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(col_id, text=header_text)
    
    def _sort_and_refresh(self):
        """Sort holdings data and refresh the display."""
        if not self.holdings_data or not self.sort_column:
            return
        
        # Create list of (ticker, data) tuples for sorting
        items = list(self.holdings_data.items())
        
        # Define sort key function
        def get_sort_key(item):
            ticker, data = item
            if self.sort_column == 'ticker':
                return ticker.lower()
            
            value = data.get(self.sort_column, 0)
            
            # Handle different data types
            if isinstance(value, str):
                # For rebalance_action, extract numeric value
                if self.sort_column == 'rebalance_action':
                    if value.startswith('Buy ') or value.startswith('Sell '):
                        try:
                            return float(value.split()[1])
                        except (IndexError, ValueError):
                            return 0
                return value.lower()
            
            return float(value) if value is not None else 0
        
        # Sort the items
        items.sort(key=get_sort_key, reverse=self.sort_reverse)
        
        # Rebuild holdings_data in sorted order
        sorted_data = {ticker: data for ticker, data in items}
        
        # Update display with sorted data
        self.update_holdings(sorted_data)
            
    def update_holdings(self, holdings_data: Dict[str, Dict[str, Any]]):
        """Update the table with new holdings data."""
        self.holdings_data = holdings_data.copy()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add holdings
        for ticker, data in holdings_data.items():
            values = []
            for col_id, _, _, _ in self.COLUMNS[1:]:  # Skip ticker column
                value = data.get(col_id, '')
                
                # Format values for display
                if col_id in ['price', 'current_value', 'target_value', 'difference']:
                    if isinstance(value, (int, float)) and value != 0:
                        value = f"${value:,.2f}"
                    else:
                        value = "$0.00"
                elif col_id in ['current_allocation', 'target_allocation']:
                    if isinstance(value, (int, float)):
                        value = f"{value:.1f}%"
                    else:
                        value = "0.0%"
                elif col_id == 'quantity':
                    if isinstance(value, (int, float)):
                        value = f"{value:.3f}"
                    else:
                        value = "0.000"
                elif col_id == 'rebalance_action':
                    if isinstance(value, (int, float)):
                        if value > 0:
                            value = f"Buy {value:.3f}"
                        elif value < 0:
                            value = f"Sell {abs(value):.3f}"
                        else:
                            value = "Hold"
                    else:
                        value = "Hold"
                        
                values.append(str(value))
                
            self.tree.insert('', tk.END, text=ticker, values=values)
            
    def get_selected_ticker(self) -> Optional[str]:
        """Get the ticker of the currently selected row."""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0], 'text')
        
    def clear_selection(self):
        """Clear the current selection."""
        self.tree.selection_remove(self.tree.selection())