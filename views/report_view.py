"""
Report view for generating detailed reports in various formats
"""

import json
import csv
from datetime import datetime
from typing import Any, Dict, List, Optional
from .base_view import BaseView
from models.bin import Bin
from models.item import Item


class ReportView(BaseView):
    """View for generating detailed reports"""
    
    def __init__(self):
        super().__init__()
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render data as report"""
        print(self.generate_text_report(data))
    
    def display_results(self, bins: List[Bin], items: List[Item], 
                       algorithm: str, execution_time: float) -> None:
        """Display results as formatted report"""
        data = self._prepare_data(bins, items, algorithm, execution_time)
        print(self.generate_text_report(data))
    
    def _prepare_data(self, bins: List[Bin], items: List[Item], 
                     algorithm: str, execution_time: float) -> Dict[str, Any]:
        """Prepare data for report generation"""
        
        total_capacity = sum(bin.capacity for bin in bins)
        total_used = sum(bin.get_used_capacity() for bin in bins)
        efficiency = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        
        used_items = set()
        for bin in bins:
            used_items.update(item.name for item in bin.items)
        unused_items = [item for item in items if item.name not in used_items]
        
        return {
            'algorithm': algorithm,
            'execution_time': execution_time,
            'timestamp': datetime.now(),
            'total_items': len(items),
            'bins_used': len(bins),
            'total_capacity': total_capacity,
            'used_capacity': total_used,
            'efficiency': efficiency,
            'bins': bins,
            'items': items,
            'unused_items': unused_items
        }
    
    def generate_text_report(self, data: Dict[str, Any]) -> str:
        """Generate detailed text report"""
        
        report = []
        report.append("=" * 80)
        report.append("BIN PACKING OPTIMIZATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Report metadata
        timestamp = data.get('timestamp', datetime.now())
        report.append(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Algorithm: {data.get('algorithm', 'N/A')}")
        report.append(f"Execution Time: {self.format_time(data.get('execution_time', 0))}")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Items: {data.get('total_items', 0)}")
        report.append(f"Bins Used: {data.get('bins_used', 0)}")
        report.append(f"Total Capacity: {data.get('total_capacity', 0)}")
        report.append(f"Used Capacity: {data.get('used_capacity', 0)}")
        report.append(f"Efficiency: {self.format_efficiency(data.get('efficiency', 0))}")
        
        # Calculate additional statistics
        bins = data.get('bins', [])
        if bins:
            utilizations = [(bin.get_used_capacity() / bin.capacity * 100) 
                           for bin in bins if bin.capacity > 0]
            if utilizations:
                report.append(f"Average Bin Utilization: {sum(utilizations) / len(utilizations):.2f}%")
                report.append(f"Min Bin Utilization: {min(utilizations):.2f}%")
                report.append(f"Max Bin Utilization: {max(utilizations):.2f}%")
        
        report.append("")
        
        # Bin details
        report.append("BIN DETAILS")
        report.append("-" * 40)
        
        for i, bin in enumerate(bins, 1):
            used = bin.get_used_capacity()
            remaining = bin.get_remaining_capacity()
            utilization = (used / bin.capacity * 100) if bin.capacity > 0 else 0
            
            report.append(f"Bin {i}:")
            report.append(f"  Capacity: {bin.capacity}")
            report.append(f"  Used: {used} ({utilization:.1f}%)")
            report.append(f"  Remaining: {remaining}")
            report.append(f"  Items ({len(bin.items)}):")
            
            for item in bin.items:
                report.append(f"    - {item.name}: {item.size}")
            
            report.append("")
        
        # Unused items
        unused_items = data.get('unused_items', [])
        if unused_items:
            report.append("UNUSED ITEMS")
            report.append("-" * 40)
            for item in unused_items:
                report.append(f"  - {item.name}: {item.size}")
            report.append("")
        
        # Performance analysis
        report.append("PERFORMANCE ANALYSIS")
        report.append("-" * 40)
        
        efficiency = data.get('efficiency', 0)
        if efficiency >= 90:
            report.append("Excellent packing efficiency (≥90%)")
        elif efficiency >= 80:
            report.append("Good packing efficiency (80-89%)")
        elif efficiency >= 70:
            report.append("Moderate packing efficiency (70-79%)")
        else:
            report.append("Poor packing efficiency (<70%)")
        
        if bins:
            wasted_space = sum(bin.get_remaining_capacity() for bin in bins)
            report.append(f"Total wasted space: {wasted_space}")
            
            if len(unused_items) > 0:
                report.append(f"Items that couldn't be packed: {len(unused_items)}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_json_report(self, data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        
        # Prepare serializable data
        report_data = {
            'metadata': {
                'algorithm': data.get('algorithm'),
                'execution_time': data.get('execution_time'),
                'timestamp': data.get('timestamp', datetime.now()).isoformat(),
                'total_items': data.get('total_items'),
                'bins_used': data.get('bins_used')
            },
            'statistics': {
                'total_capacity': data.get('total_capacity'),
                'used_capacity': data.get('used_capacity'),
                'efficiency': data.get('efficiency'),
                'wasted_space': data.get('total_capacity', 0) - data.get('used_capacity', 0)
            },
            'bins': [],
            'unused_items': []
        }
        
        # Add bin details
        for i, bin in enumerate(data.get('bins', []), 1):
            bin_data = {
                'id': i,
                'capacity': bin.capacity,
                'used_capacity': bin.get_used_capacity(),
                'remaining_capacity': bin.get_remaining_capacity(),
                'utilization': (bin.get_used_capacity() / bin.capacity * 100) if bin.capacity > 0 else 0,
                'items': [{'name': item.name, 'size': item.size} for item in bin.items]
            }
            report_data['bins'].append(bin_data)
        
        # Add unused items
        for item in data.get('unused_items', []):
            report_data['unused_items'].append({
                'name': item.name,
                'size': item.size
            })
        
        return json.dumps(report_data, indent=2)
    
    def generate_csv_report(self, data: Dict[str, Any]) -> str:
        """Generate CSV report of bin contents"""
        
        output = []
        
        # Header
        output.append(['Bin ID', 'Bin Capacity', 'Item Name', 'Item Size', 'Bin Utilization %'])
        
        # Bin data
        for i, bin in enumerate(data.get('bins', []), 1):
            utilization = (bin.get_used_capacity() / bin.capacity * 100) if bin.capacity > 0 else 0
            
            if bin.items:
                for item in bin.items:
                    output.append([i, bin.capacity, item.name, item.size, f"{utilization:.2f}"])
            else:
                output.append([i, bin.capacity, '', '', f"{utilization:.2f}"])
        
        # Convert to CSV string
        import io
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(output)
        return csv_buffer.getvalue()
    
    def save_report(self, data: Dict[str, Any], filename: str, format: str = 'txt') -> None:
        """Save report to file in specified format"""
        
        if format.lower() == 'json':
            content = self.generate_json_report(data)
        elif format.lower() == 'csv':
            content = self.generate_csv_report(data)
        else:
            content = self.generate_text_report(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def compare_algorithms(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Generate comparison report for multiple algorithms"""
        
        report = []
        report.append("=" * 80)
        report.append("ALGORITHM COMPARISON REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Create comparison table
        algorithms = list(results.keys())
        
        report.append(f"{'Algorithm':<20} {'Bins':<8} {'Efficiency':<12} {'Time':<12} {'Unused Items':<12}")
        report.append("-" * 70)
        
        for algorithm in algorithms:
            data = results[algorithm]
            efficiency = data.get('efficiency', 0)
            execution_time = data.get('execution_time', 0)
            bins_used = data.get('bins_used', 0)
            unused_count = len(data.get('unused_items', []))
            
            report.append(f"{algorithm:<20} {bins_used:<8} {efficiency:<11.1f}% {execution_time:<11.3f}s {unused_count:<12}")
        
        report.append("")
        
        # Find best algorithm for each metric
        best_efficiency = max(results.items(), key=lambda x: x[1].get('efficiency', 0))
        best_speed = min(results.items(), key=lambda x: x[1].get('execution_time', float('inf')))
        best_bins = min(results.items(), key=lambda x: x[1].get('bins_used', float('inf')))
        
        report.append("BEST PERFORMERS:")
        report.append(f"Best Efficiency: {best_efficiency[0]} ({best_efficiency[1].get('efficiency', 0):.1f}%)")
        report.append(f"Fastest: {best_speed[0]} ({best_speed[1].get('execution_time', 0):.3f}s)")
        report.append(f"Fewest Bins: {best_bins[0]} ({best_bins[1].get('bins_used', 0)} bins)")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)