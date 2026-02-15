# Quick Start Guide

## 5-Minute Setup

### 1. Install Python Dependencies

```bash
cd SmartSpeedIoT
pip install -r requirements.txt
```

### 2. Start MQTT Broker

**Option A: Using Docker (Recommended)**
```bash
docker run -p 1883:1883 hivemq/hivemq
```

**Option B: Using Public Broker**
- No setup needed - firmware/main.py use `broker.hivemq.com` by default
- Edit `config.py` if needed:
  ```python
  MQTT_BROKER_HOST = "broker.hivemq.com"
  ```

### 3. Run the Simulation

```bash
python main.py
```

Expected output:
```
================================================================================
SMART SPEED CONTROL SYSTEM - Starting Simulation
================================================================================

[Main] Connecting to MQTT broker...
[MQTT] Connecting to 127.0.0.1:1883...
[Main] Simulation initialized successfully!
```

### 4. Control the Vehicle

- **↑** = Accelerate
- **↓** = Brake  
- **←/→** = Steer
- **R** = Reset

### 5. Watch the States Change

Drive in different zones and watch:
- Speed limit changes
- HUD updates
- LED colors in Wokwi (if running)
- MQTT messages being published

## ESP32 Setup (Wokwi)

1. Go to [wokwi.com/new/esp32](https://wokwi.com/new/esp32)
2. Copy content from `firmware/esp32_smart_speed.ino` into editor
3. Click "Start Simulation"
4. Add 3 LEDs on pins 17 (green), 18 (red), 19 (yellow)
5. Run both simulations together!

## Typical Session

```
1. Terminal 1: docker run -p 1883:1883 hivemq/hivemq
2. Terminal 2: python main.py
3. Browser:    Open Wokwi ESP32 simulation
4. Keyboard:   Drive the vehicle!
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'panda3d'"**
```bash
pip install panda3d
```

**"Connection refused" MQTT error**
```bash
# Check if broker is running:
docker ps

# If not running, start it:
docker run -p 1883:1883 hivemq/hivemq
```

**Black window opens but nothing displays**
- Wait 5 seconds for Panda3D to initialize
- Check console for error messages
- Ensure GPU drivers are updated

## Next Steps

1. Read [README.md](README.md) for full architecture
2. Explore code structure in `/core` and `/ui` directories
3. Modify zones in `config.py`
4. Customize ESP32 firmware in `firmware/`
5. Extend with your own features!

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Start here - main simulation |
| `config.py` | Change settings here |
| `core/mqtt_client.py` | MQTT publishing |
| `firmware/esp32_smart_speed.ino` | LED controller |

---
**Happy coding! 🚀**
