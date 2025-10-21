import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Check authentication
if 'db' not in st.session_state:
    st.error("⚠️ Please login first")
    if st.button("🏠 Go to Login"):
        st.switch_page("Home.py")
    st.stop()

db = st.session_state.db
role = st.session_state.user_role
username = st.session_state.username

# Title
st.title("📊 Analytics Dashboard")
st.markdown(f"**Logged in as:** {st.session_state.user_name} ({role})")

# Fetch data
products_df = db.get_all_products()
sales_df = db.get_sales_data()
low_stock_df = db.get_low_stock_items()

# Date range filter
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("### 📅 Dashboard Overview")
with col2:
    date_range = st.selectbox("Time Period", ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
with col3:
    if st.button("🔄 Refresh"):
        st.rerun()

# Filter sales by date range
if not sales_df.empty and date_range != "All Time":
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
    cutoff_date = datetime.now() - timedelta(days=days_map[date_range])
    sales_df = sales_df[sales_df['date'] >= cutoff_date]

st.markdown("---")

# Key Performance Indicators
st.subheader("🎯 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_products = len(products_df)
    st.metric(
        label="Total Products",
        value=total_products,
        delta="Active Inventory"
    )

with col2:
    total_revenue = sales_df['revenue'].sum() if not sales_df.empty else 0
    st.metric(
        label="Total Revenue",
        value=f"₹{total_revenue:,.2f}",
        delta="+12.5%"
    )

with col3:
    low_stock_count = len(low_stock_df)
    st.metric(
        label="Low Stock Alerts",
        value=low_stock_count,
        delta=f"-{low_stock_count}" if low_stock_count > 0 else "0",
        delta_color="inverse"
    )

with col4:
    total_stock_value = (products_df['price'] * products_df['stock_qty']).sum() if not products_df.empty else 0
    st.metric(
        label="Stock Value",
        value=f"₹{total_stock_value:,.2f}"
    )

st.markdown("---")

# Charts Section - Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Stock Distribution by Category")
    if not products_df.empty:
        category_stock = products_df.groupby('category')['stock_qty'].sum().reset_index()
        fig = px.bar(
            category_stock, 
            x='category', 
            y='stock_qty',
            title='Stock Quantity by Category',
            color='stock_qty',
            color_continuous_scale='Blues',
            labels={'stock_qty': 'Stock Quantity', 'category': 'Category'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No product data available")

with col2:
    st.subheader("💰 Sales Trend")
    if not sales_df.empty:
        sales_trend = sales_df.groupby('date')['revenue'].sum().reset_index()
        fig = px.line(
            sales_trend, 
            x='date', 
            y='revenue',
            title='Daily Sales Revenue',
            markers=True
        )
        fig.update_traces(line_color='#FF6B6B', line_width=3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available")

# Charts Section - Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Selling Products")
    if not sales_df.empty:
        top_products = sales_df.groupby('name').agg({
            'quantity': 'sum',
            'revenue': 'sum'
        }).sort_values('revenue', ascending=False).head(10)
        
        fig = px.bar(
            top_products, 
            x=top_products.index, 
            y='revenue',
            title='Top 10 Products by Revenue',
            labels={'revenue': 'Revenue (₹)', 'index': 'Product'},
            color='revenue',
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available")

with col2:
    st.subheader("🌍 Regional Performance")
    if not sales_df.empty:
        region_sales = sales_df.groupby('region').agg({
            'revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        fig = px.pie(
            region_sales, 
            values='revenue', 
            names='region',
            title='Revenue Distribution by Region',
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No regional data available")

# Low Stock Alerts Table
st.markdown("---")
st.subheader("🚨 Low Stock Alerts")
if not low_stock_df.empty:
    st.dataframe(
        low_stock_df[['name', 'category', 'stock_qty', 'reorder_level', 'price']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
            "stock_qty": st.column_config.NumberColumn("Stock", format="%d units"),
        }
    )
    st.warning(f"⚠️ {len(low_stock_df)} products need restocking!")
else:
    st.success("✅ All products are sufficiently stocked!")

# Recent Activity
st.markdown("---")
st.subheader("📝 Recent Sales Activity")
if not sales_df.empty:
    recent_sales = sales_df.head(10)[['date', 'name', 'category', 'quantity', 'revenue', 'region']]
    st.dataframe(recent_sales, use_container_width=True, hide_index=True)
    
    # Download report
    csv = sales_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Sales Report",
        data=csv,
        file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("No recent sales activity")
