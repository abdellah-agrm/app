# sales_manager.py - Fixed version
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

# Fix for DateEntry compatibility
class SafeDateEntry:
    """A safe wrapper for DateEntry that handles compatibility issues"""
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        # Create a simple date entry using Entry widget with date validation
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable=self.var, width=12)
        self.entry.pack(side=tk.LEFT, padx=(0, 2))
        
        # Set default date to today
        today = date.today()
        self.var.set(today.strftime("%Y-%m-%d"))
        
        # Add a button to manually set date
        self.button = ttk.Button(self.frame, text="📅", width=3, 
                               command=self._show_date_picker)
        self.button.pack(side=tk.LEFT)
        
        # Store the current date
        self._date = today
        
        # Bind validation
        self.var.trace('w', self._validate_date)
    
    def _validate_date(self, *args):
        """Validate the entered date"""
        try:
            date_str = self.var.get()
            if date_str:
                self._date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass  # Keep the previous valid date
    
    def _show_date_picker(self):
        """Show a simple date picker dialog"""
        # For now, just open a simple input dialog
        result = tk.simpledialog.askstring(
            "Select Date", 
            "Enter date (YYYY-MM-DD):", 
            initialvalue=self.var.get()
        )
        if result:
            try:
                datetime.strptime(result, "%Y-%m-%d")
                self.var.set(result)
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
    
    def get_date(self):
        """Get the current date"""
        return self._date
    
    def set_date(self, new_date):
        """Set a new date"""
        if isinstance(new_date, date):
            self._date = new_date
            self.var.set(new_date.strftime("%Y-%m-%d"))
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)

