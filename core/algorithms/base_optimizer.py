"""
Base class for bin packing optimization algorithms.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
import time
import logging
from models.data_structures import Package, Container, PackingProblem
from models.optimization_result import OptimizationResult, OptimizationProgress


class BaseOptimizer(ABC):
    """
    Abstract base class for bin packing optimization algorithms.
    
    This class defines the interface that all optimization algorithms must implement.
    """
    
    def __init__(self, problem: PackingProblem, 
                 population_size: int = 1000,
                 generations: int = 50,
                 crossover_probability: float = 0.618,
                 mutation_probability: float = 0.021):
        """
        Initialize the optimizer.
        
        Args:
            problem: The bin packing problem to solve
            population_size: Size of genetic algorithm population
            generations: Number of generations to evolve
            crossover_probability: Probability of crossover operation
            mutation_probability: Probability of mutation operation
        """
        self.problem = problem
        self.population_size = population_size
        self.generations = generations
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.progress_callback: Optional[Callable[[OptimizationProgress], None]] = None
        
        # Statistics tracking
        self.statistics = {
            'fitness_history': [],
            'generation_times': [],
            'best_individual_history': []
        }
        
    def set_progress_callback(self, callback: Callable[[OptimizationProgress], None]) -> None:
        """
        Set callback function for progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
        
    @abstractmethod
    def optimize(self) -> OptimizationResult:
        """
        Run the optimization algorithm.
        
        Returns:
            OptimizationResult containing the best solution found
        """
        pass
    
    @abstractmethod
    def _evaluate_fitness(self, individual: List[Any]) -> float:
        """
        Evaluate the fitness of an individual solution.
        
        Args:
            individual: Individual solution to evaluate
            
        Returns:
            Fitness value (higher is better)
        """
        pass
    
    @abstractmethod
    def _create_individual(self) -> List[Any]:
        """
        Create a random individual solution.
        
        Returns:
            Random individual solution
        """
        pass
    
    @abstractmethod
    def _decode_solution(self, individual: List[Any]) -> OptimizationResult:
        """
        Decode an individual solution into a readable result.
        
        Args:
            individual: Individual solution to decode
            
        Returns:
            Decoded optimization result
        """
        pass
    
    def _generate_rotations(self, package: Package, package_index: int) -> List[tuple]:
        """
        Generate possible rotations for a package.
        
        Args:
            package: Package to generate rotations for
            package_index: Index of package in problem definition
            
        Returns:
            List of possible rotations
        """
        rotations = [(package.name,) + package.dimensions]
        
        if self.problem.allowed_rotations and package_index < len(self.problem.allowed_rotations):
            permissions = self.problem.allowed_rotations[package_index]
            dims = package.dimensions
            
            if len(dims) == 2 and len(permissions) >= 1 and permissions[0]:
                # 2D rotation: swap width and height
                if dims[0] != dims[1]:
                    rotations.append((f"{package.name}_r90", dims[1], dims[0]))
            
            elif len(dims) == 3 and len(permissions) >= 3:
                # 3D rotations
                x, y, z = dims
                if permissions[0] and x != y:  # XY rotation
                    rotations.append((f"{package.name}_rxy", y, x, z))
                if permissions[1] and x != z:  # XZ rotation
                    rotations.append((f"{package.name}_rxz", z, y, x))
                if permissions[2] and y != z:  # YZ rotation
                    rotations.append((f"{package.name}_ryz", x, z, y))
        
        return rotations
    
    def _can_place_package(self, placed_packages: List[tuple], 
                          new_package: tuple, position: tuple, 
                          container_dimensions: tuple) -> bool:
        """
        Check if a package can be placed at a given position.
        
        Args:
            placed_packages: Already placed packages
            new_package: Package to place
            position: Position to place package
            container_dimensions: Container dimensions
            
        Returns:
            True if package can be placed, False otherwise
        """
        # Check container bounds
        for i, (pos, dim, cont_dim) in enumerate(zip(position, new_package, container_dimensions)):
            if pos + dim > cont_dim:
                return False
        
        # Check overlap with existing packages
        for placed in placed_packages:
            if self._packages_overlap(placed, new_package, position):
                return False
        
        return True
    
    def _packages_overlap(self, package1: tuple, package2_dims: tuple, package2_pos: tuple) -> bool:
        """
        Check if two packages overlap.
        
        Args:
            package1: First package (position + dimensions)
            package2_dims: Second package dimensions
            package2_pos: Second package position
            
        Returns:
            True if packages overlap, False otherwise
        """
        # Extract position and dimensions for package1
        if len(package1) == 3:  # 1D: (position, length, name)
            p1_pos, p1_dim = (package1[0],), (package1[1],)
        elif len(package1) == 4:  # 2D: (x, y, width, height, name)
            p1_pos, p1_dim = (package1[0], package1[1]), (package1[2], package1[3])
        else:  # 3D: (x, y, z, width, height, depth, name)
            p1_pos, p1_dim = (package1[0], package1[1], package1[2]), (package1[3], package1[4], package1[5])
        
        # Check overlap in each dimension
        for i in range(len(p1_pos)):
            if (p1_pos[i] + p1_dim[i] <= package2_pos[i] or 
                package2_pos[i] + package2_dims[i] <= p1_pos[i]):
                return False
        
        return True
    
    def _report_progress(self, generation: int, best_fitness: float, avg_fitness: float, elapsed_time: float):
        """
        Report optimization progress.
        
        Args:
            generation: Current generation number
            best_fitness: Best fitness in current generation
            avg_fitness: Average fitness in current generation
            elapsed_time: Time elapsed since start
        """
        if self.progress_callback:
            remaining_time = None
            if generation > 0:
                time_per_generation = elapsed_time / generation
                remaining_generations = self.generations - generation
                remaining_time = time_per_generation * remaining_generations
            
            progress = OptimizationProgress(
                current_generation=generation,
                total_generations=self.generations,
                best_fitness=best_fitness,
                average_fitness=avg_fitness,
                elapsed_time=elapsed_time,
                estimated_time_remaining=remaining_time
            )
            
            self.progress_callback(progress)