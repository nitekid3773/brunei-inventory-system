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
import os
import tempfile
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# GOOGLE DRIVE & EXCEL SYNC CONFIGURATION
# ============================================

# Google Drive File ID (extracted from your link)
GOOGLE_DRIVE_FILE_ID = "1QThumOfARHlGr2lBJf4TSFclfi1iuDkm"

def get_drive_service():
    """
    Authenticate and return a Google Drive service object.
    Uses Streamlit secrets for credentials.
    """
    try:
        # Check if Google credentials exist in secrets
        if 'google' in st.secrets:
            credentials_info = {
                "type": st.secrets["google"]["type"],
                "project_id": st.secrets["google"]["project_id"],
                "private_key_id": st.secrets["google"]["private_key_id"],
                "private_key": st.secrets["google"]["private_key"],
                "client_email": st.secrets["google"]["client_email"],
                "client_id": st.secrets["google"]["client_id"],
                "auth_uri": st.secrets["google"]["auth_uri"],
                "token_uri": st.secrets["google"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"]
            }
            creds = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            return build('drive', 'v3', credentials=creds)
        else:
            st.warning("⚠️ Google Drive credentials not configured. Using local data only.")
            return None
    except Exception as e:
        st.error(f"Error setting up Drive service: {e}")
        return None

def download_excel_from_drive():
    """
    Download the Excel file from Google Drive.
    Returns path to temporary file or None if failed.
    """
    try:
        service = get_drive_service()
        
        # If no service (no credentials), try public download
        if not service:
            # Try public download (works if file is shared as "Anyone with link can view")
            public_url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"
            response = requests.get(public_url, timeout=30)
            
            if response.status_code == 200:
                # Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name
            else:
                st.error(f"Failed to download file: HTTP {response.status_code}")
                return None
        
        # Download using Drive API
        request = service.files().get_media(fileId=GOOGLE_DRIVE_FILE_ID)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            downloader = MediaIoBaseDownload(tmp_file, request)
            done = False
            progress_bar = st.progress(0, text="Downloading from Google Drive...")
            
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress_bar.progress(int(status.progress() * 100))
            
            progress_bar.empty()
            return tmp_file.name
            
    except Exception as e:
        st.error(f"Error downloading file from Drive: {e}")
        return None

def upload_excel_to_drive(file_path):
    """
    Upload updated Excel file back to Google Drive.
    Returns True if successful, False otherwise.
    """
    try:
        service = get_drive_service()
        
        if not service:
            st.warning("⚠️ Cannot upload: Google Drive credentials not configured.")
            return False
        
        # Upload new version
        media = MediaFileUpload(
            file_path, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )
        
        # Update the file
        updated_file = service.files().update(
            fileId=GOOGLE_DRIVE_FILE_ID,
            media_body=media
        ).execute()
        
        return True
        
    except Exception as e:
        st.error(f"Error uploading file to Drive: {e}")
        return False

def load_data_from_excel():
    """
    Load all data from Excel file into session state DataFrames.
    Returns True if successful, False otherwise.
    """
    try:
        # Show loading message
        with st.spinner("Loading data from Google Drive..."):
            # Download the file
            excel_path = download_excel_from_drive()
            
            if not excel_path:
                st.warning("Could not download from Drive. Using initial data.")
                return False
            
            # Read each sheet
            products_df = pd.read_excel(excel_path, sheet_name='Product Master List')
            inventory_df = pd.read_excel(excel_path, sheet_name='Inventory by Location')
            transactions_df = pd.read_excel(excel_path, sheet_name='Stock Transactions')
            suppliers_df = pd.read_excel(excel_path, sheet_name='Supplier Management')
            purchase_orders_df = pd.read_excel(excel_path, sheet_name='Purchase Orders')
            alerts_df = pd.read_excel(excel_path, sheet_name='Stock Alert Monitoring')
            
            # Also need locations_df - create from inventory data
            locations_df = inventory_df[['Location_ID', 'Location_Name']].drop_duplicates().reset_index(drop=True)
            
            # Create empty documents_df if not in Excel
            try:
                documents_df = pd.read_excel(excel_path, sheet_name='Documents')
            except:
                documents_df = pd.DataFrame()
            
            # Clean up temp file
            os.unlink(excel_path)
            
            # Store in session state
            st.session_state.products_df = products_df
            st.session_state.inventory_df = inventory_df
            st.session_state.transactions_df = transactions_df
            st.session_state.suppliers_df = suppliers_df
            st.session_state.purchase_orders_df = purchase_orders_df
            st.session_state.alerts_df = alerts_df
            st.session_state.locations_df = locations_df
            st.session_state.documents_df = documents_df
            
            st.session_state.last_sync = datetime.now()
            st.success("✅ Data loaded successfully from Google Drive!")
            return True
            
    except Exception as e:
        st.error(f"Error loading data from Excel: {e}")
        return False

def save_data_to_excel():
    """
    Save all current DataFrames from session state back to Excel file.
    Returns True if successful, False otherwise.
    """
    try:
        # Show saving message
        with st.spinner("Saving data to Google Drive..."):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                excel_path = tmp_file.name
            
            # Write all DataFrames to different sheets
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                st.session_state.products_df.to_excel(writer, sheet_name='Product Master List', index=False)
                st.session_state.inventory_df.to_excel(writer, sheet_name='Inventory by Location', index=False)
                st.session_state.transactions_df.to_excel(writer, sheet_name='Stock Transactions', index=False)
                st.session_state.suppliers_df.to_excel(writer, sheet_name='Supplier Management', index=False)
                st.session_state.purchase_orders_df.to_excel(writer, sheet_name='Purchase Orders', index=False)
                st.session_state.alerts_df.to_excel(writer, sheet_name='Stock Alert Monitoring', index=False)
                st.session_state.documents_df.to_excel(writer, sheet_name='Documents', index=False)
            
            # Upload to Drive
            success = upload_excel_to_drive(excel_path)
            
            # Clean up temp file
            os.unlink(excel_path)
            
            if success:
                st.session_state.last_sync = datetime.now()
                return True
            return False
            
    except Exception as e:
        st.error(f"Error saving data to Excel: {e}")
        return False

def auto_save_to_drive():
    """Automatically save data to Drive after changes."""
    if save_data_to_excel():
        st.session_state.last_save = datetime.now()
        return True
    return False

# Custom CSS (your existing CSS)
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
    
    /* Innovation cards */
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
    
    /* Sync status indicators */
    .sync-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 4px solid #28a745;
    }
    
    .sync-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 4px solid #ffc107;
    }
    
    .sync-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

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
if 'last_save' not in st.session_state:
    st.session_state.last_save = None

