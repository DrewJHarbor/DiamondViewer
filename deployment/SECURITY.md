# HARBOR Diamond Viewer - Security Guide

## Overview

The HARBOR Diamond Viewer uses wireless control for mobile devices. This guide outlines security measures and best practices for safe deployment.

## Network Security Model

### Design Philosophy
- **Local WiFi Only**: The system is designed for use on a secure, password-protected local WiFi network
- **No Internet Exposure**: The web server should NEVER be exposed to the internet
- **Physical Security**: LattePanda should be in a secured location

### Threat Model
**Protected Against:**
- Unauthorized internet access (server bound to local network only)
- Cross-site request forgery from external sites (CORS restrictions)
- Accidental motor commands from wrong network

**Requires Physical/Network Security:**
- Unauthorized users on same WiFi network (mitigated by WiFi password)
- Physical access to LattePanda (mitigated by locked enclosure)
- Motor safety (mitigated by 30-second timeout + emergency stop)

---

## Security Layers

### Layer 1: Network Isolation
**CRITICAL:** The web server MUST only be accessible on your local WiFi network.

#### WiFi Network Requirements
- **Strong WPA2/WPA3 password** (minimum 12 characters)
- **Hidden SSID** (optional but recommended)
- **MAC address filtering** (optional for high-security environments)
- **Guest network isolation** (if using guest WiFi, isolate from main network)

#### Firewall Configuration (Windows Defender)
The system automatically configures Windows Firewall when you run the setup:

1. **Inbound Rule**: Allow port 5000 for local network only
2. **Outbound Rule**: No restrictions needed (LattePanda initiates connections)

**To manually verify:**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Harbor Diamond Viewer" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private
```

#### Router Configuration
**Recommended:**
- Do NOT port forward port 5000 to the internet
- Enable router firewall
- Disable UPnP if not needed
- Use strong router admin password

### Layer 2: Application Security

#### CORS Restrictions
The web server restricts Cross-Origin requests to:
- `localhost` (testing only)
- `127.0.0.1` (testing only)
- `192.168.*.*` (typical home/office networks)
- `10.*.*.*` (corporate networks)

This prevents external websites from sending commands to your system.

#### No Authentication by Design
**Why no login screen?**
- System is designed for quick, frictionless customer use
- Physical proximity required (must scan QR code)
- WiFi password provides access control
- Addition of authentication would slow down legitimate use

**When authentication IS needed:**
If deploying in a public space or high-traffic environment, contact support for enterprise authentication module.

### Layer 3: Hardware Safety Features

#### 30-Second Timeout
- If no commands received for 30 seconds, system stops motors
- Prevents runaway motors if connection lost
- Arduino returns to manual encoder control

#### 15-Second Heartbeat
- Mobile interface sends keepalive every 15 seconds
- Ensures timeout only triggers when truly disconnected

#### Emergency Manual Override
- **Physical encoders** always work, even during wireless control
- **Joystick button** can force manual mode
- **Arduino reset button** provides hard reset if needed

---

## Deployment Security Checklist

### Pre-Deployment
- [ ] WiFi network has strong WPA2/WPA3 password
- [ ] LattePanda will be in physically secured location
- [ ] Router is NOT configured to port forward port 5000
- [ ] Windows Firewall is enabled
- [ ] Static IP is configured (prevents IP rotation attacks)

### During Setup
- [ ] Run `set_static_ip.ps1` as Administrator
- [ ] Verify only trusted devices on WiFi network
- [ ] Test QR codes only work on local network
- [ ] Verify motors stop after 30-second timeout

### Operational Security
- [ ] Change WiFi password regularly (monthly recommended)
- [ ] Monitor Windows Event Viewer for unusual access
- [ ] Keep LattePanda Windows updated
- [ ] Backup recordings folder weekly
- [ ] Review device list on router monthly

---

## Security Incident Response

### Suspected Unauthorized Access
1. **Immediately disconnect LattePanda from WiFi**
   - Windows: Disconnect WiFi adapter
   - Or: Unplug ethernet cable

2. **Check Windows Event Viewer**
   ```powershell
   eventvwr.msc
   ```
   Look for unusual network activity around port 5000

3. **Change WiFi password**

4. **Review router logs** for unauthorized devices

5. **Restart LattePanda** with fresh Windows login

### Motor Malfunction
1. **Press Arduino reset button** (immediate hardware stop)
2. **Or power cycle motors** (cut motor power supply)
3. **Check serial monitor** for error messages
4. **Verify encoder connections** aren't loose

### Network Performance Issues
1. Check number of devices on WiFi (too many = slow QR code scanning)
2. Verify static IP hasn't changed
3. Restart router if needed
4. Check Windows Task Manager for CPU/RAM usage

---

## Advanced Security (Optional)

### VPN Access
For remote monitoring (NOT recommended for production):
- Install WireGuard VPN on LattePanda
- Connect only from trusted devices
- Use strong VPN authentication

### HTTPS/TLS
Not implemented by default because:
- Adds complexity for local network use
- Self-signed certificates cause browser warnings
- Not needed when WiFi is secured with WPA2/WPA3

If required:
- Generate self-signed certificate
- Configure Flask-SocketIO with SSL context
- Distribute certificate to mobile devices

### Captive Portal
For extremely high-security environments:
- Set up LattePanda as WiFi access point
- Implement captive portal with login
- Isolate completely from other networks

---

## Compliance & Privacy

### Data Storage
- **Video recordings** stored locally on LattePanda (`recordings/` folder)
- **No cloud upload** unless explicitly configured
- **Email/SMS** only sends links, not raw video (reduces privacy risk)

### Data Retention
- Videos automatically deleted after 30 days (recommended)
- Configure in Windows Task Scheduler:
  ```powershell
  # Delete recordings older than 30 days
  forfiles /p "C:\path\to\recordings" /s /m *.mp4 /d -30 /c "cmd /c del @path"
  ```

### GDPR/Privacy Compliance
- Customers must consent before receiving video/SMS
- Include privacy notice on sharing form
- Provide method to delete customer data on request

---

## Security Updates

### Monthly
- Windows Update (critical security patches)
- Review WiFi device list
- Change WiFi password (if in public space)

### Quarterly
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Review and archive old recordings
- Test emergency stop procedures

### Annually
- Full security audit
- Replace WiFi router if outdated
- Review and update firewall rules

---

## Questions & Support

**Q: Can I access this from the internet?**
**A:** No. This is a serious security risk. The system is designed for local WiFi only.

**Q: What if I need remote access?**
**A:** Use VPN (WireGuard recommended). Never expose port 5000 directly.

**Q: Is the Arduino connection secure?**
**A:** Yes. USB serial communication is local-only and requires physical access.

**Q: Can customers hack the motors?**
**A:** Only if they have your WiFi password. Keep WiFi secure.

**Q: What about the QR codes?**
**A:** QR codes only work on local network. They're just convenient links, not security bypass.

---

**Remember:** Security is a balance between protection and usability. This system prioritizes quick customer access while maintaining reasonable security through network isolation and physical access control.
