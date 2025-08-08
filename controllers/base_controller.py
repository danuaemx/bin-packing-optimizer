"""
Base controller class providing common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class BaseController(ABC):
    """Base controller with common functionality."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._start_time = None
        
    def _start_timing(self):
        """Start timing for performance monitoring."""
        self._start_time = datetime.now()
        
    def _end_timing(self) -> float:
        """End timing and return elapsed seconds."""
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            self._start_time = None
            return elapsed
        return 0.0
        
    def _format_response(self, success: bool, data: Any = None, 
                        message: str = "", error: str = "", 
                        execution_time: Optional[float] = None) -> Dict[str, Any]:
        """Format standardized response."""
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        if data is not None:
            response["data"] = data
            
        if error:
            response["error"] = error
            
        if execution_time is not None:
            response["execution_time"] = execution_time
            
        return response
        
    def _validate_input(self, data: Dict[str, Any], required_fields: list) -> Optional[str]:
        """Validate input data has required fields."""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        return None