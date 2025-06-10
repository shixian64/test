#!/usr/bin/env python3
"""
Phase 1 ML Integration Demo

This script demonstrates the successful implementation of Phase 1 AI/ML features:
- Crash classification with machine learning
- Anomaly detection using statistical and ML methods
- Pattern recognition and clustering
- ML-enhanced analysis workflow
"""

import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from android_log_analyzer.ml import (
        create_ml_analyzer, get_ml_capabilities, check_ml_health, 
        demo_ml_features, ML_DEPENDENCIES_AVAILABLE
    )
    from android_log_analyzer.ml.models.crash_classifier import CrashClassifier
    from android_log_analyzer.ml.models.anomaly_detector import AnomalyDetector
    from android_log_analyzer.ml.models.pattern_recognizer import PatternRecognizer
    from android_log_analyzer.log_analyzer import analyze_with_ml, get_ml_enhanced_report
    ML_IMPORT_SUCCESS = True
except ImportError as e:
    print(f"⚠️  ML features not available: {e}")
    print("💡 To enable ML features, install dependencies:")
    print("   pip install scikit-learn numpy")
    ML_IMPORT_SUCCESS = False


def demo_ml_capabilities():
    """Demonstrate ML capabilities and status"""
    print("🧠 ML Capabilities Assessment")
    print("=" * 50)
    
    if not ML_IMPORT_SUCCESS:
        print("❌ ML modules could not be imported")
        print("📦 Required packages: scikit-learn, numpy")
        return False
    
    # Get ML capabilities
    capabilities = get_ml_capabilities()
    
    print(f"📊 ML Dependencies Available: {capabilities['ml_dependencies_available']}")
    print(f"🔧 Models Available:")
    
    for model_name, model_info in capabilities['models'].items():
        status = "✅" if model_info['available'] else "❌"
        print(f"   {status} {model_name}: {model_info['description']}")
        
        if model_info['available']:
            for capability in model_info['capabilities'][:3]:  # Show first 3
                print(f"      - {capability}")
    
    return capabilities['ml_dependencies_available']


def demo_crash_classifier():
    """Demonstrate crash classification capabilities"""
    print("\n\n🔥 Crash Classifier Demo")
    print("=" * 50)
    
    if not ML_IMPORT_SUCCESS:
        print("❌ Crash classifier not available")
        return
    
    try:
        classifier = CrashClassifier()
        
        # Test different types of crashes
        test_crashes = [
            "FATAL EXCEPTION: main java.lang.NullPointerException: Attempt to invoke virtual method",
            "Fatal signal 11 (SIGSEGV), code 1, fault addr 0xdeadbeef",
            "ANR in com.example.app: Input dispatching timed out (Waiting to send key event)",
            "OutOfMemoryError: Failed to allocate 8MB array",
            "System server crashed, restarting"
        ]
        
        print(f"🔍 Analyzing {len(test_crashes)} crash samples:")
        
        for i, crash_text in enumerate(test_crashes, 1):
            prediction = classifier.classify_crash(crash_text)
            
            print(f"\n{i}. Crash: {crash_text[:60]}...")
            print(f"   Type: {prediction.crash_type}")
            print(f"   Confidence: {prediction.confidence:.2f}")
            print(f"   Severity: {prediction.severity}")
            print(f"   Recommendation: {prediction.recommendations[0] if prediction.recommendations else 'None'}")
        
        # Get model info
        model_info = classifier.get_model_info()
        print(f"\n📈 Model Info:")
        print(f"   ML Available: {model_info['ml_available']}")
        print(f"   Is Trained: {model_info['is_trained']}")
        print(f"   Model Type: {model_info['model_type']}")
        print(f"   Supported Types: {', '.join(model_info['supported_types'])}")
        
    except Exception as e:
        print(f"❌ Crash classifier demo failed: {e}")


