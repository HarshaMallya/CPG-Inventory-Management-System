"""
Utils Package for CPG Inventory Management System

This package contains helper functions and utilities used across the application.

Modules:
    helpers: Common utility functions for formatting, calculations, and exports
"""

from .helpers import (
    format_currency,
    calculate_stock_status,
    export_to_csv,
    get_date_range_sales,
    calculate_growth_rate,
    validate_email,
    sanitize_input,
    generate_sku,
    calculate_reorder_quantity,
    get_stock_alert_level
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'format_currency',
    'calculate_stock_status',
    'export_to_csv',
    'get_date_range_sales',
    'calculate_growth_rate',
    'validate_email',
    'sanitize_input',
    'generate_sku',
    'calculate_reorder_quantity',
    'get_stock_alert_level'
]
