"""
Alert Notification System

Handles alert routing and delivery through multiple notification channels.
Supports logging, webhooks, email, and custom notification handlers.

Anchor: T1-RSD-003-NOTIFY
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .alert_manager import Alert, AlertSeverity


# Configure logger for notifications
logger = logging.getLogger("resilience_sentinel.notifications")


@dataclass
class NotificationConfig:
    """Configuration for a notification channel."""
    channel_type: str
    name: str
    enabled: bool = True
    severity_filter: Optional[List[AlertSeverity]] = None
    config: Dict[str, Any] = field(default_factory=dict)

    def should_notify(self, alert: Alert) -> bool:
        """Check if this channel should notify for the given alert."""
        if not self.enabled:
            return False

        if self.severity_filter:
            return alert.severity in self.severity_filter

        return True


class NotificationChannel(ABC):
    """
    Abstract base class for notification channels.

    Subclasses must implement the send() method to deliver notifications.
    """

    def __init__(self, config: NotificationConfig):
        """
        Initialize notification channel.

        Args:
            config: Channel configuration
        """
        self.config = config
        self.name = config.name
        self.enabled = config.enabled

    @abstractmethod
    async def send(self, alert: Alert) -> bool:
        """
        Send alert notification.

        Args:
            alert: Alert to send

        Returns:
            True if notification was sent successfully
        """
        pass

    def format_alert_message(self, alert: Alert) -> str:
        """
        Format alert as human-readable message.

        Args:
            alert: Alert to format

        Returns:
            Formatted message string
        """
        dt = datetime.fromtimestamp(alert.timestamp)
        return (
            f"🚨 Alert: {alert.title}\n"
            f"Severity: {alert.severity.value.upper()}\n"
            f"Message: {alert.message}\n"
            f"Metric: {alert.metric_name} = {alert.metric_value:.2f} (threshold: {alert.threshold})\n"
            f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Alert ID: {alert.id}\n"
        )


class LogNotificationChannel(NotificationChannel):
    """
    Notification channel that logs alerts.

    Logs alerts at appropriate severity levels to Python logging system.
    """

    async def send(self, alert: Alert) -> bool:
        """Log alert with appropriate severity."""
        message = self.format_alert_message(alert)

        severity_log_levels = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }

        log_level = severity_log_levels.get(alert.severity, logging.INFO)
        logger.log(log_level, message)

        return True


class WebhookNotificationChannel(NotificationChannel):
    """
    Notification channel that sends alerts to webhooks.

    Posts alert data as JSON to configured webhook URL.
    """

    async def send(self, alert: Alert) -> bool:
        """Send alert to webhook URL."""
        webhook_url = self.config.config.get("url")
        if not webhook_url:
            logger.error(f"Webhook channel '{self.name}' missing URL configuration")
            return False

        # In production, use httpx or requests to POST
        # For now, log the webhook attempt
        alert_data = alert.to_dict()
        logger.info(f"[WEBHOOK] Sending alert to {webhook_url}: {json.dumps(alert_data, indent=2)}")

        # TODO: Implement actual HTTP POST when httpx is available
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(webhook_url, json=alert_data)
        #     return response.status_code == 200

        return True


class EmailNotificationChannel(NotificationChannel):
    """
    Notification channel that sends email alerts.

    Sends formatted email notifications for alerts.
    """

    async def send(self, alert: Alert) -> bool:
        """Send alert via email."""
        smtp_config = self.config.config
        recipients = smtp_config.get("recipients", [])

        if not recipients:
            logger.error(f"Email channel '{self.name}' has no recipients configured")
            return False

        # Format email
        subject = f"[{alert.severity.value.upper()}] {alert.title}"
        body = self.format_alert_message(alert)

        # In production, use smtplib or email service
        # For now, log the email attempt
        logger.info(f"[EMAIL] Sending alert to {recipients}: {subject}")
        logger.debug(f"Email body:\n{body}")

        # TODO: Implement actual email sending
        # smtp_server = smtp_config.get("server", "localhost")
        # smtp_port = smtp_config.get("port", 587)
        # Use smtplib to send email

        return True


class ConsoleNotificationChannel(NotificationChannel):
    """
    Notification channel that prints alerts to console.

    Useful for development and testing.
    """

    async def send(self, alert: Alert) -> bool:
        """Print alert to console."""
        message = self.format_alert_message(alert)

        # Add color coding based on severity
        colors = {
            AlertSeverity.INFO: "\033[94m",      # Blue
            AlertSeverity.WARNING: "\033[93m",   # Yellow
            AlertSeverity.ERROR: "\033[91m",     # Red
            AlertSeverity.CRITICAL: "\033[95m",  # Magenta
        }
        reset = "\033[0m"

        color = colors.get(alert.severity, "")
        print(f"{color}{message}{reset}")

        return True


class CustomNotificationChannel(NotificationChannel):
    """
    Notification channel for custom handlers.

    Allows registration of custom notification functions.
    """

    def __init__(self, config: NotificationConfig, handler=None):
        """
        Initialize custom channel.

        Args:
            config: Channel configuration
            handler: Custom async handler function
        """
        super().__init__(config)
        self.handler = handler

    async def send(self, alert: Alert) -> bool:
        """Send via custom handler."""
        if not self.handler:
            logger.error(f"Custom channel '{self.name}' has no handler configured")
            return False

        try:
            result = await self.handler(alert)
            return bool(result)
        except Exception as e:
            logger.error(f"Custom handler error in '{self.name}': {e}")
            return False


class NotificationRouter:
    """
    Routes alerts to appropriate notification channels.

    Manages multiple notification channels and handles alert distribution
    based on severity filters and channel configuration.
    """

    def __init__(self):
        """Initialize notification router."""
        self.channels: Dict[str, NotificationChannel] = {}
        self.notification_history: List[Dict[str, Any]] = []

    def register_channel(self, channel: NotificationChannel):
        """
        Register a notification channel.

        Args:
            channel: NotificationChannel to register
        """
        self.channels[channel.name] = channel
        logger.info(f"Registered notification channel: {channel.name}")

    def unregister_channel(self, channel_name: str) -> bool:
        """
        Unregister a notification channel.

        Args:
            channel_name: Name of channel to remove

        Returns:
            True if channel was removed
        """
        if channel_name in self.channels:
            del self.channels[channel_name]
            logger.info(f"Unregistered notification channel: {channel_name}")
            return True
        return False

    async def route_alert(self, alert: Alert) -> Dict[str, bool]:
        """
        Route alert to all eligible notification channels.

        Args:
            alert: Alert to route

        Returns:
            Dict mapping channel names to send status
        """
        results = {}

        for name, channel in self.channels.items():
            if not channel.enabled:
                continue

            if not channel.config.should_notify(alert):
                continue

            try:
                success = await channel.send(alert)
                results[name] = success

                # Record in history
                self.notification_history.append({
                    "alert_id": alert.id,
                    "channel": name,
                    "success": success,
                    "timestamp": alert.timestamp,
                    "severity": alert.severity.value,
                })

            except Exception as e:
                logger.error(f"Error sending alert to channel '{name}': {e}")
                results[name] = False

        return results

    def get_channel(self, channel_name: str) -> Optional[NotificationChannel]:
        """Get a specific channel by name."""
        return self.channels.get(channel_name)

    def list_channels(self) -> List[str]:
        """Get list of registered channel names."""
        return list(self.channels.keys())

    def get_channel_status(self) -> Dict[str, Any]:
        """Get status of all channels."""
        return {
            name: {
                "enabled": channel.enabled,
                "type": channel.config.channel_type,
                "severity_filter": [s.value for s in channel.config.severity_filter]
                if channel.config.severity_filter
                else None,
            }
            for name, channel in self.channels.items()
        }

    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent notification history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of notification records
        """
        return self.notification_history[-limit:]

    def clear_history(self):
        """Clear notification history."""
        self.notification_history.clear()


def create_default_channels() -> List[NotificationChannel]:
    """
    Create default notification channels.

    Returns:
        List of pre-configured channels
    """
    channels = []

    # Log channel for all alerts
    log_config = NotificationConfig(
        channel_type="log",
        name="default_log",
        enabled=True,
    )
    channels.append(LogNotificationChannel(log_config))

    # Console channel for critical alerts only
    console_config = NotificationConfig(
        channel_type="console",
        name="critical_console",
        enabled=True,
        severity_filter=[AlertSeverity.CRITICAL, AlertSeverity.ERROR],
    )
    channels.append(ConsoleNotificationChannel(console_config))

    return channels


# Global router instance
_notification_router: Optional[NotificationRouter] = None


def get_notification_router() -> NotificationRouter:
    """Get or create global notification router singleton."""
    global _notification_router
    if _notification_router is None:
        _notification_router = NotificationRouter()

        # Register default channels
        for channel in create_default_channels():
            _notification_router.register_channel(channel)

    return _notification_router
