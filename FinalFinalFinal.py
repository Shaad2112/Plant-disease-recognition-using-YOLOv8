import cv2
from ultralytics import YOLO
import serial
import time
import csv
import matplotlib.pyplot as plt

# Initialize GPS Serial Communication (adjust the COM port and baud rate)
arduino_port = 'COM4'  
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate)
    print("GPS Serial connection established.")
except Exception as e:
    print(f"Error connecting to GPS: {e}")
    exit()

# List of leaf types to check
leaf_types_to_detect = [
    'Apple Scab Leaf', 'Apple rust leaf', 'Bell_pepper leaf spot','Blueberry leaf', 'Corn Gray leaf spot', 'Corn leaf blight', 'Corn rust leaf', 'Potato leaf early blight',
    'Potato leaf late blight','Squash Powdery mildew leaf', 'Tomato Early blight leaf', 'Tomato Septoria leaf spot', 'Tomato leaf bacterial spot',
    'Tomato leaf late blight', 'Tomato leaf mosaic virus', 'Tomato leaf yellow virus', 'Tomato mold leaf',
    'Tomato two spotted spider mites leaf', 'grape leaf black rot'
]

# Initialize a dictionary to count occurrences of detected leaf types
detection_count = {leaf_type: 0 for leaf_type in leaf_types_to_detect}

# Load your custom-trained YOLO model
try:
    model = YOLO(r"D:\Python\object detection\best (1).pt")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Initialize webcam (0 is usually the default webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Open a CSV file for writing detection data (latitude, longitude, class)
with open('detection_log.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Latitude', 'Longitude', 'Detected Class'])  # Header row

    while True:
        # Capture frame-by-frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Run detection on the frame
        results = model(frame)

        # Access the first result
        result = results[0]

        # Flag to track if any target leaf type is detected
        target_detected = False
        detected_class = None

        # Loop over all detected objects
        for box in result.boxes:
            # Extract bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw bounding box on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Extract class label and confidence score
            class_id = int(box.cls)
            confidence = box.conf[0]

            # Display class label and confidence (assuming your class names are in result.names)
            label = f"{result.names[class_id]}: {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Check if the detected class is in the leaf types of interest
            if result.names[class_id] in leaf_types_to_detect:
                target_detected = True
                detected_class = result.names[class_id]

                # Increment the count for the detected class
                detection_count[detected_class] += 1

        # If a target leaf type is detected, fetch and print GPS data, and save to CSV
        if target_detected:
            if ser.in_waiting > 0:
                try:
                    latitude = ser.readline().decode('utf-8').rstrip()
                    longitude = ser.readline().decode('utf-8').rstrip()
                    print(f"Detected leaf type! Latitude: {latitude}, Longitude: {longitude}, Class: {detected_class}")

                    # Write only latitude, longitude, and detected class to the CSV file
                    writer.writerow([latitude, longitude, detected_class])

                except Exception as e:
                    print(f"Error reading GPS data: {e}")

        # Display the frame with bounding boxes
        cv2.imshow('YOLO Leaf Detection with GPS', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
ser.close()  # Close GPS serial connection when done

# Plot the histogram of detected leaf types
detected_leaves = {leaf: count for leaf, count in detection_count.items() if count > 0}

if detected_leaves:
    plt.bar(detected_leaves.keys(), detected_leaves.values())
    plt.xlabel('Leaf Types')
    plt.ylabel('Number of Detections')
    plt.title('Detected Leaf Types and Their Counts')
    plt.xticks(rotation=90)  # Rotate x labels for better readability
    plt.tight_layout()
    plt.show()
else:
    print("No leaf types were detected during the session.")
