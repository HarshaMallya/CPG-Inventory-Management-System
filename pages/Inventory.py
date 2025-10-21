import streamlit as st
import pandas as pd
from utils.helpers import calculate_stock_status, generate_sku, sanitize_input

st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

# Check authentication
if 'db' not in st.session_state:
    st.error("⚠️ Please login first")
    if st.button("🏠 Go to Login"):
        st.switch_page("Home.py")
    st.stop()

db = st.session_state.db
role = st.session_state.user_role
username = st.session_state.username

st.title("📦 Inventory Management")
st.markdown(f"**Logged in as:** {st.session_state.user_name} ({role})")

# Tabs for different operations
if role in ["Admin", "Manager"]:
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Product", "📋 View Products", "✏️ Update Stock", "🗑️ Delete Product"])
else:
    tab1, tab2 = st.tabs(["📋 View Products", "📊 Stock Status"])

# TAB 1: Add Product (Admin/Manager only)
if role in ["Admin", "Manager"]:
    with tab1:
        st.subheader("Add New Product")
        
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name*", placeholder="e.g., Coca Cola 1L")
                category = st.selectbox(
                    "Category*", 
                    ["Beverages", "Snacks", "Personal Care", "Household", "Dairy", "Frozen Foods", "Bakery"]
                )
                
                # Auto-generate SKU suggestion
                products_df = db.get_all_products()
                if not products_df.empty:
                    category_products = products_df[products_df['category'] == category]
                    next_seq = len(category_products) + 1
                    suggested_sku = generate_sku(category, next_seq)
                else:
                    suggested_sku = generate_sku(category, 1)
                
                sku = st.text_input("SKU (Stock Keeping Unit)*", 
                                   value=suggested_sku,
                                   placeholder="e.g., BEV001",
                                   help="Auto-generated based on category. You can modify it.")
                
                price = st.number_input("Price (₹)*", min_value=0.0, step=0.01, format="%.2f", value=0.0)
            
            with col2:
                stock_qty = st.number_input("Initial Stock Quantity*", min_value=0, step=1, value=100)
                reorder_level = st.number_input("Reorder Level*", min_value=0, step=1, value=20,
                                               help="Alert will trigger when stock falls below this level")
                expiry_date = st.date_input("Expiry Date (Optional)", value=None)
                
                # Show stock status preview
                if stock_qty and reorder_level:
                    status = calculate_stock_status(stock_qty, reorder_level)
                    st.info(f"Initial Status: {status}")
            
            st.markdown("*Required fields")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit = st.form_submit_button("✅ Add Product", use_container_width=True, type="primary")
            
            if submit:
                # Validation
                if not name or not name.strip():
                    st.error("❌ Product name cannot be empty!")
                elif not sku or not sku.strip():
                    st.error("❌ SKU cannot be empty!")
                elif price <= 0:
                    st.error("❌ Price must be greater than 0!")
                else:
                    try:
                        # Sanitize inputs
                        clean_name = sanitize_input(name.strip())
                        clean_sku = sanitize_input(sku.strip().upper())
                        
                        db.add_product(
                            clean_name, 
                            category, 
                            clean_sku,
                            price, 
                            stock_qty, 
                            reorder_level, 
                            str(expiry_date) if expiry_date else None
                        )
                        st.success(f"✅ Product '{clean_name}' added successfully!")
                        st.success(f"📦 SKU: {clean_sku} | Stock: {stock_qty} units | Reorder Level: {reorder_level}")
                        
                        # Log activity
                        db.log_activity(username, "Product Added", f"{clean_name} (SKU: {clean_sku})")
                        
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        error_message = str(e)
                        if "UNIQUE constraint failed: products.sku" in error_message:
                            st.error(f"❌ Error: SKU '{sku.upper()}' already exists!")
                            st.info("💡 **Tip:** Each product needs a unique SKU. Try:")
                            st.code(f"{sku}A or {sku}2 or use the auto-generated SKU")
                        else:
                            st.error(f"❌ Error: {error_message}")

