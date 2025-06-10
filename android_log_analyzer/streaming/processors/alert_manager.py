"""
Alert Manager

This module provides intelligent alert management including:
- Alert routing and notification
- Alert aggregation and deduplication
- Escalation policies
- Multiple notification channels
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable

# Optional imports with fallbacks
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

from .stream_processor import Alert, AlertLevel

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Supported notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    CONSOLE = "console"
    FILE = "file"


@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationRule:
    """Alert escalation rule"""
    alert_level: AlertLevel
    delay_minutes: int
    channels: List[NotificationChannel]
    repeat_interval_minutes: Optional[int] = None


@dataclass
class AlertManagerConfig:
    """Configuration for alert manager"""
    notification_configs: List[NotificationConfig] = field(default_factory=list)
    escalation_rules: List[EscalationRule] = field(default_factory=list)
    aggregation_window: int = 300  # seconds
    max_alerts_per_hour: int = 50
    enable_deduplication: bool = True
    deduplication_window: int = 3600  # seconds


class AlertManager:
    """Intelligent alert management system"""
    
    def __init__(self, config: Optional[AlertManagerConfig] = None):
        self.config = config or AlertManagerConfig()
        self.notification_handlers = {}
        self.alert_history = []
        self.aggregated_alerts = defaultdict(list)
        self.last_notification_times = {}
        
        # Initialize notification handlers
        self._initialize_handlers()
        
        # Set up default escalation rules if none provided
        if not self.config.escalation_rules:
            self._setup_default_escalation_rules()
    
    def _initialize_handlers(self):
        """Initialize notification channel handlers"""
        self.notification_handlers = {
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.SLACK: self._send_slack,
            NotificationChannel.WEBHOOK: self._send_webhook,
            NotificationChannel.CONSOLE: self._send_console,
            NotificationChannel.FILE: self._send_file
        }
    
    def _setup_default_escalation_rules(self):
        """Setup default escalation rules"""
        self.config.escalation_rules = [
            EscalationRule(
                alert_level=AlertLevel.CRITICAL,
                delay_minutes=0,  # Immediate
                channels=[NotificationChannel.CONSOLE, NotificationChannel.EMAIL],
                repeat_interval_minutes=15
            ),
            EscalationRule(
                alert_level=AlertLevel.ERROR,
                delay_minutes=1,
                channels=[NotificationChannel.CONSOLE],
                repeat_interval_minutes=30
            ),
            EscalationRule(
                alert_level=AlertLevel.WARNING,
                delay_minutes=5,
                channels=[NotificationChannel.CONSOLE],
                repeat_interval_minutes=60
            ),
            EscalationRule(
                alert_level=AlertLevel.INFO,
                delay_minutes=10,
                channels=[NotificationChannel.FILE],
                repeat_interval_minutes=None  # No repeat
            )
        ]
    
    def process_alert(self, alert: Alert):
        """Process incoming alert"""
        try:
            # Add to history
            self.alert_history.append(alert)
            
            # Check if alert should be deduplicated
            if self.config.enable_deduplication and self._is_duplicate_alert(alert):
                logger.debug(f"Alert deduplicated: {alert.id}")
                return
            
            # Check rate limiting
            if self._is_rate_limited():
                logger.warning("Alert rate limit exceeded, dropping alert")
                return
            
            # Find applicable escalation rule
            escalation_rule = self._find_escalation_rule(alert)
            if not escalation_rule:
                logger.warning(f"No escalation rule found for alert level: {alert.level}")
                return
            
            # Process according to escalation rule
            self._process_escalation(alert, escalation_rule)
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    def _is_duplicate_alert(self, alert: Alert) -> bool:
        """Check if alert is a duplicate within deduplication window"""
        current_time = datetime.now()
        window_start = current_time - timedelta(seconds=self.config.deduplication_window)
        
        # Check recent alerts for similar content
        for recent_alert in reversed(self.alert_history[-100:]):  # Check last 100 alerts
            if recent_alert.timestamp < window_start:
                break
            
            # Check for similarity (same title and source)
            if (recent_alert.title == alert.title and 
                recent_alert.source == alert.source and
                recent_alert.id != alert.id):
                return True
        
        return False
    
    def _is_rate_limited(self) -> bool:
        """Check if alert rate limit is exceeded"""
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        
        # Count alerts in the last hour
        recent_alerts = [a for a in self.alert_history if a.timestamp >= hour_ago]
        
        return len(recent_alerts) >= self.config.max_alerts_per_hour
    
    def _find_escalation_rule(self, alert: Alert) -> Optional[EscalationRule]:
        """Find applicable escalation rule for alert"""
        for rule in self.config.escalation_rules:
            if rule.alert_level == alert.level:
                return rule
        return None
    
    def _process_escalation(self, alert: Alert, rule: EscalationRule):
        """Process alert according to escalation rule"""
        # Immediate notification if delay is 0
        if rule.delay_minutes == 0:
            self._send_notifications(alert, rule.channels)
        
        # TODO: Implement delayed notifications and repeats
        # This would require a scheduler/timer system
        
        # For now, just send immediate notifications
        if rule.delay_minutes <= 1:  # Send if delay is very short
            self._send_notifications(alert, rule.channels)
    
    def _send_notifications(self, alert: Alert, channels: List[NotificationChannel]):
        """Send notifications to specified channels"""
        for channel in channels:
            try:
                # Check if channel is enabled
                channel_config = self._get_channel_config(channel)
                if not channel_config or not channel_config.enabled:
                    continue
                
                # Send notification
                handler = self.notification_handlers.get(channel)
                if handler:
                    handler(alert, channel_config.config)
                else:
                    logger.warning(f"No handler for channel: {channel}")
                    
            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {e}")
    
    def _get_channel_config(self, channel: NotificationChannel) -> Optional[NotificationConfig]:
        """Get configuration for notification channel"""
        for config in self.config.notification_configs:
            if config.channel == channel:
                return config
        
        # Return default config if not found
        return NotificationConfig(channel=channel, enabled=True)
    
    def _send_email(self, alert: Alert, config: Dict[str, Any]):
        """Send email notification"""
        if not EMAIL_AVAILABLE:
            logger.warning("Email functionality not available (missing smtplib)")
            return

        try:
            # Email configuration
            smtp_server = config.get('smtp_server', 'localhost')
            smtp_port = config.get('smtp_port', 587)
            username = config.get('username')
            password = config.get('password')
            from_email = config.get('from_email', 'alerts@example.com')
            to_emails = config.get('to_emails', ['admin@example.com'])

            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"

            # Email body
            body = f"""
