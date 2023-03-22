import logging
from env import settings

logger = logging.getLogger("EVAL")
if settings["LOG_LEVEL"] == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
