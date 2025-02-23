from functools import wraps
from utils.logger import logger

def safe_operation(func):
    """Decorator to safely execute operations with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper
