import cv2
from ultralytics import YOLO
import serial
import time
import csv
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import os
import subprocess

# Initialize GPS Serial Communication (adjust the COM port and baud rate)
arduino_port = 'COM4'  # Change to your Arduino port (e.g., 'COM3' on Windows)
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate)
    print("GPS Serial connection established.")
except Exception as e:
    print(f"Error connecting to GPS: {e}")
    ser = None  # Continue without GPS if there is a failure

# List of leaf types to check
leaf_types_to_detect = [
    'Apple Scab Leaf', 'Apple rust leaf', 'Bell_pepper leaf spot', 'Blueberry leaf', 'Corn Gray leaf spot',
    'Corn leaf blight', 'Corn rust leaf', 'Potato leaf early blight', 'Potato leaf late blight', 'Squash Powdery mildew leaf', 
    'Tomato Early blight leaf', 'Tomato Septoria leaf spot', 'Tomato leaf bacterial spot', 'Tomato leaf late blight', 
    'Tomato leaf mosaic virus', 'Tomato leaf yellow virus', 'Tomato mold leaf', 'Tomato two spotted spider mites leaf', 'grape leaf black rot'
]

# Remedies for each plant disease
disease_remedies = {
    "Apple Scab Leaf": "Use fungicides such as Captan or Mancozeb. Ensure proper pruning to improve air circulation.",
    "Apple rust leaf": "Apply fungicides early in the season, like Myclobutanil. Remove infected leaves.",
    "Bell_pepper leaf spot": "Use copper-based fungicides and ensure proper crop rotation. Avoid overhead watering.",
    "Blueberry leaf": "Ensure good air circulation, apply fungicides like Captan if needed, and remove diseased leaves.",
    "Corn Gray leaf spot": "Use resistant hybrids, and apply fungicides such as Strobilurins or Triazoles.",
    "Corn leaf blight": "Use fungicides like Mancozeb. Crop rotation and resistant hybrids are also effective.",
    "Corn rust leaf": "Use fungicides containing Triazole, and ensure good plant spacing for air circulation.",
    "Potato leaf early blight": "Apply fungicides such as Chlorothalonil and Mancozeb. Remove affected leaves.",
    "Potato leaf late blight": "Use fungicides like Chlorothalonil and ensure proper spacing to reduce humidity.",
    "Squash Powdery mildew leaf": "Use sulfur-based fungicides, ensure proper spacing for air circulation.",
    "Tomato Early blight leaf": "Remove infected leaves, apply copper-based fungicides, and rotate crops.",
    "Tomato Septoria leaf spot": "Use fungicides like Chlorothalonil and Mancozeb. Remove infected leaves.",
    "Tomato leaf bacterial spot": "Use copper-based bactericides and avoid overhead watering.",
    "Tomato leaf late blight": "Apply fungicides like Chlorothalonil and maintain proper air circulation.",
    "Tomato leaf mosaic virus": "Remove infected plants and avoid handling healthy plants after touching infected ones.",
    "Tomato leaf yellow virus": "Control insect vectors like whiteflies with insecticides and remove infected plants.",
    "Tomato mold leaf": "Use copper-based fungicides and avoid overhead watering. Prune to improve air circulation.",
    "Tomato two spotted spider mites leaf": "Apply miticides, and ensure adequate watering to prevent drought stress.",
    "grape leaf black rot": "Use fungicides such as Mancozeb and remove infected leaves. Prune to improve air circulation."
}

# Initialize a dictionary to count occurrences of detected leaf types
detection_count = {leaf_type: 0 for leaf_type in leaf_types_to_detect}

# Load your custom-trained YOLO model
try:
    model = YOLO(r"D:\Python\object detection\best (1).pt")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Main application class with Tkinter GUI
class LeafDetectionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        # Create a label to display the video feed
        self.video_label = Label(window)
        self.video_label.pack()

        # Start and Stop buttons
        self.btn_start = tk.Button(window, text="Start Detection", command=self.start_detection)
        self.btn_start.pack()

        self.btn_stop = tk.Button(window, text="Stop Detection", command=self.stop_detection)
        self.btn_stop.pack()

        # Button to display histogram
        self.btn_histogram = tk.Button(window, text="Show Detection Histogram", command=self.show_histogram)
        self.btn_histogram.pack()

        # Button to open CSV file
        self.btn_csv = tk.Button(window, text="Open CSV File", command=self.open_csv)
        self.btn_csv.pack()

        # Label to display top 3 detections with remedies
        self.top3_label = Label(window, text="")
        self.top3_label.pack()

        self.is_running = False
        self.csv_file_path = 'detection_log.csv'

    def start_detection(self):
        print("Start Detection button clicked")
        if not self.is_running:
            self.is_running = True
            self.detection_loop()

    def stop_detection(self):
        print("Stop Detection button clicked")
        self.is_running = False
        self.cap.release()
        cv2.destroyAllWindows()
        if ser:
            ser.close()
        
        # After stopping, show the top 3 detected classes and remedies
        self.show_top_3_detections()

    def detection_loop(self):
        print("Detection loop started")
        # Open a CSV file for writing detection data (latitude, longitude, class)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Latitude', 'Longitude', 'Detected Class'])  # Header row

            while self.is_running:
                # Capture frame-by-frame from the webcam
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame.")
                    break

                # Run detection on the frame
                results = model(frame)
                result = results[0]
                target_detected = False
                detected_class = None

                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    class_id = int(box.cls)
                    confidence = box.conf[0]
                    label = f"{result.names[class_id]}: {confidence:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if result.names[class_id] in leaf_types_to_detect:
                        target_detected = True
                        detected_class = result.names[class_id]
                        detection_count[detected_class] += 1

                if target_detected and ser and ser.in_waiting > 0:
                    try:
                        latitude = ser.readline().decode('utf-8').rstrip()
                        longitude = ser.readline().decode('utf-8').rstrip()
                        print(f"Detected leaf type! Latitude: {latitude}, Longitude: {longitude}, Class: {detected_class}")
                        writer.writerow([latitude, longitude, detected_class])
                    except Exception as e:
                        print(f"Error reading GPS data: {e}")

                # Display the frame with bounding boxes in the GUI
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

                # Update the GUI window
                self.window.update_idletasks()
                self.window.update()

    def show_histogram(self):
        print("Show Histogram button clicked")
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

    def open_csv(self):
        print("Open CSV button clicked")
        # Open the CSV file with the default application (e.g., Notepad on Windows)
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(self.csv_file_path)
            else:
                subprocess.call(('xdg-open', self.csv_file_path))  # For Linux/Unix
        except Exception as e:
            print(f"Error opening CSV file: {e}")

    def show_top_3_detections(self):
        print("Showing top 3 detections")
        # Sort the detections by count and get the top 3
        top_detections = sorted(detection_count.items(), key=lambda x: x[1], reverse=True)[:3]

        # Prepare the display text
        display_text = "Top 3 Detected Leaf Types and Remedies:\n"
        for leaf_type, count in top_detections:
            remedy = disease_remedies.get(leaf_type, "No remedy available.")
            display_text += f"{leaf_type} (Count: {count})\nRemedy: {remedy}\n\n"

        self.top3_label.config(text=display_text)

# Create the main window
root = tk.Tk()
app = LeafDetectionApp(root, "Plant Disease Detection App")
root.mainloop()
