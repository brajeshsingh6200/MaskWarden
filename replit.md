# Nextwave Company Website

## Overview

This is a dynamic and fully responsive corporate website for Nextwave, designed to showcase the company's services, values, products, and culture. The website includes interactive features, admin control, and client engagement tools, making it a comprehensive business-ready web portal.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Flask Web Framework**: Modern Python web application with MVC pattern
- **Database-Driven**: SQLite database for content management and user data
- **Responsive Design**: Bootstrap-based responsive UI with custom CSS
- **Admin Panel**: Comprehensive admin interface for content management
- **Interactive Features**: Search, theme toggle, contact forms, and job applications

### Technology Stack
- **Backend**: Flask (Python) with SQLite database
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **UI Components**: Font Awesome icons, Google Fonts
- **Features**: Dark/light theme, search functionality, form validation
- **Admin System**: Session-based authentication and dashboard

## Key Components

### 1. Flask Application (`app.py`)
- **Purpose**: Main web application with routing and business logic
- **Features**: User authentication, database management, API endpoints
- **Architecture**: MVC pattern with SQLite database integration
- **Admin System**: Complete admin panel for content management

### 2. Templates (`templates/`)
- **Base Template**: Common layout with navigation and footer
- **Public Pages**: Home, About, Services, Blog, Careers, Contact
- **Admin Panel**: Login and dashboard for content management
- **Responsive Design**: Bootstrap-based responsive layouts

### 3. Static Assets (`static/`)
- **CSS**: Custom styling with dark/light theme support
- **JavaScript**: Interactive features and form validation
- **Images**: Placeholder images and company assets
- **Bootstrap & Font Awesome**: Modern UI components and icons

### 4. Database Schema**
- **Users**: Admin authentication system
- **Blog Posts**: Dynamic blog content management
- **Services**: Company services and offerings
- **Jobs**: Career opportunities and applications
- **Contact Messages**: Client inquiries and communication
- **Events**: Optional workshop and event management

### 5. Interactive Features**
- **Search**: Global search across blog posts, services, and jobs
- **Theme Toggle**: Dark/light mode switching
- **Contact Forms**: Client inquiry and job application forms
- **Admin Dashboard**: Statistics and content management interface

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