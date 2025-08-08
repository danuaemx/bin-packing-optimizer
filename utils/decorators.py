"""
Utility decorators for common functionality
"""

import time
import functools
from typing import Any, Callable, Dict, Optional
from config.logging_config import get_logger


def timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger = get_logger('performance')
            logger.debug(f"{func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger = get_logger('performance')
            logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {str(e)}")
            raise
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator to retry function on failure"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger('retry')
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {str(e)}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            
            raise last_exception
        return wrapper
    return decorator


def cache_result(maxsize: int = 128, ttl: Optional[float] = None):
    """Decorator to cache function results with optional TTL"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check if result is cached and still valid
            if key in cache:
                if ttl is None or (time.time() - cache_times[key]) < ttl:
                    return cache[key]
                else:
                    # Remove expired entry
                    del cache[key]
                    del cache_times[key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Implement LRU eviction if cache is full
            if len(cache) >= maxsize:
                # Remove oldest entry
                oldest_key = min(cache_times.keys(), key=lambda k: cache_times[k])
                del cache[oldest_key]
                del cache_times[oldest_key]
            
            cache[key] = result
            cache_times[key] = time.time()
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: (cache.clear(), cache_times.clear())
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'maxsize': maxsize,
            'hits': getattr(wrapper, '_hits', 0),
            'misses': getattr(wrapper, '_misses', 0)
        }
        
        return wrapper
    return decorator


def log_calls(level: str = 'DEBUG', include_args: bool = True, include_result: bool = False):
    """Decorator to log function calls"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger('calls')
            
            # Prepare log message
            msg_parts = [f"Calling {func.__name__}"]
            
            if include_args and (args or kwargs):
                args_str = ', '.join(str(arg) for arg in args)
                kwargs_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
                all_args = ', '.join(filter(None, [args_str, kwargs_str]))
                msg_parts.append(f"with args: {all_args}")
            
            # Log the call
            getattr(logger, level.lower())(' '.join(msg_parts))
            
            try:
                result = func(*args, **kwargs)
                
                if include_result:
                    getattr(logger, level.lower())(f"{func.__name__} returned: {result}")
                
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator


def validate_types(**type_checks):
    """Decorator to validate function argument types"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate types
            for param_name, expected_type in type_checks.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if value is not None and not isinstance(value, expected_type):
                        raise TypeError(
                            f"Parameter '{param_name}' must be of type {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls):
    """Decorator to create singleton classes"""
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


def deprecated(reason: str = "This function is deprecated"):
    """Decorator to mark functions as deprecated"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(calls_per_second: float):
    """Decorator to rate limit function calls"""
    min_interval = 1.0 / calls_per_second
    last_called = 0.0
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_called
            
            current_time = time.time()
            time_since_last = current_time - last_called
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                time.sleep(sleep_time)
            
            last_called = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def async_to_sync(func: Callable) -> Callable:
    """Decorator to run async functions synchronously"""
    import asyncio
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    
    return wrapper


def benchmark(iterations: int = 1):
    """Decorator to benchmark function performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            times = []
            result = None
            
            for i in range(iterations):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                times.append(end - start)
            
            # Log benchmark results
            logger = get_logger('benchmark')
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            logger.info(f"Benchmark {func.__name__} ({iterations} iterations):")
            logger.info(f"  Average: {avg_time:.4f}s")
            logger.info(f"  Min: {min_time:.4f}s")
            logger.info(f"  Max: {max_time:.4f}s")
            
            return result
        
        return wrapper
    return decorator