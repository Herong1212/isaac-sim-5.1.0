__copyright__ = "Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import sys

import carb
import omni.core
import omni.str

from ._log import *


def _get_caller_info(depth):
    try:
        f = sys._getframe(depth + 1)
        if f and hasattr(f, "f_code"):
            return f.f_code.co_filename, f.f_lineno, f.f_code.co_name, f.f_globals.get("__name__", "<module>")
    except ValueError:
        pass
    return "(unknown file)", 0, "(unknown function)", "(unknown module)"


def log(level: Level, msg: str, channel=None, origin_stack_depth=1):
    """Logs a message at the given level.

    origin_stack_depth -- Describes how many stack frames to move up to grab information about the origin of the log
    message (filename, line number, etc).  A valid of 1 (the default) means use the stack information from the function
    that called this function.  A value greater than 1 can be used when wrapping this function.
    """

    # OVCC-1294: This is about three orders of magnitude faster than using the inspect library.
    file, line, func, mod = _get_caller_info(origin_stack_depth)

    _log._write(channel, level, msg, mod, file, line, func)


def verbose(msg: str, channel=None, origin_stack_depth=1):
    """Logs a verbose message."""
    log(Level.VERBOSE, msg, channel, origin_stack_depth + 1)


def info(msg: str, channel=None, origin_stack_depth=1):
    """Logs an informational message."""
    log(Level.INFO, msg, channel, origin_stack_depth + 1)


def warn(msg: str, channel=None, origin_stack_depth=1):
    """Logs a warning."""
    log(Level.WARN, msg, channel, origin_stack_depth + 1)


def error(msg: str, channel=None, origin_stack_depth=1):
    """Logs an error."""
    log(Level.ERROR, msg, channel, origin_stack_depth + 1)


def fatal(msg: str, channel=None, origin_stack_depth=1):
    """Logs a fatal error.  This function only logs.  This function does _not_ terminate the process."""
    log(Level.FATAL, msg, channel, origin_stack_depth + 1)
