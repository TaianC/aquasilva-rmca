// AquaSilva Remote Monitoring and Control Application (AquaSilva RMCA), Arduino Instructions for Serial Commandment
// Performs tasks as per requested through serial, also will return sensor output when requested.

// D51 -> Relay South Input 4, GND to RESET Control
// D49 -> DS1820 (Water Temperature) Sensor I/O
// D48 -> Relay North Input 3, Light Toggle
// D50 -> Relay North Input 1, Solenoid Outlet Valve Control
// D52 -> Relay North Input 2, Solenoid Inlet Valve Control
// D53 -> AM2303 (Ambient Temperature and Humidity) Sensor I/O

#include <DHT.h>
#include <DHT_U.h>
#include <DallasTemperature.h>
#include <Servo.h>

#define DHTTYPE DHT22

DHT dht(53, DHTTYPE);
OneWire oneWire(49);
DallasTemperature sensors(&oneWire);
Servo lightControlServo;

int incomingData;
int pos = 0;
float temperature;
float humidity;
bool valveOutletActive = false;
bool valveInletActive = false;
bool lightActive = true;
bool dhtFailed = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(51, OUTPUT);
  pinMode(48, OUTPUT);
  pinMode(50, OUTPUT);
  pinMode(52, OUTPUT);

  digitalWrite(51, HIGH);
  digitalWrite(50, HIGH);
  digitalWrite(52, HIGH);
  
  dht.begin();
  sensors.begin();

  lightControlServo.attach(9);
}

void loop() {
  // Key
  // 
  
  if (Serial.available() > 0) {

    incomingData = Serial.read();

    if (incomingData == '<') {
      if (valveOutletActive == false) {
        valveOutletActive = true;
        digitalWrite(50, LOW);          
      }
      else {
        valveOutletActive = false;
        digitalWrite(50, HIGH);
      }
    }

    if (incomingData == '>') {
      if (valveInletActive == false) {
        valveInletActive = true;
        digitalWrite(52, LOW);          
      }
      else {
        valveInletActive = false;
        digitalWrite(52, HIGH);
      }
    }

    if (incomingData == 'L') {
      Serial.println(lightActive);
      if (lightActive == false) {
        lightActive = true;
        digitalWrite(48, LOW);   
        Serial.println(lightActive);       
      }
      else {
        lightActive = false;
        digitalWrite(48, HIGH);
        Serial.println(lightActive);
      }
    }

    if (incomingData == '[') {
      for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        lightControlServo.write(pos);              // tell servo to go to position in variable 'pos'
        delay(15);                       // waits 15ms for the servo to reach the position
      }
    } 

    if (incomingData == ']') {
      for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
        lightControlServo.write(pos);              // tell servo to go to position in variable 'pos'
        delay(15);                       // waits 15ms for the servo to reach the position
      }
    }

    if (incomingData == ':') {
      
    }

    if (incomingData == 'R') {
      digitalWrite(51, LOW);
    }

    if (incomingData == '%') {
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();
      if (isnan(humidity) || isnan(temperature)) {
        dhtFailed = true;
      }
      else {
        dhtFailed = false;
      }
      sensors.requestTemperatures();
      if (dhtFailed == true) {
        Serial.write("NaN");
        Serial.write(char(sensors.getTempCByIndex(0)));
        Serial.write("NaN");
      }
      else {
        Serial.write(char(temperature));
        Serial.write(char(sensors.getTempCByIndex(0)));
        Serial.write(char(humidity));
      }
    }
    if (incomingData == "?") {
      Serial.println(analogRead(8));
      Serial.println("RESULT")
    }
  }
}
