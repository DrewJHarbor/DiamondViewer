# HARBOR Diamond Viewer - Complete Setup & User Guide

**LattePanda 3 Delta Edition with Wireless Mobile Control**

A professional diamond viewing system featuring dual USB cameras, wireless iOS/Android control, customer video sharing, and automated motor positioning.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Hardware Requirements](#hardware-requirements)
4. [Installation](#installation)
5. [Network Configuration](#network-configuration)
6. [Auto-Start Setup](#auto-start-setup)
7. [Hardware Wiring](#hardware-wiring)
8. [Usage Guide](#usage-guide)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## Quick Start

**Get running in 3 steps:**

1. **Upload Arduino Firmware** → `LattePanda_Diamond_Viewer.ino` to Leonardo
2. **Set Static IP** → Run `deployment/set_static_ip.ps1` as Administrator
3. **Enable Auto-Start** → Copy `.bat` files to Windows Startup folder

Then scan QR codes from your phone to control motors!

---

## System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LattePanda 3 Delta                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Windows 10/11                                      │    │
│  │  ┌──────────────────┐    ┌─────────────────────┐  │    │
│  │  │  Display Viewer  │    │   Flask Web Server  │  │    │
│  │  │  (PyQt5)         │    │   (Port 5000)       │  │    │
│  │  │  - Dual cameras  │    │   - WebSocket       │  │    │
│  │  │  - QR codes      │    │   - Video capture   │  │    │
│  │  │  - Harbor brand  │    │   - Motor control   │  │    │
│  │  └────────┬─────────┘    └──────────┬──────────┘  │    │
│  │           │                           │             │    │
│  │           └──────────┬────────────────┘             │    │
│  │                      │                              │    │
│  │              ┌───────▼────────┐                     │    │
│  │              │  Arduino        │                     │    │
│  │              │  Controller     │                     │    │
│  │              │  (Serial USB)   │                     │    │
│  │              └───────┬─────────┘                     │    │
│  └──────────────────────┼──────────────────────────────┘    │
│                         │                                    │
│    ┌────────────────────▼──────────────────────┐            │
│    │  Arduino Leonardo (ATmega32U4)            │            │
│    │  - Stepper motor control                  │            │
│    │  - Encoder/joystick input                 │            │
│    │  - Hybrid control mode                    │            │
│    │  - 30-second safety timeout               │            │
│    └────────┬──┬──┬──────────────────────┬──┬──┘            │
└─────────────┼──┼──┼──────────────────────┼──┼───────────────┘
              │  │  │                      │  │
         ┌────▼──▼──▼────┐          ┌─────▼──▼─────┐
         │ Stepper Motors │          │   Encoders   │
         │ - Rotation     │          │ - Manual     │
         │ - X-axis (zoom)│          │   control    │
         │ - Y-axis (height)│        │ - Joystick   │
         └────────────────┘          └──────────────┘

         ┌─────────────────────────┐
         │  WiFi Network (Local)   │
         │  - Static IP: 192.168.1.100
         │  - WPA2/WPA3 secured    │
         └──────────┬──────────────┘
                    │
         ┌──────────▼─────────────┐
         │  Mobile Devices        │
         │  (iOS/Android)         │
         │  - QR code scan        │
         │  - Touch control       │
         │  - Auto-rotation       │
         │  - Video sharing       │
         └────────────────────────┘
```

### Key Features

**Display Interface:**
- Fullscreen dual-camera view (top + girdle)
- Harbor branding with colored accents
- Toggleable QR codes (Control + Share)
- Clean, button-free design

**Wireless Control:**
- Touch-optimized mobile interface
- Real-time WebSocket (<100ms latency)
- Zoom In/Out, Height Up/Down, Rotation
- Double-tap for continuous auto-rotation
- 15-second heartbeat keepalive

**Customer Sharing:**
- QR code scan → sharing form
- 30-second video recording
- GIA number detection (OCR ready)
- Email/SMS delivery (integration ready)

**Safety Features:**
- 30-second command timeout
- Manual encoder override always active
- CORS restricted to local network
- Production-grade security

---

## Hardware Requirements

### Required Components

- **LattePanda 3 Delta** (with integrated Arduino Leonardo ATmega32U4)
- **2x USB Cameras** (top view + girdle view)
- **3x Stepper Motors** with drivers
- **3x Rotary Encoders** (for manual control)
- **1x Joystick module** (optional manual control)
- **Power supply** for motors and LattePanda

### Software Requirements

- **Windows 10/11** (pre-installed on LattePanda)
- **Python 3.10+**
- **Arduino IDE** (for uploading firmware)

---

## Installation

### Step 1: Arduino Firmware Installation

#### 1.1 Install Arduino IDE
1. Download from [arduino.cc](https://www.arduino.cc/en/software)
2. Install and launch Arduino IDE

#### 1.2 Install Required Libraries
In Arduino IDE, go to **Tools → Manage Libraries** and install:
- `BasicStepperDriver` (by laurb9)
- `Encoder` (by Paul Stoffregen)
- `Bounce2` (by Thomas O Fredericks)

#### 1.3 Upload Firmware to LattePanda Leonardo
1. Connect LattePanda to power
2. In Arduino IDE:
   - **Tools → Board → Arduino AVR Boards → Arduino Leonardo**
   - **Tools → Port → COM# (Arduino Leonardo)** (auto-detected)
3. Open `LattePanda_Diamond_Viewer.ino`
4. Click **Upload** (⮕ button)
5. Wait for "Done uploading" message

#### 1.4 Verify Firmware
1. Open **Tools → Serial Monitor**
2. Set baud rate to **9600**
3. You should see: `HARBOR Diamond Viewer - LattePanda Edition`

### Step 2: Python Software Installation

#### 2.1 Install Python Dependencies
Open PowerShell or Command Prompt:
```powershell
cd C:\path\to\harbor-diamond-viewer
pip install -r requirements.txt
```

This installs:
- PyQt5 (display interface)
- OpenCV (camera capture)
- Flask + Flask-SocketIO (web server)
- QRCode (dynamic QR generation)
- Pillow (image processing)
- PySerial (Arduino communication)
- Eventlet (production async server)

#### 2.2 Test Display Viewer
```powershell
python display_viewer.py
```
- You should see fullscreen dual camera view
- Harbor branding at top
- Click **📱 Control** or **📤 Share** buttons to see QR codes
- Press **ESC** to exit

#### 2.3 Test Web Server
Open a new PowerShell window:
```powershell
python web_server.py
```
- Server should start on `http://0.0.0.0:5000`
- Note the IP address shown in output

---

## Network Configuration

### Why Static IP?
Dynamic IP addresses change, breaking QR codes. Static IP ensures QR codes always work.

### Set Static IP (Recommended)

#### Automatic Method
1. **Right-click** on `deployment/set_static_ip.ps1`
2. Select **"Run with PowerShell"** (as Administrator)
3. Follow prompts:
   ```
   IP Address: 192.168.1.100  (example - choose based on your network)
   Subnet Mask: 255.255.255.0
   Default Gateway: 192.168.1.1  (your router IP)
   DNS Server: 8.8.8.8
   ```

#### Manual Method
1. Open **Settings → Network & Internet → WiFi → Properties**
2. Under **IP Settings**, click **Edit**
3. Select **Manual** and enable **IPv4**
4. Enter:
   - IP address: `192.168.1.100`
   - Subnet prefix length: `24`
   - Gateway: `192.168.1.1`
   - DNS: `8.8.8.8`

### Test Static IP
From your phone/tablet on same WiFi:
```
http://192.168.1.100:5000/control
```
You should see the mobile control interface.

### Configure Windows Firewall
Run as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Harbor Diamond Viewer" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private
```

---

## Auto-Start Setup

Configure both programs to start automatically when LattePanda boots.

### Create Startup Shortcuts

1. Press **Win + R**, type: `shell:startup`, press Enter
2. This opens the Startup folder
3. **Right-click** inside folder → **New → Shortcut**

**For Display Viewer:**
- Target: `C:\path\to\deployment\start_display.bat`
- Name: `Harbor Display`

**For Web Server:**
- Target: `C:\path\to\deployment\start_web_server.bat`
- Name: `Harbor Web Server`

### Edit BAT Files (Update Paths)

Edit `deployment/start_display.bat`:
```batch
@echo off
cd /d C:\path\to\harbor-diamond-viewer
python display_viewer.py
```

Edit `deployment/start_web_server.bat`:
```batch
@echo off
cd /d C:\path\to\harbor-diamond-viewer
python web_server.py
```

### Test Auto-Start
1. Restart LattePanda
2. Display viewer should launch fullscreen automatically
3. Web server should start in background
4. Test QR codes work from your phone

---

## Hardware Wiring

### LattePanda Leonardo Pin Connections

#### Stepper Motors
Connect to motor drivers, then to Leonardo:

**Motor 1 (Rotation Turntable):**
- PUL → Pin 8
- DIR → Pin 9

**Motor 2 (X-axis / Zoom Rail):**
- PUL → Pin 10
- DIR → Pin 11

**Motor 3 (Y-axis / Platform Height):**
- PUL → Pin 12
- DIR → Pin 13

#### Rotary Encoders

**Rotation Encoder:**
- CH_A → Pin 2
- CH_B → Pin 3
- Button → Pin 4

**X-axis Encoder:**
- CH_A → Pin 0
- CH_B → Pin 1
- Button → Pin 5

**Y-axis Encoder:**
- CH_A → Pin 7
- CH_B → Pin 6
- Button → Pin A0 (14)

#### Joystick (Optional)
- X-axis → Pin A1
- Y-axis → Pin A2
- Button → Pin A3

#### USB Cameras
- **Top camera** → USB port (usually Camera 0)
- **Girdle camera** → USB port (usually Camera 1)

### Power Connections
- **LattePanda:** 12V DC power adapter
- **Stepper motors:** Separate 12-24V power supply
- **Important:** Share ground between LattePanda and motor power supply

---

## Usage Guide

### Customer Viewing Workflow
1. **Customer approaches** → Display shows dual camera views
2. **Operator adjusts** → Uses encoders or mobile to position diamond
3. **Customer observes** → Clear view of diamond from top and side

### Mobile Control Workflow

#### Connect to Controls
1. **Operator clicks** "📱 Control" button on display
2. **QR code appears** in bottom-left corner
3. **Scan with phone** → Opens control interface automatically
4. **Touch controls** → Instant motor response via WebSocket

#### Control Features
- **Zoom In/Out** → Move camera rail forward/backward
- **Height Up/Down** → Raise/lower platform
- **Rotation Left/Right** → Rotate diamond
- **Double-tap rotation** → Continuous auto-rotation (keeps spinning)
- **Connection status** → Green = connected, Red = disconnected

#### Manual Override
- Physical encoders work simultaneously with wireless control
- No mode switching needed
- Turn encoders to manually adjust anytime

### Video Sharing Workflow

#### Customer Receives Video
1. **Customer requests video** of their diamond
2. **Operator clicks** "📤 Share" button on display
3. **QR code appears** in bottom-right corner
4. **Customer scans** → Opens sharing form
5. **Customer enters** email or phone number
6. **System records** 30-second video from top camera
7. **System detects** GIA number from girdle view (OCR)
8. **System sends** video link + GIA number

**Note:** Email/SMS delivery requires additional integration (SendGrid/Twilio).

### Keyboard Shortcuts

**Display Viewer:**
- **ESC** → Exit fullscreen
- **F11** → Toggle fullscreen
- **Control button** → Show/hide control QR code
- **Share button** → Show/hide share QR code

---

## Security

### Security Model

**Design Philosophy:**
- **Local WiFi Only** → Never expose to internet
- **Network Isolation** → CORS restricted to local networks
- **Physical Security** → LattePanda in secured location

### WiFi Network Requirements

✅ **Strong WPA2/WPA3 password** (minimum 12 characters)
✅ **Hidden SSID** (optional but recommended)
✅ **MAC address filtering** (optional for high-security)

### What's Protected

✅ Unauthorized internet access (server bound to local network)
✅ Cross-site request forgery (CORS restrictions)
✅ Runaway motors (30-second timeout)
✅ Connection loss (Arduino returns to manual mode)

### What Requires Physical Security

⚠️ WiFi password protection (keeps unauthorized users off network)
⚠️ Physical access to LattePanda (locked enclosure recommended)
⚠️ Router configuration (no port forwarding!)

### Router Configuration

**CRITICAL - Do NOT:**
- ❌ Port forward port 5000 to the internet
- ❌ Expose LattePanda to public WiFi
- ❌ Use weak WiFi passwords

**Recommended:**
- ✅ Enable router firewall
- ✅ Disable UPnP if not needed
- ✅ Use strong router admin password
- ✅ Review connected devices monthly

### CORS Restrictions

Web server only accepts connections from:
- `localhost` (testing)
- `127.0.0.1` (testing)
- `192.168.*.*` (typical home/office)
- `10.*.*.*` (corporate networks)

External websites **cannot** send commands to your system.

### Hardware Safety Features

**30-Second Timeout:**
- No commands for 30 seconds → motors stop
- Prevents runaway motors if connection lost
- Arduino returns to manual encoder control

**15-Second Heartbeat:**
- Mobile interface sends keepalive every 15 seconds
- Ensures timeout only triggers when truly disconnected

**Manual Override:**
- Physical encoders always work
- Joystick button forces manual mode
- Arduino reset button provides hard reset

### Security Checklist

**Before Deployment:**
- [ ] WiFi has strong WPA2/WPA3 password
- [ ] LattePanda in physically secured location
- [ ] Router NOT configured to port forward port 5000
- [ ] Windows Firewall enabled
- [ ] Static IP configured

**During Setup:**
- [ ] Run `set_static_ip.ps1` as Administrator
- [ ] Only trusted devices on WiFi network
- [ ] QR codes only work on local network
- [ ] Motors stop after 30-second timeout

**Operational:**
- [ ] Change WiFi password regularly (monthly recommended)
- [ ] Monitor Windows Event Viewer
- [ ] Keep Windows updated
- [ ] Backup recordings folder weekly
- [ ] Review router device list monthly

### Incident Response

**Suspected Unauthorized Access:**
1. Disconnect LattePanda from WiFi
2. Check Windows Event Viewer (`eventvwr.msc`)
3. Change WiFi password
4. Review router logs
5. Restart LattePanda

**Motor Malfunction:**
1. Press Arduino reset button (immediate stop)
2. Or power cycle motors
3. Check Serial Monitor for errors
4. Verify encoder connections

### Privacy & Compliance

**Data Storage:**
- Videos stored locally on LattePanda (`recordings/` folder)
- No cloud upload unless explicitly configured
- Email/SMS only sends links, not raw video

**Data Retention:**
Automatically delete videos older than 30 days:
```powershell
# Add to Windows Task Scheduler
forfiles /p "C:\path\to\recordings" /s /m *.mp4 /d -30 /c "cmd /c del @path"
```

**GDPR/Privacy:**
- Customers must consent before receiving video/SMS
- Include privacy notice on sharing form
- Provide method to delete customer data on request

---

## Troubleshooting

### QR Code Doesn't Work
**Symptoms:** QR code doesn't scan or opens wrong page

**Check:**
- Phone and LattePanda on same WiFi network?
- Static IP configured correctly?

**Fix:**
1. Verify static IP: `ipconfig` in PowerShell
2. Type IP manually: `http://192.168.1.100:5000/control`
3. Re-run `set_static_ip.ps1` if needed

### Motors Don't Respond to Mobile
**Symptoms:** Buttons pressed but motors don't move

**Check:**
- Green connection status on mobile interface?
- Arduino Serial Monitor shows commands?

**Fix:**
1. Restart web server: `start_web_server.bat`
2. Re-upload Arduino firmware
3. Try physical encoders (should always work)
4. Check Serial Monitor (9600 baud) for errors

### Display Won't Start
**Symptoms:** Display viewer crashes or shows black screen

**Check:**
- Both cameras plugged in via USB?
- Cameras detected in Device Manager?

**Fix:**
1. Run manually: `python display_viewer.py`
2. Check error messages
3. Verify cameras: Device Manager → Imaging Devices
4. Try different USB ports

### Arduino Not Found
**Symptoms:** Web server can't connect to Arduino

**Check:**
- USB cable connected between LattePanda and Leonardo?
- Leonardo shown in Device Manager?

**Fix:**
1. Check Device Manager → Ports (COM# Arduino Leonardo)
2. Re-upload firmware from Arduino IDE
3. Open Serial Monitor (9600 baud) - should see "Ready"
4. Try different USB cable

### Web Server Connection Failed
**Symptoms:** Mobile can't connect to server

**Check:**
- Firewall blocking port 5000?
- Static IP set correctly?

**Fix:**
1. Test locally: `http://localhost:5000/control` on LattePanda
2. Configure firewall (see Network Configuration)
3. Check Windows Firewall settings
4. Restart web server

### Video Recording Fails
**Symptoms:** Video doesn't capture or save

**Check:**
- `recordings/` folder exists?
- Enough disk space?
- Camera 0 working?

**Fix:**
1. Create `recordings/` folder manually
2. Check disk space (need ~100MB per video)
3. Test camera: `python display_viewer.py`
4. Check OpenCV installation: `pip install --upgrade opencv-python`

---

## Maintenance

### Regular Maintenance Schedule

**Daily:**
- Clear old video recordings (manual or automated)
- Verify cameras are clean

**Weekly:**
- Clean camera lenses with microfiber cloth
- Check motor connections are secure
- Test QR codes from mobile device

**Monthly:**
- Review WiFi device list (remove unknown devices)
- Check motor performance (smooth movement?)
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Backup recordings folder

**Quarterly:**
- Full system test (all features)
- Review and archive old recordings
- Test emergency stop procedures
- Update Windows (security patches)

### Backup Strategy

**What to Backup:**
- Video recordings folder
- Arduino firmware (`LattePanda_Diamond_Viewer.ino`)
- Python source code
- Static IP configuration settings
- WiFi credentials

**Where to Backup:**
- External USB drive
- Network attached storage (NAS)
- Cloud storage (encrypted)

### Performance Monitoring

**Check These Metrics:**
- Video frame rate: Should be 30 FPS
- Control latency: Should be <100ms
- QR code generation: Should be <1 second
- Motor response: Should be instant

**Tools:**
- Windows Event Viewer (network logs)
- Arduino Serial Monitor (command acknowledgments)
- Flask server console (client connections)
- Task Manager (CPU/RAM usage)

### Software Updates

**Monthly:**
- Windows Update (critical security patches)
- Review WiFi device list
- Change WiFi password (if in public space)

**Quarterly:**
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Review and archive old recordings
- Test emergency stop procedures

**Annually:**
- Full security audit
- Replace WiFi router if outdated
- Review and update firewall rules

---

## Optional Integrations

### GIA Number OCR (Tesseract)
Automatically detect GIA numbers from girdle camera:
1. Install Tesseract OCR
2. Uncomment `pytesseract` in `requirements.txt`
3. Configure in `web_server.py`

### Email Delivery (SendGrid/Resend)
Send video links via email:
1. Sign up for SendGrid or Resend
2. Obtain API key
3. Uncomment `sendgrid` in `requirements.txt`
4. Configure in `web_server.py`

### SMS Delivery (Twilio)
Send video links via SMS:
1. Sign up for Twilio
2. Obtain Account SID, Auth Token, Phone Number
3. Uncomment `twilio` in `requirements.txt`
4. Configure in `web_server.py`

---

## Technical Specifications

**Hardware:**
- Platform: LattePanda 3 Delta
- Microcontroller: Arduino Leonardo (ATmega32U4)
- Motors: 3x Stepper motors with drivers
- Cameras: 2x USB (1920x1080 @ 30 FPS)
- Network: WiFi 802.11n/ac

**Software:**
- OS: Windows 10/11
- Display: PyQt5 fullscreen interface
- Server: Flask + Flask-SocketIO + Eventlet
- Video: OpenCV 4.9.0
- Communication: WebSocket (real-time)

**Performance:**
- Video frame rate: 30 FPS per camera
- Control latency: <100ms
- QR code generation: <1 second
- Video recording: 30 seconds exactly
- Motor response: Instant (non-blocking)

---

## Support & Resources

**Documentation Files:**
- `README.md` (this file) - Complete setup guide
- `requirements.txt` - Python dependencies
- `deployment/start_display.bat` - Display auto-start
- `deployment/start_web_server.bat` - Server auto-start
- `deployment/set_static_ip.ps1` - Network configuration

**Source Code:**
- `display_viewer.py` - Fullscreen display interface
- `web_server.py` - Flask + WebSocket server
- `templates/control.html` - Mobile control interface
- `templates/share.html` - Customer sharing form
- `LattePanda_Diamond_Viewer.ino` - Arduino firmware
- `src/arduino_controller.py` - Arduino communication

**Testing:**
- Arduino Serial Monitor (9600 baud)
- Browser DevTools (WebSocket debugging)
- Windows Event Viewer (network logs)

---

## FAQ

**Q: Can I access this from the internet?**
**A:** No. This is a serious security risk. The system is designed for local WiFi only.

**Q: What if I need remote access?**
**A:** Use VPN (WireGuard recommended). Never expose port 5000 directly.

**Q: How do I add email/SMS sending?**
**A:** See Optional Integrations section for SendGrid/Twilio setup.

**Q: Can I use this on a regular PC instead of LattePanda?**
**A:** Yes, but you'll need a separate Arduino board (Leonardo or Mega 2560) connected via USB.

**Q: What if cameras are swapped (top shows girdle view)?**
**A:** Edit `display_viewer.py` and swap camera indices (0 ↔ 1).

**Q: How much disk space do I need?**
**A:** ~100MB per recorded video. Plan for 50-100 videos (~5-10GB).

**Q: Can customers hack the motors?**
**A:** Only if they have your WiFi password. Keep WiFi secure with strong WPA2/WPA3.

**Q: What about the QR codes?**
**A:** QR codes only work on local network. They're just convenient links, not security bypass.

---

**System Ready for Production Use**

Your HARBOR Diamond Viewer is now a fully wireless, customer-facing professional system with mobile control, video sharing, and robust safety features.

For technical support, refer to the Troubleshooting section or check Arduino Serial Monitor for debugging information.
