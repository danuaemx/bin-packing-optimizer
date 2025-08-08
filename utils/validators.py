"""
Validation utilities for bin packing data
"""

import re
from typing import Any, List, Dict, Union, Optional, Tuple
from models.item import Item
from models.bin import Bin


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_positive_number(value: Union[int, float], name: str = "value") -> Union[int, float]:
    """Validate that a number is positive"""
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be a number, got {type(value).__name__}")
    
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")
    
    return value


def validate_non_negative_number(value: Union[int, float], name: str = "value") -> Union[int, float]:
    """Validate that a number is non-negative"""
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be a number, got {type(value).__name__}")
    
    if value < 0:
        raise ValidationError(f"{name} must be non-negative, got {value}")
    
    return value


def validate_string(value: str, name: str = "value", min_length: int = 1, max_length: int = None) -> str:
    """Validate string with length constraints"""
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string, got {type(value).__name__}")
    
    if len(value) < min_length:
        raise ValidationError(f"{name} must be at least {min_length} characters long")
    
    if max_length and len(value) > max_length:
        raise ValidationError(f"{name} must be at most {max_length} characters long")
    
    return value.strip()


def validate_item(item: Item) -> Item:
    """Validate an Item object"""
    if not isinstance(item, Item):
        raise ValidationError(f"Expected Item object, got {type(item).__name__}")
    
    # Validate name
    validate_string(item.name, "Item name", min_length=1, max_length=100)
    
    # Validate size
    validate_positive_number(item.size, "Item size")
    
    # Validate weight if present
    if hasattr(item, 'weight') and item.weight is not None:
        validate_non_negative_number(item.weight, "Item weight")
    
    # Validate priority if present
    if hasattr(item, 'priority') and item.priority is not None:
        validate_non_negative_number(item.priority, "Item priority")
    
    return item


def validate_bin(bin: Bin) -> Bin:
    """Validate a Bin object"""
    if not isinstance(bin, Bin):
        raise ValidationError(f"Expected Bin object, got {type(bin).__name__}")
    
    # Validate capacity
    validate_positive_number(bin.capacity, "Bin capacity")
    
    # Validate name if present
    if hasattr(bin, 'name') and bin.name is not None:
        validate_string(bin.name, "Bin name", min_length=1, max_length=100)
    
    # Validate items in bin
    if hasattr(bin, 'items') and bin.items:
        for item in bin.items:
            validate_item(item)
        
        # Check if total size exceeds capacity
        total_size = sum(item.size for item in bin.items)
        if total_size > bin.capacity:
            raise ValidationError(f"Total item size ({total_size}) exceeds bin capacity ({bin.capacity})")
    
    return bin


def validate_items_list(items: List[Item]) -> List[Item]:
    """Validate a list of items"""
    if not isinstance(items, list):
        raise ValidationError(f"Expected list of items, got {type(items).__name__}")
    
    if not items:
        raise ValidationError("Items list cannot be empty")
    
    validated_items = []
    item_names = set()
    
    for i, item in enumerate(items):
        try:
            validated_item = validate_item(item)
            
            # Check for duplicate names
            if validated_item.name in item_names:
                raise ValidationError(f"Duplicate item name: {validated_item.name}")
            
            item_names.add(validated_item.name)
            validated_items.append(validated_item)
            
        except ValidationError as e:
            raise ValidationError(f"Item {i}: {str(e)}")
    
    return validated_items


def validate_bins_list(bins: List[Bin]) -> List[Bin]:
    """Validate a list of bins"""
    if not isinstance(bins, list):
        raise ValidationError(f"Expected list of bins, got {type(bins).__name__}")
    
    if not bins:
        raise ValidationError("Bins list cannot be empty")
    
    validated_bins = []
    
    for i, bin in enumerate(bins):
        try:
            validated_bin = validate_bin(bin)
            validated_bins.append(validated_bin)
        except ValidationError as e:
            raise ValidationError(f"Bin {i}: {str(e)}")
    
    return validated_bins


