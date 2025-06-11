#!/usr/bin/env python3
"""
Create Windows Python Package

This script creates a Windows-compatible Python package that users
can run with Python installed on Windows.
"""

import os
import shutil
import zipfile
from pathlib import Path


def create_windows_python_package():
    """Create Windows Python package"""
    print("🚀 Creating Windows Python Package...")
    
    # Create package directory
    package_dir = Path("AndroidLogAnalyzer_Windows_Python")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print(f"📁 Created package directory: {package_dir}")
    
    # Copy main application files
    files_to_copy = [
        "main_app.py",
        "android_log_analyzer/",
        "README.md", 
        "README_zh-CN.md",
        "sample.log",
        "requirements.txt"
    ]
    
    for item in files_to_copy:
        src_path = Path(item)
        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, package_dir / src_path.name)
                print(f"   ✅ Copied file: {item}")
            elif src_path.is_dir():
                shutil.copytree(src_path, package_dir / src_path.name)
                print(f"   ✅ Copied directory: {item}")
        else:
            print(f"   ⚠️ Not found: {item}")
    
    # Create Windows batch files
    create_batch_files(package_dir)
    
    # Create installation script
    create_install_script(package_dir)
    
    # Create usage instructions
    create_windows_usage_guide(package_dir)
    
    # Create zip package
    zip_path = "AndroidLogAnalyzer_Windows_Python_v0.2.0.zip"
    create_zip_package(package_dir, zip_path)
    
    print(f"\n🎉 Windows Python package created successfully!")
    print(f"📦 Package: {zip_path}")
    print(f"📊 Size: {os.path.getsize(zip_path) / 1024 / 1024:.1f} MB")


def create_batch_files(package_dir):
    """Create Windows batch files"""
    print("📝 Creating Windows batch files...")
    
    # Main launcher batch file
    launcher_bat = """@echo off
echo Android Log Analyzer - Windows Python Version
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if dependencies are installed
if not exist "venv" (
    echo 🔧 Setting up virtual environment...
    python -m venv venv
    call venv\\Scripts\\activate
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    call venv\\Scripts\\activate
)

REM Run the application
if "%1"=="" (
    echo 🚀 Starting GUI mode...
    python main_app.py
) else (
    echo 🔍 Analyzing: %*
    python main_app.py %*
)

pause
"""
    
    with open(package_dir / "AndroidLogAnalyzer.bat", "w", encoding="utf-8") as f:
        f.write(launcher_bat)
    
    # Quick analysis batch file
    quick_bat = """@echo off
if "%1"=="" (
    echo Usage: %0 ^<log_file^>
    echo Example: %0 logcat.log
    pause
    exit /b 1
)

call venv\\Scripts\\activate
python main_app.py %*
pause
"""
    
    with open(package_dir / "analyze_log.bat", "w", encoding="utf-8") as f:
        f.write(quick_bat)
    
    print("   ✅ Created AndroidLogAnalyzer.bat")
    print("   ✅ Created analyze_log.bat")


def create_install_script(package_dir):
    """Create installation script"""
    print("📝 Creating installation script...")
    
    install_bat = """@echo off
echo Android Log Analyzer - Installation Script
echo ==========================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    echo.
    echo Please install Python 3.7+ from: https://python.org
    echo ⚠️ Important: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo.
echo 🔧 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo 📦 Installing dependencies...
call venv\\Scripts\\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 🚀 To run the application:
echo    - Double-click AndroidLogAnalyzer.bat for GUI mode
echo    - Use analyze_log.bat your_file.log for command line
echo.
pause
"""
    
    with open(package_dir / "install.bat", "w", encoding="utf-8") as f:
        f.write(install_bat)
    
    print("   ✅ Created install.bat")


def create_windows_usage_guide(package_dir):
    """Create Windows usage guide"""
    print("📝 Creating Windows usage guide...")
    
    usage_md = """# Android Log Analyzer - Windows Python版本使用指南

## 🎯 系统要求

- Windows 7/8/10/11 (32位或64位)
- Python 3.7+ (从 https://python.org 下载)
- 至少100MB可用磁盘空间
- 512MB可用内存

## 📦 安装步骤

### 步骤1: 安装Python
1. 访问 https://python.org/downloads/
2. 下载最新的Python 3.x版本
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH" 选项
5. 点击 "Install Now"

### 步骤2: 安装Android Log Analyzer
1. 解压下载的zip文件到任意目录
2. 双击 `install.bat` 运行安装脚本
3. 等待依赖安装完成

## 🚀 使用方法

### 方法1: 图形界面（推荐）
```
双击 AndroidLogAnalyzer.bat
```

### 方法2: 命令行分析
```cmd
analyze_log.bat your_log_file.log
```

### 方法3: 直接使用Python
```cmd
# 激活虚拟环境
venv\\Scripts\\activate

# 运行程序
python main_app.py
python main_app.py your_log_file.log
```

## 🔍 功能特点

✅ **完整功能**: 与可执行文件版本功能完全相同
✅ **智能分析**: 13种Android问题类型检测
✅ **多格式支持**: .log, .txt, .gz, .zip文件
✅ **SPRD平台**: 专门的芯片组分析支持
✅ **实时更新**: 可以轻松更新到最新版本

## 🛠️ 故障排除

### 常见问题

**Q: 提示"Python不是内部或外部命令"**
A: Python未正确安装或未添加到PATH。重新安装Python并勾选"Add Python to PATH"

**Q: 安装依赖失败**
A: 检查网络连接，或使用国内镜像：
```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**Q: 程序无法启动**
A: 确保已运行install.bat完成安装，然后使用AndroidLogAnalyzer.bat启动

**Q: 分析结果为空**
A: 检查日志文件格式，使用sample.log测试程序是否正常工作

### 获取帮助
```cmd
python main_app.py --help
```

## 📈 优势对比

| 特性 | Python版本 | 可执行文件版本 |
|------|------------|----------------|
| 文件大小 | ~10MB | ~7MB |
| 安装复杂度 | 需要Python | 即开即用 |
| 更新便利性 | ✅ 容易 | 需要重新下载 |
| 自定义能力 | ✅ 可修改 | 固定功能 |
| 系统兼容性 | 更广泛 | 仅64位Windows |

## 🔄 更新方法

1. 下载新版本的zip文件
2. 备份当前的配置文件（如果有）
3. 解压新版本覆盖旧文件
4. 运行install.bat更新依赖

## 📞 技术支持

- 项目主页: https://github.com/shixian64/test
- 问题反馈: https://github.com/shixian64/test/issues
- Python官方: https://python.org

---

**🎯 享受强大的Android日志分析功能！**
"""
    
    with open(package_dir / "WINDOWS_USAGE.md", "w", encoding="utf-8") as f:
        f.write(usage_md)
    
    print("   ✅ Created WINDOWS_USAGE.md")


def create_zip_package(package_dir, zip_path):
    """Create zip package"""
    print(f"📦 Creating zip package: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_path)
    
    print(f"   ✅ Created {zip_path}")


if __name__ == "__main__":
    create_windows_python_package()
