"""
Bin Packing Optimizer - Main Application Entry Point
Modern bin packing optimization tool with genetic algorithms
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from config.logging_config import setup_logging
from controllers.main_controller import MainController


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Bin Packing Optimizer")
        app.setApplicationVersion("2.0.0")
        
        # Create and show main controller
        controller = MainController()
        controller.show()
        
        logger.info("Application started successfully")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()