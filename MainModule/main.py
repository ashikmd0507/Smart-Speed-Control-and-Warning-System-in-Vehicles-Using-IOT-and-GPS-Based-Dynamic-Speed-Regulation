"""
================================================================================
SMART SPEED CONTROL SYSTEM - IoT CYBER-PHYSICAL SIMULATION
================================================================================

PROJECT: Smart Speed Control System with 3D Simulation and MQTT Integration
VERSION: 1.0
DATE: 2026

CYBER-PHYSICAL ARCHITECTURE:
============================
This system implements a complete cyber-physical smart speed control solution
with four distinct layers:

Layer 1 - 3D SIMULATION ENGINE (Game Layer)
    - Panda3D-based 3D graphics engine
    - Real-time vehicle physics simulation
    - Third-person camera system
    - Colored road zones representing different speed limits
    - Arrow key controls for vehicle operation

Layer 2 - SPEED MONITORING & REGULATION ENGINE
    - Continuous vehicle speed monitoring
    - Speed limit detection based on GPS position
    - Smart state management (NORMAL/WARNING/REGULATING)
    - Automatic acceleration regulation for overspeed
    - Non-blocking warning audio alerts

Layer 3 - MQTT IoT COMMUNICATION LAYER
    - Real-time telemetry publishing to HiveMQ broker
    - Topics: location, speed, state (500ms interval)
    - Automatic reconnection and clean session handling
    - Status monitoring on HUD

Layer 4 - ESP32 FIRMWARE LAYER (Arduino)
    - IoT microcontroller integration
    - WiFi connectivity
    - MQTT subscription to vehicle state
    - LED control based on system state
    - See firmware/esp32_smart_speed.ino

DATA FLOW:
==========
1. User controls vehicle with arrow keys
2. Vehicle physics engine calculates motion
3. Current position determines zone and speed limit
4. Control engine monitors speed vs limit
5. System state determined (NORMAL/WARNING/REGULATING)
6. If over limit: acceleration is reduced proportionally
7. Telemetry published to MQTT topics (lat/lon, speed, state)
8. ESP32 receives state updates via MQTT
9. ESP32 controls LEDs based on system state
10. HUD displays real-time information on screen

MQTT TOPICS:
============
- vehicle/smart_speed/location  → {"lat": float, "lon": float}
- vehicle/smart_speed/speed     → {"speed": float, "limit": float}
- vehicle/smart_speed/state     → {"state": "NORMAL|WARNING|REGULATING"}

VEHICLE ZONES:
==============
- School Zone (X: -100 to 0)   → 50 km/h (Yellow)
- City Road (X: 0 to 100)       → 60 km/h (Gray)
- Highway (X: 100 to 300)       → 80 km/h (Dark Gray)

STATE COLORS:
=============
- GREEN (NORMAL)    → Speed ≤ limit
- YELLOW (WARNING)  → limit < speed ≤ limit + 5 km/h
- RED (REGULATING)  → Speed > limit + 5 km/h

HOW TO RUN:
===========
1. Install Python 3.8+
2. Install dependencies: pip install -r requirements.txt
3. Ensure HiveMQ MQTT broker running on 127.0.0.1:1883
4. Run: python main.py
5. Controls: UP/DOWN arrows for speed, LEFT/RIGHT for steering, R to reset

HOW TO INTEGRATE WITH WOKWI:
============================
1. Upload esp32_smart_speed.ino to an ESP32 microcontroller
2. Register ESP32 on Wokwi: https://wokwi.com/
3. Connect ESP32 via USB or WiFi
4. Configure WiFi SSID and password in firmware
5. Change MQTT_SERVER to your PC's IP address (or use broker.hivemq.com)
6. Watch LEDs blink based on vehicle state in real-time!

REQUIREMENTS:
=============
- Python 3.8+
- Panda3D 3D graphics engine
- paho-mqtt for MQTT communication
- HiveMQ MQTT broker or compatible MQTT server

FILES:
======
main.py                     - Main entry point and 3D engine
config.py                   - Centralized configuration
core/physics.py            - Vehicle physics simulation
core/zone_manager.py       - Speed zone management
core/vehicle.py            - Vehicle representation
core/control_engine.py     - Speed state control logic
core/mqtt_client.py        - MQTT IoT communication
ui/hud.py                  - On-screen HUD display
ui/audio_manager.py        - Sound effects management
firmware/esp32_smart_speed.ino - ESP32 Arduino firmware

AUTHOR: IoT Development Team
LICENSE: MIT
================================================================================
"""