def validate_algorithm_name(algorithm: str) -> str:
    """Validate algorithm name"""
    valid_algorithms = [
        'first_fit', 'best_fit', 'worst_fit', 'next_fit',
        'first_fit_decreasing', 'best_fit_decreasing', 'worst_fit_decreasing',
        'genetic', 'simulated_annealing', 'greedy'
    ]
    
    algorithm = validate_string(algorithm, "Algorithm name").lower()
    
    if algorithm not in valid_algorithms:
        raise ValidationError(f"Unknown algorithm: {algorithm}. Valid algorithms: {', '.join(valid_algorithms)}")
    
    return algorithm


def validate_file_path(file_path: str, must_exist: bool = True, extension: str = None) -> str:
    """Validate file path"""
    import os
    
    file_path = validate_string(file_path, "File path")
    
    if must_exist and not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    if extension:
        if not file_path.lower().endswith(extension.lower()):
            raise ValidationError(f"File must have {extension} extension")
    
    return file_path


def validate_email(email: str) -> str:
    """Validate email address format"""
    email = validate_string(email, "Email")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    
    return email.lower()


def validate_url(url: str) -> str:
    """Validate URL format"""
    url = validate_string(url, "URL")
    
    url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    
    if not re.match(url_pattern, url):
        raise ValidationError(f"Invalid URL format: {url}")
    
    return url


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration dictionary"""
    if not isinstance(config, dict):
        raise ValidationError(f"Config must be a dictionary, got {type(config).__name__}")
    
    # Define required and optional config keys with their validators
    config_schema = {
        'algorithm': (str, True, validate_algorithm_name),
        'max_iterations': (int, False, lambda x: validate_positive_number(x, "max_iterations")),
        'timeout': (float, False, lambda x: validate_positive_number(x, "timeout")),
        'output_format': (str, False, lambda x: validate_string(x, "output_format")),
        'log_level': (str, False, lambda x: validate_string(x, "log_level")),
    }
    
    validated_config = {}
    
    # Check required keys
    for key, (expected_type, required, validator) in config_schema.items():
        if required and key not in config:
            raise ValidationError(f"Required config key missing: {key}")
        
        if key in config:
            value = config[key]
            
            # Type check
            if not isinstance(value, expected_type):
                raise ValidationError(f"Config key '{key}' must be {expected_type.__name__}, got {type(value).__name__}")
            
            # Custom validation
            try:
                validated_config[key] = validator(value)
            except ValidationError as e:
                raise ValidationError(f"Config key '{key}': {str(e)}")
    
    # Add any additional keys that aren't in schema
    for key, value in config.items():
        if key not in config_schema:
            validated_config[key] = value
    
    return validated_config


def validate_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], name: str = "value") -> Union[int, float]:
    """Validate that a value is within a specified range"""
    validate_positive_number(value, name)
    
    if value < min_val or value > max_val:
        raise ValidationError(f"{name} must be between {min_val} and {max_val}, got {value}")
    
    return value


def validate_percentage(value: Union[int, float], name: str = "percentage") -> float:
    """Validate percentage value (0-100)"""
    return validate_range(value, 0, 100, name)


class DataValidator:
    """Class for batch validation operations"""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, error: str) -> None:
        """Add validation error"""
        self.errors.append(error)
    
    def validate_item_safe(self, item: Item, index: int = None) -> bool:
        """Validate item and collect errors instead of raising"""
        try:
            validate_item(item)
            return True
        except ValidationError as e:
            error_msg = f"Item {index}: {str(e)}" if index is not None else str(e)
            self.add_error(error_msg)
            return False
    
    def validate_bin_safe(self, bin: Bin, index: int = None) -> bool:
        """Validate bin and collect errors instead of raising"""
        try:
            validate_bin(bin)
            return True
        except ValidationError as e:
            error_msg = f"Bin {index}: {str(e)}" if index is not None else str(e)
            self.add_error(error_msg)
            return False
    
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors"""
        return self.errors.copy()
    
    def clear_errors(self) -> None:
        """Clear all validation errors"""
        self.errors.clear()
    
    def raise_if_errors(self) -> None:
        """Raise ValidationError if there are any errors"""
        if self.has_errors():
            error_msg = "Validation failed:\n" + "\n".join(self.errors)
            raise ValidationError(error_msg)