"""
Android Log Analyzer

This script parses and analyzes Android logcat files to detect common critical issues
such as Java crashes, Application Not Responding (ANR) errors, native crashes,
and various system-level errors (kernel panics, watchdog timeouts, etc.).

It uses a configurable set of patterns (ISSUE_PATTERNS) to identify these issues
and generates a summary report of its findings.
"""
import re
import argparse # For command-line interface
from collections import Counter # For summarizing issues

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
ISSUE_PATTERNS = {
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
        pid (int | None): Process ID, if available.
        tid (int | None): Thread ID, if available.
        level (str): Log level (e.g., "D", "E", "W").
        tag (str): The log tag (e.g., "ActivityManager").
        message (str): The actual log message content.
    """
    def __init__(self, timestamp, pid, tid, level, tag, message):
        self.timestamp = timestamp
        self.pid = pid
        self.tid = tid
        self.level = level
        self.tag = tag
        self.message = message

    def __str__(self):
        """Returns a string representation of the LogEntry object."""
        return f"Timestamp: {self.timestamp}, PID: {self.pid}, TID: {self.tid}, Level: {self.level}, Tag: {self.tag}, Message: {self.message}"

def parse_log_line(line):
    """
    Parses a single log line string into a LogEntry object.

    The regex is designed to match standard Android logcat format, which typically looks like:
    MM-DD HH:MM:SS.mmm PID TID LEVEL TAG: Message

    It handles cases where PID or TID might be missing (common in kernel logs).

    Args:
        line (str): The raw log line string.

    Returns:
        LogEntry: A LogEntry object if parsing is successful.
        None: If the line does not match the expected log format.
    """
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
    match = log_pattern.match(line)
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
            tag=data["tag"].strip(), # Remove leading/trailing whitespace from tag
            message=data["message"].strip() # Remove leading/trailing whitespace from message
        )
    return None

def analyze_java_crash(log_entry):
    """
    Analyzes a LogEntry to detect Java crashes based on defined patterns.

    Args:
        log_entry (LogEntry): The parsed log entry to analyze.

    Returns:
        dict: A dictionary with "type" and "trigger_line" if a Java crash is detected.
        None: If no Java crash is detected.
    """
    patterns = ISSUE_PATTERNS["java_crash"]
    # Check if the log entry's tag matches one of the tags specified for Java crashes
    if log_entry.tag in patterns["tags"]:
        # Check if any of the specified keywords are present in the log message
        for keyword in patterns["message_keywords"]:
            if keyword in log_entry.message: # Case-sensitive keyword match
                return {"type": "JavaCrash", "trigger_line": log_entry}
    return None

def analyze_anr(log_entry):
    """
    Analyzes a LogEntry to detect ANR (Application Not Responding) errors.

    Args:
        log_entry (LogEntry): The parsed log entry.

    Returns:
        dict: A dictionary with ANR details ("type", "process_name", "reason", "trigger_line") if detected.
        None: If no ANR is detected.
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

def analyze_native_crash_hint(log_entry):
    """
    Analyzes a LogEntry for hints of native crashes (e.g., signals, tombstone headers).

    Args:
        log_entry (LogEntry): The parsed log entry.

    Returns:
        dict: Dictionary with native crash details if a hint is detected.
        None: Otherwise.
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


def analyze_system_error(log_entry):
    """
    Analyzes a LogEntry for various critical system errors (kernel, watchdog, etc.).

    Args:
        log_entry (LogEntry): The parsed log entry.

    Returns:
        dict: Dictionary with system error details if detected.
        None: Otherwise.
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

def analyze_memory_issue(log_entry):
    """Analyze a LogEntry for low-memory or OOM kill messages."""
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

def read_log_file(filepath, issue_patterns_config):
    """
    Reads a log file line by line, parses each line into a LogEntry object,
    and then analyzes these entries for predefined issues.

    Args:
        filepath (str): The path to the log file to be analyzed.
        issue_patterns_config (dict): The configuration dictionary (ISSUE_PATTERNS) 
                                      defining how to detect various issues. 
                                      (Currently unused as analyzers access global ISSUE_PATTERNS).

    Returns:
        list: A list of dictionaries, where each dictionary represents a detected issue.
              Returns an empty list if the file is not found or no issues are detected.
    """
    detected_issues = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_number, line_content in enumerate(f, 1):
                line = line_content.strip()
                if not line:
                    continue  # Skip empty lines

                log_entry = parse_log_line(line)
                if not log_entry:
                    print(f"Warning: Could not parse line #{line_number}: {line}")
                    continue

                java_crash_info = analyze_java_crash(log_entry)
                if java_crash_info:
                    detected_issues.append(java_crash_info)

                anr_info = analyze_anr(log_entry)
                if anr_info:
                    detected_issues.append(anr_info)

                native_crash_info = analyze_native_crash_hint(log_entry)
                if native_crash_info:
                    detected_issues.append(native_crash_info)

                system_error_info = analyze_system_error(log_entry)
                if system_error_info:
                    detected_issues.append(system_error_info)

                memory_issue_info = analyze_memory_issue(log_entry)
                if memory_issue_info:
                    detected_issues.append(memory_issue_info)
    except FileNotFoundError:
        print(f"Error: File not found at path: {filepath}")
        return detected_issues

    return detected_issues

def get_structured_report_data(detected_issues):
    """
    Processes a list of detected issues and returns a structured dictionary.

    Args:
        detected_issues (list): A list of issue dictionaries.

    Returns:
        dict: A dictionary containing 'summary_counts' and 'detailed_issues'.
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

def save_report_to_json(detected_issues, output_path):
    """Save the structured report data to a JSON file.

    Args:
        detected_issues (list): Issues returned by ``read_log_file``.
        output_path (str): Path to the JSON file to be written.
    """
    import json

    report_data = get_structured_report_data(detected_issues)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

def generate_report(detected_issues):
    """
    Generates and prints a structured textual report from the list of detected issues,
    using get_structured_report_data for data preparation.

    Args:
        detected_issues (list): A list of issue dictionaries returned by the analyzer functions.
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


def main(argv=None):
    """Command line entry point for the log analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze Android log files for common critical issues.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "logfile",
        help="Path to the Android log file to analyze.",
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

    # Placeholder for platform-specific logic (not yet implemented)
    print(
        f"Info: Analyzing for platform '{args.platform}'. (Note: Platform-specific patterns are a future enhancement.)"
    )

    detected_issues = read_log_file(args.logfile, ISSUE_PATTERNS)

    if args.json_output:
        try:
            save_report_to_json(detected_issues, args.json_output)
            print(f"JSON report written to {args.json_output}")
        except Exception as e:
            print(f"Error writing JSON report: {e}")

    generate_report(detected_issues)


if __name__ == "__main__":
    main()
