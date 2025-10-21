import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from ml_forecast import forecast_sales

st.set_page_config(page_title="Sales Forecasting", page_icon="🤖", layout="wide")

if 'db' not in st.session_state:
    st.error("⚠️ Please login first")
    if st.button("🏠 Go to Login"):
        st.switch_page("Home.py")
    st.stop()

db = st.session_state.db
role = st.session_state.user_role
username = st.session_state.username

# Check permissions
if role not in ["Admin", "Manager"]:
    st.error("🚫 Access Denied: This feature is only available for Admin and Manager roles.")
    st.info("Please contact your administrator for access.")
    st.stop()

st.title("🤖 AI-Powered Sales Forecasting")
st.markdown(f"**Logged in as:** {st.session_state.user_name} ({role})")

# Info section
with st.expander("ℹ️ How Does This Work?", expanded=False):
    st.markdown("""
    This module uses **XGBoost**, a state-of-the-art machine learning algorithm, to forecast future sales based on historical patterns.
    
    ### 🔬 Technical Details:
    - **Algorithm:** XGBoost (Extreme Gradient Boosting)
    - **Features:** Time-lagged sales data (5-day window)
    - **Metrics:** 
        - RMSE (Root Mean Square Error) - Lower is better
        - MAE (Mean Absolute Error) - Average prediction error
        - Accuracy % - Overall prediction accuracy
    
    ### 📋 Requirements:
    - **Minimum 10 sales records** for the selected product
    - Sales data should span **multiple days**
    - More data = Better predictions
    
    ### 🎯 Use Cases:
    - Demand planning and inventory optimization
    - Identifying sales trends
    - Preventing stockouts
    - Budget forecasting
    """)

sales_df = db.get_sales_data()

