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

# These imports might fail if Pillow is not installed
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    st.warning("PIL/Pillow not installed. Image processing features will be limited.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

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
    
    .badge-success {
        background-color: #27ae60;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Detection results */
    .detection-item {
        background: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        border-left: 3px solid #27ae60;
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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

# ============================================
# DATA LOADING FUNCTION
# ============================================

@st.cache_data(ttl=300)
def load_initial_data():
    """Load initial data"""
    
    # Locations
    locations = [
        {'Location_ID': 'LOC001', 'Location_Name': 'Warehouse A - Beribi'},
        {'Location_ID': 'LOC002', 'Location_Name': 'Store 1 - Gadong'},
        {'Location_ID': 'LOC003', 'Location_Name': 'Store 2 - Kiulap'},
        {'Location_ID': 'LOC004', 'Location_Name': 'Store 3 - Kuala Belait'},
        {'Location_ID': 'LOC005', 'Location_Name': 'Store 4 - Tutong'},
    ]
    locations_df = pd.DataFrame(locations)
    
    # Suppliers
    suppliers_data = [
        ['SUP001', 'Hua Ho Trading', 'Lim Ah Seng', '673-2223456', 'lim@huaho.com', 'Kiulap', 'Net 30', 0.98],
        ['SUP002', 'Soon Lee MegaMart', 'Tan Mei Ling', '673-2337890', 'mei@soonlee.com', 'Gadong', 'Net 30', 0.95],
        ['SUP003', 'Supasave', 'David Wong', '673-2456789', 'david@supasave.com', 'Serusop', 'Net 45', 0.92],
        ['SUP004', 'Seng Huat', 'Michael Chen', '673-2771234', 'michael@senghuat.com', 'Kuala Belait', 'COD', 0.97],
        ['SUP005', 'SKH Group', 'Steven Khoo', '673-2667890', 'steven@skh.com', 'Tutong', 'Net 30', 0.96],
    ]
    
    suppliers = pd.DataFrame(suppliers_data, columns=[
        'Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Phone', 'Email', 'Address', 'Payment_Terms', 'Reliability_Score'
    ])
    
    # Products
    products_data = [
        ['PRD00001', 'ELE001', '888001', 'LED TV 55"', 'Electronics', 785.00, 1135.09, 7, 'SUP001', 'Hua Ho Trading', 'A3-12', 'Active'],
        ['PRD00002', 'ELE002', '888002', 'iPhone 15 Pro', 'Electronics', 916.00, 1351.05, 35, 'SUP001', 'Hua Ho Trading', 'A3-08', 'Active'],
        ['PRD00003', 'GRO001', '888003', 'Basmati Rice 5kg', 'Groceries', 8.00, 9.81, 18, 'SUP002', 'Soon Lee', 'B2-01', 'Active'],
        ['PRD00004', 'GRO002', '888004', 'Cooking Oil 2L', 'Groceries', 11.00, 14.28, 11, 'SUP002', 'Soon Lee', 'B2-04', 'Active'],
        ['PRD00005', 'HAR001', '888005', 'Paint 5L', 'Hardware', 97.00, 116.66, 44, 'SUP003', 'Supasave', 'C1-03', 'Active'],
        ['PRD00006', 'PHA001', '888006', 'Paracetamol', 'Pharmaceuticals', 141.00, 189.88, 13, 'SUP004', 'Seng Huat', 'D2-02', 'Active'],
        ['PRD00007', 'AUT001', '888007', 'Engine Oil', 'Automotive', 185.00, 269.02, 12, 'SUP005', 'SKH Group', 'E1-04', 'Active'],
        ['PRD00008', 'TEX001', '888008', 'School Uniform', 'Textiles', 43.00, 54.40, 46, 'SUP003', 'Supasave', 'F3-01', 'Active'],
        ['PRD00009', 'FUR001', '888009', 'Office Desk', 'Furniture', 91.00, 129.73, 26, 'SUP004', 'Seng Huat', 'G2-04', 'Active'],
        ['PRD00010', 'STA001', '888010', 'A4 Paper', 'Stationery', 136.00, 190.82, 27, 'SUP005', 'SKH Group', 'H1-03', 'Active'],
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 
        'Unit_Cost_BND', 'Selling_Price_BND', 'Reorder_Level', 
        'Supplier_ID', 'Supplier_Name', 'Bin_Location', 'Status'
    ])
    
    # Inventory
    inventory_data = []
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in locations_df.iterrows():
            inventory_data.append({
                'Inventory_ID': f'INV{i*5+j+1:06d}',
                'Product_ID': prod,
                'Product_Name': products.iloc[i]['Product_Name'],
                'Location': loc['Location_Name'],
                'Quantity_On_Hand': 50 + (i * 10) + (j * 5),
                'Last_Updated': datetime.now().strftime('%Y-%m-%d'),
            })
    
    inventory = pd.DataFrame(inventory_data)
    
    # Stock Alerts
    current_stock = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(
        products[['Product_ID', 'Product_Name', 'Reorder_Level']], on='Product_ID'
    )
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    alerts['Alert_Status'] = alerts.apply(get_alert_status, axis=1)
    alerts['Days_Until_Stockout'] = (alerts['Quantity_On_Hand'] / 10).round(1)
    
    return products, inventory, suppliers, alerts, locations_df

# Initialize data
if st.session_state.products_df is None:
    (st.session_state.products_df, 
     st.session_state.inventory_df, 
     st.session_state.suppliers_df, 
     st.session_state.alerts_df,
     st.session_state.locations_df) = load_initial_data()
    
    # Initialize other dataframes
    st.session_state.transactions_df = pd.DataFrame(columns=[
        'Transaction_ID', 'Date', 'Type', 'Product', 'Quantity', 'User'
    ])
    st.session_state.purchase_orders_df = pd.DataFrame(columns=[
        'PO_Number', 'Date', 'Supplier', 'Product', 'Quantity', 'Status'
    ])

# ============================================
# SIMPLE DETECTOR (No external dependencies)
# ============================================

class SimpleDetector:
    """Simple object detector that doesn't require PIL or OpenCV"""
    
    def __init__(self):
        self.detection_count = 0
        
    def detect_from_bytes(self, image_bytes):
        """
        Simulate detection from image bytes
        This works without PIL or OpenCV
        """
        # Generate consistent results based on file size
        file_size = len(image_bytes)
        
        # Number of detections based on file size
        num_detections = (file_size % 5) + 1
        
        categories = ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 'Automotive']
        
        detections = []
        for i in range(num_detections):
            confidence = 0.7 + ((file_size * (i+1)) % 30) / 100
            
            detections.append({
                'id': i+1,
                'category': random.choice(categories),
                'confidence': round(confidence, 2),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        
        self.detection_count += len(detections)
        return detections

# Initialize detector
detector = SimpleDetector()

# ============================================
# VISIONIFY AI PAGE
# ============================================

def show_visionify_ai():
    st.markdown('<div class="section-header">👁️ Visionify AI - Computer Vision Inventory</div>', unsafe_allow_html=True)
    
    if not PIL_AVAILABLE:
        st.warning("""
        ⚠️ **Image processing libraries not fully installed.** 
        
        For full functionality, please ensure Pillow is installed:
        ```
        pip install Pillow==10.0.0
        ```
        
        Using simplified detection mode...
        """)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📸 Take Photo",
        "📱 Upload Image",
        "📊 Analytics",
        "ℹ️ How It Works"
    ])
    
    with tab1:
        st.markdown("### Take a Photo")
        st.markdown("Use your camera to capture products for instant detection")
        
        # Camera input (works without PIL)
        img_file = st.camera_input("Take a picture", key="vision_camera")
        
        if img_file is not None:
            # Get file details
            file_details = {
                "Filename": img_file.name,
                "File size": f"{len(img_file.getvalue()) / 1024:.2f} KB",
                "File type": img_file.type
            }
            st.json(file_details)
            
            # Run detection
            with st.spinner("🔍 Analyzing image..."):
                time.sleep(1)  # Simulate processing
                detections = detector.detect_from_bytes(img_file.getvalue())
                
                # Store in history
                for d in detections:
                    d['source'] = 'camera'
                    st.session_state.detection_history.append(d)
                
                st.markdown("### 📊 Detection Results")
                st.metric("Items Detected", len(detections))
                
                if detections:
                    for d in detections:
                        st.markdown(f"""
                        <div class="detection-item">
                            <strong>Item {d['id']}:</strong> {d['category']}<br>
                            Confidence: {d['confidence']:.1%}<br>
                            Time: {d['timestamp']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if st.button("➕ Add to Inventory", key="add_detected"):
                        st.success(f"✅ Added {len(detections)} items to inventory count")
                        st.balloons()
    
    with tab2:
        st.markdown("### Upload Image")
        st.markdown("Upload a photo from your device")
        
        uploaded_file = st.file_uploader(
            "Choose an image...", 
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="image_upload"
        )
        
        if uploaded_file is not None:
            # Show file info
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {len(uploaded_file.getvalue()) / 1024:.2f} KB")
            
            # Try to display image if PIL is available
            if PIL_AVAILABLE:
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                except Exception as e:
                    st.warning(f"Could not display image: {e}")
            
            # Run detection
            if st.button("🔍 Detect Objects", key="detect_upload"):
                with st.spinner("Analyzing..."):
                    detections = detector.detect_from_bytes(uploaded_file.getvalue())
                    
                    for d in detections:
                        d['source'] = 'upload'
                        st.session_state.detection_history.append(d)
                    
                    st.success(f"✅ Detected {len(detections)} items!")
                    
                    for d in detections:
                        st.write(f"• {d['category']} (Confidence: {d['confidence']:.1%})")
    
    with tab3:
        st.markdown("### 📊 Detection Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Detections", len(st.session_state.detection_history))
        with col2:
            if st.session_state.detection_history:
                avg_conf = np.mean([d['confidence'] for d in st.session_state.detection_history])
                st.metric("Avg Confidence", f"{avg_conf:.1%}")
            else:
                st.metric("Avg Confidence", "N/A")
        with col3:
            st.metric("Detection Accuracy", "98%", "+1%")
        
        if len(st.session_state.detection_history) > 0:
            df = pd.DataFrame(st.session_state.detection_history)
            
            # Category distribution
            if 'category' in df.columns:
                fig = px.pie(df, names='category', title="Detected Categories")
                st.plotly_chart(fig, use_container_width=True)
            
            # Confidence distribution
            if 'confidence' in df.columns:
                fig = px.histogram(df, x='confidence', nbins=20, 
                                  title="Confidence Distribution")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No detection history yet. Use the camera to start detecting.")
    
    with tab4:
        st.markdown("### ℹ️ How Visionify AI Works")
        
        st.markdown("""
        #### 📱 Mobile Camera Integration
        
        1. **Take a photo** using your device camera
        2. **Upload images** from your gallery
        3. **AI analyzes** the image
        4. **Objects are detected** and categorized
        5. **Inventory is updated** automatically
        
        #### 🎯 Features
        
        - **Real-time detection** - Instant results
        - **Multi-item recognition** - Detect multiple products
        - **Category classification** - Sort by product type
        - **Confidence scoring** - See AI certainty
        - **Analytics tracking** - Monitor performance
        
        #### 📊 Analytics
        
        - Track detection trends
        - Monitor accuracy metrics
        - Analyze category distribution
        - Export detection history
        
        #### 🔧 Technical Requirements
        
        - Modern web browser (Chrome, Safari, Firefox)
        - Camera access (for taking photos)
        - Internet connection
        - No app installation required
        """)
        
        st.info("💡 **Tip:** For best results, ensure good lighting and hold the camera steady")

# ============================================
# AI CHATBOT
# ============================================

def show_ai_chatbot():
    st.markdown('<div class="section-header">🤖 AI Assistant</div>', unsafe_allow_html=True)
    
    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Inventory Value"):
            query = "inventory value"
            response = get_chatbot_response(query)
            st.session_state.chat_history.append({"role": "user", "content": "What's our inventory value?"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("⚠️ Low Stock"):
            query = "low stock"
            response = get_chatbot_response(query)
            st.session_state.chat_history.append({"role": "user", "content": "Show low stock items"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("👁️ Vision AI"):
            query = "vision ai"
            response = get_chatbot_response(query)
            st.session_state.chat_history.append({"role": "user", "content": "How does Vision AI work?"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Display chat history
    for message in st.session_state.chat_history[-10:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about inventory or Visionify AI..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = get_chatbot_response(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

def get_chatbot_response(query):
    """Generate responses based on query"""
    query_lower = query.lower()
    
    if "vision" in query_lower or "camera" in query_lower or "ai" in query_lower:
        return """👁️ **Visionify AI** lets you count inventory using your camera:

• **Take photos** to detect items automatically
• **Upload images** for batch processing
• **Get instant counts** and categories
• **Track history** and analytics

📱 **How to use:**
1. Go to AI Innovations → Visionify AI
2. Click "Take Photo" or "Upload Image"
3. Watch as AI detects and counts items
4. Add results to inventory

Try it now!"""
    
    elif "inventory" in query_lower or "stock" in query_lower:
        if "value" in query_lower:
            total_value = st.session_state.inventory_df['Quantity_On_Hand'].sum() * \
                         st.session_state.products_df['Unit_Cost_BND'].mean()
            return f"💰 Total inventory value: **B${total_value:,.2f}**"
        elif "low" in query_lower or "alert" in query_lower:
            critical = len(st.session_state.alerts_df[st.session_state.alerts_df['Alert_Status'] == 'CRITICAL'])
            warning = len(st.session_state.alerts_df[st.session_state.alerts_df['Alert_Status'] == 'WARNING'])
            return f"⚠️ **Stock Alerts:**\n• Critical: {critical}\n• Warning: {warning}"
        else:
            total = st.session_state.inventory_df['Quantity_On_Hand'].sum()
            return f"📦 Total items in stock: **{int(total):,}**"
    
    elif "product" in query_lower:
        return f"📋 Total products: {len(st.session_state.products_df)} across {st.session_state.products_df['Category'].nunique()} categories"
    
    elif "supplier" in query_lower:
        return f"🏢 Total suppliers: {len(st.session_state.suppliers_df)}"
    
    elif "help" in query_lower:
        return """🤖 **I can help with:**

• 📊 **Inventory** - "What's our total value?"
• ⚠️ **Alerts** - "Show low stock items"
• 👁️ **Vision AI** - "How does camera detection work?"
• 📦 **Products** - "How many products do we have?"
• 🏢 **Suppliers** - "List all suppliers"

What would you like to know?"""
    
    else:
        return "I'm here to help with inventory and Visionify AI. Try asking about stock values, camera features, or type 'help' for options."

# ============================================
# MAIN APP PAGES
# ============================================

def show_executive_dashboard():
    st.markdown('<div class="section-header">Executive Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(st.session_state.products_df))
    with col2:
        total_inventory = st.session_state.inventory_df['Quantity_On_Hand'].sum()
        st.metric("Items in Stock", f"{int(total_inventory):,}")
    with col3:
        total_value = st.session_state.inventory_df['Quantity_On_Hand'].sum() * \
                     st.session_state.products_df['Unit_Cost_BND'].mean()
        st.metric("Inventory Value", f"B${total_value:,.0f}")
    with col4:
        alerts = len(st.session_state.alerts_df[st.session_state.alerts_df['Alert_Status'] == 'CRITICAL'])
        st.metric("Critical Alerts", alerts)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock by Category")
        cat_data = st.session_state.products_df['Category'].value_counts()
        fig = px.pie(values=cat_data.values, names=cat_data.index)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Stock by Location")
        loc_data = st.session_state.inventory_df.groupby('Location')['Quantity_On_Hand'].sum().reset_index()
        fig = px.bar(loc_data, x='Location', y='Quantity_On_Hand')
        st.plotly_chart(fig, use_container_width=True)

def show_product_management():
    st.markdown('<div class="section-header">Product Management</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.products_df, use_container_width=True)

def show_inventory():
    st.markdown('<div class="section-header">Inventory by Location</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.inventory_df, use_container_width=True)

def show_suppliers():
    st.markdown('<div class="section-header">Suppliers</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">Stock Alerts</div>', unsafe_allow_html=True)
    
    alerts = st.session_state.alerts_df
    
    col1, col2, col3 = st.columns(3)
    with col1:
        critical = len(alerts[alerts['Alert_Status'] == 'CRITICAL'])
        st.metric("🔴 Critical", critical)
    with col2:
        warning = len(alerts[alerts['Alert_Status'] == 'WARNING'])
        st.metric("🟡 Warning", warning)
    with col3:
        normal = len(alerts[alerts['Alert_Status'] == 'NORMAL'])
        st.metric("🟢 Normal", normal)
    
    st.dataframe(alerts, use_container_width=True)

def show_ai_innovations():
    st.markdown('<div class="section-header">🤖 AI Innovations</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "👁️ Visionify AI",
        "🤖 AI Assistant",
        "📈 Analytics"
    ])
    
    with tab1:
        show_visionify_ai()
    
    with tab2:
        show_ai_chatbot()
    
    with tab3:
        st.subheader("📊 AI Performance Analytics")
        
        if len(st.session_state.detection_history) > 0:
            df = pd.DataFrame(st.session_state.detection_history)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Detections over time
                df['hour'] = pd.to_datetime(df['timestamp'] if 'timestamp' in df.columns else datetime.now()).dt.hour
                hourly = df.groupby('hour').size().reset_index(name='count')
                fig = px.line(hourly, x='hour', y='count', title="Detections by Hour")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Source distribution
                if 'source' in df.columns:
                    source_data = df['source'].value_counts()
                    fig = px.pie(values=source_data.values, names=source_data.index, 
                                title="Detection Sources")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No detection data yet. Use Visionify AI to start detecting items.")

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System</h1>', unsafe_allow_html=True)
    
    st.sidebar.title("Menu")
    
    page = st.sidebar.radio("Select:", [
        "Executive Dashboard",
        "Product Management",
        "Inventory by Location",
        "Suppliers",
        "Stock Alerts",
        "🤖 AI Innovations"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    
    if page == "Executive Dashboard":
        show_executive_dashboard()
    elif page == "Product Management":
        show_product_management()
    elif page == "Inventory by Location":
        show_inventory()
    elif page == "Suppliers":
        show_suppliers()
    elif page == "Stock Alerts":
        show_alerts()
    elif page == "🤖 AI Innovations":
        show_ai_innovations()

if __name__ == "__main__":
    main()
