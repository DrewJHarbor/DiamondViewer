/*
 * Harbor Diamond Viewer - Extended with PC Control
 * 
 * This firmware extends the original Harbor_Diamond_Viewer_Steppers_v1.0
 * to add PC control via serial commands while preserving all encoder/joystick functionality.
 * 
 * Control Modes:
 * 1. Manual Mode (default): Use encoders and joystick
 * 2. PC Control Mode: Receive commands from Python application
 * 
 * Toggle modes: Press joystick button (original functionality)
 * PC can also request mode change via serial commands
 */

#include <A4988.h>
#include <BasicStepperDriver.h>
#include <DRV8825.h>
#include <DRV8834.h>
#include <DRV8880.h>
#include <MultiDriver.h>
#include <SyncDriver.h>
#include <Wire.h>
#include <Arduino.h>
#include <Encoder.h>
#include <Bounce2.h>

//---
// Pin and motor settings
//---
#define MOTOR_STEPS 1600
#define RPM 120
#define MICROSTEPS 1
#define MAX_RPM 240

// **************PIN DECLARATIONS***********************************
#define MOTOR_1_PUL  8      // Motor 1 = Rotation
#define MOTOR_1_DIR  9
#define MOTOR_2_PUL  10     // Motor 2 = Horizontal camera (X-axis)
#define MOTOR_2_DIR  11
#define MOTOR_3_PUL  12     // Motor 3 = Vertical camera (Y-axis)
#define MOTOR_3_DIR  13

#define ENCODER_1_CHLA  2
#define ENCODER_1_CHLB  3
#define ENCODER_2_CHLA  18
#define ENCODER_2_CHLB  19
#define ENCODER_3_CHLA  20
#define ENCODER_3_CHLB  21

#define ENCODER_1_BTN   4
#define ENCODER_2_BTN   5
#define ENCODER_3_BTN   6

#define JOYSTICK_X      A0
#define JOYSTICK_Y      A1
#define JOYSTICK_PRESS  A2

//---
// Declaring stepper motor, encoder, and button objects
//---
BasicStepperDriver motorOne(MOTOR_STEPS, MOTOR_1_DIR, MOTOR_1_PUL);     // Rotation
BasicStepperDriver motorTwo(MOTOR_STEPS, MOTOR_2_DIR, MOTOR_2_PUL);     // Horizontal (X)
BasicStepperDriver motorThree(MOTOR_STEPS, MOTOR_3_DIR, MOTOR_3_PUL);   // Vertical (Y)

Encoder encOne(ENCODER_1_CHLA, ENCODER_1_CHLB);
Encoder encTwo(ENCODER_2_CHLA, ENCODER_2_CHLB);
Encoder encThree(ENCODER_3_CHLA, ENCODER_3_CHLB);

Bounce2::Button encBtnOne = Bounce2::Button();
Bounce2::Button encBtnTwo = Bounce2::Button();
Bounce2::Button encBtnThree = Bounce2::Button();

// Stepper scalars
float scaleOne = 200.0;
float scaleTwo = 200.0;
float scaleThree = 200.0;

bool useJoystick = false;       // Control mode flag
long oldPosition[3] = {0, 0, 0};

// PC Control state
bool pcControlMode = false;     // NEW: PC control mode flag
bool motor1Moving = false;      // NEW: Track motor states for PC control
bool motor2Moving = false;
bool motor3Moving = false;
int motor1Direction = 0;        // NEW: Motor directions (1=forward, -1=backward, 0=stop)
int motor2Direction = 0;
int motor3Direction = 0;
unsigned long lastPCCommand = 0;  // NEW: Timestamp of last PC command
const unsigned long PC_TIMEOUT = 5000;  // NEW: 5 second timeout

//---
// Setup function
//---
void setup() {
  motorOne.begin(RPM, MICROSTEPS);
  motorTwo.begin(RPM, MICROSTEPS);
  motorThree.begin(RPM, MICROSTEPS);
  
  btn_init();
  pinMode(JOYSTICK_PRESS, INPUT_PULLUP);

  Serial.begin(9600);
  delay(100);
  Serial.println("Diamond Viewer Ready - Extended with PC Control");
  Serial.println("Commands: X_FORWARD, X_BACK, X_STOP, Y_UP, Y_DOWN, Y_STOP, ROTATE_CW, ROTATE_CCW, ROTATE_STOP, PC_MODE, MANUAL_MODE");
}

