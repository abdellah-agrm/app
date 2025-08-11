# diagnose_database.py - Run this to find your database
import os
import sqlite3

def find_database_files():
    """Find all .db files in the project"""
    print("=== Database Location Diagnostic ===")
    print(f"Current working directory: {os.getcwd()}")
    print()
    
    # Look for .db files
    db_files = []
    
    # Search in common locations
    search_dirs = [
        ".",
        "data",
        "db", 
        "src",
        "..",
        "../data",
        "../db"
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            print(f"Checking directory: {search_dir}")
            try:
                for item in os.listdir(search_dir):
                    item_path = os.path.join(search_dir, item)
                    if item.endswith('.db'):
                        db_files.append(item_path)
                        print(f"  ✓ Found database: {item_path}")
                    elif os.path.isdir(item_path):
                        print(f"  📁 Directory: {item}")
                    else:
                        print(f"  📄 File: {item}")
            except PermissionError:
                print(f"  ❌ Permission denied")
        else:
            print(f"Directory doesn't exist: {search_dir}")
        print()
    
    return db_files

def test_database(db_path):
    """Test a database file"""
    print(f"\n=== Testing Database: {db_path} ===")
    
    if not os.path.exists(db_path):
        print("❌ Database file doesn't exist!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✓ Database opened successfully")
        print(f"✓ Found {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} records")
        
        # Specifically check for users table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        users_table = cursor.fetchone()
        
        if users_table:
            print("\n✓ Users table exists")
            cursor.execute("SELECT username FROM users LIMIT 5")
            users = cursor.fetchall()
            print("Sample usernames:", [user[0] for user in users])
        else:
            print("\n❌ No 'users' table found!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return False

def main():
    print("Phone Shop App - Database Diagnostic Tool")
    print("=" * 50)
    
    # Find database files
    db_files = find_database_files()
    
    if not db_files:
        print("\n❌ No database files found!")
        print("\nPossible solutions:")
        print("1. Make sure you're running this from the project root directory")
        print("2. Check if the database was created with a different name")
        print("3. Run the database setup script if you have one")
        return
    
    print(f"\n✓ Found {len(db_files)} database file(s)")
    
    # Test each database
    working_databases = []
    for db_file in db_files:
        if test_database(db_file):
            working_databases.append(db_file)
    
    if working_databases:
        print(f"\n🎉 Working database(s) found:")
        for db in working_databases:
            print(f"  - {os.path.abspath(db)}")
        
        print(f"\n📋 To fix your app, update the database path in your code to:")
        print(f'   self.db_path = "{working_databases[0]}"')
    else:
        print(f"\n❌ No working databases found with user authentication tables")

if __name__ == "__main__":
    main()