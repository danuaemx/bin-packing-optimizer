"""
Optimization result data structures.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from .data_structures import Container, PlacedPackage


@dataclass
class ContainerSolution:
    """
    Solution for a single container.
    
    Attributes:
        container: The container used
        placed_packages: List of packages placed in this container
        utilization_rate: Space utilization percentage
        total_value: Total value of packages in container
        total_weight: Total weight of packages in container
    """
    container: Container
    placed_packages: List[PlacedPackage]
    utilization_rate: float
    total_value: Optional[float] = None
    total_weight: Optional[float] = None
    
    @property
    def used_volume(self) -> float:
        """Calculate used volume in container."""
        volume = 0.0
        for package in self.placed_packages:
            pkg_volume = 1.0
            for dim in package.dimensions:
                pkg_volume *= dim
            volume += pkg_volume
        return volume
    
    @property
    def package_count(self) -> int:
        """Get number of packages in container."""
        return len(self.placed_packages)


@dataclass
class OptimizationResult:
    """
    Complete optimization result.
    
    Attributes:
        container_solutions: List of container solutions
        total_efficiency: Overall packing efficiency
        unused_containers: List of unused containers
        unplaced_packages: Packages that couldn't be placed
        optimization_time: Time taken for optimization (seconds)
        generations_completed: Number of genetic algorithm generations
        best_fitness: Best fitness value achieved
        algorithm_stats: Additional algorithm statistics
        timestamp: When optimization was completed
    """
    container_solutions: List[ContainerSolution]
    total_efficiency: float
    unused_containers: List[Container]
    unplaced_packages: Dict[str, int]  # package_name -> quantity
    optimization_time: float
    generations_completed: int
    best_fitness: float
    algorithm_stats: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def containers_used(self) -> int:
        """Get number of containers used."""
        return len(self.container_solutions)
    
    @property
    def total_packages_placed(self) -> int:
        """Get total number of packages placed."""
        return sum(sol.package_count for sol in self.container_solutions)
    
    @property
    def total_volume_used(self) -> float:
        """Get total volume used across all containers."""
        return sum(sol.used_volume for sol in self.container_solutions)
    
    @property
    def total_volume_available(self) -> float:
        """Get total volume available across used containers."""
        return sum(sol.container.volume for sol in self.container_solutions)
    
    @property
    def average_utilization(self) -> float:
        """Get average utilization across all used containers."""
        if not self.container_solutions:
            return 0.0
        return sum(sol.utilization_rate for sol in self.container_solutions) / len(self.container_solutions)


@dataclass
class OptimizationProgress:
    """
    Progress information during optimization.
    
    Attributes:
        current_generation: Current generation number
        total_generations: Total generations to complete
        best_fitness: Best fitness in current generation
        average_fitness: Average fitness in current generation
        elapsed_time: Time elapsed since optimization started
        estimated_time_remaining: Estimated time to completion
    """
    current_generation: int
    total_generations: int
    best_fitness: float
    average_fitness: float
    elapsed_time: float
    estimated_time_remaining: Optional[float] = None
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        return (self.current_generation / self.total_generations) * 100.0 if self.total_generations > 0 else 0.0