class SalesManager:
    def __init__(self, parent_frame, user_data):
        self.parent_frame = parent_frame
        self.user_data = user_data
        self.db_path = "../data/phone_store.db"
        
        # Initialize variables
        self.sales_tree = None
        self.date_from = None
        self.date_to = None
        
        try:
            self.create_sales_list()
            self.load_sales_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize Sales Manager: {str(e)}")
            print(f"Sales Manager initialization error: {e}")

    def create_sales_list(self):
        """Create the sales list interface with safe date entries"""
        try:
            # Main container
            main_container = ttk.Frame(self.parent_frame)
            main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Title
            title_label = ttk.Label(main_container, text="Sales Management", 
                                  font=('Arial', 16, 'bold'))
            title_label.pack(pady=(0, 10))
            
            # Controls frame
            controls_frame = ttk.LabelFrame(main_container, text="Controls", padding=10)
            controls_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Date filter frame
            date_filter_frame = ttk.Frame(controls_frame)
            date_filter_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Date from
            ttk.Label(date_filter_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
            self.date_from = SafeDateEntry(date_filter_frame)
            self.date_from.pack(side=tk.LEFT, padx=(0, 15))
            
            # Date to
            ttk.Label(date_filter_frame, text="To:").pack(side=tk.LEFT, padx=(0, 5))
            self.date_to = SafeDateEntry(date_filter_frame)
            self.date_to.pack(side=tk.LEFT, padx=(0, 15))
            
            # Filter button
            filter_btn = ttk.Button(date_filter_frame, text="Filter", 
                                  command=self.filter_sales, bootstyle=PRIMARY)
            filter_btn.pack(side=tk.LEFT, padx=(10, 0))
            
            # Buttons frame
            buttons_frame = ttk.Frame(controls_frame)
            buttons_frame.pack(fill=tk.X)
            
            # Add buttons
            add_sale_btn = ttk.Button(buttons_frame, text="Add Sale", 
                                    command=self.add_sale_dialog, bootstyle=SUCCESS)
            add_sale_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            edit_sale_btn = ttk.Button(buttons_frame, text="Edit Sale", 
                                     command=self.edit_sale_dialog, bootstyle=WARNING)
            edit_sale_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            delete_sale_btn = ttk.Button(buttons_frame, text="Delete Sale", 
                                       command=self.delete_sale, bootstyle=DANGER)
            delete_sale_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            refresh_btn = ttk.Button(buttons_frame, text="Refresh", 
                                   command=self.load_sales_data, bootstyle=INFO)
            refresh_btn.pack(side=tk.LEFT)
            
            # Sales tree frame
            tree_frame = ttk.LabelFrame(main_container, text="Sales Records", padding=10)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create treeview
            columns = ("ID", "Customer", "Phone", "Product", "Quantity", "Price", "Total", "Date")
            self.sales_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            
            # Configure columns
            self.sales_tree.heading("ID", text="ID")
            self.sales_tree.heading("Customer", text="Customer")
            self.sales_tree.heading("Phone", text="Phone")
            self.sales_tree.heading("Product", text="Product")
            self.sales_tree.heading("Quantity", text="Qty")
            self.sales_tree.heading("Price", text="Price")
            self.sales_tree.heading("Total", text="Total")
            self.sales_tree.heading("Date", text="Date")
            
            # Configure column widths
            self.sales_tree.column("ID", width=50)
            self.sales_tree.column("Customer", width=120)
            self.sales_tree.column("Phone", width=100)
            self.sales_tree.column("Product", width=150)
            self.sales_tree.column("Quantity", width=60)
            self.sales_tree.column("Price", width=80)
            self.sales_tree.column("Total", width=80)
            self.sales_tree.column("Date", width=100)
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
            self.sales_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack treeview and scrollbars
            self.sales_tree.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            # Configure grid weights
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            print("Sales list interface created successfully")
            
        except Exception as e:
            print(f"Error creating sales list: {e}")
            messagebox.showerror("Error", f"Failed to create sales interface: {str(e)}")

    def load_sales_data(self):
        """Load sales data from database"""
        try:
            # Clear existing data
            if self.sales_tree:
                for item in self.sales_tree.get_children():
                    self.sales_tree.delete(item)
            
            # Connect to database and fetch data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, customer_name, customer_phone, product_name, 
                       quantity, unit_price, total_amount, sale_date 
                FROM sales 
                ORDER BY sale_date DESC
            """)
            
            sales_data = cursor.fetchall()
            conn.close()
            
            # Insert data into treeview
            if self.sales_tree:
                for sale in sales_data:
                    # Format the data for display
                    formatted_sale = (
                        sale[0],  # ID
                        sale[1],  # Customer name
                        sale[2],  # Phone
                        sale[3],  # Product
                        sale[4],  # Quantity
                        f"${sale[5]:.2f}",  # Unit price
                        f"${sale[6]:.2f}",  # Total
                        sale[7]   # Date
                    )
                    self.sales_tree.insert("", "end", values=formatted_sale)
            
            print(f"Loaded {len(sales_data)} sales records")
            
        except Exception as e:
            print(f"Error loading sales data: {e}")
            messagebox.showerror("Error", f"Failed to load sales data: {str(e)}")

    def filter_sales(self):
        """Filter sales by date range"""
        try:
            if not self.date_from or not self.date_to:
                return
            
            from_date = self.date_from.get_date()
            to_date = self.date_to.get_date()
            
            # Clear existing data
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            # Connect to database and fetch filtered data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, customer_name, customer_phone, product_name, 
                       quantity, unit_price, total_amount, sale_date 
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
                ORDER BY sale_date DESC
            """, (from_date, to_date))
            
            sales_data = cursor.fetchall()
            conn.close()
            
            # Insert filtered data
            for sale in sales_data:
                formatted_sale = (
                    sale[0],  # ID
                    sale[1],  # Customer name
                    sale[2],  # Phone
                    sale[3],  # Product
                    sale[4],  # Quantity
                    f"${sale[5]:.2f}",  # Unit price
                    f"${sale[6]:.2f}",  # Total
                    sale[7]   # Date
                )
                self.sales_tree.insert("", "end", values=formatted_sale)
            
            messagebox.showinfo("Filter Applied", f"Showing {len(sales_data)} records from {from_date} to {to_date}")
            
        except Exception as e:
            print(f"Error filtering sales: {e}")
            messagebox.showerror("Error", f"Failed to filter sales: {str(e)}")

    def add_sale_dialog(self):
        """Open dialog to add new sale"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Add New Sale")
        dialog.geometry("400x500")
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"400x500+{x}+{y}")
        
        # Create form fields
        ttk.Label(dialog, text="Customer Name:").pack(pady=5)
        customer_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=customer_name_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Customer Phone:").pack(pady=5)
        customer_phone_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=customer_phone_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Product Name:").pack(pady=5)
        product_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=product_name_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Quantity:").pack(pady=5)
        quantity_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=quantity_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Unit Price:").pack(pady=5)
        price_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=price_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Sale Date:").pack(pady=5)
        date_var = tk.StringVar()
        date_var.set(date.today().strftime("%Y-%m-%d"))
        ttk.Entry(dialog, textvariable=date_var, width=40).pack(pady=5)
        
        def save_sale():
            try:
                # Validate inputs
                if not all([customer_name_var.get(), customer_phone_var.get(), 
                          product_name_var.get(), quantity_var.get(), price_var.get()]):
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                quantity = int(quantity_var.get())
                unit_price = float(price_var.get())
                total_amount = quantity * unit_price
                
                # Save to database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO sales (customer_name, customer_phone, product_name, 
                                     quantity, unit_price, total_amount, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (customer_name_var.get(), customer_phone_var.get(), 
                     product_name_var.get(), quantity, unit_price, 
                     total_amount, date_var.get()))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Sale added successfully!")
                dialog.destroy()
                self.load_sales_data()  # Refresh the list
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantity and price!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add sale: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_sale, 
                  bootstyle=SUCCESS).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                  bootstyle=DANGER).pack(side=tk.LEFT, padx=10)

    def edit_sale_dialog(self):
        """Edit selected sale"""
        selected_item = self.sales_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a sale to edit!")
            return
        
        # Get selected sale data
        sale_values = self.sales_tree.item(selected_item[0])['values']
        sale_id = sale_values[0]
        
        # Similar dialog to add_sale_dialog but with pre-filled values
        messagebox.showinfo("Edit Sale", f"Edit functionality for sale ID: {sale_id}")
        # Implementation similar to add_sale_dialog with UPDATE query

    def delete_sale(self):
        """Delete selected sale"""
        selected_item = self.sales_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a sale to delete!")
            return
        
        sale_values = self.sales_tree.item(selected_item[0])['values']
        sale_id = sale_values[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete sale ID: {sale_id}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Sale deleted successfully!")
                self.load_sales_data()  # Refresh the list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete sale: {str(e)}")