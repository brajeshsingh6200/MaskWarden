#!/usr/bin/env python3
"""
Simple test script for Face Mask Detection System without GUI
"""

import cv2
import numpy as np
import time
import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_detector import FaceDetector
from mask_detector import MaskDetector
from config import Config

def test_detection_system():
    """Test the face mask detection system"""
    print("=== Face Mask Detection System Test ===")
    
    # Initialize components
    print("Initializing face detector...")
    face_detector = FaceDetector()
    
    print("Initializing mask detector...")
    mask_detector = MaskDetector()
    
    print("Creating test frame...")
    # Create a test frame with a simple face-like shape
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (100, 100, 100)  # Gray background
    
    # Add a simple rectangle to simulate a face
    cv2.rectangle(frame, (200, 150), (440, 330), (150, 150, 150), -1)
    cv2.putText(frame, "Test Face", (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    print("Processing test frame...")
    frame_count = 0
    
    while frame_count < 5:  # Process the test frame multiple times
        frame_count += 1
        print(f"Processing frame {frame_count}/5...")
        
        # Detect faces
        faces = face_detector.detect_faces(frame)
        
        # Process each face
        for face in faces:
            # Extract face region
            face_roi = face_detector.extract_face_roi(frame, face)
            preprocessed_face = face_detector.preprocess_face(face_roi)
            
            # Predict mask
            prediction, confidence = mask_detector.predict_mask(preprocessed_face)
            
            # Get color for prediction
            color = mask_detector.get_prediction_color(prediction)
            
            # Draw rectangle and label
            face_detector.draw_face_rectangle(frame, face, prediction, confidence, color)
        
        # Print results
        print(f"  Detected {len(faces)} faces")
        for i, face in enumerate(faces):
            print(f"  Face {i+1}: {prediction} (confidence: {confidence:.2f})")
        
        # Small delay between frames
        time.sleep(0.1)
    
    # Cleanup
    print("Test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_detection_system()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()