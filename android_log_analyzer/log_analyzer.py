"""
Android Log Analyzer

This script parses and analyzes Android logcat files to detect common critical issues
such as Java crashes, Application Not Responding (ANR) errors, native crashes,
and various system-level errors (kernel panics, watchdog timeouts, etc.).

It uses a configurable set of patterns (ISSUE_PATTERNS) to identify these issues
and generates a summary report of its findings.
"""
import argparse
import gzip
import json
import logging
import os
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import intelligent features if available
try:
    from .intelligent.smart_search import SmartSearchEngine
    from .intelligent.priority_scorer import IssuePriorityScorer, IssueContext
    INTELLIGENT_FEATURES_AVAILABLE = True
    logger.info("Intelligent features loaded successfully")
except ImportError:
    INTELLIGENT_FEATURES_AVAILABLE = False
    logger.debug("Intelligent features not available")

# Import ML features if available
try:
    from .ml import create_ml_analyzer, get_ml_capabilities, ML_DEPENDENCIES_AVAILABLE
    from .ml.models.crash_classifier import CrashClassifier
    from .ml.models.anomaly_detector import AnomalyDetector
    from .ml.models.pattern_recognizer import PatternRecognizer
    ML_FEATURES_AVAILABLE = True
    logger.info("ML features loaded successfully")
except ImportError:
    ML_FEATURES_AVAILABLE = False
    logger.debug("ML features not available")

# --- Configuration for Issue Detection ---

# ISSUE_PATTERNS defines the rules for detecting various log issues.
# Structure:
#   "issue_category": {
#       "tags": [list of log tags to check, case-sensitive],
#       "message_keywords": [list of keywords to find in the log message],
#       "extractors": { (optional)
#           "data_to_extract": r"regex_pattern_with_capture_group"
#       }
#   },
#   "system_error": { # Special category for nested system error types
#       "subtype_name": { "tags": [...], "message_keywords": [...] },
#       ...
#   }
#
# TODO: Future enhancement - Load platform-specific patterns (MTK, SPRD, Google) here,
# potentially merging them with or overriding these defaults.
ISSUE_PATTERNS: Dict[str, Any] = {
    "java_crash": {
        "tags": ["AndroidRuntime"], # Tag where Java crash signatures appear
        "message_keywords": ["FATAL EXCEPTION"], # Primary indicator of a Java crash
    },
    "anr": {
        "tags": ["ActivityManager"], # Tag for ANR messages
        "message_keywords": ["ANR in"], # Common start of an ANR message
        "extractors": {
            # Regex to capture the process name involved in the ANR
            "process_name": r"ANR in ([^ ]+)", 
            # Regex to capture the reason for the ANR (often follows "reason:")
            "reason": r"reason: (.*)" 
        }
    },
    "native_crash_hint": {
        "tags": ["DEBUG", "libc", "bionic"], # Tags often associated with native crashes
        # Keywords indicating a native crash (e.g., signal info or crash dump header)
        "message_keywords": ["Fatal signal", "*** ***"],
        "extractors": {
            # Regex to capture signal information (e.g., "Fatal signal 11 (SIGSEGV)")
            "signal_info": r"(Fatal signal \d+ \(SIG[A-Z]+\)|signal \d+ \(SIG[A-Z]+\))",
            # Regex to capture process/thread ID and name (e.g., "pid: 123, tid: 456, name: com.example.app")
            "process_info": r"(pid: \d+, tid: \d+, name: [^ ]+ >>> [^ ]+ <<<|pid: \d+, tid: \d+, name: [^ ]+)"
        }
    },
    "memory_issue": {
        "tags": ["lowmemorykiller", "ActivityManager", "kernel"],
        "message_keywords": ["Low memory", "low memory", "Out of memory", "Killed process", "Killing"],
        "extractors": {
            "killed_process": r"(?:Killed process \d+ \(([^)]+)\)|Killing '([^']+)')",
            "oom_reason": r"(Out of memory|[Ll]ow memory)"
        }
    },
    "system_error": { # Grouping for various low-level system issues
        "kernel_panic": {
            "tags": ["kernel"],
            "message_keywords": ["Kernel panic", "BUG:", "Oops"] # Indicators of kernel issues
        },
        "watchdog": {
            "tags": ["watchdog"], 
            "message_keywords": ["Watchdog triggered", "!@SyncMonitor"] # Watchdog timeout indicators
        },
        "system_server_crash": {
            "tags": ["SystemServer"], 
            "message_keywords": ["crashed"] # Indication that SystemServer process has crashed
        },
        "misc_critical": { # For other critical hardware/system messages
            "tags": [], # Empty means check any tag for these keywords
            "message_keywords": ["HAL frozen", "modem crashed", "DSP failure"]
        }
    }
}

