import logging
from typing import Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path
from pydantic import BaseSettings

class LoggingSettings(BaseSettings):
    # Log directory configuration
    LOG_DIR: str = "logs"
    LOG_FILE: str = "mcp.log"
    ERROR_LOG_FILE: str = "error.log"
    ACCESS_LOG_FILE: str = "access.log"
    PERFORMANCE_LOG_FILE: str = "performance.log"
    SECURITY_LOG_FILE: str = "security.log"
    AUDIT_LOG_FILE: str = "audit.log"
    
    # Log levels
    LOG_LEVEL: str = "INFO"
    ACCESS_LOG_LEVEL: str = "INFO"
    ERROR_LOG_LEVEL: str = "ERROR"
    PERFORMANCE_LOG_LEVEL: str = "INFO"
    SECURITY_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_LEVEL: str = "INFO"
    
    # Log format
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Log rotation
    MAX_BYTES: int = 10485760  # 10MB
    BACKUP_COUNT: int = 5
    
    # JSON logging
    JSON_LOGGING: bool = True
    JSON_FIELDS: Dict[str, str] = {
        "timestamp": "timestamp",
        "level": "level",
        "name": "name",
        "message": "message",
        "request_id": "request_id",
        "correlation_id": "correlation_id",
        "user_id": "user_id",
        "trace_id": "trace_id",
        "service": "service",
        "environment": "environment",
        "version": "version"
    }
    
    # Request logging
    REQUEST_LOGGING: bool = True
    REQUEST_LOG_FIELDS: List[str] = [
        "method",
        "path",
        "status_code",
        "duration_ms",
        "request_id",
        "correlation_id",
        "user_agent",
        "ip_address",
        "request_size",
        "response_size"
    ]
    
    # Error logging
    ERROR_LOGGING: bool = True
    ERROR_LOG_FIELDS: List[str] = [
        "exception_type",
        "exception_message",
        "stack_trace",
        "request_id",
        "correlation_id",
        "user_id",
        "error_code",
        "error_details"
    ]
    
    # Performance logging
    PERFORMANCE_LOGGING: bool = True
    PERFORMANCE_LOG_FIELDS: List[str] = [
        "operation",
        "duration_ms",
        "request_id",
        "correlation_id",
        "cache_hit",
        "db_queries",
        "memory_usage"
    ]
    
    # Security logging
    SECURITY_LOGGING: bool = True
    SECURITY_LOG_FIELDS: List[str] = [
        "event_type",
        "user_id",
        "ip_address",
        "request_id",
        "correlation_id",
        "authentication_type",
        "authentication_result"
    ]
    
    # Audit logging
    AUDIT_LOGGING: bool = True
    AUDIT_LOG_FIELDS: List[str] = [
        "action",
        "resource",
        "user_id",
        "request_id",
        "correlation_id",
        "old_value",
        "new_value",
        "timestamp"
    ]
    
    # Log handlers
    HANDLERS: Dict[str, Dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "mcp.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "error.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "access.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT
        },
        "performance_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "performance.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "security.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT
        },
        "audit_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "audit.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT
        }
    }
    
    # Log formatters
    FORMATTERS: Dict[str, Dict[str, Any]] = {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": DATE_FORMAT
        },
        "json": {
            "()": "mcp.utils.json_logging.JSONFormatter",
            "fields": JSON_FIELDS
        }
    }
    
    # Loggers
    LOGGERS: Dict[str, Dict[str, Any]] = {
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console", "file", "error_file"]
        },
        "access": {
            "level": ACCESS_LOG_LEVEL,
            "handlers": ["access_file"]
        },
        "error": {
            "level": ERROR_LOG_LEVEL,
            "handlers": ["error_file"]
        },
        "performance": {
            "level": PERFORMANCE_LOG_LEVEL,
            "handlers": ["performance_file"]
        },
        "security": {
            "level": SECURITY_LOG_LEVEL,
            "handlers": ["security_file"]
        },
        "audit": {
            "level": AUDIT_LOG_LEVEL,
            "handlers": ["audit_file"]
        }
    }
    
    # Additional logging settings
    SENTRY_ENABLED: bool = False
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_RELEASE: str = ""
    
    # Log retention
    LOG_RETENTION_DAYS: int = 30
    
    # Log cleanup
    CLEANUP_INTERVAL_HOURS: int = 24
    
    # External logging
    ELASTICSEARCH_ENABLED: bool = False
    ELASTICSEARCH_HOSTS: List[str] = []
    ELASTICSEARCH_INDEX: str = "mcp-logs"
    
    # Log sampling
    ERROR_SAMPLE_RATE: float = 1.0
    INFO_SAMPLE_RATE: float = 0.1
    
    # Log compression
    COMPRESS_LOGS: bool = True
    COMPRESSION_LEVEL: int = 9
    
    class Config:
        env_prefix = "LOGGING_"
        case_sensitive = True

# Create logging settings instance
logging_settings = LoggingSettings()

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log message
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "correlation_id": getattr(record, "correlation_id", "-"),
            "user_id": getattr(record, "user_id", "-"),
            "source": getattr(record, "source", "-"),
            "context": getattr(record, "context", {})
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

class LogConfig:
    def __init__(self):
        self.log_dir = Path(logging_settings.LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def get_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Dictionary containing logging configuration
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JSONFormatter
                },
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "json",
                    "filename": str(self.log_dir / logging_settings.LOG_FILE),
                    "maxBytes": logging_settings.MAX_BYTES,  # 10MB
                    "backupCount": logging_settings.BACKUP_COUNT,
                    "encoding": "utf8"
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "json",
                    "filename": str(self.log_dir / logging_settings.ERROR_LOG_FILE),
                    "maxBytes": logging_settings.MAX_BYTES,  # 10MB
                    "backupCount": logging_settings.BACKUP_COUNT,
                    "encoding": "utf8",
                    "level": "ERROR"
                }
            },
            "loggers": {
                "mcp": {
                    "handlers": ["console", "file", "error_file"],
                    "level": logging_settings.LOG_LEVEL,
                    "propagate": False
                },
                "uvicorn": {
                    "handlers": ["console", "file", "error_file"],
                    "level": logging_settings.LOG_LEVEL,
                    "propagate": False
                },
                "fastapi": {
                    "handlers": ["console", "file", "error_file"],
                    "level": logging_settings.LOG_LEVEL,
                    "propagate": False
                }
            }
        }

# Create logging configuration instance
log_config = LogConfig()
