# sales_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkcalendar import DateEntry
from database import create_connection
import sqlite3
from datetime import datetime
from invoice import generate_invoice_pdf
from date_entry import SafeDateEntry

class SalesManager:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.current_sale_id = None
        self.selected_phone_id = None
        self.selected_client_id = None
        
        # Create main frames
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - Form
        self.left_frame = ttk.Frame(self.main_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Right frame - List
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize UI
        self.create_sale_form()
        self.create_sales_list()
        self.load_sales()
        self.load_phones_combobox()
        self.load_clients_combobox()
        
    def create_sale_form(self):
        # Form title
        ttk.Label(self.left_frame, text="New Sale", font=('Helvetica', 14, 'bold')).pack(pady=5)
        
        # Form container
        form_frame = ttk.Frame(self.left_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sale date - Corrected version
        ttk.Label(form_frame, text="Sale Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.sale_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.sale_date_entry = ttk.Entry(form_frame, width=28, textvariable=self.sale_date_var)
        self.sale_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.sale_date_entry.bind('<FocusOut>', lambda e: self._validate_date())
        
        # Phone selection
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.phone_combobox = ttk.Combobox(form_frame, width=28, state='readonly')
        self.phone_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.phone_combobox.bind('<<ComboboxSelected>>', self.on_phone_select)
        
        # Phone details frame
        self.phone_details_frame = ttk.LabelFrame(form_frame, text="Phone Details")
        self.phone_details_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        self.phone_details_label = ttk.Label(self.phone_details_frame, text="Select a phone to view details")
        self.phone_details_label.pack(padx=5, pady=5)
        
        # Client selection
        ttk.Label(form_frame, text="Client:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.client_combobox = ttk.Combobox(form_frame, width=28)
        self.client_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.client_combobox.bind('<<ComboboxSelected>>', self.on_client_select)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.quantity_var = tk.IntVar(value=1)
        self.quantity_spinbox = ttk.Spinbox(form_frame, from_=1, to=100, width=28, 
                                          textvariable=self.quantity_var)
        self.quantity_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Unit price
        ttk.Label(form_frame, text="Unit Price:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        self.unit_price_var = tk.DoubleVar()
        self.unit_price_entry = ttk.Entry(form_frame, width=28, textvariable=self.unit_price_var, 
                                        state='readonly')
        self.unit_price_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Total price
        ttk.Label(form_frame, text="Total Price:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.E)
        self.total_price_var = tk.DoubleVar()
        self.total_price_entry = ttk.Entry(form_frame, width=28, textvariable=self.total_price_var, 
                                          state='readonly')
        self.total_price_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Payment method
        ttk.Label(form_frame, text="Payment:").grid(row=7, column=0, padx=5, pady=5, sticky=tk.E)
        self.payment_method = ttk.Combobox(form_frame, width=28, 
                                          values=['cash', 'credit_card', 'bank_transfer', 'other'])
        self.payment_method.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        self.payment_method.current(0)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=8, column=0, padx=5, pady=5, sticky=tk.NE)
        self.notes_text = tk.Text(form_frame, width=30, height=4)
        self.notes_text.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.left_frame)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Save Sale", command=self.save_sale, 
                  style='success.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_form, 
                  style='warning.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Generate Invoice", command=self.generate_invoice, 
                  style='info.TButton').grid(row=1, column=0, pady=5, columnspan=2)
        
        # Bind quantity change to update total price
        self.quantity_var.trace_add('write', self.update_total_price)
    

    # ------------------------------------------------------------
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _validate_date(self):
        if not self.validate_date(self.sale_date_var.get()):
            messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
            self.sale_date_entry.focus_set()
    # ------------------------------------------------------------


        
    def create_sales_list(self):
        # Search frame
        search_frame = ttk.Frame(self.right_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_sales)
        
        ttk.Button(search_frame, text="Search", command=self.search_sales,
                  style='secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Date filter frame
        date_filter_frame = ttk.Frame(self.right_frame)
        date_filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_filter_frame, text="Filter by Date:").pack(side=tk.LEFT, padx=5)
        
        self.date_from = DateEntry(date_filter_frame, width=12)
        self.date_from.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_filter_frame, text="to").pack(side=tk.LEFT, padx=5)
        
        self.date_to = DateEntry(date_filter_frame, width=12)
        self.date_to.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(date_filter_frame, text="Apply", command=self.filter_by_date,
                  style='secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(date_filter_frame, text="Reset", command=self.reset_date_filter,
                  style='secondary.Outline.TButton').pack(side=tk.LEFT, padx=5)
        
        # Treeview frame
        tree_frame = ttk.Frame(self.right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('id', 'sale_date', 'phone', 'client', 'quantity', 'total_price', 'payment_method')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        
        # Define headings
        self.tree.heading('id', text='ID')
        self.tree.heading('sale_date', text='Date')
        self.tree.heading('phone', text='Phone')
        self.tree.heading('client', text='Client')
        self.tree.heading('quantity', text='Qty')
        self.tree.heading('total_price', text='Total')
        self.tree.heading('payment_method', text='Payment')
        
        # Configure columns
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('sale_date', width=100)
        self.tree.column('phone', width=150)
        self.tree.column('client', width=150)
        self.tree.column('quantity', width=50, anchor=tk.CENTER)
        self.tree.column('total_price', width=80, anchor=tk.E)
        self.tree.column('payment_method', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_sale_select)
        
        # Action buttons
        action_frame = ttk.Frame(self.right_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="View Details", command=self.view_sale_details,
                  style='primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete", command=self.delete_sale,
                  style='danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh", command=self.load_sales,
                  style='info.TButton').pack(side=tk.RIGHT, padx=5)
        
    def load_sales(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            query = """
            SELECT s.id, s.sale_date, 
                   p.brand || ' ' || p.model as phone, 
                   COALESCE(c.name, 'N/A') as client,
                   s.quantity, s.total_price, s.payment_method
            FROM sales s
            LEFT JOIN phones p ON s.phone_id = p.id
            LEFT JOIN clients c ON s.client_id = c.id
            ORDER BY s.sale_date DESC
            """
            cursor.execute(query)
            sales = cursor.fetchall()
            conn.close()
            
            for sale in sales:
                self.tree.insert('', tk.END, values=sale)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load sales: {str(e)}")
    
    def search_sales(self, event=None):
        search_term = self.search_entry.get()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            query = """
            SELECT s.id, s.sale_date, 
                   p.brand || ' ' || p.model as phone, 
                   COALESCE(c.name, 'N/A') as client,
                   s.quantity, s.total_price, s.payment_method
            FROM sales s
            LEFT JOIN phones p ON s.phone_id = p.id
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE p.brand LIKE ? OR p.model LIKE ? OR c.name LIKE ? OR s.payment_method LIKE ?
            ORDER BY s.sale_date DESC
            """
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", 
                                 f"%{search_term}%", f"%{search_term}%"))
            sales = cursor.fetchall()
            conn.close()
            
            for sale in sales:
                self.tree.insert('', tk.END, values=sale)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to search sales: {str(e)}")
    
    def filter_by_date(self):
        date_from = self.date_from.entry.get()
        date_to = self.date_to.entry.get()
        
        if not date_from or not date_to:
            messagebox.showwarning("Warning", "Please select both start and end dates")
            return
            
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            query = """
            SELECT s.id, s.sale_date, 
                   p.brand || ' ' || p.model as phone, 
                   COALESCE(c.name, 'N/A') as client,
                   s.quantity, s.total_price, s.payment_method
            FROM sales s
            LEFT JOIN phones p ON s.phone_id = p.id
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.sale_date BETWEEN ? AND ?
            ORDER BY s.sale_date DESC
            """
            cursor.execute(query, (date_from, date_to))
            sales = cursor.fetchall()
            conn.close()
            
            for sale in sales:
                self.tree.insert('', tk.END, values=sale)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to filter sales: {str(e)}")
    
    def reset_date_filter(self):
        self.date_from.entry.delete(0, tk.END)
        self.date_to.entry.delete(0, tk.END)
        self.load_sales()
    
    def load_phones_combobox(self):
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, brand, model, price, quantity FROM phones WHERE quantity > 0 ORDER BY brand, model")
            phones = cursor.fetchall()
            conn.close()
            
            # Format for combobox display: "Brand Model (Price) [Qty]"
            phone_options = []
            self.phone_options_dict = {}
            
            for phone in phones:
                display_text = f"{phone[1]} {phone[2]} (${phone[3]:.2f}) [Qty: {phone[4]}]"
                phone_options.append(display_text)
                self.phone_options_dict[display_text] = phone[0]  # Store phone_id
            
            self.phone_combobox['values'] = phone_options
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load phones: {str(e)}")
    
    def load_clients_combobox(self):
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM clients ORDER BY name")
            clients = cursor.fetchall()
            conn.close()
            
            # Format for combobox display
            client_options = []
            self.client_options_dict = {}
            
            for client in clients:
                display_text = f"{client[1]}"
                client_options.append(display_text)
                self.client_options_dict[display_text] = client[0]  # Store client_id
            
            self.client_combobox['values'] = client_options
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load clients: {str(e)}")
    
    def on_phone_select(self, event):
        selected_text = self.phone_combobox.get()
        if not selected_text or selected_text not in self.phone_options_dict:
            return
            
        self.selected_phone_id = self.phone_options_dict[selected_text]
        
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT brand, model, price FROM phones WHERE id=?", (self.selected_phone_id,))
            phone = cursor.fetchone()
            conn.close()
            
            if phone:
                # Update phone details
                details = f"Brand: {phone[0]}\nModel: {phone[1]}\nPrice: ${phone[2]:.2f}"
                self.phone_details_label.config(text=details)
                
                # Update unit price
                self.unit_price_var.set(phone[2])
                self.update_total_price()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load phone details: {str(e)}")
    
    def on_client_select(self, event):
        selected_text = self.client_combobox.get()
        if not selected_text or selected_text not in self.client_options_dict:
            return
            
        self.selected_client_id = self.client_options_dict[selected_text]
    
    def update_total_price(self, *args):
        try:
            quantity = self.quantity_var.get()
            unit_price = self.unit_price_var.get()
            total = quantity * unit_price
            self.total_price_var.set(total)
        except:
            pass
    
    def clear_form(self):
        self.current_sale_id = None
        self.selected_phone_id = None
        self.selected_client_id = None
        
        self.sale_date.set_date(datetime.now())
        self.phone_combobox.set('')
        self.client_combobox.set('')
        self.quantity_var.set(1)
        self.unit_price_var.set(0)
        self.total_price_var.set(0)
        self.payment_method.current(0)
        self.notes_text.delete('1.0', tk.END)
        self.phone_details_label.config(text="Select a phone to view details")
    
    def on_sale_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
            
        sale_data = self.tree.item(selected_item)['values']
        if not sale_data:
            return
            
        self.current_sale_id = sale_data[0]
    
    def view_sale_details(self):
        if not self.current_sale_id:
            messagebox.showwarning("Warning", "Please select a sale to view details")
            return
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            query = """
            SELECT s.sale_date, p.brand, p.model, p.imei, p.price, 
                   COALESCE(c.name, 'N/A') as client_name,
                   COALESCE(c.phone, 'N/A') as client_phone,
                   s.quantity, s.unit_price, s.total_price, s.payment_method, s.notes
            FROM sales s
            LEFT JOIN phones p ON s.phone_id = p.id
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.id = ?
            """
            cursor.execute(query, (self.current_sale_id,))
            sale = cursor.fetchone()
            conn.close()
            
            if sale:
                details = (
                    f"Sale Date: {sale[0]}\n"
                    f"Phone: {sale[1]} {sale[2]}\n"
                    f"IMEI: {sale[3]}\n"
                    f"Unit Price: ${sale[4]:.2f}\n"
                    f"Client: {sale[5]}\n"
                    f"Client Phone: {sale[6]}\n"
                    f"Quantity: {sale[7]}\n"
                    f"Total Price: ${sale[9]:.2f}\n"
                    f"Payment Method: {sale[10]}\n"
                    f"Notes: {sale[11] if sale[11] else 'N/A'}"
                )
                messagebox.showinfo("Sale Details", details)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load sale details: {str(e)}")
    
    def save_sale(self):
        # Validate required fields
        if not self.selected_phone_id:
            messagebox.showerror("Error", "Please select a phone")
            return
            
        if self.quantity_var.get() < 1:
            messagebox.showerror("Error", "Quantity must be at least 1")
            return
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            
            # Check phone quantity
            cursor.execute("SELECT quantity FROM phones WHERE id=?", (self.selected_phone_id,))
            current_quantity = cursor.fetchone()[0]
            
            if current_quantity < self.quantity_var.get():
                messagebox.showerror("Error", f"Not enough stock. Only {current_quantity} available.")
                return
            
            # Prepare sale data
            sale_data = {
                'phone_id': self.selected_phone_id,
                'client_id': self.selected_client_id if self.selected_client_id else None,
                'user_id': self.user_data['id'],
                'quantity': self.quantity_var.get(),
                'unit_price': self.unit_price_var.get(),
                'total_price': self.total_price_var.get(),
                'payment_method': self.payment_method.get(),
                'sale_date': self.sale_date.entry.get(),
                'notes': self.notes_text.get('1.0', tk.END).strip()
            }
            
            # Insert sale
            cursor.execute("""
            INSERT INTO sales 
            (phone_id, client_id, user_id, quantity, unit_price, total_price, payment_method, sale_date, notes)
            VALUES (:phone_id, :client_id, :user_id, :quantity, :unit_price, :total_price, :payment_method, :sale_date, :notes)
            """, sale_data)
            
            # Update phone quantity
            new_quantity = current_quantity - sale_data['quantity']
            cursor.execute("UPDATE phones SET quantity=? WHERE id=?", 
                         (new_quantity, sale_data['phone_id']))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Sale recorded successfully")
            
            # Refresh data
            self.clear_form()
            self.load_sales()
            self.load_phones_combobox()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save sale: {str(e)}")
    
    def delete_sale(self):
        if not self.current_sale_id:
            messagebox.showwarning("Warning", "Please select a sale to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this sale?"):
            try:
                conn = create_connection('data/phone_store.db')
                cursor = conn.cursor()
                
                # Get sale details to restore phone quantity
                cursor.execute("SELECT phone_id, quantity FROM sales WHERE id=?", (self.current_sale_id,))
                sale = cursor.fetchone()
                
                if sale:
                    phone_id, sale_quantity = sale
                    
                    # Get current phone quantity
                    cursor.execute("SELECT quantity FROM phones WHERE id=?", (phone_id,))
                    current_quantity = cursor.fetchone()[0]
                    
                    # Restore quantity
                    new_quantity = current_quantity + sale_quantity
                    cursor.execute("UPDATE phones SET quantity=? WHERE id=?", (new_quantity, phone_id))
                    
                    # Delete sale
                    cursor.execute("DELETE FROM sales WHERE id=?", (self.current_sale_id,))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Sale deleted successfully")
                    
                    # Refresh data
                    self.load_sales()
                    self.load_phones_combobox()
                    
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete sale: {str(e)}")
    
    def generate_invoice(self):
        if not self.current_sale_id:
            messagebox.showwarning("Warning", "Please select a sale to generate invoice")
            return
            
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            
            # Get sale details
            query = """
            SELECT s.id, s.sale_date, s.quantity, s.unit_price, s.total_price, s.payment_method,
                   p.brand, p.model, p.imei,
                   COALESCE(c.name, 'N/A') as client_name,
                   COALESCE(c.phone, 'N/A') as client_phone,
                   COALESCE(c.address, 'N/A') as client_address,
                   u.full_name as seller_name,
                   st.name as store_name, st.address as store_address, 
                   st.phone as store_phone, st.email as store_email
            FROM sales s
            LEFT JOIN phones p ON s.phone_id = p.id
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN users u ON s.user_id = u.id
            CROSS JOIN store_info st
            WHERE s.id = ?
            """
            cursor.execute(query, (self.current_sale_id,))
            sale = cursor.fetchone()
            
            if sale:
                # Prepare invoice data
                invoice_data = {
                    'invoice_id': sale[0],
                    'date': sale[1],
                    'quantity': sale[2],
                    'unit_price': sale[3],
                    'total_price': sale[4],
                    'payment_method': sale[5],
                    'phone_brand': sale[6],
                    'phone_model': sale[7],
                    'phone_imei': sale[8],
                    'client_name': sale[9],
                    'client_phone': sale[10],
                    'client_address': sale[11],
                    'seller_name': sale[12],
                    'store_name': sale[13],
                    'store_address': sale[14],
                    'store_phone': sale[15],
                    'store_email': sale[16]
                }
                
                # Generate PDF
                pdf_path = generate_invoice_pdf(invoice_data)
                messagebox.showinfo("Success", f"Invoice generated: {pdf_path}")
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")