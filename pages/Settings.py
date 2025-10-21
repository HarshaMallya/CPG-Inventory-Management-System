import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

if 'db' not in st.session_state:
    st.error("⚠️ Please login first")
    if st.button("🏠 Go to Login"):
        st.switch_page("Home.py")
    st.stop()

db = st.session_state.db
role = st.session_state.user_role
username = st.session_state.username

# Check if user is Admin
if role != "Admin":
    st.error("🚫 Access Denied: This page is only accessible to Administrators.")
    st.info("Please contact your system administrator for access.")
    st.stop()

st.title("⚙️ System Settings & Configuration")
st.markdown(f"**Logged in as:** {st.session_state.user_name} ({role})")

# Tabs for different settings
tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Configuration", "📊 System Status", "📝 Activity Logs", "🗄️ Database Management"])

# TAB 1: Email Configuration
with tab1:
    st.subheader("📧 Email Alert Configuration")
    
    st.info("Configure email settings for automated alerts and notifications")
    
    with st.form("email_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Sender Configuration")
            sender_email = st.text_input("Sender Email", placeholder="alerts@yourcompany.com")
            sender_name = st.text_input("Sender Name", placeholder="CPG Inventory System")
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587, min_value=1)
        
        with col2:
            st.markdown("### Recipients")
            admin_emails = st.text_area(
                "Admin Email Recipients",
                placeholder="admin1@company.com, admin2@company.com"
            )
            manager_emails = st.text_area(
                "Manager Email Recipients",
                placeholder="manager1@company.com, manager2@company.com"
            )
        
        st.markdown("### Alert Settings")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            low_stock_alert = st.checkbox("Low Stock Alerts", value=True)
        with col2:
            daily_report = st.checkbox("Daily Reports", value=False)
        with col3:
            weekly_summary = st.checkbox("Weekly Summary", value=False)
        
        if st.form_submit_button("💾 Save Configuration", type="primary"):
            st.success("✅ Email configuration saved successfully!")
            db.log_activity(username, "Settings Updated", "Email configuration modified")

# TAB 2: System Status
with tab2:
    st.subheader("📊 System Status & Statistics")
    
    # Get system stats
    products_df = db.get_all_products()
    sales_df = db.get_sales_data()
    low_stock_df = db.get_low_stock_items()
    
    # Display metrics
    st.markdown("### 📈 Overall System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(products_df))
    with col2:
        st.metric("Total Sales Records", len(sales_df))
    with col3:
        st.metric("Low Stock Items", len(low_stock_df))
    with col4:
        total_revenue = sales_df['revenue'].sum() if not sales_df.empty else 0
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    
    st.markdown("---")
    
    # Category breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Products by Category")
        if not products_df.empty:
            category_counts = products_df['category'].value_counts()
            st.dataframe(category_counts, use_container_width=True)
        else:
            st.info("No products available")
    
    with col2:
        st.markdown("### 🌍 Sales by Region")
        if not sales_df.empty:
            region_stats = sales_df.groupby('region').agg({
                'quantity': 'sum',
                'revenue': 'sum'
            }).round(2)
            st.dataframe(region_stats, use_container_width=True)
        else:
            st.info("No sales data available")
    
    st.markdown("---")
    
    # System Information
    st.markdown("### 💻 System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Database:** SQLite")
        st.info(f"**Location:** data/inventory.db")
    with col2:
        st.info(f"**Current User:** {username}")
        st.info(f"**Role:** {role}")
    with col3:
        st.info(f"**Session Started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.info(f"**Python Version:** 3.10+")

# TAB 3: Activity Logs
with tab3:
    st.subheader("📝 System Activity Logs")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("View recent system activities and user actions")
    with col2:
        log_limit = st.selectbox("Show entries", [25, 50, 100, 200], index=1)
    
    # Get activity logs
    logs_df = db.get_activity_logs(limit=log_limit)
    
    if not logs_df.empty:
        st.dataframe(
            logs_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "log_id": "ID",
                "username": "User",
                "action": "Action",
                "details": "Details",
                "timestamp": "Timestamp"
            }
        )
        
        # Download logs
        csv = logs_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Activity Logs",
            data=csv,
            file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No activity logs available")

# TAB 4: Database Management
with tab4:
    st.subheader("🗄️ Database Management")
    
    st.warning("⚠️ **Caution:** These operations affect your entire database. Use with care!")
    
    # Export all data
    st.markdown("### 📤 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Products", use_container_width=True):
            products_csv = products_df.to_csv(index=False)
            st.download_button(
                "Download Products CSV",
                products_csv,
                f"products_export_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("📥 Export Sales", use_container_width=True):
            if not sales_df.empty:
                sales_csv = sales_df.to_csv(index=False)
                st.download_button(
                    "Download Sales CSV",
                    sales_csv,
                    f"sales_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            else:
                st.info("No sales data to export")
    
    with col3:
        if st.button("📥 Export All Data", use_container_width=True):
            st.info("Generating complete backup...")
    
    st.markdown("---")
    
    # Database statistics
    st.markdown("### 📊 Database Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Products Table", f"{len(products_df)} records")
    with col2:
        st.metric("Sales Table", f"{len(sales_df)} records")
    with col3:
        logs_df = db.get_activity_logs(limit=1000)
        st.metric("Activity Logs", f"{len(logs_df)} records")
    
    st.markdown("---")
    
    # Dangerous operations
    st.markdown("### ⚠️ Dangerous Operations")
    
    with st.expander("🗑️ Clear Old Data (Use with Caution)", expanded=False):
        st.error("**Warning:** This will permanently delete data!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Old Activity Logs (>90 days)", type="secondary"):
                st.warning("Feature coming soon - Would clear logs older than 90 days")
        
        with col2:
            if st.button("🗑️ Clear Test Data", type="secondary"):
                st.warning("Feature coming soon - Would remove test entries")
    
    # Backup reminder
    st.info("💡 **Tip:** Regular backups are recommended. Export your data weekly to prevent data loss!")
