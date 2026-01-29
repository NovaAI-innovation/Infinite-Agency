from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import time
import threading
import asyncio
from enum import Enum
from ..utils.logger import get_logger


class MetricType(Enum):
    """Types of metrics that can be collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Represents a metric value"""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str]
    timestamp: datetime


class MetricsCollector:
    """Collects metrics from the agency system"""
    
    def __init__(self):
        self._metrics: List[Metric] = []
        self._lock = threading.Lock()
        self._logger = get_logger(__name__)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, labels: Dict[str, str] = None):
        """Record a metric value"""
        with self._lock:
            metric = Metric(
                name=name,
                type=metric_type,
                value=value,
                labels=labels or {},
                timestamp=datetime.now()
            )
            self._metrics.append(metric)
    
    def get_metrics(self, name: str = None, labels: Dict[str, str] = None) -> List[Metric]:
        """Get metrics, optionally filtered by name and labels"""
        with self._lock:
            result = self._metrics
            
            if name:
                result = [m for m in result if m.name == name]
            
            if labels:
                result = [m for m in result if all(m.labels.get(k) == v for k, v in labels.items())]
            
            return result.copy()
    
    def get_latest_value(self, name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get the latest value for a metric"""
        metrics = self.get_metrics(name, labels)
        if metrics:
            return metrics[-1].value
        return None
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        with self._lock:
            self._metrics.clear()


class EventLogger:
    """Logs events in the agency system"""
    
    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._logger = get_logger(__name__)
    
    def log_event(self, event_type: str, domain: str, message: str, data: Dict[str, Any] = None):
        """Log an event"""
        with self._lock:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "domain": domain,
                "message": message,
                "data": data or {}
            }
            self._events.append(event)
    
    def get_events(self, event_type: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Get events, optionally filtered by type and domain"""
        with self._lock:
            result = self._events
            
            if event_type:
                result = [e for e in result if e["event_type"] == event_type]
            
            if domain:
                result = [e for e in result if e["domain"] == domain]
            
            return result.copy()
    
    def clear_events(self):
        """Clear all logged events"""
        with self._lock:
            self._events.clear()


class PerformanceMonitor:
    """Monitors performance of domain operations"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.event_logger = EventLogger()
        self._start_times: Dict[str, float] = {}
        self._logger = get_logger(__name__)
    
    def start_operation(self, operation_id: str, domain: str, operation_type: str):
        """Start timing an operation"""
        self._start_times[operation_id] = time.time()
        self.event_logger.log_event(
            event_type="operation_start",
            domain=domain,
            message=f"Started {operation_type} operation",
            data={"operation_id": operation_id, "operation_type": operation_type}
        )
    
    def end_operation(self, operation_id: str, domain: str, success: bool, error: str = None):
        """End timing an operation and record metrics"""
        start_time = self._start_times.pop(operation_id, None)
        if start_time is None:
            return
        
        duration = time.time() - start_time
        
        # Record performance metrics
        self.metrics_collector.record_metric(
            name="operation_duration_seconds",
            value=duration,
            metric_type=MetricType.HISTOGRAM,
            labels={"domain": domain, "success": str(success)}
        )
        
        self.metrics_collector.record_metric(
            name="operations_total",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"domain": domain, "success": str(success)}
        )
        
        # Log completion event
        status = "success" if success else "failure"
        message = f"Completed operation with {status}"
        if error:
            message += f": {error}"
        
        self.event_logger.log_event(
            event_type="operation_end",
            domain=domain,
            message=message,
            data={
                "operation_id": operation_id,
                "duration": duration,
                "success": success,
                "error": error
            }
        )
    
    async def monitor_async_operation(self, operation_id: str, domain: str, operation_type: str, coro):
        """Monitor an async operation"""
        self.start_operation(operation_id, domain, operation_type)
        try:
            result = await coro
            self.end_operation(operation_id, domain, True)
            return result
        except Exception as e:
            self.end_operation(operation_id, domain, False, str(e))
            raise


# Global monitoring instance
monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor"""
    return monitor