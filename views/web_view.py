"""
Web view for creating HTML output and web interfaces
"""

import json
from typing import Any, Dict, List
from datetime import datetime
from .base_view import BaseView
from models.bin import Bin
from models.item import Item


class WebView(BaseView):
    """Web-based view for HTML output"""
    
    def __init__(self, template_dir: str = "templates"):
        super().__init__()
        self.template_dir = template_dir
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render data as HTML"""
        return self.generate_html_report(data)
    
    def display_results(self, bins: List[Bin], items: List[Item], 
                       algorithm: str, execution_time: float) -> str:
        """Generate HTML report of results"""
        
        # Calculate statistics
        total_capacity = sum(bin.capacity for bin in bins)
        total_used = sum(bin.get_used_capacity() for bin in bins)
        efficiency = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        
        used_items = set()
        for bin in bins:
            used_items.update(item.name for item in bin.items)
        unused_items = [item for item in items if item.name not in used_items]
        
        data = {
            'algorithm': algorithm,
            'execution_time': execution_time,
            'total_items': len(items),
            'bins_used': len(bins),
            'total_capacity': total_capacity,
            'used_capacity': total_used,
            'efficiency': efficiency,
            'bins': bins,
            'unused_items': unused_items,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.generate_html_report(data)
    
    def generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate complete HTML report"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bin Packing Optimization Report</title>
    <style>
        {css_styles}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>Bin Packing Optimization Report</h1>
            <p class="timestamp">Generated on: {timestamp}</p>
        </header>
        
        <section class="summary">
            <h2>Summary</h2>
            <div class="stats-grid">
                {summary_stats}
            </div>
        </section>
        
        <section class="visualization">
            <h2>Visualization</h2>
            <div id="binChart"></div>
            <div id="utilizationChart"></div>
        </section>
        
        <section class="details">
            <h2>Bin Details</h2>
            {bin_details}
        </section>
        
        {unused_items_section}
    </div>
    
    <script>
        {javascript_code}
    </script>
</body>
</html>
"""
        
        css_styles = self._get_css_styles()
        summary_stats = self._generate_summary_stats(data)
        bin_details = self._generate_bin_details(data.get('bins', []))
        unused_items_section = self._generate_unused_items_section(data.get('unused_items', []))
        javascript_code = self._generate_javascript(data)
        
        return html_template.format(
            css_styles=css_styles,
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            summary_stats=summary_stats,
            bin_details=bin_details,
            unused_items_section=unused_items_section,
            javascript_code=javascript_code
        )
    
    def _get_css_styles(self) -> str:
        """Return CSS styles for the HTML report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .timestamp {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        section {
            background: white;
            margin-bottom: 2rem;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h2 {
            color: #4a5568;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
            border-bottom: 3px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        .bin-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 5px;
        }
        
        .bin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .bin-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #4a5568;
        }
        
        .utilization {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }
        
        .utilization.high { background: #48bb78; }
        .utilization.medium { background: #ed8936; }
        .utilization.low { background: #f56565; }
        
        .items-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .item-tag {
            background: #e2e8f0;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.9rem;
            color: #4a5568;
        }
        
        .unused-items {
            background: #fed7d7;
            border-left: 4px solid #f56565;
            padding: 1.5rem;
            border-radius: 5px;
        }
        
        .chart-container {
            margin: 2rem 0;
            height: 400px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            header h1 {
                font-size: 2rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _generate_summary_stats(self, data: Dict[str, Any]) -> str:
        """Generate summary statistics HTML"""
        stats = [
            ("Algorithm", data.get('algorithm', 'N/A')),
            ("Execution Time", self.format_time(data.get('execution_time', 0))),
            ("Total Items", data.get('total_items', 0)),
            ("Bins Used", data.get('bins_used', 0)),
            ("Efficiency", self.format_efficiency(data.get('efficiency', 0))),
            ("Total Capacity", data.get('total_capacity', 0))
        ]
        
        html = ""
        for label, value in stats:
            html += f"""
            <div class="stat-card">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """
        
        return html
    
    def _generate_bin_details(self, bins: List[Bin]) -> str:
        """Generate bin details HTML"""
        if not bins:
            return "<p>No bins to display.</p>"
        
        html = ""
        for i, bin in enumerate(bins, 1):
            used = bin.get_used_capacity()
            utilization = (used / bin.capacity * 100) if bin.capacity > 0 else 0
            
            utilization_class = "high" if utilization >= 80 else "medium" if utilization >= 60 else "low"
            
            items_html = ""
            for item in bin.items:
                items_html += f'<span class="item-tag">{item.name} ({item.size})</span>'
            
            html += f"""
            <div class="bin-card">
                <div class="bin-header">
                    <div class="bin-title">Bin {i}</div>
                    <div class="utilization {utilization_class}">{utilization:.1f}%</div>
                </div>
                <div class="bin-info">
                    <p><strong>Capacity:</strong> {bin.capacity}</p>
                    <p><strong>Used:</strong> {used}</p>
                    <p><strong>Remaining:</strong> {bin.get_remaining_capacity()}</p>
                    <p><strong>Items:</strong> {len(bin.items)}</p>
                </div>
                <div class="items-list">
                    {items_html}
                </div>
            </div>
            """
        
        return html
    
    def _generate_unused_items_section(self, unused_items: List) -> str:
        """Generate unused items section HTML"""
        if not unused_items:
            return ""
        
        items_html = ""
        for item in unused_items:
            items_html += f'<span class="item-tag">{item.name} ({item.size})</span>'
        
        return f"""
        <section class="unused-items">
            <h2 style="color: #f56565; border-color: #f56565;">Unused Items</h2>
            <div class="items-list">
                {items_html}
            </div>
        </section>
        """
    
    def _generate_javascript(self, data: Dict[str, Any]) -> str:
        """Generate JavaScript for interactive charts"""
        bins = data.get('bins', [])
        if not bins:
            return ""
        
        # Prepare data for charts
        bin_labels = [f'Bin {i+1}' for i in range(len(bins))]
        utilizations = []
        capacities = []
        used_capacities = []
        
        for bin in bins:
            used = bin.get_used_capacity()
            utilization = (used / bin.capacity * 100) if bin.capacity > 0 else 0
            utilizations.append(utilization)
            capacities.append(bin.capacity)
            used_capacities.append(used)
        
        return f"""
        // Bin utilization chart
        var utilizationData = [{{
            x: {json.dumps(bin_labels)},
            y: {json.dumps(utilizations)},
            type: 'bar',
            marker: {{
                color: {json.dumps(['#ff6b6b' if u < 70 else '#4ecdc4' if u < 90 else '#45b7d1' for u in utilizations])}
            }},
            name: 'Utilization %'
        }}];
        
        var utilizationLayout = {{
            title: 'Bin Utilization',
            xaxis: {{ title: 'Bins' }},
            yaxis: {{ title: 'Utilization (%)' }},
            showlegend: false
        }};
        
        Plotly.newPlot('utilizationChart', utilizationData, utilizationLayout);
        
        // Capacity vs Used chart
        var capacityData = [
            {{
                x: {json.dumps(bin_labels)},
                y: {json.dumps(capacities)},
                type: 'bar',
                name: 'Total Capacity',
                marker: {{ color: '#e0e0e0' }}
            }},
            {{
                x: {json.dumps(bin_labels)},
                y: {json.dumps(used_capacities)},
                type: 'bar',
                name: 'Used Capacity',
                marker: {{ color: '#667eea' }}
            }}
        ];
        
        var capacityLayout = {{
            title: 'Capacity vs Used Space',
            xaxis: {{ title: 'Bins' }},
            yaxis: {{ title: 'Capacity' }},
            barmode: 'overlay'
        }};
        
        Plotly.newPlot('binChart', capacityData, capacityLayout);
        """
    
    def save_html_report(self, filename: str, data: Dict[str, Any]) -> None:
        """Save HTML report to file"""
        html_content = self.generate_html_report(data)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)