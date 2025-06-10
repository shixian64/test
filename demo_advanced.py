#!/usr/bin/env python3
"""
Advanced Android Log Analyzer Demo

This script demonstrates the enhanced features for analyzing complex log packages
like SPRD ylog files with multiple subsystems.
"""

import json
import tempfile
from pathlib import Path

from android_log_analyzer.advanced_parser import AdvancedLogParser
from android_log_analyzer.sprd_analyzer import SPRDLogAnalyzer
from android_log_analyzer.utils import PerformanceMonitor, format_file_size


def demo_ylog_analysis():
    """Demonstrate analysis of the uploaded ylog.zip file"""
    print("🔍 Demo: SPRD YLog Package Analysis")
    print("=" * 60)
    
    # Look for the uploaded ylog.zip file
    ylog_path = Path("examples/sample_logs/ylog.zip")
    
    if not ylog_path.exists():
        print(f"❌ ylog.zip not found at {ylog_path}")
        print("Please ensure the file is uploaded to examples/sample_logs/")
        return
    
    print(f"📁 Found ylog package: {ylog_path}")
    print(f"📊 File size: {format_file_size(ylog_path.stat().st_size)}")
    
    # Initialize SPRD analyzer
    analyzer = SPRDLogAnalyzer()
    monitor = PerformanceMonitor()
    
    print("\n🚀 Starting SPRD-specific analysis...")
    
    try:
        # Perform advanced analysis
        results = analyzer.analyze_sprd_package(ylog_path)
        
        print("✨ Analysis completed successfully!")
        
        # Display package overview
        print("\n📦 Package Overview:")
        print("-" * 30)
        package_info = results.get('package_info', {})
        print(f"  Package Name: {package_info.get('name', 'Unknown')}")
        print(f"  Total Files: {package_info.get('total_files', 0)}")
        print(f"  Subsystems: {len(package_info.get('subsystems', []))}")
        
        # Display platform information
        sprd_analysis = results.get('sprd_analysis', {})
        platform_info = sprd_analysis.get('platform_info', {})
        if platform_info:
            print("\n🔧 Platform Information:")
            print("-" * 30)
            print(f"  Chipset: {platform_info.get('chipset', 'Unknown')}")
            print(f"  Android Version: {platform_info.get('android_version', 'Unknown')}")
            print(f"  Build Version: {platform_info.get('build_version', 'Unknown')}")
        
        # Display subsystem analysis
        subsystem_analysis = results.get('subsystem_analysis', {})
        if subsystem_analysis:
            print("\n🔬 Subsystem Analysis:")
            print("-" * 30)
            for subsystem_name, subsystem_data in subsystem_analysis.items():
                issue_count = len(subsystem_data.get('issues', []))
                file_count = subsystem_data.get('file_count', 0)
                total_size = format_file_size(subsystem_data.get('total_size', 0))
                print(f"  {subsystem_name.capitalize()}:")
                print(f"    Files: {file_count}, Size: {total_size}, Issues: {issue_count}")
        
        # Display critical issues
        critical_issues = results.get('critical_issues', [])
        if critical_issues:
            print(f"\n🚨 Critical Issues Found: {len(critical_issues)}")
            print("-" * 30)
            for i, issue in enumerate(critical_issues[:5], 1):
                print(f"  {i}. {issue.get('type', 'Unknown')} in {issue.get('subsystem', 'Unknown')}")
        
        # Display SPRD-specific analysis
        if sprd_analysis:
            print("\n📱 SPRD-Specific Analysis:")
            print("-" * 30)
            
            # Modem analysis
            modem_analysis = sprd_analysis.get('modem_analysis', {})
            if modem_analysis:
                crashes = len(modem_analysis.get('crashes', []))
                resets = len(modem_analysis.get('resets', []))
                if crashes or resets:
                    print(f"  Modem: {crashes} crashes, {resets} resets")
            
            # Connectivity analysis
            connectivity_analysis = sprd_analysis.get('connectivity_analysis', {})
            if connectivity_analysis:
                wifi_issues = len(connectivity_analysis.get('wifi_disconnects', []))
                bt_issues = len(connectivity_analysis.get('bt_failures', []))
                if wifi_issues or bt_issues:
                    print(f"  Connectivity: {wifi_issues} WiFi issues, {bt_issues} BT issues")
            
            # Audio analysis
            audio_analysis = sprd_analysis.get('audio_analysis', {})
            if audio_analysis:
                underruns = len(audio_analysis.get('underruns', []))
                if underruns:
                    print(f"  Audio: {underruns} underruns detected")
        
        # Display timeline summary
        timeline = results.get('timeline', [])
        if timeline:
            print(f"\n⏰ Timeline: {len(timeline)} events captured")
            print("-" * 30)
            # Show first few events
            for event in timeline[:3]:
                timestamp = event.get('timestamp', 'Unknown')
                subsystem = event.get('subsystem', 'Unknown')
                event_type = event.get('type', 'Unknown')
                print(f"  {timestamp} - {subsystem}: {event_type}")
            if len(timeline) > 3:
                print(f"  ... and {len(timeline) - 3} more events")
        
        # Performance summary
        print("\n⚡ Performance Summary:")
        print("-" * 30)
        monitor.increment('files_processed', package_info.get('total_files', 0))
        monitor.increment('issues_found', len(critical_issues))
        summary = monitor.get_summary()
        print(f"  Analysis Time: {summary.get('elapsed_time_seconds', 0):.2f} seconds")
        print(f"  Files Processed: {summary.get('files_processed', 0)}")
        print(f"  Issues Found: {summary.get('issues_found', 0)}")
        
        # Save detailed results
        output_file = "ylog_analysis_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Detailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


