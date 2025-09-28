import logging
import time

from pydoover.docker import Application
from pydoover import ui

from .app_config import SiaLocalControlUiConfig
from .dashboard import SiaDashboard, DashboardInterface

log = logging.getLogger()

class SiaLocalControlUiApplication(Application):
    config: SiaLocalControlUiConfig  # not necessary, but helps your IDE provide autocomplete!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.started: float = time.time()
        
        # Initialize dashboard
        self.dashboard = SiaDashboard(host="0.0.0.0", port=8091, debug=False)
        self.dashboard_interface = DashboardInterface(self.dashboard)

    async def setup(self):
        self.loop_target_period = 0.2
        
        # Start dashboard
        self.dashboard_interface.start_dashboard()
        log.info("Dashboard started on port 8091")

    async def main_loop(self):
        
        self.get_tag("flow_rate", self.config.flow_sensor_app.value)
        self.get_tag("pressure", self.config.pressure_sensor_app.value)
        self.get_tag("tank_level", self.config.tank_level_app.value)
        # a random value we set inside our simulator. Go check it out in simulators/sample!
        # Update dashboard with example data
        await self.update_dashboard_data()
    
    async def update_dashboard_data(self):
        """Update dashboard with data from various sources."""
        try:
            # Get pump control data from simulators
            target_rate = self.get_tag("TargetRate", self.config.pump_controllers.elements[0]) if self.config.pump_controllers else 15.5
            flow_rate = self.get_tag("FlowRate", self.config.pump_controllers.elements[0]) if self.config.pump_controllers else 14.2
            pump_state = self.get_tag("StateString", self.config.pump_controllers.elements[0]) if self.config.pump_controllers else "auto"
            
            # Update pump data
            self.dashboard_interface.update_pump_data(
                target_rate=target_rate,
                flow_rate=flow_rate,
                pump_state=pump_state
            )
            
            # Get pump 2 control data from simulators
            if len(self.config.pump_controllers.elements) > 1:
                pump2_target_rate = self.get_tag("TargetRate", self.config.pump_controllers.elements[1])
                pump2_flow_rate = self.get_tag("FlowRate", self.config.pump_controllers.elements[1])
                pump2_pump_state = self.get_tag("StateString", self.config.pump_controllers.elements[1])
            else:
                # Fallback values for pump 2 if not configured
                pump2_target_rate = "-"
                pump2_flow_rate = "-"
                pump2_pump_state = "-"
            
            # Update pump 2 data
            self.dashboard_interface.update_pump2_data(
                target_rate=pump2_target_rate,
                flow_rate=pump2_flow_rate,
                pump_state=pump2_pump_state
            )
            
            # Get and aggregate solar control data from all simulators
            if self.config.solar_controllers:
                battery_voltages = []
                battery_percentages = []
                panel_power_values = []
                battery_ah_values = []
                
                # Collect data from all solar controllers
                for solar_controller in self.config.solar_controllers.elements:
                    battery_voltages.append(self.get_tag("b_voltage", solar_controller))
                    battery_percentages.append(self.get_tag("b_percent", solar_controller))
                    panel_power_values.append(self.get_tag("panel_power", solar_controller))
                    battery_ah_values.append(self.get_tag("remaining_ah", solar_controller))
                
                # Aggregate data: average voltages/percentages, sum battery_ah
                battery_voltage = sum(battery_voltages) / len(battery_voltages)
                battery_percentage = sum(battery_percentages) / len(battery_percentages)
                panel_power = sum(panel_power_values) / len(panel_power_values)
                battery_ah = sum(battery_ah_values)
            else:
                # Fallback values if no solar controllers configured
                battery_voltage = 24.5
                battery_percentage = 78.0
                panel_power = 150.0
                battery_ah = 120.0
            
            # Update solar data
            self.dashboard_interface.update_solar_data(
                battery_voltage=battery_voltage,
                battery_percentage=battery_percentage,
                array_voltage=panel_power,
                battery_ah=battery_ah
            )
            
            # Get tank control data from simulators
            tank_level_mm = self.get_tag("tank_level_mm", self.config.tank_level_app.value) if self.config.tank_apps else 1250.0
            tank_level_percent = self.get_tag("tank_level_percent", self.config.tank_level_app.value) if self.config.tank_apps else 62.5
            
            # Update tank data
            self.dashboard_interface.update_tank_data(
                tank_level_mm=tank_level_mm,
                tank_level_percent=tank_level_percent
            )
            
            # Update system status
            system_status = "running" if self.state.state == "on" else "standby"
            self.dashboard_interface.update_system_status(system_status)
            
        except Exception as e:
            log.error(f"Error updating dashboard data: {e}")
            # Use fallback data if simulators are not available
            self.update_dashboard_with_fallback_data()
    
    def update_dashboard_with_fallback_data(self):
        """Update dashboard with fallback data when simulators are not available."""
        import random
        
        # Generate realistic fallback data
        target_rate = 15.0 + random.uniform(-2.0, 2.0)
        flow_rate = target_rate + random.uniform(-1.0, 1.0)
        pump_state = random.choice(["standby", "auto", "calibration"])
        
        self.dashboard_interface.update_pump_data(
            target_rate=target_rate,
            flow_rate=flow_rate,
            pump_state=pump_state
        )
        
        # Generate pump 2 fallback data
        pump2_target_rate = 12.0 + random.uniform(-1.5, 1.5)
        pump2_flow_rate = pump2_target_rate + random.uniform(-0.8, 0.8)
        pump2_pump_state = random.choice(["standby", "auto", "calibration"])
        
        self.dashboard_interface.update_pump2_data(
            target_rate=pump2_target_rate,
            flow_rate=pump2_flow_rate,
            pump_state=pump2_pump_state
        )
        
        # Generate realistic fallback solar data (simulating aggregated values)
        battery_voltage = 24.0 + random.uniform(-2.0, 2.0)
        battery_percentage = 75.0 + random.uniform(-10.0, 10.0)
        panel_power = 150.0 + random.uniform(-30.0, 30.0)
        battery_ah = 120.0 + random.uniform(-20.0, 20.0)
        
        self.dashboard_interface.update_solar_data(
            battery_voltage=battery_voltage,
            battery_percentage=battery_percentage,
            array_voltage=panel_power,
            battery_ah=battery_ah
        )
        
        tank_level_mm = 1000.0 + random.uniform(-200.0, 200.0)
        tank_level_percent = (tank_level_mm / 2000.0) * 100
        
        self.dashboard_interface.update_tank_data(
            tank_level_mm=tank_level_mm,
            tank_level_percent=tank_level_percent
        )
        
        system_status = "running" if self.state.state == "on" else "standby"
        self.dashboard_interface.update_system_status(system_status)
