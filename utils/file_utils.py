"""
File I/O utilities for bin packing data
"""

import json
import csv
import pickle
import os
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import pandas as pd
from models.item import Item
from models.bin import Bin
from utils.validators import ValidationError, validate_file_path
from config.logging_config import get_logger

logger = get_logger('file_utils')


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_items_from_json(file_path: str) -> List[Item]:
    """Load items from JSON file"""
    validate_file_path(file_path, must_exist=True, extension='.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = []
        if isinstance(data, list):
            for item_data in data:
                if isinstance(item_data, dict):
                    items.append(Item(**item_data))
                else:
                    raise ValidationError(f"Invalid item data format: {item_data}")
        elif isinstance(data, dict) and 'items' in data:
            for item_data in data['items']:
                items.append(Item(**item_data))
        else:
            raise ValidationError("JSON must contain list of items or dict with 'items' key")
        
        logger.info(f"Loaded {len(items)} items from {file_path}")
        return items
    
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON file: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Error loading items from JSON: {str(e)}")


def save_items_to_json(items: List[Item], file_path: str) -> None:
    """Save items to JSON file"""
    ensure_directory(Path(file_path).parent)
    
    try:
        items_data = []
        for item in items:
            item_dict = {
                'name': item.name,
                'size': item.size
            }
            if hasattr(item, 'weight') and item.weight is not None:
                item_dict['weight'] = item.weight
            if hasattr(item, 'priority') and item.priority is not None:
                item_dict['priority'] = item.priority
            
            items_data.append(item_dict)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(items)} items to {file_path}")
    
    except Exception as e:
        raise ValidationError(f"Error saving items to JSON: {str(e)}")


def load_items_from_csv(file_path: str, name_col: str = 'name', size_col: str = 'size') -> List[Item]:
    """Load items from CSV file"""
    validate_file_path(file_path, must_exist=True, extension='.csv')
    
    try:
        df = pd.read_csv(file_path)
        
        if name_col not in df.columns:
            raise ValidationError(f"Name column '{name_col}' not found in CSV")
        if size_col not in df.columns:
            raise ValidationError(f"Size column '{size_col}' not found in CSV")
        
        items = []
        for _, row in df.iterrows():
            item_kwargs = {
                'name': str(row[name_col]),
                'size': float(row[size_col])
            }
            
            # Add optional fields if they exist
            if 'weight' in df.columns and pd.notna(row['weight']):
                item_kwargs['weight'] = float(row['weight'])
            if 'priority' in df.columns and pd.notna(row['priority']):
                item_kwargs['priority'] = float(row['priority'])
            
            items.append(Item(**item_kwargs))
        
        logger.info(f"Loaded {len(items)} items from {file_path}")
        return items
    
    except Exception as e:
        raise ValidationError(f"Error loading items from CSV: {str(e)}")


def save_items_to_csv(items: List[Item], file_path: str) -> None:
    """Save items to CSV file"""
    ensure_directory(Path(file_path).parent)
    
    try:
        data = []
        for item in items:
            row = {
                'name': item.name,
                'size': item.size
            }
            if hasattr(item, 'weight') and item.weight is not None:
                row['weight'] = item.weight
            if hasattr(item, 'priority') and item.priority is not None:
                row['priority'] = item.priority
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        
        logger.info(f"Saved {len(items)} items to {file_path}")
    
    except Exception as e:
        raise ValidationError(f"Error saving items to CSV: {str(e)}")


def load_items_from_excel(file_path: str, sheet_name: str = 0, name_col: str = 'name', size_col: str = 'size') -> List[Item]:
    """Load items from Excel file"""
    validate_file_path(file_path, must_exist=True)
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        if name_col not in df.columns:
            raise ValidationError(f"Name column '{name_col}' not found in Excel sheet")
        if size_col not in df.columns:
            raise ValidationError(f"Size column '{size_col}' not found in Excel sheet")
        
        items = []
        for _, row in df.iterrows():
            item_kwargs = {
                'name': str(row[name_col]),
                'size': float(row[size_col])
            }
            
            # Add optional fields if they exist
            if 'weight' in df.columns and pd.notna(row['weight']):
                item_kwargs['weight'] = float(row['weight'])
            if 'priority' in df.columns and pd.notna(row['priority']):
                item_kwargs['priority'] = float(row['priority'])
            
            items.append(Item(**item_kwargs))
        
        logger.info(f"Loaded {len(items)} items from {file_path}")
        return items
    
    except Exception as e:
        raise ValidationError(f"Error loading items from Excel: {str(e)}")


