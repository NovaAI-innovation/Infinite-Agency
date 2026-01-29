from typing import Callable, Any, Optional, Dict, List, Union, Type
import asyncio
import time
import random
import functools
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import traceback
from ..utils.logger import get_logger


class ErrorCategory(Enum):
    """Categories of errors for classification"""
    TRANSIENT = "transient"      # Temporary issues that may resolve themselves
    PERMANENT = "permanent"      # Issues that won't resolve without intervention
    RESOURCE = "resource"        # Resource-related issues (limits, quotas, etc.)
    VALIDATION = "validation"    # Input validation errors
    COMMUNICATION = "communication"  # Network/communication errors
    BUSINESS_LOGIC = "business_logic"  # Domain-specific business logic errors


@dataclass
class ErrorInfo:
    """Information about an error for handling decisions"""
    exception: Exception
    category: ErrorCategory
    timestamp: float
    retry_count: int = 0
    context: Dict[str, Any] = None


class RetryStrategy(Enum):
    """Different strategies for retrying operations"""
    FIXED_INTERVAL = "fixed_interval"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    CUSTOM = "custom"


@dataclass
class RetryPolicy:
    """Policy defining how retries should be handled"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0   # Maximum delay in seconds
    jitter: bool = True       # Add randomness to delays
    multiplier: float = 2.0   # Multiplier for exponential backoff
    retryable_errors: List[Type[Exception]] = None  # Specific errors to retry
    non_retryable_errors: List[Type[Exception]] = None  # Errors not to retry
    
    def __post_init__(self):
        if self.retryable_errors is None:
            self.retryable_errors = [ConnectionError, TimeoutError, asyncio.TimeoutError]
        if self.non_retryable_errors is None:
            self.non_retryable_errors = [ValueError, TypeError, NotImplementedError]


class ErrorHandler(ABC):
    """Abstract base class for error handlers"""
    
    @abstractmethod
    async def handle_error(self, error_info: ErrorInfo) -> bool:
        """Handle an error and return whether to retry"""
        pass


class TransientErrorHandler(ErrorHandler):
    """Handles transient errors with retry logic"""
    
    def __init__(self, policy: RetryPolicy):
        self.policy = policy
        self._logger = get_logger(__name__)
    
    async def handle_error(self, error_info: ErrorInfo) -> bool:
        """Handle a transient error with retry logic"""
        if error_info.retry_count >= self.policy.max_attempts:
            self._logger.error(f"Max retry attempts ({self.policy.max_attempts}) exceeded for error: {error_info.exception}")
            return False
        
        # Check if this error type should be retried
        should_retry = self._should_retry_error(error_info.exception)
        if not should_retry:
            self._logger.info(f"Not retrying non-retryable error: {type(error_info.exception).__name__}")
            return False
        
        # Calculate delay before next retry
        delay = self._calculate_delay(error_info.retry_count)
        self._logger.warning(f"Retrying after error (attempt {error_info.retry_count + 1}/{self.policy.max_attempts}): {error_info.exception}. Delay: {delay:.2f}s")
        
        # Wait before retry
        await asyncio.sleep(delay)
        
        return True
    
    def _should_retry_error(self, exception: Exception) -> bool:
        """Determine if an error should be retried"""
        exc_type = type(exception)
        
        # Check non-retryable errors first (higher priority)
        if any(isinstance(exception, err_type) for err_type in self.policy.non_retryable_errors):
            return False
        
        # Check retryable errors
        if any(isinstance(exception, err_type) for err_type in self.policy.retryable_errors):
            return True
        
        # Default behavior based on error category
        return error_info.category in [ErrorCategory.TRANSIENT, ErrorCategory.COMMUNICATION]
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on retry strategy"""
        if self.policy.strategy == RetryStrategy.FIXED_INTERVAL:
            delay = self.policy.base_delay
        elif self.policy.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.policy.base_delay * (attempt + 1)
        elif self.policy.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.policy.base_delay * (self.policy.multiplier ** attempt)
        elif self.policy.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            # Simple Fibonacci calculation
            fib_seq = [1, 1]
            for i in range(2, attempt + 2):
                fib_seq.append(fib_seq[i-1] + fib_seq[i-2])
            delay = self.policy.base_delay * fib_seq[attempt]
        else:
            delay = self.policy.base_delay  # Default to fixed interval
        
        # Apply jitter for better distribution
        if self.policy.jitter:
            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor
        
        # Cap the delay at max_delay
        return min(delay, self.policy.max_delay)


class PermanentErrorHandler(ErrorHandler):
    """Handles permanent errors - typically no retry"""
    
    def __init__(self):
        self._logger = get_logger(__name__)
    
    async def handle_error(self, error_info: ErrorInfo) -> bool:
        """Handle a permanent error - typically no retry"""
        self._logger.error(f"Permanent error occurred, not retrying: {error_info.exception}")
        return False


