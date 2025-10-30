# Diamond Viewer - PC Integration Guide

## Overview

This guide explains how to integrate the Python PC control software with your existing Harbor Diamond Viewer hardware setup.

## What Changed

Your original Arduino firmware (`Harbor_Diamond_Viewer_Steppers_v1.0`) was designed for **manual control only** via encoders and joystick. We've created an **extended version** (`Harbor_Diamond_Viewer_PC_Control.ino`) that adds PC control capability while preserving all your existing manual control features.

## Hardware Configuration

### Motor Mapping
Your hardware uses three stepper motors controlled by the Arduino Mega 2560:

| Motor | Purpose | Python Name | Arduino Pins | Arduino Object |
|-------|---------|-------------|--------------|----------------|
| Motor 1 | Diamond Rotation | Rotation | 8 (PUL), 9 (DIR) | motorOne |
| Motor 2 | Horizontal Camera (X-axis) | X-Axis | 10 (PUL), 11 (DIR) | motorTwo |
| Motor 3 | Vertical Camera (Y-axis) | Y-Axis | 12 (PUL), 13 (DIR) | motorThree |

### Control Modes

The extended firmware supports **hybrid control** - manual and PC controls work simultaneously:

1. **Encoder Mode** (Manual - Default)
   - Control motors using the three rotary encoders
   - Fine-grained position control
   - Press encoder buttons to change sensitivity
   - **Works even when PC is connected**

2. **Joystick Mode** (Manual)
   - Control motors using the analog joystick
   - Press joystick button to toggle between Encoder/Joystick modes
   - **Works even when PC is connected**

3. **PC Control Mode** (Remote)
   - Control motors via Python application over serial
   - Automatically enabled when Python app connects
   - **Manual controls remain active** - you can use both!
   - Disconnect from software UI when done with PC control

### Safety Features

The extended firmware includes critical safety features to protect operators:

1. **5-Second Timeout Watchdog**
   - Automatically exits PC mode if no commands received for 5 seconds
   - Protects against Python app crashes or unexpected disconnects
   - All motors stop when timeout triggers

2. **Physical Mode Exit (Emergency Recovery)**
   - Press the joystick button to immediately exit PC mode
   - Works even while Python app is connected
   - Returns control to manual operation instantly
   - Provides hardware-level safety override

3. **Automatic Motor Stop**
   - Motors stop on all mode transitions
   - No runaway motor scenarios
   - Clean handoff between control modes

4. **Lighting Control Disabled**
   - Python UI includes lighting slider but it does nothing
   - Your hardware has no lighting control pins
   - Prevents unsupported command errors
   - Ready for future hardware upgrade

## Installation Steps

### Step 1: Upload Extended Arduino Firmware

1. **Backup your current firmware**:
   - Your original firmware is `Harbor_Diamond_Viewer_Steppers_v1.0.ino`
   - Keep a copy in case you need to revert

2. **Open the new firmware**:
   - Load `Harbor_Diamond_Viewer_PC_Control.ino` in Arduino IDE

3. **Verify the code compiles**:
   - Click "Verify" to ensure all libraries are installed
   - Required libraries:
     - BasicStepperDriver
     - Encoder
     - Bounce2

4. **Upload to Arduino Mega 2560**:
   - Connect Arduino via USB
   - Select correct board and COM port
   - Click "Upload"

5. **Test the upload**:
   - Open Serial Monitor (9600 baud)
   - You should see: `"Diamond Viewer Ready - Extended with PC Control"`
   - Test manual controls (encoders/joystick) to ensure they still work

### Step 2: Run the Python Application

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Connect to Arduino**:
   - Click "Refresh" to scan for COM ports
   - **Arduino is auto-detected and selected automatically!**
   - If not auto-detected, manually select your Arduino's COM port
   - Click "Connect to Arduino"
   - The Arduino will automatically switch to PC Control Mode

3. **Test the controls**:
   - Try the X-axis forward/backward buttons
   - Try the Y-axis up/down buttons
   - Try the rotation clockwise/counter-clockwise buttons
   - **While connected, try using encoders/joystick - they work too!**

4. **Disconnect when done**:
   - Click "Disconnect" in the Python app
   - Arduino automatically returns to manual control mode

## Serial Communication Protocol

### Commands Sent by Python App

| Command | Purpose | Arduino Response |
|---------|---------|------------------|
| `PC_MODE` | Enable PC control mode | "PC Control Mode Enabled" |
| `MANUAL_MODE` | Return to manual control | "Manual Control Mode Enabled" |
| `X_FORWARD` | Move camera rail forward | "X_FORWARD" |
| `X_BACK` | Move camera rail backward | "X_BACK" |
| `X_STOP` | Stop X-axis movement | "X_STOP" |
| `Y_UP` | Raise camera/base | "Y_UP" |
| `Y_DOWN` | Lower camera/base | "Y_DOWN" |
| `Y_STOP` | Stop Y-axis movement | "Y_STOP" |
| `ROTATE_CW` | Rotate diamond clockwise | "ROTATE_CW" |
| `ROTATE_CCW` | Rotate diamond counter-clockwise | "ROTATE_CCW" |
| `ROTATE_STOP` | Stop rotation | "ROTATE_STOP" |
| `STATUS` | Query system status | PC_MODE:[0/1],M1:[0/1],M2:[0/1],M3:[0/1] |

