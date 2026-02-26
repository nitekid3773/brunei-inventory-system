import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import numpy as np
import json
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

# Google Sheets ID (from your URL)
SPREADSHEET_ID = "1QThumOfARHlGr2lBJf4TSFclfi1iuDkm"

def get_google_sheets_client():
    """Connect to Google Sheets using service account"""
    try:
        # Check if credentials exist in secrets
        if 'gcp_service_account' in st.secrets:
            # Create credentials from secrets
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            )
            # Authorize and return client
            client = gspread.authorize(credentials)
            return client
        else:
            st.warning("⚠️ Google Sheets credentials not configured in secrets")
            return None
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def load_data_from_sheets():
    """Load all data from Google Sheets into session state"""
    try:
        with st.spinner("Loading data from Google Sheets..."):
            client = get_google_sheets_client()
            if not client:
                return False
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            
            # Get all worksheets
            worksheets = spreadsheet.worksheets()
            
            # Dictionary to store dataframes
            data = {}
            
            # Read each worksheet
            for worksheet in worksheets:
                sheet_name = worksheet.title
                # Get all records
                records = worksheet.get_all_records()
                if records:
                    data[sheet_name] = pd.DataFrame(records)
                else:
                    data[sheet_name] = pd.DataFrame()
            
            # Map to session state
            st.session_state.products_df = data.get('Product Master List', pd.DataFrame())
            st.session_state.inventory_df = data.get('Inventory by Location', pd.DataFrame())
            st.session_state.transactions_df = data.get('Stock Transactions', pd.DataFrame())
            st.session_state.suppliers_df = data.get('Supplier Management', pd.DataFrame())
            st.session_state.purchase_orders_df = data.get('Purchase Orders', pd.DataFrame())
            st.session_state.alerts_df = data.get('Stock Alert Monitoring', pd.DataFrame())
            
            # Create locations_df from inventory data
            if not st.session_state.inventory_df.empty:
                if 'Location_ID' in st.session_state.inventory_df.columns and 'Location_Name' in st.session_state.inventory_df.columns:
                    st.session_state.locations_df = st.session_state.inventory_df[['Location_ID', 'Location_Name']].drop_duplicates().reset_index(drop=True)
                else:
                    # Create default locations
                    st.session_state.locations_df = pd.DataFrame([
                        {'Location_ID': 'LOC001', 'Location_Name': 'Warehouse A'},
                        {'Location_ID': 'LOC002', 'Location_Name': 'Store 1'},
                        {'Location_ID': 'LOC003', 'Location_Name': 'Store 2'},
                        {'Location_ID': 'LOC004', 'Location_Name': 'Store 3'},
                        {'Location_ID': 'LOC005', 'Location_Name': 'Store 4'}
                    ])
            
            st.session_state.documents_df = pd.DataFrame()
            st.session_state.last_sync = datetime.now()
            
            st.success("✅ Data loaded successfully from Google Sheets!")
            return True
            
    except Exception as e:
        st.error(f"Error loading data from Sheets: {e}")
        return False

def save_data_to_sheets():
    """Save all data from session state back to Google Sheets"""
    try:
        with st.spinner("Saving data to Google Sheets..."):
            client = get_google_sheets_client()
            if not client:
                return False
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            
            # Define sheet names and corresponding dataframes
            sheets_data = {
                'Product Master List': st.session_state.products_df,
                'Inventory by Location': st.session_state.inventory_df,
                'Stock Transactions': st.session_state.transactions_df,
                'Supplier Management': st.session_state.suppliers_df,
                'Purchase Orders': st.session_state.purchase_orders_df,
                'Stock Alert Monitoring': st.session_state.alerts_df
            }
            
            # Update each worksheet
            for sheet_name, df in sheets_data.items():
                if not df.empty:
                    # Find the worksheet
                    try:
                        worksheet = spreadsheet.worksheet(sheet_name)
                    except:
                        # Create worksheet if it doesn't exist
                        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
                    
                    # Clear existing content
                    worksheet.clear()
                    
                    # Update with new data
                    if not df.empty:
                        # Add headers
                        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            st.session_state.last_sync = datetime.now()
            st.success("✅ Data saved successfully to Google Sheets!")
            return True
            
    except Exception as e:
        st.error(f"Error saving data to Sheets: {e}")
        return False

def auto_save_to_sheets():
    """Automatically save after changes"""
    if st.session_state.get('auto_save', True):
        save_data_to_sheets()

# ============================================
# INITIALIZE SESSION STATE
# ============================================

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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_sync' not in st.session_state:
    st.session_state.last_sync = None
if 'auto_save' not in st.session_state:
    st.session_state.auto_save = True

