#!/usr/bin/env python3
"""
Android Log Analyzer - Demo Script

This script demonstrates the enhanced features of the optimized Android Log Analyzer.
"""

import json
import tempfile
from pathlib import Path

from android_log_analyzer.config import ConfigManager
from android_log_analyzer.log_analyzer import read_log_file, generate_report, save_report_to_json
from android_log_analyzer.utils import PerformanceMonitor, format_file_size, validate_log_file


def create_sample_log():
    """Create a sample log file for demonstration."""
    sample_content = """02-15 10:00:00.123 12345 12345 E AndroidRuntime: FATAL EXCEPTION: main
02-15 10:00:00.124 12345 12345 E AndroidRuntime: Process: com.example.app, PID: 12345
02-15 10:00:00.125 12345 12345 E AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method
02-15 11:00:00.456  1001  1025 E ActivityManager: ANR in com.example.slowapp (com.example.slowapp/.MyActivity)
02-15 11:00:01.456  1001  1025 W ActivityManager: ANR in com.example.slowapp, reason: Input dispatching timed out
03-01 10:30:05.124 12345 12345 F DEBUG   : *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
03-01 10:30:05.125 12345 12345 F DEBUG   : Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0xdeadbeef
03-02 11:00:00.123     0     0 E kernel  : Kernel panic - not syncing: Attempted to kill init!
03-02 11:05:30.789   123   456 E Watchdog: !@SyncMonitor: Watchdog triggered
03-26 10:05:00.000  1234  1234 I lowmemorykiller: Killing 'com.example.memtest' (12345) to free 10240kB memory
03-26 10:05:01.000  1234  1234 W ActivityManager: Low memory killer killed process com.example.memtest
"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    temp_file.write(sample_content)
    temp_file.close()
    return temp_file.name


def demo_basic_analysis():
    """Demonstrate basic log analysis functionality."""
    print("🔍 Demo: Basic Log Analysis")
    print("=" * 50)
    
    # Create sample log
    log_file = create_sample_log()
    print(f"📁 Created sample log: {log_file}")
    print(f"📊 File size: {format_file_size(Path(log_file).stat().st_size)}")
    
    # Validate file
    if validate_log_file(log_file):
        print("✅ Log file validation passed")
    else:
        print("❌ Log file validation failed")
        return
    
    # Analyze with performance monitoring
    monitor = PerformanceMonitor()
    
    print("\n🚀 Starting analysis...")
    issues = read_log_file(log_file)
    
    monitor.increment('files_processed')
    monitor.increment('issues_found', len(issues))
    
    print(f"✨ Found {len(issues)} issues")
    
    # Generate report
    print("\n📋 Analysis Report:")
    print("-" * 30)
    generate_report(issues)
    
    # Performance summary
    print("\n⚡ Performance Summary:")
    print("-" * 30)
    monitor.log_summary()
    
    # Clean up
    Path(log_file).unlink()
    print(f"\n🧹 Cleaned up temporary file")


def demo_configuration():
    """Demonstrate configuration management."""
    print("\n⚙️  Demo: Configuration Management")
    print("=" * 50)
    
    # Create config manager
    config = ConfigManager()
    
    # Show default configuration
    print("📋 Default Configuration:")
    default_config = config.get_all()
    print(json.dumps(default_config, indent=2)[:500] + "...")
    
    # Modify configuration
    config.set('analysis.max_file_size_mb', 200)
    config.set('output.console_colors', False)
    
    print(f"\n🔧 Modified max file size: {config.get('analysis.max_file_size_mb')} MB")
    print(f"🎨 Console colors: {config.get('output.console_colors')}")
    
    # Save configuration
    temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_config.close()
    
    config.save_config(temp_config.name)
    print(f"💾 Configuration saved to: {temp_config.name}")
    
    # Load configuration
    new_config = ConfigManager(temp_config.name)
    print(f"📖 Loaded max file size: {new_config.get('analysis.max_file_size_mb')} MB")
    
    # Clean up
    Path(temp_config.name).unlink()
    print("🧹 Cleaned up configuration file")


def demo_json_export():
    """Demonstrate JSON export functionality."""
    print("\n📤 Demo: JSON Export")
    print("=" * 50)
    
    # Create and analyze sample log
    log_file = create_sample_log()
    issues = read_log_file(log_file)
    
    # Export to JSON
    temp_json = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_json.close()
    
    save_report_to_json(issues, temp_json.name)
    print(f"📁 JSON report saved to: {temp_json.name}")
    
    # Show JSON structure
    with open(temp_json.name, 'r') as f:
        report_data = json.load(f)
    
    print(f"📊 Summary counts: {report_data['summary_counts']}")
    print(f"📝 Detailed issues: {len(report_data['detailed_issues'])} items")
    
    # Show first issue details
    if report_data['detailed_issues']:
        first_issue = report_data['detailed_issues'][0]
        print(f"🔍 First issue type: {first_issue['type']}")
    
    # Clean up
    Path(log_file).unlink()
    Path(temp_json.name).unlink()
    print("🧹 Cleaned up temporary files")


def demo_gui_info():
    """Show information about the GUI."""
    print("\n🖥️  Demo: GUI Information")
    print("=" * 50)
    
    print("🎨 Enhanced GUI Features:")
    print("  • Modern responsive design with CSS Grid and Flexbox")
    print("  • Drag & drop file upload support")
    print("  • Real-time progress indicators")
    print("  • Search and filter functionality")
    print("  • Bilingual support (English/Chinese)")
    print("  • Dark mode support")
    print("  • Export functionality")
    print("  • Modal dialogs for detailed issue view")
    
    print("\n🚀 To start the GUI:")
    print("  cd log_analyzer_gui")
    print("  npm install")
    print("  npm start")
    
    print("\n🌐 GUI Features:")
    print("  • File validation and size checking")
    print("  • Animated progress bars")
    print("  • Responsive card-based summary")
    print("  • Interactive issue table")
    print("  • Language toggle with localStorage")


def main():
    """Run all demonstrations."""
    print("🎯 Android Log Analyzer - Enhanced Demo")
    print("=" * 60)
    print("This demo showcases the optimized features of the Android Log Analyzer")
    print()
    
    try:
        demo_basic_analysis()
        demo_configuration()
        demo_json_export()
        demo_gui_info()
        
        print("\n🎉 Demo completed successfully!")
        print("✨ The Android Log Analyzer has been significantly enhanced with:")
        print("   • Type safety and better error handling")
        print("   • Performance optimizations")
        print("   • Configuration management")
        print("   • Modern GUI with bilingual support")
        print("   • Comprehensive testing and CI/CD")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
