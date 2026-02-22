"""
Visionify AI Integration Module
Computer Vision Solutions for Brunei Warehouse Management
"""

import cv2
import numpy as np
from datetime import datetime
import pandas as pd

class VisionifyWarehouseAI:
    """
    Visionify AI for Brunei Inventory System
    Monitors 5 locations: Warehouse A - Beribi, Store 1-4
    """
    
    def __init__(self):
        self.locations = {
            'Warehouse A - Beribi': {'cameras': 4, 'zones': ['A', 'B', 'C', 'D']},
            'Store 1 - Gadong': {'cameras': 2, 'zones': ['Floor', 'Storage']},
            'Store 2 - Kiulap': {'cameras': 2, 'zones': ['Floor', 'Storage']},
            'Store 3 - Kuala Belait': {'cameras': 2, 'zones': ['Floor', 'Storage']},
            'Store 4 - Tutong': {'cameras': 2, 'zones': ['Floor', 'Storage']}
        }
        self.detection_log = []
        
    def detect_products(self, frame, location):
        """
        Detect and count products using computer vision
        Returns: product counts, confidence scores
        """
        # Simulated detection - production uses YOLOv8
        products_detected = {
            'LED TV': np.random.randint(0, 10),
            'Smartphone': np.random.randint(0, 15),
            'Laptop': np.random.randint(0, 8),
            'Rice_Bags': np.random.randint(20, 100),
            'Oil_Cans': np.random.randint(10, 50)
        }
        
        detection = {
            'timestamp': datetime.now(),
            'location': location,
            'products': products_detected,
            'confidence': np.random.uniform(0.85, 0.99),
            'total_items': sum(products_detected.values())
        }
        self.detection_log.append(detection)
        return detection
    
    def detect_personnel(self, frame, location):
        """
        Detect personnel and check PPE compliance
        """
        personnel_count = np.random.randint(0, 8)
        ppe_compliance = {
            'hard_hats': np.random.randint(personnel_count),
            'safety_vests': np.random.randint(personnel_count),
            'safety_shoes': np.random.randint(personnel_count)
        }
        
        return {
            'location': location,
            'personnel_count': personnel_count,
            'ppe_compliance': ppe_compliance,
            'compliance_rate': sum(ppe_compliance.values()) / (personnel_count * 3) if personnel_count > 0 else 1.0,
            'alerts': [] if sum(ppe_compliance.values()) == personnel_count * 3 else ['PPE_VIOLATION']
        }
    
    def detect_shelf_empty(self, frame, shelf_id):
        """
        Detect empty shelves for restocking alerts
        """
        occupancy = np.random.uniform(0, 1)
        return {
            'shelf_id': shelf_id,
            'occupancy_rate': occupancy,
            'empty_slots': int((1 - occupancy) * 20),
            'recommendation': 'RESTOCK_NOW' if occupancy < 0.3 else 'MONITOR' if occupancy < 0.6 else 'ADEQUATE'
        }
    
    def generate_hourly_report(self, location):
        """
        Generate hourly activity report
        """
        if not self.detection_log:
            return "No data collected"
        
        df = pd.DataFrame(self.detection_log)
        loc_data = df[df['location'] == location]
        
        if loc_data.empty:
            return f"No data for {location}"
        
        report = {
            'location': location,
            'total_detections': len(loc_data),
            'avg_confidence': loc_data['confidence'].mean(),
            'peak_hour': loc_data['timestamp'].dt.hour.mode()[0] if not loc_data.empty else None,
            'total_items_counted': sum([d['total_items'] for d in loc_data['products']]) if 'products' in loc_data else 0
        }
        return report

# Integration with inventory system
def sync_visionify_with_inventory(inventory_system, visionify_ai, location):
    """
    Sync Visionify AI detections with inventory database
    """
    detection = visionify_ai.detect_products(None, location)
    
    # Compare with database
    discrepancies = []
    for product, detected_qty in detection['products'].items():
        # Find in database
        db_qty = inventory_system.inventory[
            (inventory_system.inventory['Location'] == location) &
            (inventory_system.inventory['Product_ID'].str.contains(product[:3].upper()))
        ]['Quantity_On_Hand'].sum()
        
        if abs(detected_qty - db_qty) > 5:  # 5 unit tolerance
            discrepancies.append({
                'product': product,
                'detected': detected_qty,
                'database': db_qty,
                'variance': detected_qty - db_qty
            })
    
    return {
        'location': location,
        'timestamp': detection['timestamp'],
        'discrepancies': discrepancies,
        'accuracy': 1 - (len(discrepancies) / len(detection['products'])) if detection['products'] else 1.0
    }

if __name__ == "__main__":
    # Test Visionify AI
    vision = VisionifyWarehouseAI()
    print("Visionify AI Warehouse System Initialized")
    print(f"Monitoring {len(vision.locations)} locations across Brunei")
    
    # Simulate detection
    result = vision.detect_products(None, 'Warehouse A - Beribi')
    print(f"\nDetected {result['total_items']} items with {result['confidence']:.2%} confidence")
