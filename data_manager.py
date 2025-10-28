import pandas as pd
import os
from datetime import date

DATA_DIR = "data"
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")

# ---------- Ensure data folder exists ----------
os.makedirs(DATA_DIR, exist_ok=True)

# ---------- Load or create inventory ----------
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        return pd.read_csv(INVENTORY_FILE)
    else:
        df = pd.DataFrame(columns=["product_id", "name", "stock", "reorder_level", "category"])
        df.to_csv(INVENTORY_FILE, index=False)
        return df

# ---------- Load or create sales ----------
def load_sales():
    if os.path.exists(SALES_FILE):
        return pd.read_csv(SALES_FILE)
    else:
        df = pd.DataFrame(columns=["date", "product_id", "quantity_sold"])
        df.to_csv(SALES_FILE, index=False)
        return df

# ---------- Add new product ----------
def add_product(product_id, name, stock, reorder_level, category):
    inventory = load_inventory()

    # Check for duplicates
    if product_id in inventory["product_id"].values:
        return False, "Product ID already exists."

    # Add to inventory.csv
    new_row = {
        "product_id": product_id,
        "name": name,
        "stock": stock,
        "reorder_level": reorder_level,
        "category": category
    }
    inventory = pd.concat([inventory, pd.DataFrame([new_row])], ignore_index=True)
    inventory.to_csv(INVENTORY_FILE, index=False)

    # Add to sales.csv with zero initial sales
    sales = load_sales()
    today = date.today()
    sales = pd.concat(
        [sales, pd.DataFrame([{"date": today, "product_id": product_id, "quantity_sold": 0}])],
        ignore_index=True
    )
    sales.to_csv(SALES_FILE, index=False)

    return True, f"✅ Product '{name}' added successfully!"

# ---------- Update stock ----------
def update_stock(product_id, new_stock):
    inventory = load_inventory()
    if product_id not in inventory["product_id"].values:
        return False, "Product not found."
    inventory.loc[inventory["product_id"] == product_id, "stock"] = new_stock
    inventory.to_csv(INVENTORY_FILE, index=False)
    return True, f"Stock updated for {product_id}."
