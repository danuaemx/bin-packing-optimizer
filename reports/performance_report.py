"""
Performance analysis report for optimization algorithms.
"""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any, List, Optional
from .base_report import BaseReport


class PerformanceReport(BaseReport):
    """Generate performance analysis reports."""
    
    def __init__(self, title: str = "Performance Report", output_dir: str = "output"):
        super().__init__(title, output_dir)
        
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance report from benchmark data."""
        self.data = data
        
        # Analyze performance metrics
        self.data.update({
            'execution_metrics': self._analyze_execution_times(data),
            'algorithm_comparison': self._compare_algorithms(data),
            'scalability_analysis': self._analyze_scalability(data),
            'memory_usage': self._analyze_memory_usage(data),
            'convergence_analysis': self._analyze_convergence(data)
        })
        
        return self.data
    
    def _analyze_execution_times(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze execution time performance."""
        results = data.get('results', [])
        if not results:
            return {}
        
        times = [r.get('optimization_time', 0) for r in results]
        problem_sizes = [r.get('problem_size', 0) for r in results]
        
        return {
            'average_time': sum(times) / len(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'time_std': pd.Series(times).std() if times else 0,
            'time_per_item': [t/s if s > 0 else 0 for t, s in zip(times, problem_sizes)],
            'total_runtime': sum(times)
        }
    
    def _compare_algorithms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare different algorithm performances."""
        results = data.get('results', [])
        algorithm_stats = {}
        
        for result in results:
            algo = result.get('algorithm', 'unknown')
            if algo not in algorithm_stats:
                algorithm_stats[algo] = {
                    'times': [],
                    'efficiencies': [],
                    'fitnesses': [],
                    'runs': 0
                }
            
            algorithm_stats[algo]['times'].append(result.get('optimization_time', 0))
            algorithm_stats[algo]['efficiencies'].append(result.get('efficiency', 0))
            algorithm_stats[algo]['fitnesses'].append(result.get('best_fitness', 0))
            algorithm_stats[algo]['runs'] += 1
        
        # Calculate averages
        for algo in algorithm_stats:
            stats = algorithm_stats[algo]
            stats['avg_time'] = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            stats['avg_efficiency'] = sum(stats['efficiencies']) / len(stats['efficiencies']) if stats['efficiencies'] else 0
            stats['avg_fitness'] = sum(stats['fitnesses']) / len(stats['fitnesses']) if stats['fitnesses'] else 0
        
        return algorithm_stats
    
    def _analyze_scalability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze algorithm scalability with problem size."""
        results = data.get('results', [])
        if not results:
            return {}
        
        # Group by problem size
        size_groups = {}
        for result in results:
            size = result.get('problem_size', 0)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(result)
        
        scalability_data = {}
        for size, group_results in size_groups.items():
            times = [r.get('optimization_time', 0) for r in group_results]
            efficiencies = [r.get('efficiency', 0) for r in group_results]
            
            scalability_data[size] = {
                'avg_time': sum(times) / len(times) if times else 0,
                'avg_efficiency': sum(efficiencies) / len(efficiencies) if efficiencies else 0,
                'sample_size': len(group_results)
            }
        
        return scalability_data
    
    def _analyze_memory_usage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        results = data.get('results', [])
        memory_data = []
        
        for result in results:
            if 'memory_usage' in result:
                memory_data.append(result['memory_usage'])
        
        if not memory_data:
            return {'available': False}
        
        return {
            'available': True,
            'average_memory': sum(memory_data) / len(memory_data),
            'peak_memory': max(memory_data),
            'min_memory': min(memory_data),
            'memory_efficiency': memory_data
        }
    
    def _analyze_convergence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze algorithm convergence patterns."""
        results = data.get('results', [])
        convergence_data = {}
        
        for result in results:
            if 'fitness_history' in result:
                history = result['fitness_history']
                algo = result.get('algorithm', 'unknown')
                
                if algo not in convergence_data:
                    convergence_data[algo] = []
                
                convergence_data[algo].append({
                    'generations': len(history),
                    'initial_fitness': history[0] if history else 0,
                    'final_fitness': history[-1] if history else 0,
                    'improvement': (history[-1] - history[0]) if len(history) > 1 else 0,
                    'convergence_generation': self._find_convergence_point(history)
                })
        
        return convergence_data
    
    def _find_convergence_point(self, fitness_history: List[float]) -> int:
        """Find the generation where algorithm converged."""
        if len(fitness_history) < 10:
            return len(fitness_history)
        
        # Simple convergence detection: when improvement slows significantly
        window_size = min(10, len(fitness_history) // 4)
        threshold = 0.001  # 0.1% improvement threshold
        
        for i in range(window_size, len(fitness_history)):
            recent_improvement = (fitness_history[i] - fitness_history[i-window_size]) / fitness_history[i-window_size]
            if abs(recent_improvement) < threshold:
                return i
        
        return len(fitness_history)
    
    def export_pdf(self, filename: Optional[str] = None) -> str:
        """Export performance report as PDF."""
        if filename is None:
            filename = f"performance_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = self.output_dir / filename
        
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages(filepath) as pdf:
            # Page 1: Execution time analysis
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
            fig.suptitle(f'{self.title} - {self._format_timestamp()}', fontsize=16, fontweight='bold')
            
            self._plot_execution_times(ax1)
            self._plot_algorithm_comparison(ax2)
            self._plot_scalability(ax3)
            self._plot_convergence_analysis(ax4)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Additional pages for detailed analysis
            if self.data.get('memory_usage', {}).get('available'):
                fig, ax = plt.subplots(1, 1, figsize=(11, 8.5))
                self._plot_memory_usage(ax)
                plt.title('Memory Usage Analysis')
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
        
        self.logger.info(f"Performance report exported to {filepath}")
        return str(filepath)
    
    def export_html(self, filename: Optional[str] = None) -> str:
        """Export performance report as HTML."""
        if filename is None:
            filename = f"performance_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = self.output_dir / filename
        
        html_content = self._generate_performance_html()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML performance report exported to {filepath}")
        return str(filepath)
    
    def _generate_performance_html(self) -> str:
        """Generate HTML content for performance report."""
        execution_metrics = self.data.get('execution_metrics', {})
        algorithm_comparison = self.data.get('algorithm_comparison', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e3f2fd; border-radius: 5px; }}
        .metric-value {{ font-size: 20px; font-weight: bold; color: #1976d2; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{self.title}</h1>
    <p>Generated on: {self._format_timestamp()}</p>
    
    <h2>Execution Metrics</h2>
    <div class="metric">
        <div class="metric-value">{execution_metrics.get('average_time', 0):.3f}s</div>
        <div>Average Time</div>
    </div>
    <div class="metric">
        <div class="metric-value">{execution_metrics.get('min_time', 0):.3f}s</div>
        <div>Minimum Time</div>
    </div>
    <div class="metric">
        <div class="metric-value">{execution_metrics.get('max_time', 0):.3f}s</div>
        <div>Maximum Time</div>
    </div>
    
    <h2>Algorithm Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Algorithm</th>
                <th>Runs</th>
                <th>Avg Time (s)</th>
                <th>Avg Efficiency</th>
                <th>Avg Fitness</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for algo, stats in algorithm_comparison.items():
            html += f"""
            <tr>
                <td>{algo}</td>
                <td>{stats.get('runs', 0)}</td>
                <td>{stats.get('avg_time', 0):.3f}</td>
                <td>{stats.get('avg_efficiency', 0):.2%}</td>
                <td>{stats.get('avg_fitness', 0):.3f}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
</body>
</html>
"""
        return html
    
    def _plot_execution_times(self, ax):
        """Plot execution time distribution."""
        exec_metrics = self.data.get('execution_metrics', {})
        time_per_item = exec_metrics.get('time_per_item', [])
        
        if time_per_item:
            ax.hist(time_per_item, bins=20, alpha=0.7, color='lightblue', edgecolor='black')
            ax.set_xlabel('Time per Item (seconds)')
            ax.set_ylabel('Frequency')
            ax.set_title('Execution Time Distribution')
        else:
            ax.text(0.5, 0.5, 'No execution time data', ha='center', va='center', transform=ax.transAxes)
    
    def _plot_algorithm_comparison(self, ax):
        """Plot algorithm performance comparison."""
        algo_comparison = self.data.get('algorithm_comparison', {})
        
        if not algo_comparison:
            ax.text(0.5, 0.5, 'No algorithm data', ha='center', va='center', transform=ax.transAxes)
            return
        
        algorithms = list(algo_comparison.keys())
        avg_times = [algo_comparison[algo].get('avg_time', 0) for algo in algorithms]
        avg_efficiencies = [algo_comparison[algo].get('avg_efficiency', 0) * 100 for algo in algorithms]
        
        x = range(len(algorithms))
        width = 0.35
        
        ax2 = ax.twinx()
        
        bars1 = ax.bar([i - width/2 for i in x], avg_times, width, label='Avg Time (s)', alpha=0.7)
        bars2 = ax2.bar([i + width/2 for i in x], avg_efficiencies, width, label='Avg Efficiency (%)', alpha=0.7, color='orange')
        
        ax.set_xlabel('Algorithm')
        ax.set_ylabel('Average Time (s)', color='blue')
        ax2.set_ylabel('Average Efficiency (%)', color='orange')
        ax.set_title('Algorithm Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # Add legends
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
    
    def _plot_scalability(self, ax):
        """Plot scalability analysis."""
        scalability = self.data.get('scalability_analysis', {})
        
        if not scalability:
            ax.text(0.5, 0.5, 'No scalability data', ha='center', va='center', transform=ax.transAxes)
            return
        
        sizes = sorted(scalability.keys())
        times = [scalability[size]['avg_time'] for size in sizes]
        
        ax.plot(sizes, times, 'o-', linewidth=2, markersize=6)
        ax.set_xlabel('Problem Size')
        ax.set_ylabel('Average Time (s)')
        ax.set_title('Scalability Analysis')
        ax.grid(True, alpha=0.3)
    
    def _plot_convergence_analysis(self, ax):
        """Plot convergence analysis."""
        convergence = self.data.get('convergence_analysis', {})
        
        if not convergence:
            ax.text(0.5, 0.5, 'No convergence data', ha='center', va='center', transform=ax.transAxes)
            return
        
        for algo, data_points in convergence.items():
            convergence_points = [dp['convergence_generation'] for dp in data_points]
            improvements = [dp['improvement'] for dp in data_points]
            
            ax.scatter(convergence_points, improvements, label=algo, alpha=0.7)
        
        ax.set_xlabel('Convergence Generation')
        ax.set_ylabel('Fitness Improvement')
        ax.set_title('Convergence Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_memory_usage(self, ax):
        """Plot memory usage analysis."""
        memory_data = self.data.get('memory_usage', {})
        
        if not memory_data.get('available'):
            ax.text(0.5, 0.5, 'No memory data available', ha='center', va='center', transform=ax.transAxes)
            return
        
        memory_efficiency = memory_data.get('memory_efficiency', [])
        if memory_efficiency:
            ax.plot(memory_efficiency, linewidth=2)
            ax.set_xlabel('Run Number')
            ax.set_ylabel('Memory Usage (MB)')
            ax.set_title('Memory Usage Over Time')
            ax.grid(True, alpha=0.3)
            
            # Add average line
            avg_memory = memory_data.get('average_memory', 0)
            ax.axhline(y=avg_memory, color='red', linestyle='--', label=f'Average: {avg_memory:.1f} MB')
            ax.legend()
    
    def _prepare_csv_data(self) -> 'pd.DataFrame':
        """Prepare performance data for CSV export."""
        import pandas as pd
        
        # Combine all performance metrics into a single DataFrame
        data_rows = []
        
        # Add algorithm comparison data
        algo_comparison = self.data.get('algorithm_comparison', {})
        for algo, stats in algo_comparison.items():
            data_rows.append({
                'algorithm': algo,
                'metric_type': 'performance',
                'avg_time': stats.get('avg_time', 0),
                'avg_efficiency': stats.get('avg_efficiency', 0),
                'avg_fitness': stats.get('avg_fitness', 0),
                'runs': stats.get('runs', 0)
            })
        
        # Add scalability data
        scalability = self.data.get('scalability_analysis', {})
        for size, stats in scalability.items():
            data_rows.append({
                'problem_size': size,
                'metric_type': 'scalability',
                'avg_time': stats.get('avg_time', 0),
                'avg_efficiency': stats.get('avg_efficiency', 0),
                'sample_size': stats.get('sample_size', 0)
            })
        
        return pd.DataFrame(data_rows) if data_rows else pd.DataFrame()