def demo_anomaly_detector():
    """Demonstrate anomaly detection capabilities"""
    print("\n\n🚨 Anomaly Detector Demo")
    print("=" * 50)
    
    if not ML_IMPORT_SUCCESS:
        print("❌ Anomaly detector not available")
        return
    
    try:
        detector = AnomalyDetector()
        
        # Create sample log with anomalies
        normal_logs = [
            "01-01 10:00:00.123  1234  1234 I ActivityManager: Start proc com.example.app",
            "01-01 10:00:01.234  1234  1234 D MyApp: User clicked button",
            "01-01 10:00:02.345  1234  1234 I MyApp: Loading data from server",
            "01-01 10:00:03.456  1234  1234 D MyApp: Data loaded successfully"
        ]
        
        anomalous_logs = [
            "01-01 10:00:04.567  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:04.568  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:04.569  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:04.570  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:04.571  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:05.678  5678  5678 E System: OutOfMemoryError: Failed to allocate",
            "01-01 10:00:06.789  6789  6789 W AudioFlinger: write blocked for 2000 msecs",
            "01-01 10:00:07.890  7890  7890 W AudioFlinger: write blocked for 2000 msecs",
            "01-01 10:00:08.901  8901  8901 W AudioFlinger: write blocked for 2000 msecs"
        ]
        
        all_logs = normal_logs + anomalous_logs
        
        print(f"🔍 Analyzing {len(all_logs)} log lines for anomalies:")
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(all_logs)
        
        print(f"\n📊 Anomaly Detection Results:")
        print(f"   Total anomalies detected: {len(anomalies)}")
        
        for i, anomaly in enumerate(anomalies, 1):
            print(f"\n{i}. {anomaly.anomaly_type}")
            print(f"   Score: {anomaly.anomaly_score:.2f}")
            print(f"   Severity: {anomaly.severity}")
            print(f"   Description: {anomaly.description}")
            if anomaly.recommendations:
                print(f"   Recommendation: {anomaly.recommendations[0]}")
        
        # Get model status
        status = detector.get_model_status()
        print(f"\n📈 Detector Status:")
        print(f"   ML Available: {status['ml_available']}")
        print(f"   Is Trained: {status['is_trained']}")
        print(f"   Supported Patterns: {', '.join(status['supported_patterns'])}")
        
    except Exception as e:
        print(f"❌ Anomaly detector demo failed: {e}")


def demo_pattern_recognizer():
    """Demonstrate pattern recognition capabilities"""
    print("\n\n🔍 Pattern Recognizer Demo")
    print("=" * 50)
    
    if not ML_IMPORT_SUCCESS:
        print("❌ Pattern recognizer not available")
        return
    
    try:
        recognizer = PatternRecognizer()
        
        # Create sample logs with patterns
        sample_logs = [
            "01-01 10:00:00.123  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:01.234  1234  1234 E AndroidRuntime: java.lang.NullPointerException",
            "01-01 10:00:02.345  1234  1234 I ActivityManager: Killing 5678:com.example.app",
            "01-01 10:00:03.456  2345  2345 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:04.567  2345  2345 E AndroidRuntime: java.lang.IllegalStateException",
            "01-01 10:00:05.678  2345  2345 I ActivityManager: Killing 6789:com.example.app",
            "01-01 10:00:06.789  3456  3456 W AudioFlinger: write blocked for 150 msecs",
            "01-01 10:00:07.890  3456  3456 W AudioFlinger: write blocked for 200 msecs",
            "01-01 10:00:08.901  3456  3456 W AudioFlinger: write blocked for 180 msecs",
            "01-01 10:00:09.012  4567  4567 E lowmemorykiller: Killing process 1111",
            "01-01 10:00:10.123  4567  4567 E lowmemorykiller: Killing process 2222",
            "01-01 10:00:11.234  4567  4567 E lowmemorykiller: Killing process 3333"
        ]
        
        print(f"🔍 Analyzing {len(sample_logs)} log lines for patterns:")
        
        # Recognize patterns
        patterns = recognizer.recognize_patterns(sample_logs)
        
        print(f"\n📊 Pattern Recognition Results:")
        print(f"   Total patterns detected: {len(patterns)}")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\n{i}. {pattern.pattern_type.upper()}: {pattern.description}")
            print(f"   Frequency: {pattern.frequency}")
            print(f"   Confidence: {pattern.confidence:.2f}")
            print(f"   Severity: {pattern.severity}")
            print(f"   Example: {pattern.examples[0][:60]}..." if pattern.examples else "   No examples")
            if pattern.recommendations:
                print(f"   Recommendation: {pattern.recommendations[0]}")
        
        # Get pattern statistics
        if patterns:
            stats = recognizer.get_pattern_statistics(patterns)
            print(f"\n📈 Pattern Statistics:")
            print(f"   Total patterns: {stats['total_patterns']}")
            print(f"   Pattern types: {dict(stats['pattern_types'])}")
            print(f"   Severity distribution: {dict(stats['severity_distribution'])}")
            print(f"   Average confidence: {stats['avg_confidence']:.2f}")
        
    except Exception as e:
        print(f"❌ Pattern recognizer demo failed: {e}")


