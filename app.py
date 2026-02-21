import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    """
    Load data from Excel file
    In production, this connects to your Google Drive Excel file
    """
    # For Streamlit Cloud, we'll use the data structure from your Excel
    # In production, replace with: pd.read_excel('your_google_drive_link')
    
    # Product Master List (50 products)
    products = pd.DataFrame({
        'Product_ID': [f'PRD{i:05d}' for i in range(1, 51)],
        'SKU': ['ELE9513', 'ELE6539', 'ELE5637', 'ELE4243', 'ELE6781'] + [f'SKU{i}' for i in range(6, 51)],
        'Barcode': [8882629770, 8885034668, 8881920026, 8887653820, 8881862054] + [8882000000 + i for i in range(6, 51)],
        'Product_Name': [
            'LED TV', 'Smartphone', 'Laptop', 'Tablet', 'Bluetooth Speaker',
            'Basmati Rice 5kg', 'Cooking Oil 2L', 'Sugar 1kg', 'Flour 1kg', 'Instant Noodles',
            'Paint 5L', 'Cement 40kg', 'PVC Pipe', 'Electrical Wire', 'Light Bulb',
            'Paracetamol', 'Cough Syrup', 'Vitamin C', 'First Aid Kit', 'Bandages',
            'Engine Oil', 'Car Battery', 'Air Filter', 'Brake Pad', 'Spark Plug',
            'School Uniform', 'Baju Kurung', 'Baju Melayu', 'Songkok', 'Tudung',
            'Office Desk', 'Ergonomic Chair', 'Filing Cabinet', 'Bookshelf', 'Meeting Table',
            'A4 Paper', 'Printer Ink', 'Ballpoint Pen', 'Notebook', 'Folder',
            'Mineral Water', 'Soft Drinks', 'Orange Juice', 'Energy Drink', 'Milk',
            'Facial Cleanser', 'Moisturizer', 'Lipstick', 'Foundation', 'Shampoo'
        ],
        'Category': [
            'Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics',
            'Groceries', 'Groceries', 'Groceries', 'Groceries', 'Groceries',
            'Hardware', 'Hardware', 'Hardware', 'Hardware', 'Hardware',
            'Pharmaceuticals', 'Pharmaceuticals', 'Pharmaceuticals', 'Pharmaceuticals', 'Pharmaceuticals',
            'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive',
            'Textiles', 'Textiles', 'Textiles', 'Textiles', 'Textiles',
            'Furniture', 'Furniture', 'Furniture', 'Furniture', 'Furniture',
            'Stationery', 'Stationery', 'Stationery', 'Stationery', 'Stationery',
            'Beverages', 'Beverages', 'Beverages', 'Beverages', 'Beverages',
            'Cosmetics', 'Cosmetics', 'Cosmetics', 'Cosmetics', 'Cosmetics'
        ],
        'Unit_Cost_BND': [
            785.00, 916.00, 618.00, 1960.00, 754.00,
            8.00, 11.00, 47.00, 42.00, 3.00,
            97.00, 56.00, 49.00, 37.00, 8.00,
            141.00, 6.00, 99.00, 47.00, 76.00,
            185.00, 119.00, 160.00, 71.00, 119.00,
            43.00, 111.00, 111.00, 21.00, 119.00,
            91.00, 60.00, 128.00, 46.00, 130.00,
            136.00, 129.00, 131.00, 101.00, 56.00,
            32.00, 10.00, 22.00, 7.00, 29.00,
            23.00, 94.00, 141.00, 80.00, 88.00
        ],
        'Selling_Price_BND': [
            1135.09, 1351.05, 872.40, 2653.80, 907.19,
            9.81, 14.28, 62.97, 58.50, 4.34,
            116.66, 78.46, 71.86, 44.82, 9.95,
            189.88, 8.25, 121.28, 56.69, 110.20,
            269.02, 167.34, 209.16, 100.99, 168.95,
            54.40, 150.36, 152.78, 26.51, 173.22,
            129.73, 88.18, 164.85, 58.12, 188.59,
            190.82, 168.32, 193.55, 139.82, 73.26,
            41.07, 12.46, 26.73, 10.05, 42.27,
            32.48, 138.40, 179.42, 101.94, 125.16
        ],
        'Reorder_Level': [7, 35, 25, 6, 6, 18, 11, 46, 14, 50, 44, 34, 25, 5, 36, 13, 14, 24, 5, 5, 12, 17, 49, 14, 37, 46, 43, 21, 28, 17, 26, 8, 40, 31, 33, 27, 14, 36, 48, 27, 47, 11, 42, 37, 33, 49, 29, 24, 20, 16],
        'Preferred_Supplier': [
            'Supasave', 'Pohan Motors', 'Al-Falah Corporation', 'Hua Ho Trading', 'Soon Lee MegaMart',
            'Seng Huat', 'Al-Falah Corporation', 'Hua Ho Trading', 'Hua Ho Trading', 'Supasave',
            'SKH Group', 'Wee Hua Enterprise', 'D\'Sunlit Supermarket', 'SKH Group', 'SKH Group',
            'Al-Falah Corporation', 'Wee Hua Enterprise', 'Al-Falah Corporation', 'SKH Group', 'Supasave',
            'D\'Sunlit Supermarket', 'Joyful Mart', 'Seng Huat', 'Al-Falah Corporation', 'D\'Sunlit Supermarket',
            'Pohan Motors', 'SKH Group', 'Wee Hua Enterprise', 'Wee Hua Enterprise', 'D\'Sunlit Supermarket',
            'D\'Sunlit Supermarket', 'Supasave', 'Joyful Mart', 'Seng Huat', 'Al-Falah Corporation',
            'SKH Group', 'Hua Ho Trading', 'Supasave', 'Joyful Mart', 'Supasave',
            'Supasave', 'Pohan Motors', 'Supasave', 'D\'Sunlit Supermarket', 'SKH Group',
            'Joyful Mart', 'Hua Ho Trading', 'D\'Sunlit Supermarket', 'Soon Lee MegaMart', 'SKH Group'
        ],
        'Status': ['Active'] * 48 + ['Discontinued', 'Discontinued']
    })
    
    # Inventory by Location (250 records)
    locations = ['Warehouse A - Beribi', 'Store 1 - Gadong', 'Store 2 - Kiulap', 'Store 3 - Kuala Belait', 'Store 4 - Tutong']
    inventory_data = []
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in enumerate(locations):
            qty = [163, 132, 171, 179, 172, 19, 163, 42, 165, 76][(i*5+j) % 10] if i < 2 else (50 + (i*j) % 150)
            inventory_data.append({
                'Product_ID': prod,
                'Location': loc,
                'Quantity_On_Hand': qty,
                'Last_Updated': '2026-02-20'
            })
    inventory = pd.DataFrame(inventory_data)
    
    # Stock Transactions (150 records)
    transaction_types = ['ADJUSTMENT', 'STOCK IN', 'STOCK OUT']
    remarks_options = ['Inventory Count', 'Purchase Order', 'Sale', 'System Correction', 'Transfer from Warehouse', 
                      'Return from Customer', 'Expired', 'Damaged', 'Sample/Display']
    
    transactions = pd.DataFrame({
        'Transaction_ID': [f'TRX2026{i:04d}' for i in range(150)],
        'Date': pd.date_range(start='2025-11-01', periods=150, freq='D').tolist(),
        'Product_ID': [products['Product_ID'].iloc[i % 50] for i in range(150)],
        'Product_Name': [products['Product_Name'].iloc[i % 50] for i in range(150)],
        'Transaction_Type': [transaction_types[i % 3] for i in range(150)],
        'Quantity_Change': [5 if i % 3 == 0 else (-5 if i % 3 == 2 else 10) for i in range(150)],
        'Location': [locations[i % 5] for i in range(150)],
        'Reference_Number': [f'REF{1000+i}' for i in range(150)],
        'Remarks': [remarks_options[i % 9] for i in range(150)]
    })
    
    # Supplier Management (10 suppliers)
    suppliers = pd.DataFrame({
        'Supplier_ID': [f'SUP{i:03d}' for i in range(1, 11)],
        'Supplier_Name': [
            'Hua Ho Trading', 'Soon Lee MegaMart', 'Supasave', 'Seng Huat', 'SKH Group',
            'Wee Hua Enterprise', 'Pohan Motors', 'D\'Sunlit Supermarket', 'Joyful Mart', 'Al-Falah Corporation'
        ],
        'Contact_Person': [
            'Lim Ah Seng', 'Tan Mei Ling', 'David Wong', 'Michael Chen', 'Steven Khoo',
            'Jason Wee', 'Ahmad Pohan', 'Hjh Zainab', 'Liew KF', 'Hj Osman'
        ],
        'Phone': [
            '673-2223456', '673-2337890', '673-2456789', '673-2771234', '673-2667890',
            '673-2884567', '673-2334455', '673-2656789', '673-2781234', '673-2235678'
        ],
        'Email': [
            'purchasing@huaho.com.bn', 'orders@soonlee.com.bn', 'procurement@supasave.com.bn',
            'sales@senghuat.com.bn', 'trading@skh.com.bn', 'orders@weehua.com.bn',
            'parts@pohan.com.bn', 'procurement@dsunlit.com.bn', 'supply@joyfulmart.com.bn',
            'trading@alfalah.com.bn'
        ],
        'Address': [
            'KG Kiulap, Bandar Seri Begawan', 'Gadong Central, BSB', 'Serusop, BSB',
            'Kuala Belait', 'Tutong Town', 'Seria', 'Beribi Industrial Park', 'Menglait, BSB',
            'Kiarong', 'Lambak Kanan'
        ],
        'Payment_Terms': [
            'Cash on Delivery', 'Cash on Delivery', 'Net 45', 'Cash on Delivery', 'Net 30',
            'Net 30', 'Cash on Delivery', 'Cash on Delivery', 'Net 45', 'Cash on Delivery'
        ]
    })
    
    # Purchase Orders (40 POs)
    po_status = ['Confirmed', 'Received', 'Received', 'Received', 'Cancelled', 'Sent', 'Shipped', 'Sent', 'Sent', 'Sent',
                 'Sent', 'Confirmed', 'Draft', 'Confirmed', 'Shipped', 'Shipped', 'Cancelled', 'Sent', 'Shipped', 'Shipped',
                 'Cancelled', 'Confirmed', 'Shipped', 'Sent', 'Cancelled', 'Confirmed', 'Confirmed', 'Shipped', 'Shipped',
                 'Cancelled', 'Received', 'Received', 'Received', 'Received', 'Sent', 'Sent', 'Cancelled', 'Shipped', 'Draft']
    
    purchase_orders = pd.DataFrame({
        'PO_Number': [f'PO2026{i:04d}' for i in range(40)],
        'Supplier_ID': [f'SUP{(i % 10) + 1:03d}' for i in range(40)],
        'Supplier_Name': [suppliers['Supplier_Name'].iloc[i % 10] for i in range(40)],
        'Product_ID': [products['Product_ID'].iloc[i % 50] for i in range(40)],
        'Product_Name': [products['Product_Name'].iloc[i % 50] for i in range(40)],
        'Ordered_Quantity': [100 + (i * 10) for i in range(40)],
        'Received_Quantity': [80 + (i * 5) for i in range(40)],
        'Unit_Cost_BND': [products['Unit_Cost_BND'].iloc[i % 50] for i in range(40)],
        'Total_Cost_BND': [(100 + (i * 10)) * products['Unit_Cost_BND'].iloc[i % 50] for i in range(40)],
        'Order_Date': pd.date_range(start='2025-12-01', periods=40, freq='3D').tolist(),
        'Expected_Date': pd.date_range(start='2025-12-10', periods=40, freq='3D').tolist(),
        'Order_Status': po_status
    })
    
    # Stock Alert Monitoring (50 alerts)
    alerts = pd.DataFrame({
        'Product_ID': products['Product_ID'],
        'Product_Name': products['Product_Name'],
        'Category': products['Category'],
        'Current_Stock': [817, 465, 574, 614, 573, 355, 460, 388, 640, 724,
                         470, 400, 212, 644, 371, 838, 670, 565, 302, 392,
                         394, 391, 540, 536, 578, 465, 432, 412, 616, 594,
                         303, 614, 354, 519, 322, 501, 408, 542, 492, 578,
                         505, 221, 635, 372, 574, 410, 366, 641, 343, 444],
        'Reorder_Level': products['Reorder_Level'],
        'Alert_Status': ['🟢 NORMAL'] * 50
    })
    
    return products, inventory, transactions, suppliers, purchase_orders, alerts