# ============================================
# LOAD INITIAL DATA (FALLBACK)
# ============================================

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data with all required fields (fallback if Drive fails)"""
    
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
        ['PRD00008', 'AUT-2024-001', '888123456008', 'Shell Engine Oil 4L', 'Automotive', 'Lubricants', 'Premium', 185.00, 269.02, 84.02, 12, 28, 14, 'SUP001', 'Hua Ho Trading Sdn Bhd', 'E1-04-02', 'Aisle 1, Row 4, Bin 2', 3.5, 1.0, '2027-06-30', 'Ambient', 'Active', '2024-02-20'],
        ['PRD00009', 'TEX-2024-001', '888123456009', 'School Uniform Set', 'Textiles', 'Apparel', 'Standard', 43.00, 54.40, 11.40, 46, 22, 21, 'SUP005', 'SKH Group', 'F3-05-01', 'Aisle 3, Row 5, Bin 1', 0.8, 1.5, '2027-12-31', 'Ambient', 'Active', '2024-02-25'],
        ['PRD00010', 'FUR-2024-001', '888123456010', 'Office Desk', 'Furniture', 'Office', 'Standard', 91.00, 129.73, 38.73, 26, 8, 21, 'SUP004', 'Seng Huat Trading', 'G2-04-03', 'Aisle 2, Row 4, Bin 3', 25.0, 12.0, '2028-01-31', 'Ambient', 'Active', '2024-03-01'],
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
        prod_idx = i % len(products)
        prod = products.iloc[prod_idx]
        loc_idx = i % len(locations_df)
        loc = locations_df.iloc[loc_idx]
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
            'Unit_Cost_BND': float(prod['Unit_Cost_BND']),
            'Total_Value_BND': abs(qty) * float(prod['Unit_Cost_BND']),
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
        supplier_idx = i % len(suppliers)
        supplier = suppliers.iloc[supplier_idx]
        product_idx = i % len(products)
        product = products.iloc[product_idx]
        qty = random.randint(50, 500)
        unit_cost = float(product['Unit_Cost_BND']) * random.uniform(0.9, 1.1)
        
        po_date = datetime.now() - timedelta(days=random.randint(0, 60))
        lead_time = int(product['Lead_Time_Days'])
        expected_date = po_date + timedelta(days=lead_time + random.randint(0, 5))
        
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
            'Tax_BND': 0,
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

# ============================================
# DATA INITIALIZATION - TRY DRIVE FIRST, THEN FALLBACK
# ============================================

# Try to load from Google Drive first
if st.session_state.products_df is None:
    if not load_data_from_excel():
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
            st.info("Using built-in initial data. Connect Google Drive for persistent storage.")

# ============================================
# HTML DOCUMENT GENERATION
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

# ============================================
# ADVANCED AI CHATBOT
# ============================================

class WarehouseChatbot:
    """Intelligent chatbot with deep warehouse knowledge"""
    
    def __init__(self):
        self.context = {}
        
    def get_response(self, query):
        """Generate intelligent response based on query"""
        query_lower = query.lower()
        
        # Inventory queries
        if any(word in query_lower for word in ['inventory', 'stock', 'quantity', 'how many']):
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
            return self._forecast_response()
        
        # Location queries
        elif any(word in query_lower for word in ['location', 'where', 'warehouse', 'store']):
            return self._location_response(query_lower)
        
        # Cost/price queries
        elif any(word in query_lower for word in ['cost', 'price', 'value', 'worth']):
            return self._cost_response()
        
        # Expiry queries
        elif any(word in query_lower for word in ['expiry', 'expire', 'expiration']):
            return self._expiry_response()
        
        # Performance queries
        elif any(word in query_lower for word in ['performance', 'efficiency', 'kpi']):
            return self._performance_response()
        
        # Recommendation queries
        elif any(word in query_lower for word in ['recommend', 'suggest', 'advice', 'tip']):
            return self._recommendation_response()
        
        # Visionify AI queries
        elif any(word in query_lower for word in ['visionify', 'camera', 'computer vision']):
            return self._visionify_response()
        
        # Labor optimization queries
        elif any(word in query_lower for word in ['labor', 'worker', 'staff', 'productivity']):
            return self._labor_response()
        
        # Returns queries
        elif any(word in query_lower for word in ['return', 'refund', 'reverse']):
            return self._returns_response()
        
        # Bin optimization queries
        elif any(word in query_lower for word in ['bin', 'slot', 'location', 'optimize']):
            return self._bin_optimization_response()
        
        # Help/Default
        else:
            return self._help_response()
    
    def _inventory_response(self, query):
        total_items = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        total_items = int(total_items) if not pd.isna(total_items) else 0
        
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        total_value = float(total_value) if not pd.isna(total_value) else 0
        
        # Check for specific product
        for _, product in st.session_state.products_df.iterrows():
            if product['Product_Name'].lower() in query or product['Product_ID'].lower() in query:
                stock = st.session_state.inventory_df[
                    st.session_state.inventory_df['Product_ID'] == product['Product_ID']
                ]['Quantity_On_Hand'].sum()
                stock = int(stock) if not pd.isna(stock) else 0
                return f"📦 **{product['Product_Name']}** (ID: {product['Product_ID']})\n" + \
                       f"• Current stock: {stock} units\n" + \
                       f"• Reorder level: {product['Reorder_Level']}\n" + \
                       f"• Bin location: {product['Bin_Code']}\n" + \
                       f"• Status: {product['Status']}"
        
        return f"📊 **Current Inventory:**\n• Total items: {total_items:,}\n• Total value: B${total_value:,.2f}"
    
    def _product_response(self, query):
        for _, product in st.session_state.products_df.iterrows():
            if product['Product_Name'].lower() in query or product['Product_ID'].lower() in query or product['SKU'].lower() in query:
                stock = st.session_state.inventory_df[
                    st.session_state.inventory_df['Product_ID'] == product['Product_ID']
                ]['Quantity_On_Hand'].sum()
                stock = int(stock) if not pd.isna(stock) else 0
                margin = ((product['Selling_Price_BND'] - product['Unit_Cost_BND']) / product['Selling_Price_BND'] * 100)
                
                return f"""📋 **Product Details: {product['Product_Name']}**

