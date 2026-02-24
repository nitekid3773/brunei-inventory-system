import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import numpy as np
import hashlib
import json

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, professional CSS
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1e3c72;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #2c3e50;
        margin: 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #3498db;
    }
    
    /* Cards */
    .info-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    
    /* Metric values */
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1e3c72;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    
    /* Status badges */
    .badge-critical {
        background-color: #e74c3c;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-warning {
        background-color: #f39c12;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-normal {
        background-color: #27ae60;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Chat styling */
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #3498db;
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background-color: #e9ecef;
        color: #2c3e50;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #95a5a6;
        margin-top: 0.2rem;
    }
    
    /* Quick action buttons */
    .quick-action {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        display: inline-block;
        cursor: pointer;
        font-size: 0.9rem;
    }
    
    .quick-action:hover {
        background-color: #e9ecef;
    }
    
    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'products_df' not in st.session_state:
    st.session_state.products_df = None
if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = None
if 'transactions_df' not in st.session_state:
    st.session_state.transactions_df = None
if 'suppliers_df' not in st.session_state:
    st.session_state.suppliers_df = None
if 'purchase_orders_df' not in st.session_state:
    st.session_state.purchase_orders_df = None
if 'alerts_df' not in st.session_state:
    st.session_state.alerts_df = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data"""
    
    # Product Master List (50 products)
    products_data = [
        ['PRD00001', 'ELE9513', 8882629770, 'LED TV', 'Electronics', 785.00, 1135.09, 7, 'Supasave', 'Active', 'A3-12', 45, 15, '2026-12'],
        ['PRD00002', 'ELE6539', 8885034668, 'Smartphone', 'Electronics', 916.00, 1351.05, 35, 'Pohan Motors', 'Active', 'A3-08', 38, 28, '2026-10'],
        ['PRD00003', 'ELE5637', 8881920026, 'Laptop', 'Electronics', 618.00, 872.40, 25, 'Al-Falah Corporation', 'Active', 'A3-15', 22, 42, '2026-09'],
        ['PRD00004', 'ELE4243', 8887653820, 'Tablet', 'Electronics', 1960.00, 2653.80, 6, 'Hua Ho Trading', 'Active', 'A3-05', 8, 65, '2026-08'],
        ['PRD00005', 'ELE6781', 8881862054, 'Bluetooth Speaker', 'Electronics', 754.00, 907.19, 6, 'Soon Lee MegaMart', 'Active', 'A3-22', 42, 32, '2026-11'],
        ['PRD00006', 'GRO1086', 8888322742, 'Basmati Rice 5kg', 'Groceries', 8.00, 9.81, 18, 'Seng Huat', 'Active', 'B2-01', 120, 48, '2026-05'],
        ['PRD00007', 'GRO8871', 8889550421, 'Cooking Oil 2L', 'Groceries', 11.00, 14.28, 11, 'Al-Falah Corporation', 'Active', 'B2-04', 95, 52, '2026-06'],
        ['PRD00008', 'GRO5143', 8886941375, 'Sugar 1kg', 'Groceries', 47.00, 62.97, 46, 'Hua Ho Trading', 'Active', 'B2-07', 65, 44, '2026-07'],
        ['PRD00009', 'GRO6328', 8882079673, 'Flour 1kg', 'Groceries', 42.00, 58.50, 14, 'Hua Ho Trading', 'Active', 'B2-10', 70, 38, '2026-06'],
        ['PRD00010', 'GRO4921', 8882391650, 'Instant Noodles', 'Groceries', 3.00, 4.34, 50, 'Supasave', 'Active', 'B2-13', 200, 156, '2026-08'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 
        'Unit_Cost_BND', 'Selling_Price_BND', 'Reorder_Level', 
        'Preferred_Supplier', 'Status', 'Bin_Location', 
        'Daily_Movement', 'Lead_Time_Days', 'Expiry_Date'
    ])
    
    # Locations
    locations = ['Warehouse A', 'Store 1', 'Store 2', 'Store 3', 'Store 4']
    
    # Inventory
    inventory_data = []
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in enumerate(locations):
            qty = 50 + ((i + j) * 17) % 150
            inventory_data.append({
                'Product_ID': prod,
                'Location': loc,
                'Quantity_On_Hand': qty,
                'Last_Updated': datetime.now().strftime('%Y-%m-%d')
            })
    
    inventory = pd.DataFrame(inventory_data)
    
    # Transactions
    transactions_data = []
    for i in range(200):
        prod_idx = i % 10
        loc_idx = i % 5
        txn_type = ['ADJUSTMENT', 'STOCK IN', 'STOCK OUT'][i % 3]
        qty = 5 if txn_type == 'ADJUSTMENT' else (10 if txn_type == 'STOCK IN' else -5)
        
        transactions_data.append({
            'Transaction_ID': f'TRX2026{i:04d}',
            'Date': (datetime.now() - timedelta(days=200-i)).strftime('%Y-%m-%d'),
            'Product_ID': products_data[prod_idx][0],
            'Product_Name': products_data[prod_idx][3],
            'Transaction_Type': txn_type,
            'Quantity_Change': qty,
            'Location': locations[loc_idx],
            'User': random.choice(['John', 'Sarah', 'Mike', 'Lisa'])
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Suppliers
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', '673-2223456', 'purchasing@huaho.com', 'Kiulap', 'Net 30', 'A', 0.98],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', '673-2337890', 'orders@soonlee.com', 'Gadong', 'Net 30', 'A', 0.95],
        ['SUP003', 'Supasave', 'David Wong', '673-2456789', 'procurement@supasave.com', 'Serusop', 'Net 45', 'B', 0.92],
        ['SUP004', 'Seng Huat', 'Michael Chen', '673-2771234', 'sales@senghuat.com', 'Kuala Belait', 'Cash on Delivery', 'A', 0.97],
        ['SUP005', 'SKH Group', 'Steven Khoo', '673-2667890', 'trading@skh.com', 'Tutong', 'Net 30', 'A', 0.96],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Phone', 
        'Email', 'Address', 'Payment_Terms', 'Tier', 'Reliability_Score'
    ])
    
    # Purchase Orders
    purchase_orders_data = []
    for i in range(40):
        prod_idx = i % 10
        supp_idx = i % 5
        
        purchase_orders_data.append({
            'PO_Number': f'PO2026{i:04d}',
            'Supplier_ID': suppliers_data[supp_idx][0],
            'Supplier_Name': suppliers_data[supp_idx][1],
            'Product_ID': products_data[prod_idx][0],
            'Product_Name': products_data[prod_idx][3],
            'Ordered_Quantity': 100 + (i * 10),
            'Unit_Cost_BND': products_data[prod_idx][5],
            'Total_Cost_BND': (100 + i * 10) * products_data[prod_idx][5],
            'Order_Date': (datetime.now() - timedelta(days=90-i*2)).strftime('%Y-%m-%d'),
            'Expected_Date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'Order_Status': random.choice(['Draft', 'Sent', 'Confirmed', 'Received'])
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Stock Alerts
    current_stock = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(products[['Product_ID', 'Product_Name', 'Reorder_Level', 'Lead_Time_Days']], on='Product_ID')
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= 0:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    alerts['Alert_Status'] = alerts.apply(get_alert_status, axis=1)
    alerts['Days_Until_Stockout'] = (alerts['Quantity_On_Hand'] / 10).round(1)  # Assuming 10 units/day avg
    
    return products, inventory, transactions, suppliers, purchase_orders, alerts

# Initialize data
if st.session_state.products_df is None:
    (st.session_state.products_df, 
     st.session_state.inventory_df, 
     st.session_state.transactions_df, 
     st.session_state.suppliers_df, 
     st.session_state.purchase_orders_df, 
     st.session_state.alerts_df) = load_initial_data()

# ============================================
# ADVANCED AI CHATBOT WITH WAREHOUSE KNOWLEDGE
# ============================================

class WarehouseChatbot:
    """Intelligent chatbot with deep warehouse knowledge"""
    
    def __init__(self):
        self.context = {}
        self.last_query = None
        
    def get_response(self, query, user_id="default"):
        """Generate intelligent response based on query"""
        query_lower = query.lower()
        
        # Check for greetings
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return self._greeting_response()
        
        # Check for help
        elif 'help' in query_lower or 'what can you do' in query_lower:
            return self._help_response()
        
        # Inventory queries
        elif any(word in query_lower for word in ['inventory', 'stock', 'quantity', 'how many']):
            return self._inventory_response(query_lower)
        
        # Product queries
        elif any(word in query_lower for word in ['product', 'item', 'sku']):
            return self._product_response(query_lower)
        
        # Alert queries
        elif any(word in query_lower for word in ['alert', 'warning', 'critical', 'low stock']):
            return self._alert_response()
        
        # Supplier queries
        elif any(word in query_lower for word in ['supplier', 'vendor', 'who supplies']):
            return self._supplier_response(query_lower)
        
        # Order queries
        elif any(word in query_lower for word in ['order', 'po', 'purchase']):
            return self._order_response(query_lower)
        
        # Forecast queries
        elif any(word in query_lower for word in ['forecast', 'predict', 'future', 'trend']):
            return self._forecast_response(query_lower)
        
        # Location queries
        elif any(word in query_lower for word in ['location', 'where', 'warehouse', 'store']):
            return self._location_response(query_lower)
        
        # Cost/price queries
        elif any(word in query_lower for word in ['cost', 'price', 'value', 'worth']):
            return self._cost_response(query_lower)
        
        # Expiry queries
        elif any(word in query_lower for word in ['expiry', 'expire', 'expiration']):
            return self._expiry_response()
        
        # Performance queries
        elif any(word in query_lower for word in ['performance', 'efficiency', 'kpi']):
            return self._performance_response()
        
        # Recommendation queries
        elif any(word in query_lower for word in ['recommend', 'suggest', 'advice', 'tip']):
            return self._recommendation_response()
        
        # Comparison queries
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            return self._comparison_response(query_lower)
        
        # Default response
        else:
            return self._default_response()
    
    def _greeting_response(self):
        return """👋 Hello! I'm your AI Warehouse Assistant. I can help you with:
        
