"""
Optimization report generator for bin packing results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_report import BaseReport
from models.optimization_result import OptimizationResult


class OptimizationReport(BaseReport):
    """Generate comprehensive optimization reports."""
    
    def __init__(self, title: str = "Optimization Report", output_dir: str = "output"):
        super().__init__(title, output_dir)
        
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization report from result data."""
        self.data = data
        
        # Extract key metrics
        result = data.get('result')
        if isinstance(result, OptimizationResult):
            self.data.update({
                'summary': self._generate_summary(result),
                'efficiency_metrics': self._calculate_efficiency_metrics(result),
                'container_utilization': self._analyze_container_utilization(result),
                'item_placement': self._analyze_item_placement(result),
                'algorithm_performance': self._analyze_algorithm_performance(result)
            })
        
        return self.data
    
    def _generate_summary(self, result: OptimizationResult) -> Dict[str, Any]:
        """Generate executive summary."""
        total_items = sum(len(container.placed_packages) for container in result.container_solutions)
        
        return {
            'total_containers_used': result.containers_used,
            'total_items_placed': total_items,
            'overall_efficiency': result.total_efficiency,
            'optimization_time': result.optimization_time,
            'algorithm_used': result.algorithm_name,
            'generations_completed': result.generations_completed,
            'best_fitness': result.best_fitness,
            'total_value': sum(container.total_value for container in result.container_solutions),
            'total_cost': sum(container.total_cost for container in result.container_solutions)
        }
    
    def _calculate_efficiency_metrics(self, result: OptimizationResult) -> Dict[str, Any]:
        """Calculate detailed efficiency metrics."""
        efficiencies = []
        utilizations = []
        
        for container in result.container_solutions:
            efficiency = container.efficiency
            utilization = container.volume_utilization
            efficiencies.append(efficiency)
            utilizations.append(utilization)
        
        return {
            'efficiency_stats': {
                'mean': sum(efficiencies) / len(efficiencies) if efficiencies else 0,
                'min': min(efficiencies) if efficiencies else 0,
                'max': max(efficiencies) if efficiencies else 0,
                'std': pd.Series(efficiencies).std() if efficiencies else 0
            },
            'utilization_stats': {
                'mean': sum(utilizations) / len(utilizations) if utilizations else 0,
                'min': min(utilizations) if utilizations else 0,
                'max': max(utilizations) if utilizations else 0,
                'std': pd.Series(utilizations).std() if utilizations else 0
            },
            'containers_above_80_percent': sum(1 for e in efficiencies if e >= 0.8),
            'containers_below_50_percent': sum(1 for e in efficiencies if e < 0.5)
        }
    
    def _analyze_container_utilization(self, result: OptimizationResult) -> List[Dict[str, Any]]:
        """Analyze individual container utilization."""
        container_analysis = []
        
        for i, container in enumerate(result.container_solutions):
            analysis = {
                'container_id': container.container_id,
                'container_index': i,
                'efficiency': container.efficiency,
                'volume_utilization': container.volume_utilization,
                'weight_utilization': getattr(container, 'weight_utilization', None),
                'items_count': len(container.placed_packages),
                'total_value': container.total_value,
                'total_cost': container.total_cost,
                'dimensions': getattr(container, 'dimensions', None)
            }
            container_analysis.append(analysis)
        
        return container_analysis
    
    def _analyze_item_placement(self, result: OptimizationResult) -> Dict[str, Any]:
        """Analyze item placement patterns."""
        all_items = []
        placement_stats = {}
        
        for container in result.container_solutions:
            for package in container.placed_packages:
                all_items.append({
                    'name': package.name,
                    'dimensions': package.dimensions,
                    'position': getattr(package, 'position', None),
                    'rotation': getattr(package, 'rotation', None),
                    'value': getattr(package, 'value', None),
                    'weight': getattr(package, 'weight', None)
                })
        
        # Analyze placement patterns
        if all_items:
            dimensions_used = [item['dimensions'] for item in all_items]
            placement_stats = {
                'total_items_placed': len(all_items),
                'unique_item_types': len(set(item['name'] for item in all_items)),
                'rotation_usage': sum(1 for item in all_items if item.get('rotation')),
                'average_item_value': sum(item.get('value', 0) for item in all_items) / len(all_items)
            }
        
        return {
            'placement_statistics': placement_stats,
            'items_detail': all_items
        }
    
    def _analyze_algorithm_performance(self, result: OptimizationResult) -> Dict[str, Any]:
        """Analyze algorithm performance metrics."""
        return {
            'algorithm_name': result.algorithm_name,
            'optimization_time': result.optimization_time,
            'generations_completed': result.generations_completed,
            'best_fitness': result.best_fitness,
            'convergence_rate': getattr(result, 'convergence_rate', None),
            'fitness_improvement': getattr(result, 'fitness_improvement', None),
            'time_per_generation': result.optimization_time / result.generations_completed if result.generations_completed > 0 else 0
        }
    
    def export_pdf(self, filename: Optional[str] = None) -> str:
        """Export optimization report as PDF."""
        if filename is None:
            filename = f"optimization_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = self.output_dir / filename
        
        with PdfPages(filepath) as pdf:
            # Page 1: Summary
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
            fig.suptitle(f'{self.title} - {self._format_timestamp()}', fontsize=16, fontweight='bold')
            
            self._plot_efficiency_distribution(ax1)
            self._plot_container_utilization(ax2)
            self._plot_algorithm_performance(ax3)
            self._plot_summary_stats(ax4)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Page 2: Detailed visualization
            if self.data.get('container_utilization'):
                fig, ax = plt.subplots(1, 1, figsize=(11, 8.5))
                self._plot_detailed_container_view(ax)
                plt.title('Detailed Container Analysis')
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
        
        self.logger.info(f"PDF report exported to {filepath}")
        return str(filepath)
    
    def export_html(self, filename: Optional[str] = None) -> str:
        """Export optimization report as HTML."""
        if filename is None:
            filename = f"optimization_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = self.output_dir / filename
        
        html_content = self._generate_html_content()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report exported to {filepath}")
        return str(filepath)
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        summary = self.data.get('summary', {})
        efficiency = self.data.get('efficiency_metrics', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .metric-label {{ font-size: 14px; color: #6c757d; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        .efficiency-good {{ color: #28a745; }}
        .efficiency-warning {{ color: #ffc107; }}
        .efficiency-poor {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.title}</h1>
        <p>Generated on: {self._format_timestamp()}</p>
    </div>
    
    <div class="metrics-section">
        <h2>Key Metrics</h2>
        <div class="metric">
            <div class="metric-value">{summary.get('total_containers_used', 0)}</div>
            <div class="metric-label">Containers Used</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary.get('total_items_placed', 0)}</div>
            <div class="metric-label">Items Placed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary.get('overall_efficiency', 0):.2%}</div>
            <div class="metric-label">Overall Efficiency</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary.get('optimization_time', 0):.2f}s</div>
            <div class="metric-label">Optimization Time</div>
        </div>
    </div>
    
    <div class="container-details">
        <h2>Container Utilization</h2>
        <table>
            <thead>
                <tr>
                    <th>Container ID</th>
                    <th>Efficiency</th>
                    <th>Volume Utilization</th>
                    <th>Items Count</th>
                    <th>Total Value</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for container in self.data.get('container_utilization', []):
            efficiency_class = self._get_efficiency_class(container.get('efficiency', 0))
            html += f"""
                <tr>
                    <td>{container.get('container_id', 'N/A')}</td>
                    <td class="{efficiency_class}">{container.get('efficiency', 0):.2%}</td>
                    <td>{container.get('volume_utilization', 0):.2%}</td>
                    <td>{container.get('items_count', 0)}</td>
                    <td>${container.get('total_value', 0):.2f}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def _get_efficiency_class(self, efficiency: float) -> str:
        """Get CSS class based on efficiency level."""
        if efficiency >= 0.8:
            return "efficiency-good"
        elif efficiency >= 0.6:
            return "efficiency-warning"
        else:
            return "efficiency-poor"
    
    def _plot_efficiency_distribution(self, ax):
        """Plot efficiency distribution."""
        container_data = self.data.get('container_utilization', [])
        if not container_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Efficiency Distribution')
            return
        
        efficiencies = [c.get('efficiency', 0) for c in container_data]
        ax.hist(efficiencies, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_xlabel('Efficiency')
        ax.set_ylabel('Number of Containers')
        ax.set_title('Efficiency Distribution')
        ax.axvline(x=0.8, color='red', linestyle='--', label='Target (80%)')
        ax.legend()
    
    def _plot_container_utilization(self, ax):
        """Plot container utilization chart."""
        container_data = self.data.get('container_utilization', [])
        if not container_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Container Utilization')
            return
        
        container_ids = [f"C{i+1}" for i in range(len(container_data))]
        efficiencies = [c.get('efficiency', 0) * 100 for c in container_data]
        
        colors = ['#28a745' if e >= 80 else '#ffc107' if e >= 60 else '#dc3545' for e in efficiencies]
        
        bars = ax.bar(container_ids, efficiencies, color=colors, alpha=0.7)
        ax.set_ylabel('Efficiency (%)')
        ax.set_title('Container Utilization')
        ax.set_ylim(0, 100)
        
        # Add value labels
        for bar, eff in zip(bars, efficiencies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{eff:.1f}%', ha='center', va='bottom', fontsize=8)
    
    def _plot_algorithm_performance(self, ax):
        """Plot algorithm performance metrics."""
        perf_data = self.data.get('algorithm_performance', {})
        
        metrics = ['Time (s)', 'Generations', 'Fitness']
        values = [
            perf_data.get('optimization_time', 0),
            perf_data.get('generations_completed', 0),
            perf_data.get('best_fitness', 0) * 100  # Scale fitness for visibility
        ]
        
        ax.bar(metrics, values, color=['lightblue', 'lightgreen', 'lightcoral'])
        ax.set_title('Algorithm Performance')
        ax.set_ylabel('Value')
    
    def _plot_summary_stats(self, ax):
        """Plot summary statistics."""
        summary = self.data.get('summary', {})
        
        # Create a simple text summary
        ax.axis('off')
        summary_text = f"""
Algorithm: {summary.get('algorithm_used', 'N/A')}
Total Containers: {summary.get('total_containers_used', 0)}
Total Items: {summary.get('total_items_placed', 0)}
Overall Efficiency: {summary.get('overall_efficiency', 0):.2%}
Total Value: ${summary.get('total_value', 0):.2f}
Total Cost: ${summary.get('total_cost', 0):.2f}
Optimization Time: {summary.get('optimization_time', 0):.2f}s
"""
        ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        ax.set_title('Summary Statistics')
    
    def _plot_detailed_container_view(self, ax):
        """Plot detailed container visualization."""
        container_data = self.data.get('container_utilization', [])
        if not container_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            return
        
        # Create a grid showing container efficiency
        n_containers = len(container_data)
        cols = min(5, n_containers)
        rows = (n_containers + cols - 1) // cols
        
        for i, container in enumerate(container_data):
            row = i // cols
            col = i % cols
            
            efficiency = container.get('efficiency', 0)
            color = plt.cm.RdYlGn(efficiency)  # Color map from red to green
            
            rect = patches.Rectangle((col, rows - row - 1), 0.8, 0.8, 
                                   linewidth=1, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            
            # Add text
            ax.text(col + 0.4, rows - row - 0.5, f'{efficiency:.1%}', 
                   ha='center', va='center', fontweight='bold')
            ax.text(col + 0.4, rows - row - 0.7, f"C{i+1}", 
                   ha='center', va='center', fontsize=8)
        
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Container Efficiency Heatmap')
    
    def _prepare_csv_data(self) -> 'pd.DataFrame':
        """Prepare data for CSV export."""
        import pandas as pd
        
        container_data = self.data.get('container_utilization', [])
        if not container_data:
            return pd.DataFrame()
        
        return pd.DataFrame(container_data)