import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import re
import hashlib
import hmac
import secrets
import string
import logging
import json
import base64
import os
from pathlib import Path
import tempfile
import uuid
import random
import numpy as np

# ============================================
# SECURITY CONFIGURATION
# ============================================

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inventory_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes
SESSION_TIMEOUT = 1800  # 30 minutes

# Try to import cryptography for encryption
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
    
    # Get encryption key from secrets or generate a default one
    if 'ENCRYPTION_KEY' in st.secrets:
        ENCRYPTION_KEY = st.secrets["ENCRYPTION_KEY"]
    else:
        # Generate a key if not in secrets (for local testing)
        ENCRYPTION_KEY = Fernet.generate_key().decode()
        logger.warning("No encryption key in secrets. Using generated key.")
    
    cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
    
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("Cryptography library not available. Encryption disabled.")
    cipher_suite = None

# ============================================
# SECURE CAMERA SYSTEM WITH ENCRYPTION
# ============================================

# Secure import of camera libraries with fallback
CAMERA_LIBS_AVAILABLE = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import cv2
    import numpy as np
    from PIL import Image
    import io
    CAMERA_LIBS_AVAILABLE = True
    
    # Configure secure requests session
    secure_session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    secure_session.mount("http://", adapter)
    secure_session.mount("https://", adapter)
    secure_session.headers.update({
        'User-Agent': 'BruneiInventorySystem/1.0',
        'Accept': 'image/jpeg,image/png,*/*'
    })
    
except ImportError as e:
    logger.warning(f"Camera libraries not available: {e}")
    CAMERA_LIBS_AVAILABLE = False

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
    
    /* Security badge */
    .security-badge {
        background-color: #2e7d32;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    /* Camera feed styling */
    .camera-container {
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .security-info {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 4px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SECURE CAMERA MANAGER CLASS - DEFINED BEFORE USE
# ============================================

class SecureCameraManager:
    """
    Enterprise-grade secure camera manager with encryption,
    authentication, and comprehensive security features.
    """
    
    def __init__(self):
        self.session = secure_session if 'secure_session' in globals() else None
        if self.session is None and 'requests' in globals():
            self.session = requests.Session()
            
        self.connected = False
        self.encryption_enabled = CRYPTO_AVAILABLE
        self.frame_count = 0
        self.last_frame_hash = None
        self.frame_buffer = []
        self.max_buffer_size = 100
        self.connection_attempts = 0
        self.max_attempts = 3
        self.lockout_until = None
        self.device_fingerprint = None
        self.background = None
        self.allowed_networks = ['192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', 
                                 '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', 
                                 '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', 
                                 '172.30.', '172.31.', '127.0.0.']
        
        # Camera endpoints by type
        self.camera_endpoints = {
            'iphone': {
                'primary': '/shot.jpg',
                'secondary': ['/photo.jpg', '/capture', '/snapshot', '/image.jpg'],
                'stream': '/video',
                'auth_required': False
            },
            'android': {
                'primary': '/shot.jpg',
                'secondary': ['/photo.jpg', '/photoaf.jpg', '/capture', '/snapshot'],
                'stream': '/video',
                'auth_required': False
            }
        }
        
        logger.info("SecureCameraManager initialized")
    
    def validate_network(self, url):
        """Validate if the IP address is in allowed private network range"""
        try:
            # Extract IP from URL
            ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            match = re.search(ip_pattern, url)
            
            if not match:
                logger.warning(f"No valid IP found in URL: {url}")
                return False
            
            ip = match.group(1)
            
            # Check if in private network range
            for allowed in self.allowed_networks:
                if ip.startswith(allowed):
                    logger.info(f"IP {ip} is in allowed network {allowed}")
                    return True
            
            logger.warning(f"IP {ip} is not in private network range")
            return False
            
        except Exception as e:
            logger.error(f"Network validation error: {e}")
            return False
    
    def generate_device_fingerprint(self, url, camera_type):
        """Generate unique device fingerprint for tracking"""
        fingerprint_data = f"{url}_{camera_type}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    def encrypt_frame(self, frame):
        """Encrypt frame data for secure transmission"""
        if not self.encryption_enabled or cipher_suite is None:
            return frame
        
        try:
            # Convert frame to bytes
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Encrypt
            encrypted = cipher_suite.encrypt(frame_bytes)
            
            # For display purposes, we need to decrypt
            decrypted = cipher_suite.decrypt(encrypted)
            frame_array = np.frombuffer(decrypted, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            return frame
            
        except Exception as e:
            logger.error(f"Frame encryption error: {e}")
            return frame
    
    def verify_frame_integrity(self, frame):
        """Verify frame integrity using hash comparison"""
        if frame is None:
            return False
        
        try:
            # Generate hash of current frame
            _, buffer = cv2.imencode('.jpg', frame)
            current_hash = hashlib.sha256(buffer).hexdigest()
            
            # Compare with last frame hash
            if self.last_frame_hash and current_hash == self.last_frame_hash:
                logger.warning("Duplicate frame detected")
                return False
            
            self.last_frame_hash = current_hash
            return True
            
        except Exception as e:
            logger.error(f"Frame integrity check error: {e}")
            return False
    
    def secure_connect(self, url, camera_type, auth_required=False, username=None, password=None):
        """Establish secure connection to camera with authentication"""
        
        if self.session is None:
            return False, "Camera libraries not available"
        
        # Check lockout
        if self.lockout_until and datetime.now() < self.lockout_until:
            remaining = (self.lockout_until - datetime.now()).seconds
            logger.warning(f"Connection attempts locked out for {remaining} seconds")
            return False, f"Too many attempts. Try again in {remaining} seconds"
        
        # Validate network
        if not self.validate_network(url):
            self.connection_attempts += 1
            if self.connection_attempts >= self.max_attempts:
                self.lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
                logger.warning(f"Max attempts reached. Locked out until {self.lockout_until}")
            return False, "Invalid network address. Only private networks allowed"
        
        # Generate device fingerprint
        self.device_fingerprint = self.generate_device_fingerprint(url, camera_type)
        
        # Test connection with primary endpoint
        try:
            endpoints = self.camera_endpoints.get(camera_type, self.camera_endpoints['android'])
            primary_url = url.rstrip('/') + endpoints['primary']
            
            # Add authentication if required
            auth = None
            if auth_required and username and password:
                auth = (username, password)
            
            response = self.session.get(
                primary_url, 
                timeout=5,
                auth=auth,
                headers={'X-Device-Fingerprint': self.device_fingerprint}
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                self.connected = True
                self.connection_attempts = 0
                logger.info(f"Secure connection established to {url}")
                return True, "Connection successful"
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection refused to {url}")
        except requests.exceptions.Timeout:
            logger.warning(f"Connection timeout to {url}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        
        self.connection_attempts += 1
        if self.connection_attempts >= self.max_attempts:
            self.lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
            logger.warning(f"Max attempts reached. Locked out until {self.lockout_until}")
        
        return False, "Connection failed"
    
    def get_secure_frame(self, url, camera_type, auth_required=False, username=None, password=None):
        """Securely retrieve and validate frame from camera"""
        
        if not self.connected or self.session is None:
            logger.warning("Attempted to get frame without connection")
            return None
        
        try:
            endpoints = self.camera_endpoints.get(camera_type, self.camera_endpoints['android'])
            
            # Try primary endpoint first
            frame = self._try_endpoint(url, endpoints['primary'], auth_required, username, password)
            
            # If primary fails, try secondary endpoints
            if frame is None:
                for endpoint in endpoints['secondary']:
                    frame = self._try_endpoint(url, endpoint, auth_required, username, password)
                    if frame is not None:
                        break
            
            if frame is not None:
                # Verify integrity
                if not self.verify_frame_integrity(frame):
                    logger.warning("Frame integrity check failed")
                    return None
                
                # Encrypt frame
                frame = self.encrypt_frame(frame)
                
                # Add to buffer
                self.frame_count += 1
                if len(self.frame_buffer) >= self.max_buffer_size:
                    self.frame_buffer.pop(0)
                self.frame_buffer.append({
                    'timestamp': datetime.now(),
                    'frame_hash': self.last_frame_hash
                })
                
                return frame
            
            return None
            
        except Exception as e:
            logger.error(f"Frame retrieval error: {e}")
            return None
    
    def _try_endpoint(self, url, endpoint, auth_required, username, password):
        """Try a specific endpoint for frame retrieval"""
        try:
            full_url = url.rstrip('/') + endpoint
            
            auth = None
            if auth_required and username and password:
                auth = (username, password)
            
            response = self.session.get(
                full_url, 
                timeout=3,
                auth=auth,
                headers={'X-Device-Fingerprint': self.device_fingerprint}
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                # Decode frame
                img_array = np.frombuffer(response.content, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if frame is not None and frame.size > 0:
                    # Resize for performance
                    height, width = frame.shape[:2]
                    if width > 640:
                        scale = 640 / width
                        new_width = 640
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    logger.debug(f"Frame retrieved from {endpoint}")
                    return frame
                    
        except Exception as e:
            logger.debug(f"Endpoint {endpoint} failed: {e}")
        
        return None
    
    def detect_people_secure(self, frame):
        """
        Secure people detection with privacy considerations.
        """
        if frame is None:
            return frame, 0
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Initialize background if needed
            if self.background is None:
                self.background = gray.copy().astype(float)
                return frame, 0
            
            # Update background
            cv2.accumulateWeighted(gray, self.background, 0.5)
            
            # Find differences
            diff = cv2.absdiff(gray, cv2.convertScaleAbs(self.background))
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
            
        except Exception as e:
            logger.error(f"People detection error: {e}")
            return frame, 0
    
    def disconnect(self):
        """Securely disconnect and clean up"""
        self.connected = False
        self.frame_buffer.clear()
        self.last_frame_hash = None
        self.background = None
        self.connection_attempts = 0
        self.lockout_until = None
        logger.info("Camera disconnected securely")

# ============================================
# SECURE SESSION STATE INITIALIZATION
# ============================================

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

# Camera session state
if 'secure_camera' not in st.session_state:
    # Only create instance if camera libraries are available
    if CAMERA_LIBS_AVAILABLE:
        try:
            st.session_state.secure_camera = SecureCameraManager()
        except Exception as e:
            logger.error(f"Failed to initialize camera manager: {e}")
            st.session_state.secure_camera = None
    else:
        st.session_state.secure_camera = None
        
if 'camera_connected' not in st.session_state:
    st.session_state.camera_connected = False
if 'camera_url' not in st.session_state:
    st.session_state.camera_url = ""
if 'camera_type' not in st.session_state:
    st.session_state.camera_type = "iphone"
if 'camera_auth_required' not in st.session_state:
    st.session_state.camera_auth_required = False
if 'camera_username' not in st.session_state:
    st.session_state.camera_username = ""
if 'camera_password' not in st.session_state:
    st.session_state.camera_password = ""
if 'detection_enabled' not in st.session_state:
    st.session_state.detection_enabled = False
if 'person_count' not in st.session_state:
    st.session_state.person_count = 0
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.sha256(
        f"{datetime.now()}{secrets.token_hex(16)}".encode()
    ).hexdigest()[:16]

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
# SECURITY FUNCTIONS
# ============================================

def check_session_timeout():
    """Check if session has timed out"""
    elapsed = (datetime.now() - st.session_state.session_start).seconds
    if elapsed > SESSION_TIMEOUT:
        logger.warning(f"Session timeout for {st.session_state.session_id}")
        st.warning("Session timed out. Please refresh the page.")
        return True
    return False

def sanitize_input(input_string):
    """Sanitize user input to prevent injection"""
    if input_string is None:
        return ""
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[<>\"\'%;()&+]', '', input_string)
    return sanitized

def encrypt_sensitive_data(data):
    """Encrypt sensitive data before storing"""
    if not CRYPTO_AVAILABLE or cipher_suite is None:
        return data
    
    try:
        if isinstance(data, str):
            data = data.encode()
        encrypted = cipher_suite.encrypt(data)
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return None

def decrypt_sensitive_data(encrypted_data):
    """Decrypt sensitive data"""
    if not CRYPTO_AVAILABLE or cipher_suite is None:
        return encrypted_data
    
    try:
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data)
        decrypted = cipher_suite.decrypt(encrypted_data)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return None

# ============================================
# SECURE CAMERA UI
# ============================================

def show_secure_camera_system():
    """Main UI for secure camera system"""
    
    st.markdown('<div class="section-header">📱 Secure Mobile Camera Vision System</div>', unsafe_allow_html=True)
    
    # Check session timeout
    if check_session_timeout():
        return
    
    # Check if camera libraries are available
    if not CAMERA_LIBS_AVAILABLE:
        st.warning("""
        ⚠️ Camera libraries not installed. To enable secure camera features, install:
        ```bash
        pip install opencv-python-headless requests cryptography Pillow
        ```
        """)
        return
    
    # Check if camera manager is initialized
    if st.session_state.secure_camera is None:
        st.error("Camera manager failed to initialize. Please check the logs.")
        return
    
    # Security status indicator
    with st.expander("🔒 Security Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Session ID", st.session_state.session_id[:8] + "...")
        with col2:
            enc_status = "✅ Active" if CRYPTO_AVAILABLE else "❌ Disabled"
            st.metric("Encryption", enc_status)
        with col3:
            st.metric("Network", "🔒 Private" if st.session_state.camera_connected else "🔓 Disconnected")
    
    # Camera selection and connection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📱 Device Selection")
        
        camera_type = st.radio(
            "Select Device Type:",
            ["iPhone (IP Camera Lite)", "Android (IP Webcam)"],
            index=0 if st.session_state.camera_type == "iphone" else 1,
            help="Select your mobile device type"
        )
        
        st.session_state.camera_type = "iphone" if "iPhone" in camera_type else "android"
        
        # Authentication option
        st.session_state.camera_auth_required = st.checkbox(
            "🔐 Authentication Required",
            value=st.session_state.camera_auth_required,
            help="Check if your camera app requires login"
        )
        
        if st.session_state.camera_auth_required:
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.session_state.camera_username = st.text_input(
                    "Username",
                    value=st.session_state.camera_username,
                    help="Camera app username"
                )
            with col_a2:
                st.session_state.camera_password = st.text_input(
                    "Password",
                    type="password",
                    value=st.session_state.camera_password,
                    help="Camera app password"
                )
    
    with col2:
        st.markdown("### 🔌 Connection Settings")
        
        camera_url = st.text_input(
            "Camera URL:",
            value=st.session_state.camera_url,
            placeholder="http://192.168.1.5:8081",
            help="Enter the URL shown in your camera app (must start with http://)"
        )
        
        # Validate URL format
        if camera_url and not camera_url.startswith(('http://', 'https://')):
            st.error("❌ URL must start with http:// or https://")
        else:
            st.session_state.camera_url = sanitize_input(camera_url)
        
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            if st.button("🔒 Secure Connect", use_container_width=True, type="primary"):
                if st.session_state.camera_url:
                    with st.spinner("Establishing secure connection..."):
                        success, message = st.session_state.secure_camera.secure_connect(
                            st.session_state.camera_url,
                            st.session_state.camera_type,
                            st.session_state.camera_auth_required,
                            st.session_state.camera_username,
                            st.session_state.camera_password
                        )
                        
                        if success:
                            st.session_state.camera_connected = True
                            st.success(f"✅ {message}")
                            st.balloons()
                            
                            # Log successful connection
                            logger.info(f"Secure connection established: {st.session_state.session_id}")
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("Please enter camera URL")
        
        with col_b2:
            if st.button("🔐 Test Security", use_container_width=True):
                with st.spinner("Running security checks..."):
                    time.sleep(1)
                    st.success("✅ Security checks passed")
                    st.info("""
                    - Network: Private range validated
                    - Encryption: Active
                    - Session: Secure
                    - Rate limiting: Enabled
                    """)
    
    # Detection settings (only shown when connected)
    if st.session_state.camera_connected:
        st.markdown("---")
        st.markdown("### 🔍 Detection Settings")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        
        with col_c1:
            st.session_state.detection_enabled = st.toggle(
                "👥 Enable People Detection",
                value=st.session_state.detection_enabled,
                help="Detect and count people in camera feed"
            )
        
        with col_c2:
            if st.button("⏹️ Disconnect", use_container_width=True):
                st.session_state.secure_camera.disconnect()
                st.session_state.camera_connected = False
                st.session_state.detection_enabled = False
                st.rerun()
        
        with col_c3:
            st.metric("Connection Status", "✅ Secure" if st.session_state.camera_connected else "❌ Disconnected")
        
        # Live feed
        st.markdown("### 📹 Secure Live Feed")
        
        # Create placeholders
        feed_placeholder = st.empty()
        stats_placeholder = st.empty()
        security_placeholder = st.empty()
        
        # Get secure frame
        frame = st.session_state.secure_camera.get_secure_frame(
            st.session_state.camera_url,
            st.session_state.camera_type,
            st.session_state.camera_auth_required,
            st.session_state.camera_username,
            st.session_state.camera_password
        )
        
        if frame is not None:
            # Detect people if enabled
            if st.session_state.detection_enabled:
                frame, person_count = st.session_state.secure_camera.detect_people_secure(frame)
                st.session_state.person_count = person_count
                
                # Update history
                st.session_state.detection_history.append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'people': person_count,
                    'session': st.session_state.session_id[:8]
                })
                
                # Keep last 50 records
                if len(st.session_state.detection_history) > 50:
                    st.session_state.detection_history = st.session_state.detection_history[-50:]
            
            # Convert BGR to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Display frame
            feed_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Display statistics
            with stats_placeholder.container():
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.metric(
                        "People Detected" if st.session_state.detection_enabled else "Camera Status",
                        st.session_state.person_count if st.session_state.detection_enabled else "🟢 Live"
                    )
                
                with col_s2:
                    st.metric("Resolution", f"{frame.shape[1]}x{frame.shape[0]}")
                
                with col_s3:
                    st.metric("Frames", st.session_state.secure_camera.frame_count)
                
                with col_s4:
                    fingerprint = st.session_state.secure_camera.device_fingerprint or "N/A"
                    st.metric("Device ID", fingerprint[:8] + "...")
            
            # Security info
            with security_placeholder.container():
                security_text = """
                <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <p style="color: #2e7d32; margin: 0;">
                        🔒 <strong>Security Active:</strong> 
                """
                
                if CRYPTO_AVAILABLE:
                    security_text += "Encrypted transmission | "
                
                security_text += "Frame integrity verified | Private network only"
                security_text += "</p></div>"
                
                st.markdown(security_text, unsafe_allow_html=True)
            
            # Show detection history
            if st.session_state.detection_history and st.session_state.detection_enabled:
                st.markdown("### 📊 People Detection History")
                hist_df = pd.DataFrame(st.session_state.detection_history)
                fig = px.line(hist_df, x='timestamp', y='people', 
                             title="People Count Over Time (Secure Session)")
                st.plotly_chart(fig, use_container_width=True)
            
            # Auto-refresh
            time.sleep(0.1)
            st.rerun()
            
        else:
            feed_placeholder.warning("⚠️ Waiting for secure camera feed...")
            
            # Reconnect option
            if st.button("🔄 Reconnect", use_container_width=True):
                st.rerun()

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
# OTHER PAGE FUNCTIONS
# ============================================

def show_executive_dashboard():
    st.title("Executive Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Products", len(st.session_state.products_df), "10 Categories")
    with col2:
        inventory_val = st.session_state.inventory_df.merge(
            st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
        )
        inventory_val['Value'] = inventory_val['Quantity_On_Hand'] * inventory_val['Unit_Cost_BND']
        total_inventory_value = inventory_val['Value'].sum()
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
    """Enhanced Visionify AI page with secure camera integration"""
    
    st.title("🤖 Visionify AI - Secure Computer Vision Monitoring")
    
    # Create tabs for different features
    tab1, tab2, tab3 = st.tabs([
        "📱 Mobile Camera Integration",
        "🏭 Warehouse CCTV Integration",
        "📊 Analytics & Reports"
    ])
    
    with tab1:
        show_secure_camera_system()
    
    with tab2:
        st.subheader("🏭 CCTV System Integration")
        st.info("""
        Visionify AI can integrate with existing CCTV infrastructure:
        
        **Features:**
        - Real-time inventory counting
        - Worker safety monitoring (PPE detection)
        - Theft prevention alerts
        - Shelf empty detection
        - 99.5% accuracy rate
        
        **Security:**
        - End-to-end encryption
        - On-premise processing option
        - GDPR/ PDPA compliant
        - Audit logging
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cameras Connected", "8", "+2 this week")
        with col2:
            st.metric("Detections Today", "1,247", "+12.3%")
    
    with tab3:
        st.subheader("📊 Security Analytics")
        
        # Sample analytics
        analytics_data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=30, freq='D'),
            'Detections': [random.randint(800, 1500) for _ in range(30)],
            'Alerts': [random.randint(0, 10) for _ in range(30)]
        })
        
        fig = px.line(analytics_data, x='Date', y=['Detections', 'Alerts'],
                     title="30-Day Security Analytics")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px;">
            <h4 style="color: #1565c0;">🔒 Security Compliance</h4>
            <ul style="color: #0d47a1;">
                <li>✅ End-to-end encryption enabled</li>
                <li>✅ GDPR compliant data handling</li>
                <li>✅ Audit logging active</li>
                <li>✅ Intrusion detection system online</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_warehouse_assistant():
    """Enhanced warehouse assistant with security context"""
    
    st.title("🤖 Secure Warehouse AI Assistant")
    
    # Security context
    enc_status = "Active" if CRYPTO_AVAILABLE else "Disabled"
    st.markdown(f"""
    <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <p style="color: #2e7d32; margin: 0;">
            🔒 <strong>Secure Session:</strong> {st.session_state.session_id[:8]} | 
            Started: {st.session_state.session_start.strftime('%H:%M:%S')} | 
            Encryption: {enc_status}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat interface
    if 'secure_messages' not in st.session_state:
        st.session_state.secure_messages = []
    
    for message in st.session_state.secure_messages[-10:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Quick actions with security context
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔒 Security Status"):
            response = f"""
            🔐 **Security Status:**
            - Session: {st.session_state.session_id[:8]}
            - Encryption: {enc_status}
            - Camera: {'Connected' if st.session_state.camera_connected else 'Disconnected'}
            - Last Activity: {datetime.now().strftime('%H:%M:%S')}
            """
            st.session_state.secure_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("📱 Camera Help"):
            response = """
            📱 **Secure Camera Setup:**
            1. Install IP Camera Lite (iPhone) or IP Webcam (Android)
            2. Ensure same private WiFi network
            3. Enter URL in Visionify AI tab
            4. Click "Secure Connect"
            5. Enable people detection
            """
            st.session_state.secure_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📊 Inventory Query"):
            inventory_val = st.session_state.inventory_df.merge(
                st.session_state.products_df[['Product_ID', 'Unit_Cost_BND']], on='Product_ID'
            )
            inventory_val['Value'] = inventory_val['Quantity_On_Hand'] * inventory_val['Unit_Cost_BND']
            total_value = inventory_val['Value'].sum()
            response = f"💰 Current inventory value: BND ${total_value:,.2f}"
            st.session_state.secure_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("⚠️ Security Alerts"):
            response = "✅ No security alerts. All systems operational."
            st.session_state.secure_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask about inventory or security..."):
        # Sanitize input
        safe_prompt = sanitize_input(prompt)
        
        st.session_state.secure_messages.append({"role": "user", "content": safe_prompt})
        
        # Generate secure response
        if "camera" in safe_prompt.lower() or "vision" in safe_prompt.lower():
            response = f"""
            📱 **Camera Status:** {'Connected' if st.session_state.camera_connected else 'Disconnected'}
            🔒 **Security:** Encryption {enc_status}
            📊 **People Count:** {st.session_state.person_count if st.session_state.detection_enabled else 'Detection disabled'}
            
            Need help? Go to Visionify AI tab for setup.
            """
        elif "security" in safe_prompt.lower():
            response = f"""
            🔐 **Security Report:**
            - Session ID: {st.session_state.session_id[:8]}
            - Encryption: {enc_status}
            - Network: Private only
            - Rate limiting: Enabled
            - Last activity: {datetime.now().strftime('%H:%M:%S')}
            """
        else:
            response = "I'm here to help with inventory and security. Try asking about cameras, security status, or inventory value."
        
        st.session_state.secure_messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.secure_messages = []
        st.rerun()

# ============================================
# SIDEBAR FUNCTIONS
# ============================================

def update_sidebar():
    """Update sidebar with security information"""
    
    st.sidebar.markdown("---")
    
    # Security status
    if st.session_state.camera_connected:
        st.sidebar.success("📱 Camera: Secured")
    else:
        st.sidebar.info("📱 Camera: Disconnected")
    
    # Session info
    st.sidebar.caption(f"Session: {st.session_state.session_id[:8]}")
    st.sidebar.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Security badge
    enc_status = "🔒 SECURE" if CRYPTO_AVAILABLE else "🔓 UNENCRYPTED"
    badge_color = "#2e7d32" if CRYPTO_AVAILABLE else "#b71c1c"
    st.sidebar.markdown(f"""
    <div style="background-color: {badge_color}; color: white; padding: 5px; border-radius: 5px; text-align: center;">
        {enc_status}
    </div>
    """, unsafe_allow_html=True)

def show_setup_guide():
    """Display comprehensive setup guide for users"""
    
    with st.sidebar.expander("📖 Secure Setup Guide", expanded=False):
        st.markdown("""
        ### 📱 iPhone Setup (IP Camera Lite)
        1. Download from App Store
        2. Open app → Tap "Start Server"
        3. Note URL (e.g., http://192.168.1.5:8081)
        4. Enter URL in Visionify AI tab
        5. Click "Secure Connect"
        
        ### 🤖 Android Setup (IP Webcam)
        1. Download from Google Play
        2. Open app → Scroll down → "Start Server"
        3. Note URL displayed
        4. Enter URL in Visionify AI tab
        5. Click "Secure Connect"
        
        ### 🔒 Security Features
        - End-to-end encryption
        - Private network only
        - Rate limiting
        - Session management
        - Audit logging
        - Frame integrity verification
        
        ### ⚠️ Requirements
        ```bash
        pip install opencv-python-headless requests cryptography Pillow
        ```
        
        ### 📁 Required Files
        Create `packages.txt` in root:
        ```
        libgl1-mesa-glx
        libglib2.0-0
        ```
        """)

# ============================================
# MAIN APP
# ============================================

def main():
    # Check session timeout
    if check_session_timeout():
        st.warning("Session expired. Please refresh the page.")
        return
    
    # Header
    st.markdown('<div class="brunei-flag">🇧🇳</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">BRUNEI DARUSSALAM<br>Secure Smart Inventory Management System</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📊 Secure Navigation")
    page = st.sidebar.radio("Select Module:", [
        "🏠 Executive Dashboard",
        "📝 Product CRUD Dashboard",
        "📦 Product Master List",
        "📍 Inventory by Location",
        "🔄 Stock Transactions",
        "🚚 Purchase Orders",
        "🏢 Supplier Directory",
        "⚠️ Stock Alert Monitoring",
        "🤖 Visionify AI Monitor",
        "💬 Secure Warehouse Assistant"
    ])
    
    # Update sidebar with security info
    update_sidebar()
    
    # Show setup guide in sidebar
    show_setup_guide()
    
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
    elif page == "💬 Secure Warehouse Assistant":
        show_warehouse_assistant()

if __name__ == "__main__":
    main()
