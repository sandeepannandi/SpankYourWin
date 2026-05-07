import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSlider, QScrollArea, QFrame,
    QButtonGroup, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen

class WaveformBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.level = 0.0
        self.flash_active = False
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._stop_flash)
        
    def set_level(self, level):
        self.level = level
        self.update()

    def flash(self):
        self.flash_active = True
        self.flash_timer.start(300)
        self.update()

    def _stop_flash(self):
        self.flash_active = False
        self.flash_timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        bg_color = QColor("#1a1a1a")
        if self.flash_active:
            bg_color = QColor("#ff2222")
        painter.fillRect(rect, bg_color)
        if not self.flash_active:
            bar_width = int(rect.width() * self.level)
            painter.fillRect(0, 0, bar_width, rect.height(), QColor("#ff2222"))
        painter.setPen(QPen(QColor("#333333"), 1))
        for x in range(0, rect.width(), 40):
            painter.drawLine(x, 0, x, rect.height())

class SpankYourWinUI(QMainWindow):
    stop_clicked = pyqtSignal()
    settings_changed = pyqtSignal(dict)
    upload_sound_requested = pyqtSignal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SpankYourWin")
        self.setFixedSize(400, 650)
        self.setStyleSheet("""
            QMainWindow { background-color: #0d0d0d; }
            QWidget { background-color: #0d0d0d; color: #ff2222; font-family: 'Courier New', monospace; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { 
                border: 2px solid #ff2222; 
                background-color: #0d0d0d; 
                color: #ff2222; 
                padding: 10px; 
                font-weight: bold;
                text-transform: uppercase;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #ff2222;
                color: #0d0d0d;
            }
            QPushButton#STOP_BTN {
                background-color: #ff2222;
                color: #0d0d0d;
                font-size: 18px;
                border: none;
            }
            QPushButton#UPLOAD_BTN {
                background-color: #1a1a1a;
                font-size: 10px;
                padding: 5px;
            }
            QSlider::groove:horizontal { border: 1px solid #ff2222; height: 4px; background: #1a1a1a; }
            QSlider::handle:horizontal { background: #ff2222; border: 1px solid #ff2222; width: 15px; margin: -5px 0; }
            QFrame#DIVIDER { background-color: #ff2222; max-height: 2px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("SPANK YOUR WIN\nv1.1.0"))
        header_layout.addStretch()
        self.status_label = QLabel("[● ACTIVE]")
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)

        divider = QFrame(); divider.setObjectName("DIVIDER"); layout.addWidget(divider)

        # Visualizer
        self.visualizer = WaveformBar()
        layout.addWidget(self.visualizer)

        # Sound Pack Selector
        layout.addWidget(QLabel("SELECTED SOUND PACK"))
        pack_layout = QHBoxLayout()
        self.btn_normal = QPushButton("NORMAL")
        self.btn_normal.setCheckable(True)
        self.btn_dramatic = QPushButton("DRAMATIC")
        self.btn_dramatic.setCheckable(True)
        
        self.type_group = QButtonGroup()
        self.type_group.addButton(self.btn_normal)
        self.type_group.addButton(self.btn_dramatic)
        
        if self.settings['selected_sound_type'] == "normal":
            self.btn_normal.setChecked(True)
        else:
            self.btn_dramatic.setChecked(True)
            
        self.btn_normal.clicked.connect(lambda: self._set_type("normal"))
        self.btn_dramatic.clicked.connect(lambda: self._set_type("dramatic"))
        
        pack_layout.addWidget(self.btn_normal)
        pack_layout.addWidget(self.btn_dramatic)
        layout.addLayout(pack_layout)

        self.upload_btn = QPushButton("UPLOAD CUSTOM SOUNDS")
        self.upload_btn.setObjectName("UPLOAD_BTN")
        self.upload_btn.clicked.connect(self._handle_upload)
        layout.addWidget(self.upload_btn)

        divider2 = QFrame(); divider2.setObjectName("DIVIDER"); layout.addWidget(divider2)

        # Sensitivity Slider
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(QLabel("Sensitivity"))
        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setMinimum(100)
        self.sens_slider.setMaximum(8000)
        self.sens_slider.setValue(self.settings['thud_threshold'])
        self.sens_slider.valueChanged.connect(self._on_sens_change)
        sens_layout.addWidget(self.sens_slider)
        layout.addLayout(sens_layout)

        # Toggles
        toggles_layout = QHBoxLayout()
        self.thud_toggle = QPushButton("VOICE: ON" if self.settings['thud_enabled'] else "VOICE: OFF")
        self.thud_toggle.setCheckable(True)
        self.thud_toggle.setChecked(self.settings['thud_enabled'])
        self.thud_toggle.clicked.connect(self._toggle_thud)
        
        self.usb_toggle = QPushButton("USB: ON" if self.settings['usb_enabled'] else "USB: OFF")
        self.usb_toggle.setCheckable(True)
        self.usb_toggle.setChecked(self.settings['usb_enabled'])
        self.usb_toggle.clicked.connect(self._toggle_usb)
        
        toggles_layout.addWidget(self.thud_toggle)
        toggles_layout.addWidget(self.usb_toggle)
        layout.addLayout(toggles_layout)

        divider3 = QFrame(); divider3.setObjectName("DIVIDER"); layout.addWidget(divider3)

        # Log
        layout.addWidget(QLabel("LAST TRIGGER"))
        self.log_area = QScrollArea()
        self.log_area.setWidgetResizable(True)
        self.log_area.setStyleSheet("border: 1px solid #333333; background-color: #050505;")
        self.log_content = QWidget()
        self.log_layout = QVBoxLayout(self.log_content)
        self.log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_area.setWidget(self.log_content)
        layout.addWidget(self.log_area)

        # Stop Button
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("STOP_BTN")
        self.stop_btn.clicked.connect(self._handle_stop)
        layout.addWidget(self.stop_btn)

    def _set_type(self, s_type):
        self.settings['selected_sound_type'] = s_type
        self.settings_changed.emit(self.settings)

    def _toggle_thud(self):
        checked = self.thud_toggle.isChecked()
        self.thud_toggle.setText("VOICE: ON" if checked else "VOICE: OFF")
        self.settings['thud_enabled'] = checked
        self.settings_changed.emit(self.settings)

    def _toggle_usb(self):
        checked = self.usb_toggle.isChecked()
        self.usb_toggle.setText("USB: ON" if checked else "USB: OFF")
        self.settings['usb_enabled'] = checked
        self.settings_changed.emit(self.settings)

    def _on_sens_change(self):
        self.settings['thud_threshold'] = self.sens_slider.value()
        self.settings_changed.emit(self.settings)

    def _handle_stop(self):
        self.status_label.setText("[● STOPPED]")
        self.stop_clicked.emit()

    def _handle_upload(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Sounds", "", "Audio Files (*.mp3 *.wav)")
        if files:
            # We determine where to copy based on selected pack
            target_folder = os.path.join("sounds", "thud", self.settings['selected_sound_type'])
            os.makedirs(target_folder, exist_ok=True)
            for f in files:
                try:
                    shutil.copy(f, target_folder)
                    self.add_log_entry(f"Uploaded: {os.path.basename(f)}")
                except Exception as e:
                    print(f"Error copying file: {e}")

    def add_log_entry(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        entry = QLabel(f"> {timestamp} — {message}")
        entry.setStyleSheet("font-size: 11px; color: #ff2222; border: none;")
        self.log_layout.insertWidget(0, entry)
        if self.log_layout.count() > 50:
            item = self.log_layout.takeAt(50)
            if item.widget(): item.widget().deleteLater()
        self.visualizer.flash()

    def update_rms(self, level):
        self.visualizer.set_level(level)
