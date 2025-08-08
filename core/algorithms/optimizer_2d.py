"""
2D bin packing optimization algorithm.
"""

import random
import numpy as np
import time
from typing import List, Tuple, Any
from deap import base, creator, tools
from .base_optimizer import BaseOptimizer
from models.data_structures import Package, Container, PlacedPackage
from models.optimization_result import OptimizationResult, ContainerSolution


class Optimizer2D(BaseOptimizer):
    """2D bin packing optimizer using genetic algorithms."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_deap()
        
    def _setup_deap(self):
        """Setup DEAP genetic algorithm components."""
        # Clean up any existing DEAP classes
        if hasattr(creator, 'FitnessMax'):
            delattr(creator, 'FitnessMax')
        if hasattr(creator, 'Individual'):
            delattr(creator, 'Individual')
            
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", tools.cxUniform, indpb=self.crossover_probability)
        self.toolbox.register("mutate", self._mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
    def optimize(self) -> OptimizationResult:
        """Run 2D bin packing optimization."""
        self.logger.info("Starting 2D optimization")
        start_time = time.time()
        
        population = self.toolbox.population(n=self.population_size)
        
        # Evaluate initial population
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
            
        for generation in range(self.generations):
            # Evolution process similar to 1D but with 2D placement logic
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Apply crossover and mutation
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_probability:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
                    
            for mutant in offspring:
                if random.random() < self.mutation_probability:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
                    
            # Evaluate and replace
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
                
            population[:] = offspring
            
            # Progress reporting
            fits = [ind.fitness.values[0] for ind in population]
            best_fitness = max(fits)
            avg_fitness = sum(fits) / len(fits)
            elapsed_time = time.time() - start_time
            self._report_progress(generation, best_fitness, avg_fitness, elapsed_time)
            
        best_individual = tools.selBest(population, 1)[0]
        result = self._decode_solution(best_individual)
        result.optimization_time = time.time() - start_time
        result.generations_completed = self.generations
        result.best_fitness = best_individual.fitness.values[0]
        
        return result
        
    def _create_individual(self) -> List[Any]:
        """Create random individual for 2D packing."""
        individual = []
        
        for container in self.problem.containers:
            if container.is_optional:
                individual.append(random.randint(0, 1))
            else:
                individual.append(1)
                
            for package in self.problem.packages:
                quantity = random.randint(package.min_quantity, package.max_quantity)
                individual.append(quantity)
                
        return individual
        
    def _evaluate_fitness(self, individual: List[Any]) -> Tuple[float]:
        """Evaluate fitness for 2D packing."""
        try:
            result = self._decode_solution(individual)
            efficiency = result.total_efficiency
            containers_used = result.containers_used
            total_containers = len(self.problem.containers)
            
            container_penalty = 1.0 - (containers_used / total_containers) * 0.1
            fitness = efficiency * container_penalty
            
            return (fitness,)
        except Exception:
            return (0.0,)
            
    def _decode_solution(self, individual: List[Any]) -> OptimizationResult:
        """Decode individual into 2D optimization result."""
        container_solutions = []
        unused_containers = []
        unplaced_packages = {pkg.name: pkg.max_quantity for pkg in self.problem.packages}
        
        idx = 0
        for container in self.problem.containers:
            use_container = individual[idx]
            idx += 1
            
            if not use_container:
                unused_containers.append(container)
                idx += len(self.problem.packages)
                continue
                
            placed_packages = []
            package_quantities = []
            
            for package in self.problem.packages:
                quantity = individual[idx]
                package_quantities.append(quantity)
                idx += 1
                
            # 2D placement using bottom-left-fill algorithm
            container_width, container_height = container.dimensions
            
            for package, quantity in zip(self.problem.packages, package_quantities):
                rotations = self._generate_rotations(package, self.problem.packages.index(package))
                
                for _ in range(quantity):
                    placed = False
                    
                    for rotation in rotations:
                        if len(rotation) >= 3:
                            name, width, height = rotation[0], rotation[1], rotation[2]
                        else:
                            name, width, height = rotation[0], package.dimensions[0], package.dimensions[1]
                            
                        # Try to find position using bottom-left strategy
                        for y in range(0, container_height - height + 1):
                            for x in range(0, container_width - width + 1):
                                if self._can_place_2d(placed_packages, (x, y), (width, height)):
                                    placed_package = PlacedPackage(
                                        package_name=name,
                                        position=(x, y),
                                        dimensions=(width, height),
                                        rotation=name if '_r' in name else None
                                    )
                                    placed_packages.append(placed_package)
                                    
                                    base_name = package.name
                                    if unplaced_packages[base_name] > 0:
                                        unplaced_packages[base_name] -= 1
                                        
                                    placed = True
                                    break
                            if placed:
                                break
                        if placed:
                            break
                    if not placed:
                        break
                        
            if placed_packages:
                used_area = sum(pkg.dimensions[0] * pkg.dimensions[1] for pkg in placed_packages)
                total_area = container_width * container_height
                utilization = used_area / total_area
                
                solution = ContainerSolution(
                    container=container,
                    placed_packages=placed_packages,
                    utilization_rate=utilization
                )
                container_solutions.append(solution)
            else:
                unused_containers.append(container)
                
        total_efficiency = (sum(sol.utilization_rate for sol in container_solutions) / 
                          len(container_solutions)) if container_solutions else 0.0
                          
        return OptimizationResult(
            container_solutions=container_solutions,
            total_efficiency=total_efficiency,
            unused_containers=unused_containers,
            unplaced_packages=unplaced_packages,
            optimization_time=0.0,
            generations_completed=0,
            best_fitness=0.0
        )
        
    def _can_place_2d(self, placed_packages: List[PlacedPackage], 
                     position: Tuple[int, int], dimensions: Tuple[int, int]) -> bool:
        """Check if package can be placed at position in 2D."""
        x, y = position
        width, height = dimensions
        
        for placed in placed_packages:
            px, py = placed.position
            pw, ph = placed.dimensions
            
            # Check for overlap
            if not (x + width <= px or px + pw <= x or 
                   y + height <= py or py + ph <= y):
                return False
                
        return True
        
    def _mutate_individual(self, individual: List[Any]) -> Tuple[List[Any]]:
        """Mutate individual for 2D packing."""
        if random.random() < 0.1:
            idx = random.randint(0, len(individual) - 1)
            
            # Determine gene type and mutate accordingly
            gene_idx = 0
            for container in self.problem.containers:
                if gene_idx == idx and container.is_optional:
                    individual[idx] = 1 - individual[idx]
                    return (individual,)
                gene_idx += 1
                
                for package in self.problem.packages:
                    if gene_idx == idx:
                        individual[idx] = random.randint(package.min_quantity, package.max_quantity)
                        return (individual,)
                    gene_idx += 1
                    
        return (individual,)