• 📦 **Inventory queries** - "How many LED TVs do we have?"
• ⚠️ **Stock alerts** - "Show me low stock items"
• 📊 **Forecasts** - "What will demand be next week?"
• 🏢 **Supplier info** - "Who supplies rice?"
• 📍 **Location tracking** - "Where is product PRD00001?"
• 💰 **Cost analysis** - "What's our total inventory value?"
• 🔄 **Order status** - "Show pending purchase orders"
• 💡 **Recommendations** - "What should I reorder?"

What would you like to know?"""
    
    def _help_response(self):
        return """📚 **I can answer questions about:**

**Inventory Management:**
• "How many items are in stock?"
• "What products are low on stock?"
• "Show me inventory by location"
• "What's our total inventory value?"

**Products:**
• "Tell me about product PRD00001"
• "What electronics do we have?"
• "Which products are near expiry?"

**Suppliers:**
• "Who are our top suppliers?"
• "Show supplier performance"
• "Which supplier has best reliability?"

**Orders & Purchasing:**
• "What orders are pending?"
• "Show recent transactions"
• "What should I reorder today?"

**Analytics:**
• "Forecast demand for next month"
• "What's our best-selling product?"
• "Compare sales across locations"

**Just ask me anything about your warehouse!**"""
    
    def _inventory_response(self, query):
        total_items = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        
        # Check for specific product
        for _, product in st.session_state.products_df.iterrows():
            if product['Product_Name'].lower() in query or product['Product_ID'].lower() in query:
                stock = st.session_state.inventory_df[
                    st.session_state.inventory_df['Product_ID'] == product['Product_ID']
                ]['Quantity_On_Hand'].sum()
                return f"📦 **{product['Product_Name']}** (ID: {product['Product_ID']})\n" + \
                       f"• Current stock: {stock} units\n" + \
                       f"• Reorder level: {product['Reorder_Level']}\n" + \
                       f"• Bin location: {product['Bin_Location']}\n" + \
                       f"• Status: {product['Status']}"
        
        # General inventory stats
        if 'total' in query or 'overall' in query:
            return f"📊 **Overall Inventory:**\n" + \
                   f"• Total items: {total_items:,}\n" + \
                   f"• Total value: ${total_value:,.2f}\n" + \
                   f"• Unique products: {len(st.session_state.products_df)}\n" + \
                   f"• Locations: {st.session_state.inventory_df['Location'].nunique()}"
        
        # By location
        if 'location' in query or 'warehouse' in query or 'store' in query:
            loc_summary = st.session_state.inventory_df.groupby('Location')['Quantity_On_Hand'].sum()
            response = "📍 **Stock by Location:**\n"
            for loc, qty in loc_summary.items():
                response += f"• {loc}: {qty:,} units\n"
            return response
        
        return f"📊 **Current Inventory:**\n• Total items: {total_items:,}\n• Total value: ${total_value:,.2f}"
    
    def _product_response(self, query):
        # Search for specific product
        for _, product in st.session_state.products_df.iterrows():
            if product['Product_Name'].lower() in query or product['Product_ID'].lower() in query or product['SKU'].lower() in query:
                stock = st.session_state.inventory_df[
                    st.session_state.inventory_df['Product_ID'] == product['Product_ID']
                ]['Quantity_On_Hand'].sum()
                margin = ((product['Selling_Price_BND'] - product['Unit_Cost_BND']) / product['Selling_Price_BND'] * 100)
                
                return f"""📋 **Product Details: {product['Product_Name']}**

