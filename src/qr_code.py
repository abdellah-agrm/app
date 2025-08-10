# qr_code.py
import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from database import create_connection
import sqlite3

class QRScanner:
    def __init__(self, parent):
        self.parent = parent
        self.camera = None
        self.scanning = False
        self.current_frame = None
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera frame
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(fill=tk.BOTH, expand=True)
        
        self.camera_label = ttk.Label(self.camera_frame, text="Camera feed will appear here")
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Start Camera", command=self.start_camera,
                  style='success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Stop Camera", command=self.stop_camera,
                  style='danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Scan from File", command=self.scan_from_file,
                  style='info.TButton').pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.main_frame, text="Scan Results")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10, state='disabled')
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Phone details frame
        self.phone_frame = ttk.LabelFrame(self.main_frame, text="Phone Details")
        self.phone_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.phone_details = tk.Text(self.phone_frame, height=10, state='disabled')
        self.phone_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Start camera automatically
        self.start_camera()
        
    def start_camera(self):
        if self.scanning:
            return
            
        try:
            self.camera = cv2.VideoCapture(0)
            self.scanning = True
            self.update_camera()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            self.camera_label.config(text="Camera not available")
    
    def stop_camera(self):
        self.scanning = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.camera_label.config(image='', text="Camera stopped")
    
    def update_camera(self):
        if not self.scanning or not self.camera:
            return
            
        ret, frame = self.camera.read()
        if ret:
            # Convert to RGB and resize
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            
            # Try to decode QR codes
            decoded_objects = decode(frame)
            if decoded_objects:
                for obj in decoded_objects:
                    data = obj.data.decode('utf-8')
                    self.process_qr_data(data)
                    
                    # Draw rectangle around QR code
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                        hull = list(map(tuple, np.squeeze(hull)))
                    else:
                        hull = points
                    
                    n = len(hull)
                    for j in range(0, n):
                        cv2.line(frame, hull[j], hull[(j+1) % n], (255, 0, 0), 3)
            
            # Convert to ImageTk format
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            self.current_frame = frame
            
        # Schedule next update
        self.camera_label.after(10, self.update_camera)
    
    def scan_from_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                img = cv2.imread(file_path)
                if img is not None:
                    # Convert to grayscale for better QR detection
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    decoded_objects = decode(gray)
                    
                    if decoded_objects:
                        for obj in decoded_objects:
                            data = obj.data.decode('utf-8')
                            self.process_qr_data(data)
                    else:
                        self.update_results("No QR code found in the image")
                else:
                    messagebox.showerror("Error", "Failed to load image")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to scan image: {str(e)}")
    
    def process_qr_data(self, data):
        self.update_results(f"Scanned QR Code: {data}")
        
        # Check if this is a phone QR code (format: "PHONE_ID:123")
        if data.startswith("PHONE_ID:"):
            phone_id = data.split(":")[1].strip()
            self.lookup_phone_details(phone_id)
        else:
            self.update_phone_details("QR code doesn't contain phone information")
    
    def lookup_phone_details(self, phone_id):
        try:
            conn = create_connection('data/phone_store.db')
            cursor = conn.cursor()
            cursor.execute("""
            SELECT p.id, p.brand, p.model, p.imei, p.color, p.storage, p.ram, 
                   p.condition, p.price, p.quantity, p.description
            FROM phones p
            WHERE p.id = ?
            """, (phone_id,))
            phone = cursor.fetchone()
            conn.close()
            
            if phone:
                details = (
                    f"ID: {phone[0]}\n"
                    f"Brand: {phone[1]}\n"
                    f"Model: {phone[2]}\n"
                    f"IMEI: {phone[3]}\n"
                    f"Color: {phone[4]}\n"
                    f"Storage: {phone[5]}\n"
                    f"RAM: {phone[6]}\n"
                    f"Condition: {phone[7]}\n"
                    f"Price: ${phone[8]:.2f}\n"
                    f"Quantity: {phone[9]}\n"
                    f"Description: {phone[10] if phone[10] else 'N/A'}"
                )
                self.update_phone_details(details)
            else:
                self.update_phone_details("Phone not found in database")
                
        except sqlite3.Error as e:
            self.update_phone_details(f"Database error: {str(e)}")
    
    def update_results(self, text):
        self.results_text.config(state='normal')
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state='disabled')
    
    def update_phone_details(self, text):
        self.phone_details.config(state='normal')
        self.phone_details.delete('1.0', tk.END)
        self.phone_details.insert(tk.END, text)
        self.phone_details.config(state='disabled')
    
    def __del__(self):
        self.stop_camera()