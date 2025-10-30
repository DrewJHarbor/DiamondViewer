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
        self.setWindowTitle("Diamond Viewer Control System")
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
        
        title_label = QLabel("Diamond Viewer System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        camera_layout.addWidget(title_label)
        
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
        self.swap_button = QPushButton("Swap Cameras (Space)")
        self.swap_button.clicked.connect(self.swap_cameras)
        self.swap_button.setMinimumHeight(40)
        button_layout.addWidget(self.swap_button)
        
        self.fullscreen_button = QPushButton("Toggle Fullscreen (F)")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen_current)
        self.fullscreen_button.setMinimumHeight(40)
        button_layout.addWidget(self.fullscreen_button)
        
        camera_layout.addLayout(button_layout)
        
        main_layout.addLayout(camera_layout, 7)
        
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 3)
        
    def create_control_panel(self):
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_widget.setLayout(control_layout)
        
        header = QLabel("Hardware Controls")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        control_layout.addWidget(header)
        
        arduino_group = QGroupBox("Arduino Connection")
        arduino_layout = QVBoxLayout()
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        port_layout.addWidget(self.port_combo)
        
        self.refresh_ports_button = QPushButton("Refresh")
        self.refresh_ports_button.clicked.connect(self.refresh_serial_ports)
        port_layout.addWidget(self.refresh_ports_button)
        arduino_layout.addLayout(port_layout)
        
        self.connect_button = QPushButton("Connect to Arduino")
        self.connect_button.clicked.connect(self.toggle_arduino_connection)
        arduino_layout.addWidget(self.connect_button)
        
        self.connection_status = QLabel("Status: Disconnected")
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setStyleSheet("padding: 5px; background-color: #8B0000; border-radius: 3px;")
        arduino_layout.addWidget(self.connection_status)
        
        arduino_group.setLayout(arduino_layout)
        control_layout.addWidget(arduino_group)
        
        x_axis_group = QGroupBox("X-Axis (Zoom Camera Rail)")
        x_layout = QVBoxLayout()
        
        x_buttons = QHBoxLayout()
        self.x_back_button = QPushButton("◄◄ Back")
        self.x_back_button.pressed.connect(lambda: self.move_axis('X', -1))
        self.x_back_button.released.connect(lambda: self.stop_axis('X'))
        x_buttons.addWidget(self.x_back_button)
        
        self.x_forward_button = QPushButton("Forward ►►")
        self.x_forward_button.pressed.connect(lambda: self.move_axis('X', 1))
        self.x_forward_button.released.connect(lambda: self.stop_axis('X'))
        x_buttons.addWidget(self.x_forward_button)
        
        x_layout.addLayout(x_buttons)
        
        self.x_position_label = QLabel("Position: 0")
        self.x_position_label.setAlignment(Qt.AlignCenter)
        x_layout.addWidget(self.x_position_label)
        
        x_axis_group.setLayout(x_layout)
        control_layout.addWidget(x_axis_group)
        
        y_axis_group = QGroupBox("Y-Axis (Base Height)")
        y_layout = QVBoxLayout()
        
        y_buttons = QHBoxLayout()
        self.y_down_button = QPushButton("▼▼ Down")
        self.y_down_button.pressed.connect(lambda: self.move_axis('Y', -1))
        self.y_down_button.released.connect(lambda: self.stop_axis('Y'))
        y_buttons.addWidget(self.y_down_button)
        
        self.y_up_button = QPushButton("Up ▲▲")
        self.y_up_button.pressed.connect(lambda: self.move_axis('Y', 1))
        self.y_up_button.released.connect(lambda: self.stop_axis('Y'))
        y_buttons.addWidget(self.y_up_button)
        
        y_layout.addLayout(y_buttons)
        
        self.y_position_label = QLabel("Position: 0")
        self.y_position_label.setAlignment(Qt.AlignCenter)
        y_layout.addWidget(self.y_position_label)
        
        y_axis_group.setLayout(y_layout)
        control_layout.addWidget(y_axis_group)
        
        rotation_group = QGroupBox("Rotation")
        rotation_layout = QVBoxLayout()
        
        rotation_buttons = QHBoxLayout()
        self.rotate_ccw_button = QPushButton("↶ CCW")
        self.rotate_ccw_button.pressed.connect(lambda: self.rotate(-1))
        self.rotate_ccw_button.released.connect(self.stop_rotation)
        rotation_buttons.addWidget(self.rotate_ccw_button)
        
        self.rotate_cw_button = QPushButton("CW ↷")
        self.rotate_cw_button.pressed.connect(lambda: self.rotate(1))
        self.rotate_cw_button.released.connect(self.stop_rotation)
        rotation_buttons.addWidget(self.rotate_cw_button)
        
        rotation_layout.addLayout(rotation_buttons)
        
        self.rotation_label = QLabel("Angle: 0°")
        self.rotation_label.setAlignment(Qt.AlignCenter)
        rotation_layout.addWidget(self.rotation_label)
        
        rotation_group.setLayout(rotation_layout)
        control_layout.addWidget(rotation_group)
        
        lighting_group = QGroupBox("Lighting Control")
        lighting_layout = QVBoxLayout()
        
        self.lighting_slider = QSlider(Qt.Horizontal)
        self.lighting_slider.setMinimum(0)
        self.lighting_slider.setMaximum(100)
        self.lighting_slider.setValue(50)
        self.lighting_slider.valueChanged.connect(self.update_lighting)
        lighting_layout.addWidget(self.lighting_slider)
        
        self.lighting_label = QLabel("Intensity: 50%")
        self.lighting_label.setAlignment(Qt.AlignCenter)
        lighting_layout.addWidget(self.lighting_label)
        
        lighting_group.setLayout(lighting_layout)
        control_layout.addWidget(lighting_group)
        
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
        self.port_combo.clear()
        
        if available_ports:
            self.port_combo.addItems(available_ports)
            self.connection_status.setText(f"Status: {len(available_ports)} port(s) found")
            self.connection_status.setStyleSheet("padding: 5px; background-color: #555; border-radius: 3px;")
        else:
            self.port_combo.setPlaceholderText("Enter COM port manually (e.g., COM3)")
            self.connection_status.setText("Status: No ports detected - Enter manually")
            self.connection_status.setStyleSheet("padding: 5px; background-color: #8B4513; border-radius: 3px;")
    
    def toggle_arduino_connection(self):
        if self.arduino.is_connected():
            self.arduino.disconnect()
            self.heartbeat_timer.stop()  # Stop heartbeat when disconnecting
            self.connect_button.setText("Connect to Arduino")
            self.connection_status.setText("Status: Disconnected")
            self.connection_status.setStyleSheet("padding: 5px; background-color: #8B0000; border-radius: 3px;")
        else:
            port = self.port_combo.currentText().strip()
            if not port:
                QMessageBox.warning(self, "No Port Selected", 
                                  "Please enter a COM port (e.g., COM3) or click 'Refresh' to scan for available ports.")
                return
            
            if self.arduino.connect(port):
                self.connect_button.setText("Disconnect")
                self.connection_status.setText(f"Status: Connected ({port})")
                self.connection_status.setStyleSheet("padding: 5px; background-color: #006400; border-radius: 3px;")
                self.heartbeat_timer.start(self.heartbeat_interval)  # Start heartbeat when connected
            else:
                self.connection_status.setText("Status: Connection failed")
                self.connection_status.setStyleSheet("padding: 5px; background-color: #8B0000; border-radius: 3px;")
                QMessageBox.warning(self, "Connection Error", 
                                  f"Failed to connect to Arduino on {port}\n\nPlease check:\n- Arduino is plugged in\n- Correct COM port selected\n- No other program is using the port")
    
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
