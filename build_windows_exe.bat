@echo off
echo ========================================
echo Android Log Analyzer - Windows EXE Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found:
python --version
echo.

REM Check if we're in the right directory
if not exist "android_log_analyzer" (
    echo ❌ Please run this script from the project root directory
    echo The android_log_analyzer folder should be present
    pause
    exit /b 1
)

echo ✅ Project directory confirmed
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv_build" (
    echo 🔧 Creating build virtual environment...
    python -m venv venv_build
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment exists
)

echo.
echo 📦 Installing dependencies...
call venv_build\Scripts\activate
python -m pip install --upgrade pip
pip install -e .
pip install pyinstaller

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "AndroidLogAnalyzer_Windows_EXE" rmdir /s /q AndroidLogAnalyzer_Windows_EXE

echo.
echo 🔨 Building Windows executable...
echo This may take a few minutes...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name AndroidLogAnalyzer ^
    --add-data "android_log_analyzer;android_log_analyzer" ^
    --add-data "README.md;." ^
    --add-data "README_zh-CN.md;." ^
    --add-data "sample.log;." ^
    --hidden-import android_log_analyzer ^
    --hidden-import android_log_analyzer.log_analyzer ^
    --hidden-import android_log_analyzer.config ^
    --hidden-import android_log_analyzer.utils ^
    --hidden-import android_log_analyzer.intelligent ^
    --hidden-import android_log_analyzer.intelligent.smart_search ^
    --hidden-import android_log_analyzer.intelligent.priority_scorer ^
    --hidden-import android_log_analyzer.intelligent.report_generator ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import tkinter.scrolledtext ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --clean ^
    --noconfirm ^
    main_app.py

if errorlevel 1 (
    echo ❌ Build failed!
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo.

REM Create distribution package
echo 📦 Creating distribution package...
mkdir AndroidLogAnalyzer_Windows_EXE
copy dist\AndroidLogAnalyzer.exe AndroidLogAnalyzer_Windows_EXE\
copy README.md AndroidLogAnalyzer_Windows_EXE\
copy README_zh-CN.md AndroidLogAnalyzer_Windows_EXE\
copy sample.log AndroidLogAnalyzer_Windows_EXE\

REM Create batch file for command line usage
echo @echo off > AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo echo Android Log Analyzer - Command Line Mode >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo echo. >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo if "%%1"=="" ( >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo     echo Usage: %%0 ^<log_file^> >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo     echo Example: %%0 logcat.log >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo     echo. >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo     echo Or just run AndroidLogAnalyzer.exe for GUI mode >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo     pause >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo ^) else ( >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo     AndroidLogAnalyzer.exe %%* >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat
echo ^) >> AndroidLogAnalyzer_Windows_EXE\analyze_log.bat

REM Create usage guide
echo # Android Log Analyzer - Windows EXE Usage Guide > AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo. >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo ## Quick Start >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo. >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo ### GUI Mode (Recommended) >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo Double-click AndroidLogAnalyzer.exe >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo. >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo ### Command Line Mode >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo AndroidLogAnalyzer.exe your_log_file.log >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo analyze_log.bat your_log_file.log >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo. >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo ## System Requirements >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo - Windows 7/8/10/11 (64-bit) >> AndroidLogAnalyzer_Windows_EXE\USAGE.md
echo - No additional software required >> AndroidLogAnalyzer_Windows_EXE\USAGE.md

REM Create ZIP package
echo 📦 Creating ZIP package...
powershell -command "Compress-Archive -Path 'AndroidLogAnalyzer_Windows_EXE\*' -DestinationPath 'AndroidLogAnalyzer_Windows_EXE_v0.2.0.zip' -Force"

if errorlevel 1 (
    echo ⚠️ ZIP creation failed, but EXE is ready in AndroidLogAnalyzer_Windows_EXE folder
) else (
    echo ✅ ZIP package created: AndroidLogAnalyzer_Windows_EXE_v0.2.0.zip
)

echo.
echo 🎉 Windows EXE build completed successfully!
echo.
echo 📊 Build Results:
for %%f in (AndroidLogAnalyzer_Windows_EXE\AndroidLogAnalyzer.exe) do echo    EXE Size: %%~zf bytes
echo    Location: AndroidLogAnalyzer_Windows_EXE\AndroidLogAnalyzer.exe
if exist "AndroidLogAnalyzer_Windows_EXE_v0.2.0.zip" (
    for %%f in (AndroidLogAnalyzer_Windows_EXE_v0.2.0.zip) do echo    ZIP Size: %%~zf bytes
    echo    Package: AndroidLogAnalyzer_Windows_EXE_v0.2.0.zip
)
echo.
echo 🚀 Next Steps:
echo 1. Test the EXE: AndroidLogAnalyzer_Windows_EXE\AndroidLogAnalyzer.exe
echo 2. Try with sample: AndroidLogAnalyzer.exe sample.log
echo 3. Distribute the AndroidLogAnalyzer_Windows_EXE folder or ZIP file
echo.
pause
