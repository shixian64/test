"""
Issue Priority Scoring System

This module provides intelligent priority scoring for detected issues.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Issue priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    @classmethod
    def from_score(cls, score: int) -> 'Priority':
        """Convert numeric score to priority level"""
        if score >= 90:
            return cls.CRITICAL
        elif score >= 70:
            return cls.HIGH
        elif score >= 40:
            return cls.MEDIUM
        else:
            return cls.LOW


@dataclass
class IssueContext:
    """Additional context for priority calculation"""
    app_version: Optional[str] = None
    user_count_affected: int = 0
    release_stage: str = "production"


@dataclass
class PriorityFactors:
    """Factors that influence issue priority"""
    severity_weight: float = 0.3
    frequency_weight: float = 0.25
    system_impact_weight: float = 0.2
    user_impact_weight: float = 0.15
    business_impact_weight: float = 0.1


class IssuePriorityScorer:
    """Intelligent priority scoring system for log issues"""
    
    def __init__(self, factors: Optional[PriorityFactors] = None):
        self.factors = factors or PriorityFactors()
        
        self.severity_scores = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }
    
    def calculate_priority(self, issue: Dict[str, Any], context: Optional[IssueContext] = None) -> Dict[str, Any]:
        """Calculate comprehensive priority score for an issue"""
        context = context or IssueContext()
        
        # Simple scoring for demo
        severity = issue.get('severity', 'medium')
        frequency = issue.get('frequency', 0)
        
        base_score = self.severity_scores.get(severity, 50)
        frequency_bonus = min(frequency * 2, 30)
        total_score = base_score + frequency_bonus
        
        priority = Priority.from_score(int(total_score))
        
        return {
            'priority': priority.value,
            'total_score': total_score,
            'breakdown': {
                'severity_score': base_score,
                'frequency_score': frequency_bonus,
                'system_impact_score': 50,
                'user_impact_score': 50,
                'business_impact_score': 50
            },
            'recommendations': [
                f"Address this {priority.value} priority issue",
                "Review and fix the underlying cause",
                "Monitor for similar issues"
            ]
        }
    
    def batch_prioritize(self, issues: List[Dict[str, Any]], context: Optional[IssueContext] = None) -> List[Dict[str, Any]]:
        """Prioritize a batch of issues"""
        prioritized_issues = []
        
        for issue in issues:
            priority_info = self.calculate_priority(issue, context)
            issue_with_priority = {**issue, **priority_info}
            prioritized_issues.append(issue_with_priority)
        
        prioritized_issues.sort(key=lambda x: x['total_score'], reverse=True)
        return prioritized_issues
    
    def get_priority_distribution(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of priorities across issues"""
        distribution = {priority.value: 0 for priority in Priority}
        
        for issue in issues:
            if 'priority' in issue:
                distribution[issue['priority']] += 1
        
        return distribution
