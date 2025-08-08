"""
Application configuration settings.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class OptimizationSettings:
    """Default optimization algorithm settings."""
    default_population_size: int = 1000
    default_generations: int = 50
    default_crossover_probability: float = 0.618
    default_mutation_probability: float = 0.021
    tournament_size: int = 3
    grid_step_size: int = 1


@dataclass
class UISettings:
    """User interface settings."""
    window_width: int = 1200
    window_height: int = 800
    theme_color: str = "#1976D2"
    secondary_color: str = "#1565C0"
    background_color: str = "#ffffff"
    text_color: str = "#212529"


@dataclass
class ReportSettings:
    """Report generation settings."""
    default_dpi: int = 300
    chart_width: int = 10
    chart_height: int = 6
    export_formats: list = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['pdf', 'png', 'csv', 'json']


class AppConfig:
    """Main application configuration."""
    
    def __init__(self):
        self.optimization = OptimizationSettings()
        self.ui = UISettings()
        self.reports = ReportSettings()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'optimization': self.optimization.__dict__,
            'ui': self.ui.__dict__,
            'reports': self.reports.__dict__
        }


# Global configuration instance
config = AppConfig()