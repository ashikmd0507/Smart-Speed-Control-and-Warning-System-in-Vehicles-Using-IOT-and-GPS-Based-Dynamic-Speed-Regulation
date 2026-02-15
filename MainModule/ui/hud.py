"""
Smart Speed Control System - HUD Module
======================================

Implements all on-screen HUD displays including:
- Current speed and speed limit
- Zone information
- System state indicator
- GPS coordinates (simulated)
- MQTT connection status
- Warning indicators

Uses Panda3D text rendering for real-time HUD updates.

Author: IoT Development Team
Version: 1.0
"""

import config


class HUD:
    """
    Heads-Up Display for the Smart Speed Control System.
    
    Attributes:
        base (ShowBase): Panda3D ShowBase instance
        text_elements (dict): Dictionary of text display elements
        update_interval (float): Time between HUD updates
        last_update (float): Time of last update
    """
    
    def __init__(self, base):
        """
        Initialize HUD system.
        
        Args:
            base: Panda3D ShowBase instance
        """
        self.base = base
        self.text_elements = {}
        self.update_interval = config.HUD_UPDATE_INTERVAL
        self.last_update = 0
        self._create_text_elements()
    
    def _create_text_elements(self):
        """Create all HUD text elements and position them on screen."""
        # Title
        self._create_text_element(
            "title",
            "SMART SPEED CONTROL SYSTEM",
            x=0.05,
            y=0.95,
            scale=0.08,
            color=(0.0, 1.0, 1.0, 1)  # Cyan
        )
        
        # Speed display (large, prominent)
        self._create_text_element(
            "speed",
            "Speed: 0 km/h",
            x=0.05,
            y=0.85,
            scale=0.07,
            color=(0.0, 1.0, 0.0, 1)  # Green
        )
        
        # Speed limit
        self._create_text_element(
            "limit",
            "Limit: 80 km/h",
            x=0.05,
            y=0.78,
            scale=0.06,
            color=(1.0, 1.0, 1.0, 1)  # White
        )
        
        # Zone name
        self._create_text_element(
            "zone",
            "Zone: Highway",
            x=0.05,
            y=0.71,
            scale=0.06,
            color=(1.0, 1.0, 1.0, 1)  # White
        )
        
        # System state (color-coded)
        self._create_text_element(
            "state",
            "State: NORMAL",
            x=0.05,
            y=0.64,
            scale=0.06,
            color=(0.0, 1.0, 0.0, 1)  # Green (NORMAL)
        )
        
        # GPS coordinates
        self._create_text_element(
            "gps",
            "GPS: (0.000000, 0.000000)",
            x=0.05,
            y=0.57,
            scale=0.05,
            color=(0.8, 0.8, 0.8, 1)  # Light gray
        )
        
        # MQTT Status
        self._create_text_element(
            "mqtt",
            "MQTT: [Connecting...]",
            x=0.05,
            y=0.50,
            scale=0.05,
            color=(1.0, 1.0, 0.0, 1)  # Yellow (connecting)
        )
        
        # Overspeed indicator
        self._create_text_element(
            "overspeed",
            "Overspeed: 0 km/h",
            x=0.05,
            y=0.43,
            scale=0.05,
            color=(1.0, 1.0, 1.0, 1)  # White
        )
        
        # Regulation factor
        self._create_text_element(
            "regulation",
            "Regulation: 100%",
            x=0.05,
            y=0.36,
            scale=0.05,
            color=(1.0, 1.0, 1.0, 1)  # White
        )
        
        # Controls help
        self._create_text_element(
            "controls_title",
            "CONTROLS:",
            x=0.70,
            y=0.95,
            scale=0.06,
            color=(1.0, 1.0, 1.0, 1)  # White
        )
        
        self._create_text_element(
            "controls",
            "UP/DOWN - Throttle/Brake\nLEFT/RIGHT - Steer\nR - Reset",
            x=0.70,
            y=0.88,
            scale=0.05,
            color=(0.7, 0.7, 0.7, 1)  # Gray
        )
        
        # FPS counter
        self._create_text_element(
            "fps",
            "FPS: 60",
            x=0.70,
            y=0.05,
            scale=0.05,
            color=(1.0, 1.0, 1.0, 1)  # White
        )
    
    def _create_text_element(self, name, text, x, y, scale, color):
        """
        Create a text element on the screen.
        
        Args:
            name (str): Unique identifier for this text element
            text (str): Text to display
            x (float): Horizontal position (0-1)
            y (float): Vertical position (0-1)
            scale (float): Text scale
            color (tuple): RGBA color
        """
        # Use Panda3D's TextNode for direct text rendering
        try:
            from panda3d.core import TextNode
            text_node = TextNode("text_" + name)
            text_node.setText(text)
            text_np = self.base.render2d.attachNewNode(text_node)
            text_np.setScale(scale * 0.1)
            text_np.setX(x - 1.0)  # Convert from 0-1 to -1 to 1
            text_np.setY(y - 1.0)
            text_node.setTextColor(*color)
            self.text_elements[name] = text_np
        except Exception as e:
            # Fallback if TextNode not available
            print(f"[HUD] Warning: Could not create text element '{name}': {e}")
            self.text_elements[name] = None
    
    def update(self, vehicle_state, zone_info, control_state, mqtt_status, dt):
        """
        Update all HUD elements with current data.
        
        Args:
            vehicle_state (dict): Vehicle state information
            zone_info (dict): Current zone information
            control_state (dict): Control engine state
            mqtt_status (dict): MQTT connection status
            dt (float): Delta time since last update
        """
        if not self.base:
            return
        
        # Extract data
        speed = vehicle_state.get("velocity", 0.0)
        position = vehicle_state.get("position", (0, 0, 0))
        limit = zone_info.get("speed_limit", 80)
        zone_name = zone_info.get("zone_name", "Unknown")
        state = control_state.get("state", "NORMAL")
        state_color = control_state.get("color", (1, 1, 1))
        overspeed = control_state.get("overspeed", 0)
        regulation_factor = control_state.get("regulation_factor", 1.0)
        connected = mqtt_status.get("connected", False)
        
        # Update speed
        self._update_text_element(
            "speed",
            f"Speed: {speed:.1f} km/h",
            color=(0.0, 1.0, 0.0, 1) if speed <= limit else (1.0, 0.5, 0.0, 1)
        )
        
        # Update speed limit
        self._update_text_element(
            "limit",
            f"Limit: {limit:.0f} km/h",
            color=(1.0, 1.0, 1.0, 1)
        )
        
        # Update zone
        self._update_text_element(
            "zone",
            f"Zone: {zone_name}",
            color=zone_info.get("color", (1, 1, 1)) + (1,)
        )
        
        # Update state with color coding
        state_color_rgba = (state_color[0], state_color[1], state_color[2], 1.0)
        self._update_text_element(
            "state",
            f"State: {state}",
            color=state_color_rgba
        )
        
        # Update GPS
        lat = position[0] / 1000.0  # Simulate GPS from coordinates
        lon = position[1] / 1000.0
        self._update_text_element(
            "gps",
            f"GPS: ({lat:.6f}, {lon:.6f})",
            color=(0.8, 0.8, 0.8, 1)
        )
        
        # Update MQTT status
        mqtt_text = "[Connected]" if connected else "[Disconnected]"
        mqtt_color = (0.0, 1.0, 0.0, 1) if connected else (1.0, 0.0, 0.0, 1)
        self._update_text_element(
            "mqtt",
            f"MQTT: {mqtt_text}",
            color=mqtt_color
        )
        
        # Update overspeed
        self._update_text_element(
            "overspeed",
            f"Overspeed: {overspeed:.1f} km/h",
            color=(1.0, 0.0, 0.0, 1) if overspeed > 0 else (1.0, 1.0, 1.0, 1)
        )
        
        # Update regulation factor
        reg_percent = int(regulation_factor * 100)
        self._update_text_element(
            "regulation",
            f"Regulation: {reg_percent}%",
            color=(1.0, 1.0, 1.0, 1)
        )
        
        # Update FPS
        fps = self.base.clock.getAverageFrameRate()
        self._update_text_element(
            "fps",
            f"FPS: {fps:.0f}",
            color=(1.0, 1.0, 1.0, 1)
        )
    
    def _update_text_element(self, name, text, color=None):
        """
        Update text content and optionally color of an element.
        
        Args:
            name (str): Text element identifier
            text (str): New text to display
            color (tuple): Optional RGBA color
        """
        if name not in self.text_elements:
            return
        
        element = self.text_elements[name]
        if element is None:
            return
        
        try:
            # Update text - access the TextNode directly from the NodePath
            if hasattr(element, 'node'):
                text_node = element.node()
                if hasattr(text_node, 'setText'):
                    text_node.setText(text)
            
            # Update color if provided
            if color and hasattr(element, 'node'):
                text_node = element.node()
                if hasattr(text_node, 'setTextColor'):
                    text_node.setTextColor(*color)
        except Exception as e:
            pass  # Silent fail if not supported
    
    def get_hud_data(self):
        """
        Get all current HUD data for telemetry or logging.
        
        Returns:
            dict: Current HUD state
        """
        return {
            "elements": list(self.text_elements.keys()),
            "update_interval": self.update_interval
        }
