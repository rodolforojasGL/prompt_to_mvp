import logging
import sys
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger("brains-backend")
logger.setLevel(LOG_LEVEL)

# Prevent multiple handlers in reload (e.g., when using --reload in dev)
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False