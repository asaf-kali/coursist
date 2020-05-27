###############################################################################
# Supplies basic logging functionality.
###############################################################################


import logging
import sys
from logging import Filter

INITIATED = False


class LevelFilter(Filter):
    """
    Uses to make handlers print logs between a range, and not with minimum.
    """

    def __init__(self, low, high):
        Filter.__init__(self)
        self._low = low
        self._high = high

    def filter(self, record):
        if self._low <= record.levelno < self._high:
            return True
        return False


def init():
    """
    Inits the logger. Happens only once.
    :return: the initiated logger.
    """
    logger = logging.getLogger()

    global INITIATED
    if INITIATED:
        return logger
    INITIATED = True

    logger.setLevel(logging.INFO)

    file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s")
    std_formatter = logging.Formatter("%(message)s")

    out_handler = logging.StreamHandler(sys.stdout)
    out_handler.setFormatter(std_formatter)
    out_handler.addFilter(LevelFilter(logging.NOTSET, logging.WARNING))

    err_handler = logging.StreamHandler(sys.stderr)
    err_handler.setLevel(logging.WARNING)
    err_handler.setFormatter(std_formatter)

    file_handler = logging.FileHandler("server.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(out_handler)
    logger.addHandler(err_handler)
    logger.addHandler(file_handler)

    return logger


def wrap(obj) -> str:
    return f"[{obj}]"


log = init()
