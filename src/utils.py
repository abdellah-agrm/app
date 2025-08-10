# utils.py
import os
import sqlite3
from tkinter import messagebox
from database import create_connection

def backup_database():
    """ Create a backup of the database """
    try:
        if not os.path.exists('data/backups'):
            os.makedirs('data/backups')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/backups/phone_store_backup_{timestamp}.db"
        
        # Connect to the original database
        source = create_connection('data/phone_store.db')
        
        # Create the backup database
        backup = sqlite3.connect(backup_path)
        
        # Copy the database
        with backup:
            source.backup(backup)
        
        # Close connections
        source.close()
        backup.close()
        
        return backup_path
        
    except Exception as e:
        messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
        return None

def restore_database(backup_path):
    """ Restore database from a backup """
    if not os.path.exists(backup_path):
        messagebox.showerror("Error", "Backup file not found")
        return False
        
    try:
        # Connect to the backup database
        source = sqlite3.connect(backup_path)
        
        # Connect to the main database (will be overwritten)
        target = create_connection('data/phone_store.db')
        
        # Copy the database
        with target:
            source.backup(target)
        
        # Close connections
        source.close()
        target.close()
        
        return True
        
    except Exception as e:
        messagebox.showerror("Restore Error", f"Failed to restore backup: {str(e)}")
        return False

def export_to_csv(table_name, file_path):
    """ Export a database table to CSV """
    try:
        conn = create_connection('data/phone_store.db')
        cursor = conn.cursor()
        
        # Get table data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
            
        return True
        
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export {table_name}: {str(e)}")
        return False

def import_from_csv(table_name, file_path):
    """ Import data from CSV to a database table """
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "CSV file not found")
        return False
        
    try:
        conn = create_connection('data/phone_store.db')
        cursor = conn.cursor()
        
        # Read CSV
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            columns = next(reader)  # Get header row
            
            # Prepare insert statement
            placeholders = ', '.join(['?'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert rows
            for row in reader:
                cursor.execute(query, row)
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import {table_name}: {str(e)}")
        return False