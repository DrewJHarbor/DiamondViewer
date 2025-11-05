# HARBOR Diamond Viewer - LattePanda 3 Delta Setup Guide

Complete deployment guide for installing the HARBOR Diamond Viewer on LattePanda 3 Delta with wireless mobile control.

## Hardware Requirements

- **LattePanda 3 Delta** (with integrated Arduino Leonardo ATmega32U4)
- **2x USB Cameras** (top view + girdle view)
- **3x Stepper Motors** with drivers
- **3x Rotary Encoders** (for manual control)
- **1x Joystick module** (optional manual control)
- **Power supply** for motors and LattePanda

## Software Requirements

- **Windows 10/11** (pre-installed on LattePanda)
- **Python 3.10+**
- **Arduino IDE** (for uploading firmware)

---

## Step 1: Arduino Firmware Installation

### 1.1 Install Arduino IDE
1. Download Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
2. Install and launch Arduino IDE

### 1.2 Install Required Libraries
In Arduino IDE:
- Go to **Tools → Manage Libraries**
- Install:
  - `BasicStepperDriver` (search for "StepperDriver" by laurb9)
  - `Encoder` (by Paul Stoffregen)
  - `Bounce2` (by Thomas O Fredericks)

### 1.3 Upload Firmware to LattePanda Leonardo
1. Connect LattePanda to power
2. In Arduino IDE:
   - **Tools → Board → Arduino AVR Boards → Arduino Leonardo**
   - **Tools → Port → COM# (Arduino Leonardo)** (auto-detected)
3. Open `LattePanda_Diamond_Viewer.ino`
4. Click **Upload** (⮕ button)
5. Wait for "Done uploading" message

### 1.4 Verify Firmware
1. Open **Tools → Serial Monitor**
2. Set baud rate to **9600**
3. You should see: `HARBOR Diamond Viewer - LattePanda Edition`

---

## Step 2: Python Software Installation

### 2.1 Install Python Dependencies
Open PowerShell or Command Prompt:
```powershell
cd C:\path\to\harbor-diamond-viewer
pip install PyQt5 opencv-python pyserial qrcode pillow flask flask-socketio flask-cors
```

### 2.2 Test Display Viewer
```powershell
python display_viewer.py
```
- You should see fullscreen dual camera view
- Harbor branding at top
- Click **Control** button to see QR code
- Press **ESC** to exit

### 2.3 Test Web Server
Open a new PowerShell window:
```powershell
python web_server.py
```
- Server should start on `http://0.0.0.0:5000`
- Check for IP address in output

---

## Step 3: Network Configuration (Static IP)

**Why Static IP?** Prevents IP address changes which would break QR codes.

### 3.1 Set Static IP (Recommended)
1. **Right-click** on `deployment/set_static_ip.ps1`
2. Select **"Run with PowerShell"** (as Administrator)
3. Follow prompts:
   ```
   IP Address: 192.168.1.100  (example - choose your own)
   Subnet: 255.255.255.0
   Gateway: 192.168.1.1  (your router IP)
   DNS: 8.8.8.8
   ```

### 3.2 Test Static IP
From your phone/tablet on same WiFi:
```
http://192.168.1.100:5000/control
```
You should see the mobile control interface.

---

## Step 4: Auto-Start Configuration

Set up both programs to start automatically when LattePanda boots.

### 4.1 Create Startup Shortcuts

1. Press **Win + R**, type: `shell:startup`, press Enter
2. This opens the Startup folder
3. **Right-click** inside folder → **New → Shortcut**

**For Display Viewer:**
- Target: `C:\path\to\deployment\start_display.bat`
- Name: `Harbor Display`

**For Web Server:**
- Target: `C:\path\to\deployment\start_web_server.bat`
- Name: `Harbor Web Server`

### 4.2 Test Auto-Start
1. Restart LattePanda
2. Display viewer should launch fullscreen automatically
3. Web server should start in background
4. Test QR codes work

---

## Step 5: Hardware Wiring

### 5.1 LattePanda Leonardo Pin Connections

