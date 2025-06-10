"""
Machine Learning Module for Android Log Analyzer

This module provides AI/ML capabilities for intelligent log analysis including:
- Crash classification and categorization
- Anomaly detection and pattern recognition
- Predictive analysis and trend detection
- Advanced feature extraction and modeling
"""

# Import models with fallback handling
try:
    from .models.crash_classifier import CrashClassifier, CrashPrediction
    CRASH_CLASSIFIER_AVAILABLE = True
except ImportError:
    CRASH_CLASSIFIER_AVAILABLE = False

try:
    from .models.anomaly_detector import AnomalyDetector, AnomalyResult
    ANOMALY_DETECTOR_AVAILABLE = True
except ImportError:
    ANOMALY_DETECTOR_AVAILABLE = False

try:
    from .models.pattern_recognizer import PatternRecognizer, Pattern, PatternCluster
    PATTERN_RECOGNIZER_AVAILABLE = True
except ImportError:
    PATTERN_RECOGNIZER_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "Android Log Analyzer ML Team"

# Check for ML dependencies
try:
    import sklearn
    import numpy as np
    ML_DEPENDENCIES_AVAILABLE = True
except ImportError:
    ML_DEPENDENCIES_AVAILABLE = False

__all__ = [
    # Models
    'CrashClassifier',
    'CrashPrediction',
    'AnomalyDetector', 
    'AnomalyResult',
    'PatternRecognizer',
    'Pattern',
    'PatternCluster',
    
    # Availability flags
    'CRASH_CLASSIFIER_AVAILABLE',
    'ANOMALY_DETECTOR_AVAILABLE', 
    'PATTERN_RECOGNIZER_AVAILABLE',
    'ML_DEPENDENCIES_AVAILABLE',
    
    # Factory functions
    'create_ml_analyzer',
    'get_ml_capabilities'
]


def create_ml_analyzer():
    """
    Create a complete ML analyzer with all available models
    
    Returns:
        Dictionary containing available ML models
    """
    analyzer = {}
    
    if CRASH_CLASSIFIER_AVAILABLE:
        analyzer['crash_classifier'] = CrashClassifier()
    
    if ANOMALY_DETECTOR_AVAILABLE:
        analyzer['anomaly_detector'] = AnomalyDetector()
    
    if PATTERN_RECOGNIZER_AVAILABLE:
        analyzer['pattern_recognizer'] = PatternRecognizer()
    
    return analyzer


def get_ml_capabilities():
    """
    Get information about available ML capabilities
    
    Returns:
        Dictionary with ML feature availability and descriptions
    """
    return {
        'ml_dependencies_available': ML_DEPENDENCIES_AVAILABLE,
        'models': {
            'crash_classifier': {
                'available': CRASH_CLASSIFIER_AVAILABLE,
                'description': 'Machine learning-based crash classification',
                'capabilities': [
                    'Java exception classification',
                    'Native crash detection',
                    'ANR identification',
                    'OOM detection',
                    'System crash analysis'
                ]
            },
            'anomaly_detector': {
                'available': ANOMALY_DETECTOR_AVAILABLE,
                'description': 'Statistical and ML-based anomaly detection',
                'capabilities': [
                    'Unusual pattern detection',
                    'Performance anomaly identification',
                    'Log volume analysis',
                    'Error rate monitoring',
                    'System behavior analysis'
                ]
            },
            'pattern_recognizer': {
                'available': PATTERN_RECOGNIZER_AVAILABLE,
                'description': 'Advanced pattern recognition and clustering',
                'capabilities': [
                    'Recurring pattern identification',
                    'Message clustering',
                    'Sequence pattern detection',
                    'Frequency analysis',
                    'Template matching'
                ]
            }
        },
        'requirements': {
            'required_packages': [
                'scikit-learn>=1.0.0',
                'numpy>=1.20.0'
            ],
            'optional_packages': [
                'tensorflow>=2.8.0',
                'torch>=1.10.0',
                'transformers>=4.20.0'
            ]
        }
    }


