import streamlit as st


if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Please log in to access this page.")
    st.stop()

from data_manager import load_inventory, add_product, update_stock

st.set_page_config(page_title="Inventory Overview", layout="wide")

st.markdown("<div class='card'><h3>📦 Inventory Overview</h3></div>", unsafe_allow_html=True)

# Load inventory
inventory = load_inventory()

# ---------- Add Product Form ----------
st.markdown("### ➕ Add New Product")

with st.form("add_product_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        product_id = st.text_input("Product ID")
        name = st.text_input("Product Name")
    with col2:
        stock = st.number_input("Initial Stock", min_value=0, step=1)
        reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
    with col3:
        category = st.selectbox("Category", ["Food", "Beverage", "Personal Care", "Other"])

    submitted = st.form_submit_button("Add Product")

    if submitted:
        success, msg = add_product(product_id, name, stock, reorder_level, category)
        if success:
            st.success(msg)
        else:
            st.error(msg)

# ---------- Show Inventory Table ----------
st.markdown("### Current Inventory")
st.dataframe(inventory, use_container_width=True)

# ---------- Update Stock ----------
st.markdown("###  Update Stock Level")
product_to_update = st.selectbox("Select Product", inventory["product_id"].tolist() if not inventory.empty else [])
new_stock = st.number_input("New Stock Value", min_value=0, step=1)
if st.button("Update Stock"):
    success, msg = update_stock(product_to_update, new_stock)
    if success:
        st.success(msg)
    else:
        st.error(msg)
