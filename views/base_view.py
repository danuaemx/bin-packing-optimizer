"""
Base view class for all view implementations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from models.bin import Bin
from models.item import Item


class BaseView(ABC):
    """Abstract base class for all views"""
    
    def __init__(self):
        self.data = {}
    
    @abstractmethod
    def render(self, data: Dict[str, Any]) -> None:
        """Render the view with given data"""
        pass
    
    @abstractmethod
    def display_results(self, bins: List[Bin], items: List[Item], 
                       algorithm: str, execution_time: float) -> None:
        """Display optimization results"""
        pass
    
    def format_efficiency(self, efficiency: float) -> str:
        """Format efficiency percentage"""
        return f"{efficiency:.2f}%"
    
    def format_time(self, time_seconds: float) -> str:
        """Format execution time"""
        if time_seconds < 1:
            return f"{time_seconds * 1000:.2f}ms"
        return f"{time_seconds:.3f}s"