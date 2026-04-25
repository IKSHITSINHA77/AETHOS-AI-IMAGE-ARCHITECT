from ultralytics import YOLO
import os

print("--- Starting smoke test ---")
try:
    model = YOLO("yolov8n.pt")
    print("YOLO model loaded successfully!")
    # Test on a small dummy if possible, or just confirm it works
    print("Success")
except Exception as e:
    print(f"Error: {e}")
