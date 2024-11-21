import serial
import time  # Import time module for adding a delay

# Set up the serial connection (adjust the COM port and baud rate)
arduino_port = 'COM4'  # Change to your Arduino port (e.g., 'COM3' on Windows)
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)

print("Reading GPS coordinates (latitude and longitude) from Arduino every 1 seconds:")

while True:
    if ser.in_waiting > 0:
        # Read latitude and longitude data from serial
        latitude = ser.readline().decode('utf-8').rstrip()
        longitude = ser.readline().decode('utf-8').rstrip()

        # Print latitude and longitude together
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        
        # Add a delay of 1 seconds
        time.sleep(1)