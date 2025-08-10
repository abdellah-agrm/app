# auth.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from database import create_connection
import sqlite3

class LoginWindow:
    def __init__(self, master, on_login_success):
        self.master = master
        self.on_login_success = on_login_success
        
        self.master.title("Phone Store Manager - Login")
        self.master.geometry("400x300")
        self.master.resizable(False, False)
        
        # Style
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12))
        
        # Main frame
        self.main_frame = ttk.Frame(self.master, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Logo/Title
        ttk.Label(self.main_frame, text="Phone Store Manager", font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Login form
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.username_entry = ttk.Entry(form_frame, width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.password_entry = ttk.Entry(form_frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Login button
        ttk.Button(self.main_frame, text="Login", command=self.authenticate, 
                  style='primary.TButton').pack(pady=10)
        
        # Focus on username entry
        self.username_entry.focus_set()
        
        # Bind Enter key to login
        self.master.bind('<Return>', lambda event: self.authenticate())

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, full_name FROM users WHERE username=? AND password=?", 
                          (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2],
                    'full_name': user[3]
                }
                self.on_login_success(user_data)
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

def show_login_window(on_login_success):
    root = ttk.Window(themename="litera")
    LoginWindow(root, on_login_success)
    root.mainloop()