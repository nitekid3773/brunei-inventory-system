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

# Clean, beginner-friendly CSS
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
    
    /* Cards for metrics and info */
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
    
    /* Data tables */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Chat messages */
    .chat-user {
        background-color: #3498db;
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .chat-bot {
        background-color: #f0f2f6;
        color: #2c3e50;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    /* Divider */
    .divider {
        margin: 2rem 0;
        border-top: 1px solid #e0e0e0;
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

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data"""
    
    # Product Master List (50 products)
    products_data = [
        ['PRD00001', 'ELE9513', 8882629770, 'LED TV', 'Electronics', 785.00, 1135.09, 7, 'Supasave', 'Active', 'A3-12'],
        ['PRD00002', 'ELE6539', 8885034668, 'Smartphone', 'Electronics', 916.00, 1351.05, 35, 'Pohan Motors', 'Active', 'A3-08'],
        ['PRD00003', 'ELE5637', 8881920026, 'Laptop', 'Electronics', 618.00, 872.40, 25, 'Al-Falah Corporation', 'Active', 'A3-15'],
        ['PRD00004', 'ELE4243', 8887653820, 'Tablet', 'Electronics', 1960.00, 2653.80, 6, 'Hua Ho Trading', 'Active', 'A3-05'],
        ['PRD00005', 'ELE6781', 8881862054, 'Bluetooth Speaker', 'Electronics', 754.00, 907.19, 6, 'Soon Lee MegaMart', 'Active', 'A3-22'],
        ['PRD00006', 'GRO1086', 8888322742, 'Basmati Rice 5kg', 'Groceries', 8.00, 9.81, 18, 'Seng Huat', 'Active', 'B2-01'],
        ['PRD00007', 'GRO8871', 8889550421, 'Cooking Oil 2L', 'Groceries', 11.00, 14.28, 11, 'Al-Falah Corporation', 'Active', 'B2-04'],
        ['PRD00008', 'GRO5143', 8886941375, 'Sugar 1kg', 'Groceries', 47.00, 62.97, 46, 'Hua Ho Trading', 'Active', 'B2-07'],
        ['PRD00009', 'GRO6328', 8882079673, 'Flour 1kg', 'Groceries', 42.00, 58.50, 14, 'Hua Ho Trading', 'Active', 'B2-10'],
        ['PRD00010', 'GRO4921', 8882391650, 'Instant Noodles', 'Groceries', 3.00, 4.34, 50, 'Supasave', 'Active', 'B2-13'],
        ['PRD00011', 'HAR7985', 8884408841, 'Paint 5L', 'Hardware', 97.00, 116.66, 44, 'SKH Group', 'Active', 'C1-03'],
        ['PRD00012', 'HAR7642', 8882206083, 'Cement 40kg', 'Hardware', 56.00, 78.46, 34, 'Wee Hua Enterprise', 'Active', 'C1-06'],
        ['PRD00013', 'HAR3920', 8885403285, 'PVC Pipe', 'Hardware', 49.00, 71.86, 25, 'D\'Sunlit Supermarket', 'Active', 'C1-09'],
        ['PRD00014', 'HAR3822', 8881779092, 'Electrical Wire', 'Hardware', 37.00, 44.82, 5, 'SKH Group', 'Active', 'C1-12'],
        ['PRD00015', 'HAR5003', 8882343059, 'Light Bulb', 'Hardware', 8.00, 9.95, 36, 'SKH Group', 'Active', 'C1-15'],
        ['PRD00016', 'PHA7337', 8887613548, 'Paracetamol', 'Pharmaceuticals', 141.00, 189.88, 13, 'Al-Falah Corporation', 'Active', 'D2-02'],
        ['PRD00017', 'PHA2752', 8884040859, 'Cough Syrup', 'Pharmaceuticals', 6.00, 8.25, 14, 'Wee Hua Enterprise', 'Active', 'D2-05'],
        ['PRD00018', 'PHA3733', 8887351786, 'Vitamin C', 'Pharmaceuticals', 99.00, 121.28, 24, 'Al-Falah Corporation', 'Active', 'D2-08'],
        ['PRD00019', 'PHA3787', 8884640696, 'First Aid Kit', 'Pharmaceuticals', 47.00, 56.69, 5, 'SKH Group', 'Active', 'D2-11'],
        ['PRD00020', 'PHA4363', 8882862764, 'Bandages', 'Pharmaceuticals', 76.00, 110.20, 5, 'Supasave', 'Active', 'D2-14'],
        ['PRD00021', 'AUT3704', 8886967946, 'Engine Oil', 'Automotive', 185.00, 269.02, 12, 'D\'Sunlit Supermarket', 'Active', 'E1-04'],
        ['PRD00022', 'AUT9292', 8881721650, 'Car Battery', 'Automotive', 119.00, 167.34, 17, 'Joyful Mart', 'Active', 'E1-08'],
        ['PRD00023', 'AUT9310', 8885977758, 'Air Filter', 'Automotive', 160.00, 209.16, 49, 'Seng Huat', 'Active', 'E1-12'],
        ['PRD00024', 'AUT7977', 8884903306, 'Brake Pad', 'Automotive', 71.00, 100.99, 14, 'Al-Falah Corporation', 'Discontinued', 'E1-16'],
        ['PRD00025', 'AUT6650', 8881362520, 'Spark Plug', 'Automotive', 119.00, 168.95, 37, 'D\'Sunlit Supermarket', 'Active', 'E1-20'],
        ['PRD00026', 'TEX9302', 8882287897, 'School Uniform', 'Textiles', 43.00, 54.40, 46, 'Pohan Motors', 'Discontinued', 'F3-01'],
        ['PRD00027', 'TEX1181', 8883333480, 'Baju Kurung', 'Textiles', 111.00, 150.36, 43, 'SKH Group', 'Active', 'F3-05'],
        ['PRD00028', 'TEX8677', 8887970607, 'Baju Melayu', 'Textiles', 111.00, 152.78, 21, 'Wee Hua Enterprise', 'Active', 'F3-09'],
        ['PRD00029', 'TEX8913', 8883535721, 'Songkok', 'Textiles', 21.00, 26.51, 28, 'Wee Hua Enterprise', 'Active', 'F3-13'],
        ['PRD00030', 'TEX1792', 8882337786, 'Tudung', 'Textiles', 119.00, 173.22, 17, 'D\'Sunlit Supermarket', 'Active', 'F3-17'],
        ['PRD00031', 'FUR1215', 8886673723, 'Office Desk', 'Furniture', 91.00, 129.73, 26, 'D\'Sunlit Supermarket', 'Active', 'G2-04'],
        ['PRD00032', 'FUR6787', 8882195570, 'Ergonomic Chair', 'Furniture', 60.00, 88.18, 8, 'Supasave', 'Active', 'G2-08'],
        ['PRD00033', 'FUR5417', 8888670445, 'Filing Cabinet', 'Furniture', 128.00, 164.85, 40, 'Joyful Mart', 'Active', 'G2-12'],
        ['PRD00034', 'FUR3970', 8881510403, 'Bookshelf', 'Furniture', 46.00, 58.12, 31, 'Seng Huat', 'Active', 'G2-16'],
        ['PRD00035', 'FUR6963', 8883713384, 'Meeting Table', 'Furniture', 130.00, 188.59, 33, 'Al-Falah Corporation', 'Active', 'G2-20'],
        ['PRD00036', 'STA3134', 8883269795, 'A4 Paper', 'Stationery', 136.00, 190.82, 27, 'SKH Group', 'Active', 'H1-03'],
        ['PRD00037', 'STA1487', 8887250125, 'Printer Ink', 'Stationery', 129.00, 168.32, 14, 'Hua Ho Trading', 'Active', 'H1-07'],
        ['PRD00038', 'STA4935', 8882810353, 'Ballpoint Pen', 'Stationery', 131.00, 193.55, 36, 'Supasave', 'Active', 'H1-11'],
        ['PRD00039', 'STA6275', 8882205355, 'Notebook', 'Stationery', 101.00, 139.82, 48, 'Joyful Mart', 'Active', 'H1-15'],
        ['PRD00040', 'STA4686', 8884757367, 'Folder', 'Stationery', 56.00, 73.26, 27, 'Supasave', 'Active', 'H1-19'],
        ['PRD00041', 'BEV9661', 8882964355, 'Mineral Water', 'Beverages', 32.00, 41.07, 47, 'Supasave', 'Active', 'I2-02'],
        ['PRD00042', 'BEV4750', 8883937121, 'Soft Drinks', 'Beverages', 10.00, 12.46, 11, 'Pohan Motors', 'Active', 'I2-06'],
        ['PRD00043', 'BEV2188', 8882771996, 'Orange Juice', 'Beverages', 22.00, 26.73, 42, 'Supasave', 'Active', 'I2-10'],
        ['PRD00044', 'BEV2566', 8885056530, 'Energy Drink', 'Beverages', 7.00, 10.05, 37, 'D\'Sunlit Supermarket', 'Active', 'I2-14'],
        ['PRD00045', 'BEV2659', 8885907179, 'Milk', 'Beverages', 29.00, 42.27, 33, 'SKH Group', 'Active', 'I2-18'],
        ['PRD00046', 'COS4275', 8882812675, 'Facial Cleanser', 'Cosmetics', 23.00, 32.48, 49, 'Joyful Mart', 'Active', 'J1-05'],
        ['PRD00047', 'COS6234', 8881405934, 'Moisturizer', 'Cosmetics', 94.00, 138.40, 29, 'Hua Ho Trading', 'Active', 'J1-10'],
        ['PRD00048', 'COS4817', 8886216590, 'Lipstick', 'Cosmetics', 141.00, 179.42, 24, 'D\'Sunlit Supermarket', 'Active', 'J1-15'],
        ['PRD00049', 'COS9429', 8882217059, 'Foundation', 'Cosmetics', 80.00, 101.94, 20, 'Soon Lee MegaMart', 'Active', 'J1-20'],
        ['PRD00050', 'COS3684', 8888986667, 'Shampoo', 'Cosmetics', 88.00, 125.16, 16, 'SKH Group', 'Active', 'J1-25'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 
        'Unit_Cost_BND', 'Selling_Price_BND', 'Reorder_Level', 
        'Preferred_Supplier', 'Status', 'Bin_Location'
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
    for i in range(150):
        prod_idx = i % 50
        loc_idx = i % 5
        txn_type = ['ADJUSTMENT', 'STOCK IN', 'STOCK OUT'][i % 3]
        qty = 5 if txn_type == 'ADJUSTMENT' else (10 if txn_type == 'STOCK IN' else -5)
        
        transactions_data.append({
            'Transaction_ID': f'TRX2026{i:04d}',
            'Date': (datetime.now() - timedelta(days=150-i)).strftime('%Y-%m-%d'),
            'Product_ID': products_data[prod_idx][0],
            'Product_Name': products_data[prod_idx][3],
            'Transaction_Type': txn_type,
            'Quantity_Change': qty,
            'Location': locations[loc_idx]
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Suppliers
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', '673-2223456', 'purchasing@huaho.com', 'Kiulap', 'Net 30'],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', '673-2337890', 'orders@soonlee.com', 'Gadong', 'Net 30'],
        ['SUP003', 'Supasave', 'David Wong', '673-2456789', 'procurement@supasave.com', 'Serusop', 'Net 45'],
        ['SUP004', 'Seng Huat', 'Michael Chen', '673-2771234', 'sales@senghuat.com', 'Kuala Belait', 'Cash on Delivery'],
        ['SUP005', 'SKH Group', 'Steven Khoo', '673-2667890', 'trading@skh.com', 'Tutong', 'Net 30'],
        ['SUP006', 'Wee Hua Enterprise', 'Jason Wee', '673-2884567', 'orders@weehua.com', 'Seria', 'Net 30'],
        ['SUP007', 'Pohan Motors', 'Ahmad Pohan', '673-2334455', 'parts@pohan.com', 'Beribi', 'Cash on Delivery'],
        ['SUP008', 'D\'Sunlit', 'Hjh Zainab', '673-2656789', 'procurement@dsunlit.com', 'Menglait', 'Net 45'],
        ['SUP009', 'Joyful Mart', 'Liew KF', '673-2781234', 'supply@joyfulmart.com', 'Kiarong', 'Net 30'],
        ['SUP010', 'Al-Falah', 'Hj Osman', '673-2235678', 'trading@alfalah.com', 'Lambak Kanan', 'Cash on Delivery'],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Phone', 
        'Email', 'Address', 'Payment_Terms'
    ])
    
    # Purchase Orders
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
            'Unit_Cost_BND': products_data[prod_idx][5],
            'Total_Cost_BND': (100 + i * 10) * products_data[prod_idx][5],
            'Order_Date': (datetime.now() - timedelta(days=90-i*2)).strftime('%Y-%m-%d'),
            'Order_Status': random.choice(['Draft', 'Sent', 'Confirmed', 'Received'])
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Stock Alerts
    current_stock = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(products[['Product_ID', 'Product_Name', 'Reorder_Level']], on='Product_ID')
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    alerts['Alert_Status'] = alerts.apply(get_alert_status, axis=1)
    
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
# HELPER FUNCTIONS
# ============================================

def generate_product_id():
    existing_ids = st.session_state.products_df['Product_ID'].tolist()
    numbers = [int(id.replace('PRD', '')) for id in existing_ids]
    next_num = max(numbers) + 1
    return f"PRD{next_num:05d}"

def generate_sku(category):
    prefix = category[:3].upper()
    return f"{prefix}{random.randint(10000, 99999)}"

def generate_barcode():
    return int(f"888{random.randint(1000000, 9999999)}")

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
    return errors

def add_product(product_data):
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
    
    locations = ['Warehouse A', 'Store 1', 'Store 2', 'Store 3', 'Store 4']
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
    st.session_state.crud_mode = "view"
    st.session_state.editing_product = None

# ============================================
# CORE DASHBOARD PAGES
# ============================================

def show_executive_dashboard():
    st.markdown('<div class="section-header">Executive Dashboard</div>', unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(st.session_state.products_df)
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-value">{total_products}</div>
            <div class="metric-label">Total Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_inventory = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-value">{total_inventory:,}</div>
            <div class="metric-label">Items in Stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-value">${total_value:,.0f}</div>
            <div class="metric-label">Inventory Value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        locations = st.session_state.inventory_df['Location'].nunique()
        st.markdown(f"""
        <div class="info-card">
            <div class="metric-value">{locations}</div>
            <div class="metric-label">Locations</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Products by Category")
        category_data = st.session_state.products_df['Category'].value_counts()
        fig = px.pie(values=category_data.values, names=category_data.index)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Stock by Location")
        location_data = st.session_state.inventory_df.groupby('Location')['Quantity_On_Hand'].sum().reset_index()
        fig = px.bar(location_data, x='Location', y='Quantity_On_Hand')
        st.plotly_chart(fig, use_container_width=True)

def show_product_crud():
    st.markdown('<div class="section-header">Product Management</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", len(st.session_state.products_df))
    col2.metric("Active Products", len(st.session_state.products_df[st.session_state.products_df['Status'] == 'Active']))
    col3.metric("Categories", st.session_state.products_df['Category'].nunique())
    col4.metric("Suppliers", st.session_state.suppliers_df['Supplier_Name'].nunique())
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        if st.button("➕ Add New", use_container_width=True):
            st.session_state.crud_mode = "add"
            st.rerun()
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Add/Edit forms
    if st.session_state.crud_mode == "add":
        with st.form("add_product_form"):
            st.subheader("Add New Product")
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name *")
                category = st.selectbox("Category *", 
                    ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                     'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                     'Beverages', 'Cosmetics'])
            
            with col2:
                unit_cost = st.number_input("Unit Cost *", min_value=0.01, value=100.00)
                selling_price = st.number_input("Selling Price *", min_value=0.01, value=150.00)
                reorder_level = st.number_input("Reorder Level *", min_value=1, value=10)
            
            preferred_supplier = st.selectbox("Preferred Supplier *", 
                st.session_state.suppliers_df['Supplier_Name'].tolist())
            status = st.selectbox("Status", ['Active', 'Discontinued'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Product"):
                    if not product_name:
                        st.error("Product Name is required!")
                    elif selling_price <= unit_cost:
                        st.error("Selling Price must be greater than Unit Cost!")
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
                            st.success(f"Product added! ID: {result}")
                            time.sleep(1)
                            reset_crud_mode()
                            st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    reset_crud_mode()
                    st.rerun()
    
    elif st.session_state.crud_mode == "edit" and st.session_state.editing_product:
        product = st.session_state.products_df[
            st.session_state.products_df['Product_ID'] == st.session_state.editing_product
        ].iloc[0]
        
        with st.form("edit_product_form"):
            st.subheader(f"Edit Product: {product['Product_Name']}")
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name *", value=product['Product_Name'])
                category = st.selectbox("Category *",
                    ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                     'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                     'Beverages', 'Cosmetics'],
                    index=['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                           'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                           'Beverages', 'Cosmetics'].index(product['Category']))
            
            with col2:
                unit_cost = st.number_input("Unit Cost *", value=float(product['Unit_Cost_BND']))
                selling_price = st.number_input("Selling Price *", value=float(product['Selling_Price_BND']))
                reorder_level = st.number_input("Reorder Level *", value=int(product['Reorder_Level']))
            
            suppliers = st.session_state.suppliers_df['Supplier_Name'].tolist()
            preferred_supplier = st.selectbox("Preferred Supplier *", suppliers,
                index=suppliers.index(product['Preferred_Supplier']))
            status = st.selectbox("Status", ['Active', 'Discontinued'],
                index=0 if product['Status'] == 'Active' else 1)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Update Product"):
                    if not product_name:
                        st.error("Product Name is required!")
                    elif selling_price <= unit_cost:
                        st.error("Selling Price must be greater than Unit Cost!")
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
                        success, _ = update_product(st.session_state.editing_product, updated_data)
                        if success:
                            st.success("Product updated!")
                            time.sleep(1)
                            reset_crud_mode()
                            st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    reset_crud_mode()
                    st.rerun()
    
    else:
        # Product list view
        search = st.text_input("🔍 Search by name, ID, or SKU", placeholder="Type to search...")
        
        filtered_df = st.session_state.products_df
        if search:
            filtered_df = filtered_df[
                filtered_df['Product_Name'].str.contains(search, case=False) |
                filtered_df['Product_ID'].str.contains(search, case=False) |
                filtered_df['SKU'].str.contains(search, case=False)
            ]
        
        st.info(f"Showing {len(filtered_df)} of {len(st.session_state.products_df)} products")
        
        for _, row in filtered_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.write(f"**{row['Product_Name']}**")
                st.caption(f"{row['Product_ID']} | SKU: {row['SKU']}")
            
            with col2:
                st.write(f"Category: {row['Category']}")
                st.write(f"Supplier: {row['Preferred_Supplier']}")
            
            with col3:
                st.write(f"Cost: ${row['Unit_Cost_BND']:.2f}")
                st.write(f"Price: ${row['Selling_Price_BND']:.2f}")
            
            with col4:
                st.write(f"Reorder: {row['Reorder_Level']}")
                badge_class = "badge-active" if row['Status'] == 'Active' else "badge-inactive"
                st.markdown(f"<span class='{badge_class}'>{row['Status']}</span>", unsafe_allow_html=True)
            
            with col5:
                if st.button("✏️ Edit", key=f"edit_{row['Product_ID']}", use_container_width=True):
                    st.session_state.crud_mode = "edit"
                    st.session_state.editing_product = row['Product_ID']
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
                            st.success(f"Deleted: {deleted}")
                            time.sleep(1)
                            st.rerun()
                    with col_d2:
                        if st.button("✗ No", key=f"can_{row['Product_ID']}", use_container_width=True):
                            st.session_state.delete_confirmation[delete_key] = False
                            st.rerun()
            
            st.markdown("---")

def show_product_list():
    st.markdown('<div class="section-header">Product Master List</div>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search products...")
    category = st.multiselect("Filter by Category", st.session_state.products_df['Category'].unique())
    
    filtered_df = st.session_state.products_df
    if search:
        filtered_df = filtered_df[filtered_df['Product_Name'].str.contains(search, case=False)]
    if category:
        filtered_df = filtered_df[filtered_df['Category'].isin(category)]
    
    st.dataframe(filtered_df, use_container_width=True)

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
    
    col1, col2 = st.columns(2)
    with col1:
        txn_type = st.multiselect("Transaction Type", st.session_state.transactions_df['Transaction_Type'].unique())
    with col2:
        location = st.multiselect("Location", st.session_state.transactions_df['Location'].unique())
    
    filtered_df = st.session_state.transactions_df
    if txn_type:
        filtered_df = filtered_df[filtered_df['Transaction_Type'].isin(txn_type)]
    if location:
        filtered_df = filtered_df[filtered_df['Location'].isin(location)]
    
    st.dataframe(filtered_df.sort_values('Date', ascending=False), use_container_width=True)

def show_purchase_orders():
    st.markdown('<div class="section-header">Purchase Orders</div>', unsafe_allow_html=True)
    
    status_filter = st.multiselect("Filter by Status", st.session_state.purchase_orders_df['Order_Status'].unique())
    
    filtered_df = st.session_state.purchase_orders_df
    if status_filter:
        filtered_df = filtered_df[filtered_df['Order_Status'].isin(status_filter)]
    
    st.dataframe(filtered_df.sort_values('Order_Date', ascending=False), use_container_width=True)

def show_suppliers():
    st.markdown('<div class="section-header">Suppliers</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">Stock Alerts</div>', unsafe_allow_html=True)
    
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

def show_visionify():
    st.markdown('<div class="section-header">Visionify AI</div>', unsafe_allow_html=True)
    st.info("Visionify AI provides computer vision solutions that integrate with existing CCTV systems for real-time inventory tracking and worker safety monitoring.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Features:**
        - Real-time stock counting
        - Shelf empty detection
        - Personnel safety monitoring
        - Theft prevention alerts
        """)
    with col2:
        st.metric("Cameras Connected", "8", "+2 this month")
        st.metric("AI Detections", "1,247", "+12.3%")

def show_ai_assistant():
    st.markdown('<div class="section-header">AI Assistant</div>', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your inventory..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simple responses
        response = "I can help with inventory queries. Try asking about stock levels, products, or suppliers."
        if "stock" in prompt.lower():
            total = st.session_state.inventory_df['Quantity_On_Hand'].sum()
            response = f"Total items in stock: {total:,}"
        elif "product" in prompt.lower():
            response = f"Total products: {len(st.session_state.products_df)}"
        elif "value" in prompt.lower():
            value = (st.session_state.inventory_df.merge(
                st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
            ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
            response = f"Total inventory value: ${value:,.2f}"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ============================================
# AI INNOVATIONS (Grouped under one category)
# ============================================

def show_ai_innovations():
    st.markdown('<div class="section-header">AI Innovations</div>', unsafe_allow_html=True)
    
    # Create tabs for each AI innovation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Smart Binning", 
        "Demand Forecasting", 
        "Vision Counting", 
        "Cold Chain", 
        "Returns Management"
    ])
    
    with tab1:
        st.subheader("Smart Bin Location Optimizer")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Current Layout Efficiency: 67%**
            
            **AI Recommendations:**
            - Move fast-moving items near shipping
            - Group frequently ordered items together
            - Place heavy items at waist height
            """)
            
            if st.button("Optimize Layout"):
                st.success("Layout optimized! Expected travel time reduction: 23%")
        
        with col2:
            # Sample velocity data
            velocity_data = pd.DataFrame({
                'Product': ['LED TV', 'Rice 5kg', 'Cooking Oil', 'Smartphone', 'Mineral Water'],
                'Daily Movement': [45, 38, 32, 28, 25]
            })
            fig = px.bar(velocity_data, x='Product', y='Daily Movement', 
                        title="Fast-Moving Items")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Demand Forecasting")
        
        # Generate forecast data
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast = pd.DataFrame({
            'Date': dates,
            'Rice': [120 + 20*np.sin(i/7) + random.randint(-5,5) for i in range(30)],
            'Oil': [85 + 15*np.sin(i/7) + random.randint(-3,3) for i in range(30)],
            'TV': [45 + 10*np.sin(i/14) + random.randint(-2,2) for i in range(30)]
        })
        
        fig = px.line(forecast, x='Date', y=['Rice', 'Oil', 'TV'],
                     title="30-Day Demand Forecast")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Forecast Insights:**
        - Rice demand expected to increase by 22% next week
        - Electronics demand stable
        - Prepare for Hari Raya peak in 4 weeks
        """)
    
    with tab3:
        st.subheader("Vision Counting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Camera 1 - Aisle A3 (Electronics)**
            - LED TVs detected: 23 (System: 25)
            - Smartphones: 42 (System: 40)
            - Accuracy: 94.5%
            """)
        
        with col2:
            st.markdown("""
            **Camera 2 - Aisle B7 (Groceries)**
            - Rice pallets: 18 (System: 18)
            - Cooking Oil: 32 (System: 32)
            - Accuracy: 98.2%
            """)
        
        if st.button("Run Full Count"):
            with st.spinner("AI analyzing camera feeds..."):
                time.sleep(2)
                st.success("Count complete! 99.2% accuracy overall")
    
    with tab4:
        st.subheader("Cold Chain Monitoring")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Temperature Zones:**
            - Pharma Freezer (-20°C): ✅ -19.8°C
            - Chiller (4°C): ⚠️ 4.2°C
            - Cool Room (15°C): ✅ 15.5°C
            - Ambient (25°C): ✅ 25.1°C
            """)
        
        with col2:
            st.warning("""
            **Alert: Chiller temperature trending up**
            - Current: 4.2°C (target: 2-4°C)
            - Check door seals
            - Schedule maintenance
            """)
        
        # Temperature trend
        temp_data = pd.DataFrame({
            'Hour': list(range(24)),
            'Temperature': [4.0 + 0.5*np.sin(i/12) + 0.1*random.random() for i in range(24)]
        })
        fig = px.line(temp_data, x='Hour', y='Temperature', 
                     title="Chiller Temperature (Last 24h)")
        fig.add_hline(y=4, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("Returns Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            returns_data = pd.DataFrame({
                'Product': ['LED TV', 'Smartphone', 'Rice 5kg', 'Engine Oil'],
                'Qty': [3, 8, 12, 5],
                'Reason': ['Damaged', 'Defective', 'Expired', 'Wrong item'],
                'Value': [2355, 7200, 96, 375]
            })
            st.dataframe(returns_data, use_container_width=True)
        
        with col2:
            st.markdown("""
            **AI Insights:**
            - Smartphone returns spike after updates
            - Rice expiry in monsoon months
            - TV damage during afternoon shifts
            
            **Recovered Value:** $12,450 (+18% vs last month)
            """)
        
        # Returns trend
        returns_trend = pd.DataFrame({
            'Week': ['W1', 'W2', 'W3', 'W4'],
            'Returns': [4500, 5200, 6100, 5800],
            'Recovered': [3200, 4100, 5200, 4900]
        })
        fig = px.bar(returns_trend, x='Week', y=['Returns', 'Recovered'],
                    title="Returns vs Recovery Value",
                    barmode='group')
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    # Simple sidebar navigation
    st.sidebar.title("Menu")
    
    page = st.sidebar.radio("Select Page:", [
        "Executive Dashboard",
        "Product Management",
        "Product List",
        "Inventory by Location",
        "Stock Transactions",
        "Purchase Orders",
        "Suppliers",
        "Stock Alerts",
        "Visionify AI",
        "AI Assistant",
        "AI Innovations"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    
    # Page routing
    if page == "Executive Dashboard":
        show_executive_dashboard()
    elif page == "Product Management":
        show_product_crud()
    elif page == "Product List":
        show_product_list()
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
    elif page == "Visionify AI":
        show_visionify()
    elif page == "AI Assistant":
        show_ai_assistant()
    elif page == "AI Innovations":
        show_ai_innovations()

if __name__ == "__main__":
    main()