import sys
import time
import config
from panda3d.core import Point3, Vec3, VBase4, AmbientLight, DirectionalLight
from panda3d.core import TextNode, LineSegs, CardMaker, Texture, WindowProperties
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

# Import project modules
from core.physics import VehiclePhysics
from core.vehicle import Vehicle
from core.zone_manager import ZoneManager
from core.control_engine import ControlEngine
from core.mqtt_client import SmartSpeedMQTTClient
from ui.hud import HUD
from ui.audio_manager import AudioManager


class SmartSpeedSimulation(ShowBase):
    """
    Main Smart Speed Control System simulation engine.
    Extends Panda3D ShowBase with custom simulation logic.
    """
    
    def __init__(self):
        """Initialize the Smart Speed Simulation."""
        ShowBase.__init__(self)
        
        print("\n" + "="*80)
        print("SMART SPEED CONTROL SYSTEM - Starting Simulation")
        print("="*80 + "\n")
        
        # Configuration - Set window properties
        props = WindowProperties()
        props.setTitle("Smart Speed Control System - IoT Simulation")
        props.setSize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        props.setOrigin(50, 50)  # Position window on screen
        self.win.requestProperties(props)
        
        # Ensure window is open and focused
        print("[Graphics] Waiting for window to initialize...")
        time.sleep(1)  # Give window time to open
        
        # Request focus
        props = WindowProperties()
        props.setForeground(True)
        self.win.requestProperties(props)
        
        # Initialize core systems
        self.physics_engine = VehiclePhysics()
        self.vehicle = Vehicle(self.physics_engine)
        self.zone_manager = ZoneManager()
        self.control_engine = ControlEngine()
        self.mqtt_client = SmartSpeedMQTTClient()
        self.audio_manager = AudioManager(self)
        self.hud = HUD(self)
        
        # Game state
        self.running = True
        self.last_mqtt_publish = 0
        self.fps_timer = 0
        
        # Vehicle input state
        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False
        
        # Initialize 3D environment
        self._setup_environment()
        
        # Set up input handling
        self._setup_input()
        
        # Register update task
        self.taskMgr.add(self._update_task, "SimulationUpdate")
        
        # Configure camera
        self._setup_camera()
        
        # Connect MQTT
        print("[Main] Connecting to MQTT broker...")
        self.mqtt_client.connect()
        
        # Register state change callback
        self.control_engine.add_state_callback(self._on_control_state_change)
        
        print("[Main] [+] Simulation initialized successfully!")
        print("[Main] [+] 3D Window should be visible on your screen")
        print("[Main] [+] Controls: UP/DOWN = Speed | LEFT/RIGHT = Steer | R = Reset")
        print("[Main] [+] Telemetry publishing to MQTT broker...\n")
    
    def _setup_environment(self):
        """Setup 3D environment with ground, zones, and lighting."""
        print("[Graphics] Setting up 3D environment...")
        
        # Clear default lighting and add custom lights
        self.render.clearLight()
        
        # Add ambient light
        alight = AmbientLight("ambient")
        alight.setColor(VBase4(0.6, 0.6, 0.6, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Add directional light (sun)
        dlight = DirectionalLight("sun")
        dlight.setColor(VBase4(1, 1, 1, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setP(-60)
        self.render.setLight(dlnp)
        
        # Create ground plane
        self._create_ground()
        
        # Create road zones
        self._create_zones()
        
        # Create vehicle
        self._create_vehicle()
    
    def _create_ground(self):
        """Create the ground plane."""
        cm = CardMaker("ground")
        cm.setFrame(-config.GROUND_SIZE/2, config.GROUND_SIZE/2,
                   -config.GROUND_SIZE/4, config.GROUND_SIZE/4)
        
        ground = self.render.attachNewNode(cm.generate())
        ground.setP(-90)
        ground.setColor(0.5, 0.5, 0.5, 1.0)
        
        print("[Graphics] Ground plane created")
    
    def _create_zones(self):
        """Create visual representations of speed zones."""
        zones_info = self.zone_manager.get_all_zones_info()
        
        for zone_info in zones_info:
            x_min, x_max = zone_info["position"]["x_range"]
            y_min, y_max = zone_info["position"]["y_range"]
            r, g, b = zone_info["color"]
            
            # Create zone rectangle
            cm = CardMaker(f"zone_{zone_info['id']}")
            width = x_max - x_min
            height = y_max - y_min
            cm.setFrame(0, width, 0, height)
            
            zone_node = self.render.attachNewNode(cm.generate())
            zone_node.setX(x_min)
            zone_node.setY(y_min)
            zone_node.setZ(0.01)  # Slightly above ground
            zone_node.setP(-90)
            zone_node.setColor(r, g, b, 0.3)  # Semi-transparent
            
            print(f"[Graphics] Zone '{zone_info['name']}' created at X:{x_min}-{x_max}")
    
    def _create_vehicle(self):
        """Create the vehicle as a simple cube."""
        cm = CardMaker("vehicle")
        cm.setFrame(-config.VEHICLE_SIZE/2, config.VEHICLE_SIZE/2,
                   -config.VEHICLE_SIZE/2, config.VEHICLE_SIZE/2)
        
        vehicle_model = self.render.attachNewNode(cm.generate())
        vehicle_model.setColor(0.0, 1.0, 1.0, 1.0)  # Cyan
        
        self.vehicle.set_3d_node(vehicle_model)
        print("[Graphics] Vehicle created and ready")
    
    def _setup_camera(self):
        """Setup third-person camera following vehicle."""
        self.camera.setPos(config.CAMERA_DISTANCE, 0, config.CAMERA_HEIGHT)
        self.camera.lookAt(0, 0, 0)
    
    def _setup_input(self):
        """Setup keyboard input handlers."""
        self.accept("arrow_up", self._key_pressed, ["up"])
        self.accept("arrow_up-up", self._key_released, ["up"])
        self.accept("arrow_down", self._key_pressed, ["down"])
        self.accept("arrow_down-up", self._key_released, ["down"])
        self.accept("arrow_left", self._key_pressed, ["left"])
        self.accept("arrow_left-up", self._key_released, ["left"])
        self.accept("arrow_right", self._key_pressed, ["right"])
        self.accept("arrow_right-up", self._key_released, ["right"])
        self.accept("r", self._reset_vehicle)
    
    def _key_pressed(self, key):
        """Handle key press."""
        if key == "up":
            self.key_up = True
        elif key == "down":
            self.key_down = True
        elif key == "left":
            self.key_left = True
        elif key == "right":
            self.key_right = True
    
    def _key_released(self, key):
        """Handle key release."""
        if key == "up":
            self.key_up = False
        elif key == "down":
            self.key_down = False
        elif key == "left":
            self.key_left = False
        elif key == "right":
            self.key_right = False
    
    def _reset_vehicle(self):
        """Reset vehicle to initial position."""
        self.vehicle.reset()
        print("[Main] Vehicle reset")
    
    def _update_task(self, task):
        """Main simulation update task (called every frame)."""
        try:
            dt = globalClock.getDt()  # Delta time since last frame
            
            # Calculate input values
            acceleration = 0.0
            steering = 0.0
            braking = False
            
            if self.key_up:
                acceleration = 1.0
            elif self.key_down:
                braking = True
            
            if self.key_left:
                steering = -1.0
            elif self.key_right:
                steering = 1.0
            
            # Update zone based on vehicle position
            x, y, z = self.vehicle.position
            self.zone_manager.update_position(x, y)
            speed_limit = self.zone_manager.get_speed_limit(x, y)
            
            # Get acceleration multiplier from control engine
            accel_multiplier = self.control_engine.get_acceleration_multiplier()
            
            # Update vehicle
            velocity, position = self.vehicle.update(
                dt, acceleration, steering, braking, accel_multiplier
            )
            
            # Update control engine
            self.control_engine.update(velocity, speed_limit)
            
            # Update control engine state
            control_state = self.control_engine.get_current_state()
            
            # Update 3D node position
            self.vehicle.update_3d_representation()
            
            # Update camera to follow vehicle
            self._update_camera()
            
            # Update HUD
            vehicle_state = {"position": position, "velocity": velocity}
            zone_info = self.zone_manager.get_current_state()
            mqtt_status = self.mqtt_client.get_status()
            
            self.hud.update(vehicle_state, zone_info, control_state, mqtt_status, dt)
            
            # Publish MQTT telemetry
            current_time = time.time()
            if current_time - self.last_mqtt_publish >= config.MQTT_PUBLISH_INTERVAL:
                self._publish_telemetry()
                self.last_mqtt_publish = current_time  # Update timestamp AFTER completed publishes
            
            return Task.cont
        
        except Exception as e:
            print(f"[Update] Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            return Task.cont  # Continue despite error
    
    def _update_camera(self):
        """Update camera position to follow vehicle."""
        vx, vy, vz = self.vehicle.position
        heading_rad = __import__('math').radians(self.vehicle.heading)
        
        # Position camera behind and above vehicle
        cam_x = vx - config.CAMERA_DISTANCE * __import__('math').cos(heading_rad)
        cam_y = vy - config.CAMERA_DISTANCE * __import__('math').sin(heading_rad)
        cam_z = vz + config.CAMERA_HEIGHT
        
        self.camera.setPos(cam_x, cam_y, cam_z)
        self.camera.lookAt(vx, vy, vz + 2)
    
    def _publish_telemetry(self):
        """Publish vehicle telemetry via MQTT."""
        if not self.mqtt_client.is_connected():
            print("[MQTT] ⚠️  Not connected, skipping publish")
            return
        
        x, y, z = self.vehicle.position
        speed = self.vehicle.velocity
        state = self.control_engine.current_state
        state_color = self.control_engine.get_current_state()["color"]
        
        # Publish location (simulated GPS)
        loc_result = self.mqtt_client.publish_location(x / 1000.0, y / 1000.0)
        print(f"[MQTT] 📍 Location published: {loc_result} (lat: {x/1000.0:.4f}, lon: {y/1000.0:.4f})")
        
        # Publish speed
        speed_limit = self.zone_manager.get_speed_limit(x, y)
        speed_result = self.mqtt_client.publish_speed(speed, speed_limit)
        print(f"[MQTT] 🚗 Speed published: {speed_result} (speed: {speed:.1f} km/h, limit: {speed_limit:.0f} km/h)")
        
        # Publish state
        state_result = self.mqtt_client.publish_state(state, state_color)
        print(f"[MQTT] 🎛️  State published: {state_result} (state: {state})")
        
        # Summary
        if loc_result and speed_result and state_result:
            print(f"[MQTT] ✅ All telemetry published successfully\n")
        else:
            print(f"[MQTT] ⚠️  Some publishes failed!\n")
    
    def _on_control_state_change(self, old_state, new_state, speed, limit):
        """Callback when control state changes."""
        if new_state == config.SPEED_STATE_WARNING:
            print(f"[Control] ⚠️  WARNING: Speed {speed:.1f} exceeds limit {limit:.0f}!")
            self.audio_manager.play_warning_sound()
        
        elif new_state == config.SPEED_STATE_REGULATING:
            print(f"[Control] 🔴 REGULATING: Speed {speed:.1f} >> limit {limit:.0f}!")
            self.audio_manager.play_regulating_sound()
        
        elif new_state == config.SPEED_STATE_NORMAL:
            print(f"[Control] ✅ NORMAL: Compliant speed {speed:.1f} km/h")
            self.audio_manager.stop_sound()


def main():
    """Main entry point."""
    try:
        sim = SmartSpeedSimulation()
        sim.run()
    except KeyboardInterrupt:
        print("\n\n[Main] Simulation interrupted by user")
    except Exception as e:
        print(f"\n\n[Main] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[Main] Cleaning up...")
        if 'sim' in locals():
            sim.mqtt_client.disconnect()
        print("[Main] Goodbye!\n")


if __name__ == "__main__":
    main()
