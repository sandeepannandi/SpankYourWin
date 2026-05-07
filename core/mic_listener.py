import pyaudio
import numpy as np
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

class MicListener(QObject, threading.Thread):
    voice_detected = pyqtSignal()
    rms_update = pyqtSignal(float)

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

        try:
            self.audio = pyaudio.PyAudio()
        except:
            self.audio = None

    def run(self):
        if not self.audio: return
        self._running = True
        try:
            stream = self.audio.open(
                format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                input=True, frames_per_buffer=self.CHUNK
            )
        except: return

        while self._running:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                if len(audio_data) == 0: continue
                
                rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
                
                # Emit update for visualizer
                self.rms_update.emit(min(rms / 4000.0, 1.0))

                settings = self.settings()
                if settings['enabled'] and settings['thud_enabled']:
                    current_time = time.time()
                    if current_time - self.last_trigger_time > self.cooldown:
                        if rms > settings['thud_threshold']:
                            print(f"!!! TRIGGER: Voice Detected! RMS: {rms:.0f}")
                            self.voice_detected.emit()
                            self.last_trigger_time = current_time

            except: break

        try:
            stream.stop_stream()
            stream.close()
        except: pass

    def stop(self):
        self._running = False
        if self.audio:
            try: self.audio.terminate()
            except: pass
