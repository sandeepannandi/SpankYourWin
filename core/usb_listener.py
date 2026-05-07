import psutil
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

    def _get_drive_ids(self):
        try:
            return set(p.device for p in psutil.disk_partitions(all=True))
        except:
            return set()

    def run(self):
        self._running = True
        previous_devices = self._get_drive_ids()
        
        while self._running:
            try:
                time.sleep(1.0)
                current_devices = self._get_drive_ids()
                
                # Arrival
                new_devices = current_devices - previous_devices
                if new_devices:
                    print(f"DEBUG: USB Inserted! {new_devices}")
                    settings = self.settings()
                    if settings['enabled'] and settings['usb_enabled']:
                        self.usb_inserted.emit()
                
                # Removal
                removed_devices = previous_devices - current_devices
                if removed_devices:
                    print(f"DEBUG: USB Removed! {removed_devices}")
                    settings = self.settings()
                    if settings['enabled'] and settings['usb_enabled']:
                        self.usb_removed.emit()
                
                previous_devices = current_devices
            except:
                time.sleep(2.0)

    def stop(self):
        self._running = False
