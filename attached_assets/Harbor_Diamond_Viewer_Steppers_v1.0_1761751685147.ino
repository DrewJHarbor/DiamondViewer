#include <A4988.h>
#include <BasicStepperDriver.h>
#include <DRV8825.h>
#include <DRV8834.h>
#include <DRV8880.h>
#include <MultiDriver.h>
#include <SyncDriver.h>

#include <Wire.h>
#include <Arduino.h>
#include <BasicStepperDriver.h>
#include <Encoder.h>
#include <Bounce2.h>

//---
// Pin and motor settings
//---
#define MOTOR_STEPS 1600     // Number of steps per revolution (1.8 degrees/step)
#define RPM 120             // Speed of turning
#define MICROSTEPS 1        // This is hardwired on your controller
#define MAX_RPM 240         // Control the max speed (might up this)

// **************PIN DECLARATIONS***********************************
// Avoid pins 0 and 1 as they're for serial communication
#define MOTOR_1_PUL  8      // Pulse and direction pins for stepper motors
#define MOTOR_1_DIR  9      //motor one is rotate
#define MOTOR_2_PUL  10
#define MOTOR_2_DIR  11     //motor two is horizontal camera
#define MOTOR_3_PUL  12
#define MOTOR_3_DIR  13     //motor three is vertical camera

// Use interrupt-capable pins for the encoders (pins 2, 3, 18-21 on Mega)
#define ENCODER_1_CHLA  2   // Channel A and B pins for all encoders
#define ENCODER_1_CHLB  3   // For best results, all 3 pins should be interrupts.
#define ENCODER_2_CHLA  18
#define ENCODER_2_CHLB  19
#define ENCODER_3_CHLA  20
#define ENCODER_3_CHLB  21
//Encoder button pins
#define ENCODER_1_BTN   4
#define ENCODER_2_BTN   5
#define ENCODER_3_BTN   6
//Joystick pins
#define JOYSTICK_X      A0
#define JOYSTICK_Y      A1
#define JOYSTICK_PRESS  A2

//---
// Declaring stepper motor, encoder, and button objects
//---
BasicStepperDriver motorOne(MOTOR_STEPS, MOTOR_1_DIR, MOTOR_1_PUL);     //motor one is rotate
BasicStepperDriver motorTwo(MOTOR_STEPS, MOTOR_2_DIR, MOTOR_2_PUL);     //motor two is horizontal camera
BasicStepperDriver motorThree(MOTOR_STEPS, MOTOR_3_DIR, MOTOR_3_PUL);   //motor three is vertical camera

Encoder encOne(ENCODER_1_CHLA, ENCODER_1_CHLB);
Encoder encTwo(ENCODER_2_CHLA, ENCODER_2_CHLB);
Encoder encThree(ENCODER_3_CHLA, ENCODER_3_CHLB);

Bounce2::Button encBtnOne = Bounce2::Button();
Bounce2::Button encBtnTwo = Bounce2::Button();
Bounce2::Button encBtnThree = Bounce2::Button();

// Stepper scalars, these will probably be floats or doubles for more granular control
float scaleOne = 200.0;
float scaleTwo = 200.0;
float scaleThree = 200.0;

bool useJoystick = false;       //flag to control which controller to use

long oldPosition[3] = {0, 0, 0};      //array to store encoder position

//---
// Setup function
//---
void setup() {
  motorOne.begin(RPM, MICROSTEPS);    //initialize all motors
  motorTwo.begin(RPM, MICROSTEPS);
  motorThree.begin(RPM, MICROSTEPS);
  
  btn_init();       //initialize all buttons

  // Initialize joystick pin as an input with a pullup resistor
  pinMode(JOYSTICK_PRESS, INPUT_PULLUP);


  Serial.begin(9600); // Initialize serial for debugging
}

//---
// Main loop
//---
void loop() {
  // Always call nextAction() for each motor to make progress on any current move
  // This is the core of the non-blocking functionality
  motorOne.nextAction();
  motorTwo.nextAction();
  motorThree.nextAction();

  btn_check();    //call to keep button debouncing updated
  scalar_update();

// Use a simple toggle to switch between control modes
  if (digitalRead(JOYSTICK_PRESS) == LOW) {
    delay(50); // Simple debounce for the joystick button
    if (digitalRead(JOYSTICK_PRESS) == LOW) {
      bool previousMode = useJoystick;
      useJoystick = !useJoystick;
      Serial.println(useJoystick ? "Joystick Control Mode" : "Encoder Control Mode");
      //Checking state change and then stopping infinite run of motors and reseting encoder values
      if(previousMode && !useJoystick){
        motorOne.startMove(0);
        motorOne.setRPM(RPM);
        motorTwo.startMove(0);
        motorTwo.setRPM(RPM);
        motorThree.startMove(0);
        motorThree.setRPM(RPM);
        resetAllEncoders();
      }
      while(digitalRead(JOYSTICK_PRESS) == LOW); // Wait for button release
    }
  }

  if (useJoystick) {
    joystick_check();
  } else {
    // Read the encoders and start a new move if a change is detected
    read_and_move(encOne, motorOne, scaleOne, 0);
    read_and_move(encTwo, motorTwo, scaleTwo, 1);
    read_and_move(encThree, motorThree, scaleThree, 2);
  }
}

