import logging
from logging import handlers

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        self.err_logger = logging.getLogger(f"error-{name}")
        self.err_logger.setLevel(logging.WARNING)

        handler = handlers.RotatingFileHandler('wakontainer.log', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] %(message)s'))
        
        err_handler = handlers.RotatingFileHandler('wakontainer.err', encoding='utf-8')
        err_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] %(message)s'))

        self.logger.addHandler(handler)
        self.err_logger.addHandler(err_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.err_logger.warning(message)

    def error(self, message):
        self.err_logger.error(message)