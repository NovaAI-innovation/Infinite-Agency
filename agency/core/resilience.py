from typing import Callable, Any, Optional, Dict
import asyncio
import time
import functools
from enum import Enum
from dataclasses import dataclass
from ..utils.logger import get_logger


class CircuitState(Enum):
    """States for circuit breaker pattern"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Tripped, requests blocked
    HALF_OPEN = "half_open"  # Testing if failure condition is resolved


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None


class CircuitBreaker:
    """Circuit breaker implementation for resilience"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        reset_timeout: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.reset_timeout = reset_timeout
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._last_attempt_time: Optional[float] = None
        self._logger = get_logger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call a function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self._logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN - request rejected")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    async def acall(self, func: Callable, *args, **kwargs) -> Any:
        """Async version of call with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self._logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN - request rejected")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Called when operation succeeds"""
        self.metrics.success_count += 1
        self.metrics.failure_count = 0  # Reset failure count on success
        self.state = CircuitState.CLOSED
        self._logger.debug("Circuit breaker operation succeeded")
    
    def _on_failure(self):
        """Called when operation fails"""
        self.metrics.failure_count += 1
        self.metrics.last_failure_time = time.time()
        
        if self.metrics.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self._logger.warning(f"Circuit breaker OPENED after {self.metrics.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.metrics.last_failure_time is None:
            return False
        
        time_since_failure = time.time() - self.metrics.last_failure_time
        return time_since_failure >= self.reset_timeout


class RetryHandler:
    """Handles retry logic with exponential backoff"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._logger = get_logger(__name__)
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                if attempt > 0:
                    self._logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                if attempt == self.max_attempts - 1:
                    self._logger.error(f"Operation failed after {self.max_attempts} attempts: {e}")
                    raise e
                
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                self._logger.warning(f"Operation failed on attempt {attempt + 1}, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
        
        # This should never be reached, but included for completeness
        raise last_exception or Exception("Unknown error in retry handler")


class ResilienceManager:
    """Manages resilience patterns across the agency"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self._logger = get_logger(__name__)
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create a circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            from .config import get_config
            config = get_config()
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold,
                timeout=config.circuit_breaker_timeout
            )
        return self.circuit_breakers[service_name]
    
    def get_retry_handler(self, service_name: str) -> RetryHandler:
        """Get or create a retry handler for a service"""
        if service_name not in self.retry_handlers:
            from .config import get_config
            config = get_config()
            self.retry_handlers[service_name] = RetryHandler(
                max_attempts=config.max_retry_attempts,
                base_delay=config.retry_delay_base
            )
        return self.retry_handlers[service_name]
    
    async def execute_with_resilience(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with both circuit breaker and retry protection"""
        circuit_breaker = self.get_circuit_breaker(service_name)
        retry_handler = self.get_retry_handler(service_name)
        
        async def protected_func(*f_args, **f_kwargs):
            return await circuit_breaker.acall(retry_handler.execute_with_retry, func, *f_args, **f_kwargs)
        
        return await protected_func(*args, **kwargs)


# Global resilience manager instance
resilience_manager = ResilienceManager()


def get_resilience_manager() -> ResilienceManager:
    """Get the global resilience manager"""
    return resilience_manager