if not sales_df.empty and len(sales_df) >= 10:
    st.success(f"✅ {len(sales_df)} sales records available for analysis")
    
    # Product selection
    products = sales_df['name'].unique()
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        selected_product = st.selectbox(
            "📦 Select Product to Forecast",
            products,
            help="Choose a product with sufficient sales history"
        )
    
    with col2:
        product_sales_count = len(sales_df[sales_df['name'] == selected_product])
        st.metric("Sales Records", product_sales_count)
    
    with col3:
        if product_sales_count >= 10:
            st.success("✅ Sufficient Data")
        else:
            st.warning("⚠️ Need More Data")
    
    # Show product details
    product_info = db.get_all_products()
    if not product_info.empty:
        product_details = product_info[product_info['name'] == selected_product].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"**Category:** {product_details['category']}")
        with col2:
            st.info(f"**SKU:** {product_details['sku']}")
        with col3:
            st.info(f"**Current Stock:** {product_details['stock_qty']} units")
        with col4:
            st.info(f"**Price:** ₹{product_details['price']:.2f}")
    
    st.markdown("---")
    
    # Check if product has enough data
    if product_sales_count < 10:
        st.warning(f"⚠️ **{selected_product}** has only {product_sales_count} sales records.")
        st.info("**Minimum 10 sales records required** for reliable forecasting. Please record more sales transactions for this product.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🚀 Generate AI Forecast", use_container_width=True, type="primary"):
                with st.spinner("🔄 Training AI model and generating predictions..."):
                    forecast_df, result = forecast_sales(sales_df, selected_product)
                    
                    if forecast_df is not None:
                        # Store in session state
                        st.session_state.forecast_data = forecast_df
                        st.session_state.forecast_metrics = result
                        st.session_state.forecast_product = selected_product
                        
                        # Log activity
                        db.log_activity(username, "ML Forecast", f"Generated forecast for {selected_product}")
        
        # Display forecast if available
        if 'forecast_data' in st.session_state and st.session_state.forecast_product == selected_product:
            forecast_df = st.session_state.forecast_data
            metrics = st.session_state.forecast_metrics
            
            st.success("✅ Forecast Generated Successfully!")
            
            # Display metrics
            st.markdown("### 📈 Model Performance Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "RMSE (Root Mean Square Error)", 
                    f"{metrics['rmse']:.2f}",
                    help="Lower values indicate better predictions"
                )
            
            with col2:
                st.metric(
                    "MAE (Mean Absolute Error)", 
                    f"{metrics['mae']:.2f}",
                    help="Average prediction error in units"
                )
            
            with col3:
                st.metric(
                    "Prediction Accuracy", 
                    f"{metrics['accuracy']:.1f}%",
                    help="Overall model accuracy"
                )
            
            st.markdown("---")
            
            # Plot forecast
            st.subheader("📊 Sales Forecast Visualization")
            
            fig = go.Figure()
            
            # Actual sales
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['actual'],
                name='Actual Sales',
                mode='lines+markers',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=8)
            ))
            
            # Predicted sales
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['predicted'],
                name='Predicted Sales',
                mode='lines+markers',
                line=dict(color='#A23B72', width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))
            
            fig.update_layout(
                title=f'Sales Forecast for {selected_product}',
                xaxis_title='Date',
                yaxis_title='Sales Quantity (Units)',
                hovermode='x unified',
                height=500,
                template='plotly_white',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast details table
            st.markdown("---")
            st.subheader("📋 Detailed Forecast Data")
            
            forecast_display = forecast_df.copy()
            forecast_display['difference'] = forecast_display['predicted'] - forecast_display['actual']
            forecast_display['accuracy_%'] = (1 - abs(forecast_display['difference'] / forecast_display['actual'])) * 100
            forecast_display['accuracy_%'] = forecast_display['accuracy_%'].clip(lower=0)  # Ensure no negative values
            
            st.dataframe(
                forecast_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "date": "Date",
                    "actual": st.column_config.NumberColumn("Actual Sales", format="%d units"),
                    "predicted": st.column_config.NumberColumn("Predicted Sales", format="%.2f units"),
                    "difference": st.column_config.NumberColumn("Difference", format="%.2f"),
                    "accuracy_%": st.column_config.NumberColumn("Accuracy", format="%.1f%%"),
                }
            )
            
            # Insights and Recommendations
            st.markdown("---")
            st.subheader("💡 Key Insights & Recommendations")
            
            avg_actual = forecast_df['actual'].mean()
            avg_predicted = forecast_df['predicted'].mean()
            trend_diff = ((avg_predicted - avg_actual) / avg_actual * 100)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Sales Trend Analysis")
                
                if trend_diff > 10:
                    st.success("📈 **Upward Trend Detected**")
                    st.info(f"Predicted sales are **{trend_diff:.1f}% higher** than historical average")
                    st.markdown("""
                    **Recommendations:**
                    - ✅ Increase stock levels
                    - ✅ Plan for higher demand
                    - ✅ Consider bulk ordering
                    """)
                elif trend_diff < -10:
                    st.warning("📉 **Downward Trend Detected**")
                    st.info(f"Predicted sales are **{abs(trend_diff):.1f}% lower** than historical average")
                    st.markdown("""
                    **Recommendations:**
                    - ⚠️ Reduce procurement
                    - ⚠️ Consider promotions
                    - ⚠️ Review pricing strategy
                    """)
                else:
                    st.info("➡️ **Stable Trend**")
                    st.success(f"Sales pattern is stable (±{abs(trend_diff):.1f}%)")
                    st.markdown("""
                    **Recommendations:**
                    - ✅ Maintain current stock levels
                    - ✅ Continue monitoring
                    """)
            
            with col2:
                st.markdown("### 📦 Inventory Recommendations")
                
                current_stock = product_details['stock_qty']
                reorder_level = product_details['reorder_level']
                recommended_stock = int(avg_predicted * 7)  # 7 days of predicted demand
                
                st.metric("Current Stock", f"{current_stock} units")
                st.metric("Average Daily Demand (Predicted)", f"{avg_predicted:.1f} units")
                st.metric("Recommended Stock (7 days)", f"{recommended_stock} units")
                
                if current_stock < recommended_stock:
                    shortage = recommended_stock - current_stock
                    st.error(f"⚠️ **Stock Shortage:** Need {shortage} more units")
                elif current_stock > recommended_stock * 2:
                    st.warning(f"📦 **Possible Overstock:** Consider reducing orders")
                else:
                    st.success("✅ **Optimal Stock Level**")
            
            # Export forecast
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                csv = forecast_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download Forecast (CSV)",
                    data=csv,
                    file_name=f"forecast_{selected_product}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Generate New Forecast", use_container_width=True):
                    del st.session_state.forecast_data
                    del st.session_state.forecast_metrics
                    st.rerun()
                    
elif not sales_df.empty:
    st.warning(f"⚠️ Need at least 10 sales records for accurate forecasting. Currently have {len(sales_df)} records.")
    st.info("💡 **Tip:** Record more sales transactions to unlock AI forecasting!")
    
    if st.button("💰 Record Sales"):
        st.switch_page("pages/Sales.py")
else:
    st.info("📭 No sales data available yet.")
    st.markdown("""
    ### Get Started with AI Forecasting:
    
    1. **Add products** to your inventory
    2. **Record at least 10 sales** transactions
    3. **Return here** to generate AI-powered forecasts!
    
    The more data you have, the more accurate the predictions will be.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Products", use_container_width=True):
            st.switch_page("pages/Inventory.py")
    with col2:
        if st.button("💰 Record Sales", use_container_width=True):
            st.switch_page("pages/Sales.py")
