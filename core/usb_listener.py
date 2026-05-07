import subprocess
import threading
import time
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import QObject, pyqtSignal

class USBListener(QObject, threading.Thread):
    usb_inserted = pyqtSignal()
    usb_removed = pyqtSignal()

    def __init__(self, settings_manager):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.daemon = True
        self.settings = settings_manager
        self._running = False

    def _get_pnp_entities(self):
        """Get all PnP device IDs via wmic. This catches mice, keyboards, drives, etc."""
        try:
            # We use creationflags to hide the console window that pops up
            result = subprocess.run(
                ['wmic', 'path', 'Win32_PnPEntity', 'get', 'DeviceID'],
                capture_output=True, text=True, creationflags=0x08000000 # CREATE_NO_WINDOW
            )
            # Filter non-empty lines and ignore header
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and "DeviceID" not in l]
            return set(lines)
        except Exception as e:
            print(f"ERROR: USB polling failed: {e}")
            return set()

    def run(self):
        self._running = True
        print("DEBUG: USBListener starting broad PnP polling...")
        
        previous_devices = self._get_pnp_entities()
        
        while self._running:
            try:
                time.sleep(1.0)
                current_devices = self._get_pnp_entities()
                
                # Plugin
                new_devices = current_devices - previous_devices
                if new_devices:
                    print(f"DEBUG: Hardware Plugged! Count: {len(new_devices)}")
                    settings = self.settings()
                    if settings['enabled'] and settings['usb_enabled']:
                        self.usb_inserted.emit()
                
                # Unplug
                removed_devices = previous_devices - current_devices
                if removed_devices:
                    print(f"DEBUG: Hardware Removed! Count: {len(removed_devices)}")
                    settings = self.settings()
                    if settings['enabled'] and settings['usb_enabled']:
                        self.usb_removed.emit()
                
                previous_devices = current_devices
            except:
                time.sleep(2.0)

    def stop(self):
        self._running = False
