"""
Stock Inventory System with AI Vision
Compatible with Streamlit Cloud and IP Camera Lite
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import numpy as np
import json
from collections import defaultdict
import warnings
import sys
import os

# Suppress warnings
warnings.filterwarnings('ignore')

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
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1e3c72;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #2c3e50;
        margin: 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #3498db;
    }
    
    .info-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    
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
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .camera-status {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
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
if 'locations_df' not in st.session_state:
    st.session_state.locations_df = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'vision_enabled' not in st.session_state:
    st.session_state.vision_enabled = False
if 'camera_connected' not in st.session_state:
    st.session_state.camera_connected = False
if 'camera_url' not in st.session_state:
    st.session_state.camera_url = "http://192.168.100.158:8081"
if 'person_count' not in st.session_state:
    st.session_state.person_count = 0
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

# Try to import camera libraries
CAMERA_AVAILABLE = False
CAMERA_ERROR = None

try:
    import requests
    import cv2
    import numpy as np
    CAMERA_AVAILABLE = True
except ImportError as e:
    CAMERA_ERROR = str(e)

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data"""
    
    # Locations
    locations = [
        {'Location_ID': 'LOC001', 'Location_Name': 'Warehouse A - Beribi', 'Manager': 'Ali Rahman'},
        {'Location_ID': 'LOC002', 'Location_Name': 'Store 1 - Gadong', 'Manager': 'Siti Aminah'},
        {'Location_ID': 'LOC003', 'Location_Name': 'Store 2 - Kiulap', 'Manager': 'John Lee'},
        {'Location_ID': 'LOC004', 'Location_Name': 'Store 3 - Kuala Belait', 'Manager': 'Hassan Bakar'},
        {'Location_ID': 'LOC005', 'Location_Name': 'Store 4 - Tutong', 'Manager': 'Nurul Huda'},
    ]
    locations_df = pd.DataFrame(locations)
    
    # Suppliers
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', 'lim@huaho.com', 'Electronics'],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', 'mei.ling@soonlee.com', 'Groceries'],
        ['SUP003', 'Supasave', 'David Wong', 'david@supasave.com', 'General'],
        ['SUP004', 'Seng Huat Trading', 'Michael Chen', 'michael@senghuat.com', 'Hardware'],
        ['SUP005', 'SKH Group', 'Steven Khoo', 'steven@skh.com', 'Electronics'],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Email', 'Category'
    ])
    
    # Products
    products_data = [
        ['PRD00001', 'Samsung 55" 4K TV', 'Electronics', 785.00, 1135.09, 10, 'SUP001', 'Active'],
        ['PRD00002', 'iPhone 15 Pro', 'Electronics', 916.00, 1351.05, 35, 'SUP005', 'Active'],
        ['PRD00003', 'MacBook Air M2', 'Electronics', 618.00, 872.40, 25, 'SUP005', 'Active'],
        ['PRD00004', 'Basmati Rice 5kg', 'Groceries', 8.00, 9.81, 50, 'SUP002', 'Active'],
        ['PRD00005', 'Cooking Oil 2L', 'Groceries', 11.00, 14.28, 40, 'SUP002', 'Active'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'Product_Name', 'Category', 'Unit_Cost', 'Selling_Price', 
        'Reorder_Level', 'Supplier_ID', 'Status'
    ])
    
    # Inventory
    inventory_data = []
    for i, prod in enumerate(products['Product_ID']):
        for j, (_, loc) in enumerate(locations_df.iterrows()):
            qty = 50 + ((i + j) * 10) % 100
            inventory_data.append({
                'Inventory_ID': f'INV{i:03d}{j:03d}',
                'Product_ID': prod,
                'Product_Name': products.iloc[i]['Product_Name'],
                'Location_ID': loc['Location_ID'],
                'Location_Name': loc['Location_Name'],
                'Quantity': qty,
            })
    
    inventory = pd.DataFrame(inventory_data)
    
    # Alerts
    alerts_data = []
    for _, prod in products.iterrows():
        total_qty = inventory[inventory['Product_ID'] == prod['Product_ID']]['Quantity'].sum()
        if total_qty < prod['Reorder_Level']:
            alerts_data.append({
                'Product_ID': prod['Product_ID'],
                'Product_Name': prod['Product_Name'],
                'Current_Stock': total_qty,
                'Reorder_Level': prod['Reorder_Level'],
                'Status': 'CRITICAL' if total_qty < prod['Reorder_Level']/2 else 'WARNING'
            })
    
    alerts = pd.DataFrame(alerts_data)
    
    return products, inventory, suppliers, alerts, locations_df

