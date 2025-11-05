import cv2
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QGroupBox, QGridLayout,
                             QComboBox, QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QFont
from src.camera_widget import CameraWidget
from src.arduino_controller import ArduinoController

class DiamondViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HARBOR Diamond Viewer")
        self.setGeometry(100, 100, 1600, 1000)
        
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
        self.apply_professional_theme()
        self.init_cameras()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Professional header bar
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Camera section
        camera_section = self.create_camera_section()
        content_layout.addWidget(camera_section, 7)
        
        # Control panel
        control_panel = self.create_control_panel()
        content_layout.addWidget(control_panel, 3)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
    def create_header(self):
        """Create professional header with branding"""
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(90)
        header.setStyleSheet("""
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #1a1a2e);
                border-bottom: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E91E63, stop:0.33 #9C27B0, stop:0.66 #2196F3, stop:1 #E91E63);
            }
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 0, 30, 0)
        header.setLayout(header_layout)
        
        # Left side - Logo and title
        left_section = QHBoxLayout()
        
        # Company branding with accent dots
        brand_container = QWidget()
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(12)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_container.setLayout(brand_layout)
        
        # Accent dots
        dots_widget = QWidget()
        dots_layout = QHBoxLayout()
        dots_layout.setSpacing(4)
        dots_layout.setContentsMargins(0, 0, 0, 0)
        dots_widget.setLayout(dots_layout)
        
        for color in ['#E91E63', '#9C27B0', '#2196F3']:
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"""
                background-color: {color};
                border-radius: 6px;
            """)
            dots_layout.addWidget(dot)
        
        brand_layout.addWidget(dots_widget)
        
        # Harbor text
        harbor_label = QLabel("HARBOR")
        harbor_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: white;
            letter-spacing: 6px;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        brand_layout.addWidget(harbor_label)
        
        left_section.addWidget(brand_container)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); max-width: 2px;")
        left_section.addWidget(divider)
        
        # Subtitle
        subtitle = QLabel("Diamond Inspection System")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #B0B0B0;
            font-weight: 400;
            margin-left: 5px;
        """)
        left_section.addWidget(subtitle)
        left_section.addStretch()
        
        header_layout.addLayout(left_section)
        
        # Right side - Connection status
        self.header_status = QLabel("● System Ready")
        self.header_status.setStyleSheet("""
            font-size: 14px;
            color: #FFA726;
            font-weight: 600;
            padding: 8px 16px;
            background-color: rgba(255, 167, 38, 0.1);
            border-radius: 16px;
            border: 1px solid rgba(255, 167, 38, 0.3);
        """)
        header_layout.addWidget(self.header_status)
        
        return header
        
    def create_camera_section(self):
        """Create camera viewing area with professional styling"""
        section = QFrame()
        section.setObjectName("cameraSection")
        section.setStyleSheet("""
            #cameraSection {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        section.setLayout(layout)
        
        # Camera container
        self.camera_container = QWidget()
        self.split_layout = QVBoxLayout()
        self.split_layout.setSpacing(12)
        self.camera_container.setLayout(self.split_layout)
        
        self.top_camera_widget = CameraWidget("Top View Camera", 0)
        self.top_camera_widget.clicked.connect(lambda: self.toggle_fullscreen('top'))
        self.split_layout.addWidget(self.top_camera_widget)
        
        self.side_camera_widget = CameraWidget("Side View Camera (Girdle)", 1)
        self.side_camera_widget.clicked.connect(lambda: self.toggle_fullscreen('side'))
        self.split_layout.addWidget(self.side_camera_widget)
        
        layout.addWidget(self.camera_container)
        
        # Camera controls
        controls = QHBoxLayout()
        controls.setSpacing(10)
        
        btn_style = """
            QPushButton {
                font-size: 13px;
                font-weight: 600;
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 12px 20px;
                min-height: 44px;
            }
            QPushButton:hover {
                background-color: #353535;
                border-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """
        
        self.swap_button = QPushButton("⇄  Switch Views")
        self.swap_button.clicked.connect(self.swap_cameras)
        self.swap_button.setStyleSheet(btn_style)
        controls.addWidget(self.swap_button)
        
        self.fullscreen_button = QPushButton("⛶  Fullscreen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen_current)
        self.fullscreen_button.setStyleSheet(btn_style)
        controls.addWidget(self.fullscreen_button)
        
        layout.addLayout(controls)
        
        return section
    
    def create_control_panel(self):
        """Create professional control panel"""
        panel = QFrame()
        panel.setObjectName("controlPanel")
        panel.setStyleSheet("""
            #controlPanel {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        panel.setLayout(layout)
        
        # Connection section
        conn_section = self.create_connection_section()
        layout.addWidget(conn_section)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #333; max-height: 1px;")
        layout.addWidget(sep)
        
        # Controls title
        title = QLabel("POSITIONING CONTROLS")
        title.setStyleSheet("""
            font-size: 13px;
            font-weight: 700;
            color: #888;
            letter-spacing: 2px;
            padding: 10px 0;
        """)
        layout.addWidget(title)
        
        # Control groups
        control_style = """
            QPushButton {
                font-size: 13px;
                font-weight: 600;
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 16px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #353535;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """
        
        # Zoom Control
        zoom_group = self.create_control_group("🔍 ZOOM", control_style, [
            ("◀  Out", lambda: self.move_axis('X', -1), lambda: self.stop_axis('X')),
            ("In  ▶", lambda: self.move_axis('X', 1), lambda: self.stop_axis('X'))
        ])
        layout.addWidget(zoom_group)
        
        # Height Control
        height_group = self.create_control_group("↕  HEIGHT", control_style, [
            ("▼  Down", lambda: self.move_axis('Y', -1), lambda: self.stop_axis('Y')),
            ("Up  ▲", lambda: self.move_axis('Y', 1), lambda: self.stop_axis('Y'))
        ])
        layout.addWidget(height_group)
        
        # Rotation Control
        rotation_group = self.create_control_group("🔄 ROTATION", control_style, [
            ("↶  Left", lambda: self.rotate(-1), self.stop_rotation),
            ("Right  ↷", lambda: self.rotate(1), self.stop_rotation)
        ])
        layout.addWidget(rotation_group)
        
        layout.addStretch()
        
        # Footer info
        footer = QLabel("Press SPACE to switch • F for fullscreen • ESC to exit")
        footer.setStyleSheet("""
            font-size: 11px;
            color: #666;
            padding: 10px;
            text-align: center;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        return panel
    
    def create_connection_section(self):
        """Create connection control section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        section.setLayout(layout)
        
        self.connect_button = QPushButton("🔌  CONNECT SYSTEM")
        self.connect_button.clicked.connect(self.toggle_arduino_connection)
        self.connect_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 700;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 16px;
                min-height: 54px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        layout.addWidget(self.connect_button)
        
        self.connection_status = QLabel("● System Disconnected")
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setStyleSheet("""
            font-size: 13px;
            padding: 12px;
            color: #E57373;
            background-color: rgba(229, 115, 115, 0.1);
            border-radius: 8px;
            font-weight: 600;
            border: 1px solid rgba(229, 115, 115, 0.3);
        """)
        layout.addWidget(self.connection_status)
        
        return section
    
    def create_control_group(self, title, button_style, buttons):
        """Create a control group with title and buttons"""
        group = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        group.setLayout(layout)
        
        # Title
        label = QLabel(title)
        label.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #999;
            letter-spacing: 1px;
        """)
        layout.addWidget(label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        for btn_text, press_fn, release_fn in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet(button_style)
            btn.pressed.connect(press_fn)
            btn.released.connect(release_fn)
            btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)
        
        return group
        
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
        arduino_port = ArduinoController.find_arduino_port()
        
        if arduino_port:
            self.header_status.setText("● Arduino Detected")
            self.header_status.setStyleSheet("""
                font-size: 14px;
                color: #66BB6A;
                font-weight: 600;
                padding: 8px 16px;
                background-color: rgba(102, 187, 106, 0.1);
                border-radius: 16px;
                border: 1px solid rgba(102, 187, 106, 0.3);
            """)
        elif available_ports:
            self.header_status.setText(f"● {len(available_ports)} Port(s) Found")
        else:
            self.header_status.setText("● No Devices Found")
    
    def toggle_arduino_connection(self):
        if self.arduino.is_connected():
            self.arduino.disconnect()
            self.heartbeat_timer.stop()
            self.connect_button.setText("🔌  CONNECT SYSTEM")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: 700;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2196F3, stop:1 #1976D2);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 16px;
                    min-height: 54px;
                    letter-spacing: 1px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #42A5F5, stop:1 #2196F3);
                }
            """)
            self.connection_status.setText("● System Disconnected")
            self.connection_status.setStyleSheet("""
                font-size: 13px;
                padding: 12px;
                color: #E57373;
                background-color: rgba(229, 115, 115, 0.1);
                border-radius: 8px;
                font-weight: 600;
                border: 1px solid rgba(229, 115, 115, 0.3);
            """)
            self.header_status.setText("● System Ready")
            self.header_status.setStyleSheet("""
                font-size: 14px;
                color: #FFA726;
                font-weight: 600;
                padding: 8px 16px;
                background-color: rgba(255, 167, 38, 0.1);
                border-radius: 16px;
                border: 1px solid rgba(255, 167, 38, 0.3);
            """)
        else:
            port = ArduinoController.find_arduino_port()
            
            if not port:
                ports = ArduinoController.list_available_ports()
                if ports:
                    port = ports[0]
                else:
                    QMessageBox.warning(self, "No Device Found", 
                                      "Cannot find the system hardware.\n\n"
                                      "Please check:\n"
                                      "• System is plugged in via USB\n"
                                      "• Drivers are installed")
                    return
            
            if self.arduino.connect(port):
                self.connect_button.setText("✓  DISCONNECT")
                self.connect_button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        font-weight: 700;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #66BB6A, stop:1 #4CAF50);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        padding: 16px;
                        min-height: 54px;
                        letter-spacing: 1px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #81C784, stop:1 #66BB6A);
                    }
                """)
                self.connection_status.setText(f"● Connected to {port}")
                self.connection_status.setStyleSheet("""
                    font-size: 13px;
                    padding: 12px;
                    color: #66BB6A;
                    background-color: rgba(102, 187, 106, 0.1);
                    border-radius: 8px;
                    font-weight: 600;
                    border: 1px solid rgba(102, 187, 106, 0.3);
                """)
                self.header_status.setText("● System Connected")
                self.header_status.setStyleSheet("""
                    font-size: 14px;
                    color: #66BB6A;
                    font-weight: 600;
                    padding: 8px 16px;
                    background-color: rgba(102, 187, 106, 0.1);
                    border-radius: 16px;
                    border: 1px solid rgba(102, 187, 106, 0.3);
                """)
                self.heartbeat_timer.start(self.heartbeat_interval)
            else:
                QMessageBox.warning(self, "Connection Error", 
                                  f"Could not connect to the system.\n\n"
                                  "Please check:\n"
                                  "• System is powered on\n"
                                  "• USB cable is connected\n"
                                  "• No other program is using the system")
    
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
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.swap_cameras()
        elif event.key() == Qt.Key_F:
            self.toggle_fullscreen_current()
        elif event.key() == Qt.Key_Escape and self.fullscreen_mode:
            self.toggle_fullscreen(None)
    
    def apply_professional_theme(self):
        """Apply professional dark theme with modern aesthetics"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: #E0E0E0;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 8px 16px;
            }
        """)
    
    def closeEvent(self, event):
        self.arduino.disconnect()
        self.top_camera_widget.release_camera()
        self.side_camera_widget.release_camera()
        event.accept()