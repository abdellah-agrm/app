# database_helper.py - Create this new file to handle database paths
import os
import sqlite3

def get_database_path():
    """Get the correct database path, trying multiple common locations"""
    possible_paths = [
        "data/phone_store.db",  # Current structure
        "../data/phone_store.db",  # If running from src/
        "phone_store.db",  # Root directory
        "db/phone_store.db",  # Alternative structure
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "phone_store.db"),  # Absolute path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found data at: {path}")
            return path
    
    # If no data found, check what files exist
    print("data not found. Current directory contents:")
    print("Current working directory:", os.getcwd())
    
    # Check common directories
    for check_dir in [".", "data", "db", ".."]:
        if os.path.exists(check_dir):
            print(f"\nContents of {check_dir}:")
            try:
                for item in os.listdir(check_dir):
                    print(f"  {item}")
            except PermissionError:
                print(f"  Permission denied to list {check_dir}")
    
    # Return default path (will create if needed)
    return "data/phone_store.db"

def ensure_database_directory():
    """Ensure the database directory exists"""
    db_path = get_database_path()
    db_dir = os.path.dirname(db_path)
    
    if db_dir and not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    return db_path

def test_database_connection(db_path):
    """Test if we can connect to the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        users_table = cursor.fetchone()
        
        if users_table:
            print("✓ Users table found")
            # Check if there are any users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✓ Found {user_count} users in database")
        else:
            print("✗ Users table not found - you may need to run database setup")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Run diagnostics
    print("=== Database Diagnostics ===")
    db_path = ensure_database_directory()
    print(f"Using database path: {db_path}")
    test_database_connection(db_path)