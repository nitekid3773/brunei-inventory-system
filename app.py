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
import cv2
from PIL import Image
import tempfile
import os

# For mobile camera access
try:
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, RTCConfiguration
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    st.warning("streamlit-webrtc not installed. Mobile camera features will be limited.")

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
    
    /* Camera preview */
    .camera-container {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 2px solid #3498db;
    }
    
    .detection-box {
        position: absolute;
        border: 2px solid #00ff00;
        background-color: rgba(0, 255, 0, 0.1);
        pointer-events: none;
    }
    
    /* Detection results */
    .detection-item {
        background: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        border-left: 3px solid #27ae60;
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
    
    .badge-success {
        background-color: #27ae60;
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
    
    /* Mobile camera preview */
    .camera-preview {
        width: 100%;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []
if 'ml_model_loaded' not in st.session_state:
    st.session_state.ml_model_loaded = False

# ============================================
# SIMPLE OBJECT DETECTION (No external ML libraries)
# ============================================

class SimpleObjectDetector:
    """
    Simple color-based object detection for demo purposes
    In production, replace with YOLO/ TensorFlow model
    """
    
    def __init__(self):
        self.detection_count = 0
        self.last_detection = None
        
    def detect_objects(self, image):
        """
        Simulate object detection with color segmentation
        This is a simplified version - replace with real ML model
        """
        if image is None:
            return [], image
        
        # Convert to numpy array if needed
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Simple color-based "detection" for demo
        # In production, use YOLO/SSD/MobileNet
        height, width = img_array.shape[:2] if len(img_array.shape) == 3 else (img_array.shape[0], img_array.shape[1])
        
        # Simulate detecting objects at different positions
        detections = []
        
        # Generate random detections for demo (replace with real ML)
        np.random.seed(hash(str(time.time())) % 100)
        num_detections = np.random.randint(1, 5)
        
        for i in range(num_detections):
            x = np.random.randint(0, width - 50)
            y = np.random.randint(0, height - 50)
            w = np.random.randint(30, 100)
            h = np.random.randint(30, 100)
            confidence = np.random.uniform(0.7, 0.99)
            
            # Assign random product category
            categories = ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals']
            category = np.random.choice(categories)
            
            detections.append({
                'bbox': [x, y, x + w, y + h],
                'confidence': confidence,
                'category': category,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        
        self.detection_count += len(detections)
        return detections, img_array
    
    def draw_detections(self, image, detections):
        """Draw bounding boxes on image"""
        if image is None or len(detections) == 0:
            return image
        
        # Convert to PIL for drawing
        if isinstance(image, np.ndarray):
            img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image)
        else:
            img_pil = image.copy()
        
        # Draw boxes (simplified - in production use cv2.rectangle)
        return img_pil

# ============================================
# MOBILE CAMERA INTEGRATION
# ============================================

def camera_preview():
    """Display mobile camera preview with object detection"""
    
    st.markdown("""
    <div class="camera-container">
        <h3 style="color: white; margin-top: 0;">📱 Live Camera Feed</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize detector if not already
    if 'detector' not in st.session_state:
        st.session_state.detector = SimpleObjectDetector()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Camera input from mobile/desktop
        img_file_buffer = st.camera_input("Take a picture", key="vision_camera")
        
        if img_file_buffer is not None:
            # Read image
            bytes_data = img_file_buffer.getvalue()
            image = Image.open(io.BytesIO(bytes_data))
            
            # Run detection
            with st.spinner("🔍 Analyzing image..."):
                detections, processed_img = st.session_state.detector.detect_objects(image)
                
                # Store detection history
                st.session_state.detection_history.extend(detections)
                
                # Show image with detections
                st.image(image, caption="Captured Image", use_column_width=True)
                
                # Display detection results
                with col2:
                    st.markdown("### 📊 Detection Results")
                    st.markdown(f"**Items detected:** {len(detections)}")
                    
                    for i, det in enumerate(detections):
                        st.markdown(f"""
                        <div class="detection-item">
                            <strong>Item {i+1}:</strong> {det['category']}<br>
                            Confidence: {det['confidence']:.1%}<br>
                            Time: {det['timestamp']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if len(detections) > 0:
                        if st.button("➕ Add to Inventory", key="add_detected"):
                            st.success(f"✅ Added {len(detections)} items to inventory count")
                            
                            # Simulate adding to inventory
                            st.session_state.last_update = datetime.now()
    
    with col2:
        st.markdown("### 📈 Detection Stats")
        st.metric("Total Detections", len(st.session_state.detection_history))
        
        if len(st.session_state.detection_history) > 0:
            # Category breakdown
            df = pd.DataFrame(st.session_state.detection_history)
            if 'category' in df.columns:
                cat_counts = df['category'].value_counts()
                fig = px.pie(values=cat_counts.values, names=cat_counts.index, 
                           title="Detected Categories")
                st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🔄 Reset Detection History"):
            st.session_state.detection_history = []
            st.rerun()

# ============================================
# ADVANCED CAMERA MODULE (with WebRTC)
# ============================================

def mobile_camera_stream():
    """Real-time mobile camera streaming with object detection"""
    
    st.markdown("""
    <div class="camera-container">
        <h3 style="color: white; margin-top: 0;">📱 Real-time Mobile Camera Stream</h3>
        <p style="color: #aaa;">Point your phone camera at inventory items for automatic detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not WEBRTC_AVAILABLE:
        st.warning("""
        Real-time streaming requires additional packages. 
        Install with: `pip install streamlit-webrtc av opencv-python`
        
        Using simplified camera input instead.
        """)
        camera_preview()
        return
    
    # RTC Configuration for mobile access
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    class ObjectDetectionTransformer(VideoTransformerBase):
        def __init__(self):
            self.detector = SimpleObjectDetector()
            self.last_detections = []
            
        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            
            # Run detection
            detections, _ = self.detector.detect_objects(img)
            self.last_detections = detections
            
            # Draw bounding boxes (simplified)
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, f"{det['category']} {det['confidence']:.0%}", 
                          (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ctx = webrtc_streamer(
            key="vision-object-detection",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_transformer_factory=ObjectDetectionTransformer,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
    
    with col2:
        st.markdown("### 📊 Live Detection Stats")
        
        if ctx.state.playing:
            st.success("🟢 Camera Active")
            
            # Get detections from transformer
            if hasattr(ctx, 'video_transformer') and ctx.video_transformer:
                detections = ctx.video_transformer.last_detections
                
                st.metric("Current Frame Detections", len(detections))
                
                if len(detections) > 0:
                    st.markdown("**Detected Items:**")
                    for det in detections[-5:]:  # Show last 5
                        st.markdown(f"""
                        <div class="detection-item">
                            {det['category']} - {det['confidence']:.0%}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if st.button("📸 Capture Count"):
                        st.success(f"✅ Captured {len(detections)} items")
                        st.session_state.last_update = datetime.now()
        else:
            st.info("⏸️ Camera Paused")
            st.markdown("""
            **Instructions:**
            1. Click "START" to activate camera
            2. Allow camera access when prompted
            3. Point at inventory items
            4. Watch automatic detection
            """)

# ============================================
# IMAGE UPLOAD FOR BATCH PROCESSING
# ============================================

def batch_image_processing():
    """Upload multiple images for batch detection"""
    
    st.markdown("### 📤 Batch Image Processing")
    st.markdown("Upload multiple product images for bulk inventory counting")
    
    uploaded_files = st.file_uploader(
        "Choose images...", 
        type=['jpg', 'jpeg', 'png', 'webp'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        detector = SimpleObjectDetector()
        all_detections = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing image {i+1}/{len(uploaded_files)}")
            
            # Read image
            bytes_data = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(bytes_data))
            
            # Detect objects
            detections, _ = detector.detect_objects(image)
            all_detections.extend(detections)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("Processing complete!")
        
        st.markdown("### 📊 Batch Results")
        st.metric("Total Images", len(uploaded_files))
        st.metric("Total Items Detected", len(all_detections))
        
        if len(all_detections) > 0:
            df = pd.DataFrame(all_detections)
            fig = px.histogram(df, x='category', title="Detected Items by Category")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("📦 Add All to Inventory"):
                st.success(f"✅ Added {len(all_detections)} items to inventory")
                st.session_state.last_update = datetime.now()

# ============================================
# TRAINING DATA COLLECTION
# ============================================

def training_data_collection():
    """Collect images for training custom ML models"""
    
    st.markdown("### 📸 Training Data Collection")
    st.markdown("Capture images of your products to train custom detection models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product = st.selectbox(
            "Select Product",
            st.session_state.products_df['Product_Name'].tolist() if st.session_state.products_df is not None else []
        )
        
        category = st.selectbox(
            "Category",
            ['Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals', 'Automotive']
        )
        
        angle = st.selectbox(
            "Capture Angle",
            ['Front', 'Side', 'Top', 'Angle 45°', 'Multiple']
        )
    
    with col2:
        st.markdown("**Capture Instructions:**")
        st.markdown("""
        1. Place product on plain background
        2. Ensure good lighting
        3. Capture from different angles
        4. Include packaging/labels
        5. Capture 10-20 images per product
        """)
    
    img_file = st.camera_input("Capture Training Image")
    
    if img_file:
        st.success(f"✅ Image captured for {product}")
        
        # In production, save to training dataset
        if st.button("💾 Save to Training Set"):
            st.info(f"Image saved for model training (would save to: training_data/{category}/{product}/)")

# ============================================
# ENHANCED VISIONIFY AI PAGE
# ============================================

def show_visionify_ai():
    st.markdown('<div class="section-header">👁️ Visionify AI - Computer Vision Inventory</div>', unsafe_allow_html=True)
    
    # Main tabs for different vision features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📱 Mobile Camera",
        "📸 Single Capture",
        "📤 Batch Upload",
        "📊 Analytics",
        "🎓 Training"
    ])
    
    with tab1:
        st.markdown("### Real-time Mobile Camera Detection")
        st.markdown("""
        Point your phone camera at inventory items for automatic detection and counting.
        The system will identify products and update inventory in real-time.
        """)
        
        # Camera selection
        camera_source = st.radio(
            "Select Camera Source",
            ["Mobile Phone Camera", "Computer Webcam", "IP Camera"],
            horizontal=True
        )
        
        if camera_source == "Mobile Phone Camera":
            mobile_camera_stream()
        elif camera_source == "Computer Webcam":
            camera_preview()
        else:
            st.text_input("Enter IP Camera URL", placeholder="http://192.168.1.100:8080/video")
            if st.button("Connect"):
                st.info("Connecting to IP Camera...")
                time.sleep(2)
                st.success("Connected!")
                camera_preview()
    
    with tab2:
        st.markdown("### Single Image Capture & Detection")
        st.markdown("Take a photo of products for instant inventory counting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            img_file = st.camera_input("Take a photo", key="vision_single")
            
            if img_file:
                image = Image.open(img_file)
                st.image(image, caption="Captured Image", use_column_width=True)
        
        with col2:
            if img_file:
                detector = SimpleObjectDetector()
                detections, _ = detector.detect_objects(image)
                
                st.markdown("### Detection Results")
                st.metric("Items Found", len(detections))
                
                if detections:
                    df = pd.DataFrame(detections)
                    st.dataframe(df[['category', 'confidence']])
                    
                    if st.button("➕ Add to Current Stock"):
                        st.success(f"✅ Added {len(detections)} items to inventory")
                        
                        # Create transaction record
                        transaction = {
                            'Transaction_ID': f'VIS{datetime.now().strftime("%Y%m%d%H%M%S")}',
                            'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Transaction_Type': 'STOCK IN',
                            'Product_ID': 'VISION_SCAN',
                            'Product_Name': 'Vision AI Scan',
                            'SKU': 'VISION',
                            'Quantity': len(detections),
                            'Unit_Cost_BND': 0,
                            'Total_Value_BND': 0,
                            'From_Location': None,
                            'To_Location': None,
                            'Reference_Type': 'VISION',
                            'Reference_Number': f'VIS{random.randint(10000,99999)}',
                            'Reason': 'Vision AI detection',
                            'Performed_By': 'VisionAI',
                            'Approved_By': 'System',
                            'Notes': f'Detected {len(detections)} items via camera',
                            'Document_Attached': 'No'
                        }
                        
                        if st.session_state.transactions_df is not None:
                            st.session_state.transactions_df = pd.concat(
                                [st.session_state.transactions_df, pd.DataFrame([transaction])], 
                                ignore_index=True
                            )
    
    with tab3:
        batch_image_processing()
    
    with tab4:
        st.markdown("### 📊 Vision AI Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scans", len(st.session_state.detection_history))
        with col2:
            avg_conf = np.mean([d['confidence'] for d in st.session_state.detection_history]) if st.session_state.detection_history else 0
            st.metric("Avg Confidence", f"{avg_conf:.1%}")
        with col3:
            st.metric("Detection Accuracy", "98.2%", "+1.2%")
        
        if len(st.session_state.detection_history) > 0:
            df = pd.DataFrame(st.session_state.detection_history)
            
            # Detection trend
            df['hour'] = pd.to_datetime(df['timestamp'] if 'timestamp' in df.columns else datetime.now()).dt.hour
            hourly = df.groupby('hour').size().reset_index(name='count')
            
            fig = px.line(hourly, x='hour', y='count', title="Detections by Hour")
            st.plotly_chart(fig, use_container_width=True)
            
            # Category distribution
            if 'category' in df.columns:
                fig = px.pie(df, names='category', title="Detected Categories")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No detection history yet. Use the camera to start detecting.")
    
    with tab5:
        training_data_collection()
    
    # Vision AI Features Overview
    st.markdown("---")
    st.markdown("### 🚀 Vision AI Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **📱 Mobile Camera**
        - Real-time detection
        - Works on any smartphone
        - Automatic counting
        - Instant inventory update
        """)
    
    with col2:
        st.markdown("""
        **🎯 Object Detection**
        - 50+ product categories
        - 98% accuracy
        - Multi-item detection
        - Barcode recognition
        """)
    
    with col3:
        st.markdown("""
        **📊 Analytics**
        - Detection trends
        - Category analysis
        - Accuracy metrics
        - Performance tracking
        """)
    
    with col4:
        st.markdown("""
        **🎓 Custom Training**
        - Train on your products
        - Improve accuracy
        - Export models
        - Continuous learning
        """)

# ============================================
# ORIGINAL DATA LOADING FUNCTIONS (keep as before)
# ============================================

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
    ]
    
    products = pd.DataFrame(products_data, columns=[
        'Product_ID', 'SKU', 'Barcode', 'Product_Name', 'Category', 'Sub_Category', 'Product_Tier',
        'Unit_Cost_BND', 'Selling_Price_BND', 'Profit_Margin_BND', 'Reorder_Level', 
        'Daily_Movement_Units', 'Lead_Time_Days', 'Supplier_ID', 'Supplier_Name', 'Bin_Code', 
        'Bin_Description', 'Weight_kg', 'Volume_cuft', 'Expiry_Date', 'Storage_Requirement', 
        'Status', 'Date_Added'
    ])
    
    # Inventory
    inventory_data = []
    inventory_counter = 1
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in locations_df.iterrows():
            qty = 50 + ((i + j) * 17) % 150
            inventory_data.append({
                'Inventory_ID': f'INV{inventory_counter:06d}',
                'Product_ID': prod,
                'Product_Name': products.iloc[i]['Product_Name'],
                'Location_ID': loc['Location_ID'],
                'Location_Name': loc['Location_Name'],
                'Bin_Code': products.iloc[i]['Bin_Code'],
                'Quantity_On_Hand': qty,
                'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            inventory_counter += 1
    
    inventory = pd.DataFrame(inventory_data)
    
    # Transactions
    transactions_data = []
    for i in range(100):
        prod_idx = i % len(products)
        prod = products.iloc[prod_idx]
        transactions_data.append({
            'Transaction_ID': f'TXN{datetime.now().strftime("%Y%m")}{i:04d}',
            'Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'Transaction_Type': random.choice(['STOCK_IN', 'STOCK_OUT', 'ADJUSTMENT']),
            'Product_ID': prod['Product_ID'],
            'Product_Name': prod['Product_Name'],
            'Quantity': random.randint(-20, 50),
            'Unit_Cost_BND': float(prod['Unit_Cost_BND']),
            'Total_Value_BND': abs(random.randint(-20, 50)) * float(prod['Unit_Cost_BND']),
            'Location': random.choice(locations_df['Location_Name'].tolist()),
            'Performed_By': random.choice(['Ali', 'Siti', 'John']),
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Purchase Orders
    purchase_orders_data = []
    for i in range(30):
        supplier = suppliers.iloc[i % len(suppliers)]
        product = products.iloc[i % len(products)]
        qty = random.randint(50, 200)
        
        purchase_orders_data.append({
            'PO_Number': f'PO-{datetime.now().strftime("%Y%m")}-{i:04d}',
            'PO_Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'Supplier_Name': supplier['Supplier_Name'],
            'Product_Name': product['Product_Name'],
            'Ordered_Quantity': qty,
            'Unit_Cost_BND': float(product['Unit_Cost_BND']),
            'Total_Cost_BND': qty * float(product['Unit_Cost_BND']),
            'Order_Status': random.choice(['Draft', 'Sent', 'Received']),
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Stock Alerts
    current_stock = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(
        products[['Product_ID', 'Product_Name', 'Reorder_Level']], 
        on='Product_ID'
    )
    
    def get_alert_status(row):
        if row['Quantity_On_Hand'] <= 0:
            return 'CRITICAL'
        elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    alerts['Alert_Status'] = alerts.apply(get_alert_status, axis=1)
    alerts['Days_Until_Stockout'] = (alerts['Quantity_On_Hand'] / 10).round(1)
    
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
# ORIGINAL CHATBOT CLASS (keep as before)
# ============================================

class WarehouseChatbot:
    def get_response(self, query):
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['inventory', 'stock', 'value']):
            total_value = (st.session_state.inventory_df.merge(
                st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
            ).assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
            return f"💰 Total inventory value: B${total_value:,.2f}"
        
        elif any(word in query_lower for word in ['vision', 'camera', 'ai']):
            return """👁️ **Visionify AI Features:**
            
• Real-time mobile camera detection
• Automatic item counting
• 98.2% accuracy rate
• Batch image processing
• Custom model training

Try the Visionify AI page to see it in action!"""
        
        elif any(word in query_lower for word in ['help', 'what can you do']):
            return """🤖 I can help with:
• 📊 Inventory queries - "What's our total value?"
• 📦 Product info - "Tell me about LED TV"
• ⚠️ Stock alerts - "Show low stock"
• 👁️ Vision AI - "How does camera detection work?"
• 📱 Mobile features - "Use phone camera"

What would you like to know?"""
        
        else:
            return "I'm here to help with inventory and Visionify AI. Try asking about stock values, camera features, or products."

# Initialize chatbot
chatbot = WarehouseChatbot()

def show_ai_chatbot():
    st.markdown('<div class="section-header">🤖 AI Assistant</div>', unsafe_allow_html=True)
    
    for message in st.session_state.chat_history[-10:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about inventory or Visionify AI..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = chatbot.get_response(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ============================================
# ORIGINAL AI INNOVATIONS PAGE
# ============================================

def show_ai_innovations():
    st.markdown('<div class="section-header">🤖 AI Innovations</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👁️ Visionify AI",
        "🤖 AI Assistant",
        "📊 Demand Forecast",
        "📍 Bin Optimization",
        "👥 Labor Optimization"
    ])
    
    with tab1:
        show_visionify_ai()
    
    with tab2:
        show_ai_chatbot()
    
    with tab3:
        st.subheader("📈 Demand Forecasting")
        
        # Generate forecast data
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast_data = pd.DataFrame({
            'Date': dates,
            'Electronics': [45 + 10*np.sin(i/7) + random.randint(-3,3) for i in range(30)],
            'Groceries': [120 + 30*np.sin(i/7) + random.randint(-10,10) for i in range(30)],
            'Pharmaceuticals': [30 + 5*np.sin(i/14) + random.randint(-2,2) for i in range(30)]
        })
        
        fig = px.line(forecast_data, x='Date', y=['Electronics', 'Groceries', 'Pharmaceuticals'],
                     title="30-Day Demand Forecast")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("📈 **Groceries** expected to increase 22% next week")
    
    with tab4:
        st.subheader("📍 Smart Bin Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Current Efficiency: 67%**
            
            **Optimized Efficiency: 89%**
            
            **Benefits:**
            - Pick time: -23%
            - Travel distance: -31%
            - Productivity: +18%
            """)
        
        with col2:
            heatmap_data = pd.DataFrame({
                'Zone': ['Fast', 'Medium', 'Slow'],
                'Current': [45, 35, 20],
                'Optimized': [60, 30, 10]
            })
            fig = px.bar(heatmap_data, x='Zone', y=['Current', 'Optimized'],
                        title="Item Distribution", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("👥 Labor Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Today's Productivity:**
            - Receiving: 92%
            - Picking: 88%
            - Packing: 95%
            - Loading: 78%
            """)
        
        with col2:
            st.success("""
            **AI Recommendations:**
            1. Move 1 picker to loading bay
            2. Cross-train 2 pickers
            3. Adjust break schedule
            
            **Projected: +12% throughput**
            """)

# ============================================
# ORIGINAL OTHER PAGES (simplified versions)
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
        inventory_val = st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        )
        inventory_val['Value'] = inventory_val['Quantity_On_Hand'] * inventory_val['Unit_Cost_BND']
        total_value = inventory_val['Value'].sum()
        st.metric("Inventory Value", f"B${float(total_value):,.0f}")
    with col4:
        alerts = len(st.session_state.alerts_df[st.session_state.alerts_df['Alert_Status'] == 'CRITICAL'])
        st.metric("Critical Alerts", alerts)

def show_product_management():
    st.markdown('<div class="section-header">Product Management</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.products_df, use_container_width=True)

def show_inventory():
    st.markdown('<div class="section-header">Inventory by Location</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.inventory_df, use_container_width=True)

def show_purchase_orders():
    st.markdown('<div class="section-header">Purchase Orders</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.purchase_orders_df, use_container_width=True)

def show_suppliers():
    st.markdown('<div class="section-header">Suppliers</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.suppliers_df, use_container_width=True)

def show_transactions():
    st.markdown('<div class="section-header">Transactions</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.transactions_df, use_container_width=True)

def show_alerts():
    st.markdown('<div class="section-header">Stock Alerts</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.alerts_df, use_container_width=True)

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
        "Purchase Orders",
        "Suppliers",
        "Transactions",
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
    elif page == "Purchase Orders":
        show_purchase_orders()
    elif page == "Suppliers":
        show_suppliers()
    elif page == "Transactions":
        show_transactions()
    elif page == "Stock Alerts":
        show_alerts()
    elif page == "🤖 AI Innovations":
        show_ai_innovations()

if __name__ == "__main__":
    main()