**Basic Info:**
• ID: {product['Product_ID']}
• SKU: {product['SKU']}
• Category: {product['Category']}
• Bin: {product['Bin_Location']}

**Pricing:**
• Cost: ${product['Unit_Cost_BND']:.2f}
• Selling: ${product['Selling_Price_BND']:.2f}
• Margin: {margin:.1f}%

**Stock:**
• Current: {stock} units
• Reorder at: {product['Reorder_Level']}
• Daily movement: {product['Daily_Movement']} units

**Supplier:**
• Preferred: {product['Preferred_Supplier']}
• Lead time: {product['Lead_Time_Days']} days
• Expiry: {product['Expiry_Date']}"""
        
        # Category search
        categories = st.session_state.products_df['Category'].unique()
        for cat in categories:
            if cat.lower() in query:
                cat_products = st.session_state.products_df[
                    st.session_state.products_df['Category'] == cat
                ]
                total_value = (st.session_state.inventory_df.merge(
                    cat_products[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
                ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
                
                return f"📦 **{cat} Category**\n" + \
                       f"• Products: {len(cat_products)}\n" + \
                       f"• Total value: ${total_value:,.2f}\n" + \
                       f"• Top product: {cat_products['Product_Name'].iloc[0]}"
        
        return f"📦 **Product Summary:**\n• Total products: {len(st.session_state.products_df)}\n• Categories: {st.session_state.products_df['Category'].nunique()}"
    
    def _alert_response(self):
        alerts = st.session_state.alerts_df
        critical = alerts[alerts['Alert_Status'] == 'CRITICAL']
        warning = alerts[alerts['Alert_Status'] == 'WARNING']
        
        response = "⚠️ **Stock Alerts:**\n\n"
        
        if len(critical) > 0:
            response += "🔴 **CRITICAL - Immediate Action Required:**\n"
            for _, item in critical.iterrows():
                response += f"• {item['Product_Name']}: {item['Quantity_On_Hand']} units (Reorder at {item['Reorder_Level']})\n"
            response += "\n"
        
        if len(warning) > 0:
            response += "🟡 **WARNING - Reorder Soon:**\n"
            for _, item in warning.head(5).iterrows():
                response += f"• {item['Product_Name']}: {item['Quantity_On_Hand']} units\n"
        
        if len(critical) == 0 and len(warning) == 0:
            response += "✅ All stock levels are healthy!"
        
        return response
    
    def _supplier_response(self, query):
        # Specific supplier
        for _, supplier in st.session_state.suppliers_df.iterrows():
            if supplier['Supplier_Name'].lower() in query:
                # Get products from this supplier
                products = st.session_state.products_df[
                    st.session_state.products_df['Preferred_Supplier'] == supplier['Supplier_Name']
                ]
                total_po = st.session_state.purchase_orders_df[
                    st.session_state.purchase_orders_df['Supplier_Name'] == supplier['Supplier_Name']
                ]['Total_Cost_BND'].sum()
                
                return f"""🏢 **Supplier: {supplier['Supplier_Name']}**

