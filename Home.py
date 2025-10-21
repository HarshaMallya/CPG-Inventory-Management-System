import streamlit as st
from database import InventoryDB
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Page configuration
st.set_page_config(
    page_title="CPG Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
try:
    with open('assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

# Load authentication config
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login form
# Fixed login for latest streamlit-authenticator
try:
    name, authentication_status, username = authenticator.login('main')
except:
    name, authentication_status, username = authenticator.login('Login', 'main')


# Check authentication status
if authentication_status == False:
    st.error('❌ Username/password is incorrect')
    st.stop()
    
if authentication_status == None:
    st.warning('⚠️ Please enter your username and password')
    st.info("""
    **Demo Credentials:**
    
    🔑 **Admin Access:**
    - Username: `admin`
    - Password: `admin123`
    
    🔑 **Manager Access:**
    - Username: `manager`
    - Password: `manager123`
    
    🔑 **Employee Access:**
    - Username: `employee`
    - Password: `employee123`
    """)
    st.stop()

# User is authenticated - Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = InventoryDB()

if 'user_role' not in st.session_state:
    st.session_state.user_role = config['credentials']['usernames'][username]['role']

if 'username' not in st.session_state:
    st.session_state.username = username

if 'user_name' not in st.session_state:
    st.session_state.user_name = name

db = st.session_state.db

# Log login activity (only once per session)
if 'login_logged' not in st.session_state:
    db.log_activity(username, "Login", f"User logged in as {st.session_state.user_role}")
    st.session_state.login_logged = True

# Sidebar with user info
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    
    # Role badge with color
    role = st.session_state.user_role
    role_class = role.lower()
    st.markdown(f'<div class="role-badge {role_class}">{role}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display email
    st.caption(f"📧 {config['credentials']['usernames'][username]['email']}")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_main"):
        db.log_activity(username, "Logout", f"User logged out from {role} role")
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        authenticator.logout(location='sidebar')
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ Logged out successfully!")
        st.rerun()
    
    st.markdown("---")
    
    # Quick Stats in Sidebar
    products_df = db.get_all_products()
    low_stock_df = db.get_low_stock_items()
    
    st.markdown("### 📊 Quick Stats")
    st.write(f"**Total Products:** {len(products_df)}")
    st.write(f"**Low Stock Items:** {len(low_stock_df)}")
    
    st.markdown("---")
    
    # Role-based permissions
    st.markdown("### 🔐 Your Permissions")
    if role == "Admin":
        st.success("✅ Full System Access")
        st.info("• Manage all products\n• View all reports\n• Configure settings\n• User management\n• Delete products\n• Send email alerts")
    elif role == "Manager":
        st.success("✅ Manager Access")
        st.info("• Add/Edit products\n• Record sales\n• View reports\n• Export data\n• Send email alerts")
    else:
        st.success("✅ Employee Access")
        st.info("• View products\n• Record sales\n• View inventory\n• Basic reporting")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Main Homepage Content - LOGO AND TITLE

# Logo centered
st.markdown('<div style="text-align: center; margin: 2rem 0 1rem;">', unsafe_allow_html=True)

try:
    st.image("assets/logo.png", width=220)
except:
    st.image("https://img.icons8.com/color/96/warehouse.png", width=200)

st.markdown('</div>', unsafe_allow_html=True)

# Title - Visible purple color
st.markdown("""
    <div style="text-align: center;">
        <h1 style="
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            color: #6366f1;
            margin: 1rem 0 2rem;
            padding: 0;
            line-height: 1.3;
        ">
            Smart CPG Inventory<br/>& Sales Management System
        </h1>
    </div>
""", unsafe_allow_html=True)

# Welcome section
st.markdown(f"""
<div class="info-box">
<h2 style="margin-top: 0;">🎯 Welcome, {st.session_state.user_name}!</h2>

<p style="font-size: 1.1em; line-height: 1.6;">
This comprehensive system helps Consumer Packaged Goods (CPG) companies manage their operations efficiently with:
</p>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
    <div>📊 Real-Time Dashboard</div>
    <div>📦 Inventory Management</div>
    <div>💰 Sales Tracking</div>
    <div>🚨 Smart Alerts</div>
    <div>📈 Analytics & Reports</div>
    <div>🤖 AI Forecasting</div>
    <div>🔐 Role-Based Access</div>
    <div>📧 Email Notifications</div>
</div>
</div>
""", unsafe_allow_html=True)

# Display Key Metrics
st.markdown("## 📊 Today's Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_products = len(products_df)
    st.metric("Total Products", total_products, delta="Active")

with col2:
    sales_df = db.get_sales_data()
    total_revenue = sales_df['revenue'].sum() if not sales_df.empty else 0
    st.metric("Total Revenue", f"₹{total_revenue:,.2f}", delta="+12.5%")

with col3:
    low_stock_count = len(low_stock_df)
    st.metric("Low Stock Alerts", low_stock_count, 
              delta=f"-{low_stock_count}" if low_stock_count > 0 else "0",
              delta_color="inverse")

with col4:
    if not products_df.empty:
        total_stock_value = (products_df['price'] * products_df['stock_qty']).sum()
        st.metric("Stock Value", f"₹{total_stock_value:,.2f}")

# Quick Actions
st.markdown("## ⚡ Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if role in ["Admin", "Manager"]:
        if st.button("📦 Add New Product", use_container_width=True, type="primary"):
            st.switch_page("pages/Inventory.py")
    else:
        if st.button("📦 View Products", use_container_width=True):
            st.switch_page("pages/Inventory.py")

with col2:
    if st.button("💰 Record Sale", use_container_width=True, type="primary"):
        st.switch_page("pages/Sales.py")

with col3:
    if st.button("📊 View Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/Dashboard.py")

with col4:
    if role in ["Admin", "Manager"]:
        if st.button("🤖 AI Forecasting", use_container_width=True, type="primary"):
            st.switch_page("pages/Forecasting.py")

# Low Stock Alerts
if not low_stock_df.empty:
    st.markdown("## 🚨 Urgent: Low Stock Items")
    
    if role in ["Admin", "Manager"]:
        with st.expander("📧 Send Email Alert"):
            st.info("Use a Gmail account with 2-Factor Authentication and an App Password.")
            
            col1, col2 = st.columns(2)
            with col1:
                sender_email = st.text_input("Sender Email (Gmail)", "your-email@gmail.com")
                sender_password = st.text_input("Gmail App Password", type="password")
            with col2:
                recipient_emails = st.text_area("Recipient Emails (comma-separated)", "manager@company.com")
            
            if st.button("📤 Send Low Stock Alert", type="primary"):
                from email_alerts import EmailAlertSystem
                email_system = EmailAlertSystem()
                recipients = [email.strip() for email in recipient_emails.split(',')]
                
                with st.spinner("Sending email..."):
                    success, message = email_system.send_low_stock_alert(
                        low_stock_df, sender_email, sender_password, recipients
                    )
                    
                if success:
                    st.success(message)
                    db.log_activity(username, "Email Alert", f"Sent alert to {len(recipients)} recipients")
                else:
                    st.error(message)
    
    st.dataframe(
        low_stock_df[['name', 'category', 'sku', 'stock_qty', 'reorder_level', 'price']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
            "stock_qty": st.column_config.NumberColumn("Stock", format="%d units"),
            "reorder_level": st.column_config.NumberColumn("Reorder Level", format="%d units"),
        }
    )
else:
    st.success("✅ All products are well-stocked!")

# Recent Activity
if not sales_df.empty:
    st.markdown("## 📝 Recent Sales Activity")
    recent_sales = sales_df.head(5)[['date', 'name', 'quantity', 'revenue', 'region', 'recorded_by']]
    st.dataframe(
        recent_sales, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "revenue": st.column_config.NumberColumn("Revenue", format="₹%.2f"),
            "quantity": st.column_config.NumberColumn("Quantity", format="%d units"),
        }
    )

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p>🔐 Logged in as: <strong>{st.session_state.user_name}</strong> ({role})</p>
    <p>📧 Need help? Contact support@cpginventory.com</p>
    <p>© 2025 Smart CPG Inventory Management System | Built with Streamlit & Python</p>
</div>

""", unsafe_allow_html=True)
