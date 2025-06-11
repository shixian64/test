"""
ADB Log Collector

This module provides real-time log collection from Android devices via ADB.
Supports continuous monitoring, filtering, and streaming of log data.
"""

import subprocess
import threading
import queue
import logging
import time
import re
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Structured log entry"""

    timestamp: datetime
    pid: int
    tid: int
    level: str
    tag: str
    message: str
    raw_line: str
    device_id: Optional[str] = None


@dataclass
class CollectorConfig:
    """Configuration for ADB log collector"""

    device_id: Optional[str] = None
    buffer_types: List[str] = None  # main, system, radio, events, crash
    log_level: str = "V"  # V, D, I, W, E, F
    filter_tags: List[str] = None
    exclude_tags: List[str] = None
    max_buffer_size: int = 10000
    reconnect_interval: int = 5
    timeout: int = 30


class ADBLogCollector:
    """Real-time ADB log collector"""

    def __init__(self, config: Optional[CollectorConfig] = None):
        self.config = config or CollectorConfig()
        self.is_running = False
        self.log_queue = queue.Queue(maxsize=self.config.max_buffer_size)
        self.process = None
        self.thread = None
        self.callbacks = []
        self.stats = {
            "total_lines": 0,
            "parsed_lines": 0,
            "errors": 0,
            "start_time": None,
            "last_log_time": None,
        }

        # Android log pattern
        self.log_pattern = re.compile(
            r"(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+"  # timestamp
            r"(\d+)\s+"  # pid
            r"(\d+)\s+"  # tid
            r"([VDIWEF])\s+"  # level
            r"([^:]+):\s*"  # tag
            r"(.*)"  # message
        )

    def add_callback(self, callback: Callable[[LogEntry], None]):
        """Add callback for processing log entries"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[LogEntry], None]):
        """Remove callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def start(self) -> bool:
        """Start real-time log collection"""
        if self.is_running:
            logger.warning("Collector is already running")
            return False

        try:
            # Check ADB availability
            if not self._check_adb():
                logger.error("ADB not available or no devices connected")
                return False

            # Start collection thread
            self.is_running = True
            self.stats["start_time"] = datetime.now()
            self.thread = threading.Thread(target=self._collect_logs, daemon=True)
            self.thread.start()

            logger.info("ADB log collector started")
            return True

        except Exception as e:
            logger.error(f"Failed to start collector: {e}")
            self.is_running = False
            return False

    def stop(self):
        """Stop log collection"""
        if not self.is_running:
            return

        self.is_running = False

        # Terminate ADB process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating ADB process: {e}")

        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        logger.info("ADB log collector stopped")

    def get_log_entry(self, timeout: Optional[float] = None) -> Optional[LogEntry]:
        """Get next log entry from queue"""
        try:
            return self.log_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = self.stats.copy()
        if stats["start_time"]:
            stats["uptime"] = (datetime.now() - stats["start_time"]).total_seconds()
        return stats

    def _check_adb(self) -> bool:
        """Check if ADB is available and devices are connected"""
        try:
            # Check ADB command
            result = subprocess.run(
                ["adb", "version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False

            # Check connected devices
            result = subprocess.run(
                ["adb", "devices"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False

            # Parse device list
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            devices = [line.split("\t")[0] for line in lines if "\tdevice" in line]

            if not devices:
                logger.warning("No devices connected")
                return False

            # Use specified device or first available
            if self.config.device_id:
                if self.config.device_id not in devices:
                    logger.error(f"Device {self.config.device_id} not found")
                    return False
            else:
                self.config.device_id = devices[0]
                logger.info(f"Using device: {self.config.device_id}")

            return True

        except subprocess.TimeoutExpired:
            logger.error("ADB command timed out")
            return False
        except FileNotFoundError:
            logger.error("ADB command not found")
            return False
        except Exception as e:
            logger.error(f"Error checking ADB: {e}")
            return False

    def _collect_logs(self):
        """Main log collection loop"""
        while self.is_running:
            try:
                self._run_logcat()
            except Exception as e:
                logger.error(f"Log collection error: {e}")
                self.stats["errors"] += 1

                if self.is_running:
                    logger.info(
                        f"Reconnecting in {self.config.reconnect_interval} seconds..."
                    )
                    time.sleep(self.config.reconnect_interval)

    def _run_logcat(self):
        """Run logcat command and process output"""
        # Build logcat command
        cmd = ["adb"]

        if self.config.device_id:
            cmd.extend(["-s", self.config.device_id])

        cmd.append("logcat")

        # Add buffer types
        if self.config.buffer_types:
            for buffer_type in self.config.buffer_types:
                cmd.extend(["-b", buffer_type])

        # Add log level filter
        cmd.extend(["-v", "time"])  # Use time format
        cmd.append(f"*:{self.config.log_level}")

        logger.info(f"Starting logcat: {' '.join(cmd)}")

        # Start logcat process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Process output lines
        try:
            for line in iter(self.process.stdout.readline, ""):
                if not self.is_running:
                    break

                line = line.rstrip("\n\r")
                if line:
                    self._process_log_line(line)

        except Exception as e:
            logger.error(f"Error reading logcat output: {e}")
        finally:
            if self.process:
                self.process.terminate()

    def _process_log_line(self, line: str):
        """Process a single log line"""
        self.stats["total_lines"] += 1

        try:
            # Parse log line
            log_entry = self._parse_log_line(line)
            if log_entry:
                # Apply filters
                if self._should_include_log(log_entry):
                    # Add to queue
                    try:
                        self.log_queue.put_nowait(log_entry)
                        self.stats["parsed_lines"] += 1
                        self.stats["last_log_time"] = datetime.now()

                        # Call callbacks
                        for callback in self.callbacks:
                            try:
                                callback(log_entry)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")

                    except queue.Full:
                        # Queue is full, remove oldest entry
                        try:
                            self.log_queue.get_nowait()
                            self.log_queue.put_nowait(log_entry)
                        except queue.Empty:
                            pass

        except Exception as e:
            logger.error(f"Error processing log line: {e}")
            self.stats["errors"] += 1

    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """Parse log line into structured entry"""
        match = self.log_pattern.match(line)
        if not match:
            return None

        timestamp_str, pid_str, tid_str, level, tag, message = match.groups()

        try:
            # Parse timestamp (assuming current year)
            current_year = datetime.now().year
            timestamp = datetime.strptime(
                f"{current_year}-{timestamp_str}", "%Y-%m-%d %H:%M:%S.%f"
            )

            return LogEntry(
                timestamp=timestamp,
                pid=int(pid_str),
                tid=int(tid_str),
                level=level,
                tag=tag.strip(),
                message=message,
                raw_line=line,
                device_id=self.config.device_id,
            )

        except ValueError as e:
            logger.debug(f"Failed to parse log line: {line} - {e}")
            return None

    def _should_include_log(self, log_entry: LogEntry) -> bool:
        """Check if log entry should be included based on filters"""
        # Filter by tags
        if self.config.filter_tags:
            if log_entry.tag not in self.config.filter_tags:
                return False

        # Exclude tags
        if self.config.exclude_tags:
            if log_entry.tag in self.config.exclude_tags:
                return False

        return True


class MockADBCollector:
    """Mock ADB collector for testing without real device"""

    def __init__(self, config: Optional[CollectorConfig] = None):
        self.config = config or CollectorConfig()
        self.is_running = False
        self.log_queue = queue.Queue(maxsize=self.config.max_buffer_size)
        self.thread = None
        self.callbacks = []
        self.stats = {
            "total_lines": 0,
            "parsed_lines": 0,
            "errors": 0,
            "start_time": None,
            "last_log_time": None,
        }

        # Sample log entries for simulation
        self.sample_logs = [
            "01-01 10:00:00.123  1234  1234 I ActivityManager: Start proc com.example.app",
            "01-01 10:00:01.234  1234  1234 D MyApp: User clicked button",
            "01-01 10:00:02.345  1234  1234 I MyApp: Loading data from server",
            "01-01 10:00:03.456  1234  1234 W MyApp: Network timeout, retrying",
            "01-01 10:00:04.567  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main",
            "01-01 10:00:05.678  5678  5678 I ActivityManager: ANR in com.example.app",
            "01-01 10:00:06.789  2345  2345 E System: OutOfMemoryError: Failed to allocate",
            "01-01 10:00:07.890  3456  3456 W AudioFlinger: write blocked for 150 msecs",
        ]
        self.log_index = 0

    def add_callback(self, callback: Callable[[LogEntry], None]):
        """Add callback for processing log entries"""
        self.callbacks.append(callback)

    def start(self) -> bool:
        """Start mock log collection"""
        if self.is_running:
            return False

        self.is_running = True
        self.stats["start_time"] = datetime.now()
        self.thread = threading.Thread(target=self._generate_logs, daemon=True)
        self.thread.start()

        logger.info("Mock ADB collector started")
        return True

    def stop(self):
        """Stop mock collection"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Mock ADB collector stopped")

    def get_log_entry(self, timeout: Optional[float] = None) -> Optional[LogEntry]:
        """Get next log entry from queue"""
        try:
            return self.log_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = self.stats.copy()
        if stats["start_time"]:
            stats["uptime"] = (datetime.now() - stats["start_time"]).total_seconds()
        return stats

    def _generate_logs(self):
        """Generate mock log entries"""
        collector = ADBLogCollector()

        while self.is_running:
            # Get next sample log
            log_line = self.sample_logs[self.log_index % len(self.sample_logs)]
            self.log_index += 1

            # Parse and process
            log_entry = collector._parse_log_line(log_line)
            if log_entry:
                log_entry.device_id = "mock_device"
                log_entry.timestamp = datetime.now()  # Use current time

                try:
                    self.log_queue.put_nowait(log_entry)
                    self.stats["parsed_lines"] += 1
                    self.stats["last_log_time"] = datetime.now()

                    # Call callbacks
                    for callback in self.callbacks:
                        try:
                            callback(log_entry)
                        except Exception as e:
                            logger.error(f"Mock callback error: {e}")

                except queue.Full:
                    try:
                        self.log_queue.get_nowait()
                        self.log_queue.put_nowait(log_entry)
                    except queue.Empty:
                        pass

            # Simulate real-time delay
            time.sleep(1.0 + (self.log_index % 3) * 0.5)  # 1-2.5 second intervals
