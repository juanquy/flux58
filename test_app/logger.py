import datetime
import os
import sys
import traceback
import logging
from logging.handlers import RotatingFileHandler
import threading

# Global logger instance
app_logger = None
db = None

# Log levels
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

# Thread-local storage for request context
_thread_local = threading.local()

def set_request_context(user_id=None, ip_address=None):
    """Set user information for the current request/thread"""
    _thread_local.user_id = user_id
    _thread_local.ip_address = ip_address

def get_request_context():
    """Get user information for the current request/thread"""
    user_id = getattr(_thread_local, 'user_id', None)
    ip_address = getattr(_thread_local, 'ip_address', None)
    return user_id, ip_address

def clear_request_context():
    """Clear user information for the current request/thread"""
    if hasattr(_thread_local, 'user_id'):
        del _thread_local.user_id
    if hasattr(_thread_local, 'ip_address'):
        del _thread_local.ip_address

def setup_logger(name, log_dir='logs', log_level=logging.INFO):
    """
    Set up a logger instance for a specific module
    
    Args:
        name: Name of the module (e.g. __name__)
        log_dir: Directory to store log files
        log_level: Log level (default: INFO)
        
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # If handlers are already configured, return logger
    if logger.handlers:
        return logger
    
    # Format for log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating, max 10MB, keep 10 backup files)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'flux58.log'),
        maxBytes=10*1024*1024,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Don't propagate to root logger
    logger.propagate = False
    
    return logger

def init_logger(database=None, log_dir='logs', log_level=logging.INFO):
    """Initialize the main application logger"""
    global app_logger, db
    
    if app_logger is not None:
        return app_logger
    
    # Store database instance for database logging
    db = database
    
    # Set up main app logger
    app_logger = setup_logger('flux58', log_dir, log_level)
    
    return app_logger

def _log_to_database(level, module, message):
    """Log message to database if database is available"""
    if db is None:
        return
    
    try:
        # Get request context
        user_id, ip_address = get_request_context()
        
        # Log to database using PostgreSQL
        db.add_log(level, module, message, user_id, ip_address)
    except Exception as e:
        # If database logging fails, at least log to file
        if app_logger:
            app_logger.error(f"Failed to log to database: {str(e)}")

def debug(message, module=None):
    """Log a debug message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.debug(message)
    
    # Debug messages are typically not logged to DB to avoid filling it up

def info(message, module=None):
    """Log an info message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.info(message)
    
    _log_to_database(INFO, module, message)

def warning(message, module=None):
    """Log a warning message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.warning(message)
    
    _log_to_database(WARNING, module, message)

def error(message, module=None, exc_info=None):
    """Log an error message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if exc_info:
        if app_logger:
            app_logger.error(message, exc_info=True)
        
        # Add exception details to database log
        tb = traceback.format_exc()
        full_message = f"{message}\n{tb}"
        _log_to_database(ERROR, module, full_message)
    else:
        if app_logger:
            app_logger.error(message)
        
        _log_to_database(ERROR, module, message)

def critical(message, module=None, exc_info=None):
    """Log a critical message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if exc_info:
        if app_logger:
            app_logger.critical(message, exc_info=True)
        
        # Add exception details to database log
        tb = traceback.format_exc()
        full_message = f"{message}\n{tb}"
        _log_to_database(CRITICAL, module, full_message)
    else:
        if app_logger:
            app_logger.critical(message)
        
        _log_to_database(CRITICAL, module, message)

def exception(message, module=None):
    """Log an exception message (includes traceback)"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.exception(message)
    
    # Format exception info for database
    tb = traceback.format_exc()
    full_message = f"{message}\n{tb}"
    _log_to_database(ERROR, module, full_message)

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module = func.__module__
        
        info(f"Function {func_name} called", module)
        
        try:
            result = func(*args, **kwargs)
            debug(f"Function {func_name} completed successfully", module)
            return result
        except Exception as e:
            error(f"Function {func_name} failed: {str(e)}", module, exc_info=True)
            raise
    
    return wrapper