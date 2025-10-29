import sys
from PyQt5.QtWidgets import QApplication
from src.diamond_viewer import DiamondViewerApp

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    viewer = DiamondViewerApp()
    viewer.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
