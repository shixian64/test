"""
Smart Search Engine for Android Log Analyzer

This module provides intelligent search capabilities including:
- Natural language query processing
- Semantic search
- Query suggestions
- Pattern matching
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """Types of search queries"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    PATTERN = "pattern"


@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    line_number: int
    content: str
    relevance_score: float
    match_type: SearchType
    context_lines: List[str]
    highlights: List[Tuple[int, int]]


@dataclass
class QuerySuggestion:
    """Query suggestion with confidence score"""
    suggestion: str
    confidence: float
    category: str
    description: str


class SmartSearchEngine:
    """Intelligent search engine for log analysis"""
    
    def __init__(self):
        self.patterns = {
            'crash': {
                'keywords': ['crash', 'exception', 'fatal', 'abort'],
                'patterns': [r'FATAL EXCEPTION', r'java\.lang\.\w*Exception']
            },
            'memory': {
                'keywords': ['oom', 'memory', 'gc', 'heap'],
                'patterns': [r'OutOfMemoryError', r'Low memory killer']
            },
            'performance': {
                'keywords': ['slow', 'lag', 'timeout', 'anr'],
                'patterns': [r'ANR in.*', r'timeout.*ms']
            }
        }
        
        self.common_queries = [
            "show all crashes",
            "find memory issues", 
            "performance problems"
        ]
    
    def smart_search(self, query: str, logs: List[str], max_results: int = 100) -> List[SearchResult]:
        """Perform intelligent search across log lines"""
        results = []
        query_lower = query.lower()
        
        for i, line in enumerate(logs):
            if query_lower in line.lower():
                results.append(SearchResult(
                    line_number=i + 1,
                    content=line,
                    relevance_score=1.0,
                    match_type=SearchType.EXACT,
                    context_lines=[],
                    highlights=[(line.lower().find(query_lower), 
                               line.lower().find(query_lower) + len(query_lower))]
                ))
        
        return results[:max_results]
    
    def suggest_queries(self, partial_query: str) -> List[QuerySuggestion]:
        """Generate query suggestions"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        for query in self.common_queries:
            if partial_lower in query.lower():
                confidence = len(partial_lower) / len(query)
                suggestions.append(QuerySuggestion(
                    suggestion=query,
                    confidence=confidence,
                    category="common",
                    description=f"Common search: {query}"
                ))
        
        return suggestions[:10]
