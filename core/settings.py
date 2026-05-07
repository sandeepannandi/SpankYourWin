import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "thud_threshold": 800,
    "selected_sound_type": "normal", # "normal" or "dramatic"
    "volume": 1,
    "enabled": True,
    "thud_enabled": True,
    "usb_enabled": True
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
