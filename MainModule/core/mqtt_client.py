"""
Smart Speed Control System - MQTT IoT Communication Module
==========================================================

Handles all MQTT communication with the HiveMQ broker.
Publishes vehicle telemetry (location, speed, state) every 500ms.
Implements automatic reconnection and clean session management.

Uses paho-mqtt client library for robust MQTT protocol support.

Author: IoT Development Team
Version: 1.0
"""

import json
import time
import threading
import paho.mqtt.client as mqtt
import config


class SmartSpeedMQTTClient:
    """
    MQTT client for Smart Speed Control System.
    
    Attributes:
        broker_host (str): MQTT broker hostname/IP
        broker_port (int): MQTT broker port
        client (mqtt.Client): Paho MQTT client instance
        connected (bool): Current connection status
        last_publish_time (float): Timestamp of last publication
    """
    
    def __init__(self):
        """Initialize MQTT client with broker configuration."""
        self.broker_host = config.MQTT_BROKER_HOST
        self.broker_port = config.MQTT_BROKER_PORT
        self.client = None
        self.connected = False
        self.last_publish_time = 0
        self._lock = threading.Lock()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize and configure MQTT client."""
        self.client = mqtt.Client(
            client_id=config.MQTT_CLIENT_ID,
            clean_session=True,
            protocol=mqtt.MQTTv311
        )
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_message = self._on_message
        
        # Set will message for connection state notification
        will_payload = json.dumps({
            "status": "offline",
            "timestamp": time.time()
        })
        self.client.will_set(
            "vehicle/smart_speed/status",
            will_payload,
            qos=config.MQTT_QOS,
            retain=False
        )
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        MQTT connection callback.
        
        Args:
            client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc (int): Connection result code
        """
        if rc == 0:
            self.connected = True
            print(f"[MQTT] Connected to broker {self.broker_host}:{self.broker_port}")
            
            # Publish online status
            online_payload = json.dumps({
                "status": "online",
                "timestamp": time.time()
            })
            self.client.publish(
                "vehicle/smart_speed/status",
                online_payload,
                qos=config.MQTT_QOS,
                retain=False
            )
        else:
            self.connected = False
            error_msg = mqtt.connack_string(rc)
            print(f"[MQTT] Connection failed: {error_msg} (code {rc})")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        MQTT disconnection callback.
        
        Args:
            client: MQTT client instance
            userdata: User data
            rc (int): Disconnection code
        """
        self.connected = False
        if rc != 0:
            print(f"[MQTT] Unexpected disconnection (code {rc})")
        else:
            print("[MQTT] Disconnected from broker")
    
    def _on_publish(self, client, userdata, mid):
        """
        MQTT publish callback (message ID mid successfully published).
        
        Args:
            client: MQTT client instance
            userdata: User data
            mid (int): Message ID
        """
        pass  # Silent operation - no logging for each publish
    
    def _on_message(self, client, userdata, msg):
        """
        MQTT message receive callback.
        
        Args:
            client: MQTT client instance
            userdata: User data
            msg: MQTT message object
        """
        try:
            payload = msg.payload.decode('utf-8')
            print(f"[MQTT] Message received on {msg.topic}: {payload}")
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")
    
    def connect(self):
        """
        Connect to MQTT broker.
        
        Returns:
            bool: True if connection initiated successfully
        """
        try:
            self.client.connect(
                self.broker_host,
                self.broker_port,
                keepalive=config.MQTT_KEEP_ALIVE
            )
            self.client.loop_start()  # Start background thread for MQTT loop
            print(f"[MQTT] Connecting to {self.broker_host}:{self.broker_port}...")
            return True
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        try:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                print("[MQTT] Disconnect initiated")
        except Exception as e:
            print(f"[MQTT] Disconnection error: {e}")
        finally:
            self.connected = False
    
    def publish_location(self, latitude, longitude):
        """
        Publish vehicle location (simulated GPS coordinates).
        
        Args:
            latitude (float): Latitude (simulated from X coordinate)
            longitude (float): Longitude (simulated from Y coordinate)
        
        Returns:
            bool: True if publish was successful
        """
        # Note: Throttling is handled by main.py, not here
        # This allows location, speed, and state to publish together
        
        try:
            with self._lock:
                payload = json.dumps({
                    "lat": round(latitude, 6),
                    "lon": round(longitude, 6),
                    "timestamp": time.time()
                })
                
                result = self.client.publish(
                    config.MQTT_TOPICS["location"],
                    payload,
                    qos=config.MQTT_QOS,
                    retain=False
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    return True
                else:
                    print(f"[MQTT] Publish error for location: {result.rc}")
                    return False
        except Exception as e:
            print(f"[MQTT] Error publishing location: {e}")
            return False
    
    def publish_speed(self, speed, speed_limit):
        """
        Publish current speed and speed limit.
        
        Args:
            speed (float): Current speed in km/h
            speed_limit (float): Current speed limit in km/h
        
        Returns:
            bool: True if publish was successful
        """
        # Note: Throttling is handled by main.py, not here
        # This allows location, speed, and state to publish together
        
        try:
            with self._lock:
                payload = json.dumps({
                    "speed": round(speed, 2),
                    "limit": round(speed_limit, 2),
                    "overspeed": round(max(0, speed - speed_limit), 2),
                    "timestamp": time.time()
                })
                
                result = self.client.publish(
                    config.MQTT_TOPICS["speed"],
                    payload,
                    qos=config.MQTT_QOS,
                    retain=False
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    return True
                else:
                    print(f"[MQTT] Publish error for speed: {result.rc}")
                    return False
        except Exception as e:
            print(f"[MQTT] Error publishing speed: {e}")
            return False
    
    def publish_state(self, state, color_rgb=None):
        """
        Publish current control system state.
        
        Args:
            state (str): Current state (NORMAL/WARNING/REGULATING)
            color_rgb (tuple): RGB color tuple (optional)
        
        Returns:
            bool: True if publish was successful
        """
        # Note: Throttling is handled by main.py, not here
        # This allows location, speed, and state to publish together
        
        try:
            with self._lock:
                payload_dict = {
                    "state": state,
                    "timestamp": time.time()
                }
                
                if color_rgb:
                    payload_dict["color"] = {
                        "r": int(color_rgb[0] * 255),
                        "g": int(color_rgb[1] * 255),
                        "b": int(color_rgb[2] * 255)
                    }
                
                payload = json.dumps(payload_dict)
                
                result = self.client.publish(
                    config.MQTT_TOPICS["state"],
                    payload,
                    qos=config.MQTT_QOS,
                    retain=True  # Retain state message
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    return True
                else:
                    print(f"[MQTT] Publish error for state: {result.rc}")
                    return False
        except Exception as e:
            print(f"[MQTT] Error publishing state: {e}")
            return False
    
    def _should_publish(self):
        """
        Check if enough time has elapsed since last publish.
        Respects MQTT_PUBLISH_INTERVAL from config.
        
        Returns:
            bool: True if ready to publish
        """
        current_time = time.time()
        if current_time - self.last_publish_time >= config.MQTT_PUBLISH_INTERVAL:
            return True
        return False
    
    def is_connected(self):
        """
        Check current connection status.
        
        Returns:
            bool: True if connected to broker
        """
        return self.connected
    
    def get_status(self):
        """
        Get current MQTT client status.
        
        Returns:
            dict: Status information
        """
        return {
            "connected": self.connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "client_id": config.MQTT_CLIENT_ID,
            "last_publish": self.last_publish_time
        }