# Pre-compile regexes in ISSUE_PATTERNS for efficiency.
# This is done once when the script loads.
for issue_type, patterns in ISSUE_PATTERNS.items():
    if "extractors" in patterns:
        for key, regex_str in patterns["extractors"].items():
            # ANR reason extraction should be case-insensitive for "reason: ..."
            if issue_type == "anr" and key == "reason":
                patterns["extractors"][key] = re.compile(regex_str, re.IGNORECASE)
            else:
                patterns["extractors"][key] = re.compile(regex_str)
    # Pre-compile for nested system_error patterns as well (if they had extractors)
    if issue_type == "system_error": 
        for sub_type, sub_patterns in patterns.items():
            if "extractors" in sub_patterns: 
                for key, regex_str in sub_patterns["extractors"].items():
                     sub_patterns["extractors"][key] = re.compile(regex_str)


class LogEntry:
    """
    Represents a single parsed log line from an Android logcat file.

    Attributes:
        timestamp (str): The timestamp of the log entry (e.g., "03-26 10:00:00.123").
        pid (Optional[int]): Process ID, if available.
        tid (Optional[int]): Thread ID, if available.
        level (str): Log level (e.g., "D", "E", "W").
        tag (str): The log tag (e.g., "ActivityManager").
        message (str): The actual log message content.
    """
    def __init__(
        self,
        timestamp: str,
        pid: Optional[int],
        tid: Optional[int],
        level: str,
        tag: str,
        message: str
    ) -> None:
        self.timestamp = timestamp
        self.pid = pid
        self.tid = tid
        self.level = level
        self.tag = tag
        self.message = message

    def __str__(self) -> str:
        """Returns a string representation of the LogEntry object."""
        return (
            f"Timestamp: {self.timestamp}, PID: {self.pid}, TID: {self.tid}, "
            f"Level: {self.level}, Tag: {self.tag}, Message: {self.message}"
        )

    def __repr__(self) -> str:
        """Returns a detailed string representation for debugging."""
        return (
            f"LogEntry(timestamp='{self.timestamp}', pid={self.pid}, tid={self.tid}, "
            f"level='{self.level}', tag='{self.tag}', message='{self.message}')"
        )

def parse_log_line(line: str) -> Optional[LogEntry]:
    """
    Parses a single log line string into a LogEntry object.

    The regex is designed to match standard Android logcat format, which typically looks like:
    MM-DD HH:MM:SS.mmm PID TID LEVEL TAG: Message

    It handles cases where PID or TID might be missing (common in kernel logs).

    Args:
        line: The raw log line string.

    Returns:
        A LogEntry object if parsing is successful, None otherwise.

    Raises:
        ValueError: If the line format is completely invalid.
    """
    try:
        # Regex breakdown:
        # ^(?P<timestamp>\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})  - Captures "MM-DD HH:MM:SS.mmm"
        # \s+                                                 - One or more spaces
        # (?P<pid>\d+)?                                       - Optional PID (digits)
        # \s+                                                 - One or more spaces
        # (?P<tid>\d+)?                                       - Optional TID (digits)
        # \s+                                                 - One or more spaces
        # (?P<level>[A-Z])                                    - Log level (single uppercase letter)
        # \s+                                                 - One or more spaces
        # (?P<tag>[^:]*)                                      - Log tag (any char except colon)
        # :\s*                                                - Colon, followed by zero or more spaces
        # (?P<message>.*)$                                    - The rest is the message
        log_pattern = re.compile(
            r"^(?P<timestamp>\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+"
            r"(?P<pid>\d+)?\s+(?P<tid>\d+)?\s+"
            r"(?P<level>[A-Z])\s+"
            r"(?P<tag>[^:]*):\s*(?P<message>.*)$"
        )
        match = log_pattern.match(line.strip())
        if match:
            data = match.groupdict()
            # Convert PID and TID to integers if they exist, otherwise None
            pid = int(data["pid"]) if data["pid"] else None
            tid = int(data["tid"]) if data["tid"] else None
            return LogEntry(
                timestamp=data["timestamp"],
                pid=pid,
                tid=tid,
                level=data["level"],
                tag=data["tag"].strip(),  # Remove leading/trailing whitespace from tag
                message=data["message"].strip()  # Remove leading/trailing whitespace from message
            )
        return None
    except (ValueError, AttributeError) as e:
        logger.debug(f"Failed to parse log line: {line[:100]}... Error: {e}")
        return None

def iter_log_lines(filepath: Union[str, Path]) -> Iterator[str]:
    """
    Yield log lines from plain text or compressed files (.gz or .zip).

    Args:
        filepath: Path to the log file (supports .log, .txt, .gz, .zip)

    Yields:
        str: Individual log lines

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
        zipfile.BadZipFile: If zip file is corrupted
    """
    filepath = Path(filepath)

    try:
        if filepath.suffix.lower() == ".gz":
            with gzip.open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    yield line.rstrip('\n\r')
        elif filepath.suffix.lower() == ".zip":
            with zipfile.ZipFile(filepath) as z:
                for name in z.namelist():
                    if not name.lower().endswith((".log", ".txt")):
                        continue
                    with z.open(name) as f:
                        for line in f:
                            yield line.decode("utf-8", errors="ignore").rstrip('\n\r')
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    yield line.rstrip('\n\r')
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        raise

