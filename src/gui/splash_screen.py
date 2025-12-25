"""
Splash screen for Stock Allocation Tool.

Provides visual feedback during application startup with progress indication.
Uses threading to keep the UI responsive during heavy imports.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import queue


class SplashScreen:
    """
    Threaded splash screen that stays responsive during heavy imports.
    
    Uses a background thread for imports while keeping the GUI animated
    on the main thread.
    """
    
    def __init__(self):
        """Initialize the splash screen."""
        self.root = tk.Tk()
        self.root.title("Stock Allocation Tool")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')
        
        # Remove window decorations for a cleaner look
        self.root.overrideredirect(True)
        
        # Configure colors
        bg_color = "#f0f0f0"
        text_color = "#333333"
        accent_color = "#007bff"
        
        self.root.configure(bg=bg_color)
        
        # Create main frame with border
        main_frame = tk.Frame(self.root, bg=bg_color, relief="raised", bd=2)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Application title
        title_label = tk.Label(
            main_frame,
            text="Stock Allocation Tool",
            font=("Arial", 18, "bold"),
            bg=bg_color,
            fg=text_color
        )
        title_label.pack(pady=(30, 10))
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text="Version 1.0.0",
            font=("Arial", 10),
            bg=bg_color,
            fg=text_color
        )
        version_label.pack(pady=(0, 20))
        
        # Loading message
        self.status_label = tk.Label(
            main_frame,
            text="Loading application...",
            font=("Arial", 10),
            bg=bg_color,
            fg=text_color
        )
        self.status_label.pack(pady=(0, 15))
        
        # Progress bar with smooth animation
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=(0, 30))
        
        # Start progress animation
        self.progress.start(5)  # Smooth animation
        
        # Copyright info
        copyright_label = tk.Label(
            main_frame,
            text="Portfolio Management Tool",
            font=("Arial", 8),
            bg=bg_color,
            fg=text_color
        )
        copyright_label.pack(side="bottom", pady=(0, 10))
        
        # Keep window on top
        self.root.attributes('-topmost', True)
        
        # Threading setup
        self.message_queue = queue.Queue()
        self.loading_complete = False
        self.controller = None
        self.error = None
        
        # Update the display
        self.root.update()
    
    def update_status(self, message: str):
        """
        Update the status message on the splash screen.
        Thread-safe method that can be called from any thread.
        
        Args:
            message: Status message to display
        """
        # Put message in queue for main thread to process
        self.message_queue.put(('status', message))
    
    def _process_messages(self):
        """Process messages from the background thread."""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                if msg_type == 'status':
                    self.status_label.config(text=data)
                elif msg_type == 'complete':
                    self.controller = data
                    self.loading_complete = True
                elif msg_type == 'error':
                    self.error = data
                    self.loading_complete = True
        except queue.Empty:
            pass
        
        # Schedule next check
        if not self.loading_complete:
            self.root.after(50, self._process_messages)
    
    def start_loading(self, load_function):
        """
        Start the loading process in a background thread.
        
        Args:
            load_function: Function to call for loading (should return controller or raise exception)
        """
        def background_load():
            try:
                controller = load_function(self)
                self.message_queue.put(('complete', controller))
            except Exception as e:
                self.message_queue.put(('error', e))
        
        # Start background thread
        thread = threading.Thread(target=background_load, daemon=True)
        thread.start()
        
        # Start processing messages
        self._process_messages()
    
    def wait_for_completion(self):
        """
        Wait for loading to complete while keeping the GUI responsive.
        
        Returns:
            tuple: (controller, error) - one will be None
        """
        while not self.loading_complete:
            self.root.update()
            time.sleep(0.01)  # Small delay to prevent busy waiting
        
        return self.controller, self.error
    
    def close(self):
        """Close the splash screen."""
        try:
            if self.progress:
                self.progress.stop()
            if self.root:
                self.root.destroy()
        except:
            pass  # Ignore errors during cleanup
    
    def show(self):
        """Show the splash screen (non-blocking)."""
        self.root.update()
        return self


def show_splash_screen():
    """
    Create and show a splash screen.
    
    Returns:
        SplashScreen: The splash screen instance
    """
    return SplashScreen().show()