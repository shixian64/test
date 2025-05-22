# Android Log Analyzer

## Overview

This tool analyzes Android log files (typically from `logcat`) to detect common critical issues. It helps in quickly identifying problems like application crashes, system errors, and performance issues from extensive log data.

## Features

The analyzer can detect the following types of issues:

*   **Java Crashes**: Identifies "FATAL EXCEPTION" messages typically indicating an application crash due to an unhandled Java exception.
*   **Application Not Responding (ANRs)**: Detects ANR messages from the ActivityManager, indicating that an application has become unresponsive.
*   **Native Crash Hints**: Looks for signs of native code crashes, such as fatal signals (SIGSEGV, SIGABRT, etc.) and tombstone headers (`*** ***`).
*   **Kernel/System Errors**:
    *   **Kernel Panics**: Detects "Kernel panic" messages.
    *   **Kernel BUGs/Oops**: Identifies kernel "BUG:" or "Oops" messages.
    *   **Watchdog Timeouts**: Flags issues where the system watchdog has triggered.
    *   **SystemServer Crashes**: Notes when the main Android SystemServer process crashes.
    *   **Miscellaneous Critical Errors**: Catches other critical system messages like "HAL frozen", "modem crashed", or "DSP failure".

## Requirements

*   Python 3 (tested with Python 3.6 and later).
*   Uses standard Python libraries (`re`, `argparse`, `collections`). No external packages are required for the core functionality.

## Usage

To analyze a log file, run the script from the command line:

```bash
python android_log_analyzer/log_analyzer.py <path_to_your_logfile> [options]
```

**Arguments:**

*   `<path_to_your_logfile>`: (Required) The path to the Android log file you want to analyze.
*   `--platform PLATFORM`, `-p PLATFORM`: (Optional) Specify the platform type. Choices: `google`, `mtk`, `sprd`. Default: `google`. (Note: Platform-specific pattern loading is a future enhancement).

**Example:**

```bash
python android_log_analyzer/log_analyzer.py my_android_logs.txt
python android_log_analyzer/log_analyzer.py an_mtk_log.txt -p mtk
```

## Output

The script outputs a structured report to the console:

1.  **Summary**:
    *   Total counts for each major issue type (Java Crashes, ANRs, Native Crash Hints, System Errors).
    *   For System Errors, a sub-summary of specific subtypes (e.g., KernelPanic, Watchdog).
2.  **Details**:
    *   A numbered list of each detected issue.
    *   For each issue, relevant extracted information is provided:
        *   **Java Crash**: The triggering log line.
        *   **ANR**: Process name, reason (if available), and the triggering log line.
        *   **Native Crash Hint**: Signal information, process details (if available on the same line), and the triggering log line.
        *   **System Error**: The specific subtype (e.g., KernelPanic) and the triggering log line.

## Running Tests

Unit tests are provided to ensure the analyzer works correctly. To run the tests, navigate to the parent directory of `android_log_analyzer` (e.g., the root of this project if `android_log_analyzer` is a subdirectory) and use the command:

```bash
python -m unittest android_log_analyzer.test_log_analyzer
```

Alternatively, from within the `android_log_analyzer` directory:

```bash
python test_log_analyzer.py
```

## Extending Patterns

The core of the issue detection logic relies on the `ISSUE_PATTERNS` dictionary defined at the beginning of the `log_analyzer.py` script. You can extend or refine the tool's capabilities by:

*   Adding new issue categories.
*   Modifying existing keywords or tags for better accuracy.
*   Adding new `extractors` (regular expressions) to pull more specific details from log lines.
*   (Future) Implementing platform-specific pattern loading based on the `--platform` argument.

Always ensure that any new regex patterns are well-tested.
