#!/usr/bin/env python3
"""
Project Health Check Script

This script performs comprehensive checks on the Android Log Analyzer project
to ensure all components are working correctly before final commit.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")


def check_python_syntax():
    """Check Python files for syntax errors"""
    print_header("Python Syntax Check")
    
    python_files = [
        'android_log_analyzer/__init__.py',
        'android_log_analyzer/__main__.py',
        'android_log_analyzer/log_analyzer.py',
        'android_log_analyzer/advanced_parser.py',
        'android_log_analyzer/sprd_analyzer.py',
        'android_log_analyzer/config.py',
        'android_log_analyzer/utils.py',
        'log_analyzer_gui/main_gui.py',
        'demo.py',
        'demo_advanced.py',
        'tests/test_config.py'
    ]
    
    errors = 0
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                             check=True, capture_output=True)
                print_success(f"Syntax OK: {file_path}")
            except subprocess.CalledProcessError as e:
                print_error(f"Syntax Error in {file_path}: {e}")
                errors += 1
        else:
            print_warning(f"File not found: {file_path}")
    
    return errors == 0


def check_imports():
    """Check if all imports work correctly"""
    print_header("Import Check")
    
    try:
        # Test core imports
        from android_log_analyzer import read_log_file, ConfigManager, PerformanceMonitor
        print_success("Core imports successful")
        
        # Test advanced imports
        from android_log_analyzer.advanced_parser import AdvancedLogParser
        from android_log_analyzer.sprd_analyzer import SPRDLogAnalyzer
        print_success("Advanced imports successful")
        
        # Test functionality
        issues = read_log_file('sample.log')
        print_success(f"Basic analysis works: {len(issues)} issues found")
        
        # Test advanced classes
        parser = AdvancedLogParser()
        sprd_analyzer = SPRDLogAnalyzer()
        print_success("Advanced analyzers created successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Import error: {e}")
        return False


def check_file_structure():
    """Check if all required files exist"""
    print_header("File Structure Check")
    
    required_files = [
        'README.md',
        'README_zh-CN.md',
        'PROJECT_STRUCTURE.md',
        'pyproject.toml',
        'setup.py',
        'requirements.txt',
        'requirements-dev.txt',
        'Makefile',
        'android_log_analyzer/__init__.py',
        'android_log_analyzer/log_analyzer.py',
        'android_log_analyzer/advanced_parser.py',
        'android_log_analyzer/sprd_analyzer.py',
        'log_analyzer_gui/package.json',
        'log_analyzer_gui/main_gui.py',
        'log_analyzer_gui/web/main.html',
        'log_analyzer_gui/web/script.js',
        'log_analyzer_gui/web/style.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def check_javascript():
    """Check JavaScript syntax"""
    print_header("JavaScript Syntax Check")
    
    js_files = [
        'log_analyzer_gui/web/script.js',
        'log_analyzer_gui/electron_bootstrap.js'
    ]
    
    errors = 0
    for file_path in js_files:
        if os.path.exists(file_path):
            try:
                subprocess.run(['node', '-c', file_path], 
                             check=True, capture_output=True)
                print_success(f"JavaScript OK: {file_path}")
            except subprocess.CalledProcessError as e:
                print_error(f"JavaScript Error in {file_path}: {e}")
                errors += 1
            except FileNotFoundError:
                print_warning("Node.js not found, skipping JavaScript check")
                break
        else:
            print_warning(f"File not found: {file_path}")
    
    return errors == 0


def check_package_json():
    """Check package.json validity"""
    print_header("Package.json Check")
    
    package_json_path = 'log_analyzer_gui/package.json'
    if os.path.exists(package_json_path):
        try:
            import json
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            required_fields = ['name', 'version', 'main', 'scripts']
            for field in required_fields:
                if field in package_data:
                    print_success(f"Package.json has {field}: {package_data[field]}")
                else:
                    print_error(f"Package.json missing {field}")
                    return False
            
            return True
            
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in package.json: {e}")
            return False
    else:
        print_error("package.json not found")
        return False


def run_tests():
    """Run the test suite"""
    print_header("Test Suite")
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("All tests passed")
            print(result.stdout)
            return True
        else:
            print_error("Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print_warning("pytest not found, skipping tests")
        return True


def check_documentation():
    """Check documentation files"""
    print_header("Documentation Check")
    
    doc_files = {
        'README.md': 'Main documentation',
        'README_zh-CN.md': 'Chinese documentation',
        'PROJECT_STRUCTURE.md': 'Project structure',
        'OPTIMIZATION_SUMMARY.md': 'Optimization details'
    }
    
    all_good = True
    for file_path, description in doc_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:  # Basic content check
                    print_success(f"{description}: {len(content)} characters")
                else:
                    print_warning(f"{description}: Very short content")
        else:
            print_error(f"Missing: {description}")
            all_good = False
    
    return all_good


def main():
    """Run all checks"""
    print("🎯 Android Log Analyzer - Project Health Check")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Python Syntax", check_python_syntax),
        ("Imports", check_imports),
        ("JavaScript", check_javascript),
        ("Package.json", check_package_json),
        ("Tests", run_tests),
        ("Documentation", check_documentation)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_error(f"Error in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print_header("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n📊 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("🎉 All checks passed! Project is ready for commit.")
        return 0
    else:
        print_error(f"⚠️  {total - passed} checks failed. Please fix issues before commit.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
