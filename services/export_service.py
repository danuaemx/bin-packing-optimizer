"""
Export service for generating reports and files.
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from models.optimization_result import OptimizationResult
from models.data_structures import PackingProblem


class ExportService:
    """
    Service for exporting optimization results to various formats.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def export_to_json(self, result: OptimizationResult, 
                      problem: PackingProblem, filepath: str) -> bool:
        """
        Export optimization result to JSON format.
        
        Args:
            result: Optimization result to export
            problem: Original packing problem
            filepath: Path to save JSON file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_data = {
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "optimization_time": result.optimization_time,
                    "generations_completed": result.generations_completed,
                    "best_fitness": result.best_fitness,
                    "total_efficiency": result.total_efficiency,
                    "containers_used": result.containers_used,
                    "packages_placed": result.total_packages_placed
                },
                "problem_definition": {
                    "packages": [
                        {
                            "name": pkg.name,
                            "dimensions": pkg.dimensions,
                            "min_quantity": pkg.min_quantity,
                            "max_quantity": pkg.max_quantity,
                            "package_type": pkg.package_type.value,
                            "weight": pkg.weight,
                            "value": pkg.value
                        }
                        for pkg in problem.packages
                    ],
                    "containers": [
                        {
                            "id": container.id,
                            "dimensions": container.dimensions,
                            "is_optional": container.is_optional,
                            "container_type": container.container_type.value,
                            "max_weight": container.max_weight,
                            "cost": container.cost
                        }
                        for container in problem.containers
                    ]
                },
                "solution": {
                    "container_solutions": [
                        {
                            "container_id": sol.container.id,
                            "utilization_rate": sol.utilization_rate,
                            "placed_packages": [
                                {
                                    "package_name": pkg.package_name,
                                    "position": pkg.position,
                                    "dimensions": pkg.dimensions,
                                    "rotation": pkg.rotation
                                }
                                for pkg in sol.placed_packages
                            ]
                        }
                        for sol in result.container_solutions
                    ],
                    "unused_containers": [container.id for container in result.unused_containers],
                    "unplaced_packages": result.unplaced_packages
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Successfully exported results to JSON: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
            return False
            
    def export_to_csv(self, result: OptimizationResult, filepath: str) -> bool:
        """
        Export optimization result to CSV format.
        
        Args:
            result: Optimization result to export
            filepath: Path to save CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Container_ID', 'Package_Name', 'Position_X', 'Position_Y', 
                    'Position_Z', 'Width', 'Height', 'Depth', 'Rotation', 'Utilization_Rate'
                ])
                
                # Write data
                for solution in result.container_solutions:
                    for package in solution.placed_packages:
                        row = [
                            solution.container.id,
                            package.package_name,
                        ]
                        
                        # Handle different dimensions
                        position = list(package.position) + [None] * (3 - len(package.position))
                        dimensions = list(package.dimensions) + [None] * (3 - len(package.dimensions))
                        
                        row.extend(position[:3])  # Position X, Y, Z
                        row.extend(dimensions[:3])  # Width, Height, Depth
                        row.append(package.rotation or "None")
                        row.append(f"{solution.utilization_rate:.4f}")
                        
                        writer.writerow(row)
                        
            self.logger.info(f"Successfully exported results to CSV: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {e}")
            return False
            
    def export_summary_report(self, result: OptimizationResult, 
                            problem: PackingProblem, filepath: str) -> bool:
        """
        Export a summary report in text format.
        
        Args:
            result: Optimization result to export
            problem: Original packing problem
            filepath: Path to save text file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("BIN PACKING OPTIMIZATION REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Problem summary
                f.write("PROBLEM SUMMARY\n")
                f.write("-" * 20 + "\n")
                f.write(f"Packages: {len(problem.packages)}\n")
                f.write(f"Containers: {len(problem.containers)}\n")
                f.write(f"Dimensions: {problem.dimensions_count}D\n\n")
                
                # Optimization results
                f.write("OPTIMIZATION RESULTS\n")
                f.write("-" * 25 + "\n")
                f.write(f"Total Efficiency: {result.total_efficiency:.2%}\n")
                f.write(f"Containers Used: {result.containers_used}\n")
                f.write(f"Packages Placed: {result.total_packages_placed}\n")
                f.write(f"Optimization Time: {result.optimization_time:.2f} seconds\n")
                f.write(f"Generations: {result.generations_completed}\n")
                f.write(f"Best Fitness: {result.best_fitness:.6f}\n\n")
                
                # Container details
                f.write("CONTAINER DETAILS\n")
                f.write("-" * 20 + "\n")
                for i, solution in enumerate(result.container_solutions, 1):
                    f.write(f"Container {i}: {solution.container.id}\n")
                    f.write(f"  Utilization: {solution.utilization_rate:.2%}\n")
                    f.write(f"  Packages: {len(solution.placed_packages)}\n")
                    f.write(f"  Dimensions: {solution.container.dimensions}\n\n")
                
                # Unplaced packages
                if result.unplaced_packages:
                    f.write("UNPLACED PACKAGES\n")
                    f.write("-" * 20 + "\n")
                    for package_name, quantity in result.unplaced_packages.items():
                        if quantity > 0:
                            f.write(f"  {package_name}: {quantity}\n")
                    f.write("\n")
                    
            self.logger.info(f"Successfully exported summary report: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export summary report: {e}")
            return False