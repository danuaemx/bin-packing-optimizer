"""
Comparison report for analyzing multiple optimization runs.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from .base_report import BaseReport


class ComparisonReport(BaseReport):
    """Generate comparison reports between different optimization scenarios."""
    
    def __init__(self, title: str = "Comparison Report", output_dir: str = "output"):
        super().__init__(title, output_dir)
        
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison report from multiple results."""
        self.data = data
        
        scenarios = data.get('scenarios', [])
        if len(scenarios) < 2:
            raise ValueError("At least 2 scenarios required for comparison")
        
        self.data.update({
            'scenario_summary': self._analyze_scenarios(scenarios),
            'statistical_comparison': self._statistical_analysis(scenarios),
            'efficiency_comparison': self._compare_efficiencies(scenarios),
            'cost_benefit_analysis': self._cost_benefit_analysis(scenarios),
            'recommendations': self._generate_recommendations(scenarios)
        })
        
        return self.data
    
    def _analyze_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze each scenario individually."""
        scenario_summaries = []
        
        for i, scenario in enumerate(scenarios):
            result = scenario.get('result')
            if not result:
                continue
                
            summary = {
                'scenario_id': scenario.get('name', f'Scenario_{i+1}'),
                'algorithm': scenario.get('algorithm', 'Unknown'),
                'containers_used': getattr(result, 'containers_used', 0),
                'total_efficiency': getattr(result, 'total_efficiency', 0),
                'optimization_time': getattr(result, 'optimization_time', 0),
                'total_cost': sum(getattr(container, 'total_cost', 0) 
                                for container in getattr(result, 'container_solutions', [])),
                'total_value': sum(getattr(container, 'total_value', 0) 
                                 for container in getattr(result, 'container_solutions', [])),
                'items_placed': sum(len(getattr(container, 'placed_packages', [])) 
                                  for container in getattr(result, 'container_solutions', [])),
                'best_fitness': getattr(result, 'best_fitness', 0)
            }
            scenario_summaries.append(summary)
        
        return scenario_summaries
    
    def _statistical_analysis(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform statistical analysis across scenarios."""
        scenario_summaries = self.data.get('scenario_summary', [])
        
        if not scenario_summaries:
            return {}
        
        metrics = ['total_efficiency', 'optimization_time', 'containers_used', 'total_cost']
        statistical_data = {}
        
        for metric in metrics:
            values = [scenario.get(metric, 0) for scenario in scenario_summaries]
            
            statistical_data[metric] = {
                'mean': np.mean(values),
                'median': np.median(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'range': np.max(values) - np.min(values),
                'coefficient_of_variation': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
            }
        
        return statistical_data
    
    def _compare_efficiencies(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare efficiency metrics across scenarios."""
        scenario_summaries = self.data.get('scenario_summary', [])
        
        if not scenario_summaries:
            return {}
        
        efficiencies = [scenario.get('total_efficiency', 0) for scenario in scenario_summaries]
        scenario_names = [scenario.get('scenario_id', '') for scenario in scenario_summaries]
        
        # Find best and worst performing scenarios
        best_idx = np.argmax(efficiencies)
        worst_idx = np.argmin(efficiencies)
        
        efficiency_comparison = {
            'best_scenario': {
                'name': scenario_names[best_idx],
                'efficiency': efficiencies[best_idx],
                'details': scenario_summaries[best_idx]
            },
            'worst_scenario': {
                'name': scenario_names[worst_idx],
                'efficiency': efficiencies[worst_idx],
                'details': scenario_summaries[worst_idx]
            },
            'efficiency_spread': max(efficiencies) - min(efficiencies),
            'scenarios_above_80_percent': sum(1 for e in efficiencies if e >= 0.8),
            'average_efficiency': np.mean(efficiencies)
        }
        
        return efficiency_comparison
    
    def _cost_benefit_analysis(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform cost-benefit analysis."""
        scenario_summaries = self.data.get('scenario_summary', [])
        
        if not scenario_summaries:
            return {}
        
        cost_benefit_data = []
        
        for scenario in scenario_summaries:
            total_cost = scenario.get('total_cost', 0)
            total_value = scenario.get('total_value', 0)
            efficiency = scenario.get('total_efficiency', 0)
            time = scenario.get('optimization_time', 0)
            
            # Calculate various cost-benefit metrics
            roi = (total_value - total_cost) / total_cost if total_cost > 0 else 0
            value_per_second = total_value / time if time > 0 else 0
            efficiency_per_cost = efficiency / total_cost if total_cost > 0 else 0
            
            cost_benefit_data.append({
                'scenario_id': scenario.get('scenario_id'),
                'roi': roi,
                'value_per_second': value_per_second,
                'efficiency_per_cost': efficiency_per_cost,
                'cost_efficiency_ratio': total_cost / efficiency if efficiency > 0 else float('inf')
            })
        
        # Find best ROI scenario
        best_roi_scenario = max(cost_benefit_data, key=lambda x: x['roi'])
        
        return {
            'cost_benefit_details': cost_benefit_data,
            'best_roi_scenario': best_roi_scenario,
            'average_roi': np.mean([cb['roi'] for cb in cost_benefit_data])
        }
    
    def _generate_recommendations(self, scenarios: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on comparison results."""
        recommendations = []
        
        efficiency_comparison = self.data.get('efficiency_comparison', {})
        cost_benefit = self.data.get('cost_benefit_analysis', {})
        statistical = self.data.get('statistical_comparison', {})
        
        # Efficiency-based recommendations
        if efficiency_comparison:
            best_scenario = efficiency_comparison.get('best_scenario', {})
            if best_scenario:
                recommendations.append(
                    f"For maximum efficiency ({best_scenario.get('efficiency', 0):.2%}), "
                    f"use {best_scenario.get('name', 'the best performing scenario')}."
                )
        
        # Cost-benefit recommendations
        if cost_benefit:
            best_roi = cost_benefit.get('best_roi_scenario', {})
            if best_roi:
                recommendations.append(
                    f"For best return on investment ({best_roi.get('roi', 0):.2%}), "
                    f"consider {best_roi.get('scenario_id', 'the optimal scenario')}."
                )
        
        # Statistical insights
        if statistical:
            time_stats = statistical.get('optimization_time', {})
            efficiency_stats = statistical.get('total_efficiency', {})
            
            if time_stats and efficiency_stats:
                if time_stats.get('coefficient_of_variation', 0) > 0.3:
                    recommendations.append(
                        "High variation in optimization times detected. "
                        "Consider investigating algorithm parameters for consistency."
                    )
                
                if efficiency_stats.get('mean', 0) < 0.7:
                    recommendations.append(
                        "Average efficiency below 70%. Consider algorithm tuning or "
                        "problem formulation adjustments."
                    )
        
        # General recommendations
        scenario_summaries = self.data.get('scenario_summary', [])
        if len(scenario_summaries) >= 3:
            recommendations.append(
                "With multiple scenarios tested, consider implementing ensemble "
                "methods or adaptive algorithm selection."
            )
        
        return recommendations
    
    def export_pdf(self, filename: Optional[str] = None) -> str:
        """Export comparison report as PDF."""
        if filename is None:
            filename = f"comparison_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = self.output_dir / filename
        
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages(filepath) as pdf:
            # Page 1: Overview comparison
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
            fig.suptitle(f'{self.title} - {self._format_timestamp()}', fontsize=16, fontweight='bold')
            
            self._plot_efficiency_comparison(ax1)
            self._plot_time_comparison(ax2)
            self._plot_cost_benefit(ax3)
            self._plot_statistical_summary(ax4)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Page 2: Detailed analysis
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
            self._plot_scenario_radar(ax1)
            self._plot_recommendations(ax2)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        
        self.logger.info(f"Comparison report exported to {filepath}")
        return str(filepath)
    
    def export_html(self, filename: Optional[str] = None) -> str:
        """Export comparison report as HTML."""
        if filename is None:
            filename = f"comparison_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = self.output_dir / filename
        
        html_content = self._generate_comparison_html()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML comparison report exported to {filepath}")
        return str(filepath)
    
    def _generate_comparison_html(self) -> str:
        """Generate HTML content for comparison report."""
        scenario_summaries = self.data.get('scenario_summary', [])
        efficiency_comparison = self.data.get('efficiency_comparison', {})
        recommendations = self.data.get('recommendations', [])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .scenario-card {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .best {{ background-color: #d4edda; border-color: #c3e6cb; }}
        .worst {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        .recommendations {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{self.title}</h1>
    <p>Generated on: {self._format_timestamp()}</p>
    
    <h2>Scenario Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Scenario</th>
                <th>Algorithm</th>
                <th>Efficiency</th>
                <th>Time (s)</th>
                <th>Containers</th>
                <th>Total Cost</th>
                <th>Items Placed</th>
            </tr>
        </thead>
        <tbody>
"""
        
        best_scenario_name = efficiency_comparison.get('best_scenario', {}).get('name', '')
        worst_scenario_name = efficiency_comparison.get('worst_scenario', {}).get('name', '')
        
        for scenario in scenario_summaries:
            scenario_name = scenario.get('scenario_id', '')
            row_class = ''
            if scenario_name == best_scenario_name:
                row_class = 'class="best"'
            elif scenario_name == worst_scenario_name:
                row_class = 'class="worst"'
            
            html += f"""
            <tr {row_class}>
                <td>{scenario_name}</td>
                <td>{scenario.get('algorithm', 'N/A')}</td>
                <td>{scenario.get('total_efficiency', 0):.2%}</td>
                <td>{scenario.get('optimization_time', 0):.3f}</td>
                <td>{scenario.get('containers_used', 0)}</td>
                <td>${scenario.get('total_cost', 0):.2f}</td>
                <td>{scenario.get('items_placed', 0)}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
"""
        
        for recommendation in recommendations:
            html += f"<li>{recommendation}</li>"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        return html
    
    def _plot_efficiency_comparison(self, ax):
        """Plot efficiency comparison across scenarios."""
        scenario_summaries = self.data.get('scenario_summary', [])
        
        if not scenario_summaries:
            ax.text(0.5, 0.5, 'No scenario data', ha='center', va='center', transform=ax.transAxes)
            return
        
        names = [s.get('scenario_id', '') for s in scenario_summaries]
        efficiencies = [s.get('total_efficiency', 0) * 100 for s in scenario_summaries]
        
        colors = ['green' if e == max(efficiencies) else 'red' if e == min(efficiencies) else 'skyblue' 
                 for e in efficiencies]
        
        bars = ax.bar(names, efficiencies, color=colors, alpha=0.7)
        ax.set_ylabel('Efficiency (%)')
        ax.set_title('Efficiency Comparison')
        ax.set_ylim(0, 100)
        
        # Add value labels
        for bar, eff in zip(bars, efficiencies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{eff:.1f}%', ha='center', va='bottom')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _plot_time_comparison(self, ax):
        """Plot optimization time comparison."""
        scenario_summaries = self.data.get('scenario_summary', [])
        
        if not scenario_summaries:
            ax.text(0.5, 0.5, 'No scenario data', ha='center', va='center', transform=ax.transAxes)
            return
        
        names = [s.get('scenario_id', '') for s in scenario_summaries]
        times = [s.get('optimization_time', 0) for s in scenario_summaries]
        
        ax.bar(names, times, color='lightcoral', alpha=0.7)
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Optimization Time Comparison')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _plot_cost_benefit(self, ax):
        """Plot cost-benefit analysis."""
        cost_benefit = self.data.get('cost_benefit_analysis', {})
        cost_benefit_details = cost_benefit.get('cost_benefit_details', [])
        
        if not cost_benefit_details:
            ax.text(0.5, 0.5, 'No cost-benefit data', ha='center', va='center', transform=ax.transAxes)
            return
        
        scenario_names = [cb.get('scenario_id', '') for cb in cost_benefit_details]
        rois = [cb.get('roi', 0) * 100 for cb in cost_benefit_details]  # Convert to percentage
        
        colors = ['green' if roi > 0 else 'red' for roi in rois]
        
        bars = ax.bar(scenario_names, rois, color=colors, alpha=0.7)
        ax.set_ylabel('ROI (%)')
        ax.set_title('Return on Investment')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Add value labels
        for bar, roi in zip(bars, rois):
            height = bar.get_height()
            va = 'bottom' if height >= 0 else 'top'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{roi:.1f}%', ha='center', va=va)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _plot_statistical_summary(self, ax):
        """Plot statistical summary."""
        statistical = self.data.get('statistical_comparison', {})
        
        if not statistical:
            ax.text(0.5, 0.5, 'No statistical data', ha='center', va='center', transform=ax.transAxes)
            return
        
        # Create a summary table view
        ax.axis('off')
        
        summary_text = "Statistical Summary\n\n"
        
        for metric, stats in statistical.items():
            if isinstance(stats, dict):
                summary_text += f"{metric.replace('_', ' ').title()}:\n"
                summary_text += f"  Mean: {stats.get('mean', 0):.3f}\n"
                summary_text += f"  Std:  {stats.get('std', 0):.3f}\n"
                summary_text += f"  Range: {stats.get('range', 0):.3f}\n\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        ax.set_title('Statistical Summary')
    
    def _plot_scenario_radar(self, ax):
        """Plot radar chart comparing scenarios."""
        scenario_summaries = self.data.get('scenario_summary', [])
        
        if len(scenario_summaries) < 2:
            ax.text(0.5, 0.5, 'Need at least 2 scenarios for radar chart', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Select key metrics for radar chart
        metrics = ['total_efficiency', 'containers_used', 'optimization_time', 'items_placed']
        metric_labels = ['Efficiency', 'Containers', 'Time', 'Items']
        
        # Normalize data to 0-1 scale for radar chart
        all_values = {}
        for metric in metrics:
            values = [s.get(metric, 0) for s in scenario_summaries]
            if max(values) > 0:
                all_values[metric] = [(v - min(values)) / (max(values) - min(values)) for v in values]
            else:
                all_values[metric