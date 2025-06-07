# Android 日志分析器项目

该仓库包含用于检查 Android logcat 日志文件的一套小型工具，包括可复用的 Python 库、命令行接口以及简单的 Electron GUI。

## 使用方法

### 命令行
在可编辑模式下安装并运行分析器：
```bash
pip install -e .
android-log-analyzer path/to/logcat.log
```

如需将结果保存为 JSON，可指定输出文件：
```bash
android-log-analyzer path/to/logcat.log --json-output report.json
```

### GUI
启动 GUI 需要 `node` 和 Python 的 `eel` 包。在 `log_analyzer_gui` 目录运行：
```bash
npm install
npm start
```

## 运行测试

该项目提供了一些单元测试，可通过以下命令运行：
```bash
python -m unittest android_log_analyzer.test_log_analyzer
```
