"""
CNN Model Training Module for Face Mask Detection
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from config import Config
import logging

class MaskDetectionModelTrainer:
    """Class for training the face mask detection CNN model"""
    
    def __init__(self):
        self.model = None
        self.history = None
        self.logger = logging.getLogger(__name__)
        
    def create_model(self):
        """Create the CNN model architecture"""
        try:
            model = Sequential()
            
            # First Convolutional Block
            model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)))
            model.add(BatchNormalization())
            model.add(MaxPooling2D(pool_size=(2, 2)))
            model.add(Dropout(0.25))
            
            # Second Convolutional Block
            model.add(Conv2D(64, (3, 3), activation='relu'))
            model.add(BatchNormalization())
            model.add(MaxPooling2D(pool_size=(2, 2)))
            model.add(Dropout(0.25))
            
            # Third Convolutional Block
            model.add(Conv2D(128, (3, 3), activation='relu'))
            model.add(BatchNormalization())
            model.add(MaxPooling2D(pool_size=(2, 2)))
            model.add(Dropout(0.25))
            
            # Fourth Convolutional Block
            model.add(Conv2D(256, (3, 3), activation='relu'))
            model.add(BatchNormalization())
            model.add(MaxPooling2D(pool_size=(2, 2)))
            model.add(Dropout(0.25))
            
            # Fully Connected Layers
            model.add(Flatten())
            model.add(Dense(512, activation='relu'))
            model.add(BatchNormalization())
            model.add(Dropout(0.5))
            
            model.add(Dense(256, activation='relu'))
            model.add(BatchNormalization())
            model.add(Dropout(0.5))
            
            # Output Layer
            model.add(Dense(1, activation='sigmoid'))
            
            # Compile the model
            model.compile(
                optimizer=Adam(learning_rate=Config.LEARNING_RATE),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            self.model = model
            self.logger.info("Model created successfully")
            return model
            
        except Exception as e:
            self.logger.error(f"Error creating model: {str(e)}")
            raise
    
    def prepare_data(self):
        """Prepare training and validation data generators"""
        try:
            # Data augmentation for training
            train_datagen = ImageDataGenerator(
                rescale=1.0/255.0,
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                horizontal_flip=True,
                fill_mode='nearest',
                validation_split=0.2
            )
            
            # Only rescaling for validation
            val_datagen = ImageDataGenerator(
                rescale=1.0/255.0,
                validation_split=0.2
            )
            
            # Training data generator
            train_generator = train_datagen.flow_from_directory(
                Config.TRAIN_DATA_PATH,
                target_size=Config.MODEL_INPUT_SIZE,
                batch_size=Config.BATCH_SIZE,
                class_mode='binary',
                subset='training'
            )
            
            # Validation data generator
            val_generator = val_datagen.flow_from_directory(
                Config.TRAIN_DATA_PATH,
                target_size=Config.MODEL_INPUT_SIZE,
                batch_size=Config.BATCH_SIZE,
                class_mode='binary',
                subset='validation'
            )
            
            self.logger.info("Data generators prepared successfully")
            return train_generator, val_generator
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {str(e)}")
            raise
    
    def train_model(self, train_generator, val_generator):
        """Train the CNN model"""
        try:
            # Callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                ModelCheckpoint(
                    Config.MODEL_PATH,
                    monitor='val_accuracy',
                    save_best_only=True,
                    mode='max'
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.2,
                    patience=5,
                    min_lr=1e-7
                )
            ]
            
            # Calculate steps per epoch
            steps_per_epoch = train_generator.samples // Config.BATCH_SIZE
            validation_steps = val_generator.samples // Config.BATCH_SIZE
            
            # Train the model
            self.history = self.model.fit(
                train_generator,
                steps_per_epoch=steps_per_epoch,
                epochs=Config.EPOCHS,
                validation_data=val_generator,
                validation_steps=validation_steps,
                callbacks=callbacks,
                verbose=1
            )
            
            self.logger.info("Model training completed successfully")
            return self.history
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            self.logger.warning("No training history available")
            return
            
        try:
            plt.figure(figsize=(12, 4))
            
            # Plot training & validation accuracy
            plt.subplot(1, 2, 1)
            plt.plot(self.history.history['accuracy'], label='Training Accuracy')
            plt.plot(self.history.history['val_accuracy'], label='Validation Accuracy')
            plt.title('Model Accuracy')
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.legend()
            
            # Plot training & validation loss
            plt.subplot(1, 2, 2)
            plt.plot(self.history.history['loss'], label='Training Loss')
            plt.plot(self.history.history['val_loss'], label='Validation Loss')
            plt.title('Model Loss')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.legend()
            
            plt.tight_layout()
            plt.savefig('logs/training_history.png')
            plt.show()
            
            self.logger.info("Training history plotted and saved")
            
        except Exception as e:
            self.logger.error(f"Error plotting training history: {str(e)}")
    
    def evaluate_model(self, test_generator):
        """Evaluate the trained model"""
        try:
            if self.model is None:
                raise ValueError("Model not trained yet")
                
            # Evaluate the model
            test_loss, test_accuracy = self.model.evaluate(test_generator, verbose=0)
            
            self.logger.info(f"Test Accuracy: {test_accuracy:.4f}")
            self.logger.info(f"Test Loss: {test_loss:.4f}")
            
            return test_accuracy, test_loss
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def save_model(self, model_path=None):
        """Save the trained model"""
        try:
            if self.model is None:
                raise ValueError("Model not trained yet")
                
            save_path = model_path or Config.MODEL_PATH
            self.model.save(save_path)
            self.logger.info(f"Model saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

def main():
    """Main function for training the model"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Check if training data exists
        if not os.path.exists(Config.TRAIN_DATA_PATH):
            logger.error(f"Training data path does not exist: {Config.TRAIN_DATA_PATH}")
            logger.info("Please add training images to the following directories:")
            logger.info(f"- {Config.WITH_MASK_PATH}")
            logger.info(f"- {Config.WITHOUT_MASK_PATH}")
            return
            
        # Initialize trainer
        trainer = MaskDetectionModelTrainer()
        
        # Create model
        model = trainer.create_model()
        logger.info("Model architecture:")
        model.summary()
        
        # Prepare data
        train_gen, val_gen = trainer.prepare_data()
        
        # Train model
        history = trainer.train_model(train_gen, val_gen)
        
        # Plot training history
        trainer.plot_training_history()
        
        # Save model
        trainer.save_model()
        
        logger.info("Training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")

if __name__ == "__main__":
    main()
