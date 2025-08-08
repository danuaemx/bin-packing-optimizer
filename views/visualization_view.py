"""
Visualization view for creating charts and graphs
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from .base_view import BaseView
from models.bin import Bin
from models.item import Item


class VisualizationView(BaseView):
    """View for creating visualizations of bin packing results"""
    
    def __init__(self, style: str = 'default', figsize: Tuple[int, int] = (12, 8)):
        super().__init__()
        self.style = style
        self.figsize = figsize
        plt.style.use(style)
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render data as visualization"""
        if 'bins' in data and 'items' in data:
            self.plot_bin_packing(data['bins'], data.get('title', 'Bin Packing Results'))
    
    def display_results(self, bins: List[Bin], items: List[Item], 
                       algorithm: str, execution_time: float) -> None:
        """Display results as multiple visualizations"""
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Bin Packing Results - {algorithm}', fontsize=16, fontweight='bold')
        
        # Plot 1: Bin utilization
        self._plot_bin_utilization(bins, ax1)
        
        # Plot 2: Item distribution
        self._plot_item_distribution(bins, items, ax2)
        
        # Plot 3: Bin packing visualization
        self._plot_bin_packing_2d(bins, ax3)
        
        # Plot 4: Statistics
        self._plot_statistics(bins, items, algorithm, execution_time, ax4)
        
        plt.tight_layout()
        plt.show()
    
    def _plot_bin_utilization(self, bins: List[Bin], ax) -> None:
        """Plot bin utilization chart"""
        bin_numbers = [f'Bin {i+1}' for i in range(len(bins))]
        utilizations = []
        
        for bin in bins:
            used = bin.get_used_capacity()
            utilization = (used / bin.capacity * 100) if bin.capacity > 0 else 0
            utilizations.append(utilization)
        
        colors = ['#ff9999' if u < 70 else '#99ff99' if u < 90 else '#9999ff' for u in utilizations]
        
        bars = ax.bar(bin_numbers, utilizations, color=colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel('Utilization (%)')
        ax.set_title('Bin Utilization')
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, util in zip(bars, utilizations):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{util:.1f}%', ha='center', va='bottom')
        
        # Add horizontal line at 80% (good utilization threshold)
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='80% Target')
        ax.legend()
    
    def _plot_item_distribution(self, bins: List[Bin], items: List[Item], ax) -> None:
        """Plot item size distribution"""
        all_sizes = [item.size for item in items]
        
        ax.hist(all_sizes, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_xlabel('Item Size')
        ax.set_ylabel('Frequency')
        ax.set_title('Item Size Distribution')
        
        # Add statistics
        mean_size = np.mean(all_sizes)
        median_size = np.median(all_sizes)
        ax.axvline(mean_size, color='red', linestyle='--', label=f'Mean: {mean_size:.1f}')
        ax.axvline(median_size, color='green', linestyle='--', label=f'Median: {median_size:.1f}')
        ax.legend()
    
    def _plot_bin_packing_2d(self, bins: List[Bin], ax) -> None:
        """Plot 2D representation of bin packing"""
        if not bins:
            ax.text(0.5, 0.5, 'No bins to display', ha='center', va='center', transform=ax.transAxes)
            return
        
        # Create a simple 2D visualization
        max_capacity = max(bin.capacity for bin in bins) if bins else 1
        colors = plt.cm.Set3(np.linspace(0, 1, len(bins)))
        
        y_pos = 0
        for i, (bin, color) in enumerate(zip(bins, colors)):
            # Draw bin outline
            rect = patches.Rectangle((0, y_pos), max_capacity, 1, 
                                   linewidth=2, edgecolor='black', facecolor='white')
            ax.add_patch(rect)
            
            # Draw items in bin
            x_pos = 0
            item_colors = plt.cm.viridis(np.linspace(0, 1, len(bin.items)))
            for item, item_color in zip(bin.items, item_colors):
                item_rect = patches.Rectangle((x_pos, y_pos), item.size, 1,
                                            facecolor=item_color, alpha=0.7,
                                            edgecolor='black', linewidth=1)
                ax.add_patch(item_rect)
                
                # Add item label if there's space
                if item.size > max_capacity * 0.05:  # Only label if item is large enough
                    ax.text(x_pos + item.size/2, y_pos + 0.5, item.name,
                           ha='center', va='center', fontsize=8, rotation=0)
                
                x_pos += item.size
            
            # Add bin label
            ax.text(-max_capacity * 0.05, y_pos + 0.5, f'Bin {i+1}',
                   ha='right', va='center', fontweight='bold')
            
            y_pos += 1.5
        
        ax.set_xlim(-max_capacity * 0.1, max_capacity * 1.1)
        ax.set_ylim(-0.5, len(bins) * 1.5)
        ax.set_xlabel('Capacity')
        ax.set_title('Bin Packing Layout')
        ax.set_yticks([])
    
    def _plot_statistics(self, bins: List[Bin], items: List[Item], 
                        algorithm: str, execution_time: float, ax) -> None:
        """Plot summary statistics"""
        ax.axis('off')
        
        # Calculate statistics
        total_capacity = sum(bin.capacity for bin in bins)
        total_used = sum(bin.get_used_capacity() for bin in bins)
        efficiency = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        
        used_items = set()
        for bin in bins:
            used_items.update(item.name for item in bin.items)
        unused_items = len([item for item in items if item.name not in used_items])
        
        # Create statistics text
        stats_text = f"""
OPTIMIZATION STATISTICS

Algorithm: {algorithm}
Execution Time: {self.format_time(execution_time)}

Total Items: {len(items)}
Unused Items: {unused_items}
Bins Used: {len(bins)}

Total Capacity: {total_capacity}
Used Capacity: {total_used}
Efficiency: {self.format_efficiency(efficiency)}

Average Bin Utilization: {np.mean([(bin.get_used_capacity() / bin.capacity * 100) for bin in bins]):.1f}%
"""
        
        ax.text(0.1, 0.9, stats_text, transform=ax.transAxes, fontsize=12,
               verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    def plot_bin_packing(self, bins: List[Bin], title: str = "Bin Packing Results") -> None:
        """Create a standalone bin packing visualization"""
        fig, ax = plt.subplots(figsize=self.figsize)
        self._plot_bin_packing_2d(bins, ax)
        plt.title(title)
        plt.tight_layout()
        plt.show()
    
    def plot_efficiency_comparison(self, results: Dict[str, Tuple[List[Bin], float]]) -> None:
        """Compare efficiency of different algorithms"""
        algorithms = list(results.keys())
        efficiencies = []
        execution_times = []
        
        for algorithm, (bins, exec_time) in results.items():
            total_capacity = sum(bin.capacity for bin in bins)
            total_used = sum(bin.get_used_capacity() for bin in bins)
            efficiency = (total_used / total_capacity * 100) if total_capacity > 0 else 0
            efficiencies.append(efficiency)
            execution_times.append(exec_time)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Efficiency comparison
        bars1 = ax1.bar(algorithms, efficiencies, color='lightblue', alpha=0.7)
        ax1.set_ylabel('Efficiency (%)')
        ax1.set_title('Algorithm Efficiency Comparison')
        ax1.set_ylim(0, 100)
        
        for bar, eff in zip(bars1, efficiencies):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{eff:.1f}%', ha='center', va='bottom')
        
        # Execution time comparison
        bars2 = ax2.bar(algorithms, execution_times, color='lightcoral', alpha=0.7)
        ax2.set_ylabel('Execution Time (s)')
        ax2.set_title('Algorithm Speed Comparison')
        
        for bar, time in zip(bars2, execution_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{time:.3f}s', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def save_visualization(self, filename: str, dpi: int = 300) -> None:
        """Save current visualization to file"""
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')