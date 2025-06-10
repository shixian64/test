# Android Log Analyzer

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

**Language / 语言**: [English](README.md) | [中文](README_zh-CN.md)

</div>

A comprehensive toolkit for analyzing Android logcat files to detect crashes, ANRs, memory issues, and other critical problems. The project includes a Python library, command-line interface, and optional Electron-based GUI.

## Features

### 🔍 Core Analysis
- **Multi-format Support**: Analyze `.log`, `.txt`, `.gz`, and `.zip` files
- **Issue Detection**: Automatically detect Java crashes, ANRs, native crashes, system errors, and memory issues
- **Complex Package Analysis**: Support for multi-file log packages and archives
- **Performance Optimized**: Efficient parsing with optional parallel processing

### 📱 Platform-Specific Support
- **SPRD/Unisoc Platform**: Specialized analysis for SPRD chipset logs
- **YLog Package Support**: Native support for SPRD ylog format
- **Multi-Subsystem Analysis**: Separate analysis for Android, Modem, Audio, Connectivity, and Sensor logs
- **Platform Information Extraction**: Automatic detection of chipset, Android version, and build info

### 🎨 Enhanced User Interface
- **Modern GUI**: Responsive web interface with drag-and-drop support
- **Bilingual Support**: Complete English/Chinese interface
- **Subsystem Tabs**: Organized view of different log subsystems
- **Interactive Timeline**: Chronological view of events across all subsystems
- **Advanced Filtering**: Filter by subsystem, severity, and issue type

### ⚙️ Advanced Features
- **Configuration Management**: JSON-based configuration system
- **Performance Monitoring**: Built-in analysis performance tracking
- **Export Options**: JSON export and report generation
- **Cross-platform**: Works on Windows, macOS, and Linux

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/shixian64/test.git
cd test
pip install -e .

# Or install development dependencies
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Analyze a single log file
android-log-analyzer path/to/logcat.log

# Analyze all log files in a directory
android-log-analyzer path/to/logs/

# Save results as JSON
android-log-analyzer path/to/logcat.log --json-output report.json

# Specify platform (future feature)
android-log-analyzer path/to/logcat.log --platform mtk

# Analyze complex log packages (NEW!)
android-log-analyzer examples/sample_logs/ylog.zip
```

### Advanced Analysis (NEW!)

```bash
# Analyze SPRD ylog packages
android-log-analyzer ylog.zip --platform sprd

# Run advanced demo
python demo_advanced.py

# Test with sample files
android-log-analyzer examples/sample_logs/ylog.zip --json-output ylog_results.json
```

## Advanced Usage

### Configuration

Create a configuration file to customize analysis behavior:

```bash
# Generate sample configuration
python -m android_log_analyzer.config
```

Example configuration (`config.json`):

```json
{
  "analysis": {
    "max_file_size_mb": 200,
    "enable_parallel_processing": true,
    "max_workers": 4
  },
  "output": {
    "json_indent": 2,
    "console_colors": true
  }
}
```

### Python API

```python
from android_log_analyzer import read_log_file, generate_report

# Analyze a log file
issues = read_log_file("path/to/logcat.log")

# Generate report
generate_report(issues)

# Access individual issues
for issue in issues:
    print(f"Found {issue['type']}: {issue.get('process_name', 'Unknown')}")
```

## GUI Application

The project includes an optional Electron-based GUI for interactive analysis.

### Prerequisites

- Node.js 14+ and npm
- Python with `eel` package

### Setup and Launch

```bash
cd log_analyzer_gui
npm install
npm start
```

## Issue Detection

The analyzer can detect the following types of issues:

### Java Crashes
- Fatal exceptions in Android Runtime
- Stack traces and error details
- Process information

### ANRs (Application Not Responding)
- Input dispatching timeouts
- Broadcast receiver timeouts
- Service timeouts
- Process and reason extraction

### Native Crashes
- Signal-based crashes (SIGSEGV, SIGABRT, etc.)
- Tombstone indicators
- Process and thread information

### System Errors
- Kernel panics
- Watchdog timeouts
- System server crashes
- Hardware-related errors

### Memory Issues
- Low memory killer events
- Out of memory conditions
- Process terminations

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=android_log_analyzer

# Run specific test file
python -m pytest tests/test_log_analyzer.py -v
```

### Code Quality

```bash
# Format code
black android_log_analyzer/ tests/

# Check style
flake8 android_log_analyzer/ tests/

# Type checking
mypy android_log_analyzer/
```

### Project Structure

```
android-log-analyzer/
├── android_log_analyzer/          # Main package
│   ├── __init__.py
│   ├── log_analyzer.py           # Core analysis logic
│   ├── config.py                 # Configuration management
│   ├── utils.py                  # Utility functions
│   └── test_log_analyzer.py      # Legacy tests
├── tests/                        # Test suite
│   ├── test_config.py
│   ├── test_utils.py
│   └── test_log_analyzer.py
├── log_analyzer_gui/             # Electron GUI
│   ├── package.json
│   ├── main_gui.py
│   └── web/
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Build configuration
└── setup.py                     # Package setup
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.1.0
- Initial release
- Basic log parsing and issue detection
- Command-line interface
- JSON export functionality
- Electron GUI (beta)

## Support

- **Issues**: [GitHub Issues](https://github.com/example/android-log-analyzer/issues)
- **Documentation**: [Wiki](https://github.com/example/android-log-analyzer/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/example/android-log-analyzer/discussions)
