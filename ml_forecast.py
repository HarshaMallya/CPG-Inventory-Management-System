import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta

def forecast_sales(sales_df, product_name, forecast_days=30):
    """Forecast sales for a specific product using XGBoost"""
    try:
        import xgboost as xgb
        
        product_sales = sales_df[sales_df['name'] == product_name].copy()
        product_sales['date'] = pd.to_datetime(product_sales['date'])
        product_sales = product_sales.sort_values('date')
        
        daily_sales = product_sales.groupby('date')['quantity'].sum().reset_index()
        
        if len(daily_sales) < 10:
            return None, "Not enough data for forecasting (minimum 10 records required)"
        
        def create_lagged_features(data, lag=5):
            lagged_data = data.copy()
            for i in range(1, min(lag + 1, len(data))):
                lagged_data[f'lag_{i}'] = lagged_data['quantity'].shift(i)
            return lagged_data.dropna()
        
        sales_with_lags = create_lagged_features(daily_sales, lag=5)
        
        if len(sales_with_lags) < 5:
            return None, "Insufficient data after feature engineering"
        
        X = sales_with_lags.drop(columns=['date', 'quantity'])
        y = sales_with_lags['quantity']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        
        forecast_df = pd.DataFrame({
            'date': sales_with_lags.iloc[-len(y_test):]['date'].values,
            'actual': y_test.values,
            'predicted': predictions
        })
        
        metrics = {
            'rmse': rmse,
            'mae': mae,
            'accuracy': max(0, 100 - (mae / y_test.mean() * 100))
        }
        
        return forecast_df, metrics
        
    except ImportError:
        return None, "XGBoost not installed. Run: pip install xgboost"
    except Exception as e:
        return None, f"Error: {str(e)}"