//---
// Main loop
//---
void loop() {
  // Always call nextAction() for non-blocking motor control
  motorOne.nextAction();
  motorTwo.nextAction();
  motorThree.nextAction();

  btn_check();
  scalar_update();

  // Check for serial commands from PC
  checkSerialCommands();

  // Check for PC mode timeout (safety feature)
  if (pcControlMode && (millis() - lastPCCommand > PC_TIMEOUT)) {
    Serial.println("PC mode timeout - returning to manual control");
    pcControlMode = false;
    stopAllMotors();
  }

  // Check for joystick button press to toggle modes
  if (digitalRead(JOYSTICK_PRESS) == LOW) {
    delay(50);
    if (digitalRead(JOYSTICK_PRESS) == LOW) {
      // If in PC mode, exit to manual control
      if (pcControlMode) {
        pcControlMode = false;
        stopAllMotors();
        Serial.println("Exiting PC Control Mode - Manual Control Enabled");
      } else {
        // Toggle between encoder and joystick modes
        bool previousMode = useJoystick;
        useJoystick = !useJoystick;
        Serial.println(useJoystick ? "Joystick Control Mode" : "Encoder Control Mode");
        
        if(previousMode && !useJoystick){
          stopAllMotors();
          resetAllEncoders();
        }
      }
      while(digitalRead(JOYSTICK_PRESS) == LOW);
    }
  }

  // Execute control based on mode
  if (pcControlMode) {
    // PC Control Mode: Execute PC commands
    executePCControl();
  } else if (useJoystick) {
    // Manual Joystick Mode
    joystick_check();
  } else {
    // Manual Encoder Mode
    read_and_move(encOne, motorOne, scaleOne, 0);
    read_and_move(encTwo, motorTwo, scaleTwo, 1);
    read_and_move(encThree, motorThree, scaleThree, 2);
  }
}

//---
// NEW: Check for serial commands from PC
//---
void checkSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.length() > 0) {
      processCommand(command);
    }
  }
}

//---
// NEW: Process serial commands
//---
void processCommand(String cmd) {
  // Reset timeout timer on any command received
  lastPCCommand = millis();
  
  // Mode control commands
  if (cmd == "PC_MODE") {
    pcControlMode = true;
    stopAllMotors();
    Serial.println("PC Control Mode Enabled");
    return;
  }
  else if (cmd == "MANUAL_MODE") {
    pcControlMode = false;
    stopAllMotors();
    Serial.println("Manual Control Mode Enabled");
    return;
  }
  
  // Only process motor commands if in PC mode
  if (!pcControlMode) {
    Serial.println("ERROR: Not in PC control mode");
    return;
  }
  
  // X-Axis (Motor 2 - Horizontal camera)
  if (cmd == "X_FORWARD") {
    motor2Direction = 1;
    motor2Moving = true;
    Serial.println("X_FORWARD");
  }
  else if (cmd == "X_BACK") {
    motor2Direction = -1;
    motor2Moving = true;
    Serial.println("X_BACK");
  }
  else if (cmd == "X_STOP") {
    motor2Moving = false;
    motor2Direction = 0;
    motorTwo.startMove(0);
    Serial.println("X_STOP");
  }
  
  // Y-Axis (Motor 3 - Vertical camera)
  else if (cmd == "Y_UP") {
    motor3Direction = 1;
    motor3Moving = true;
    Serial.println("Y_UP");
  }
  else if (cmd == "Y_DOWN") {
    motor3Direction = -1;
    motor3Moving = true;
    Serial.println("Y_DOWN");
  }
  else if (cmd == "Y_STOP") {
    motor3Moving = false;
    motor3Direction = 0;
    motorThree.startMove(0);
    Serial.println("Y_STOP");
  }
  
  // Rotation (Motor 1)
  else if (cmd == "ROTATE_CW") {
    motor1Direction = 1;
    motor1Moving = true;
    Serial.println("ROTATE_CW");
  }
  else if (cmd == "ROTATE_CCW") {
    motor1Direction = -1;
    motor1Moving = true;
    Serial.println("ROTATE_CCW");
  }
  else if (cmd == "ROTATE_STOP") {
    motor1Moving = false;
    motor1Direction = 0;
    motorOne.startMove(0);
    Serial.println("ROTATE_STOP");
  }
  
  // Status query
  else if (cmd == "STATUS") {
    Serial.print("PC_MODE:");
    Serial.print(pcControlMode);
    Serial.print(",M1:");
    Serial.print(motor1Moving);
    Serial.print(",M2:");
    Serial.print(motor2Moving);
    Serial.print(",M3:");
    Serial.println(motor3Moving);
  }
  
  else {
    Serial.print("Unknown command: ");
    Serial.println(cmd);
  }
}

