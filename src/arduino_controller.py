import serial
import serial.tools.list_ports
import time

class ArduinoController:
    def __init__(self):
        self.serial_connection = None
        self.connected = False
        
    def connect(self, port, baudrate=9600):
        try:
            self.serial_connection = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            self.connected = True
            
            # Clear any startup messages
            while self.serial_connection.in_waiting > 0:
                msg = self.serial_connection.readline().decode('utf-8').strip()
                print(f"Arduino startup: {msg}")
            
            self.send_command("PC_MODE")
            time.sleep(0.2)
            
            # Read response
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                print(f"Arduino response: {response}")
            
            return True
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            self.connected = False
            if self.serial_connection:
                try:
                    self.serial_connection.close()
                except:
                    pass
                self.serial_connection = None
            return False
    
    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.send_command("MANUAL_MODE")
            time.sleep(0.1)
            self.serial_connection.close()
        self.connected = False
    
    def is_connected(self):
        return self.connected and self.serial_connection and self.serial_connection.is_open
    
    def send_command(self, command):
        if self.is_connected():
            try:
                self.serial_connection.write(f"{command}\n".encode())
                print(f"Sent command: {command}")
                return True
            except Exception as e:
                print(f"Error sending command: {e}")
                return False
        else:
            print(f"Cannot send '{command}' - not connected")
        return False
    
    def move_axis(self, axis, direction):
        if axis == 'X':
            if direction > 0:
                self.send_command("X_FORWARD")
            else:
                self.send_command("X_BACK")
        elif axis == 'Y':
            if direction > 0:
                self.send_command("Y_UP")
            else:
                self.send_command("Y_DOWN")
    
    def stop_axis(self, axis):
        if axis == 'X':
            self.send_command("X_STOP")
        elif axis == 'Y':
            self.send_command("Y_STOP")
    
    def rotate(self, direction):
        if direction > 0:
            self.send_command("ROTATE_CW")
        else:
            self.send_command("ROTATE_CCW")
    
    def stop_rotation(self):
        self.send_command("ROTATE_STOP")
    
    def set_lighting(self, intensity):
        pass
    
    @staticmethod
    def list_available_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