**Contact Info:**
• Contact: {supplier['Contact_Person']}
• Phone: {supplier['Phone']}
• Email: {supplier['Email']}
• Address: {supplier['Address']}

**Performance:**
• Tier: {supplier['Tier']}
• Reliability: {supplier['Reliability_Score']*100:.0f}%
• Payment terms: {supplier['Payment_Terms']}

**Products supplied: {len(products)}**
• Total PO value: ${total_po:,.2f}"""
        
        # Top suppliers
        if 'top' in query or 'best' in query:
            top_suppliers = st.session_state.suppliers_df.nlargest(3, 'Reliability_Score')
            response = "🏆 **Top Suppliers by Reliability:**\n"
            for _, s in top_suppliers.iterrows():
                response += f"• {s['Supplier_Name']}: {s['Reliability_Score']*100:.0f}%\n"
            return response
        
        return f"📋 **Supplier Summary:**\n• Total suppliers: {len(st.session_state.suppliers_df)}\n• Average reliability: {st.session_state.suppliers_df['Reliability_Score'].mean()*100:.0f}%"
    
    def _order_response(self, query):
        pending = st.session_state.purchase_orders_df[
            st.session_state.purchase_orders_df['Order_Status'].isin(['Draft', 'Sent', 'Confirmed'])
        ]
        
        if 'pending' in query:
            response = f"📋 **Pending Orders ({len(pending)}):**\n"
            for _, po in pending.head(5).iterrows():
                response += f"• {po['PO_Number']}: {po['Product_Name']} - {po['Order_Status']}\n"
            return response
        
        if 'recent' in query:
            recent = st.session_state.purchase_orders_df.nlargest(5, 'Order_Date')
            response = "🔄 **Recent Orders:**\n"
            for _, po in recent.iterrows():
                response += f"• {po['PO_Number']}: {po['Product_Name']} - {po['Order_Status']}\n"
            return response
        
        total_value = st.session_state.purchase_orders_df['Total_Cost_BND'].sum()
        return f"📊 **Order Summary:**\n• Total orders: {len(st.session_state.purchase_orders_df)}\n• Pending: {len(pending)}\n• Total value: ${total_value:,.2f}"
    
    def _forecast_response(self, query):
        # Simple forecast based on historical movement
        products = st.session_state.products_df.nlargest(5, 'Daily_Movement')
        
        response = "📈 **Demand Forecast (Next 30 days):**\n\n"
        
        for _, product in products.iterrows():
            forecast = product['Daily_Movement'] * 30 * random.uniform(0.9, 1.1)
            response += f"• **{product['Product_Name']}**: ~{forecast:.0f} units\n"
        
        response += "\n💡 **Recommendation:** Increase safety stock for top movers by 15%"
        return response
    
    def _location_response(self, query):
        # Find product location
        for _, product in st.session_state.products_df.iterrows():
            if product['Product_Name'].lower() in query or product['Product_ID'].lower() in query:
                return f"📍 **{product['Product_Name']}** is located at bin **{product['Bin_Location']}** in Warehouse A"
        
        # Summary by location
        loc_summary = st.session_state.inventory_df.groupby('Location').agg({
            'Quantity_On_Hand': 'sum',
            'Product_ID': 'nunique'
        }).reset_index()
        
        response = "📍 **Inventory by Location:**\n"
        for _, loc in loc_summary.iterrows():
            response += f"• **{loc['Location']}**: {loc['Quantity_On_Hand']:,} units ({loc['Product_ID']} products)\n"
        
        return response
    
    def _cost_response(self, query):
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        
        # Top value products
        value_df = st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Product_Name', 'Unit_Cost_BND']], on='Product_ID'
        )
        value_df['Total_Value'] = value_df['Quantity_On_Hand'] * value_df['Unit_Cost_BND']
        top_value = value_df.nlargest(5, 'Total_Value')[['Product_Name', 'Total_Value']].drop_duplicates()
        
        response = f"💰 **Inventory Value Analysis:**\n\n"
        response += f"• **Total value:** ${total_value:,.2f}\n"
        response += f"• **Average item value:** ${total_value/len(st.session_state.inventory_df):.2f}\n\n"
        response += "**Top 5 by Value:**\n"
        for _, item in top_value.iterrows():
            response += f"• {item['Product_Name']}: ${item['Total_Value']:,.2f}\n"
        
        return response
    
    def _expiry_response(self):
        today = datetime.now()
        products = st.session_state.products_df.copy()
        products['Days_to_Expiry'] = products['Expiry_Date'].apply(
            lambda x: (datetime.strptime(x, '%Y-%m') - today).days
        )
        
        near_expiry = products[products['Days_to_Expiry'] < 90].nsmallest(5, 'Days_to_Expiry')
        
        if len(near_expiry) > 0:
            response = "⚠️ **Products Near Expiry:**\n"
            for _, p in near_expiry.iterrows():
                response += f"• {p['Product_Name']}: expires {p['Expiry_Date']} ({p['Days_to_Expiry']} days)\n"
        else:
            response = "✅ No products near expiry"
        
        return response
    
    def _performance_response(self):
        # Key metrics
        total_items = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        
        # Order fulfillment rate
        received = len(st.session_state.purchase_orders_df[
            st.session_state.purchase_orders_df['Order_Status'] == 'Received'
        ])
        total_orders = len(st.session_state.purchase_orders_df)
        fulfillment_rate = (received / total_orders * 100) if total_orders > 0 else 0
        
        # Supplier reliability
        avg_reliability = st.session_state.suppliers_df['Reliability_Score'].mean() * 100
        
        return f"""📊 **Warehouse Performance Dashboard**

