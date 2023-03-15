import logging


def createLogger(logHandler):
    logger = logging.getLogger(logHandler)
    return logger