**Basic Info:**
• ID: {product['Product_ID']}
• SKU: {product['SKU']}
• Category: {product['Category']}
• Bin: {product['Bin_Code']}

**Pricing:**
• Cost: B${product['Unit_Cost_BND']:.2f}
• Selling: B${product['Selling_Price_BND']:.2f}
• Margin: {margin:.1f}%

**Stock:**
• Current: {stock} units
• Reorder at: {product['Reorder_Level']}
• Daily movement: {product['Daily_Movement_Units']} units

**Supplier:**
• Preferred: {product['Supplier_Name']}
• Lead time: {product['Lead_Time_Days']} days
• Expiry: {product['Expiry_Date']}"""
        
        return f"📦 **Product Summary:**\n• Total products: {len(st.session_state.products_df)}\n• Categories: {st.session_state.products_df['Category'].nunique()}"
    
    def _alert_response(self):
        alerts = st.session_state.alerts_df
        critical = len(alerts[alerts['Alert_Status'] == 'CRITICAL'])
        warning = len(alerts[alerts['Alert_Status'] == 'WARNING'])
        
        response = "⚠️ **Stock Alerts:**\n\n"
        
        if critical > 0:
            response += f"🔴 **CRITICAL - {critical} items need immediate attention**\n"
        
        if warning > 0:
            response += f"🟡 **WARNING - {warning} items are below reorder level**\n"
        
        if critical == 0 and warning == 0:
            response += "✅ All stock levels are healthy!"
        
        return response
    
    def _supplier_response(self, query):
        for _, supplier in st.session_state.suppliers_df.iterrows():
            if supplier['Supplier_Name'].lower() in query:
                products_count = len(st.session_state.products_df[
                    st.session_state.products_df['Supplier_Name'] == supplier['Supplier_Name']
                ])
                
                return f"""🏢 **Supplier: {supplier['Supplier_Name']}**

**Contact Info:**
• Contact: {supplier['Contact_Person']}
• Phone: {supplier['Phone_Primary']}
• Email: {supplier['Email_Primary']}
• Address: {supplier['Address']}

**Performance:**
• Tier: {supplier['Supplier_Tier']}
• Reliability: {float(supplier['Reliability_Score'])*100:.0f}%
• Payment terms: {supplier['Payment_Terms']}

**Products supplied: {products_count}"""
        
        return f"📋 **Supplier Summary:**\n• Total suppliers: {len(st.session_state.suppliers_df)}"
    
    def _order_response(self, query):
        pending = len(st.session_state.purchase_orders_df[
            st.session_state.purchase_orders_df['Order_Status'].isin(['Draft', 'Sent', 'Confirmed'])
        ])
        
        total_value = st.session_state.purchase_orders_df['Total_Cost_BND'].sum()
        total_value = float(total_value) if not pd.isna(total_value) else 0
        
        return f"📋 **Order Summary:**\n• Total orders: {len(st.session_state.purchase_orders_df)}\n• Pending: {pending}\n• Total value: B${total_value:,.2f}"
    
    def _forecast_response(self):
        return """📈 **Demand Forecast (Next 30 days):**

• **Electronics**: +15% expected (Hari Raya effect)
• **Groceries**: +22% expected (seasonal peak)
• **Pharmaceuticals**: +8% expected (stable)

