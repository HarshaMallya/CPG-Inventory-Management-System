import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd

class EmailAlertSystem:
    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
    def send_low_stock_alert(self, low_stock_items, sender_email, sender_password, recipient_emails):
        """Send email alert for low stock items"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🚨 Low Stock Alert - {datetime.now().strftime("%Y-%m-%d")}'
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            
            html = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: Arial, sans-serif; }}
                  .header {{ background-color: #ff6b6b; color: white; padding: 20px; text-align: center; }}
                  .content {{ padding: 20px; }}
                  table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                  th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                  th {{ background-color: #4CAF50; color: white; }}
                  .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; margin-top: 20px; }}
                  .critical {{ background-color: #ffcccc; }}
                </style>
              </head>
              <body>
                <div class="header">
                  <h1>🚨 CPG Inventory Alert</h1>
                  <p>Low Stock Items Detected</p>
                </div>
                <div class="content">
                  <p>Dear Team,</p>
                  <p>The following products have fallen below their reorder levels and require immediate restocking:</p>
                  
                  <table>
                    <tr>
                      <th>Product Name</th>
                      <th>Category</th>
                      <th>SKU</th>
                      <th>Current Stock</th>
                      <th>Reorder Level</th>
                      <th>Status</th>
                    </tr>
            """
            
            for _, item in low_stock_items.iterrows():
                status_class = 'critical' if item['stock_qty'] == 0 else ''
                status_text = '🔴 OUT OF STOCK' if item['stock_qty'] == 0 else '🟡 LOW STOCK'
                
                html += f"""
                    <tr class="{status_class}">
                      <td>{item['name']}</td>
                      <td>{item['category']}</td>
                      <td>{item['sku']}</td>
                      <td>{item['stock_qty']} units</td>
                      <td>{item['reorder_level']} units</td>
                      <td>{status_text}</td>
                    </tr>
                """
            
            html += f"""
                  </table>
                  
                  <p style="margin-top: 20px;"><strong>Action Required:</strong> Please review and restock these items immediately.</p>
                </div>
                <div class="footer">
                  <p>📧 CPG Inventory Management System</p>
                  <p>Automated Alert - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_emails, msg.as_string())
            server.quit()
            
            return True, "Email alert sent successfully!"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_daily_report(self, sales_summary, inventory_summary, sender_email, sender_password, recipient_emails):
        """Send daily sales and inventory summary report"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'📊 Daily CPG Report - {datetime.now().strftime("%Y-%m-%d")}'
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #2c3e50;">📊 Daily Performance Report</h2>
                <p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d")}</p>
                
                <h3 style="color: #27ae60;">💰 Sales Summary</h3>
                <p><strong>Total Revenue:</strong> ₹{sales_summary.get('total_revenue', 0):,.2f}</p>
                <p><strong>Total Units Sold:</strong> {sales_summary.get('total_units', 0)}</p>
                <p><strong>Transactions:</strong> {sales_summary.get('total_transactions', 0)}</p>
                
                <h3 style="color: #e74c3c;">📦 Inventory Summary</h3>
                <p><strong>Total Products:</strong> {inventory_summary.get('total_products', 0)}</p>
                <p><strong>Low Stock Items:</strong> {inventory_summary.get('low_stock_count', 0)}</p>
                <p><strong>Inventory Value:</strong> ₹{inventory_summary.get('total_value', 0):,.2f}</p>
                
                <p style="margin-top: 20px; color: #7f8c8d;">This is an automated report from CPG Inventory Management System.</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_emails, msg.as_string())
            server.quit()
            
            return True, "Daily report sent successfully!"
            
        except Exception as e:
            return False, f"Failed to send report: {str(e)}"
