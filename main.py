#!/usr/bin/env python3
"""
Main entry point for the Face Mask Detection System
"""

import sys
import os
import logging
from gui_app import FaceMaskDetectionGUI
from config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/system.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['models', 'logs', 'data', 'data/train', 'data/train/with_mask', 'data/train/without_mask']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main function to start the application"""
    try:
        # Create necessary directories
        create_directories()
        
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Face Mask Detection System")
        
        # Start the GUI application
        app = FaceMaskDetectionGUI()
        app.run()
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        logging.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
