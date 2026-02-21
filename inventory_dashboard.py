import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Brunei Inventory System",
    page_icon="🇧🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Brunei theme
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #F7E017 0%, #000000 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #F7E017;
    }
    .stButton>button {
        background-color: #F7E017;
        color: black;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Generate Brunei-specific data
@st.cache_data
def generate_brunei_data():
    """Generate sample data for Brunei market"""
    
    # Brunei suppliers
    suppliers = [
        "Hua Ho Trading", "Soon Lee MegaMart", "Supasave", 
        "Seng Huat", "SKH Group", "Wee Hua Enterprise",
        "Pohan Motors", "D'Sunlit Supermarket", "Joyful Mart", 
        "Al-Falah Corporation"
    ]
    
    # Brunei locations
    locations = [
        "Warehouse - Beribi",
        "Store - Gadong", 
        "Store - Kiulap",
        "Store - Kuala Belait", 
        "Store - Tutong"
    ]
    
    # Product categories with Brunei-relevant items
    products_data = []
    
    # Electronics
    for item in ["LED TV 55\"", "Smartphone", "Laptop", "Tablet", "Bluetooth Speaker"]:
        products_data.append({
            "Product_ID": f"PRD{len(products_data)+1:04d}",
            "SKU": f"ELEC{random.randint(1000,9999)}",
            "Product_Name": item,
            "Category": "Electronics",
            "Unit_Cost_BND": round(random.uniform(100, 2000), 2),
            "Selling_Price_BND": round(random.uniform(150, 2500), 2),
            "Reorder_Level": random.randint(5, 15),
            "Supplier": random.choice(suppliers),
            "Status": "Active"
        })
    
    # Groceries
    for item in ["Basmati Rice 5kg", "Cooking Oil 2L", "Sugar 1kg", "Flour 1kg", "Instant Noodles"]:
        products_data.append({
            "Product_ID": f"PRD{len(products_data)+1:04d}",
            "SKU": f"GR{random.randint(1000,9999)}",
            "Product_Name": item,
            "Category": "Groceries",
            "Unit_Cost_BND": round(random.uniform(2, 30), 2),
            "Selling_Price_BND": round(random.uniform(3, 40), 2),
            "Reorder_Level": random.randint(20, 50),
            "Supplier": random.choice(suppliers),
            "Status": "Active"
        })
    
    # Hardware
    for item in ["Paint 5L", "Cement 40kg", "PVC Pipe", "Electrical Wire", "Light Bulb"]:
        products_data.append({
            "Product_ID": f"PRD{len(products_data)+1:04d}",
            "SKU": f"HDW{random.randint(1000,9999)}",
            "Product_Name": item,
            "Category": "Hardware",
            "Unit_Cost_BND": round(random.uniform(5, 80), 2),
            "Selling_Price_BND": round(random.uniform(8, 120), 2),
            "Reorder_Level": random.randint(10, 30),
            "Supplier": random.choice(suppliers),
            "Status": "Active"
        })
    
    # Automotive
    for item in ["Engine Oil", "Car Battery", "Air Filter", "Brake Pad", "Spark Plug"]:
        products_data.append({
            "Product_ID": f"PRD{len(products_data)+1:04d}",
            "SKU": f"ATM{random.randint(1000,9999)}",
            "Product_Name": item,
            "Category": "Automotive",
            "Unit_Cost_BND": round(random.uniform(15, 200), 2),
            "Selling_Price_BND": round(random.uniform(25, 300), 2),
            "Reorder_Level": random.randint(8, 20),
            "Supplier": random.choice(suppliers),
            "Status": "Active"
        })
    
    products_df = pd.DataFrame(products_data)
    
    # Generate Inventory
    inventory_data = []
    for _, product in products_df.iterrows():
        for loc in locations:
            inventory_data.append({
                "Product_ID": product["Product_ID"],
                "Location": loc,
                "Quantity": random.randint(0, 150),
                "Last_Updated": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")
            })
    
    inventory_df = pd.DataFrame(inventory_data)
    
    # Generate Transactions
    transactions_data = []
    types = ["STOCK IN", "STOCK OUT", "ADJUSTMENT"]
    
    for i in range(100):
        product = products_df.sample(1).iloc[0]
        trans_type = random.choice(types)
        
        if trans_type == "STOCK IN":
            qty = random.randint(10, 50)
        elif trans_type == "STOCK OUT":
            qty = -random.randint(1, 20)
        else:
            qty = random.choice([-5, -2, 2, 5])
        
        transactions_data.append({
            "Date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "Product": product["Product_Name"],
            "Type": trans_type,
            "Quantity": qty,
            "Location": random.choice(locations)
        })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    return {
        "products": products_df,
        "inventory": inventory_df,
        "transactions": transactions_df,
        "suppliers": suppliers,
        "locations": locations
    }

# Load data
data = generate_brunei_data()

# Header
st.markdown("""
    <div class="main-header">
        <h1>🇧🇳 Brunei Darussalam Inventory Management System</h1>
        <p style="font-size: 1.2rem;">Real-time Tracking | Multi-location | AI-Ready</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/9c/Flag_of_Brunei.svg", width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Dashboard",
    "Products",
    "Inventory",
    "Transactions",
    "Stock Alerts",
    "Visionify AI"
])

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(data["products"])
        st.metric("Total Products", total_products)
    
    with col2:
        total_stock = data["inventory"]["Quantity"].sum()
        st.metric("Total Items in Stock", f"{total_stock:,}")
    
    with col3:
        total_value = (data["inventory"]["Quantity"] * 
                      data["products"]["Unit_Cost_BND"].mean()).sum()
        st.metric("Inventory Value", f"B${total_value:,.0f}")
    
    with col4:
        locations = len(data["locations"])
        st.metric("Locations", locations)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock by Category")
        cat_stock = data["inventory"].merge(
            data["products"][["Product_ID", "Category"]], on="Product_ID"
        ).groupby("Category")["Quantity"].sum().reset_index()
        
        fig = px.pie(cat_stock, values="Quantity", names="Category",
                    title="Inventory Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Stock by Location")
        loc_stock = data["inventory"].groupby("Location")["Quantity"].sum().reset_index()
        
        fig = px.bar(loc_stock, x="Location", y="Quantity",
                    title="Inventory by Location",
                    color="Quantity")
        st.plotly_chart(fig, use_container_width=True)

# Products Page
elif page == "Products":
    st.header("📦 Product Master List")
    
    # Search and filter
    search = st.text_input("Search Products")
    category = st.selectbox("Category", ["All"] + list(data["products"]["Category"].unique()))
    
    # Filter products
    filtered = data["products"].copy()
    if search:
        filtered = filtered[filtered["Product_Name"].str.contains(search, case=False)]
    if category != "All":
        filtered = filtered[filtered["Category"] == category]
    
    # Display
    st.dataframe(
        filtered,
        column_config={
            "Unit_Cost_BND": "Cost (BND)",
            "Selling_Price_BND": "Price (BND)",
        },
        use_container_width=True
    )

# Inventory Page
elif page == "Inventory":
    st.header("📍 Inventory by Location")
    
    # Location selector
    selected_loc = st.selectbox("Select Location", data["locations"])
    
    # Get inventory for selected location
    loc_inv = data["inventory"][data["inventory"]["Location"] == selected_loc]
    loc_inv = loc_inv.merge(
        data["products"][["Product_ID", "Product_Name", "Category"]], 
        on="Product_ID"
    )
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(loc_inv))
    with col2:
        st.metric("Total Quantity", loc_inv["Quantity"].sum())
    with col3:
        low_stock = len(loc_inv[loc_inv["Quantity"] < 20])
        st.metric("Low Stock Items", low_stock)
    
    # Display
    st.dataframe(loc_inv, use_container_width=True)

# Transactions Page
elif page == "Transactions":
    st.header("📊 Stock Transactions")
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end = st.date_input("End Date", datetime.now())
    
    # Filter transactions
    transactions = data["transactions"].copy()
    transactions["Date"] = pd.to_datetime(transactions["Date"])
    mask = (transactions["Date"].dt.date >= start) & (transactions["Date"].dt.date <= end)
    filtered = transactions[mask]
    
    # Summary
    st.metric("Total Transactions", len(filtered))
    
    # Display
    st.dataframe(filtered.sort_values("Date", ascending=False), use_container_width=True)
    
    # Chart
    daily = filtered.groupby("Date")["Quantity"].sum().reset_index()
    fig = px.line(daily, x="Date", y="Quantity", title="Daily Stock Movement")
    st.plotly_chart(fig, use_container_width=True)

# Stock Alerts Page
elif page == "Stock Alerts":
    st.header("⚠️ Stock Alert Monitoring")
    
    # Calculate alerts
    current_stock = data["inventory"].groupby("Product_ID")["Quantity"].sum().reset_index()
    alerts = current_stock.merge(
        data["products"][["Product_ID", "Product_Name", "Reorder_Level"]], 
        on="Product_ID"
    )
    
    alerts["Status"] = alerts.apply(
        lambda x: "🔴 CRITICAL" if x["Quantity"] == 0 
        else "🟡 LOW" if x["Quantity"] <= x["Reorder_Level"]
        else "🟢 NORMAL",
        axis=1
    )
    
    # Alert counts
    col1, col2, col3 = st.columns(3)
    with col1:
        critical = len(alerts[alerts["Status"] == "🔴 CRITICAL"])
        st.metric("Critical Stock", critical, "Out of Stock")
    with col2:
        low = len(alerts[alerts["Status"] == "🟡 LOW"])
        st.metric("Low Stock", low, "Reorder Soon")
    with col3:
        normal = len(alerts[alerts["Status"] == "🟢 NORMAL"])
        st.metric("Normal Stock", normal, "OK")
    
    # Show alerts
    st.subheader("Items Needing Attention")
    attention = alerts[alerts["Status"].str.contains("CRITICAL|LOW")]
    
    if len(attention) > 0:
        st.dataframe(attention, use_container_width=True)
        
        # Reorder suggestions
        st.subheader("Suggested Reorders")
        attention["Suggested_Order"] = attention["Reorder_Level"] * 2 - attention["Quantity"]
        attention["Suggested_Order"] = attention["Suggested_Order"].apply(lambda x: max(x, 10))
        st.dataframe(attention[["Product_Name", "Quantity", "Reorder_Level", "Suggested_Order"]])
    else:
        st.success("✅ All stock levels are normal!")

# Visionify AI Page
elif page == "Visionify AI":
    st.header("👁️ Visionify AI Integration")
    
    st.markdown("""
    ### AI-Powered Warehouse Monitoring
    
    **Features for Brunei Businesses:**
    
    📦 **Automated Inventory Tracking**
    - Real-time stock counting
    - Automatic reorder triggers
    - Bin-level monitoring
    
    🛡️ **Worker Safety**
    - PPE compliance detection
    - Restricted area alerts
    - Slip and fall detection
    
    📊 **Analytics**
    - Warehouse heat maps
    - Productivity tracking
    - Bottleneck identification
    """)
    
    # Demo metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cameras Connected", "8", "+2 this month")
    with col2:
        st.metric("AI Detections", "1,247", "+12.3%")
    with col3:
        st.metric("Safety Alerts", "3", "-2 from yesterday")
    
    # Investment options
    st.subheader("💰 Investment Plans")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Basic**\n\nBND 500/month\n\n• 4 cameras\n• Basic counting\n• Email alerts")
    with col2:
        st.warning("**Professional**\n\nBND 1,200/month\n\n• 10 cameras\n• Safety monitoring\n• Dashboard")
    with col3:
        st.error("**Enterprise**\n\nCustom pricing\n\n• Unlimited cameras\n• Full analytics\n• Dedicated support")
    
    if st.button("📞 Request Brunei Demo"):
        st.success("Thank you! Our Gadong team will contact you within 24 hours.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Brunei Locations")
for loc in data["locations"]:
    st.sidebar.markdown(f"- {loc}")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
