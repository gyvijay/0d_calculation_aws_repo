import os
import sys
import json
import inspect
import threading
import requests
import websocket

# Web Framework imports
from flask import Flask, render_template, send_from_directory, jsonify
from flask_socketio import SocketIO

import paho.mqtt.client as mqtt

# Import your custom modules
import calculations
import svg_processor  
import config  # Importing the complete configuration matrix module

# ==============================================================================
# FLASK & REAL-TIME MULTI-PAGE WEB CONFIGURATION
# ==============================================================================
app = Flask(__name__)

# Enforce async_mode='threading' to safely bridge background threads with WebSockets
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Route 1: Serve the core multi-page interface layout template
@app.route('/')
def index():
    return render_template('index.html')

# Route 2: Dynamic JSON lookup API allowing index.html to read pages from config.py
@app.route('/api/pages')
def get_dashboard_pages():
    client_pages = [
        {"title": p["title"], "filename": p["live_filename"]} 
        for p in config.DASHBOARD_PAGES
    ]
    return jsonify(client_pages)

# Route 3: Dynamic static server path to safely route files from your new cache folder
@app.route('/live-static/<filename>')
def serve_live_cache_svg(filename):
    response = send_from_directory(config.CACHE_DIR, filename)
    
    # Strict cache headers to bypass local browser proxy caches completely
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ==============================================================================
# WEB DIAGNOSTIC TUNNEL LOGGER
# ==============================================================================
@socketio.on('connect')
def handle_web_connection():
    print("\n🟢 SUCCESS: A web browser has officially linked into the real-time socket tunnel! 🟢\n")

# ==============================================================================
# THREAD-SAFE DATA STORAGE HOOKS
# ==============================================================================
class DataStorage:
    def __init__(self):
        self.lock = threading.Lock()
        self.signals = {}
        self.attributes = {}

data_store = DataStorage()