def analyze_java_crash(log_entry: LogEntry) -> Optional[Dict[str, Any]]:
    """
    Analyzes a LogEntry to detect Java crashes based on defined patterns.

    Args:
        log_entry: The parsed log entry to analyze.

    Returns:
        A dictionary with "type" and "trigger_line" if a Java crash is detected,
        None otherwise.
    """
    patterns = ISSUE_PATTERNS["java_crash"]
    # Check if the log entry's tag matches one of the tags specified for Java crashes
    if log_entry.tag in patterns["tags"]:
        # Check if any of the specified keywords are present in the log message
        for keyword in patterns["message_keywords"]:
            if keyword in log_entry.message: # Case-sensitive keyword match
                return {"type": "JavaCrash", "trigger_line": log_entry}
    return None

def analyze_anr(log_entry: LogEntry) -> Optional[Dict[str, Any]]:
    """
    Analyzes a LogEntry to detect ANR (Application Not Responding) errors.

    Args:
        log_entry: The parsed log entry.

    Returns:
        A dictionary with ANR details ("type", "process_name", "reason", "trigger_line")
        if detected, None otherwise.
    """
    patterns = ISSUE_PATTERNS["anr"]
    if log_entry.tag in patterns["tags"]:
        for keyword in patterns["message_keywords"]:
            if keyword in log_entry.message: # Check for "ANR in"
                extracted_data = {"type": "ANR", "trigger_line": log_entry}
                # Attempt to extract specific details using pre-compiled regexes
                for key, compiled_regex in patterns["extractors"].items():
                    match = compiled_regex.search(log_entry.message)
                    if match:
                        extracted_data[key] = match.group(1).strip()
                    else:
                        # Default values if extraction fails
                        extracted_data[key] = "Unknown" if key == "process_name" else None
                
                # Fallback for process_name if the specific regex failed but "ANR in" was present
                if extracted_data.get("process_name") == "Unknown" or extracted_data.get("process_name") is None:
                    # A more generic regex to capture the process name after "ANR in "
                    generic_match = re.search(r"ANR in ([^ \(]+)", log_entry.message)
                    if generic_match:
                        extracted_data["process_name"] = generic_match.group(1).strip()
                    # If still not found, it remains "Unknown Process" or whatever the default was.
                return extracted_data
    return None

def analyze_native_crash_hint(log_entry: LogEntry) -> Optional[Dict[str, Any]]:
    """
    Analyzes a LogEntry for hints of native crashes (e.g., signals, tombstone headers).

    Args:
        log_entry: The parsed log entry.

    Returns:
        Dictionary with native crash details if a hint is detected, None otherwise.
    """
    patterns = ISSUE_PATTERNS["native_crash_hint"]
    # Native crash indicators can be in specific tags OR identified by message keywords (like "*** ***")
    tag_match = log_entry.tag in patterns["tags"]
    keyword_match = any(keyword in log_entry.message for keyword in patterns["message_keywords"])

    if tag_match or keyword_match:
        # The "*** ***" pattern is a strong indicator of a native crash dump start.
        if "*** ***" in patterns["message_keywords"] and "*** ***" in log_entry.message:
            extracted_data = {"type": "NativeCrashHint", "trigger_line": log_entry, "signal_info": None, "process_info": None}
            # Attempt to extract further details if they are on the same line
            for key, compiled_regex in patterns["extractors"].items():
                match = compiled_regex.search(log_entry.message)
                if match:
                    extracted_data[key] = match.group(1).strip()
            return extracted_data

        # For other keywords (like "Fatal signal") or specific tag matches
        # We expect more specific information (like signal details) to confirm the hint.
        if any(keyword in log_entry.message for keyword in patterns["message_keywords"] if keyword != "*** ***") or tag_match:
            extracted_data = {"type": "NativeCrashHint", "trigger_line": log_entry, "signal_info": None, "process_info": None}
            found_specific_detail = False
            for key, compiled_regex in patterns["extractors"].items():
                match = compiled_regex.search(log_entry.message)
                if match:
                    extracted_data[key] = match.group(1).strip()
                    found_specific_detail = True 
            
            # Only return if a specific detail (like signal or process info) was actually extracted.
            # This avoids flagging generic lines from DEBUG/libc tags as native crashes without more evidence.
            if found_specific_detail:
                return extracted_data
    return None