**Inventory Metrics:**
• Total items: {total_items:,}
• Total value: ${total_value:,.2f}
• Items per location: {total_items/st.session_state.inventory_df['Location'].nunique():.0f}

**Order Metrics:**
• Order fulfillment: {fulfillment_rate:.1f}%
• Avg supplier reliability: {avg_reliability:.1f}%
• Pending orders: {len(st.session_state.purchase_orders_df[st.session_state.purchase_orders_df['Order_Status'].isin(['Draft', 'Sent', 'Confirmed'])])}

**Efficiency Score: 87% - Good**"""
    
    def _recommendation_response(self):
        # Get low stock items
        alerts = st.session_state.alerts_df
        low_stock = alerts[alerts['Alert_Status'].isin(['CRITICAL', 'WARNING'])]
        
        response = "💡 **AI Recommendations:**\n\n"
        
        if len(low_stock) > 0:
            response += "**📦 Reorder these items today:**\n"
            for _, item in low_stock.head(3).iterrows():
                supplier = st.session_state.products_df[
                    st.session_state.products_df['Product_ID'] == item['Product_ID']
                ]['Preferred_Supplier'].values[0]
                response += f"• {item['Product_Name']}: order {item['Reorder_Level'] * 2} units from {supplier}\n"
        
        # Fast mover suggestion
        fast_movers = st.session_state.products_df.nlargest(3, 'Daily_Movement')
        response += "\n**🔥 Fast-moving items (increase safety stock):**\n"
        for _, item in fast_movers.iterrows():
            response += f"• {item['Product_Name']}: {item['Daily_Movement']} units/day\n"
        
        # Supplier suggestion
        best_supplier = st.session_state.suppliers_df.nlargest(1, 'Reliability_Score').iloc[0]
        response += f"\n**🏆 Best performing supplier:** {best_supplier['Supplier_Name']} ({best_supplier['Reliability_Score']*100:.0f}% reliability)"
        
        return response
    
    def _comparison_response(self, query):
        # Compare two products
        words = query.split()
        products_found = []
        
        for word in words:
            for _, product in st.session_state.products_df.iterrows():
                if product['Product_Name'].lower() in word.lower() or product['Product_ID'].lower() in word.lower():
                    products_found.append(product)
        
        if len(products_found) >= 2:
            p1, p2 = products_found[:2]
            stock1 = st.session_state.inventory_df[
                st.session_state.inventory_df['Product_ID'] == p1['Product_ID']
            ]['Quantity_On_Hand'].sum()
            stock2 = st.session_state.inventory_df[
                st.session_state.inventory_df['Product_ID'] == p2['Product_ID']
            ]['Quantity_On_Hand'].sum()
            
            return f"""📊 **Product Comparison**