//---
// NEW: Execute PC control movements
//---
void executePCControl() {
  // Motor 1 (Rotation)
  if (motor1Moving) {
    if (motorOne.nextAction() == false) {
      motorOne.startMove(motor1Direction * 1000000);  // Large number for continuous movement
    }
  }
  
  // Motor 2 (Horizontal / X-axis)
  if (motor2Moving) {
    if (motorTwo.nextAction() == false) {
      motorTwo.startMove(motor2Direction * 1000000);
    }
  }
  
  // Motor 3 (Vertical / Y-axis)
  if (motor3Moving) {
    if (motorThree.nextAction() == false) {
      motorThree.startMove(motor3Direction * 1000000);
    }
  }
}

//---
// NEW: Stop all motors
//---
void stopAllMotors() {
  motor1Moving = false;
  motor2Moving = false;
  motor3Moving = false;
  motor1Direction = 0;
  motor2Direction = 0;
  motor3Direction = 0;
  motorOne.startMove(0);
  motorTwo.startMove(0);
  motorThree.startMove(0);
}

//---
// Original encoder control function
//---
void read_and_move(Encoder& encoder, BasicStepperDriver& motor, float scale, int index) {
  long currentPosition = encoder.read();

  if (motor.nextAction() == false) {
    long move_amount = currentPosition - oldPosition[index];

    if (abs(move_amount) > 0) {
      Serial.print("Encoder move detected. New position: ");
      Serial.println(currentPosition);
      long motor_steps = (long)(move_amount * MICROSTEPS * scale);
      motor.startMove(motor_steps);
      Serial.print("Starting new move with steps: ");
      Serial.println(motor_steps);
      
      oldPosition[index] = currentPosition;
    }
  }
}

//---
// Original button initialization
//---
void btn_init(){
  encBtnOne.attach(ENCODER_1_BTN, INPUT_PULLUP);
  encBtnOne.interval(25);
  encBtnOne.setPressedState(LOW); 
  encBtnTwo.attach(ENCODER_2_BTN, INPUT_PULLUP);
  encBtnTwo.interval(25);
  encBtnTwo.setPressedState(LOW);
  encBtnThree.attach(ENCODER_3_BTN, INPUT_PULLUP);
  encBtnThree.interval(25);
  encBtnThree.setPressedState(LOW);
}

//---
// Original button checking
//---
void btn_check(){
  encBtnOne.update();
  encBtnTwo.update();
  encBtnThree.update();
}

//---
// Original scalar update
//---
void scalar_update(){
  if(encBtnOne.pressed()){
    if(scaleOne == 200.0){
      scaleOne = 10.0;
    }
    else
      scaleOne = 200.0;
  }
  if(encBtnTwo.pressed()){
    if(scaleTwo == 200.0){
      scaleTwo = 20.0;
    }
    else
      scaleTwo = 200.0;
  }
  if(encBtnThree.pressed()){
    if(scaleThree == 200.0){
      scaleThree = 20.0;
    }
    else
      scaleThree = 200.0;
  }
}

//---
// Original joystick control
//---
void joystick_check() {
  int joystickX_val = analogRead(JOYSTICK_X);
  int joystickY_val = analogRead(JOYSTICK_Y);
  
  control_motor_with_joystick(joystickX_val, motorOne);
  control_motor_with_joystick(joystickY_val, motorTwo);
}

//---
// Original joystick motor control
//---
void control_motor_with_joystick(int joystickValue, BasicStepperDriver& motor) {
  const int deadzone = 50; 
  int center = 512;
  float mappedRPM = 0;
  static float prevMappedRPM = 0;

  if (abs(joystickValue - center) > deadzone) {
    if (joystickValue > center) {
      prevMappedRPM = mappedRPM;
      mappedRPM = map(joystickValue, center + deadzone, 1023, 0, MAX_RPM);
      if(mappedRPM != prevMappedRPM){
        Serial.println(mappedRPM);
      }
      motor.setRPM(mappedRPM);
      if (motor.nextAction() == false) {
        motor.startMove(1000000000);
      }
    } else {
      prevMappedRPM = mappedRPM;
      mappedRPM = map(joystickValue, 0, center - deadzone, MAX_RPM, 0);
      if(mappedRPM != prevMappedRPM){
        Serial.println(mappedRPM);
      }
      motor.setRPM(mappedRPM);
      if (motor.nextAction() == false) {
        motor.startMove(-1000000000);
      }
    }
  } else {
    motor.setRPM(0); 
  }
}

//---
// Original encoder reset
//---
void resetAllEncoders(){
  encOne.write(0);
  oldPosition[0] = 0;
  encTwo.write(0);
  oldPosition[1] = 0;
  encThree.write(0);
  oldPosition[2] = 0;
  Serial.println("Encoder and motor states reset");
}
