"""
Streaming Module for Android Log Analyzer

This module provides real-time log processing capabilities including:
- Real-time log collection from Android devices
- Stream processing and analysis
- Intelligent alerting and notification
- Continuous monitoring and metrics
"""

from .realtime_monitor import RealTimeMonitor, MonitorConfig, create_demo_monitor
from .collectors.adb_collector import ADBLogCollector, MockADBCollector, CollectorConfig, LogEntry
from .processors.stream_processor import StreamProcessor, ProcessorConfig, Alert, AlertLevel, StreamMetrics
from .processors.alert_manager import AlertManager, AlertManagerConfig, NotificationChannel, NotificationConfig

__version__ = "0.1.0"
__author__ = "Android Log Analyzer Streaming Team"

__all__ = [
    # Main monitor
    'RealTimeMonitor',
    'MonitorConfig',
    'create_demo_monitor',
    
    # Collectors
    'ADBLogCollector',
    'MockADBCollector', 
    'CollectorConfig',
    'LogEntry',
    
    # Processors
    'StreamProcessor',
    'ProcessorConfig',
    'StreamMetrics',
    
    # Alerts
    'Alert',
    'AlertLevel',
    'AlertManager',
    'AlertManagerConfig',
    'NotificationChannel',
    'NotificationConfig',
    
    # Utility functions
    'get_streaming_capabilities',
    'check_streaming_health',
    'demo_streaming_features'
]


def get_streaming_capabilities():
    """
    Get information about available streaming capabilities
    
    Returns:
        Dictionary with streaming feature availability and descriptions
    """
    return {
        'real_time_collection': {
            'description': 'Real-time log collection from Android devices via ADB',
            'capabilities': [
                'Live log streaming from connected devices',
                'Multiple device support',
                'Configurable log levels and filters',
                'Buffer management and overflow handling',
                'Connection recovery and reconnection'
            ],
            'requirements': ['ADB installed and accessible', 'Connected Android device']
        },
        'stream_processing': {
            'description': 'Real-time stream processing and analysis',
            'capabilities': [
                'Sliding window analysis',
                'Pattern detection and classification',
                'ML-enhanced analysis (if available)',
                'Real-time metrics calculation',
                'Configurable thresholds and rules'
            ],
            'features': ['Error rate monitoring', 'Crash detection', 'ANR identification', 'Memory issue tracking']
        },
        'alert_management': {
            'description': 'Intelligent alerting and notification system',
            'capabilities': [
                'Multi-channel notifications',
                'Alert deduplication and aggregation',
                'Escalation policies',
                'Rate limiting and suppression',
                'Customizable notification formats'
            ],
            'channels': ['Console', 'Email', 'Slack', 'Webhook', 'File logging']
        },
        'monitoring_system': {
            'description': 'Complete real-time monitoring solution',
            'capabilities': [
                'Integrated log collection and processing',
                'Real-time metrics and statistics',
                'Health monitoring and diagnostics',
                'Configurable monitoring policies',
                'Extensible callback system'
            ],
            'metrics': ['Logs per second', 'Error rates', 'Alert counts', 'System health scores']
        }
    }


