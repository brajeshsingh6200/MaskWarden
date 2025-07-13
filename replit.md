# Face Mask Detection System

## Overview

This is a computer vision application that detects whether people are wearing face masks in real-time video feeds. The system uses OpenCV for face detection, TensorFlow/Keras for mask classification, and provides a GUI interface for monitoring compliance. It includes violation logging, alerting capabilities, and model training functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Modular Design**: The system is organized into separate modules for different functionalities (face detection, mask detection, GUI, utilities)
- **Configuration-Driven**: Centralized configuration management through `config.py`
- **Event-Driven GUI**: Tkinter-based GUI with real-time video processing
- **Machine Learning Pipeline**: Custom CNN model training and inference

### Technology Stack
- **Computer Vision**: OpenCV for face detection and video processing
- **Machine Learning**: TensorFlow/Keras for mask classification
- **GUI Framework**: Tkinter for the desktop interface
- **Image Processing**: PIL/Pillow for image manipulation
- **Data Management**: CSV logging for violation records

## Key Components

### 1. Face Detection (`face_detector.py`)
- **Purpose**: Detects faces in video frames using OpenCV Haar Cascades
- **Technology**: OpenCV CascadeClassifier
- **Configuration**: Configurable detection parameters (scale factor, min neighbors, min size)

### 2. Mask Detection (`mask_detector.py`)
- **Purpose**: Classifies detected faces as wearing masks or not
- **Technology**: Custom CNN model trained with TensorFlow/Keras
- **Input**: Preprocessed face images (224x224 pixels)
- **Output**: Binary classification with confidence scores

### 3. Model Training (`model_trainer.py`)
- **Purpose**: Trains the CNN model for mask detection
- **Architecture**: 4-layer CNN with batch normalization and dropout
- **Features**: Data augmentation, early stopping, model checkpointing
- **Training Data**: Expects organized directories with "with_mask" and "without_mask" categories

### 4. GUI Application (`gui_app.py`)
- **Purpose**: Provides user interface for real-time monitoring
- **Features**: Live video feed, statistics display, violation alerts
- **Threading**: Uses separate threads for video processing to maintain UI responsiveness

### 5. Utilities (`utils.py`)
- **ViolationLogger**: CSV-based logging of mask violations with cooldown periods
- **AlertManager**: Handles violation alerts and notifications
- **VideoProcessor**: Video stream processing utilities

### 6. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Settings**: Model parameters, detection thresholds, GUI settings, file paths

## Data Flow

1. **Video Input**: Camera feed or video file input
2. **Face Detection**: OpenCV detects faces in each frame
3. **Face Preprocessing**: Detected faces are cropped and resized to 224x224
4. **Mask Classification**: CNN model predicts mask presence with confidence
5. **Violation Detection**: Non-masked faces trigger violation logging
6. **GUI Updates**: Real-time display of results and statistics
7. **Logging**: Violations are recorded to CSV with timestamps and positions

## External Dependencies

### Core Libraries
- **OpenCV**: Face detection and video processing
- **TensorFlow/Keras**: Machine learning model training and inference
- **Tkinter**: GUI framework (built into Python)
- **PIL/Pillow**: Image processing
- **NumPy**: Numerical operations
- **Matplotlib**: Training visualization

### System Dependencies
- **Haar Cascade Files**: OpenCV's pre-trained face detection model
- **Camera Access**: System camera for real-time detection
- **File System**: Local storage for models, logs, and training data

## Deployment Strategy

### Local Development
- **Setup**: Create required directories (models, logs, data)
- **Dependencies**: Install Python packages via requirements file
- **Training**: Train model using provided data structure
- **Execution**: Run through `main.py` entry point

### Directory Structure
```
├── models/          # Trained ML models
├── logs/           # System logs and violation records
├── data/           # Training data
│   └── train/
│       ├── with_mask/
│       └── without_mask/
├── config.py       # Configuration settings
├── main.py         # Application entry point
└── [module files]  # Core functionality modules
```

### Configuration Requirements
- **Model Path**: Trained model must be available at configured path
- **Cascade Files**: OpenCV Haar cascade files must be accessible
- **Camera Access**: System camera permissions required
- **File Permissions**: Write access needed for logs and model saving

### Training Prerequisites
- **Dataset**: Organized training images in with_mask/without_mask directories
- **Computing Resources**: GPU recommended for training (CPU fallback available)
- **Storage**: Sufficient disk space for model files and logs

### Runtime Dependencies
- **Real-time Processing**: Adequate CPU/GPU for video processing
- **Memory**: Sufficient RAM for model inference and video buffers
- **Display**: Monitor for GUI interface