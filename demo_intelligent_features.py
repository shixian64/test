#!/usr/bin/env python3
"""
Intelligent Features Demo

This script demonstrates the new intelligent features of the Android Log Analyzer:
- Smart search with natural language queries
- Intelligent priority scoring
- Automated report generation
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from android_log_analyzer.intelligent.smart_search import SmartSearchEngine, SearchType
    from android_log_analyzer.intelligent.priority_scorer import IssuePriorityScorer, IssueContext, Priority
    from android_log_analyzer.intelligent.report_generator import IntelligentReportGenerator, ReportConfig
except ImportError:
    print("❌ Intelligent features not yet integrated into main package")
    print("💡 This is a preview of upcoming features")
    print("🔧 Run this demo after integrating the intelligent modules")
    sys.exit(1)


def demo_smart_search():
    """Demonstrate smart search capabilities"""
    print("🔍 Smart Search Engine Demo")
    print("=" * 50)
    
    # Sample log data
    sample_logs = [
        "2024-01-15 10:30:15.123  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
        "2024-01-15 10:30:15.124  1234  1234 E AndroidRuntime: Process: com.example.app, PID: 1234",
        "2024-01-15 10:30:15.125  1234  1234 E AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method",
        "2024-01-15 10:30:16.200  5678  5678 I ActivityManager: Killing 9876:com.example.app/u0a123 (adj 900): remove task",
        "2024-01-15 10:30:17.300  2345  2345 W AudioFlinger: write blocked for 150 msecs, 5 delayed writes",
        "2024-01-15 10:30:18.400  3456  3456 E WifiManager: Failed to connect to network: timeout",
        "2024-01-15 10:30:19.500  4567  4567 D GC: Explicit concurrent mark sweep GC freed 1024KB",
        "2024-01-15 10:30:20.600  5678  5678 E System: OutOfMemoryError: Failed to allocate 8MB",
        "2024-01-15 10:30:21.700  6789  6789 I ANR: Application Not Responding: com.example.app",
        "2024-01-15 10:30:22.800  7890  7890 W Performance: Slow operation detected: 2500ms"
    ]
    
    search_engine = SmartSearchEngine()
    
    # Test different types of queries
    test_queries = [
        "show all crashes",
        "find memory issues", 
        "performance problems",
        "network errors",
        "java.lang.NullPointerException",
        "timeout",
        "ANR"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        results = search_engine.smart_search(query, sample_logs, max_results=3)
        
        if results:
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. Line {result.line_number}: {result.content[:80]}...")
                print(f"      Relevance: {result.relevance_score:.2f}, Type: {result.match_type.value}")
        else:
            print("   No results found")
    
    # Test query suggestions
    print(f"\n💡 Query Suggestions for 'cra':")
    suggestions = search_engine.suggest_queries("cra")
    for suggestion in suggestions[:3]:
        print(f"   - {suggestion.suggestion} (confidence: {suggestion.confidence:.2f})")


def demo_priority_scoring():
    """Demonstrate intelligent priority scoring"""
    print("\n\n📊 Priority Scoring Demo")
    print("=" * 50)
    
    # Sample issues
    sample_issues = [
        {
            'type': 'java_crash',
            'severity': 'critical',
            'frequency': 15,
            'component': 'application',
            'message': 'NullPointerException in main activity',
            'affects_system_stability': False,
            'blocks_user_action': True
        },
        {
            'type': 'native_crash',
            'severity': 'critical',
            'frequency': 3,
            'component': 'system_server',
            'message': 'SIGSEGV in system process',
            'affects_system_stability': True,
            'causes_reboot': True
        },
        {
            'type': 'anr',
            'severity': 'high',
            'frequency': 8,
            'component': 'application',
            'message': 'Application not responding on UI thread',
            'blocks_user_action': True,
            'affects_user_experience': True
        },
        {
            'type': 'memory_issue',
            'severity': 'medium',
            'frequency': 25,
            'component': 'application',
            'message': 'High memory usage detected',
            'affects_performance': True
        },
        {
            'type': 'network_issue',
            'severity': 'low',
            'frequency': 2,
            'component': 'application',
            'message': 'Connection timeout',
            'affects_user_experience': False
        }
    ]
    
    scorer = IssuePriorityScorer()
    
    # Create context
    context = IssueContext(
        app_version="1.2.3",
        user_count_affected=1500,
        release_stage="production"
    )
    
    print("🎯 Individual Issue Scoring:")
    for i, issue in enumerate(sample_issues, 1):
        priority_info = scorer.calculate_priority(issue, context)
        
        print(f"\n{i}. {issue['type'].replace('_', ' ').title()}")
        print(f"   Priority: {priority_info['priority'].upper()} (Score: {priority_info['total_score']})")
        print(f"   Breakdown: Severity={priority_info['breakdown']['severity_score']:.1f}, "
              f"Frequency={priority_info['breakdown']['frequency_score']:.1f}, "
              f"Impact={priority_info['breakdown']['system_impact_score']:.1f}")
        print(f"   Top Recommendation: {priority_info['recommendations'][0]}")
    
    # Batch prioritization
    print(f"\n📋 Batch Prioritization (sorted by priority):")
    prioritized = scorer.batch_prioritize(sample_issues, context)
    
    for i, issue in enumerate(prioritized, 1):
        print(f"{i}. {issue['priority'].upper()}: {issue['type'].replace('_', ' ').title()} "
              f"(Score: {issue['total_score']:.1f})")
    
    # Priority distribution
    distribution = scorer.get_priority_distribution(prioritized)
    print(f"\n📊 Priority Distribution:")
    for priority, count in distribution.items():
        if count > 0:
            print(f"   {priority.upper()}: {count} issues")


def demo_report_generation():
    """Demonstrate intelligent report generation"""
    print("\n\n📄 Report Generation Demo")
    print("=" * 50)
    
    # Sample analysis data
    analysis_data = {
        'package_info': {
            'name': 'sample_ylog.zip',
            'size': 52428800,  # 50MB
            'total_files': 25,
            'subsystems': ['android', 'modem', 'audio', 'connectivity']
        },
        'summary': {
            'total_issues': 47,
            'critical_issues': 3
        },
        'critical_issues': [
            {
                'type': 'native_crash',
                'severity': 'critical',
                'frequency': 5,
                'subsystem': 'system',
                'message': 'SIGSEGV in system_server process',
                'affects_system_stability': True,
                'causes_reboot': True
            },
            {
                'type': 'java_crash',
                'severity': 'critical',
                'frequency': 12,
                'subsystem': 'android',
                'message': 'NullPointerException in MainActivity.onCreate()',
                'blocks_user_action': True,
                'affects_user_experience': True
            },
            {
                'type': 'anr',
                'severity': 'critical',
                'frequency': 8,
                'subsystem': 'android',
                'message': 'Input dispatching timed out',
                'blocks_user_action': True
            }
        ],
        'subsystem_analysis': {
            'android': {
                'file_count': 8,
                'total_size': 20971520,  # 20MB
                'issues': [
                    {'type': 'java_crash', 'message': 'NullPointerException in MainActivity'},
                    {'type': 'anr', 'message': 'Input dispatching timed out'},
                    {'type': 'memory_issue', 'message': 'High GC pressure detected'}
                ],
                'statistics': {
                    'issue_types': {
                        'java_crash': 5,
                        'anr': 3,
                        'memory_issue': 8
                    }
                }
            },
            'modem': {
                'file_count': 3,
                'total_size': 10485760,  # 10MB
                'issues': [
                    {'type': 'modem_crash', 'message': 'CP assert detected'},
                    {'type': 'signal_issue', 'message': 'Weak signal strength'}
                ],
                'statistics': {
                    'issue_types': {
                        'modem_crash': 2,
                        'signal_issue': 4
                    }
                }
            },
            'audio': {
                'file_count': 2,
                'total_size': 5242880,  # 5MB
                'issues': [
                    {'type': 'audio_underrun', 'message': 'PCM underrun detected'},
                    {'type': 'codec_error', 'message': 'Audio codec initialization failed'}
                ],
                'statistics': {
                    'issue_types': {
                        'audio_underrun': 8,
                        'codec_error': 2
                    }
                }
            }
        }
    }
    
    # Generate different types of reports
    report_configs = [
        ReportConfig(audience="executive", format="markdown"),
        ReportConfig(audience="technical", format="markdown"),
        ReportConfig(audience="mixed", format="markdown")
    ]
    
    for config in report_configs:
        print(f"\n📋 {config.audience.title()} Report:")
        print("-" * 30)
        
        generator = IntelligentReportGenerator(config)
        report = generator.generate_comprehensive_report(analysis_data)
        
        # Show first few lines of the report
        lines = report.split('\n')
        for line in lines[:15]:  # Show first 15 lines
            print(line)
        
        print(f"\n... (Report continues for {len(lines)} total lines)")
        
        # Save full report to file
        filename = f"sample_{config.audience}_report.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"💾 Full report saved to: {filename}")


def demo_integration():
    """Demonstrate integration of all intelligent features"""
    print("\n\n🔗 Integration Demo")
    print("=" * 50)
    
    print("🎯 Intelligent Analysis Workflow:")
    print("1. Smart search identifies relevant log entries")
    print("2. Priority scorer evaluates issue importance")
    print("3. Report generator creates comprehensive analysis")
    print("4. Recommendations guide next actions")
    
    print(f"\n💡 Benefits of Intelligent Features:")
    print("✅ Faster issue identification with natural language search")
    print("✅ Automated priority assessment saves manual triage time")
    print("✅ Comprehensive reports for different audiences")
    print("✅ Actionable recommendations accelerate resolution")
    print("✅ Consistent analysis across different log formats")
    
    print(f"\n🚀 Next Steps for Implementation:")
    print("1. Integrate smart search into GUI interface")
    print("2. Add priority scoring to issue detection pipeline")
    print("3. Implement automated report generation")
    print("4. Create API endpoints for external integration")
    print("5. Add machine learning models for pattern recognition")


def main():
    """Run all intelligent features demonstrations"""
    print("🧠 Android Log Analyzer - Intelligent Features Demo")
    print("=" * 80)
    print("This demo showcases the new intelligent capabilities that make")
    print("log analysis faster, smarter, and more actionable.")
    print()
    
    try:
        demo_smart_search()
        demo_priority_scoring()
        demo_report_generation()
        demo_integration()
        
        print("\n" + "=" * 80)
        print("🎉 Intelligent Features Demo Completed!")
        print("✨ These features transform basic log analysis into intelligent insights")
        print("📈 Ready to implement in production for enhanced productivity")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