Alert Details:
- Level: {alert.level.value.upper()}
- Title: {alert.title}
- Description: {alert.description}
- Timestamp: {alert.timestamp}
- Source: {alert.source}

Metadata:
{json.dumps(alert.metadata, indent=2)}
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            if username and password:
                server.starttls()
                server.login(username, password)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack(self, alert: Alert, config: Dict[str, Any]):
        """Send Slack notification"""
        if not REQUESTS_AVAILABLE:
            logger.warning("Slack functionality not available (missing requests library)")
            return

        try:
            webhook_url = config.get('webhook_url')
            if not webhook_url:
                logger.error("Slack webhook URL not configured")
                return

            # Slack message format
            color_map = {
                AlertLevel.CRITICAL: "danger",
                AlertLevel.ERROR: "warning",
                AlertLevel.WARNING: "warning",
                AlertLevel.INFO: "good"
            }

            payload = {
                "attachments": [{
                    "color": color_map.get(alert.level, "warning"),
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {"title": "Level", "value": alert.level.value.upper(), "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": True}
                    ]
                }]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Slack alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_webhook(self, alert: Alert, config: Dict[str, Any]):
        """Send webhook notification"""
        if not REQUESTS_AVAILABLE:
            logger.warning("Webhook functionality not available (missing requests library)")
            return

        try:
            url = config.get('url')
            if not url:
                logger.error("Webhook URL not configured")
                return

            # Webhook payload
            payload = {
                "alert": {
                    "id": alert.id,
                    "level": alert.level.value,
                    "title": alert.title,
                    "description": alert.description,
                    "timestamp": alert.timestamp.isoformat(),
                    "source": alert.source,
                    "metadata": alert.metadata
                }
            }

            headers = config.get('headers', {'Content-Type': 'application/json'})

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"Webhook alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _send_console(self, alert: Alert, config: Dict[str, Any]):
        """Send console notification"""
        try:
            # Format console message
            level_emoji = {
                AlertLevel.CRITICAL: "🚨",
                AlertLevel.ERROR: "❌",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.INFO: "ℹ️"
            }
            
            emoji = level_emoji.get(alert.level, "📢")
            
            print(f"\n{emoji} ALERT [{alert.level.value.upper()}] {emoji}")
            print(f"Title: {alert.title}")
            print(f"Description: {alert.description}")
            print(f"Time: {alert.timestamp}")
            print(f"Source: {alert.source}")
            if alert.metadata:
                print(f"Metadata: {json.dumps(alert.metadata, indent=2)}")
            print("-" * 50)
            
            logger.info(f"Console alert displayed: {alert.title}")
            
        except Exception as e:
            logger.error(f"Failed to send console alert: {e}")
    
    def _send_file(self, alert: Alert, config: Dict[str, Any]):
        """Send file notification"""
        try:
            file_path = config.get('file_path', 'alerts.log')
            
            # Format log entry
            log_entry = {
                "timestamp": alert.timestamp.isoformat(),
                "level": alert.level.value,
                "title": alert.title,
                "description": alert.description,
                "source": alert.source,
                "metadata": alert.metadata
            }
            
            # Append to file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.info(f"File alert logged: {alert.title}")
            
        except Exception as e:
            logger.error(f"Failed to send file alert: {e}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        if not self.alert_history:
            return {}
        
        # Calculate statistics
        total_alerts = len(self.alert_history)
        level_counts = defaultdict(int)
        
        for alert in self.alert_history:
            level_counts[alert.level.value] += 1
        
        # Recent alerts (last hour)
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_alerts = [a for a in self.alert_history if a.timestamp >= hour_ago]
        
        return {
            "total_alerts": total_alerts,
            "alerts_by_level": dict(level_counts),
            "recent_alerts_count": len(recent_alerts),
            "alert_rate_per_hour": len(recent_alerts),
            "last_alert_time": self.alert_history[-1].timestamp.isoformat() if self.alert_history else None
        }
