#include <SoftwareSerial.h>
#include <TinyGPS++.h>

TinyGPSPlus gps;
SoftwareSerial gpsSerial(4, 3); // RX, TX

void setup() {
  Serial.begin(9600);
  gpsSerial.begin(9600);
}

void loop() {
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      if (gps.location.isValid()) {
        float latitude = gps.location.lat();
        float longitude = gps.location.lng();
        
        // Send latitude and longitude to the serial port
        //Serial.print("Latitude: ");
        Serial.println(latitude, 6); // Print latitude with 6 decimal places
        //Serial.print("Longitude: ");
        Serial.println(longitude, 6); // Print longitude with 6 decimal places
      }
    }
  }
}
