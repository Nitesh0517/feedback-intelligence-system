import logging
import sys
import re
from typing import Any

# Patterns to mask sensitive tokens/passwords
SENSITIVE_PATTERNS = [
    re.compile(r"(api[-_]?key|password|secret|token)[\s:=]+['\"]?([^\s'\"]+)['\"]?", re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Filter that masks sensitive credentials from logs."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in SENSITIVE_PATTERNS:
                msg = pattern.sub(r"\1: [REDACTED]", msg)
            record.msg = msg
        return True


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured, secret-safe logging."""
    logger = logging.getLogger("feedback_intelligence")
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        
        logger.addHandler(handler)
        logger.propagate = False
        
    return logger


logger = setup_logging()
