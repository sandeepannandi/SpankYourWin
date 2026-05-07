# SpankYourWin

**A brutalist, audio-reactive Windows application for the ultimate hardware experience.**

SpankYourWin is a specialized desktop tool designed to respond to your environment in real-time. Whether it's the sound of your voice or the mechanical act of plugging in hardware, SpankYourWin reacts with randomized audio triggers and system ducking.

---

## Features

- **Voice-Activated Triggers**: High-sensitivity RMS detection listens for vocal cues and reacts instantly.
- **Bi-Directional USB Reactivity**: Triggers unique sound events for both **Universal Serial Bus (USB) insertions** and **removals**.
- **Sound Pack Architecture**:
  - Organizes sounds into **Normal** and **Dramatic** packs.
  - Native **Upload** support: Drag and drop or browse to add custom `.mp3` or `.wav` files directly from the UI.
- **Intelligent Audio Ducking**: Automatically lowers the volume of background applications (Spotify, YouTube, etc.) during triggers to ensure your sounds are heard.
- **Brutalist Hacker UI**: A high-contrast, terminal-inspired interface with real-time waveform visualization and activity logs.

---

## Tech Stack

- **Python 3.10+**
- **PyQt6**: Core UI Framework.
- **PyAudio & NumPy**: Real-time signal processing and RMS calculation.
- **pycaw**: Windows Audio Session Control for dynamic volume ducking.
- **psutil**: Robust hardware polling for device detection.
- **playsound**: Multi-threaded audio playback.

---

## Getting Started

### Prerequisites

You must have Python 3.10 or higher installed. It is recommended to use a virtual environment.

```bash
# Clone the repository
git clone https://github.com/sandeepannandi/SpankYourWin.git
cd SpankYourWin

# Install dependencies
pip install -r requirements.txt
```

### Usage

1.  **Launch the Application**:
    ```bash
    python main.py
    ```
2.  **Configure Sensitivity**: Use the slider to adjust the threshold for voice activation.
3.  **Choose a Pack**: Toggle between **NORMAL** and **DRAMATIC** sound packs.
4.  **Add Your Own Sounds**: Click the **UPLOAD CUSTOM SOUNDS** button to add your favorite tracks to the current pack.
5.  **Let it Listen**: The app runs as a visible window and provides real-time feedback via the waveform bar and log area.

---

## Project Structure

```text
SpankYourWin/
├── main.py              # Application Entry Point
├── core/
│   ├── mic_listener.py  # Audio Signal Processing
│   ├── usb_listener.py  # Hardware Event Polling
│   ├── sound_engine.py  # Playback & Ducking Logic
│   └── settings.py      # JSON Configuration Management
├── ui/
│   └── app.py           # PyQt6 Dashboard & Styling
└── sounds/              # Audio Assets
    ├── thud/            # Pack Directories
    │   ├── normal/
    │   └── dramatic/
    └── usb/             # USB Events
```

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
