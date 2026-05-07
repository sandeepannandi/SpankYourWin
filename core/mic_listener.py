import pyaudio
import numpy as np
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

class MicListener(QObject, threading.Thread):
    # Signals to communicate with UI
    thud_detected = pyqtSignal(str)  # "normal" or "dramatic"
    rms_update = pyqtSignal(float)   # For visualizer

    def __init__(self, settings_manager):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.daemon = True
        self.settings = settings_manager
        self._running = False
        self.last_trigger_time = 0
        self.cooldown = 0.5
        
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.audio = pyaudio.PyAudio()

    def run(self):
        self._running = True
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
        except Exception as e:
            print(f"Failed to open audio stream: {e}")
            return

        while self._running:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
                
                # Normalize RMS for UI visualizer (roughly 0-1 range)
                # Max value for int16 is 32768, but typical peaks are lower
                normalized_rms = min(rms / 10000.0, 1.0)
                self.rms_update.emit(normalized_rms)

                # Detection logic
                settings = self.settings() # Get latest settings
                if settings['enabled'] and settings['thud_enabled']:
                    current_time = time.time()
                    if current_time - self.last_trigger_time > self.cooldown:
                        if rms > settings['thud_threshold_high']:
                            self.thud_detected.emit("dramatic")
                            self.last_trigger_time = current_time
                        elif rms > settings['thud_threshold_low']:
                            self.thud_detected.emit("normal")
                            self.last_trigger_time = current_time

            except Exception as e:
                print(f"Error in mic listener loop: {e}")
                break

        stream.stop_stream()
        stream.close()

    def stop(self):
        self._running = False
        self.audio.terminate()