# ============================================
# LOAD INITIAL DATA (FALLBACK)
# ============================================

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data with all required fields (fallback if Sheets fails)"""
    
    # Locations
    locations = [
        {'Location_ID': 'LOC001', 'Location_Name': 'Warehouse A', 'Type': 'Warehouse', 'Capacity': 10000, 'Manager': 'Ali Rahman'},
        {'Location_ID': 'LOC002', 'Location_Name': 'Store 1', 'Type': 'Retail Store', 'Capacity': 5000, 'Manager': 'Siti Aminah'},
        {'Location_ID': 'LOC003', 'Location_Name': 'Store 2', 'Type': 'Retail Store', 'Capacity': 4500, 'Manager': 'John Lee'},
        {'Location_ID': 'LOC004', 'Location_Name': 'Store 3', 'Type': 'Retail Store', 'Capacity': 4000, 'Manager': 'Hassan Bakar'},
        {'Location_ID': 'LOC005', 'Location_Name': 'Store 4', 'Type': 'Retail Store', 'Capacity': 3500, 'Manager': 'Nurul Huda'},
    ]
    locations_df = pd.DataFrame(locations)
    
    # Suppliers
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', 'General Manager', '673-2223456', 'lim.ah.seng@huaho.com', 'Lot 123, Kg Kiulap', 'Net 30', 'A+', 0.98, 'Electronics, Groceries', '2022-01-15', 'Yes', '50000'],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', 'Procurement Director', '673-2337890', 'mei.ling@soonlee.com', 'Unit 45, Gadong Central', 'Net 30', 'A', 0.95, 'Groceries, Household', '2022-03-20', 'Yes', '75000'],
        ['SUP003', 'Supasave', 'David Wong', 'Supply Chain Manager', '673-2456789', 'david.wong@supasave.com', 'No. 78, Serusop', 'Net 45', 'B+', 0.92, 'General Trading', '2022-02-10', 'Yes', '60000'],
        ['SUP004', 'Seng Huat', 'Michael Chen', 'Owner', '673-2771234', 'michael.chen@senghuat.com', 'Lot 56, Kuala Belait', 'Cash on Delivery', 'A', 0.97, 'Hardware, Tools', '2022-04-05', 'Yes', '35000'],
        ['SUP005', 'SKH Group', 'Steven Khoo', 'Operations Manager', '673-2667890', 'steven.khoo@skh.com', 'Unit 12, Tutong', 'Net 30', 'A', 0.96, 'Electronics, Furniture', '2022-01-30', 'Yes', '80000'],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Position', 'Phone', 'Email', 'Address', 
        'Payment_Terms', 'Supplier_Tier', 'Reliability_Score', 'Product_Categories', 'Since_Date', 'Active', 'Credit_Limit'
    ])
    
    # Products
    products_data = [
        ['PRD00001', 'ELE-001', '888123456001', 'Samsung 55" LED TV', 'Electronics', 'Premium', 785.00, 1135.09, 7, 45, 15, 'SUP001', 'Hua Ho Trading', 'A3-12-01', 'Aisle 3, Row 12, Bin 1', 18.5, 25.0, '2026-12-31', 'Ambient', 'Active', '2024-01-15'],
        ['PRD00002', 'ELE-002', '888123456002', 'iPhone 15 Pro', 'Electronics', 'Premium', 916.00, 1351.05, 35, 38, 28, 'SUP005', 'SKH Group', 'A3-08-03', 'Aisle 3, Row 8, Bin 3', 6.2, 8.5, '2026-10-31', 'Secure Cabinet', 'Active', '2024-01-20'],
        ['PRD00003', 'GRO-001', '888123456004', 'Basmati Rice 5kg', 'Groceries', 'Staple', 8.00, 9.81, 18, 120, 48, 'SUP002', 'Soon Lee', 'B2-01-04', 'Aisle 2, Row 1, Bin 4', 5.0, 8.0, '2026-05-31', 'Dry Storage', 'Active', '2024-02-01'],
        ['PRD00004', 'HAR-001', '888123456006', 'Paint 5L White', 'Hardware', 'Standard', 97.00, 116.66, 44, 35, 14, 'SUP004', 'Seng Huat', 'C1-03-02', 'Aisle 1, Row 3, Bin 2', 6.5, 1.2, '2027-01-31', 'Ambient', 'Active', '2024-02-10'],
        ['PRD00005', 'PHA-001', '888123456007', 'Paracetamol 500mg', 'Pharmaceuticals', 'Essential', 141.00, 189.88, 13, 65, 21, 'SUP003', 'Supasave', 'D2-02-05', 'Aisle 2, Row 2, Bin 5', 0.5, 0.8, '2026-03-31', 'Cool Storage', 'Active', '2024-02-15'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 'Product_Tier',
        'Unit_Cost_BND', 'Selling_Price_BND', 'Reorder_Level', 'Daily_Movement_Units', 
        'Lead_Time_Days', 'Supplier_ID', 'Supplier_Name', 'Bin_Code', 'Bin_Description', 
        'Weight_kg', 'Volume_cuft', 'Expiry_Date', 'Storage_Requirement', 'Status', 'Date_Added'
    ])
    
    # Inventory
    inventory_data = []
    inv_counter = 1
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in locations_df.iterrows():
            qty = 50 + ((i + j) * 17) % 150
            inventory_data.append({
                'Inventory_ID': f'INV{inv_counter:06d}',
                'Product_ID': prod,
                'Product_Name': products.iloc[i]['Product_Name'],
                'Location_ID': loc['Location_ID'],
                'Location_Name': loc['Location_Name'],
                'Bin_Code': products.iloc[i]['Bin_Code'],
                'Quantity_On_Hand': qty,
                'Last_Updated': datetime.now().strftime('%Y-%m-%d')
            })
            inv_counter += 1
    
    inventory = pd.DataFrame(inventory_data)
    
    # Alerts
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
    
    return products, inventory, pd.DataFrame(), suppliers, pd.DataFrame(), alerts, locations_df, pd.DataFrame()

# ============================================
# DATA INITIALIZATION
# ============================================

# Try to load from Google Sheets first
if st.session_state.products_df is None:
    if not load_data_from_sheets():
        # Fall back to initial data
        with st.spinner("Loading initial data..."):
            (st.session_state.products_df, 
             st.session_state.inventory_df, 
             st.session_state.transactions_df, 
             st.session_state.suppliers_df, 
             st.session_state.purchase_orders_df, 
             st.session_state.alerts_df,
             st.session_state.locations_df,
             st.session_state.documents_df) = load_initial_data()
            st.info("Using built-in initial data. Connect Google Sheets for persistent storage.")

# ============================================
# CORE FUNCTIONS (simplified for space - keep your existing functions here)
# ============================================

def generate_product_id():
    existing_ids = st.session_state.products_df['Product_ID'].tolist() if not st.session_state.products_df.empty else []
    numbers = [int(id.replace('PRD', '')) for id in existing_ids if id.startswith('PRD')]
    next_num = max(numbers) + 1 if numbers else 1
    return f"PRD{next_num:05d}"

def generate_sku(category):
    year = datetime.now().strftime('%y')
    prefix = category[:3].upper()
    return f"{prefix}{year}{random.randint(100, 999)}"

def generate_barcode():
    return f"888{random.randint(1000000, 9999999)}"

def add_product(product_data):
    # Validate and add product
    product_data['Product_ID'] = generate_product_id()
    product_data['SKU'] = generate_sku(product_data['Category'])
    product_data['Barcode'] = generate_barcode()
    product_data['Date_Added'] = datetime.now().strftime('%Y-%m-%d')
    product_data['Status'] = 'Active'
    
    new_row = pd.DataFrame([product_data])
    st.session_state.products_df = pd.concat([st.session_state.products_df, new_row], ignore_index=True)
    
    # Add inventory for all locations
    for _, loc in st.session_state.locations_df.iterrows():
        new_inv = pd.DataFrame([{
            'Inventory_ID': f'INV{len(st.session_state.inventory_df)+1:06d}',
            'Product_ID': product_data['Product_ID'],
            'Product_Name': product_data['Product_Name'],
            'Location_ID': loc['Location_ID'],
            'Location_Name': loc['Location_Name'],
            'Bin_Code': product_data.get('Bin_Code', ''),
            'Quantity_On_Hand': 0,
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        }])
        st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, new_inv], ignore_index=True)
    
    st.session_state.last_update = datetime.now()
    auto_save_to_sheets()
    return True, product_data['Product_ID']

def update_product(product_id, updated_data):
    mask = st.session_state.products_df['Product_ID'] == product_id
    for key, value in updated_data.items():
        if key in st.session_state.products_df.columns:
            st.session_state.products_df.loc[mask, key] = value
    auto_save_to_sheets()
    return True, None

def delete_product(product_id):
    product_name = st.session_state.products_df[st.session_state.products_df['Product_ID'] == product_id]['Product_Name'].values[0]
    st.session_state.products_df = st.session_state.products_df[st.session_state.products_df['Product_ID'] != product_id]
    st.session_state.inventory_df = st.session_state.inventory_df[st.session_state.inventory_df['Product_ID'] != product_id]
    auto_save_to_sheets()
    return product_name

# [Keep all your existing UI functions here - show_product_crud, show_inventory, etc.]
# For brevity, I'm not including all UI functions, but keep them from your original file

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Menu")
        
        # Google Sheets Sync Status
        st.markdown("### 📊 Google Sheets Sync")
        if st.session_state.last_sync:
            st.success(f"✅ Last sync: {st.session_state.last_sync.strftime('%H:%M:%S')}")
        else:
            st.info("Not synced yet")
        
        st.session_state.auto_save = st.checkbox("Auto-save", value=st.session_state.auto_save)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Load", use_container_width=True):
                load_data_from_sheets()
        with col2:
            if st.button("📤 Save", use_container_width=True):
                save_data_to_sheets()
        
        st.markdown("---")
        
        # Navigation
        page = st.radio("Select:", [
            "Executive Dashboard",
            "Product Management",
            "Inventory by Location",
            "Purchase Orders",
            "Suppliers",
            "Transaction History",
            "Stock Alerts",
            "🤖 AI Innovations"
        ])
        
        st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    
    # Route to pages (keep your existing page functions)
    if page == "Executive Dashboard":
        # show_executive_dashboard()  # Add your function
        st.write("Dashboard coming soon...")
    elif page == "Product Management":
        # show_product_crud()  # Add your function
        st.write("Product Management coming soon...")
    # ... add all your other page conditions

if __name__ == "__main__":
    main()
