import sys
import logging
from nyvalis.tools import log

logger = log.get(log.LIB_NAME)

if not logger.hasHandlers():
    logger.setLevel(logging.NOTSET)
    handler = logging.StreamHandler()
    handler.setFormatter(log.handlers.CustomFormatter(log.DEFAULT_FMT, log.DEFAULT_DATEFMT, colored=True, iso=True))
    logger.addHandler(handler)
    logger.propagate = False

if "-v" in sys.argv:
    logger.setLevel(logging.DEBUG)


from nyvalis.core.builder import Builder
from nyvalis.core.invoker import command
