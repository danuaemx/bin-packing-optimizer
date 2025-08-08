"""
Optimization service for managing bin packing algorithms.
"""

import logging
from typing import Optional, Callable, Dict, Any
from models.data_structures import PackingProblem
from models.optimization_result import OptimizationResult, OptimizationProgress
from models.validation import validate_packing_problem, validate_optimization_parameters
from core.algorithms.optimizer_1d import Optimizer1D
from core.algorithms.optimizer_2d import Optimizer2D
from core.algorithms.optimizer_3d import Optimizer3D
from core.algorithms.base_optimizer import BaseOptimizer


class OptimizationService:
    """
    Service for managing bin packing optimization operations.
    
    This service provides a high-level interface for running optimization
    algorithms and manages the selection of appropriate algorithms based
    on problem dimensions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._algorithm_map = {
            1: Optimizer1D,
            2: Optimizer2D,
            3: Optimizer3D
        }
        
    def optimize_packing(self, 
                        problem: PackingProblem,
                        population_size: int = 1000,
                        generations: int = 50,
                        crossover_probability: float = 0.618,
                        mutation_probability: float = 0.021,
                        progress_callback: Optional[Callable[[OptimizationProgress], None]] = None) -> OptimizationResult:
        """
        Optimize a bin packing problem.
        
        Args:
            problem: The packing problem to solve
            population_size: Size of genetic algorithm population
            generations: Number of generations to evolve
            crossover_probability: Probability of crossover operation
            mutation_probability: Probability of mutation operation
            progress_callback: Optional callback for progress updates
            
        Returns:
            OptimizationResult containing the best solution found
            
        Raises:
            ValueError: If problem or parameters are invalid
        """
        # Validate inputs
        self._validate_inputs(problem, population_size, generations, 
                            crossover_probability, mutation_probability)
        
        # Select appropriate algorithm
        dimensions = problem.dimensions_count
        if dimensions not in self._algorithm_map:
            raise ValueError(f"Unsupported problem dimensions: {dimensions}")
            
        self.logger.info(f"Starting {dimensions}D optimization with {len(problem.packages)} packages "
                        f"and {len(problem.containers)} containers")
        
        # Create and configure optimizer
        optimizer_class = self._algorithm_map[dimensions]
        optimizer = optimizer_class(
            problem=problem,
            population_size=population_size,
            generations=generations,
            crossover_probability=crossover_probability,
            mutation_probability=mutation_probability
        )
        
        if progress_callback:
            optimizer.set_progress_callback(progress_callback)
            
        # Run optimization
        try:
            result = optimizer.optimize()
            self.logger.info(f"Optimization completed successfully. "
                           f"Efficiency: {result.total_efficiency:.2%}, "
                           f"Containers used: {result.containers_used}")
            return result
            
        except Exception as e:
            self.logger.error(f"Optimization failed: {e}", exc_info=True)
            raise
            
    def _validate_inputs(self, problem: PackingProblem, population_size: int, 
                        generations: int, crossover_prob: float, mutation_prob: float):
        """Validate optimization inputs."""
        # Validate problem
        problem_errors = validate_packing_problem(problem)
        if problem_errors:
            raise ValueError(f"Invalid packing problem: {'; '.join(problem_errors)}")
            
        # Validate parameters
        param_errors = validate_optimization_parameters(
            population_size, generations, crossover_prob, mutation_prob
        )
        if param_errors:
            raise ValueError(f"Invalid optimization parameters: {'; '.join(param_errors)}")
            
    def get_algorithm_info(self, dimensions: int) -> Dict[str, Any]:
        """
        Get information about the algorithm used for given dimensions.
        
        Args:
            dimensions: Number of dimensions (1, 2, or 3)
            
        Returns:
            Dictionary with algorithm information
        """
        if dimensions not in self._algorithm_map:
            return {"error": f"Unsupported dimensions: {dimensions}"}
            
        optimizer_class = self._algorithm_map[dimensions]
        
        return {
            "name": optimizer_class.__name__,
            "dimensions": dimensions,
            "description": optimizer_class.__doc__ or "No description available",
            "supported_features": [
                "Genetic Algorithm",
                "Multiple Containers",
                "Optional Containers",
                "Package Rotations",
                "Quantity Constraints"
            ]
        }
        
    def estimate_optimization_time(self, problem: PackingProblem, 
                                 population_size: int, generations: int) -> float:
        """
        Estimate optimization time based on problem complexity.
        
        Args:
            problem: The packing problem
            population_size: GA population size
            generations: Number of generations
            
        Returns:
            Estimated time in seconds
        """
        # Basic complexity estimation
        package_count = len(problem.packages)
        container_count = len(problem.containers)
        dimensions = problem.dimensions_count
        
        # Rough estimation based on empirical data
        base_time = 0.1  # Base time per generation
        complexity_factor = (package_count * container_count * dimensions) / 100
        
        estimated_time = base_time * complexity_factor * generations * (population_size / 1000)
        
        return max(estimated_time, 1.0)  # Minimum 1 second