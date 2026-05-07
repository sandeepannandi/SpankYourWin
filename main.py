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
            # Check for Global Override first
            override_path = settings.get('custom_override_path')
            
            if override_path and os.path.exists(override_path):
                sound_path = override_path
            else:
                # Normal pack/random logic
                pack_type = settings['selected_sound_type']
                if source_name == "plugin":
                    folder = "sounds/usb/plugin"
                elif source_name == "unplug":
                    folder = "sounds/usb/pugoff"
                else:
                    folder = os.path.join("sounds", "thud", pack_type)
                
                if not os.path.exists(folder):
                    folder = "sounds" 

                sound_path = engine.pick_random_sound(folder)

            if sound_path:
                msg = "VOICE trigger" if "voice" in source_name else f"USB {source_name}"
                if override_path:
                    msg += " [LOCKED]"
                window.add_log_entry(msg)
                engine.play_sound(sound_path, volume=settings['volume'])
            else:
                window.add_log_entry(f"No sound found for {source_name}")

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
