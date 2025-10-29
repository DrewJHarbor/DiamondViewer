/*
 * Diamond Viewer - Arduino Mega 2560 Firmware
 * 
 * This firmware controls the Diamond Viewer hardware including:
 * - X-axis stepper motor (zoom camera rail)
 * - Y-axis stepper motor (base height)
 * - Rotation stepper motor (diamond rotation)
 * - Lighting control (PWM)
 * 
 * Serial Communication: 9600 baud
 * Commands are received as plain text strings ending with newline
 */

// Pin Definitions - Adjust these based on your wiring
#define X_STEP_PIN 2
#define X_DIR_PIN 3
#define X_ENABLE_PIN 4

#define Y_STEP_PIN 5
#define Y_DIR_PIN 6
#define Y_ENABLE_PIN 7

#define ROTATE_STEP_PIN 8
#define ROTATE_DIR_PIN 9
#define ROTATE_ENABLE_PIN 10

#define LIGHT_PIN 11  // PWM pin for lighting

// Movement states
bool x_moving = false;
bool y_moving = false;
bool rotating = false;

int x_direction = 0;
int y_direction = 0;
int rotate_direction = 0;

// Lighting
int light_intensity = 128;  // 0-255 (50% default)

// Timing
unsigned long last_step_time = 0;
const int step_delay = 1000;  // Microseconds between steps (adjust for speed)

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Configure motor pins
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);
  
  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  
  pinMode(ROTATE_STEP_PIN, OUTPUT);
  pinMode(ROTATE_DIR_PIN, OUTPUT);
  pinMode(ROTATE_ENABLE_PIN, OUTPUT);
  
  pinMode(LIGHT_PIN, OUTPUT);
  
  // Enable all motors (LOW = enabled for most drivers)
  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(ROTATE_ENABLE_PIN, LOW);
  
  // Set initial lighting
  analogWrite(LIGHT_PIN, light_intensity);
  
  Serial.println("Diamond Viewer Ready");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  // Execute movements
  unsigned long current_time = micros();
  if (current_time - last_step_time >= step_delay) {
    last_step_time = current_time;
    
    if (x_moving) {
      stepMotor(X_STEP_PIN, X_DIR_PIN, x_direction);
    }
    
    if (y_moving) {
      stepMotor(Y_STEP_PIN, Y_DIR_PIN, y_direction);
    }
    
    if (rotating) {
      stepMotor(ROTATE_STEP_PIN, ROTATE_DIR_PIN, rotate_direction);
    }
  }
}

void processCommand(String cmd) {
  // X-Axis Commands
  if (cmd == "X_FORWARD") {
    x_moving = true;
    x_direction = 1;
    digitalWrite(X_DIR_PIN, HIGH);
    Serial.println("X-Axis: Forward");
  }
  else if (cmd == "X_BACK") {
    x_moving = true;
    x_direction = -1;
    digitalWrite(X_DIR_PIN, LOW);
    Serial.println("X-Axis: Backward");
  }
  else if (cmd == "X_STOP") {
    x_moving = false;
    Serial.println("X-Axis: Stopped");
  }
  
  // Y-Axis Commands
  else if (cmd == "Y_UP") {
    y_moving = true;
    y_direction = 1;
    digitalWrite(Y_DIR_PIN, HIGH);
    Serial.println("Y-Axis: Up");
  }
  else if (cmd == "Y_DOWN") {
    y_moving = true;
    y_direction = -1;
    digitalWrite(Y_DIR_PIN, LOW);
    Serial.println("Y-Axis: Down");
  }
  else if (cmd == "Y_STOP") {
    y_moving = false;
    Serial.println("Y-Axis: Stopped");
  }
  
  // Rotation Commands
  else if (cmd == "ROTATE_CW") {
    rotating = true;
    rotate_direction = 1;
    digitalWrite(ROTATE_DIR_PIN, HIGH);
    Serial.println("Rotation: Clockwise");
  }
  else if (cmd == "ROTATE_CCW") {
    rotating = true;
    rotate_direction = -1;
    digitalWrite(ROTATE_DIR_PIN, LOW);
    Serial.println("Rotation: Counter-Clockwise");
  }
  else if (cmd == "ROTATE_STOP") {
    rotating = false;
    Serial.println("Rotation: Stopped");
  }
  
  // Lighting Commands
  else if (cmd.startsWith("LIGHT_")) {
    String value_str = cmd.substring(6);
    int value = value_str.toInt();
    
    // Convert 0-100 to 0-255
    light_intensity = map(value, 0, 100, 0, 255);
    light_intensity = constrain(light_intensity, 0, 255);
    
    analogWrite(LIGHT_PIN, light_intensity);
    Serial.print("Lighting: ");
    Serial.print(value);
    Serial.println("%");
  }
  
  else {
    Serial.print("Unknown command: ");
    Serial.println(cmd);
  }
}

void stepMotor(int step_pin, int dir_pin, int direction) {
  digitalWrite(step_pin, HIGH);
  delayMicroseconds(5);
  digitalWrite(step_pin, LOW);
}

/*
 * HARDWARE SETUP NOTES:
 * 
 * 1. Stepper Motor Drivers (e.g., A4988, DRV8825):
 *    - Connect STEP, DIR, and ENABLE pins as defined above
 *    - Power stepper motors with appropriate voltage
 *    - Set microstepping with MS1, MS2, MS3 pins
 * 
 * 2. Lighting:
 *    - Use PWM-capable pin (11 by default)
 *    - Connect to LED driver or MOSFET for high-power LEDs
 *    - Add appropriate current-limiting resistors
 * 
 * 3. Optional Enhancements:
 *    - Add limit switches for safety (endstops)
 *    - Add encoders for position feedback
 *    - Add emergency stop button
 *    - Implement acceleration/deceleration curves
 * 
 * 4. Wiring Checklist:
 *    - Common ground between Arduino and motor drivers
 *    - Separate power supply for motors (not from Arduino)
 *    - Decoupling capacitors on motor power lines
 *    - Shielded cables for stepper motors to reduce EMI
 */