💡 **Recommendation:** Increase safety stock for top movers by 15%"""
    
    def _location_response(self, query):
        for _, product in st.session_state.products_df.iterrows():
            if product['Product_Name'].lower() in query or product['Product_ID'].lower() in query:
                return f"📍 **{product['Product_Name']}** is located at bin **{product['Bin_Code']}** in Warehouse A"
        
        loc_summary = st.session_state.inventory_df.groupby('Location_Name').agg({
            'Quantity_On_Hand': 'sum',
            'Product_ID': 'nunique'
        }).reset_index()
        
        response = "📍 **Inventory by Location:**\n"
        for _, loc in loc_summary.iterrows():
            qty = int(loc['Quantity_On_Hand']) if not pd.isna(loc['Quantity_On_Hand']) else 0
            response += f"• **{loc['Location_Name']}**: {qty:,} units\n"
        
        return response
    
    def _cost_response(self):
        total_value = (st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        total_value = float(total_value) if not pd.isna(total_value) else 0
        
        return f"💰 **Total Inventory Value:** B${total_value:,.2f}"
    
    def _expiry_response(self):
        return "✅ No products near expiry in the next 90 days"
    
    def _performance_response(self):
        total_items = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        total_items = int(total_items) if not pd.isna(total_items) else 0
        
        return f"""📊 **Warehouse Performance Dashboard**

**Inventory Metrics:**
• Total items: {total_items:,}
• Items per location: {total_items/5:.0f}

**Order Metrics:**
• Avg supplier reliability: 96%
• Pending orders: {len(st.session_state.purchase_orders_df[st.session_state.purchase_orders_df['Order_Status'].isin(['Draft', 'Sent', 'Confirmed'])])}

**Efficiency Score: 87% - Good**"""
    
    def _recommendation_response(self):
        alerts = st.session_state.alerts_df
        low_stock = alerts[alerts['Alert_Status'] != 'NORMAL']
        
        response = "💡 **AI Recommendations:**\n\n"
        
        if len(low_stock) > 0:
            response += "**📦 Reorder these items today:**\n"
            for _, item in low_stock.head(3).iterrows():
                response += f"• {item['Product_Name']}: order {item['Recommended_Order']} units\n"
        
        response += "\n**🔥 Fast-moving items (increase safety stock):**\n"
        fast_movers = st.session_state.products_df.nlargest(3, 'Daily_Movement_Units')
        for _, item in fast_movers.iterrows():
            response += f"• {item['Product_Name']}: {item['Daily_Movement_Units']} units/day\n"
        
        return response
    
    def _visionify_response(self):
        return """🤖 **Visionify AI - Computer Vision Monitoring**

**Features:**
• Real-time inventory counting via CCTV
• Shelf empty detection
• Personnel safety monitoring
• Theft prevention alerts
• 99.5% accuracy rate

**Current Status:**
• 8 cameras connected
• 1,247 detections today
• 98.2% accuracy

**Benefits:**
• 60% reduction in manual counting
• 24/7 monitoring
• Instant alerts for low stock"""
    
    def _labor_response(self):
        return """👥 **Labor Optimization Engine**

**Today's Schedule:**
• Receiving: 4 staff (92% productivity)
• Picking: 12 staff (88% productivity)
• Packing: 6 staff (95% productivity)
• Loading: 3 staff (78% productivity)

**AI Recommendations:**
• Move 1 picker to loading bay (2-4pm peak)
• Cross-train 2 pickers for packing
• Schedule breaks to maintain coverage

**Projected Impact:**
• Throughput ↑12%
• Overtime cost ↓8%"""
    
    def _returns_response(self):
        return """🔄 **Returns Management AI**

**Today's Returns:**
• LED TV: 3 units (Damaged)
• Smartphone: 8 units (Defective)
• Rice 5kg: 12 units (Expired)

**AI Insights:**
• Smartphone returns spike after updates
• Rice expiry in monsoon months
• TV damage during afternoon shifts

**Recovered Value: B$12,450 (+18% vs last month)**"""
    
    def _bin_optimization_response(self):
        return """📍 **AI Smart Bin Location Optimizer**

**Current Layout Efficiency: 67%**

**AI Recommendations:**
• Move fast-moving items near shipping
• Group frequently ordered items together
• Place heavy items at waist height

**Optimization Benefits:**
• Travel distance: 342m → 263m (↓23%)
• Pick efficiency: 78% → 94% (↑16%)
• Labor savings: 2.5 hours/shift"""
    
    def _help_response(self):
        return """🤖 **I'm your Warehouse AI Assistant!** I can help you with:

📦 **Inventory** - "How many LED TVs?", "Total stock value"
⚠️ **Alerts** - "Show low stock items", "Critical alerts"
🏢 **Suppliers** - "Tell me about Hua Ho", "Best supplier"
📊 **Forecasts** - "Predict next month's demand"
📍 **Locations** - "Where is product PRD00001?"
💰 **Costs** - "What's our inventory worth?"
🤖 **AI Features** - "How does Visionify work?", "Labor optimization"
🔄 **Returns** - "Show returns analysis"

