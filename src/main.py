# main.py - Updated version
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from auth import show_login_window
from phone_manager import PhoneManager
from sales_manager import SalesManager
from reports import ReportsManager
from database import create_connection

class MainApplication:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        try:
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {str(e)}")
            self.root.destroy()

    def setup_ui(self):
        self.root.title(f"Phone Store Manager - {self.user_data['full_name']} ({self.user_data['role'].capitalize()})")
        self.root.geometry("1200x700")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', font=('Helvetica', 12))
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame = ttk.Frame(self.main_container, bootstyle="light")
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.header_frame, text=f"Welcome, {self.user_data['full_name']}", 
                 font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(self.header_frame, text="Logout", command=self.logout,
                  style='danger.Outline.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Main content
        self.setup_tabs()

    def setup_tabs(self):
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        try:
            # Phone Management Tab
            self.phone_tab = ttk.Frame(self.notebook)
            PhoneManager(self.phone_tab, self.user_data)
            self.notebook.add(self.phone_tab, text="Phone Management")
            
            # Sales Management Tab
            self.sales_tab = ttk.Frame(self.notebook)
            SalesManager(self.sales_tab, self.user_data)
            self.notebook.add(self.sales_tab, text="Sales")
            
            # Reports Tab
            self.reports_tab = ttk.Frame(self.notebook)
            ReportsManager(self.reports_tab, self.user_data)
            self.notebook.add(self.reports_tab, text="Reports")
            
            # Settings Tab
            self.settings_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.settings_tab, text="Settings")
            
            # Disable tabs based on role
            if self.user_data['role'] == 'seller':
                self.notebook.tab(2, state='disabled')  # Reports
                self.notebook.tab(3, state='disabled')  # Settings
                
        except Exception as e:
            messagebox.showerror("Tab Error", f"Failed to create tabs: {str(e)}")
            raise

    def logout(self):
        self.root.destroy()
        show_login_window(MainApplication.start_main_app)

    @staticmethod
    def start_main_app(user_data):
        root = ttk.Window(themename="litera")
        MainApplication(root, user_data)
        root.mainloop()

if __name__ == "__main__":
    try:
        from database import initialize_database
        initialize_database()
        show_login_window(MainApplication.start_main_app)
    except Exception as e:
        messagebox.showerror("Startup Error", f"Application failed to start: {str(e)}")