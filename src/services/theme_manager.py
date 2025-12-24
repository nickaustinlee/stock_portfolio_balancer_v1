"""
Theme Manager for the Stock Allocation Tool.

This module provides the ThemeManager class that handles theme management
including light and dark color schemes, theme application to UI elements,
and theme preference persistence.
"""

import os
import json
from typing import Dict, Any, Optional

# Optional tkinter imports for environments where GUI is not available
try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    # Create mock classes for testing environments without tkinter
    class MockTk:
        pass
    class MockTTK:
        class Widget:
            pass
        class Style:
            def configure(self, *args, **kwargs):
                pass
            def map(self, *args, **kwargs):
                pass
    
    tk = MockTk()
    ttk = MockTTK()
    TKINTER_AVAILABLE = False


class ThemeManager:
    """
    Theme management service for handling light and dark color schemes.
    
    Provides methods for applying themes to UI elements, persisting preferences,
    and immediate theme switching without requiring application restart.
    """
    
    def __init__(self, preferences_file: str = "theme_preferences.json"):
        """
        Initialize the theme manager.
        
        Args:
            preferences_file: Path to the theme preferences file
        """
        self.preferences_file = preferences_file
        self.current_theme = "light"
        
        # Light theme color scheme
        self.light_colors = {
            "bg": "#ffffff",
            "fg": "#000000",
            "table_bg": "#f8f9fa",
            "table_fg": "#000000",
            "table_select_bg": "#007bff",
            "table_select_fg": "#ffffff",
            "button_bg": "#e9ecef",
            "button_fg": "#000000",
            "button_active_bg": "#dee2e6",
            "entry_bg": "#ffffff",
            "entry_fg": "#000000",
            "entry_select_bg": "#007bff",
            "frame_bg": "#f8f9fa",
            "label_bg": "#ffffff",
            "label_fg": "#000000",
            "accent": "#007bff",
            "border": "#dee2e6",
            "status_bg": "#f8f9fa",
            "status_fg": "#6c757d"
        }
        
        # Dark theme color scheme
        self.dark_colors = {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "table_bg": "#3c3c3c",
            "table_fg": "#ffffff",
            "table_select_bg": "#0d6efd",
            "table_select_fg": "#ffffff",
            "button_bg": "#4a4a4a",
            "button_fg": "#ffffff",
            "button_active_bg": "#5a5a5a",
            "entry_bg": "#3c3c3c",
            "entry_fg": "#ffffff",
            "entry_select_bg": "#0d6efd",
            "frame_bg": "#2b2b2b",
            "label_bg": "#2b2b2b",
            "label_fg": "#ffffff",
            "accent": "#0d6efd",
            "border": "#4a4a4a",
            "status_bg": "#3c3c3c",
            "status_fg": "#adb5bd"
        }
        
        # Load saved theme preference
        self.current_theme = self.load_theme_preference()
        
    def get_current_colors(self) -> Dict[str, str]:
        """
        Get the current theme's color scheme.
        
        Returns:
            Dictionary containing color values for the current theme
        """
        return self.dark_colors if self.current_theme == "dark" else self.light_colors
        
    def get_theme_colors(self, theme: str) -> Dict[str, str]:
        """
        Get color scheme for a specific theme.
        
        Args:
            theme: Theme name ("light" or "dark")
            
        Returns:
            Dictionary containing color values for the specified theme
        """
        if theme == "dark":
            return self.dark_colors.copy()
        else:
            return self.light_colors.copy()
            
    def apply_theme(self, widget: Any, theme: Optional[str] = None) -> None:
        """
        Apply theme colors to a widget and its children recursively.
        
        Args:
            widget: The widget to apply the theme to
            theme: Theme name ("light" or "dark"), uses current theme if None
        """
        if not TKINTER_AVAILABLE:
            # Skip theme application if tkinter is not available
            return
            
        if theme is None:
            theme = self.current_theme
            
        colors = self.get_theme_colors(theme)
        
        # Apply theme to the widget
        self._apply_widget_theme(widget, colors)
        
        # Recursively apply to all children
        for child in widget.winfo_children():
            self.apply_theme(child, theme)
            
    def _apply_widget_theme(self, widget: Any, colors: Dict[str, str]) -> None:
        """
        Apply theme colors to a specific widget based on its type.
        
        Args:
            widget: The widget to style
            colors: Color scheme dictionary
        """
        if not TKINTER_AVAILABLE:
            return
            
        widget_class = widget.winfo_class()
        
        try:
            if widget_class == "Tk":
                # Main window
                widget.configure(bg=colors["bg"])
                
            elif widget_class == "Frame":
                # Regular frames
                widget.configure(bg=colors["frame_bg"])
                
            elif widget_class == "Toplevel":
                # Dialog windows
                widget.configure(bg=colors["bg"])
                
            elif widget_class == "Label":
                # Labels
                widget.configure(
                    bg=colors["label_bg"],
                    fg=colors["label_fg"]
                )
                
            elif widget_class == "Button":
                # Regular buttons
                widget.configure(
                    bg=colors["button_bg"],
                    fg=colors["button_fg"],
                    activebackground=colors["button_active_bg"],
                    activeforeground=colors["button_fg"]
                )
                
            elif widget_class == "Entry":
                # Entry widgets
                widget.configure(
                    bg=colors["entry_bg"],
                    fg=colors["entry_fg"],
                    selectbackground=colors["entry_select_bg"],
                    selectforeground=colors["entry_select_fg"],
                    insertbackground=colors["entry_fg"]
                )
                
            elif widget_class == "Text":
                # Text widgets
                widget.configure(
                    bg=colors["entry_bg"],
                    fg=colors["entry_fg"],
                    selectbackground=colors["entry_select_bg"],
                    selectforeground=colors["entry_select_fg"],
                    insertbackground=colors["entry_fg"]
                )
                
            elif widget_class == "Listbox":
                # Listbox widgets
                widget.configure(
                    bg=colors["table_bg"],
                    fg=colors["table_fg"],
                    selectbackground=colors["table_select_bg"],
                    selectforeground=colors["table_select_fg"]
                )
                
            elif widget_class == "Canvas":
                # Canvas widgets
                widget.configure(bg=colors["bg"])
                
            elif widget_class == "Scrollbar":
                # Scrollbar widgets
                widget.configure(
                    bg=colors["button_bg"],
                    troughcolor=colors["frame_bg"],
                    activebackground=colors["button_active_bg"]
                )
                
            # Handle ttk widgets
            elif TKINTER_AVAILABLE and isinstance(widget, ttk.Widget):
                self._apply_ttk_theme(widget, colors)
                
        except Exception:
            # Some widgets may not support certain configuration options
            # Silently ignore these errors to maintain compatibility
            pass
            
    def _apply_ttk_theme(self, widget: Any, colors: Dict[str, str]) -> None:
        """
        Apply theme to ttk widgets using styles.
        
        Args:
            widget: The ttk widget to style
            colors: Color scheme dictionary
        """
        if not TKINTER_AVAILABLE:
            return
            
        try:
            style = ttk.Style()
            widget_class = widget.winfo_class()
            
            if widget_class == "TFrame":
                # TTK Frames
                style.configure("TFrame", background=colors["frame_bg"])
                
            elif widget_class == "TLabel":
                # TTK Labels
                style.configure("TLabel", 
                    background=colors["label_bg"],
                    foreground=colors["label_fg"]
                )
                
            elif widget_class == "TButton":
                # TTK Buttons
                style.configure("TButton",
                    background=colors["button_bg"],
                    foreground=colors["button_fg"]
                )
                style.map("TButton",
                    background=[('active', colors["button_active_bg"])]
                )
                
            elif widget_class == "TEntry":
                # TTK Entry widgets
                style.configure("TEntry",
                    fieldbackground=colors["entry_bg"],
                    foreground=colors["entry_fg"],
                    bordercolor=colors["border"]
                )
                
            elif widget_class == "TCheckbutton":
                # TTK Checkbuttons
                style.configure("TCheckbutton",
                    background=colors["frame_bg"],
                    foreground=colors["label_fg"]
                )
                
            elif widget_class == "TLabelFrame":
                # TTK LabelFrames
                style.configure("TLabelFrame",
                    background=colors["frame_bg"],
                    foreground=colors["label_fg"]
                )
                style.configure("TLabelFrame.Label",
                    background=colors["frame_bg"],
                    foreground=colors["label_fg"]
                )
                
            elif widget_class == "Treeview":
                # TTK Treeview (tables)
                style.configure("Treeview",
                    background=colors["table_bg"],
                    foreground=colors["table_fg"],
                    fieldbackground=colors["table_bg"]
                )
                style.configure("Treeview.Heading",
                    background=colors["button_bg"],
                    foreground=colors["button_fg"]
                )
                style.map("Treeview",
                    background=[('selected', colors["table_select_bg"])],
                    foreground=[('selected', colors["table_select_fg"])]
                )
                
            elif widget_class == "TScrollbar":
                # TTK Scrollbars
                style.configure("TScrollbar",
                    background=colors["button_bg"],
                    troughcolor=colors["frame_bg"],
                    arrowcolor=colors["button_fg"]
                )
                
        except Exception:
            # Some style configurations may not be supported
            # Silently ignore these errors
            pass
            
    def toggle_theme(self) -> str:
        """
        Toggle between light and dark themes.
        
        Returns:
            The new theme name after toggling
        """
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_theme_preference(self.current_theme)
        return self.current_theme
        
    def set_theme(self, theme: str) -> None:
        """
        Set the current theme.
        
        Args:
            theme: Theme name ("light" or "dark")
        """
        if theme in ["light", "dark"]:
            self.current_theme = theme
            self.save_theme_preference(theme)
            
    def save_theme_preference(self, theme: str) -> None:
        """
        Save theme preference to file.
        
        Args:
            theme: Theme name to save
        """
        try:
            preferences = {"theme": theme}
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)
        except (OSError, IOError):
            # Silently ignore file errors for theme preferences
            # Theme will default to light mode if preferences can't be saved
            pass
            
    def load_theme_preference(self) -> str:
        """
        Load theme preference from file.
        
        Returns:
            The saved theme name, defaults to "light" if not found
        """
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    theme = preferences.get("theme", "light")
                    return theme if theme in ["light", "dark"] else "light"
        except (OSError, IOError, json.JSONDecodeError):
            # Return default theme if file can't be read or is corrupted
            pass
            
        return "light"
        
    def apply_theme_to_application(self, root_widget: Any) -> None:
        """
        Apply the current theme to the entire application.
        
        Args:
            root_widget: The root widget of the application
        """
        if TKINTER_AVAILABLE:
            self.apply_theme(root_widget, self.current_theme)
        
    def get_current_theme(self) -> str:
        """
        Get the current theme name.
        
        Returns:
            Current theme name ("light" or "dark")
        """
        return self.current_theme
        
    def is_dark_mode(self) -> bool:
        """
        Check if dark mode is currently active.
        
        Returns:
            True if dark mode is active, False otherwise
        """
        return self.current_theme == "dark"