# phone_manager.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import qrcode
import os
from datetime import datetime
from database import create_connection
import sqlite3


class PhoneManager:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.current_phone_id = None
        self.qr_image = None

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
        self.create_form()
        self.create_phone_list()
        self.load_phones()

    def create_form(self):
        # Form title
        ttk.Label(
            self.left_frame, text="Phone Details", font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        # Form container
        form_frame = ttk.Frame(self.left_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Form fields
        fields = [
            ("brand", "Brand:", "text"),
            ("model", "Model:", "text"),
            ("imei", "IMEI:", "text"),
            ("color", "Color:", "text"),
            ("storage", "Storage:", "text"),
            ("ram", "RAM:", "text"),
            ("condition", "Condition:", "combobox", ["new", "used", "refurbished"]),
            ("price", "Price:", "number"),
            ("cost_price", "Cost Price:", "number"),
            ("quantity", "Quantity:", "number"),
            ("description", "Description:", "textarea"),
        ]

        self.entries = {}
        row = 0
        for field in fields:
            label = ttk.Label(form_frame, text=field[1])
            label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.E)

            if field[2] == "text":
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            elif field[2] == "number":
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            elif field[2] == "combobox":
                entry = ttk.Combobox(form_frame, width=28, values=field[3])
                entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            elif field[2] == "textarea":
                entry = tk.Text(form_frame, width=30, height=4)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)

            self.entries[field[0]] = entry
            row += 1

        # QR Code Frame
        self.qr_frame = ttk.Frame(self.left_frame, borderwidth=1, relief=tk.SOLID)
        self.qr_frame.pack(pady=10)

        self.qr_label = ttk.Label(self.qr_frame, text="QR Code will appear here")
        self.qr_label.pack(padx=10, pady=10)

        # Buttons frame
        buttons_frame = ttk.Frame(self.left_frame)
        buttons_frame.pack(pady=10)

        ttk.Button(
            buttons_frame, text="Save", command=self.save_phone, style="success.TButton"
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            buttons_frame,
            text="Clear",
            command=self.clear_form,
            style="warning.TButton",
        ).grid(row=0, column=1, padx=5)
        ttk.Button(
            buttons_frame,
            text="Print QR",
            command=self.print_qr_code,
            style="info.TButton",
        ).grid(row=1, column=0, pady=5, columnspan=2)

    def create_phone_list(self):
        # Search frame
        search_frame = ttk.Frame(self.right_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_phones)

        ttk.Button(
            search_frame,
            text="Search",
            command=self.search_phones,
            style="secondary.TButton",
        ).pack(side=tk.LEFT, padx=5)

        # Treeview frame
        tree_frame = ttk.Frame(self.right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        columns = ("id", "brand", "model", "imei", "price", "quantity")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("brand", text="Brand")
        self.tree.heading("model", text="Model")
        self.tree.heading("imei", text="IMEI")
        self.tree.heading("price", text="Price")
        self.tree.heading("quantity", text="Qty")

        # Configure columns
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("brand", width=100)
        self.tree.column("model", width=150)
        self.tree.column("imei", width=150)
        self.tree.column("price", width=80, anchor=tk.E)
        self.tree.column("quantity", width=50, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_phone_select)

        # Action buttons
        action_frame = ttk.Frame(self.right_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            action_frame, text="Edit", command=self.edit_phone, style="primary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame,
            text="Delete",
            command=self.delete_phone,
            style="danger.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame, text="Refresh", command=self.load_phones, style="info.TButton"
        ).pack(side=tk.RIGHT, padx=5)

    def load_phones(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = create_connection("data/phone_store.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, brand, model, imei, price, quantity FROM phones ORDER BY brand, model"
            )
            phones = cursor.fetchall()
            conn.close()

            for phone in phones:
                self.tree.insert("", tk.END, values=phone)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load phones: {str(e)}")

    def search_phones(self, event=None):
        search_term = self.search_entry.get()

        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = create_connection("data/phone_store.db")
            cursor = conn.cursor()
            query = """
            SELECT id, brand, model, imei, price, quantity 
            FROM phones 
            WHERE brand LIKE ? OR model LIKE ? OR imei LIKE ?
            ORDER BY brand, model
            """
            cursor.execute(
                query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            )
            phones = cursor.fetchall()
            conn.close()

            for phone in phones:
                self.tree.insert("", tk.END, values=phone)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to search phones: {str(e)}")

    def clear_form(self):
        self.current_phone_id = None
        for field, entry in self.entries.items():
            if isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)

        # Clear QR code display
        self.qr_label.config(image="", text="QR Code will appear here")
        self.qr_image = None

    def on_phone_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        phone_data = self.tree.item(selected_item)["values"]
        if not phone_data:
            return

        self.current_phone_id = phone_data[0]

        try:
            conn = create_connection("data/phone_store.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM phones WHERE id=?", (self.current_phone_id,))
            phone = cursor.fetchone()
            conn.close()

            if phone:
                # Map data to form fields
                fields = [
                    "brand",
                    "model",
                    "imei",
                    "color",
                    "storage",
                    "ram",
                    "condition",
                    "price",
                    "cost_price",
                    "quantity",
                    "description",
                ]

                for i, field in enumerate(fields):
                    if field in self.entries:
                        entry = self.entries[field]
                        if isinstance(entry, tk.Text):
                            entry.delete("1.0", tk.END)
                            entry.insert("1.0", phone[i + 1] if phone[i + 1] else "")
                        else:
                            entry.delete(0, tk.END)
                            entry.insert(0, phone[i + 1] if phone[i + 1] else "")

                # Display QR code if exists
                qr_path = phone[11]  # qr_code_path field
                if qr_path and os.path.exists(qr_path):
                    self.display_qr_code(qr_path)
                else:
                    self.generate_qr_code()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to load phone details: {str(e)}"
            )

    def save_phone(self):
        # Validate required fields
        if not self.entries["brand"].get() or not self.entries["model"].get():
            messagebox.showerror("Error", "Brand and Model are required fields")
            return

        try:
            conn = create_connection("data/phone_store.db")
            cursor = conn.cursor()

            # Prepare data
            phone_data = {
                "brand": self.entries["brand"].get(),
                "model": self.entries["model"].get(),
                "imei": self.entries["imei"].get(),
                "color": self.entries["color"].get(),
                "storage": self.entries["storage"].get(),
                "ram": self.entries["ram"].get(),
                "condition": self.entries["condition"].get(),
                "price": float(self.entries["price"].get() or 0),
                "cost_price": float(self.entries["cost_price"].get() or 0),
                "quantity": int(self.entries["quantity"].get() or 1),
                "description": self.entries["description"].get("1.0", tk.END).strip(),
            }

            if self.current_phone_id:
                # Update existing phone
                phone_data["id"] = self.current_phone_id
                cursor.execute(
                    """
                UPDATE phones 
                SET brand=:brand, model=:model, imei=:imei, color=:color, storage=:storage, 
                    ram=:ram, condition=:condition, price=:price, cost_price=:cost_price, 
                    quantity=:quantity, description=:description, updated_at=CURRENT_TIMESTAMP
                WHERE id=:id
                """,
                    phone_data,
                )
                messagebox.showinfo("Success", "Phone updated successfully")
            else:
                # Insert new phone
                cursor.execute(
                    """
                INSERT INTO phones 
                (brand, model, imei, color, storage, ram, condition, price, cost_price, quantity, description)
                VALUES (:brand, :model, :imei, :color, :storage, :ram, :condition, :price, :cost_price, :quantity, :description)
                """,
                    phone_data,
                )
                self.current_phone_id = cursor.lastrowid
                messagebox.showinfo("Success", "Phone added successfully")

                # Generate QR code for new phone
                self.generate_qr_code()

            conn.commit()
            conn.close()

            # Refresh phone list
            self.load_phones()

        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers for price and quantity"
            )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save phone: {str(e)}")

    def edit_phone(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a phone to edit")
            return

        self.on_phone_select(None)  # Load selected phone into form

    def delete_phone(self):
        if not self.current_phone_id:
            messagebox.showwarning("Warning", "Please select a phone to delete")
            return

        if self.user_data["role"] != "admin":
            messagebox.showerror("Permission Denied", "Only admin can delete phones")
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this phone?"
        ):
            try:
                conn = create_connection("data/phone_store.db")
                cursor = conn.cursor()

                # Get QR code path to delete the file
                cursor.execute(
                    "SELECT qr_code_path FROM phones WHERE id=?",
                    (self.current_phone_id,),
                )
                qr_path = cursor.fetchone()[0]

                # Delete phone from database
                cursor.execute(
                    "DELETE FROM phones WHERE id=?", (self.current_phone_id,)
                )
                conn.commit()
                conn.close()

                # Delete QR code file if exists
                if qr_path and os.path.exists(qr_path):
                    os.remove(qr_path)

                messagebox.showinfo("Success", "Phone deleted successfully")
                self.clear_form()
                self.load_phones()

            except sqlite3.Error as e:
                messagebox.showerror(
                    "Database Error", f"Failed to delete phone: {str(e)}"
                )

    def generate_qr_code(self):
        if not self.current_phone_id:
            messagebox.showwarning("Warning", "Please save phone details first")
            return

        try:
            conn = create_connection("data/phone_store.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT brand, model, imei FROM phones WHERE id=?", (self.current_phone_id,)
            )
            phone = cursor.fetchone()
            conn.close()

            if phone:
                # Create QR code data - simplified version
                qr_data = f"PHONE:{self.current_phone_id}|{phone[0]}|{phone[1]}|{phone[2]}"

                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                # Save QR code image
                qr_dir = "data/qr_codes"
                if not os.path.exists(qr_dir):
                    os.makedirs(qr_dir)

                qr_path = os.path.join(qr_dir, f"phone_{self.current_phone_id}.png")
                img.save(qr_path)

                # Update database with QR code path
                conn = create_connection("data/phone_store.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE phones SET qr_code_path=? WHERE id=?",
                    (qr_path, self.current_phone_id),
                )
                conn.commit()
                conn.close()

                # Display QR code
                self.display_qr_code(qr_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")

    def display_qr_code(self, qr_path):
        try:
            # Open and resize the image
            img = Image.open(qr_path)
            img = img.resize((200, 200), Image.LANCZOS)

            # Convert to PhotoImage
            self.qr_image = ImageTk.PhotoImage(img)

            # Update the label
            self.qr_label.config(image=self.qr_image)
            self.qr_label.image = self.qr_image  # Keep a reference!

        except Exception as e:
            messagebox.showerror("Error", f"Failed to display QR code: {str(e)}")
            self.qr_label.config(image="", text="QR Code not available")

    def print_qr_code(self):
        if not hasattr(self, "qr_image") or not self.qr_image:
            messagebox.showwarning("Warning", "No QR code to print")
            return

        try:
            # Get the QR code path from the database
            conn = create_connection("data/phone_store.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT qr_code_path FROM phones WHERE id=?", (self.current_phone_id,)
            )
            qr_path = cursor.fetchone()[0]
            conn.close()

            if qr_path and os.path.exists(qr_path):
                # Open the image
                img = Image.open(qr_path)

                # Ask user where to save the printable version
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    initialfile=f"phone_qr_{self.current_phone_id}.png",
                )

                if file_path:
                    img.save(file_path)
                    messagebox.showinfo(
                        "Success",
                        f"QR code saved to:\n{file_path}\nYou can print this file.",
                    )
            else:
                messagebox.showerror("Error", "QR code file not found")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to print QR code: {str(e)}")
