import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Brunei-specific categories and suppliers
brunei_categories = [
    'Electronics', 'Groceries', 'Hardware', 'Pharmaceuticals',
    'Automotive', 'Textiles', 'Furniture', 'Stationery',
    'Beverages', 'Cosmetics'
]

brunei_suppliers = [
    {'name': 'Hua Ho Trading', 'contact': 'Lim Ah Seng', 'phone': '673-2223456', 
     'email': 'purchasing@huaho.com.bn', 'address': 'KG Kiulap, Bandar Seri Begawan'},
    {'name': 'Soon Lee MegaMart', 'contact': 'Tan Mei Ling', 'phone': '673-2337890', 
     'email': 'orders@soonlee.com.bn', 'address': 'Gadong Central, BSB'},
    {'name': 'Supasave', 'contact': 'David Wong', 'phone': '673-2456789', 
     'email': 'procurement@supasave.com.bn', 'address': 'Serusop, BSB'},
    {'name': 'Seng Huat', 'contact': 'Michael Chen', 'phone': '673-2771234', 
     'email': 'sales@senghuat.com.bn', 'address': 'Kuala Belait'},
    {'name': 'SKH Group', 'contact': 'Steven Khoo', 'phone': '673-2667890', 
     'email': 'trading@skh.com.bn', 'address': 'Tutong Town'},
    {'name': 'Wee Hua Enterprise', 'contact': 'Jason Wee', 'phone': '673-2884567', 
     'email': 'orders@weehua.com.bn', 'address': 'Seria'},
    {'name': 'Pohan Motors', 'contact': 'Ahmad Pohan', 'phone': '673-2334455', 
     'email': 'parts@pohan.com.bn', 'address': 'Beribi Industrial Park'},
    {'name': 'D’Sunlit Supermarket', 'contact': 'Hjh Zainab', 'phone': '673-2656789', 
     'email': 'procurement@dsunlit.com.bn', 'address': 'Menglait, BSB'},
    {'name': 'Joyful Mart', 'contact': 'Liew KF', 'phone': '673-2781234', 
     'email': 'supply@joyfulmart.com.bn', 'address': 'Kiarong'},
    {'name': 'Al-Falah Corporation', 'contact': 'Hj Osman', 'phone': '673-2235678', 
     'email': 'trading@alfalah.com.bn', 'address': 'Lambak Kanan'}
]

# Locations (Brunei-based)
locations = ['Warehouse A - Beribi', 'Store 1 - Gadong', 'Store 2 - Kiulap', 
             'Store 3 - Kuala Belait', 'Store 4 - Tutong']

def generate_product_master(num_products=50):
    """Generate Product Master List with Brunei-relevant products"""
    
    products = []
    categories_with_products = {
        'Electronics': ['LED TV', 'Smartphone', 'Laptop', 'Tablet', 'Bluetooth Speaker', 
                       'Power Bank', 'HDMI Cable', 'USB Flash Drive', 'Wireless Mouse', 'Router'],
        'Groceries': ['Basmati Rice 5kg', 'Cooking Oil 2L', 'Sugar 1kg', 'Flour 1kg', 
                     'Instant Noodles', 'Canned Sardines', 'Soy Sauce', 'Coffee Powder', 'Tea Bags', 'Biscuits'],
        'Hardware': ['Paint 5L', 'Cement 40kg', 'PVC Pipe', 'Electrical Wire', 'Light Bulb', 
                    'Door Lock', 'Hammer', 'Screwdriver Set', 'Drill Bit', 'Sandpaper'],
        'Pharmaceuticals': ['Paracetamol', 'Cough Syrup', 'Antihistamine', 'Vitamin C', 
                           'First Aid Kit', 'Bandages', 'Antiseptic', 'Eye Drops', 'Pain Relief Gel', 'Thermometer'],
        'Automotive': ['Engine Oil', 'Car Battery', 'Air Filter', 'Brake Pad', 'Spark Plug', 
                      'Windshield Wiper', 'Coolant', 'Transmission Fluid', 'Tire', 'Car Wax'],
        'Textiles': ['School Uniform', 'Baju Kurung', 'Baju Melayu', 'Songkok', 'Tudung', 
                    'Office Shirt', 'Pants', 'T-Shirt', 'Towel', 'Bed Sheet'],
        'Furniture': ['Office Desk', 'Ergonomic Chair', 'Filing Cabinet', 'Bookshelf', 
                     'Meeting Table', 'Reception Sofa', 'Coffee Table', 'Wardrobe', 'Bed Frame', 'Dining Set'],
        'Stationery': ['A4 Paper', 'Printer Ink', 'Ballpoint Pen', 'Notebook', 'Folder', 
                      'Stapler', 'Paper Clip', 'Highlighters', 'Calculator', 'Whiteboard Marker'],
        'Beverages': ['Mineral Water', 'Soft Drinks', 'Orange Juice', 'Energy Drink', 
                     'Milk', 'Yogurt Drink', 'Teh Tarik 3-in-1', 'Kopi-O', 'Chocolate Drink', 'Soy Milk'],
        'Cosmetics': ['Facial Cleanser', 'Moisturizer', 'Lipstick', 'Foundation', 
                     'Shampoo', 'Conditioner', 'Body Lotion', 'Perfume', 'Nail Polish', 'Makeup Remover']
    }
    
    product_id = 1
    for category, product_names in categories_with_products.items():
        for i, name in enumerate(product_names[:5]):  # Take first 5 from each category
            # Generate realistic Brunei prices in BND
            if category == 'Electronics':
                unit_cost = random.randint(50, 2000)
            elif category in ['Groceries', 'Beverages']:
                unit_cost = random.randint(2, 50)
            elif category == 'Automotive':
                unit_cost = random.randint(15, 300)
            else:
                unit_cost = random.randint(5, 150)
            
            selling_price = unit_cost * random.uniform(1.2, 1.5)
            
            product = {
                'Product_ID': f'PRD{product_id:05d}',
                'SKU': f'{category[:3].upper()}{random.randint(1000,9999)}',
                'Barcode': f'888{random.randint(1000000,9999999)}',
                'Product_Name': name,
                'Category': category,
                'Unit_Cost_BND': round(unit_cost, 2),
                'Selling_Price_BND': round(selling_price, 2),
                'Reorder_Level': random.randint(5, 50),
                'Preferred_Supplier': random.choice([s['name'] for s in brunei_suppliers]),
                'Status': random.choices(['Active', 'Discontinued'], weights=[0.95, 0.05])[0]
            }
            products.append(product)
            product_id += 1
    
    return pd.DataFrame(products)

