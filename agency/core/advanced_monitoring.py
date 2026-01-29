from typing import Dict, Any, List, Optional, Callable, Union
import asyncio
import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from ..utils.logger import get_logger


class AlertSeverity(Enum):
    """Severity levels for alerts"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts"""
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    SYSTEM_HEALTH = "system_health"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Representation of an alert"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    source: str
    data: Dict[str, Any] = None
    acknowledged: bool = False
    acknowledged_by: str = None
    acknowledged_at: datetime = None


class AlertNotifier:
    """Notifies alerts through various channels"""
    
    def __init__(self):
        self.notifiers: Dict[str, Callable] = {
            "console": self._notify_console,
            "email": self._notify_email,
            "webhook": self._notify_webhook,
            "slack": self._notify_slack
        }
        self._logger = get_logger(__name__)
    
    def add_notifier(self, name: str, notifier_func: Callable):
        """Add a custom notifier"""
        self.notifiers[name] = notifier_func
    
    async def notify(self, alert: Alert, channels: List[str] = None):
        """Send an alert through specified channels"""
        if channels is None:
            channels = ["console"]  # Default to console
        
        for channel in channels:
            if channel in self.notifiers:
                try:
                    await self.notifiers[channel](alert)
                except Exception as e:
                    self._logger.error(f"Failed to send alert via {channel}: {e}")
            else:
                self._logger.warning(f"Unknown notification channel: {channel}")
    
    async def _notify_console(self, alert: Alert):
        """Notify via console/log"""
        self._logger.warning(f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.description}")
    
    async def _notify_email(self, alert: Alert):
        """Notify via email (placeholder implementation)"""
        # This would require SMTP configuration
        self._logger.info(f"Email notification would be sent for alert: {alert.title}")
    
    async def _notify_webhook(self, alert: Alert):
        """Notify via webhook"""
        # Placeholder - would call configured webhook URLs
        self._logger.info(f"Webhook notification would be sent for alert: {alert.title}")
    
    async def _notify_slack(self, alert: Alert):
        """Notify via Slack"""
        # Placeholder - would call Slack API
        self._logger.info(f"Slack notification would be sent for alert: {alert.title}")


class MetricThreshold:
    """Defines threshold conditions for triggering alerts"""
    
    def __init__(self, metric_name: str, condition: str, threshold: float, window: timedelta = None):
        self.metric_name = metric_name
        self.condition = condition  # 'gt', 'lt', 'ge', 'le', 'eq', 'ne'
        self.threshold = threshold
        self.window = window or timedelta(minutes=5)  # Default 5-minute window
    
    def evaluate(self, current_value: float) -> bool:
        """Evaluate if the threshold condition is met"""
        if self.condition == 'gt':
            return current_value > self.threshold
        elif self.condition == 'lt':
            return current_value < self.threshold
        elif self.condition == 'ge':
            return current_value >= self.threshold
        elif self.condition == 'le':
            return current_value <= self.threshold
        elif self.condition == 'eq':
            return current_value == self.threshold
        elif self.condition == 'ne':
            return current_value != self.threshold
        else:
            raise ValueError(f"Unknown condition: {self.condition}")


class AlertRule:
    """Defines a rule for triggering alerts based on metrics"""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        alert_type: AlertType, 
        severity: AlertSeverity,
        condition: Callable[[Dict[str, Any]], bool],
        notification_channels: List[str] = None
    ):
        self.name = name
        self.description = description
        self.alert_type = alert_type
        self.severity = severity
        self.condition = condition  # Function that takes metrics dict and returns bool
        self.notification_channels = notification_channels or ["console"]
        self.triggered = False  # Track if alert is currently triggered


