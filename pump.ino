#include <SoftwareSerial.h>
#include <TinyGPS++.h>

TinyGPSPlus gps;
SoftwareSerial gpsSerial(4, 3); // RX, TX
const int ledPin = 13;  // LED connected to pin 13

void setup() {
  pinMode(ledPin, OUTPUT);    // Set pin 13 as output for the LED
  Serial.begin(9600);         // Start serial communication for Arduino
  gpsSerial.begin(9600);      // Start GPS communication
}

void loop() {
  // Step 1: Send GPS data to Python
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      if (gps.location.isValid()) {
        float latitude = gps.location.lat();
        float longitude = gps.location.lng();

        // Send latitude and longitude as "latitude,longitude" to Python
        Serial.print(latitude, 6);
        Serial.print(",");
        Serial.println(longitude, 6);

        delay(1000);  // Send data every 1 second
      }
    }
  }

  // Step 2: Listen for signals from Python to control LED
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the command from Python until newline
    command.trim();  // Remove any leading or trailing whitespace

    if (command == "ON") {
      digitalWrite(ledPin, HIGH);  // Turn the LED on
      delay(5000);                 // Keep it on for 1 second
      digitalWrite(ledPin, LOW);   // Turn the LED off
    } else if (command == "OFF") {
      digitalWrite(ledPin, LOW);   // Keep the LED off
    }
  }
}