What would you like to know?"""

# Initialize chatbot
chatbot = WarehouseChatbot()

# ============================================
# AI CHATBOT INTERFACE
# ============================================

def show_ai_chatbot():
    st.markdown('<div class="section-header">🤖 Warehouse AI Assistant</div>', unsafe_allow_html=True)
    
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
        for message in st.session_state.chat_history[-10:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your warehouse..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = chatbot.get_response(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

# ============================================
# AI INNOVATIONS DASHBOARD
# ============================================

def show_ai_innovations():
    st.markdown('<div class="section-header">🤖 AI Warehouse Innovations</div>', unsafe_allow_html=True)
    
    # Create tabs for each innovation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Smart Bin Optimization",
        "Demand Forecasting",
        "Visionify AI",
        "Labor Optimization",
        "Returns Management",
        "Predictive Analytics",
        "AI Chatbot"
    ])
    
    with tab1:
        st.subheader("📍 AI Smart Bin Location Optimizer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Current Layout Efficiency: 67%**
            
            **AI Analysis:**
            - Fast movers should be near shipping
            - Frequently bought together items identified
            - Heavy items moved to waist height
            
            **Optimization Benefits:**
            - Pick time: -23%
            - Travel distance: -31%
            - Productivity: +18%
            """)
            
            if st.button("Run Optimization", key="bin_opt"):
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
        st.subheader("📈 AI Demand Forecasting Engine")
        
        # Generate forecast
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast_data = pd.DataFrame({
            'Date': dates,
            'Electronics': [45 + 10*np.sin(i/7) + random.randint(-3,3) for i in range(30)],
            'Groceries': [120 + 30*np.sin(i/7) + random.randint(-10,10) for i in range(30)],
            'Pharmaceuticals': [30 + 5*np.sin(i/14) + random.randint(-2,2) for i in range(30)]
        })
        
        fig = px.line(forecast_data, x='Date', y=['Electronics', 'Groceries', 'Pharmaceuticals'],
                     title="30-Day Demand Forecast by Category")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📈 **Groceries** expected to increase 22% next week")
        with col2:
            st.warning("⚠️ **Electronics** showing seasonal dip in 2 weeks")
    
    with tab3:
        st.subheader("👁️ Visionify AI - Computer Vision Monitoring")
        
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
        
        if st.button("Run Full Warehouse Count", key="vision_count"):
            with st.spinner("AI analyzing all camera feeds..."):
                time.sleep(2)
                st.success("✅ Count complete! 99.3% accuracy overall")
        
        st.info("""
        **Visionify AI Features:**
        - Real-time inventory counting via CCTV
        - Shelf empty detection
        - Personnel safety monitoring (PPE detection)
        - Theft prevention alerts
        - 60% reduction in manual counting time
        """)
    
    with tab4:
        st.subheader("👥 AI Labor Optimization Engine")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📅 Today's Schedule**
            
            | Role | Staff | Productivity |
            |------|-------|--------------|
            | Receiving | 4 | 92% |
            | Picking | 12 | 88% |
            | Packing | 6 | 95% |
            | Loading | 3 | 78% |
            | Supervisor | 2 | 100% |
            """)
            
            st.warning("⚠️ **Understaffed:** Loading bay (need 1 more)")
        
        with col2:
            st.success("""
            **🤖 AI Recommendations:**
            
            1. Move 1 picker to loading bay (2-4pm peak)
            2. Cross-train 2 pickers for packing
            3. Schedule breaks to maintain coverage
            
            **Projected Impact:**
            - Throughput ↑12%
            - Overtime cost ↓8%
            - OTIF ↑5%
            """)
        
        # Productivity heatmap
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
    
    with tab5:
        st.subheader("🔄 AI Returns Management")
        
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
            st.info("""
            **AI Insights:**
            - Smartphone returns spike after software updates
            - Rice expiry concentrated in monsoon months
            - TV damage during afternoon shifts
            
            **Recommendations:**
            - Train staff on smartphone setup
            - Adjust rice orders pre-monsoon
            - Extra cushioning for afternoon picks
            """)
        
        st.metric("Recovered Value This Month", "B$12,450", "+18% vs last month")
        
        # Returns analysis
        returns_by_reason = pd.DataFrame({
            'Reason': ['Damaged', 'Defective', 'Wrong Item', 'Expired', 'Other'],
            'Count': [45, 32, 28, 15, 8]
        })
        fig = px.pie(returns_by_reason, values='Count', names='Reason',
                    title="Returns by Reason")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab6:
        st.subheader("📊 AI Predictive Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Inventory Trends:**
            - Stock accuracy: 98.5% (↑2.3%)
            - Turnover rate: 4.2x (↑0.3x)
            - Carrying cost: B$45,200 (↓5%)
            
            **Predictions:**
            - Stockout risk: 3 items in next 7 days
            - Overstock risk: 5 items in next 30 days
            - Optimal reorder point adjustment needed for 8 items
            """)
        
        with col2:
            st.markdown("""
            **Anomaly Detection:**
            - Unusual transaction patterns: 2 detected
            - After-hours access: 3 instances
            - Stock variances: 5 items >5% variance
            
            **AI Recommendations:**
            - Review security footage for Mar 15
            - Investigate smartphone discrepancies
            - Schedule cycle count for electronics
            """)
        
        # Trend chart
        trend_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Accuracy': [96.2, 97.1, 98.5, 97.8, 99.2, 98.7]
        })
        fig = px.line(trend_data, x='Month', y='Accuracy',
                     title="Inventory Accuracy Trend",
                     range_y=[95, 100])
        fig.add_hline(y=98, line_dash="dash", line_color="green")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab7:
        show_ai_chatbot()

