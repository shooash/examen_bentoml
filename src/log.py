import logging
from .targets import Targets

def get_logger(name : str = 'DS BentoML Exam') -> logging.Logger:
    # Log
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler())
        logger.addHandler(logging.FileHandler(Targets.logs('logs.log')))
        for h in logger.handlers:
            h.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.setLevel(logging.DEBUG)
    return logger