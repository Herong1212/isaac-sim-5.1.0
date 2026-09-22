"""
Advanced helper class for adding/removing "Window" menu to your extension & controlling ui.Window creation/show/hide. Only thing required is function to create ui_window
"""

# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# pylint: disable=redefined-outer-name
import asyncio
from typing import Dict, Optional

import carb
import omni.ext
import omni.kit.menu.utils
import omni.ui as ui

from .builder_utils import MenuItemDescription

registered_windows: Dict[str, str] = {}


class MenuHelperExtensionFull:
    """
    Advanced helper class for adding/removing "Window" menu to your extension & controlling ui.Window creation/show/hide. Only thing required is function to create ui_window
    """

    class ArrayRedirect:
        def __init__(self, array_ptr, index):
            self.__array_ptr = array_ptr
            self.__index = index
            super().__init__()

        def __getattr__(self, name):
            return self.__array_ptr[self.__index].__getattribute__(name)

        def __repr__(self):
            return str(self.__array_ptr[self.__index])

        def __eq__(self, other):
            return self.__array_ptr[self.__index].__eq__(other)

        def __ne__(self, other):
            return self.__array_ptr[self.__index].__ne__(other)

        def __gt__(self, other):
            return self.__array_ptr[self.__index].__gt__(other)

        def __ge__(self, other):
            return self.__array_ptr[self.__index].__ge__(other)

        def __lt__(self, other):
            return self.__array_ptr[self.__index].__lt__(other)

        def __le__(self, other):
            return self.__array_ptr[self.__index].__le__(other)

        def __hash__(self):
            return self.__array_ptr[self.__index].__hash__()

    def __get_window(self, window, index) -> ui.Window:
        if self._window_attr_name[index]:
            return getattr(window, self._window_attr_name[index])
        return window

    def __init__(self):
        super().__init__()
        self._verbose = False
        self._window = None
        self._window_list = None
        self._create_window_fn = None
        self._window_name = None
        self._window_attr_name = None
        self._menu_desc = None
        self._menu_group = None
        self._menu_entry = None

    def __register_window(self, window_name, owner_fn):
        if window_name in registered_windows:
            carb.log_error(
                f'menu_startup: window "{window_name}" already registered by {registered_windows[window_name]}'
            )
            return False

        if hasattr(owner_fn, "__module__"):
            registered_windows[window_name] = owner_fn.__module__
        else:
            registered_windows[window_name] = "unknown"

        return True

    def __unregister_window(self, window_name):
        if window_name in registered_windows:
            del registered_windows[window_name]

    def menu_startup(
        self, create_window_fn, window_name, menu_desc, menu_group, window_attr_name=None, verbose=False
    ) -> Optional[int]:
        if verbose:
            print("[MenuHelperExtensionFull] menu_startup")

        if not self.__register_window(window_name, create_window_fn):
            return None

        if not getattr(self, "_window", None) or self._window is None:
            self._verbose = []
            self._window_list = []
            # for backwards compatibility self._window returns self._window_list[0]
            self._window = MenuHelperExtensionFull.ArrayRedirect(self._window_list, 0)
            self._create_window_fn = []
            self._window_name = []
            self._window_attr_name = []
            self._menu_desc = []
            self._menu_group = []
            self._menu_entry = []

        index = len(self._window_list)
        self._verbose.append(verbose)
        self._window_list.append(None)
        self._create_window_fn.append(create_window_fn)
        self._window_name.append(window_name)
        self._window_attr_name.append(window_attr_name)
        self._menu_desc.append(menu_desc)
        self._menu_group.append(menu_group)
        self._menu_entry.append(None)

        self._setup_menu(index)
        ui.Workspace.set_show_window_fn(self._window_name[index], lambda v, i=index: self.show_window(None, v, i))

        return index

    def menu_shutdown(self, index=-1) -> bool:
        if index == -1:
            if not getattr(self, "_window", None) or self._window is None:
                return False

            if any(v for v in self._verbose):
                print(f"[MenuHelperExtensionFull] on_shutdown index:{index}")

            for idx, _ in enumerate(self._window_list):
                self._destroy_menu(idx)
                ui.Workspace.set_show_window_fn(self._window_name[idx], None)
                self.__unregister_window(self._window_name[idx])
                if self._window_list[idx]:
                    self._window_list[idx].destroy()
                    self._window_list[idx] = None

            self._verbose = []
            self._window_list = []
            del self._window
            self._create_window_fn = []
            self._window_name = []
            self._window_attr_name = []
            self._menu_desc = []
            self._menu_group = []
            self._menu_entry = []
        else:
            if self._verbose[index]:
                print(f"[MenuHelperExtensionFull] on_shutdown index:{index}")

            self._destroy_menu(index)
            ui.Workspace.set_show_window_fn(self._window_name[index], None)
            self.__unregister_window(self._window_name[index])
            if self._window_list[index]:
                self._window_list[index].destroy()
            self._window_list[index] = None
            self._verbose[index] = False
            self._create_window_fn[index] = None
            self._window_name[index] = ""
            self._window_attr_name[index] = None
            self._menu_desc[index] = None
            self._menu_group[index] = None
            self._menu_entry[index] = None

        return True

    def _get_action_name(self, menu_path):
        import re

        action = (
            re.sub(r"[^\x00-\x7F]", "", menu_path)
            .lower()
            .strip()
            .replace("/", "_")
            .replace(" ", "_")
            .replace("__", "_")
        )
        return (self.__class__.__module__, f"menu_toggle_window_helper_{action}")

    def _setup_menu(self, index):
        import omni.kit.actions.core

        extension_id, action_name = self._get_action_name(self._menu_desc[index])
        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            action_name,
            lambda i=index: self._toggle_window(i),
            display_name=action_name,
            description=action_name,
            tag=action_name,
        )

        self._menu_entry[index] = omni.kit.menu.utils.build_submenu_dict(
            [
                MenuItemDescription(
                    name=f"{self._menu_group[index]}/{self._menu_desc[index]}",
                    ticked=True,  # menu item is ticked
                    ticked_fn=lambda i=index: self._is_visible(
                        i
                    ),  # gets called when the menu needs to get the state of the ticked menu
                    onclick_action=(extension_id, action_name),
                )
            ]
        )

        for group in self._menu_entry[index]:
            omni.kit.menu.utils.add_menu_items(self._menu_entry[index][group], name=group)

    def _destroy_menu(self, index=0):
        extension_id, action_name = self._get_action_name(self._menu_desc[index])
        omni.kit.actions.core.get_action_registry().deregister_action(extension_id, action_name)

        for group in self._menu_entry[index]:
            omni.kit.menu.utils.remove_menu_items(self._menu_entry[index][group], name=group)

        self._menu_entry[index] = None

    def _refresh_menu(self, index=0):
        if self._verbose[index]:
            print(f'[MenuHelperExtensionFull] _refresh_menu name:"{self._window_name[index]}" index:{index}')
        if self._menu_entry[index]:
            omni.kit.menu.utils.refresh_menu_items(f"{self._menu_group[index]}/{self._menu_desc[index]}")

    async def _destroy_window_async(self, index):
        if self._verbose[index]:
            print(f'[MenuHelperExtensionFull] _destroy_window_async name:"{self._window_name[index]}" index:{index}')

        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window_list[index]:
            self.__unregister_window(self._window_name[index])
            self._window_list[index].destroy()
            self._window_list[index] = None

    def _is_visible(self, index) -> bool:
        return False if self._window_list[index] is None else self._window_list[index].visible

    def _show(self, index=0):
        if self._verbose[index]:
            print(f'[MenuHelperExtensionFull] _show name:"{self._window_name[index]}" index:{index}')

        if self._window_list[index] is None:
            self.show_window(None, True, index)
        if self._window_list[index] and not self._window_list[index].visible:
            self.show_window(None, True, index)

    def _hide(self, index=0):
        if self._verbose[index]:
            print(f'[MenuHelperExtensionFull] _hide name:"{self._window_name[index]}" index:{index}')

        if self._window_list[index] is not None:
            self.show_window(None, False, index)

    def _toggle_window(self, index=0):
        import inspect

        if self._verbose[index]:
            print(f'[MenuHelperExtensionFull] _toggle_window name:"{self._window_name[index]}" index:{index}')

        if self._is_visible(index):
            if len(inspect.getfullargspec(self._hide).args) == 2:
                self._hide(index)
            else:
                self._hide()
        else:
            if len(inspect.getfullargspec(self._show).args) == 2:
                self._show(index)
            else:
                self._show()

    def _visiblity_changed_func(self, visible, index):
        if self._verbose[index]:
            print(
                f'[MenuHelperExtensionFull] _visiblity_changed_func name:"{self._window_name[index]}" visible:{visible}index:{index}'
            )

        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async(index))

        # this only tags test menu to update when menu is opening, so it
        # doesn't matter that is called before window has been destroyed
        self._refresh_menu(index)

    def show_window(self, menu, value, index):
        if self._verbose[index]:
            print(
                f'[MenuHelperExtensionFull] show_window menu:{menu} value:{value} name:"{self._window_name[index]}" index:{index}'
            )

        if value:
            self._window_list[index] = self.__get_window(self._create_window_fn[index](), index)
            # set visible to false to allow visibility_changed_* to be called
            self._window_list[index].visible = False

            if getattr(self._window_list[index], "set_visibility_changed_listener", None):
                self._window_list[index].set_visibility_changed_listener(
                    lambda v, i=index: self._visiblity_changed_func(v, i)
                )
            else:
                self._window_list[index].set_visibility_changed_fn(
                    lambda v, i=index: self._visiblity_changed_func(v, i)
                )

            # set visible to true to call visibility_changed_*
            self._window_list[index].visible = True

        elif self._window_list[index]:
            self._window_list[index].visible = False


class MenuHelperWindow(ui.Window):
    def __init__(self, *args, **kwargs):
        verbose = kwargs.get("verbose")

        super().__init__(*args, **kwargs)
        self._visiblity_changed_listener = None
        self._verbose = verbose
        self.set_visibility_changed_fn(self._visibility_changed_fn)

    def destroy(self):
        if self._verbose:
            print("[WindowMenuHelper] destroy")

        self.set_visibility_changed_listener(None)
        super().destroy()

    def _visibility_changed_fn(self, visible):
        if self._verbose:
            print(f"[WindowMenuHelper] _visibility_changed_fn visible:{visible}")

        if self._visiblity_changed_listener:
            self._visiblity_changed_listener(visible)

    def set_visibility_changed_listener(self, listener):
        if self._verbose:
            print(f"[WindowMenuHelper] set_visibility_changed_listener listener:{listener}")

        self._visiblity_changed_listener = listener
