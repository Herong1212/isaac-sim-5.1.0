__copyright__ = "Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

"""This module contains bindings to C++ carb::profiler::IProfiler interface."""

# This module depends on other modules. VSCode python language server scrapes
# modules in an isolated environment (ignoring PYTHONPATH set). `import` fails and for that we have separate code
# path to explicitly add it's folder to sys.path and import again.
try:
    import carb
except:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..")))
    import carb

import asyncio
import functools

from ._profiler import *


def begin(mask, name, stack_offset=0):
    if not is_profiler_active():
        return

    if supports_dynamic_source_locations():
        import sys

        frame = sys._getframe(stack_offset).f_back
        if frame and frame.f_code:
            f_code = frame.f_code

            filepath = f_code.co_filename
            function = f_code.co_name
            lineno = frame.f_lineno

            begin_with_location(mask, name, function, filepath, lineno)
        else:
            begin_with_location(mask, name)

    else:
        begin_with_location(mask, name)


def profile(func=None, mask=1, zone_name=None, add_args=False):
    """Decorator to profile function call

    Example:

    .. code-block:: python

        import carb.profiler

        @carb.profiler.profile
        def foo():
            pass

        # Or:
        @carb.profiler.profile(mask=10, zone_name="Foonction", add_args=True)
        def foo():
            pass
    """

    def decorator(f):
        if asyncio.iscoroutinefunction(f):

            @functools.wraps(f)
            async def async_wrapper(*args, **kwargs):
                active_zone_name = zone_name if zone_name is not None else f.__name__
                if add_args:
                    active_zone_name += str(args) + str(kwargs)

                carb.profiler.begin(mask, active_zone_name, stack_offset=1)
                try:
                    r = await f(*args, **kwargs)
                finally:
                    carb.profiler.end(mask)
                return r

            return async_wrapper
        else:

            @functools.wraps(f)
            def wrapper(*args, **kwds):
                active_zone_name = zone_name if zone_name is not None else f.__name__
                if add_args:
                    active_zone_name += str(args) + str(kwds)

                carb.profiler.begin(mask, active_zone_name, stack_offset=1)
                try:
                    r = f(*args, **kwds)
                finally:
                    carb.profiler.end(mask)
                return r

            return wrapper

    if carb.profiler.is_profiler_active():
        return decorator(func) if func else decorator
    return func if func else lambda f: f
