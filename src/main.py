# main.py - Fixed version with proper error handling
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import os

# Add the src directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MainApplication:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        
        # Initialize variables
        self.sales_tab = None
        
        try:
            self.setup_ui()
            print("Main application initialized successfully")
        except Exception as e:
            print(f"Error during initialization: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {str(e)}")
            # Don't destroy root here, let the caller handle it
            return

    def setup_ui(self):
        """Setup the main UI"""
        try:
            # Configure the root window
            self.root.title("Phone Shop Management System")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
            
            # Create welcome label
            welcome_frame = ttk.Frame(self.root)
            welcome_frame.pack(fill=tk.X, pady=10)
            
            welcome_label = ttk.Label(
                welcome_frame,
                text=f"Welcome, {self.user_data.get('username', 'User')}!",
                font=('Arial', 16, 'bold')
            )
            welcome_label.pack()
            
            # Setup tabs
            self.setup_tabs()
            
        except Exception as e:
            print(f"Error in setup_ui: {e}")
            raise

    def setup_tabs(self):
        """Setup the tabbed interface"""
        try:
            # Create notebook (tabbed interface)
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create tabs
            self.create_sales_tab()
            self.create_inventory_tab()
            self.create_customers_tab()
            self.create_reports_tab()
            
        except Exception as e:
            print(f"Error in setup_tabs: {e}")
            raise

    def create_sales_tab(self):
        """Create the sales management tab"""
        try:
            # Create sales tab
            self.sales_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.sales_tab, text="Sales Management")
            
            # Initialize sales manager with error handling
            try:
                from sales_manager import SalesManager
                self.sales_manager = SalesManager(self.sales_tab, self.user_data)
            except ImportError as e:
                print(f"Could not import SalesManager: {e}")
                # Create a placeholder
                error_label = ttk.Label(
                    self.sales_tab,
                    text="Sales Manager module not available",
                    font=('Arial', 12)
                )
                error_label.pack(expand=True)
            except Exception as e:
                print(f"Error initializing SalesManager: {e}")
                # Create error display in tab
                error_frame = ttk.Frame(self.sales_tab)
                error_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
                
                ttk.Label(
                    error_frame,
                    text="Error loading Sales Manager",
                    font=('Arial', 14, 'bold'),
                    foreground='red'
                ).pack(pady=10)
                
                ttk.Label(
                    error_frame,
                    text=f"Details: {str(e)}",
                    font=('Arial', 10)
                ).pack(pady=5)
                
                retry_btn = ttk.Button(
                    error_frame,
                    text="Retry",
                    command=self.retry_sales_manager,
                    bootstyle=WARNING
                )
                retry_btn.pack(pady=10)
                
        except Exception as e:
            print(f"Error creating sales tab: {e}")
            raise

    def retry_sales_manager(self):
        """Retry initializing the sales manager"""
        try:
            # Clear the sales tab
            for widget in self.sales_tab.winfo_children():
                widget.destroy()
            
            # Try to reinitialize
            from sales_manager import SalesManager
            self.sales_manager = SalesManager(self.sales_tab, self.user_data)
            messagebox.showinfo("Success", "Sales Manager loaded successfully!")
            
        except Exception as e:
            print(f"Retry failed: {e}")
            messagebox.showerror("Error", f"Failed to load Sales Manager: {str(e)}")

    def create_inventory_tab(self):
        """Create the inventory management tab"""
        try:
            inventory_tab = ttk.Frame(self.notebook)
            self.notebook.add(inventory_tab, text="Inventory")
            
            # Placeholder content
            ttk.Label(
                inventory_tab,
                text="Inventory Management",
                font=('Arial', 16, 'bold')
            ).pack(expand=True)
            
        except Exception as e:
            print(f"Error creating inventory tab: {e}")

    def create_customers_tab(self):
        """Create the customers management tab"""
        try:
            customers_tab = ttk.Frame(self.notebook)
            self.notebook.add(customers_tab, text="Customers")
            
            # Placeholder content
            ttk.Label(
                customers_tab,
                text="Customer Management",
                font=('Arial', 16, 'bold')
            ).pack(expand=True)
            
        except Exception as e:
            print(f"Error creating customers tab: {e}")

    def create_reports_tab(self):
        """Create the reports tab"""
        try:
            reports_tab = ttk.Frame(self.notebook)
            self.notebook.add(reports_tab, text="Reports")
            
            # Placeholder content
            ttk.Label(
                reports_tab,
                text="Reports & Analytics",
                font=('Arial', 16, 'bold')
            ).pack(expand=True)
            
        except Exception as e:
            print(f"Error creating reports tab: {e}")


def start_main_app(user_data):
    """Start the main application safely"""
    try:
        # Create new root window for main app
        root = ttk.Window(themename="morph")  # Using ttkbootstrap window
        
        # Initialize main application
        app = MainApplication(root, user_data)
        
        # Center the window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Start the main loop
        root.mainloop()
        
    except Exception as e:
        print(f"Critical error in start_main_app: {e}")
        if 'root' in locals():
            try:
                root.destroy()
            except:
                pass
        messagebox.showerror("Critical Error", f"Application failed to start: {str(e)}")


if __name__ == "__main__":
    # Test the application directly
    test_user_data = {
        'username': 'TestUser',
        'user_id': 1,
        'role': 'admin'
    }
    start_main_app(test_user_data)