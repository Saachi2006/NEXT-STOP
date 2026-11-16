
import cv2
import serial
import time
import os

# CHANGE THIS to your ESP32 COM port
PORT = "COM3"

BAUD_RATE = 115200

# Your video filename
VIDEO_FILE = "NEXT_STOP_VIDEO.mp4"

# Stop notification times (in seconds)
# These are starting estimates; we can fine-tune them later.
events = events = events = [
    (3, "APPROACH,Maple Road"),
    (12, "APPROACH,City Hall"),
    (22, "APPROACH,Riverside"),
    (30, "APPROACH_DESTINATION,College Gate"),
    (35, "ARRIVED,College Gate")
]

# Check that the video exists
if not os.path.exists(VIDEO_FILE):
    print("ERROR: Video file not found!")
    print("Check the video filename and folder.")
    raise SystemExit

# Open video
video = cv2.VideoCapture(VIDEO_FILE)


if not video.isOpened():
    print("ERROR: Could not open video.")
    raise SystemExit

# Connect to ESP32
try:
    esp32 = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    esp32.reset_input_buffer()
    print("ESP32 connected successfully!")
except serial.SerialException as error:
    print("Could not connect to ESP32:", error)
    video.release()
    raise SystemExit

print("Starting journey simulation...")

start_time = time.perf_counter()
event_index = 0

try:
    while True:
        elapsed = time.perf_counter() - start_time

        # Send each stop command once
        while event_index < len(events) and elapsed >= events[event_index][0]:
            command = events[event_index][1]
            esp32.write((command + "\n").encode())
            print("Sent:", command)
            event_index += 1

        # Read and display video
        success, frame = video.read()

        if not success:
            print("Journey video finished.")
            break

        cv2.imshow("NEXT STOP - Journey Simulation", frame)

        fps = video.get(cv2.CAP_PROP_FPS)
        delay = max(1, int(1000 / fps)) if fps > 0 else 33

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

finally:
    video.release()
    cv2.destroyAllWindows()
    esp32.close()
    print("Simulation stopped.")
