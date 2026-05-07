import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSlider, QScrollArea, QFrame,
    QSizePolicy
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
        
        # Background
        bg_color = QColor("#1a1a1a")
        if self.flash_active:
            bg_color = QColor("#ff2222")
        painter.fillRect(rect, bg_color)
        
        # Visualizer bar
        if not self.flash_active:
            bar_width = int(rect.width() * self.level)
            painter.fillRect(0, 0, bar_width, rect.height(), QColor("#ff2222"))
            
        # Grid lines (hacker look)
        painter.setPen(QPen(QColor("#333333"), 1))
        for x in range(0, rect.width(), 40):
            painter.drawLine(x, 0, x, rect.height())

class SpankYourWinUI(QMainWindow):
    stop_clicked = pyqtSignal()
    settings_changed = pyqtSignal(dict)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SpankYourWin — I can hear you")
        self.setFixedSize(400, 600)
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
            }
            QPushButton:checked {
                background-color: #ff2222;
                color: #0d0d0d;
            }
            QPushButton#STOP_BTN {
                background-color: #ff2222;
                color: #0d0d0d;
                font-size: 20px;
                border: none;
            }
            QSlider::groove:horizontal {
                border: 1px solid #ff2222;
                height: 4px;
                background: #1a1a1a;
            }
            QSlider::handle:horizontal {
                background: #ff2222;
                border: 1px solid #ff2222;
                width: 15px;
                margin: -5px 0;
            }
            QFrame#DIVIDER {
                background-color: #ff2222;
                max-height: 2px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("SPANK YOUR WIN\nv1.0.0")
        self.status_label = QLabel("[● ACTIVE]")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)

        divider = QFrame()
        divider.setObjectName("DIVIDER")
        layout.addWidget(divider)

        # Visualizer
        self.visualizer = WaveformBar()
        layout.addWidget(self.visualizer)

        divider2 = QFrame()
        divider2.setObjectName("DIVIDER")
        layout.addWidget(divider2)

        # Thud Detection
        thud_layout = QHBoxLayout()
        thud_label = QLabel("THUD DETECTION")
        self.thud_toggle = QPushButton("ON" if self.settings['thud_enabled'] else "OFF")
        self.thud_toggle.setCheckable(True)
        self.thud_toggle.setChecked(self.settings['thud_enabled'])
        self.thud_toggle.clicked.connect(self._toggle_thud)
        thud_layout.addWidget(thud_label)
        thud_layout.addStretch()
        thud_layout.addWidget(self.thud_toggle)
        layout.addLayout(thud_layout)

        # Sensitivity Slider
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(QLabel("Sensitivity"))
        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setMinimum(500)
        self.sens_slider.setMaximum(3000)
        self.sens_slider.setValue(self.settings['thud_threshold_low'])
        self.sens_slider.valueChanged.connect(self._on_sens_change)
        sens_layout.addWidget(self.sens_slider)
        layout.addLayout(sens_layout)

        # USB Detection
        usb_layout = QHBoxLayout()
        usb_label = QLabel("USB DETECTION")
        self.usb_toggle = QPushButton("ON" if self.settings['usb_enabled'] else "OFF")
        self.usb_toggle.setCheckable(True)
        self.usb_toggle.setChecked(self.settings['usb_enabled'])
        self.usb_toggle.clicked.connect(self._toggle_usb)
        usb_layout.addWidget(usb_label)
        usb_layout.addStretch()
        usb_layout.addWidget(self.usb_toggle)
        layout.addLayout(usb_layout)

        divider3 = QFrame()
        divider3.setObjectName("DIVIDER")
        layout.addWidget(divider3)

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

    def _toggle_thud(self):
        checked = self.thud_toggle.isChecked()
        self.thud_toggle.setText("ON" if checked else "OFF")
        self.settings['thud_enabled'] = checked
        self.settings_changed.emit(self.settings)

    def _toggle_usb(self):
        checked = self.usb_toggle.isChecked()
        self.usb_toggle.setText("ON" if checked else "OFF")
        self.settings['usb_enabled'] = checked
        self.settings_changed.emit(self.settings)

    def _on_sens_change(self):
        val = self.sens_slider.value()
        self.settings['thud_threshold_low'] = val
        # Automatically bump high threshold to be always higher than low
        self.settings['thud_threshold_high'] = val + 1500
        self.settings_changed.emit(self.settings)

    def _handle_stop(self):
        self.status_label.setText("[● STOPPED]")
        self.stop_clicked.emit()

    def add_log_entry(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        entry = QLabel(f"> {timestamp} — {message}")
        entry.setStyleSheet("font-size: 12px; color: #ff2222; border: none;")
        self.log_layout.insertWidget(0, entry) # Newest first
        
        # Keep log size to 50
        if self.log_layout.count() > 50:
            item = self.log_layout.takeAt(self.log_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()
        
        # Flash visualizer
        self.visualizer.flash()

    def update_rms(self, level):
        self.visualizer.set_level(level)