# Initialize data
if st.session_state.products_df is None:
    (st.session_state.products_df, 
     st.session_state.inventory_df, 
     st.session_state.suppliers_df, 
     st.session_state.alerts_df,
     st.session_state.locations_df) = load_initial_data()

# ============================================
# CAMERA FUNCTIONS
# ============================================

def test_camera_connection(url):
    """Test if camera is reachable"""
    try:
        # Try different endpoints
        endpoints = ['/shot.jpg', '/photo.jpg', '/']
        
        for endpoint in endpoints:
            try:
                full_url = url.rstrip('/') + endpoint
                response = requests.get(full_url, timeout=3)
                if response.status_code == 200:
                    if endpoint == '/' or len(response.content) > 1000:
                        return True, f"Connected via {endpoint}"
            except:
                continue
        return False, "Could not connect to camera"
    except Exception as e:
        return False, str(e)

def get_camera_frame(url):
    """Get a single frame from camera"""
    try:
        endpoints = ['/shot.jpg', '/photo.jpg']
        
        for endpoint in endpoints:
            try:
                full_url = url.rstrip('/') + endpoint
                response = requests.get(full_url, timeout=2)
                if response.status_code == 200 and len(response.content) > 1000:
                    # Convert to numpy array
                    img_array = np.frombuffer(response.content, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if frame is not None:
                        # Resize for performance
                        height, width = frame.shape[:2]
                        if width > 640:
                            scale = 640 / width
                            new_width = 640
                            new_height = int(height * scale)
                            frame = cv2.resize(frame, (new_width, new_height))
                        return frame
            except:
                continue
        return None
    except:
        return None

def detect_people(frame):
    """Simple people detection using motion and contours"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Initialize background if needed
        if not hasattr(st.session_state, 'background'):
            st.session_state.background = gray.copy().astype(float)
            return frame, 0
        
        # Update background
        cv2.accumulateWeighted(gray, st.session_state.background, 0.5)
        
        # Find differences
        diff = cv2.absdiff(gray, cv2.convertScaleAbs(st.session_state.background))
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        person_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < area < 50000:  # Person-sized objects
                person_count += 1
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Person", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, person_count
    except:
        return frame, 0

# ============================================
# PAGE FUNCTIONS
# ============================================

def show_dashboard():
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(st.session_state.products_df))
    with col2:
        total_inventory = st.session_state.inventory_df['Quantity'].sum()
        st.metric("Items in Stock", f"{int(total_inventory):,}")
    with col3:
        total_value = total_inventory * st.session_state.products_df['Unit_Cost'].mean()
        st.metric("Inventory Value", f"${total_value:,.0f}")
    with col4:
        alerts = len(st.session_state.alerts_df) if st.session_state.alerts_df is not None else 0
        st.metric("Active Alerts", alerts)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock by Category")
        cat_stock = st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Category']], on='Product_ID'
        ).groupby('Category')['Quantity'].sum().reset_index()
        fig = px.pie(cat_stock, values='Quantity', names='Category')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Stock by Location")
        loc_stock = st.session_state.inventory_df.groupby('Location_Name')['Quantity'].sum().reset_index()
        fig = px.bar(loc_stock, x='Location_Name', y='Quantity')
        st.plotly_chart(fig, use_container_width=True)

def show_products():
    st.markdown('<div class="section-header">📦 Products</div>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search products", "")
    
    df = st.session_state.products_df.copy()
    if search:
        df = df[df['Product_Name'].str.contains(search, case=False) | 
                df['Product_ID'].str.contains(search, case=False)]
    
    st.dataframe(df, use_container_width=True)

def show_inventory():
    st.markdown('<div class="section-header">📍 Inventory</div>', unsafe_allow_html=True)
    
    location = st.selectbox("Select Location", 
        ['All'] + st.session_state.locations_df['Location_Name'].tolist())
    
    df = st.session_state.inventory_df
    if location != 'All':
        df = df[df['Location_Name'] == location]
    
    st.dataframe(df, use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">⚠️ Alerts</div>', unsafe_allow_html=True)
    
    if st.session_state.alerts_df is not None and len(st.session_state.alerts_df) > 0:
        for _, alert in st.session_state.alerts_df.iterrows():
            color = "badge-critical" if alert['Status'] == 'CRITICAL' else "badge-warning"
            st.markdown(f"""
            <div class="info-card">
                <span class="{color}">{alert['Status']}</span>
                <h3>{alert['Product_Name']}</h3>
                <p>Current Stock: {alert['Current_Stock']} | Reorder Level: {alert['Reorder_Level']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("✅ No active alerts")

def show_vision():
    st.markdown('<div class="section-header">👁️ Vision System</div>', unsafe_allow_html=True)
    
    if not CAMERA_AVAILABLE:
        st.warning("⚠️ Camera libraries not available. Install: opencv-python-headless and requests")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Camera Settings")
        
        # Camera URL input
        camera_url = st.text_input(
            "Camera URL",
            value=st.session_state.camera_url,
            help="URL from IP Camera Lite app (e.g., http://192.168.100.158:8081)"
        )
        st.session_state.camera_url = camera_url
        
        # Test connection button
        if st.button("🔌 Test Connection", use_container_width=True):
            with st.spinner("Testing camera connection..."):
                success, message = test_camera_connection(camera_url)
                if success:
                    st.success(f"✅ Connected! {message}")
                    st.balloons()
                else:
                    st.error(f"❌ Failed: {message}")
        
        # Connect button
        if st.button("📱 Start Camera", use_container_width=True, type="primary"):
            st.session_state.camera_connected = True
        
        # Vision toggle
        if st.session_state.camera_connected:
            st.session_state.vision_enabled = st.toggle(
                "🔍 Enable People Detection",
                value=st.session_state.vision_enabled
            )
    
    with col2:
        st.markdown("### Instructions")
        st.info("""
        1. Install IP Camera Lite on iPhone
        2. Open app and tap "Start Server"
        3. Enter URL above
        4. Click "Test Connection"
        5. Click "Start Camera"
        """)
    
    # Live feed
    if st.session_state.camera_connected:
        st.markdown("### 📹 Live Feed")
        
        # Get frame
        frame = get_camera_frame(st.session_state.camera_url)
        
        if frame is not None:
            # Detect people if enabled
            if st.session_state.vision_enabled:
                frame, person_count = detect_people(frame)
                st.session_state.person_count = person_count
                
                # Update history
                st.session_state.detection_history.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'people': person_count
                })
                if len(st.session_state.detection_history) > 50:
                    st.session_state.detection_history = st.session_state.detection_history[-50:]
            
            # Display frame
            st.image(frame, channels="BGR", use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("People Detected", st.session_state.person_count)
            with col2:
                st.metric("Frame Size", f"{frame.shape[1]}x{frame.shape[0]}")
            with col3:
                if st.button("⏹️ Stop Camera"):
                    st.session_state.camera_connected = False
                    st.session_state.vision_enabled = False
                    st.rerun()
            
            # History chart
            if st.session_state.detection_history:
                hist_df = pd.DataFrame(st.session_state.detection_history)
                fig = px.line(hist_df, x='time', y='people', title="People Detection History")
                st.plotly_chart(fig, use_container_width=True)
            
            # Auto-refresh
            time.sleep(0.1)
            st.rerun()
        else:
            st.warning("⚠️ Waiting for camera feed...")
            if st.button("⏹️ Disconnect"):
                st.session_state.camera_connected = False
                st.rerun()

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">📦 Stock Inventory System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Menu")
        
        page = st.radio("Navigate to:", [
            "Dashboard",
            "Products",
            "Inventory",
            "Alerts",
            "👁️ Vision System"
        ])
        
        st.markdown("---")
        
        # Status
        if st.session_state.camera_connected:
            st.success("📱 Camera: Connected")
        else:
            st.info("📱 Camera: Disconnected")
        
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "Products":
        show_products()
    elif page == "Inventory":
        show_inventory()
    elif page == "Alerts":
        show_alerts()
    elif page == "👁️ Vision System":
        show_vision()

if __name__ == "__main__":
    main()