class MonitoringService:
    """Centralized monitoring service for the agency"""
    
    def __init__(self):
        self.metrics_collector = None  # Will be set from monitoring module
        self.alert_notifier = AlertNotifier()
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: List[Alert] = []
        self._alert_id_counter = 0
        self._logger = get_logger(__name__)
        self._monitoring_task = None
        self._shutdown = False
    
    def set_metrics_collector(self, collector):
        """Set the metrics collector to use"""
        self.metrics_collector = collector
    
    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.alert_rules.append(rule)
        self._logger.info(f"Added alert rule: {rule.name}")
    
    def create_alert_rule_from_threshold(
        self, 
        name: str, 
        metric_name: str, 
        condition: str, 
        threshold: float,
        alert_type: AlertType,
        severity: AlertSeverity,
        description: str = "",
        notification_channels: List[str] = None
    ) -> AlertRule:
        """Create an alert rule based on a metric threshold"""
        threshold_obj = MetricThreshold(metric_name, condition, threshold)
        
        def condition_func(metrics: Dict[str, Any]) -> bool:
            if metric_name in metrics:
                current_value = metrics[metric_name]
                if isinstance(current_value, list) and len(current_value) > 0:
                    # If it's a list, use the most recent value
                    current_value = current_value[-1]['value'] if isinstance(current_value[-1], dict) else current_value[-1]
                return threshold_obj.evaluate(float(current_value))
            return False
        
        rule = AlertRule(
            name=name,
            description=description or f"Alert when {metric_name} {condition} {threshold}",
            alert_type=alert_type,
            severity=severity,
            condition=condition_func,
            notification_channels=notification_channels
        )
        
        self.add_alert_rule(rule)
        return rule
    
    async def start_monitoring(self, check_interval: float = 30.0):
        """Start the monitoring loop"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._logger.warning("Monitoring is already running")
            return
        
        self._shutdown = False
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(check_interval))
        self._logger.info(f"Started monitoring with {check_interval}s interval")
    
    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self._shutdown = True
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Stopped monitoring")
    
    async def _monitoring_loop(self, check_interval: float):
        """Main monitoring loop"""
        while not self._shutdown:
            try:
                # Evaluate all alert rules
                await self._evaluate_alert_rules()
                
                # Sleep until next check
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in monitoring loop: {e}")
                # Continue monitoring despite errors
    
    async def _evaluate_alert_rules(self):
        """Evaluate all alert rules and trigger alerts if conditions are met"""
        if not self.metrics_collector:
            return
        
        # Get current metrics
        # Note: This assumes the metrics collector has a get_latest_values method
        # In a real implementation, you'd need to adapt this to your actual metrics collector
        try:
            # Placeholder - in real implementation, get actual metrics
            current_metrics = {}
            if hasattr(self.metrics_collector, 'get_latest_values'):
                current_metrics = self.metrics_collector.get_latest_values()
            elif hasattr(self.metrics_collector, 'get_metrics'):
                # Get all metrics and extract latest values
                all_metrics = self.metrics_collector.get_metrics()
                for metric in all_metrics:
                    if metric.name not in current_metrics:
                        current_metrics[metric.name] = []
                    current_metrics[metric.name].append({'value': metric.value, 'timestamp': metric.timestamp})
        
            for rule in self.alert_rules:
                is_triggered = rule.condition(current_metrics)
                
                if is_triggered and not rule.triggered:
                    # Alert condition is met and wasn't previously triggered
                    await self._trigger_alert(rule, current_metrics)
                    rule.triggered = True
                elif not is_triggered and rule.triggered:
                    # Alert condition is no longer met, resolve the alert
                    await self._resolve_alert(rule)
                    rule.triggered = False
        except Exception as e:
            self._logger.error(f"Error evaluating alert rules: {e}")
    
    async def _trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Trigger an alert based on a rule"""
        self._alert_id_counter += 1
        alert_id = f"alert_{self._alert_id_counter}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            type=rule.alert_type,
            severity=rule.severity,
            title=f"Alert: {rule.name}",
            description=rule.description,
            timestamp=datetime.now(),
            source="MonitoringService",
            data=metrics
        )
        
        self.active_alerts.append(alert)
        
        # Notify about the alert
        await self.alert_notifier.notify(alert, rule.notification_channels)
        
        self._logger.warning(f"Triggered alert: {alert.title} (ID: {alert.id})")
    
    async def _resolve_alert(self, rule: AlertRule):
        """Resolve an alert when condition is no longer met"""
        # Find and remove the active alert for this rule
        for i, alert in enumerate(self.active_alerts):
            if alert.title == f"Alert: {rule.name}" and not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                self._logger.info(f"Resolved alert: {alert.title} (ID: {alert.id})")
                break
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.active_alerts if not alert.acknowledged]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system"):
        """Acknowledge an alert"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                self._logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
                return True
        return False


class HealthChecker:
    """Checks health of various system components"""
    
    def __init__(self, registry, task_lifecycle_manager):
        self.registry = registry
        self.task_lifecycle_manager = task_lifecycle_manager
        self._logger = get_logger(__name__)
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {},
            "issues": []
        }
        
        # Check domain registry
        domains = self.registry.get_all_domains()
        health_report["components"]["domain_registry"] = {
            "status": "healthy" if domains else "warning",
            "domain_count": len(domains),
            "domains": [d.name for d in domains]
        }
        
        if not domains:
            health_report["issues"].append("No domains registered")
            health_report["overall_status"] = "unhealthy"
        
        # Check communication system
        # This would check the communication hub status
        health_report["components"]["communication_system"] = {
            "status": "healthy",  # Placeholder
            "message": "Communication system operational"
        }
        
        # Check resource usage
        # This would check actual resource usage vs quotas
        health_report["components"]["resource_management"] = {
            "status": "healthy",  # Placeholder
            "message": "Resource management operational"
        }
        
        # Check task lifecycle manager
        # This would check agent pools and task queues
        health_report["components"]["task_lifecycle"] = {
            "status": "healthy",  # Placeholder
            "message": "Task lifecycle management operational"
        }
        
        # Update overall status based on component statuses
        for comp_name, comp_status in health_report["components"].items():
            if comp_status["status"] == "unhealthy":
                health_report["overall_status"] = "unhealthy"
            elif comp_status["status"] == "warning" and health_report["overall_status"] == "healthy":
                health_report["overall_status"] = "warning"
        
        return health_report
    
    async def check_domain_health(self, domain_name: str) -> Dict[str, Any]:
        """Check health of a specific domain"""
        domain = self.registry.get_domain(domain_name)
        if not domain:
            return {
                "domain": domain_name,
                "status": "not_found",
                "error": f"Domain {domain_name} not found"
            }
        
        # Perform a simple test operation
        try:
            # Use a simple query that should work for most domains
            test_input = "health check"
            if hasattr(domain, 'can_handle') and hasattr(domain, 'execute'):
                # Create a minimal DomainInput for testing
                from ..core.base_domain import DomainInput
                input_data = DomainInput(query=test_input)
                
                if domain.can_handle(input_data):
                    result = await domain.execute(input_data)
                    return {
                        "domain": domain_name,
                        "status": "healthy" if result.success else "unhealthy",
                        "response_time": getattr(result, 'execution_time', 'unknown'),
                        "message": result.error if not result.success else "OK"
                    }
                else:
                    return {
                        "domain": domain_name,
                        "status": "healthy",  # Can't handle health check, but domain exists
                        "message": "Domain exists but doesn't handle health checks"
                    }
            else:
                return {
                    "domain": domain_name,
                    "status": "unhealthy",
                    "error": "Domain doesn't have required methods"
                }
        except Exception as e:
            return {
                "domain": domain_name,
                "status": "unhealthy", 
                "error": str(e)
            }


# Global monitoring service instance
monitoring_service = MonitoringService()


def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service"""
    return monitoring_service