def generate_inventory_by_location(product_master):
    """Generate inventory data for multiple locations"""
    
    inventory = []
    
    for _, product in product_master.iterrows():
        for location in locations:
            # Random quantity between 0 and 200
            quantity = random.randint(0, 200)
            
            # Random last updated date within last 30 days
            last_updated = datetime.now() - timedelta(days=random.randint(0, 30))
            
            inventory.append({
                'Product_ID': product['Product_ID'],
                'Location': location,
                'Quantity_On_Hand': quantity,
                'Last_Updated': last_updated.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return pd.DataFrame(inventory)

def generate_stock_transactions(product_master, num_transactions=100):
    """Generate transaction history"""
    
    transaction_types = ['STOCK IN', 'STOCK OUT', 'ADJUSTMENT']
    reasons = {
        'STOCK IN': ['Purchase Order', 'Return from Customer', 'Transfer from Warehouse'],
        'STOCK OUT': ['Sale', 'Damaged', 'Expired', 'Transfer to Store'],
        'ADJUSTMENT': ['Inventory Count', 'System Correction', 'Sample/Display']
    }
    
    transactions = []
    
    for i in range(num_transactions):
        product = product_master.sample(1).iloc[0]
        trans_type = random.choice(transaction_types)
        
        if trans_type == 'STOCK IN':
            quantity_change = random.randint(10, 100)
        elif trans_type == 'STOCK OUT':
            quantity_change = -random.randint(1, 20)
        else:  # ADJUSTMENT
            quantity_change = random.randint(-10, 10)
        
        # Ensure quantity change is not zero for adjustments
        if quantity_change == 0:
            quantity_change = random.choice([-5, 5])
        
        transaction_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        transactions.append({
            'Transaction_ID': f'TRX{datetime.now().strftime("%Y%m")}{i:04d}',
            'Date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Product_ID': product['Product_ID'],
            'Product_Name': product['Product_Name'],
            'Transaction_Type': trans_type,
            'Quantity_Change': quantity_change,
            'Location': random.choice(locations),
            'Reference_Number': f'REF{random.randint(1000,9999)}',
            'Remarks': random.choice(reasons[trans_type]),
            'User': random.choice(['admin', 'cashier1', 'manager', 'stock_clerk'])
        })
    
    return pd.DataFrame(transactions)

def generate_supplier_data():
    """Create supplier management data"""
    suppliers = []
    for i, supplier in enumerate(brunei_suppliers, 1):
        suppliers.append({
            'Supplier_ID': f'SUP{i:03d}',
            'Supplier_Name': supplier['name'],
            'Contact_Person': supplier['contact'],
            'Phone': supplier['phone'],
            'Email': supplier['email'],
            'Address': supplier['address'],
            'Payment_Terms': random.choice(['Net 30', 'Net 45', 'Cash on Delivery']),
            'Category': random.choice(['General', 'Electronics', 'Groceries', 'All'])
        })
    return pd.DataFrame(suppliers)

def generate_purchase_orders(product_master, suppliers_df, num_pos=30):
    """Generate purchase order data"""
    
    statuses = ['Draft', 'Sent', 'Confirmed', 'Shipped', 'Received', 'Cancelled']
    
    pos = []
    for i in range(num_pos):
        supplier = suppliers_df.sample(1).iloc[0]
        product = product_master.sample(1).iloc[0]
        quantity = random.randint(20, 500)
        
        po_date = datetime.now() - timedelta(days=random.randint(0, 60))
        expected_date = po_date + timedelta(days=random.randint(3, 14))
        
        pos.append({
            'PO_Number': f'PO{datetime.now().strftime("%Y%m")}{i:04d}',
            'Supplier_ID': supplier['Supplier_ID'],
            'Supplier_Name': supplier['Supplier_Name'],
            'Product_ID': product['Product_ID'],
            'Product_Name': product['Product_Name'],
            'Ordered_Quantity': quantity,
            'Received_Quantity': random.randint(0, quantity),
            'Unit_Cost_BND': product['Unit_Cost_BND'],
            'Total_Cost_BND': quantity * product['Unit_Cost_BND'],
            'Order_Date': po_date.strftime('%Y-%m-%d'),
            'Expected_Date': expected_date.strftime('%Y-%m-%d'),
            'Order_Status': random.choices(statuses, weights=[0.1, 0.2, 0.2, 0.2, 0.2, 0.1])[0],
            'Payment_Status': random.choice(['Pending', 'Partial', 'Paid'])
        })
    
    return pd.DataFrame(pos)

def generate_stock_alerts(product_master, inventory_df):
    """Generate stock alert monitoring data"""
    
    alerts = []
    
    # Get current stock levels
    current_stock = inventory_df.groupby('Product_ID')['Quantity_On_Hand'].sum().reset_index()
    
    for _, product in product_master.iterrows():
        stock_row = current_stock[current_stock['Product_ID'] == product['Product_ID']]
        current_qty = stock_row['Quantity_On_Hand'].values[0] if not stock_row.empty else 0
        
        alert_status = 'Normal'
        if current_qty <= 0:
            alert_status = 'Out of Stock'
        elif current_qty <= product['Reorder_Level']:
            alert_status = 'Low Stock - Reorder'
        
        alerts.append({
            'Product_ID': product['Product_ID'],
            'Product_Name': product['Product_Name'],
            'Category': product['Category'],
            'Current_Stock': current_qty,
            'Reorder_Level': product['Reorder_Level'],
            'Alert_Status': alert_status,
            'Location_Breakdown': ', '.join([f"{loc}: {qty}" for loc, qty in 
                                            inventory_df[inventory_df['Product_ID'] == product['Product_ID']]
                                            .groupby('Location')['Quantity_On_Hand'].sum().items()])
        })
    
    return pd.DataFrame(alerts)

# Generate all data
def generate_all_data():
    """Generate all inventory data"""
    
    print("Generating Product Master List...")
    product_master = generate_product_master(50)
    
    print("Generating Inventory by Location...")
    inventory = generate_inventory_by_location(product_master)
    
    print("Generating Stock Transactions...")
    transactions = generate_stock_transactions(product_master, 150)
    
    print("Generating Supplier Data...")
    suppliers = generate_supplier_data()
    
    print("Generating Purchase Orders...")
    pos = generate_purchase_orders(product_master, suppliers, 40)
    
    print("Generating Stock Alerts...")
    alerts = generate_stock_alerts(product_master, inventory)
    
    # Save to Excel with multiple sheets
    with pd.ExcelWriter('/content/drive/MyDrive/brunei_inventory_system.xlsx', engine='openpyxl') as writer:
        product_master.to_excel(writer, sheet_name='Product Master List', index=False)
        inventory.to_excel(writer, sheet_name='Inventory by Location', index=False)
        transactions.to_excel(writer, sheet_name='Stock Transactions', index=False)
        suppliers.to_excel(writer, sheet_name='Supplier Management', index=False)
        pos.to_excel(writer, sheet_name='Purchase Orders', index=False)
        alerts.to_excel(writer, sheet_name='Stock Alert Monitoring', index=False)
    
    print("Data generation complete! File saved to Google Drive.")
    return {
        'product_master': product_master,
        'inventory': inventory,
        'transactions': transactions,
        'suppliers': suppliers,
        'pos': pos,
        'alerts': alerts
    }

# Run the generator
if __name__ == "__main__":
    data = generate_all_data()
