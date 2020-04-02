// AquaSilva Water Level Sensor Testing
// Plug sensor into A8.

const int pin = A0; 
int data;         
int incomingData;

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {

    incomingData = Serial.read();

    if (incomingData == "!") {
      data = analogRead(pin);
      Serial.println(data);
    }
  }
}