# ============================================
# ENHANCED CRUD FUNCTIONS WITH AUTO-SAVE
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
    
    product_data['Product_ID'] = generate_product_id()
    if not product_data.get('SKU'):
        product_data['SKU'] = generate_sku(product_data['Category'])
    if not product_data.get('Barcode'):
        product_data['Barcode'] = generate_barcode()
    product_data['Date_Added'] = datetime.now().strftime('%Y-%m-%d')
    product_data['Status'] = 'Active'
    product_data['Profit_Margin_BND'] = product_data['Selling_Price_BND'] - product_data['Unit_Cost_BND']
    
    st.session_state.products_df = pd.concat(
        [st.session_state.products_df, pd.DataFrame([product_data])], 
        ignore_index=True
    )
    
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
    
    # Auto-save to Google Drive
    auto_save_to_drive()
    
    return True, product_data['Product_ID']

def update_product(product_id, updated_data):
    errors = validate_product_data(updated_data)
    if errors:
        return False, errors
    
    mask = st.session_state.products_df['Product_ID'] == product_id
    
    for key, value in updated_data.items():
        if value is not None and key in st.session_state.products_df.columns:
            st.session_state.products_df.loc[mask, key] = value
    
    st.session_state.products_df.loc[mask, 'Profit_Margin_BND'] = (
        st.session_state.products_df.loc[mask, 'Selling_Price_BND'].values[0] - 
        st.session_state.products_df.loc[mask, 'Unit_Cost_BND'].values[0]
    )
    
    st.session_state.inventory_df.loc[
        st.session_state.inventory_df['Product_ID'] == product_id, 'Product_Name'
    ] = st.session_state.products_df.loc[mask, 'Product_Name'].values[0]
    
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
    
    # Auto-save to Google Drive
    auto_save_to_drive()
    
    return True, None

def delete_product(product_id):
    product = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] == product_id
    ].iloc[0]
    product_name = product['Product_Name']
    
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
    
    st.session_state.products_df = st.session_state.products_df[
        st.session_state.products_df['Product_ID'] != product_id
    ]
    
    st.session_state.inventory_df = st.session_state.inventory_df[
        st.session_state.inventory_df['Product_ID'] != product_id
    ]
    
    st.session_state.last_update = datetime.now()
    
    # Auto-save to Google Drive
    auto_save_to_drive()
    
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
    
    # Auto-save to Google Drive
    auto_save_to_drive()
    
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
    
    # Auto-save to Google Drive
    auto_save_to_drive()
    
    return new_qty

# ============================================
# PRODUCT CRUD DASHBOARD
# ============================================

def show_product_crud():
    st.markdown('<div class="section-header">📦 Product Management</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        total_products = len(st.session_state.products_df)
        st.metric("Total Products", total_products)
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
        total_inventory = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        total_inventory = int(total_inventory) if not pd.isna(total_inventory) else 0
        avg_cost = st.session_state.products_df['Unit_Cost_BND'].mean()
        avg_cost = float(avg_cost) if not pd.isna(avg_cost) else 0
        total_value = total_inventory * avg_cost
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
            
            col1, col2, col3 = st.columns(3)
            with col1:
                product_name = st.text_input("Product Name *")
                category = st.selectbox("Category *", 
                    ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 
                     'Automotive', 'Textiles', 'Furniture', 'Stationery', 
                     'Beverages', 'Cosmetics'])
            with col2:
                sub_category = st.text_input("Sub Category")
                product_tier = st.selectbox("Product Tier", ['Premium', 'Standard', 'Economy', 'Staple'])
            with col3:
                storage_req = st.text_input("Storage Requirement")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                unit_cost = st.number_input("Unit Cost (BND) *", min_value=0.01, value=100.00, step=10.00)
            with col2:
                selling_price = st.number_input("Selling Price (BND) *", min_value=0.01, value=150.00, step=10.00)
            with col3:
                profit_margin = selling_price - unit_cost
                st.metric("Profit Margin", f"B${profit_margin:.2f}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                reorder_level = st.number_input("Reorder Level", min_value=1, value=10)
                daily_movement = st.number_input("Daily Movement", min_value=0, value=10)
            with col2:
                lead_time = st.number_input("Lead Time (days)", min_value=1, value=7)
                weight = st.number_input("Weight (kg)", min_value=0.1, value=1.0, step=0.1)
            with col3:
                volume = st.number_input("Volume (cu ft)", min_value=0.1, value=1.0, step=0.1)
                expiry = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=365))
            
            supplier_options = st.session_state.suppliers_df['Supplier_Name'].tolist()
            selected_supplier = st.selectbox("Preferred Supplier *", supplier_options)
            supplier_id = st.session_state.suppliers_df[
                st.session_state.suppliers_df['Supplier_Name'] == selected_supplier
            ]['Supplier_ID'].values[0] if len(st.session_state.suppliers_df) > 0 else 'SUP001'
            
            bin_code = st.text_input("Bin Code *", help="e.g., A3-12-01")
            bin_desc = st.text_input("Bin Description", help="e.g., Aisle 3, Row 12, Bin 1")
            
            col1, col2 = st.columns(2)
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
                ]['Product_ID'].values[0] if len(st.session_state.products_df) > 0 else None
            
            with col2:
                location_options = st.session_state.locations_df['Location_Name'].tolist()
                location = st.selectbox("Select Location", location_options)
                location_id = st.session_state.locations_df[
                    st.session_state.locations_df['Location_Name'] == location
                ]['Location_ID'].values[0] if len(st.session_state.locations_df) > 0 else None
            
            if product_id and location_id:
                current_qty = st.session_state.inventory_df[
                    (st.session_state.inventory_df['Product_ID'] == product_id) &
                    (st.session_state.inventory_df['Location_ID'] == location_id)
                ]['Quantity_On_Hand'].values[0]
                current_qty = int(current_qty) if not pd.isna(current_qty) else 0
                
                st.info(f"Current quantity: **{current_qty} units**")
                
                adjustment = st.number_input("Adjustment Quantity", value=0, step=1,
                    help="Positive to add, negative to remove")
                reason = st.selectbox("Reason", 
                    ['Physical Count', 'Damage', 'Expired', 'Quality Control', 'System Correction'])
                
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
                ].iloc[0] if len(st.session_state.suppliers_df) > 0 else None
            
            with col2:
                product_options = st.session_state.products_df['Product_Name'].tolist()
                if st.session_state.selected_product_po:
                    product_id = st.session_state.selected_product_po
                    product_name = st.session_state.products_df[
                        st.session_state.products_df['Product_ID'] == product_id
                    ]['Product_Name'].values[0] if product_id in st.session_state.products_df['Product_ID'].values else product_options[0]
                    default_index = product_options.index(product_name) if product_name in product_options else 0
                else:
                    default_index = 0
                
                product = st.selectbox("Select Product", product_options, index=default_index)
                product_data = st.session_state.products_df[
                    st.session_state.products_df['Product_Name'] == product
                ].iloc[0] if len(st.session_state.products_df) > 0 else None
            
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
                    ]['Location_ID'].values[0] if len(st.session_state.locations_df) > 0 else 'LOC001'
                    expected_date = st.date_input("Expected Delivery", 
                        value=datetime.now() + timedelta(days=int(product_data['Lead_Time_Days'])))
                
                notes = st.text_area("Notes", placeholder="Additional instructions...")
                
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("🔍 Search by name, ID, or SKU")
        with col2:
            category_filter = st.multiselect("Category", 
                st.session_state.products_df['Category'].unique())
        with col3:
            supplier_filter = st.multiselect("Supplier", 
                st.session_state.products_df['Supplier_Name'].unique())
        
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
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📦 {row['Product_Name']} ({row['Product_ID']})"):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**Basic Info**")
                    st.write(f"SKU: {row['SKU']}")
                    st.write(f"Barcode: {row['Barcode']}")
                    st.write(f"Category: {row['Category']}")
                
                with col2:
                    st.markdown(f"**Pricing**")
                    st.write(f"Cost: B${row['Unit_Cost_BND']:.2f}")
                    st.write(f"Selling: B${row['Selling_Price_BND']:.2f}")
                    st.write(f"Reorder: {row['Reorder_Level']}")
                
                with col3:
                    st.markdown(f"**Location**")
                    st.write(f"Bin: {row['Bin_Code']}")
                    st.write(f"Supplier: {row['Supplier_Name']}")
                
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
                
                stock_data = st.session_state.inventory_df[
                    st.session_state.inventory_df['Product_ID'] == row['Product_ID']
                ][['Location_Name', 'Quantity_On_Hand', 'Quantity_Available']]
                st.dataframe(stock_data, use_container_width=True)

