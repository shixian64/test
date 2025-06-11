"""
Pattern Recognition Engine

This module provides advanced pattern recognition for Android logs using
machine learning and statistical analysis to identify recurring issues,
trends, and behavioral patterns.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import hashlib

# Try to import ML libraries
try:
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Detected pattern information"""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    severity: str
    examples: List[str]
    first_seen: datetime
    last_seen: datetime
    recommendations: List[str]


@dataclass
class PatternCluster:
    """Cluster of similar patterns"""

    cluster_id: str
    patterns: List[Pattern]
    centroid_description: str
    total_frequency: int
    severity: str


class PatternRecognizer:
    """Advanced pattern recognition engine for Android logs"""

    def __init__(self):
        self.known_patterns = {}
        self.pattern_history = defaultdict(list)
        self.vectorizer = None
        self.clusterer = None

        # Pre-defined pattern templates
        self.pattern_templates = {
            "crash_sequence": {
                "patterns": [
                    r"FATAL EXCEPTION.*",
                    r"Process.*crashed",
                    r"ActivityManager.*killing",
                ],
                "description": "Application crash sequence",
                "severity": "critical",
            },
            "memory_pressure": {
                "patterns": [
                    r"GC.*freed.*",
                    r"Low memory killer.*",
                    r"OutOfMemoryError.*",
                ],
                "description": "Memory pressure indicators",
                "severity": "high",
            },
            "performance_degradation": {
                "patterns": [
                    r"Choreographer.*skipped.*frames",
                    r"ActivityManager.*slow operation",
                    r"Input.*timeout",
                ],
                "description": "Performance degradation signs",
                "severity": "medium",
            },
            "network_issues": {
                "patterns": [
                    r"ConnectException.*",
                    r"SocketTimeoutException.*",
                    r"UnknownHostException.*",
                ],
                "description": "Network connectivity problems",
                "severity": "medium",
            },
            "system_instability": {
                "patterns": [
                    r"Watchdog.*triggered",
                    r"System server.*crashed",
                    r"Kernel panic.*",
                ],
                "description": "System instability indicators",
                "severity": "critical",
            },
        }

        if ML_AVAILABLE:
            self._initialize_ml_components()

    def _initialize_ml_components(self):
        """Initialize machine learning components"""
        # TF-IDF vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(
            max_features=500, ngram_range=(1, 3), stop_words="english", lowercase=True
        )

        # DBSCAN for clustering similar patterns
        self.clusterer = DBSCAN(eps=0.3, min_samples=2, metric="cosine")

        logger.info("Initialized ML components for pattern recognition")

    def recognize_patterns(self, log_lines: List[str]) -> List[Pattern]:
        """
        Recognize patterns in log lines

        Args:
            log_lines: List of log lines to analyze

        Returns:
            List of recognized patterns
        """
        patterns = []

        # Template-based pattern recognition
        template_patterns = self._recognize_template_patterns(log_lines)
        patterns.extend(template_patterns)

        # Frequency-based pattern recognition
        frequency_patterns = self._recognize_frequency_patterns(log_lines)
        patterns.extend(frequency_patterns)

        # ML-based pattern recognition
        if ML_AVAILABLE:
            ml_patterns = self._recognize_ml_patterns(log_lines)
            patterns.extend(ml_patterns)

        # Sequence pattern recognition
        sequence_patterns = self._recognize_sequence_patterns(log_lines)
        patterns.extend(sequence_patterns)

        # Deduplicate and merge similar patterns
        patterns = self._deduplicate_patterns(patterns)

        return patterns

    def _recognize_template_patterns(self, log_lines: List[str]) -> List[Pattern]:
        """Recognize patterns using predefined templates"""
        patterns = []

        for template_name, template_config in self.pattern_templates.items():
            template_patterns = template_config["patterns"]
            matches = []

            for line in log_lines:
                for pattern in template_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append(line)
                        break

            if matches:
                pattern_id = self._generate_pattern_id(template_name, matches)

                patterns.append(
                    Pattern(
                        pattern_id=pattern_id,
                        pattern_type="template",
                        description=template_config["description"],
                        frequency=len(matches),
                        confidence=0.9,  # High confidence for template matches
                        severity=template_config["severity"],
                        examples=matches[:5],  # First 5 examples
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        recommendations=self._get_template_recommendations(
                            template_name
                        ),
                    )
                )

        return patterns

    def _recognize_frequency_patterns(self, log_lines: List[str]) -> List[Pattern]:
        """Recognize patterns based on frequency analysis"""
        patterns = []

        # Extract log messages (remove timestamps, PIDs, etc.)
        messages = []
        for line in log_lines:
            # Extract message part after tag
            match = re.search(r"[VDIWEF]\s+[^:]+:\s*(.*)", line)
            if match:
                message = match.group(1)
                # Normalize message (replace numbers and specific values)
                normalized = self._normalize_message(message)
                messages.append((normalized, line))

        # Count message frequencies
        message_counts = Counter(msg[0] for msg in messages)

        # Identify frequent patterns (appearing more than threshold)
        threshold = max(3, len(log_lines) // 100)  # At least 3 or 1% of logs

        for normalized_msg, count in message_counts.items():
            if count >= threshold:
                # Get original examples
                examples = [msg[1] for msg in messages if msg[0] == normalized_msg]

                pattern_id = self._generate_pattern_id("frequency", [normalized_msg])

                patterns.append(
                    Pattern(
                        pattern_id=pattern_id,
                        pattern_type="frequency",
                        description=f"Frequent message pattern: {normalized_msg[:100]}...",
                        frequency=count,
                        confidence=min(0.8, count / len(log_lines)),
                        severity=self._infer_severity(normalized_msg),
                        examples=examples[:5],
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        recommendations=self._get_frequency_recommendations(
                            normalized_msg
                        ),
                    )
                )

        return patterns

    def _recognize_ml_patterns(self, log_lines: List[str]) -> List[Pattern]:
        """Recognize patterns using machine learning clustering"""
        patterns = []

        if not ML_AVAILABLE or len(log_lines) < 10:
            return patterns

        try:
            # Extract and normalize messages
            messages = []
            original_lines = []

            for line in log_lines:
                match = re.search(r"[VDIWEF]\s+[^:]+:\s*(.*)", line)
                if match:
                    message = match.group(1)
                    normalized = self._normalize_message(message)
                    if len(normalized) > 10:  # Filter out very short messages
                        messages.append(normalized)
                        original_lines.append(line)

            if len(messages) < 5:
                return patterns

            # Vectorize messages
            tfidf_matrix = self.vectorizer.fit_transform(messages)

            # Cluster similar messages
            clusters = self.clusterer.fit_predict(tfidf_matrix.toarray())

            # Process clusters
            cluster_groups = defaultdict(list)
            for i, cluster_id in enumerate(clusters):
                if cluster_id != -1:  # Ignore noise points
                    cluster_groups[cluster_id].append((messages[i], original_lines[i]))

            # Create patterns from clusters
            for cluster_id, cluster_items in cluster_groups.items():
                if len(cluster_items) >= 2:  # At least 2 items in cluster
                    cluster_messages = [item[0] for item in cluster_items]
                    cluster_examples = [item[1] for item in cluster_items]

                    # Find common terms in cluster
                    common_description = self._find_common_terms(cluster_messages)

                    pattern_id = self._generate_pattern_id(
                        "ml_cluster", cluster_messages
                    )

                    patterns.append(
                        Pattern(
                            pattern_id=pattern_id,
                            pattern_type="ml_cluster",
                            description=f"ML-detected pattern: {common_description}",
                            frequency=len(cluster_items),
                            confidence=0.7,
                            severity=self._infer_severity(common_description),
                            examples=cluster_examples[:5],
                            first_seen=datetime.now(),
                            last_seen=datetime.now(),
                            recommendations=[
                                "Investigate clustered messages for common cause"
                            ],
                        )
                    )

        except Exception as e:
            logger.error(f"ML pattern recognition failed: {e}")

        return patterns

    def _recognize_sequence_patterns(self, log_lines: List[str]) -> List[Pattern]:
        """Recognize sequential patterns in logs"""
        patterns = []

        # Look for common sequences (e.g., crash sequences)
        sequences = []
        current_sequence = []

        for line in log_lines:
            # Extract log level and tag
            match = re.search(r"([VDIWEF])\s+([^:]+):", line)
            if match:
                level, tag = match.groups()
                current_sequence.append((level, tag, line))

                # Limit sequence length
                if len(current_sequence) > 10:
                    current_sequence.pop(0)

                # Check for known sequence patterns
                if len(current_sequence) >= 3:
                    sequence_pattern = self._check_sequence_pattern(current_sequence)
                    if sequence_pattern:
                        sequences.append(sequence_pattern)

        # Create patterns from sequences
        sequence_counts = Counter(seq["type"] for seq in sequences)

        for seq_type, count in sequence_counts.items():
            if count >= 2:  # At least 2 occurrences
                examples = [
                    seq["example"] for seq in sequences if seq["type"] == seq_type
                ]

                pattern_id = self._generate_pattern_id("sequence", [seq_type])

                patterns.append(
                    Pattern(
                        pattern_id=pattern_id,
                        pattern_type="sequence",
                        description=f"Sequential pattern: {seq_type}",
                        frequency=count,
                        confidence=0.8,
                        severity="high",  # Sequences often indicate problems
                        examples=examples[:5],
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        recommendations=[f"Investigate {seq_type} sequence pattern"],
                    )
                )

        return patterns

    def _normalize_message(self, message: str) -> str:
        """Normalize log message for pattern matching"""
        # Replace numbers with placeholder
        normalized = re.sub(r"\b\d+\b", "<NUM>", message)

        # Replace hex addresses
        normalized = re.sub(r"0x[0-9a-fA-F]+", "<ADDR>", normalized)

        # Replace file paths
        normalized = re.sub(r"/[^\s]+", "<PATH>", normalized)

        # Replace timestamps
        normalized = re.sub(r"\d{2}:\d{2}:\d{2}", "<TIME>", normalized)

        # Replace package names
        normalized = re.sub(r"com\.[a-zA-Z0-9.]+", "<PACKAGE>", normalized)

        return normalized.strip()

    def _check_sequence_pattern(
        self, sequence: List[Tuple[str, str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Check if sequence matches known patterns"""
        # Extract levels and tags
        levels = [item[0] for item in sequence]
        tags = [item[1] for item in sequence]

        # Check for crash sequence: E -> E -> I (Error -> Error -> Info/Kill)
        if len(levels) >= 3 and levels[-3:] == ["E", "E", "I"]:
            if any("AndroidRuntime" in tag for tag in tags[-3:]):
                return {
                    "type": "crash_sequence",
                    "example": " -> ".join(
                        item[2][:50] + "..." for item in sequence[-3:]
                    ),
                }

        # Check for ANR sequence
        if any("ANR" in item[2] for item in sequence):
            return {
                "type": "anr_sequence",
                "example": " -> ".join(item[2][:50] + "..." for item in sequence[-3:]),
            }

        return None

    def _find_common_terms(self, messages: List[str]) -> str:
        """Find common terms in a list of messages"""
        if not messages:
            return "Unknown pattern"

        # Split messages into words
        all_words = []
        for message in messages:
            words = re.findall(r"\w+", message.lower())
            all_words.extend(words)

        # Find most common words (excluding very common ones)
        common_words = ["the", "and", "or", "in", "on", "at", "to", "for", "of", "with"]
        word_counts = Counter(
            word for word in all_words if word not in common_words and len(word) > 2
        )

        # Get top 3 most common words
        top_words = [word for word, count in word_counts.most_common(3)]

        return " ".join(top_words) if top_words else messages[0][:50]

    def _infer_severity(self, message: str) -> str:
        """Infer severity from message content"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["fatal", "crash", "panic", "abort"]):
            return "critical"
        elif any(word in message_lower for word in ["error", "exception", "fail"]):
            return "high"
        elif any(word in message_lower for word in ["warn", "slow", "timeout"]):
            return "medium"
        else:
            return "low"

    def _generate_pattern_id(self, pattern_type: str, content: List[str]) -> str:
        """Generate unique pattern ID"""
        content_str = "".join(content)
        hash_obj = hashlib.md5(content_str.encode())
        return f"{pattern_type}_{hash_obj.hexdigest()[:8]}"

    def _get_template_recommendations(self, template_name: str) -> List[str]:
        """Get recommendations for template patterns"""
        recommendations_map = {
            "crash_sequence": [
                "Analyze crash stack trace",
                "Check for null pointer exceptions",
                "Review recent code changes",
            ],
            "memory_pressure": [
                "Monitor memory usage",
                "Optimize memory allocations",
                "Check for memory leaks",
            ],
            "performance_degradation": [
                "Profile application performance",
                "Optimize UI operations",
                "Check for blocking operations",
            ],
            "network_issues": [
                "Check network connectivity",
                "Review API endpoints",
                "Implement retry mechanisms",
            ],
            "system_instability": [
                "Check system logs",
                "Review hardware status",
                "Contact system administrator",
            ],
        }

        return recommendations_map.get(template_name, ["Investigate pattern manually"])

    def _get_frequency_recommendations(self, message: str) -> List[str]:
        """Get recommendations for frequent patterns"""
        if "error" in message.lower():
            return ["Investigate frequent error cause", "Add error handling"]
        elif "timeout" in message.lower():
            return ["Optimize timeout operations", "Check network conditions"]
        else:
            return [
                "Review frequent message pattern",
                "Consider reducing log verbosity",
            ]

    def _deduplicate_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Remove duplicate patterns"""
        seen_ids = set()
        unique_patterns = []

        for pattern in patterns:
            if pattern.pattern_id not in seen_ids:
                seen_ids.add(pattern.pattern_id)
                unique_patterns.append(pattern)

        return unique_patterns

    def cluster_patterns(self, patterns: List[Pattern]) -> List[PatternCluster]:
        """Cluster similar patterns together"""
        if not patterns or not ML_AVAILABLE:
            return []

        clusters = []

        try:
            # Extract pattern descriptions
            descriptions = [pattern.description for pattern in patterns]

            # Vectorize descriptions
            tfidf_matrix = self.vectorizer.fit_transform(descriptions)

            # Cluster patterns
            cluster_labels = self.clusterer.fit_predict(tfidf_matrix.toarray())

            # Group patterns by cluster
            cluster_groups = defaultdict(list)
            for i, cluster_id in enumerate(cluster_labels):
                if cluster_id != -1:
                    cluster_groups[cluster_id].append(patterns[i])

            # Create pattern clusters
            for cluster_id, cluster_patterns in cluster_groups.items():
                total_frequency = sum(p.frequency for p in cluster_patterns)
                max_severity = max(
                    cluster_patterns,
                    key=lambda p: ["low", "medium", "high", "critical"].index(
                        p.severity
                    ),
                ).severity

                clusters.append(
                    PatternCluster(
                        cluster_id=f"cluster_{cluster_id}",
                        patterns=cluster_patterns,
                        centroid_description=self._find_common_terms(
                            [p.description for p in cluster_patterns]
                        ),
                        total_frequency=total_frequency,
                        severity=max_severity,
                    )
                )

        except Exception as e:
            logger.error(f"Pattern clustering failed: {e}")

        return clusters

    def get_pattern_statistics(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """Get statistics about recognized patterns"""
        if not patterns:
            return {}

        return {
            "total_patterns": len(patterns),
            "pattern_types": Counter(p.pattern_type for p in patterns),
            "severity_distribution": Counter(p.severity for p in patterns),
            "total_frequency": sum(p.frequency for p in patterns),
            "avg_confidence": sum(p.confidence for p in patterns) / len(patterns),
            "most_frequent": max(patterns, key=lambda p: p.frequency).description,
        }
