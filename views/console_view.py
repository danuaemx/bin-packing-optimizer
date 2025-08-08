"""
Console view for displaying results in terminal
"""

import os
from typing import Any, Dict, List
from colorama import Fore, Back, Style, init
from .base_view import BaseView
from models.bin import Bin
from models.item import Item

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ConsoleView(BaseView):
    """Console-based view for terminal output"""
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        return hasattr(os.sys.stdout, 'isatty') and os.sys.stdout.isatty()
    
    def _colorize(self, text: str, color: str = Fore.WHITE) -> str:
        """Apply color to text if colors are enabled"""
        if self.use_colors:
            return f"{color}{text}{Style.RESET_ALL}"
        return text
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render data to console"""
        print(self._colorize("=" * 60, Fore.CYAN))
        print(self._colorize("BIN PACKING OPTIMIZATION RESULTS", Fore.CYAN))
        print(self._colorize("=" * 60, Fore.CYAN))
        
        for key, value in data.items():
            print(f"{self._colorize(key.capitalize(), Fore.YELLOW)}: {value}")
    
    def display_results(self, bins: List[Bin], items: List[Item], 
                       algorithm: str, execution_time: float) -> None:
        """Display optimization results in console"""
        
        # Header
        print("\n" + self._colorize("=" * 70, Fore.CYAN))
        print(self._colorize("BIN PACKING OPTIMIZATION RESULTS", Fore.CYAN))
        print(self._colorize("=" * 70, Fore.CYAN))
        
        # Algorithm info
        print(f"\n{self._colorize('Algorithm:', Fore.YELLOW)} {algorithm}")
        print(f"{self._colorize('Execution Time:', Fore.YELLOW)} {self.format_time(execution_time)}")
        print(f"{self._colorize('Total Items:', Fore.YELLOW)} {len(items)}")
        print(f"{self._colorize('Bins Used:', Fore.YELLOW)} {len(bins)}")
        
        # Calculate statistics
        total_capacity = sum(bin.capacity for bin in bins)
        total_used = sum(bin.get_used_capacity() for bin in bins)
        efficiency = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        
        print(f"{self._colorize('Total Capacity:', Fore.YELLOW)} {total_capacity}")
        print(f"{self._colorize('Used Capacity:', Fore.YELLOW)} {total_used}")
        print(f"{self._colorize('Efficiency:', Fore.YELLOW)} {self.format_efficiency(efficiency)}")
        
        # Bin details
        print(f"\n{self._colorize('BIN DETAILS:', Fore.GREEN)}")
        print(self._colorize("-" * 50, Fore.GREEN))
        
        for i, bin in enumerate(bins, 1):
            used = bin.get_used_capacity()
            remaining = bin.get_remaining_capacity()
            bin_efficiency = (used / bin.capacity * 100) if bin.capacity > 0 else 0
            
            print(f"\n{self._colorize(f'Bin {i}:', Fore.BLUE)}")
            print(f"  Capacity: {bin.capacity}")
            print(f"  Used: {used} ({self.format_efficiency(bin_efficiency)})")
            print(f"  Remaining: {remaining}")
            print(f"  Items: {len(bin.items)}")
            
            if bin.items:
                print(f"  Item details:")
                for item in bin.items:
                    print(f"    - {item.name}: {item.size}")
        
        # Unused items
        used_items = set()
        for bin in bins:
            used_items.update(item.name for item in bin.items)
        
        unused_items = [item for item in items if item.name not in used_items]
        
        if unused_items:
            print(f"\n{self._colorize('UNUSED ITEMS:', Fore.RED)}")
            print(self._colorize("-" * 30, Fore.RED))
            for item in unused_items:
                print(f"  - {item.name}: {item.size}")
        
        print(f"\n{self._colorize('=' * 70, Fore.CYAN)}")
    
    def display_progress(self, current: int, total: int, message: str = "") -> None:
        """Display progress bar"""
        if total == 0:
            return
            
        progress = current / total
        bar_length = 40
        filled_length = int(bar_length * progress)
        
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        percentage = progress * 100
        
        progress_text = f"\r{self._colorize('Progress:', Fore.YELLOW)} |{bar}| {percentage:.1f}% {message}"
        print(progress_text, end="", flush=True)
        
        if current == total:
            print()  # New line when complete
    
    def display_error(self, error_message: str) -> None:
        """Display error message"""
        print(f"\n{self._colorize('ERROR:', Fore.RED)} {error_message}")
    
    def display_warning(self, warning_message: str) -> None:
        """Display warning message"""
        print(f"\n{self._colorize('WARNING:', Fore.YELLOW)} {warning_message}")
    
    def display_success(self, success_message: str) -> None:
        """Display success message"""
        print(f"\n{self._colorize('SUCCESS:', Fore.GREEN)} {success_message}")