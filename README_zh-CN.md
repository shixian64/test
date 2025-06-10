# Android 日志分析器

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

**Language / 语言**: [English](README.md) | [中文](README_zh-CN.md)

</div>

一个全面的 Android logcat 文件分析工具包，用于检测崩溃、ANR、内存问题和其他关键问题。该项目包括 Python 库、命令行界面和可选的基于 Electron 的 GUI。

## 功能特性

- **多格式支持**: 分析 `.log`、`.txt`、`.gz` 和 `.zip` 文件
- **问题检测**: 自动检测 Java 崩溃、ANR、原生崩溃、系统错误和内存问题
- **灵活输出**: 控制台报告、JSON 导出和可选的 GUI
- **性能优化**: 高效解析，支持可选的并行处理
- **可配置**: 可自定义检测模式和分析设置
- **跨平台**: 支持 Windows、macOS 和 Linux

## 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/shixian64/test.git
cd test
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

## 高级用法

### 配置管理

创建配置文件来自定义分析行为：

```bash
# 生成示例配置
python -m android_log_analyzer.config
```

配置文件示例 (`config.json`)：

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

# 分析日志文件
issues = read_log_file("path/to/logcat.log")

# 生成报告
generate_report(issues)

# 访问单个问题
for issue in issues:
    print(f"发现 {issue['type']}: {issue.get('process_name', '未知')}")
```

## GUI 应用程序

该项目包含一个可选的基于 Electron 的 GUI，用于交互式分析。

### 前置要求

- Node.js 14+ 和 npm
- 安装了 `eel` 包的 Python

### 设置和启动

```bash
cd log_analyzer_gui
npm install
npm start
```

## 问题检测

分析器可以检测以下类型的问题：

### Java 崩溃
- Android Runtime 中的致命异常
- 堆栈跟踪和错误详情
- 进程信息

### ANR（应用程序无响应）
- 输入分发超时
- 广播接收器超时
- 服务超时
- 进程和原因提取

### 原生崩溃
- 基于信号的崩溃（SIGSEGV、SIGABRT 等）
- Tombstone 指示器
- 进程和线程信息

### 系统错误
- 内核恐慌
- 看门狗超时
- 系统服务器崩溃
- 硬件相关错误

### 内存问题
- 低内存杀手事件
- 内存不足情况
- 进程终止

## 开发

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行带覆盖率的测试
python -m pytest --cov=android_log_analyzer

# 运行特定测试文件
python -m pytest tests/test_log_analyzer.py -v
```

### 代码质量

```bash
# 格式化代码
black android_log_analyzer/ tests/

# 检查代码风格
flake8 android_log_analyzer/ tests/

# 类型检查
mypy android_log_analyzer/
```

### 项目结构

```
android-log-analyzer/
├── android_log_analyzer/          # 主包
│   ├── __init__.py
│   ├── log_analyzer.py           # 核心分析逻辑
│   ├── config.py                 # 配置管理
│   ├── utils.py                  # 工具函数
│   └── test_log_analyzer.py      # 遗留测试
├── tests/                        # 测试套件
│   ├── test_config.py
│   ├── test_utils.py
│   └── test_log_analyzer.py
├── log_analyzer_gui/             # Electron GUI
│   ├── package.json
│   ├── main_gui.py
│   └── web/
├── requirements.txt              # 依赖
├── requirements-dev.txt          # 开发依赖
├── pyproject.toml               # 构建配置
└── setup.py                     # 包设置
```

## 贡献

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 进行更改
4. 为新功能添加测试
5. 运行测试套件 (`python -m pytest`)
6. 提交更改 (`git commit -m 'Add amazing feature'`)
7. 推送到分支 (`git push origin feature/amazing-feature`)
8. 打开 Pull Request

## 许可证

该项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 更新日志

### 版本 0.1.0
- 初始发布
- 基本日志解析和问题检测
- 命令行界面
- JSON 导出功能
- Electron GUI（测试版）

## 支持

- **问题**: [GitHub Issues](https://github.com/shixian64/test/issues)
- **文档**: [Wiki](https://github.com/shixian64/test/wiki)
- **讨论**: [GitHub Discussions](https://github.com/shixian64/test/discussions)
