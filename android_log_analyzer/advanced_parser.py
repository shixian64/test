"""
Advanced Android Log Parser for Complex Log Structures

This module handles complex log structures like SPRD ylog packages,
supporting multiple subsystems and nested archive formats.
"""

import gzip
import json
import logging
import re
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

from .config import ConfigManager
from .log_analyzer import LogEntry, parse_log_line
from .utils import PerformanceMonitor, safe_file_size, validate_log_file

logger = logging.getLogger(__name__)


class LogSubsystem:
    """Represents a log subsystem (AP, Modem, Audio, etc.)"""

    def __init__(self, name: str, path: Path, log_type: str):
        self.name = name
        self.path = path
        self.log_type = log_type
        self.files: List[Path] = []
        self.issues: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}


class AdvancedLogParser:
    """Advanced parser for complex Android log structures"""

    # SPRD/Unisoc log file patterns
    SPRD_LOG_PATTERNS = {
        "android_main": r".*android(_main)?\.log$",
        "android_system": r".*android_system\.log$",
        "android_events": r".*android_events\.log$",
        "android_radio": r".*android_radio\.log$",
        "kernel": r".*kernel\.log$",
        "modem": r".*md_\d+.*\.log$",
        "audio": r".*ag_\d+.*\.log$",
        "connectivity": r".*wcn_\d+.*\.log$",
        "sensor": r".*sp_\d+.*\.log$",
        "lastlog": r".*lastlog\.log$",
        "lastkmsg": r".*lastkmsg\.log$",
        "ylog_debug": r".*ylogdebug\.log$",
        "slog_debug": r".*slogdbg_.*\.log$",
    }

    # Critical file patterns for priority analysis
    CRITICAL_FILES = {"android_main", "android_system", "kernel", "lastlog", "lastkmsg"}

    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
        self.subsystems: Dict[str, LogSubsystem] = {}
        self.monitor = PerformanceMonitor()

    def analyze_log_package(self, package_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze a complete log package (zip/tar containing multiple logs)

        Args:
            package_path: Path to the log package

        Returns:
            Comprehensive analysis results
        """
        package_path = Path(package_path)
        logger.info(f"Analyzing log package: {package_path}")

        # Extract and categorize files
        extracted_files = self._extract_package(package_path)
        self._categorize_files(extracted_files)

        # Analyze each subsystem
        analysis_results = {
            "package_info": {
                "name": package_path.name,
                "size": safe_file_size(package_path),
                "total_files": len(extracted_files),
                "subsystems": list(self.subsystems.keys()),
            },
            "subsystem_analysis": {},
            "critical_issues": [],
            "summary": {},
            "timeline": [],
            "performance_metrics": {},
        }

        # Analyze critical files first
        critical_issues = self._analyze_critical_files()
        analysis_results["critical_issues"] = critical_issues

        # Analyze each subsystem
        for name, subsystem in self.subsystems.items():
            logger.info(f"Analyzing subsystem: {name}")
            subsystem_result = self._analyze_subsystem(subsystem)
            analysis_results["subsystem_analysis"][name] = subsystem_result

        # Generate timeline and summary
        analysis_results["timeline"] = self._generate_timeline()
        analysis_results["summary"] = self._generate_summary(analysis_results)
        analysis_results["performance_metrics"] = self.monitor.get_summary()

        return analysis_results

    def _extract_package(self, package_path: Path) -> List[Path]:
        """Extract files from package and return list of extracted files"""
        extracted_files = []
        extract_dir = package_path.parent / f"{package_path.stem}_extracted"

        try:
            if package_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(package_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif package_path.suffix.lower() in [".tar", ".tar.gz", ".tgz"]:
                with tarfile.open(package_path, "r:*") as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                # Single file
                return [package_path]

            # Recursively find all log files
            for file_path in extract_dir.rglob("*"):
                if file_path.is_file() and self._is_log_file(file_path):
                    extracted_files.append(file_path)

        except Exception as e:
            logger.error(f"Error extracting package {package_path}: {e}")

        return extracted_files

    def _is_log_file(self, file_path: Path) -> bool:
        """Check if file is a log file based on extension and content"""
        log_extensions = {".log", ".txt", ".cap", ".csv"}

        # Check extension
        if file_path.suffix.lower() in log_extensions:
            return True

        # Check if it's a compressed log
        if file_path.suffix.lower() in {".gz", ".bz2"}:
            stem = file_path.stem
            if any(ext in stem for ext in [".log", ".txt"]):
                return True

        # Check content for small files
        if file_path.stat().st_size < 1024 * 1024:  # 1MB
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    first_line = f.readline()
                    # Look for log-like patterns
                    if re.search(r"\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", first_line):
                        return True
            except:
                pass

        return False

    def _categorize_files(self, files: List[Path]) -> None:
        """Categorize files into subsystems"""
        for file_path in files:
            categorized = False

            for log_type, pattern in self.SPRD_LOG_PATTERNS.items():
                if re.search(pattern, str(file_path), re.IGNORECASE):
                    subsystem_name = self._get_subsystem_name(log_type)

                    if subsystem_name not in self.subsystems:
                        self.subsystems[subsystem_name] = LogSubsystem(
                            subsystem_name, file_path.parent, log_type
                        )

                    self.subsystems[subsystem_name].files.append(file_path)
                    categorized = True
                    break

            if not categorized:
                # Create 'other' subsystem for uncategorized files
                if "other" not in self.subsystems:
                    self.subsystems["other"] = LogSubsystem(
                        "other", file_path.parent, "unknown"
                    )
                self.subsystems["other"].files.append(file_path)

    def _get_subsystem_name(self, log_type: str) -> str:
        """Map log type to subsystem name"""
        mapping = {
            "android_main": "android",
            "android_system": "android",
            "android_events": "android",
            "android_radio": "android",
            "kernel": "kernel",
            "modem": "modem",
            "audio": "audio",
            "connectivity": "connectivity",
            "sensor": "sensor",
            "lastlog": "system",
            "lastkmsg": "system",
            "ylog_debug": "debug",
            "slog_debug": "debug",
        }
        return mapping.get(log_type, "other")

    def _analyze_critical_files(self) -> List[Dict[str, Any]]:
        """Analyze critical files first for immediate issues"""
        critical_issues = []

        for subsystem in self.subsystems.values():
            for file_path in subsystem.files:
                if any(
                    pattern in str(file_path).lower() for pattern in self.CRITICAL_FILES
                ):
                    try:
                        issues = self._quick_analyze_file(file_path)
                        for issue in issues:
                            issue["source_file"] = str(file_path)
                            issue["subsystem"] = subsystem.name
                            issue["priority"] = "critical"
                        critical_issues.extend(issues)
                    except Exception as e:
                        logger.error(f"Error analyzing critical file {file_path}: {e}")

        return critical_issues

    def _quick_analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Quick analysis of a single file for critical issues"""
        from .log_analyzer import read_log_file

        try:
            # Use existing analyzer for now, can be enhanced later
            return read_log_file(file_path)
        except Exception as e:
            logger.error(f"Error in quick analysis of {file_path}: {e}")
            return []

    def _analyze_subsystem(self, subsystem: LogSubsystem) -> Dict[str, Any]:
        """Analyze a complete subsystem"""
        result = {
            "name": subsystem.name,
            "file_count": len(subsystem.files),
            "total_size": sum(safe_file_size(f) for f in subsystem.files),
            "issues": [],
            "statistics": {},
            "timeline": [],
        }

        # Analyze each file in the subsystem
        for file_path in subsystem.files:
            try:
                file_issues = self._quick_analyze_file(file_path)
                for issue in file_issues:
                    issue["source_file"] = str(file_path)
                    issue["subsystem"] = subsystem.name
                result["issues"].extend(file_issues)

                self.monitor.increment("files_processed")

            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")
                self.monitor.increment("errors_encountered")

        # Generate subsystem statistics
        result["statistics"] = self._generate_subsystem_stats(result["issues"])

        return result

    def _generate_subsystem_stats(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics for a subsystem"""
        stats = {
            "total_issues": len(issues),
            "issue_types": {},
            "severity_distribution": {},
            "time_range": None,
        }

        for issue in issues:
            # Count issue types
            issue_type = issue.get("type", "unknown")
            stats["issue_types"][issue_type] = (
                stats["issue_types"].get(issue_type, 0) + 1
            )

            # Count severity (if available)
            severity = issue.get("severity", "medium")
            stats["severity_distribution"][severity] = (
                stats["severity_distribution"].get(severity, 0) + 1
            )

        return stats

    def _generate_timeline(self) -> List[Dict[str, Any]]:
        """Generate timeline of events across all subsystems"""
        timeline = []

        for subsystem in self.subsystems.values():
            for issue in subsystem.issues:
                if "timestamp" in issue:
                    timeline.append(
                        {
                            "timestamp": issue["timestamp"],
                            "subsystem": subsystem.name,
                            "type": issue.get("type", "unknown"),
                            "description": issue.get("message", "No description"),
                            "severity": issue.get("severity", "medium"),
                        }
                    )

        # Sort by timestamp
        timeline.sort(key=lambda x: x.get("timestamp", ""))

        return timeline

    def _generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary of the analysis"""
        total_issues = sum(
            len(subsys.get("issues", []))
            for subsys in analysis_results["subsystem_analysis"].values()
        )

        summary = {
            "total_issues": total_issues,
            "critical_issues": len(analysis_results["critical_issues"]),
            "subsystems_analyzed": len(self.subsystems),
            "most_problematic_subsystem": None,
            "issue_distribution": {},
            "recommendations": [],
        }

        # Find most problematic subsystem
        max_issues = 0
        for name, subsys in analysis_results["subsystem_analysis"].items():
            issue_count = len(subsys.get("issues", []))
            if issue_count > max_issues:
                max_issues = issue_count
                summary["most_problematic_subsystem"] = name

        # Generate recommendations
        if summary["critical_issues"] > 0:
            summary["recommendations"].append(
                "Critical issues found - immediate attention required"
            )

        if summary["total_issues"] > 100:
            summary["recommendations"].append(
                "High issue count - consider system stability review"
            )

        return summary
