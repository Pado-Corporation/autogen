from .jobs import *
from .functions import *
from config import Config
import logging

config = Config()

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

logger = logging.getLogger()
logger.setLevel(log_levels.get(config.log_level, logging.NOTSET))
