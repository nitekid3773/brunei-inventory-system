import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #3498db;
        transition: transform 0.2s;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    /* Innovation Cards */
    .innovation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .innovation-card h3 {
        margin-top: 0;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        padding-bottom: 0.5rem;
    }
    
    /* Status Indicators */
    .status-critical {
        background-color: #e74c3c;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-warning {
        background-color: #f39c12;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-normal {
        background-color: #27ae60;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-active {
        background-color: #27ae60;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-discontinued {
        background-color: #95a5a6;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #ecf0f1;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        color: white;
        box-shadow: 0 2px 8px rgba(52,152,219,0.4);
    }
    
    /* Chat messages */
    .user-message {
        background-color: #3498db;
        color: white;
        padding: 10px 15px;
        border-radius: 20px 20px 5px 20px;
        margin: 5px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background-color: #ecf0f1;
        color: #2c3e50;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 5px;
        margin: 5px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    /* Mobile view optimization */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .metric-value {
            font-size: 1.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data persistence
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
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'crud_mode' not in st.session_state:
    st.session_state.crud_mode = "view"
if 'editing_product' not in st.session_state:
    st.session_state.editing_product = None
if 'delete_confirmation' not in st.session_state:
    st.session_state.delete_confirmation = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mobile_view' not in st.session_state:
    st.session_state.mobile_view = False
if 'current_pick_session' not in st.session_state:
    st.session_state.current_pick_session = None

@st.cache_data(ttl=300)
def load_initial_data():
    """
    Load initial data from Excel file structure
    """
    
    # Product Master List (50 products)
    products_data = [
        ['PRD00001', 'ELE9513', 8882629770, 'LED TV', 'Electronics', 785.00, 1135.09, 7, 'Supasave', 'Active', 'A3-12', 15, 45],
        ['PRD00002', 'ELE6539', 8885034668, 'Smartphone', 'Electronics', 916.00, 1351.05, 35, 'Pohan Motors', 'Active', 'A3-08', 38, 32],
        ['PRD00003', 'ELE5637', 8881920026, 'Laptop', 'Electronics', 618.00, 872.40, 25, 'Al-Falah Corporation', 'Active', 'A3-15', 22, 28],
        ['PRD00004', 'ELE4243', 8887653820, 'Tablet', 'Electronics', 1960.00, 2653.80, 6, 'Hua Ho Trading', 'Active', 'A3-05', 8, 15],
        ['PRD00005', 'ELE6781', 8881862054, 'Bluetooth Speaker', 'Electronics', 754.00, 907.19, 6, 'Soon Lee MegaMart', 'Active', 'A3-22', 42, 55],
        ['PRD00006', 'GRO1086', 8888322742, 'Basmati Rice 5kg', 'Groceries', 8.00, 9.81, 18, 'Seng Huat', 'Active', 'B2-01', 120, 85],
        ['PRD00007', 'GRO8871', 8889550421, 'Cooking Oil 2L', 'Groceries', 11.00, 14.28, 11, 'Al-Falah Corporation', 'Active', 'B2-04', 95, 72],
        ['PRD00008', 'GRO5143', 8886941375, 'Sugar 1kg', 'Groceries', 47.00, 62.97, 46, 'Hua Ho Trading', 'Active', 'B2-07', 65, 48],
        ['PRD00009', 'GRO6328', 8882079673, 'Flour 1kg', 'Groceries', 42.00, 58.50, 14, 'Hua Ho Trading', 'Active', 'B2-10', 70, 52],
        ['PRD00010', 'GRO4921', 8882391650, 'Instant Noodles', 'Groceries', 3.00, 4.34, 50, 'Supasave', 'Active', 'B2-13', 200, 150],
        ['PRD00011', 'HAR7985', 8884408841, 'Paint 5L', 'Hardware', 97.00, 116.66, 44, 'SKH Group', 'Active', 'C1-03', 35, 28],
        ['PRD00012', 'HAR7642', 8882206083, 'Cement 40kg', 'Hardware', 56.00, 78.46, 34, 'Wee Hua Enterprise', 'Active', 'C1-06', 80, 45],
        ['PRD00013', 'HAR3920', 8885403285, 'PVC Pipe', 'Hardware', 49.00, 71.86, 25, 'D\'Sunlit Supermarket', 'Active', 'C1-09', 120, 85],
        ['PRD00014', 'HAR3822', 8881779092, 'Electrical Wire', 'Hardware', 37.00, 44.82, 5, 'SKH Group', 'Active', 'C1-12', 45, 32],
        ['PRD00015', 'HAR5003', 8882343059, 'Light Bulb', 'Hardware', 8.00, 9.95, 36, 'SKH Group', 'Active', 'C1-15', 150, 95],
        ['PRD00016', 'PHA7337', 8887613548, 'Paracetamol', 'Pharmaceuticals', 141.00, 189.88, 13, 'Al-Falah Corporation', 'Active', 'D2-02', 65, 42],
        ['PRD00017', 'PHA2752', 8884040859, 'Cough Syrup', 'Pharmaceuticals', 6.00, 8.25, 14, 'Wee Hua Enterprise', 'Active', 'D2-05', 85, 55],
        ['PRD00018', 'PHA3733', 8887351786, 'Vitamin C', 'Pharmaceuticals', 99.00, 121.28, 24, 'Al-Falah Corporation', 'Active', 'D2-08', 45, 35],
        ['PRD00019', 'PHA3787', 8884640696, 'First Aid Kit', 'Pharmaceuticals', 47.00, 56.69, 5, 'SKH Group', 'Active', 'D2-11', 30, 22],
        ['PRD00020', 'PHA4363', 8882862764, 'Bandages', 'Pharmaceuticals', 76.00, 110.20, 5, 'Supasave', 'Active', 'D2-14', 55, 38],
        ['PRD00021', 'AUT3704', 8886967946, 'Engine Oil', 'Automotive', 185.00, 269.02, 12, 'D\'Sunlit Supermarket', 'Active', 'E1-04', 42, 28],
        ['PRD00022', 'AUT9292', 8881721650, 'Car Battery', 'Automotive', 119.00, 167.34, 17, 'Joyful Mart', 'Active', 'E1-08', 25, 18],
        ['PRD00023', 'AUT9310', 8885977758, 'Air Filter', 'Automotive', 160.00, 209.16, 49, 'Seng Huat', 'Active', 'E1-12', 38, 25],
        ['PRD00024', 'AUT7977', 8884903306, 'Brake Pad', 'Automotive', 71.00, 100.99, 14, 'Al-Falah Corporation', 'Discontinued', 'E1-16', 0, 0],
        ['PRD00025', 'AUT6650', 8881362520, 'Spark Plug', 'Automotive', 119.00, 168.95, 37, 'D\'Sunlit Supermarket', 'Active', 'E1-20', 65, 42],
        ['PRD00026', 'TEX9302', 8882287897, 'School Uniform', 'Textiles', 43.00, 54.40, 46, 'Pohan Motors', 'Discontinued', 'F3-01', 0, 0],
        ['PRD00027', 'TEX1181', 8883333480, 'Baju Kurung', 'Textiles', 111.00, 150.36, 43, 'SKH Group', 'Active', 'F3-05', 28, 22],
        ['PRD00028', 'TEX8677', 8887970607, 'Baju Melayu', 'Textiles', 111.00, 152.78, 21, 'Wee Hua Enterprise', 'Active', 'F3-09', 35, 28],
        ['PRD00029', 'TEX8913', 8883535721, 'Songkok', 'Textiles', 21.00, 26.51, 28, 'Wee Hua Enterprise', 'Active', 'F3-13', 45, 32],
        ['PRD00030', 'TEX1792', 8882337786, 'Tudung', 'Textiles', 119.00, 173.22, 17, 'D\'Sunlit Supermarket', 'Active', 'F3-17', 52, 38],
        ['PRD00031', 'FUR1215', 8886673723, 'Office Desk', 'Furniture', 91.00, 129.73, 26, 'D\'Sunlit Supermarket', 'Active', 'G2-04', 12, 8],
        ['PRD00032', 'FUR6787', 8882195570, 'Ergonomic Chair', 'Furniture', 60.00, 88.18, 8, 'Supasave', 'Active', 'G2-08', 18, 12],
        ['PRD00033', 'FUR5417', 8888670445, 'Filing Cabinet', 'Furniture', 128.00, 164.85, 40, 'Joyful Mart', 'Active', 'G2-12', 15, 10],
        ['PRD00034', 'FUR3970', 8881510403, 'Bookshelf', 'Furniture', 46.00, 58.12, 31, 'Seng Huat', 'Active', 'G2-16', 22, 15],
        ['PRD00035', 'FUR6963', 8883713384, 'Meeting Table', 'Furniture', 130.00, 188.59, 33, 'Al-Falah Corporation', 'Active', 'G2-20', 8, 5],
        ['PRD00036', 'STA3134', 8883269795, 'A4 Paper', 'Stationery', 136.00, 190.82, 27, 'SKH Group', 'Active', 'H1-03', 95, 65],
        ['PRD00037', 'STA1487', 8887250125, 'Printer Ink', 'Stationery', 129.00, 168.32, 14, 'Hua Ho Trading', 'Active', 'H1-07', 42, 30],
        ['PRD00038', 'STA4935', 8882810353, 'Ballpoint Pen', 'Stationery', 131.00, 193.55, 36, 'Supasave', 'Active', 'H1-11', 150, 95],
        ['PRD00039', 'STA6275', 8882205355, 'Notebook', 'Stationery', 101.00, 139.82, 48, 'Joyful Mart', 'Active', 'H1-15', 85, 60],
        ['PRD00040', 'STA4686', 8884757367, 'Folder', 'Stationery', 56.00, 73.26, 27, 'Supasave', 'Active', 'H1-19', 110, 75],
        ['PRD00041', 'BEV9661', 8882964355, 'Mineral Water', 'Beverages', 32.00, 41.07, 47, 'Supasave', 'Active', 'I2-02', 200, 140],
        ['PRD00042', 'BEV4750', 8883937121, 'Soft Drinks', 'Beverages', 10.00, 12.46, 11, 'Pohan Motors', 'Active', 'I2-06', 180, 125],
        ['PRD00043', 'BEV2188', 8882771996, 'Orange Juice', 'Beverages', 22.00, 26.73, 42, 'Supasave', 'Active', 'I2-10', 95, 70],
        ['PRD00044', 'BEV2566', 8885056530, 'Energy Drink', 'Beverages', 7.00, 10.05, 37, 'D\'Sunlit Supermarket', 'Active', 'I2-14', 150, 100],
        ['PRD00045', 'BEV2659', 8885907179, 'Milk', 'Beverages', 29.00, 42.27, 33, 'SKH Group', 'Active', 'I2-18', 85, 60],
        ['PRD00046', 'COS4275', 8882812675, 'Facial Cleanser', 'Cosmetics', 23.00, 32.48, 49, 'Joyful Mart', 'Active', 'J1-05', 65, 45],
        ['PRD00047', 'COS6234', 8881405934, 'Moisturizer', 'Cosmetics', 94.00, 138.40, 29, 'Hua Ho Trading', 'Active', 'J1-10', 42, 30],
        ['PRD00048', 'COS4817', 8886216590, 'Lipstick', 'Cosmetics', 141.00, 179.42, 24, 'D\'Sunlit Supermarket', 'Active', 'J1-15', 55, 38],
        ['PRD00049', 'COS9429', 8882217059, 'Foundation', 'Cosmetics', 80.00, 101.94, 20, 'Soon Lee MegaMart', 'Active', 'J1-20', 38, 28],
        ['PRD00050', 'COS3684', 8888986667, 'Shampoo', 'Cosmetics', 88.00, 125.16, 16, 'SKH Group', 'Active', 'J1-25', 72, 50],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 
        'Unit_Cost_BND', 'Selling_Price_BND', 'Reorder_Level', 
        'Preferred_Supplier', 'Status', 'Bin_Location', 
        'Daily_Movement', 'Current_Stock'
    ])
    
    # Inventory by Location (250 records - 50 products × 5 locations)
    locations = ['Warehouse A - Beribi', 'Store 1 - Gadong', 'Store 2 - Kiulap', 'Store 3 - Kuala Belait', 'Store 4 - Tutong']
    
    inventory_data = []
    base_quantities = {
        'PRD00001': [163, 132, 171, 179, 172],
        'PRD00002': [19, 163, 42, 165, 76],
        'PRD00003': [64, 159, 175, 40, 136],
        'PRD00004': [143, 159, 102, 78, 132],
        'PRD00005': [104, 2, 115, 169, 183],
        'PRD00006': [33, 110, 86, 111, 15],
        'PRD00007': [164, 85, 71, 47, 93],
        'PRD00008': [4, 96, 109, 35, 144],
        'PRD00009': [67, 21, 198, 168, 186],
        'PRD00010': [189, 103, 83, 154, 195],
    }
    
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in enumerate(locations):
            if prod in base_quantities:
                qty = base_quantities[prod][j]
            else:
                qty = 50 + ((i + j) * 17) % 150
            
            inventory_data.append({
                'Product_ID': prod,
                'Location': loc,
                'Quantity_On_Hand': qty,
                'Last_Updated': datetime.now().strftime('%Y-%m-%d')
            })
    
    inventory = pd.DataFrame(inventory_data)
    
    # Stock Transactions
    transaction_types = ['ADJUSTMENT', 'STOCK IN', 'STOCK OUT']
    remarks_options = ['Inventory Count', 'Purchase Order', 'Sale', 'System Correction', 
                      'Transfer from Warehouse', 'Return from Customer', 'Expired', 
                      'Damaged', 'Sample/Display']
    
    transactions_data = []
    for i in range(150):
        prod_idx = i % 50
        loc_idx = i % 5
        txn_type = transaction_types[i % 3]
        
        qty = 5 if txn_type == 'ADJUSTMENT' else (10 if txn_type == 'STOCK IN' else -5)
        
        transactions_data.append({
            'Transaction_ID': f'TRX2026{i:04d}',
            'Date': (datetime.now() - timedelta(days=150-i)).strftime('%Y-%m-%d'),
            'Product_ID': products_data[prod_idx][0],
            'Product_Name': products_data[prod_idx][3],
            'Transaction_Type': txn_type,
            'Quantity_Change': qty,
            'Location': locations[loc_idx],
            'Reference_Number': f'REF{1000+i}',
            'Remarks': remarks_options[i % 9]
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Supplier Management
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', '673-2223456', 'purchasing@huaho.com', 'KG Kiulap', 'Net 30', 'Gold'],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', '673-2337890', 'orders@soonlee.com', 'Gadong Central', 'Net 30', 'Platinum'],
        ['SUP003', 'Supasave', 'David Wong', '673-2456789', 'procurement@supasave.com', 'Serusop', 'Net 45', 'Silver'],
        ['SUP004', 'Seng Huat', 'Michael Chen', '673-2771234', 'sales@senghuat.com', 'Kuala Belait', 'Cash on Delivery', 'Gold'],
        ['SUP005', 'SKH Group', 'Steven Khoo', '673-2667890', 'trading@skh.com', 'Tutong Town', 'Net 30', 'Platinum'],
        ['SUP006', 'Wee Hua Enterprise', 'Jason Wee', '673-2884567', 'orders@weehua.com', 'Seria', 'Net 30', 'Silver'],
        ['SUP007', 'Pohan Motors', 'Ahmad Pohan', '673-2334455', 'parts@pohan.com', 'Beribi', 'Cash on Delivery', 'Gold'],
        ['SUP008', 'D\'Sunlit Supermarket', 'Hjh Zainab', '673-2656789', 'procurement@dsunlit.com', 'Menglait', 'Net 45', 'Silver'],
        ['SUP009', 'Joyful Mart', 'Liew KF', '673-2781234', 'supply@joyfulmart.com', 'Kiarong', 'Net 30', 'Bronze'],
        ['SUP010', 'Al-Falah Corporation', 'Hj Osman', '673-2235678', 'trading@alfalah.com', 'Lambak Kanan', 'Cash on Delivery', 'Gold'],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Phone', 
        'Email', 'Address', 'Payment_Terms', 'Tier'
    ])
    
    # Purchase Orders
    po_status = ['Draft', 'Sent', 'Confirmed', 'Shipped', 'Received', 'Cancelled']
    
    purchase_orders_data = []
    for i in range(40):
        prod_idx = i % 50
        supp_idx = i % 10
        
        purchase_orders_data.append({
            'PO_Number': f'PO2026{i:04d}',
            'Supplier_ID': suppliers_data[supp_idx][0],
            'Supplier_Name': suppliers_data[supp_idx][1],
            'Product_ID': products_data[prod_idx][0],
            'Product_Name': products_data[prod_idx][3],
            'Ordered_Quantity': 100 + (i * 10),
            'Received_Quantity': 80 + (i * 5),
            'Unit_Cost_BND': products_data[prod_idx][5],
            'Total_Cost_BND': (100 + i * 10) * products_data[prod_idx][5],
            'Order_Date': (datetime.now() - timedelta(days=90-i*2)).strftime('%Y-%m-%d'),
            'Expected_Date': (datetime.now() + timedelta(days=30-i)).strftime('%Y-%m-%d'),
            'Order_Status': random.choice(po_status)
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Stock Alert Monitoring
    current_stock = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(products[['Product_ID', 'Product_Name', 'Category', 'Reorder_Level']], on='Product_ID')
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    alerts['Alert_Status'] = alerts.apply(get_alert_status, axis=1)
    
    return products, inventory, transactions, suppliers, purchase_orders, alerts

# Initialize data in session state
if st.session_state.products_df is None:
    (st.session_state.products_df, 
     st.session_state.inventory_df, 
     st.session_state.transactions_df, 
     st.session_state.suppliers_df, 
     st.session_state.purchase_orders_df, 
     st.session_state.alerts_df) = load_initial_data()

# ============================================
# CRUD OPERATIONS FUNCTIONS
# ============================================

def generate_product_id():
    """Generate a new unique Product ID"""
    existing_ids = st.session_state.products_df['Product_ID'].tolist()
    numbers = [int(id.replace('PRD', '')) for id in existing_ids]
    next_num = max(numbers) + 1
    return f"PRD{next_num:05d}"

def generate_sku(category):
    """Generate a new SKU based on category"""
    prefix = category[:3].upper()
    return f"{prefix}{random.randint(10000, 99999)}"

def generate_barcode():
    """Generate a new barcode"""
    return int(f"888{random.randint(1000000, 9999999)}")

def validate_product_data(data):
    """Validate product data before saving"""
    errors = []
    
    if not data.get('Product_Name'):
        errors.append("Product Name is required")
    
    if data.get('Unit_Cost_BND', 0) <= 0:
        errors.append("Unit Cost must be greater than 0")
    
    if data.get('Selling_Price_BND', 0) <= 0:
        errors.append("Selling Price must be greater than 0")
    
    if data.get('Selling_Price_BND', 0) <= data.get('Unit_Cost_BND', 0):
        errors.append("Selling Price should be greater than Unit Cost")
    
    if data.get('Reorder_Level', 0) < 0:
        errors.append("Reorder Level cannot be negative")
    
    return errors

def add_product(product_data):
    """Add a new product to the database"""
    errors = validate_product_data(product_data)
    if errors:
        return False, errors
    
    product_data['Product_ID'] = generate_product_id()
    if not product_data.get('SKU'):
        product_data['SKU'] = generate_sku(product_data['Category'])
    if not product_data.get('Barcode'):
        product_data['Barcode'] = generate_barcode()
    
    st.session_state.products_df = pd.concat(
        [st.session_state.products_df, pd.DataFrame([product_data])], 
        ignore_index=True
    )
    
    locations = ['Warehouse A - Beribi', 'Store 1 - Gadong', 'Store 2 - Kiulap', 
                 'Store 3 - Kuala Belait', 'Store 4 - Tutong']
    
    new_inventory = []
    for loc in locations:
        new_inventory.append({
            'Product_ID': product_data['Product_ID'],
            'Location': loc,
            'Quantity_On_Hand': 0,
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        })
    
    st.session_state.inventory_df = pd.concat(
        [st.session_state.inventory_df, pd.DataFrame(new_inventory)], 
        ignore_index=True
    )
    
    st.session_state.last_update = datetime.now()
    return True, product_data['Product_ID']

def update_product(product_id, updated_data):
    """Update an existing product"""
    errors = validate_product_data(updated_data)
    if errors:
        return False, errors
    
    mask = st.session_state.products_df['Product_ID'] == product_id
    
    for key, value in updated_data.items():
        if value is not None and key in st.session_state.products_df.columns:
            st.session_state.products_df.loc[mask, key] = value
    
    if 'Product_Name' in updated_data:
        st.session_state.transactions_df.loc[
            st.session_state.transactions_df['Product_ID'] == product_id, 'Product_Name'
        ] = updated_data['Product_Name']
        
        st.session_state.purchase_orders_df.loc[
            st.session_state.purchase_orders_df['Product_ID'] == product_id, 'Product_Name'
        ] = updated_data['Product_Name']
    
    st.session_state.last_update = datetime.now()
    return True, None

def delete_product(product_id):
    """Delete a product and all related records"""
    product_name = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] == product_id
    ]['Product_Name'].values[0]
    
    st.session_state.products_df = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] != product_id
    ]
    
    st.session_state.inventory_df = st.session_state.inventory_df[
        st.session_state.inventory_df['Product_ID'] != product_id
    ]
    
    st.session_state.transactions_df = st.session_state.transactions_df[
        st.session_state.transactions_df['Product_ID'] != product_id
    ]
    
    st.session_state.purchase_orders_df = st.session_state.purchase_orders_df[
        st.session_state.purchase_orders_df['Product_ID'] != product_id
    ]
    
    st.session_state.last_update = datetime.now()
    return product_name

