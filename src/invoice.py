# invoice.py
from fpdf import FPDF
from datetime import datetime
import os
from database import create_connection
import sqlite3

def generate_invoice_pdf(invoice_data):
    try:
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add logo if exists
        logo_path = 'data/store_logo.png'  # You can add a logo file to this path
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=30)
        
        # Store info
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt=invoice_data['store_name'], ln=1, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 5, txt=invoice_data['store_address'], ln=1, align='C')
        pdf.cell(0, 5, txt=f"Phone: {invoice_data['store_phone']}", ln=1, align='C')
        if invoice_data['store_email']:
            pdf.cell(0, 5, txt=f"Email: {invoice_data['store_email']}", ln=1, align='C')
        pdf.ln(10)
        
        # Invoice title
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt="INVOICE", ln=1, align='C')
        pdf.ln(5)
        
        # Invoice details
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 5, txt="Invoice #:", ln=0)
        pdf.cell(50, 5, txt=str(invoice_data['invoice_id']), ln=1)
        
        pdf.cell(40, 5, txt="Date:", ln=0)
        pdf.cell(50, 5, txt=invoice_data['date'], ln=1)
        
        pdf.cell(40, 5, txt="Seller:", ln=0)
        pdf.cell(50, 5, txt=invoice_data['seller_name'], ln=1)
        pdf.ln(5)
        
        # Client info
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 5, txt="Bill To:", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 5, txt="Name:", ln=0)
        pdf.cell(50, 5, txt=invoice_data['client_name'], ln=1)
        
        if invoice_data['client_phone'] != 'N/A':
            pdf.cell(40, 5, txt="Phone:", ln=0)
            pdf.cell(50, 5, txt=invoice_data['client_phone'], ln=1)
            
        if invoice_data['client_address'] != 'N/A':
            pdf.cell(40, 5, txt="Address:", ln=0)
            pdf.cell(50, 5, txt=invoice_data['client_address'], ln=1)
        pdf.ln(10)
        
        # Items table
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 5, txt="Item Details", ln=1)
        pdf.ln(2)
        
        # Table header
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(100, 6, txt="Description", border=1, ln=0)
        pdf.cell(20, 6, txt="Qty", border=1, ln=0, align='C')
        pdf.cell(30, 6, txt="Unit Price", border=1, ln=0, align='R')
        pdf.cell(30, 6, txt="Amount", border=1, ln=1, align='R')
        
        # Table row
        pdf.set_font("Arial", size=10)
        description = f"{invoice_data['phone_brand']} {invoice_data['phone_model']}\nIMEI: {invoice_data['phone_imei']}"
        
        # Split description into lines that fit in the cell
        max_width = 100
        line_height = 5
        desc_lines = []
        words = description.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if pdf.get_string_width(test_line) < max_width:
                current_line = test_line
            else:
                desc_lines.append(current_line)
                current_line = word
        if current_line:
            desc_lines.append(current_line)
        
        # Calculate row height based on description lines
        row_height = max(6, len(desc_lines) * line_height)
        
        # Description cell
        pdf.cell(100, row_height, txt="", border='LTR', ln=0)
        # Save x,y position after description cell
        x, y = pdf.get_x(), pdf.get_y()
        
        # Print each line of description
        for i, line in enumerate(desc_lines):
            pdf.text(x + 2, y + 3 + (i * line_height), line)
        
        # Other cells
        pdf.set_xy(x + 100, y)
        pdf.cell(20, row_height, txt=str(invoice_data['quantity']), border='LTR', ln=0, align='C')
        pdf.cell(30, row_height, txt=f"${invoice_data['unit_price']:.2f}", border='LTR', ln=0, align='R')
        pdf.cell(30, row_height, txt=f"${invoice_data['total_price']:.2f}", border='LTR', ln=1, align='R')
        
        # Bottom border for the row
        pdf.cell(100, 0, border='LBR', ln=0)
        pdf.cell(20, 0, border='LBR', ln=0)
        pdf.cell(30, 0, border='LBR', ln=0)
        pdf.cell(30, 0, border='LBR', ln=1)
        pdf.ln(5)
        
        # Total
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(150, 8, txt="Total:", ln=0, align='R')
        pdf.cell(30, 8, txt=f"${invoice_data['total_price']:.2f}", ln=1, align='R')
        
        # Payment method
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, txt=f"Payment Method: {invoice_data['payment_method'].replace('_', ' ').title()}", ln=1)
        pdf.ln(10)
        
        # Footer
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, txt="Thank you for your business!", ln=1, align='C')
        pdf.cell(0, 5, txt="This is a computer generated invoice.", ln=1, align='C')
        
        # Create invoices directory if not exists
        invoices_dir = 'data/invoices'
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)
        
        # Save the PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(invoices_dir, f"invoice_{invoice_data['invoice_id']}_{timestamp}.pdf")
        pdf.output(pdf_path)
        
        return pdf_path
        
    except Exception as e:
        raise Exception(f"Failed to generate invoice: {str(e)}")