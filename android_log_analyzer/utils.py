"""
Utility functions for Android Log Analyzer.

This module contains helper functions for file operations, performance monitoring,
and other common tasks.
"""
import functools
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Iterator, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure.
        
    Returns:
        Wrapped function that logs execution time.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {e}")
            raise
    return wrapper


def batch_process(
    items: List[T], 
    processor: Callable[[T], Any], 
    batch_size: int = 100,
    max_workers: Optional[int] = None
) -> List[Any]:
    """
    Process items in batches with optional parallel processing.
    
    Args:
        items: List of items to process.
        processor: Function to process each item.
        batch_size: Number of items per batch.
        max_workers: Maximum number of worker threads. If None, uses sequential processing.
        
    Returns:
        List of processing results.
    """
    results = []
    
    if max_workers and max_workers > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit batches
            futures = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                future = executor.submit(_process_batch, batch, processor)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
    else:
        # Sequential processing
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = _process_batch(batch, processor)
            results.extend(batch_results)
    
    return results


def _process_batch(batch: List[T], processor: Callable[[T], Any]) -> List[Any]:
    """
    Process a single batch of items.
    
    Args:
        batch: Batch of items to process.
        processor: Function to process each item.
        
    Returns:
        List of processing results for the batch.
    """
    results = []
    for item in batch:
        try:
            result = processor(item)
            if result is not None:
                results.append(result)
        except Exception as e:
            logger.error(f"Error processing item {item}: {e}")
    return results


def safe_file_size(file_path: Union[str, Path]) -> int:
    """
    Safely get file size in bytes.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        File size in bytes, or 0 if file doesn't exist or can't be accessed.
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes.
        
    Returns:
        Formatted size string (e.g., "1.5 MB").
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def chunked_file_reader(
    file_path: Union[str, Path], 
    chunk_size: int = 8192
) -> Iterator[str]:
    """
    Read file in chunks to handle large files efficiently.
    
    Args:
        file_path: Path to the file.
        chunk_size: Size of each chunk in bytes.
        
    Yields:
        File content chunks.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def validate_log_file(file_path: Union[str, Path], max_size_mb: int = 100) -> bool:
    """
    Validate if a file is suitable for log analysis.
    
    Args:
        file_path: Path to the file.
        max_size_mb: Maximum allowed file size in MB.
        
    Returns:
        True if file is valid for analysis, False otherwise.
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        logger.warning(f"File does not exist: {file_path}")
        return False
    
    # Check if it's a file (not directory)
    if not file_path.is_file():
        logger.warning(f"Path is not a file: {file_path}")
        return False
    
    # Check file size
    size_bytes = safe_file_size(file_path)
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > max_size_mb:
        logger.warning(f"File too large ({format_file_size(size_bytes)}): {file_path}")
        return False
    
    # Check file extension
    supported_extensions = {'.log', '.txt', '.gz', '.zip'}
    if file_path.suffix.lower() not in supported_extensions:
        logger.warning(f"Unsupported file extension: {file_path}")
        return False
    
    return True


def create_progress_callback(total_items: int, update_interval: int = 100) -> Callable[[int], None]:
    """
    Create a progress callback function.
    
    Args:
        total_items: Total number of items to process.
        update_interval: How often to update progress (every N items).
        
    Returns:
        Progress callback function.
    """
    def progress_callback(current_item: int) -> None:
        if current_item % update_interval == 0 or current_item == total_items:
            percentage = (current_item / total_items) * 100
            logger.info(f"Progress: {current_item}/{total_items} ({percentage:.1f}%)")
    
    return progress_callback


class PerformanceMonitor:
    """Monitor performance metrics during analysis."""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'files_processed': 0,
            'lines_processed': 0,
            'lines_parsed': 0,
            'issues_found': 0,
            'errors_encountered': 0
        }
    
    def increment(self, metric: str, value: int = 1) -> None:
        """Increment a metric counter."""
        if metric in self.metrics:
            self.metrics[metric] += value
        else:
            logger.warning(f"Unknown metric: {metric}")
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since monitor creation."""
        return time.time() - self.start_time
    
    def get_summary(self) -> dict:
        """Get performance summary."""
        elapsed = self.get_elapsed_time()
        summary = self.metrics.copy()
        summary['elapsed_time_seconds'] = elapsed
        
        # Calculate rates
        if elapsed > 0:
            summary['lines_per_second'] = self.metrics['lines_processed'] / elapsed
            summary['files_per_second'] = self.metrics['files_processed'] / elapsed
        
        return summary
    
    def log_summary(self) -> None:
        """Log performance summary."""
        summary = self.get_summary()
        logger.info("Performance Summary:")
        for key, value in summary.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")
