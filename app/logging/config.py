import logging
import logging.config
import os
import yaml
import time
import json
from logging.handlers import RotatingFileHandler
from app.config.settings import settings

def setup_logging():
    """Configure the logging system using a YAML file or defaults."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Default configuration if YAML file is missing
    default_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(message)s",
                "class": "app.logging.config.JSONFormatter"
            },
            "console": {
                "format": "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filename": os.path.join(log_dir, "app.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG" if settings.environment == "development" else "INFO",
                "formatter": "console" if os.getenv("LOG_CONSOLE_JSON", "false").lower() != "true" else "json"
            }
        },
        "loggers": {
            "devanchor": {
                "level": "DEBUG" if settings.environment == "development" else "INFO",
                "handlers": ["file", "console"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
    
    # Load YAML configuration if available
    config_path = os.path.join(os.path.dirname(__file__), "logging.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = default_config
    
    # Apply configuration
    logging.config.dictConfig(config)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        try:
            # Convert record.created (float timestamp) to struct_time
            ct = time.localtime(record.created)
            # Format timestamp with milliseconds
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            microsecond = int(record.msecs * 1000)
            timestamp = f"{timestamp}.{microsecond:06d}"

            log_data = {
                "timestamp": timestamp,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "funcName": record.funcName,
                "line": record.lineno,
            }
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            if hasattr(record, 'extra'):
                log_data.update(getattr(record, 'extra', {}))
            return json.dumps(log_data)
        except Exception as e:
            return json.dumps({"error": f"Failed to format log: {str(e)}"})