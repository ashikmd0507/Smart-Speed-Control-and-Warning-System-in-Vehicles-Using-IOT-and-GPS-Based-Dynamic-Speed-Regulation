/*
================================================================================
SMART SPEED CONTROL SYSTEM - ESP32 ARDUINO FIRMWARE
================================================================================

PROJECT: Smart Speed Control System with Real-Time LED Indicators
VERSION: 1.0
PLATFORM: ESP32 Microcontroller
MQTT BROKER: HiveMQ (broker.hivemq.com or local 127.0.0.1:1883)

PURPOSE:
========
This firmware runs on an ESP32 microcontroller and subscribes to the Smart Speed
Control System's MQTT topics to receive real-time vehicle state information.
Based on the received state, the firmware controls colored LEDs to indicate
the current system status:

- GREEN LED (GPIO 17)    → NORMAL state (speed compliant)
- YELLOW LED (GPIO 19)  → WARNING state (slight overspeed)
- RED LED (GPIO 18)     → REGULATING state (significant overspeed)

MQTT TOPICS SUBSCRIBED:
======================
- vehicle/smart_speed/state   → Current system state (NORMAL/WARNING/REGULATING)
- vehicle/smart_speed/speed   → Speed and limit information

LED BEHAVIOR:
=============
NORMAL:
  - Green LED ON (steady)
  - Yellow LED OFF
  - Red LED OFF

WARNING:
  - Green LED OFF
  - Yellow LED BLINK (2 Hz)
  - Red LED OFF

REGULATING:
  - Green LED OFF
  - Yellow LED OFF
  - Red LED ON (steady)

NETWORK:
========
WiFi SSID: Wokwi-GUEST (or any available network)
WiFi Password: (depends on network)
MQTT Server: broker.hivemq.com (or use local IP)
MQTT Port: 1883

WOKWI INTEGRATION:
==================
1. Create a new ESP32 project on Wokwi
2. Upload this firmware code
3. Add LED components to pins GPIO 17 (green), GPIO 18 (red), GPIO 19 (yellow)
4. Update WiFi credentials if needed
5. Ensure main.py is running and publishing to MQTT
6. Watch the LEDs update in real-time!

SETUP:
======
1. Install Arduino IDE and ESP32 Board Support
2. Install PubSubClient library (Sketch > Include Library > Manage Libraries)
3. Update WiFi SSID and password below
4. Select ESP32 Dev Module as board
5. Upload to ESP32

FEATURES:
- Non-blocking WiFi and MQTT operations using millis()
- Automatic reconnection to WiFi and MQTT broker
- Real-time LED control based on system state
- Serial debug output
- Clean code structure with proper error handling

AUTHOR: IoT Development Team
LICENSE: MIT
================================================================================
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ===========================
// CONFIGURATION
// ===========================

// WiFi Configuration
const char* ssid = "Wokwi-GUEST";           // WiFi network name
const char* password = "";                  // WiFi password (empty for open network)

// MQTT Configuration
// IMPORTANT: For local development, replace "broker.hivemq.com" with your PC IP
// Example: const char* mqtt_server = "192.168.1.100";
const char* mqtt_server = "broker.hivemq.com";  // MQTT broker address
const int mqtt_port = 1883;                     // MQTT port
const char* mqtt_client_id = "esp32_smart_speed_01";

// LED GPIO Pins
const int LED_GREEN = 17;    // Green LED (GPIO 17) - NORMAL state
const int LED_YELLOW = 19;   // Yellow LED (GPIO 19) - WARNING state
const int LED_RED = 18;      // Red LED (GPIO 18) - REGULATING state

// Timing Constants (milliseconds)
const unsigned long WIFI_RECONNECT_INTERVAL = 5000;      // 5 seconds
const unsigned long MQTT_RECONNECT_INTERVAL = 5000;      // 5 seconds
const unsigned long BLINK_INTERVAL = 500;                // 500ms for 2 Hz blink
const unsigned long SERIAL_UPDATE_INTERVAL = 1000;       // 1 second

// MQTT Topics
const char* topic_state = "vehicle/smart_speed/state";
const char* topic_speed = "vehicle/smart_speed/speed";

// ===========================
// GLOBAL VARIABLES
// ===========================

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long last_wifi_check = 0;
unsigned long last_mqtt_check = 0;
unsigned long last_blink_toggle = 0;
unsigned long last_serial_update = 0;

// State variables
String current_state = "NORMAL";
bool blink_state = false;
float current_speed = 0.0;
float speed_limit = 80.0;

// ===========================
// FUNCTION DECLARATIONS
// ===========================

void setup_pins();
void setup_wifi();
void reconnect_wifi();
void setup_mqtt();
void reconnect_mqtt();
void mqtt_callback(char* topic, byte* payload, unsigned int length);
void update_leds();
void blink_yellow_led();
void print_status();
void parse_state_message(const char* payload, size_t length);
void parse_speed_message(const char* payload, size_t length);

// ===========================
// SETUP FUNCTION
// ===========================

void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\n");
  Serial.println("================================================================================");
  Serial.println("SMART SPEED CONTROL SYSTEM - ESP32 FIRMWARE");
  Serial.println("================================================================================\n");
  
  setup_pins();
  setup_wifi();
  setup_mqtt();
  
  Serial.println("Setup complete! System running...\n");
}

// ===========================
// MAIN LOOP
// ===========================

void loop() {
  // Non-blocking WiFi check and reconnection
  unsigned long now = millis();
  
  if (now - last_wifi_check >= WIFI_RECONNECT_INTERVAL) {
    last_wifi_check = now;
    
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[WiFi] ❌ Connection lost, reconnecting...");
      reconnect_wifi();
    }
  }
  
  // Non-blocking MQTT check and reconnection
  if (now - last_mqtt_check >= MQTT_RECONNECT_INTERVAL) {
    last_mqtt_check = now;
    
    if (!client.connected()) {
      Serial.println("[MQTT] ❌ MQTT disconnected, reconnecting...");
      reconnect_mqtt();
    }
  }
  
  // Process MQTT messages - CRITICAL: Call frequently to process incoming messages
  if (client.connected()) {
    client.loop();  // Process any incoming messages from subscribed topics
  }
  
  // Update LED blinking state
  update_leds();
  
  // Print status updates
  if (now - last_serial_update >= SERIAL_UPDATE_INTERVAL) {
    last_serial_update = now;
    print_status();
  }
  
  // Small delay to prevent watchdog timeout
  delay(10);
}

// ===========================
// SETUP FUNCTIONS
// ===========================

void setup_pins() {
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Turn off all LEDs initially
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  
  Serial.println("[Setup] LED pins configured");
}

void setup_wifi() {
  Serial.print("[WiFi] Connecting to SSID: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected!");
    Serial.print("[WiFi] IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi] Connection failed, will retry in background");
  }
}

void reconnect_wifi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  
  Serial.println("[WiFi] Attempting to reconnect...");
  WiFi.reconnect();
}

void setup_mqtt() {
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
  
  // Set keepalive to 60 seconds (default is 60, ensure it's set)
  client.setKeepAlive(60);
  
  // Set buffer sizes if needed (for larger JSON messages)
  // client.setBufferSize(512);
  
  Serial.print("[MQTT] Server: ");
  Serial.print(mqtt_server);
  Serial.print(":");
  Serial.print(mqtt_port);
  Serial.print(" | KeepAlive: 60s | ");
  Serial.println("Waiting for connection...");
}

void reconnect_mqtt() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[MQTT] WiFi not connected, skipping MQTT connection");
    return;
  }
  
  if (client.connected()) {
    return;
  }
  
  Serial.print("[MQTT] Attempting to connect as ");
  Serial.println(mqtt_client_id);
  Serial.print("[MQTT] Broker: ");
  Serial.print(mqtt_server);
  Serial.print(":");
  Serial.println(mqtt_port);
  
  if (client.connect(mqtt_client_id)) {
    Serial.println("[MQTT] ✅ Connected to broker successfully");
    delay(100);  // Brief delay after connection
    
    // Subscribe to topics
    boolean sub_state = client.subscribe(topic_state, 1);  // QoS 1
    boolean sub_speed = client.subscribe(topic_speed, 1);  // QoS 1
    
    Serial.print("[MQTT] Subscribe state topic: ");
    Serial.println(sub_state ? "✅ SUCCESS" : "❌ FAILED");
    Serial.print("[MQTT] Subscribe speed topic: ");
    Serial.println(sub_speed ? "✅ SUCCESS" : "❌ FAILED");
    
    Serial.println("[MQTT] ✅ Ready to receive messages");
  } else {
    int rc = client.state();
    Serial.print("[MQTT] ❌ Connection failed, state=");
    Serial.print(rc);
    Serial.print(" (");
    
    switch(rc) {
      case -4: Serial.print("MQTT_CONNECTION_TIMEOUT"); break;
      case -3: Serial.print("MQTT_CONNECTION_LOST"); break;
      case -2: Serial.print("MQTT_CONNECT_FAILED"); break;
      case -1: Serial.print("MQTT_DISCONNECTED"); break;
      case 0: Serial.print("MQTT_CONNECTED"); break;
      case 1: Serial.print("MQTT_CONNECT_BAD_PROTOCOL"); break;
      case 2: Serial.print("MQTT_CONNECT_BAD_CLIENT_ID"); break;
      case 3: Serial.print("MQTT_CONNECT_UNAVAILABLE"); break;
      case 4: Serial.print("MQTT_CONNECT_BAD_CREDENTIALS"); break;
      case 5: Serial.print("MQTT_CONNECT_UNAUTHORIZED"); break;
      default: Serial.print("UNKNOWN");
    }
    Serial.println(")");
  }
}

// ===========================
// MQTT CALLBACK
// ===========================

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  // Convert topic to string
  String topic_str(topic);
  
  // Convert payload to string for logging
  String payload_str = "";
  for (unsigned int i = 0; i < length; i++) {
    payload_str += (char)payload[i];
  }
  
  Serial.println("");
  Serial.println("═══════════════════════════════════════════════════════════");
  Serial.println("📨 [CALLBACK TRIGGERED] ✅ MESSAGE RECEIVED");
  Serial.print("[MQTT] Topic: ");
  Serial.println(topic_str);
  Serial.print("[MQTT] Payload Length: ");
  Serial.print(length);
  Serial.println(" bytes");
  Serial.print("[MQTT] Payload Content: ");
  Serial.println(payload_str);
  Serial.println("═══════════════════════════════════════════════════════════");
  Serial.println("");
  
  // Parse message based on topic
  if (topic_str == topic_state) {
    Serial.println("[Parse] Processing STATE message...");
    parse_state_message((const char*)payload, length);
  } 
  else if (topic_str == topic_speed) {
    Serial.println("[Parse] Processing SPEED message...");
    parse_speed_message((const char*)payload, length);
  }
  else {
    Serial.print("[MQTT] ⚠️  WARNING: Unknown topic: ");
    Serial.println(topic_str);
  }
}

void parse_state_message(const char* payload, size_t length) {
  // JSON payload: {"state": "NORMAL/WARNING/REGULATING", ...}
  
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("[MQTT] JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }
  
  if (doc.containsKey("state")) {
    current_state = doc["state"].as<String>();
    Serial.print("[Control] State changed to: ");
    Serial.println(current_state);
  }
}

void parse_speed_message(const char* payload, size_t length) {
  // JSON payload: {"speed": float, "limit": float, ...}
  
  Serial.print("[Debug] Parsing speed message, length: ");
  Serial.println(length);
  
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("[MQTT] JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }
  
  if (doc.containsKey("speed")) {
    current_speed = doc["speed"].as<float>();
    Serial.print("[Speed] Updated to: ");
    Serial.print(current_speed);
    Serial.println(" km/h");
  }
  
  if (doc.containsKey("limit")) {
    speed_limit = doc["limit"].as<float>();
    Serial.print("[Limit] Updated to: ");
    Serial.print(speed_limit);
    Serial.println(" km/h");
  }
}

// ===========================
// LED CONTROL FUNCTIONS
// ===========================

void update_leds() {
  // Turn off all LEDs first
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  
  // Set LED based on current state
  if (current_state == "NORMAL") {
    // Green ON
    digitalWrite(LED_GREEN, HIGH);
  }
  else if (current_state == "WARNING") {
    // Yellow BLINK
    blink_yellow_led();
  }
  else if (current_state == "REGULATING") {
    // Red ON
    digitalWrite(LED_RED, HIGH);
  }
}

void blink_yellow_led() {
  unsigned long now = millis();
  
  // Toggle blink state every BLINK_INTERVAL ms
  if (now - last_blink_toggle >= BLINK_INTERVAL) {
    last_blink_toggle = now;
    blink_state = !blink_state;
  }
  
  if (blink_state) {
    digitalWrite(LED_YELLOW, HIGH);
  } else {
    digitalWrite(LED_YELLOW, LOW);
  }
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

void print_status() {
  Serial.print("[Status] WiFi: ");
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("CONNECTED (");
    Serial.print(WiFi.localIP());
    Serial.print(") | ");
  } else {
    Serial.print("DISCONNECTED | ");
  }
  
  Serial.print("MQTT: ");
  Serial.print(client.connected() ? "CONNECTED | " : "DISCONNECTED | ");
  
  Serial.print("State: ");
  Serial.print(current_state);
  Serial.print(" | Speed: ");
  Serial.print(current_speed);
  Serial.print(" km/h (Limit: ");
  Serial.print(speed_limit);
  Serial.println(" km/h)");
}

/*
================================================================================
WOKWI SIMULATION SETUP:
================================================================================

Components needed on Wokwi:
1. ESP32 (provided)
2. LED (Green) connected to GPIO 17, cathode to GND
3. LED (Yellow) connected to GPIO 19, cathode to GND
4. LED (Red) connected to GPIO 18, cathode to GND
5. 3x 220Ω resistors in series with LEDs

Wiring:
- ESP32 GND → Common GND rail
- LED Green anode → 220Ω resistor → GPIO 17
- LED Yellow anode → 220Ω resistor → GPIO 19
- LED Red anode → 220Ω resistor → GPIO 18
- All LED cathodes → GND

Run the simulation:
1. Click "Start simulation" in Wokwi
2. Run main.py in Smart Speed Control System
3. Drive the vehicle and watch the LEDs respond!

================================================================================
*/
