"""
Views module for bin-packing-optimizer
Handles different output formats and visualizations
"""

from .console_view import ConsoleView
from .web_view import WebView
from .visualization_view import VisualizationView
from .report_view import ReportView

__all__ = ['ConsoleView', 'WebView', 'VisualizationView', 'ReportView']