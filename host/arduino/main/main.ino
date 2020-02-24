// AquaSilva Remote Monitoring and Control Application (AquaSilva RMCA), Arduino Instructions for Serial Commandment
// Performs tasks as per requested through serial, also will return sensor output when requested.

// D40 -> RESET
// D48 -> Relay North Input 3, Light Toggle
// D50 -> Relay North Input 1, Solenoid Outlet Valve Control
// D52 -> Relay North Input 2, Solenoid Inlet Valve Control
// D53 -> AM2303 Sensor I/O

#include "DHT.h"

#define DHTTYPE DHT22

DHT dht(53, DHTTYPE);

int incomingData;
bool valveOutletActive = false;
bool valveInletActive = false;
bool lightActive = true;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(40, OUTPUT);
  pinMode(48, OUTPUT);
  pinMode(50, OUTPUT);
  pinMode(52, OUTPUT);
  dht.begin();
}

void loop() {
  // Key
  // 

  digitalWrite(50, HIGH);
  digitalWrite(52, HIGH);

  if (Serial.available() > 0) {

    incomingData = Serial.read();

    if (incomingData == '<') {
      if (valveOutletActive == false) {
        valveOutletActive = true;
        digitalWrite(50, LOW);          
      }
      if (valveOutletActive == true) {
        valveOutletActive = false;
        digitalWrite(50, HIGH);
      }
    }

    if (incomingData == '>') {
      if (valveInletActive == false) {
        valveInletActive = true;
        digitalWrite(52, LOW);          
      }
      if (valveInletActive == true) {
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
      if (lightActive == true) {
        lightActive = false;
        digitalWrite(48, HIGH);
        Serial.println(lightActive);
      }
    }

    if (incomingData == '[') {
      
    }

    if (incomingData == ']') {

    }

    if (incomingData == 'R') {
      digitalWrite(40, HIGH)
    }

    if (incomingData == '%') {
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();
      if (isnan(humidity) || isnan(temperature)) {
        dhtFailed = true
      }

    }
  }
}
