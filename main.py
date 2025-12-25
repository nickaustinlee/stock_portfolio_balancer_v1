#!/usr/bin/env python3
"""
Standalone entry point for the Stock Allocation Tool application.

This entry point is designed to work both in development and when packaged
with PyInstaller. It handles proper path resolution for imports and resources.
"""

import sys
import os
from pathlib import Path


def setup_paths():
    """Setup proper paths for both development and packaged execution."""
    if getattr(sys, 'frozen', False):
        # Running as packaged executable
        application_path = Path(sys.executable).parent
        # For PyInstaller, the temporary folder is sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
            bundle_dir = Path(sys._MEIPASS)
        else:
            bundle_dir = application_path
        # Data files should be stored in the application directory
        data_dir = application_path
    else:
        # Running in development
        application_path = Path(__file__).parent
        bundle_dir = application_path
        data_dir = application_path
    
    # Add src directory to Python path
    src_path = bundle_dir / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    else:
        # Fallback for development
        src_path = application_path / 'src'
        if src_path.exists():
            sys.path.insert(0, str(src_path))
    
    # Set working directory to data directory for file operations
    os.chdir(str(data_dir))
    
    return application_path, bundle_dir, data_dir


def main():
    """Main application entry point with threaded loading for responsive UI."""
    splash = None
    
    try:
        # Setup paths for imports
        app_path, bundle_path, data_path = setup_paths()
        
        # Show splash screen immediately
        try:
            import tkinter as tk
            sys.path.insert(0, str(bundle_path / 'src') if bundle_path else 'src')
            from gui.splash_screen import show_splash_screen
            
            splash = show_splash_screen()
            
        except Exception as e:
            print(f"Could not show splash screen: {e}")
        
        # Define the loading function that will run in background thread
        def load_application(splash_screen):
            """Load the application components in background thread."""
            
            # Update status and import heavy dependencies
            splash_screen.update_status("Loading core libraries...")
            from controllers.portfolio_controller import PortfolioController
            
            splash_screen.update_status("Initializing services...")
            from utils.debug import logger
            
            # Show debug status
            if logger.debug_enabled:
                logger.info("Debug mode enabled")
                logger.info(f"Application path: {app_path}")
                logger.info(f"Bundle path: {bundle_path}")
                logger.info(f"Data path: {data_path}")
                logger.info(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
            
            # Create and initialize the controller
            splash_screen.update_status("Creating application...")
            controller = PortfolioController()
            
            splash_screen.update_status("Ready!")
            return controller
        
        if splash:
            # Start loading in background thread
            splash.start_loading(load_application)
            
            # Wait for completion while keeping GUI responsive
            controller, error = splash.wait_for_completion()
            
            if error:
                raise error
            
            # Brief pause to show "Ready!" message
            import time
            time.sleep(0.3)
            
            # Close splash screen
            splash.close()
            splash = None
        else:
            # Fallback if splash screen failed
            controller = load_application(type('MockSplash', (), {'update_status': lambda self, msg: print(msg)})())
        
        # Initialize GUI and start the application
        controller.initialize_gui()
        controller.run()
        
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except ImportError as e:
        if splash:
            splash.close()
        error_msg = f"Import error: {e}"
        print(error_msg)
        print("Please ensure all dependencies are installed.")
        # Try to show a simple error dialog if tkinter is available
        try:
            import tkinter as tk
            import tkinter.messagebox as messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Import Error", error_msg)
        except:
            pass  # If tkinter fails too, just print to console
        sys.exit(1)
    except Exception as e:
        if splash:
            splash.close()
        error_msg = f"Application error: {e}"
        print(error_msg)
        # Try to show error dialog
        try:
            import tkinter as tk
            import tkinter.messagebox as messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
        except:
            pass
        sys.exit(1)
    finally:
        # Clean shutdown
        try:
            if splash:
                splash.close()
            if 'controller' in locals():
                controller.shutdown()
        except:
            pass


if __name__ == "__main__":
    main()