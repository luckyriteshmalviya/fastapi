import logging 
import time
import functools
from pythonjsonlogger import jsonlogger
import sys

# date format - YY:MM:DD 

error_format = '%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s'
timing_format = '%(asctime)s:%(name)s:%(message)s'
error_file = 'logs.log'
timing_file = 'timing.log'

class Logger:
    def __init__(self, name, file, format):
        self.logger = logging.getLogger(name) 
        fileHandler = logging.FileHandler(file)
        fileHandler.setLevel(logging.DEBUG) 
        self.logger.setLevel(logging.DEBUG)
        fileFormat = logging.Formatter(format)
        fileHandler.setFormatter(fileFormat) 
        self.logger.addHandler(fileHandler)
        
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleFormatter = jsonlogger.JsonFormatter(format)
        consoleHandler.setFormatter(consoleFormatter)
        consoleHandler.setLevel(logging.DEBUG)
        self.logger.addHandler(consoleHandler)

    def return_log_msg(self, status_code, message):
        return str(status_code) + ':' + message
    
    
class Timer:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tic = time.perf_counter()
            value = func(*args, **kwargs)
            toc = time.perf_counter()
            elapsed_time = toc - tic
            self.logger.logger.info({'functionName':func.__name__, 'elapsedTime':f"{elapsed_time:0.4f} seconds"})
            return value
        return wrapper
    