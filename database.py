import sqlite3
import pandas as pd
from datetime import datetime
import os
import bcrypt

os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class InventoryDB:
    def __init__(self, db_name='data/inventory.db'):
        os.makedirs('data', exist_ok=True)
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name, timeout=20.0, check_same_thread=False)
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    sku TEXT UNIQUE NOT NULL,
                    price REAL NOT NULL,
                    stock_qty INTEGER NOT NULL,
                    reorder_level INTEGER NOT NULL,
                    expiry_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    date TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    revenue REAL NOT NULL,
                    region TEXT,
                    recorded_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Activity logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    # Product operations
    def add_product(self, name, category, sku, price, stock_qty, reorder_level, expiry_date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO products (name, category, sku, price, stock_qty, reorder_level, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, sku, price, stock_qty, reorder_level, expiry_date))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_all_products(self):
        conn = self.get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM products ORDER BY created_at DESC", conn)
            return df
        finally:
            conn.close()
    
    def update_stock(self, product_id, new_quantity):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE products SET stock_qty = ? WHERE product_id = ?', 
                         (new_quantity, product_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def delete_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    # Sales operations
    def add_sale(self, product_id, quantity, region='North', recorded_by='System'):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT price, stock_qty FROM products WHERE product_id = ?", (product_id,))
            result = cursor.fetchone()
            
            if result:
                price, current_stock = result
                revenue = price * quantity
                
                cursor.execute('''
                    INSERT INTO sales (product_id, date, quantity, revenue, region, recorded_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product_id, datetime.now().strftime('%Y-%m-%d'), quantity, revenue, region, recorded_by))
                
                new_stock = current_stock - quantity
                cursor.execute("UPDATE products SET stock_qty = ? WHERE product_id = ?", 
                             (new_stock, product_id))
                
                conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_sales_data(self):
        conn = self.get_connection()
        try:
            df = pd.read_sql_query('''
                SELECT s.*, p.name, p.category 
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                ORDER BY s.date DESC
            ''', conn)
            return df
        finally:
            conn.close()
    
    def get_low_stock_items(self):
        conn = self.get_connection()
        try:
            df = pd.read_sql_query('''
                SELECT * FROM products WHERE stock_qty <= reorder_level
                ORDER BY stock_qty ASC
            ''', conn)
            return df
        finally:
            conn.close()
    
    # Activity logging
    def log_activity(self, username, action, details=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO activity_logs (username, action, details)
                VALUES (?, ?, ?)
            ''', (username, action, details))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_activity_logs(self, limit=50):
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(f'''
                SELECT * FROM activity_logs 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            ''', conn)
            return df
        finally:
            conn.close()