//---
// Function to read an encoder and control a motor
//---
/*void read_and_move(Encoder& encoder, BasicStepperDriver& motor, float scale, int index) {

  long newPosition = encoder.read();
  long move_amount = newPosition - oldPosition[index];

  if (abs(move_amount) > 0) {
    Serial.println(newPosition);
    if (motor.nextAction() == false) { // Check if the motor is currently idle
      long motor_steps = (long)(move_amount * MICROSTEPS * scale);
      motor.startMove(motor_steps);
      Serial.print("start new move: ");
      Serial.println(motor_steps);
      oldPosition[index] = newPosition; // Only update oldPosition after starting a move
    }
  }
}
*/
void read_and_move(Encoder& encoder, BasicStepperDriver& motor, float scale, int index) {
  // Read the current position of the encoder
  long currentPosition = encoder.read();

  // If the motor is currently idle, command a new move
  if (motor.nextAction() == false) {
    long move_amount = currentPosition - oldPosition[index];

    if (abs(move_amount) > 0) {
      Serial.print("Encoder move detected. New position: ");
      Serial.println(currentPosition);
      long motor_steps = (long)(move_amount * MICROSTEPS * scale);
      motor.startMove(motor_steps);
      Serial.print("Starting new move with steps: ");
      Serial.println(motor_steps);
      
      // Update the oldPosition to the current position so the next calculation is correct
      oldPosition[index] = currentPosition;
    }
  }
}

void btn_init(){
  encBtnOne.attach(ENCODER_1_BTN, INPUT_PULLUP);
  encBtnOne.interval(25);   //in ms, non blocking
  encBtnOne.setPressedState(LOW); 
  encBtnTwo.attach(ENCODER_2_BTN, INPUT_PULLUP);
  encBtnTwo.interval(25);   //in ms, non blocking
  encBtnTwo.setPressedState(LOW);
  encBtnThree.attach(ENCODER_3_BTN, INPUT_PULLUP);
  encBtnThree.interval(25);   //in ms, non blocking
  encBtnThree.setPressedState(LOW);
}

void btn_check(){
  encBtnOne.update();
  encBtnTwo.update();
  encBtnThree.update();
}

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
// Joystick control function
//---
void joystick_check() {
  // Read joystick values
  int joystickX_val = analogRead(JOYSTICK_X);
  int joystickY_val = analogRead(JOYSTICK_Y);
  
  // Control motorOne and motorTwo with the joystick's X and Y axes
  control_motor_with_joystick(joystickX_val, motorOne);
  control_motor_with_joystick(joystickY_val, motorTwo);
  
  // You could add logic for the third motor here if needed
}

//---
// Generic function to control a motor with a joystick axis
//---
void control_motor_with_joystick(int joystickValue, BasicStepperDriver& motor) {
  // Define a deadzone to prevent jitter
  const int deadzone = 50; 
  int center = 512;
  float mappedRPM = 0;
  float prevMappedRPM = 0;

  if (abs(joystickValue - center) > deadzone) {
    // Map the joystick value to a range of RPMs
    if (joystickValue > center) {
      prevMappedRPM = mappedRPM;
      mappedRPM = map(joystickValue, center + deadzone, 1023, 0, MAX_RPM);
      if(mappedRPM != prevMappedRPM){
        Serial.println(mappedRPM);
      }
      motor.setRPM(mappedRPM);
      if (motor.nextAction() == false) {
        motor.startMove(1000000000); // A very large number of steps
      }
    } else { // joystickValue < center
      prevMappedRPM = mappedRPM;
      mappedRPM = map(joystickValue, 0, center - deadzone, MAX_RPM, 0);
      if(mappedRPM != prevMappedRPM){
        Serial.println(mappedRPM);
      }
      motor.setRPM(mappedRPM);
      if (motor.nextAction() == false) {
        motor.startMove(-1000000000); // A very large negative number of steps
      }
    }
  } else {
    // Joystick is in the deadzone, set motor speed to 0 to stop it
    motor.setRPM(0); 
  }
}

//reset all encoder states 
void resetAllEncoders(){
  encOne.write(0);
  oldPosition[0] = 0;
  encTwo.write(0);
  oldPosition[1] = 0;
  encThree.write(0);
  oldPosition[2] = 0;
  Serial.println("Encoder and motor states reset");
}