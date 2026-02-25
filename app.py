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
from collections import defaultdict
import warnings
import subprocess
import sys
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System with AI Vision",
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
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .code-block {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 4px;
        padding: 1rem;
        font-family: monospace;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# COMPUTER VISION DETECTION WITH MULTIPLE BACKENDS
# ============================================

CV_AVAILABLE = False
CV_BACKEND = None
CV_ERROR = None

# Try different CV backends
try:
    # Try OpenCV first
    import cv2
    CV_AVAILABLE = True
    CV_BACKEND = "opencv"
except ImportError as e:
    CV_ERROR = str(e)
    try:
        # Try Pillow as fallback for basic image processing
        from PIL import Image
        CV_AVAILABLE = True
        CV_BACKEND = "pillow"
    except ImportError:
        CV_ERROR = "No image processing libraries available"

# Try YOLO/ML libraries
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import supervision as sv
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False

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
if 'vision_demo_mode' not in st.session_state:
    st.session_state.vision_demo_mode = False
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
if 'show_install_guide' not in st.session_state:
    st.session_state.show_install_guide = False

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
    
    # Suppliers
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
    
    # Products
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
    
    # Inventory (simplified for this version)
    inventory_data = []
    inventory_counter = 1
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in enumerate(locations_df.iterrows()):
            qty = 50 + ((i + j) * 17) % 150
            inventory_data.append({
                'Inventory_ID': f'INV{inventory_counter:06d}',
                'Product_ID': prod,
                'Product_Name': products.iloc[i]['Product_Name'],
                'Location_ID': loc[1]['Location_ID'],
                'Location_Name': loc[1]['Location_Name'],
                'Quantity_On_Hand': qty,
                'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            inventory_counter += 1
    
    inventory = pd.DataFrame(inventory_data)
    
    # Transactions (simplified)
    transactions_data = []
    for i in range(50):
        prod_idx = i % len(products)
        prod = products.iloc[prod_idx]
        transactions_data.append({
            'Transaction_ID': f'TXN{i:04d}',
            'Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'Product_ID': prod['Product_ID'],
            'Product_Name': prod['Product_Name'],
            'Quantity': random.randint(1, 20),
            'Type': random.choice(['IN', 'OUT'])
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Purchase Orders (simplified)
    purchase_orders_data = []
    for i in range(20):
        supplier_idx = i % len(suppliers)
        supplier = suppliers.iloc[supplier_idx]
        product_idx = i % len(products)
        product = products.iloc[product_idx]
        
        purchase_orders_data.append({
            'PO_Number': f'PO-{i:04d}',
            'PO_Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'Supplier_Name': supplier['Supplier_Name'],
            'Product_Name': product['Product_Name'],
            'Quantity': random.randint(50, 200),
            'Status': random.choice(['Draft', 'Approved', 'Received'])
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Alerts
    alerts_data = []
    for i, prod in products.iterrows():
        stock = random.randint(0, 50)
        if stock < prod['Reorder_Level']:
            alerts_data.append({
                'Product_ID': prod['Product_ID'],
                'Product_Name': prod['Product_Name'],
                'Current_Stock': stock,
                'Reorder_Level': prod['Reorder_Level'],
                'Status': 'CRITICAL' if stock < prod['Reorder_Level']/2 else 'WARNING'
            })
    
    alerts = pd.DataFrame(alerts_data) if alerts_data else pd.DataFrame()
    
    return products, inventory, transactions, suppliers, purchase_orders, alerts, locations_df, pd.DataFrame()

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
# VISION SYSTEM WITH MULTIPLE BACKENDS
# ============================================

def check_system_dependencies():
    """Check and display system dependency status"""
    st.markdown("### System Dependencies Check")
    
    deps = {
        "libGL.so.1": "OpenGL library",
        "libgomp.so.1": "OpenMP library",
        "libgcc_s.so.1": "GCC runtime"
    }
    
    for dep, name in deps.items():
        try:
            # Try to run ldconfig to check for libraries
            result = subprocess.run(['ldconfig', '-p'], capture_output=True, text=True)
            if dep in result.stdout:
                st.success(f"✅ {name}: Found")
            else:
                st.warning(f"⚠️ {name}: Not found")
        except Exception as e:
            st.warning(f"⚠️ {name}: Could not check ({str(e)})")

def show_installation_guide():
    """Show detailed installation guide"""
    st.markdown("""
    <div class="error-box">
        <h3>🔧 System Dependencies Missing</h3>
        <p>The error <code>libGL.so.1: cannot open shared object file</code> indicates missing system libraries.</p>
    </div>
    
    <h4>For Streamlit Cloud Deployment:</h4>
    <div class="code-block">
        # Create a packages.txt file in your repository root with:
        libgl1-mesa-glx
        libglib2.0-0
        libsm6
        libxext6
        libxrender-dev
        libgomp1
        libgcc-s1
    </div>
    
    <h4>For Local Development (Ubuntu/Debian):</h4>
    <div class="code-block">
        sudo apt-get update
        sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
    </div>
    
    <h4>For Local Development (macOS):</h4>
    <div class="code-block">
        brew install libomp
        brew install glib
    </div>
    
    <h4>Alternative: Use Headless OpenCV</h4>
    <div class="code-block">
        pip uninstall opencv-python
        pip install opencv-python-headless
    </div>
    """, unsafe_allow_html=True)

class SimpleVisionSystem:
    """Simplified vision system using PIL if OpenCV is not available"""
    
    def __init__(self):
        self.backend = CV_BACKEND
        self.frame_count = 0
        
    def process_frame(self, frame_data=None):
        """Process a frame or generate simulated data"""
        if self.backend == "opencv":
            return self._process_with_opencv()
        else:
            return self._generate_simulated_data()
    
    def _process_with_opencv(self):
        """Process with OpenCV (simulated for now)"""
        # This would contain actual OpenCV code
        # For now, return simulated data
        return self._generate_simulated_data()
    
    def _generate_simulated_data(self):
        """Generate simulated detection data"""
        self.frame_count += 1
        
        # Simulate varying counts
        person_count = 5 + int(3 * np.sin(self.frame_count / 10)) + random.randint(-2, 2)
        person_count = max(0, person_count)
        
        object_counts = {
            'person': person_count,
            'forklift': random.randint(0, 3),
            'pallet': random.randint(5, 15),
            'box': random.randint(20, 50)
        }
        
        return {
            'timestamp': datetime.now(),
            'person_count': person_count,
            'object_counts': object_counts,
            'total_objects': sum(object_counts.values()),
            'confidence': random.uniform(0.85, 0.98)
        }

def create_vision_visualization(data):
    """Create a visualization of vision data"""
    import plotly.graph_objects as go
    
    # Create a grid heatmap
    grid_size = 30
    heatmap_data = np.zeros((grid_size, grid_size))
    
    # Add "detections" based on object counts
    for _ in range(data['total_objects']):
        x = random.randint(0, grid_size-1)
        y = random.randint(0, grid_size-1)
        heatmap_data[x, y] += random.uniform(0.5, 1.0)
    
    # Add people with higher intensity
    for _ in range(data['person_count']):
        x = random.randint(0, grid_size-1)
        y = random.randint(0, grid_size-1)
        heatmap_data[x, y] += random.uniform(1.5, 2.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        colorscale='Viridis',
        showscale=False,
        hovertemplate='X: %{x}<br>Y: %{y}<br>Intensity: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=400,
        title=f"Live Detection View - {data['timestamp'].strftime('%H:%M:%S')}",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # Add annotations for object types
    annotations = []
    y_pos = 0.95
    for obj, count in data['object_counts'].items():
        if count > 0:
            annotations.append(dict(
                x=0.02,
                y=y_pos,
                xref="paper",
                yref="paper",
                text=f"• {obj}: {count}",
                showarrow=False,
                font=dict(size=12, color="white"),
                bgcolor="rgba(0,0,0,0.5)"
            ))
            y_pos -= 0.05
    
    fig.update_layout(annotations=annotations)
    
    return fig

def show_vision_demo():
    """Show enhanced vision demo with simulated data"""
    st.markdown('<div class="success-box">📹 Vision Demo Mode - Simulated Data</div>', unsafe_allow_html=True)
    
    # Initialize vision system
    if 'vision_system' not in st.session_state:
        st.session_state.vision_system = SimpleVisionSystem()
    if 'detection_history' not in st.session_state:
        st.session_state.detection_history = []
    
    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎮 Start Simulation"):
            st.session_state.simulation_running = True
    with col2:
        if st.button("⏹️ Stop Simulation"):
            st.session_state.simulation_running = False
    with col3:
        update_rate = st.slider("Update Rate (Hz)", 1, 10, 5)
    
    # Main display area
    feed_placeholder = st.empty()
    stats_cols = st.columns(4)
    chart_placeholder = st.empty()
    
    # Run simulation
    if st.session_state.get('simulation_running', False):
        # Create a placeholder for the loop
        simulation_placeholder = st.empty()
        
        while st.session_state.simulation_running:
            # Get simulated data
            data = st.session_state.vision_system.process_frame()
            st.session_state.detection_history.append(data)
            
            # Keep last 100 records
            if len(st.session_state.detection_history) > 100:
                st.session_state.detection_history = st.session_state.detection_history[-100:]
            
            # Update display
            with feed_placeholder.container():
                # Create a visual representation
                fig = create_vision_visualization(data)
                st.plotly_chart(fig, use_container_width=True)
            
            # Update metrics
            with stats_cols[0]:
                st.metric("People", data['person_count'])
            with stats_cols[1]:
                st.metric("Total Objects", data['total_objects'])
            with stats_cols[2]:
                st.metric("Confidence", f"{data['confidence']*100:.1f}%")
            with stats_cols[3]:
                st.metric("FPS", update_rate)
            
            # Update history chart
            if len(st.session_state.detection_history) > 1:
                hist_df = pd.DataFrame(st.session_state.detection_history)
                fig2 = px.line(hist_df, y=['person_count', 'total_objects'], 
                              title="Detection History")
                chart_placeholder.plotly_chart(fig2, use_container_width=True)
            
            # Check if we should stop
            if not st.session_state.simulation_running:
                break
            
            time.sleep(1/update_rate)
    
    # Export option
    if st.button("📥 Export Detection Data"):
        if st.session_state.detection_history:
            df = pd.DataFrame(st.session_state.detection_history)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                file_name=f"vision_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def show_vision_system():
    """Main vision system interface"""
    st.markdown('<div class="section-header">👁️ AI Vision System</div>', unsafe_allow_html=True)
    
    # Check if we're in demo mode
    if st.session_state.get('vision_demo_mode', False):
        show_vision_demo()
        if st.button("Exit Demo Mode"):
            st.session_state.vision_demo_mode = False
            st.session_state.simulation_running = False
            st.rerun()
        return
    
    # Show current status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### System Status")
        if CV_AVAILABLE:
            st.success(f"✅ Computer Vision: Available (Backend: {CV_BACKEND})")
            
            if YOLO_AVAILABLE:
                st.success("✅ YOLO: Available")
            else:
                st.warning("⚠️ YOLO: Not installed (for object detection)")
            
            if SUPERVISION_AVAILABLE:
                st.success("✅ Supervision: Available")
            else:
                st.warning("⚠️ Supervision: Not installed (for tracking)")
        else:
            st.error(f"❌ Computer Vision: Not available")
            if CV_ERROR:
                st.code(f"Error: {CV_ERROR}")
    
    with col2:
        st.markdown("### Quick Actions")
        if st.button("🎮 Try Demo Mode (No Camera Needed)"):
            st.session_state.vision_demo_mode = True
            st.rerun()
        
        if st.button("🔧 Show Installation Guide"):
            st.session_state.show_install_guide = not st.session_state.show_install_guide
    
    # Show installation guide if requested
    if st.session_state.get('show_install_guide', False):
        show_installation_guide()
    
    # System dependencies check
    with st.expander("🔍 System Dependencies Check"):
        check_system_dependencies()
    
    # If OpenCV is available but missing system libs, show fix
    if CV_ERROR and 'libGL' in str(CV_ERROR):
        st.markdown("""
        <div class="warning-box">
            <h4>📦 Missing System Libraries</h4>
            <p>Create a <code>packages.txt</code> file in your repository root with:</p>
            <pre><code>libgl1-mesa-glx
libglib2.0-0
libsm6
libxext6
libxrender-dev
libgomp1</code></pre>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button for packages.txt
        packages_content = """libgl1-mesa-glx
libglib2.0-0
libsm6
libxext6
libxrender-dev
libgomp1"""
        
        st.download_button(
            "📥 Download packages.txt",
            packages_content,
            file_name="packages.txt",
            mime="text/plain"
        )

# ============================================
# AI CHATBOT
# ============================================

class WarehouseChatbot:
    def __init__(self):
        pass
    
    def get_response(self, query):
        query_lower = query.lower()
        
        if 'inventory' in query_lower:
            total_items = st.session_state.inventory_df['Quantity_On_Hand'].sum()
            return f"📊 Current total inventory: {int(total_items):,} units"
        elif 'product' in query_lower:
            return f"📦 Total products: {len(st.session_state.products_df)}"
        elif 'alert' in query_lower or 'low stock' in query_lower:
            if st.session_state.alerts_df is not None and len(st.session_state.alerts_df) > 0:
                critical = len(st.session_state.alerts_df[st.session_state.alerts_df['Status'] == 'CRITICAL'])
                return f"⚠️ {critical} critical alerts, {len(st.session_state.alerts_df)-critical} warnings"
            else:
                return "✅ No active alerts"
        elif 'supplier' in query_lower:
            return f"🏢 {len(st.session_state.suppliers_df)} suppliers in database"
        elif 'order' in query_lower:
            return f"📋 {len(st.session_state.purchase_orders_df)} purchase orders"
        else:
            return """🤖 I can help you with:
- 📦 Inventory queries
- ⚠️ Stock alerts
- 🏢 Supplier information
- 📊 Reports and analytics
What would you like to know?"""

def show_ai_chatbot():
    st.markdown('<div class="section-header">🤖 Warehouse AI Assistant</div>', unsafe_allow_html=True)
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = WarehouseChatbot()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history[-10:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your warehouse..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = st.session_state.chatbot.get_response(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Clear button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ============================================
# PAGE FUNCTIONS
# ============================================

def show_executive_dashboard():
    st.markdown('<div class="section-header">📊 Executive Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(st.session_state.products_df))
    with col2:
        total_inventory = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        st.metric("Items in Stock", f"{int(total_inventory):,}")
    with col3:
        total_value = total_inventory * st.session_state.products_df['Unit_Cost_BND'].mean()
        st.metric("Inventory Value", f"B${total_value:,.0f}")
    with col4:
        alerts = len(st.session_state.alerts_df) if st.session_state.alerts_df is not None else 0
        st.metric("Active Alerts", alerts)
    
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

def show_product_crud():
    st.markdown('<div class="section-header">📦 Product Management</div>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Search products", "")
    
    df = st.session_state.products_df
    if search:
        df = df[df['Product_Name'].str.contains(search, case=False) | 
                df['Product_ID'].str.contains(search, case=False)]
    
    st.dataframe(df[['Product_ID', 'Product_Name', 'Category', 'Unit_Cost_BND', 'Selling_Price_BND', 'Status']], 
                 use_container_width=True)

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
    
    st.dataframe(display_df, use_container_width=True)

def show_purchase_orders():
    st.markdown('<div class="section-header">📋 Purchase Orders</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.purchase_orders_df, use_container_width=True)

def show_suppliers():
    st.markdown('<div class="section-header">🏢 Suppliers</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_transactions():
    st.markdown('<div class="section-header">📊 Transactions</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.transactions_df, use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">⚠️ Stock Alerts</div>', unsafe_allow_html=True)
    
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

def show_ai_innovations():
    st.markdown('<div class="section-header">🤖 AI Warehouse Innovations</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👁️ Vision System",
        "📍 Smart Bin Optimization",
        "📈 Demand Forecasting",
        "👥 Labor Optimization",
        "🤖 AI Chatbot",
        "📋 Integration"
    ])
    
    with tab1:
        show_vision_system()
    
    with tab2:
        st.subheader("📍 Smart Bin Optimization")
        st.info("Optimize bin locations based on product movement")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Efficiency", "67%")
        with col2:
            st.metric("Optimized Efficiency", "89%", "+22%")
    
    with tab3:
        st.subheader("📈 Demand Forecasting")
        
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast = pd.DataFrame({
            'Date': dates,
            'Forecast': [100 + 20*np.sin(i/7) + random.randint(-10, 10) for i in range(30)]
        })
        
        fig = px.line(forecast, x='Date', y='Forecast', title="30-Day Demand Forecast")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("👥 Labor Optimization")
        st.info("Optimize workforce allocation based on demand")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Staff", "27")
        with col2:
            st.metric("Optimal Staff", "24", "-3")
    
    with tab5:
        show_ai_chatbot()
    
    with tab6:
        st.subheader("📋 System Integration")
        st.markdown("""
        **Available Integrations:**
        - ✅ Inventory Management
        - ✅ Purchase Orders
        - ✅ Supplier Directory
        - ⏳ Computer Vision (Requires setup)
        - ⏳ Barcode Scanning (Coming soon)
        """)

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">📦 Stock Inventory System with AI Vision</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.title("Menu")
        
        page = st.radio("Navigate to:", [
            "Executive Dashboard",
            "Product Management",
            "Inventory by Location",
            "Purchase Orders",
            "Suppliers",
            "Transaction History",
            "Stock Alerts",
            "🤖 AI Innovations"
        ])
        
        st.markdown("---")
        
        # Status indicators
        if CV_AVAILABLE:
            st.success(f"✅ Vision: {CV_BACKEND}")
        else:
            st.warning("⚠️ Vision: Limited")
            if st.button("🎮 Try Demo"):
                st.session_state.vision_demo_mode = True
        
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
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
    elif page == "🤖 AI Innovations":
        show_ai_innovations()

if __name__ == "__main__":
    main()