def reset_crud_mode():
    """Reset CRUD mode to view"""
    st.session_state.crud_mode = "view"
    st.session_state.editing_product = None

# ============================================
# INNOVATION 1: AI-Powered Bin Location Optimization
# ============================================
def show_smart_binning():
    st.header("📍 AI Smart Bin Location Optimizer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>Current Layout Efficiency: 67%</h3>
            <p><strong>AI Recommendations:</strong></p>
            <p>🔥 <strong>Fast Movers (Zone A - Near Shipping)</strong></p>
            <ul>
                <li>LED TV (moves 45 units/day) → Bin A1</li>
                <li>Cooking Oil (moves 38 units/day) → Bin A2</li>
                <li>Rice 5kg (moves 32 units/day) → Bin A3</li>
            </ul>
            <p>📦 <strong>Medium Movers (Zone B)</strong></p>
            <ul>
                <li>Smartphone accessories</li>
                <li>Hardware tools</li>
                <li>Cosmetics</li>
            </ul>
            <p>❄️ <strong>Slow Movers (Zone C - Upper Levels)</strong></p>
            <ul>
                <li>Furniture</li>
                <li>Seasonal items</li>
                <li>Bulk paper products</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Apply AI Optimization"):
            st.success("✅ Bin locations reorganized! Expected travel time reduction: 23%")
    
    with col2:
        # Calculate velocity-based recommendations
        velocity_data = st.session_state.products_df.nlargest(10, 'Daily_Movement')[['Product_Name', 'Daily_Movement', 'Bin_Location']]
        
        fig = px.bar(velocity_data, x='Product_Name', y='Daily_Movement',
                    title="Top 10 Fast-Moving Items",
                    color='Daily_Movement',
                    color_continuous_scale='Viridis')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Optimization Benefits:**
        - Travel distance: 342m → 263m (↓23%)
        - Pick efficiency: 78% → 94% (↑16%)
        - Labor savings: 2.5 hours/shift
        """)

# ============================================
# INNOVATION 2: Predictive Demand Forecasting
# ============================================
def show_demand_forecasting():
    st.header("📈 AI Demand Forecasting Engine")
    
    # Generate forecast data
    dates = pd.date_range(start=datetime.now(), periods=90, freq='D')
    forecast_data = pd.DataFrame({
        'Date': dates,
        'LED_TV': [max(0, 45 + 10*np.sin(2*np.pi*i/30) + random.randint(-5,5)) for i in range(90)],
        'Rice_5kg': [max(0, 120 + 30*np.sin(2*np.pi*i/7) + random.randint(-10,10)) for i in range(90)],
        'Engine_Oil': [max(0, 28 + 5*np.sin(2*np.pi*i/14) + random.randint(-3,3)) for i in range(90)]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📊 90-Day Demand Forecast</h3>
            <p><strong>Top Products by Predicted Demand:</strong></p>
            <ul>
                <li><strong>Basmati Rice 5kg</strong> - 3,720 units ↑22% (Hari Raya peak)</li>
                <li><strong>Cooking Oil 2L</strong> - 2,850 units ↑15%</li>
                <li><strong>LED TV 55"</strong> - 2,560 units ↑8%</li>
                <li><strong>Mineral Water</strong> - 2,240 units ↑12%</li>
                <li><strong>Paracetamol</strong> - 1,850 units ↑5%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("""
        **⚠️ Seasonal Alerts:**
        - 🕌 **Hari Raya** (Next month): Increase grocery stock by 40%
        - 🎓 **School Term** (Next week): Boost stationery by 25%
        - 🌧️ **Monsoon** (Current): Prepare for delivery delays
        """)
    
    with col2:
        fig = px.line(forecast_data, x='Date', y=['LED_TV', 'Rice_5kg', 'Engine_Oil'],
                     title="90-Day Demand Forecast with Seasonality")
        fig.add_vline(x=forecast_data.iloc[30]['Date'], 
                     line_dash="dash", line_color="red",
                     annotation_text="Hari Raya Peak")
        st.plotly_chart(fig, use_container_width=True)
    
    # Reorder recommendations
    st.subheader("📋 AI Reorder Recommendations")
    
    rec_data = pd.DataFrame({
        'Product': ['Basmati Rice 5kg', 'Cooking Oil 2L', 'LED TV', 'Mineral Water'],
        'Current_Stock': [355, 460, 817, 505],
        'Forecast_Demand': [1240, 950, 855, 745],
        'Recommended_Order': [900, 500, 0, 250],
        'Supplier': ['Seng Huat', 'Al-Falah', 'Supasave', 'Supasave']
    })
    st.table(rec_data)

# ============================================
# INNOVATION 3: Computer Vision Inventory Counting
# ============================================
def show_vision_counting():
    st.header("📸 AI Vision Stock Counter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📹 Camera 1 - Aisle A3 (Electronics)</h3>
            <p><strong>🔍 AI Detection Results:</strong></p>
            <ul>
                <li>LED TVs detected: 23 (System shows 25) ⚠️ -2 variance</li>
                <li>Smartphones detected: 42 (System shows 40) ⚠️ +2 variance</li>
                <li>Laptops detected: 15 (System shows 15) ✅ Match</li>
            </ul>
            <p><strong>Confidence Score:</strong> 94.5%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📹 Camera 2 - Aisle B7 (Groceries)</h3>
            <p><strong>🔍 AI Detection Results:</strong></p>
            <ul>
                <li>Rice 5kg pallets: 18 (System shows 18) ✅ Match</li>
                <li>Cooking Oil cases: 32 (System shows 32) ✅ Match</li>
                <li>Flour bags: 24 (System shows 24) ✅ Match</li>
            </ul>
            <p><strong>Confidence Score:</strong> 98.2%</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 Trigger Full Warehouse Count"):
        with st.spinner("AI analyzing all camera feeds..."):
            time.sleep(2)
            st.success("✅ Count complete! Variances detected in 3 locations")
    
    # Accuracy trend
    st.subheader("📊 Inventory Accuracy Trend")
    accuracy_data = pd.DataFrame({
        'Week': ['W1', 'W2', 'W3', 'W4', 'W5'],
        'Accuracy': [96.2, 97.1, 98.5, 97.8, 99.2]
    })
    fig = px.line(accuracy_data, x='Week', y='Accuracy', 
                 title="Inventory Accuracy % - Last 5 Weeks",
                 range_y=[95, 100])
    fig.add_hline(y=98, line_dash="dash", line_color="green")
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# INNOVATION 4: Voice-Powered Picking
# ============================================
def show_voice_picking():
    st.header("🎤 AI Voice-Directed Picking")
    
    if st.session_state.current_pick_session is None:
        st.session_state.current_pick_session = {
            'picker': 'Ahmad',
            'wave': '1567',
            'items': [
                {'name': 'LED TV', 'qty': 3, 'bin': 'A3-12', 'status': 'pending'},
                {'name': 'Smartphone', 'qty': 5, 'bin': 'A3-08', 'status': 'pending'},
                {'name': 'Laptop', 'qty': 2, 'bin': 'A3-15', 'status': 'pending'}
            ],
            'completed': 0
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🎧 Current Pick Session</h3>
        """, unsafe_allow_html=True)
        
        st.write(f"**Picker:** {st.session_state.current_pick_session['picker']} (ID: WH234)")
        st.write(f"**Wave:** #{st.session_state.current_pick_session['wave']}")
        st.write(f"**Progress:** {st.session_state.current_pick_session['completed']}/3 items")
        
        st.markdown("**Active Order:**")
        for item in st.session_state.current_pick_session['items']:
            status_icon = "✅" if item['status'] == 'completed' else "⏳"
            st.write(f"{status_icon} {item['qty']}x {item['name']} (Bin {item['bin']})")
        
        st.markdown("**Voice Commands:**")
        st.caption("• 'Next item' → Move to next pick")
        st.caption("• 'Confirm quantity' → Verify pick")
        st.caption("• 'Wrong location' → Report error")
        st.caption("• 'Complete wave' → Finish batch")
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📊 Pick Performance</h3>
        """, unsafe_allow_html=True)
        
        perf_data = pd.DataFrame({
            'Metric': ['Picks/Hour', 'Accuracy', 'Travel Time', 'Fatigue Level'],
            'Value': ['142', '99.8%', '2.3 min', 'Low'],
            'Target': ['150', '99.5%', '2.5 min', '-']
        })
        st.table(perf_data)
        
        st.info("💡 **AI Coaching:** *You can save 30 seconds by taking the left aisle for your next pick*")
        
        if st.button("🎯 Start Voice Session"):
            st.success("Voice picking activated. Speak your commands.")
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

# ============================================
# INNOVATION 5: Predictive Maintenance
# ============================================
def show_predictive_maintenance():
    st.header("🔧 AI Predictive Maintenance")
    
    equipment = pd.DataFrame({
        'Equipment': ['Forklift 1', 'Forklift 2', 'Conveyor A', 'Pallet Jack', 'Charger Station'],
        'Health_%': [92, 78, 95, 88, 72],
        'Last_Service': ['2026-01-15', '2025-12-20', '2026-02-01', '2026-01-25', '2025-12-10'],
        'Next_Service': ['2026-04-15', '2026-03-20', '2026-05-01', '2026-04-25', '2026-03-10']
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Equipment Health Status")
        
        for _, row in equipment.iterrows():
            color = "🟢" if row['Health_%'] > 85 else "🟡" if row['Health_%'] > 70 else "🔴"
            st.markdown(f"{color} **{row['Equipment']}**: {row['Health_%']}% health")
            st.caption(f"Last: {row['Last_Service']} | Next: {row['Next_Service']}")
            st.progress(row['Health_%']/100)
    
    with col2:
        st.subheader("🔮 AI Predictions")
        
        st.warning("""
        **⚠️ Forklift 2 requires maintenance within 7 days**
        - Predicted failure: Hydraulic pump (92% confidence)
        - Estimated downtime: 4 hours
        - Recommended: Schedule service on Mar 15
        
        **🟡 Pallet Jack bearings wearing**
        - 72% health remaining
        - Monitor vibration levels
        - Order replacement parts
        """)
        
        # Maintenance schedule
        st.subheader("📅 Optimized Schedule")
        schedule_data = pd.DataFrame({
            'Week': ['Mar 8-14', 'Mar 15-21', 'Mar 22-28', 'Mar 29-Apr 4'],
            'Maintenance': ['Forklift 2', 'All Forklifts', 'Conveyor A', 'Charger Station'],
            'Duration': ['4 hours', '8 hours', '2 hours', '3 hours']
        })
        st.table(schedule_data)

# ============================================
# INNOVATION 6: Dynamic Slotting with RL
# ============================================
def show_dynamic_slotting():
    st.header("🧠 AI Dynamic Slotting Engine")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📍 Current Slotting</h3>
            <pre>
Aisle 1 [Electronics]
[TV] [TV] [TV] [Phone] [Phone] [Tablet]

Aisle 2 [Groceries]
[Rice] [Rice] [Oil] [Oil] [Flour] [Flour]

Aisle 3 [Mixed]
[Tools] [Paint] [Cables] [Cases] [Random]
            </pre>
            <p><strong>Travel Distance:</strong> 342m/day</p>
            <p><strong>Pick Efficiency:</strong> 78%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🤖 AI-Optimized</h3>
            <pre>
Aisle 1 [Fast Movers + Affinity]
[Rice] [TV] [Rice] [Oil] [TV] [Phone]

Aisle 2 [Medium Movers]
[Flour] [Tablet] [Tools] [Paint] [Cables]

Aisle 3 [Slow Movers + Bulk]
[Furniture] [Bulk] [Seasonal] [Backup]
            </pre>
            <p><strong>Travel Distance:</strong> 263m/day ↓23%</p>
            <p><strong>Pick Efficiency:</strong> 94% ↑16%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Learning curve
    learning_data = pd.DataFrame({
        'Week': [1,2,3,4,5,6,7,8],
        'Efficiency': [78, 82, 85, 88, 91, 93, 94, 94]
    })
    fig = px.line(learning_data, x='Week', y='Efficiency',
                 title="Picking Efficiency Improvement Over Time")
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# INNOVATION 7: Cold Chain Monitoring with IoT
# ============================================
def show_cold_chain():
    st.header("❄️ AI Cold Chain Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🌡️ Current Temperatures</h3>
        """, unsafe_allow_html=True)
        
        zones = ['Pharma Freezer (-20°C)', 'Chiller (4°C)', 'Cool Room (15°C)', 'Ambient (25°C)']
        temps = [-19.8, 4.2, 15.5, 25.1]
        alerts = ['✅', '⚠️', '✅', '✅']
        
        for zone, temp, alert in zip(zones, temps, alerts):
            color = "🟢" if alert == '✅' else "🟡"
            st.markdown(f"{color} **{zone}**: {temp}°C")
        
        st.warning("""
        **⚠️ Alert: Chiller temperature trending up**
        - Current: 4.2°C (target: 2-4°C)
        - Predicted to reach 4.5°C in 2 hours
        - Check door seals and compressor
        """)
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>💊 Vaccine Stock (Pharma Freezer)</h3>
        """, unsafe_allow_html=True)
        
        vaccines = pd.DataFrame({
            'Product': ['COVID-19', 'Influenza', 'Childhood', 'Travel'],
            'Current': [1200, 850, 2300, 450],
            'Min': [1000, 500, 2000, 400],
            'Max': [5000, 2000, 5000, 1000],
            'Expiry': ['2026-06', '2026-03', '2026-09', '2026-04']
        })
        st.table(vaccines)
        
        if st.button("📋 Generate Temperature Report"):
            st.success("Temperature log exported to compliance system")

# ============================================
# INNOVATION 8: Labor Optimization Engine
# ============================================
def show_labor_optimization():
    st.header("👥 AI Labor Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📅 Today's Schedule</h3>
        """, unsafe_allow_html=True)
        
        shifts = pd.DataFrame({
            'Role': ['Receiving', 'Picking', 'Packing', 'Loading', 'Supervisor'],
            'Staff': [4, 12, 6, 3, 2],
            'Current': [3, 10, 5, 2, 2],
            'Productivity': [92, 88, 95, 78, 100]
        })
        st.table(shifts)
        
        st.markdown("**⚠️ Understaffed:** Loading bay (need 1 more)")
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🤖 AI Recommendations</h3>
        """, unsafe_allow_html=True)
        
        st.success("""
        **Optimization Suggestions:**
        
        1. Move 1 picker to loading bay (2-4pm peak)
        2. Cross-train 2 pickers for packing
        3. Schedule breaks to maintain coverage
        4. Offer overtime to 2 staff for evening
        
        **Projected Impact:**
        - Throughput ↑12%
        - Overtime cost ↓8%
        - OTIF ↑5%
        """)
    
    # Productivity heatmap
    st.subheader("📊 Hourly Productivity Heatmap")
    heatmap_data = pd.DataFrame({
        'Hour': list(range(6, 22)),
        'Picking': [45, 68, 92, 105, 98, 112, 145, 138, 132, 125, 98, 76, 54, 32, 18, 8],
        'Packing': [32, 45, 67, 78, 82, 95, 112, 108, 98, 92, 76, 54, 38, 22, 12, 5],
        'Loading': [12, 18, 25, 34, 45, 58, 72, 85, 92, 88, 76, 58, 42, 28, 15, 6]
    })
    
    fig = px.line(heatmap_data, x='Hour', y=['Picking', 'Packing', 'Loading'],
                 title="Productivity by Hour")
    fig.add_vline(x=14, line_dash="dash", line_color="red",
                 annotation_text="Peak Hour")
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# INNOVATION 9: Returns Management AI
# ============================================
def show_returns_management():
    st.header("🔄 AI Returns Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📦 Today's Returns</h3>
        """, unsafe_allow_html=True)
        
        returns = pd.DataFrame({
            'Product': ['LED TV', 'Smartphone', 'Rice 5kg', 'Engine Oil'],
            'Qty': [3, 8, 12, 5],
            'Reason': ['Damaged', 'Defective', 'Expired', 'Wrong item'],
            'Disposition': ['Repair', 'Refurbish', 'Write-off', 'Restock'],
            'Value': [2355, 7200, 96, 375]
        })
        st.table(returns)
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🤖 AI Analysis</h3>
        """, unsafe_allow_html=True)
        
        st.info("""
        **Patterns Detected:**
        - 📱 Smartphone returns spike after software updates
        - 🍚 Rice expiry concentrated in monsoon months
        - 📺 TV damage during afternoon shifts
        
        **Recommendations:**
        - Train staff on smartphone setup
        - Adjust rice orders pre-monsoon
        - Extra cushioning for afternoon picks
        """)
    
    st.metric("Recovered Value This Month", "$12,450", "+18% vs last month")

# ============================================
# INNOVATION 10: Sustainability Dashboard
# ============================================
def show_sustainability():
    st.header("🌱 AI Green Warehouse Initiative")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>⚡ Energy Consumption</h3>
        """, unsafe_allow_html=True)
        
        energy = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'kWh': [45200, 44800, 46100, 45800, 47100, 46300],
            'Solar': [3200, 3800, 4500, 5200, 5800, 6100]
        })
        
        fig = px.bar(energy, x='Month', y=['kWh', 'Solar'],
                    title="Energy Usage vs Solar Generation",
                    barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>♻️ Sustainability Metrics</h3>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **Carbon Footprint:** 124 tons CO2 (↓8% YoY)
        **Recycling Rate:** 76% (target 80%)
        **Water Usage:** 45,000L (↓12%)
        **LED Lighting:** 95% conversion complete
        
        **AI Recommendations:**
        - Install motion sensors in low-traffic areas
        - Optimize HVAC schedule for off-hours
        - Convert remaining 5% to LED by June
        """)
    
    st.success("💰 **Annual Savings:** $48,000 from sustainability initiatives")

# ============================================
# MOBILE APP INTEGRATION
# ============================================
def show_mobile_app():
    st.header("📱 Warehouse Mobile App")
    
    # Mobile view toggle
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("📱 Switch to Mobile View"):
            st.session_state.mobile_view = not st.session_state.mobile_view
    
    if st.session_state.mobile_view:
        # Mobile-optimized view
        st.markdown("""
        <style>
            .mobile-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 20px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .mobile-header {
                background: #3498db;
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 15px;
            }
            .mobile-menu {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin: 15px 0;
            }
            .mobile-menu-item {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                cursor: pointer;
                border: 1px solid #dee2e6;
            }
            .mobile-menu-item:hover {
                background: #e9ecef;
            }
        </style>
        
        <div class="mobile-container">
            <div class="mobile-header">
                <h3>Stock Inventory</h3>
                <p>Picker: Ahmad | Wave #1567</p>
            </div>
            
            <div class="mobile-menu">
                <div class="mobile-menu-item">📦 Scan Item</div>
                <div class="mobile-menu-item">📍 Find Bin</div>
                <div class="mobile-menu-item">📋 My Tasks</div>
                <div class="mobile-menu-item">📊 Performance</div>
            </div>
            
            <h4>Current Task</h4>
            <div class="mobile-menu-item" style="text-align: left;">
                <p><strong>3x LED TV</strong><br>Bin: A3-12<br>Status: ⏳ Pending</p>
            </div>
            <div class="mobile-menu-item" style="text-align: left;">
                <p><strong>5x Smartphone</strong><br>Bin: A3-08<br>Status: ⏳ Pending</p>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button style="flex:1; background: #27ae60; color: white; padding: 12px; border: none; border-radius: 5px;">✓ Confirm Pick</button>
                <button style="flex:1; background: #e74c3c; color: white; padding: 12px; border: none; border-radius: 5px;">✗ Report Issue</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Desktop view of mobile features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="dashboard-card">
                <h3>📦 Picker View</h3>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>Voice-directed picking</li>
                    <li>Barcode scanning</li>
                    <li>Real-time location</li>
                    <li>Task prioritization</li>
                </ul>
                <p style="color: #27ae60;">12 active pickers</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="dashboard-card">
                <h3>👤 Supervisor View</h3>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>Team performance</li>
                    <li>Exception alerts</li>
                    <li>Resource reallocation</li>
                    <li>Shift management</li>
                </ul>
                <p style="color: #f39c12;">3 alerts pending</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="dashboard-card">
                <h3>📊 Manager View</h3>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>KPI dashboards</li>
                    <li>Forecast accuracy</li>
                    <li>Budget tracking</li>
                    <li>Strategic reports</li>
                </ul>
                <p style="color: #3498db;">All metrics green</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Mobile adoption stats
        st.subheader("📊 Mobile App Adoption")
        adoption_data = pd.DataFrame({
            'Week': ['W1', 'W2', 'W3', 'W4'],
            'Active_Users': [15, 28, 35, 42],
            'Tasks_Completed': [320, 580, 720, 890]
        })
        fig = px.line(adoption_data, x='Week', y=['Active_Users', 'Tasks_Completed'],
                     title="Mobile App Usage Growth")
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# CRUD DASHBOARD UI
# ============================================
def show_product_crud_dashboard():
    """Main CRUD dashboard for product management"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
        <h1>📝 Product Master List Management</h1>
        <p style="font-size: 1.2rem;">Create, Read, Update, and Delete Products in Real-Time</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(st.session_state.products_df))
    
    with col2:
        active_count = len(st.session_state.products_df[
            st.session_state.products_df['Status'] == 'Active'
        ])
        st.metric("Active Products", active_count)
    
    with col3:
        categories = st.session_state.products_df['Category'].nunique()
        st.metric("Categories", categories)
    
    with col4:
        suppliers = st.session_state.suppliers_df['Supplier_Name'].nunique()
        st.metric("Suppliers", suppliers)
    
    st.markdown("---")
    
    # CRUD Action Buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    
    with col1:
        if st.button("➕ ADD NEW PRODUCT", use_container_width=True):
            st.session_state.crud_mode = "add"
            st.session_state.editing_product = None
            st.rerun()
    
    with col2:
        if st.button("📋 VIEW ALL", use_container_width=True):
            reset_crud_mode()
            st.rerun()
    
    with col3:
        if st.button("🔄 REFRESH", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # CRUD Mode Content
    if st.session_state.crud_mode == "add":
        show_add_product_form()
    elif st.session_state.crud_mode == "edit" and st.session_state.editing_product:
        show_edit_product_form(st.session_state.editing_product)
    else:
        show_product_list()

def show_add_product_form():
    """Display form for adding new products"""
    
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; margin: 1rem 0;">
        <h2 style="color: #2c3e50;">➕ Add New Product</h2>
    """, unsafe_allow_html=True)
    
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name *", 
                placeholder="Enter product name"
            )
            
            category = st.selectbox(
                "Category *",
                ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                 'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                 'Beverages', 'Cosmetics']
            )
            
            st.text_input(
                "SKU (Auto-generated)", 
                value=generate_sku(category if 'category' in locals() else 'Electronics'),
                disabled=True
            )
            
            st.text_input(
                "Barcode (Auto-generated)", 
                value=str(generate_barcode()),
                disabled=True
            )
        
        with col2:
            unit_cost = st.number_input(
                "Unit Cost *", 
                min_value=0.01, 
                value=100.00, 
                step=10.00,
                format="%.2f"
            )
            
            selling_price = st.number_input(
                "Selling Price *", 
                min_value=0.01, 
                value=150.00, 
                step=10.00,
                format="%.2f"
            )
            
            reorder_level = st.number_input(
                "Reorder Level *", 
                min_value=1, 
                value=10, 
                step=1
            )
            
            suppliers = st.session_state.suppliers_df['Supplier_Name'].tolist()
            preferred_supplier = st.selectbox(
                "Preferred Supplier *", 
                suppliers
            )
            
            status = st.selectbox(
                "Status", 
                ['Active', 'Discontinued']
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 SAVE PRODUCT", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ CANCEL", use_container_width=True)
        
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
                    'Unit_Cost_BND': unit_cost,
                    'Selling_Price_BND': selling_price,
                    'Reorder_Level': reorder_level,
                    'Preferred_Supplier': preferred_supplier,
                    'Status': status
                }
                
                success, result = add_product(product_data)
                
                if success:
                    st.success(f"✅ Product '{product_name}' added successfully! Product ID: {result}")
                    st.balloons()
                    time.sleep(2)
                    reset_crud_mode()
                    st.rerun()
                else:
                    st.error(f"❌ Error adding product: {', '.join(result)}")
        
        if cancelled:
            reset_crud_mode()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_edit_product_form(product_id):
    """Display form for editing existing products"""
    
    product = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] == product_id
    ].iloc[0]
    
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; margin: 1rem 0;">
        <h2 style="color: #2c3e50;">✏️ Edit Product: {product['Product_Name']}</h2>
        <p><strong>Product ID:</strong> {product_id}</p>
    """, unsafe_allow_html=True)
    
    with st.form("edit_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name *", 
                value=product['Product_Name']
            )
            
            category = st.selectbox(
                "Category *",
                ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                 'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                 'Beverages', 'Cosmetics'],
                index=['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                       'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                       'Beverages', 'Cosmetics'].index(product['Category'])
            )
            
            st.text_input("SKU", value=product['SKU'], disabled=True)
            st.text_input("Barcode", value=str(product['Barcode']), disabled=True)
        
        with col2:
            unit_cost = st.number_input(
                "Unit Cost *", 
                min_value=0.01, 
                value=float(product['Unit_Cost_BND']), 
                step=10.00,
                format="%.2f"
            )
            
            selling_price = st.number_input(
                "Selling Price *", 
                min_value=0.01, 
                value=float(product['Selling_Price_BND']), 
                step=10.00,
                format="%.2f"
            )
            
            reorder_level = st.number_input(
                "Reorder Level *", 
                min_value=1, 
                value=int(product['Reorder_Level']), 
                step=1
            )
            
            suppliers = st.session_state.suppliers_df['Supplier_Name'].tolist()
            preferred_supplier = st.selectbox(
                "Preferred Supplier *", 
                suppliers,
                index=suppliers.index(product['Preferred_Supplier'])
            )
            
            status = st.selectbox(
                "Status", 
                ['Active', 'Discontinued'],
                index=0 if product['Status'] == 'Active' else 1
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 UPDATE PRODUCT", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ CANCEL", use_container_width=True)
        
        if submitted:
            if not product_name:
                st.error("❌ Product Name is required!")
            elif selling_price <= unit_cost:
                st.error("❌ Selling Price must be greater than Unit Cost!")
            else:
                updated_data = {
                    'Product_Name': product_name,
                    'Category': category,
                    'Unit_Cost_BND': unit_cost,
                    'Selling_Price_BND': selling_price,
                    'Reorder_Level': reorder_level,
                    'Preferred_Supplier': preferred_supplier,
                    'Status': status
                }
                
                success, errors = update_product(product_id, updated_data)
                
                if success:
                    st.success(f"✅ Product '{product_name}' updated successfully!")
                    time.sleep(2)
                    reset_crud_mode()
                    st.rerun()
                else:
                    st.error(f"❌ Error updating product: {', '.join(errors)}")
        
        if cancelled:
            reset_crud_mode()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_product_list():
    """Display product list with edit/delete options"""
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Search by Product Name or ID", placeholder="Type to search...")
    
    with col2:
        category_filter = st.multiselect(
            "Category",
            options=st.session_state.products_df['Category'].unique(),
            default=[]
        )
    
    with col3:
        status_filter = st.multiselect(
            "Status",
            options=['Active', 'Discontinued'],
            default=['Active']
        )
    
    filtered_df = st.session_state.products_df.copy()
    
    if search:
        filtered_df = filtered_df[
            filtered_df['Product_Name'].str.contains(search, case=False) |
            filtered_df['Product_ID'].str.contains(search, case=False) |
            filtered_df['SKU'].str.contains(search, case=False)
        ]
    
    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    
    st.info(f"📊 Showing {len(filtered_df)} of {len(st.session_state.products_df)} products")
    
    for idx, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{row['Product_Name']}**")
                st.caption(f"ID: {row['Product_ID']} | SKU: {row['SKU']}")
            
            with col2:
                st.markdown(f"Category: {row['Category']}")
                st.markdown(f"Supplier: {row['Preferred_Supplier']}")
            
            with col3:
                st.markdown(f"Cost: ${row['Unit_Cost_BND']:.2f}")
                st.markdown(f"Price: ${row['Selling_Price_BND']:.2f}")
            
            with col4:
                st.markdown(f"Reorder: {row['Reorder_Level']}")
                status_class = "status-active" if row['Status'] == 'Active' else "status-discontinued"
                st.markdown(f"<span class='{status_class}'>{row['Status']}</span>", unsafe_allow_html=True)
            
            with col5:
                if st.button("✏️ Edit", key=f"edit_{row['Product_ID']}", use_container_width=True):
                    st.session_state.crud_mode = "edit"
                    st.session_state.editing_product = row['Product_ID']
                    st.rerun()
                
                delete_key = f"delete_{row['Product_ID']}"
                if delete_key not in st.session_state.delete_confirmation:
                    st.session_state.delete_confirmation[delete_key] = False
                
                if not st.session_state.delete_confirmation[delete_key]:
                    if st.button("🗑️ Delete", key=delete_key, use_container_width=True):
                        st.session_state.delete_confirmation[delete_key] = True
                        st.rerun()
                else:
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        if st.button("✅ Yes", key=f"confirm_{row['Product_ID']}", use_container_width=True):
                            deleted_name = delete_product(row['Product_ID'])
                            st.session_state.delete_confirmation[delete_key] = False
                            st.success(f"✅ Product '{deleted_name}' deleted successfully!")
                            time.sleep(1)
                            st.rerun()
                    with col_d2:
                        if st.button("❌ No", key=f"cancel_{row['Product_ID']}", use_container_width=True):
                            st.session_state.delete_confirmation[delete_key] = False
                            st.rerun()
            
            st.markdown("---")

# ============================================
# EXISTING PAGES
# ============================================

def show_executive_dashboard():
    st.header("Executive Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(st.session_state.products_df))
    with col2:
        total_inventory_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        st.metric("Inventory Value", f"${total_inventory_value:,.0f}")
    with col3:
        st.metric("Locations", st.session_state.inventory_df['Location'].nunique())
    with col4:
        pending_statuses = ['Confirmed', 'Sent', 'Draft', 'Shipped']
        pending_orders = len(st.session_state.purchase_orders_df[
            st.session_state.purchase_orders_df['Order_Status'].isin(pending_statuses)
        ])
        st.metric("Pending Orders", pending_orders)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Products by Category")
        category_data = st.session_state.products_df['Category'].value_counts()
        fig = px.pie(values=category_data.values, names=category_data.index)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Stock by Location")
        location_data = st.session_state.inventory_df.groupby('Location')['Quantity_On_Hand'].sum().reset_index()
        fig = px.bar(location_data, x='Location', y='Quantity_On_Hand',
                    color='Quantity_On_Hand', color_continuous_scale='Viridis')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_product_master():
    st.header("Product Master List")
    
    search = st.text_input("🔍 Search products...")
    category_filter = st.multiselect("Filter by Category:", st.session_state.products_df['Category'].unique())
    
    filtered_df = st.session_state.products_df
    if search:
        filtered_df = filtered_df[filtered_df['Product_Name'].str.contains(search, case=False)]
    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    
    st.dataframe(filtered_df, use_container_width=True)

def show_inventory_by_location():
    st.header("Multi-Location Inventory")
    
    location_filter = st.selectbox("Select Location:", ['All'] + list(st.session_state.inventory_df['Location'].unique()))
    
    if location_filter != 'All':
        display_df = st.session_state.inventory_df[st.session_state.inventory_df['Location'] == location_filter]
    else:
        display_df = st.session_state.inventory_df
    
    display_df = display_df.merge(st.session_state.products_df[['Product_ID', 'Product_Name', 'Category']], on='Product_ID')
    st.dataframe(display_df[['Product_ID', 'Product_Name', 'Category', 'Location', 'Quantity_On_Hand', 'Last_Updated']], 
                use_container_width=True)

def show_stock_transactions():
    st.header("Stock Transaction History")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        txn_type = st.multiselect("Transaction Type:", st.session_state.transactions_df['Transaction_Type'].unique())
    with col2:
        location_filter = st.multiselect("Location:", st.session_state.transactions_df['Location'].unique())
    with col3:
        product_search = st.text_input("Product Name:")
    
    filtered_txn = st.session_state.transactions_df
    if txn_type:
        filtered_txn = filtered_txn[filtered_txn['Transaction_Type'].isin(txn_type)]
    if location_filter:
        filtered_txn = filtered_txn[filtered_txn['Location'].isin(location_filter)]
    if product_search:
        filtered_txn = filtered_txn[filtered_txn['Product_Name'].str.contains(product_search, case=False)]
    
    st.dataframe(filtered_txn.sort_values('Date', ascending=False), use_container_width=True)

def show_purchase_orders():
    st.header("Purchase Order Management")
    
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect("Filter by Status:", st.session_state.purchase_orders_df['Order_Status'].unique())
    with col2:
        supplier_filter = st.multiselect("Filter by Supplier:", st.session_state.purchase_orders_df['Supplier_Name'].unique())
    
    filtered_po = st.session_state.purchase_orders_df
    if status_filter:
        filtered_po = filtered_po[filtered_po['Order_Status'].isin(status_filter)]
    if supplier_filter:
        filtered_po = filtered_po[filtered_po['Supplier_Name'].isin(supplier_filter)]
    
    st.dataframe(filtered_po.sort_values('Order_Date', ascending=False), use_container_width=True)

def show_supplier_directory():
    st.header("Supplier Directory")
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_stock_alerts():
    st.header("Automated Stock Alert System")
    
    stock_levels = st.session_state.inventory_df.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    stock_levels = stock_levels.merge(
        st.session_state.products_df[['Product_ID', 'Product_Name', 'Reorder_Level']], on='Product_ID'
    )
    
    def get_status(row):
        if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    stock_levels['Alert_Status'] = stock_levels.apply(get_status, axis=1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Critical", len(stock_levels[stock_levels['Alert_Status'] == 'CRITICAL']))
    col2.metric("Warning", len(stock_levels[stock_levels['Alert_Status'] == 'WARNING']))
    col3.metric("Normal", len(stock_levels[stock_levels['Alert_Status'] == 'NORMAL']))
    
    st.dataframe(stock_levels, use_container_width=True)

def show_visionify_ai():
    st.header("Visionify AI - Computer Vision Monitoring")
    st.info("Visionify AI provides computer vision solutions that integrate with existing CCTV systems for real-time inventory tracking and worker safety monitoring.")

def show_warehouse_assistant():
    st.header("Warehouse AI Assistant")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your inventory..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simple response based on keywords
        response = generate_ai_response(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_ai_response(prompt):
    """Generate AI response based on keywords"""
    prompt_lower = prompt.lower()
    
    if "inventory value" in prompt_lower:
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        return f"💰 Total inventory value: ${total_value:,.2f}"
    
    elif "low stock" in prompt_lower or "reorder" in prompt_lower:
        stock_levels = st.session_state.inventory_df.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
        stock_levels = stock_levels.merge(
            st.session_state.products_df[['Product_ID', 'Product_Name', 'Reorder_Level']], on='Product_ID'
        )
        low_stock = stock_levels[stock_levels['Quantity_On_Hand'] <= stock_levels['Reorder_Level']]
        if len(low_stock) > 0:
            return f"⚠️ {len(low_stock)} products need reordering. Check Stock Alerts page."
        else:
            return "✅ All stock levels are healthy!"
    
    elif "forecast" in prompt_lower or "demand" in prompt_lower:
        return "📈 Check the Demand Forecasting page for AI-powered predictions."
    
    elif "mobile" in prompt_lower or "app" in prompt_lower:
        return "📱 The mobile app is available for pickers, supervisors, and managers. Check the Mobile App Integration page."
    
    else:
        return "I can help with inventory queries, stock alerts, forecasts, and mobile app features. What would you like to know?"

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio("Select Module:", [
        "Executive Dashboard",
        "Product CRUD Dashboard",
        "Product Master List",
        "Inventory by Location",
        "Stock Transactions",
        "Purchase Orders",
        "Supplier Directory",
        "Stock Alert Monitoring",
        "Visionify AI Monitor",
        "Warehouse AI Assistant",
        "---",
        "AI Innovation 1: Smart Binning",
        "AI Innovation 2: Demand Forecasting",
        "AI Innovation 3: Vision Counting",
        "AI Innovation 4: Voice Picking",
        "AI Innovation 5: Predictive Maintenance",
        "AI Innovation 6: Dynamic Slotting",
        "AI Innovation 7: Cold Chain",
        "AI Innovation 8: Labor Optimization",
        "AI Innovation 9: Returns Management",
        "AI Innovation 10: Sustainability",
        "---",
        "Mobile App Integration"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Route to appropriate page
    if page == "Executive Dashboard":
        show_executive_dashboard()
    elif page == "Product CRUD Dashboard":
        show_product_crud_dashboard()
    elif page == "Product Master List":
        show_product_master()
    elif page == "Inventory by Location":
        show_inventory_by_location()
    elif page == "Stock Transactions":
        show_stock_transactions()
    elif page == "Purchase Orders":
        show_purchase_orders()
    elif page == "Supplier Directory":
        show_supplier_directory()
    elif page == "Stock Alert Monitoring":
        show_stock_alerts()
    elif page == "Visionify AI Monitor":
        show_visionify_ai()
    elif page == "Warehouse AI Assistant":
        show_warehouse_assistant()
    elif page == "AI Innovation 1: Smart Binning":
        show_smart_binning()
    elif page == "AI Innovation 2: Demand Forecasting":
        show_demand_forecasting()
    elif page == "AI Innovation 3: Vision Counting":
        show_vision_counting()
    elif page == "AI Innovation 4: Voice Picking":
        show_voice_picking()
    elif page == "AI Innovation 5: Predictive Maintenance":
        show_predictive_maintenance()
    elif page == "AI Innovation 6: Dynamic Slotting":
        show_dynamic_slotting()
    elif page == "AI Innovation 7: Cold Chain":
        show_cold_chain()
    elif page == "AI Innovation 8: Labor Optimization":
        show_labor_optimization()
    elif page == "AI Innovation 9: Returns Management":
        show_returns_management()
    elif page == "AI Innovation 10: Sustainability":
        show_sustainability()
    elif page == "Mobile App Integration":
        show_mobile_app()

if __name__ == "__main__":
    main()
