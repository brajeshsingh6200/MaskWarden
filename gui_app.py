"""
GUI Application for Face Mask Detection System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import os

from face_detector import FaceDetector
from mask_detector import MaskDetector
from utils import ViolationLogger, AlertManager, VideoProcessor
from model_trainer import MaskDetectionModelTrainer
from config import Config
import logging

class FaceMaskDetectionGUI:
    """Main GUI application for face mask detection"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(Config.WINDOW_TITLE)
        self.root.geometry(Config.WINDOW_SIZE)
        
        # Initialize components
        self.logger = logging.getLogger(__name__)
        self.face_detector = FaceDetector()
        self.mask_detector = MaskDetector()
        self.violation_logger = ViolationLogger()
        self.alert_manager = AlertManager()
        self.video_processor = VideoProcessor()
        
        # GUI variables
        self.is_running = False
        self.cap = None
        self.current_frame = None
        self.frame_count = 0
        self.start_time = time.time()
        
        # Statistics
        self.stats = {
            'total_faces': 0,
            'masked_faces': 0,
            'unmasked_faces': 0,
            'violations': 0
        }
        
        # Create GUI
        self.create_gui()
        
        # Setup logging display
        self.setup_logging_display()
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Controls
        self.create_control_panel(main_frame)
        
        # Right panel - Video display
        self.create_video_panel(main_frame)
        
        # Bottom panel - Statistics and logs
        self.create_status_panel(main_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Start/Stop buttons
        self.start_button = ttk.Button(
            control_frame,
            text="Start Detection",
            command=self.start_detection,
            style="Success.TButton"
        )
        self.start_button.pack(fill=tk.X, pady=(0, 5))
        
        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Detection",
            command=self.stop_detection,
            state=tk.DISABLED,
            style="Danger.TButton"
        )
        self.stop_button.pack(fill=tk.X, pady=(0, 10))
        
        # Model controls
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Model Management:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.train_button = ttk.Button(
            control_frame,
            text="Train Model",
            command=self.train_model
        )
        self.train_button.pack(fill=tk.X, pady=(5, 0))
        
        self.load_model_button = ttk.Button(
            control_frame,
            text="Load Model",
            command=self.load_model
        )
        self.load_model_button.pack(fill=tk.X, pady=(5, 0))
        
        # Model status
        self.model_status_var = tk.StringVar()
        self.model_status_var.set("Model: Not Loaded")
        ttk.Label(control_frame, textvariable=self.model_status_var).pack(anchor=tk.W, pady=(10, 0))
        
        # Settings
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 10))
        
        ttk.Label(control_frame, text="Settings:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Confidence threshold
        ttk.Label(control_frame, text="Confidence Threshold:").pack(anchor=tk.W, pady=(5, 0))
        self.confidence_var = tk.DoubleVar(value=Config.CONFIDENCE_THRESHOLD)
        confidence_scale = ttk.Scale(
            control_frame,
            from_=0.1,
            to=1.0,
            variable=self.confidence_var,
            orient=tk.HORIZONTAL
        )
        confidence_scale.pack(fill=tk.X, pady=(0, 5))
        
        # Alert settings
        self.alert_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            control_frame,
            text="Enable Alerts",
            variable=self.alert_enabled_var
        ).pack(anchor=tk.W, pady=(5, 0))
        
        self.logging_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            control_frame,
            text="Enable Logging",
            variable=self.logging_enabled_var
        ).pack(anchor=tk.W, pady=(5, 0))
    
    def create_video_panel(self, parent):
        """Create the video display panel"""
        video_frame = ttk.LabelFrame(parent, text="Live Video Feed", padding="10")
        video_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video display
        self.video_label = ttk.Label(video_frame, text="Video feed will appear here", anchor=tk.CENTER)
        self.video_label.pack(expand=True, fill=tk.BOTH)
        
        # Update model status
        self.update_model_status()
    
    def create_status_panel(self, parent):
        """Create the status and statistics panel"""
        status_frame = ttk.LabelFrame(parent, text="Status & Statistics", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(status_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Statistics tab
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        
        # Create statistics display
        self.create_statistics_display(stats_frame)
        
        # Logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Logs")
        
        # Create logs display
        self.create_logs_display(logs_frame)
    
    def create_statistics_display(self, parent):
        """Create the statistics display"""
        # Statistics labels
        self.stats_vars = {}
        
        stats_labels = [
            ("Total Faces Detected", "total_faces"),
            ("Faces with Mask", "masked_faces"),
            ("Faces without Mask", "unmasked_faces"),
            ("Violations Logged", "violations")
        ]
        
        for i, (label, key) in enumerate(stats_labels):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            self.stats_vars[key] = tk.StringVar(value="0")
            ttk.Label(parent, textvariable=self.stats_vars[key], font=("Arial", 10, "bold")).grid(row=i, column=1, sticky=tk.W)
        
        # FPS display
        ttk.Label(parent, text="FPS:").grid(row=len(stats_labels), column=0, sticky=tk.W, padx=(0, 10))
        self.fps_var = tk.StringVar(value="0.0")
        ttk.Label(parent, textvariable=self.fps_var, font=("Arial", 10, "bold")).grid(row=len(stats_labels), column=1, sticky=tk.W)
        
        # Clear statistics button
        ttk.Button(
            parent,
            text="Clear Statistics",
            command=self.clear_statistics
        ).grid(row=len(stats_labels) + 1, column=0, columnspan=2, pady=(10, 0))
    
    def create_logs_display(self, parent):
        """Create the logs display"""
        # Log text area
        self.log_text = tk.Text(parent, height=10, width=50)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Clear logs button
        ttk.Button(
            parent,
            text="Clear Logs",
            command=self.clear_logs
        ).pack(side=tk.BOTTOM, pady=(10, 0))
    
    def setup_logging_display(self):
        """Setup logging to display in GUI"""
        class GuiLogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        # Add GUI handler to logger
        gui_handler = GuiLogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
    
    def start_detection(self):
        """Start face mask detection"""
        try:
            if not self.mask_detector.is_model_available():
                messagebox.showerror("Error", "Model not available. Please train or load a model first.")
                return
            
            # Initialize camera
            self.cap = self.video_processor.initialize_camera()
            
            # Reset statistics
            self.stats = {
                'total_faces': 0,
                'masked_faces': 0,
                'unmasked_faces': 0,
                'violations': 0
            }
            
            self.frame_count = 0
            self.start_time = time.time()
            
            # Update UI
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Start detection thread
            self.detection_thread = threading.Thread(target=self.detection_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()
            
            self.logger.info("Face mask detection started")
            
        except Exception as e:
            self.logger.error(f"Error starting detection: {str(e)}")
            messagebox.showerror("Error", f"Could not start detection: {str(e)}")
    
    def stop_detection(self):
        """Stop face mask detection"""
        try:
            self.is_running = False
            
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Update UI
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Clear video display
            self.video_label.config(image='', text="Video feed will appear here")
            
            self.logger.info("Face mask detection stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping detection: {str(e)}")
    
    def detection_loop(self):
        """Main detection loop"""
        while self.is_running:
            try:
                if self.cap is None:
                    break
                
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Could not read frame from camera")
                    break
                
                # Process frame
                self.process_frame(frame)
                
                # Update GUI
                self.root.after(0, self.update_gui)
                
                # Small delay to prevent overwhelming the GUI
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Error in detection loop: {str(e)}")
                break
    
    def process_frame(self, frame):
        """Process a single frame for face mask detection"""
        try:
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            
            # Process each face
            for face in faces:
                if not self.face_detector.is_valid_face(face, frame.shape):
                    continue
                
                # Extract and preprocess face
                face_roi = self.face_detector.extract_face_roi(frame, face)
                face_processed = self.face_detector.preprocess_face(face_roi)
                
                if face_processed is not None:
                    # Predict mask
                    prediction, confidence = self.mask_detector.predict_mask(face_processed)
                    
                    # Validate prediction
                    prediction, is_valid = self.mask_detector.validate_prediction(prediction, confidence)
                    
                    if is_valid:
                        # Update statistics
                        self.stats['total_faces'] += 1
                        if prediction == "With Mask":
                            self.stats['masked_faces'] += 1
                        elif prediction == "No Mask":
                            self.stats['unmasked_faces'] += 1
                            
                            # Log violation
                            if self.logging_enabled_var.get():
                                face_center = self.face_detector.get_face_center(face)
                                self.violation_logger.log_violation(
                                    prediction, confidence, face_center
                                )
                                self.stats['violations'] += 1
                            
                            # Trigger alert
                            if self.alert_enabled_var.get():
                                self.alert_manager.trigger_alert(
                                    f"face_{face[0]}_{face[1]}",
                                    "MASK VIOLATION DETECTED!"
                                )
                    
                    # Draw face rectangle
                    color = self.mask_detector.get_prediction_color(prediction)
                    self.face_detector.draw_face_rectangle(
                        frame, face, prediction, confidence, color
                    )
            
            # Show active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            for i, (alert_id, message) in enumerate(active_alerts.items()):
                self.alert_manager.show_alert(frame, message, (50, 50 + i * 40))
            
            # Clean up expired alerts
            self.alert_manager.cleanup_expired_alerts()
            
            # Add info overlay
            fps = self.video_processor.calculate_fps(self.frame_count, self.start_time)
            violation_count = self.violation_logger.get_violation_count()
            model_status = "Active" if self.mask_detector.is_model_available() else "Inactive"
            
            self.video_processor.add_info_overlay(frame, fps, violation_count, model_status)
            
            # Update frame count
            self.frame_count += 1
            
            # Store current frame
            self.current_frame = frame
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
    
    def update_gui(self):
        """Update GUI with current frame and statistics"""
        try:
            if self.current_frame is not None:
                # Convert frame to PhotoImage
                frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                
                # Update video display
                self.video_label.config(image=frame_tk, text="")
                self.video_label.image = frame_tk
            
            # Update statistics
            for key, var in self.stats_vars.items():
                var.set(str(self.stats[key]))
            
            # Update FPS
            fps = self.video_processor.calculate_fps(self.frame_count, self.start_time)
            self.fps_var.set(f"{fps:.1f}")
            
        except Exception as e:
            self.logger.error(f"Error updating GUI: {str(e)}")
    
    def train_model(self):
        """Train the mask detection model"""
        try:
            # Check if training data exists
            if not os.path.exists(Config.TRAIN_DATA_PATH):
                messagebox.showerror(
                    "Error", 
                    f"Training data not found at {Config.TRAIN_DATA_PATH}\n"
                    f"Please add images to:\n"
                    f"- {Config.WITH_MASK_PATH}\n"
                    f"- {Config.WITHOUT_MASK_PATH}"
                )
                return
            
            # Confirm training
            if not messagebox.askyesno("Confirm Training", "This will take some time. Continue?"):
                return
            
            # Disable buttons during training
            self.train_button.config(state=tk.DISABLED)
            self.model_status_var.set("Model: Training...")
            
            # Start training in separate thread
            training_thread = threading.Thread(target=self.train_model_thread)
            training_thread.daemon = True
            training_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting model training: {str(e)}")
            messagebox.showerror("Error", f"Could not start training: {str(e)}")
    
    def train_model_thread(self):
        """Train model in separate thread"""
        try:
            trainer = MaskDetectionModelTrainer()
            
            # Create and train model
            trainer.create_model()
            train_gen, val_gen = trainer.prepare_data()
            trainer.train_model(train_gen, val_gen)
            trainer.save_model()
            
            # Reload model in mask detector
            self.mask_detector.load_model()
            
            # Update GUI
            self.root.after(0, self.training_completed)
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            self.root.after(0, lambda: self.training_failed(str(e)))
    
    def training_completed(self):
        """Handle training completion"""
        self.train_button.config(state=tk.NORMAL)
        self.update_model_status()
        messagebox.showinfo("Success", "Model training completed successfully!")
    
    def training_failed(self, error_msg):
        """Handle training failure"""
        self.train_button.config(state=tk.NORMAL)
        self.update_model_status()
        messagebox.showerror("Error", f"Model training failed: {error_msg}")
    
    def load_model(self):
        """Load a pre-trained model"""
        try:
            model_path = filedialog.askopenfilename(
                title="Select Model File",
                filetypes=[("H5 files", "*.h5"), ("All files", "*.*")]
            )
            
            if model_path:
                # Update config
                Config.MODEL_PATH = model_path
                
                # Reload model
                self.mask_detector.load_model()
                
                # Update GUI
                self.update_model_status()
                
                messagebox.showinfo("Success", "Model loaded successfully!")
                
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            messagebox.showerror("Error", f"Could not load model: {str(e)}")
    
    def update_model_status(self):
        """Update model status display"""
        if self.mask_detector.is_model_available():
            self.model_status_var.set("Model: Ready")
        else:
            self.model_status_var.set("Model: Not Loaded")
    
    def clear_statistics(self):
        """Clear all statistics"""
        self.stats = {
            'total_faces': 0,
            'masked_faces': 0,
            'unmasked_faces': 0,
            'violations': 0
        }
        self.frame_count = 0
        self.start_time = time.time()
        
        # Update GUI
        for key, var in self.stats_vars.items():
            var.set("0")
        self.fps_var.set("0.0")
        
        self.logger.info("Statistics cleared")
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        self.logger.info("Log display cleared")
    
    def on_closing(self):
        """Handle application closing"""
        try:
            if self.is_running:
                self.stop_detection()
            
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    def run(self):
        """Run the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = FaceMaskDetectionGUI()
    app.run()
