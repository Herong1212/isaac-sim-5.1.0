"""This module provides functionalities to manage a global singleton instance of PrimDataAccessorRegistry, including getting, setting, and resetting the registry."""

from .prim_data_accessor_registry import PrimDataAccessorRegistry

__prim_data_accessor_registry = None


def get_prim_data_accessor_registry() -> PrimDataAccessorRegistry:
    """Returns the singleton instance of the PrimDataAccessorRegistry.

    Returns:
        :obj:`PrimDataAccessorRegistry`: The singleton instance of the PrimDataAccessorRegistry."""
    global __prim_data_accessor_registry
    if not __prim_data_accessor_registry:
        __prim_data_accessor_registry = PrimDataAccessorRegistry()
    return __prim_data_accessor_registry


def set_prim_data_accessor_registry(obj: PrimDataAccessorRegistry):
    """Sets the global PrimDataAccessorRegistry instance.

    Args:
        obj (:obj:`PrimDataAccessorRegistry`): The PrimDataAccessorRegistry instance to set as the global registry."""
    global __prim_data_accessor_registry
    __prim_data_accessor_registry = obj


def clean_prim_data_accessor_registry():
    """Resets the global `PrimDataAccessorRegistry` instance to `None`.

    This function is intended to clear the current prim data accessor registry in
    the system, effectively resetting its state for purposes such as
    reinitialization or cleanup at the end of a session."""
    global __prim_data_accessor_registry
    __prim_data_accessor_registry = None