### Connection Flow

```
1. Python app opens serial port
2. Wait 2 seconds (Arduino reset delay)
3. Python sends: "PC_MODE"
4. Arduino responds: "PC Control Mode Enabled"
5. Python can now send motor commands
...
6. When user clicks Disconnect:
7. Python sends: "MANUAL_MODE"
8. Arduino responds: "Manual Control Mode Enabled"
9. Python closes serial port
10. User can now use encoders/joystick again
```

## Important Notes

### Lighting Control

⚠️ **Note**: Your Arduino hardware does not include lighting control pins or functionality. The Python application has a lighting slider in the UI, but **it will not do anything** with your current hardware.

**Options**:
1. Leave the lighting slider in the UI (it's harmless, just non-functional)
2. Hide it by modifying the Python code (see below)

To hide the lighting control:
- Edit `src/diamond_viewer.py`
- Comment out or remove the `lighting_group` section (lines ~178-193)

### Safety Considerations

1. **Mode Awareness**: Always know which control mode you're in
   - PC mode: Arduino ignores encoders/joystick
   - Manual mode: Arduino ignores PC commands

2. **Emergency Stop**: If needed, press the Arduino reset button or unplug USB

3. **Coordinate Systems**: Ensure your PC controls match expected motion:
   - X_FORWARD should move camera rail forward (not backward)
   - Y_UP should raise the base (not lower it)
   - If directions are reversed, swap commands in Python code

4. **Limit Switches**: If you have limit switches, they work in all modes

## Troubleshooting

### Arduino doesn't enter PC Control Mode

**Problem**: Python app connects, but motors don't respond

**Solutions**:
- Check Serial Monitor - do you see "PC Control Mode Enabled"?
- Verify baud rate is 9600 in both Python and Arduino
- Try manually sending "PC_MODE" via Serial Monitor
- Check that you uploaded the extended firmware (not the original)

### Motors move in wrong direction

**Problem**: X_FORWARD moves backward, etc.

**Solutions**:
- Swap the direction in Python code, OR
- Invert motor direction pins in Arduino code

**Python fix** (src/arduino_controller.py):
```python
# Swap forward/back commands
def move_axis(self, axis, direction):
    if axis == 'X':
        if direction > 0:
            self.send_command("X_BACK")  # Swapped
        else:
            self.send_command("X_FORWARD")  # Swapped
```

### Can't switch back to manual mode

**Problem**: Encoders/joystick don't work after using PC control

**Solutions**:
- Disconnect Python app (sends MANUAL_MODE automatically)
- Manually send "MANUAL_MODE" via Serial Monitor
- Press Arduino reset button
- Unplug/replug Arduino USB

### Motors keep running

**Problem**: Motors don't stop when releasing button in Python app

**Solutions**:
- Check that button release event is firing
- Try clicking the corresponding STOP button
- Send manual STOP command via Serial Monitor
- Use Arduino reset button as emergency stop

## Testing Checklist

Before using in production:

- [ ] Upload extended firmware successfully
- [ ] Manual encoder control still works
- [ ] Manual joystick control still works
- [ ] Python app can connect to Arduino
- [ ] PC mode is enabled when Python connects
- [ ] X-axis moves correctly in both directions
- [ ] Y-axis moves correctly in both directions
- [ ] Rotation works clockwise and counter-clockwise
- [ ] Motors stop when releasing buttons
- [ ] Manual mode restored when Python disconnects
- [ ] Cameras display correctly in split screen
- [ ] Fullscreen camera switching works
- [ ] No unexpected motor movements

## Reverting to Original Firmware

If you need to return to manual-only control:

1. Open `Harbor_Diamond_Viewer_Steppers_v1.0.ino` in Arduino IDE
2. Upload to Arduino Mega 2560
3. Your original encoder/joystick control is restored
4. Python PC control will not work (no command parsing)

## Future Enhancements

Possible improvements:

1. **Position Feedback**: Use encoder values to display exact position in Python GUI
2. **Preset Positions**: Save favorite positions and recall them with one click
3. **Auto-Scanning**: Automated movement sequences for consistent diamond inspection
4. **Touch Screen**: Add touch controls for the Python interface
5. **Image Capture**: Capture and annotate diamond photos directly from the app
6. **Lighting Integration**: Add LED control hardware and software support

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Arduino Serial Monitor for error messages
3. Verify all hardware connections
4. Test manual controls first, then PC controls

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-29  
**Compatible Firmware**: Harbor_Diamond_Viewer_PC_Control.ino  
**Compatible Python App**: Diamond Viewer Control System v1.0
