# auth.py - Fixed version with proper main app integration
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

class AuthWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Phone Shop - Login")
        self.master.geometry("400x500")
        self.master.resizable(False, False)
        
        # Center the window
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.master.winfo_screenheight() // 2) - (500 // 2)
        self.master.geometry(f"400x500+{x}+{y}")
        
        # Find the correct database path
        self.db_path = self.find_database_path()
        print(f"Using database path: {self.db_path}")
        self.create_login_ui()
        
        # Bind Enter key to login
        self.master.bind('<Return>', lambda event: self.authenticate())

    def find_database_path(self):
        """Find the correct database path"""
        import os
        
        possible_paths = [
            "data/phone_store.db",  # Standard structure
            "../data/phone_store.db",  # If running from src/
            "phone_store.db",  # Root directory
            "db/phone_store.db",  # Alternative structure
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "phone_store.db"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found data at: {path}")
                return path
        
        # Print diagnostic info
        print("data not found! Current directory:", os.getcwd())
        print("Contents of current directory:")
        for item in os.listdir("."):
            print(f"  {item}")
        
        # Try the most likely path
        return "data/phone_store.db"

    def create_login_ui(self):
        """Create the login interface"""
        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Title
        title_label = ttk.Label(main_frame, text="Phone Shop Management", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 30))
        
        subtitle_label = ttk.Label(main_frame, text="Login to Continue", 
                                  font=('Arial', 12))
        subtitle_label.pack(pady=(0, 40))
        
        # Login form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(expand=True, fill=tk.BOTH)
        
        # Username
        ttk.Label(form_frame, text="Username:", font=('Arial', 11)).pack(anchor='w', pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, 
                                       font=('Arial', 11), width=25)
        self.username_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Password
        ttk.Label(form_frame, text="Password:", font=('Arial', 11)).pack(anchor='w', pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                       show="*", font=('Arial', 11), width=25)
        self.password_entry.pack(fill=tk.X, pady=(0, 30))
        
        # Login button
        self.login_btn = ttk.Button(form_frame, text="Login", 
                                   command=self.authenticate, 
                                   bootstyle=PRIMARY, width=20)
        self.login_btn.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ttk.Label(form_frame, text="", font=('Arial', 10))
        self.status_label.pack(pady=(0, 20))
        
        # Focus on username entry
        self.username_entry.focus()

    def authenticate(self):
        """Authenticate user credentials"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.show_status("Please enter both username and password", "error")
            return
        
        try:
            # Hash the password
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            # Check credentials in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, full_name 
                FROM users 
                WHERE username = ? AND password = ?
            """, (username, password_hash))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                self.show_status("Login successful!", "success")
                user_dict = {
                    'user_id': user_data[0],
                    'username': user_data[1],
                    'role': user_data[2],
                    'full_name': user_data[3] if user_data[3] else user_data[1]
                }
                
                # Close login window and start main app
                self.on_login_success(user_dict)
            else:
                self.show_status("Invalid username or password", "error")
                
        except sqlite3.Error as e:
            self.show_status(f"Database error: {str(e)}", "error")
            print(f"Database error during authentication: {e}")
        except Exception as e:
            self.show_status(f"Login error: {str(e)}", "error")
            print(f"Authentication error: {e}")

    def show_status(self, message, status_type="info"):
        """Show status message"""
        colors = {
            "success": "green",
            "error": "red",
            "info": "blue"
        }
        
        self.status_label.config(text=message, foreground=colors.get(status_type, "black"))
        
        if status_type == "success":
            # Clear the message after 2 seconds for success
            self.master.after(2000, lambda: self.status_label.config(text=""))

    def on_login_success(self, user_data):
        """Handle successful login"""
        try:
            # Import here to avoid circular imports
            from main import start_main_app
            
            # Hide the login window
            self.master.withdraw()
            
            # Start main application
            start_main_app(user_data)
            
            # Close login window after main app closes
            self.master.destroy()
            
        except Exception as e:
            print(f"Error starting main application: {e}")
            messagebox.showerror("Error", f"Failed to start main application: {str(e)}")
            # Show login window again if main app fails
            self.master.deiconify()


def main():
    """Main function to start the application"""
    try:
        # Create the main window with ttkbootstrap
        root = ttk_boot.Window(themename="morph")
        
        # Create auth window
        auth_window = AuthWindow(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"Critical error starting application: {e}")
        messagebox.showerror("Critical Error", f"Application failed to start: {str(e)}")


if __name__ == "__main__":
    main()