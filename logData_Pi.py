import logging


class logData(object):
    def __init__(self, lgger_name):
        # TODO make the format better
        # TODO give the ability to split logs, so no huge files are created
        fileHandler = logging.FileHandler('RPi_Status.log')  # Create the necessary file
        strmHandler = logging.StreamHandler()  # Limited use, removed in the end product
        # Set the formatting for the logs
        # Include level:time_of_log:name_of_logger:log_message
        fileHandler.setFormatter(logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s'))
        self.logger = logging.getLogger(lgger_name)  # Initialize the logger
        self.logger.setLevel(logging.INFO)  # Set the logging level for the current logger
        self.logger.addHandler(fileHandler)  # Add the file handler to the logger
        self.logger.addHandler(strmHandler)  # Used when debugging

    def log(self, level, msg):
        if level == "DEBUG":
            self.logger.debug(msg)
        elif level == "INFO":
            self.logger.info(msg)
        elif level == "WARNING":
            self.logger.warning(msg)
        elif level == "ERROR":
            self.logger.error(msg)
        elif level == "CRITICAL":
            self.logger.critical(msg)
        elif level == "EXCEPT":
            self.logger.error(msg, exc_info=True)
