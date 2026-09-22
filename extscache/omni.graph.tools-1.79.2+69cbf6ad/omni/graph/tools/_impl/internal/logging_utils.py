"""Simple support for a common logging facility that can be used by any node generation function.

This is part of the _internal module. Objects with a leading underscore are not intended to be used outside
of this module. All others may only be used for internal OmniGraph purposes.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from types import TracebackType
from typing import Any

import carb

__all__ = [
    "LOG",
    "OmniGraphExtensionError",
    "set_registration_logging",
    "TemporaryLogLocation",
]


# ==============================================================================================================
class OmniGraphExtensionError(Exception):
    """Exception raised when there was an error in the extension's node type analysis process"""


# ==============================================================================================================
# Create a logger and selectively turn on logging if the OGN debugging environment variable is set.
# If either environment variable is a string that looks like a path then divert the output there.
# If neither are set then a NullHandler is used to prevent any logging. It's anticipated that this will not
# present any significant performance problem as there are no tight loops in this code.
#
# Usage:    LOG.info("This is a %s message", "formatted")
#
# If you are in particularly time-sensitive code and don't want even the overhead of a call to the disabled log
# then you can use the disabled state of the log and do this:
#
#   _ = LOG.disabled or LOG.info("This will not even get called to be ignored")
# or
#   if not LOG.disabled:
#       LOG.info("Multi-line logs")
#       LOG.info("are easier to read")
#       LOG.info("inside an if-block")
#
LOG = logging.getLogger("ogn_registration")
LOG.setLevel(logging.INFO)
LOG.disabled = True
_LAST_LOGGING_LOCATION = None


# ==============================================================================================================
def set_registration_logging(location: str | Path | None):
    """Redefine the registration logging location.
    Args:
        location: Where the logging output should go. None means disable logging, a string indicates a file
                  location, an empty or numerical string means stdout, and stdout/stderr/cout/cerr redirects
                  to the streams of the same name
    """
    global _LAST_LOGGING_LOCATION
    if not location:
        new_handler = logging.NullHandler()
        LOG.disabled = True
    elif isinstance(location, Path):
        new_handler = logging.FileHandler(str(location), encoding="utf-8")
        LOG.disabled = False
    elif not location.isnumeric():
        if location in ["stdout", "cout"]:
            new_handler = logging.StreamHandler(sys.stdout)
        elif location in ["stderr", "cerr"]:
            new_handler = logging.StreamHandler(sys.stderr)
        else:  # pragma: no cover
            try:
                new_handler = logging.FileHandler(location, encoding="utf-8")
            except PermissionError:
                carb.log_warn(f"Could not set logging to '{location}' - no write permission on file")
                new_handler = logging.StreamHandler(sys.stdout)
        LOG.disabled = False
    else:
        new_handler = logging.StreamHandler(sys.stdout)
        LOG.disabled = False

    new_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    LOG.addHandler(new_handler)
    for handler in LOG.handlers:
        if handler != new_handler:
            LOG.removeHandler(handler)
    _LAST_LOGGING_LOCATION = location


# ==============================================================================================================
class TemporaryLogLocation:  # pragma: no cover (debugging utility).
    """Context manager to temporarily redirect where the log directory goes.
    with TemporaryLogLocation(new_log_location):
        do_loggable_function()
    """

    def __init__(self, new_location: Path | str | None):
        self.__previous_location = _LAST_LOGGING_LOCATION
        self.__new_location = new_location

    def __enter__(self):
        set_registration_logging(self.__new_location)
        return self.__new_location

    def __exit__(self, exit_type: Any, value: Any, traceback: TracebackType):
        set_registration_logging(self.__previous_location)
        self.__new_location = None
        self.__previous_location = None
