"""
Mask Detection Module using trained CNN model
"""

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from config import Config
import logging
import os

class MaskDetector:
    """Class for detecting face masks using trained CNN model"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained mask detection model"""
        try:
            if not os.path.exists(Config.MODEL_PATH):
                self.logger.warning(f"Model file not found: {Config.MODEL_PATH}")
                self.logger.info("Please train the model first using model_trainer.py")
                return
                
            self.model = load_model(Config.MODEL_PATH)
            self.logger.info("Mask detection model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            self.model = None
    
    def predict_mask(self, face_image):
        """
        Predict if face is wearing a mask
        
        Args:
            face_image: Preprocessed face image
            
        Returns:
            Tuple of (prediction, confidence)
        """
        try:
            if self.model is None:
                return "Unknown", 0.0
                
            if face_image is None:
                return "Unknown", 0.0
                
            # Make prediction
            prediction = self.model.predict(face_image, verbose=0)[0][0]
            
            # Convert to binary classification
            if prediction > Config.MASK_THRESHOLD:
                return "With Mask", prediction
            else:
                return "No Mask", 1.0 - prediction
                
        except Exception as e:
            self.logger.error(f"Error predicting mask: {str(e)}")
            return "Unknown", 0.0
    
    def get_prediction_color(self, prediction):
        """
        Get color based on prediction
        
        Args:
            prediction: Prediction string
            
        Returns:
            BGR color tuple
        """
        color_map = {
            "With Mask": Config.COLOR_MASK,
            "No Mask": Config.COLOR_NO_MASK,
            "Unknown": Config.COLOR_UNKNOWN
        }
        
        return color_map.get(prediction, Config.COLOR_UNKNOWN)
    
    def is_model_available(self):
        """Check if model is available for prediction"""
        return self.model is not None
    
    def get_model_summary(self):
        """Get model summary information"""
        if self.model is None:
            return "Model not loaded"
            
        try:
            # Get model information
            total_params = self.model.count_params()
            input_shape = self.model.input_shape
            output_shape = self.model.output_shape
            
            summary = f"""
            Model Summary:
            - Total Parameters: {total_params:,}
            - Input Shape: {input_shape}
            - Output Shape: {output_shape}
            - Model Type: Binary Classification (Mask/No Mask)
            """
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting model summary: {str(e)}")
            return "Error getting model summary"
    
    def validate_prediction(self, prediction, confidence):
        """
        Validate prediction based on confidence threshold
        
        Args:
            prediction: Prediction string
            confidence: Confidence score
            
        Returns:
            Tuple of (validated_prediction, is_valid)
        """
        try:
            is_valid = confidence >= Config.CONFIDENCE_THRESHOLD
            
            if not is_valid:
                return "Unknown", False
                
            return prediction, True
            
        except Exception as e:
            self.logger.error(f"Error validating prediction: {str(e)}")
            return "Unknown", False
    
    def batch_predict(self, face_images):
        """
        Predict masks for multiple faces
        
        Args:
            face_images: List of preprocessed face images
            
        Returns:
            List of (prediction, confidence) tuples
        """
        try:
            if self.model is None:
                return [("Unknown", 0.0)] * len(face_images)
                
            if not face_images:
                return []
                
            # Stack images for batch prediction
            batch_images = np.vstack(face_images)
            
            # Make batch prediction
            predictions = self.model.predict(batch_images, verbose=0)
            
            # Process predictions
            results = []
            for prediction in predictions:
                pred_value = prediction[0]
                if pred_value > Config.MASK_THRESHOLD:
                    results.append(("With Mask", pred_value))
                else:
                    results.append(("No Mask", 1.0 - pred_value))
                    
            return results
            
        except Exception as e:
            self.logger.error(f"Error in batch prediction: {str(e)}")
            return [("Unknown", 0.0)] * len(face_images)
