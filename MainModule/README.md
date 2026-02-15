# Smart Speed Control System - IoT Cyber-Physical Simulation

A professional-grade, production-structured simulation system demonstrating real-time smart speed control with 3D graphics, IoT communication, and embedded systems integration.

## 🎯 Project Objective

This system simulates a real-world smart speed control infrastructure where:

1. **User drives a 3D vehicle** on a simulated road with multiple speed zones
2. **System dynamically monitors speed** against zone-specific limits
3. **Automatic speed regulation** occurs when vehicle exceeds limits
4. **Real-time telemetry** is published via MQTT to IoT devices
5. **ESP32 microcontroller** responds in real-time to control states via MQTT

## 🏗️ Architecture Overview

### Four-Layer Cyber-Physical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: 3D Simulation Engine (Panda3D)                     │
│ - Real-time 3D graphics and physics                         │
│ - Player vehicle control with arrow keys                    │
│ - Colored road zones for visual feedback                    │
│ - Third-person camera system                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Speed Monitoring & Regulation Engine               │
│ - Real-time speed monitoring                                │
│ - Zone detection via GPS coordinates                        │
│ - Smart state management (NORMAL/WARNING/REGULATING)        │
│ - Automatic acceleration regulation                         │
│ - Audio warning system                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: MQTT IoT Communication                             │
│ - Real-time telemetry publishing                            │
│ - Topics: location, speed, state (500ms intervals)          │
│ - Automatic reconnection handling                           │
│ - Clean session management                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: ESP32 Firmware & LED Control                       │
│ - WiFi connectivity                                         │
│ - MQTT subscription and message parsing                     │
│ - Real-time LED control (Green/Yellow/Red)                  │
│ - Non-blocking operations with millis()                     │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

```
User Input (Arrow Keys)
    ↓
Vehicle Physics Engine (Acceleration, Friction, Steering)
    ↓
Position Update → Zone Manager (Determine Speed Limit)
    ↓
Control Engine (Compare Speed vs Limit)
    ↓
State Determination (NORMAL/WARNING/REGULATING)
    ├→ Regulation Factor Calculation
    ├→ Audio Manager (Play Sound Effects)
    └→ HUD Updates
    ↓
MQTT Client (Publish Telemetry)
    ├→ Location (lat/lon from X/Y)
    ├→ Speed & Limit
    └→ System State
    ↓
ESP32 Firmware (Receive Messages)
    ↓
LED Control (Green/Yellow/Red)
```

## 🔧 Project Structure

```
SmartSpeedIoT/
├── main.py                           # Main entry point
├── config.py                         # Centralized configuration
├── requirements.txt                  # Python dependencies
│
├── core/                             # Core simulation engines
│   ├── __init__.py
│   ├── physics.py                   # Vehicle physics simulation
│   ├── vehicle.py                   # Vehicle representation
│   ├── zone_manager.py              # Speed zone management
│   ├── control_engine.py            # Speed control state machine
│   └── mqtt_client.py               # IoT MQTT communication
│
├── ui/                              # User interface components
│   ├── __init__.py
│   ├── hud.py                       # On-screen HUD display
│   └── audio_manager.py             # Sound effects management
│
├── assets/                          # Placeholder for 3D models/textures
└── firmware/
    └── esp32_smart_speed.ino        # ESP32 Arduino firmware
```

## 🚗 Vehicle Simulation Details

### Speed Zones

| Zone | Location | Speed Limit | Color | Visual |
|------|----------|-------------|-------|--------|
| **School Zone** | X: -100 to 0 | 50 km/h | Yellow | Semi-transparent overlay |
| **City Road** | X: 0 to 100 | 60 km/h | Gray | Semi-transparent overlay |
| **Highway** | X: 100 to 300 | 80 km/h | Dark Gray | Semi-transparent overlay |

### Vehicle Physics

- **Max Speed**: 120 km/h
- **Acceleration**: 30 km/h/sec
- **Deceleration (Normal)**: 15 km/h/sec
- **Deceleration (Brake)**: 40 km/h/sec
- **Friction**: 5 km/h/sec (passive)
- **Steering**: 90°/sec

### Speed Control States

**NORMAL (Green)**
- Speed ≤ Speed Limit
- Normal acceleration available
- No alerts or sounds
- Green LED on (steady)

