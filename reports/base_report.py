"""
Base report class for all report generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path


class BaseReport(ABC):
    """Abstract base class for all report generators."""
    
    def __init__(self, title: str = "Report", output_dir: str = "output"):
        self.title = title
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data = {}
        
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the report content."""
        pass
    
    @abstractmethod
    def export_pdf(self, filename: Optional[str] = None) -> str:
        """Export report as PDF."""
        pass
    
    @abstractmethod
    def export_html(self, filename: Optional[str] = None) -> str:
        """Export report as HTML."""
        pass
    
    def export_json(self, filename: Optional[str] = None) -> str:
        """Export report data as JSON."""
        if filename is None:
            filename = f"{self.title.lower().replace(' ', '_')}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        export_data = {
            'title': self.title,
            'generated_at': self.timestamp.isoformat(),
            'data': self.data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"JSON report exported to {filepath}")
        return str(filepath)
    
    def export_csv(self, filename: Optional[str] = None) -> str:
        """Export report data as CSV."""
        import pandas as pd
        
        if filename is None:
            filename = f"{self.title.lower().replace(' ', '_')}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        
        # Convert data to DataFrame
        df = self._prepare_csv_data()
        df.to_csv(filepath, index=False)
        
        self.logger.info(f"CSV report exported to {filepath}")
        return str(filepath)
    
    def _prepare_csv_data(self) -> 'pd.DataFrame':
        """Prepare data for CSV export. Override in subclasses."""
        import pandas as pd
        return pd.DataFrame([self.data])
    
    def _format_timestamp(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')