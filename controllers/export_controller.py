"""
Controller for advanced export and reporting operations.
"""

from typing import Dict, Any, List, Optional
from .base_controller import BaseController
from services.export_service import ExportService

class ExportController(BaseController):
    """Handles export and report generation requests."""
    
    def __init__(self):
        super().__init__()
        self.export_service = ExportService()
        
    def generate_report(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report.
        
        Args:
            request_data: Contains result data and report configuration
            
        Returns:
            Generated report in requested format
        """
        self._start_timing()
        
        try:
            # Validate request
            validation_error = self._validate_input(request_data, ['result'])
            if validation_error:
                return self._format_response(False, error=validation_error)
            
            result_data = request_data['result']
            report_config = request_data.get('config', {})
            report_format = report_config.get('format', 'pdf')
            
            # Generate report
            report = self.export_service.generate_optimization_report(
                result_data, 
                report_config
            )
            
            execution_time = self._end_timing()
            
            return self._format_response(
                True,
                data={
                    "report_content": report,
                    "format": report_format,
                    "filename": f"optimization_report.{report_format}"
                },
                message="Report generated successfully",
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            return self._format_response(
                False,
                error=f"Report generation failed: {str(e)}",
                execution_time=self._end_timing()
            )
    
    def export_visualization(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export packing visualization."""
        try:
            result_data = request_data.get('result')
            viz_config = request_data.get('config', {})
            
            if not result_data:
                return self._format_response(False, error="No result data provided")
            
            visualization = self.export_service.generate_packing_visualization(
                result_data, 
                viz_config
            )
            
            return self._format_response(
                True,
                data=visualization,
                message="Visualization exported successfully"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def export_summary(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export optimization summary."""
        try:
            results = request_data.get('results', [])
            summary_type = request_data.get('type', 'standard')
            
            if not results:
                return self._format_response(False, error="No results provided")
            
            summary = self.export_service.generate_summary_report(results, summary_type)
            
            return self._format_response(
                True,
                data=summary,
                message="Summary exported successfully"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def get_export_formats(self) -> Dict[str, Any]:
        """Get available export formats and their capabilities."""
        try:
            formats = self.export_service.get_supported_formats()
            
            return self._format_response(
                True,
                data=formats,
                message="Export formats retrieved"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def export_configuration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export optimization configuration for reuse."""
        try:
            problem_data = request_data.get('problem')
            config_name = request_data.get('name', 'optimization_config')
            
            if not problem_data:
                return self._format_response(False, error="No problem data provided")
            
            config = self.export_service.export_configuration(problem_data, config_name)
            
            return self._format_response(
                True,
                data=config,
                message="Configuration exported successfully"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))