import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sales Tracking", page_icon="💰", layout="wide")

if 'db' not in st.session_state:
    st.error("⚠️ Please login first")
    if st.button("🏠 Go to Login"):
        st.switch_page("Home.py")
    st.stop()

db = st.session_state.db
role = st.session_state.user_role
username = st.session_state.username

st.title("💰 Sales Tracking")
st.markdown(f"**Logged in as:** {st.session_state.user_name} ({role})")

tab1, tab2 = st.tabs(["🛒 Record New Sale", "📊 Sales History"])

# TAB 1: Record Sale
with tab1:
    st.subheader("Record New Sale")
    
    products_df = db.get_all_products()
    
    if not products_df.empty:
        with st.form("sales_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.selectbox(
                    "Select Product*", 
                    products_df['name'].tolist(),
                    help="Choose the product being sold"
                )
                
                if product_name:
                    current_stock = products_df[products_df['name'] == product_name]['stock_qty'].values[0]
                    product_price = products_df[products_df['name'] == product_name]['price'].values[0]
                    st.info(f"📦 Available Stock: **{current_stock}** units | Price: **₹{product_price}**")
                
                quantity = st.number_input(
                    "Quantity Sold*", 
                    min_value=1, 
                    max_value=int(current_stock) if current_stock > 0 else 1,
                    step=1,
                    value=1
                )
            
            with col2:
                region = st.selectbox(
                    "Sales Region*", 
                    ["North", "South", "East", "West", "Central"]
                )
                
                if product_name and quantity:
                    total_amount = product_price * quantity
                    st.metric("Total Amount", f"₹{total_amount:,.2f}")
            
            st.markdown("*Required fields")
            
            submit = st.form_submit_button("✅ Record Sale", use_container_width=True, type="primary")
            
            if submit:
                product_id = products_df[products_df['name'] == product_name]['product_id'].values[0]
                
                if quantity <= current_stock:
                    db.add_sale(product_id, quantity, region, username)
                    st.success(f"✅ Sale Recorded Successfully!")
                    st.success(f"📦 Sold: **{quantity}** units of **{product_name}**")
                    st.success(f"💰 Revenue: **₹{total_amount:,.2f}**")
                    st.success(f"📍 Region: **{region}**")
                    
                    # Log activity
                    db.log_activity(username, "Sale Recorded", f"{quantity} units of {product_name}")
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Insufficient Stock! Only {current_stock} units available.")
    else:
        st.warning("⚠️ No products available. Please add products first!")
        if st.button("➕ Go to Add Products"):
            st.switch_page("pages/Inventory.py")

# TAB 2: Sales History
with tab2:
    st.subheader("Sales History & Analytics")
    
    sales_df = db.get_sales_data()
    
    if not sales_df.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_filter = st.date_input("Filter by Date", value=None)
        
        with col2:
            region_filter = st.multiselect(
                "Filter by Region",
                options=sales_df['region'].unique(),
                default=sales_df['region'].unique()
            )
        
        with col3:
            category_filter = st.multiselect(
                "Filter by Category",
                options=sales_df['category'].unique(),
                default=sales_df['category'].unique()
            )
        
        # Apply filters
        filtered_sales = sales_df[
            (sales_df['region'].isin(region_filter)) &
            (sales_df['category'].isin(category_filter))
        ]
        
        if date_filter:
            filtered_sales = filtered_sales[filtered_sales['date'] == str(date_filter)]
        
        # Summary metrics
        st.markdown("### 📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", len(filtered_sales))
        
        with col2:
            total_revenue = filtered_sales['revenue'].sum()
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        
        with col3:
            total_units = filtered_sales['quantity'].sum()
            st.metric("Units Sold", total_units)
        
        with col4:
            avg_sale = filtered_sales['revenue'].mean()
            st.metric("Avg Sale Value", f"₹{avg_sale:,.2f}")
        
        st.markdown("---")
        
        # Sales table
        st.subheader("📋 Transaction Details")
        st.dataframe(
            filtered_sales[['date', 'name', 'category', 'quantity', 'revenue', 'region', 'recorded_by']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "revenue": st.column_config.NumberColumn("Revenue", format="₹%.2f"),
                "quantity": st.column_config.NumberColumn("Quantity", format="%d units"),
            }
        )
        
        # Download button
        csv = filtered_sales.to_csv(index=False)
        st.download_button(
            label="📥 Download Sales Report (CSV)",
            data=csv,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No sales data available yet. Start recording sales!")
