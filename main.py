import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.app import SpankYourWinUI
from core.settings import load_settings, save_settings
from core.sound_engine import SoundEngine
from core.mic_listener import MicListener
from core.usb_listener import USBListener

def main():
    app = QApplication(sys.argv)
    
    # Init settings
    settings = load_settings()
    
    # Init Sound Engine
    engine = SoundEngine()
    
    # Init UI
    window = SpankYourWinUI(settings)
    
    # Thread-safe settings getter
    def get_settings():
        return settings

    # Init Listeners
    mic_thread = MicListener(get_settings)
    usb_thread = USBListener(get_settings)
    
    # Signal Connections
    def on_thud(intensity):
        folder = "sounds/thud/dramatic" if intensity == "dramatic" else "sounds/thud/normal"
        # If specific folders don't exist, fallback to base thud folder
        if not os.path.exists(folder):
            folder = "sounds/thud"
            
        sound_path = engine.pick_random_sound(folder)
        if sound_path:
            window.add_log_entry(f"THUD detected ({intensity})")
            engine.play_sound(sound_path, volume=settings['volume'])
        else:
            window.add_log_entry(f"THUD detected but no sound found in {folder}")

    def on_usb():
        folder = "sounds/usb"
        sound_path = engine.pick_random_sound(folder)
        if sound_path:
            window.add_log_entry("USB inserted")
            engine.play_sound(sound_path, volume=settings['volume'])
        else:
            window.add_log_entry("USB inserted but no sound found in sounds/usb")

    def sync_settings(new_settings):
        nonlocal settings
        settings = new_settings
        save_settings(settings)

    mic_thread.thud_detected.connect(on_thud)
    mic_thread.rms_update.connect(window.update_rms)
    usb_thread.usb_inserted.connect(on_usb)
    window.settings_changed.connect(sync_settings)
    
    def cleanup():
        mic_thread.stop()
        usb_thread.stop()
        sys.exit()

    window.stop_clicked.connect(cleanup)
    app.aboutToQuit.connect(cleanup)

    # Start threads
    mic_thread.start()
    usb_thread.start()

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
