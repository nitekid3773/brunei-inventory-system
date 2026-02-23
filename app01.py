import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import re

# Page configuration
st.set_page_config(
    page_title="Brunei Smart Inventory System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Brunei theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        background: linear-gradient(90deg, #FFD700 0%, #000000 50%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
    }
    
    /* CRUD Dashboard Specific Styles */
    .crud-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .crud-header {
        background: linear-gradient(135deg, #FFD700 0%, #000000 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #FFD700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .status-active {
        background-color: #00cc66;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-discontinued {
        background-color: #ff4444;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .edit-form {
        background-color: #e9ecef;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #00cc66;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .warning-message {
        background-color: #ffa500;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    
    .brunei-flag {
        text-align: center;
        font-size: 3rem;
    }
    
    .stButton>button {
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: black;
        color: #FFD700;
        border: 1px solid #FFD700;
    }
    
    .delete-btn>button {
        background-color: #ff4444;
        color: white;
    }
    
    .delete-btn>button:hover {
        background-color: #cc0000;
        color: white;
    }
    
    .edit-btn>button {
        background-color: #00cc66;
        color: white;
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
    st.session_state.crud_mode = "view"  # view, add, edit
if 'editing_product' not in st.session_state:
    st.session_state.editing_product = None
if 'delete_confirmation' not in st.session_state:
    st.session_state.delete_confirmation = {}

@st.cache_data(ttl=300)
def load_initial_data():
    """
    Load initial data from Excel file structure
    """
    
    # Product Master List (50 products)
    products_data = [
        ['PRD00001', 'ELE9513', 8882629770, 'LED TV', 'Electronics', 785.00, 1135.09, 7, 'Supasave', 'Active'],
        ['PRD00002', 'ELE6539', 8885034668, 'Smartphone', 'Electronics', 916.00, 1351.05, 35, 'Pohan Motors', 'Active'],
        ['PRD00003', 'ELE5637', 8881920026, 'Laptop', 'Electronics', 618.00, 872.40, 25, 'Al-Falah Corporation', 'Active'],
        ['PRD00004', 'ELE4243', 8887653820, 'Tablet', 'Electronics', 1960.00, 2653.80, 6, 'Hua Ho Trading', 'Active'],
        ['PRD00005', 'ELE6781', 8881862054, 'Bluetooth Speaker', 'Electronics', 754.00, 907.19, 6, 'Soon Lee MegaMart', 'Active'],
        ['PRD00006', 'GRO1086', 8888322742, 'Basmati Rice 5kg', 'Groceries', 8.00, 9.81, 18, 'Seng Huat', 'Active'],
        ['PRD00007', 'GRO8871', 8889550421, 'Cooking Oil 2L', 'Groceries', 11.00, 14.28, 11, 'Al-Falah Corporation', 'Active'],
        ['PRD00008', 'GRO5143', 8886941375, 'Sugar 1kg', 'Groceries', 47.00, 62.97, 46, 'Hua Ho Trading', 'Active'],
        ['PRD00009', 'GRO6328', 8882079673, 'Flour 1kg', 'Groceries', 42.00, 58.50, 14, 'Hua Ho Trading', 'Active'],
        ['PRD00010', 'GRO4921', 8882391650, 'Instant Noodles', 'Groceries', 3.00, 4.34, 50, 'Supasave', 'Active'],
        ['PRD00011', 'HAR7985', 8884408841, 'Paint 5L', 'Hardware', 97.00, 116.66, 44, 'SKH Group', 'Active'],
        ['PRD00012', 'HAR7642', 8882206083, 'Cement 40kg', 'Hardware', 56.00, 78.46, 34, 'Wee Hua Enterprise', 'Active'],
        ['PRD00013', 'HAR3920', 8885403285, 'PVC Pipe', 'Hardware', 49.00, 71.86, 25, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00014', 'HAR3822', 8881779092, 'Electrical Wire', 'Hardware', 37.00, 44.82, 5, 'SKH Group', 'Active'],
        ['PRD00015', 'HAR5003', 8882343059, 'Light Bulb', 'Hardware', 8.00, 9.95, 36, 'SKH Group', 'Active'],
        ['PRD00016', 'PHA7337', 8887613548, 'Paracetamol', 'Pharmaceuticals', 141.00, 189.88, 13, 'Al-Falah Corporation', 'Active'],
        ['PRD00017', 'PHA2752', 8884040859, 'Cough Syrup', 'Pharmaceuticals', 6.00, 8.25, 14, 'Wee Hua Enterprise', 'Active'],
        ['PRD00018', 'PHA3733', 8887351786, 'Vitamin C', 'Pharmaceuticals', 99.00, 121.28, 24, 'Al-Falah Corporation', 'Active'],
        ['PRD00019', 'PHA3787', 8884640696, 'First Aid Kit', 'Pharmaceuticals', 47.00, 56.69, 5, 'SKH Group', 'Active'],
        ['PRD00020', 'PHA4363', 8882862764, 'Bandages', 'Pharmaceuticals', 76.00, 110.20, 5, 'Supasave', 'Active'],
        ['PRD00021', 'AUT3704', 8886967946, 'Engine Oil', 'Automotive', 185.00, 269.02, 12, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00022', 'AUT9292', 8881721650, 'Car Battery', 'Automotive', 119.00, 167.34, 17, 'Joyful Mart', 'Active'],
        ['PRD00023', 'AUT9310', 8885977758, 'Air Filter', 'Automotive', 160.00, 209.16, 49, 'Seng Huat', 'Active'],
        ['PRD00024', 'AUT7977', 8884903306, 'Brake Pad', 'Automotive', 71.00, 100.99, 14, 'Al-Falah Corporation', 'Discontinued'],
        ['PRD00025', 'AUT6650', 8881362520, 'Spark Plug', 'Automotive', 119.00, 168.95, 37, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00026', 'TEX9302', 8882287897, 'School Uniform', 'Textiles', 43.00, 54.40, 46, 'Pohan Motors', 'Discontinued'],
        ['PRD00027', 'TEX1181', 8883333480, 'Baju Kurung', 'Textiles', 111.00, 150.36, 43, 'SKH Group', 'Active'],
        ['PRD00028', 'TEX8677', 8887970607, 'Baju Melayu', 'Textiles', 111.00, 152.78, 21, 'Wee Hua Enterprise', 'Active'],
        ['PRD00029', 'TEX8913', 8883535721, 'Songkok', 'Textiles', 21.00, 26.51, 28, 'Wee Hua Enterprise', 'Active'],
        ['PRD00030', 'TEX1792', 8882337786, 'Tudung', 'Textiles', 119.00, 173.22, 17, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00031', 'FUR1215', 8886673723, 'Office Desk', 'Furniture', 91.00, 129.73, 26, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00032', 'FUR6787', 8882195570, 'Ergonomic Chair', 'Furniture', 60.00, 88.18, 8, 'Supasave', 'Active'],
        ['PRD00033', 'FUR5417', 8888670445, 'Filing Cabinet', 'Furniture', 128.00, 164.85, 40, 'Joyful Mart', 'Active'],
        ['PRD00034', 'FUR3970', 8881510403, 'Bookshelf', 'Furniture', 46.00, 58.12, 31, 'Seng Huat', 'Active'],
        ['PRD00035', 'FUR6963', 8883713384, 'Meeting Table', 'Furniture', 130.00, 188.59, 33, 'Al-Falah Corporation', 'Active'],
        ['PRD00036', 'STA3134', 8883269795, 'A4 Paper', 'Stationery', 136.00, 190.82, 27, 'SKH Group', 'Active'],
        ['PRD00037', 'STA1487', 8887250125, 'Printer Ink', 'Stationery', 129.00, 168.32, 14, 'Hua Ho Trading', 'Active'],
        ['PRD00038', 'STA4935', 8882810353, 'Ballpoint Pen', 'Stationery', 131.00, 193.55, 36, 'Supasave', 'Active'],
        ['PRD00039', 'STA6275', 8882205355, 'Notebook', 'Stationery', 101.00, 139.82, 48, 'Joyful Mart', 'Active'],
        ['PRD00040', 'STA4686', 8884757367, 'Folder', 'Stationery', 56.00, 73.26, 27, 'Supasave', 'Active'],
        ['PRD00041', 'BEV9661', 8882964355, 'Mineral Water', 'Beverages', 32.00, 41.07, 47, 'Supasave', 'Active'],
        ['PRD00042', 'BEV4750', 8883937121, 'Soft Drinks', 'Beverages', 10.00, 12.46, 11, 'Pohan Motors', 'Active'],
        ['PRD00043', 'BEV2188', 8882771996, 'Orange Juice', 'Beverages', 22.00, 26.73, 42, 'Supasave', 'Active'],
        ['PRD00044', 'BEV2566', 8885056530, 'Energy Drink', 'Beverages', 7.00, 10.05, 37, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00045', 'BEV2659', 8885907179, 'Milk', 'Beverages', 29.00, 42.27, 33, 'SKH Group', 'Active'],
        ['PRD00046', 'COS4275', 8882812675, 'Facial Cleanser', 'Cosmetics', 23.00, 32.48, 49, 'Joyful Mart', 'Active'],
        ['PRD00047', 'COS6234', 8881405934, 'Moisturizer', 'Cosmetics', 94.00, 138.40, 29, 'Hua Ho Trading', 'Active'],
        ['PRD00048', 'COS4817', 8886216590, 'Lipstick', 'Cosmetics', 141.00, 179.42, 24, 'D\'Sunlit Supermarket', 'Active'],
        ['PRD00049', 'COS9429', 8882217059, 'Foundation', 'Cosmetics', 80.00, 101.94, 20, 'Soon Lee MegaMart', 'Active'],
        ['PRD00050', 'COS3684', 8888986667, 'Shampoo', 'Cosmetics', 88.00, 125.16, 16, 'SKH Group', 'Active'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 
        'Unit_Cost_BND', 'Selling_Price_BND', 'Reorder_Level', 
        'Preferred_Supplier', 'Status'
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
            'Date': (datetime.now() - pd.Timedelta(days=150-i)).strftime('%Y-%m-%d'),
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
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', '673-2223456', 'purchasing@huaho.com.bn', 'KG Kiulap, Bandar Seri Begawan', 'Cash on Delivery'],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', '673-2337890', 'orders@soonlee.com.bn', 'Gadong Central, BSB', 'Cash on Delivery'],
        ['SUP003', 'Supasave', 'David Wong', '673-2456789', 'procurement@supasave.com.bn', 'Serusop, BSB', 'Net 45'],
        ['SUP004', 'Seng Huat', 'Michael Chen', '673-2771234', 'sales@senghuat.com.bn', 'Kuala Belait', 'Cash on Delivery'],
        ['SUP005', 'SKH Group', 'Steven Khoo', '673-2667890', 'trading@skh.com.bn', 'Tutong Town', 'Net 30'],
        ['SUP006', 'Wee Hua Enterprise', 'Jason Wee', '673-2884567', 'orders@weehua.com.bn', 'Seria', 'Net 30'],
        ['SUP007', 'Pohan Motors', 'Ahmad Pohan', '673-2334455', 'parts@pohan.com.bn', 'Beribi Industrial Park', 'Cash on Delivery'],
        ['SUP008', 'D\'Sunlit Supermarket', 'Hjh Zainab', '673-2656789', 'procurement@dsunlit.com.bn', 'Menglait, BSB', 'Cash on Delivery'],
        ['SUP009', 'Joyful Mart', 'Liew KF', '673-2781234', 'supply@joyfulmart.com.bn', 'Kiarong', 'Net 45'],
        ['SUP010', 'Al-Falah Corporation', 'Hj Osman', '673-2235678', 'trading@alfalah.com.bn', 'Lambak Kanan', 'Cash on Delivery'],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Phone', 
        'Email', 'Address', 'Payment_Terms'
    ])
    
    # Purchase Orders
    po_status = [
        'Confirmed', 'Received', 'Received', 'Received', 'Cancelled',
        'Sent', 'Shipped', 'Sent', 'Sent', 'Sent',
        'Sent', 'Confirmed', 'Draft', 'Confirmed', 'Shipped',
        'Shipped', 'Cancelled', 'Sent', 'Shipped', 'Shipped',
        'Cancelled', 'Confirmed', 'Shipped', 'Sent', 'Cancelled',
        'Confirmed', 'Confirmed', 'Shipped', 'Shipped', 'Cancelled',
        'Received', 'Received', 'Received', 'Received', 'Sent',
        'Sent', 'Cancelled', 'Shipped', 'Draft', 'Draft'
    ]
    
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
            'Order_Date': (datetime.now() - pd.Timedelta(days=90-i*2)).strftime('%Y-%m-%d'),
            'Expected_Date': (datetime.now() + pd.Timedelta(days=30-i)).strftime('%Y-%m-%d'),
            'Order_Status': po_status[i]
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Stock Alert Monitoring
    current_stock = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(products[['Product_ID', 'Product_Name', 'Category', 'Reorder_Level']], on='Product_ID')
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return '🔴 CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return '🟡 WARNING'
        else:
            return '🟢 NORMAL'
    
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
    import random
    return f"{prefix}{random.randint(10000, 99999)}"

def generate_barcode():
    """Generate a new barcode"""
    import random
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
    # Validate data
    errors = validate_product_data(product_data)
    if errors:
        return False, errors
    
    # Generate IDs
    product_data['Product_ID'] = generate_product_id()
    if not product_data.get('SKU'):
        product_data['SKU'] = generate_sku(product_data['Category'])
    if not product_data.get('Barcode'):
        product_data['Barcode'] = generate_barcode()
    
    # Add to products dataframe
    st.session_state.products_df = pd.concat(
        [st.session_state.products_df, pd.DataFrame([product_data])], 
        ignore_index=True
    )
    
    # Add initial inventory for all locations
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
    # Validate data
    errors = validate_product_data(updated_data)
    if errors:
        return False, errors
    
    # Find the product
    mask = st.session_state.products_df['Product_ID'] == product_id
    
    # Update fields
    for key, value in updated_data.items():
        if value is not None and key in st.session_state.products_df.columns:
            st.session_state.products_df.loc[mask, key] = value
    
    # Update product name in related tables
    if 'Product_Name' in updated_data:
        # Update transactions
        st.session_state.transactions_df.loc[
            st.session_state.transactions_df['Product_ID'] == product_id, 'Product_Name'
        ] = updated_data['Product_Name']
        
        # Update purchase orders
        st.session_state.purchase_orders_df.loc[
            st.session_state.purchase_orders_df['Product_ID'] == product_id, 'Product_Name'
        ] = updated_data['Product_Name']
    
    st.session_state.last_update = datetime.now()
    return True, None

def delete_product(product_id):
    """Delete a product and all related records"""
    # Get product name for confirmation
    product_name = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] == product_id
    ]['Product_Name'].values[0]
    
    # Remove from products
    st.session_state.products_df = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] != product_id
    ]
    
    # Remove from inventory
    st.session_state.inventory_df = st.session_state.inventory_df[
        st.session_state.inventory_df['Product_ID'] != product_id
    ]
    
    # Remove from transactions
    st.session_state.transactions_df = st.session_state.transactions_df[
        st.session_state.transactions_df['Product_ID'] != product_id
    ]
    
    # Remove from purchase orders
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
# CRUD DASHBOARD UI
# ============================================

def show_product_crud_dashboard():
    """Main CRUD dashboard for product management"""
    
    st.markdown("""
    <div class="crud-header">
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
    <div class="crud-container">
        <h2 style="color: #FFD700; margin-bottom: 1.5rem;">➕ Add New Product</h2>
    """, unsafe_allow_html=True)
    
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name *", 
                placeholder="Enter product name",
                help="Required field"
            )
            
            category = st.selectbox(
                "Category *",
                ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                 'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                 'Beverages', 'Cosmetics'],
                help="Select product category"
            )
            
            # Auto-generated fields
            st.text_input(
                "SKU (Auto-generated)", 
                value=generate_sku(category if 'category' in locals() else 'Electronics'),
                disabled=True,
                help="Will be generated automatically"
            )
            
            st.text_input(
                "Barcode (Auto-generated)", 
                value=str(generate_barcode()),
                disabled=True,
                help="Will be generated automatically"
            )
        
        with col2:
            unit_cost = st.number_input(
                "Unit Cost (BND) *", 
                min_value=0.01, 
                value=100.00, 
                step=10.00,
                format="%.2f",
                help="Cost price in Brunei Dollar"
            )
            
            selling_price = st.number_input(
                "Selling Price (BND) *", 
                min_value=0.01, 
                value=150.00, 
                step=10.00,
                format="%.2f",
                help="Retail price in Brunei Dollar"
            )
            
            reorder_level = st.number_input(
                "Reorder Level *", 
                min_value=1, 
                value=10, 
                step=1,
                help="Minimum stock level before reordering"
            )
            
            # Supplier selection
            suppliers = st.session_state.suppliers_df['Supplier_Name'].tolist()
            preferred_supplier = st.selectbox(
                "Preferred Supplier *", 
                suppliers,
                help="Select preferred supplier for this product"
            )
            
            status = st.selectbox(
                "Status", 
                ['Active', 'Discontinued'],
                help="Product status"
            )
        
        # Submit buttons
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
                # Prepare product data
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
                
                # Add to database
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
    
    # Get current product data
    product = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] == product_id
    ].iloc[0]
    
    st.markdown(f"""
    <div class="crud-container">
        <h2 style="color: #FFD700; margin-bottom: 1.5rem;">✏️ Edit Product: {product['Product_Name']}</h2>
        <p style="margin-bottom: 1rem;"><strong>Product ID:</strong> {product_id}</p>
    """, unsafe_allow_html=True)
    
    with st.form("edit_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name *", 
                value=product['Product_Name'],
                help="Required field"
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
            
            # Read-only fields
            st.text_input("SKU", value=product['SKU'], disabled=True)
            st.text_input("Barcode", value=str(product['Barcode']), disabled=True)
        
        with col2:
            unit_cost = st.number_input(
                "Unit Cost (BND) *", 
                min_value=0.01, 
                value=float(product['Unit_Cost_BND']), 
                step=10.00,
                format="%.2f"
            )
            
            selling_price = st.number_input(
                "Selling Price (BND) *", 
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
            
            # Supplier selection
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
        
        # Submit buttons
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
                # Prepare updated data
                updated_data = {
                    'Product_Name': product_name,
                    'Category': category,
                    'Unit_Cost_BND': unit_cost,
                    'Selling_Price_BND': selling_price,
                    'Reorder_Level': reorder_level,
                    'Preferred_Supplier': preferred_supplier,
                    'Status': status
                }
                
                # Update in database
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
    
    # Search and filter
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
    
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    
    # Show results count
    st.info(f"📊 Showing {len(filtered_df)} of {len(st.session_state.products_df)} products")
    
    # Display products in cards
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
                st.markdown(f"**Cost:** BND ${row['Unit_Cost_BND']:.2f}")
                st.markdown(f"**Price:** BND ${row['Selling_Price_BND']:.2f}")
            
            with col4:
                st.markdown(f"Reorder: {row['Reorder_Level']}")
                status_class = "status-active" if row['Status'] == 'Active' else "status-discontinued"
                st.markdown(f"<span class='{status_class}'>{row['Status']}</span>", unsafe_allow_html=True)
            
            with col5:
                # Edit button
                if st.button("✏️ Edit", key=f"edit_{row['Product_ID']}", use_container_width=True):
                    st.session_state.crud_mode = "edit"
                    st.session_state.editing_product = row['Product_ID']
                    st.rerun()
                
                # Delete button with confirmation
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
# MAIN APP
# ============================================

def main():
    # Header
    st.markdown('<div class="brunei-flag">🇧🇳</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">BRUNEI DARUSSALAM<br>Smart Inventory Management System</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Select Module:", [
        "🏠 Executive Dashboard",
        "📝 Product CRUD Dashboard",  # New dedicated CRUD page
        "📦 Product Master List",
        "📍 Inventory by Location",
        "🔄 Stock Transactions",
        "🚚 Purchase Orders",
        "🏢 Supplier Directory",
        "⚠️ Stock Alert Monitoring",
        "🤖 Visionify AI Monitor",
        "💬 Warehouse AI Assistant"
    ])
    
    # Show last update time
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Route to appropriate page
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard()
    elif page == "📝 Product CRUD Dashboard":
        show_product_crud_dashboard()
    elif page == "📦 Product Master List":
        show_product_master()
    elif page == "📍 Inventory by Location":
        show_inventory_by_location()
    elif page == "🔄 Stock Transactions":
        show_stock_transactions()
    elif page == "🚚 Purchase Orders":
        show_purchase_orders()
    elif page == "🏢 Supplier Directory":
        show_supplier_directory()
    elif page == "⚠️ Stock Alert Monitoring":
        show_stock_alerts()
    elif page == "🤖 Visionify AI Monitor":
        show_visionify_ai()
    elif page == "💬 Warehouse AI Assistant":
        show_warehouse_assistant()

# ============================================
# EXISTING PAGES (abbreviated for brevity)
# ============================================

def show_executive_dashboard():
    st.title("Executive Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Products", len(st.session_state.products_df), "10 Categories")
    with col2:
        total_inventory_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        st.metric("💰 Inventory Value", f"BND ${total_inventory_value:,.0f}")
    with col3:
        st.metric("📍 Locations", st.session_state.inventory_df['Location'].nunique(), "1 Warehouse + 4 Stores")
    with col4:
        pending_statuses = ['Confirmed', 'Sent', 'Draft', 'Shipped']
        pending_orders = len(st.session_state.purchase_orders_df[
            st.session_state.purchase_orders_df['Order_Status'].isin(pending_statuses)
        ])
        st.metric("📋 Pending Orders", pending_orders, "Require Attention")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Products by Category")
        category_data = st.session_state.products_df['Category'].value_counts()
        fig = px.pie(values=category_data.values, names=category_data.index)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📍 Stock Distribution by Location")
        location_data = st.session_state.inventory_df.groupby('Location')['Quantity_On_Hand'].sum().reset_index()
        fig = px.bar(location_data, x='Location', y='Quantity_On_Hand',
                    color='Quantity_On_Hand', color_continuous_scale='Viridis')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_product_master():
    st.title("Product Master List")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 Search products...")
    with col2:
        category_filter = st.multiselect("Filter by Category:", st.session_state.products_df['Category'].unique())
    
    filtered_df = st.session_state.products_df
    if search:
        filtered_df = filtered_df[filtered_df['Product_Name'].str.contains(search, case=False)]
    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    
    st.dataframe(filtered_df, use_container_width=True)

def show_inventory_by_location():
    st.title("Multi-Location Inventory")
    
    location_filter = st.selectbox("Select Location:", ['All'] + list(st.session_state.inventory_df['Location'].unique()))
    
    if location_filter != 'All':
        display_df = st.session_state.inventory_df[st.session_state.inventory_df['Location'] == location_filter]
    else:
        display_df = st.session_state.inventory_df
    
    display_df = display_df.merge(st.session_state.products_df[['Product_ID', 'Product_Name', 'Category']], on='Product_ID')
    st.dataframe(display_df[['Product_ID', 'Product_Name', 'Category', 'Location', 'Quantity_On_Hand', 'Last_Updated']], 
                use_container_width=True)

def show_stock_transactions():
    st.title("Stock Transaction History")
    
    # Filters
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
    st.title("Purchase Order Management")
    
    # Filters
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
    st.title("Supplier Directory")
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_stock_alerts():
    st.title("Automated Stock Alert System")
    
    # Calculate alerts
    stock_levels = st.session_state.inventory_df.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    stock_levels = stock_levels.merge(
        st.session_state.products_df[['Product_ID', 'Product_Name', 'Reorder_Level']], on='Product_ID'
    )
    
    def get_status(row):
        if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return '🔴 CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return '🟡 WARNING'
        else:
            return '🟢 NORMAL'
    
    stock_levels['Alert_Status'] = stock_levels.apply(get_status, axis=1)
    
    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Critical", len(stock_levels[stock_levels['Alert_Status'] == '🔴 CRITICAL']))
    col2.metric("🟡 Warning", len(stock_levels[stock_levels['Alert_Status'] == '🟡 WARNING']))
    col3.metric("🟢 Normal", len(stock_levels[stock_levels['Alert_Status'] == '🟢 NORMAL']))
    
    st.dataframe(stock_levels, use_container_width=True)

def show_visionify_ai():
    st.title("Visionify AI - Computer Vision Monitoring")
    st.info("Visionify AI provides computer vision solutions that integrate with existing CCTV systems for real-time inventory tracking and worker safety monitoring.")

def show_warehouse_assistant():
    st.title("🤖 Warehouse AI Assistant")
    
    # Simple chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your inventory..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simple response
        response = "I'm here to help with your inventory questions. Try asking about products, stock levels, or suppliers."
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
