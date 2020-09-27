import logging
from logging import Filter

from django.conf import settings


class LevelFilter(Filter):
    """
    Uses to make handlers print logs between a range, and not with just a minimum.
    """

    def __init__(self, low, high=None):
        Filter.__init__(self)
        self._low = low
        self._high = high if high else 100

    def filter(self, record):
        if self._low <= record.levelno < self._high:
            return True
        return False


def wrap(obj) -> str:
    return f"[{obj}]"


def reconfigure_logging():
    log_configurator = logging.config.DictConfigurator(settings.LOGGING)
    log_configurator.configure()
    logging.captureWarnings(True)


log = logging.getLogger("coursist")