# TAB 2: View Products
tab_index = 1 if role in ["Admin", "Manager"] else 0
with (tab2 if role in ["Admin", "Manager"] else tab1):
    st.subheader("All Products")
    
    products_df = db.get_all_products()
    
    if not products_df.empty:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_categories = st.multiselect(
                "Filter by Category", 
                options=products_df['category'].unique(),
                default=products_df['category'].unique()
            )
        
        with col2:
            search_term = st.text_input("🔍 Search by Name")
        
        with col3:
            sort_by = st.selectbox("Sort by", ["name", "stock_qty", "price", "category", "created_at"])
        
        with col4:
            stock_filter = st.selectbox("Stock Status", ["All", "Low Stock Only", "Out of Stock", "Well Stocked"])
        
        # Apply filters
        filtered_df = products_df[products_df['category'].isin(selected_categories)]
        
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
        
        # Apply stock filter
        if stock_filter == "Low Stock Only":
            filtered_df = filtered_df[filtered_df['stock_qty'] <= filtered_df['reorder_level']]
        elif stock_filter == "Out of Stock":
            filtered_df = filtered_df[filtered_df['stock_qty'] == 0]
        elif stock_filter == "Well Stocked":
            filtered_df = filtered_df[filtered_df['stock_qty'] > filtered_df['reorder_level']]
        
        filtered_df = filtered_df.sort_values(by=sort_by)
        
        # Display count
        st.info(f"📊 Showing {len(filtered_df)} of {len(products_df)} products")
        
        # Add stock status column
        if not filtered_df.empty:
            display_df = filtered_df.copy()
            display_df['Status'] = display_df.apply(
                lambda row: calculate_stock_status(row['stock_qty'], row['reorder_level']), 
                axis=1
            )
            
            # Display dataframe
            st.dataframe(
                display_df[['product_id', 'name', 'category', 'sku', 'price', 'stock_qty', 'reorder_level', 'Status', 'expiry_date']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_id": "ID",
                    "name": "Product Name",
                    "category": "Category",
                    "sku": "SKU",
                    "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                    "stock_qty": st.column_config.NumberColumn("Stock", format="%d units"),
                    "reorder_level": st.column_config.NumberColumn("Reorder Level", format="%d units"),
                    "Status": "Stock Status",
                    "expiry_date": "Expiry Date"
                }
            )
            
            # Summary statistics
            st.markdown("---")
            st.subheader("📊 Inventory Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Products", len(filtered_df))
            
            with col2:
                total_value = (filtered_df['price'] * filtered_df['stock_qty']).sum()
                st.metric("Total Value", f"₹{total_value:,.2f}")
            
            with col3:
                low_stock = len(filtered_df[filtered_df['stock_qty'] <= filtered_df['reorder_level']])
                st.metric("Low Stock Items", low_stock, 
                         delta=f"-{low_stock}" if low_stock > 0 else "0",
                         delta_color="inverse")
            
            with col4:
                total_units = filtered_df['stock_qty'].sum()
                st.metric("Total Units", f"{total_units:,}")
            
            # Download
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Inventory Report (CSV)",
                data=csv,
                file_name=f"inventory_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No products match your filters.")
        
    else:
        st.warning("⚠️ No products in inventory.")
        if role in ["Admin", "Manager"]:
            st.info("💡 Use the 'Add Product' tab to add your first product!")

# TAB 3: Update Stock (Admin/Manager only)
if role in ["Admin", "Manager"]:
    with tab3:
        st.subheader("Update Stock Levels")
        
        products_df = db.get_all_products()
        
        if not products_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                product_to_update = st.selectbox(
                    "Select Product", 
                    products_df['name'].tolist(),
                    key="update_select"
                )
            
            if product_to_update:
                product_data = products_df[products_df['name'] == product_to_update].iloc[0]
                product_id = product_data['product_id']
                current_stock = product_data['stock_qty']
                reorder_level = product_data['reorder_level']
                product_sku = product_data['sku']
                product_price = product_data['price']
                
                with col2:
                    st.info(f"**SKU:** {product_sku} | **Price:** ₹{product_price:.2f}")
                    current_status = calculate_stock_status(current_stock, reorder_level)
                    st.info(f"**Current Status:** {current_status}")
                
                st.markdown("---")
                
                # Update options
                update_type = st.radio(
                    "Update Type",
                    ["Set New Quantity", "Add Stock (Restock)", "Remove Stock (Sold/Damaged)"],
                    horizontal=True
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if update_type == "Set New Quantity":
                        new_quantity = st.number_input(
                            f"New Quantity (Current: {current_stock})", 
                            min_value=0, 
                            value=int(current_stock),
                            step=1
                        )
                    elif update_type == "Add Stock (Restock)":
                        add_qty = st.number_input("Quantity to Add", min_value=1, step=1, value=10)
                        new_quantity = current_stock + add_qty
                        st.success(f"✅ New total will be: **{new_quantity}** units")
                    else:
                        max_remove = int(current_stock) if current_stock > 0 else 1
                        remove_qty = st.number_input(
                            "Quantity to Remove", 
                            min_value=1, 
                            max_value=max_remove,
                            step=1,
                            value=min(10, max_remove)
                        )
                        new_quantity = max(0, current_stock - remove_qty)
                        st.warning(f"⚠️ New total will be: **{new_quantity}** units")
                
                with col2:
                    st.markdown("### 📊 Updated Status Preview")
                    new_status = calculate_stock_status(new_quantity, reorder_level)
                    
                    if new_quantity == 0:
                        st.error(f"{new_status}")
                    elif new_quantity <= reorder_level:
                        st.warning(f"{new_status}")
                    else:
                        st.success(f"{new_status}")
                    
                    new_value = new_quantity * product_price
                    st.metric("Updated Stock Value", f"₹{new_value:,.2f}")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("✅ Update Stock", use_container_width=True, type="primary"):
                        db.update_stock(product_id, new_quantity)
                        st.success(f"✅ Stock updated successfully!")
                        st.success(f"📦 {product_to_update}: {current_stock} → {new_quantity} units")
                        
                        # Log activity
                        db.log_activity(username, "Stock Updated", 
                                       f"{product_to_update}: {current_stock} → {new_quantity}")
                        
                        st.balloons()
                        st.rerun()