def install_ml_dependencies():
    """
    Provide instructions for installing ML dependencies
    
    Returns:
        Installation instructions
    """
    return {
        'pip_install': [
            'pip install scikit-learn>=1.0.0',
            'pip install numpy>=1.20.0'
        ],
        'conda_install': [
            'conda install scikit-learn',
            'conda install numpy'
        ],
        'requirements_file': '''
# ML dependencies for Android Log Analyzer
scikit-learn>=1.0.0
numpy>=1.20.0

# Optional advanced ML libraries
# tensorflow>=2.8.0
# torch>=1.10.0
# transformers>=4.20.0
        '''.strip()
    }


def check_ml_health():
    """
    Check the health and status of ML components
    
    Returns:
        Health check results
    """
    health_status = {
        'overall_status': 'healthy' if ML_DEPENDENCIES_AVAILABLE else 'degraded',
        'components': {}
    }
    
    # Check crash classifier
    if CRASH_CLASSIFIER_AVAILABLE:
        try:
            classifier = CrashClassifier()
            health_status['components']['crash_classifier'] = {
                'status': 'healthy',
                'model_info': classifier.get_model_info()
            }
        except Exception as e:
            health_status['components']['crash_classifier'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        health_status['components']['crash_classifier'] = {
            'status': 'unavailable',
            'reason': 'Import failed'
        }
    
    # Check anomaly detector
    if ANOMALY_DETECTOR_AVAILABLE:
        try:
            detector = AnomalyDetector()
            health_status['components']['anomaly_detector'] = {
                'status': 'healthy',
                'model_info': detector.get_model_status()
            }
        except Exception as e:
            health_status['components']['anomaly_detector'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        health_status['components']['anomaly_detector'] = {
            'status': 'unavailable',
            'reason': 'Import failed'
        }
    
    # Check pattern recognizer
    if PATTERN_RECOGNIZER_AVAILABLE:
        try:
            recognizer = PatternRecognizer()
            health_status['components']['pattern_recognizer'] = {
                'status': 'healthy',
                'templates': len(recognizer.pattern_templates)
            }
        except Exception as e:
            health_status['components']['pattern_recognizer'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        health_status['components']['pattern_recognizer'] = {
            'status': 'unavailable',
            'reason': 'Import failed'
        }
    
    return health_status


def demo_ml_features():
    """
    Run a quick demo of all available ML features
    
    Returns:
        Demo results
    """
    demo_results = {
        'ml_available': ML_DEPENDENCIES_AVAILABLE,
        'features_tested': {}
    }
    
    # Sample log data for testing
    sample_logs = [
        "01-01 10:00:00.123  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
        "01-01 10:00:00.124  1234  1234 E AndroidRuntime: java.lang.NullPointerException",
        "01-01 10:00:01.200  5678  5678 I ActivityManager: ANR in com.example.app",
        "01-01 10:00:02.300  2345  2345 E System: OutOfMemoryError: Failed to allocate",
        "01-01 10:00:03.400  3456  3456 E DEBUG: Fatal signal 11 (SIGSEGV)"
    ]
    
    # Test crash classifier
    if CRASH_CLASSIFIER_AVAILABLE:
        try:
            classifier = CrashClassifier()
            prediction = classifier.classify_crash(sample_logs[0])
            demo_results['features_tested']['crash_classifier'] = {
                'status': 'success',
                'prediction': {
                    'crash_type': prediction.crash_type,
                    'confidence': prediction.confidence,
                    'severity': prediction.severity
                }
            }
        except Exception as e:
            demo_results['features_tested']['crash_classifier'] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Test anomaly detector
    if ANOMALY_DETECTOR_AVAILABLE:
        try:
            detector = AnomalyDetector()
            anomalies = detector.detect_anomalies(sample_logs)
            demo_results['features_tested']['anomaly_detector'] = {
                'status': 'success',
                'anomalies_found': len(anomalies)
            }
        except Exception as e:
            demo_results['features_tested']['anomaly_detector'] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Test pattern recognizer
    if PATTERN_RECOGNIZER_AVAILABLE:
        try:
            recognizer = PatternRecognizer()
            patterns = recognizer.recognize_patterns(sample_logs)
            demo_results['features_tested']['pattern_recognizer'] = {
                'status': 'success',
                'patterns_found': len(patterns)
            }
        except Exception as e:
            demo_results['features_tested']['pattern_recognizer'] = {
                'status': 'error',
                'error': str(e)
            }
    
    return demo_results
