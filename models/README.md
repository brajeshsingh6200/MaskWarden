# Models Directory

This directory contains the trained machine learning models for face mask detection.

## Files

- `mask_detector_model.h5` - Trained CNN model for mask detection (generated after training)

## Model Architecture

The face mask detection model is a Convolutional Neural Network (CNN) with the following architecture:

### Input Layer
- Input shape: (224, 224, 3) - RGB images resized to 224x224 pixels

### Convolutional Layers
1. **Conv2D Block 1**: 32 filters, 3x3 kernel, ReLU activation
   - BatchNormalization
   - MaxPooling2D (2x2)
   - Dropout (0.25)

2. **Conv2D Block 2**: 64 filters, 3x3 kernel, ReLU activation
   - BatchNormalization
   - MaxPooling2D (2x2)
   - Dropout (0.25)

3. **Conv2D Block 3**: 128 filters, 3x3 kernel, ReLU activation
   - BatchNormalization
   - MaxPooling2D (2x2)
   - Dropout (0.25)

4. **Conv2D Block 4**: 256 filters, 3x3 kernel, ReLU activation
   - BatchNormalization
   - MaxPooling2D (2x2)
   - Dropout (0.25)

### Fully Connected Layers
- Flatten layer
- Dense layer: 512 units, ReLU activation
  - BatchNormalization
  - Dropout (0.5)
- Dense layer: 256 units, ReLU activation
  - BatchNormalization
  - Dropout (0.5)
- Output layer: 1 unit, Sigmoid activation (binary classification)

### Compilation
- Optimizer: Adam (learning rate: 0.001)
- Loss function: Binary crossentropy
- Metrics: Accuracy

## Training Data Requirements

To train the model, you need to organize your training data as follows:

