"""
DroneBlock Logger Module.

Provides centralized and consistent logging functionalities across the framework.
"""

import logging
import sys

# Custom TRACE level (lower than DEBUG)
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, message, *args, **kws):
    """Emits a trace log message."""
    if self.isEnabledFor(TRACE_LEVEL):
        # pylint: disable=protected-access
        self._log(TRACE_LEVEL, message, args, **kws)


logging.Logger.trace = trace

# Configure a centralized logger for droneblock
logger = logging.getLogger("droneblock")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: str):
    """Returns a child logger for a specific module."""
    return logging.getLogger(f"droneblock.{name}")


def set_level(level):
    """Sets the global log level for droneblock."""
    logger.setLevel(level)