def analyze_system_error(log_entry: LogEntry) -> Optional[Dict[str, Any]]:
    """
    Analyzes a LogEntry for various critical system errors (kernel, watchdog, etc.).

    Args:
        log_entry: The parsed log entry.

    Returns:
        Dictionary with system error details if detected, None otherwise.
    """
    system_patterns = ISSUE_PATTERNS["system_error"]
    for error_subtype, patterns in system_patterns.items():
        # Check if the log entry's tag matches the ones defined for this error subtype.
        # If `patterns["tags"]` is empty, it implies a generic keyword search across any tag.
        tag_check_passed = False
        if not patterns["tags"]: 
            tag_check_passed = True # Match any tag if no specific tags are listed
        elif log_entry.tag and log_entry.tag.lower() in [tag.lower() for tag in patterns["tags"]]:
            tag_check_passed = True # Case-insensitive tag comparison

        if tag_check_passed:
            for keyword in patterns["message_keywords"]:
                # Keyword matching is case-insensitive for system errors.
                if keyword.lower() in log_entry.message.lower():
                    return {"type": "SystemError", "error_subtype": error_subtype, "trigger_line": log_entry}
    return None

def analyze_memory_issue(log_entry: LogEntry) -> Optional[Dict[str, Any]]:
    """
    Analyze a LogEntry for low-memory or OOM kill messages.

    Args:
        log_entry: The parsed log entry.

    Returns:
        Dictionary with memory issue details if detected, None otherwise.
    """
    patterns = ISSUE_PATTERNS["memory_issue"]
    keyword_match = any(k.lower() in log_entry.message.lower() for k in patterns["message_keywords"])

    if keyword_match:
        issue = {"type": "MemoryIssue", "trigger_line": log_entry}
        for key, regex in patterns.get("extractors", {}).items():
            match = regex.search(log_entry.message)
            if match:
                # Regex might have multiple capture groups; pick the first non-empty
                for grp in match.groups():
                    if grp:
                        issue[key] = grp.strip()
                        break
        return issue
    return None

