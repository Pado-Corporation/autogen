import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.debug("test")
import better_exceptions

better_exceptions.hook()
a = 3
raise Exception(a)
