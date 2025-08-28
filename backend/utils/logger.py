import logging

class AppLogger:
    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message, exc_info=True)
    
    def critical(self, message: str):
        self.logger.critical(message, exc_info=True)

def get_logger(name: str) -> AppLogger:
    return AppLogger(name)