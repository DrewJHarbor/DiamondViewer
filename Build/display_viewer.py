"""
HARBOR Diamond Viewer - Display Only
Fullscreen dual camera viewer with Harbor branding and toggleable QR codes
Integrated with Flask web server for mobile control
"""

import sys
import cv2
import socket
import qrcode
import threading
import os
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

# Import web server to run in background
try:
    from web_server import start_web_server
    WEB_SERVER_AVAILABLE = True
except ImportError:
    WEB_SERVER_AVAILABLE = False
    print("Warning: web_server.py not found - mobile control will not be available")


class CameraWidget(QWidget):
    """Widget for displaying camera feed"""
    
    def __init__(self, camera_index=0, title="Camera"):
        super().__init__()
        self.camera_index = camera_index
        self.title = title
        self.camera = None
        
        self.init_ui()
        self.init_camera()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Camera display label
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #000000;")
        self.camera_label.setScaledContents(True)
        layout.addWidget(self.camera_label)
        
        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def init_camera(self):
        """Initialize camera capture"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.timer.start(33)  # ~30 FPS
            else:
                self.show_error(f"Camera {self.camera_index} not available")
        except Exception as e:
            self.show_error(f"Error opening camera: {str(e)}")
    
    def update_frame(self):
        """Update camera frame"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Display in label
                pixmap = QPixmap.fromImage(qt_image)
                self.camera_label.setPixmap(pixmap)
    
    def show_error(self, message):
        """Show error message"""
        self.camera_label.setText(f"{self.title}\n\n{message}")
        self.camera_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ff5252;
            font-size: 16px;
            padding: 20px;
        """)
    
    def cleanup(self):
        """Release camera resources"""
        if self.timer.isActive():
            self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None


class DisplayViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HARBOR Diamond Viewer")
        self.showFullScreen()
        
        self.camera_top = None
        self.camera_side = None
        
        # QR code visibility states
        self.control_qr_visible = False
        self.share_qr_visible = False
        
        self.init_ui()
        self.init_cameras()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Harbor branding header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Camera display area
        camera_container = QWidget()
        camera_container.setStyleSheet("background-color: #000000;")
        camera_layout = QHBoxLayout(camera_container)
        camera_layout.setContentsMargins(0, 0, 0, 0)
        camera_layout.setSpacing(2)
        
        # Top camera
        self.top_camera_widget = CameraWidget(0, "Top View")
        camera_layout.addWidget(self.top_camera_widget)
        
        # Side camera
        self.side_camera_widget = CameraWidget(1, "Girdle View")
        camera_layout.addWidget(self.side_camera_widget)
        
        main_layout.addWidget(camera_container)
        
        # QR code overlay containers (hidden by default)
        self.create_qr_overlays()
        
    def create_header(self):
        """Create Harbor branded header with QR toggle buttons"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a1a, stop:1 #2d2d2d);
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Harbor logo/branding
        branding_layout = QHBoxLayout()
        
        harbor_text = QLabel("HARBOR")
        harbor_text.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            letter-spacing: 2px;
        """)
        branding_layout.addWidget(harbor_text)
        
        # Colored squares accent
        colors = ["#E91E63", "#9C27B0", "#2196F3"]
        for color in colors:
            square = QLabel()
            square.setFixedSize(12, 12)
            square.setStyleSheet(f"background-color: {color}; margin-left: 5px;")
            branding_layout.addWidget(square)
        
        branding_layout.addStretch()
        layout.addLayout(branding_layout)
        
        layout.addStretch()
        
        # QR toggle buttons
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #424242;
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 12px 20px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
        """
        
        self.control_qr_button = QPushButton("📱 Control")
        self.control_qr_button.setStyleSheet(button_style)
        self.control_qr_button.clicked.connect(self.toggle_control_qr)
        layout.addWidget(self.control_qr_button)
        
        self.share_qr_button = QPushButton("📤 Share")
        self.share_qr_button.setStyleSheet(button_style)
        self.share_qr_button.clicked.connect(self.toggle_share_qr)
        layout.addWidget(self.share_qr_button)
        
        return header
    
    def create_qr_overlays(self):
        """Create QR code overlay widgets"""
        # Control QR overlay
        self.control_qr_overlay = QLabel(self.centralWidget())
        self.control_qr_overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 200);
            border: 3px solid #2196F3;
            border-radius: 10px;
            padding: 20px;
        """)
        self.control_qr_overlay.setAlignment(Qt.AlignCenter)
        self.control_qr_overlay.hide()
        
        # Share QR overlay
        self.share_qr_overlay = QLabel(self.centralWidget())
        self.share_qr_overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 200);
            border: 3px solid #E91E63;
            border-radius: 10px;
            padding: 20px;
        """)
        self.share_qr_overlay.setAlignment(Qt.AlignCenter)
        self.share_qr_overlay.hide()
        
    def init_cameras(self):
        """Start camera update timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(33)  # ~30 FPS
        
    def update_frames(self):
        """Update both camera feeds"""
        self.top_camera_widget.update_frame()
        self.side_camera_widget.update_frame()
        
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def generate_qr_code(self, url, title):
        """Generate QR code image for given URL"""
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QPixmap
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qimage = QImage()
        qimage.loadFromData(buffer.read())
        
        # Create pixmap with text
        pixmap = QPixmap.fromImage(qimage).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Add title text
        label_pixmap = QPixmap(350, 380)
        label_pixmap.fill(Qt.transparent)
        
        from PyQt5.QtGui import QPainter
        painter = QPainter(label_pixmap)
        painter.drawPixmap(25, 0, pixmap)
        
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(0, 330, 350, 50, Qt.AlignCenter, title)
        painter.end()
        
        return label_pixmap
    
    def toggle_control_qr(self):
        """Toggle control QR code visibility"""
        self.control_qr_visible = not self.control_qr_visible
        
        if self.control_qr_visible:
            ip = self.get_local_ip()
            url = f"http://{ip}:5000/control"
            pixmap = self.generate_qr_code(url, "Scan to Control")
            self.control_qr_overlay.setPixmap(pixmap)
            
            # Position in bottom-left corner
            overlay_width = 390
            overlay_height = 420
            x = 20
            y = self.height() - overlay_height - 20
            self.control_qr_overlay.setGeometry(x, y, overlay_width, overlay_height)
            self.control_qr_overlay.show()
            self.control_qr_overlay.raise_()
            
            self.control_qr_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #2196F3;
                    color: white;
                    border: 2px solid #1976D2;
                    border-radius: 8px;
                    padding: 12px 20px;
                    margin-left: 10px;
                }
            """)
        else:
            self.control_qr_overlay.hide()
            self.control_qr_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #424242;
                    color: white;
                    border: 2px solid #555;
                    border-radius: 8px;
                    padding: 12px 20px;
                    margin-left: 10px;
                }
                QPushButton:hover {
                    background-color: #555;
                    border-color: #777;
                }
            """)
    
    def toggle_share_qr(self):
        """Toggle share QR code visibility"""
        self.share_qr_visible = not self.share_qr_visible
        
        if self.share_qr_visible:
            ip = self.get_local_ip()
            url = f"http://{ip}:5000/share"
            pixmap = self.generate_qr_code(url, "Scan to Receive Video")
            self.share_qr_overlay.setPixmap(pixmap)
            
            # Position in bottom-right corner
            overlay_width = 390
            overlay_height = 420
            x = self.width() - overlay_width - 20
            y = self.height() - overlay_height - 20
            self.share_qr_overlay.setGeometry(x, y, overlay_width, overlay_height)
            self.share_qr_overlay.show()
            self.share_qr_overlay.raise_()
            
            self.share_qr_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #E91E63;
                    color: white;
                    border: 2px solid #C2185B;
                    border-radius: 8px;
                    padding: 12px 20px;
                    margin-left: 10px;
                }
            """)
        else:
            self.share_qr_overlay.hide()
            self.share_qr_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #424242;
                    color: white;
                    border: 2px solid #555;
                    border-radius: 8px;
                    padding: 12px 20px;
                    margin-left: 10px;
                }
                QPushButton:hover {
                    background-color: #555;
                    border-color: #777;
                }
            """)
    
    def resizeEvent(self, event):
        """Handle window resize to reposition QR codes"""
        super().resizeEvent(event)
        # Safety check: only reposition if QR visibility flags exist
        if hasattr(self, 'control_qr_visible') and self.control_qr_visible:
            self.toggle_control_qr()
            self.toggle_control_qr()
        if hasattr(self, 'share_qr_visible') and self.share_qr_visible:
            self.toggle_share_qr()
            self.toggle_share_qr()
    
    def keyPressEvent(self, a0):
        """Handle keyboard shortcuts"""
        if a0.key() == Qt.Key_Escape:
            self.close()
        elif a0.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
    
    def closeEvent(self, a0):
        """Cleanup on close"""
        self.top_camera_widget.release()
        self.side_camera_widget.release()
        
        # Web server will automatically stop when main thread exits
        print("Shutting down HARBOR Diamond Viewer...")


def main():
    # Start web server in background thread
    if WEB_SERVER_AVAILABLE:
        web_server_thread = threading.Thread(target=start_web_server, daemon=True)
        web_server_thread.start()
        print("✓ Web server started in background")
    else:
        print("⚠ Web server not available - mobile control disabled")
    
    # Start PyQt5 display application
    app = QApplication(sys.argv)
    viewer = DisplayViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