**WARNING (Yellow)**
- Speed Limit < Speed ≤ Speed Limit + 5 km/h
- Reduced acceleration (50% multiplier)
- Warning beep sound
- Yellow LED blinking (2 Hz)

**REGULATING (Red)**
- Speed > Speed Limit + 5 km/h
- Minimal acceleration (proportionally reduced)
- Alarm sound
- Red LED on (steady)

## 📡 MQTT Topics & Payloads

### Topic: `vehicle/smart_speed/location`
**Published**: Every 500ms
```json
{
  "lat": 0.123456,
  "lon": -0.654321,
  "timestamp": 1708020145.234
}
```

### Topic: `vehicle/smart_speed/speed`
**Published**: Every 500ms
```json
{
  "speed": 65.5,
  "limit": 60.0,
  "overspeed": 5.5,
  "timestamp": 1708020145.234
}
```

### Topic: `vehicle/smart_speed/state`
**Published**: Every 500ms (retained)
```json
{
  "state": "WARNING",
  "color": {
    "r": 255,
    "g": 255,
    "b": 0
  },
  "timestamp": 1708020145.234
}
```

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| **↑ (Up Arrow)** | Accelerate |
| **↓ (Down Arrow)** | Brake |
| **← (Left Arrow)** | Turn Left |
| **→ (Right Arrow)** | Turn Right |
| **R** | Reset Vehicle Position |

## 🎮 HUD Display Elements

The on-screen HUD displays:

- **Current Speed** (km/h)
- **Speed Limit** (km/h)
- **Current Zone Name**
- **System State** (NORMAL/WARNING/REGULATING)
- **GPS Coordinates** (simulated from X/Y)
- **MQTT Connection Status**
- **Overspeed Value** (km/h above limit)
- **Acceleration Regulation** (%)
- **FPS Counter**
- **Control Instructions**

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Panda3D 3D graphics engine
- paho-mqtt library
- HiveMQ MQTT broker (local or cloud)

### Installation

1. **Clone or download the project**
```bash
cd SmartSpeedIoT
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start MQTT Broker**
```bash
# Option A: Local HiveMQ (if installed)
docker run -p 1883:1883 hivemq/hivemq

# Option B: Use cloud broker
# Edit config.py: MQTT_BROKER_HOST = "broker.hivemq.com"
```

5. **Run the simulation**
```bash
python main.py
```

### Running the Project

Once started:

1. The 3D window opens showing the vehicle on the road
2. Press arrow keys to drive
3. MQTT messages are published in real-time
4. Monitor the colored zones as you move
5. Press R to reset position

## 🔌 ESP32 Integration with Wokwi

### Step 1: Create Wokwi Project

1. Go to [wokwi.com](https://wokwi.com)
2. Create new ESP32 project
3. Copy contents of `firmware/esp32_smart_speed.ino` into Wokwi editor

### Step 2: Add Components to Wokwi

Add these components:
- 1x ESP32
- 3x LEDs (any color)
- 3x 220Ω Resistors

### Step 3: Wire Components

```
ESP32 PIN ASSIGNMENTS:
- GPIO 17 → 220Ω Resistor → Green LED → GND
- GPIO 18 → 220Ω Resistor → Red LED → GND
- GPIO 19 → 220Ω Resistor → Yellow LED → GND
```

### Step 4: Configure Firmware

Edit the firmware if needed:
```cpp
const char* ssid = "Wokwi-GUEST";
const char* mqtt_server = "broker.hivemq.com";  // Change to local IP for local broker
```

### Step 5: Run Simulation

1. Start Wokwi simulation
2. Run `python main.py` on your PC
3. Drive the vehicle - watch the LEDs respond!

**LED Behaviors:**
- ✅ **Green LED** (steady) → Vehicle speed is normal
- ⚠️ **Yellow LED** (blinking 2Hz) → Speed slightly over limit (warning)
- 🔴 **Red LED** (steady) → Significant overspeed (regulating)

## 🎨 Visual Features

- **3D Rendering**: Real-time 3D graphics with Panda3D
- **Colored Road Zones**: Visual indication of speed limits
- **Third-Person Camera**: Dynamic camera following vehicle
- **Lighting & Shadows**: Ambient and directional lighting
- **Modern HUD**: Technical on-screen display with real-time updates
- **Vehicle Model**: Simple geometric cube (extensible to complex models)

## 🔊 Audio System

- **Non-blocking Sound Playback**: Doesn't freeze simulation
- **Warning Beep**: 1000 Hz tone when entering WARNING state
- **Alarm Sound**: 800-1000 Hz double tone when entering REGULATING state
- **Configurable**: Can be toggled on/off in config.py

## 📊 Performance

- **Target FPS**: 60 fps
- **Physics Update Rate**: 60 Hz
- **MQTT Publish Interval**: 500 ms (2 updates/sec)
- **HUD Update Interval**: 50 ms
- **CPU Usage**: Optimized with non-blocking operations

## 🔐 Configuration

All system configuration in `config.py`:

```python
# MQTT Settings
MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1883

