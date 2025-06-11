#!/usr/bin/env python3
"""
Build script for creating Windows executable

This script automates the process of building a Windows executable
from the Android Log Analyzer project using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking build requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Check main modules
    try:
        import android_log_analyzer
        print(f"✅ Android Log Analyzer {android_log_analyzer.__version__}")
    except ImportError:
        print("❌ Android Log Analyzer package not found")
        return False
    
    return True


def clean_build_dirs():
    """Clean previous build directories"""
    print("🧹 Cleaning previous build files...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean Python cache files
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                os.remove(os.path.join(root, file))


def create_version_info():
    """Create version info file for Windows executable"""
    print("📝 Creating version info...")
    
    version_info = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 2, 0, 0),
    prodvers=(0, 2, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Android Log Analyzer Team'),
           StringStruct(u'FileDescription', u'Android Log Analyzer'),
           StringStruct(u'FileVersion', u'0.2.0'),
           StringStruct(u'InternalName', u'AndroidLogAnalyzer'),
           StringStruct(u'LegalCopyright', u'© 2024 Android Log Analyzer Team'),
           StringStruct(u'OriginalFilename', u'AndroidLogAnalyzer.exe'),
           StringStruct(u'ProductName', u'Android Log Analyzer'),
           StringStruct(u'ProductVersion', u'0.2.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Create version info
    create_version_info()
    
    # Build command
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'build_config.spec'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def create_distribution():
    """Create distribution package"""
    print("📦 Creating distribution package...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ No dist directory found")
        return False
    
    exe_file = dist_dir / 'AndroidLogAnalyzer.exe'
    if not exe_file.exists():
        print("❌ Executable not found in dist directory")
        return False
    
    # Create distribution folder
    package_dir = Path('AndroidLogAnalyzer_Windows')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    # Copy executable
    shutil.copy2(exe_file, package_dir / 'AndroidLogAnalyzer.exe')
    
    # Copy documentation
    docs_to_copy = ['README.md', 'README_zh-CN.md']
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, package_dir / doc)
    
    # Copy sample files
    samples_to_copy = ['sample.log']
    for sample in samples_to_copy:
        if Path(sample).exists():
            shutil.copy2(sample, package_dir / sample)
    
    # Create usage instructions
    usage_text = """# Android Log Analyzer - Windows版本使用说明

## 快速开始

### GUI模式（推荐）
双击 `AndroidLogAnalyzer.exe` 启动图形界面

### 命令行模式
在命令提示符中运行：
```
AndroidLogAnalyzer.exe path/to/logfile.log
```

## 功能特点

✅ **支持多种日志格式**
- .log, .txt 文本文件
- .gz, .zip 压缩文件
- SPRD ylog 包格式

✅ **智能问题检测**
- Java崩溃分析
- ANR（应用无响应）检测
- 原生崩溃分析
- 内存问题检测
- 系统错误分析

✅ **用户友好界面**
- 拖拽文件支持
- 实时分析进度
- 详细结果展示
- JSON导出功能

## 使用示例

1. 启动程序
2. 点击"Browse"选择日志文件
3. 点击"Analyze Log"开始分析
4. 查看分析结果
5. 可选择导出为JSON格式

## 技术支持

如有问题，请查看README.md文档或联系开发团队。

---
Android Log Analyzer v0.2.0
© 2024 Android Log Analyzer Team
"""
    
    with open(package_dir / 'USAGE.md', 'w', encoding='utf-8') as f:
        f.write(usage_text)
    
    # Create batch file for command line usage
    batch_content = """@echo off
echo Android Log Analyzer - Command Line Mode
echo.
if "%1"=="" (
    echo Usage: %0 ^<log_file^>
    echo Example: %0 logcat.log
    echo.
    echo Or just run AndroidLogAnalyzer.exe for GUI mode
    pause
) else (
    AndroidLogAnalyzer.exe %*
)
"""
    
    with open(package_dir / 'analyze_log.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✅ Distribution package created: {package_dir}")
    print(f"   Executable size: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True


def main():
    """Main build process"""
    print("🚀 Android Log Analyzer - Windows Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('android_log_analyzer').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable():
        print("❌ Build process failed")
        sys.exit(1)
    
    # Create distribution
    if not create_distribution():
        print("❌ Distribution creation failed")
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the executable in AndroidLogAnalyzer_Windows/")
    print("2. Distribute the entire AndroidLogAnalyzer_Windows/ folder")
    print("3. Users can run AndroidLogAnalyzer.exe directly")
    
    # Show final statistics
    exe_path = Path('AndroidLogAnalyzer_Windows/AndroidLogAnalyzer.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / 1024 / 1024
        print(f"\n📊 Final executable size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
