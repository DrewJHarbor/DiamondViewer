# HARBOR Diamond Viewer

A simple, professional Windows application for viewing and inspecting diamonds with dual cameras and easy controls. Designed for non-technical operators.

## Features

### Camera System
- **Dual Camera Display**: See your diamond from top and side simultaneously
- **Clear Views**: High-quality real-time video optimized for diamond inspection
- **Switch Views**: Easy one-button camera swap
- **Fullscreen Mode**: Click any view to see it larger

### Simple Controls
- **One-Click Connection**: Just click "Connect System" - it finds your hardware automatically
- **Zoom**: Large "In" and "Out" buttons to adjust camera distance
- **Height**: "Up" and "Down" buttons to raise/lower the platform
- **Rotation**: "Left" and "Right" buttons to rotate the diamond
- **Manual Controls Work Too**: Your physical encoders and joystick still work while connected

### Professional Interface
- **Harbor Branding**: Clean, professional look with company logo
- **Large Buttons**: Easy to see and use
- **Clear Status**: Green when connected, red when disconnected
- **Dark Theme**: Optimized for viewing diamond details

## Installation

### Requirements
- Windows PC (tested on Windows 10/11)
- Python 3.11 or higher
- 2x USB cameras
- Arduino Mega 2560 with custom firmware
- USB cable for Arduino connection

### Setup

1. Install dependencies (automatically installed via uv/pip):
```bash
python -m pip install PyQt5 opencv-python pyserial
```

2. Connect your hardware:
   - Plug in both USB cameras
   - Connect Arduino Mega 2560 via USB
   - Note the COM port number (e.g., COM3, COM4)

3. Upload the Arduino firmware (see `arduino_example.ino`)

4. Run the application:
```bash
python main.py
```

## Usage

### Starting the Application

1. Launch the application: `python main.py`
2. You'll see the Harbor Diamond Viewer with dual camera views
3. Click the big blue **"Connect System"** button
   - The system automatically finds your hardware
   - Button turns green when connected
   - That's it! You're ready to use the controls
   - Click "Connect to Arduino"
   - Status should change to "Connected"

### Camera Controls

- **Split View**: Default mode shows both cameras
- **Fullscreen**: Click on either camera view to expand it
- **Swap Cameras**: Press `Space` key or click "Swap Cameras" button
- **Exit Fullscreen**: Press `Esc` or `F` key, or click the camera again

### Hardware Controls

#### X-Axis (Zoom Camera Rail)
- **Forward**: Click and hold "Forward ►►" button
- **Backward**: Click and hold "◄◄ Back" button
- Release button to stop movement

#### Y-Axis (Base Height)
- **Up**: Click and hold "Up ▲▲" button
- **Down**: Click and hold "▼▼ Down" button
- Release button to stop movement

#### Rotation
- **Clockwise**: Click and hold "CW ↷" button
- **Counter-Clockwise**: Click and hold "↶ CCW" button
- Release button to stop rotation

#### Lighting
- Adjust the slider to set lighting intensity (0-100%)
- Changes apply in real-time

### Keyboard Shortcuts

- `Space`: Swap camera views
- `F`: Toggle fullscreen mode
- `Esc`: Exit fullscreen mode

## Arduino Communication Protocol

The application sends simple text commands over serial to control the hardware:

### Movement Commands
- `X_FORWARD`: Move zoom camera forward
- `X_BACK`: Move zoom camera backward
- `X_STOP`: Stop X-axis movement
- `Y_UP`: Raise base
- `Y_DOWN`: Lower base
- `Y_STOP`: Stop Y-axis movement

### Rotation Commands
- `ROTATE_CW`: Rotate clockwise
- `ROTATE_CCW`: Rotate counter-clockwise
- `ROTATE_STOP`: Stop rotation

### Lighting Command
- `LIGHT_<value>`: Set lighting intensity (0-100)
  - Example: `LIGHT_50` sets lighting to 50%

## Project Structure

```
diamond-viewer/
├── src/
│   ├── diamond_viewer.py      # Main application window
│   ├── camera_widget.py        # Camera display widgets
│   └── arduino_controller.py   # Serial communication
├── main.py                     # Application entry point
├── arduino_example.ino         # Arduino firmware example
├── README.md                   # This file
└── replit.md                   # Development notes
```

## Configuration

### Camera Indices
By default, cameras are assigned as:
- Camera 0: Top View
- Camera 1: Side View (Girdle)

If your cameras are detected in a different order, you can swap them using the "Swap Cameras" feature.

### COM Port
- The application automatically detects available COM ports on startup
- Use the "Refresh" button to rescan if you plug in the Arduino after launching
- The dropdown is editable for manual entry if auto-detection doesn't find your port
- Serial communication uses 9600 baud rate

## Troubleshooting

### Cameras Not Detected
- Verify cameras are plugged into USB ports
- Check Windows Device Manager to confirm cameras are recognized
- Try swapping camera indices if they appear in wrong order
- Some cameras may use different indices (try 0, 1, 2)

### Arduino Connection Failed
- Verify Arduino is plugged in via USB
- Check the correct COM port is selected
- Ensure no other program is using the serial port
- Try unplugging and replugging the Arduino
- Verify Arduino firmware is uploaded correctly

### Performance Issues
- Close other applications using webcams (Zoom, Skype, etc.)
- Reduce lighting effects if system is slow
- Ensure adequate lighting for camera capture
- Check USB connections are secure

## Future Enhancements

- Touch screen support with gesture controls
- Preset position saving and recall
- Image capture and annotation tools
- Automated scanning sequences
- Encoder feedback integration
- Lighting presets for different diamond types
- Video recording capabilities

## Technical Details

- **Framework**: PyQt5
- **Camera Handling**: OpenCV (cv2)
- **Serial Communication**: PySerial
- **Update Rate**: 30 FPS camera refresh
- **Serial Baud Rate**: 9600
- **Supported OS**: Windows 10/11

## License

Proprietary - Internal use only

## Support

For technical support or questions, please contact your system administrator.
