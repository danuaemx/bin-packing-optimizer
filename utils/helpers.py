"""
Helper utility functions
"""

import time
import uuid
import hashlib
from typing import Any, List, Dict, Union
from datetime import datetime, timedelta


def format_size(size: Union[int, float], unit: str = "units") -> str:
    """Format size with appropriate unit"""
    if size >= 1000000:
        return f"{size/1000000:.2f}M {unit}"
    elif size >= 1000:
        return f"{size/1000:.2f}K {unit}"
    else:
        return f"{size:.2f} {unit}"


def format_time(seconds: float) -> str:
    """Format time duration in human readable format"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def calculate_efficiency(used_capacity: float, total_capacity: float) -> float:
    """Calculate packing efficiency percentage"""
    if total_capacity == 0:
        return 0.0
    return (used_capacity / total_capacity) * 100


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique identifier"""
    unique_id = str(uuid.uuid4()).replace('-', '')[:length]
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_hash(data: str) -> str:
    """Generate MD5 hash of data"""
    return hashlib.md5(data.encode()).hexdigest()


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten a nested list"""
    return [item for sublist in nested_list for item in sublist]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division that returns default value for division by zero"""
    return numerator / denominator if denominator != 0 else default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))


def percentage_to_float(percentage: str) -> float:
    """Convert percentage string to float (e.g., '85%' -> 0.85)"""
    if isinstance(percentage, str) and percentage.endswith('%'):
        return float(percentage[:-1]) / 100
    return float(percentage)


def float_to_percentage(value: float, decimal_places: int = 2) -> str:
    """Convert float to percentage string"""
    return f"{value * 100:.{decimal_places}f}%"


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def __str__(self) -> str:
        return f"{self.description}: {format_time(self.elapsed)}"


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1) -> None:
        """Update progress"""
        self.current = min(self.current + increment, self.total)
    
    def set_progress(self, current: int) -> None:
        """Set absolute progress"""
        self.current = clamp(current, 0, self.total)
    
    @property
    def percentage(self) -> float:
        """Get completion percentage"""
        return safe_divide(self.current, self.total) * 100
    
    @property
    def eta(self) -> str:
        """Estimate time to completion"""
        if self.current == 0:
            return "Unknown"
        
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed
        remaining = (self.total - self.current) / rate if rate > 0 else 0
        
        return format_time(remaining)
    
    def __str__(self) -> str:
        bar_length = 30
        filled_length = int(bar_length * self.current / self.total) if self.total > 0 else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        return f"{self.description}: |{bar}| {self.current}/{self.total} ({self.percentage:.1f}%) ETA: {self.eta}"


def memory_usage() -> Dict[str, float]:
    """Get current memory usage information"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent()
    }


def benchmark_function(func, *args, iterations: int = 1, **kwargs) -> Dict[str, Any]:
    """Benchmark a function's performance"""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        times.append(end - start)
    
    return {
        'min_time': min(times),
        'max_time': max(times),
        'avg_time': sum(times) / len(times),
        'total_time': sum(times),
        'iterations': iterations,
        'result': result if iterations == 1 else None
    }