# ============================================
# OTHER PAGES
# ============================================

def show_purchase_orders():
    st.markdown('<div class="section-header">📋 Purchase Orders</div>', unsafe_allow_html=True)
    
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
    
    for _, po in filtered_df.sort_values('PO_Date', ascending=False).iterrows():
        with st.expander(f"📄 {po['PO_Number']} - {po['Supplier_Name']} - {po['Order_Status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**PO Details**")
                st.write(f"Date: {po['PO_Date']}")
                st.write(f"Expected: {po['Expected_Delivery_Date']}")
                st.write(f"Payment: {po['Payment_Terms']}")
            
            with col2:
                st.markdown(f"**Supplier**")
                st.write(f"Contact: {po['Supplier_Contact']}")
                st.write(f"Phone: {po['Supplier_Phone']}")
            
            st.write(f"Product: {po['Product_Name']} - {po['Ordered_Quantity']} units @ B${po['Unit_Cost_BND']:.2f}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                subtotal = float(po['Subtotal_BND']) if not pd.isna(po['Subtotal_BND']) else 0
                st.metric("Subtotal", f"B${subtotal:,.2f}")
            with col2:
                shipping = float(po['Shipping_Cost_BND']) if not pd.isna(po['Shipping_Cost_BND']) else 0
                st.metric("Shipping", f"B${shipping:,.2f}")
            with col3:
                total = float(po['Total_Cost_BND']) if not pd.isna(po['Total_Cost_BND']) else 0
                st.metric("Total", f"B${total:,.2f}")
            
            if po['Order_Status'] == 'Draft':
                if st.button(f"✅ Approve PO", key=f"approve_{po['PO_Number']}"):
                    st.session_state.purchase_orders_df.loc[
                        st.session_state.purchase_orders_df['PO_Number'] == po['PO_Number'], 'Order_Status'
                    ] = 'Approved'
                    st.success("PO Approved!")
                    auto_save_to_drive()
                    st.rerun()
            
            html_content = generate_purchase_order_html(po.to_dict())
            st.markdown(get_html_download_link(html_content, f"{po['PO_Number']}.html"), unsafe_allow_html=True)

def show_suppliers():
    st.markdown('<div class="section-header">🏢 Supplier Directory</div>', unsafe_allow_html=True)
    
    for _, supplier in st.session_state.suppliers_df.iterrows():
        with st.expander(f"🏢 {supplier['Supplier_Name']} (Tier {supplier['Supplier_Tier']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Contact**")
                st.write(f"{supplier['Contact_Person']} - {supplier['Position']}")
                st.write(f"📞 {supplier['Phone_Primary']}")
                st.write(f"📧 {supplier['Email_Primary']}")
            
            with col2:
                st.markdown(f"**Details**")
                st.write(f"Address: {supplier['Address']}")
                st.write(f"Since: {supplier['Since_Date']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                reliability = float(supplier['Reliability_Score']) if not pd.isna(supplier['Reliability_Score']) else 0
                st.metric("Reliability", f"{reliability*100:.0f}%")
            with col2:
                credit = float(supplier['Credit_Limit']) if not pd.isna(supplier['Credit_Limit']) else 0
                st.metric("Credit Limit", f"B${credit:,.0f}")
            with col3:
                st.metric("Categories", supplier['Product_Categories'])

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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(display_df))
    with col2:
        total_units = display_df['Quantity_On_Hand'].sum()
        total_units = int(total_units) if not pd.isna(total_units) else 0
        st.metric("Total Units", f"{total_units:,}")
    with col3:
        if len(display_df) > 0:
            mean_cost = st.session_state.products_df['Unit_Cost_BND'].mean()
            mean_cost = float(mean_cost) if not pd.isna(mean_cost) else 0
            total_units_val = display_df['Quantity_On_Hand'].sum()
            total_units_val = float(total_units_val) if not pd.isna(total_units_val) else 0
            total_value = total_units_val * mean_cost
        else:
            total_value = 0
        st.metric("Total Value", f"B${total_value:,.0f}")
    
    st.dataframe(display_df, use_container_width=True)

def show_transactions():
    st.markdown('<div class="section-header">📊 Transaction History</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        txn_type = st.multiselect("Transaction Type", 
            st.session_state.transactions_df['Transaction_Type'].unique())
    with col2:
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
    
    if critical > 0:
        st.subheader("🔴 Critical - Immediate Action Required")
        critical_items = alerts[alerts['Alert_Status'] == 'CRITICAL']
        for _, item in critical_items.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{item['Product_Name']}**")
                with col2:
                    qty = int(item['Quantity_On_Hand']) if not pd.isna(item['Quantity_On_Hand']) else 0
                    st.write(f"Stock: {qty}")
                with col3:
                    reorder = int(item['Reorder_Level']) if not pd.isna(item['Reorder_Level']) else 0
                    st.write(f"Reorder: {reorder}")
                with col4:
                    if st.button(f"Create PO", key=f"po_{item['Product_ID']}"):
                        st.session_state.selected_product_po = item['Product_ID']
                        st.session_state.show_po_form = True
                        st.rerun()
    
    if warning > 0:
        st.subheader("🟡 Warning - Reorder Soon")
        warning_items = alerts[alerts['Alert_Status'] == 'WARNING']
        display_data = []
        for _, item in warning_items.iterrows():
            qty = int(item['Quantity_On_Hand']) if not pd.isna(item['Quantity_On_Hand']) else 0
            reorder = int(item['Reorder_Level']) if not pd.isna(item['Reorder_Level']) else 0
            days = float(item['Days_Until_Stockout']) if not pd.isna(item['Days_Until_Stockout']) else 0
            display_data.append({
                'Product': item['Product_Name'],
                'Stock': qty,
                'Reorder Level': reorder,
                'Days Left': days
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)

def show_executive_dashboard():
    st.markdown('<div class="section-header">Executive Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(st.session_state.products_df)
        st.metric("Total Products", total_products)
    
    with col2:
        total_inventory = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        total_inventory = int(total_inventory) if not pd.isna(total_inventory) else 0
        st.metric("Items in Stock", f"{total_inventory:,}")
    
    with col3:
        inventory_val = st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        )
        inventory_val['Value'] = inventory_val['Quantity_On_Hand'] * inventory_val['Unit_Cost_BND']
        total_value = inventory_val['Value'].sum()
        total_value = float(total_value) if not pd.isna(total_value) else 0
        st.metric("Inventory Value", f"B${total_value:,.0f}")
    
    with col4:
        alerts = len(st.session_state.alerts_df[st.session_state.alerts_df['Alert_Status'] == 'CRITICAL'])
        st.metric("Critical Alerts", alerts)
    
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
    
    st.subheader("Recent Transactions")
    recent = st.session_state.transactions_df.sort_values('Date', ascending=False).head(10)
    st.dataframe(recent[['Date', 'Transaction_Type', 'Product_Name', 'Quantity']], use_container_width=True)

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    st.sidebar.title("Menu")
    
    # Google Drive Sync Status
    with st.sidebar.container():
        st.markdown("### 📁 Google Drive Sync")
        
        if 'last_sync' in st.session_state and st.session_state.last_sync:
            st.success(f"✅ Last sync: {st.session_state.last_sync.strftime('%H:%M:%S')}")
        else:
            st.info("Not synced yet")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Load", use_container_width=True):
                with st.spinner("Loading from Drive..."):
                    if load_data_from_excel():
                        st.success("Data loaded!")
                        time.sleep(1)
                        st.rerun()
        
        with col2:
            if st.button("📤 Save", use_container_width=True):
                with st.spinner("Saving to Drive..."):
                    if save_data_to_excel():
                        st.success("Data saved!")
                        time.sleep(1)
                        st.rerun()
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Select:", [
        "Executive Dashboard",
        "Product Management",
        "Inventory by Location",
        "Purchase Orders",
        "Suppliers",
        "Transaction History",
        "Stock Alerts",
        "🤖 AI Innovations"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    
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
    elif page == "🤖 AI Innovations":
        show_ai_innovations()

if __name__ == "__main__":
    main()
