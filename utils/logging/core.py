import logging
import contextvars
from functools import wraps

_current_logger = contextvars.ContextVar("current_logger", default=None)

def get_logger():
    logger = _current_logger.get()
    if logger is None:
        raise RuntimeError("No logger is active. Use inside a @logged function.")
    return logger

def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        token = _current_logger.set(logger)
        try:
            return func(*args, **kwargs)
        finally:
            _current_logger.reset(token)
    return wrapper
