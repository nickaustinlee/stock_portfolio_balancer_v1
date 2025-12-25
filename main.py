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
    """
    Setup proper paths for both development and packaged execution.
    
    PyInstaller creates a complex execution environment that requires special handling:
    
    Development mode:
    - Files are in their original locations (src/, main.py, etc.)
    - Python imports work normally
    - Data files are in the project directory
    
    PyInstaller packaged mode:
    - All Python files are bundled into a compressed archive
    - At runtime, PyInstaller extracts files to a temporary directory
    - The executable and data files are in different locations
    - Import paths need to be adjusted to find the extracted files
    
    Returns:
        tuple: (application_path, bundle_dir, data_dir)
    """
    
    # Check if we're running as a PyInstaller-packaged executable
    # sys.frozen is set to True by PyInstaller when running as an executable
    if getattr(sys, 'frozen', False):
        # When packaged, sys.executable points to our actual executable file
        # e.g., "/Applications/StockAllocationTool.app/Contents/MacOS/StockAllocationTool"
        application_path = Path(sys.executable).parent
        
        # _MEIPASS is PyInstaller's "secret sauce" - it's a special attribute that
        # PyInstaller sets to point to the temporary directory where it extracts
        # all the bundled Python files, libraries, and resources at runtime.
        # 
        # Why does this exist?
        # - PyInstaller bundles everything into the executable as compressed data
        # - At startup, it extracts this to a temp dir (usually /var/folders/... on macOS)
        # - _MEIPASS points to this temp extraction directory
        # - This is where we need to look for our Python modules and bundled files
        if hasattr(sys, '_MEIPASS'):
            bundle_dir = Path(sys._MEIPASS)
        else:
            # Fallback: if _MEIPASS doesn't exist (shouldn't happen with modern PyInstaller)
            # just use the application directory
            bundle_dir = application_path
        
        # For data files (portfolio.json, exports/, etc.), we want them to be
        # persistent and accessible to the user, so we put them next to the
        # executable, not in the temporary extraction directory
        data_dir = application_path
        
    else:
        # Running in development - everything is in the normal project structure
        # __file__ is this main.py script, so parent directory is the project root
        application_path = Path(__file__).parent
        bundle_dir = application_path  # Same as app path in development
        data_dir = application_path    # Same as app path in development
    
    # Now we need to make sure Python can import our modules
    # In development: src/ is relative to the project root
    # In packaged mode: src/ was bundled and extracted to the _MEIPASS directory
    src_path = bundle_dir / 'src'
    
    if src_path.exists():
        # Add the src directory to Python's import path so we can do:
        # from controllers.portfolio_controller import PortfolioController
        sys.path.insert(0, str(src_path))
    else:
        # Fallback: try looking for src/ relative to the application
        # This handles edge cases in different PyInstaller configurations
        src_path = application_path / 'src'
        if src_path.exists():
            sys.path.insert(0, str(src_path))
    
    # Set the working directory to where we want data files to be created
    # This ensures portfolio.json, exports/, etc. are created in a sensible location
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
            
            # Show debug status (only visible when debug mode is enabled)
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