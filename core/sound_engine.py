import os
import random
import threading
import traceback
import time
# pyrefly: ignore [missing-import]
from playsound import playsound
# pyrefly: ignore [missing-import]
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class SoundEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._active_sounds = 0
        self._lock = threading.Lock()

    def pick_random_sound(self, folder):
        if not os.path.isabs(folder):
            abs_folder = os.path.join(self.base_dir, folder)
        else:
            abs_folder = folder
            
        print(f"DEBUG: Looking for sounds in {abs_folder}")
        if not os.path.exists(abs_folder):
            return None
            
        sounds = [f for f in os.listdir(abs_folder) if f.endswith(('.mp3', '.wav'))]
        if not sounds:
            return None
            
        return os.path.join(abs_folder, random.choice(sounds))

    def play_sound(self, filepath, volume=1.0):
        threading.Thread(target=self._play_task, args=(filepath, volume), daemon=True).start()

    def _play_task(self, filepath, volume):
        try:
            with self._lock:
                self._active_sounds += 1
                if self._active_sounds == 1:
                    print(f"DEBUG: First sound starting - Ducking...")
                    self.duck_audio(0.1) # Duck deeper to be safe
            
            print(f"DEBUG: play_sound starting for {filepath}")
            playsound(filepath)
            print(f"DEBUG: playsound finished for {filepath}")
            
        except Exception:
            traceback.print_exc()
        finally:
            with self._lock:
                self._active_sounds -= 1
                if self._active_sounds == 0:
                    print(f"DEBUG: All sounds finished - Unducking...")
                    # Small delay before unducking to prevent snappy volume jumps
                    time.sleep(0.3)
                    self.unduck_audio()

    def duck_audio(self, level=0.2):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process and session.Process.name().lower() != "python.exe":
                    volume.SetMasterVolume(level, None)
        except Exception as e:
            print(f"Ducking error: {e}")

    def unduck_audio(self):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process and session.Process.name().lower() != "python.exe":
                    volume.SetMasterVolume(1.0, None)
        except Exception as e:
            print(f"Unducking error: {e}")
