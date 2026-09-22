"""This module provides functionality for creating a 'Create' menu in kit, allowing for registration of actions and menu items related to primitive creation like shapes, lights, audio sources, cameras, and more, with support for toggling options such as 'High Quality' for primitives."""

__all__ = [
    "CreateMenuExtension",
    "rebuild_menus",
]

from .create import CreateMenuExtension, rebuild_menus
