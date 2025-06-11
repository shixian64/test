"""
Real-time Monitor

This module provides a complete real-time monitoring system that integrates
log collection, stream processing, and alert management.
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime

from .collectors.adb_collector import ADBLogCollector, MockADBCollector, CollectorConfig
from .processors.stream_processor import StreamProcessor, ProcessorConfig, Alert
from .processors.alert_manager import (
    AlertManager,
    AlertManagerConfig,
    NotificationChannel,
    NotificationConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    """Configuration for real-time monitor"""

    use_mock_collector: bool = True  # Use mock by default for demo
    collector_config: Optional[CollectorConfig] = None
    processor_config: Optional[ProcessorConfig] = None
    alert_manager_config: Optional[AlertManagerConfig] = None
    auto_start: bool = False


class RealTimeMonitor:
    """Complete real-time monitoring system"""

    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()

        # Initialize components
        self.collector = None
        self.processor = None
        self.alert_manager = None

        # State
        self.is_running = False
        self.monitor_thread = None
        self.stats = {
            "start_time": None,
            "total_logs_processed": 0,
            "total_alerts_generated": 0,
            "uptime_seconds": 0,
        }

        # Callbacks
        self.log_callbacks = []
        self.alert_callbacks = []
        self.metrics_callbacks = []

        self._initialize_components()

        if self.config.auto_start:
            self.start()

    def _initialize_components(self):
        """Initialize monitoring components"""
        try:
            # Initialize collector
            collector_config = self.config.collector_config or CollectorConfig()

            if self.config.use_mock_collector:
                self.collector = MockADBCollector(collector_config)
                logger.info("Initialized mock ADB collector")
            else:
                self.collector = ADBLogCollector(collector_config)
                logger.info("Initialized real ADB collector")

            # Initialize stream processor
            processor_config = self.config.processor_config or ProcessorConfig()
            self.processor = StreamProcessor(processor_config)
            logger.info("Initialized stream processor")

            # Initialize alert manager
            alert_config = self.config.alert_manager_config or AlertManagerConfig()

            # Add default console notification if no configs provided
            if not alert_config.notification_configs:
                alert_config.notification_configs = [
                    NotificationConfig(
                        channel=NotificationChannel.CONSOLE, enabled=True
                    )
                ]

            self.alert_manager = AlertManager(alert_config)
            logger.info("Initialized alert manager")

            # Connect components
            self._connect_components()

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def _connect_components(self):
        """Connect components together"""
        # Connect collector to processor
        self.collector.add_callback(self._on_log_entry)

        # Connect processor to alert manager
        self.processor.add_alert_callback(self._on_alert)

        # Connect processor analysis callback
        self.processor.add_analysis_callback(self._on_analysis)

    def add_log_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for log entries"""
        self.log_callbacks.append(callback)

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback for alerts"""
        self.alert_callbacks.append(callback)

    def add_metrics_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for metrics updates"""
        self.metrics_callbacks.append(callback)

    def start(self) -> bool:
        """Start real-time monitoring"""
        if self.is_running:
            logger.warning("Monitor is already running")
            return False

        try:
            # Start components
            if not self.processor.start():
                logger.error("Failed to start stream processor")
                return False

            if not self.collector.start():
                logger.error("Failed to start log collector")
                self.processor.stop()
                return False

            # Start monitoring thread
            self.is_running = True
            self.stats["start_time"] = datetime.now()
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self.monitor_thread.start()

            logger.info("Real-time monitor started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start monitor: {e}")
            self.stop()
            return False

    def stop(self):
        """Stop real-time monitoring"""
        if not self.is_running:
            return

        logger.info("Stopping real-time monitor...")

        self.is_running = False

        # Stop components
        if self.collector:
            self.collector.stop()

        if self.processor:
            self.processor.stop()

        # Wait for monitor thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        logger.info("Real-time monitor stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        status = {
            "is_running": self.is_running,
            "components": {
                "collector": "initialized" if self.collector else "not_initialized",
                "processor": "initialized" if self.processor else "not_initialized",
                "alert_manager": (
                    "initialized" if self.alert_manager else "not_initialized"
                ),
            },
            "stats": self.stats.copy(),
        }

        # Update uptime
        if self.stats["start_time"]:
            status["stats"]["uptime_seconds"] = (
                datetime.now() - self.stats["start_time"]
            ).total_seconds()

        # Get component stats
        if self.collector:
            status["collector_stats"] = self.collector.get_stats()

        if self.processor:
            status["processor_metrics"] = self.processor.get_metrics().__dict__

        if self.alert_manager:
            status["alert_stats"] = self.alert_manager.get_alert_statistics()

        return status

    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts"""
        if not self.alert_manager:
            return []

        return self.alert_manager.alert_history[-limit:]

    def _monitor_loop(self):
        """Main monitoring loop"""
        last_metrics_update = time.time()

        while self.is_running:
            try:
                # Update metrics periodically
                current_time = time.time()
                if current_time - last_metrics_update >= 5.0:  # Every 5 seconds
                    self._update_metrics()
                    last_metrics_update = current_time

                # Sleep briefly
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")

    def _update_metrics(self):
        """Update and broadcast metrics"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "monitor_stats": self.stats,
                "collector_stats": self.collector.get_stats() if self.collector else {},
                "processor_metrics": (
                    self.processor.get_metrics().__dict__ if self.processor else {}
                ),
                "alert_stats": (
                    self.alert_manager.get_alert_statistics()
                    if self.alert_manager
                    else {}
                ),
            }

            # Notify metrics callbacks
            for callback in self.metrics_callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    logger.error(f"Metrics callback error: {e}")

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    def _on_log_entry(self, log_entry):
        """Handle log entry from collector"""
        try:
            # Update stats
            self.stats["total_logs_processed"] += 1

            # Send to processor
            self.processor.process_log(log_entry)

            # Create log data for callbacks
            log_data = {
                "timestamp": log_entry.timestamp.isoformat(),
                "level": log_entry.level,
                "tag": log_entry.tag,
                "message": log_entry.message,
                "pid": log_entry.pid,
                "tid": log_entry.tid,
                "device_id": log_entry.device_id,
            }

            # Notify log callbacks
            for callback in self.log_callbacks:
                try:
                    callback(log_data)
                except Exception as e:
                    logger.error(f"Log callback error: {e}")

        except Exception as e:
            logger.error(f"Error handling log entry: {e}")

    def _on_alert(self, alert: Alert):
        """Handle alert from processor"""
        try:
            # Update stats
            self.stats["total_alerts_generated"] += 1

            # Send to alert manager
            self.alert_manager.process_alert(alert)

            # Notify alert callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")

        except Exception as e:
            logger.error(f"Error handling alert: {e}")

    def _on_analysis(self, analysis_result: Dict[str, Any]):
        """Handle analysis result from processor"""
        try:
            # Log analysis results for debugging
            if analysis_result.get("patterns_detected"):
                logger.debug(
                    f"Patterns detected: {analysis_result['patterns_detected']}"
                )

        except Exception as e:
            logger.error(f"Error handling analysis result: {e}")


def create_demo_monitor() -> RealTimeMonitor:
    """Create a demo real-time monitor with sample configuration"""

    # Configure collector for demo
    collector_config = CollectorConfig(
        device_id="demo_device",
        log_level="V",  # Verbose - capture all logs
        max_buffer_size=1000,
    )

    # Configure processor for demo
    processor_config = ProcessorConfig(
        window_size=30,  # 30 second window
        error_threshold=3,  # Alert on 3+ errors
        crash_threshold=1,  # Alert on any crash
        enable_ml_analysis=True,
    )

    # Configure alert manager for demo
    alert_config = AlertManagerConfig(
        notification_configs=[
            NotificationConfig(channel=NotificationChannel.CONSOLE, enabled=True),
            NotificationConfig(
                channel=NotificationChannel.FILE,
                enabled=True,
                config={"file_path": "demo_alerts.log"},
            ),
        ],
        max_alerts_per_hour=20,
        enable_deduplication=True,
    )

    # Create monitor config
    monitor_config = MonitorConfig(
        use_mock_collector=True,  # Use mock for demo
        collector_config=collector_config,
        processor_config=processor_config,
        alert_manager_config=alert_config,
        auto_start=False,
    )

    return RealTimeMonitor(monitor_config)
