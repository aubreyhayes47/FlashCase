"""
Centralized logging configuration for FlashCase backend.

Provides structured logging with JSON formatting for production environments
and human-readable formatting for development.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs logs in JSON format for easy parsing by log aggregation tools
    like CloudWatch, Stackdriver, or ELK stack.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add specific fields for different log types
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        
        if hasattr(record, "method"):
            log_data["method"] = record.method
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # AI-specific fields
        if hasattr(record, "tokens_used"):
            log_data["tokens_used"] = record.tokens_used
        
        if hasattr(record, "model"):
            log_data["model"] = record.model
        
        if hasattr(record, "cost_estimate"):
            log_data["cost_estimate"] = record.cost_estimate
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for development environments.
    
    Makes logs more readable in terminal with color coding.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build message
        message = f"{color}[{record.levelname}]{reset} {timestamp} - {record.name} - {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


def setup_logging(environment: str = "development", log_level: str = "INFO") -> None:
    """
    Setup application logging configuration.
    
    Args:
        environment: Environment name ('development', 'production', 'staging')
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Use JSON formatter for production, colored for development
    if environment.lower() in ["production", "prod", "staging"]:
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set logging levels for specific modules
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Keep our application logs at specified level
    logging.getLogger("app").setLevel(getattr(logging, log_level.upper()))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Request logging helper
class RequestLogger:
    """Helper class for logging HTTP requests with consistent format."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize request logger."""
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        user_id: str = None,
        request_id: str = None,
        extra: Dict[str, Any] = None
    ) -> None:
        """
        Log HTTP request with standard fields.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            user_id: Optional user ID
            request_id: Optional request ID for tracing
            extra: Optional extra fields to include
        """
        log_record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "",
            0,
            f"{method} {endpoint} - {status_code} ({duration_ms:.2f}ms)",
            (),
            None
        )
        
        log_record.method = method
        log_record.endpoint = endpoint
        log_record.status_code = status_code
        log_record.duration_ms = duration_ms
        
        if user_id:
            log_record.user_id = user_id
        
        if request_id:
            log_record.request_id = request_id
        
        if extra:
            log_record.extra_fields = extra
        
        self.logger.handle(log_record)


# AI logging helper
class AILogger:
    """Helper class for logging AI operations with token usage."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize AI logger."""
        self.logger = logger
    
    def log_ai_request(
        self,
        operation: str,
        model: str,
        tokens_used: int,
        cost_estimate: float,
        duration_ms: float,
        user_id: str = None,
        success: bool = True,
        error: str = None
    ) -> None:
        """
        Log AI operation with token usage and cost.
        
        Args:
            operation: AI operation name (chat, rewrite, autocomplete)
            model: AI model used
            tokens_used: Number of tokens consumed
            cost_estimate: Estimated cost in dollars
            duration_ms: Operation duration in milliseconds
            user_id: Optional user ID
            success: Whether operation was successful
            error: Optional error message
        """
        level = logging.INFO if success else logging.ERROR
        message = f"AI {operation} - {model} - {tokens_used} tokens (${cost_estimate:.4f}) in {duration_ms:.2f}ms"
        
        if error:
            message += f" - Error: {error}"
        
        log_record = self.logger.makeRecord(
            self.logger.name,
            level,
            "",
            0,
            message,
            (),
            None
        )
        
        log_record.operation = operation
        log_record.model = model
        log_record.tokens_used = tokens_used
        log_record.cost_estimate = cost_estimate
        log_record.duration_ms = duration_ms
        log_record.success = success
        
        if user_id:
            log_record.user_id = user_id
        
        if error:
            log_record.error = error
        
        self.logger.handle(log_record)