def save_results_to_file(bins: List[Bin], file_path: str, format: str = 'json', metadata: Optional[Dict] = None) -> None:
    """Save bin packing results to file"""
    ensure_directory(Path(file_path).parent)
    
    # Prepare data
    results_data = {
        'metadata': metadata or {},
        'bins': [],
        'summary': {
            'total_bins': len(bins),
            'total_capacity': sum(bin.capacity for bin in bins),
            'used_capacity': sum(bin.get_used_capacity() for bin in bins),
            'efficiency': 0.0
        }
    }
    
    # Calculate efficiency
    if results_data['summary']['total_capacity'] > 0:
        results_data['summary']['efficiency'] = (
            results_data['summary']['used_capacity'] / 
            results_data['summary']['total_capacity'] * 100
        )
    
    # Add bin details
    for i, bin in enumerate(bins):
        bin_data = {
            'id': i + 1,
            'capacity': bin.capacity,
            'used_capacity': bin.get_used_capacity(),
            'remaining_capacity': bin.get_remaining_capacity(),
            'utilization': (bin.get_used_capacity() / bin.capacity * 100) if bin.capacity > 0 else 0,
            'items': [{'name': item.name, 'size': item.size} for item in bin.items]
        }
        results_data['bins'].append(bin_data)
    
    # Save based on format
    try:
        if format.lower() == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == 'pickle':
            with open(file_path, 'wb') as f:
                pickle.dump(results_data, f)
        
        elif format.lower() == 'csv':
            # Flatten data for CSV
            csv_data = []
            for bin_data in results_data['bins']:
                for item in bin_data['items']:
                    csv_data.append({
                        'bin_id': bin_data['id'],
                        'bin_capacity': bin_data['capacity'],
                        'bin_utilization': bin_data['utilization'],
                        'item_name': item['name'],
                        'item_size': item['size']
                    })
            
            df = pd.DataFrame(csv_data)
            df.to_csv(file_path, index=False)
        
        else:
            raise ValidationError(f"Unsupported format: {format}")
        
        logger.info(f"Saved results to {file_path} in {format} format")
    
    except Exception as e:
        raise ValidationError(f"Error saving results: {str(e)}")


def export_to_excel(data: Dict[str, Any], file_path: str, include_charts: bool = True) -> None:
    """Export results to Excel with multiple sheets and optional charts"""
    ensure_directory(Path(file_path).parent)
    
    try:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Bins', 'Total Capacity', 'Used Capacity', 'Efficiency (%)'],
                'Value': [
                    data.get('total_bins', 0),
                    data.get('total_capacity', 0),
                    data.get('used_capacity', 0),
                    data.get('efficiency', 0)
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Bins detail sheet
            bins_data = []
            for bin_data in data.get('bins', []):
                bins_data.append({
                    'Bin ID': bin_data['id'],
                    'Capacity': bin_data['capacity'],
                    'Used Capacity': bin_data['used_capacity'],
                    'Remaining Capacity': bin_data['remaining_capacity'],
                    'Utilization (%)': bin_data['utilization'],
                    'Item Count': len(bin_data['items'])
                })
            
            if bins_data:
                pd.DataFrame(bins_data).to_excel(writer, sheet_name='Bins', index=False)
            
            # Items detail sheet
            items_data = []
            for bin_data in data.get('bins', []):
                for item in bin_data['items']:
                    items_data.append({
                        'Bin ID': bin_data['id'],
                        'Item Name': item['name'],
                        'Item Size': item['size'],
                        'Bin Capacity': bin_data['capacity'],
                        'Bin Utilization (%)': bin_data['utilization']
                    })
            
            if items_data:
                pd.DataFrame(items_data).to_excel(writer, sheet_name='Items', index=False)
        
        logger.info(f"Exported results to Excel: {file_path}")
    
    except Exception as e:
        raise ValidationError(f"Error exporting to Excel: {str(e)}")


def backup_file(file_path: str, backup_dir: str = 'backups') -> str:
    """Create backup of existing file"""
    if not os.path.exists(file_path):
        return None
    
    backup_path = ensure_directory(backup_dir)
    file_name = Path(file_path).name
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_path / f"{timestamp}_{file_name}"
    
    import shutil
    shutil.copy2(file_path, backup_file)
    
    logger.info(f"Created backup: {backup_file}")
    return str(backup_file)


def cleanup_old_files(directory: str, max_age_days: int = 30, pattern: str = "*") -> int:
    """Clean up old files in directory"""
    import time
    
    directory_path = Path(directory)
    if not directory_path.exists():
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    deleted_count = 0
    
    for file_path in directory_path.glob(pattern):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                file_path.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old file: {file_path}")
    
    logger.info(f"Cleaned up {deleted_count} old files from {directory}")
    return deleted_count


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get detailed file information"""
    path = Path(file_path)
    
    if not path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    stat = path.stat()
    
    return {
        'name': path.name,
        'size_bytes': stat.st_size,
        'size_mb': stat.st_size / (1024 * 1024),
        'created': pd.Timestamp.fromtimestamp(stat.st_ctime),
        'modified': pd.Timestamp.fromtimestamp(stat.st_mtime),
        'extension': path.suffix,
        'is_file': path.is_file(),
        'is_directory': path.is_dir(),
        'parent': str(path.parent)
    }