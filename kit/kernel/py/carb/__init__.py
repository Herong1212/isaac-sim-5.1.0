__copyright__ = "Copyright (c) 2018-2021, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

"""This package is the gateway to all things Carbonite. If you are starting from scratch:

    >>> import carb
    >>> f = carb.get_framework()
    >>> f.startup()

There is however no need to start up the framework if you are working within a Carbonite
based application. This has already been handled.

Attributes:
    logging (carb.pycarb.logging.ILogging): Gives access to the ILogging interface, which
        can be used to set configuration for logging.

    filesystem (carb.pycarb.filesystem.IFileSystem): Gives access to the IFileSystem interface, which is used to
        read and write files in a platform independent manner, using a uniform path format
        that supports utf8 and long paths.
"""
import sys
import traceback
from functools import cache, wraps

from ._carb import *

sys.modules["carb.logging"] = logging
sys.modules["carb.filesystem"] = filesystem


def _get_caller_info():
    f = sys._getframe(2)
    if f is None or not hasattr(f, "f_code"):
        return "(unknown file)", 0, "(unknown function)", "(unknown module)"

    return f.f_code.co_filename, f.f_lineno, f.f_code.co_name, f.f_globals.get("__name__", "")


def log_error(msg):
    file, lno, func, mod = _get_caller_info()
    log(mod, logging.LEVEL_ERROR, file, func, lno, f"{msg}")


def log_warn(msg):
    file, lno, func, mod = _get_caller_info()
    log(mod, logging.LEVEL_WARN, file, func, lno, f"{msg}")


def log_info(msg):
    file, lno, func, mod = _get_caller_info()
    log(mod, logging.LEVEL_INFO, file, func, lno, f"{msg}")


def log_verbose(msg):
    file, lno, func, mod = _get_caller_info()
    log(mod, logging.LEVEL_VERBOSE, file, func, lno, f"{msg}")


# Backwards compatibility
Framework.breakpoint = lambda self: breakpoint()
Framework.wait_for_native_debugger = lambda self, timeout, stop, quiet: wait_for_native_debugger(timeout, stop, quiet)


@cache
def _is_developer_warnings_enabled():
    from .settings import get_settings

    return bool(get_settings().get("/app/enableDeveloperWarnings"))


def log_deprecation(message: str):
    """Log deprecation message."""
    if _is_developer_warnings_enabled():
        log_warn(message)
    else:
        log_info(message)


def deprecated(message=""):
    """Decorator which can be used to mark functions or classes as deprecated. It will result in warn log when the function is used or a class is instantiated."""

    def deprecated_decorator(obj):
        if isinstance(obj, type):  # Check if it's a class
            # Create a wrapper class to preserve the class type
            class WrappedClass(obj):
                def __init__(self, *args, **kwargs):
                    log_deprecation(
                        "`{}` is deprecated. {}. Callstack: {}".format(
                            obj.__name__, message, "".join(traceback.format_stack(limit=4)[:-1])
                        )
                    )
                    super().__init__(*args, **kwargs)

            return WrappedClass
        else:  # a function

            @wraps(obj)
            def wrapped(*args, **kwargs):
                log_deprecation(
                    "`{}` is deprecated. {}. Callstack: {}".format(
                        obj.__name__, message, "".join(traceback.format_stack(limit=4))[:-1]
                    )
                )
                return obj(*args, **kwargs)

            return wrapped

    return deprecated_decorator
