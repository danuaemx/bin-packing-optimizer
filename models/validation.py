"""
Data validation utilities for bin packing models.
"""

from typing import List, Tuple, Any
from .data_structures import Package, Container, PackingProblem


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_package(package: Package) -> List[str]:
    """
    Validate a package and return list of validation errors.
    
    Args:
        package: Package to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not package.name or not package.name.strip():
        errors.append("Package name cannot be empty")
    
    if len(package.dimensions) not in [1, 2, 3]:
        errors.append("Package dimensions must be 1D, 2D, or 3D")
    
    if any(d <= 0 for d in package.dimensions):
        errors.append("All package dimensions must be positive")
    
    if package.min_quantity < 0:
        errors.append("Minimum quantity cannot be negative")
    
    if package.max_quantity < package.min_quantity:
        errors.append("Maximum quantity cannot be less than minimum quantity")
    
    if package.weight is not None and package.weight < 0:
        errors.append("Package weight cannot be negative")
    
    if package.value is not None and package.value < 0:
        errors.append("Package value cannot be negative")
    
    return errors


def validate_container(container: Container) -> List[str]:
    """
    Validate a container and return list of validation errors.
    
    Args:
        container: Container to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not container.id or not container.id.strip():
        errors.append("Container ID cannot be empty")
    
    if len(container.dimensions) not in [1, 2, 3]:
        errors.append("Container dimensions must be 1D, 2D, or 3D")
    
    if any(d <= 0 for d in container.dimensions):
        errors.append("All container dimensions must be positive")
    
    if container.max_weight is not None and container.max_weight <= 0:
        errors.append("Maximum weight must be positive")
    
    if container.cost is not None and container.cost < 0:
        errors.append("Container cost cannot be negative")
    
    return errors


def validate_packing_problem(problem: PackingProblem) -> List[str]:
    """
    Validate a complete packing problem.
    
    Args:
        problem: Packing problem to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Validate packages
    if not problem.packages:
        errors.append("At least one package must be provided")
    else:
        for i, package in enumerate(problem.packages):
            package_errors = validate_package(package)
            errors.extend([f"Package {i+1}: {error}" for error in package_errors])
    
    # Validate containers
    if not problem.containers:
        errors.append("At least one container must be provided")
    else:
        for i, container in enumerate(problem.containers):
            container_errors = validate_container(container)
            errors.extend([f"Container {i+1}: {error}" for error in container_errors])
    
    # Check dimension consistency
    if problem.packages and problem.containers:
        package_dims = set(len(p.dimensions) for p in problem.packages)
        container_dims = set(len(c.dimensions) for c in problem.containers)
        
        if len(package_dims) > 1:
            errors.append("All packages must have the same number of dimensions")
        
        if len(container_dims) > 1:
            errors.append("All containers must have the same number of dimensions")
        
        if package_dims and container_dims and package_dims != container_dims:
            errors.append("Packages and containers must have the same number of dimensions")
    
    # Validate rotation permissions
    if problem.allowed_rotations is not None:
        if len(problem.allowed_rotations) != len(problem.packages):
            errors.append("Rotation permissions must be provided for all packages")
    
    return errors


def validate_optimization_parameters(population_size: int, generations: int, 
                                   crossover_prob: float, mutation_prob: float) -> List[str]:
    """
    Validate optimization algorithm parameters.
    
    Args:
        population_size: Size of genetic algorithm population
        generations: Number of generations to run
        crossover_prob: Crossover probability
        mutation_prob: Mutation probability
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if population_size <= 0:
        errors.append("Population size must be positive")
    
    if population_size < 10:
        errors.append("Population size should be at least 10 for meaningful results")
    
    if generations <= 0:
        errors.append("Number of generations must be positive")
    
    if not 0.0 <= crossover_prob <= 1.0:
        errors.append("Crossover probability must be between 0.0 and 1.0")
    
    if not 0.0 <= mutation_prob <= 1.0:
        errors.append("Mutation probability must be between 0.0 and 1.0")
    
    return errors