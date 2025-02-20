import logging
from nivalis.tools import log

logger = log.get(log.LIB_LOGGER)
logger.setLevel(logging.NOTSET)
handler = logging.StreamHandler()
handler.setFormatter(log.handlers.CustomFormatter(log.DEFAULT_FMT, log.DEFAULT_DATEFMT, colored=True, iso=True))
logger.addHandler(handler)
logger.propagate = False

from nivalis.core.builder import Builder
from nivalis.core.invoker import command
