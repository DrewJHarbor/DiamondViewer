# HARBOR Diamond Viewer - LattePanda Edition

## Project Overview
Professional diamond viewing system for LattePanda 3 Delta featuring dual USB cameras, wireless iOS/Android control via WiFi, customer video sharing, and automated motor positioning. Designed for non-technical jewelry store operators and their customers.

## Important Note
**This application is designed to run on LattePanda 3 Delta (Windows PC with integrated Arduino Leonardo).** It cannot run in Replit's environment because:
1. No display server (headless Linux environment)
2. No physical USB cameras connected
3. No Arduino hardware connected
4. Replit is for **development only** - deploy to LattePanda for production use

## Hardware Platform

### LattePanda 3 Delta
- **Windows 10/11** - Main operating system
- **Integrated Arduino Leonardo (ATmega32U4)** - Motor control microcontroller
- **WiFi Built-in** - For wireless mobile control
- **USB Ports** - For dual cameras
- **Display Output** - For customer-facing fullscreen viewer

### Connected Hardware
- 2x USB cameras (top view + girdle view)
- 3x stepper motors (rotation, X-axis zoom, Y-axis height)
- 3x rotary encoders (manual control)
- 1x joystick (optional manual control)

## Project Structure

```
harbor-diamond-viewer/
├── display_viewer.py              # Fullscreen display with QR codes
├── web_server.py                  # Flask + WebSocket server
├── LattePanda_Diamond_Viewer.ino  # Arduino Leonardo firmware
├── src/
│   └── arduino_controller.py      # Arduino serial communication
├── templates/
│   ├── control.html               # Mobile control interface
│   └── share.html                 # Customer sharing form
├── deployment/
│   ├── start_display.bat          # Auto-start display viewer
│   ├── start_web_server.bat       # Auto-start web server
│   └── set_static_ip.ps1          # Static IP configuration
├── recordings/                    # Video recordings folder
├── requirements.txt               # Python dependencies
└── README.md                      # Complete setup guide
```

## Architecture

**Display Layer:**
- PyQt5 fullscreen interface (customer-facing)
- Dual camera split-screen view
- Toggleable QR codes (Control + Share)
- Harbor branding

**Network Layer:**
- Flask web server (port 5000)
- WebSocket for real-time control (<100ms latency)
- CORS restricted to local networks
- Production-grade with eventlet

**Control Layer:**
- Mobile web interface (iOS/Android compatible)
- Touch-optimized buttons
- Auto-rotation feature (double-tap)
- 15-second heartbeat keepalive

**Hardware Layer:**
- Arduino Leonardo firmware (ATmega32U4)
- 3x stepper motor control
- 3x encoder manual override
- 30-second safety timeout

## Features Implemented

