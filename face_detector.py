"""
Face Detection Module using OpenCV Haar Cascades
"""

import cv2
import numpy as np
from config import Config
import logging

class FaceDetector:
    """Class for detecting faces in images using OpenCV"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.face_cascade = None
        self.load_cascade()
    
    def load_cascade(self):
        """Load the Haar cascade classifier for face detection"""
        try:
            cascade_path = Config.get_opencv_cascade_path()
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise ValueError("Could not load face cascade classifier")
                
            self.logger.info("Face cascade classifier loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading face cascade: {str(e)}")
            raise
    
    def detect_faces(self, frame):
        """
        Detect faces in the given frame
        
        Args:
            frame: Input image frame
            
        Returns:
            List of face rectangles (x, y, w, h)
        """
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=Config.FACE_DETECTION_SCALE_FACTOR,
                minNeighbors=Config.FACE_DETECTION_MIN_NEIGHBORS,
                minSize=Config.FACE_DETECTION_MIN_SIZE
            )
            
            return faces
            
        except Exception as e:
            self.logger.error(f"Error detecting faces: {str(e)}")
            return []
    
    def extract_face_roi(self, frame, face_rect):
        """
        Extract face region of interest from frame
        
        Args:
            frame: Input image frame
            face_rect: Face rectangle (x, y, w, h)
            
        Returns:
            Extracted face region
        """
        try:
            x, y, w, h = face_rect
            
            # Add padding around the face
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(frame.shape[1] - x, w + 2 * padding)
            h = min(frame.shape[0] - y, h + 2 * padding)
            
            # Extract face region
            face_roi = frame[y:y+h, x:x+w]
            
            return face_roi
            
        except Exception as e:
            self.logger.error(f"Error extracting face ROI: {str(e)}")
            return None
    
    def preprocess_face(self, face_roi):
        """
        Preprocess face region for model prediction
        
        Args:
            face_roi: Face region of interest
            
        Returns:
            Preprocessed face ready for model input
        """
        try:
            if face_roi is None or face_roi.size == 0:
                return None
                
            # Resize to model input size
            face_resized = cv2.resize(face_roi, Config.MODEL_INPUT_SIZE)
            
            # Normalize pixel values
            face_normalized = face_resized.astype(np.float32) / 255.0
            
            # Add batch dimension
            face_batch = np.expand_dims(face_normalized, axis=0)
            
            return face_batch
            
        except Exception as e:
            self.logger.error(f"Error preprocessing face: {str(e)}")
            return None
    
    def draw_face_rectangle(self, frame, face_rect, label, confidence, color):
        """
        Draw rectangle around detected face with label
        
        Args:
            frame: Input frame
            face_rect: Face rectangle (x, y, w, h)
            label: Text label
            confidence: Confidence score
            color: Rectangle color
        """
        try:
            x, y, w, h = face_rect
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Prepare label text
            text = f"{label}: {confidence:.2f}"
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Draw label background
            cv2.rectangle(
                frame,
                (x, y - text_height - 10),
                (x + text_width, y),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                frame,
                text,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            
        except Exception as e:
            self.logger.error(f"Error drawing face rectangle: {str(e)}")
    
    def get_face_center(self, face_rect):
        """
        Get center point of face rectangle
        
        Args:
            face_rect: Face rectangle (x, y, w, h)
            
        Returns:
            Tuple of (center_x, center_y)
        """
        x, y, w, h = face_rect
        center_x = x + w // 2
        center_y = y + h // 2
        return (center_x, center_y)
    
    def is_valid_face(self, face_rect, frame_shape):
        """
        Check if detected face is valid
        
        Args:
            face_rect: Face rectangle (x, y, w, h)
            frame_shape: Frame dimensions
            
        Returns:
            Boolean indicating if face is valid
        """
        try:
            x, y, w, h = face_rect
            frame_height, frame_width = frame_shape[:2]
            
            # Check if face is within frame bounds
            if x < 0 or y < 0 or x + w > frame_width or y + h > frame_height:
                return False
                
            # Check minimum face size
            if w < Config.FACE_DETECTION_MIN_SIZE[0] or h < Config.FACE_DETECTION_MIN_SIZE[1]:
                return False
                
            # Check aspect ratio (faces should be roughly square)
            aspect_ratio = w / h
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating face: {str(e)}")
            return False
