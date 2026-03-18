from .core import get_logger

def warn(msg, *args, **kwargs):
    get_logger().warning(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    get_logger().info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    get_logger().error(msg, *args, **kwargs)