### Display Interface ✅
- Fullscreen dual-camera view (PyQt5 + OpenCV)
- Harbor branding with colored accents (#E91E63, #673AB7, #2196F3)
- Toggleable QR codes (hide/show to avoid blocking view)
- Dynamic IP detection (QR codes auto-update)
- Clean, button-free design

### Wireless Mobile Control ✅
- Touch-optimized web interface (50px+ buttons)
- Real-time WebSocket communication
- Zoom In/Out (X-axis motor)
- Height Up/Down (Y-axis motor)
- Rotation Left/Right
- **Double-tap rotation** = continuous auto-rotation
- Connection status indicator (green/red)
- Works on iOS, Android, tablets, phones

### Customer Video Sharing ✅
- Separate QR code for customers
- Mobile-friendly form (email/phone input)
- 30-second video recording from top camera
- Video saved locally (`recordings/` folder)
- **Ready for integration:**
  - GIA number OCR (Tesseract placeholder)
  - Email delivery (SendGrid/Resend placeholder)
  - SMS delivery (Twilio placeholder)

### Hardware Control ✅
- Arduino Leonardo firmware for LattePanda
- Hybrid control mode (wireless + encoders work simultaneously)
- 30-second command timeout (safety feature)
- Manual encoder override always active
- Auto-rotation support (continuous spinning)
- Non-blocking motor control

### Security Features ✅
- CORS restricted to local networks (192.168.*.*, 10.*.*.*)
- Production mode (debug=False)
- Eventlet async server for stability
- Static IP configuration (prevents QR code rotation)
- Windows Firewall configuration included
- 30-second timeout prevents runaway motors

## Deployment Instructions

### Quick Start (3 Steps)
1. **Upload Arduino firmware** → `LattePanda_Diamond_Viewer.ino` to Leonardo
2. **Set static IP** → Run `deployment/set_static_ip.ps1` as Administrator
3. **Enable auto-start** → Copy `.bat` files to Windows Startup folder

**Full instructions:** See `README.md` for complete setup guide.

### Installation Checklist
- [ ] Arduino IDE installed
- [ ] Arduino libraries installed (BasicStepperDriver, Encoder, Bounce2)
- [ ] Firmware uploaded to Leonardo
- [ ] Python 3.10+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Static IP configured
- [ ] Firewall rule added (port 5000)
- [ ] Auto-start shortcuts created
- [ ] Hardware wired correctly (see README.md)
- [ ] Both cameras connected via USB
- [ ] System tested (QR codes work from phone)

## Technical Specifications

**Software Stack:**
- OS: Windows 10/11
- Display: PyQt5 5.15.10
- Video: OpenCV 4.9.0
- Web Framework: Flask 3.1.2 + Flask-SocketIO 5.5.1
- WebSocket: python-socketio 5.14.3
- Async Server: eventlet 0.40.3
- QR Generation: qrcode 8.2
- Arduino: PySerial 3.5
- Python: 3.10+

**Performance:**
- Video frame rate: 30 FPS per camera
- Control latency: <100ms (WebSocket)
- QR code generation: <1 second
- Video recording: 30 seconds exactly
- Motor response: Instant (non-blocking)

**Security:**
- CORS: Local network only
- Timeout: 30 seconds
- Firewall: Windows Defender configured
- WiFi: WPA2/WPA3 required

## Communication Protocols

### WebSocket Events (Client → Server)
- `arduino_connect` - Connect to Arduino
- `move_axis` - Move X/Y axis (params: axis, direction)
- `stop_axis` - Stop X/Y axis (params: axis)
- `rotate` - Single rotation (params: direction)
- `auto_rotate` - Continuous rotation (params: direction)
- `stop_rotation` - Stop rotation
- `heartbeat` - Keep connection alive

### WebSocket Events (Server → Client)
- `status` - System status update
- `connected` - Connection established
- `disconnected` - Connection lost
- `error` - Error message

### Arduino Serial Commands
- `X_FORWARD`, `X_BACK`, `X_STOP`
- `Y_UP`, `Y_DOWN`, `Y_STOP`
- `ROTATE_CW`, `ROTATE_CCW`, `ROTATE_STOP`
- `AUTO_ROTATE_CW`, `AUTO_ROTATE_CCW`, `AUTO_ROTATE_STOP`
- `PING` - Heartbeat

### HTTP Endpoints
- `GET /` - Landing page
- `GET /control` - Mobile control interface
- `GET /share` - Customer sharing form
- `GET /api/status` - System status
- `POST /api/video/record` - Start video recording
- `GET /api/video/<id>` - Retrieve recorded video
- `POST /api/share` - Send video via email/SMS

## User Preferences

- **Control Style:** Large touch buttons (50px+ height) for mobile
- **Display Design:** Clean fullscreen with no controls (QR codes toggleable)
- **Network:** WiFi-based (not Bluetooth) for iOS/Android compatibility
- **Security:** Local WiFi only, never expose to internet
- **Safety:** 30-second timeout, manual encoder override always active
- **Branding:** Harbor colors (#E91E63, #673AB7, #2196F3)

## Recent Changes

### 2025-11-05: LattePanda Migration & Wireless Control
- ✅ Migrated from PC + Arduino Mega → LattePanda 3 Delta + Leonardo
- ✅ Created fullscreen display-only viewer with toggleable QR codes
- ✅ Built Flask + WebSocket web server with production security
- ✅ Developed mobile control interface with auto-rotation
- ✅ Implemented customer video sharing workflow
- ✅ Updated Arduino firmware for Leonardo (ATmega32U4)
- ✅ Created deployment package with auto-start scripts
- ✅ Consolidated all setup guides into single README.md
- ✅ Added security best practices documentation
- ✅ Fixed NumPy compatibility (downgraded to <2.0 for OpenCV)

### 2025-10-30: Initial PC Version
- ✅ Created dual-camera viewer with control buttons
- ✅ Implemented Arduino Mega 2560 communication
- ✅ Added manual encoder control support

## Future Enhancements

### Pending Features (Ready for Integration)
- GIA number OCR (Tesseract) - placeholder in place
- Email delivery (SendGrid/Resend) - placeholder in place
- SMS delivery (Twilio) - placeholder in place

### Planned Features
- Snapshot capture from cameras
- Video library management
- Customer database
- Analytics dashboard
- Cloud backup integration

## Development Notes

### Why LattePanda 3 Delta?
- All-in-one solution (Windows PC + Arduino in one device)
- Integrated Leonardo eliminates need for separate Arduino board
- Compact form factor suitable for jewelry store counters
- Built-in WiFi for wireless control
- Sufficient performance for dual camera + web server

### Why QR Codes Instead of Typing IP?
- Faster for non-technical operators
- No typos or confusion
- Works immediately after scanning
- Dynamic IP detection prevents configuration issues

### Why No Authentication?
- Physical proximity required (must scan QR code)
- WiFi password provides access control
- Faster customer experience
- Enterprise authentication available if needed

### Why Local Network Only?
- Security: Prevents internet exposure
- Privacy: Videos stored locally only
- Reliability: No cloud dependencies
- Performance: Low latency control

## Testing

**Arduino Serial Monitor (9600 baud):**
- Verify firmware upload successful
- Check command acknowledgments
- Monitor encoder positions
- Debug motor issues

**Browser DevTools:**
- Check WebSocket connection
- Monitor event transmission
- Debug mobile interface
- Test QR code scanning

**Windows Event Viewer:**
- Monitor network access
- Check for security issues
- Review system logs

## Support

**Troubleshooting:**
- See README.md Troubleshooting section
- Check Arduino Serial Monitor (9600 baud)
- Review Flask server console logs
- Test components individually

**Documentation:**
- README.md - Complete setup guide
- requirements.txt - Python dependencies
- LattePanda_Diamond_Viewer.ino - Arduino firmware

**Contact:**
- For technical support, refer to README.md
- For security issues, see README.md Security section
