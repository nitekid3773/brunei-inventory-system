import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import numpy as np
import json
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    
    .badge-active {
        background-color: #27ae60;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-inactive {
        background-color: #95a5a6;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Document styling */
    .document-preview {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 8px;
        border: 1px dashed #dee2e6;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.4rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #2980b9;
        color: white;
    }
    
    /* Print styles */
    @media print {
        .no-print {
            display: none;
        }
        .print-only {
            display: block;
        }
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
if 'locations_df' not in st.session_state:
    st.session_state.locations_df = None
if 'documents_df' not in st.session_state:
    st.session_state.documents_df = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'crud_mode' not in st.session_state:
    st.session_state.crud_mode = "view"
if 'editing_product' not in st.session_state:
    st.session_state.editing_product = None
if 'delete_confirmation' not in st.session_state:
    st.session_state.delete_confirmation = {}
if 'show_po_form' not in st.session_state:
    st.session_state.show_po_form = False
if 'selected_product_po' not in st.session_state:
    st.session_state.selected_product_po = None

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data with all required fields"""
    
    # Locations
    locations = [
        {'Location_ID': 'LOC001', 'Location_Name': 'Warehouse A - Beribi', 'Type': 'Warehouse', 'Capacity': 10000, 'Current_Utilization': 7200, 'Manager': 'Ali Rahman'},
        {'Location_ID': 'LOC002', 'Location_Name': 'Store 1 - Gadong', 'Type': 'Retail Store', 'Capacity': 5000, 'Current_Utilization': 3800, 'Manager': 'Siti Aminah'},
        {'Location_ID': 'LOC003', 'Location_Name': 'Store 2 - Kiulap', 'Type': 'Retail Store', 'Capacity': 4500, 'Current_Utilization': 4100, 'Manager': 'John Lee'},
        {'Location_ID': 'LOC004', 'Location_Name': 'Store 3 - Kuala Belait', 'Type': 'Retail Store', 'Capacity': 4000, 'Current_Utilization': 3200, 'Manager': 'Hassan Bakar'},
        {'Location_ID': 'LOC005', 'Location_Name': 'Store 4 - Tutong', 'Type': 'Retail Store', 'Capacity': 3500, 'Current_Utilization': 2800, 'Manager': 'Nurul Huda'},
    ]
    locations_df = pd.DataFrame(locations)
    
    # Suppliers with complete details
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading Sdn Bhd', 'Lim Ah Seng', 'General Manager', '673-2223456', '673-2223457', 'lim.ah.seng@huaho.com.bn', 'purchasing@huaho.com.bn', 'Lot 123, Kg Kiulap, Bandar Seri Begawan', 'BE1118', 'GST Registered', 'Net 30', 'A+', 0.98, 'Electronics, Groceries', '2022-01-15', 'Yes', '50000'],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', 'Procurement Director', '673-2337890', '673-2337891', 'mei.ling@soonlee.com', 'orders@soonlee.com', 'Unit 45, Gadong Central, BSB', 'BE3318', 'GST Registered', 'Net 30', 'A', 0.95, 'Groceries, Household', '2022-03-20', 'Yes', '75000'],
        ['SUP003', 'Supasave Corporation', 'David Wong', 'Supply Chain Manager', '673-2456789', '673-2456780', 'david.wong@supasave.com', 'procurement@supasave.com', 'No. 78, Spg 32, Serusop, BSB', 'BE2218', 'GST Registered', 'Net 45', 'B+', 0.92, 'General Trading', '2022-02-10', 'Yes', '60000'],
        ['SUP004', 'Seng Huat Trading', 'Michael Chen', 'Owner', '673-2771234', '673-2771235', 'michael.chen@senghuat.com', 'sales@senghuat.com', 'Lot 56, Jalan Maulana, Kuala Belait', 'KA1133', 'Non-GST', 'Cash on Delivery', 'A', 0.97, 'Hardware, Tools', '2022-04-05', 'Yes', '35000'],
        ['SUP005', 'SKH Group', 'Steven Khoo', 'Operations Manager', '673-2667890', '673-2667891', 'steven.khoo@skh.com', 'trading@skh.com', 'Unit 12, Bangunan SKH, Tutong', 'TU2211', 'GST Registered', 'Net 30', 'A', 0.96, 'Electronics, Furniture', '2022-01-30', 'Yes', '80000'],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Position', 'Phone_Primary', 'Phone_Secondary', 
        'Email_Primary', 'Email_Secondary', 'Address', 'Postal_Code', 'Tax_Status', 'Payment_Terms', 
        'Supplier_Tier', 'Reliability_Score', 'Product_Categories', 'Since_Date', 'Active', 'Credit_Limit'
    ])
    
    # Product Master List with complete details
    products_data = [
        ['PRD00001', 'ELE-2024-001', '888123456001', 'Samsung 55" 4K LED TV', 'Electronics', 'Consumer Electronics', 'Premium', 785.00, 1135.09, 350.09, 7, 45, 15, 'SUP001', 'Hua Ho Trading Sdn Bhd', 'A3-12-01', 'Aisle 3, Row 12, Bin 1', 18.5, 25.0, '2026-12-31', 'Temperature Controlled', 'Active', '2024-01-15'],
        ['PRD00002', 'ELE-2024-002', '888123456002', 'iPhone 15 Pro 256GB', 'Electronics', 'Consumer Electronics', 'Premium', 916.00, 1351.05, 435.05, 35, 38, 28, 'SUP005', 'SKH Group', 'A3-08-03', 'Aisle 3, Row 8, Bin 3', 6.2, 8.5, '2026-10-31', 'Secure Cabinet', 'Active', '2024-01-20'],
        ['PRD00003', 'ELE-2024-003', '888123456003', 'MacBook Air M2', 'Electronics', 'Consumer Electronics', 'Premium', 618.00, 872.40, 254.40, 25, 22, 42, 'SUP005', 'SKH Group', 'A3-15-02', 'Aisle 3, Row 15, Bin 2', 2.8, 3.2, '2026-09-30', 'Secure Cabinet', 'Active', '2024-01-25'],
        ['PRD00004', 'GRO-2024-001', '888123456004', 'Royal Basmati Rice 5kg', 'Groceries', 'Food & Beverages', 'Staple', 8.00, 9.81, 1.81, 18, 120, 48, 'SUP002', 'Soon Lee MegaMart', 'B2-01-04', 'Aisle 2, Row 1, Bin 4', 5.0, 8.0, '2026-05-31', 'Dry Storage', 'Active', '2024-02-01'],
        ['PRD00005', 'GRO-2024-002', '888123456005', 'Seri Mas Cooking Oil 2L', 'Groceries', 'Food & Beverages', 'Staple', 11.00, 14.28, 3.28, 11, 95, 52, 'SUP002', 'Soon Lee MegaMart', 'B2-04-01', 'Aisle 2, Row 4, Bin 1', 2.0, 2.2, '2026-06-30', 'Dry Storage', 'Active', '2024-02-05'],
        ['PRD00006', 'HAR-2024-001', '888123456006', 'Jotun Paint 5L White', 'Hardware', 'Building Materials', 'Standard', 97.00, 116.66, 19.66, 44, 35, 14, 'SUP004', 'Seng Huat Trading', 'C1-03-02', 'Aisle 1, Row 3, Bin 2', 6.5, 1.2, '2027-01-31', 'Ambient', 'Active', '2024-02-10'],
        ['PRD00007', 'PHA-2024-001', '888123456007', 'Paracetamol 500mg 100s', 'Pharmaceuticals', 'Medicines', 'Essential', 141.00, 189.88, 48.88, 13, 65, 21, 'SUP003', 'Supasave Corporation', 'D2-02-05', 'Aisle 2, Row 2, Bin 5', 0.5, 0.8, '2026-03-31', 'Cool Storage', 'Active', '2024-02-15'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 'Sub_Category', 'Product_Tier',
        'Unit_Cost_BND', 'Selling_Price_BND', 'Profit_Margin_BND', 'Reorder_Level', 
        'Daily_Movement_Units', 'Lead_Time_Days', 'Supplier_ID', 'Supplier_Name', 'Bin_Code', 
        'Bin_Description', 'Weight_kg', 'Volume_cuft', 'Expiry_Date', 'Storage_Requirement', 
        'Status', 'Date_Added'
    ])
    
    # Inventory by Location with detailed tracking
    inventory_data = []
    inventory_counter = 1
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in locations_df.iterrows():
            qty = 50 + ((i + j) * 17) % 150
            min_stock = products.iloc[i]['Reorder_Level'] * 0.5
            max_stock = products.iloc[i]['Reorder_Level'] * 3
            reserved = random.randint(0, 10)
            inventory_data.append({
                'Inventory_ID': f'INV{inventory_counter:06d}',
                'Product_ID': prod,
                'Product_Name': products.iloc[i]['Product_Name'],
                'Location_ID': loc['Location_ID'],
                'Location_Name': loc['Location_Name'],
                'Bin_Code': products.iloc[i]['Bin_Code'],
                'Quantity_On_Hand': qty,
                'Quantity_Reserved': reserved,
                'Quantity_Available': qty - reserved,
                'Minimum_Stock': min_stock,
                'Maximum_Stock': max_stock,
                'Last_Count_Date': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d'),
                'Last_Count_By': random.choice(['Ali', 'Siti', 'John', 'Hassan']),
                'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Updated_By': 'System'
            })
            inventory_counter += 1
    
    inventory = pd.DataFrame(inventory_data)
    
    # Stock Transactions with complete audit trail
    transaction_types = ['STOCK_IN', 'STOCK_OUT', 'ADJUSTMENT', 'TRANSFER', 'RETURN', 'DAMAGE']
    transaction_reasons = {
        'STOCK_IN': ['Purchase Order Received', 'Supplier Return', 'Transfer In', 'Initial Stock'],
        'STOCK_OUT': ['Customer Sale', 'Internal Use', 'Transfer Out', 'Sample'],
        'ADJUSTMENT': ['Physical Count', 'System Correction', 'Quality Control'],
        'TRANSFER': ['Replenishment', 'Stock Redistribution'],
        'RETURN': ['Customer Return', 'Supplier Return'],
        'DAMAGE': ['Damaged Goods', 'Expired', 'Quality Issue']
    }
    users = ['Ali', 'Siti', 'John', 'Hassan', 'Nurul', 'Ahmad', 'Lisa', 'Kevin']
    
    transactions_data = []
    for i in range(200):
        prod = products.sample(1).iloc[0]
        loc = locations_df.sample(1).iloc[0]
        txn_type = random.choice(transaction_types)
        qty = random.randint(1, 50) if txn_type in ['STOCK_IN', 'TRANSFER'] else -random.randint(1, 20)
        user = random.choice(users)
        
        transactions_data.append({
            'Transaction_ID': f'TXN{datetime.now().strftime("%Y%m")}{i:04d}',
            'Date': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d %H:%M:%S'),
            'Transaction_Type': txn_type,
            'Product_ID': prod['Product_ID'],
            'Product_Name': prod['Product_Name'],
            'SKU': prod['SKU'],
            'Quantity': qty,
            'Unit_Cost_BND': prod['Unit_Cost_BND'],
            'Total_Value_BND': abs(qty) * prod['Unit_Cost_BND'],
            'From_Location': loc['Location_ID'] if qty < 0 else None,
            'To_Location': loc['Location_ID'] if qty > 0 else None,
            'Reference_Type': random.choice(['PO', 'SO', 'INV', 'ADJ']),
            'Reference_Number': f'REF{random.randint(10000, 99999)}',
            'Reason': random.choice(transaction_reasons[txn_type]),
            'Performed_By': user,
            'Approved_By': random.choice(['Manager', 'Supervisor', 'System']),
            'Notes': f'Auto-generated transaction for {txn_type}',
            'Document_Attached': random.choice(['Yes', 'No'])
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Purchase Orders with complete documentation
    po_status = ['Draft', 'Pending Approval', 'Approved', 'Sent to Supplier', 'Confirmed', 'Shipped', 'Partially Received', 'Received', 'Cancelled']
    payment_terms = ['Net 30', 'Net 45', 'Cash on Delivery', '50% Advance']
    shipping_methods = ['Sea Freight', 'Air Freight', 'Land Transport', 'Courier']
    
    purchase_orders_data = []
    for i in range(50):
        supplier = suppliers.sample(1).iloc[0]
        product = products.sample(1).iloc[0]
        qty = random.randint(50, 500)
        unit_cost = product['Unit_Cost_BND'] * random.uniform(0.9, 1.1)
        
        po_date = datetime.now() - timedelta(days=random.randint(0, 60))
        expected_date = po_date + timedelta(days=product['Lead_Time_Days'] + random.randint(0, 5))
        
        purchase_orders_data.append({
            'PO_Number': f'PO-{datetime.now().strftime("%Y%m")}-{i:04d}',
            'PO_Date': po_date.strftime('%Y-%m-%d'),
            'Supplier_ID': supplier['Supplier_ID'],
            'Supplier_Name': supplier['Supplier_Name'],
            'Supplier_Address': supplier['Address'],
            'Supplier_Contact': supplier['Contact_Person'],
            'Supplier_Phone': supplier['Phone_Primary'],
            'Supplier_Email': supplier['Email_Primary'],
            'Ship_To_Location': random.choice(locations_df['Location_ID'].tolist()),
            'Payment_Terms': random.choice(payment_terms),
            'Shipping_Method': random.choice(shipping_methods),
            'Expected_Delivery_Date': expected_date.strftime('%Y-%m-%d'),
            'Product_ID': product['Product_ID'],
            'Product_Name': product['Product_Name'],
            'SKU': product['SKU'],
            'Ordered_Quantity': qty,
            'Received_Quantity': random.randint(0, qty),
            'Unit_Cost_BND': round(unit_cost, 2),
            'Subtotal_BND': round(qty * unit_cost, 2),
            'Tax_BND': 0,  # Brunei no GST
            'Shipping_Cost_BND': round(random.uniform(50, 500), 2),
            'Total_Cost_BND': round(qty * unit_cost + random.uniform(50, 500), 2),
            'Currency': 'BND',
            'Order_Status': random.choice(po_status),
            'Payment_Status': random.choice(['Pending', 'Partial', 'Paid']),
            'Created_By': random.choice(['Ali', 'Siti', 'John']),
            'Approved_By': random.choice(['Manager', 'Director']) if random.random() > 0.3 else 'Pending',
            'Approval_Date': (datetime.now() - timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d') if random.random() > 0.3 else None,
            'Notes': f'Purchase order for {product["Product_Name"]}',
            'Terms_Conditions': 'Standard terms apply. Goods once sold are not returnable.'
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Documents registry
    documents_data = []
    for i, po in enumerate(purchase_orders_data[:20]):
        documents_data.append({
            'Document_ID': f'DOC{i:06d}',
            'Document_Type': 'Purchase Order',
            'Reference_Number': po['PO_Number'],
            'Document_Date': po['PO_Date'],
            'Issued_By': po['Created_By'],
            'Issued_To': po['Supplier_Name'],
            'Total_Amount': po['Total_Cost_BND'],
            'Status': 'Active',
            'File_Path': f'/documents/po/{po["PO_Number"]}.pdf'
        })
    
    documents = pd.DataFrame(documents_data) if documents_data else pd.DataFrame()
    
    # Stock Alerts
    current_stock = inventory.groupby('Product_ID').agg({
        'Quantity_On_Hand': 'sum',
        'Quantity_Available': 'sum'
    }).reset_index()
    
    alerts = current_stock.merge(
        products[['Product_ID', 'Product_Name', 'Category', 'Reorder_Level', 'Supplier_Name', 'Lead_Time_Days']], 
        on='Product_ID'
    )
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= 0:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    alerts['Alert_Status'] = alerts.apply(get_alert_status, axis=1)
    alerts['Days_Until_Stockout'] = (alerts['Quantity_On_Hand'] / 10).round(1)
    alerts['Recommended_Order'] = alerts.apply(
        lambda x: int(x['Reorder_Level'] * 2 - x['Quantity_On_Hand']) if x['Alert_Status'] != 'NORMAL' else 0, 
        axis=1
    )
    
    return products, inventory, transactions, suppliers, purchase_orders, alerts, locations_df, documents

# Initialize data
if st.session_state.products_df is None:
    (st.session_state.products_df, 
     st.session_state.inventory_df, 
     st.session_state.transactions_df, 
     st.session_state.suppliers_df, 
     st.session_state.purchase_orders_df, 
     st.session_state.alerts_df,
     st.session_state.locations_df,
     st.session_state.documents_df) = load_initial_data()

# ============================================
# HTML DOCUMENT GENERATION (No external dependencies)
# ============================================

def generate_purchase_order_html(po_data):
    """Generate HTML for purchase order"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Purchase Order {po_data['PO_Number']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #1e3c72; margin-bottom: 5px; }}
            .header h3 {{ color: #666; margin-top: 0; }}
            .company-info {{ margin-bottom: 30px; }}
            .po-details {{ margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th {{ background-color: #1e3c72; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .totals {{ float: right; width: 300px; }}
            .totals table {{ width: 100%; }}
            .totals td {{ padding: 5px; border: none; }}
            .totals .total-row {{ font-weight: bold; border-top: 2px solid #000; }}
            .footer {{ margin-top: 50px; }}
            .signature {{ margin-top: 50px; }}
            .signature-line {{ width: 200px; border-bottom: 1px solid #000; margin-top: 30px; }}
            .terms {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PURCHASE ORDER</h1>
            <h3>{po_data['PO_Number']}</h3>
        </div>
        
        <div class="company-info">
            <table>
                <tr>
                    <td><strong>Your Company Name</strong><br>
                    Address Line 1<br>
                    Bandar Seri Begawan, Brunei<br>
                    Tel: +673 123 4567 | Email: purchases@company.com</td>
                    <td><strong>Date:</strong> {po_data['PO_Date']}<br>
                    <strong>Payment Terms:</strong> {po_data['Payment_Terms']}<br>
                    <strong>Shipping Method:</strong> {po_data['Shipping_Method']}<br>
                    <strong>Expected Delivery:</strong> {po_data['Expected_Delivery_Date']}</td>
                </tr>
            </table>
        </div>
        
        <div class="po-details">
            <table>
                <tr>
                    <th colspan="2">Supplier Information</th>
                </tr>
                <tr>
                    <td><strong>Supplier:</strong> {po_data['Supplier_Name']}</td>
                    <td><strong>Contact:</strong> {po_data['Supplier_Contact']}</td>
                </tr>
                <tr>
                    <td><strong>Address:</strong> {po_data['Supplier_Address']}</td>
                    <td><strong>Phone:</strong> {po_data['Supplier_Phone']}</td>
                </tr>
                <tr>
                    <td><strong>Email:</strong> {po_data['Supplier_Email']}</td>
                    <td><strong>Ship To:</strong> {po_data['Ship_To_Location']}</td>
                </tr>
            </table>
        </div>
        
        <table>
            <tr>
                <th>Item</th>
                <th>SKU</th>
                <th>Quantity</th>
                <th>Unit Price (BND)</th>
                <th>Total (BND)</th>
            </tr>
            <tr>
                <td>{po_data['Product_Name']}</td>
                <td>{po_data['SKU']}</td>
                <td>{po_data['Ordered_Quantity']}</td>
                <td>B${po_data['Unit_Cost_BND']:.2f}</td>
                <td>B${po_data['Subtotal_BND']:.2f}</td>
            </tr>
        </table>
        
        <div class="totals">
            <table>
                <tr>
                    <td>Subtotal:</td>
                    <td align="right">B${po_data['Subtotal_BND']:.2f}</td>
                </tr>
                <tr>
                    <td>Shipping:</td>
                    <td align="right">B${po_data['Shipping_Cost_BND']:.2f}</td>
                </tr>
                <tr>
                    <td>Tax (0%):</td>
                    <td align="right">B$0.00</td>
                </tr>
                <tr class="total-row">
                    <td><strong>TOTAL:</strong></td>
                    <td align="right"><strong>B${po_data['Total_Cost_BND']:.2f}</strong></td>
                </tr>
            </table>
        </div>
        
        <div style="clear: both;"></div>
        
        <div class="terms">
            <h4>Terms and Conditions:</h4>
            <p>{po_data['Terms_Conditions']}</p>
            <ol>
                <li>Goods must be delivered by the expected delivery date.</li>
                <li>Invoice must reference this PO number.</li>
                <li>All goods subject to inspection upon receipt.</li>
                <li>Payment terms as agreed above.</li>
            </ol>
        </div>
        
        <div class="signature">
            <table style="width: 100%; margin-top: 50px;">
                <tr>
                    <td style="text-align: center;">
                        <div class="signature-line"></div>
                        <p>Authorized Signature</p>
                    </td>
                    <td style="text-align: center;">
                        <div class="signature-line"></div>
                        <p>Date</p>
                    </td>
                </tr>
            </table>
        </div>
        
        <div class="footer">
            <p style="text-align: center; font-size: 11px; color: #999;">This is a computer generated document. No signature required.</p>
        </div>
    </body>
    </html>
    """
    return html

def get_html_download_link(html_content, filename):
    """Generate download link for HTML file"""
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" class="btn btn-primary" style="background-color: #27ae60; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">📥 Download {filename}</a>'
    return href

def get_txt_download_link(text_content, filename):
    """Generate download link for text file"""
    b64 = base64.b64encode(text_content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="btn btn-primary" style="background-color: #3498db; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">📥 Download {filename}</a>'
    return href

# ============================================
# ENHANCED CRUD FUNCTIONS
# ============================================

def generate_product_id():
    existing_ids = st.session_state.products_df['Product_ID'].tolist()
    numbers = [int(id.replace('PRD', '')) for id in existing_ids]
    next_num = max(numbers) + 1
    return f"PRD{next_num:05d}"

def generate_sku(category):
    year = datetime.now().strftime('%Y')
    prefix = category[:3].upper()
    return f"{prefix}-{year}-{random.randint(100, 999)}"

def generate_barcode():
    return f"888{random.randint(1000000, 9999999)}"

def validate_product_data(data):
    errors = []
    if not data.get('Product_Name'):
        errors.append("Product Name is required")
    if data.get('Unit_Cost_BND', 0) <= 0:
        errors.append("Unit Cost must be greater than 0")
    if data.get('Selling_Price_BND', 0) <= 0:
        errors.append("Selling Price must be greater than 0")
    if data.get('Selling_Price_BND', 0) <= data.get('Unit_Cost_BND', 0):
        errors.append("Selling Price must be greater than Unit Cost")
    if not data.get('Supplier_ID'):
        errors.append("Supplier is required")
    if not data.get('Bin_Code'):
        errors.append("Bin Location is required")
    return errors

def add_product(product_data):
    errors = validate_product_data(product_data)
    if errors:
        return False, errors
    
    # Generate IDs
    product_data['Product_ID'] = generate_product_id()
    if not product_data.get('SKU'):
        product_data['SKU'] = generate_sku(product_data['Category'])
    if not product_data.get('Barcode'):
        product_data['Barcode'] = generate_barcode()
    product_data['Date_Added'] = datetime.now().strftime('%Y-%m-%d')
    product_data['Status'] = 'Active'
    product_data['Profit_Margin_BND'] = product_data['Selling_Price_BND'] - product_data['Unit_Cost_BND']
    
    # Add to products dataframe
    st.session_state.products_df = pd.concat(
        [st.session_state.products_df, pd.DataFrame([product_data])], 
        ignore_index=True
    )
    
    # Add initial inventory for all locations
    for _, loc in st.session_state.locations_df.iterrows():
        new_inv = {
            'Inventory_ID': f'INV{len(st.session_state.inventory_df)+1:06d}',
            'Product_ID': product_data['Product_ID'],
            'Product_Name': product_data['Product_Name'],
            'Location_ID': loc['Location_ID'],
            'Location_Name': loc['Location_Name'],
            'Bin_Code': product_data['Bin_Code'],
            'Quantity_On_Hand': 0,
            'Quantity_Reserved': 0,
            'Quantity_Available': 0,
            'Minimum_Stock': product_data['Reorder_Level'] * 0.5,
            'Maximum_Stock': product_data['Reorder_Level'] * 3,
            'Last_Count_Date': datetime.now().strftime('%Y-%m-%d'),
            'Last_Count_By': 'System',
            'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Updated_By': 'System'
        }
        st.session_state.inventory_df = pd.concat(
            [st.session_state.inventory_df, pd.DataFrame([new_inv])], 
            ignore_index=True
        )
    
    # Create transaction record
    transaction = {
        'Transaction_ID': f'TXN{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Transaction_Type': 'STOCK_IN',
        'Product_ID': product_data['Product_ID'],
        'Product_Name': product_data['Product_Name'],
        'SKU': product_data['SKU'],
        'Quantity': 0,
        'Unit_Cost_BND': product_data['Unit_Cost_BND'],
        'Total_Value_BND': 0,
        'From_Location': None,
        'To_Location': None,
        'Reference_Type': 'NEW',
        'Reference_Number': 'INITIAL',
        'Reason': 'New product added to system',
        'Performed_By': 'Admin',
        'Approved_By': 'System',
        'Notes': f'Product {product_data["Product_Name"]} added to inventory',
        'Document_Attached': 'No'
    }
    st.session_state.transactions_df = pd.concat(
        [st.session_state.transactions_df, pd.DataFrame([transaction])], 
        ignore_index=True
    )
    
    st.session_state.last_update = datetime.now()
    return True, product_data['Product_ID']

def update_product(product_id, updated_data):
    errors = validate_product_data(updated_data)
    if errors:
        return False, errors
    
    mask = st.session_state.products_df['Product_ID'] == product_id
    old_product = st.session_state.products_df[mask].iloc[0].to_dict()
    
    # Update fields
    for key, value in updated_data.items():
        if value is not None and key in st.session_state.products_df.columns:
            st.session_state.products_df.loc[mask, key] = value
    
    # Update profit margin
    st.session_state.products_df.loc[mask, 'Profit_Margin_BND'] = (
        st.session_state.products_df.loc[mask, 'Selling_Price_BND'].values[0] - 
        st.session_state.products_df.loc[mask, 'Unit_Cost_BND'].values[0]
    )
    
    # Update inventory with new product name
    st.session_state.inventory_df.loc[
        st.session_state.inventory_df['Product_ID'] == product_id, 'Product_Name'
    ] = st.session_state.products_df.loc[mask, 'Product_Name'].values[0]
    
    # Create transaction record for update
    transaction = {
        'Transaction_ID': f'TXN{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Transaction_Type': 'ADJUSTMENT',
        'Product_ID': product_id,
        'Product_Name': st.session_state.products_df.loc[mask, 'Product_Name'].values[0],
        'SKU': st.session_state.products_df.loc[mask, 'SKU'].values[0],
        'Quantity': 0,
        'Unit_Cost_BND': st.session_state.products_df.loc[mask, 'Unit_Cost_BND'].values[0],
        'Total_Value_BND': 0,
        'From_Location': None,
        'To_Location': None,
        'Reference_Type': 'UPDATE',
        'Reference_Number': 'PRODUCT_UPDATE',
        'Reason': 'Product details updated',
        'Performed_By': 'Admin',
        'Approved_By': 'System',
        'Notes': f'Product updated: {json.dumps(updated_data)}',
        'Document_Attached': 'No'
    }
    st.session_state.transactions_df = pd.concat(
        [st.session_state.transactions_df, pd.DataFrame([transaction])], 
        ignore_index=True
    )
    
    st.session_state.last_update = datetime.now()
    return True, None

def delete_product(product_id):
    product = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] == product_id
    ].iloc[0]
    product_name = product['Product_Name']
    
    # Create deletion record
    transaction = {
        'Transaction_ID': f'TXN{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Transaction_Type': 'ADJUSTMENT',
        'Product_ID': product_id,
        'Product_Name': product_name,
        'SKU': product['SKU'],
        'Quantity': 0,
        'Unit_Cost_BND': product['Unit_Cost_BND'],
        'Total_Value_BND': 0,
        'From_Location': None,
        'To_Location': None,
        'Reference_Type': 'DELETE',
        'Reference_Number': 'PRODUCT_DELETE',
        'Reason': 'Product removed from system',
        'Performed_By': 'Admin',
        'Approved_By': 'System',
        'Notes': f'Product {product_name} deleted',
        'Document_Attached': 'No'
    }
    st.session_state.transactions_df = pd.concat(
        [st.session_state.transactions_df, pd.DataFrame([transaction])], 
        ignore_index=True
    )
    
    # Remove from products
    st.session_state.products_df = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] != product_id
    ]
    
    # Remove from inventory
    st.session_state.inventory_df = st.session_state.inventory_df[
        st.session_state.inventory_df['Product_ID'] != product_id
    ]
    
    st.session_state.last_update = datetime.now()
    return product_name

def create_purchase_order(po_data):
    """Create new purchase order with documentation"""
    po_number = f'PO-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}'
    
    po_record = {
        'PO_Number': po_number,
        'PO_Date': datetime.now().strftime('%Y-%m-%d'),
        'Supplier_ID': po_data['Supplier_ID'],
        'Supplier_Name': po_data['Supplier_Name'],
        'Supplier_Address': po_data['Supplier_Address'],
        'Supplier_Contact': po_data['Supplier_Contact'],
        'Supplier_Phone': po_data['Supplier_Phone'],
        'Supplier_Email': po_data['Supplier_Email'],
        'Ship_To_Location': po_data['Ship_To_Location'],
        'Payment_Terms': po_data['Payment_Terms'],
        'Shipping_Method': po_data['Shipping_Method'],
        'Expected_Delivery_Date': po_data['Expected_Delivery_Date'],
        'Product_ID': po_data['Product_ID'],
        'Product_Name': po_data['Product_Name'],
        'SKU': po_data['SKU'],
        'Ordered_Quantity': po_data['Ordered_Quantity'],
        'Received_Quantity': 0,
        'Unit_Cost_BND': po_data['Unit_Cost_BND'],
        'Subtotal_BND': po_data['Ordered_Quantity'] * po_data['Unit_Cost_BND'],
        'Tax_BND': 0,
        'Shipping_Cost_BND': po_data['Shipping_Cost_BND'],
        'Total_Cost_BND': po_data['Ordered_Quantity'] * po_data['Unit_Cost_BND'] + po_data['Shipping_Cost_BND'],
        'Currency': 'BND',
        'Order_Status': 'Draft',
        'Payment_Status': 'Pending',
        'Created_By': 'Admin',
        'Approved_By': 'Pending',
        'Approval_Date': None,
        'Notes': po_data['Notes'],
        'Terms_Conditions': 'Standard terms apply. Goods once sold are not returnable.'
    }
    
    st.session_state.purchase_orders_df = pd.concat(
        [st.session_state.purchase_orders_df, pd.DataFrame([po_record])], 
        ignore_index=True
    )
    
    # Create document record
    doc_record = {
        'Document_ID': f'DOC{len(st.session_state.documents_df)+1:06d}' if st.session_state.documents_df is not None and len(st.session_state.documents_df) > 0 else 'DOC000001',
        'Document_Type': 'Purchase Order',
        'Reference_Number': po_number,
        'Document_Date': datetime.now().strftime('%Y-%m-%d'),
        'Issued_By': 'Admin',
        'Issued_To': po_data['Supplier_Name'],
        'Total_Amount': po_record['Total_Cost_BND'],
        'Status': 'Draft',
        'File_Path': f'/documents/po/{po_number}.html'
    }
    
    if st.session_state.documents_df is None or len(st.session_state.documents_df) == 0:
        st.session_state.documents_df = pd.DataFrame([doc_record])
    else:
        st.session_state.documents_df = pd.concat(
            [st.session_state.documents_df, pd.DataFrame([doc_record])], 
            ignore_index=True
        )
    
    return po_record

def adjust_inventory(product_id, location_id, quantity, reason):
    """Adjust inventory quantity with documentation"""
    mask = (st.session_state.inventory_df['Product_ID'] == product_id) & \
           (st.session_state.inventory_df['Location_ID'] == location_id)
    
    old_qty = st.session_state.inventory_df.loc[mask, 'Quantity_On_Hand'].values[0]
    new_qty = old_qty + quantity
    
    st.session_state.inventory_df.loc[mask, 'Quantity_On_Hand'] = new_qty
    st.session_state.inventory_df.loc[mask, 'Quantity_Available'] = new_qty - \
        st.session_state.inventory_df.loc[mask, 'Quantity_Reserved'].values[0]
    st.session_state.inventory_df.loc[mask, 'Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.inventory_df.loc[mask, 'Updated_By'] = 'Admin'
    
    # Create transaction record
    product = st.session_state.products_df[st.session_state.products_df['Product_ID'] == product_id].iloc[0]
    location = st.session_state.locations_df[st.session_state.locations_df['Location_ID'] == location_id].iloc[0]
    
    transaction = {
        'Transaction_ID': f'TXN{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Transaction_Type': 'ADJUSTMENT',
        'Product_ID': product_id,
        'Product_Name': product['Product_Name'],
        'SKU': product['SKU'],
        'Quantity': quantity,
        'Unit_Cost_BND': product['Unit_Cost_BND'],
        'Total_Value_BND': abs(quantity) * product['Unit_Cost_BND'],
        'From_Location': location_id if quantity < 0 else None,
        'To_Location': location_id if quantity > 0 else None,
        'Reference_Type': 'ADJ',
        'Reference_Number': f'ADJ{random.randint(10000, 99999)}',
        'Reason': reason,
        'Performed_By': 'Admin',
        'Approved_By': 'System',
        'Notes': f'Inventory adjusted from {old_qty} to {new_qty}',
        'Document_Attached': 'No'
    }
    st.session_state.transactions_df = pd.concat(
        [st.session_state.transactions_df, pd.DataFrame([transaction])], 
        ignore_index=True
    )
    
    return new_qty

# ============================================
# ENHANCED CRUD DASHBOARD
# ============================================

def show_product_crud():
    st.markdown('<div class="section-header">📦 Complete Product Management</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Products", len(st.session_state.products_df))
    with col2:
        active = len(st.session_state.products_df[st.session_state.products_df['Status'] == 'Active'])
        st.metric("Active", active)
    with col3:
        categories = st.session_state.products_df['Category'].nunique()
        st.metric("Categories", categories)
    with col4:
        suppliers = st.session_state.suppliers_df['Supplier_Name'].nunique()
        st.metric("Suppliers", suppliers)
    with col5:
        total_value = (st.session_state.inventory_df['Quantity_On_Hand'].sum() * 
                      st.session_state.products_df['Unit_Cost_BND'].mean())
        st.metric("Inventory Value", f"B${total_value:,.0f}")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 5])
    with col1:
        if st.button("➕ Add Product", use_container_width=True):
            st.session_state.crud_mode = "add"
            st.session_state.editing_product = None
            st.rerun()
    with col2:
        if st.button("📦 Create PO", use_container_width=True):
            st.session_state.show_po_form = True
            st.rerun()
    with col3:
        if st.button("🔄 Adjust Stock", use_container_width=True):
            st.session_state.crud_mode = "adjust"
            st.rerun()
    
    st.markdown("---")
    
    # Add Product Form
    if st.session_state.crud_mode == "add":
        with st.form("add_product_form", clear_on_submit=True):
            st.subheader("➕ Add New Product")
            
            # Basic Information
            st.markdown("**Basic Information**")
            col1, col2, col3 = st.columns(3)
            with col1:
                product_name = st.text_input("Product Name *", help="Full product name")
                category = st.selectbox("Category *", 
                    ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                     'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                     'Beverages', 'Cosmetics'])
            with col2:
                sub_category = st.text_input("Sub Category", help="e.g., Consumer Electronics")
                product_tier = st.selectbox("Product Tier", ['Premium', 'Standard', 'Economy', 'Staple'])
            with col3:
                storage_req = st.text_input("Storage Requirement", help="e.g., Temperature Controlled")
            
            # Pricing Information (BND)
            st.markdown("**Pricing Information (BND)**")
            col1, col2, col3 = st.columns(3)
            with col1:
                unit_cost = st.number_input("Unit Cost *", min_value=0.01, value=100.00, step=10.00, format="%.2f")
            with col2:
                selling_price = st.number_input("Selling Price *", min_value=0.01, value=150.00, step=10.00, format="%.2f")
            with col3:
                profit_margin = selling_price - unit_cost
                st.metric("Profit Margin", f"B${profit_margin:.2f}")
            
            # Inventory Settings
            st.markdown("**Inventory Settings**")
            col1, col2, col3 = st.columns(3)
            with col1:
                reorder_level = st.number_input("Reorder Level", min_value=1, value=10)
                daily_movement = st.number_input("Daily Movement (units)", min_value=0, value=10)
            with col2:
                lead_time = st.number_input("Lead Time (days)", min_value=1, value=7)
                weight = st.number_input("Weight (kg)", min_value=0.1, value=1.0, step=0.1)
            with col3:
                volume = st.number_input("Volume (cu ft)", min_value=0.1, value=1.0, step=0.1)
                expiry = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=365))
            
            # Supplier Information
            st.markdown("**Supplier Information**")
            col1, col2 = st.columns(2)
            with col1:
                supplier_options = st.session_state.suppliers_df['Supplier_Name'].tolist()
                selected_supplier = st.selectbox("Preferred Supplier *", supplier_options)
                supplier_id = st.session_state.suppliers_df[
                    st.session_state.suppliers_df['Supplier_Name'] == selected_supplier
                ]['Supplier_ID'].values[0] if len(st.session_state.suppliers_df[
                    st.session_state.suppliers_df['Supplier_Name'] == selected_supplier
                ]) > 0 else 'SUP001'
            
            # Location Information
            st.markdown("**Location Information**")
            col1, col2 = st.columns(2)
            with col1:
                bin_code = st.text_input("Bin Code *", help="e.g., A3-12-01")
                bin_desc = st.text_input("Bin Description", help="e.g., Aisle 3, Row 12, Bin 1")
            
            # Submit buttons
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                submitted = st.form_submit_button("💾 Save Product", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submitted:
                if not product_name:
                    st.error("❌ Product Name is required!")
                elif selling_price <= unit_cost:
                    st.error("❌ Selling Price must be greater than Unit Cost!")
                else:
                    product_data = {
                        'SKU': generate_sku(category),
                        'Barcode': generate_barcode(),
                        'Product_Name': product_name,
                        'Category': category,
                        'Sub_Category': sub_category,
                        'Product_Tier': product_tier,
                        'Unit_Cost_BND': unit_cost,
                        'Selling_Price_BND': selling_price,
                        'Reorder_Level': reorder_level,
                        'Daily_Movement_Units': daily_movement,
                        'Lead_Time_Days': lead_time,
                        'Supplier_ID': supplier_id,
                        'Supplier_Name': selected_supplier,
                        'Bin_Code': bin_code,
                        'Bin_Description': bin_desc,
                        'Weight_kg': weight,
                        'Volume_cuft': volume,
                        'Expiry_Date': expiry.strftime('%Y-%m-%d'),
                        'Storage_Requirement': storage_req,
                        'Image_URL': ''
                    }
                    
                    success, result = add_product(product_data)
                    
                    if success:
                        st.success(f"✅ Product added successfully! ID: {result}")
                        st.balloons()
                        time.sleep(2)
                        st.session_state.crud_mode = "view"
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {', '.join(result)}")
            
            if cancelled:
                st.session_state.crud_mode = "view"
                st.rerun()
    
    # Adjust Stock Form
    elif st.session_state.crud_mode == "adjust":
        with st.form("adjust_stock_form"):
            st.subheader("🔄 Adjust Inventory")
            
            col1, col2 = st.columns(2)
            with col1:
                product_options = st.session_state.products_df['Product_Name'].tolist()
                product = st.selectbox("Select Product", product_options)
                product_id = st.session_state.products_df[
                    st.session_state.products_df['Product_Name'] == product
                ]['Product_ID'].values[0] if len(st.session_state.products_df[
                    st.session_state.products_df['Product_Name'] == product
                ]) > 0 else None
            
            with col2:
                location_options = st.session_state.locations_df['Location_Name'].tolist()
                location = st.selectbox("Select Location", location_options)
                location_id = st.session_state.locations_df[
                    st.session_state.locations_df['Location_Name'] == location
                ]['Location_ID'].values[0] if len(st.session_state.locations_df[
                    st.session_state.locations_df['Location_Name'] == location
                ]) > 0 else None
            
            if product_id and location_id:
                current_qty = st.session_state.inventory_df[
                    (st.session_state.inventory_df['Product_ID'] == product_id) &
                    (st.session_state.inventory_df['Location_ID'] == location_id)
                ]['Quantity_On_Hand'].values[0]
                
                st.info(f"Current quantity: **{current_qty} units**")
                
                col1, col2 = st.columns(2)
                with col1:
                    adjustment = st.number_input("Adjustment Quantity", value=0, step=1,
                        help="Positive to add, negative to remove")
                with col2:
                    reason = st.selectbox("Reason", 
                        ['Physical Count', 'Damage', 'Expired', 'Quality Control', 'System Correction'])
                
                notes = st.text_area("Notes", placeholder="Additional details...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Apply Adjustment"):
                        new_qty = adjust_inventory(product_id, location_id, adjustment, reason)
                        st.success(f"✅ Inventory adjusted! New quantity: {new_qty}")
                        time.sleep(2)
                        st.session_state.crud_mode = "view"
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.crud_mode = "view"
                        st.rerun()
            else:
                st.warning("Please select both product and location")
    
    # Create Purchase Order Form
    elif st.session_state.show_po_form:
        with st.form("create_po_form"):
            st.subheader("📦 Create Purchase Order")
            
            col1, col2 = st.columns(2)
            with col1:
                supplier_options = st.session_state.suppliers_df['Supplier_Name'].tolist()
                supplier = st.selectbox("Select Supplier", supplier_options)
                supplier_data = st.session_state.suppliers_df[
                    st.session_state.suppliers_df['Supplier_Name'] == supplier
                ].iloc[0] if len(st.session_state.suppliers_df[
                    st.session_state.suppliers_df['Supplier_Name'] == supplier
                ]) > 0 else None
            
            with col2:
                product_options = st.session_state.products_df['Product_Name'].tolist()
                if st.session_state.selected_product_po:
                    default_index = product_options.index(
                        st.session_state.products_df[
                            st.session_state.products_df['Product_ID'] == st.session_state.selected_product_po
                        ]['Product_Name'].values[0]
                    ) if st.session_state.selected_product_po in st.session_state.products_df['Product_ID'].values else 0
                else:
                    default_index = 0
                
                product = st.selectbox("Select Product", product_options, index=default_index)
                product_data = st.session_state.products_df[
                    st.session_state.products_df['Product_Name'] == product
                ].iloc[0] if len(st.session_state.products_df[
                    st.session_state.products_df['Product_Name'] == product
                ]) > 0 else None
            
            if supplier_data is not None and product_data is not None:
                col1, col2, col3 = st.columns(3)
                with col1:
                    quantity = st.number_input("Order Quantity", min_value=1, value=100)
                with col2:
                    unit_price = st.number_input("Unit Price (BND)", 
                        value=float(product_data['Unit_Cost_BND']), step=10.00)
                with col3:
                    shipping = st.number_input("Shipping Cost (BND)", min_value=0.0, value=100.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    payment_terms = st.selectbox("Payment Terms", 
                        ['Net 30', 'Net 45', 'Cash on Delivery', '50% Advance'])
                    shipping_method = st.selectbox("Shipping Method", 
                        ['Sea Freight', 'Air Freight', 'Land Transport', 'Courier'])
                with col2:
                    location_options = st.session_state.locations_df['Location_Name'].tolist()
                    location = st.selectbox("Ship To", location_options)
                    location_id = st.session_state.locations_df[
                        st.session_state.locations_df['Location_Name'] == location
                    ]['Location_ID'].values[0] if len(st.session_state.locations_df[
                        st.session_state.locations_df['Location_Name'] == location
                    ]) > 0 else 'LOC001'
                    expected_date = st.date_input("Expected Delivery", 
                        value=datetime.now() + timedelta(days=product_data['Lead_Time_Days']))
                
                notes = st.text_area("Notes", placeholder="Additional instructions for supplier...")
                
                # Preview
                st.markdown("### Order Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    subtotal = quantity * unit_price
                    st.metric("Subtotal", f"B${subtotal:,.2f}")
                with col2:
                    st.metric("Shipping", f"B${shipping:,.2f}")
                with col3:
                    total = subtotal + shipping
                    st.metric("Total", f"B${total:,.2f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ Create Purchase Order"):
                        po_data = {
                            'Supplier_ID': supplier_data['Supplier_ID'],
                            'Supplier_Name': supplier_data['Supplier_Name'],
                            'Supplier_Address': supplier_data['Address'],
                            'Supplier_Contact': supplier_data['Contact_Person'],
                            'Supplier_Phone': supplier_data['Phone_Primary'],
                            'Supplier_Email': supplier_data['Email_Primary'],
                            'Ship_To_Location': location_id,
                            'Payment_Terms': payment_terms,
                            'Shipping_Method': shipping_method,
                            'Expected_Delivery_Date': expected_date.strftime('%Y-%m-%d'),
                            'Product_ID': product_data['Product_ID'],
                            'Product_Name': product_data['Product_Name'],
                            'SKU': product_data['SKU'],
                            'Ordered_Quantity': quantity,
                            'Unit_Cost_BND': unit_price,
                            'Shipping_Cost_BND': shipping,
                            'Notes': notes
                        }
                        
                        po = create_purchase_order(po_data)
                        st.success(f"✅ Purchase Order {po['PO_Number']} created!")
                        
                        # Generate HTML document
                        html_content = generate_purchase_order_html(po)
                        st.markdown(get_html_download_link(html_content, f"{po['PO_Number']}.html"), unsafe_allow_html=True)
                        
                        time.sleep(3)
                        st.session_state.show_po_form = False
                        st.session_state.selected_product_po = None
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_po_form = False
                        st.session_state.selected_product_po = None
                        st.rerun()
            else:
                st.warning("Please select both supplier and product")
    
    # Product List View
    else:
        st.subheader("Product List")
        
        # Search and filters
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("🔍 Search by name, ID, or SKU")
        with col2:
            category_filter = st.multiselect("Category", 
                st.session_state.products_df['Category'].unique())
        with col3:
            supplier_filter = st.multiselect("Supplier", 
                st.session_state.products_df['Supplier_Name'].unique())
        
        # Apply filters
        filtered_df = st.session_state.products_df.copy()
        if search:
            filtered_df = filtered_df[
                filtered_df['Product_Name'].str.contains(search, case=False) |
                filtered_df['Product_ID'].str.contains(search, case=False) |
                filtered_df['SKU'].str.contains(search, case=False)
            ]
        if category_filter:
            filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
        if supplier_filter:
            filtered_df = filtered_df[filtered_df['Supplier_Name'].isin(supplier_filter)]
        
        st.info(f"Showing {len(filtered_df)} of {len(st.session_state.products_df)} products")
        
        # Display products
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📦 {row['Product_Name']} ({row['Product_ID']})"):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**Basic Info**")
                    st.write(f"SKU: {row['SKU']}")
                    st.write(f"Barcode: {row['Barcode']}")
                    st.write(f"Category: {row['Category']}")
                    st.write(f"Tier: {row['Product_Tier']}")
                
                with col2:
                    st.markdown(f"**Pricing (BND)**")
                    st.write(f"Cost: B${row['Unit_Cost_BND']:.2f}")
                    st.write(f"Selling: B${row['Selling_Price_BND']:.2f}")
                    st.write(f"Margin: B${row['Profit_Margin_BND']:.2f}")
                    st.write(f"Reorder Level: {row['Reorder_Level']}")
                
                with col3:
                    st.markdown(f"**Location**")
                    st.write(f"Bin: {row['Bin_Code']}")
                    st.write(f"Description: {row['Bin_Description']}")
                    st.write(f"Supplier: {row['Supplier_Name']}")
                    st.write(f"Lead Time: {row['Lead_Time_Days']} days")
                
                with col4:
                    status_class = "badge-active" if row['Status'] == 'Active' else "badge-inactive"
                    st.markdown(f"<span class='{status_class}'>{row['Status']}</span>", unsafe_allow_html=True)
                    
                    if st.button("✏️ Edit", key=f"edit_{row['Product_ID']}", use_container_width=True):
                        st.session_state.crud_mode = "edit"
                        st.session_state.editing_product = row['Product_ID']
                        st.rerun()
                    
                    if st.button("📦 Create PO", key=f"po_{row['Product_ID']}", use_container_width=True):
                        st.session_state.selected_product_po = row['Product_ID']
                        st.session_state.show_po_form = True
                        st.rerun()
                    
                    delete_key = f"del_{row['Product_ID']}"
                    if delete_key not in st.session_state.delete_confirmation:
                        st.session_state.delete_confirmation[delete_key] = False
                    
                    if not st.session_state.delete_confirmation[delete_key]:
                        if st.button("🗑️ Delete", key=delete_key, use_container_width=True):
                            st.session_state.delete_confirmation[delete_key] = True
                            st.rerun()
                    else:
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            if st.button("✓ Yes", key=f"conf_{row['Product_ID']}", use_container_width=True):
                                deleted = delete_product(row['Product_ID'])
                                st.session_state.delete_confirmation[delete_key] = False
                                st.success(f"✅ {deleted} deleted!")
                                time.sleep(1)
                                st.rerun()
                        with col_d2:
                            if st.button("✗ No", key=f"can_{row['Product_ID']}", use_container_width=True):
                                st.session_state.delete_confirmation[delete_key] = False
                                st.rerun()
                
                # Current stock levels
                stock_data = st.session_state.inventory_df[
                    st.session_state.inventory_df['Product_ID'] == row['Product_ID']
                ][['Location_Name', 'Quantity_On_Hand', 'Quantity_Available']]
                st.dataframe(stock_data, use_container_width=True)

# ============================================
# OTHER PAGES
# ============================================

def show_purchase_orders():
    st.markdown('<div class="section-header">📋 Purchase Orders</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect("Filter by Status", 
            st.session_state.purchase_orders_df['Order_Status'].unique())
    with col2:
        supplier_filter = st.multiselect("Filter by Supplier", 
            st.session_state.purchase_orders_df['Supplier_Name'].unique())
    
    filtered_df = st.session_state.purchase_orders_df
    if status_filter:
        filtered_df = filtered_df[filtered_df['Order_Status'].isin(status_filter)]
    if supplier_filter:
        filtered_df = filtered_df[filtered_df['Supplier_Name'].isin(supplier_filter)]
    
    # Display POs
    for _, po in filtered_df.sort_values('PO_Date', ascending=False).iterrows():
        with st.expander(f"📄 {po['PO_Number']} - {po['Supplier_Name']} - {po['Order_Status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**PO Details**")
                st.write(f"Date: {po['PO_Date']}")
                st.write(f"Expected Delivery: {po['Expected_Delivery_Date']}")
                st.write(f"Payment Terms: {po['Payment_Terms']}")
                st.write(f"Shipping Method: {po['Shipping_Method']}")
            
            with col2:
                st.markdown(f"**Supplier Info**")
                st.write(f"Contact: {po['Supplier_Contact']}")
                st.write(f"Phone: {po['Supplier_Phone']}")
                st.write(f"Email: {po['Supplier_Email']}")
            
            st.markdown(f"**Items**")
            st.write(f"Product: {po['Product_Name']} (SKU: {po['SKU']})")
            st.write(f"Quantity: {po['Ordered_Quantity']} units @ B${po['Unit_Cost_BND']:.2f}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Subtotal", f"B${po['Subtotal_BND']:,.2f}")
            with col2:
                st.metric("Shipping", f"B${po['Shipping_Cost_BND']:,.2f}")
            with col3:
                st.metric("Total", f"B${po['Total_Cost_BND']:,.2f}")
            
            if po['Order_Status'] == 'Draft':
                if st.button(f"✅ Approve PO", key=f"approve_{po['PO_Number']}"):
                    st.session_state.purchase_orders_df.loc[
                        st.session_state.purchase_orders_df['PO_Number'] == po['PO_Number'], 'Order_Status'
                    ] = 'Approved'
                    st.success("PO Approved!")
                    st.rerun()
            
            # Generate HTML document
            html_content = generate_purchase_order_html(po.to_dict())
            st.markdown(get_html_download_link(html_content, f"{po['PO_Number']}.html"), unsafe_allow_html=True)

def show_suppliers():
    st.markdown('<div class="section-header">🏢 Supplier Directory</div>', unsafe_allow_html=True)
    
    for _, supplier in st.session_state.suppliers_df.iterrows():
        with st.expander(f"🏢 {supplier['Supplier_Name']} (Tier {supplier['Supplier_Tier']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Contact Information**")
                st.write(f"Contact: {supplier['Contact_Person']}")
                st.write(f"Position: {supplier['Position']}")
                st.write(f"Phone: {supplier['Phone_Primary']} / {supplier['Phone_Secondary']}")
                st.write(f"Email: {supplier['Email_Primary']} / {supplier['Email_Secondary']}")
            
            with col2:
                st.markdown(f"**Business Details**")
                st.write(f"Address: {supplier['Address']}")
                st.write(f"Postal: {supplier['Postal_Code']}")
                st.write(f"Tax Status: {supplier['Tax_Status']}")
                st.write(f"Since: {supplier['Since_Date']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Reliability", f"{supplier['Reliability_Score']*100:.0f}%")
            with col2:
                st.metric("Credit Limit", f"B${supplier['Credit_Limit']}")
            with col3:
                st.metric("Categories", supplier['Product_Categories'])
            
            # Show recent POs from this supplier
            po_count = len(st.session_state.purchase_orders_df[
                st.session_state.purchase_orders_df['Supplier_ID'] == supplier['Supplier_ID']
            ])
            st.write(f"**Purchase Orders:** {po_count} total")

def show_inventory():
    st.markdown('<div class="section-header">📍 Inventory by Location</div>', unsafe_allow_html=True)
    
    location = st.selectbox("Select Location", 
        ['All'] + st.session_state.locations_df['Location_Name'].tolist())
    
    if location != 'All':
        display_df = st.session_state.inventory_df[
            st.session_state.inventory_df['Location_Name'] == location
        ]
    else:
        display_df = st.session_state.inventory_df
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(display_df))
    with col2:
        total_units = display_df['Quantity_On_Hand'].sum()
        st.metric("Total Units", f"{total_units:,}")
    with col3:
        total_value = (display_df['Quantity_On_Hand'] * 
                      st.session_state.products_df['Unit_Cost_BND'].mean())
        st.metric("Total Value", f"B${total_value:,.0f}")
    
    st.dataframe(display_df, use_container_width=True)

def show_transactions():
    st.markdown('<div class="section-header">📊 Transaction History</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        txn_type = st.multiselect("Transaction Type", 
            st.session_state.transactions_df['Transaction_Type'].unique())
    with col2:
        date_range = st.date_input("Date Range", 
            [datetime.now() - timedelta(days=30), datetime.now()])
    with col3:
        product_search = st.text_input("Search Product")
    
    filtered_df = st.session_state.transactions_df
    if txn_type:
        filtered_df = filtered_df[filtered_df['Transaction_Type'].isin(txn_type)]
    if product_search:
        filtered_df = filtered_df[filtered_df['Product_Name'].str.contains(product_search, case=False)]
    
    st.dataframe(filtered_df.sort_values('Date', ascending=False), use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">⚠️ Stock Alerts</div>', unsafe_allow_html=True)
    
    alerts = st.session_state.alerts_df
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        critical = len(alerts[alerts['Alert_Status'] == 'CRITICAL'])
        st.metric("Critical", critical, delta_color="inverse")
    with col2:
        warning = len(alerts[alerts['Alert_Status'] == 'WARNING'])
        st.metric("Warning", warning)
    with col3:
        normal = len(alerts[alerts['Alert_Status'] == 'NORMAL'])
        st.metric("Normal", normal)
    
    # Critical alerts
    if critical > 0:
        st.subheader("🔴 Critical - Immediate Action Required")
        critical_items = alerts[alerts['Alert_Status'] == 'CRITICAL']
        for _, item in critical_items.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{item['Product_Name']}**")
                with col2:
                    st.write(f"Stock: {item['Quantity_On_Hand']}")
                with col3:
                    st.write(f"Reorder: {item['Reorder_Level']}")
                with col4:
                    if st.button(f"Create PO", key=f"po_{item['Product_ID']}"):
                        st.session_state.selected_product_po = item['Product_ID']
                        st.session_state.show_po_form = True
                        st.rerun()
    
    # Warning alerts
    if warning > 0:
        st.subheader("🟡 Warning - Reorder Soon")
        warning_items = alerts[alerts['Alert_Status'] == 'WARNING']
        st.dataframe(warning_items[['Product_Name', 'Quantity_On_Hand', 'Reorder_Level', 'Days_Until_Stockout']])

# ============================================
# MAIN APP
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
        st.metric("Inventory Value", f"B${total_value:,.0f}")
    
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
        loc_stock = st.session_state.inventory_df.groupby('Location_Name')['Quantity_On_Hand'].sum().reset_index()
        fig = px.bar(loc_stock, x='Location_Name', y='Quantity_On_Hand')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Transactions")
    recent = st.session_state.transactions_df.sort_values('Date', ascending=False).head(10)
    st.dataframe(recent[['Date', 'Transaction_Type', 'Product_Name', 'Quantity', 'Performed_By']], 
                use_container_width=True)

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Menu")
    
    page = st.sidebar.radio("Select:", [
        "Executive Dashboard",
        "Product Management",
        "Inventory by Location",
        "Purchase Orders",
        "Suppliers",
        "Transaction History",
        "Stock Alerts"
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
    elif page == "Purchase Orders":
        show_purchase_orders()
    elif page == "Suppliers":
        show_suppliers()
    elif page == "Transaction History":
        show_transactions()
    elif page == "Stock Alerts":
        show_alerts()

if __name__ == "__main__":
    main()
