# Android Log Analyzer / Android 日志分析器

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

<div id="language-toggle">
  <button onclick="toggleLanguage('en')" id="btn-en" class="lang-btn active">English</button>
  <button onclick="toggleLanguage('zh')" id="btn-zh" class="lang-btn">中文</button>
</div>

</div>

<div id="content-en" class="lang-content">

A comprehensive toolkit for analyzing Android logcat files to detect crashes, ANRs, memory issues, and other critical problems. The project includes a Python library, command-line interface, and optional Electron-based GUI.

</div>

<div id="content-zh" class="lang-content" style="display: none;">

一个全面的 Android logcat 文件分析工具包，用于检测崩溃、ANR、内存问题和其他关键问题。该项目包括 Python 库、命令行界面和可选的基于 Electron 的 GUI。

</div>

<style>
.lang-btn {
  padding: 8px 16px;
  margin: 0 4px;
  border: 1px solid #ddd;
  background: #f8f9fa;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.lang-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.lang-btn:hover {
  background: #e9ecef;
}

.lang-btn.active:hover {
  background: #0056b3;
}

.lang-content {
  margin-top: 20px;
}
</style>

<script>
function toggleLanguage(lang) {
  // Get all language content elements
  const enElements = document.querySelectorAll('[id*="-en"]');
  const zhElements = document.querySelectorAll('[id*="-zh"]');
  const enBtn = document.getElementById('btn-en');
  const zhBtn = document.getElementById('btn-zh');

  if (lang === 'en') {
    // Show English content
    enElements.forEach(el => el.style.display = 'block');
    zhElements.forEach(el => el.style.display = 'none');
    enBtn.classList.add('active');
    zhBtn.classList.remove('active');
    localStorage.setItem('preferred-language', 'en');
  } else {
    // Show Chinese content
    enElements.forEach(el => el.style.display = 'none');
    zhElements.forEach(el => el.style.display = 'block');
    enBtn.classList.remove('active');
    zhBtn.classList.add('active');
    localStorage.setItem('preferred-language', 'zh');
  }
}

// Load preferred language on page load
document.addEventListener('DOMContentLoaded', function() {
  const preferredLang = localStorage.getItem('preferred-language') || 'en';
  toggleLanguage(preferredLang);
});
</script>

<div id="features-en" class="lang-content">

## Features

- **Multi-format Support**: Analyze `.log`, `.txt`, `.gz`, and `.zip` files
- **Issue Detection**: Automatically detect Java crashes, ANRs, native crashes, system errors, and memory issues
- **Flexible Output**: Console reports, JSON export, and optional GUI
- **Performance Optimized**: Efficient parsing with optional parallel processing
- **Configurable**: Customizable detection patterns and analysis settings
- **Cross-platform**: Works on Windows, macOS, and Linux

</div>

<div id="features-zh" class="lang-content" style="display: none;">

## 功能特性

- **多格式支持**: 分析 `.log`、`.txt`、`.gz` 和 `.zip` 文件
- **问题检测**: 自动检测 Java 崩溃、ANR、原生崩溃、系统错误和内存问题
- **灵活输出**: 控制台报告、JSON 导出和可选的 GUI
- **性能优化**: 高效解析，支持可选的并行处理
- **可配置**: 可自定义检测模式和分析设置
- **跨平台**: 支持 Windows、macOS 和 Linux

</div>

<div id="quickstart-en" class="lang-content">

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/example/android-log-analyzer.git
cd android-log-analyzer
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
```

</div>

<div id="quickstart-zh" class="lang-content" style="display: none;">

## 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/example/android-log-analyzer.git
cd android-log-analyzer
pip install -e .

# 或安装开发依赖
pip install -e ".[dev]"
```

### 基本用法

```bash
# 分析单个日志文件
android-log-analyzer path/to/logcat.log

# 分析目录中的所有日志文件
android-log-analyzer path/to/logs/

# 将结果保存为 JSON
android-log-analyzer path/to/logcat.log --json-output report.json

# 指定平台（未来功能）
android-log-analyzer path/to/logcat.log --platform mtk
```

</div>

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
