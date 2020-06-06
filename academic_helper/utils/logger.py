import logging
from logging import Filter


class LevelFilter(Filter):
    """
    Uses to make handlers print logs between a range, and not with just a minimum.
    """

    def __init__(self, low, high):
        Filter.__init__(self)
        self._low = low
        self._high = high

    def filter(self, record):
        if self._low <= record.levelno < self._high:
            return True
        return False


def wrap(obj) -> str:
    return f"[{obj}]"


log = logging.getLogger("coursist")
