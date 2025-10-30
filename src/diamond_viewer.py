import cv2
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QGroupBox, QGridLayout,
                             QComboBox, QMessageBox, QFrame)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from src.camera_widget import CameraWidget
from src.arduino_controller import ArduinoController

class DiamondViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HARBOR Diamond Viewer")
        self.setGeometry(100, 100, 1400, 900)
        
        self.camera_top = None
        self.camera_side = None
        self.fullscreen_mode = False
        self.active_camera = None
        
        self.arduino = ArduinoController()
        
        # Heartbeat timer to keep connection alive
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)
        self.heartbeat_interval = 15000  # 15 seconds
        
        self.init_ui()
        self.apply_dark_theme()
        self.init_cameras()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        camera_layout = QVBoxLayout()
        
        # Harbor branding header
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_widget.setLayout(header_layout)
        
        # Company name with accent squares
        brand_container = QWidget()
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(0, 10, 0, 10)
        brand_container.setLayout(brand_layout)
        
        brand_layout.addStretch()
        
        # Harbor text
        harbor_label = QLabel("HARBOR")
        harbor_label.setAlignment(Qt.AlignCenter)
        harbor_label.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold; 
            color: white;
            letter-spacing: 8px;
            padding: 0px;
            margin: 0px;
        """)
        brand_layout.addWidget(harbor_label)
        
        # Colored accent squares
        accent_container = QWidget()
        accent_layout = QHBoxLayout()
        accent_layout.setContentsMargins(10, 0, 0, 0)
        accent_layout.setSpacing(2)
        accent_container.setLayout(accent_layout)
        
        # Pink square
        pink_square = QLabel()
        pink_square.setFixedSize(15, 15)
        pink_square.setStyleSheet("background-color: #E91E63; border-radius: 2px;")
        accent_layout.addWidget(pink_square)
        
        # Purple square
        purple_square = QLabel()
        purple_square.setFixedSize(15, 15)
        purple_square.setStyleSheet("background-color: #9C27B0; border-radius: 2px;")
        accent_layout.addWidget(purple_square)
        
        # Blue square
        blue_square = QLabel()
        blue_square.setFixedSize(15, 15)
        blue_square.setStyleSheet("background-color: #2196F3; border-radius: 2px;")
        accent_layout.addWidget(blue_square)
        
        brand_layout.addWidget(accent_container)
        brand_layout.addStretch()
        
        header_layout.addWidget(brand_container)
        
        # Subtitle
        subtitle = QLabel("Diamond Viewer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18px; color: #AAA; padding: 5px;")
        header_layout.addWidget(subtitle)
        
        camera_layout.addWidget(header_widget)
        
        self.camera_container = QWidget()
        self.split_layout = QVBoxLayout()
        self.camera_container.setLayout(self.split_layout)
        
        self.top_camera_widget = CameraWidget("Top View Camera", 0)
        self.top_camera_widget.clicked.connect(lambda: self.toggle_fullscreen('top'))
        self.split_layout.addWidget(self.top_camera_widget)
        
        self.side_camera_widget = CameraWidget("Side View Camera (Girdle)", 1)
        self.side_camera_widget.clicked.connect(lambda: self.toggle_fullscreen('side'))
        self.split_layout.addWidget(self.side_camera_widget)
        
        camera_layout.addWidget(self.camera_container)
        
        button_layout = QHBoxLayout()
        
        self.swap_button = QPushButton("🔄 Switch Views")
        self.swap_button.clicked.connect(self.swap_cameras)
        self.swap_button.setMinimumHeight(45)
        self.swap_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #424242;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        button_layout.addWidget(self.swap_button)
        
        self.fullscreen_button = QPushButton("⛶ Fullscreen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen_current)
        self.fullscreen_button.setMinimumHeight(45)
        self.fullscreen_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #424242;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        button_layout.addWidget(self.fullscreen_button)
        
        camera_layout.addLayout(button_layout)
        
        main_layout.addLayout(camera_layout, 7)
        
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 3)
        
    def create_control_panel(self):
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_widget.setLayout(control_layout)
        
        control_layout.addSpacing(20)
        
        # Simplified connection section
        self.connect_button = QPushButton("🔌 Connect System")
        self.connect_button.clicked.connect(self.toggle_arduino_connection)
        self.connect_button.setMinimumHeight(50)
        self.connect_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #2196F3;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        control_layout.addWidget(self.connect_button)
        
        self.connection_status = QLabel("● Not Connected")
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setStyleSheet("""
            font-size: 14px;
            padding: 10px;
            color: #E53935;
            font-weight: bold;
        """)
        control_layout.addWidget(self.connection_status)
        
        control_layout.addSpacing(20)
        
        # Port combo (hidden by default, shown only if needed)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.setVisible(False)
        
        # Simplified control labels with larger buttons
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #424242;
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 15px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """
        
        # Zoom Control
        zoom_label = QLabel("🔍 Zoom")
        zoom_label.setAlignment(Qt.AlignCenter)
        zoom_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 15px 5px 5px 5px; color: #AAA;")
        control_layout.addWidget(zoom_label)
        
        x_buttons = QHBoxLayout()
        self.x_back_button = QPushButton("◀ Out")
        self.x_back_button.setStyleSheet(button_style)
        self.x_back_button.pressed.connect(lambda: self.move_axis('X', -1))
        self.x_back_button.released.connect(lambda: self.stop_axis('X'))
        x_buttons.addWidget(self.x_back_button)
        
        self.x_forward_button = QPushButton("In ▶")
        self.x_forward_button.setStyleSheet(button_style)
        self.x_forward_button.pressed.connect(lambda: self.move_axis('X', 1))
        self.x_forward_button.released.connect(lambda: self.stop_axis('X'))
        x_buttons.addWidget(self.x_forward_button)
        
        control_layout.addLayout(x_buttons)
        control_layout.addSpacing(15)
        
        # Height Control
        height_label = QLabel("↕️ Height")
        height_label.setAlignment(Qt.AlignCenter)
        height_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; color: #AAA;")
        control_layout.addWidget(height_label)
        
        y_buttons = QHBoxLayout()
        self.y_down_button = QPushButton("▼ Down")
        self.y_down_button.setStyleSheet(button_style)
        self.y_down_button.pressed.connect(lambda: self.move_axis('Y', -1))
        self.y_down_button.released.connect(lambda: self.stop_axis('Y'))
        y_buttons.addWidget(self.y_down_button)
        
        self.y_up_button = QPushButton("Up ▲")
        self.y_up_button.setStyleSheet(button_style)
        self.y_up_button.pressed.connect(lambda: self.move_axis('Y', 1))
        self.y_up_button.released.connect(lambda: self.stop_axis('Y'))
        y_buttons.addWidget(self.y_up_button)
        
        control_layout.addLayout(y_buttons)
        control_layout.addSpacing(15)
        
        # Rotation Control
        rotation_label = QLabel("🔄 Rotation")
        rotation_label.setAlignment(Qt.AlignCenter)
        rotation_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; color: #AAA;")
        control_layout.addWidget(rotation_label)
        
        rotation_buttons = QHBoxLayout()
        self.rotate_ccw_button = QPushButton("↶ Left")
        self.rotate_ccw_button.setStyleSheet(button_style)
        self.rotate_ccw_button.pressed.connect(lambda: self.rotate(-1))
        self.rotate_ccw_button.released.connect(self.stop_rotation)
        rotation_buttons.addWidget(self.rotate_ccw_button)
        
        self.rotate_cw_button = QPushButton("Right ↷")
        self.rotate_cw_button.setStyleSheet(button_style)
        self.rotate_cw_button.pressed.connect(lambda: self.rotate(1))
        self.rotate_cw_button.released.connect(self.stop_rotation)
        rotation_buttons.addWidget(self.rotate_cw_button)
        
        control_layout.addLayout(rotation_buttons)
        
        control_layout.addStretch()
        
        return control_widget
    
    def init_cameras(self):
        self.refresh_serial_ports()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)
        
    def update_frames(self):
        self.top_camera_widget.update_frame()
        self.side_camera_widget.update_frame()
        
    def toggle_fullscreen(self, camera):
        if self.fullscreen_mode:
            self.split_layout.addWidget(self.top_camera_widget)
            self.split_layout.addWidget(self.side_camera_widget)
            self.top_camera_widget.show()
            self.side_camera_widget.show()
            self.fullscreen_mode = False
            self.active_camera = None
        else:
            if camera == 'top':
                self.side_camera_widget.hide()
                self.active_camera = 'top'
            else:
                self.top_camera_widget.hide()
                self.active_camera = 'side'
            self.fullscreen_mode = True
    
    def toggle_fullscreen_current(self):
        if self.fullscreen_mode:
            self.toggle_fullscreen(None)
        else:
            self.toggle_fullscreen('top')
    
    def swap_cameras(self):
        if self.fullscreen_mode:
            if self.active_camera == 'top':
                self.toggle_fullscreen('side')
            else:
                self.toggle_fullscreen('top')
        else:
            temp_index_top = self.top_camera_widget.camera_index
            temp_index_side = self.side_camera_widget.camera_index
            
            self.top_camera_widget.set_camera_index(temp_index_side)
            self.side_camera_widget.set_camera_index(temp_index_top)
    
    def refresh_serial_ports(self):
        available_ports = ArduinoController.list_available_ports()
        arduino_port = ArduinoController.find_arduino_port()  # Auto-detect Arduino
        self.port_combo.clear()
        
        if available_ports:
            self.port_combo.addItems(available_ports)
            
            # Auto-select Arduino if found
            if arduino_port:
                index = self.port_combo.findText(arduino_port)
                if index >= 0:
                    self.port_combo.setCurrentIndex(index)
                    self.connection_status.setText(f"Status: Arduino auto-detected on {arduino_port}")
                    self.connection_status.setStyleSheet("padding: 5px; background-color: #006400; border-radius: 3px;")
                else:
                    self.connection_status.setText(f"Status: {len(available_ports)} port(s) found")
                    self.connection_status.setStyleSheet("padding: 5px; background-color: #555; border-radius: 3px;")
            else:
                self.connection_status.setText(f"Status: {len(available_ports)} port(s) found - Select Arduino")
                self.connection_status.setStyleSheet("padding: 5px; background-color: #555; border-radius: 3px;")
        else:
            self.port_combo.setPlaceholderText("Enter COM port manually (e.g., COM3)")
            self.connection_status.setText("Status: No ports detected - Enter manually")
            self.connection_status.setStyleSheet("padding: 5px; background-color: #8B4513; border-radius: 3px;")
    
    def toggle_arduino_connection(self):
        if self.arduino.is_connected():
            self.arduino.disconnect()
            self.heartbeat_timer.stop()
            self.connect_button.setText("🔌 Connect System")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.connection_status.setText("● Not Connected")
            self.connection_status.setStyleSheet("""
                font-size: 14px;
                padding: 10px;
                color: #E53935;
                font-weight: bold;
            """)
        else:
            # Auto-detect Arduino port
            port = ArduinoController.find_arduino_port()
            
            if not port:
                # Fallback to any available port
                ports = ArduinoController.list_available_ports()
                if ports:
                    port = ports[0]
                else:
                    QMessageBox.warning(self, "No Device Found", 
                                      "Cannot find the system hardware.\n\nPlease check:\n• System is plugged in via USB\n• Drivers are installed")
                    return
            
            if self.arduino.connect(port):
                self.connect_button.setText("✓ Disconnect")
                self.connect_button.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        font-weight: bold;
                        background-color: #4CAF50;
                        color: white;
                        border-radius: 8px;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #388E3C;
                    }
                """)
                self.connection_status.setText(f"● Connected")
                self.connection_status.setStyleSheet("""
                    font-size: 14px;
                    padding: 10px;
                    color: #4CAF50;
                    font-weight: bold;
                """)
                self.heartbeat_timer.start(self.heartbeat_interval)
            else:
                QMessageBox.warning(self, "Connection Error", 
                                  f"Could not connect to the system.\n\nPlease check:\n• System is powered on\n• USB cable is connected\n• No other program is using the system")
    
    def send_heartbeat(self):
        """Send periodic PING command to keep Arduino connection alive"""
        if self.arduino.is_connected():
            self.arduino.send_command("PING")
    
    def move_axis(self, axis, direction):
        self.arduino.move_axis(axis, direction)
    
    def stop_axis(self, axis):
        self.arduino.stop_axis(axis)
    
    def rotate(self, direction):
        self.arduino.rotate(direction)
    
    def stop_rotation(self):
        self.arduino.stop_rotation()
    
    def update_lighting(self, value):
        self.lighting_label.setText(f"Intensity: {value}%")
        self.arduino.set_lighting(value)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.swap_cameras()
        elif event.key() == Qt.Key_F:
            self.toggle_fullscreen_current()
        elif event.key() == Qt.Key_Escape and self.fullscreen_mode:
            self.toggle_fullscreen(None)
    
    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(220, 220, 220))
        palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0078D7;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: #3a3a3a;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078D7;
                border: 1px solid #0078D7;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #3a3a3a;
            }
            QComboBox:hover {
                border: 1px solid #0078D7;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ddd;
                margin-right: 5px;
            }
        """)
    
    def closeEvent(self, event):
        self.arduino.disconnect()
        self.top_camera_widget.release_camera()
        self.side_camera_widget.release_camera()
        event.accept()
