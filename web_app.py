#!/usr/bin/env python3
"""
Web-based Face Mask Detection System using Flask
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import base64
import io
import json
import time
from datetime import datetime
import threading
import os

from face_detector import FaceDetector
from mask_detector import MaskDetector
from config import Config
from utils import ViolationLogger, AlertManager

app = Flask(__name__)
app.secret_key = 'face_mask_detection_system_2024'

# Global variables
face_detector = None
mask_detector = None
violation_logger = None
alert_manager = None
camera_active = False
current_stats = {
    'total_faces': 0,
    'masked_faces': 0,
    'unmasked_faces': 0,
    'violations': 0,
    'fps': 0
}

def initialize_components():
    """Initialize all detection components"""
    global face_detector, mask_detector, violation_logger, alert_manager
    
    print("Initializing face mask detection components...")
    face_detector = FaceDetector()
    mask_detector = MaskDetector()
    violation_logger = ViolationLogger()
    alert_manager = AlertManager()
    print("Components initialized successfully!")

def process_frame(frame):
    """Process a single frame for face mask detection"""
    global current_stats
    
    if face_detector is None:
        return frame
    
    # Detect faces
    faces = face_detector.detect_faces(frame)
    current_stats['total_faces'] = len(faces)
    
    masked_count = 0
    unmasked_count = 0
    
    # Process each face
    for face in faces:
        # Extract face region
        face_roi = face_detector.extract_face_roi(frame, face)
        preprocessed_face = face_detector.preprocess_face(face_roi)
        
        # Predict mask
        prediction, confidence = mask_detector.predict_mask(preprocessed_face)
        
        # Update statistics
        if prediction == "With Mask":
            masked_count += 1
        elif prediction == "No Mask":
            unmasked_count += 1
            current_stats['violations'] += 1
        
        # Get color for prediction
        color = mask_detector.get_prediction_color(prediction)
        
        # Draw rectangle and label
        face_detector.draw_face_rectangle(frame, face, prediction, confidence, color)
    
    current_stats['masked_faces'] = masked_count
    current_stats['unmasked_faces'] = unmasked_count
    
    return frame

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    return jsonify(current_stats)

@app.route('/api/start_camera')
def start_camera():
    """Start camera detection"""
    global camera_active
    camera_active = True
    return jsonify({'status': 'success', 'message': 'Camera started'})

@app.route('/api/stop_camera')
def stop_camera():
    """Stop camera detection"""
    global camera_active
    camera_active = False
    return jsonify({'status': 'success', 'message': 'Camera stopped'})

@app.route('/api/test_detection')
def test_detection():
    """Test detection with a sample frame"""
    # Create a test frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (100, 100, 100)  # Gray background
    
    # Add some test rectangles to simulate faces
    cv2.rectangle(frame, (200, 150), (440, 330), (150, 150, 150), -1)
    cv2.putText(frame, "Test Detection", (220, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Process the frame
    processed_frame = process_frame(frame)
    
    # Convert to base64 for web display
    _, buffer = cv2.imencode('.jpg', processed_frame)
    img_str = base64.b64encode(buffer).decode()
    
    return jsonify({
        'status': 'success',
        'image': img_str,
        'stats': current_stats
    })

@app.route('/api/model_status')
def model_status():
    """Get model status information"""
    status = {
        'tensorflow_available': mask_detector.is_model_available() if mask_detector else False,
        'model_loaded': mask_detector.model is not None if mask_detector else False,
        'face_detector_ready': face_detector is not None,
        'cascade_path': Config.get_opencv_cascade_path()
    }
    return jsonify(status)

# Create templates directory and index.html
def create_templates():
    """Create the HTML template"""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Mask Detection System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .control-panel {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .start-btn {
            background-color: #4CAF50;
            color: white;
        }
        .stop-btn {
            background-color: #f44336;
            color: white;
        }
        .test-btn {
            background-color: #2196F3;
            color: white;
        }
        .status-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .video-container {
            text-align: center;
            margin-top: 20px;
        }
        .video-frame {
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .status-message {
            text-align: center;
            padding: 20px;
            color: #666;
            font-style: italic;
        }
        .model-status {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .model-status h3 {
            margin-top: 0;
            color: #1976d2;
        }
        .status-item {
            margin: 5px 0;
        }
        .status-ok {
            color: #4caf50;
        }
        .status-warning {
            color: #ff9800;
        }
        .status-error {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Face Mask Detection System</h1>
        
        <div class="model-status">
            <h3>System Status</h3>
            <div id="model-status-content">
                <div class="status-item">Loading system status...</div>
            </div>
        </div>
        
        <div class="control-panel">
            <button class="test-btn" onclick="testDetection()">Test Detection</button>
            <button class="start-btn" onclick="startCamera()">Start Camera</button>
            <button class="stop-btn" onclick="stopCamera()">Stop Camera</button>
        </div>
        
        <div class="status-panel">
            <div class="stat-card">
                <div class="stat-value" id="total-faces">0</div>
                <div class="stat-label">Total Faces</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="masked-faces">0</div>
                <div class="stat-label">With Mask</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="unmasked-faces">0</div>
                <div class="stat-label">No Mask</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="violations">0</div>
                <div class="stat-label">Violations</div>
            </div>
        </div>
        
        <div class="video-container">
            <div id="video-content">
                <div class="status-message">
                    Click "Test Detection" to see the system in action
                </div>
            </div>
        </div>
    </div>

    <script>
        let statsInterval;
        
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-faces').textContent = data.total_faces;
                    document.getElementById('masked-faces').textContent = data.masked_faces;
                    document.getElementById('unmasked-faces').textContent = data.unmasked_faces;
                    document.getElementById('violations').textContent = data.violations;
                });
        }
        
        function updateModelStatus() {
            fetch('/api/model_status')
                .then(response => response.json())
                .then(data => {
                    const statusContent = document.getElementById('model-status-content');
                    statusContent.innerHTML = `
                        <div class="status-item">
                            <strong>Face Detector:</strong> 
                            <span class="${data.face_detector_ready ? 'status-ok' : 'status-error'}">
                                ${data.face_detector_ready ? 'Ready' : 'Not Ready'}
                            </span>
                        </div>
                        <div class="status-item">
                            <strong>Model Loaded:</strong> 
                            <span class="${data.model_loaded ? 'status-ok' : 'status-warning'}">
                                ${data.model_loaded ? 'Yes' : 'No (Running in demo mode)'}
                            </span>
                        </div>
                        <div class="status-item">
                            <strong>TensorFlow:</strong> 
                            <span class="${data.tensorflow_available ? 'status-ok' : 'status-warning'}">
                                ${data.tensorflow_available ? 'Available' : 'Not Available'}
                            </span>
                        </div>
                    `;
                });
        }
        
        function testDetection() {
            fetch('/api/test_detection')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('video-content').innerHTML = 
                            `<img src="data:image/jpeg;base64,${data.image}" class="video-frame" alt="Detection Result">`;
                        updateStats();
                    }
                });
        }
        
        function startCamera() {
            fetch('/api/start_camera')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('video-content').innerHTML = 
                            '<div class="status-message">Camera started (no camera available in this environment)</div>';
                        statsInterval = setInterval(updateStats, 1000);
                    }
                });
        }
        
        function stopCamera() {
            fetch('/api/stop_camera')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('video-content').innerHTML = 
                            '<div class="status-message">Camera stopped</div>';
                        if (statsInterval) {
                            clearInterval(statsInterval);
                        }
                    }
                });
        }
        
        // Initialize page
        updateStats();
        updateModelStatus();
        
        // Update stats every 5 seconds
        setInterval(updateStats, 5000);
        setInterval(updateModelStatus, 10000);
    </script>
</body>
</html>
    '''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    try:
        print("Starting Face Mask Detection Web Application...")
        
        # Create templates
        create_templates()
        
        # Initialize components
        initialize_components()
        
        # Start the Flask application
        print("Starting web server on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()