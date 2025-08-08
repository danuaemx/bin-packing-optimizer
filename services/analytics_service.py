"""
Analytics service for processing optimization results.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Tuple
from models.optimization_result import OptimizationResult
from models.data_structures import PackingProblem


class AnalyticsService:
    """
    Service for analyzing optimization results and generating insights.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_result(self, result: OptimizationResult, 
                      problem: PackingProblem) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of optimization results.
        
        Args:
            result: Optimization result to analyze
            problem: Original packing problem
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            "efficiency_metrics": self._calculate_efficiency_metrics(result),
            "space_utilization": self._analyze_space_utilization(result),
            "container_analysis": self._analyze_containers(result),
            "package_analysis": self._analyze_packages(result, problem),
            "optimization_performance": self._analyze_optimization_performance(result),
            "recommendations": self._generate_recommendations(result, problem)
        }
        
        return analysis
        
    def _calculate_efficiency_metrics(self, result: OptimizationResult) -> Dict[str, float]:
        """Calculate various efficiency metrics."""
        if not result.container_solutions:
            return {
                "overall_efficiency": 0.0,
                "average_utilization": 0.0,
                "utilization_variance": 0.0,
                "best_container_utilization": 0.0,
                "worst_container_utilization": 0.0
            }
            
        utilizations = [sol.utilization_rate for sol in result.container_solutions]
        
        return {
            "overall_efficiency": result.total_efficiency,
            "average_utilization": np.mean(utilizations),
            "utilization_variance": np.var(utilizations),
            "best_container_utilization": max(utilizations),
            "worst_container_utilization": min(utilizations),
            "utilization_std": np.std(utilizations)
        }
        
    def _analyze_space_utilization(self, result: OptimizationResult) -> Dict[str, Any]:
        """Analyze space utilization patterns."""
        total_volume_used = 0
        total_volume_available = 0
        container_volumes = []
        
        for solution in result.container_solutions:
            used_volume = solution.used_volume
            container_volume = solution.container.volume
            
            total_volume_used += used_volume
            total_volume_available += container_volume
            container_volumes.append({
                "container_id": solution.container.id,
                "used_volume": used_volume,
                "total_volume": container_volume,
                "utilization": solution.utilization_rate,
                "wasted_space": container_volume - used_volume
            })
            
        return {
            "total_volume_used": total_volume_used,
            "total_volume_available": total_volume_available,
            "global_utilization": total_volume_used / total_volume_available if total_volume_available > 0 else 0,
            "total_wasted_space": total_volume_available - total_volume_used,
            "container_volumes": container_volumes
        }
        
    def _analyze_containers(self, result: OptimizationResult) -> Dict[str, Any]:
        """Analyze container usage patterns."""
        used_containers = len(result.container_solutions)
        unused_containers = len(result.unused_containers)
        total_containers = used_containers + unused_containers
        
        container_types = {}
        for solution in result.container_solutions:
            container_type = solution.container.container_type.value
            if container_type not in container_types:
                container_types[container_type] = {
                    "count": 0,
                    "total_utilization": 0,
                    "containers": []
                }
            container_types[container_type]["count"] += 1
            container_types[container_type]["total_utilization"] += solution.utilization_rate
            container_types[container_type]["containers"].append({
                "id": solution.container.id,
                "utilization": solution.utilization_rate,
                "packages": len(solution.placed_packages)
            })
            
        # Calculate average utilization per type
        for container_type in container_types:
            count = container_types[container_type]["count"]
            container_types[container_type]["average_utilization"] = (
                container_types[container_type]["total_utilization"] / count
            )
            
        return {
            "total_containers": total_containers,
            "used_containers": used_containers,
            "unused_containers": unused_containers,
            "container_usage_rate": used_containers / total_containers if total_containers > 0 else 0,
            "container_types": container_types
        }
        
    def _analyze_packages(self, result: OptimizationResult, 
                         problem: PackingProblem) -> Dict[str, Any]:
        """Analyze package placement patterns."""
        package_stats = {}
        total_packages_requested = 0
        total_packages_placed = 0
        
        # Initialize package statistics
        for package in problem.packages:
            package_stats[package.name] = {
                "requested_min": package.min_quantity,
                "requested_max": package.max_quantity,
                "placed": 0,
                "unplaced": result.unplaced_packages.get(package.name, 0),
                "placement_rate": 0.0,
                "containers_used": [],
                "rotations_used": set()
            }
            total_packages_requested += package.max_quantity
            
        # Count placed packages
        for solution in result.container_solutions:
            for placed_package in solution.placed_packages:
                base_name = placed_package.package_name.split('_')[0]
                if base_name in package_stats:
                    package_stats[base_name]["placed"] += 1
                    package_stats[base_name]["containers_used"].append(solution.container.id)
                    if placed_package.rotation:
                        package_stats[base_name]["rotations_used"].add(placed_package.rotation)
                    total_packages_placed += 1
                    
        # Calculate placement rates
        for package_name in package_stats:
            stats = package_stats[package_name]
            max_requested = stats["requested_max"]
            if max_requested > 0:
                stats["placement_rate"] = stats["placed"] / max_requested
                
        return {
            "total_packages_requested": total_packages_requested,
            "total_packages_placed": total_packages_placed,
            "overall_placement_rate": total_packages_placed / total_packages_requested if total_packages_requested > 0 else 0,
            "package_details": package_stats
        }
        
    def _analyze_optimization_performance(self, result: OptimizationResult) -> Dict[str, Any]:
        """Analyze optimization algorithm performance."""
        performance = {
            "optimization_time": result.optimization_time,
            "generations_completed": result.generations_completed,
            "best_fitness": result.best_fitness,
            "time_per_generation": result.optimization_time / result.generations_completed if result.generations_completed > 0 else 0
        }
        
        # Analyze fitness evolution if available
        if result.algorithm_stats and "fitness_history" in result.algorithm_stats:
            fitness_history = result.algorithm_stats["fitness_history"]
            if fitness_history:
                initial_fitness = fitness_history[0]["best"]
                final_fitness = fitness_history[-1]["best"]
                improvement = final_fitness - initial_fitness
                
                performance.update({
                    "initial_fitness": initial_fitness,
                    "final_fitness": final_fitness,
                    "fitness_improvement": improvement,
                    "improvement_rate": improvement / initial_fitness if initial_fitness > 0 else 0,
                    "convergence_generation": self._find_convergence_point(fitness_history)
                })
                
        return performance
        
    def _find_convergence_point(self, fitness_history: List[Dict]) -> int:
        """Find the generation where the algorithm converged."""
        if len(fitness_history) < 10:
            return len(fitness_history)
            
        # Look for point where improvement becomes minimal
        threshold = 0.001  # 0.1% improvement threshold
        
        for i in range(10, len(fitness_history)):
            recent_improvement = (fitness_history[i]["best"] - 
                                fitness_history[i-10]["best"]) / fitness_history[i-10]["best"]
            if abs(recent_improvement) < threshold:
                return i
                
        return len(fitness_history)
        
    def _generate_recommendations(self, result: OptimizationResult, 
                                problem: PackingProblem) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Efficiency recommendations
        if result.total_efficiency < 0.7:
            recommendations.append(
                "Consider increasing population size or generations for better optimization results."
            )
            
        if result.total_efficiency < 0.5:
            recommendations.append(
                "Low efficiency detected. Review container sizes or package dimensions for better fit."
            )
            
        # Container usage recommendations
        unused_count = len(result.unused_containers)
        total_count = len(result.container_solutions) + unused_count
        
        if unused_count > total_count * 0.5:
            recommendations.append(
                "Many containers remain unused. Consider reducing the number of available containers."
            )
            
        # Utilization variance recommendations
        if result.container_solutions:
            utilizations = [sol.utilization_rate for sol in result.container_solutions]
            if np.std(utilizations) > 0.2:
                recommendations.append(
                    "High variance in container utilization. Consider balancing package distribution."
                )
                
        # Package placement recommendations
        total_unplaced = sum(result.unplaced_packages.values())
        if total_unplaced > 0:
            recommendations.append(
                f"{total_unplaced} packages could not be placed. Consider adding more containers or "
                "adjusting package quantities."
            )
            
        if not recommendations:
            recommendations.append("Optimization results look good! No major issues detected.")
            
        return recommendations
        
    def compare_results(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """
        Compare multiple optimization results.
        
        Args:
            results: List of optimization results to compare
            
        Returns:
            Comparison analysis
        """
        if not results:
            return {"error": "No results to compare"}
            
        comparison = {
            "result_count": len(results),
            "efficiency_comparison": [],
            "time_comparison": [],
            "best_result_index": 0,
            "worst_result_index": 0
        }
        
        best_efficiency = -1
        worst_efficiency = 2
        
        for i, result in enumerate(results):
            comparison["efficiency_comparison"].append({
                "index": i,
                "efficiency": result.total_efficiency,
                "containers_used": result.containers_used,
                "packages_placed": result.total_packages_placed
            })
            
            comparison["time_comparison"].append({
                "index": i,
                "optimization_time": result.optimization_time,
                "generations": result.generations_completed,
                "time_per_generation": result.optimization_time / result.generations_completed if result.generations_completed > 0 else 0
            })
            
            if result.total_efficiency > best_efficiency:
                best_efficiency = result.total_efficiency
                comparison["best_result_index"] = i
                
            if result.total_efficiency < worst_efficiency:
                worst_efficiency = result.total_efficiency
                comparison["worst_result_index"] = i
                
        return comparison