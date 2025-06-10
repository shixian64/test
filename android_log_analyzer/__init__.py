"""
Android Log Analyzer Package

A comprehensive toolkit for analyzing Android logcat files to detect crashes,
ANRs, memory issues, and other critical problems.
"""

from .log_analyzer import read_log_file, generate_report, get_structured_report_data
from .config import ConfigManager
from .utils import PerformanceMonitor, format_file_size

__version__ = "0.2.0"
__author__ = "Android Log Analyzer Team"

__all__ = [
    'read_log_file',
    'generate_report',
    'get_structured_report_data',
    'ConfigManager',
    'PerformanceMonitor',
    'format_file_size'
]
