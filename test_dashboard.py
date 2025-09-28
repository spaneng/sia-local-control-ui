#!/usr/bin/env python3
"""
Test script for SIA Local Control Dashboard
This script can be used to test the dashboard independently of the main application.
"""

import time
import threading
import random
from src.sia_local_control_ui.dashboard import SiaDashboard, DashboardInterface

def test_dashboard():
    """Test the dashboard with simulated data."""
    print("Starting SIA Local Control Dashboard Test...")
    
    # Create dashboard instance
    dashboard = SiaDashboard(host="127.0.0.1", port=8091, debug=False)
    dashboard_interface = DashboardInterface(dashboard)
    
    # Start dashboard in background thread
    dashboard_interface.start_dashboard()
    
    print("Dashboard started on http://127.0.0.1:8091")
    print("Press Ctrl+C to stop the test")
    
    try:
        # Simulate data updates
        while True:
            # Generate realistic test data
            pump_data = {
                'target_rate': 15.0 + random.uniform(-2.0, 2.0),
                'flow_rate': 14.5 + random.uniform(-1.5, 1.5),
                'pump_state': random.choice(['standby', 'auto', 'calibration'])
            }
            
            solar_data = {
                'battery_voltage': 24.0 + random.uniform(-2.0, 2.0),
                'battery_percentage': 75.0 + random.uniform(-15.0, 15.0),
                'array_voltage': 28.0 + random.uniform(-3.0, 3.0),
                'battery_ah': 100.0 + random.uniform(-20.0, 20.0)
            }
            
            tank_data = {
                'tank_level_mm': 1000.0 + random.uniform(-300.0, 300.0),
                'tank_level_percent': 50.0 + random.uniform(-20.0, 20.0)
            }
            
            # Update dashboard data
            dashboard_interface.update_pump_data(**pump_data)
            dashboard_interface.update_solar_data(**solar_data)
            dashboard_interface.update_tank_data(**tank_data)
            dashboard_interface.update_system_status('running')
            
            print(f"Updated dashboard data: Pump={pump_data['pump_state']}, "
                  f"Battery={solar_data['battery_percentage']:.1f}%, "
                  f"Tank={tank_data['tank_level_percent']:.1f}%")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\nStopping dashboard test...")
        dashboard_interface.stop_dashboard()
        print("Dashboard stopped.")

if __name__ == "__main__":
    test_dashboard()
