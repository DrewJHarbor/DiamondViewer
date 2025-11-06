/*
 * HARBOR Diamond Viewer - LattePanda 3 Delta Edition
 * 
 * Firmware for LattePanda 3 Delta's integrated Arduino Leonardo (ATmega32U4)
 * Supports wireless control from mobile devices + physical encoders/joystick
 * 
 * Hardware: LattePanda 3 Delta
 * Microcontroller: ATmega32U4 (Arduino Leonardo compatible)
 * Motors: 3x Stepper motors (Rotation, X-axis zoom, Y-axis height)
 * Control: Physical encoders + joystick + WiFi (via Python/Flask on Windows)
 * 
 * Features:
 * - Hybrid control mode (manual + wireless simultaneously)
 * - Auto-rotation (continuous rotation triggered by double-tap on mobile)
 * - 30-second safety timeout with 15-second heartbeat
 * - Compatible with existing encoder/joystick hardware
 */

#include <BasicStepperDriver.h>
#include <Encoder.h>
#include <Bounce2.h>

//---
// Motor Settings
//---
#define MOTOR_STEPS 1600
#define RPM 120
#define MICROSTEPS 1
#define MAX_RPM 240

//---
// Pin Definitions for LattePanda Leonardo (ATmega32U4)
// Note: Leonardo has different pin layout than Mega 2560
//---

// Stepper Motor Pins
#define MOTOR_1_PUL  8      // Motor 1 = Rotation (base turntable)
#define MOTOR_1_DIR  9
#define MOTOR_2_PUL  10     // Motor 2 = X-axis (zoom camera rail)
#define MOTOR_2_DIR  11
#define MOTOR_3_PUL  12     // Motor 3 = Y-axis (base height)
#define MOTOR_3_DIR  13

// Encoder Pins (using interrupt-capable pins on Leonardo)
#define ENCODER_1_CHLA  2   // Rotation encoder
#define ENCODER_1_CHLB  3
#define ENCODER_2_CHLA  0   // X-axis encoder (Leonardo: pins 0,1,2,3,7 support interrupts)
#define ENCODER_2_CHLB  1
#define ENCODER_3_CHLA  7   // Y-axis encoder
#define ENCODER_3_CHLB  6

// Encoder Buttons
#define ENCODER_1_BTN   4
#define ENCODER_2_BTN   5
#define ENCODER_3_BTN   14  // A0 as digital pin

// Joystick
#define JOYSTICK_X      A1
#define JOYSTICK_Y      A2
#define JOYSTICK_PRESS  A3

//---
// Motor Objects
//---
BasicStepperDriver motorOne(MOTOR_STEPS, MOTOR_1_DIR, MOTOR_1_PUL);     // Rotation
BasicStepperDriver motorTwo(MOTOR_STEPS, MOTOR_2_DIR, MOTOR_2_PUL);     // X-axis (zoom)
BasicStepperDriver motorThree(MOTOR_STEPS, MOTOR_3_DIR, MOTOR_3_PUL);   // Y-axis (height)

//---
// Encoder Objects
//---
Encoder encOne(ENCODER_1_CHLA, ENCODER_1_CHLB);     // Rotation
Encoder encTwo(ENCODER_2_CHLA, ENCODER_2_CHLB);     // X-axis
Encoder encThree(ENCODER_3_CHLA, ENCODER_3_CHLB);   // Y-axis

Bounce2::Button encBtnOne = Bounce2::Button();
Bounce2::Button encBtnTwo = Bounce2::Button();
Bounce2::Button encBtnThree = Bounce2::Button();

//---
// Control State Variables
//---
float scaleOne = 200.0;     // Rotation sensitivity
float scaleTwo = 200.0;     // X-axis sensitivity
float scaleThree = 200.0;   // Y-axis sensitivity

bool useJoystick = false;
long oldPosition[3] = {0, 0, 0};

// Wireless (PC) Control State
bool pcControlActive = false;
bool motor1Moving = false;
bool motor2Moving = false;
bool motor3Moving = false;
int motor1Direction = 0;    // 1=CW, -1=CCW, 0=stop
int motor2Direction = 0;    // 1=forward, -1=back, 0=stop
int motor3Direction = 0;    // 1=up, -1=down, 0=stop

// Auto-rotation feature (triggered by double-tap on mobile)
bool autoRotationActive = false;
int autoRotationDirection = 0;  // 1=CW, -1=CCW

// Safety timeout
unsigned long lastPCCommand = 0;
const unsigned long PC_TIMEOUT = 30000;  // 30 seconds

