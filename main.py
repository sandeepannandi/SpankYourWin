import sys
import os
import traceback
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QApplication
from ui.app import SpankYourWinUI
from core.settings import load_settings, save_settings
from core.sound_engine import SoundEngine
from core.mic_listener import MicListener
from core.usb_listener import USBListener

def main():
    try:
        print("--- SPANKYOURWIN STARTING ---")
        app = QApplication(sys.argv)
        
        settings = load_settings()
        engine = SoundEngine()
        window = SpankYourWinUI(settings)
        
        def get_settings():
            return settings

        mic_thread = MicListener(get_settings)
        usb_thread = USBListener(get_settings)
        
        def on_trigger(source_name):
            pack_type = settings['selected_sound_type']
            
            # Dynamic Folder Mapping
            if source_name == "plugin":
                folder = "sounds/usb/plugin"
            elif source_name == "unplug":
                folder = "sounds/usb/pugoff"
            else:
                # Voice pack
                folder = os.path.join("sounds", "thud", pack_type)
            
            if not os.path.exists(folder):
                print(f"Warning: Folder not found {folder}")
                folder = "sounds" # Ultimate fallback

            sound_path = engine.pick_random_sound(folder)
            if sound_path:
                msg = "VOICE trigger" if source_name == "voice" else f"USB {source_name}"
                window.add_log_entry(msg)
                engine.play_sound(sound_path, volume=settings['volume'])
            else:
                window.add_log_entry(f"Trigger {source_name} but no sound in {folder}")

        def sync_settings(new_settings):
            nonlocal settings
            settings = new_settings
            save_settings(settings)

        mic_thread.voice_detected.connect(lambda: on_trigger("voice"))
        mic_thread.rms_update.connect(window.update_rms)
        
        usb_thread.usb_inserted.connect(lambda: on_trigger("plugin"))
        usb_thread.usb_removed.connect(lambda: on_trigger("unplug"))
        
        window.settings_changed.connect(sync_settings)
        
        def cleanup():
            mic_thread.stop()
            usb_thread.stop()
            sys.exit(0)

        window.stop_clicked.connect(cleanup)
        app.aboutToQuit.connect(cleanup)

        mic_thread.start()
        usb_thread.start()
        window.show()
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
