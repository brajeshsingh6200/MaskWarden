"""
Configuration settings for the Face Mask Detection System
"""

import os

class Config:
    """Configuration class containing all system settings"""
    
    # Model settings
    MODEL_PATH = "models/mask_detector_model.h5"
    MODEL_INPUT_SIZE = (224, 224)
    BATCH_SIZE = 32
    EPOCHS = 20
    LEARNING_RATE = 0.001
    
    # Face detection settings
    FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"
    FACE_DETECTION_SCALE_FACTOR = 1.1
    FACE_DETECTION_MIN_NEIGHBORS = 5
    FACE_DETECTION_MIN_SIZE = (30, 30)
    
    # Video processing settings
    VIDEO_WIDTH = 640
    VIDEO_HEIGHT = 480
    FPS = 30
    
    # Detection thresholds
    MASK_THRESHOLD = 0.5
    CONFIDENCE_THRESHOLD = 0.5
    
    # Logging settings
    LOG_FILE = "logs/violations.csv"
    LOG_LEVEL = "INFO"
    
    # Alert settings
    ALERT_DURATION = 3  # seconds
    VIOLATION_COOLDOWN = 5  # seconds between logging same violation
    
    # GUI settings
    WINDOW_TITLE = "Face Mask Detection System"
    WINDOW_SIZE = "800x600"
    
    # Colors (BGR format for OpenCV)
    COLOR_MASK = (0, 255, 0)  # Green
    COLOR_NO_MASK = (0, 0, 255)  # Red
    COLOR_UNKNOWN = (255, 255, 0)  # Yellow
    
    # Data paths
    TRAIN_DATA_PATH = "data/train"
    WITH_MASK_PATH = "data/train/with_mask"
    WITHOUT_MASK_PATH = "data/train/without_mask"
    
    # Model architecture
    MODEL_ARCHITECTURE = {
        'conv_layers': [
            {'filters': 32, 'kernel_size': (3, 3), 'activation': 'relu'},
            {'filters': 64, 'kernel_size': (3, 3), 'activation': 'relu'},
            {'filters': 128, 'kernel_size': (3, 3), 'activation': 'relu'}
        ],
        'dense_layers': [
            {'units': 512, 'activation': 'relu'},
            {'units': 256, 'activation': 'relu'},
            {'units': 1, 'activation': 'sigmoid'}
        ],
        'dropout_rate': 0.5
    }
    
    @staticmethod
    def get_opencv_cascade_path():
        """Get the path to OpenCV's Haar cascade file"""
        import cv2
        return cv2.data.haarcascades + Config.FACE_CASCADE_PATH
