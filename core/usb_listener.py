import win32gui
import win32con
import win32api
import threading
from PyQt6.QtCore import QObject, pyqtSignal

# GUID for USB devices (Interface Class)
# GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"

class USBListener(QObject, threading.Thread):
    usb_inserted = pyqtSignal()

    def __init__(self, settings_manager):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.daemon = True
        self.settings = settings_manager
        self._running = False

    def run(self):
        self._running = True
        
        # We need a window to receive WM_DEVICECHANGE
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "USBListenerWindow"
        wc.hInstance = win32api.GetModuleHandle(None)
        
        try:
            class_atom = win32gui.RegisterClass(wc)
            self.hwnd = win32gui.CreateWindow(
                class_atom, "USB Listener", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )
        except Exception as e:
            print(f"Failed to create USB listener window: {e}")
            return

        while self._running:
            win32gui.PumpWaitingMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            # DBT_DEVICEARRIVAL = 0x8000
            if wparam == 0x8000:
                settings = self.settings()
                if settings['enabled'] and settings['usb_enabled']:
                    self.usb_inserted.emit()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def stop(self):
        self._running = False
        if hasattr(self, 'hwnd'):
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
