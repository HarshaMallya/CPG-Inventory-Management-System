"""
Helper functions for CPG Inventory Management System
"""

import pandas as pd
from datetime import datetime, timedelta
import re
import hashlib

def format_currency(amount):
    """
    Format number as Indian currency (Rupees)
    
    Args:
        amount (float): Amount to format
    
    Returns:
        str: Formatted currency string
    """
    return f"₹{amount:,.2f}"

def calculate_stock_status(stock_qty, reorder_level):
    """
    Return stock status with emoji indicator
    
    Args:
        stock_qty (int): Current stock quantity
        reorder_level (int): Reorder level threshold
    
    Returns:
        str: Status string with emoji
    """
    if stock_qty == 0:
        return "🔴 Out of Stock"
    elif stock_qty <= reorder_level:
        return "🟡 Low Stock"
    elif stock_qty <= reorder_level * 2:
        return "🟢 Adequate Stock"
    else:
        return "🟢 Well Stocked"

def export_to_csv(dataframe, filename, folder='reports'):
    """
    Export dataframe to CSV with timestamp
    
    Args:
        dataframe (pd.DataFrame): Data to export
        filename (str): Base filename
        folder (str): Destination folder
    
    Returns:
        str: Full path of exported file
    """
    import os
    
    # Create folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_filename = f"{folder}/{filename}_{timestamp}.csv"
    dataframe.to_csv(full_filename, index=False)
    return full_filename

def get_date_range_sales(sales_df, start_date, end_date):
    """
    Filter sales by date range
    
    Args:
        sales_df (pd.DataFrame): Sales dataframe
        start_date (str/datetime): Start date
        end_date (str/datetime): End date
    
    Returns:
        pd.DataFrame: Filtered sales data
    """
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    mask = (sales_df['date'] >= pd.to_datetime(start_date)) & \
           (sales_df['date'] <= pd.to_datetime(end_date))
    return sales_df.loc[mask]

def calculate_growth_rate(current, previous):
    """
    Calculate percentage growth rate
    
    Args:
        current (float): Current value
        previous (float): Previous value
    
    Returns:
        float: Growth rate percentage
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100

def validate_email(email):
    """
    Validate email address format
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """
    Sanitize user input to prevent SQL injection and XSS
    
    Args:
        text (str): Input text to sanitize
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = str(text).strip()
    text = re.sub(r'[<>"\']', '', text)
    return text

def generate_sku(category, sequence_number):
    """
    Generate SKU code based on category and sequence
    
    Args:
        category (str): Product category
        sequence_number (int): Sequence number
    
    Returns:
        str: Generated SKU code
    """
    category_codes = {
        'Beverages': 'BEV',
        'Snacks': 'SNK',
        'Personal Care': 'PC',
        'Household': 'HH',
        'Dairy': 'DRY',
        'Frozen Foods': 'FRZ',
        'Bakery': 'BAK'
    }
    
    code = category_codes.get(category, 'GEN')
    return f"{code}{sequence_number:03d}"

def calculate_reorder_quantity(avg_daily_sales, lead_time_days, safety_stock_days=7):
    """
    Calculate recommended reorder quantity
    
    Args:
        avg_daily_sales (float): Average daily sales
        lead_time_days (int): Lead time in days
        safety_stock_days (int): Safety stock buffer in days
    
    Returns:
        int: Recommended reorder quantity
    """
    reorder_qty = avg_daily_sales * (lead_time_days + safety_stock_days)
    return int(reorder_qty)

def get_stock_alert_level(stock_qty, reorder_level):
    """
    Get stock alert level (0-3)
    
    Args:
        stock_qty (int): Current stock
        reorder_level (int): Reorder threshold
    
    Returns:
        int: Alert level (0=Good, 1=Low, 2=Critical, 3=Out)
    """
    if stock_qty == 0:
        return 3  # Out of stock
    elif stock_qty <= reorder_level * 0.5:
        return 2  # Critical
    elif stock_qty <= reorder_level:
        return 1  # Low
    else:
        return 0  # Good

def calculate_inventory_turnover(sales_df, products_df, product_id, period_days=30):
    """
    Calculate inventory turnover ratio
    
    Args:
        sales_df (pd.DataFrame): Sales data
        products_df (pd.DataFrame): Products data
        product_id (int): Product ID
        period_days (int): Period in days
    
    Returns:
        float: Turnover ratio
    """
    # Get sales for the period
    cutoff_date = datetime.now() - timedelta(days=period_days)
    product_sales = sales_df[
        (sales_df['product_id'] == product_id) & 
        (pd.to_datetime(sales_df['date']) >= cutoff_date)
    ]
    
    total_sold = product_sales['quantity'].sum()
    
    # Get average inventory
    product_info = products_df[products_df['product_id'] == product_id]
    if not product_info.empty:
        avg_inventory = product_info['stock_qty'].values[0]
        if avg_inventory > 0:
            return total_sold / avg_inventory
    
    return 0.0

def format_date(date_string, output_format='%Y-%m-%d'):
    """
    Format date string to desired format
    
    Args:
        date_string (str): Input date string
        output_format (str): Desired output format
    
    Returns:
        str: Formatted date string
    """
    try:
        date_obj = pd.to_datetime(date_string)
        return date_obj.strftime(output_format)
    except:
        return date_string

def calculate_revenue_per_region(sales_df):
    """
    Calculate total revenue by region
    
    Args:
        sales_df (pd.DataFrame): Sales data
    
    Returns:
        dict: Revenue by region
    """
    if sales_df.empty:
        return {}
    
    region_revenue = sales_df.groupby('region')['revenue'].sum().to_dict()
    return region_revenue

def get_top_products(sales_df, limit=10, metric='revenue'):
    """
    Get top products by revenue or quantity
    
    Args:
        sales_df (pd.DataFrame): Sales data
        limit (int): Number of products to return
        metric (str): 'revenue' or 'quantity'
    
    Returns:
        pd.DataFrame: Top products
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    top_products = sales_df.groupby('name')[metric].sum().sort_values(ascending=False).head(limit)
    return top_products.reset_index()

def hash_string(text):
    """
    Create SHA-256 hash of a string
    
    Args:
        text (str): Text to hash
    
    Returns:
        str: Hexadecimal hash
    """
    return hashlib.sha256(text.encode()).hexdigest()