//---
// Setup
//---
void setup() {
  // Initialize motors
  motorOne.begin(RPM, MICROSTEPS);
  motorTwo.begin(RPM, MICROSTEPS);
  motorThree.begin(RPM, MICROSTEPS);
  
  // Initialize encoder buttons
  encBtnOne.attach(ENCODER_1_BTN, INPUT_PULLUP);
  encBtnOne.interval(5);
  encBtnOne.setPressedState(LOW);
  
  encBtnTwo.attach(ENCODER_2_BTN, INPUT_PULLUP);
  encBtnTwo.interval(5);
  encBtnTwo.setPressedState(LOW);
  
  encBtnThree.attach(ENCODER_3_BTN, INPUT_PULLUP);
  encBtnThree.interval(5);
  encBtnThree.setPressedState(LOW);
  
  pinMode(JOYSTICK_PRESS, INPUT_PULLUP);

  // Serial communication with LattePanda Windows
  Serial.begin(9600);
  while (!Serial && millis() < 3000) {
    ; // Wait for serial port (Leonardo specific)
  }
  
  Serial.println("HARBOR Diamond Viewer - LattePanda Edition");
  Serial.println("Ready for wireless + manual control");
  Serial.println("Commands: X_FORWARD, X_BACK, X_STOP, Y_UP, Y_DOWN, Y_STOP, ROTATE_CW, ROTATE_CCW, ROTATE_STOP, AUTO_ROTATE_CW, AUTO_ROTATE_CCW, AUTO_ROTATE_STOP, PING");
}

//---
// Main Loop
//---
void loop() {
  // Non-blocking motor control
  motorOne.nextAction();
  motorTwo.nextAction();
  motorThree.nextAction();

  // Check encoder buttons
  encBtnOne.update();
  encBtnTwo.update();
  encBtnThree.update();
  
  // Update encoder scalars based on button presses
  updateEncoderScalars();

  // Process wireless commands from LattePanda
  processSerialCommands();

  // Safety timeout check
  if (pcControlActive && (millis() - lastPCCommand > PC_TIMEOUT)) {
    // Timeout - return to manual mode for safety
    pcControlActive = false;
    autoRotationActive = false;
    stopAllMotors();
    Serial.println("STATUS:TIMEOUT");
  }

  // Handle auto-rotation (continuous spinning)
  if (autoRotationActive) {
    if (!motorOne.getStepsRemaining()) {
      // Keep rotating
      motorOne.startRotate(360 * autoRotationDirection);
    }
  } else {
    // Manual control (encoders/joystick) - always available
    if (!pcControlActive || !motor1Moving) {
      handleRotationEncoder();
    }
  }
  
  if (!pcControlActive || !motor2Moving) {
    handleXAxisEncoder();
  }
  
  if (!pcControlActive || !motor3Moving) {
    handleYAxisEncoder();
  }

  // Joystick control (if enabled)
  if (useJoystick && !pcControlActive) {
    handleJoystickControl();
  }
  
  // Joystick button toggle
  if (digitalRead(JOYSTICK_PRESS) == LOW) {
    delay(200);  // Debounce
    useJoystick = !useJoystick;
    Serial.print("JOYSTICK:");
    Serial.println(useJoystick ? "ON" : "OFF");
  }
}

