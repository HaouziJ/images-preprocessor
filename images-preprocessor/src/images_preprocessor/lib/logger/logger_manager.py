import logging


class LoggerManager:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger_name: str, log_level=logging.INFO):
        self.logger_name = logger_name
        self.log_level = log_level

    def create_logger(self):
        pass

    logging.basicConfig(format='%(asctime)s - %(levelname)s - ImagePreprocessor - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
