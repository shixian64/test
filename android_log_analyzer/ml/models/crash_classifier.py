"""
Crash Classifier Model

This module provides machine learning-based crash classification for Android logs.
Uses text classification to categorize different types of crashes and their severity.
"""

import re
import logging
import pickle
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Try to import ML libraries with fallbacks
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CrashPrediction:
    """Crash classification prediction result"""
    crash_type: str
    confidence: float
    severity: str
    description: str
    recommendations: List[str]


class CrashClassifier:
    """Machine learning-based crash classifier"""
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path
        self.pipeline = None
        self.is_trained = False
        
        # Crash type patterns for feature extraction
        self.crash_patterns = {
            'java_exception': [
                r'java\.lang\.\w*Exception',
                r'FATAL EXCEPTION',
                r'AndroidRuntime.*FATAL'
            ],
            'native_crash': [
                r'Fatal signal \d+',
                r'SIGSEGV|SIGABRT|SIGBUS',
                r'tombstone',
                r'backtrace:'
            ],
            'anr': [
                r'ANR in',
                r'Input dispatching timed out',
                r'Broadcast of Intent.*took'
            ],
            'oom': [
                r'OutOfMemoryError',
                r'Low memory killer',
                r'killed.*oom'
            ],
            'system_crash': [
                r'System server crashed',
                r'Kernel panic',
                r'Watchdog.*triggered'
            ]
        }
        
        # Severity indicators
        self.severity_indicators = {
            'critical': [
                'system server', 'kernel panic', 'fatal signal',
                'sigsegv', 'sigabrt', 'system_server'
            ],
            'high': [
                'anr', 'native crash', 'fatal exception',
                'outofmemoryerror', 'tombstone'
            ],
            'medium': [
                'exception', 'error', 'crash', 'killed'
            ],
            'low': [
                'warning', 'info', 'debug'
            ]
        }
        
        if ML_AVAILABLE:
            self._initialize_model()
        else:
            logger.warning("ML libraries not available, using rule-based classification")
    
    def _initialize_model(self):
        """Initialize the ML pipeline"""
        if not ML_AVAILABLE:
            return
        
        # Create pipeline with TF-IDF vectorizer and Naive Bayes classifier
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english',
                lowercase=True
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Try to load pre-trained model
        if self.model_path and self.model_path.exists():
            self._load_model()
        else:
            # Train with synthetic data if no model exists
            self._train_with_synthetic_data()
    
    def _load_model(self):
        """Load pre-trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                self.pipeline = pickle.load(f)
            self.is_trained = True
            logger.info(f"Loaded pre-trained crash classifier from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._train_with_synthetic_data()
    
    def _save_model(self):
        """Save trained model to disk"""
        if not self.model_path or not self.is_trained:
            return
        
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            logger.info(f"Saved crash classifier to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _train_with_synthetic_data(self):
        """Train model with synthetic crash data"""
        if not ML_AVAILABLE:
            return
        
        # Generate synthetic training data
        training_data = self._generate_synthetic_training_data()
        
        if not training_data:
            logger.warning("No training data available")
            return
        
        texts, labels = zip(*training_data)
        
        try:
            # Train the model
            self.pipeline.fit(texts, labels)
            self.is_trained = True
            
            # Save the model
            self._save_model()
            
            logger.info(f"Trained crash classifier with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
    
    def _generate_synthetic_training_data(self) -> List[Tuple[str, str]]:
        """Generate synthetic training data for crash classification"""
        training_data = []
        
        # Java exception samples
        java_samples = [
            ("FATAL EXCEPTION: main java.lang.NullPointerException", "java_exception"),
            ("AndroidRuntime: FATAL EXCEPTION: java.lang.IllegalStateException", "java_exception"),
            ("java.lang.OutOfMemoryError: Failed to allocate", "oom"),
            ("java.lang.RuntimeException: Unable to start activity", "java_exception"),
        ]
        
        # Native crash samples
        native_samples = [
            ("Fatal signal 11 (SIGSEGV), code 1", "native_crash"),
            ("Fatal signal 6 (SIGABRT), code -6", "native_crash"),
            ("tombstone written to /data/tombstones/", "native_crash"),
            ("backtrace: #00 pc 0000beef", "native_crash"),
        ]
        
        # ANR samples
        anr_samples = [
            ("ANR in com.example.app: Input dispatching timed out", "anr"),
            ("ANR in system_server: Broadcast of Intent took 15000ms", "anr"),
            ("Input event dispatching timed out sending to application", "anr"),
        ]
        
        # OOM samples
        oom_samples = [
            ("OutOfMemoryError: Failed to allocate 8MB", "oom"),
            ("Low memory killer: Killing process 1234", "oom"),
            ("killed process 5678 (com.example.app) oom", "oom"),
        ]
        
        # System crash samples
        system_samples = [
            ("System server crashed, restarting", "system_crash"),
            ("Kernel panic - not syncing", "system_crash"),
            ("Watchdog triggered! dumping kernel log", "system_crash"),
        ]
        
        training_data.extend(java_samples)
        training_data.extend(native_samples)
        training_data.extend(anr_samples)
        training_data.extend(oom_samples)
        training_data.extend(system_samples)
        
        return training_data
    
    def classify_crash(self, log_text: str) -> CrashPrediction:
        """
        Classify a crash from log text
        
        Args:
            log_text: Log text containing crash information
            
        Returns:
            CrashPrediction with classification results
        """
        if ML_AVAILABLE and self.is_trained:
            return self._ml_classify(log_text)
        else:
            return self._rule_based_classify(log_text)
    
    def _ml_classify(self, log_text: str) -> CrashPrediction:
        """Machine learning-based classification"""
        try:
            # Predict crash type
            prediction = self.pipeline.predict([log_text])[0]
            probabilities = self.pipeline.predict_proba([log_text])[0]
            confidence = max(probabilities)
            
            # Determine severity
            severity = self._determine_severity(log_text, prediction)
            
            # Generate description and recommendations
            description = self._generate_description(prediction, confidence)
            recommendations = self._generate_recommendations(prediction)
            
            return CrashPrediction(
                crash_type=prediction,
                confidence=confidence,
                severity=severity,
                description=description,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return self._rule_based_classify(log_text)
    
    def _rule_based_classify(self, log_text: str) -> CrashPrediction:
        """Rule-based classification fallback"""
        log_lower = log_text.lower()
        
        # Check patterns for each crash type
        for crash_type, patterns in self.crash_patterns.items():
            for pattern in patterns:
                if re.search(pattern, log_text, re.IGNORECASE):
                    severity = self._determine_severity(log_text, crash_type)
                    description = f"Rule-based classification: {crash_type}"
                    recommendations = self._generate_recommendations(crash_type)
                    
                    return CrashPrediction(
                        crash_type=crash_type,
                        confidence=0.8,  # Fixed confidence for rule-based
                        severity=severity,
                        description=description,
                        recommendations=recommendations
                    )
        
        # Default classification
        return CrashPrediction(
            crash_type="unknown",
            confidence=0.5,
            severity="medium",
            description="Unable to classify crash type",
            recommendations=["Manual investigation required"]
        )
    
    def _determine_severity(self, log_text: str, crash_type: str) -> str:
        """Determine crash severity based on text and type"""
        log_lower = log_text.lower()
        
        # Check severity indicators
        for severity, indicators in self.severity_indicators.items():
            for indicator in indicators:
                if indicator in log_lower:
                    return severity
        
        # Default severity based on crash type
        type_severity_map = {
            'system_crash': 'critical',
            'native_crash': 'critical',
            'java_exception': 'high',
            'anr': 'high',
            'oom': 'medium'
        }
        
        return type_severity_map.get(crash_type, 'medium')
    
    def _generate_description(self, crash_type: str, confidence: float) -> str:
        """Generate human-readable description"""
        descriptions = {
            'java_exception': 'Java runtime exception detected',
            'native_crash': 'Native code crash with signal',
            'anr': 'Application Not Responding detected',
            'oom': 'Out of Memory condition detected',
            'system_crash': 'System-level crash detected'
        }
        
        base_desc = descriptions.get(crash_type, f'Crash type: {crash_type}')
        return f"{base_desc} (confidence: {confidence:.2f})"
    
    def _generate_recommendations(self, crash_type: str) -> List[str]:
        """Generate recommendations based on crash type"""
        recommendations_map = {
            'java_exception': [
                "Review stack trace for null pointer access",
                "Add null checks and exception handling",
                "Validate input parameters"
            ],
            'native_crash': [
                "Analyze tombstone file for crash details",
                "Check for memory corruption or buffer overflows",
                "Review native code for unsafe operations"
            ],
            'anr': [
                "Move heavy operations off UI thread",
                "Optimize database and network operations",
                "Add progress indicators for long operations"
            ],
            'oom': [
                "Optimize memory usage and reduce allocations",
                "Implement proper bitmap recycling",
                "Use memory profiling tools"
            ],
            'system_crash': [
                "Check system logs for hardware issues",
                "Review kernel and driver compatibility",
                "Contact device manufacturer if persistent"
            ]
        }
        
        return recommendations_map.get(crash_type, ["Investigate crash cause manually"])
    
    def batch_classify(self, log_texts: List[str]) -> List[CrashPrediction]:
        """Classify multiple crashes in batch"""
        return [self.classify_crash(text) for text in log_texts]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'ml_available': ML_AVAILABLE,
            'is_trained': self.is_trained,
            'model_type': 'Naive Bayes with TF-IDF' if ML_AVAILABLE else 'Rule-based',
            'supported_types': list(self.crash_patterns.keys()),
            'model_path': str(self.model_path) if self.model_path else None
        }
