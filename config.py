import os

# ==============================================================================
# BASE DIRECTORY & DYNAMIC SVG FOLDERS CONFIG
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "svg_templates")
CACHE_DIR = os.path.join(BASE_DIR, "svg_cache")

# ==============================================================================
# DYNAMIC DASHBOARD PAGES CONFIGURATION
# To add a new page/subsystem loop in the future, simply add another item here!
# ==============================================================================
# ==============================================================================
# DYNAMIC DASHBOARD PAGES CONFIGURATION
# Updated to match your exact file structure on disk!
# ==============================================================================
DASHBOARD_PAGES = [
    {
        "title": "Fuel Cell System Page 1",
        "template": "svg_templates/EH_5-10kW_FCPS.svg"
    },
    {
        "title": "Fuel Cell System Page 2",
        "template": "svg_templates/EH_5-10kW_FCPS_PG2.svg"
    }
]

# ==============================================================================
# THINGSBOARD HYBRID CONNECTION CONFIG
# ==============================================================================
TB_HOST = "demo.thingsboard.io"

# 1. User Web Credentials (REQUIRED for WebSocket Telemetry Fetching)
EMAIL = "ehwebiot@gmail.com" 
PASSWORD = "EH@12345"

# 2. Source Device IDs & Tokens
SOURCE_DEVICE_ID = "cb5873b0-527c-11f1-b620-2ff6df252135"
SOURCE_DEVICE_TOKEN = "HEVEFAgD0bnP7UoM1z9y"

# 3. Destination Device Token
DESTINATION_DEVICE_TOKEN = "fpS71xafYPhKbQpGlHFP"

# ==============================================================================
# TELEMETRY SUBSCRIPTIONS (From Source Device via WebSockets)
# ==============================================================================
SUBSCRIBE_SIGNALS = [
    "PV_402_VI_FC_Out_V",          # Stack Voltage
    "PV_401_II_FC_Out_A",          # Stack Current
    "PV_302_PI_Clt_Stk_In_kPaa",   # Coolant Pressure In
    "PV_303_PI_Clt_Stk_Out_kPaa",  # Coolant Pressure Out
    "PV_302_TC_Clt_Stk_In_degC",   # Coolant Temperature In
    "PV_303_TC_Clt_Stk_Out_degC"   # Coolant Temperature Out
]

# ==============================================================================
# SHARED ATTRIBUTES (From Source Device via MQTT)
# ==============================================================================
SUBSCRIBE_ATTRIBUTES = [
    "Power_Demand",
    "current_limit",
    "enable_control"
]

# ==============================================================================
# SVG TEXT MAPPING
# LEFT  = ThingsBoard key / Calculation function name
# RIGHT = Placeholder text inside SVG
# ==============================================================================
SVG_TEXT_MAP = {
    "PV_402_VI_FC_Out_V":          "402_VI",
    "PV_401_II_FC_Out_A":          "401_II",
    "PV_302_PI_Clt_Stk_In_kPaa":   "302_PI",
    "PV_303_PI_Clt_Stk_Out_kPaa":  "303_PI",
    "PV_404_PI_FC_Out_W":          "PWR_W",
    "PVC_303_DP_Clt_Stk_kPaa":     "DP_P",
    "SV_501_PC_FC_Usr_Dmd_W":      "PWR_DMD",
}