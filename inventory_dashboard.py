"""
🇧🇳 Brunei Darussalam Inventory Management System
Professional Dashboard with Visionify AI Integration and Intelligent Warehouse Chatbot
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import random
import json
import time

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Brunei Inventory System",
    page_icon="🇧🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS FOR BRUNEI THEME
# ============================================
st.markdown("""
    <style>
    /* Main header with Brunei colors */
    .main-header {
        background: linear-gradient(135deg, #F7E017 0%, #000000 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #F7E017;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Brunei badge */
    .brunei-badge {
        background-color: #F7E017;
        color: black;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
        border: 2px solid black;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #F7E017;
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: black;
        color: #F7E017;
        border: 1px solid #F7E017;
    }
    
    /* Alert boxes */
    .alert-critical {
        background-color: #ff4b4b;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background-color: #ffa500;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .alert-success {
        background-color: #00cc66;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Chatbot styling */
    .chat-container {
        background-color: #f9f9f9;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #ddd;
    }
    
    .user-message {
        background-color: #F7E017;
        color: black;
        padding: 10px 15px;
        border-radius: 20px 20px 5px 20px;
        margin: 5px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background-color: #e9ecef;
        color: black;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 5px;
        margin: 5px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    .chat-timestamp {
        font-size: 0.7rem;
        color: #666;
        margin: 2px 0;
    }
    
    .chat-header {
        background-color: black;
        color: #F7E017;
        padding: 15px;
        border-radius: 10px 10px 0 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background-color: white;
        border: 2px solid #F7E017;
        color: black;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        cursor: pointer;
        margin: 5px;
        transition: all 0.3s;
    }
    .quick-action-btn:hover {
        background-color: #F7E017;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# WAREHOUSE KNOWLEDGE BASE FOR CHATBOT
# ============================================

WAREHOUSE_KNOWLEDGE = {
    "general": {
        "what is warehousing": "Warehousing is the process of storing physical inventory for sale or distribution. In Brunei, warehousing is crucial for managing goods in our tropical climate, requiring proper humidity and temperature control.",
        "warehouse types": """
        **Common Warehouse Types in Brunei:**
        1. **Public Warehouses** - Third-party facilities (like those in Beribi Industrial Park)
        2. **Private Warehouses** - Company-owned (Hua Ho, Soon Lee)
        3. **Distribution Centers** - Focus on moving goods quickly
        4. **Climate-Controlled** - Essential for electronics, pharmaceuticals
        5. **Bonded Warehouses** - For imported goods, customs-bonded
        """,
        "warehouse layout": """
        **Optimal Warehouse Layout Principles:**
        - **Receiving Area**: Near entrance for quick unloading
        - **Putaway Zone**: Temporary storage before shelving
        - **Storage Area**: Organized by SKU velocity (fast-movers near shipping)
        - **Picking Area**: Ergonomic design for efficient order fulfillment
        - **Packing Station**: With adequate supplies and space
        - **Shipping Area**: Near exit with dock levelers
        - **Office Space**: For supervisors and systems
        """
    },
    
    "inventory_management": {
        "abc analysis": """
        **ABC Analysis for Inventory:**
        - **A Items (10-20% of items, 70-80% value)**: High-value, tight control, frequent counting
        - **B Items (20-30% of items, 15-20% value)**: Moderate control, periodic review
        - **C Items (50-60% of items, 5-10% value)**: Simple controls, bulk storage
        
        **Example from Brunei Market:**
        - A Items: Electronics (TVs, phones), high-value automotive parts
        - B Items: Hardware tools, cosmetics
        - C Items: Groceries, stationery
        """,
        
        "safety stock": """
        **Safety Stock Calculation:**
        Safety Stock = (Maximum Daily Usage × Maximum Lead Time) - (Average Daily Usage × Average Lead Time)
        
        **For Brunei businesses, consider:**
        - Weather delays (monsoon season Nov-March)
        - Shipment delays from Singapore/Malaysia
        - Local holidays (Hari Raya, Chinese New Year)
        - Supplier reliability scores
        
        **Recommended Safety Stock Levels:**
        - Critical items: 30-50 days
        - Regular items: 14-21 days
        - Slow movers: 7-10 days
        """,
        
        "reorder point": """
        **Reorder Point Formula:**
        Reorder Point = (Average Daily Usage × Lead Time) + Safety Stock
        
        **Example (Brunei context):**
        If you sell 10 units/day of cooking oil, lead time 5 days, safety stock 20:
        Reorder Point = (10 × 5) + 20 = 70 units
        
        **When stock hits 70, system automatically triggers purchase order**
        """,
        
        "cycle counting": """
        **Cycle Counting Best Practices:**
        
        **Frequency by Category:**
        - A Items: Monthly or weekly
        - B Items: Quarterly
        - C Items: Bi-annually
        
        **Benefits:**
        - No warehouse shutdown needed
        - Higher accuracy than annual counts
        - Identify root causes of discrepancies
        - Maintain inventory accuracy (>95%)
        
        **Brunei warehouses typically count 50-100 items daily**
        """
    },
    
    "warehouse_operations": {
        "receiving process": """
        **Receiving Process Best Practices:**
        
        1. **Pre-Receiving**: 
           - Schedule appointments
           - Verify ASN (Advanced Shipping Notice)
           - Prepare receiving area
        
        2. **Physical Receiving**:
           - Count items against PO
           - Inspect for damage
           - Check expiry dates (especially for groceries/pharma)
           - Verify temperature (if applicable)
        
        3. **System Update**:
           - Enter received quantities
           - Update inventory
           - Generate receiving report
        
        4. **Putaway**:
           - Assign storage locations
           - Move to designated areas
           - Update bin locations
        """,
        
        "picking strategies": """
        **Picking Methods Comparison:**
        
        1. **Piece Picking**: Individual items
           - Best for: Small orders, retail stores
           - Accuracy: 99.5%
           - Speed: Slow
        
        2. **Case Picking**: Full boxes
           - Best for: Wholesale, bulk orders
           - Accuracy: 99.8%
           - Speed: Medium
        
        3. **Pallet Picking**: Full pallets
           - Best for: Large transfers
           - Accuracy: 99.9%
           - Speed: Fast
        
        4. **Zone Picking**: Pickers assigned to zones
           - Best for: Large warehouses
           - Accuracy: 99.7%
           - Speed: Very Fast
        
        5. **Batch Picking**: Multiple orders at once
           - Best for: Similar items
           - Efficiency: High
        """,
        
        "slotting optimization": """
        **Warehouse Slotting Optimization:**
        
        **Fast Movers (A Items):**
        - Place near shipping
        - Waist-high shelves
        - Wide aisles for access
        
        **Medium Movers (B Items):**
        - Mid-level shelving
        - Reasonable proximity
        
        **Slow Movers (C Items):**
        - Upper/lower shelves
        - Back of warehouse
        
        **Special Considerations for Brunei:**
        - Electronics: Climate-controlled zones
        - Food items: FIFO (First-In-First-Out) priority
        - Hazardous materials: Segregated areas
        - High-value items: Secure, locked cages
        """
    },
    
    "technology": {
        "wms benefits": """
        **Warehouse Management System (WMS) Benefits:**
        
        1. **Real-time Inventory Visibility**: Know stock levels instantly
        2. **Improved Accuracy**: Reduce errors by 95%
        3. **Space Utilization**: Optimize storage by 20-30%
        4. **Labor Productivity**: Increase efficiency by 25%
        5. **Customer Service**: Faster, accurate orders
        
        **ROI for Brunei Warehouses:**
        - Average payback: 6-12 months
        - Error reduction: 99.5% accuracy
        - Space savings: 20% more capacity
        """,
        
        "barcode vs rfid": """
        **Barcode vs RFID Comparison:**
        
        **Barcodes:**
        - Cost: $0.01-0.05 each
        - Scan rate: One at a time
        - Line of sight: Required
        - Read range: Few inches
        - Durability: Can be damaged
        - Best for: Retail, small warehouses
        
        **RFID:**
        - Cost: $0.10-0.50 each
        - Scan rate: 100+ per second
        - Line of sight: Not required
        - Read range: Up to 30 feet
        - Durability: Rugged
        - Best for: Large warehouses, high-value items
        
        **Brunei Recommendation:**
        - Start with barcodes (lower cost)
        - Add RFID for high-value electronics
        """,
        
        "visionify ai": """
        **Visionify AI Features for Warehouses:**
        
        **Inventory Tracking:**
        - Real-time stock counting via CCTV
        - Bin-level inventory visibility
        - Automatic low-stock alerts
        - 99.5% accuracy rate
        
        **Safety Monitoring:**
        - PPE compliance detection
        - Restricted area alerts
        - Slip and fall detection
        - Forklift proximity warnings
        
        **Analytics:**
        - Heat maps of activity
        - Productivity tracking
        - Bottleneck identification
        - Predictive maintenance
        
        **ROI for Brunei:**
        - Reduce shrinkage by 80%
        - Improve safety by 60%
        - Save 20% on labor costs
        - Payback: 6-8 months
        """
    },
    
    "safety_compliance": {
        "osh requirements": """
        **Brunei Warehouse Safety Requirements (SHENA):**
        
        1. **Fire Safety**:
           - Fire extinguishers every 75m
           - Clear emergency exits
           - Sprinkler systems
           - Fire drills quarterly
        
        2. **Equipment Safety**:
           - Forklift operator certification
           - Regular maintenance logs
           - Speed limits (5km/h indoors)
           - Horns and lights working
        
        3. **Personal Protective Equipment (PPE)**:
           - Safety shoes (steel-toe)
           - High-visibility vests
           - Hard hats in racking areas
           - Gloves for material handling
        
        4. **Ergonomics**:
           - Proper lifting techniques
           - Mechanical lift assistance
           - Anti-fatigue mats
           - Regular breaks
        
        5. **Housekeeping**:
           - Clear aisles (min 1m width)
           - Spill kits available
           - Proper waste disposal
           - Regular inspections
        """,
        
        "temperature control": """
        **Temperature Requirements for Brunei Climate:**
        
        **Ambient Storage (25-30°C):**
        - Dry goods
        - Hardware
        - Textiles
        
        **Cool Storage (15-20°C):**
        - Electronics
        - Cosmetics
        - Some pharmaceuticals
        
        **Cold Storage (2-8°C):**
        - Fresh food
        - Vaccines
        - Some chemicals
        
        **Frozen Storage (-18 to -22°C):**
        - Frozen food
        - Ice cream
        - Some pharmaceuticals
        
        **Monitoring Requirements:**
        - Continuous temperature logging
        - Alarms for deviations
        - Backup power systems
        - Calibrated sensors monthly
        """
    },
    
    "brunei_specific": {
        "local regulations": """
        **Brunei Warehouse Regulations:**
        
        1. **Business License**: Required from Ministry of Finance
        2. **Import/Export**: Customs bonded warehouse license for imports
        3. **Halal Certification**: For food/pharmaceutical warehouses
        4. **Environmental**: Waste disposal permits
        5. **Building**: Fire safety certificate from Fire Department
        
        **Key Authorities:**
        - SHENA (Safety, Health and Environment Authority)
        - Royal Customs and Excise
        - Ministry of Primary Resources (halal)
        - Brunei Fire and Rescue Department
        """,
        
        "logistics challenges": """
        **Brunei Logistics Considerations:**
        
        **Seasonal Challenges:**
        - Monsoon season (Nov-Mar): Delivery delays
        - Hari Raya: Port closures, staff leave
        - Chinese New Year: Supplier closures
        
        **Infrastructure:**
        - Muara Port: Main entry point
        - Land links: Only to Miri, Sarawak
        - Air freight: Brunei International Airport
        
        **Solutions:**
        - Build safety stock before monsoon
        - Diversify suppliers (local + regional)
        - Use technology for visibility
        - Partner with reliable logistics providers
        """,
        
        "local best practices": """
        **Best Practices for Brunei Warehouses:**
        
        1. **Climate Control**: Invest in dehumidifiers for electronics
        2. **Halal Compliance**: Separate storage for halal/non-halal
        3. **Local Suppliers**: Build relationships with Brunei vendors
        4. **Multi-lingual Staff**: Malay, English, Mandarin speakers
        5. **Community Relations**: Good neighbor policy
        
        **Success Metrics:**
        - Inventory accuracy: >98%
        - Order fill rate: >95%
        - On-time delivery: >97%
        - Employee retention: >85%
        """
    },
    
    "metrics_kpis": {
        "key metrics": """
        **Essential Warehouse KPIs:**
        
        1. **Inventory Accuracy**:
           - Target: >98%
           - Formula: (Counted Value / System Value) × 100
        
        2. **Order Fill Rate**:
           - Target: >95%
           - Formula: (Orders Shipped Complete / Total Orders) × 100
        
        3. **On-Time Delivery**:
           - Target: >97%
           - Formula: (Orders Delivered On Time / Total Orders) × 100
        
        4. **Storage Utilization**:
           - Target: 80-85%
           - Formula: (Used Space / Total Space) × 100
        
        5. **Labor Productivity**:
           - Target: Varies by operation
           - Formula: Units Handled / Labor Hours
        
        6. **Carrying Cost**:
           - Target: 20-30% of inventory value
           - Includes: Storage, insurance, taxes, obsolescence
        
        7. **Dock-to-Stock Time**:
           - Target: <24 hours
           - Time from receipt to available inventory
        """,
        
        "cost analysis": """
        **Warehouse Cost Breakdown:**
        
        **Fixed Costs (40-50%):**
        - Rent/Mortgage: 15-20%
        - Equipment depreciation: 10-15%
        - Insurance: 5-8%
        - Property taxes: 3-5%
        - IT systems: 5-7%
        
        **Variable Costs (50-60%):**
        - Labor: 30-40%
        - Utilities: 8-12%
        - Maintenance: 5-8%
        - Supplies: 3-5%
        - Transportation: 5-10%
        
        **Cost Reduction Strategies:**
        - Automate repetitive tasks
        - Optimize layout for efficiency
        - Cross-train employees
        - Implement energy-efficient lighting
        - Regular equipment maintenance
        """
    }
}

# ============================================
# CHATBOT RESPONSE FUNCTION
# ============================================

def get_chatbot_response(user_input, context_data=None):
    """Generate intelligent responses based on user queries"""
    
    user_input_lower = user_input.lower()
    
    # System status queries
    if any(word in user_input_lower for word in ["system status", "health", "working", "status"]):
        return f"""
        **🟢 System Status: Online**
        
        **Current Metrics:**
        - Products Tracked: {len(context_data['products']) if context_data else '50+'}
        - Locations: 5 across Brunei
        - Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        - Data Accuracy: 99.5%
        
        **All systems operational! ✅**
        """
    
    # Stock alerts queries
    elif any(word in user_input_lower for word in ["alert", "low stock", "critical", "reorder"]):
        if context_data and 'stock_alerts' in context_data:
            critical = len(context_data['stock_alerts'][context_data['stock_alerts']['Alert_Status'].str.contains('CRITICAL')])
            low = len(context_data['stock_alerts'][context_data['stock_alerts']['Alert_Status'].str.contains('LOW')])
            
            return f"""
            **⚠️ Current Stock Alerts:**
            
            🔴 **Critical Stock**: {critical} items
            - Out of stock or below 50% of reorder level
            - Immediate action required
            
            🟡 **Low Stock**: {low} items
            - Below reorder level
            - Reorder soon
            
            🟢 **Normal**: {len(context_data['stock_alerts']) - critical - low} items
            
            **Recommended Actions:**
            1. Review critical items first
            2. Generate purchase orders
            3. Contact preferred suppliers
            """
    
    # Product queries
    elif any(word in user_input_lower for word in ["product", "item", "sku", "barcode"]):
        return """
        **📦 Product Information Available:**
        
        You can find detailed product information in the **Product Master List** page.
        
        **Each product includes:**
        - Product ID and SKU
        - Category classification
        - Cost and selling price (BND)
        - Reorder level
        - Preferred supplier
        - Current status
        
        **To search for a specific product:**
        1. Go to Product Master List
        2. Use the search box
        3. Filter by category
        """
    
    # Location queries
    elif any(word in user_input_lower for word in ["location", "where", "store", "warehouse"]):
        return f"""
        **📍 Our Brunei Locations:**
        
        1. **Warehouse A - Beribi Industrial Park**
           - Main distribution center
           - 50,000 sq ft
           - Climate-controlled zones
        
        2. **Store 1 - Gadong Central**
           - Retail outlet
           - Fast-moving consumer goods
        
        3. **Store 2 - Kiulap Commercial Area**
           - Electronics and gadgets focus
        
        4. **Store 3 - Kuala Belait Town**
           - Serving the Belait district
        
        5. **Store 4 - Tutong Town Centre**
           - Serving the Tutong district
        
        **Current stock across all locations:**
        - Total items: {context_data['inventory']['Quantity_On_Hand'].sum() if context_data else 'Available in dashboard'}
        """
    
    # Visionify AI queries
    elif any(word in user_input_lower for word in ["visionify", "ai", "camera", "computer vision"]):
        return WAREHOUSE_KNOWLEDGE['technology']['visionify ai']
    
    # Safety queries
    elif any(word in user_input_lower for word in ["safety", "osh", "ppe", "hazard"]):
        return WAREHOUSE_KNOWLEDGE['safety_compliance']['osh requirements']
    
    # ABC Analysis
    elif "abc" in user_input_lower and "analysis" in user_input_lower:
        return WAREHOUSE_KNOWLEDGE['inventory_management']['abc analysis']
    
    # Safety stock
    elif "safety stock" in user_input_lower:
        return WAREHOUSE_KNOWLEDGE['inventory_management']['safety stock']
    
    # Reorder point
    elif "reorder point" in user_input_lower or "reorder level" in user_input_lower:
        return WAREHOUSE_KNOWLEDGE['inventory_management']['reorder point']
    
    # Cycle counting
    elif "cycle count" in user_input_lower:
        return WAREHOUSE_KNOWLEDGE['inventory_management']['cycle counting']
    
    # Receiving
    elif any(word in user_input_lower for word in ["receiving", "receive", "unload"]):
        return WAREHOUSE_KNOWLEDGE['warehouse_operations']['receiving process']
    
    # Picking
    elif any(word in user_input_lower for word in ["picking", "pick", "order fulfillment"]):
        return WAREHOUSE_KNOWLEDGE['warehouse_operations']['picking strategies']
    
    # Slotting
    elif any(word in user_input_lower for word in ["slotting", "storage location", "putaway"]):
        return WAREHOUSE_KNOWLEDGE['warehouse_operations']['slotting optimization']
    
    # WMS
    elif "wms" in user_input_lower or "warehouse management system" in user_input_lower:
        return WAREHOUSE_KNOWLEDGE['technology']['wms benefits']
    
    # Barcode vs RFID
    elif any(word in user_input_lower for word in ["barcode", "rfid", "scan"]):
        return WAREHOUSE_KNOWLEDGE['technology']['barcode vs rfid']
    
    # Temperature control
    elif any(word in user_input_lower for word in ["temperature", "climate", "cold storage", "humidity"]):
        return WAREHOUSE_KNOWLEDGE['safety_compliance']['temperature control']
    
    # Brunei regulations
    elif any(word in user_input_lower for word in ["brunei regulation", "license", "permit", "law"]):
        return WAREHOUSE_KNOWLEDGE['brunei_specific']['local regulations']
    
    # Logistics challenges
    elif any(word in user_input_lower for word in ["logistics", "challenge", "delivery", "transport"]):
        return WAREHOUSE_KNOWLEDGE['brunei_specific']['logistics challenges']
    
    # Best practices
    elif "best practice" in user_input_lower:
        return WAREHOUSE_KNOWLEDGE['brunei_specific']['local best practices']
    
    # KPIs
    elif any(word in user_input_lower for word in ["kpi", "metric", "performance", "measure"]):
        return WAREHOUSE_KNOWLEDGE['metrics_kpis']['key metrics']
    
    # Cost analysis
    elif any(word in user_input_lower for word in ["cost", "budget", "expense", "spend"]):
        return WAREHOUSE_KNOWLEDGE['metrics_kpis']['cost analysis']
    
    # Warehouse types
    elif any(word in user_input_lower for word in ["type of warehouse", "warehouse type"]):
        return WAREHOUSE_KNOWLEDGE['general']['warehouse types']
    
    # Layout
    elif any(word in user_input_lower for word in ["layout", "design", "arrangement"]):
        return WAREHOUSE_KNOWLEDGE['general']['warehouse layout']
    
    # Greetings
    elif any(word in user_input_lower for word in ["hi", "hello", "hey", "greetings"]):
        return """
        **👋 Hello! Welcome to the Brunei Inventory System Assistant!**
        
        I'm here to help you with:
        - 📦 **Warehouse operations** (receiving, picking, storage)
        - 📊 **Inventory management** (ABC analysis, safety stock, reorder points)
        - 🤖 **Technology** (WMS, barcode/RFID, Visionify AI)
        - 🛡️ **Safety compliance** (OSH requirements, temperature control)
        - 🇧🇳 **Brunei-specific information** (regulations, best practices)
        - 📈 **KPIs and metrics** (performance tracking, cost analysis)
        
        **Try asking me:**
        - "What is ABC analysis?"
        - "How do I calculate safety stock?"
        - "Tell me about Visionify AI"
        - "What are Brunei warehouse regulations?"
        - "Show me current stock alerts"
        - "Explain picking strategies"
        
        How can I assist you today?
        """
    
    # Help
    elif any(word in user_input_lower for word in ["help", "what can you do", "capabilities"]):
        return """
        **🤖 I Can Help You With:**
        
        **Warehouse Operations:**
        - Receiving processes and best practices
        - Picking strategies (piece, case, pallet, zone, batch)
        - Slotting optimization for efficiency
        - Cycle counting methods
        
        **Inventory Management:**
        - ABC analysis for item classification
        - Safety stock calculation
        - Reorder point determination
        - Stock alert interpretation
        
        **Technology:**
        - WMS benefits and ROI
        - Barcode vs RFID comparison
        - Visionify AI features and pricing
        - System integration options
        
        **Safety & Compliance:**
        - Brunei OSH requirements (SHENA)
        - Temperature control requirements
        - PPE requirements
        - Fire safety regulations
        
        **Brunei-Specific:**
        - Local regulations and licenses
        - Logistics challenges and solutions
        - Best practices for Brunei warehouses
        - Local supplier information
        
        **Analytics:**
        - Key warehouse KPIs
        - Cost analysis and reduction
        - Performance metrics
        - ROI calculations
        
        **Just ask me anything about warehousing!**
        """
    
    # Default response
    else:
        return """
        **📚 I can help you with various warehousing topics!**
        
        **Try asking about:**
        - 🔍 **Specific topics**: "ABC analysis", "safety stock", "picking strategies"
        - 📊 **System info**: "current alerts", "system status", "locations"
        - 🤖 **Technology**: "Visionify AI", "WMS benefits", "barcode vs RFID"
        - 🛡️ **Safety**: "OSH requirements", "temperature control", "PPE"
        - 🇧🇳 **Brunei**: "local regulations", "logistics challenges", "best practices"
        - 📈 **Metrics**: "KPIs", "cost analysis", "performance"
        
        **Or just type "help" to see all my capabilities!**
        
        What would you like to know about warehousing?
        """

# ============================================
# CHATBOT INTERFACE
# ============================================

def render_chatbot(data):
    """Render the AI chatbot interface"""
    
    st.markdown("""
    <div class="chat-header">
        🤖 Warehouse AI Assistant
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your warehouse AI assistant. Ask me anything about warehousing, inventory management, or our system!",
                "timestamp": datetime.now().strftime("%H:%M")
            }
        ]
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Stock Alerts"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Show me current stock alerts",
                "timestamp": datetime.now().strftime("%H:%M")
            })
            response = get_chatbot_response("stock alerts", data)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    with col2:
        if st.button("🏭 ABC Analysis"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Explain ABC analysis",
                "timestamp": datetime.now().strftime("%H:%M")
            })
            response = get_chatbot_response("abc analysis", data)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    with col3:
        if st.button("🤖 Visionify AI"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Tell me about Visionify AI",
                "timestamp": datetime.now().strftime("%H:%M")
            })
            response = get_chatbot_response("visionify ai", data)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    with col4:
        if st.button("📋 Safety Rules"):
            st.session_state.messages.append({
                "role": "user",
                "content": "What are warehouse safety requirements?",
                "timestamp": datetime.now().strftime("%H:%M")
            })
            response = get_chatbot_response("safety requirements", data)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div style="overflow: auto;">
                        <div class="user-message">
                            {message["content"]}
                            <div class="chat-timestamp">{message["timestamp"]}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="overflow: auto;">
                        <div class="bot-message">
                            {message["content"]}
                            <div class="chat-timestamp">{message["timestamp"]}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # User input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input("Ask me anything about warehousing...", key="user_input")
        
        with col2:
            submitted = st.form_submit_button("Send 📤")
        
        if submitted and user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            # Get bot response
            with st.spinner("Thinking..."):
                time.sleep(0.5)  # Small delay for natural feel
                response = get_chatbot_response(user_input, data)
            
            # Add bot response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your warehouse AI assistant. Ask me anything about warehousing, inventory management, or our system!",
                "timestamp": datetime.now().strftime("%H:%M")
            }
        ]
        st.rerun()

# ============================================
# BRUNEI-SPECIFIC DATA (CACHED)
# ============================================
@st.cache_data
def load_brunei_data():
    """Load all Brunei-specific inventory data"""
    
    # Brunei Suppliers (10)
    suppliers = pd.DataFrame({
        'Supplier_ID': [f'SUP{i+1:03d}' for i in range(10)],
        'Supplier_Name': [
            'Hua Ho Trading Sdn Bhd',
            'Soon Lee MegaMart',
            'Supasave Corporation',
            'Seng Huat Trading',
            'SKH Group',
            'Wee Hua Enterprise',
            'Pohan Motors Sdn Bhd',
            'D\'Sunlit Supermarket',
            'Joyful Mart',
            'Al-Falah Corporation'
        ],
        'Contact_Person': [
            'Lim Ah Seng', 'Tan Mei Ling', 'David Wong', 'Michael Chen',
            'Steven Khoo', 'Jason Wee', 'Ahmad Pohan', 'Hjh Zainab',
            'Liew KF', 'Hj Osman'
        ],
        'Phone': [
            '673-2223456', '673-2337890', '673-2456789', '673-2771234',
            '673-2667890', '673-2884567', '673-2334455', '673-2656789',
            '673-2781234', '673-2235678'
        ],
        'Email': [
            'purchasing@huaho.com.bn', 'orders@soonlee.com.bn',
            'procurement@supasave.com.bn', 'sales@senghuat.com.bn',
            'trading@skh.com.bn', 'orders@weehua.com.bn',
            'parts@pohan.com.bn', 'procurement@dsunlit.com.bn',
            'supply@joyfulmart.com.bn', 'trading@alfalah.com.bn'
        ],
        'Address': [
            'KG Kiulap, BSB', 'Gadong Central, BSB', 'Serusop, BSB',
            'Kuala Belait', 'Tutong Town', 'Seria',
            'Beribi Industrial Park', 'Menglait, BSB',
            'Kiarong, BSB', 'Lambak Kanan, BSB'
        ]
    })
    
    # Brunei Locations
    locations = [
        'Warehouse A - Beribi Industrial Park',
        'Store 1 - Gadong Central',
        'Store 2 - Kiulap Commercial Area',
        'Store 3 - Kuala Belait Town',
        'Store 4 - Tutong Town Centre'
    ]
    
    # Product Categories with items
    categories = {
        'Electronics': [
            'Samsung 55" 4K LED TV', 'iPhone 15 Pro', 'MacBook Air M2',
            'iPad Pro 12.9"', 'Sony Bluetooth Speaker', 'TP-Link WiFi Router',
            'Logitech Wireless Mouse', 'SanDisk 1TB SSD', 'HP LaserJet Printer',
            'Samsung Galaxy Tab'
        ],
        'Groceries': [
            'Royal Basmati Rice 5kg', 'Seri Mas Cooking Oil 2L', 'Gula Pasir 1kg',
            'Tepung Gandum 1kg', 'Indomie Instant Noodles (40pcs)',
            'Ayam Brand Sardines', 'Kicap Cap Kipas 700ml', 'Nescafe Gold 200g',
            'Lipton Tea Bags 100s', "Jacob's Biscuits Family Pack"
        ],
        'Hardware': [
            'Jotun Paint 5L White', 'Portland Cement 40kg', 'PVC Pipe 4" x 6m',
            'Electrical Wire 2.5mm (100m)', 'LED Bulb 15W', 'Door Lock Set',
            'Stanley Hammer', 'Screwdriver Set (12pcs)', 'Bosch Drill Bit Set',
            'Sandpaper Assorted (10pcs)'
        ],
        'Pharmaceuticals': [
            'Paracetamol 500mg 100s', 'Actifed Cough Syrup', 'Clarityn Antihistamine',
            'Vitamin C 1000mg 60s', 'First Aid Kit (50pcs)', 'Elastic Bandage 4"',
            'Dettol Antiseptic 500ml', 'Visine Eye Drops', 'Voltaren Gel 100g',
            'Digital Thermometer'
        ],
        'Automotive': [
            'Shell Helix Engine Oil 4L', 'GS Battery NS40', 'Air Filter (Universal)',
            'Brake Pad Set (Front)', 'NGK Spark Plug (4pcs)', 'Windshield Wiper Pair',
            'Coolant 4L', 'ATF Transmission Fluid 4L', 'Tyre 205/55 R16',
            'Car Wax Premium'
        ]
    }
    
    # Generate Product Master
    products = []
    product_id = 1
    
    for category, items in categories.items():
        for item in items:
            # Generate realistic Brunei prices
            if category == 'Electronics':
                cost = round(random.uniform(100, 2000), 2)
            elif category == 'Groceries':
                cost = round(random.uniform(2, 50), 2)
            elif category == 'Hardware':
                cost = round(random.uniform(5, 200), 2)
            elif category == 'Pharmaceuticals':
                cost = round(random.uniform(5, 100), 2)
            else:  # Automotive
                cost = round(random.uniform(20, 300), 2)
            
            selling_price = round(cost * random.uniform(1.3, 1.6), 2)
            
            products.append({
                'Product_ID': f'PRD{product_id:04d}',
                'SKU': f'{category[:3].upper()}{random.randint(10000, 99999)}',
                'Barcode': f'888{random.randint(1000000, 9999999)}',
                'Product_Name': item,
                'Category': category,
                'Unit_Cost_BND': cost,
                'Selling_Price_BND': selling_price,
                'Reorder_Level': random.randint(5, 50),
                'Preferred_Supplier': random.choice(suppliers['Supplier_Name'].tolist()),
                'Status': 'Active'
            })
            product_id += 1
    
    products_df = pd.DataFrame(products)
    
    # Generate Inventory by Location
    inventory = []
    for _, product in products_df.iterrows():
        for loc in locations:
            # Different quantities by category
            if product['Category'] == 'Electronics':
                qty = random.randint(0, 30)
            elif product['Category'] == 'Groceries':
                qty = random.randint(0, 150)
            else:
                qty = random.randint(0, 80)
            
            inventory.append({
                'Product_ID': product['Product_ID'],
                'Location': loc,
                'Quantity_On_Hand': qty,
                'Last_Updated': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d')
            })
    
    inventory_df = pd.DataFrame(inventory)
    
    # Generate Stock Transactions
    transactions = []
    trans_types = ['STOCK IN', 'STOCK OUT', 'ADJUSTMENT']
    
    for i in range(200):
        product = products_df.sample(1).iloc[0]
        trans_type = random.choice(trans_types)
        
        if trans_type == 'STOCK IN':
            qty = random.randint(5, 50)
        elif trans_type == 'STOCK OUT':
            qty = -random.randint(1, 20)
        else:
            qty = random.choice([-5, -2, 2, 5])
        
        trans_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        transactions.append({
            'Transaction_ID': f'TRX{i:05d}',
            'Date': trans_date.strftime('%Y-%m-%d'),
            'Product_ID': product['Product_ID'],
            'Product_Name': product['Product_Name'],
            'Type': trans_type,
            'Quantity': qty,
            'Location': random.choice(locations)
        })
    
    transactions_df = pd.DataFrame(transactions)
    
    # Generate Purchase Orders
    pos = []
    statuses = ['Draft', 'Sent', 'Confirmed', 'Shipped', 'Received']
    
    for i in range(50):
        supplier = suppliers.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        qty = random.randint(20, 200)
        
        po_date = datetime.now() - timedelta(days=random.randint(0, 45))
        
        pos.append({
            'PO_Number': f'PO{i:05d}',
            'Supplier': supplier['Supplier_Name'],
            'Product': product['Product_Name'],
            'Ordered_Quantity': qty,
            'Unit_Cost': product['Unit_Cost_BND'],
            'Total_Cost': qty * product['Unit_Cost_BND'],
            'Order_Date': po_date.strftime('%Y-%m-%d'),
            'Status': random.choice(statuses)
        })
    
    pos_df = pd.DataFrame(pos)
    
    # Generate Stock Alerts
    current_stock = inventory_df.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    alerts = current_stock.merge(
        products_df[['Product_ID', 'Product_Name', 'Reorder_Level']], 
        on='Product_ID'
    )
    
    alerts['Alert_Status'] = alerts.apply(
        lambda x: '🔴 CRITICAL' if x['Quantity_On_Hand'] == 0 
        else '🟡 LOW' if x['Quantity_On_Hand'] <= x['Reorder_Level']
        else '🟢 NORMAL',
        axis=1
    )
    
    return {
        'products': products_df,
        'inventory': inventory_df,
        'transactions': transactions_df,
        'suppliers': suppliers,
        'purchase_orders': pos_df,
        'stock_alerts': alerts,
        'locations': locations
    }

# ============================================
# LOAD DATA
# ============================================
with st.spinner('Loading Brunei Inventory System...'):
    data = load_brunei_data()

# ============================================
# HEADER
# ============================================
st.markdown("""
    <div class="main-header">
        <h1>🇧🇳 Brunei Darussalam Inventory Management System</h1>
        <p style="font-size: 1.2rem;">Professional Inventory Tracking | Multi-Location Management | AI-Powered Insights</p>
        <div class="brunei-badge">📍 Operating in Beribi, Gadong, Kiulap, Kuala Belait & Tutong</div>
    </div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR NAVIGATION
# ============================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9c/Flag_of_Brunei.svg", 
             caption="Brunei Darussalam", width=200)
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    page = st.radio(
        "Select Page",
        [
            "🏠 Dashboard Overview",
            "📋 Product Master List",
            "📍 Inventory by Location",
            "📊 Stock Transactions",
            "🤝 Supplier Management",
            "📦 Purchase Orders",
            "⚠️ Stock Alert Monitoring",
            "👁️ Visionify AI Integration",
            "📈 Reports & Analytics",
            "🤖 AI Chatbot Assistant"  # New page for chatbot
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📍 Our Locations")
    for loc in data['locations']:
        st.markdown(f"- {loc}")
    
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("**Data Status:** ✅ Live")
    st.markdown("**Version:** 3.0.0 (with AI Chatbot)")

# ============================================
# PAGE ROUTING
# ============================================

if page == "🏠 Dashboard Overview":
    st.header("📊 Dashboard Overview")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(data['products'])
        st.metric(
            label="Total Products",
            value=f"{total_products}",
            delta="Active SKUs"
        )
    
    with col2:
        total_inventory = data['inventory']['Quantity_On_Hand'].sum()
        st.metric(
            label="Total Items in Stock",
            value=f"{total_inventory:,}",
            delta="Across all locations"
        )
    
    with col3:
        total_value = (data['inventory']['Quantity_On_Hand'] * 
                      data['products']['Unit_Cost_BND'].mean()).sum()
        st.metric(
            label="Inventory Value",
            value=f"B${total_value:,.0f}",
            delta="Current"
        )
    
    with col4:
        low_stock = len(data['stock_alerts'][data['stock_alerts']['Alert_Status'].str.contains('CRITICAL|LOW')])
        st.metric(
            label="Low Stock Alerts",
            value=low_stock,
            delta="Need attention",
            delta_color="inverse"
        )
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Stock Distribution by Category")
        cat_stock = data['inventory'].merge(
            data['products'][['Product_ID', 'Category']], on='Product_ID'
        ).groupby('Category')['Quantity_On_Hand'].sum().reset_index()
        
        fig = px.pie(
            cat_stock, 
            values='Quantity_On_Hand', 
            names='Category',
            title="Inventory by Category",
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📍 Stock by Location")
        loc_stock = data['inventory'].groupby('Location')['Quantity_On_Hand'].sum().reset_index()
        
        fig = px.bar(
            loc_stock, 
            x='Location', 
            y='Quantity_On_Hand',
            title="Inventory Distribution by Location",
            color='Quantity_On_Hand',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Transactions
    st.subheader("📋 Recent Stock Movements")
    recent = data['transactions'].sort_values('Date', ascending=False).head(10)
    st.dataframe(recent, use_container_width=True)

elif page == "📋 Product Master List":
    st.header("📋 Product Master List")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + list(data['products']['Category'].unique())
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        search = st.text_input("🔍 Search Products", placeholder="Enter product name...")
    
    with col3:
        show_discontinued = st.checkbox("Show Discontinued Products", value=False)
    
    # Filter data
    filtered = data['products'].copy()
    
    if selected_category != 'All':
        filtered = filtered[filtered['Category'] == selected_category]
    
    if search:
        filtered = filtered[filtered['Product_Name'].str.contains(search, case=False)]
    
    if not show_discontinued:
        filtered = filtered[filtered['Status'] == 'Active']
    
    # Display metrics
    st.info(f"📊 Showing {len(filtered)} products")
    
    # Display table
    st.dataframe(
        filtered,
        column_config={
            "Unit_Cost_BND": st.column_config.NumberColumn(
                "Unit Cost (BND)",
                format="B$%.2f"
            ),
            "Selling_Price_BND": st.column_config.NumberColumn(
                "Selling Price (BND)",
                format="B$%.2f"
            ),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Export option
    if st.button("📥 Export to CSV"):
        csv = filtered.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="brunei_products.csv",
            mime="text/csv"
        )

elif page == "📍 Inventory by Location":
    st.header("📍 Inventory by Location")
    
    # Location selector
    selected_location = st.selectbox("Select Location", data['locations'])
    
    # Get inventory for location
    loc_inventory = data['inventory'][data['inventory']['Location'] == selected_location]
    loc_inventory = loc_inventory.merge(
        data['products'][['Product_ID', 'Product_Name', 'Category', 'Reorder_Level']], 
        on='Product_ID'
    )
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Items", len(loc_inventory))
    
    with col2:
        total_qty = loc_inventory['Quantity_On_Hand'].sum()
        st.metric("Total Quantity", f"{total_qty:,}")
    
    with col3:
        low_stock = len(loc_inventory[loc_inventory['Quantity_On_Hand'] < loc_inventory['Reorder_Level']])
        st.metric("Low Stock Items", low_stock)
    
    # Display inventory
    st.subheader(f"📋 Inventory at {selected_location}")
    st.dataframe(
        loc_inventory[['Product_ID', 'Product_Name', 'Category', 'Quantity_On_Hand', 'Reorder_Level', 'Last_Updated']],
        use_container_width=True,
        hide_index=True
    )
    
    # Category breakdown for this location
    cat_breakdown = loc_inventory.groupby('Category')['Quantity_On_Hand'].sum().reset_index()
    
    fig = px.pie(
        cat_breakdown, 
        values='Quantity_On_Hand', 
        names='Category',
        title=f"Category Breakdown at {selected_location}",
        hole=0.3
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Stock Transactions":
    st.header("📊 Stock Transaction History")
    
    # Date range filter
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now()
        )
    
    # Transaction type filter
    trans_types = ['All'] + list(data['transactions']['Type'].unique())
    selected_type = st.selectbox("Transaction Type", trans_types)
    
    # Filter transactions
    transactions = data['transactions'].copy()
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    
    mask = (transactions['Date'].dt.date >= start_date) & (transactions['Date'].dt.date <= end_date)
    filtered = transactions[mask]
    
    if selected_type != 'All':
        filtered = filtered[filtered['Type'] == selected_type]
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Transactions", len(filtered))
    
    with col2:
        net_change = filtered['Quantity'].sum()
        st.metric("Net Stock Change", f"{net_change:+,}")
    
    with col3:
        avg_daily = len(filtered) / max((end_date - start_date).days, 1)
        st.metric("Avg Daily Transactions", f"{avg_daily:.1f}")
    
    # Display transactions
    st.subheader("📋 Transaction List")
    st.dataframe(
        filtered.sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Movement chart
    daily_movement = filtered.groupby('Date')['Quantity'].sum().reset_index()
    
    fig = px.line(
        daily_movement, 
        x='Date', 
        y='Quantity',
        title="Daily Stock Movement",
        markers=True
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🤝 Supplier Management":
    st.header("🤝 Supplier Management")
    
    # Search suppliers
    search = st.text_input("🔍 Search Suppliers", placeholder="Enter supplier name...")
    
    suppliers = data['suppliers'].copy()
    
    if search:
        suppliers = suppliers[suppliers['Supplier_Name'].str.contains(search, case=False)]
    
    # Display suppliers
    st.subheader(f"📋 Supplier List ({len(suppliers)} suppliers)")
    st.dataframe(
        suppliers,
        use_container_width=True,
        hide_index=True
    )
    
    # Supplier stats
    st.subheader("📊 Supplier Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Products per supplier
        supplier_products = data['products']['Preferred_Supplier'].value_counts().reset_index()
        supplier_products.columns = ['Supplier', 'Product Count']
        
        fig = px.bar(
            supplier_products.head(10),
            x='Supplier',
            y='Product Count',
            title="Top 10 Suppliers by Product Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Active suppliers
        st.info("**Quick Facts**")
        st.markdown(f"- Total Suppliers: {len(suppliers)}")
        st.markdown(f"- Average Products per Supplier: {data['products']['Preferred_Supplier'].value_counts().mean():.1f}")
        st.markdown(f"- Most Active Supplier: {data['products']['Preferred_Supplier'].mode()[0]}")

elif page == "📦 Purchase Orders":
    st.header("📦 Purchase Orders")
    
    # Status filter
    statuses = ['All'] + list(data['purchase_orders']['Status'].unique())
    selected_status = st.selectbox("Filter by Status", statuses)
    
    # Filter POs
    pos = data['purchase_orders'].copy()
    
    if selected_status != 'All':
        pos = pos[pos['Status'] == selected_status]
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total POs", len(pos))
    
    with col2:
        total_value = pos['Total_Cost'].sum()
        st.metric("Total Value", f"B${total_value:,.0f}")
    
    with col3:
        pending = len(pos[pos['Status'].isin(['Draft', 'Sent', 'Confirmed'])])
        st.metric("Pending POs", pending)
    
    # Display POs
    st.subheader("📋 Purchase Order List")
    st.dataframe(
        pos.sort_values('Order_Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # PO value chart
    pos_by_status = pos.groupby('Status')['Total_Cost'].sum().reset_index()
    
    fig = px.pie(
        pos_by_status,
        values='Total_Cost',
        names='Status',
        title="PO Value by Status"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "⚠️ Stock Alert Monitoring":
    st.header("⚠️ Stock Alert Monitoring")
    
    # Alert summary
    alerts = data['stock_alerts'].copy()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        critical = len(alerts[alerts['Alert_Status'].str.contains('CRITICAL')])
        st.markdown(f"""
            <div class="alert-critical">
                <h3>🔴 CRITICAL: {critical}</h3>
                <p>Out of Stock or Urgent</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low = len(alerts[alerts['Alert_Status'].str.contains('LOW')])
        st.markdown(f"""
            <div class="alert-warning">
                <h3>🟡 LOW STOCK: {low}</h3>
                <p>Below Reorder Level</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        normal = len(alerts[alerts['Alert_Status'].str.contains('NORMAL')])
        st.markdown(f"""
            <div class="alert-success">
                <h3>🟢 NORMAL: {normal}</h3>
                <p>Adequate Stock</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Show critical alerts first
    st.subheader("🚨 Immediate Action Required")
    critical_alerts = alerts[alerts['Alert_Status'].str.contains('CRITICAL')]
    
    if len(critical_alerts) > 0:
        st.dataframe(
            critical_alerts[['Product_ID', 'Product_Name', 'Current_Stock', 'Reorder_Level', 'Alert_Status']],
            use_container_width=True,
            hide_index=True
        )
        
        # Auto-reorder suggestions
        st.subheader("📦 Suggested Reorders")
        critical_alerts['Suggested_Order'] = critical_alerts['Reorder_Level'] * 2 - critical_alerts['Current_Stock']
        critical_alerts['Suggested_Order'] = critical_alerts['Suggested_Order'].apply(lambda x: max(x, 10))
        
        st.dataframe(
            critical_alerts[['Product_Name', 'Current_Stock', 'Reorder_Level', 'Suggested_Order']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No critical alerts! All stock levels are acceptable.")
    
    # Show low stock alerts
    st.subheader("⚠️ Low Stock Items")
    low_alerts = alerts[alerts['Alert_Status'].str.contains('LOW') & ~alerts['Alert_Status'].str.contains('CRITICAL')]
    
    if len(low_alerts) > 0:
        st.dataframe(
            low_alerts[['Product_ID', 'Product_Name', 'Current_Stock', 'Reorder_Level', 'Alert_Status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No low stock items at this time.")

elif page == "👁️ Visionify AI Integration":
    st.header("👁️ Visionify AI - Computer Vision for Warehouses")
    
    st.markdown("""
    ### Transform Your Warehouse with AI
    
    Visionify AI integrates with your existing CCTV cameras to provide real-time inventory tracking and safety monitoring.
    """)
    
    # Features in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📦 Automated Inventory
        - Real-time stock counting
        - Bin-level monitoring
        - Automatic reorder triggers
        - 99.5% accuracy rate
        """)
    
    with col2:
        st.markdown("""
        #### 🛡️ Worker Safety
        - PPE compliance detection
        - Restricted area alerts
        - Slip and fall detection
        - Heat map generation
        """)
    
    with col3:
        st.markdown("""
        #### 📊 Analytics
        - Productivity tracking
        - Bottleneck identification
        - Movement patterns
        - Predictive analytics
        """)
    
    # Demo metrics
    st.subheader("📊 Live Demo Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cameras Connected", "8", "+2 this month")
    
    with col2:
        st.metric("AI Detections", "1,247", "+12.3%")
    
    with col3:
        st.metric("Accuracy Rate", "99.5%", "+0.3%")
    
    with col4:
        st.metric("Safety Alerts", "3", "-2 from yesterday")
    
    # ROI Calculator
    st.subheader("💰 ROI Calculator for Brunei Businesses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        warehouse_size = st.number_input("Warehouse Size (sq ft)", min_value=1000, value=10000, step=1000)
        employees = st.number_input("Number of Employees", min_value=1, value=20, step=1)
    
    with col2:
        monthly_inventory_value = st.number_input("Monthly Inventory Value (BND)", min_value=10000, value=500000, step=10000)
        current_shrinkage = st.slider("Current Shrinkage %", 0.0, 10.0, 2.5, 0.1)
    
    if st.button("Calculate ROI"):
        savings = monthly_inventory_value * (current_shrinkage / 100) * 12
        labor_savings = employees * 500 * 12  # Estimated savings per employee
        
        st.success(f"""
        ### Estimated Annual Savings: B${savings + labor_savings:,.0f}
        - Inventory Shrinkage Reduction: B${savings:,.0f}
        - Labor Efficiency Savings: B${labor_savings:,.0f}
        - ROI Period: {(50000 / (savings + labor_savings) * 12):.1f} months
        """)
    
    # Pricing for Brunei
    st.subheader("💼 Investment Plans for Brunei Market")
    
    plan1, plan2, plan3 = st.columns(3)
    
    with plan1:
        st.markdown("""
        #### 🌱 Basic
        **BND 500/month**
        - Up to 4 cameras
        - Basic inventory counting
        - Email alerts
        - 1 user
        - Email support
        """)
        if st.button("Choose Basic", key="basic"):
            st.success("Demo request sent! Our team will contact you.")
    
    with plan2:
        st.markdown("""
        #### 🚀 Professional
        **BND 1,200/month**
        - Up to 10 cameras
        - Safety monitoring
        - Real-time dashboard
        - 5 users
        - Priority support
        """)
        if st.button("Choose Professional", key="pro"):
            st.success("Demo request sent! Our team will contact you.")
    
    with plan3:
        st.markdown("""
        #### 🏢 Enterprise
        **Custom Pricing**
        - Unlimited cameras
        - Full analytics suite
        - API access
        - Unlimited users
        - Dedicated support
        """)
        if st.button("Contact Sales", key="enterprise"):
            st.success("Our enterprise team will contact you within 24 hours.")
    
    # Contact form
    st.subheader("📞 Request Brunei Demo")
    
    with st.form("demo_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Your Name")
            company = st.text_input("Company Name")
            phone = st.text_input("Phone Number")
        
        with col2:
            email = st.text_input("Email Address")
            location = st.selectbox("Location", ["Bandar Seri Begawan", "Kuala Belait", "Tutong", "Temburong", "Other"])
            cameras = st.number_input("Number of Cameras", min_value=1, value=4)
        
        submitted = st.form_submit_button("Submit Demo Request")
        
        if submitted:
            st.success(f"✅ Thank you {name}! Our Gadong team will contact you at {email} within 24 hours to schedule your Brunei demo.")

elif page == "📈 Reports & Analytics":
    st.header("📈 Reports & Analytics")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Inventory Valuation", "Stock Movement Analysis", "Supplier Performance", "Category Analysis"]
    )
    
    if report_type == "Inventory Valuation":
        st.subheader("Inventory Valuation Report")
        
        valuation = data['inventory'].groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
        valuation = valuation.merge(
            data['products'][['Product_ID', 'Product_Name', 'Unit_Cost_BND', 'Category']], 
            on='Product_ID'
        )
        valuation['Total_Value'] = valuation['Quantity_On_Hand'] * valuation['Unit_Cost_BND']
        valuation = valuation.sort_values('Total_Value', ascending=False)
        
        total_value = valuation['Total_Value'].sum()
        st.metric("Total Inventory Value", f"B${total_value:,.2f}")
        
        # Top products chart
        fig = px.bar(
            valuation.head(20),
            x='Product_Name',
            y='Total_Value',
            title="Top 20 Products by Value",
            color='Category'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Valuation by category
        cat_value = valuation.groupby('Category')['Total_Value'].sum().reset_index()
        
        fig = px.pie(
            cat_value,
            values='Total_Value',
            names='Category',
            title="Inventory Value by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.dataframe(valuation, use_container_width=True, hide_index=True)
    
    elif report_type == "Stock Movement Analysis":
        st.subheader("Stock Movement Analysis")
        
        # Movement by type
        movement_by_type = data['transactions'].groupby('Type')['Quantity'].sum().reset_index()
        
        fig = px.bar(
            movement_by_type,
            x='Type',
            y='Quantity',
            title="Net Movement by Transaction Type",
            color='Type'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Movement over time
        daily = data['transactions'].groupby('Date')['Quantity'].sum().reset_index()
        daily['Date'] = pd.to_datetime(daily['Date'])
        daily = daily.sort_values('Date')
        
        fig = px.line(
            daily,
            x='Date',
            y='Quantity',
            title="Daily Stock Movement (30 Day Trend)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif report_type == "Supplier Performance":
        st.subheader("Supplier Performance Report")
        
        # Products per supplier
        supplier_products = data['products']['Preferred_Supplier'].value_counts().reset_index()
        supplier_products.columns = ['Supplier', 'Product Count']
        
        fig = px.bar(
            supplier_products,
            x='Supplier',
            y='Product Count',
            title="Products Supplied by Vendor"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # PO value by supplier
        po_by_supplier = data['purchase_orders'].groupby('Supplier')['Total_Cost'].sum().reset_index()
        po_by_supplier = po_by_supplier.sort_values('Total_Cost', ascending=False)
        
        fig = px.pie(
            po_by_supplier.head(10),
            values='Total_Cost',
            names='Supplier',
            title="Top 10 Suppliers by PO Value"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Category Analysis
        st.subheader("Category Analysis")
        
        # Stock by category
        cat_stock = data['inventory'].merge(
            data['products'][['Product_ID', 'Category']], on='Product_ID'
        ).groupby('Category')['Quantity_On_Hand'].sum().reset_index()
        
        fig = px.bar(
            cat_stock,
            x='Category',
            y='Quantity_On_Hand',
            title="Stock Levels by Category",
            color='Quantity_On_Hand'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Value by category (using valuation from above)
        valuation = data['inventory'].groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
        valuation = valuation.merge(
            data['products'][['Product_ID', 'Unit_Cost_BND', 'Category']], 
            on='Product_ID'
        )
        valuation['Total_Value'] = valuation['Quantity_On_Hand'] * valuation['Unit_Cost_BND']
        cat_value = valuation.groupby('Category')['Total_Value'].sum().reset_index()
        
        fig = px.bar(
            cat_value,
            x='Category',
            y='Total_Value',
            title="Inventory Value by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "🤖 AI Chatbot Assistant":
    st.header("🤖 Warehouse AI Assistant")
    
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <p style="font-size: 1.1rem; margin: 0;">
            💡 <strong>Ask me anything about warehousing, inventory management, or our system!</strong>
        </p>
        <p style="margin: 0.5rem 0 0 0; color: #666;">
            Try questions like: "What is ABC analysis?", "How to calculate safety stock?", 
            "Tell me about Visionify AI", "What are Brunei warehouse regulations?"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render the chatbot
    render_chatbot(data)

# ============================================
# FOOTER
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Contact")
st.sidebar.markdown("""
**Brunei Office**  
Unit 8, Gadong Commercial Area  
Bandar Seri Begawan  
Phone: +673 123 4567  
Email: info@bruneiinventory.com
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Investor Information")
st.sidebar.markdown("""
- **ROI**: 6 months
- **Market**: Brunei & Borneo
- **Funding**: BND 250,000
- **Scalability**: ASEAN ready
- **AI Assistant**: 24/7 warehouse expertise
""")
