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
    Load data from Excel file structure
    Based on Product_Master_List.xlsx with 50 products, 5 locations, 10 suppliers
    """
    
    # Product Master List (50 products) - Based on your actual Excel data
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
    
    # Sample quantities based on your Excel data patterns
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
    
    # Generate inventory for all 50 products
    for i, prod in enumerate(products['Product_ID']):
        for j, loc in enumerate(locations):
            if prod in base_quantities:
                qty = base_quantities[prod][j]
            else:
                # Generate realistic quantities for other products
                qty = 50 + ((i + j) * 17) % 150
            
            inventory_data.append({
                'Product_ID': prod,
                'Location': loc,
                'Quantity_On_Hand': qty,
                'Last_Updated': '2026-02-20'
            })
    
    inventory = pd.DataFrame(inventory_data)
    
    # Stock Transactions (150 records)
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
            'Date': pd.Timestamp('2025-11-01') + pd.Timedelta(days=i),
            'Product_ID': products_data[prod_idx][0],
            'Product_Name': products_data[prod_idx][3],
            'Transaction_Type': txn_type,
            'Quantity_Change': qty,
            'Location': locations[loc_idx],
            'Reference_Number': f'REF{1000+i}',
            'Remarks': remarks_options[i % 9]
        })
    
    transactions = pd.DataFrame(transactions_data)
    
    # Supplier Management (10 suppliers)
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
    
    # Purchase Orders (40 POs)
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
            'Order_Date': pd.Timestamp('2025-12-01') + pd.Timedelta(days=i*3),
            'Expected_Date': pd.Timestamp('2025-12-10') + pd.Timedelta(days=i*3),
            'Order_Status': po_status[i]
        })
    
    purchase_orders = pd.DataFrame(purchase_orders_data)
    
    # Stock Alert Monitoring (50 alerts)
    current_stock = [
        817, 465, 574, 614, 573, 355, 460, 388, 640, 724,
        470, 400, 212, 644, 371, 838, 670, 565, 302, 392,
        394, 391, 540, 536, 578, 465, 432, 412, 616, 594,
        303, 614, 354, 519, 322, 501, 408, 542, 492, 578,
        505, 221, 635, 372, 574, 410, 366, 641, 343, 444
    ]
    
    alerts_data = []
    for i, prod in enumerate(products_data):
        status = '🟢 NORMAL' if current_stock[i] > prod[7] else ('🟡 WARNING' if current_stock[i] > prod[7] * 0.5 else '🔴 CRITICAL')
        
        alerts_data.append({
            'Product_ID': prod[0],
            'Product_Name': prod[3],
            'Category': prod[4],
            'Current_Stock': current_stock[i],
            'Reorder_Level': prod[7],
            'Alert_Status': status
        })
    
    alerts = pd.DataFrame(alerts_data)
    
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
            # FIXED: Using a simple list of colors instead of color sequence
            fig = px.pie(values=category_data.values, names=category_data.index)
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
            # FIXED: Using a simple list of colors instead of color sequence
            fig = px.pie(values=po_status.values, names=po_status.index)
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
        # FIXED: Removed color sequence parameter
        fig = px.pie(values=txn_dist.values, names=txn_dist.index, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "🚚 Purchase Orders (40 POs)":
        st.title("Purchase Order Management")
        
        # Status overview
        status_counts = purchase_orders['Order_Status'].value_counts()
        cols = st.columns(min(len(status_counts), 6))
        for i, (status, count) in enumerate(status_counts.items()):
            with cols[i % len(cols)]:
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
                    title="Total PO Value by Supplier", color='Total_Cost_BND',
                    color_continuous_scale='Viridis')
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
        
        # FIXED: Removed color_discrete_sequence parameter
        fig = px.scatter(supplier_activity, x='Order_Count', y='Total_Spend_BND',
                        size='Total_Units', text='Supplier_Name', 
                        title="Supplier Performance Matrix")
        st.plotly_chart(fig, use_container_width=True)
        
        # Payment terms distribution
        st.subheader("💳 Payment Terms Distribution")
        payment_terms = suppliers['Payment_Terms'].value_counts()
        # FIXED: Removed color sequence parameter
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
            
            # FIXED: Removed color_discrete_sequence parameter
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