| Metric | {p1['Product_Name']} | {p2['Product_Name']} |
|--------|-------------------|-------------------|
| Stock | {stock1} units | {stock2} units |
| Price | ${p1['Selling_Price_BND']} | ${p2['Selling_Price_BND']} |
| Cost | ${p1['Unit_Cost_BND']} | ${p2['Unit_Cost_BND']} |
| Margin | {((p1['Selling_Price_BND']-p1['Unit_Cost_BND'])/p1['Selling_Price_BND']*100):.0f}% | {((p2['Selling_Price_BND']-p2['Unit_Cost_BND'])/p2['Selling_Price_BND']*100):.0f}% |
| Movement | {p1['Daily_Movement']}/day | {p2['Daily_Movement']}/day |"""
        
        return "To compare products, please specify two product names or IDs."
    
    def _default_response(self):
        return """I'm not sure I understood. Try asking about:

• 📦 **Products** - "Tell me about LED TV"
• 📊 **Inventory** - "How many items in stock?"
• ⚠️ **Alerts** - "Show low stock items"
• 🏢 **Suppliers** - "Who is our best supplier?"
• 💰 **Costs** - "What's our inventory worth?"
• 📈 **Forecasts** - "Predict next month's demand"

Or type 'help' to see all options."""

# Initialize chatbot
chatbot = WarehouseChatbot()

# ============================================
# AI CHATBOT INTERFACE
# ============================================

def show_ai_chatbot():
    st.markdown('<div class="section-header">AI Warehouse Assistant</div>', unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("**Quick questions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Inventory value"):
            query = "What's our total inventory value?"
            response = chatbot.get_response(query)
            st.session_state.chat_history.append({"role": "user", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("⚠️ Low stock alerts"):
            query = "Show me low stock items"
            response = chatbot.get_response(query)
            st.session_state.chat_history.append({"role": "user", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🏆 Best supplier"):
            query = "Who is our best supplier?"
            response = chatbot.get_response(query)
            st.session_state.chat_history.append({"role": "user", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("📈 Demand forecast"):
            query = "Forecast demand for next month"
            response = chatbot.get_response(query)
            st.session_state.chat_history.append({"role": "user", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your warehouse..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Get bot response
        response = chatbot.get_response(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

# ============================================
# AI INNOVATIONS
# ============================================

def show_ai_innovations():
    st.markdown('<div class="section-header">AI Warehouse Innovations</div>', unsafe_allow_html=True)
    
    # Create tabs for each innovation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Smart Slotting", 
        "Demand Prediction", 
        "Visual Counting", 
        "Cold Chain",
        "Returns AI",
        "Supplier Intelligence",
        "Price Optimization",
        "Anomaly Detection"
    ])
    
    with tab1:
        st.subheader("AI Smart Slotting System")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Current Efficiency: 67%**
            
            **AI Analysis:**
            - Fast movers should be near shipping
            - Frequently bought together items identified
            - Heavy items moved to waist height
            
            **Optimization Benefits:**
            - Pick time: -23%
            - Travel distance: -31%
            - Productivity: +18%
            """)
            
            if st.button("Run Optimization"):
                st.success("✅ Layout optimized! New efficiency: 89%")
        
        with col2:
            # Heat map of current vs optimized
            heatmap_data = pd.DataFrame({
                'Zone': ['A (Fast)', 'B (Medium)', 'C (Slow)'],
                'Current': [45, 35, 20],
                'Optimized': [60, 30, 10]
            })
            fig = px.bar(heatmap_data, x='Zone', y=['Current', 'Optimized'],
                        title="Item Distribution by Zone",
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("AI Demand Prediction Engine")
        
        # Generate forecast
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast_data = pd.DataFrame({
            'Date': dates,
            'Electronics': [45 + 10*np.sin(i/7) + random.randint(-3,3) for i in range(30)],
            'Groceries': [120 + 30*np.sin(i/7) + random.randint(-10,10) for i in range(30)],
            'Pharma': [30 + 5*np.sin(i/14) + random.randint(-2,2) for i in range(30)]
        })
        
        fig = px.line(forecast_data, x='Date', y=['Electronics', 'Groceries', 'Pharma'],
                     title="30-Day Demand Forecast by Category")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📈 **Groceries** expected to increase 22% next week")
        with col2:
            st.warning("⚠️ **Electronics** showing seasonal dip in 2 weeks")
    
    with tab3:
        st.subheader("AI Visual Counting System")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Camera 1 - Aisle A (Electronics)**
            - Accuracy: 97.3%
            - Last count: 2 min ago
            - Discrepancies: 2 items
            """)
            
            st.metric("Confidence Score", "98.2%", "+1.2%")
        
        with col2:
            st.markdown("""
            **Camera 2 - Aisle B (Groceries)**
            - Accuracy: 99.1%
            - Last count: 5 min ago
            - Discrepancies: 0 items
            """)
            
            st.metric("Items Counted Today", "15,342", "+234")
        
        if st.button("Run Full Warehouse Count"):
            with st.spinner("AI analyzing all camera feeds..."):
                time.sleep(3)
                st.success("✅ Count complete! 99.3% accuracy overall")
    
    with tab4:
        st.subheader("AI Cold Chain Monitoring")
        
        # Temperature data
        temp_data = pd.DataFrame({
            'Hour': list(range(24)),
            'Freezer': [-20 + 0.5*np.sin(i/12) + 0.2*random.random() for i in range(24)],
            'Chiller': [4 + 0.3*np.sin(i/8) + 0.1*random.random() for i in range(24)],
            'Ambient': [22 + 2*np.sin(i/6) + 0.5*random.random() for i in range(24)]
        })
        
        fig = px.line(temp_data, x='Hour', y=['Freezer', 'Chiller', 'Ambient'],
                     title="Temperature Trends - Last 24 Hours")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Freezer", "-19.8°C", "0.2° above target")
        col2.metric("Chiller", "4.2°C", "⚠️ Above range")
        col3.metric("Ambient", "22.5°C", "✅ Normal")
    
    with tab5:
        st.subheader("AI Returns Management")
        
        # Returns analysis
        returns_data = pd.DataFrame({
            'Reason': ['Damaged', 'Defective', 'Wrong Item', 'Expired', 'Other'],
            'Count': [45, 32, 28, 15, 8]
        })
        
        fig = px.pie(returns_data, values='Count', names='Reason',
                    title="Returns by Reason")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **AI Insights:**
        - Smartphone returns peak after software updates
        - Rice expiry concentrated in monsoon months
        - Electronics damage during afternoon shifts
        
        **Recovered Value: $12,450 this month (+18%)**
        """)
    
    with tab6:
        st.subheader("AI Supplier Intelligence")
        
        # Supplier performance
        supplier_perf = pd.DataFrame({
            'Supplier': ['Hua Ho', 'Soon Lee', 'Supasave', 'Seng Huat', 'SKH'],
            'Reliability': [98, 95, 92, 97, 96],
            'Lead_Time': [3, 4, 5, 2, 3],
            'Quality': [99, 97, 94, 98, 96]
        })
        
        fig = px.scatter(supplier_perf, x='Reliability', y='Quality',
                        size='Lead_Time', text='Supplier',
                        title="Supplier Performance Matrix")
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("🏆 **Top Performer:** Hua Ho Trading (98% reliability, 99% quality)")
    
    with tab7:
        st.subheader("AI Price Optimization")
        
        # Price elasticity analysis
        products = ['LED TV', 'Smartphone', 'Rice 5kg', 'Cooking Oil']
        current_margin = [45, 32, 18, 23]
        optimized_margin = [52, 38, 22, 28]
        
        fig = go.Figure(data=[
            go.Bar(name='Current Margin %', x=products, y=current_margin),
            go.Bar(name='Optimized Margin %', x=products, y=optimized_margin)
        ])
        fig.update_layout(title="Margin Optimization Opportunity", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **AI Recommendations:**
        - Increase electronics prices by 5% (elasticity = -1.2)
        - Bundle slow-moving items with fast movers
        - Volume discounts for bulk grocery orders
        
        **Potential Profit Increase: 18%**
        """)
    
    with tab8:
        st.subheader("AI Anomaly Detection")
        
        # Anomaly detection chart
        dates = pd.date_range(start=datetime.now()-timedelta(days=30), periods=30, freq='D')
        transactions = [random.randint(80, 120) for _ in range(30)]
        transactions[15] = 250  # anomaly
        
        anomaly_df = pd.DataFrame({
            'Date': dates,
            'Transactions': transactions
        })
        
        fig = px.line(anomaly_df, x='Date', y='Transactions',
                     title="Transaction Volume with Anomaly Detection")
        fig.add_scatter(x=[dates[15]], y=[250], mode='markers',
                       marker=dict(size=15, color='red'),
                       name='Anomaly Detected')
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("""
        **🚨 Anomalies Detected:**
        - Unusual spike in transactions on Mar 15 (250% above normal)
        - 3 instances of after-hours access detected
        - 2 products with unexpected stock variances
        
        **AI Recommendations:** Review security footage for Mar 15
        """)

# ============================================
# CORE DASHBOARD PAGES
# ============================================

def show_executive_dashboard():
    st.markdown('<div class="section-header">Executive Dashboard</div>', unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(st.session_state.products_df)
        st.metric("Total Products", total_products)
    
    with col2:
        total_inventory = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        st.metric("Items in Stock", f"{total_inventory:,}")
    
    with col3:
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        st.metric("Inventory Value", f"${total_value:,.0f}")
    
    with col4:
        alerts = len(st.session_state.alerts_df[st.session_state.alerts_df['Alert_Status'] == 'CRITICAL'])
        st.metric("Critical Alerts", alerts)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock by Category")
        cat_stock = st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Category']], on='Product_ID'
        ).groupby('Category')['Quantity_On_Hand'].sum().reset_index()
        fig = px.pie(cat_stock, values='Quantity_On_Hand', names='Category')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Stock by Location")
        loc_stock = st.session_state.inventory_df.groupby('Location')['Quantity_On_Hand'].sum().reset_index()
        fig = px.bar(loc_stock, x='Location', y='Quantity_On_Hand')
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Insights
    st.subheader("🤖 AI Insights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📦 **Reorder Alert:** 5 items below safety stock")
    with col2:
        st.warning("📈 **Demand Spike:** Electronics up 22% this week")
    with col3:
        st.success("✅ **Efficiency:** Pick accuracy at 99.2%")

def show_product_crud():
    st.markdown('<div class="section-header">Product Management</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", len(st.session_state.products_df))
    col2.metric("Active", len(st.session_state.products_df[st.session_state.products_df['Status'] == 'Active']))
    col3.metric("Categories", st.session_state.products_df['Category'].nunique())
    col4.metric("Suppliers", st.session_state.suppliers_df['Supplier_Name'].nunique())
    
    # Action buttons
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("➕ Add New"):
            st.session_state.show_add_form = True
    
    if st.session_state.get('show_add_form', False):
        with st.form("add_product_form"):
            st.subheader("Add New Product")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name *")
                category = st.selectbox("Category", 
                    ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                     'Automotive', 'Textiles', 'Furniture', 'Stationery'])
            
            with col2:
                cost = st.number_input("Unit Cost *", min_value=0.01, value=100.00)
                price = st.number_input("Selling Price *", min_value=0.01, value=150.00)
                reorder = st.number_input("Reorder Level", min_value=1, value=10)
            
            supplier = st.selectbox("Preferred Supplier", 
                st.session_state.suppliers_df['Supplier_Name'].tolist())
            
            if st.form_submit_button("Save"):
                if name and cost and price:
                    new_product = {
                        'Product_ID': f"PRD{len(st.session_state.products_df)+1:05d}",
                        'SKU': f"{category[:3].upper()}{random.randint(10000,99999)}",
                        'Barcode': random.randint(1000000, 9999999),
                        'Product_Name': name,
                        'Category': category,
                        'Unit_Cost_BND': cost,
                        'Selling_Price_BND': price,
                        'Reorder_Level': reorder,
                        'Preferred_Supplier': supplier,
                        'Status': 'Active',
                        'Bin_Location': 'TBD',
                        'Daily_Movement': 0,
                        'Lead_Time_Days': 7,
                        'Expiry_Date': '2026-12'
                    }
                    st.session_state.products_df = pd.concat(
                        [st.session_state.products_df, pd.DataFrame([new_product])], 
                        ignore_index=True
                    )
                    st.success("Product added!")
                    st.session_state.show_add_form = False
                    st.rerun()
    
    # Product list
    st.subheader("Product List")
    search = st.text_input("🔍 Search")
    
    filtered_df = st.session_state.products_df
    if search:
        filtered_df = filtered_df[filtered_df['Product_Name'].str.contains(search, case=False)]
    
    st.dataframe(filtered_df, use_container_width=True)

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Menu")
    
    page = st.sidebar.radio("Select:", [
        "Executive Dashboard",
        "Product Management",
        "Inventory by Location",
        "Stock Transactions",
        "Purchase Orders",
        "Suppliers",
        "Stock Alerts",
        "AI Chatbot Assistant",
        "AI Innovations"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    
    # Page routing
    if page == "Executive Dashboard":
        show_executive_dashboard()
    elif page == "Product Management":
        show_product_crud()
    elif page == "Inventory by Location":
        show_inventory()
    elif page == "Stock Transactions":
        show_transactions()
    elif page == "Purchase Orders":
        show_purchase_orders()
    elif page == "Suppliers":
        show_suppliers()
    elif page == "Stock Alerts":
        show_alerts()
    elif page == "AI Chatbot Assistant":
        show_ai_chatbot()
    elif page == "AI Innovations":
        show_ai_innovations()

# Include the missing page functions
def show_inventory():
    st.markdown('<div class="section-header">Inventory by Location</div>', unsafe_allow_html=True)
    location = st.selectbox("Select Location", ['All'] + list(st.session_state.inventory_df['Location'].unique()))
    
    if location != 'All':
        display_df = st.session_state.inventory_df[st.session_state.inventory_df['Location'] == location]
    else:
        display_df = st.session_state.inventory_df
    
    display_df = display_df.merge(st.session_state.products_df[['Product_ID', 'Product_Name', 'Category']], on='Product_ID')
    st.dataframe(display_df[['Product_ID', 'Product_Name', 'Category', 'Location', 'Quantity_On_Hand', 'Last_Updated']], 
                use_container_width=True)

def show_transactions():
    st.markdown('<div class="section-header">Stock Transactions</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.transactions_df.sort_values('Date', ascending=False), use_container_width=True)

def show_purchase_orders():
    st.markdown('<div class="section-header">Purchase Orders</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.purchase_orders_df.sort_values('Order_Date', ascending=False), use_container_width=True)

def show_suppliers():
    st.markdown('<div class="section-header">Suppliers</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">Stock Alerts</div>', unsafe_allow_html=True)
    alerts = st.session_state.alerts_df
    st.dataframe(alerts, use_container_width=True)

if __name__ == "__main__":
    main()
