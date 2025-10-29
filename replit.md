# Diamond Viewer Control System

## Project Overview
This is a Windows desktop application for controlling a dual-camera Diamond Viewer system with Arduino-based hardware control. The application provides a professional interface for viewing diamonds from multiple angles while controlling motorized positioning and lighting systems.

## Important Note
**This application is designed to run on Windows PCs (not in Replit's Linux environment).** It requires:
- A Windows 10/11 PC (such as an Intel NUC)
- Physical USB cameras connected to the PC
- Arduino Mega 2560 connected via USB
- Display output (monitor)

The Replit environment is used for **development only** - the code cannot run here because:
1. No display server (headless Linux environment)
2. No physical USB cameras connected
3. No Arduino hardware connected

## Project Structure

### Core Application Files
- `main.py` - Application entry point
- `diamond_viewer.py` - Main window and UI logic
- `camera_widget.py` - Camera display widget with click handling
- `arduino_controller.py` - Serial communication with Arduino

### Documentation
- `README.md` - Complete user documentation
- `arduino_example.ino` - Arduino firmware example code

### Configuration
- `.gitignore` - Git ignore rules for Python projects
- `pyproject.toml` - Python project dependencies
- `.replit` - Replit configuration

## Features Implemented

### Camera System
✅ Dual USB camera support (OpenCV)
✅ Split-screen layout
✅ Click-to-fullscreen functionality
✅ Camera view swapping (Space key)
✅ Real-time video streaming at 30 FPS

### Hardware Control
✅ Arduino serial communication (PySerial)
✅ X-axis movement control (zoom camera rail)
✅ Y-axis movement control (base height)
✅ Rotation control (clockwise/counter-clockwise)
✅ Lighting intensity control (0-100%)

### User Interface
✅ Professional dark theme
✅ Intuitive button controls
✅ Real-time status indicators
✅ Keyboard shortcuts (Space, F, Esc)
✅ Connection status display

## Deployment Instructions

To deploy this application to a Windows PC:

1. **Copy all files** to the Windows machine:
   - main.py
   - src/ directory (with all .py files)
   - arduino_example.ino (for Arduino firmware)
   - README.md (for reference)

2. **Install Python 3.11+** on Windows

3. **Install dependencies**:
   ```cmd
   pip install PyQt5 opencv-python pyserial
   ```

4. **Upload Arduino firmware**:
   - Open `arduino_example.ino` in Arduino IDE
   - Adjust pin numbers based on your wiring
   - Upload to Arduino Mega 2560

5. **Connect hardware**:
   - Plug in both USB cameras
   - Connect Arduino via USB
   - Note the COM port (e.g., COM3)

6. **Run the application**:
   ```cmd
   python main.py
   ```

## Technical Details

- **Framework**: PyQt5 for GUI
- **Camera**: OpenCV (cv2) for USB camera capture
- **Serial**: PySerial for Arduino communication
- **Update Rate**: 30 FPS camera refresh
- **Baud Rate**: 9600 for Arduino serial
- **Python Version**: 3.11+

## Future Enhancements
- Touch screen support with gestures
- Preset position memory
- Image capture and annotation
- Automated scanning sequences
- Encoder position feedback
- Lighting presets
- Video recording

## Recent Changes
- 2025-10-29: Initial development completed
  - Created dual-camera viewer with split-screen
  - Implemented Arduino control interface with dynamic COM port discovery
  - Added dark theme UI optimized for diamond viewing
  - Created comprehensive documentation and Arduino example code
  - Fixed: Dynamic port scanning with refresh capability
  - Fixed: Manual COM port entry support when auto-detection fails
  - Fixed: Improved connection error handling and user feedback