def demo_advanced_features():
    """Demonstrate advanced analysis features"""
    print("\n🎯 Demo: Advanced Analysis Features")
    print("=" * 60)
    
    print("🌟 Enhanced Features Available:")
    print("  • Multi-subsystem analysis (Android, Modem, Audio, Connectivity)")
    print("  • Platform-specific issue detection (SPRD/Unisoc)")
    print("  • Timeline reconstruction across subsystems")
    print("  • Compressed archive support (.zip, .tar.gz)")
    print("  • Performance monitoring and statistics")
    print("  • Enhanced GUI with subsystem tabs")
    print("  • Bilingual interface (English/Chinese)")
    
    print("\n🔧 SPRD-Specific Enhancements:")
    print("  • YLog package format support")
    print("  • Modem crash and reset detection")
    print("  • Audio underrun analysis")
    print("  • WiFi/BT connectivity issue tracking")
    print("  • Thermal throttling detection")
    print("  • Power management issue analysis")
    
    print("\n📊 GUI Enhancements:")
    print("  • Package overview with metadata")
    print("  • Platform information display")
    print("  • Subsystem-specific analysis tabs")
    print("  • Interactive timeline view")
    print("  • Advanced filtering options")
    print("  • Export functionality")


def demo_gui_instructions():
    """Show instructions for using the enhanced GUI"""
    print("\n🖥️  Demo: Enhanced GUI Usage")
    print("=" * 60)
    
    print("🚀 To test the enhanced GUI:")
    print("1. Start the GUI:")
    print("   cd log_analyzer_gui")
    print("   npm install")
    print("   npm start")
    
    print("\n2. Upload the ylog.zip file:")
    print("   • Drag and drop the ylog.zip file")
    print("   • Or click 'Select File' and browse")
    
    print("\n3. Explore the enhanced features:")
    print("   • Package Overview - Shows file count, size, subsystems")
    print("   • Platform Information - Chipset, Android version, build")
    print("   • Subsystem Analysis - Tabs for each subsystem")
    print("   • Event Timeline - Chronological view of issues")
    print("   • Advanced Filters - Filter by subsystem, severity")
    
    print("\n4. Language switching:")
    print("   • Click the language toggle (EN/中文) in top-right")
    print("   • All interface elements will switch languages")
    
    print("\n5. Export results:")
    print("   • Click 'Export JSON' for detailed data")
    print("   • Click 'Generate Report' for formatted output")


def main():
    """Run all advanced demonstrations"""
    print("🎯 Android Log Analyzer - Advanced Features Demo")
    print("=" * 80)
    print("This demo showcases the enhanced capabilities for analyzing")
    print("complex log packages like SPRD ylog files.")
    print()
    
    try:
        demo_ylog_analysis()
        demo_advanced_features()
        demo_gui_instructions()
        
        print("\n🎉 Advanced demo completed!")
        print("✨ The Android Log Analyzer now supports:")
        print("   • Complex log package analysis")
        print("   • SPRD/Unisoc platform-specific detection")
        print("   • Multi-subsystem analysis")
        print("   • Enhanced GUI with modern interface")
        print("   • Bilingual support")
        print("   • Performance monitoring")
        
        print("\n📁 Files to explore:")
        print("   • ylog_analysis_results.json - Detailed analysis results")
        print("   • examples/sample_logs/ylog.zip - Sample log package")
        print("   • Enhanced GUI at http://localhost:8000")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
