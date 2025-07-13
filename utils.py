"""
Utility functions for the Face Mask Detection System
"""

import cv2
import csv
import os
import time
from datetime import datetime
import logging
from config import Config

class ViolationLogger:
    """Class for logging mask violations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.log_file = Config.LOG_FILE
        self.last_violation_time = {}
        self.setup_csv_log()
    
    def setup_csv_log(self):
        """Setup CSV log file with headers"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            # Check if file exists and has headers
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        'timestamp',
                        'violation_type',
                        'confidence',
                        'face_position',
                        'duration'
                    ])
                    
            self.logger.info(f"CSV log file setup: {self.log_file}")
            
        except Exception as e:
            self.logger.error(f"Error setting up CSV log: {str(e)}")
    
    def log_violation(self, violation_type, confidence, face_position, duration=None):
        """
        Log a mask violation
        
        Args:
            violation_type: Type of violation (e.g., "No Mask")
            confidence: Confidence score
            face_position: Face position tuple (x, y)
            duration: Duration of violation in seconds
        """
        try:
            current_time = time.time()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check cooldown period
            face_key = f"{face_position[0]}_{face_position[1]}"
            if face_key in self.last_violation_time:
                time_diff = current_time - self.last_violation_time[face_key]
                if time_diff < Config.VIOLATION_COOLDOWN:
                    return  # Skip logging due to cooldown
            
            # Update last violation time
            self.last_violation_time[face_key] = current_time
            
            # Log to CSV
            with open(self.log_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp,
                    violation_type,
                    f"{confidence:.3f}",
                    f"{face_position[0]},{face_position[1]}",
                    duration or "N/A"
                ])
            
            self.logger.info(f"Violation logged: {violation_type} at {face_position}")
            
        except Exception as e:
            self.logger.error(f"Error logging violation: {str(e)}")
    
    def get_violation_count(self, hours=24):
        """
        Get violation count for the last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Number of violations
        """
        try:
            if not os.path.exists(self.log_file):
                return 0
                
            current_time = datetime.now()
            count = 0
            
            with open(self.log_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    log_time = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
                    time_diff = (current_time - log_time).total_seconds() / 3600
                    
                    if time_diff <= hours:
                        count += 1
                        
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting violation count: {str(e)}")
            return 0

class AlertManager:
    """Class for managing alerts and notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_alerts = {}
        self.alert_start_times = {}
    
    def show_alert(self, frame, message, position=(50, 50)):
        """
        Show alert message on frame
        
        Args:
            frame: Video frame
            message: Alert message
            position: Text position tuple
        """
        try:
            # Alert styling
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            color = (0, 0, 255)  # Red
            thickness = 2
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                message, font, font_scale, thickness
            )
            
            # Draw alert background
            cv2.rectangle(
                frame,
                (position[0] - 10, position[1] - text_height - 10),
                (position[0] + text_width + 10, position[1] + 10),
                (0, 0, 0),
                -1
            )
            
            # Draw alert border
            cv2.rectangle(
                frame,
                (position[0] - 10, position[1] - text_height - 10),
                (position[0] + text_width + 10, position[1] + 10),
                color,
                2
            )
            
            # Draw alert text
            cv2.putText(
                frame,
                message,
                position,
                font,
                font_scale,
                color,
                thickness
            )
            
        except Exception as e:
            self.logger.error(f"Error showing alert: {str(e)}")
    
    def trigger_alert(self, alert_id, message):
        """
        Trigger an alert
        
        Args:
            alert_id: Unique alert identifier
            message: Alert message
        """
        try:
            current_time = time.time()
            
            # Check if alert is already active
            if alert_id in self.active_alerts:
                # Check if alert duration has expired
                if current_time - self.alert_start_times[alert_id] > Config.ALERT_DURATION:
                    self.clear_alert(alert_id)
                else:
                    return  # Alert still active
            
            # Activate new alert
            self.active_alerts[alert_id] = message
            self.alert_start_times[alert_id] = current_time
            
            self.logger.warning(f"Alert triggered: {message}")
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")
    
    def clear_alert(self, alert_id):
        """Clear an active alert"""
        try:
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
                del self.alert_start_times[alert_id]
                
        except Exception as e:
            self.logger.error(f"Error clearing alert: {str(e)}")
    
    def get_active_alerts(self):
        """Get all active alerts"""
        return self.active_alerts.copy()
    
    def cleanup_expired_alerts(self):
        """Clean up expired alerts"""
        try:
            current_time = time.time()
            expired_alerts = []
            
            for alert_id, start_time in self.alert_start_times.items():
                if current_time - start_time > Config.ALERT_DURATION:
                    expired_alerts.append(alert_id)
            
            for alert_id in expired_alerts:
                self.clear_alert(alert_id)
                
        except Exception as e:
            self.logger.error(f"Error cleaning up alerts: {str(e)}")

class VideoProcessor:
    """Class for video processing utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def initialize_camera(self, camera_index=0):
        """
        Initialize camera capture
        
        Args:
            camera_index: Camera index (0 for default camera)
            
        Returns:
            OpenCV VideoCapture object
        """
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open camera {camera_index}")
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.VIDEO_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.VIDEO_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, Config.FPS)
            
            self.logger.info(f"Camera {camera_index} initialized successfully")
            return cap
            
        except Exception as e:
            self.logger.error(f"Error initializing camera: {str(e)}")
            raise
    
    def add_info_overlay(self, frame, fps, violation_count, model_status):
        """
        Add information overlay to frame
        
        Args:
            frame: Video frame
            fps: Current FPS
            violation_count: Number of violations
            model_status: Model status string
        """
        try:
            # Overlay styling
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (255, 255, 255)
            thickness = 2
            
            # Frame dimensions
            height, width = frame.shape[:2]
            
            # Create info text
            info_lines = [
                f"FPS: {fps:.1f}",
                f"Violations (24h): {violation_count}",
                f"Model: {model_status}",
                f"Time: {datetime.now().strftime('%H:%M:%S')}"
            ]
            
            # Draw info background
            overlay_height = len(info_lines) * 25 + 20
            cv2.rectangle(
                frame,
                (10, height - overlay_height),
                (300, height - 10),
                (0, 0, 0),
                -1
            )
            
            # Draw info text
            for i, line in enumerate(info_lines):
                y_pos = height - overlay_height + 25 + (i * 25)
                cv2.putText(
                    frame,
                    line,
                    (20, y_pos),
                    font,
                    font_scale,
                    color,
                    thickness
                )
                
        except Exception as e:
            self.logger.error(f"Error adding info overlay: {str(e)}")
    
    def calculate_fps(self, frame_count, start_time):
        """
        Calculate current FPS
        
        Args:
            frame_count: Number of frames processed
            start_time: Start time
            
        Returns:
            Current FPS
        """
        try:
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                return frame_count / elapsed_time
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating FPS: {str(e)}")
            return 0.0