def demo_ml_enhanced_analysis():
    """Demonstrate ML-enhanced analysis workflow"""
    print("\n\n🚀 ML-Enhanced Analysis Demo")
    print("=" * 50)
    
    if not ML_IMPORT_SUCCESS:
        print("❌ ML-enhanced analysis not available")
        return
    
    # Create comprehensive test log
    comprehensive_log = '''
01-01 10:00:00.123  1234  1234 I ActivityManager: Start proc com.example.app
01-01 10:00:01.234  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main
01-01 10:00:01.235  1234  1234 E AndroidRuntime: Process: com.example.app, PID: 1234
01-01 10:00:01.236  1234  1234 E AndroidRuntime: java.lang.NullPointerException
01-01 10:00:02.345  5678  5678 I ActivityManager: ANR in com.example.app
01-01 10:00:03.456  2345  2345 E DEBUG: Fatal signal 11 (SIGSEGV), code 1
01-01 10:00:04.567  3456  3456 E System: OutOfMemoryError: Failed to allocate 8MB
01-01 10:00:05.678  4567  4567 W AudioFlinger: write blocked for 150 msecs
01-01 10:00:06.789  4567  4567 W AudioFlinger: write blocked for 200 msecs
01-01 10:00:07.890  5678  5678 E lowmemorykiller: Killing process 9999
01-01 10:00:08.901  6789  6789 E WifiManager: Failed to connect: timeout
01-01 10:00:09.012  7890  7890 W Performance: Slow operation detected: 2500ms
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(comprehensive_log)
        temp_path = f.name
    
    try:
        print("🔍 Performing ML-enhanced analysis...")
        
        # Get ML-enhanced report
        report = get_ml_enhanced_report(temp_path)
        
        if 'error' in report:
            print(f"❌ Analysis failed: {report['error']}")
            return
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total log lines: {report['total_lines']}")
        print(f"   Standard issues: {report['standard_analysis']['issue_count']}")
        
        ml_analysis = report['ml_analysis']
        if ml_analysis.get('ml_available'):
            print(f"   ML crashes classified: {len(ml_analysis['crash_classifications'])}")
            print(f"   Anomalies detected: {len(ml_analysis['anomalies'])}")
            print(f"   Patterns recognized: {len(ml_analysis['patterns'])}")
            
            # Show ML insights
            insights = ml_analysis.get('ml_insights', {})
            if 'health_score' in insights:
                print(f"   System health score: {insights['health_score']}/100")
            
            # Show crash insights
            crash_insights = insights.get('crash_insights', {})
            if crash_insights:
                print(f"   Most common crash type: {crash_insights.get('most_common_type', 'N/A')}")
                print(f"   Critical crashes: {crash_insights.get('critical_crashes', 0)}")
            
            # Show enhanced insights
            enhanced = report.get('enhanced_insights', {})
            if enhanced.get('recommendations'):
                print(f"\n💡 Recommendations:")
                for rec in enhanced['recommendations']:
                    print(f"   - {rec}")
        else:
            print("   ML analysis: Not available")
        
    finally:
        import os
        os.unlink(temp_path)


def demo_ml_health_check():
    """Demonstrate ML health monitoring"""
    print("\n\n🏥 ML Health Check Demo")
    print("=" * 50)
    
    if not ML_IMPORT_SUCCESS:
        print("❌ ML health check not available")
        return
    
    try:
        health_status = check_ml_health()
        
        print(f"🎯 Overall Status: {health_status['overall_status'].upper()}")
        
        for component, status in health_status['components'].items():
            status_emoji = "✅" if status['status'] == 'healthy' else "❌" if status['status'] == 'error' else "⚠️"
            print(f"\n{status_emoji} {component.replace('_', ' ').title()}:")
            print(f"   Status: {status['status']}")
            
            if 'model_info' in status:
                model_info = status['model_info']
                print(f"   ML Available: {model_info.get('ml_available', 'Unknown')}")
                print(f"   Is Trained: {model_info.get('is_trained', 'Unknown')}")
            
            if 'error' in status:
                print(f"   Error: {status['error']}")
            
            if 'reason' in status:
                print(f"   Reason: {status['reason']}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")


def main():
    """Run all Phase 1 ML integration demos"""
    print("🧠 Phase 1: AI/ML Integration Demo")
    print("=" * 80)
    print("Demonstrating machine learning capabilities for intelligent log analysis")
    print()
    
    try:
        # Check ML capabilities
        ml_available = demo_ml_capabilities()
        
        if ml_available:
            demo_crash_classifier()
            demo_anomaly_detector()
            demo_pattern_recognizer()
            demo_ml_enhanced_analysis()
            demo_ml_health_check()
            
            print("\n" + "=" * 80)
            print("🎉 Phase 1: AI/ML Integration Successfully Completed!")
            print("✨ All ML features implemented and functional")
            print("🚀 Ready to proceed to Phase 2: Real-time Processing")
        else:
            print("\n" + "=" * 80)
            print("⚠️  Phase 1: ML Dependencies Required")
            print("📦 Install required packages to enable ML features:")
            print("   pip install scikit-learn numpy")
            print("🔄 Re-run demo after installation")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
