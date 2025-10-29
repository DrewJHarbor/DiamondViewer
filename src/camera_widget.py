import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QCursor, QMouseEvent

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class CameraWidget(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, title, camera_index):
        super().__init__()
        self.title = title
        self.camera_index = camera_index
        self.camera = None
        self.default_image = None
        
        self.init_ui()
        self.init_camera()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            padding: 5px;
            background-color: #1e1e1e;
            border-radius: 3px;
        """)
        layout.addWidget(self.title_label)
        
        self.frame_label = ClickableLabel()
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setMinimumSize(640, 480)
        self.frame_label.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #555;
            border-radius: 5px;
        """)
        self.frame_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.frame_label.clicked.connect(self.on_click)
        layout.addWidget(self.frame_label)
        
        self.show_no_camera_message()
        
    def init_camera(self):
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                self.camera = None
        except:
            self.camera = None
    
    def set_camera_index(self, index):
        self.release_camera()
        self.camera_index = index
        self.init_camera()
    
    def update_frame(self):
        if self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    self.frame_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.frame_label.setPixmap(scaled_pixmap)
            else:
                self.show_no_camera_message()
        else:
            self.show_no_camera_message()
    
    def show_no_camera_message(self):
        self.frame_label.setText(f"Camera {self.camera_index} not available\n\nClick to expand view")
        self.frame_label.setStyleSheet("""
            background-color: #1a1a1a;
            border: 2px solid #555;
            border-radius: 5px;
            color: #888;
            font-size: 14px;
        """)
    
    def on_click(self):
        self.clicked.emit()
    
    def release_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
