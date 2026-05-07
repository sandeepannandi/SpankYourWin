import os
import random
import threading
import traceback
# pyrefly: ignore [missing-import]
from playsound import playsound
# pyrefly: ignore [missing-import]
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class SoundEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def pick_random_sound(self, folder):
        # Ensure folder is absolute
        if not os.path.isabs(folder):
            abs_folder = os.path.join(self.base_dir, folder)
        else:
            abs_folder = folder
            
        print(f"DEBUG: Looking for sounds in {abs_folder}")
        
        if not os.path.exists(abs_folder):
            print(f"Warning: Folder {abs_folder} not found.")
            return None
        
        sounds = [f for f in os.listdir(abs_folder) if f.endswith(('.mp3', '.wav'))]
        if not sounds:
            print(f"Warning: No sounds found in {abs_folder}.")
            return None
        
        return os.path.join(abs_folder, random.choice(sounds))

    def play_sound(self, filepath, volume=1.0):
        if not filepath:
            return
        # Ensure absolute path
        abs_path = os.path.abspath(filepath)
        print(f"DEBUG: play_sound starting thread for {abs_path}")
        threading.Thread(target=self._play_task, args=(abs_path, volume), daemon=True).start()

    def _play_task(self, filepath, volume):
        with self.lock:
            print(f"DEBUG: _play_task ducking audio for {filepath}")
            self.duck_audio(0.3)
            try:
                # playsound 1.2.2 works best with absolute paths on Windows
                playsound(filepath)
                print(f"DEBUG: playsound finished for {filepath}")
            except Exception as e:
                print(f"Error playing sound: {filepath} -> {e}")
                traceback.print_exc()
            finally:
                print(f"DEBUG: unducking audio")
                self.unduck_audio()

    def duck_audio(self, level=0.3):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process:
                    # Don't duck our own process if we can identify it
                    # But for now, duck all for simplicity
                    volume_control = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume_control.SetMasterVolume(level, None)
        except Exception as e:
            print(f"Ducking error: {e}")

    def unduck_audio(self):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process:
                    volume_control = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume_control.SetMasterVolume(1.0, None)
        except Exception as e:
            print(f"Unducking error: {e}")
