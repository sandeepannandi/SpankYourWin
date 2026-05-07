import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "thud_threshold_low": 1000,
    "thud_threshold_high": 2500,
    "volume": 0.8,
    "enabled": True,
    "thud_enabled": True,
    "usb_enabled": True
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
