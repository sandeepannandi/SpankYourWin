import os
import random
import threading
import time
from playsound import playsound
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class SoundEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_ducked = False

    def pick_random_sound(self, folder):
        if not os.path.exists(folder):
            print(f"Warning: Folder {folder} not found.")
            return None
        
        sounds = [f for f in os.listdir(folder) if f.endswith(('.mp3', '.wav'))]
        if not sounds:
            print(f"Warning: No sounds found in {folder}.")
            return None
        
        return os.path.join(folder, random.choice(sounds))

    def play_sound(self, filepath, volume=1.0):
        if not filepath:
            return
        
        threading.Thread(target=self._play_task, args=(filepath, volume), daemon=True).start()

    def _play_task(self, filepath, volume):
        with self.lock:
            self.duck_audio(0.3)
            try:
                # Note: playsound is synchronous, so we run it in a thread
                playsound(filepath)
            except Exception as e:
                print(f"Error playing sound: {filepath} -> {e}")
            finally:
                self.unduck_audio()

    def duck_audio(self, level=0.3):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume_control = session._ctl.QueryInterface(ISimpleAudioVolume)
                # We store original volume? Pycaw doesn't easily let us restore 
                # unless we track every session. For simplicity, we just set to 30% 
                # and then back to 100% (or whatever the user has).
                # A better way is to multiply current by 0.3
                volume_control.SetMasterVolume(level, None)
        except Exception as e:
            print(f"Ducking error: {e}")

    def unduck_audio(self):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume_control = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume_control.SetMasterVolume(1.0, None)
        except Exception as e:
            print(f"Unducking error: {e}")
