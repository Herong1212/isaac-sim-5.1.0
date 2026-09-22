# Copyright (c) 2020-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""Context menu core functionality"""

__all__ = ['ContextMenuWidgetExtension', 'DefaultMenuDelegate', 'get_instance', 'close_menu', 'reorder_menu_dict']

import asyncio
import copy
import carb

import omni.ext
from omni import ui
from functools import partial
from typing import Callable, List, Tuple
from pathlib import Path
from omni.kit.menu.core import IconMenuBaseDelegate
from omni.kit.menu.core import uiMenu as _uiMenu
from omni.kit.menu.core import uiMenuItem as _uiMenuItem

_extension_instance = None

class DefaultMenuDelegate(IconMenuBaseDelegate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_settings("omni.kit.widget.context_menu")

    # override core build functions
    # get style
    def _build_item_get_style(self, item: ui.Menu) -> dict:
        style = ContextMenuWidgetExtension.default_delegate.get_style()
        if item.delegate and hasattr(item.delegate, "get_style"):
            style = style | item.delegate.get_style()
        return style

    # build label
    def _build_item_label(self, item):
        ui.Label(f"{item.text}        ", height=self.TEXT_SIZE, name="Enabled" if item.enabled else "Disabled")

    # build hotkey
    def _build_item_hotkey(self, item):
        pass


class ContextMenuWidgetExtension(omni.ext.IExt):
    """Context menu core functionality"""

    # ---------------------------------------------- core functions ----------------------------------------------

    def __init__(self):
        """
        ContextMenuWidgetExtension init function.
        """
        super().__init__()

    def on_startup(self, ext_id):
        """
        ContextMenuWidgetExtension startup function.

        Args:
            ext_id (str): Extension identifier.
        """
        global _extension_instance
        _extension_instance = self

        # backwards compatibility
        ContextMenuWidgetExtension.uiMenu = _uiMenu
        ContextMenuWidgetExtension.uiMenuItem = _uiMenuItem
        ContextMenuWidgetExtension.DefaultMenuDelegate = DefaultMenuDelegate
        ContextMenuWidgetExtension.default_delegate = DefaultMenuDelegate()

        self._context_menu = None
        self._context_menu_items = []

        manager = omni.kit.app.get_app().get_extension_manager()
        extension_path = manager.get_extension_path(ext_id)
        global TEST_DATA_PATH
        TEST_DATA_PATH = Path(extension_path).joinpath("data").joinpath("tests")

    def on_shutdown(self):
        """
        ContextMenuWidgetExtension shutdown function.
        """
        global _extension_instance
        _extension_instance = None

        if self._context_menu:
            self._context_menu.destroy()
        self._context_menu = None
        self._context_menu_items = []

        ContextMenuWidgetExtension.uiMenu = None
        ContextMenuWidgetExtension.uiMenuItem = None
        ContextMenuWidgetExtension.DefaultMenuDelegate = None
        ContextMenuWidgetExtension.default_delegate = None

    @property
    def name(self) -> str:
        """
        Name of current context menu.

        Returns:
            (str): Name of current context menu.
        """
        if self._context_menu:
            return self._context_menu.text

    def close_menu(self):
        """
        Close currently open context menu. Used by tests not to leave context menu in bad state.
        """
        if self._context_menu:
            self._context_menu.destroy()
        self._context_menu = None
        self._context_menu_items = []

    def separator(self, name: str="") -> bool:
        """
        Creates a menu separator.

        Args:
            name (str): Name of the menu separator. Optional.
        """
        if self.menu_item_count > 1:
            if isinstance(self.menu_item_prev, ui.Separator) and self.menu_item_prev.text == name:
                return False
            self.menu_item_prev = ui.Separator(name)
            return True
        return False # pragma: no cover

    def menu(self, name: str, delegate=None, glyph="", submenu=False, tearable=False, **kwargs): # pragma: no cover
        """
        Creates a menu.

        Args:
            name (str): Name of the menu.
            delegate (ui.MenuDelegate): Specify the delegate to create a custom menu. Optional.
            glyph (str): Path of the glyph image to show before the menu name. Optional.
            submenu (bool): Enables the submenu marker. Optional.
            tearable (bool): The ability to tear the window off. Optional.

        Returns:
            (uiMenu): Menu item created.
        """
        item = ContextMenuWidgetExtension.uiMenu(
            name,
            delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate,
            glyph=glyph,
            submenu=submenu,
            tearable=tearable,
            **kwargs
        )
        self._context_menu_items.append(item)
        self.menu_item_prev = item
        self.menu_item_count += 1
        return self.menu_item_prev

    def menu_item(self, name: str, triggered_fn: Callable = None, enabled: bool = True, checkable: bool = False, checked: bool = False, is_async_func=False, delegate=None, additional_kwargs=None, glyph=""):
        """
        Creates a menu item.

        Args:
            name (str): Name of the menu item.
            triggered_fn (Callable): Function to call when menu item is clicked. Optional.
            enabled (bool): Enable the menu item. Optional.
            checkable (bool): This property holds whether this menu item is checkable. A checkable item is one which has an on/off state. Optional.
            checked (bool): This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked. Optional.
            is_async_func (bool): Optional.
            delegate (ui.MenuDelegate): Specify the delegate to create a custom menu. Optional.
            additional_kwargs (dict): Additional keyword arguments to pass to ui.MenuItem. Optional.
            glyph (str): Path of the glyph image to show before the menu name. Optional.

        Returns:
            (uiMenuItem): Menu item created.
        """
        menuitem_kwargs = {"triggered_fn": triggered_fn, "enabled": enabled, "checkable": checkable, "checked": checked}
        if additional_kwargs:
            menuitem_kwargs.update(additional_kwargs)
        if delegate and hasattr(delegate, "get_parameters"):
            delegate.get_parameters(name, menuitem_kwargs)

        # async functions are created but are not visible, so exclude from prev logic
        if is_async_func:
            item = ContextMenuWidgetExtension.uiMenuItem(name, **menuitem_kwargs, delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate, glyph=glyph)
            self._context_menu_items.append(item)
            self.menu_item_prev = item
            return item

        item = ContextMenuWidgetExtension.uiMenuItem(name, **menuitem_kwargs, delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate, glyph=glyph)
        self._context_menu_items.append(item)
        self.menu_item_prev = item
        self.menu_item_count += 1
        return self.menu_item_prev

    def _get_fn_result(self, menu_entry: dict, name: str, objects: list):
        try:
            if not name in menu_entry:
                return True
            if menu_entry[name] is None:
                return True
            if isinstance(menu_entry[name], list):
                for show_fn in menu_entry[name]:
                    if not show_fn(objects):
                        return False
            else:
                if not menu_entry[name](objects):
                    return False
            return True
        except Exception as exc: # pragma: no cover
            carb.log_warn(f"_get_fn_result error for {name}: {exc}")
            return False

    def _has_click_fn(self, menu_entry):
        if "onclick_fn" in menu_entry and menu_entry["onclick_fn"] is not None:
            return True
        if "onclick_action" in menu_entry and menu_entry["onclick_action"] is not None:
            return True
        return False # pragma: no cover

    def _execute_action(self, action: Tuple, objects):
        if not action:
            return

        try:
            import omni.kit.actions.core
            import omni.kit.app

            async def execute_action(action):
                await omni.kit.app.get_app().next_update_async()
                # only forward the accepted parameters for this action
                action_obj = omni.kit.actions.core.acquire_action_registry().get_action(action[0], action[1])
                params = {key: objects[key] for key in action_obj.parameters if key in objects}
                omni.kit.actions.core.execute_action(*action, **params)

            # omni.ui can sometimes crash is menu callback does ui calls.
            # To avoid this, use async function with frame delay
            asyncio.ensure_future(execute_action(action))
        except ModuleNotFoundError: # pragma: no cover
            carb.log_warn(f"execute_action: error omni.kit.actions.core not loaded")
        except Exception as exc: # pragma: no cover
            carb.log_warn(f"execute_action: error {exc}")

    def _set_hotkey_for_action(self, menu_entry: dict, menu_item: ui.MenuItem):
        try:
            from omni.kit.hotkeys.core import get_hotkey_registry

            onclick_action = menu_entry["onclick_action"]
            hotkey_registry = get_hotkey_registry()
            if not hotkey_registry:
                raise ImportError

            for hk in hotkey_registry.get_all_hotkeys_for_extension(onclick_action[0]):
                # Hotkey text should be empty instead of None to avoid type conversion issue.
                menu_item.hotkey_text = hk.key_text if hk.action_id == onclick_action[1] else ""
        except ImportError: # pragma: no cover
            pass

    def _build_menu(self, menu_entry: dict, objects: dict, delegate) -> bool:
        if "name" in menu_entry and isinstance(menu_entry["name"], dict):
            menu_entry_name = menu_entry["name"]
            if "name_fn" in menu_entry:
                menu_entry_name = menu_entry["name_fn"](objects)

            for item in menu_entry_name:
                menu_item_count = self.menu_item_count

                glyph = None
                if "glyph" in menu_entry and menu_entry["glyph"]:
                    glyph = menu_entry["glyph"]

                tearable = False
                if delegate:
                    tearable = menu_entry.get("tearable", True)
                    if hasattr(delegate, "get_parameters"):
                        menuitem_kwargs = { "tearable": tearable }
                        delegate.get_parameters("tearable", menuitem_kwargs)
                        tearable = menuitem_kwargs["tearable"]

                menu = ContextMenuWidgetExtension.uiMenu(f"{item}", tearable=tearable, delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate, glyph=glyph, submenu=True)
                self._context_menu_items.append(menu)
                with menu:
                    for menu_entry in menu_entry_name[item]:
                        if isinstance(menu_entry, list):
                            for item in menu_entry:
                                self._build_menu(item, objects, delegate)
                        else:
                            self._build_menu(menu_entry, objects, delegate)

                # no submenu items created, remove
                if menu_item_count == self.menu_item_count:
                    menu.visible = False
                    return False
            return True

        if not self._get_fn_result(menu_entry, "show_fn", objects):
            return False

        if "populate_fn" in menu_entry:
            self.menu_item_prev = None
            menu_entry["populate_fn"](objects)
            return True

        menu_entry_name = menu_entry["name"] if "name" in menu_entry else ""
        if "name_fn" in menu_entry and menu_entry["name_fn"] is not None:
            menu_entry_name = menu_entry["name_fn"](objects)

        if menu_entry_name == "" or menu_entry_name.endswith("/"):
            header = menu_entry["header"] if "header" in menu_entry else ""
            if "show_fn_async" in menu_entry:
                menu_item = ui.Separator(header, visible=False)
                asyncio.ensure_future(menu_entry["show_fn_async"](objects, menu_item))
            return self.separator(header)

        checked = False
        checkable = False
        if "checked_fn" in menu_entry and self._has_click_fn(menu_entry):
            checkable = True
            checked = self._get_fn_result(menu_entry, "checked_fn", objects)

        menu_item = None
        is_async_func = bool("show_fn_async" in menu_entry)
        additional_kwargs = menu_entry.get("additional_kwargs", None)

        glyph = None
        if "glyph" in menu_entry and menu_entry["glyph"]:
            glyph = menu_entry["glyph"]

        if self._has_click_fn(menu_entry):
            enabled = self._get_fn_result(menu_entry, "enabled_fn", objects)
            if "onclick_action" in menu_entry and menu_entry["onclick_action"]:
                triggered_fn=partial(self._execute_action, menu_entry["onclick_action"], objects)
            else:
                triggered_fn=partial(menu_entry["onclick_fn"], objects)

            menu_item = self.menu_item(
                menu_entry_name,
                triggered_fn=triggered_fn,
                enabled=enabled,
                checkable=checkable,
                checked=checked,
                is_async_func=is_async_func,
                delegate=delegate,
                glyph=glyph,
                additional_kwargs=additional_kwargs,
            )
        else:
            menu_item = self.menu_item(menu_entry_name, enabled=False, checkable=checkable, checked=checked, is_async_func=is_async_func, delegate=delegate, glyph=glyph, additional_kwargs=additional_kwargs)

        if "onclick_action" in menu_entry:
            self._set_hotkey_for_action(menu_entry, menu_item)

        if menu_item and is_async_func:
            menu_item.visible = False
            asyncio.ensure_future(menu_entry["show_fn_async"](objects, menu_item))

        return True

    def show_context_menu(self, menu_name: str, objects: dict, menu_list: List[dict], min_menu_entries: int = 1, delegate = None) -> None:
        """
        build context menu from menu_list

        Args:
            menu_name (str): menu name
            objects (dict): context_menu data
            menu_list (list): list of dictionaries containing context menu values
            min_menu_entries (int): minimal number of menu needed for menu to be visible
        """
        try:
            if self._context_menu:
                self._context_menu.destroy()
            self._context_menu_items = []

            style = delegate.get_style() if delegate and hasattr(delegate, "get_style") else ContextMenuWidgetExtension.default_delegate.get_style()
            menuitem_kwargs = { "tearable": True if delegate else False }
            if delegate and hasattr(delegate, "get_parameters"):
                delegate.get_parameters("tearable", menuitem_kwargs)

            self._context_menu = ContextMenuWidgetExtension.uiMenu(f"Context menu {menu_name}",
                                         delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate,
                                         style=style,
                                         **menuitem_kwargs)

            self.menu_item_count = 0
            top_level_menu_count = 0
            self.menu_item_prev = None

            with self._context_menu:
                for menu_entry in menu_list:
                    if isinstance(menu_entry, list):
                        for item in menu_entry:
                            if self._build_menu(item, objects, delegate):
                                self.menu_item_count += 1
                                top_level_menu_count += 1
                    elif self._build_menu(menu_entry, objects, delegate):
                        self.menu_item_count += 1
                        top_level_menu_count += 1

            # Show it
            if top_level_menu_count >= min_menu_entries:
                # if the last menu item was a Separator, hide it
                if isinstance(self.menu_item_prev, ui.Separator):
                    self.menu_item_prev.visible = False
                if all(k in objects for k in ("menu_xpos", "menu_ypos")):
                    self._context_menu.show_at(objects["menu_xpos"], objects["menu_ypos"])
                else:
                    self._context_menu.show()
        except Exception as exc: # pragma: no cover
            carb.log_error(f"show_context_menu: error {exc}")

    def get_context_menu(self):
        """
        Gets current context_menu.

        Returns:
            (str): Current context_menu.
        """
        return self._context_menu

################## public static functions ##################


def get_instance():
    """
    Get instance of context menu class

    Returns:
        (ContextMenuWidgetExtension): Instance of class.
    """
    return _extension_instance


def close_menu():
    """
    Close currently open context menu. Used by tests not to leave context menu in bad state.
    """
    if _extension_instance:
        _extension_instance.close_menu()


def reorder_menu_dict(menu_dict: List[dict]):
    """
    Reorder menus using "appear_after" value in menu

    Args:
        menu_dict (list): list of dictionaries
    """

    def find_entry(menu_dict, name):
        for index, menu_entry in enumerate(menu_dict):
            if "name" in menu_entry:
                if menu_entry["name"] == name:
                    return index
        return -1 # pragma: no cover

    for index, menu_entry in enumerate(menu_dict.copy()):
        if "appear_after" in menu_entry:
            new_index = find_entry(menu_dict, menu_entry["appear_after"])
            if new_index != -1:
                menu_dict.remove(menu_entry)
                menu_dict.insert(new_index + 1, menu_entry)