# ==============================================================================
# BACKGROUND THINGSBOARD DATA ENGINE
# ==============================================================================
class ThingsBoardWorker:
    def __init__(self, storage):
        self.store = storage
        self.jwt_token = None
        
        self.mqtt_host = config.TB_HOST.replace("https://", "").replace("http://", "").split(":")[0]
        self.mqtt_port = 1883
        
        # Inbound Client A: Attributes (Updated to VERSION2 to fix deprecation warning)
        self.mqtt_rx = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_rx.username_pw_set(config.SOURCE_DEVICE_TOKEN)
        self.mqtt_rx.on_connect = self.on_mqtt_rx_connect
        self.mqtt_rx.on_message = self.on_mqtt_rx_message

        # Outbound Client B: Calculations (Updated to VERSION2 to fix deprecation warning)
        self.mqtt_tx = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_tx.username_pw_set(config.DESTINATION_DEVICE_TOKEN)
        self.mqtt_tx.on_connect = self.on_mqtt_tx_connect

    def start_connection(self):
        print("Logging into ThingsBoard Cluster (REST API Authentication)...")
        try:
            clean_http = config.TB_HOST if config.TB_HOST.startswith(("http://", "https://")) else f"https://{config.TB_HOST}"
            r = requests.post(
                f"{clean_http}/api/auth/login",
                json={"username": config.EMAIL, "password": config.PASSWORD},
                timeout=10
            )
            if r.status_code != 200:
                print(f"REST Login Failed: {r.text}")
                return False
            
            self.jwt_token = r.json()["token"]
            print("REST Web Token Acquired Successfully.")
            
            print(f"Spinning up MQTT connections to {self.mqtt_host}...")
            self.mqtt_rx.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            self.mqtt_tx.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            self.mqtt_rx.loop_start()
            self.mqtt_tx.loop_start()

            # Launch WebSocket stream reader thread
            t = threading.Thread(target=self.run_websocket_loop, daemon=True)
            t.start()
            return True
        except Exception as e:
            print(f"Network Pipeline Initialization Error: {e}")
            return False

    def send_telemetry(self, key, value):
        if value is None:
            return
        try:
            payload = json.dumps({key: value})
            self.mqtt_tx.publish("v1/devices/me/telemetry", payload, qos=1)
            print(f"Published Calculated Data via MQTT -> {payload}")
        except Exception as e:
            print(f"Remote MQTT Publish Error: {e}")

    def run_calculations(self):
        functions = inspect.getmembers(calculations, inspect.isfunction)
        
        with self.store.lock:
            sig_copy = self.store.signals.copy()
            attr_copy = self.store.attributes.copy()

        for name, func in functions:
            try:
                value = func(sig_copy, attr_copy)
                with self.store.lock:
                    self.store.signals[name] = value
                
                threading.Thread(target=self.send_telemetry, args=(name, value), daemon=True).start()
            except KeyError:
                pass
            except Exception as e:
                print(f"Calculation Error inside {name}: {e}")

    def on_mqtt_tx_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print("Destination MQTT TX Client Connected.")
        else:
            print(f"Destination MQTT TX Client connection failed (Reason Code: {reason_code})")

    def on_mqtt_rx_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print("Source MQTT RX Client Connected.")
            client.subscribe("v1/devices/me/attributes")
            
            request_id = "202"
            req_payload = json.dumps({"sharedKeys": ",".join(config.SUBSCRIBE_ATTRIBUTES)})
            client.publish(f"v1/devices/me/attributes/request/{request_id}", req_payload)
            print("Subscribed to MQTT Source Attribute Channels.")

    def on_mqtt_rx_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))
            updated = False

            if topic == "v1/devices/me/attributes":
                with self.store.lock:
                    for key, val in payload.items():
                        if key in config.SUBSCRIBE_ATTRIBUTES:
                            self.store.attributes[key] = val
                            updated = True
                            print(f"MQTT Attribute Update -> {key} = {val}")

            elif "attributes/response/" in topic:
                shared_data = payload.get("shared", {})
                with self.store.lock:
                    for key, val in shared_data.items():
                        if key in config.SUBSCRIBE_ATTRIBUTES:
                            self.store.attributes[key] = val
                            updated = True
                            print(f"MQTT Initial Attribute State -> {key} = {val}")

            if updated:
                self.process_ui_cycle()
        except Exception as e:
            print("Inbound MQTT Message Processing Error:", e)

    def on_ws_open(self, ws):
        print("Telemetry WebSocket Tunnel Connected Successfully.")
        cmd = {
            "tsSubCmds": [{"entityType": "DEVICE", "entityId": config.SOURCE_DEVICE_ID, "scope": "LATEST_TELEMETRY", "cmdId": 1}],
            "attrSubCmds": [],
            "historyCmds": []
        }
        ws.send(json.dumps(cmd))

    def on_ws_message(self, ws, message):
        try:
            data = json.loads(message)
            if "data" not in data or data.get("subscriptionId") != 1:
                return

            rx_data = data["data"]
            updated = False

            with self.store.lock:
                for signal in config.SUBSCRIBE_SIGNALS:
                    if signal in rx_data:
                        try:
                            val = float(rx_data[signal][0][1])
                            self.store.signals[signal] = val
                            updated = True
                            print(f"WS Telemetry -> {signal} = {val}")
                        except Exception as e:
                            print(f"WS Telemetry Extraction Error: {e}")

            if updated:
                self.process_ui_cycle()
        except Exception as e:
            print("Inbound WebSocket Message Processing Error:", e)

    def on_ws_error(self, ws, error):
        print("WebSocket Tunnel Error:", error)

    def on_ws_close(self, ws, close_status_code, close_msg):
        print("WebSocket Tunnel Channel Closed.")

    def run_websocket_loop(self):
        clean_url = config.TB_HOST.replace("https://", "wss://").replace("http://", "ws://")
        if not clean_url.startswith(("ws://", "wss://")):
            clean_url = f"wss://{clean_url}"
            
        ws = websocket.WebSocketApp(
            f"{clean_url}/api/ws/plugins/telemetry?token={self.jwt_token}",
            on_open=self.on_ws_open,
            on_message=self.on_ws_message,
            on_error=self.on_ws_error,
            on_close=self.on_ws_close
        )
        ws.run_forever()

    def process_ui_cycle(self):
        self.run_calculations()
        
        with self.store.lock:
            current_signals = self.store.signals.copy()
            current_attributes = self.store.attributes.copy()
        
        svg_processor.generate_live_svgs(current_signals, current_attributes)
        
        # Broadcast real-time ping out across all application namespaces
        socketio.emit('refresh_svg')

# ==============================================================================
# ENGINE MAIN RUNNER BLOCK
# ==============================================================================
if __name__ == "__main__":
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    tb_worker = ThingsBoardWorker(data_store)
    
    if tb_worker.start_connection():
        print("\n=== Web Server Pipeline Initiated Successfully ===")
        print("Open your web browser and go to: http://127.0.0.1:5000\n")
        
        socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
    else:
        print("Fatal Network Error: Cloud pipeline connection failed to authenticate.")