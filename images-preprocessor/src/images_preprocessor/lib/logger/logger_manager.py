import logging
import time
import os
from logging import Logger

class LoggerManager:

    __levels = {
        'CRITICAL': logging.CRITICAL,
        'FATAL': logging.FATAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }

    def __init__(self, logger_name: str = "LOGGER", log_folder: str = "", log_level: str = "INFO"):

        """
        Logger Manager class creating logger to stream messages based on logging level.
        :param: logger_name: String name of the logger
        :param: log_folder: String path of the log file
        :param: log_level: String level of the logging
        """

        self.__logger_name = logger_name
        self.__log_folder = log_folder
        self.__log_level = self.__levels[log_level]
        self.__logger = None
        self.__file_writer_service: bool = False

    @property
    def logger_name(self):
        return self.__logger_name

    @logger_name.setter
    def logger_name(self, logger_name):
        self.__logger_name = logger_name

    @property
    def log_folder(self):
        return self.__log_folder

    @log_folder.setter
    def log_folder(self, log_folder):
        self.__log_folder = log_folder

    @property
    def log_level(self):
        return self.__log_level

    @log_level.setter
    def log_level(self, log_level):
        self.__log_level = self.__levels[log_level]

    @property
    def logger(self):
        return self.__create_logger()

    @property
    def file_writer_service(self):
        if not self.log_folder:
            self.__file_writer_service = False
        else:
            self.__file_writer_service = True
        return self.__file_writer_service

    def __create_logger(self):
        logger: Logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - {} - %(message)s'.format(self.logger_name),
                                      '%Y-%m-%d %H:%M:%S')

        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        if self.file_writer_service:
            self.__set_file_writer(logger)

        return logger

    def __set_file_writer(self, logger):
        timestamp = time.strftime('%Y%m%d')
        log_file_path = os.path.join(self.log_folder, "{}_{}.log".format(timestamp, self.logger_name))
        file_handler = logging.FileHandler(log_file_path)
        logger.addHandler(file_handler)