class ResourceErrorHandler(ErrorHandler):
    """Handles resource-related errors with specific strategies"""
    
    def __init__(self, policy: RetryPolicy):
        self.policy = policy
        self._logger = get_logger(__name__)
    
    async def handle_error(self, error_info: ErrorInfo) -> bool:
        """Handle a resource error with specific strategies"""
        # For resource errors, we might want to wait longer or implement backpressure
        if error_info.retry_count >= self.policy.max_attempts:
            self._logger.error(f"Max retry attempts exceeded for resource error: {error_info.exception}")
            return False
        
        # Resource errors often benefit from longer delays
        delay = self.policy.base_delay * (2 ** error_info.retry_count)  # Exponential backoff
        if self.policy.jitter:
            delay *= random.uniform(1.0, 1.5)  # More conservative jitter for resource errors
        
        delay = min(delay, self.policy.max_delay)
        
        self._logger.warning(f"Retrying resource error (attempt {error_info.retry_count + 1}): {error_info.exception}. Delay: {delay:.2f}s")
        await asyncio.sleep(delay)
        
        return True


class ErrorHandlingManager:
    """Manages different error handlers and routes errors appropriately"""
    
    def __init__(self):
        self.handlers: Dict[ErrorCategory, ErrorHandler] = {}
        self.fallback_policy = RetryPolicy()
        self._logger = get_logger(__name__)
    
    def register_handler(self, category: ErrorCategory, handler: ErrorHandler):
        """Register a handler for a specific error category"""
        self.handlers[category] = handler
    
    def get_handler(self, category: ErrorCategory) -> ErrorHandler:
        """Get the appropriate handler for an error category"""
        return self.handlers.get(category)
    
    async def handle_error(self, exception: Exception, category: ErrorCategory, context: Dict[str, Any] = None) -> bool:
        """Handle an error using the appropriate strategy"""
        error_info = ErrorInfo(
            exception=exception,
            category=category,
            timestamp=time.time(),
            retry_count=getattr(exception, 'retry_count', 0),
            context=context
        )
        
        handler = self.get_handler(category)
        if handler is None:
            # Use fallback strategy for unhandled categories
            handler = TransientErrorHandler(self.fallback_policy)
        
        try:
            return await handler.handle_error(error_info)
        except Exception as e:
            self._logger.error(f"Error in error handler: {e}")
            # If the error handler itself fails, don't retry
            return False


class AsyncRetryExecutor:
    """Executes async functions with comprehensive retry logic"""
    
    def __init__(self, error_manager: ErrorHandlingManager, default_policy: RetryPolicy = None):
        self.error_manager = error_manager
        self.default_policy = default_policy or RetryPolicy()
        self._logger = get_logger(__name__)
    
    async def execute_with_retry(
        self, 
        func: Callable, 
        *args, 
        error_category: ErrorCategory = ErrorCategory.TRANSIENT,
        context: Dict[str, Any] = None,
        custom_policy: RetryPolicy = None,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic"""
        policy = custom_policy or self.default_policy
        retry_count = 0
        
        while True:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # Increment retry count on the exception for tracking
                if not hasattr(e, 'retry_count'):
                    e.retry_count = 0
                e.retry_count += 1
                retry_count = e.retry_count
                
                # Attempt to handle the error
                should_retry = await self.error_manager.handle_error(
                    e, error_category, {**(context or {}), "retry_count": retry_count}
                )
                
                if not should_retry:
                    self._logger.error(f"Execution failed after {retry_count} attempts: {e}")
                    raise e


# Global error handling manager instance
error_handling_manager = ErrorHandlingManager()
retry_executor = AsyncRetryExecutor(error_handling_manager)


def get_error_handling_manager() -> ErrorHandlingManager:
    """Get the global error handling manager"""
    return error_handling_manager


def get_retry_executor() -> AsyncRetryExecutor:
    """Get the global retry executor"""
    return retry_executor


def retryable(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retryable_errors: List[Type[Exception]] = None,
    non_retryable_errors: List[Type[Exception]] = None
):
    """Decorator to make async functions retryable"""
    def decorator(func):
        policy = RetryPolicy(
            max_attempts=max_attempts,
            strategy=strategy,
            base_delay=base_delay,
            max_delay=max_delay,
            jitter=jitter,
            retryable_errors=retryable_errors,
            non_retryable_errors=non_retryable_errors
        )
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            executor = AsyncRetryExecutor(error_handling_manager, policy)
            return await executor.execute_with_retry(func, *args, **kwargs)
        
        return wrapper
    return decorator