//---
// Serial Command Processing
//---
void processSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    lastPCCommand = millis();  // Update timeout timer
    pcControlActive = true;
    
    // X-axis (zoom) commands
    if (command == "X_FORWARD") {
      motor2Moving = true;
      motor2Direction = 1;
      motorTwo.startMove(1000000);  // Continuous movement
      Serial.println("ACK:X_FORWARD");
    }
    else if (command == "X_BACK") {
      motor2Moving = true;
      motor2Direction = -1;
      motorTwo.startMove(-1000000);
      Serial.println("ACK:X_BACK");
    }
    else if (command == "X_STOP") {
      motor2Moving = false;
      motor2Direction = 0;
      motorTwo.stop();
      Serial.println("ACK:X_STOP");
    }
    
    // Y-axis (height) commands
    else if (command == "Y_UP") {
      motor3Moving = true;
      motor3Direction = 1;
      motorThree.startMove(1000000);
      Serial.println("ACK:Y_UP");
    }
    else if (command == "Y_DOWN") {
      motor3Moving = true;
      motor3Direction = -1;
      motorThree.startMove(-1000000);
      Serial.println("ACK:Y_DOWN");
    }
    else if (command == "Y_STOP") {
      motor3Moving = false;
      motor3Direction = 0;
      motorThree.stop();
      Serial.println("ACK:Y_STOP");
    }
    
    // Rotation commands
    else if (command == "ROTATE_CW") {
      autoRotationActive = false;  // Cancel auto-rotation
      motor1Moving = true;
      motor1Direction = 1;
      motorOne.startRotate(360);
      Serial.println("ACK:ROTATE_CW");
    }
    else if (command == "ROTATE_CCW") {
      autoRotationActive = false;
      motor1Moving = true;
      motor1Direction = -1;
      motorOne.startRotate(-360);
      Serial.println("ACK:ROTATE_CCW");
    }
    else if (command == "ROTATE_STOP") {
      motor1Moving = false;
      motor1Direction = 0;
      autoRotationActive = false;
      motorOne.stop();
      Serial.println("ACK:ROTATE_STOP");
    }
    
    // Auto-rotation commands (continuous spinning triggered by double-tap)
    else if (command == "AUTO_ROTATE_CW") {
      autoRotationActive = true;
      autoRotationDirection = 1;
      motor1Moving = true;
      motorOne.startRotate(360);  // Start first rotation
      Serial.println("ACK:AUTO_ROTATE_CW");
    }
    else if (command == "AUTO_ROTATE_CCW") {
      autoRotationActive = true;
      autoRotationDirection = -1;
      motor1Moving = true;
      motorOne.startRotate(-360);
      Serial.println("ACK:AUTO_ROTATE_CCW");
    }
    else if (command == "AUTO_ROTATE_STOP") {
      autoRotationActive = false;
      motor1Moving = false;
      motor1Direction = 0;
      motorOne.stop();
      Serial.println("ACK:AUTO_ROTATE_STOP");
    }
    
    // Heartbeat (keeps connection alive)
    else if (command == "PING") {
      Serial.println("PONG");
    }
    
    // Status query
    else if (command == "STATUS") {
      Serial.print("MODE:");
      Serial.print(pcControlActive ? "PC" : "MANUAL");
      Serial.print(",AUTO_ROT:");
      Serial.println(autoRotationActive ? "ON" : "OFF");
    }
    
    else {
      Serial.print("ERROR:Unknown command: ");
      Serial.println(command);
    }
  }
}

//---
// Encoder Handling
//---
void handleRotationEncoder() {
  long newPosition = encOne.read();
  long delta = newPosition - oldPosition[0];
  
  if (abs(delta) > scaleOne) {
    int steps = (delta / scaleOne) * 50;
    motorOne.move(steps);
    oldPosition[0] = newPosition;
  }
}

void handleXAxisEncoder() {
  long newPosition = encTwo.read();
  long delta = newPosition - oldPosition[1];
  
  if (abs(delta) > scaleTwo) {
    int steps = (delta / scaleTwo) * 50;
    motorTwo.move(steps);
    oldPosition[1] = newPosition;
  }
}

void handleYAxisEncoder() {
  long newPosition = encThree.read();
  long delta = newPosition - oldPosition[2];
  
  if (abs(delta) > scaleThree) {
    int steps = (delta / scaleThree) * 50;
    motorThree.move(steps);
    oldPosition[2] = newPosition;
  }
}

//---
// Encoder Scalar Adjustment (button press changes sensitivity)
//---
void updateEncoderScalars() {
  if (encBtnOne.pressed()) {
    scaleOne = (scaleOne == 200.0) ? 400.0 : 200.0;
    Serial.print("Rotation scale: ");
    Serial.println(scaleOne);
  }
  
  if (encBtnTwo.pressed()) {
    scaleTwo = (scaleTwo == 200.0) ? 400.0 : 200.0;
    Serial.print("X-axis scale: ");
    Serial.println(scaleTwo);
  }
  
  if (encBtnThree.pressed()) {
    scaleThree = (scaleThree == 200.0) ? 400.0 : 200.0;
    Serial.print("Y-axis scale: ");
    Serial.println(scaleThree);
  }
}

//---
// Joystick Control
//---
void handleJoystickControl() {
  int joyX = analogRead(JOYSTICK_X);
  int joyY = analogRead(JOYSTICK_Y);
  
  // X-axis control (horizontal movement)
  if (joyX < 400) {
    motorTwo.move(-100);
  } else if (joyX > 600) {
    motorTwo.move(100);
  }
  
  // Y-axis control (vertical movement)
  if (joyY < 400) {
    motorThree.move(-100);
  } else if (joyY > 600) {
    motorThree.move(100);
  }
}

//---
// Utility Functions
//---
void stopAllMotors() {
  motorOne.stop();
  motorTwo.stop();
  motorThree.stop();
  motor1Moving = false;
  motor2Moving = false;
  motor3Moving = false;
  motor1Direction = 0;
  motor2Direction = 0;
  motor3Direction = 0;
}