def read_log_file(
    filepath: Union[str, Path],
    issue_patterns_config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Reads a log file line by line, parses each line into a LogEntry object,
    and then analyzes these entries for predefined issues.

    Args:
        filepath: The path to the log file to be analyzed.
        issue_patterns_config: The configuration dictionary defining how to detect
                              various issues. If None, uses global ISSUE_PATTERNS.

    Returns:
        A list of dictionaries, where each dictionary represents a detected issue.
        Returns an empty list if the file is not found or no issues are detected.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        PermissionError: If the file can't be read due to permissions.
    """
    detected_issues: List[Dict[str, Any]] = []
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if not filepath.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    # Use provided config or default
    patterns_config = issue_patterns_config or ISSUE_PATTERNS

    try:
        logger.info(f"Analyzing log file: {filepath}")
        line_count = 0
        parsed_count = 0

        for line_number, line_content in enumerate(iter_log_lines(filepath), 1):
            line_count += 1
            line = line_content.strip()
            if not line:
                continue  # Skip empty lines

            log_entry = parse_log_line(line)
            if not log_entry:
                logger.debug(f"Could not parse line #{line_number}: {line[:100]}...")
                continue

            parsed_count += 1

            # Analyze for different types of issues
            analyzers = [
                analyze_java_crash,
                analyze_anr,
                analyze_native_crash_hint,
                analyze_system_error,
                analyze_memory_issue,
            ]

            for analyzer in analyzers:
                try:
                    result = analyzer(log_entry)
                    if result:
                        detected_issues.append(result)
                except Exception as e:
                    logger.error(f"Error in analyzer {analyzer.__name__}: {e}")

        logger.info(f"Processed {line_count} lines, parsed {parsed_count} entries, found {len(detected_issues)} issues")

    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        raise

    return detected_issues

def read_logs_from_directory(
    directory: Union[str, Path],
    issue_patterns_config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Recursively read all log files within the specified directory.

    Args:
        directory: Path to the directory containing log files.
        issue_patterns_config: Configuration for issue detection patterns.

    Returns:
        List of detected issues from all log files.

    Raises:
        FileNotFoundError: If the directory doesn't exist.
        PermissionError: If the directory can't be accessed.
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    all_issues: List[Dict[str, Any]] = []
    supported_extensions = (".log", ".txt", ".gz", ".zip")

    logger.info(f"Scanning directory: {directory}")

    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                logger.debug(f"Processing file: {file_path}")
                try:
                    issues = read_log_file(file_path, issue_patterns_config)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    continue

        logger.info(f"Found {len(all_issues)} total issues in directory")

    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        raise

    return all_issues

def get_structured_report_data(detected_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Processes a list of detected issues and returns a structured dictionary.

    Args:
        detected_issues: A list of issue dictionaries.

    Returns:
        A dictionary containing 'summary_counts' and 'detailed_issues'.
    """
    summary_counts = Counter(issue["type"] for issue in detected_issues)
    
    detailed_issues_list = []
    for issue_dict in detected_issues:
        # Create a clean representation, converting LogEntry to string
        clean_issue = {
            "type": issue_dict.get("type"),
            "trigger_line_str": str(issue_dict.get("trigger_line")),
            # Include other relevant fields, ensuring they are serializable
            "process_name": issue_dict.get("process_name"), 
            "reason": issue_dict.get("reason"),
            "signal_info": issue_dict.get("signal_info"),
            "process_info": issue_dict.get("process_info"),
            "error_subtype": issue_dict.get("error_subtype"),
            "killed_process": issue_dict.get("killed_process"),
            "oom_reason": issue_dict.get("oom_reason"),
        }
        # Remove keys with None values for cleaner output, if desired
        clean_issue = {k: v for k, v in clean_issue.items() if v is not None}
        detailed_issues_list.append(clean_issue)
        
    return {
        "summary_counts": dict(summary_counts), # Convert Counter to dict for broader compatibility
        "detailed_issues": detailed_issues_list
    }

def save_report_to_json(
    detected_issues: List[Dict[str, Any]],
    output_path: Union[str, Path]
) -> None:
    """
    Save the structured report data to a JSON file.

    Args:
        detected_issues: Issues returned by read_log_file.
        output_path: Path to the JSON file to be written.

    Raises:
        PermissionError: If the output file can't be written.
        OSError: If there's an I/O error writing the file.
    """
    output_path = Path(output_path)

    try:
        report_data = get_structured_report_data(detected_issues)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to: {output_path}")

    except Exception as e:
        logger.error(f"Error saving report to {output_path}: {e}")
        raise

def generate_report(detected_issues: List[Dict[str, Any]]) -> None:
    """
    Generates and prints a structured textual report from the list of detected issues,
    using get_structured_report_data for data preparation.

    Args:
        detected_issues: A list of issue dictionaries returned by the analyzer functions.
    """
    report_data = get_structured_report_data(detected_issues)
    summary_counts = report_data["summary_counts"]
    detailed_issues_list = report_data["detailed_issues"]

    print("\nLog Analysis Report")
    print("===================")

    if not detected_issues: # Or check if not detailed_issues_list
        print("No issues detected.")
        print("===================")
        return

    # --- Summary Section ---
    # Re-calculate system error subtypes for CLI summary, or pass it through get_structured_report_data
    system_error_subtypes_counts = Counter(
        issue["error_subtype"] for issue in detailed_issues_list 
        if issue["type"] == "SystemError" and "error_subtype" in issue
    )

    print("Summary:")
    print(f"  Java Crashes: {summary_counts.get('JavaCrash', 0)}")
    print(f"  ANRs: {summary_counts.get('ANR', 0)}")
    print(f"  Native Crash Hints: {summary_counts.get('NativeCrashHint', 0)}")
    print(f"  System Errors: {summary_counts.get('SystemError', 0)}")
    print(f"  Memory Issues: {summary_counts.get('MemoryIssue', 0)}")
    if summary_counts.get('SystemError', 0) > 0:
        for subtype, count in sorted(system_error_subtypes_counts.items()):
            print(f"    - {subtype}: {count}")
    print("===================")
    
    # --- Details Section ---
    print("Details:")

    issue_number_tracker = {} 
    for issue in detailed_issues_list:
        issue_type = issue["type"]
        issue_number_tracker[issue_type] = issue_number_tracker.get(issue_type, 0) + 1
        
        print(f"\n--- {issue_type} #{issue_number_tracker[issue_type]} ---")
        
        # Print details from the already processed 'issue' dictionary
        print(f"  Trigger: {issue.get('trigger_line_str', 'N/A')}")
        if issue_type == "ANR":
            print(f"  Process: {issue.get('process_name', 'N/A')}")
            print(f"  Reason: {issue.get('reason', 'N/A')}")
        elif issue_type == "NativeCrashHint":
            print(f"  Signal: {issue.get('signal_info', 'N/A')}")
            print(f"  Process Info: {issue.get('process_info', 'N/A')}")
        elif issue_type == "SystemError":
            print(f"  Subtype: {issue.get('error_subtype', 'N/A')}")
        elif issue_type == "MemoryIssue":
            if 'killed_process' in issue:
                print(f"  Killed Process: {issue.get('killed_process')}")
            if 'oom_reason' in issue:
                print(f"  Reason: {issue.get('oom_reason')}")
        # Other specific fields can be added if needed
        
    print("\n===================")


def main(argv: Optional[List[str]] = None) -> None:
    """
    Command line entry point for the log analyzer.

    Args:
        argv: Command line arguments. If None, uses sys.argv.
    """
    parser = argparse.ArgumentParser(
        description="Analyze Android log files for common critical issues.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "logfile",
        help=(
            "Path to a log file or a directory containing log files.\n"
            "Compressed .gz or .zip files are also supported."
        ),
    )
    parser.add_argument(
        "--platform",
        "-p",
        choices=["google", "mtk", "sprd"],
        default="google",
        help=(
            "Specify the platform type for potentially loading platform-specific patterns.\n"
            "Currently, this option is a placeholder for future enhancements.\n"
            "Default: google."
        ),
    )
    parser.add_argument(
        "--json-output",
        "-j",
        help="Optional path to save the analysis results as JSON",
    )
    args = parser.parse_args(argv)

    # Configure logging level based on verbosity
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Placeholder for platform-specific logic (not yet implemented)
        logger.info(f"Analyzing for platform '{args.platform}'. "
                   "(Note: Platform-specific patterns are a future enhancement.)")

        # Determine if input is directory or file
        input_path = Path(args.logfile)
        if input_path.is_dir():
            detected_issues = read_logs_from_directory(input_path, ISSUE_PATTERNS)
        elif input_path.is_file():
            detected_issues = read_log_file(input_path, ISSUE_PATTERNS)
        else:
            logger.error(f"Input path does not exist or is not accessible: {input_path}")
            return

        # Save JSON report if requested
        if args.json_output:
            try:
                save_report_to_json(detected_issues, args.json_output)
                print(f"JSON report written to {args.json_output}")
            except Exception as e:
                logger.error(f"Error writing JSON report: {e}")
                return

        # Generate and display text report
        generate_report(detected_issues)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise


# Intelligent Features Integration

def smart_search_logs(query: str, log_files: List[Union[str, Path]], max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Perform intelligent search across multiple log files

    Args:
        query: Natural language or keyword search query
        log_files: List of log file paths to search
        max_results: Maximum number of results to return

    Returns:
        List of search results with relevance scoring
    """
    if not INTELLIGENT_FEATURES_AVAILABLE:
        logger.warning("Intelligent features not available. Using basic search.")
        return basic_search_logs(query, log_files, max_results)

    search_engine = SmartSearchEngine()
    all_results = []

    for log_file in log_files:
        try:
            # Read log lines
            log_lines = []
            for line in iter_log_lines(log_file):
                log_lines.append(line)

            # Perform smart search
            results = search_engine.smart_search(query, log_lines, max_results)

            # Add file information to results
            for result in results:
                result_dict = {
                    'file': str(log_file),
                    'line_number': result.line_number,
                    'content': result.content,
                    'relevance_score': result.relevance_score,
                    'match_type': result.match_type.value,
                    'highlights': result.highlights
                }
                all_results.append(result_dict)

        except Exception as e:
            logger.error(f"Error searching in {log_file}: {e}")

    # Sort by relevance score
    all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return all_results[:max_results]


def basic_search_logs(query: str, log_files: List[Union[str, Path]], max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Basic search functionality when intelligent features are not available
    """
    results = []
    query_lower = query.lower()

    for log_file in log_files:
        try:
            for line_number, line in enumerate(iter_log_lines(log_file), 1):
                if query_lower in line.lower():
                    results.append({
                        'file': str(log_file),
                        'line_number': line_number,
                        'content': line,
                        'relevance_score': 1.0,
                        'match_type': 'basic',
                        'highlights': []
                    })

                    if len(results) >= max_results:
                        break

        except Exception as e:
            logger.error(f"Error searching in {log_file}: {e}")

    return results


def prioritize_issues(issues: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Add intelligent priority scoring to detected issues

    Args:
        issues: List of detected issues
        context: Additional context for priority calculation

    Returns:
        Issues with priority information added
    """
    if not INTELLIGENT_FEATURES_AVAILABLE:
        logger.warning("Intelligent features not available. Using basic prioritization.")
        return basic_prioritize_issues(issues)

    scorer = IssuePriorityScorer()

    # Create context object
    issue_context = None
    if context:
        issue_context = IssueContext(
            app_version=context.get('app_version'),
            user_count_affected=context.get('user_count_affected', 0),
            release_stage=context.get('release_stage', 'production')
        )

    prioritized_issues = []

    for issue in issues:
        try:
            # Convert issue to format expected by priority scorer
            issue_data = {
                'type': issue.get('type', 'unknown').lower(),
                'severity': _determine_severity(issue),
                'frequency': 1,  # Default frequency, could be enhanced
                'component': _determine_component(issue),
                'message': _get_issue_message(issue)
            }

            # Calculate priority
            priority_info = scorer.calculate_priority(issue_data, issue_context)

            # Add priority information to original issue
            enhanced_issue = {**issue}
            enhanced_issue.update(priority_info)

            prioritized_issues.append(enhanced_issue)

        except Exception as e:
            logger.error(f"Error prioritizing issue: {e}")
            prioritized_issues.append(issue)  # Add original issue if prioritization fails

    # Sort by priority score
    prioritized_issues.sort(key=lambda x: x.get('total_score', 0), reverse=True)

    return prioritized_issues


def basic_prioritize_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Basic prioritization when intelligent features are not available"""
    priority_order = ['JavaCrash', 'NativeCrashHint', 'ANR', 'SystemError', 'MemoryIssue']

    def get_priority_score(issue):
        issue_type = issue.get('type', 'Unknown')
        try:
            return len(priority_order) - priority_order.index(issue_type)
        except ValueError:
            return 0

    return sorted(issues, key=get_priority_score, reverse=True)


def _determine_severity(issue: Dict[str, Any]) -> str:
    """Determine severity based on issue type"""
    issue_type = issue.get('type', '').lower()

    severity_mapping = {
        'javacrash': 'critical',
        'nativecrashint': 'critical',
        'anr': 'high',
        'systemerror': 'high',
        'memoryissue': 'medium'
    }

    return severity_mapping.get(issue_type, 'medium')


def _determine_component(issue: Dict[str, Any]) -> str:
    """Determine component based on issue details"""
    trigger_line = issue.get('trigger_line')
    if trigger_line and hasattr(trigger_line, 'tag'):
        tag = trigger_line.tag.lower()

        if 'system' in tag:
            return 'system_server'
        elif 'activity' in tag:
            return 'activity'
        elif 'service' in tag:
            return 'service'
        else:
            return 'application'

    return 'unknown'


def _get_issue_message(issue: Dict[str, Any]) -> str:
    """Extract message from issue"""
    trigger_line = issue.get('trigger_line')
    if trigger_line and hasattr(trigger_line, 'message'):
        return trigger_line.message

    return issue.get('type', 'Unknown issue')


def analyze_with_ml(log_lines: List[str]) -> Dict[str, Any]:
    """
    Perform ML-enhanced analysis on log lines

    Args:
        log_lines: List of log lines to analyze

    Returns:
        Dictionary with ML analysis results
    """
    if not ML_FEATURES_AVAILABLE:
        logger.warning("ML features not available for enhanced analysis")
        return {'ml_available': False}

    try:
        # Create ML analyzer
        ml_analyzer = create_ml_analyzer()

        results = {
            'ml_available': True,
            'crash_classifications': [],
            'anomalies': [],
            'patterns': [],
            'ml_insights': {}
        }

        # Crash classification
        if 'crash_classifier' in ml_analyzer:
            classifier = ml_analyzer['crash_classifier']

            # Find potential crash lines
            crash_lines = [line for line in log_lines
                          if any(keyword in line.lower()
                                for keyword in ['exception', 'fatal', 'crash', 'abort'])]

            for crash_line in crash_lines[:10]:  # Limit to first 10 crashes
                prediction = classifier.classify_crash(crash_line)
                results['crash_classifications'].append({
                    'line': crash_line,
                    'prediction': {
                        'crash_type': prediction.crash_type,
                        'confidence': prediction.confidence,
                        'severity': prediction.severity,
                        'description': prediction.description,
                        'recommendations': prediction.recommendations
                    }
                })

        # Anomaly detection
        if 'anomaly_detector' in ml_analyzer:
            detector = ml_analyzer['anomaly_detector']
            anomalies = detector.detect_anomalies(log_lines)

            for anomaly in anomalies:
                results['anomalies'].append({
                    'is_anomaly': anomaly.is_anomaly,
                    'score': anomaly.anomaly_score,
                    'type': anomaly.anomaly_type,
                    'description': anomaly.description,
                    'severity': anomaly.severity,
                    'recommendations': anomaly.recommendations
                })

        # Pattern recognition
        if 'pattern_recognizer' in ml_analyzer:
            recognizer = ml_analyzer['pattern_recognizer']
            patterns = recognizer.recognize_patterns(log_lines)

            for pattern in patterns:
                results['patterns'].append({
                    'pattern_id': pattern.pattern_id,
                    'type': pattern.pattern_type,
                    'description': pattern.description,
                    'frequency': pattern.frequency,
                    'confidence': pattern.confidence,
                    'severity': pattern.severity,
                    'examples': pattern.examples,
                    'recommendations': pattern.recommendations
                })

            # Get pattern statistics
            if patterns:
                results['ml_insights']['pattern_stats'] = recognizer.get_pattern_statistics(patterns)

        # Generate ML insights
        results['ml_insights'].update(_generate_ml_insights(results))

        logger.info(f"ML analysis completed: {len(results['crash_classifications'])} crashes, "
                   f"{len(results['anomalies'])} anomalies, {len(results['patterns'])} patterns")

        return results

    except Exception as e:
        logger.error(f"ML analysis failed: {e}")
        return {'ml_available': False, 'error': str(e)}


def _generate_ml_insights(ml_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate high-level insights from ML analysis results"""
    insights = {}

    # Crash insights
    crashes = ml_results.get('crash_classifications', [])
    if crashes:
        crash_types = [c['prediction']['crash_type'] for c in crashes]
        crash_severities = [c['prediction']['severity'] for c in crashes]

        insights['crash_insights'] = {
            'total_crashes': len(crashes),
            'most_common_type': max(set(crash_types), key=crash_types.count) if crash_types else None,
            'critical_crashes': sum(1 for s in crash_severities if s == 'critical'),
            'avg_confidence': sum(c['prediction']['confidence'] for c in crashes) / len(crashes)
        }

    # Anomaly insights
    anomalies = ml_results.get('anomalies', [])
    if anomalies:
        anomaly_types = [a['type'] for a in anomalies]
        anomaly_severities = [a['severity'] for a in anomalies]

        insights['anomaly_insights'] = {
            'total_anomalies': len(anomalies),
            'most_common_type': max(set(anomaly_types), key=anomaly_types.count) if anomaly_types else None,
            'critical_anomalies': sum(1 for s in anomaly_severities if s == 'critical'),
            'avg_score': sum(a['score'] for a in anomalies) / len(anomalies)
        }

    # Pattern insights
    patterns = ml_results.get('patterns', [])
    if patterns:
        pattern_types = [p['type'] for p in patterns]
        pattern_severities = [p['severity'] for p in patterns]

        insights['pattern_insights'] = {
            'total_patterns': len(patterns),
            'most_common_type': max(set(pattern_types), key=pattern_types.count) if pattern_types else None,
            'high_frequency_patterns': sum(1 for p in patterns if p['frequency'] > 5),
            'avg_confidence': sum(p['confidence'] for p in patterns) / len(patterns)
        }

    # Overall health score
    total_issues = len(crashes) + len(anomalies) + len(patterns)
    critical_issues = (insights.get('crash_insights', {}).get('critical_crashes', 0) +
                      insights.get('anomaly_insights', {}).get('critical_anomalies', 0))

    if total_issues > 0:
        health_score = max(0, 100 - (critical_issues * 20) - (total_issues * 2))
        insights['health_score'] = min(100, health_score)
    else:
        insights['health_score'] = 100

    return insights


def get_ml_enhanced_report(log_file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Generate ML-enhanced analysis report for a log file

    Args:
        log_file_path: Path to log file

    Returns:
        Enhanced analysis report with ML insights
    """
    try:
        # Read log file
        log_lines = []
        for line in iter_log_lines(log_file_path):
            log_lines.append(line)

        # Perform standard analysis
        standard_issues = read_log_file(log_file_path)

        # Perform ML analysis
        ml_results = analyze_with_ml(log_lines)

        # Combine results
        enhanced_report = {
            'file_path': str(log_file_path),
            'total_lines': len(log_lines),
            'standard_analysis': {
                'issues': standard_issues,
                'issue_count': len(standard_issues)
            },
            'ml_analysis': ml_results,
            'enhanced_insights': {}
        }

        # Generate enhanced insights
        if ml_results.get('ml_available'):
            enhanced_report['enhanced_insights'] = _combine_standard_and_ml_insights(
                standard_issues, ml_results
            )

        return enhanced_report

    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        return {'error': str(e)}


def _combine_standard_and_ml_insights(standard_issues: List[Dict[str, Any]],
                                    ml_results: Dict[str, Any]) -> Dict[str, Any]:
    """Combine insights from standard and ML analysis"""
    insights = {
        'analysis_summary': {
            'standard_issues': len(standard_issues),
            'ml_crashes': len(ml_results.get('crash_classifications', [])),
            'ml_anomalies': len(ml_results.get('anomalies', [])),
            'ml_patterns': len(ml_results.get('patterns', []))
        }
    }

    # Cross-reference standard issues with ML classifications
    ml_crashes = ml_results.get('crash_classifications', [])
    if standard_issues and ml_crashes:
        insights['correlation'] = {
            'standard_vs_ml_crashes': {
                'standard_count': len([i for i in standard_issues if 'crash' in i.get('type', '').lower()]),
                'ml_count': len(ml_crashes),
                'correlation_score': min(1.0, len(ml_crashes) / max(len(standard_issues), 1))
            }
        }

    # Priority recommendations based on combined analysis
    recommendations = []

    if ml_results.get('ml_insights', {}).get('health_score', 100) < 70:
        recommendations.append("System health score is low - immediate attention required")

    if len(ml_results.get('anomalies', [])) > 5:
        recommendations.append("Multiple anomalies detected - investigate system stability")

    if len(ml_results.get('patterns', [])) > 10:
        recommendations.append("Many recurring patterns found - consider optimization")

    insights['recommendations'] = recommendations

    return insights


if __name__ == "__main__":
    main()