# Vehicle Physics
VEHICLE_MAX_SPEED = 120  # km/h
VEHICLE_ACCELERATION = 30  # km/h/sec

# Speed Control
SPEED_WARNING_TOLERANCE = 5  # km/h

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
```

## 🐛 Troubleshooting

### MQTT Connection Issues
- Ensure HiveMQ broker is running: `docker ps`
- Check firewall allows port 1883
- Verify IP address in config.py

### Panda3D Import Errors
```bash
pip install --upgrade panda3d
```

### ESP32 Won't Upload
- Select correct board: Tools → Board → ESP32 Dev Module
- Check COM port selection
- Install CH340 driver if needed

### No LED Response
- Verify GPIO pin numbers in firmware
- Check MQTT topic subscriptions
- Monitor serial output in Arduino IDE

## 📚 Key Files Explained

### `main.py`
- Entry point for the entire simulation
- Initializes Panda3D rendering engine
- Manages game loop and physics updates
- Handles user input and camera
- Publishes MQTT telemetry

### `config.py`
- Centralized configuration management
- MQTT broker settings
- Vehicle physics parameters
- Zone definitions
- HUD display settings

### `core/physics.py`
- Realistic vehicle physics engine
- Acceleration, deceleration, friction calculations
- Steering and rotation
- Speed limiting during regulation

### `core/zone_manager.py`
- Manages speed control zones
- Dynamically determines current zone from position
- Provides speed limits and zone information

### `core/control_engine.py`
- Smart state management (NORMAL/WARNING/REGULATING)
- Calculates acceleration multiplier for regulation
- Triggers callbacks on state changes

### `core/mqtt_client.py`
- Handles MQTT communication
- Publishes location, speed, and state
- Automatic reconnection
- Thread-safe operations

### `firmware/esp32_smart_speed.ino`
- Complete ESP32 firmware
- WiFi and MQTT connectivity
- LED control logic
- Non-blocking millis() timing

## 🎓 Learning Outcomes

This project demonstrates:

- **Cyber-Physical Systems**: Integration of digital systems with physical devices
- **IoT Architecture**: Multi-layer design with distributed intelligence
- **Real-Time Systems**: Physics simulation at 60 Hz with MQTT at 2 Hz
- **MQTT Protocol**: Publish-subscribe IoT communication
- **Embedded Systems**: ESP32 firmware development
- **3D Graphics**: Real-time rendering with Panda3D
- **Software Architecture**: Modular, scalable code structure
- **State Machines**: Smart control state transitions
- **Non-Blocking Operations**: Responsive systems design

## 📝 Code Quality

- **Modular Design**: Separate concerns into dedicated modules
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Graceful degradation on errors
- **Configuration**: Centralized, easy to modify
- **Type Hints**: Clear function signatures
- **Production-Ready**: Professional code structure

## 🔄 Extensibility

Easy to extend with:

- **New Speed Zones**: Add entries to `config.py` ZONES dictionary
- **Complex Vehicle Models**: Replace cube with 3D model in `_create_vehicle()`
- **Additional LEDs**: Expand GPIO pins in ESP32 firmware
- **Data Logging**: Add database integration to MQTT client
- **Web Dashboard**: Add REST API or WebSocket server
- **Advanced Physics**: Implement suspension, traction control, etc.

## 📞 Support & Documentation

- **Inline Comments**: Every major function documented
- **Docstrings**: All classes and methods have detailed docstrings
- **README**: Complete project documentation (this file)
- **Code Examples**: Real-world ESP32 and Panda3D integration

## ⚖️ License

MIT License - Feel free to use for educational and commercial projects

## 👨‍💻 Authors

IoT Development Team

---

**Last Updated**: February 2026
**Version**: 1.0 Production Release
