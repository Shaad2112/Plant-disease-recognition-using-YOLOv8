import csv
import serial
import time

# Set up serial communication with Arduino
arduino = serial.Serial(port='COM4', baudrate=9600, timeout=.1)  # Adjust 'COM4' to your port

def get_real_time_gps():
    if arduino.in_waiting > 0:
        data = arduino.readline().decode().strip()  # Read GPS data from Arduino
        lat, lng = data.split(',')  # Assume latitude and longitude are sent as "lat,lng"
        return float(lat), float(lng)
    return None, None

def read_csv_and_match(file_path, real_time_lat, real_time_lng):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        matched = False
        for row in reader:
            # Extract latitude and longitude from the row
            latitude = float(row[0])
            longitude = float(row[1])
            
            # Check if real-time GPS matches the current row
            if abs(latitude - real_time_lat) < 0.0001 and abs(longitude - real_time_lng) < 0.0001:
                matched = True
                break  # Exit the loop if a match is found

        # Send the signal to Arduino based on whether there was a match
        if matched:
            arduino.write(b'ON')  # Send "ON" signal to Arduino
            print("LED is ON")
        else:
            arduino.write(b'OFF')  # Send "OFF" signal to Arduino
            print("LED is OFF")

# File path to the CSV file
file_path = r'D:\Python\object detection\detection_log.csv'

# Continuously check every second
while True:
    real_time_lat, real_time_lng = get_real_time_gps()  # Get real-time GPS from Arduino
    
    # Proceed only if valid GPS data is received
    if real_time_lat is not None and real_time_lng is not None:
        read_csv_and_match(file_path, real_time_lat, real_time_lng)
    else:
        print("Waiting for GPS data...")
    
    time.sleep(1)  # Check every second
