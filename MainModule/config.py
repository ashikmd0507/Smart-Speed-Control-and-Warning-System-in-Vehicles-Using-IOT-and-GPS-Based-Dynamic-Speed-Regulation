"""
Smart Speed Control System - Configuration Module
==================================================

Centralized configuration management for the entire IoT system.
Defines all constants, MQTT parameters, zone definitions, and physics parameters.
"""

# ===========================
# MQTT BROKER CONFIGURATION
# ===========================
MQTT_BROKER_HOST = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = "smart_speed_controller_01"
MQTT_PUBLISH_INTERVAL = 0.5  # seconds (500 ms)
MQTT_QOS = 1
MQTT_KEEP_ALIVE = 60

# MQTT Topics
MQTT_TOPICS = {
    "location": "vehicle/smart_speed/location",
    "speed": "vehicle/smart_speed/speed",
    "state": "vehicle/smart_speed/state"
}

# ===========================
# VEHICLE PHYSICS PARAMETERS
# ===========================
VEHICLE_MAX_SPEED = 120  # km/h
VEHICLE_ACCELERATION = 30  # km/h per second
VEHICLE_DECELERATION_NORMAL = 15  # km/h per second
VEHICLE_DECELERATION_BRAKE = 40  # km/h per second
VEHICLE_FRICTION = 5  # km/h per second (passive deceleration)
VEHICLE_STEERING_SPEED = 90  # degrees per second
VEHICLE_INITIAL_POSITION = (0, 0, 0)  # x, y, z coordinates

# ===========================
# SPEED CONTROL ZONES
# ===========================
ZONES = {
    "school": {
        "name": "School Zone",
        "speed_limit": 50,  # km/h
        "color": (1.0, 0.8, 0.0),  # Yellow
        "x_range": (-100, 0),
        "y_range": (-50, 50),
    },
    "city": {
        "name": "City Road",
        "speed_limit": 60,  # km/h
        "color": (0.8, 0.8, 0.8),  # Gray
        "x_range": (0, 100),
        "y_range": (-50, 50),
    },
    "highway": {
        "name": "Highway",
        "speed_limit": 80,  # km/h
        "color": (0.4, 0.4, 0.4),  # Dark Gray
        "x_range": (100, 300),
        "y_range": (-50, 50),
    }
}

# ===========================
# SPEED CONTROL STATE THRESHOLDS
# ===========================
SPEED_WARNING_TOLERANCE = 5  # km/h (limit + 5 = WARNING state)
SPEED_REGULATING_THRESHOLD = 5.1  # km/h (limit + 5 = REGULATING state)

# Speed states
SPEED_STATE_NORMAL = "NORMAL"
SPEED_STATE_WARNING = "WARNING"
SPEED_STATE_REGULATING = "REGULATING"

# ===========================
# HUD DISPLAY SETTINGS
# ===========================
HUD_TEXT_SCALE = 0.06
HUD_TEXT_HEIGHT = 0.95
HUD_UPDATE_INTERVAL = 0.05  # seconds
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# ===========================
# 3D ENVIRONMENT SETTINGS
# ===========================
CAMERA_DISTANCE = 15  # units behind vehicle
CAMERA_HEIGHT = 8  # units above ground
LIGHTING_BRIGHTNESS = 1.5
GROUND_SIZE = 400
VEHICLE_SIZE = 2.0

# ===========================
# AUDIO SETTINGS
# ===========================
ENABLE_AUDIO = True
WARNING_SOUND_FILE = "warning.wav"
REGULATING_SOUND_FILE = "regulating.wav"

# ===========================
# GAME LOOP SETTINGS
# ===========================
TARGET_FPS = 60
PHYSICS_UPDATE_RATE = 0.016  # ~60 FPS
