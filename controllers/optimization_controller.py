"""
Controller for bin packing optimization operations.
"""

from typing import Dict, Any, List, Optional
from .base_controller import BaseController
from services.optimization_service import OptimizationService
from models.data_structures import PackingProblem, Package, Container
from models.validation import ValidationService

class OptimizationController(BaseController):
    """Handles optimization-related requests."""
    
    def __init__(self):
        super().__init__()
        self.optimization_service = OptimizationService()
        self.validation_service = ValidationService()
        
    def optimize_packing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute bin packing optimization.
        
        Args:
            request_data: Contains packages, containers, and optimization parameters
            
        Returns:
            Optimization result with packing solution
        """
        self._start_timing()
        
        try:
            # Validate request
            validation_error = self._validate_input(
                request_data, 
                ['packages', 'containers']
            )
            if validation_error:
                return self._format_response(False, error=validation_error)
            
            # Parse and validate problem data
            problem = self._parse_packing_problem(request_data)
            if not problem:
                return self._format_response(False, error="Invalid problem data")
                
            validation_result = self.validation_service.validate_packing_problem(problem)
            if not validation_result.is_valid:
                return self._format_response(
                    False, 
                    error=f"Validation failed: {validation_result.error_message}"
                )
            
            # Execute optimization
            self.logger.info(f"Starting optimization for {len(problem.packages)} packages")
            result = self.optimization_service.optimize(problem)
            
            execution_time = self._end_timing()
            
            if result.is_feasible:
                self.logger.info(f"Optimization completed successfully in {execution_time:.2f}s")
                return self._format_response(
                    True,
                    data=result.to_dict(),
                    message="Optimization completed successfully",
                    execution_time=execution_time
                )
            else:
                return self._format_response(
                    False,
                    data=result.to_dict(),
                    error="No feasible solution found",
                    execution_time=execution_time
                )
                
        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            return self._format_response(
                False,
                error=f"Optimization failed: {str(e)}",
                execution_time=self._end_timing()
            )
    
    def get_optimization_methods(self) -> Dict[str, Any]:
        """Get available optimization methods and their descriptions."""
        try:
            methods = self.optimization_service.get_available_methods()
            return self._format_response(
                True,
                data=methods,
                message="Available optimization methods retrieved"
            )
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def validate_problem(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a packing problem without solving it.
        
        Args:
            request_data: Problem definition to validate
            
        Returns:
            Validation result
        """
        try:
            problem = self._parse_packing_problem(request_data)
            if not problem:
                return self._format_response(False, error="Invalid problem data")
                
            validation_result = self.validation_service.validate_packing_problem(problem)
            
            return self._format_response(
                validation_result.is_valid,
                data={
                    "is_valid": validation_result.is_valid,
                    "warnings": validation_result.warnings,
                    "suggestions": validation_result.suggestions
                },
                message="Validation completed",
                error=validation_result.error_message if not validation_result.is_valid else ""
            )
            
        except Exception as e:
            return self._format_response(False, error=f"Validation failed: {str(e)}")
    
    def _parse_packing_problem(self, data: Dict[str, Any]) -> Optional[PackingProblem]:
        """Parse request data into PackingProblem object."""
        try:
            # Parse packages
            packages = []
            for pkg_data in data['packages']:
                package = Package(
                    name=pkg_data['name'],
                    dimensions=tuple(pkg_data['dimensions']),
                    min_quantity=pkg_data.get('min_quantity', 1),
                    max_quantity=pkg_data.get('max_quantity', 1),
                    package_type=pkg_data.get('package_type', 'regular'),
                    weight=pkg_data.get('weight'),
                    value=pkg_data.get('value')
                )
                packages.append(package)
            
            # Parse containers
            containers = []
            for cont_data in data['containers']:
                container = Container(
                    id=cont_data['id'],
                    dimensions=tuple(cont_data['dimensions']),
                    is_optional=cont_data.get('is_optional', False),
                    container_type=cont_data.get('container_type', 'standard'),
                    max_weight=cont_data.get('max_weight'),
                    cost=cont_data.get('cost')
                )
                containers.append(container)
            
            return PackingProblem(
                packages=packages,
                containers=containers,
                allowed_rotations=data.get('allowed_rotations'),
                objective=data.get('objective', 'minimize_containers')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse packing problem: {str(e)}")
            return None