def main():
    # Header
    st.markdown('<div class="brunei-flag">🇧🇳</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">BRUNEI DARUSSALAM<br>Smart Inventory Management System</h1>', 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Powered by AI & Computer Vision Technology</h3>", 
                unsafe_allow_html=True)
    
    # Load data
    products, inventory, transactions, suppliers, purchase_orders, alerts = load_data()
    
    # Calculate metrics
    total_products = len(products)
    total_inventory_value = (inventory.merge(products[['Product_ID', 'Unit_Cost_BND']], on='Product_ID')
                            .assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
    total_locations = inventory['Location'].nunique()
    pending_statuses = ['Confirmed', 'Sent', 'Draft', 'Shipped']
    pending_orders = len(purchase_orders[purchase_orders['Order_Status'].isin(pending_statuses)])
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Select Module:", [
        "🏠 Executive Dashboard",
        "📦 Product Master (50 Products)",
        "📍 Inventory by Location (5 Sites)",
        "🔄 Stock Transactions (150 Records)",
        "🚚 Purchase Orders (40 POs)",
        "🏢 Supplier Directory (10 Suppliers)",
        "⚠️ Stock Alert Monitoring",
        "🤖 Visionify AI Monitor",
        "💬 Warehouse AI Assistant"
    ])
    
    if page == "🏠 Executive Dashboard":
        st.title("Executive Dashboard")
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Total Products", total_products, "10 Categories")
        with col2:
            st.metric("💰 Inventory Value", f"BND ${total_inventory_value:,.0f}")
        with col3:
            st.metric("📍 Locations", total_locations, "1 Warehouse + 4 Stores")
        with col4:
            st.metric("📋 Pending Orders", pending_orders, "Require Attention")
        
        st.markdown("---")
        
        # Charts row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Products by Category")
            category_data = products['Category'].value_counts()
            fig = px.pie(values=category_data.values, names=category_data.index, 
                        color_discrete_sequence=px.colors.sequential.Gold_r)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📍 Stock Distribution by Location")
            location_data = inventory.groupby('Location')['Quantity_On_Hand'].sum().reset_index()
            fig = px.bar(location_data, x='Location', y='Quantity_On_Hand',
                        color='Quantity_On_Hand', color_continuous_scale='Viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Charts row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Inventory Value by Category")
            merged_value = inventory.merge(products[['Product_ID', 'Unit_Cost_BND', 'Category']], on='Product_ID')
            merged_value['Total_Value'] = merged_value['Quantity_On_Hand'] * merged_value['Unit_Cost_BND']
            category_value = merged_value.groupby('Category')['Total_Value'].sum().reset_index()
            fig = px.bar(category_value, x='Category', y='Total_Value',
                        color='Total_Value', color_continuous_scale='Blues')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Purchase Order Status")
            po_status = purchase_orders['Order_Status'].value_counts()
            fig = px.pie(values=po_status.values, names=po_status.index,
                        color_discrete_sequence=px.colors.sequential.Plasma_r)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent transactions
        st.subheader("🔄 Recent Stock Movements")
        recent_txn = transactions.sort_values('Date', ascending=False).head(10)
        st.dataframe(recent_txn[['Date', 'Product_Name', 'Transaction_Type', 'Quantity_Change', 'Location']], 
                    use_container_width=True)
    
    elif page == "📦 Product Master (50 Products)":
        st.title("Product Master List")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("🔍 Search products...")
        with col2:
            category_filter = st.multiselect("Filter by Category:", products['Category'].unique())
        
        filtered_df = products
        if search:
            filtered_df = filtered_df[filtered_df['Product_Name'].str.contains(search, case=False)]
        if category_filter:
            filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Product analysis
        st.subheader("💰 Profit Margin Analysis")
        products['Margin_BND'] = products['Selling_Price_BND'] - products['Unit_Cost_BND']
        products['Margin_%'] = ((products['Selling_Price_BND'] - products['Unit_Cost_BND']) / 
                               products['Selling_Price_BND'] * 100).round(2)
        
        fig = px.scatter(products, x='Unit_Cost_BND', y='Margin_%', 
                        color='Category', size='Margin_BND',
                        hover_data=['Product_Name'], title="Profit Margins by Product")
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "📍 Inventory by Location (5 Sites)":
        st.title("Multi-Location Inventory")
        
        location_filter = st.selectbox("Select Location:", ['All'] + list(inventory['Location'].unique()))
        
        if location_filter != 'All':
            display_df = inventory[inventory['Location'] == location_filter]
        else:
            display_df = inventory
        
        # Merge with product names
        display_df = display_df.merge(products[['Product_ID', 'Product_Name', 'Category']], on='Product_ID')
        
        # Calculate totals
        display_df['Total_Value'] = display_df['Quantity_On_Hand'] * display_df.merge(
            products[['Product_ID', 'Unit_Cost_BND']], on='Product_ID')['Unit_Cost_BND']
        
        st.dataframe(display_df[['Product_ID', 'Product_Name', 'Category', 'Location', 'Quantity_On_Hand', 'Last_Updated']], 
                    use_container_width=True)
        
        # Location summary
        st.subheader("📊 Location Summary")
        location_summary = inventory.groupby('Location').agg({
            'Quantity_On_Hand': 'sum',
            'Product_ID': 'nunique'
        }).reset_index()
        location_summary.columns = ['Location', 'Total_Units', 'Unique_Products']
        
        # Add values
        loc_values = []
        for loc in location_summary['Location']:
            loc_inv = inventory[inventory['Location'] == loc]
            loc_val = (loc_inv.merge(products[['Product_ID', 'Unit_Cost_BND']], on='Product_ID')
                      .assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
            loc_values.append(loc_val)
        location_summary['Total_Value_BND'] = loc_values
        
        st.dataframe(location_summary, use_container_width=True)
        
        # Visual comparison
        fig = px.bar(location_summary, x='Location', y='Total_Value_BND',
                    color='Total_Units', title='Inventory Value by Location')
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "🔄 Stock Transactions (150 Records)":
        st.title("Stock Transaction History")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            txn_type = st.multiselect("Transaction Type:", transactions['Transaction_Type'].unique())
        with col2:
            location_filter = st.multiselect("Location:", transactions['Location'].unique())
        with col3:
            product_search = st.text_input("Product Name:")
        
        filtered_txn = transactions
        if txn_type:
            filtered_txn = filtered_txn[filtered_txn['Transaction_Type'].isin(txn_type)]
        if location_filter:
            filtered_txn = filtered_txn[filtered_txn['Location'].isin(location_filter)]
        if product_search:
            filtered_txn = filtered_txn[filtered_txn['Product_Name'].str.contains(product_search, case=False)]
        
        st.dataframe(filtered_txn.sort_values('Date', ascending=False), use_container_width=True)
        
        # Transaction analysis
        st.subheader("📈 Transaction Trends")
        txn_summary = transactions.groupby(['Date', 'Transaction_Type']).size().reset_index(name='Count')
        fig = px.line(txn_summary, x='Date', y='Count', color='Transaction_Type', markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Transaction type distribution
        st.subheader("📊 Transaction Type Distribution")
        txn_dist = transactions['Transaction_Type'].value_counts()
        fig = px.pie(values=txn_dist.values, names=txn_dist.index, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "🚚 Purchase Orders (40 POs)":
        st.title("Purchase Order Management")
        
        # Status overview
        status_counts = purchase_orders['Order_Status'].value_counts()
        cols = st.columns(len(status_counts))
        for i, (status, count) in enumerate(status_counts.items()):
            with cols[i]:
                color = "🔵" if status == "Confirmed" else "🟢" if status == "Received" else "🟡" if status == "Shipped" else "🟠" if status == "Sent" else "⚪"
                st.metric(f"{color} {status}", count)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status:", purchase_orders['Order_Status'].unique())
        with col2:
            supplier_filter = st.multiselect("Filter by Supplier:", purchase_orders['Supplier_Name'].unique())
        
        filtered_po = purchase_orders
        if status_filter:
            filtered_po = filtered_po[filtered_po['Order_Status'].isin(status_filter)]
        if supplier_filter:
            filtered_po = filtered_po[filtered_po['Supplier_Name'].isin(supplier_filter)]
        
        st.dataframe(filtered_po.sort_values('Order_Date', ascending=False), use_container_width=True)
        
        # PO Value analysis
        st.subheader("💵 Purchase Order Analysis")
        po_value_by_supplier = purchase_orders.groupby('Supplier_Name')['Total_Cost_BND'].sum().reset_index()
        fig = px.bar(po_value_by_supplier, x='Supplier_Name', y='Total_Cost_BND',
                    title="Total PO Value by Supplier")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "🏢 Supplier Directory (10 Suppliers)":
        st.title("Supplier Directory")
        
        st.dataframe(suppliers[['Supplier_ID', 'Supplier_Name', 'Contact_Person', 'Phone', 'Email', 'Address', 'Payment_Terms']], 
                    use_container_width=True)
        
        # Supplier performance
        st.subheader("📈 Supplier Performance")
        supplier_activity = purchase_orders.groupby('Supplier_Name').agg({
            'Total_Cost_BND': 'sum',
            'PO_Number': 'count',
            'Ordered_Quantity': 'sum'
        }).reset_index()
        supplier_activity.columns = ['Supplier_Name', 'Total_Spend_BND', 'Order_Count', 'Total_Units']
        
        fig = px.scatter(supplier_activity, x='Order_Count', y='Total_Spend_BND',
                        size='Total_Units', text='Supplier_Name', 
                        title="Supplier Performance Matrix")
        st.plotly_chart(fig, use_container_width=True)
        
        # Payment terms distribution
        st.subheader("💳 Payment Terms Distribution")
        payment_terms = suppliers['Payment_Terms'].value_counts()
        fig = px.pie(values=payment_terms.values, names=payment_terms.index)
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "⚠️ Stock Alert Monitoring":
        st.title("Automated Stock Alert System")
        
        # Calculate current stock levels
        stock_levels = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
        stock_levels = stock_levels.merge(products[['Product_ID', 'Product_Name', 'Category', 'Reorder_Level']], on='Product_ID')
        
        # Determine status
        def get_status(row):
            if row['Quantity_On_Hand'] <= row['Reorder_Level'] * 0.5:
                return '🔴 CRITICAL'
            elif row['Quantity_On_Hand'] <= row['Reorder_Level']:
                return '🟡 WARNING'
            else:
                return '🟢 NORMAL'
        
        stock_levels['Alert_Status'] = stock_levels.apply(get_status, axis=1)
        
        # Summary metrics
        critical_count = len(stock_levels[stock_levels['Alert_Status'] == '🔴 CRITICAL'])
        warning_count = len(stock_levels[stock_levels['Alert_Status'] == '🟡 WARNING'])
        normal_count = len(stock_levels[stock_levels['Alert_Status'] == '🟢 NORMAL'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 Critical", critical_count)
        col2.metric("🟡 Warning", warning_count)
        col3.metric("🟢 Normal", normal_count)
        
        # Alert table
        st.subheader("Stock Levels by Product")
        
        # Filter options
        status_filter = st.multiselect("Filter by Status:", ['🔴 CRITICAL', '🟡 WARNING', '🟢 NORMAL'], default=['🔴 CRITICAL', '🟡 WARNING'])
        category_filter = st.multiselect("Filter by Category:", products['Category'].unique())
        
        display_alerts = stock_levels
        if status_filter:
            display_alerts = display_alerts[display_alerts['Alert_Status'].isin(status_filter)]
        if category_filter:
            display_alerts = display_alerts[display_alerts['Category'].isin(category_filter)]
        
        st.dataframe(display_alerts[['Alert_Status', 'Product_ID', 'Product_Name', 'Category', 'Quantity_On_Hand', 'Reorder_Level']], 
                    use_container_width=True)
        
        # Auto-generate PO suggestions for low stock
        st.subheader("📝 Suggested Purchase Orders")
        low_stock = stock_levels[stock_levels['Alert_Status'].isin(['🔴 CRITICAL', '🟡 WARNING'])]
        
        if not low_stock.empty:
            for _, item in low_stock.iterrows():
                supplier = products[products['Product_ID'] == item['Product_ID']]['Preferred_Supplier'].values[0]
                unit_cost = products[products['Product_ID'] == item['Product_ID']]['Unit_Cost_BND'].values[0]
                suggested_qty = int(item['Reorder_Level'] * 2 - item['Quantity_On_Hand'])
                total_cost = suggested_qty * unit_cost
                
                with st.expander(f"📦 {item['Product_Name']} ({item['Alert_Status']})"):
                    st.write(f"**Current Stock:** {item['Quantity_On_Hand']} units")
                    st.write(f"**Reorder Level:** {item['Reorder_Level']} units")
                    st.write(f"**Suggested Order:** {suggested_qty} units")
                    st.write(f"**Supplier:** {supplier}")
                    st.write(f"**Est. Cost:** BND ${total_cost:,.2f}")
                    st.button(f"Create PO for {item['Product_Name']}", key=item['Product_ID'])
        else:
            st.success("✅ All stock levels are healthy! No orders needed.")
    
    elif page == "🤖 Visionify AI Monitor":
        st.title("Visionify AI - Computer Vision Monitoring")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;'>
        <h3>🎥 AI-Powered Warehouse Monitoring</h3>
        <p>Integrating with existing CCTV systems for real-time inventory tracking and safety monitoring across 5 Brunei locations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📹 Camera Feed Status")
            
            locations_cam = {
                'Warehouse A - Beribi': {'status': '🔴 Live', 'cameras': 4},
                'Store 1 - Gadong': {'status': '🟢 Live', 'cameras': 2},
                'Store 2 - Kiulap': {'status': '🟢 Live', 'cameras': 2},
                'Store 3 - Kuala Belait': {'status': '🟡 Maintenance', 'cameras': 2},
                'Store 4 - Tutong': {'status': '🟢 Live', 'cameras': 2}
            }
            
            for loc, data in locations_cam.items():
                st.write(f"{data['status']} **{loc}** ({data['cameras']} cameras)")
            
            st.markdown("---")
            st.subheader("🎯 AI Detection Modules")
            st.checkbox("📦 Product Recognition & Counting", value=True)
            st.checkbox("👷 Personnel Safety (PPE Detection)", value=True)
            st.checkbox("📊 Shelf Empty Detection", value=True)
            st.checkbox("🚨 Unauthorized Access Alert", value=True)
            st.checkbox("📱 Mobile Phone Usage Detection", value=False)
        
        with col2:
            st.subheader("📊 Vision AI Analytics")
            
            # Simulated detection data based on your locations
            detection_data = pd.DataFrame({
                'Hour': list(range(8, 20)),
                'Warehouse_A': [12, 15, 18, 20, 16, 14, 10, 8, 5, 3, 2, 1],
                'Store_1_Gadong': [25, 30, 35, 40, 38, 35, 30, 25, 20, 15, 10, 5],
                'Store_2_Kiulap': [20, 25, 28, 32, 30, 28, 25, 20, 15, 10, 8, 4]
            })
            
            fig = px.line(detection_data, x='Hour', 
                         y=['Warehouse_A', 'Store_1_Gadong', 'Store_2_Kiulap'],
                         title='Customer/Personnel Detection by Hour')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.subheader("⚡ Real-time Alerts")
            st.error("🚨 Unauthorized access detected - Warehouse A Zone B (12:34 PM)")
            st.warning("⚠️ Low stock detected on Shelf A-12 via camera (11:45 AM)")
            st.success("✅ Safety check completed - All PPE detected (10:00 AM)")
            st.info("📦 Auto-counted 50 LED TVs in Warehouse A (09:30 AM)")
        
        st.markdown("---")
        st.info("""
        **Visionify AI Integration Features for Brunei:**
        - **Real-time Object Detection**: YOLOv8 model trained on 50 product categories
        - **Multi-location Support**: 5 locations across Brunei (Beribi, Gadong, Kiulap, Kuala Belait, Tutong)
        - **Safety Compliance**: Automatic PPE detection for warehouse staff
        - **Inventory Automation**: 60% reduction in manual counting time
        - **Theft Prevention**: Anomaly detection in restricted zones
        - **Integration**: Works with existing Hikvision/Dahua CCTV systems
        """)
    
    elif page == "💬 Warehouse AI Assistant":
        st.title("🤖 Warehouse Management AI Assistant")
        
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700;'>
        <h4>Ask me anything about your Brunei inventory system, warehouse management, or logistics!</h4>
        <p><strong>Example questions:</strong> "What's my inventory value?", "Which products need reordering?", "Tell me about Visionify AI"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize chat history
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your inventory..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response based on your actual data
            response = generate_warehouse_response(prompt, products, inventory, purchase_orders, suppliers)
            
            with st.chat_message("assistant"):
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

def generate_warehouse_response(prompt, products, inventory, purchase_orders, suppliers):
    """Generate contextual responses based on your actual data"""
    prompt_lower = prompt.lower()
    
    # Inventory value query
    if any(word in prompt_lower for word in ['inventory value', 'total value', 'worth']):
        total_value = (inventory.merge(products[['Product_ID', 'Unit_Cost_BND']], on='Product_ID')
                      .assign(Value=lambda x: x['Quantity_On_Hand'] * x['Unit_Cost_BND'])['Value'].sum())
        return f"💰 Your total inventory value across all 5 locations is **BND ${total_value:,.2f}**."
    
    # Product count query
    elif any(word in prompt_lower for word in ['how many products', 'total products', 'product count']):
        return f"📦 You have **{len(products)} products** across **{products['Category'].nunique()} categories**: {', '.join(products['Category'].unique())}."
    
    # Location query
    elif any(word in prompt_lower for word in ['locations', 'stores', 'warehouse']):
        locations = inventory['Location'].unique()
        loc_summary = inventory.groupby('Location')['Quantity_On_Hand'].sum()
        response = "📍 Your inventory is distributed across **5 locations**:\n\n"
        for loc in locations:
            response += f"- **{loc}**: {loc_summary[loc]:,} units\n"
        return response
    
    # Low stock query
    elif any(word in prompt_lower for word in ['low stock', 'reorder', 'critical']):
        stock_levels = inventory.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
        stock_levels = stock_levels.merge(products[['Product_ID', 'Product_Name', 'Reorder_Level']], on='Product_ID')
        low_stock = stock_levels[stock_levels['Quantity_On_Hand'] <= stock_levels['Reorder_Level']]
        
        if len(low_stock) > 0:
            response = f"⚠️ **{len(low_stock)} products** are at or below reorder level:\n\n"
            for _, item in low_stock.head(5).iterrows():
                response += f"- {item['Product_Name']}: {item['Quantity_On_Hand']} units (Reorder: {item['Reorder_Level']})\n"
            return response
        else:
            return "✅ All products are currently above reorder levels. No immediate action needed!"
    
    # Supplier query
    elif any(word in prompt_lower for word in ['suppliers', 'vendors', 'who supplies']):
        return f"🏢 You work with **{len(suppliers)} suppliers** in Brunei:\n\n" + \
               "\n".join([f"- **{row['Supplier_Name']}** ({row['Contact_Person']}, {row['Phone']})" 
                         for _, row in suppliers.iterrows()])
    
    # Purchase order query
    elif any(word in prompt_lower for word in ['purchase order', 'po', 'orders']):
        pending = len(purchase_orders[purchase_orders['Order_Status'].isin(['Confirmed', 'Sent', 'Draft', 'Shipped'])])
        total_po_value = purchase_orders['Total_Cost_BND'].sum()
        return f"📋 You have **{len(purchase_orders)} total purchase orders**.\n" + \
               f"- **{pending}** are pending (Confirmed/Sent/Draft/Shipped)\n" + \
               f"- Total value of all POs: **BND ${total_po_value:,.2f}**"
    
    # Electronics category
    elif any(word in prompt_lower for word in ['electronics', 'led tv', 'smartphone', 'laptop']):
        electronics = products[products['Category'] == 'Electronics']
        return f"📱 **Electronics Category** ({len(electronics)} products):\n\n" + \
               "\n".join([f"- {row['Product_Name']}: Cost BND ${row['Unit_Cost_BND']}, Sells BND ${row['Selling_Price_BND']}" 
                         for _, row in electronics.iterrows()])
    
    # Groceries category
    elif any(word in prompt_lower for word in ['groceries', 'rice', 'cooking oil', 'sugar']):
        groceries = products[products['Category'] == 'Groceries']
        return f"🍚 **Groceries Category** ({len(groceries)} products):\n\n" + \
               "\n".join([f"- {row['Product_Name']}: Cost BND ${row['Unit_Cost_BND']}, Sells BND ${row['Selling_Price_BND']}" 
                         for _, row in groceries.iterrows()])
    
    # Visionify AI
    elif any(word in prompt_lower for word in ['visionify', 'ai', 'camera', 'computer vision']):
        return """
        🤖 **Visionify AI Integration**
        
        Visionify provides computer vision solutions that integrate with your existing CCTV systems across all 5 Brunei locations:
        
        **Key Features:**
        - 📦 **Automated Inventory Counting**: Cameras automatically count stock on shelves
        - 👷 **Safety Monitoring**: Detects PPE compliance (hard hats, vests, safety shoes)
        - 🚨 **Theft Prevention**: Anomaly detection for unauthorized access
        - 📊 **Real-time Analytics**: Heat maps of customer movement in stores
        - 🔔 **Instant Alerts**: Mobile notifications for low stock or safety violations
        
        **ROI for Your Business:**
        - 60% reduction in manual stock-taking time
        - 40% improvement in inventory accuracy
        - 24/7 monitoring without human fatigue
        - Works with existing Hikvision/Dahua CCTV systems
        
        **Locations Monitored:**
        - Warehouse A - Beribi (4 cameras)
        - Store 1 - Gadong (2 cameras)
        - Store 2 - Kiulap (2 cameras)
        - Store 3 - Kuala Belait (2 cameras)
        - Store 4 - Tutong (2 cameras)
        """
    
    # Brunei logistics
    elif any(word in prompt_lower for word in ['brunei', 'logistics', 'shipping', 'import']):
        return """
        🇧🇳 **Brunei Darussalam Logistics Information**
        
        **Your Distribution Network:**
        - Warehouse A - Beribi (Main distribution center)
        - Store 1 - Gadong (High-traffic retail)
        - Store 2 - Kiulap (Commercial district)
        - Store 3 - Kuala Belait (West Brunei)
        - Store 4 - Tutong (Central Brunei)
        
        **Local Suppliers in Your Network:**
        - Hua Ho Trading (KG Kiulap) - Cash on Delivery
        - Soon Lee MegaMart (Gadong) - Cash on Delivery
        - Supasave (Serusop) - Net 45
        - Seng Huat (Kuala Belait) - Cash on Delivery
        - And 6 more suppliers across Brunei
        
        **Key Logistics Considerations:**
        - No GST in Brunei (0% sales tax)
        - Main ports: Muara Port for sea freight
        - Well-connected highway system between districts
        - All major suppliers located within 100km radius
        """
    
    # Help/Default
    else:
        return """
        🤖 **I'm your Brunei Inventory AI Assistant!** I can help you with:
        
        📊 **Inventory Queries:**
        - "What's my total inventory value?" → BND $4.65M+
        - "How many products do I have?" → 50 products, 10 categories
        - "Which locations do I have?" → 5 locations across Brunei
        
        📦 **Product Information:**
        - Ask about any category: Electronics, Groceries, Hardware, Pharmaceuticals, etc.
        - "Tell me about electronics" → Lists all 5 electronic products
        
        🏢 **Supplier Information:**
        - "Who are my suppliers?" → Lists all 10 Brunei suppliers with contacts
        
        📋 **Purchase Orders:**
        - "How many pending orders?" → 26 pending POs
        
        ⚠️ **Stock Alerts:**
        - "What needs reordering?" → Shows low stock items
        
        🤖 **Visionify AI:**
        - "How does Visionify work?" → Explains computer vision integration
        
        🇧🇳 **Brunei Logistics:**
        - "Tell me about Brunei logistics" → Local market information
        
        What would you like to know about your inventory system?
        """

if __name__ == "__main__":
    main()
