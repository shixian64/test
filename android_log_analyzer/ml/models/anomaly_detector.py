"""
Anomaly Detection Model

This module provides machine learning-based anomaly detection for Android logs.
Detects unusual patterns and behaviors that might indicate problems.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import re
from datetime import datetime, timedelta

# Try to import ML libraries with fallbacks
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_extraction.text import CountVectorizer
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    description: str
    severity: str
    recommendations: List[str]


@dataclass
class LogMetrics:
    """Log metrics for anomaly detection"""
    timestamp: datetime
    log_level: str
    tag: str
    message_length: int
    error_count: int
    warning_count: int
    frequency: float


class AnomalyDetector:
    """Machine learning-based anomaly detector for Android logs"""
    
    def __init__(self):
        self.isolation_forest = None
        self.scaler = None
        self.is_trained = False
        self.baseline_metrics = {}
        
        # Anomaly patterns
        self.anomaly_patterns = {
            'high_frequency_errors': {
                'pattern': r'(ERROR|FATAL)',
                'threshold': 10,  # errors per minute
                'severity': 'high'
            },
            'memory_pressure': {
                'pattern': r'(GC|memory|heap|oom)',
                'threshold': 5,
                'severity': 'medium'
            },
            'performance_degradation': {
                'pattern': r'(slow|timeout|lag|delay)',
                'threshold': 3,
                'severity': 'medium'
            },
            'system_instability': {
                'pattern': r'(crash|fatal|abort|panic)',
                'threshold': 2,
                'severity': 'critical'
            }
        }
        
        if ML_AVAILABLE:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the anomaly detection model"""
        if not ML_AVAILABLE:
            return
        
        # Isolation Forest for anomaly detection
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        
        # Scaler for feature normalization
        self.scaler = StandardScaler()
        
        logger.info("Initialized anomaly detection model")
    
    def extract_features(self, log_lines: List[str], time_window: int = 60) -> np.ndarray:
        """
        Extract features from log lines for anomaly detection
        
        Args:
            log_lines: List of log lines
            time_window: Time window in seconds for aggregation
            
        Returns:
            Feature matrix for anomaly detection
        """
        if not log_lines:
            return np.array([])
        
        # Parse log lines and extract metrics
        metrics = self._parse_log_metrics(log_lines)
        
        # Aggregate metrics by time windows
        windowed_metrics = self._aggregate_by_time_window(metrics, time_window)
        
        # Convert to feature matrix
        features = self._metrics_to_features(windowed_metrics)
        
        return np.array(features)
    
    def _parse_log_metrics(self, log_lines: List[str]) -> List[LogMetrics]:
        """Parse log lines and extract metrics"""
        metrics = []
        
        # Android log pattern: MM-DD HH:MM:SS.mmm PID TID LEVEL TAG: MESSAGE
        log_pattern = r'(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+\d+\s+\d+\s+([VDIWEF])\s+([^:]+):\s*(.*)'
        
        for line in log_lines:
            match = re.match(log_pattern, line)
            if match:
                timestamp_str, level, tag, message = match.groups()
                
                try:
                    # Parse timestamp (assuming current year)
                    current_year = datetime.now().year
                    timestamp = datetime.strptime(f"{current_year}-{timestamp_str}", "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    timestamp = datetime.now()
                
                # Count error indicators
                error_count = len(re.findall(r'(error|exception|fail)', message, re.IGNORECASE))
                warning_count = len(re.findall(r'(warn|slow|timeout)', message, re.IGNORECASE))
                
                metrics.append(LogMetrics(
                    timestamp=timestamp,
                    log_level=level,
                    tag=tag,
                    message_length=len(message),
                    error_count=error_count,
                    warning_count=warning_count,
                    frequency=1.0
                ))
        
        return metrics
    
    def _aggregate_by_time_window(self, metrics: List[LogMetrics], window_seconds: int) -> List[Dict[str, Any]]:
        """Aggregate metrics by time windows"""
        if not metrics:
            return []
        
        # Group metrics by time windows
        windows = defaultdict(list)
        
        start_time = min(m.timestamp for m in metrics)
        
        for metric in metrics:
            window_index = int((metric.timestamp - start_time).total_seconds() // window_seconds)
            windows[window_index].append(metric)
        
        # Aggregate each window
        aggregated = []
        
        for window_metrics in windows.values():
            if not window_metrics:
                continue
            
            # Count by log level
            level_counts = Counter(m.log_level for m in window_metrics)
            
            # Count by tag
            tag_counts = Counter(m.tag for m in window_metrics)
            
            # Aggregate features
            window_data = {
                'total_logs': len(window_metrics),
                'error_logs': level_counts.get('E', 0),
                'warning_logs': level_counts.get('W', 0),
                'info_logs': level_counts.get('I', 0),
                'debug_logs': level_counts.get('D', 0),
                'avg_message_length': np.mean([m.message_length for m in window_metrics]),
                'total_errors': sum(m.error_count for m in window_metrics),
                'total_warnings': sum(m.warning_count for m in window_metrics),
                'unique_tags': len(tag_counts),
                'top_tag_frequency': max(tag_counts.values()) if tag_counts else 0
            }
            
            aggregated.append(window_data)
        
        return aggregated
    
    def _metrics_to_features(self, windowed_metrics: List[Dict[str, Any]]) -> List[List[float]]:
        """Convert windowed metrics to feature vectors"""
        features = []
        
        for window in windowed_metrics:
            feature_vector = [
                window['total_logs'],
                window['error_logs'],
                window['warning_logs'],
                window['info_logs'],
                window['debug_logs'],
                window['avg_message_length'],
                window['total_errors'],
                window['total_warnings'],
                window['unique_tags'],
                window['top_tag_frequency'],
                # Derived features
                window['error_logs'] / max(window['total_logs'], 1),  # Error rate
                window['warning_logs'] / max(window['total_logs'], 1),  # Warning rate
                window['total_errors'] / max(window['total_logs'], 1),  # Error density
            ]
            
            features.append(feature_vector)
        
        return features
    
    def train(self, log_lines: List[str]) -> bool:
        """
        Train the anomaly detection model
        
        Args:
            log_lines: Training log lines (assumed to be normal)
            
        Returns:
            True if training successful
        """
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available for training")
            return False
        
        try:
            # Extract features
            features = self.extract_features(log_lines)
            
            if len(features) == 0:
                logger.warning("No features extracted for training")
                return False
            
            # Normalize features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train isolation forest
            self.isolation_forest.fit(features_scaled)
            
            # Store baseline metrics
            self.baseline_metrics = {
                'mean': np.mean(features_scaled, axis=0),
                'std': np.std(features_scaled, axis=0),
                'feature_count': features_scaled.shape[1]
            }
            
            self.is_trained = True
            logger.info(f"Trained anomaly detector with {len(features)} samples")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")
            return False
    
    def detect_anomalies(self, log_lines: List[str]) -> List[AnomalyResult]:
        """
        Detect anomalies in log lines
        
        Args:
            log_lines: Log lines to analyze
            
        Returns:
            List of anomaly detection results
        """
        results = []
        
        # Rule-based anomaly detection (always available)
        rule_based_results = self._rule_based_detection(log_lines)
        results.extend(rule_based_results)
        
        # ML-based detection if available and trained
        if ML_AVAILABLE and self.is_trained:
            ml_results = self._ml_based_detection(log_lines)
            results.extend(ml_results)
        
        return results
    
    def _rule_based_detection(self, log_lines: List[str]) -> List[AnomalyResult]:
        """Rule-based anomaly detection"""
        results = []
        
        # Analyze patterns over time windows
        metrics = self._parse_log_metrics(log_lines)
        windowed_metrics = self._aggregate_by_time_window(metrics, 60)  # 1-minute windows
        
        for window in windowed_metrics:
            # Check for high error rate
            error_rate = window['error_logs'] / max(window['total_logs'], 1)
            if error_rate > 0.1:  # More than 10% errors
                results.append(AnomalyResult(
                    is_anomaly=True,
                    anomaly_score=error_rate,
                    anomaly_type='high_error_rate',
                    description=f'High error rate detected: {error_rate:.2%}',
                    severity='high',
                    recommendations=[
                        'Investigate error patterns',
                        'Check for system issues',
                        'Review recent changes'
                    ]
                ))
            
            # Check for unusual log volume
            if window['total_logs'] > 1000:  # Very high log volume
                results.append(AnomalyResult(
                    is_anomaly=True,
                    anomaly_score=window['total_logs'] / 1000,
                    anomaly_type='high_log_volume',
                    description=f'Unusually high log volume: {window["total_logs"]} logs/minute',
                    severity='medium',
                    recommendations=[
                        'Check for log spam',
                        'Review logging configuration',
                        'Monitor system performance'
                    ]
                ))
        
        # Pattern-based detection
        pattern_results = self._pattern_based_detection(log_lines)
        results.extend(pattern_results)
        
        return results
    
    def _pattern_based_detection(self, log_lines: List[str]) -> List[AnomalyResult]:
        """Pattern-based anomaly detection"""
        results = []
        
        for pattern_name, pattern_config in self.anomaly_patterns.items():
            pattern = pattern_config['pattern']
            threshold = pattern_config['threshold']
            severity = pattern_config['severity']
            
            # Count pattern occurrences
            matches = []
            for line in log_lines:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(line)
            
            # Check if threshold exceeded
            if len(matches) > threshold:
                results.append(AnomalyResult(
                    is_anomaly=True,
                    anomaly_score=len(matches) / threshold,
                    anomaly_type=pattern_name,
                    description=f'Pattern "{pattern_name}" detected {len(matches)} times (threshold: {threshold})',
                    severity=severity,
                    recommendations=self._get_pattern_recommendations(pattern_name)
                ))
        
        return results
    
    def _ml_based_detection(self, log_lines: List[str]) -> List[AnomalyResult]:
        """ML-based anomaly detection"""
        results = []
        
        try:
            # Extract features
            features = self.extract_features(log_lines)
            
            if len(features) == 0:
                return results
            
            # Normalize features
            features_scaled = self.scaler.transform(features)
            
            # Predict anomalies
            predictions = self.isolation_forest.predict(features_scaled)
            scores = self.isolation_forest.decision_function(features_scaled)
            
            # Process results
            for i, (prediction, score) in enumerate(zip(predictions, scores)):
                if prediction == -1:  # Anomaly detected
                    results.append(AnomalyResult(
                        is_anomaly=True,
                        anomaly_score=abs(score),
                        anomaly_type='ml_detected_anomaly',
                        description=f'ML model detected anomaly in time window {i+1}',
                        severity=self._score_to_severity(abs(score)),
                        recommendations=[
                            'Review logs in this time period',
                            'Check for unusual system behavior',
                            'Correlate with external events'
                        ]
                    ))
            
        except Exception as e:
            logger.error(f"ML-based anomaly detection failed: {e}")
        
        return results
    
    def _get_pattern_recommendations(self, pattern_name: str) -> List[str]:
        """Get recommendations for specific pattern anomalies"""
        recommendations_map = {
            'high_frequency_errors': [
                'Investigate error root causes',
                'Check system stability',
                'Review error handling'
            ],
            'memory_pressure': [
                'Monitor memory usage',
                'Optimize memory allocations',
                'Check for memory leaks'
            ],
            'performance_degradation': [
                'Profile application performance',
                'Check system resources',
                'Optimize slow operations'
            ],
            'system_instability': [
                'Check system logs',
                'Review recent changes',
                'Monitor hardware health'
            ]
        }
        
        return recommendations_map.get(pattern_name, ['Investigate anomaly manually'])
    
    def _score_to_severity(self, score: float) -> str:
        """Convert anomaly score to severity level"""
        if score > 0.5:
            return 'critical'
        elif score > 0.3:
            return 'high'
        elif score > 0.1:
            return 'medium'
        else:
            return 'low'
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get anomaly detector status"""
        return {
            'ml_available': ML_AVAILABLE,
            'is_trained': self.is_trained,
            'baseline_metrics': self.baseline_metrics,
            'supported_patterns': list(self.anomaly_patterns.keys())
        }
