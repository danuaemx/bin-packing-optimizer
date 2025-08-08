"""
Controller for analytics and reporting operations.
"""

from typing import Dict, Any, List, Optional
from .base_controller import BaseController
from services.analytics_service import AnalyticsService
from models.optimization_result import OptimizationResult

class AnalyticsController(BaseController):
    """Handles analytics and reporting requests."""
    
    def __init__(self):
        super().__init__()
        self.analytics_service = AnalyticsService()
        
    def analyze_solution(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an optimization solution.
        
        Args:
            request_data: Contains optimization result and analysis parameters
            
        Returns:
            Analysis report
        """
        self._start_timing()
        
        try:
            # Validate request
            validation_error = self._validate_input(request_data, ['result'])
            if validation_error:
                return self._format_response(False, error=validation_error)
            
            # Parse optimization result
            result_data = request_data['result']
            analysis_options = request_data.get('options', {})
            
            # Perform analysis
            analysis = self.analytics_service.analyze_solution(
                result_data, 
                analysis_options
            )
            
            execution_time = self._end_timing()
            
            return self._format_response(
                True,
                data=analysis,
                message="Solution analysis completed",
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Solution analysis failed: {str(e)}")
            return self._format_response(
                False,
                error=f"Analysis failed: {str(e)}",
                execution_time=self._end_timing()
            )
    
    def generate_efficiency_report(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate efficiency analysis report."""
        try:
            solutions = request_data.get('solutions', [])
            
            if not solutions:
                return self._format_response(False, error="No solutions provided")
            
            report = self.analytics_service.generate_efficiency_report(solutions)
            
            return self._format_response(
                True,
                data=report,
                message="Efficiency report generated"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def compare_solutions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare multiple optimization solutions.
        
        Args:
            request_data: Contains list of solutions to compare
            
        Returns:
            Comparison analysis
        """
        try:
            solutions = request_data.get('solutions', [])
            comparison_metrics = request_data.get('metrics', ['efficiency', 'cost', 'utilization'])
            
            if len(solutions) < 2:
                return self._format_response(False, error="At least 2 solutions required for comparison")
            
            comparison = self.analytics_service.compare_solutions(solutions, comparison_metrics)
            
            return self._format_response(
                True,
                data=comparison,
                message="Solution comparison completed"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def get_optimization_statistics(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistical analysis of optimization results."""
        try:
            results_data = request_data.get('results', [])
            
            if not results_data:
                return self._format_response(False, error="No results provided")
            
            statistics = self.analytics_service.calculate_statistics(results_data)
            
            return self._format_response(
                True,
                data=statistics,
                message="Statistics calculated"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def generate_visualization_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for visualization components."""
        try:
            result_data = request_data.get('result')
            chart_type = request_data.get('chart_type', 'container_utilization')
            
            if not result_data:
                return self._format_response(False, error="No result data provided")
            
            viz_data = self.analytics_service.prepare_visualization_data(
                result_data, 
                chart_type
            )
            
            return self._format_response(
                True,
                data=viz_data,
                message="Visualization data prepared"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))