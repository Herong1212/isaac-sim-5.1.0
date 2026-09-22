"""
Collection of tools to help with debugging the operation of scripts.
Mainly lives here so that all OGN-related files can access it, though the tools are pretty general.
"""

import os
import weakref
from contextlib import suppress
from functools import partial, wraps
from typing import Dict, List

from omni.ext import get_dangling_references

__all__ = []

# ======================================================================
# Environment variable gating display and execution of debugging information
# - The value "1" sets OGN_DEBUG for general debugging
# - Any string containing "eval" sets OGN_EVAL_DEBUG
# - Either "1" or a string containing "gc" sets OGN_GC_DEBUG
# - Either "1" or a string containing "ui" sets OGN_UI_DEBUG
# e.g. you could enable UI and GC by setting it to "gc, ui"
_ogn_debug_env_var = os.getenv("OGN_DEBUG")
has_debugging = _ogn_debug_env_var is not None
OGN_DEBUG = _ogn_debug_env_var == "1"
OGN_EVAL_DEBUG = has_debugging and (_ogn_debug_env_var.lower().find("eval") >= 0)
OGN_GC_DEBUG = has_debugging and (_ogn_debug_env_var == "1" or _ogn_debug_env_var.lower().find("gc") >= 0)
OGN_UI_DEBUG = has_debugging and (_ogn_debug_env_var == "1" or _ogn_debug_env_var.lower().find("ui") >= 0)


# ======================================================================
def __dbg(gate_variable: bool, message: str, *args, **kwargs):  # pragma: no cover  Debugging only
    """
    Print out a debugging message if the gate_variable is enabled, additional args will be passed
    to format the given message.
    """
    if gate_variable:
        if args or kwargs:
            print("DBG: " + message.format(*args, **kwargs), flush=True)
        else:
            print(f"DBG: {message}", flush=True)


# Define a few helper functions that provide debugging for some standard environment variables.
# Even more efficient use pattern is "OGN_DEBUG and dbg(X)" to prevent side effects.
dbg = partial(__dbg, OGN_DEBUG)
dbg_eval = partial(__dbg, OGN_EVAL_DEBUG)
dbg_gc = partial(__dbg, OGN_GC_DEBUG)
dbg_ui = partial(__dbg, OGN_UI_DEBUG)


# ======================================================================
# String used for indenting debugging information, so that nested function calls are visually distinct
INDENT = ""


# ======================================================================
def function_trace(env_var=None):  # pragma: no cover  Debugging only
    """
    Debugging decorator that adds function call tracing, potentially gated by an environment variable.

    Use as a normal function decorator:

    .. code-block:: python

        @function_trace()
        def my_function(value: str) -> str:
            return value + value

    Calling my_function("X") with debugging enabled will print this:

        Calling my_function('X')
          'my_function' returned 'XX'

    The extra parameter lets you selectively disable it based on environment variables:

    .. code-block:: python

        @function_trace("OGN_DEBUG")
        def my_function(value: str) -> str:
            return value + value

    This version only enables debugging if the environment variable "OGN_DEBUG" is set
    """

    def inner_decorator(func):
        """Having an inner decorator allows parameters to be passed to the outer one"""

        @wraps(func)
        def wrapper_debug(*args, **kwargs):
            """Wrapper function to add debugging information before and after forwarding calls"""
            if env_var is None or os.getenv(env_var) is not None:
                global INDENT
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                print(f"{INDENT}Calling {func.__name__}({signature})")
                INDENT += "  "
                value = func(*args, **kwargs)
                print(f"{INDENT}{func.__name__!r} returned {value!r}")
                INDENT = INDENT[:-2]
                return value

            return func(*args, **kwargs)

        return wrapper_debug

    return inner_decorator


# ======================================================================
def __validate_property_destruction(weak_property, name: str):
    """Check that the weak reference to a property value references a destroyed value"""
    # Check to see if the property value is still being referenced
    if OGN_GC_DEBUG:
        with suppress(AttributeError, TypeError):
            if weak_property() is not None:
                print(f"Property {name} destroy failed: {get_dangling_references(weak_property())}", flush=True)


# ----------------------------------------------------------------------
def __destroy_property_member(obj_property, name: str):
    """Try to call destroy for the obj_property - returns a weak reference to it for later use"""
    dbg(f"Destroying member {name} on {obj_property}")
    try:
        # Use a weak reference to perform a simple test for "real" destruction
        weak_property = weakref.ref(obj_property)
        obj_property.destroy()
    except AttributeError:
        dbg_gc(f"...obj_property {name} has no destroy method")
        weak_property = None
    except TypeError:
        dbg_gc(f"...obj_property {name} cannot be weak referenced")
        weak_property = None

    return weak_property


# ----------------------------------------------------------------------
def __destroy_property_list(property_list: List, base_name: str):
    """Walk a list of properties, recursively destroying them"""
    dbg_gc(f"Destroying list {property_list} as {base_name}")
    index = 0
    # The non-standard loop is to make sure this execution frame does not retain references to the objects
    while property_list:
        property_member = property_list.pop(0)
        debug_name = f"{base_name}[{index}]"
        index += 1
        dbg_gc(f"...destroying member {debug_name}")
        if isinstance(property_member, list):
            dbg_gc("...(as list)")
            __destroy_property_list(property_member, debug_name)
        elif isinstance(property_member, dict):
            dbg_gc("...(as dictionary)")
            __destroy_property_dict(property_member, debug_name)
        else:
            dbg_gc("...(as object)")
            weak_property = __destroy_property_member(property_member, debug_name)
            property_member = None
            __validate_property_destruction(weak_property, debug_name)


# ----------------------------------------------------------------------
def __destroy_property_dict(property_dict: Dict, base_name: str):
    """Walk a dictionary of properties, recursively destroying them"""
    dbg_gc(f"Destroying dictionary {property_dict} as {base_name}")
    # The non-standard loop is to make sure this execution frame does not retain references to the objects
    while property_dict:
        property_key, property_member = property_dict.popitem()
        debug_name = f"{base_name}[{property_key}]"
        dbg_gc(f"...destroying member {debug_name}")
        if isinstance(property_member, list):
            dbg_gc("...(as list)")
            __destroy_property_list(property_member, debug_name)
        elif isinstance(property_member, dict):
            dbg_gc("...(as dictionary)")
            __destroy_property_dict(property_member, debug_name)
        else:
            dbg_gc("...(as object)")
            weak_property = __destroy_property_member(property_member, debug_name)
            property_member = None
            __validate_property_destruction(weak_property, debug_name)


# ----------------------------------------------------------------------
def destroy_property(self, property_name: str):
    """Call the destroy method on a property and set it to None - helps with garbage collection

    In a class's destroy() or __del__ method you can call this to generically handle member destruction
    when such things do not happen automatically (e.g. when you cross into the C++-bindings, or the
    objects have circular references)

        def destroy(self):
            destroy_property(self, "_widget")

    If the property is a list then the list members are individually destroyed.
    If the property is a dictionary then the values of the dictionary are individually destroyed.

    NOTE: Only call this if you are the owner of the property, otherwise just set it to None.

    Args:
        self: The object owning the property to be destroyed (can be anything with a destroy() method)
        property_name: Name of the property to be destroyed
    """
    debug_name = f"{type(self).__name__}.{property_name}"
    # If the property name uses the double-underscore convention for "internal" data then the name must
    # be embellished with the class name to allow access, since this function is not part of the class.
    property_to_access = property_name if property_name[0:2] != "__" else f"_{type(self).__name__}{property_name}"
    obj_property = getattr(self, property_to_access, None)
    if obj_property is None:
        dbg_gc(f"Destroyed None member {debug_name} {self} {property_to_access}")
        return
    dbg_gc(f"Destroy property {debug_name}")
    if isinstance(obj_property, list):
        dbg_gc("(as list)")
        __destroy_property_list(obj_property, debug_name)
        setattr(self, property_to_access, [])
    elif isinstance(obj_property, dict):
        dbg_gc("(as dictionary)")
        __destroy_property_dict(obj_property, debug_name)
        setattr(self, property_to_access, {})
    else:
        dbg_gc("(as object)")
        weak_property = __destroy_property_member(obj_property, debug_name)
        setattr(self, property_to_access, None)
        obj_property = None
        __validate_property_destruction(weak_property, debug_name)
