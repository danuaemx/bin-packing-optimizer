"""
1D bin packing optimization algorithm.
"""

import random
import numpy as np
from typing import List, Tuple, Any
from deap import base, creator, tools, algorithms
from .base_optimizer import BaseOptimizer
from models.data_structures import Package, Container, PlacedPackage
from models.optimization_result import OptimizationResult, ContainerSolution


class Optimizer1D(BaseOptimizer):
    """1D bin packing optimizer using genetic algorithms."""
    
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
            
        # Create fitness and individual classes
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        # Setup toolbox
        self.toolbox = base.Toolbox()
        
        # Register genetic operators
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", tools.cxUniform, indpb=self.crossover_probability)
        self.toolbox.register("mutate", self._mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Statistics
        self.stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)
        
    def optimize(self) -> OptimizationResult:
        """Run 1D bin packing optimization."""
        self.logger.info("Starting 1D optimization")
        start_time = time.time()
        
        # Create initial population
        population = self.toolbox.population(n=self.population_size)
        
        # Evaluate initial population
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
            
        # Evolution loop
        for generation in range(self.generations):
            gen_start = time.time()
            
            # Selection and breeding
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_probability:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
                    
            # Mutation
            for mutant in offspring:
                if random.random() < self.mutation_probability:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
                    
            # Evaluate invalid individuals
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
                
            # Replace population
            population[:] = offspring
            
            # Statistics
            fits = [ind.fitness.values[0] for ind in population]
            best_fitness = max(fits)
            avg_fitness = sum(fits) / len(fits)
            
            self.statistics['fitness_history'].append({
                'generation': generation,
                'best': best_fitness,
                'average': avg_fitness,
                'std': np.std(fits)
            })
            
            gen_time = time.time() - gen_start
            self.statistics['generation_times'].append(gen_time)
            
            # Report progress
            elapsed_time = time.time() - start_time
            self._report_progress(generation, best_fitness, avg_fitness, elapsed_time)
            
        # Get best solution
        best_individual = tools.selBest(population, 1)[0]
        result = self._decode_solution(best_individual)
        
        result.optimization_time = time.time() - start_time
        result.generations_completed = self.generations
        result.best_fitness = best_individual.fitness.values[0]
        result.algorithm_stats = self.statistics
        
        self.logger.info(f"1D optimization completed in {result.optimization_time:.2f} seconds")
        return result
        
    def _create_individual(self) -> List[Any]:
        """Create a random individual for 1D packing."""
        individual = []
        
        for container in self.problem.containers:
            # Container usage (0 or 1 for optional containers)
            if container.is_optional:
                individual.append(random.randint(0, 1))
            else:
                individual.append(1)  # Always use non-optional containers
                
            # Package quantities for this container
            for package in self.problem.packages:
                quantity = random.randint(package.min_quantity, package.max_quantity)
                individual.append(quantity)
                
        return individual
        
    def _evaluate_fitness(self, individual: List[Any]) -> Tuple[float]:
        """Evaluate fitness of a 1D packing solution."""
        try:
            result = self._decode_solution(individual)
            
            # Fitness components
            efficiency = result.total_efficiency
            containers_used = result.containers_used
            total_containers = len(self.problem.containers)
            
            # Fitness = efficiency * container_usage_penalty
            container_penalty = 1.0 - (containers_used / total_containers) * 0.1
            fitness = efficiency * container_penalty
            
            return (fitness,)
            
        except Exception as e:
            self.logger.warning(f"Fitness evaluation failed: {e}")
            return (0.0,)
            
    def _decode_solution(self, individual: List[Any]) -> OptimizationResult:
        """Decode individual into optimization result."""
        container_solutions = []
        unused_containers = []
        unplaced_packages = {pkg.name: pkg.max_quantity for pkg in self.problem.packages}
        
        idx = 0
        for container in self.problem.containers:
            # Check if container is used
            use_container = individual[idx]
            idx += 1
            
            if not use_container:
                unused_containers.append(container)
                # Skip package quantities for this container
                idx += len(self.problem.packages)
                continue
                
            # Get package quantities for this container
            container_packages = []
            package_quantities = []
            
            for package in self.problem.packages:
                quantity = individual[idx]
                package_quantities.append(quantity)
                idx += 1
                
            # Try to place packages in container
            placed_packages = []
            current_position = 0
            
            for package, quantity in zip(self.problem.packages, package_quantities):
                rotations = self._generate_rotations(package, self.problem.packages.index(package))
                
                for _ in range(quantity):
                    placed = False
                    for rotation in rotations:
                        name, length = rotation[0], rotation[1]
                        
                        if current_position + length <= container.dimensions[0]:
                            placed_package = PlacedPackage(
                                package_name=name,
                                position=(current_position,),
                                dimensions=(length,),
                                rotation=rotation[0] if len(rotation) > 1 else None
                            )
                            placed_packages.append(placed_package)
                            current_position += length
                            
                            # Update unplaced count
                            base_name = package.name
                            if unplaced_packages[base_name] > 0:
                                unplaced_packages[base_name] -= 1
                            
                            placed = True
                            break
                            
                    if not placed:
                        break
                        
            if placed_packages:
                # Calculate utilization
                used_volume = sum(pkg.dimensions[0] for pkg in placed_packages)
                utilization = used_volume / container.dimensions[0]
                
                solution = ContainerSolution(
                    container=container,
                    placed_packages=placed_packages,
                    utilization_rate=utilization
                )
                container_solutions.append(solution)
            else:
                unused_containers.append(container)
                
        # Calculate overall efficiency
        if container_solutions:
            total_efficiency = sum(sol.utilization_rate for sol in container_solutions) / len(container_solutions)
        else:
            total_efficiency = 0.0
            
        return OptimizationResult(
            container_solutions=container_solutions,
            total_efficiency=total_efficiency,
            unused_containers=unused_containers,
            unplaced_packages=unplaced_packages,
            optimization_time=0.0,
            generations_completed=0,
            best_fitness=0.0
        )
        
    def _mutate_individual(self, individual: List[Any]) -> Tuple[List[Any]]:
        """Mutate an individual solution."""
        if random.random() < 0.1:  # 10% chance to mutate each gene
            idx = random.randint(0, len(individual) - 1)
            
            # Determine what type of gene this is
            container_idx = 0
            gene_idx = 0
            
            for i, container in enumerate(self.problem.containers):
                if gene_idx == idx:
                    # This is a container usage gene
                    if container.is_optional:
                        individual[idx] = 1 - individual[idx]  # Flip usage
                    break
                    
                gene_idx += 1
                
                # Check if it's a package quantity gene
                for j, package in enumerate(self.problem.packages):
                    if gene_idx == idx:
                        # This is a package quantity gene
                        individual[idx] = random.randint(package.min_quantity, package.max_quantity)
                        return (individual,)
                    gene_idx += 1
                    
        return (individual,)