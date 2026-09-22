# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides an interface for registering and managing custom menus, selection handlers, search delegates, and file open handlers within the Content Browser of NVIDIA's Omniverse Kit."""

__all__ = [
    "get_instance",
    "custom_menus",
    "selection_handlers",
    "search_delegate",
    "register_context_menu",
    "deregister_context_menu",
    "register_listview_menu",
    "deregister_listview_menu",
    "register_import_menu",
    "deregister_import_menu",
    "register_file_open_handler",
    "deregister_file_open_handler",
    "register_selection_handler",
    "deregister_selection_handler",
    "register_search_delegate",
    "deregister_search_delegate",
    "register_checkpoint_menu",
    "deregister_checkpoint_menu",
]

from typing import Callable, Union, Set
from collections import OrderedDict
from .extension import ContentBrowserRegistryExtension, get_instance


def custom_menus() -> OrderedDict:
    """Retrieves an ordered dictionary of custom menus registered within the application.\n\nReturns:\n    OrderedDict: An ordered dictionary where keys are menu identifiers and values\n    are specific menu configurations. If no menus are registered, an empty OrderedDict is returned."""
    registry = get_instance()
    if registry:
        return registry._custom_menus
    return OrderedDict()


def selection_handlers() -> Set:
    """Retrieves the set of registered selection handlers from the Content Browser Registry.

    Returns:
        Set: A set of registered selection handlers, or an empty set if the registry is not available."""
    registry = get_instance()
    if registry:
        return registry._selection_handlers
    return set()


def search_delegate() -> "SearchDelegate":
    """Retrieves the current search delegate instance from the content browser registry.

    Returns:
        SearchDelegate: The search delegate object if the registry is initialized, otherwise None."""
    registry = get_instance()
    if registry:
        return registry._search_delegate
    return None


def register_context_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1):
    """Adds a new context menu option.

    Args:
        name (str): Identifier for the menu option.
        glyph (str): Icon representation for the menu option.
        click_fn (Callable): Function to execute on menu option click.
        show_fn (Callable): Function to determine if the menu option should be shown.
        index (int, optional): Position in the menu to insert the option. Defaults to -1."""
    registry = get_instance()
    if registry:
        registry.register_custom_menu("context", name, glyph, click_fn, show_fn, index=index)


def deregister_context_menu(name: str):
    """Removes a previously registered context menu.

    Args:
        name (str): The name of the menu to deregister."""
    registry = get_instance()
    if registry:
        registry.deregister_custom_menu("context", name)


def register_listview_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1):
    """Registers a menu item to the listview context menu.

    Args:
        name (str): The unique name for the menu item.
        glyph (str): The icon glyph associated with the menu item.
        click_fn (Callable): The function to call when the item is clicked.
        show_fn (Callable): The function to determine menu item visibility.
        index (int, optional): Position to insert the item into the menu. Defaults to -1."""
    registry = get_instance()
    if registry:
        registry.register_custom_menu("listview", name, glyph, click_fn, show_fn, index=index)


def deregister_listview_menu(name: str):
    """Removes a previously registered listview menu.

    Args:
        name (str): The name of the menu to deregister."""
    registry = get_instance()
    if registry:
        registry.deregister_custom_menu("listview", name)


def register_import_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable):
    """Registers a custom menu item for the import context.

    Args:
        name (str): The unique name for the menu item.
        glyph (str): The icon glyph for the menu item.
        click_fn (Callable): The function to call when the menu item is clicked.
        show_fn (Callable): The function to determine if the menu should be shown.
    """
    registry = get_instance()
    if registry:
        registry.register_custom_menu("import", name, glyph, click_fn, show_fn)


def deregister_import_menu(name: str):
    """Removes a custom menu item from the import menu.

    Args:
        name (str): The name of the menu item to remove."""
    registry = get_instance()
    if registry:
        registry.deregister_custom_menu("import", name)


def register_file_open_handler(name: str, open_fn: Callable, file_type: Union[int, Callable]):
    """Registers a handler for opening files.

    Args:
        name (str): Identifier for the open handler.
        open_fn (Callable): Function to call when opening a file.
        file_type (Union[int, Callable]): Type of file or function determining the file type.
    """
    registry = get_instance()
    if registry:
        registry.register_custom_menu("file_open", name, None, open_fn, file_type)


def deregister_file_open_handler(name: str):
    """Removes a previously registered file open handler.

    Args:
        name (str): The name of the handler to deregister."""
    registry = get_instance()
    if registry:
        registry.deregister_custom_menu("file_open", name)


def register_selection_handler(handler: Callable):
    """Registers a selection handler to the registry.

    Args:
        handler (Callable): Function to handle selection events."""
    registry = get_instance()
    if registry:
        registry.register_selection_handler(handler)


def deregister_selection_handler(handler: Callable):
    """Removes a selection handler from the registry.

    Args:
        handler (Callable): The function to be removed from the selection handlers."""
    registry = get_instance()
    if registry:
        registry.deregister_selection_handler(handler)


def register_search_delegate(search_delegate: "SearchDelegate"):
    """Registers a search delegate.

    Args:
        search_delegate (SearchDelegate): The delegate to handle search queries."""
    registry = get_instance()
    if registry:
        registry.register_search_delegate(search_delegate)


def deregister_search_delegate(search_delegate: "SearchDelegate"):
    """Removes a previously registered search delegate.

    Args:
        search_delegate (SearchDelegate): The delegate to remove from the registry."""
    registry = get_instance()
    if registry:
        registry.deregister_search_delegate(search_delegate)


def register_checkpoint_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable, index=-1):
    """Registers a custom menu item under the 'checkpoint' category.

    Args:
        name (str): The unique name for the checkpoint menu item.
        glyph (str): Glyph icon associated with the menu item.
        click_fn (Callable): Function to call when the menu item is clicked.
        show_fn (Callable): Function to determine visibility of the menu item.
        index (int, optional): Position in the menu to insert the item at. Defaults to -1."""
    registry = get_instance()
    if registry:
        registry.register_custom_menu("checkpoint", name, glyph, click_fn, show_fn, index)


def deregister_checkpoint_menu(name: str):
    """Deregisters a previously registered checkpoint menu.

    Args:
        name (str): The name of the checkpoint menu to deregister."""
    registry = get_instance()
    if registry:
        registry.deregister_custom_menu("checkpoint", name)
