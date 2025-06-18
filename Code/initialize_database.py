import sqlite3
import os
from db_utils import get_connection, get_db_path

def initialize_database():
    # Get the current directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'supermarket.db')
    
    print(f"Initializing database at: {db_path}")
    
    # Connect to database (creates it if it doesn't exist)
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image_path TEXT,
        details TEXT,
        category TEXT,
        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        quantity INTEGER DEFAULT 10
    )
    ''')
    
    # Create cashier_activity table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cashier_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cashier_username TEXT,
        login_time TEXT,
        logout_time TEXT,
        active_hours TEXT
    )
    ''')
    
    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        amount FLOAT
    )
    ''')
    
    # Create default admin account
    cursor.execute("SELECT * FROM accounts WHERE username = 'admin' AND role = 'Administrator'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO accounts (username, password, role) 
        VALUES ('admin', 'admin', 'Administrator')
        ''')
        print("Created default admin account (username: admin, password: admin)")
    
    # Insert sample product data
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        # Load sample data from SQL file
        with open(os.path.join(current_dir, 'supermarket.sql'), 'r') as f:
            sql_script = f.read()
            
        # Extract INSERT statements
        import re
        insert_statements = re.findall(r'INSERT INTO products.*?;', sql_script, re.DOTALL)
        
        if insert_statements:
            for stmt in insert_statements:
                # Execute the statement
                cursor.execute(stmt)
            
            # Update all products to have a default quantity of 10
            cursor.execute("UPDATE products SET quantity = 10 WHERE quantity IS NULL")
            print(f"Added {len(insert_statements)} sample products with default quantity of 10")
    
    print("Đang kiểm tra số lượng sản phẩm...")
    cursor.execute("UPDATE products SET quantity = 10 WHERE quantity IS NULL OR quantity = 0")
    updated_rows = cursor.rowcount
    if updated_rows > 0:
        print(f"Đã cập nhật {updated_rows} sản phẩm với số lượng mặc định là 10")
    
    conn.commit()
    conn.close()
    print("Hoàn tất khởi tạo cơ sở dữ liệu!")

if __name__ == "__main__":
    initialize_database()