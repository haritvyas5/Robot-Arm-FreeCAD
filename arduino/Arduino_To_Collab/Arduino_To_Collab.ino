// Read four potentiometers and send one comma-separated message per line.
// Adapted from haritvyas5/Robot-Arm; see the repository MIT license.

const int potPin1 = A0;  // Base rotation.
const int potPin2 = A1;  // Shoulder.
const int potPin3 = A2;  // Elbow.
const int potPin4 = A3;  // Wrist.

void setup() {
  Serial.begin(9600);  // Match BAUD_RATE in robot_arm.py.
}

void loop() {
  int sensorValue1 = analogRead(potPin1);
  int sensorValue2 = analogRead(potPin2);
  int sensorValue3 = analogRead(potPin3);
  int sensorValue4 = analogRead(potPin4);

  Serial.print(sensorValue1);
  Serial.print(",");
  Serial.print(sensorValue2);
  Serial.print(",");
  Serial.print(sensorValue3);
  Serial.print(",");
  Serial.println(sensorValue4);  // End the message with a newline.

  delay(10);  // Pause briefly before reading the knobs again.
}