**Stepper Motors (connect to motor drivers, then to Leonardo):**
- **Motor 1 (Rotation):**
  - PUL → Pin 8
  - DIR → Pin 9

- **Motor 2 (X-axis / Zoom):**
  - PUL → Pin 10
  - DIR → Pin 11

- **Motor 3 (Y-axis / Height):**
  - PUL → Pin 12
  - DIR → Pin 13

**Encoders:**
- **Rotation Encoder:**
  - CH_A → Pin 2
  - CH_B → Pin 3
  - Button → Pin 4

- **X-axis Encoder:**
  - CH_A → Pin 0
  - CH_B → Pin 1
  - Button → Pin 5

- **Y-axis Encoder:**
  - CH_A → Pin 7
  - CH_B → Pin 6
  - Button → Pin A0 (14)

**Joystick (optional):**
- X-axis → Pin A1
- Y-axis → Pin A2
- Button → Pin A3

**Cameras:**
- Top camera → USB port (usually shows as Camera 0)
- Girdle camera → USB port (usually shows as Camera 1)

### 5.2 Power Connections
- LattePanda: Use 12V DC power adapter
- Stepper motors: Connect to separate 12-24V power supply
- **Important:** Share ground between LattePanda and motor power supply

---

## Step 6: Mobile Control Usage

### 6.1 Connect Phone/Tablet to WiFi
Ensure your mobile device is on the **same WiFi network** as LattePanda.

### 6.2 Scan QR Code
1. On the display viewer, click **📱 Control** button
2. QR code appears in bottom-left corner
3. Scan with phone camera
4. Opens mobile control interface

### 6.3 Control Features
- **Zoom In/Out:** Move camera rail forward/backward
- **Height Up/Down:** Raise/lower platform
- **Rotation Left/Right:** Rotate diamond
- **Double-tap rotation:** Starts continuous auto-rotation

---

## Step 7: Customer Sharing Feature

### 7.1 Enable Share QR Code
1. Click **📤 Share** button on display
2. QR code appears in bottom-right corner
3. Customer scans with their phone

### 7.2 Customer Receives Video
1. Customer enters email or phone number
2. System records 30-second video from top camera
3. Detects GIA number from girdle view
4. Sends video link + GIA number via email/SMS

**Note:** Email/SMS sending requires additional setup (see Email/SMS Integration section below).

---

## Troubleshooting

### Display won't start
- Check camera connections (USB)
- Verify cameras are detected: `ls /dev/video*` or Device Manager
- Try running manually: `python display_viewer.py`

### Web server connection failed
- Check firewall settings (allow port 5000)
- Verify static IP is set correctly
- Test with: `http://localhost:5000/control` on LattePanda itself

### Arduino not detected
- Check USB connection
- Verify COM port in Device Manager
- Re-upload firmware from Arduino IDE

### Motors not responding
- Verify wiring matches pin diagram
- Check motor power supply
- Test manual encoder control first
- Check Serial Monitor for command acknowledgments

### QR code doesn't work
- Verify phone and LattePanda on same WiFi
- Check static IP configuration
- Try typing IP address manually: `http://192.168.1.100:5000/control`

---

## Email/SMS Integration (Optional)

To enable customer sharing via email/SMS, you'll need:

### Email Integration
- SendGrid or Resend account
- API key
- Configure in `web_server.py`

### SMS Integration
- Twilio account
- Account SID, Auth Token, Phone Number
- Configure in `web_server.py`

See `INTEGRATION_GUIDE.md` for detailed setup instructions.

---

## Maintenance

### Regular Checks
- Clean camera lenses weekly
- Verify motor connections monthly
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Backup recordings folder periodically

### Software Updates
1. Pull latest code
2. Re-upload Arduino firmware if changed
3. Restart services

---

## Support

For technical support or questions:
- Check documentation in repository
- Review Arduino Serial Monitor for debugging
- Test components individually before system integration

---

**Congratulations!** Your HARBOR Diamond Viewer is now fully deployed on LattePanda with wireless mobile control.
