# database.py
import sqlite3
from sqlite3 import Error
import os

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite version {sqlite3.version}")
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_tables(conn):
    """ Create all necessary tables """
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'seller')),
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    sql_create_phones_table = """
    CREATE TABLE IF NOT EXISTS phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        imei TEXT UNIQUE,
        color TEXT,
        storage TEXT,
        ram TEXT,
        condition TEXT CHECK(condition IN ('new', 'used', 'refurbished')),
        price REAL NOT NULL,
        cost_price REAL,
        quantity INTEGER DEFAULT 1,
        qr_code_path TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    sql_create_clients_table = """
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    sql_create_sales_table = """
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_id INTEGER NOT NULL,
        client_id INTEGER,
        user_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL,
        payment_method TEXT CHECK(payment_method IN ('cash', 'credit_card', 'bank_transfer', 'other')),
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (phone_id) REFERENCES phones (id),
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    
    sql_create_store_info_table = """
    CREATE TABLE IF NOT EXISTS store_info (
        id INTEGER PRIMARY KEY DEFAULT 1,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        logo_path TEXT,
        tax_number TEXT,
        CONSTRAINT one_row CHECK (id = 1)
    );
    """
    
    try:
        c = conn.cursor()
        c.execute(sql_create_users_table)
        c.execute(sql_create_phones_table)
        c.execute(sql_create_clients_table)
        c.execute(sql_create_sales_table)
        c.execute(sql_create_store_info_table)
        conn.commit()
        
        # Insert default admin user if users table is empty
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                     ('admin', 'admin123', 'admin', 'Administrator'))
            c.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                     ('seller', 'seller123', 'seller', 'Seller User'))
            conn.commit()
        
        # Insert default store info if empty
        c.execute("SELECT COUNT(*) FROM store_info")
        if c.fetchone()[0] == 0:
            c.execute("""
            INSERT INTO store_info (name, address, phone, email) 
            VALUES (?, ?, ?, ?)
            """, ('My Phone Store', '123 Main St, City', '+1234567890', 'store@example.com'))
            conn.commit()
            
    except Error as e:
        print(e)

def initialize_database():
    """ Initialize the database with tables and default data """
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create qr_codes directory if it doesn't exist
    if not os.path.exists('data/qr_codes'):
        os.makedirs('data/qr_codes')
    
    db_path = 'data/phone_store.db'
    conn = create_connection(db_path)
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")