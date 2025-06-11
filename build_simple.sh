#!/bin/bash

# Android Log Analyzer - Simple Build Script for Linux
# This script creates a Windows-compatible executable using PyInstaller

echo "🚀 Android Log Analyzer - Simple Build Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "android_log_analyzer" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create version info file
echo "📝 Creating version info..."
cat > version_info.txt << 'EOF'
# UTF-8
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
)
EOF

# Build using PyInstaller with simple command
echo "🔨 Building executable..."
pyinstaller \
    --onefile \
    --windowed \
    --name AndroidLogAnalyzer \
    --add-data "android_log_analyzer:android_log_analyzer" \
    --add-data "README.md:." \
    --add-data "sample.log:." \
    --hidden-import android_log_analyzer \
    --hidden-import android_log_analyzer.log_analyzer \
    --hidden-import android_log_analyzer.config \
    --hidden-import android_log_analyzer.utils \
    --hidden-import android_log_analyzer.intelligent \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.filedialog \
    --hidden-import tkinter.messagebox \
    --hidden-import tkinter.scrolledtext \
    --version-file version_info.txt \
    --clean \
    --noconfirm \
    main_app.py

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    
    # Create distribution package
    echo "📦 Creating distribution package..."
    
    PACKAGE_DIR="AndroidLogAnalyzer_Windows"
    rm -rf "$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR"
    
    # Copy executable
    if [ -f "dist/AndroidLogAnalyzer.exe" ]; then
        cp "dist/AndroidLogAnalyzer.exe" "$PACKAGE_DIR/"
        echo "   ✅ Copied executable"
    elif [ -f "dist/AndroidLogAnalyzer" ]; then
        cp "dist/AndroidLogAnalyzer" "$PACKAGE_DIR/AndroidLogAnalyzer.exe"
        echo "   ✅ Copied executable (renamed)"
    else
        echo "   ❌ Executable not found"
        exit 1
    fi
    
    # Copy documentation
    [ -f "README.md" ] && cp "README.md" "$PACKAGE_DIR/"
    [ -f "README_zh-CN.md" ] && cp "README_zh-CN.md" "$PACKAGE_DIR/"
    [ -f "sample.log" ] && cp "sample.log" "$PACKAGE_DIR/"
    
    # Create usage instructions
    cat > "$PACKAGE_DIR/USAGE.md" << 'EOF'
# Android Log Analyzer - Windows版本使用说明

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

---
Android Log Analyzer v0.2.0
© 2024 Android Log Analyzer Team
EOF
    
    # Create batch file for command line
    cat > "$PACKAGE_DIR/analyze_log.bat" << 'EOF'
@echo off
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
EOF
    
    # Show results
    echo ""
    echo "🎉 Build completed successfully!"
    echo ""
    echo "📋 Distribution package created: $PACKAGE_DIR/"
    echo "   📁 Contents:"
    ls -la "$PACKAGE_DIR/"
    echo ""
    
    if [ -f "$PACKAGE_DIR/AndroidLogAnalyzer.exe" ]; then
        SIZE=$(du -h "$PACKAGE_DIR/AndroidLogAnalyzer.exe" | cut -f1)
        echo "📊 Executable size: $SIZE"
    fi
    
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the executable in $PACKAGE_DIR/"
    echo "2. Distribute the entire $PACKAGE_DIR/ folder"
    echo "3. Users can run AndroidLogAnalyzer.exe directly"
    
else
    echo "❌ Build failed!"
    exit 1
fi