def check_streaming_health():
    """
    Check the health and status of streaming components
    
    Returns:
        Health check results for streaming system
    """
    health_status = {
        'overall_status': 'healthy',
        'components': {}
    }
    
    # Check ADB availability
    try:
        import subprocess
        result = subprocess.run(['adb', 'version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            health_status['components']['adb'] = {
                'status': 'available',
                'version': result.stdout.decode().split('\n')[0] if result.stdout else 'unknown'
            }
        else:
            health_status['components']['adb'] = {
                'status': 'error',
                'message': 'ADB command failed'
            }
    except FileNotFoundError:
        health_status['components']['adb'] = {
            'status': 'not_found',
            'message': 'ADB not installed or not in PATH'
        }
        health_status['overall_status'] = 'degraded'
    except Exception as e:
        health_status['components']['adb'] = {
            'status': 'error',
            'message': str(e)
        }
        health_status['overall_status'] = 'degraded'
    
    # Check collector
    try:
        collector = MockADBCollector()
        health_status['components']['collector'] = {
            'status': 'healthy',
            'type': 'mock_available'
        }
    except Exception as e:
        health_status['components']['collector'] = {
            'status': 'error',
            'error': str(e)
        }
        health_status['overall_status'] = 'error'
    
    # Check processor
    try:
        processor = StreamProcessor()
        health_status['components']['processor'] = {
            'status': 'healthy',
            'ml_enabled': processor.ml_analyzer is not None
        }
    except Exception as e:
        health_status['components']['processor'] = {
            'status': 'error',
            'error': str(e)
        }
        health_status['overall_status'] = 'error'
    
    # Check alert manager
    try:
        alert_manager = AlertManager()
        health_status['components']['alert_manager'] = {
            'status': 'healthy',
            'notification_handlers': len(alert_manager.notification_handlers)
        }
    except Exception as e:
        health_status['components']['alert_manager'] = {
            'status': 'error',
            'error': str(e)
        }
        health_status['overall_status'] = 'error'
    
    return health_status


def demo_streaming_features():
    """
    Run a quick demo of streaming features
    
    Returns:
        Demo results showing streaming capabilities
    """
    demo_results = {
        'streaming_available': True,
        'features_tested': {}
    }
    
    # Test collector
    try:
        collector = MockADBCollector()
        demo_results['features_tested']['collector'] = {
            'status': 'success',
            'type': 'mock_collector',
            'config': 'default'
        }
    except Exception as e:
        demo_results['features_tested']['collector'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Test processor
    try:
        processor = StreamProcessor()
        demo_results['features_tested']['processor'] = {
            'status': 'success',
            'ml_enabled': processor.ml_analyzer is not None,
            'window_size': processor.config.window_size
        }
    except Exception as e:
        demo_results['features_tested']['processor'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Test alert manager
    try:
        alert_manager = AlertManager()
        demo_results['features_tested']['alert_manager'] = {
            'status': 'success',
            'channels': len(alert_manager.notification_handlers),
            'escalation_rules': len(alert_manager.config.escalation_rules)
        }
    except Exception as e:
        demo_results['features_tested']['alert_manager'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Test complete monitor
    try:
        monitor = create_demo_monitor()
        demo_results['features_tested']['monitor'] = {
            'status': 'success',
            'components_initialized': all([
                monitor.collector is not None,
                monitor.processor is not None,
                monitor.alert_manager is not None
            ])
        }
    except Exception as e:
        demo_results['features_tested']['monitor'] = {
            'status': 'error',
            'error': str(e)
        }
    
    return demo_results


def get_streaming_requirements():
    """
    Get requirements for streaming functionality
    
    Returns:
        Dictionary with requirements and installation instructions
    """
    return {
        'system_requirements': {
            'adb': {
                'description': 'Android Debug Bridge for device communication',
                'installation': [
                    'Install Android SDK Platform Tools',
                    'Add ADB to system PATH',
                    'Enable USB debugging on Android device'
                ],
                'verification': 'Run "adb version" to verify installation'
            },
            'python_packages': {
                'required': ['threading', 'queue', 'subprocess'],
                'optional': ['requests (for webhook notifications)', 'smtplib (for email notifications)']
            }
        },
        'device_requirements': {
            'android_device': {
                'description': 'Android device with USB debugging enabled',
                'setup': [
                    'Enable Developer Options',
                    'Enable USB Debugging',
                    'Connect device via USB',
                    'Authorize computer for debugging'
                ],
                'verification': 'Run "adb devices" to see connected devices'
            }
        },
        'network_requirements': {
            'notifications': {
                'email': 'SMTP server access for email notifications',
                'slack': 'Slack webhook URL for Slack notifications',
                'webhook': 'HTTP endpoint for webhook notifications'
            }
        }
    }


def create_production_monitor(device_id: str = None, enable_email: bool = False, 
                            email_config: dict = None) -> RealTimeMonitor:
    """
    Create a production-ready real-time monitor
    
    Args:
        device_id: Specific Android device ID to monitor
        enable_email: Whether to enable email notifications
        email_config: Email configuration dictionary
        
    Returns:
        Configured RealTimeMonitor for production use
    """
    # Production collector config
    collector_config = CollectorConfig(
        device_id=device_id,
        log_level="W",  # Warning and above for production
        buffer_types=["main", "system", "crash"],
        max_buffer_size=5000,
        reconnect_interval=10
    )
    
    # Production processor config
    processor_config = ProcessorConfig(
        window_size=300,  # 5 minute window
        error_threshold=10,  # Alert on 10+ errors in 5 minutes
        crash_threshold=1,  # Alert on any crash
        anr_threshold=1,  # Alert on any ANR
        enable_ml_analysis=True,
        buffer_size=2000
    )
    
    # Production alert config
    notification_configs = [
        NotificationConfig(
            channel=NotificationChannel.CONSOLE,
            enabled=True
        ),
        NotificationConfig(
            channel=NotificationChannel.FILE,
            enabled=True,
            config={'file_path': 'production_alerts.log'}
        )
    ]
    
    # Add email if configured
    if enable_email and email_config:
        notification_configs.append(
            NotificationConfig(
                channel=NotificationChannel.EMAIL,
                enabled=True,
                config=email_config
            )
        )
    
    alert_config = AlertManagerConfig(
        notification_configs=notification_configs,
        max_alerts_per_hour=100,
        enable_deduplication=True,
        deduplication_window=1800  # 30 minutes
    )
    
    # Create monitor config
    monitor_config = MonitorConfig(
        use_mock_collector=False,  # Use real ADB for production
        collector_config=collector_config,
        processor_config=processor_config,
        alert_manager_config=alert_config,
        auto_start=False
    )
    
    return RealTimeMonitor(monitor_config)
