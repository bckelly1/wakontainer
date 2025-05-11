import logging
from logging.handlers import RotatingFileHandler
import sys

class Logger:
    def __init__(self, name='wakontainer'):
        # Create a logger and set the overall logging level to DEBUG
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # handle all levels

        # Handler: all log levels to wakontainer.log (rotating file)
        file_handler = RotatingFileHandler(
            'logs/wakontainer.log', maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)  # log all messages to file

        # Handler: warnings and errors to wakontainer.err (rotating file)
        err_handler = RotatingFileHandler(
            'logs/wakontainer.err', maxBytes=5*1024*1024, backupCount=3
        )
        err_handler.setLevel(logging.WARNING)  # only WARNING and above

        # Handler: all log levels to console (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)  # log all messages to console

        # Common log message format for all handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        err_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add all handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(err_handler)
        self.logger.addHandler(console_handler)

    # Convenience methods to log with this configuration
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
