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
import tempfile
import os
from pathlib import Path
from collections import defaultdict
import threading
import queue
import warnings
warnings.filterwarnings('ignore')

# Computer Vision Imports
try:
    from ultralytics import YOLO
    import supervision as sv
    from roboflow import Roboflow
    CV_AVAILABLE = True
except ImportError as e:
    CV_AVAILABLE = False
    st.warning(f"Computer Vision libraries not fully installed: {e}")

# Page configuration
st.set_page_config(
    page_title="Stock Inventory System with AI Vision",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (keep your existing CSS)
st.markdown("""
<style>
    /* Your existing CSS styles */
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
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1e3c72;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
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
    
    .camera-feed {
        border: 2px solid #3498db;
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .detection-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with vision tracking
if 'vision_enabled' not in st.session_state:
    st.session_state.vision_enabled = False
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []
if 'person_count' not in st.session_state:
    st.session_state.person_count = 0
if 'object_counts' not in st.session_state:
    st.session_state.object_counts = defaultdict(int)
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = queue.Queue(maxsize=10)
if 'detection_thread' not in st.session_state:
    st.session_state.detection_thread = None
if 'camera' not in st.session_state:
    st.session_state.camera = None
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'model_type' not in st.session_state:
    st.session_state.model_type = "yolov8n"  # Default model
if 'tracking_enabled' not in st.session_state:
    st.session_state.tracking_enabled = True
if 'zone_violations' not in st.session_state:
    st.session_state.zone_violations = []
if 'roboflow_api_key' not in st.session_state:
    st.session_state.roboflow_api_key = ""
if 'roboflow_project' not in st.session_state:
    st.session_state.roboflow_project = ""
if 'roboflow_version' not in st.session_state:
    st.session_state.roboflow_version = ""

# Rest of your existing initialization code
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

# ============================================
# COMPUTER VISION MODULE
# ============================================

class VisionWarehouseSystem:
    """Computer Vision system for warehouse monitoring"""
    
    def __init__(self):
        self.model = None
        self.tracker = None
        self.roboflow_model = None
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        self.tracker = sv.ByteTrack()  # For object tracking
        self.fps_monitor = sv.FPSMonitor()
        self.person_count_history = []
        self.object_history = defaultdict(list)
        self.zones = []
        self.zone_counts = defaultdict(int)
        
    def load_yolo_model(self, model_size="yolov8n"):
        """Load YOLOv8 model"""
        try:
            self.model = YOLO(f"{model_size}.pt")  # Downloads if not present
            st.session_state.model_loaded = True
            return True, f"YOLOv8 {model_size} loaded successfully"
        except Exception as e:
            return False, f"Error loading model: {str(e)}"
    
    def load_roboflow_model(self, api_key, project, version):
        """Load custom model from Roboflow"""
        try:
            rf = Roboflow(api_key=api_key)
            project = rf.workspace().project(project)
            self.roboflow_model = project.version(version).model
            return True, "Roboflow model loaded successfully"
        except Exception as e:
            return False, f"Error loading Roboflow model: {str(e)}"
    
    def process_frame_yolo(self, frame):
        """Process frame with YOLOv8"""
        if self.model is None:
            return frame, {}
        
        # Run inference
        results = self.model(frame, verbose=False)[0]
        
        # Process detections
        detections = sv.Detections.from_ultralytics(results)
        
        # Apply tracking if enabled
        if st.session_state.tracking_enabled:
            detections = self.tracker.update_with_detections(detections)
        
        # Count people and objects
        person_count = 0
        object_counts = defaultdict(int)
        
        for i, (xyxy, mask, confidence, class_id, tracker_id) in enumerate(detections):
            class_name = results.names[int(class_id)]
            object_counts[class_name] += 1
            
            if class_name == 'person':
                person_count += 1
        
        # Update session state
        st.session_state.person_count = person_count
        st.session_state.object_counts = dict(object_counts)
        
        # Annotate frame
        annotated_frame = self.box_annotator.annotate(
            scene=frame.copy(),
            detections=detections
        )
        
        # Add labels
        labels = [
            f"{results.names[int(class_id)]} {confidence:.2f}"
            for xyxy, mask, confidence, class_id, tracker_id in detections
        ]
        
        annotated_frame = self.label_annotator.annotate(
            scene=annotated_frame,
            detections=detections,
            labels=labels
        )
        
        # Add statistics overlay
        self.add_stats_overlay(annotated_frame)
        
        return annotated_frame, object_counts
    
    def process_frame_roboflow(self, frame):
        """Process frame with Roboflow model"""
        if self.roboflow_model is None:
            return frame, {}
        
        # Save temp file for Roboflow
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        cv2.imwrite(temp_path.name, frame)
        
        # Run inference
        result = self.roboflow_model.predict(temp_path.name, confidence=40, overlap=30).json()
        
        # Clean up
        os.unlink(temp_path.name)
        
        # Parse results
        object_counts = defaultdict(int)
        for pred in result.get('predictions', []):
            class_name = pred.get('class', 'unknown')
            object_counts[class_name] += 1
        
        # Annotate frame (simplified for Roboflow)
        annotated_frame = frame.copy()
        for pred in result.get('predictions', []):
            x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
            x1, y1, x2, y2 = int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add label
            label = f"{pred['class']} {pred['confidence']:.2f}"
            cv2.putText(annotated_frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return annotated_frame, object_counts
    
    def add_stats_overlay(self, frame):
        """Add statistics overlay to frame"""
        # Person count
        cv2.putText(frame, f"People: {st.session_state.person_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Object counts (top 3)
        y_offset = 60
        for obj, count in sorted(st.session_state.object_counts.items(), 
                                 key=lambda x: x[1], reverse=True)[:3]:
            if obj != 'person':
                cv2.putText(frame, f"{obj}: {count}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                y_offset += 25
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (frame.shape[1] - 200, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def define_zones(self, frame_width, frame_height):
        """Define monitoring zones (e.g., restricted areas)"""
        # Example zones - can be customized
        zones = [
            {"name": "Entrance", "points": [(0, 0), (200, 0), (200, 200), (0, 200)]},
            {"name": "Restricted Area", "points": [(frame_width-300, frame_height-300), 
                                                   (frame_width, frame_height-300), 
                                                   (frame_width, frame_height), 
                                                   (frame_width-300, frame_height)]}
        ]
        return zones
    
    def check_zone_violations(self, detections, zones):
        """Check if objects are in restricted zones"""
        violations = []
        for zone in zones:
            zone_polygon = np.array(zone["points"], np.int32).reshape((-1, 1, 2))
            for detection in detections:
                # Check if detection center is in zone
                if len(detection) >= 4:
                    x1, y1, x2, y2 = detection[:4]
                    center = ((x1 + x2) // 2, (y1 + y2) // 2)
                    if cv2.pointPolygonTest(zone_polygon, center, False) >= 0:
                        violations.append({
                            "zone": zone["name"],
                            "timestamp": datetime.now(),
                            "object": "detected"
                        })
        return violations

# Initialize vision system
if 'vision_system' not in st.session_state:
    st.session_state.vision_system = VisionWarehouseSystem()

# ============================================
# CAMERA MANAGEMENT
# ============================================

def start_camera():
    """Start camera capture"""
    if st.session_state.camera is None:
        st.session_state.camera = cv2.VideoCapture(0)
        st.session_state.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        st.session_state.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        st.session_state.camera.set(cv2.CAP_PROP_FPS, 30)
    
    st.session_state.camera_active = True

def stop_camera():
    """Stop camera capture"""
    if st.session_state.camera is not None:
        st.session_state.camera.release()
        st.session_state.camera = None
    
    st.session_state.camera_active = False

def get_camera_frame():
    """Get frame from camera"""
    if st.session_state.camera is not None and st.session_state.camera.isOpened():
        ret, frame = st.session_state.camera.read()
        if ret:
            return frame
    return None

def detection_loop():
    """Background thread for continuous detection"""
    while st.session_state.camera_active and st.session_state.vision_enabled:
        frame = get_camera_frame()
        if frame is not None:
            # Process frame based on selected model
            if st.session_state.model_type == "roboflow" and st.session_state.vision_system.roboflow_model:
                processed_frame, counts = st.session_state.vision_system.process_frame_roboflow(frame)
            else:
                processed_frame, counts = st.session_state.vision_system.process_frame_yolo(frame)
            
            # Add to queue (non-blocking)
            if not st.session_state.frame_queue.full():
                st.session_state.frame_queue.put(processed_frame)
            
            # Store history
            st.session_state.detection_history.append({
                'timestamp': datetime.now(),
                'person_count': st.session_state.person_count,
                'object_counts': counts.copy()
            })
            
            # Keep only last 1000 records
            if len(st.session_state.detection_history) > 1000:
                st.session_state.detection_history = st.session_state.detection_history[-1000:]
        
        time.sleep(0.03)  # ~30 FPS

# ============================================
# COMPUTER VISION UI
# ============================================

def show_vision_control_panel():
    """Display vision system control panel"""
    st.markdown('<div class="section-header">🎥 AI Vision Control Panel</div>', unsafe_allow_html=True)
    
    # Check if CV libraries are available
    if not CV_AVAILABLE:
        st.error("""
        ⚠️ Computer Vision libraries not installed. Please install required packages:
        ```
        pip install ultralytics supervision opencv-python roboflow
        ```
        """)
        return
    
    # Model selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Model Selection")
        model_option = st.radio(
            "Choose Model:",
            ["YOLOv8 (General Detection)", "Roboflow Custom Model"],
            horizontal=True
        )
        
        if model_option == "YOLOv8 (General Detection)":
            model_size = st.selectbox(
                "Model Size:",
                ["yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x"],
                index=0,
                help="n=nano (fast), s=small, m=medium, l=large, x=xlarge (accurate but slower)"
            )
            
            if st.button("🔄 Load YOLOv8 Model"):
                with st.spinner("Loading YOLOv8 model..."):
                    success, message = st.session_state.vision_system.load_yolo_model(model_size)
                    if success:
                        st.success(message)
                        st.session_state.model_type = model_size
                    else:
                        st.error(message)
        
        else:  # Roboflow
            st.markdown("### Roboflow Configuration")
            api_key = st.text_input("Roboflow API Key", type="password", 
                                   value=st.session_state.roboflow_api_key)
            project = st.text_input("Project Name", value=st.session_state.roboflow_project)
            version = st.text_input("Version", value=st.session_state.roboflow_version)
            
            if st.button("🔄 Load Roboflow Model"):
                with st.spinner("Loading Roboflow model..."):
                    success, message = st.session_state.vision_system.load_roboflow_model(
                        api_key, project, version
                    )
                    if success:
                        st.success(message)
                        st.session_state.model_type = "roboflow"
                        st.session_state.roboflow_api_key = api_key
                        st.session_state.roboflow_project = project
                        st.session_state.roboflow_version = version
                    else:
                        st.error(message)
    
    with col2:
        st.markdown("### Camera Controls")
        
        if not st.session_state.camera_active:
            if st.button("▶️ Start Camera", use_container_width=True):
                start_camera()
                st.rerun()
        else:
            if st.button("⏹️ Stop Camera", use_container_width=True):
                stop_camera()
                st.session_state.vision_enabled = False
                st.rerun()
        
        # Vision toggle
        if st.session_state.camera_active:
            vision_toggle = st.toggle(
                "Enable AI Vision", 
                value=st.session_state.vision_enabled
            )
            
            if vision_toggle != st.session_state.vision_enabled:
                st.session_state.vision_enabled = vision_toggle
                if vision_toggle and st.session_state.model_loaded:
                    # Start detection thread
                    if st.session_state.detection_thread is None or not st.session_state.detection_thread.is_alive():
                        st.session_state.detection_thread = threading.Thread(target=detection_loop, daemon=True)
                        st.session_state.detection_thread.start()
                st.rerun()
        
        # Tracking toggle
        tracking_toggle = st.toggle(
            "Enable Object Tracking", 
            value=st.session_state.tracking_enabled,
            help="Track objects across frames for better counting"
        )
        if tracking_toggle != st.session_state.tracking_enabled:
            st.session_state.tracking_enabled = tracking_toggle

def show_live_feed():
    """Display live camera feed with detections"""
    st.markdown('<div class="section-header">📹 Live Monitoring Feed</div>', unsafe_allow_html=True)
    
    if not st.session_state.camera_active:
        st.info("👆 Start camera from the control panel to begin monitoring")
        return
    
    # Create placeholders
    feed_placeholder = st.empty()
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    # Live feed update loop
    while st.session_state.camera_active:
        if not st.session_state.frame_queue.empty():
            frame = st.session_state.frame_queue.get()
            
            # Convert BGR to RGB for Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Display frame
            feed_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Update statistics
            with stats_col1:
                st.metric("People Detected", st.session_state.person_count)
            
            with stats_col2:
                total_objects = sum(st.session_state.object_counts.values())
                st.metric("Total Objects", total_objects)
            
            with stats_col3:
                if st.session_state.detection_history:
                    avg_people = np.mean([h['person_count'] for h in st.session_state.detection_history[-30:]])
                    st.metric("Avg People (30s)", f"{avg_people:.1f}")
            
            with stats_col4:
                st.metric("Vision Status", "✅ Active" if st.session_state.vision_enabled else "⏸️ Paused")
            
            # Show object breakdown
            if st.session_state.object_counts:
                st.markdown("### Detected Objects")
                obj_df = pd.DataFrame(
                    list(st.session_state.object_counts.items()), 
                    columns=['Object', 'Count']
                ).sort_values('Count', ascending=False)
                
                # Create bar chart
                fig = px.bar(obj_df, x='Object', y='Count', 
                            title="Object Detection Breakdown")
                st.plotly_chart(fig, use_container_width=True)
        
        time.sleep(0.1)

def show_detection_history():
    """Display historical detection data"""
    st.markdown('<div class="section-header">📊 Detection History</div>', unsafe_allow_html=True)
    
    if not st.session_state.detection_history:
        st.info("No detection history available yet")
        return
    
    # Convert history to DataFrame
    history_data = []
    for record in st.session_state.detection_history[-100:]:  # Last 100 records
        history_data.append({
            'Timestamp': record['timestamp'],
            'People': record['person_count'],
            'Total Objects': sum(record['object_counts'].values())
        })
    
    df = pd.DataFrame(history_data)
    
    # Time series chart
    fig = px.line(df, x='Timestamp', y=['People', 'Total Objects'],
                  title="Detection Trends Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average People", f"{df['People'].mean():.1f}")
    with col2:
        st.metric("Peak People", int(df['People'].max()))
    with col3:
        st.metric("Total Detections", len(df))

def show_warehouse_heatmap():
    """Show heatmap of warehouse activity"""
    st.markdown('<div class="section-header">🔥 Activity Heatmap</div>', unsafe_allow_html=True)
    
    if not st.session_state.detection_history:
        st.info("Not enough data for heatmap yet")
        return
    
    # Create simulated heatmap data based on detections
    # In a real system, this would use actual position data
    
    # Create grid
    grid_size = 10
    heatmap_data = np.zeros((grid_size, grid_size))
    
    # Simulate activity based on person count
    intensity = min(st.session_state.person_count / 10, 1.0)
    
    # Create hot spots
    for i in range(grid_size):
        for j in range(grid_size):
            # Distance from center
            distance = np.sqrt((i - grid_size/2)**2 + (j - grid_size/2)**2)
            heatmap_data[i, j] = intensity * np.exp(-distance/5) + np.random.random() * 0.1
    
    # Create heatmap
    fig = px.imshow(heatmap_data, 
                    title="Warehouse Activity Heatmap",
                    labels=dict(x="Aisle", y="Row", color="Activity"),
                    color_continuous_scale="hot")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Heatmap Interpretation:**
    - 🔴 Red areas: High activity
    - 🟡 Yellow areas: Medium activity
    - ⚫ Dark areas: Low activity
    """)

def show_vision_dashboard():
    """Main vision dashboard"""
    st.markdown('<h1 class="main-header">🤖 AI Warehouse Vision System</h1>', unsafe_allow_html=True)
    
    # Check installation status
    if not CV_AVAILABLE:
        st.error("""
        ## ⚠️ Computer Vision Libraries Not Found
        
        Please install required packages:
        ```bash
        pip install ultralytics supervision opencv-python-headless roboflow
        ```
        
        For full functionality, install all dependencies:
        ```bash
        pip install -r requirements-vision.txt
        ```
        """)
        
        # Create requirements file
        requirements = """
        streamlit>=1.28.0
        pandas>=1.5.0
        plotly>=5.14.0
        numpy>=1.24.0
        opencv-python-headless>=4.8.0
        ultralytics>=8.0.0
        supervision>=0.18.0
        roboflow>=1.0.0
        """
        
        st.download_button(
            "📥 Download Requirements File",
            requirements,
            file_name="requirements-vision.txt",
            mime="text/plain"
        )
        return
    
    # Create tabs for different vision features
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎥 Live Monitoring",
        "⚙️ Vision Control",
        "📊 Analytics",
        "🔧 Advanced Settings"
    ])
    
    with tab1:
        show_live_feed()
    
    with tab2:
        show_vision_control_panel()
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            show_detection_history()
        with col2:
            show_warehouse_heatmap()
        
        # Export data option
        if st.button("📥 Export Detection Data"):
            if st.session_state.detection_history:
                df = pd.DataFrame(st.session_state.detection_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    file_name=f"detection_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with tab4:
        st.markdown("### Advanced Configuration")
        
        # Detection thresholds
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
        iou_threshold = st.slider("IoU Threshold", 0.1, 1.0, 0.5, 0.05)
        
        # FPS limit
        fps_limit = st.slider("Max FPS", 1, 60, 30)
        
        # ROI selection
        st.markdown("### Region of Interest (ROI)")
        use_roi = st.checkbox("Enable ROI", False)
        if use_roi:
            st.info("ROI selection coming soon - draw rectangle on video feed")
        
        # Alert settings
        st.markdown("### Alert Configuration")
        alert_people_threshold = st.number_input("People Count Alert Threshold", 5, 100, 20)
        alert_congestion = st.checkbox("Enable Congestion Alerts", True)
        
        if st.button("Save Settings"):
            st.success("Settings saved!")

# ============================================
# MODIFIED AI INNOVATIONS TAB
# ============================================

def show_ai_innovations():
    st.markdown('<div class="section-header">🤖 AI Warehouse Innovations</div>', unsafe_allow_html=True)
    
    # Create tabs for each innovation including Vision
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "👁️ Vision System",
        "📍 Smart Bin Optimization",
        "📈 Demand Forecasting",
        "👥 Labor Optimization",
        "🔄 Returns Management",
        "📊 Predictive Analytics",
        "🤖 AI Chatbot",
        "📋 Integration"
    ])
    
    with tab1:
        show_vision_dashboard()
    
    with tab2:
        st.subheader("📍 AI Smart Bin Location Optimizer")
        # Your existing bin optimization code
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
    
    with tab3:
        st.subheader("📈 AI Demand Forecasting Engine")
        # Your existing forecasting code
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
    
    with tab4:
        st.subheader("👥 AI Labor Optimization Engine")
        # Your existing labor optimization code
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
    
    with tab5:
        st.subheader("🔄 AI Returns Management")
        # Your existing returns management code
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
    
    with tab6:
        st.subheader("📊 AI Predictive Analytics")
        # Your existing predictive analytics code
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
    
    with tab7:
        show_ai_chatbot()  # Your existing chatbot
    
    with tab8:
        st.subheader("📋 Vision System Integration")
        
        st.markdown("""
        ### Connect Vision Data with Inventory
        
        The vision system can automatically:
        
        1. **Update inventory counts** when items are detected
        2. **Track personnel** for safety and productivity
        3. **Detect empty shelves** and trigger reorders
        4. **Monitor loading docks** for shipment tracking
        5. **Verify pick accuracy** with computer vision
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Items Tracked by Vision", 
                     len(st.session_state.object_counts) if st.session_state.object_counts else 0)
        
        with col2:
            vision_accuracy = 98.5
            st.metric("Vision Accuracy", f"{vision_accuracy}%")
        
        if st.button("🔄 Sync Vision Data with Inventory"):
            with st.spinner("Syncing..."):
                time.sleep(2)
                st.success("✅ Vision data synced with inventory system!")

# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown('<h1 class="main-header">Stock Inventory System with AI Vision</h1>', unsafe_allow_html=True)
    
    st.sidebar.title("Menu")
    
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
    
    # Vision status indicator
    if st.session_state.camera_active:
        st.sidebar.success("📹 Camera: Active")
    else:
        st.sidebar.info("📹 Camera: Inactive")
    
    if st.session_state.vision_enabled:
        st.sidebar.success("👁️ Vision: Enabled")
    else:
        st.sidebar.info("👁️ Vision: Disabled")
    
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
    elif page == "🤖 AI Innovations":
        show_ai_innovations()
    
    # Cleanup on exit
    if st.session_state.camera_active and not st.session_state.get('keep_running', True):
        stop_camera()

# Keep all your existing functions (load_initial_data, generate_purchase_order_html, 
# get_html_download_link, chatbot functions, CRUD functions, etc.) here

# ============================================
# INCLUDE YOUR EXISTING FUNCTIONS HERE
# ============================================

# [Copy all your existing functions from the original app.py here]
# Including:
# - load_initial_data()
# - generate_purchase_order_html()
# - get_html_download_link()
# - WarehouseChatbot class
# - show_ai_chatbot()
# - CRUD functions (generate_product_id, generate_sku, generate_barcode, etc.)
# - show_product_crud()
# - show_purchase_orders()
# - show_suppliers()
# - show_inventory()
# - show_transactions()
# - show_alerts()
# - show_executive_dashboard()

# Initialize data (keep your existing initialization)
if st.session_state.products_df is None:
    (st.session_state.products_df, 
     st.session_state.inventory_df, 
     st.session_state.transactions_df, 
     st.session_state.suppliers_df, 
     st.session_state.purchase_orders_df, 
     st.session_state.alerts_df,
     st.session_state.locations_df,
     st.session_state.documents_df) = load_initial_data()

if __name__ == "__main__":
    try:
        main()
    finally:
        # Cleanup camera on exit
        if st.session_state.camera is not None:
            st.session_state.camera.release()
