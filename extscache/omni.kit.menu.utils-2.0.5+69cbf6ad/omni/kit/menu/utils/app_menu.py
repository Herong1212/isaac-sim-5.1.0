"""
ui.Menu and ui.MenuItem menu libraries
"""

__all__ = ["MenuItemOrder", "MenuState", "MenuActionControl", "IconMenuDelegate", "AppMenu"]


# pylint: disable=protected-access, redefined-outer-name
import asyncio
import sys
import weakref
from enum import IntFlag
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import carb
import omni.kit.app
from carb.eventdispatcher import Event, get_eventdispatcher
from omni import ui
from omni.kit.menu.core import IconMenuBaseDelegate, uiMenu, uiMenuItem

from .builder_utils import (
    MenuAlignment,
    MenuItemDescription,
    PrebuiltItemOrder,
    create_prebuild_entry,
    get_action_path,
    get_menu_name,
    has_delegate_func,
)
from .layout import MenuLayout  # noqa # pylint: disable=unused-import


class MenuItemOrder:
    """
    "appear_after" values. FIRST will be top of list and LAST will be bottom of list.
    """

    FIRST = "@first"
    LAST = "@last"


class MenuState(IntFlag):
    """
    Internal state. Invalid is before EVENT_APP_READY event received and Created is after.
    """

    Invalid = 0
    Created = 1


class MenuActionControl:
    """
    Setting for executing actions. Either NODELAY which is executed instantly or NONE which is async with 1 frame delay
    """

    NONE = "@MenuActionControl.NONE"
    NODELAY = "@MenuActionControl.NODELAY"


class IconMenuDelegate(IconMenuBaseDelegate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_settings("omni.kit.menu.utils")


class AppMenu:
    __logged_no_window: bool = False

    def __init__(self, get_instance: Optional[callable] = None, menu_bar: Optional[ui.MenuBar] = None):
        """
        Create app menu for menu bar.

        Args:
            get_instance (Optional[callable]): Callback to get extension instance, defaults to None. Deprecated.
            menu_bar (Optional[ui.MenuBar]): Menu bar to create menus, defaults to None which means use menu bar in main window.
        """
        if get_instance:
            carb.log_info("AppMenu get_instance is deprecated. Please use menu_bar instead")

        self.ready_state = MenuState.Invalid
        self._menu_hooks = [self.sort_menu_hook]
        self._active_menus = {}
        self._menu_count = {}
        self._main_menus = {}
        self.set_right_padding(0)
        self._dirty_menus = {}
        self._radio_groups = {}
        self._torn_menus = []
        self._stats = omni.kit.menu.utils.get_debug_stats()
        self._last_item = None
        self._visible_menus = []
        self._prebuilt_menus = []
        self._menu_bar = menu_bar

        self._menu_defs = {}
        self._menu_delegates = {}
        self._menu_order = {}
        self._menu_layout = MenuLayout()
        self._hooks = []

        if "triggered_refresh" not in self._stats:
            self._stats["triggered_refresh"] = 0

        if "refreshed_menu_items" not in self._stats:
            self._stats["refreshed_menu_items"] = {}

        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()

        # setup window
        if menu_bar:
            self._menubar = menu_bar
        else:
            mainwindow_loaded = next(
                (
                    ext
                    for ext in ext_manager.get_extensions()
                    if ext["id"].startswith("omni.kit.mainwindow") and ext["enabled"]
                ),
                None,
            )
            if mainwindow_loaded:
                from omni.kit.mainwindow import get_main_window

                self._menu_bar = get_main_window().get_main_menu_bar()
            else:
                self._menu_bar = None
                carb.log_info("omni.kit.mainwindow is not loaded. Menus are disabled")

                # if mainwindow loads later, need to refresh menu_creator
                manager = omni.kit.app.get_app().get_extension_manager()
                self._hooks.append(
                    manager.subscribe_to_extension_enable(
                        on_enable_fn=lambda _: self._mainwindow_loaded(),
                        on_disable_fn=None,
                        ext_name="omni.kit.mainwindow",
                        hook_name="omni.kit.menu.utils omni.kit.mainwindow listener",
                    )
                )
        if self._menu_bar:
            self._menu_bar.visible = True

        self._dict = carb.dictionary.get_dictionary()
        self._icon_delegate = IconMenuDelegate()

        # set app started trigger. refresh_menu_items & rebuild_menus won't do anything until self.ready_state is MenuState.Created
        self._app_ready_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_APP_READY,
            on_event=self._set_ready_state,
            observer_name="omni.kit.menu.utils app started trigger",
        )

        # Hook to extension enable/disable
        # to setup hotkey with different ways with omni.kit.hotkeys.core enabled/disabled
        hooks = ext_manager.get_hooks()
        self.__extension_enabled_hook = hooks.create_extension_state_change_hook(
            self.__on_ext_changed, omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE
        )
        self.__extension_disabled_hook = hooks.create_extension_state_change_hook(
            self.__on_ext_changed, omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE
        )

        self.__actions_map: Dict[str, MenuItemDescription] = {}
        try:
            from omni.kit.hotkeys.core import (
                HOTKEY_CHANGED_GLOBAL_EVENT,
                HOTKEY_DEREGISTER_GLOBAL_EVENT,
                HOTKEY_REGISTER_GLOBAL_EVENT,
            )

            # Watch hotkey events
            self.__hotkey_register_event_sub = (  # pylint: disable=unused-private-member
                get_eventdispatcher().observe_event(
                    event_name=HOTKEY_REGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_changed
                )
            )
            self.__hotkey_deregister_event_sub = (  # pylint: disable=unused-private-member
                get_eventdispatcher().observe_event(
                    event_name=HOTKEY_DEREGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_changed
                )
            )
            self.__hotkey_change_event_sub = (  # pylint: disable=unused-private-member
                get_eventdispatcher().observe_event(
                    event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self._on_hotkey_changed
                )
            )
        except ImportError:  # pragma: no cover
            self.__hotkey_register_event_sub = None  # pylint: disable=unused-private-member
            self.__hotkey_deregister_event_sub = None  # pylint: disable=unused-private-member
            self.__hotkey_change_event_sub = None  # pylint: disable=unused-private-member

    def _set_ready_state(self, _):
        self.ready_state = MenuState.Created
        self.build_menus_after_loading()

    @staticmethod
    def sort_menu_hook(merged_menu):
        def priority_sort(menu_entry):
            if hasattr(menu_entry, "priority"):
                return menu_entry.priority
            return 0

        for name in merged_menu.keys():
            if name in merged_menu:
                merged_menu[name].sort(key=priority_sort)

    def destroy(self):  # pragma: no cover
        if self._menu_layout:
            self._menu_layout.destroy()
            del self._menu_layout
            self._menu_layout = None

        self.__extension_enabled_hook = None
        self.__extension_disabled_hook = None

        self.__hotkey_register_event_sub = None  # pylint: disable=unused-private-member
        self.__hotkey_deregister_event_sub = None  # pylint: disable=unused-private-member
        self.__hotkey_change_event_sub = None  # pylint: disable=unused-private-member
        for action_path in self._active_menus:
            self._active_menus[action_path] = None
        del self._active_menus
        self._active_menus = {}
        self._main_menus = {}
        self._radio_groups = {}
        self._menu_bar.clear()
        self._menu_bar = None

    def add_menu_items(
        self,
        menu: list,
        name: str,
        menu_index: int,
        can_rebuild_menus: bool,
        delegate=None,
    ) -> list:
        if not menu and delegate:
            menu = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]

        if menu and not isinstance(menu[0], MenuItemDescription):
            carb.log_error(f"add_menu_items: menu {menu} is not a MenuItemDescription")
            return None

        self._stats["add_menu_items"] += 1

        if name not in self._menu_defs:
            self._menu_defs[name] = []
        self._menu_defs[name].append(menu)

        if name in self._menu_delegates:
            _delegate, count = self._menu_delegates[name]
            if delegate and _delegate and delegate != _delegate:
                carb.log_warn(f"add_menu_items: menu {menu} cannot change delegate")
            self._menu_delegates[name] = (_delegate, count + 1)
        elif delegate:
            self._menu_delegates[name] = (delegate, 1)

        if menu_index != 0 and name not in self._menu_order:
            self._menu_order[name] = menu_index

        if can_rebuild_menus:
            self.rebuild_menus()

        return menu

    def replace_menu_items(self, new_menu: list, old_menu: list, name: str) -> list:
        if new_menu and not isinstance(new_menu[0], MenuItemDescription):
            carb.log_error(f"replace_menu_items: menu {new_menu} is not a MenuItemDescription")
            return None

        if name not in self._menu_defs:
            carb.log_error(f"replace_menu_items: menu {name} doesn't exist, was it added?")
            return None

        try:
            index = self._menu_defs[name].index(old_menu)
            self._menu_defs[name][index] = new_menu
            self._stats["replace_menu_items"] += 1

            self.rebuild_menus()

            return new_menu
        except Exception:  # pylint: disable=broad-exception-caught
            carb.log_error(f"replace_menu_items: old_menu {old_menu} not found")

        return None

    def set_default_menu_priority(self, name: str, menu_index: int):
        if menu_index == 0:
            return

        for _, index in self._menu_order.items():
            if index == menu_index:
                return
        self._menu_order[name] = menu_index

    def remove_menu_items(self, menu: list, name: str, can_rebuild_menus: bool):
        self._stats["remove_menu_items"] += 1
        try:
            if name in self._menu_defs:
                self._menu_defs[name].remove(menu)

            if name in self._menu_delegates:
                delegate, count = self._menu_delegates[name]
                if count == 1:
                    del self._menu_delegates[name]
                else:
                    self._menu_delegates[name] = (delegate, count - 1)

            if can_rebuild_menus:
                self.rebuild_menus()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            carb.log_warn(f'omni.kit.menu.utils remove_menu_items "{name}" failed {exc}')

    def add_layout(
        self,
        layout: List[
            Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]
        ],
    ):
        self._stats["add_layout"] += 1
        self._menu_layout.add_layout(layout)
        self.rebuild_menus()

    def remove_layout(
        self,
        layout: List[
            Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]
        ],
    ):
        self._stats["remove_layout"] += 1
        self._menu_layout.remove_layout(layout)
        self.rebuild_menus()

    def get_merged_menus(self):
        return self.merge_menus(self._menu_defs.keys(), self._menu_defs, self._menu_order)

    def rebuild_menus(self):
        if not self.ready_state & MenuState.Created:
            self._stats["rebuild_menus_skipped"] += 1
            return

        self._stats["rebuild_menus"] += 1

        if self._menu_bar:
            self.create_menu()

    def get_menu_layout(self):
        return self._menu_layout

    def get_menu_data(self):
        return self._menu_defs, self._menu_order, self._menu_delegates

    def clear_menu_data(self):
        self._menu_defs = {}
        self._menu_order = {}
        self._menu_delegates = {}

    def build_menus_after_loading(self):
        self._menu_layout.menus_created()
        self.rebuild_menus()

    def add_hook(self, callback: Callable):
        self._menu_hooks.append(callback)

    def remove_hook(self, callback: Callable):
        try:
            self._menu_hooks.remove(callback)
        except Exception as exc:  # pragma: no cover # pylint: disable=broad-except
            carb.log_warn(f"omni.kit.menu.utils remove_hook failed {exc}")

    def merge_menus(self, menu_keys: list, menu_defs: list, menu_order: list, delegates=None):
        merged_menu = {}
        delegates = delegates if delegates else {}

        def order_sort(name):
            if name in menu_order:
                return menu_order[name]
            return 0

        def get_item_menu_index(menu: list, name: str):
            for index, item in enumerate(menu):
                if item.name == name:
                    return index
            return -1

        def process_part(name, part, can_retry):
            used = False
            if not isinstance(part.appear_after, list):
                part.appear_after = [part.appear_after]

            for aindex, after in enumerate(part.appear_after):
                if after in [MenuItemOrder.FIRST, MenuItemOrder.LAST] and can_retry and aindex != 0:
                    break

                if after == MenuItemOrder.FIRST:
                    merged_menu[name].insert(0, part)
                    used = True
                    break
                if after == MenuItemOrder.LAST:
                    merged_menu[name].append(part)
                    used = True
                    break

                index = get_item_menu_index(merged_menu[name], after)
                # found something but if its not 1st choice, it can be skipped as it will be added to retry list
                # this can happen if appear_after item also has an appear_after so may not of been added yet
                if can_retry and index != -1 and aindex != 0:
                    break

                if index != -1:
                    merged_menu[name].insert(index + 1, part)
                    used = True
                    break

            return used

        def get_items(sorted_keys, can_retry):
            appear_after_retries = []
            for name in sorted_keys:
                if name not in merged_menu:
                    merged_menu[name] = []
                for parts in menu_defs[name]:
                    for part in parts:
                        if part.appear_after:
                            used = process_part(name, part, can_retry)
                            if not used:
                                appear_after_retries.append((name, part))
                        else:
                            merged_menu[name].append(part)

            for name, part in appear_after_retries:
                used = process_part(name, part, can_retry)
                if not used and not can_retry:
                    carb.log_verbose(
                        f'Warning: menu item "{part.name}" failed to find appear_after index "{part.appear_after}"'
                    )
                    merged_menu[name].append(part)

        # order using menu_order
        sorted_keys = list(menu_keys)
        if menu_order:
            sorted_keys.sort(key=order_sort)

        # get menu non-appear_after items & appear_after items
        get_items(sorted_keys, True)
        get_items(sorted_keys, False)

        for hook_fn in self._menu_hooks:
            hook_fn(merged_menu)

        # prebuild menus so layout can be applied before building
        self._prebuilt_menus = {}
        for name, item in merged_menu.items():
            self.prebuild_menu(
                item, name, get_action_path(name, None), delegates[name][0] if name in delegates else None
            )

        prebuilt_menus = self._prebuilt_menus
        self._prebuilt_menus = None
        self.get_menu_layout().apply_layout(prebuilt_menus)
        return prebuilt_menus

    def prebuild_menu(self, menus, prefix_name, action_prefix, delegate):
        try:
            import copy

            def prebuild_menu_item(entry, prefix_name, action_prefix):
                item = copy.copy(entry)
                item.user["prebuilt_order"] = PrebuiltItemOrder.UNORDERED

                # add submenu items to list
                create_prebuild_entry(self._prebuilt_menus, prefix_name, action_prefix)

                # check if item already on list, to avoid duplicates
                duplicate = False
                if item.name != "":
                    for old_item in self._prebuilt_menus[action_prefix]["items"]:
                        if item.name == old_item.name:
                            duplicate = True
                            break

                if not duplicate:
                    # prefix_name cannot be "" as creating submenus with "" causes problems
                    self._prebuilt_menus[action_prefix]["items"].append(item)
                    self._prebuilt_menus[action_prefix]["prefix_name"] = prefix_name if prefix_name else "Empty"
                    self._prebuilt_menus[action_prefix]["remapped"] = []
                    self._prebuilt_menus[action_prefix]["action_prefix"] = action_prefix
                    self._prebuilt_menus[action_prefix]["menu_alignment"] = MenuAlignment.DEFAULT
                    self._prebuilt_menus[action_prefix]["delegate"] = delegate
                    self._prebuilt_menus[action_prefix]["parent"] = None

                    if has_delegate_func(delegate, "get_menu_alignment"):
                        self._prebuilt_menus[action_prefix]["menu_alignment"] = delegate.get_menu_alignment()

                if item.sub_menu and entry.name:
                    sub_prefix = get_menu_name(entry)
                    sub_action = get_action_path(action_prefix, entry.name)
                    for sub_item in item.sub_menu:
                        prebuild_menu_item(sub_item, sub_prefix, sub_action)
                    self._prebuilt_menus[sub_action]["sub_menu"] = True
                    self._prebuilt_menus[sub_action]["parent"] = item
                    item.sub_menu = sub_action

            for menu_entry in menus:
                prebuild_menu_item(menu_entry, prefix_name, action_prefix)
        except Exception as e:  # pragma: no cover # pylint: disable=broad-except
            import traceback

            carb.log_error(f"Error {e} creating menu {menu_entry}")
            traceback.print_exc(file=sys.stdout)

    def get_fn_result(self, menu_entry: MenuItemDescription, name: str, default: bool = True):
        fn = getattr(menu_entry, name)
        if not fn:
            return default
        if isinstance(fn, list):
            for fn_item in fn:
                if fn_item and not fn_item():
                    return False
        else:
            if fn and not fn():
                return False
        return default

    def set_right_padding(self, padding):
        self._right_padding = padding

    def create_menu(self):
        menu_defs, menu_order, delegates = self.get_menu_data()

        self._menu_bar.clear()
        self._active_menus = {}
        self._radio_groups = {}
        self._main_menus = {}
        self._visible_menus = {}
        self._last_item = {}
        self._menu_count = {}
        self._dirty_menus = {}

        menus = self.merge_menus(menu_defs.keys(), menu_defs, menu_order, delegates)
        right_menus = []
        with self._menu_bar:
            for name, item in menus.items():
                if "sub_menu" not in item:
                    if item["menu_alignment"] == MenuAlignment.RIGHT:
                        right_menus.append(name)
                    else:
                        self._build_menu(item, menus, True, None)

            if right_menus:
                ui.Spacer().identifier = "right_aligned_menus"
                for name in right_menus:
                    self._build_menu(menus[name], menus, True, None)
                ui.Spacer(width=self._right_padding).identifier = "right_padding"

        for key, item in self._main_menus.items():
            if key not in self._visible_menus:
                item.visible = False

            if key in self._menu_count and self._menu_count[key] == 0:
                item.visible = False

            if key in self._last_item and isinstance(self._last_item[key], ui.Separator):
                self._last_item[key].visible = False

        self._last_item = None
        self._visible_menus = None

        return menus

    def refresh_menu_items(self, name: str, action_path: str = ""):
        if not self.ready_state & MenuState.Created:
            self._stats["refresh_menu_items_skipped"] += 1
            return

        if self._menu_bar is None:
            return

        if not name and action_path:
            name = action_path.split("_")[0]

        if name not in self._dirty_menus:
            self._dirty_menus[name] = set()

        if action_path:
            self._dirty_menus[name].add(action_path)
        else:
            self._dirty_menus[name] = set()

        # torn menus have to be updated now as they never call on_triggered
        if self._torn_menus:
            menu_defs, menu_order, _ = self.get_menu_data()
            menus = self.merge_menus(menu_defs.keys(), menu_defs, menu_order)

            for ap in self._torn_menus:
                self._refresh_menu_item(ap, menus, [])

    def _submenu_is_shown(self, action_prefix: str, visible: bool, delegate: Any, refresh: bool):
        if action_prefix in self._main_menus:
            self._main_menus[action_prefix].visible = visible
            if has_delegate_func(delegate, "update_menu_item"):
                delegate.update_menu_item(self._main_menus[action_prefix], refresh)

    def _refresh_menu_item(self, action_path: str, menus: list, action_path_items: list):
        if action_path in menus:
            self._refresh_menu(
                menus[action_path]["action_prefix"], menus[action_path], menus, action_path_items=action_path_items
            )
            for remapped in menus[action_path]["remapped"]:
                self._refresh_menu(
                    menus[remapped]["action_prefix"], menus[remapped], menus, action_path_items=action_path_items
                )

    # update to use new prebuild/layouts
    def _refresh_menu(
        self, action_prefix, prebuilt_menus, prebuilt_menus_root, action_path_items=None, visible_override=None
    ):
        menus = prebuilt_menus["items"]
        delegate = prebuilt_menus["delegate"] if "delegate" in prebuilt_menus else None

        visible_count = 0
        for menu_entry in sorted(menus, key=lambda a: a.user["prebuilt_order"]):
            try:
                action_path = get_action_path(action_prefix, menu_entry.name)
                visible = self.get_fn_result(menu_entry, "show_fn") if menu_entry.show_fn else True
                menu_name = get_menu_name(menu_entry)

                # handle sub_menu before action_path/active_menus can skip it
                if menu_entry.sub_menu and menu_entry.sub_menu in prebuilt_menus_root:
                    visible = self._refresh_menu(
                        action_path,
                        prebuilt_menus_root[menu_entry.sub_menu],
                        prebuilt_menus_root,
                        action_path_items,
                        self.get_fn_result(menu_entry, "show_fn", None),
                    )
                    # update visibility
                    if visible_override is not None:
                        visible = visible_override
                    visible_count += 1 if visible and menu_name != "" else 0
                    self._submenu_is_shown(menu_entry.sub_menu, visible, delegate, True)
                    continue

                # is item being refreshed
                if action_path_items and action_path not in action_path_items:
                    # Not being refreshed, but need to keep visible for sub menus
                    visible_count += 1 if visible and menu_name != "" else 0
                    continue

                # is item active
                if action_path not in self._active_menus:
                    continue

                if action_path not in self._stats["refreshed_menu_items"]:
                    self._stats["refreshed_menu_items"][action_path] = 0
                self._stats["refreshed_menu_items"][action_path] += 1

                enabled = menu_entry.enabled
                value = menu_entry.ticked_value
                if menu_entry.enable_fn:
                    enabled = self.get_fn_result(menu_entry, "enable_fn")
                if menu_entry.ticked_fn:
                    value = self.get_fn_result(menu_entry, "ticked_fn")

                item = self._active_menus[action_path]
                item.enabled = enabled
                item.checked = value
                item.visible = visible
                item.hotkey_text = menu_entry.original_menu_item.hotkey_text
                if has_delegate_func(delegate, "update_menu_item"):
                    delegate.update_menu_item(item, True)
                visible_count += 1 if item.visible else 0
            except Exception as e:  # pragma: no cover # pylint: disable=broad-except
                import traceback

                carb.log_error(f"Error {e} refreshing menu {menu_entry}")
                traceback.print_exc(file=sys.stdout)

        return visible_count > 0

    def _build_menu(
        self,
        prebuilt_menus,
        prebuilt_menus_root,
        is_root_menu,
        parent_menu,
        visible_override=None,
        menu_checkable=False,
        menu_hotkey_text=False,
        glyph=None,
    ) -> int:
        self._torn_menus = []

        def on_triggered():
            if self._dirty_menus:
                self._stats["triggered_refresh"] += 1
                menu_defs, menu_order, _ = self.get_menu_data()
                menus = self.merge_menus(menu_defs.keys(), menu_defs, menu_order)
                for name, item in self._dirty_menus.items():
                    self._refresh_menu_item(get_action_path(name, None), menus, item)
                self._dirty_menus = {}

        def on_torn(state: bool, action_prefix: str):
            if state:
                self._torn_menus.append(action_prefix)
            elif action_prefix in self._torn_menus:
                self._torn_menus.remove(action_prefix)

        def prep_menu(
            main_menu,
            prefix_name: str,
            action_prefix: str,
            visible: bool,
            delegate: callable,
            glyph: str,
            menu_checkable: bool,
            menu_hotkey_text: bool,
        ):
            if action_prefix not in main_menu:
                default_style = self._icon_delegate.get_style()
                if hasattr(delegate, "get_style"):
                    default_style = default_style | delegate.get_style()

                main_menu[action_prefix] = uiMenu(
                    prefix_name,
                    spacing=2,
                    visible=visible,
                    delegate=delegate,
                    glyph=glyph,
                    menu_checkable=menu_checkable,
                    menu_hotkey_text=menu_hotkey_text,
                    submenu=not is_root_menu,
                    parent_menu=parent_menu,
                    style=default_style,
                )
                # only set triggered_fn on root menus as it won't get triggered on submenus
                if is_root_menu:
                    main_menu[action_prefix].set_triggered_fn(on_triggered)
                main_menu[action_prefix].set_teared_changed_fn(lambda s, a=action_prefix: on_torn(s, a))
                self._menu_count[action_prefix] = 0

        menus = prebuilt_menus["items"]
        action_prefix = prebuilt_menus["action_prefix"]
        delegate = prebuilt_menus["delegate"] if "delegate" in prebuilt_menus else None
        visible_count = 0

        # this menu item is built with menu_checkable passed via caller
        prep_menu(
            self._main_menus,
            parent_menu.name if parent_menu else prebuilt_menus["prefix_name"],
            action_prefix,
            True if visible_override is None else visible_override,
            delegate if delegate else self._icon_delegate,
            glyph,
            menu_checkable,
            menu_hotkey_text,
        )

        def execute_radio_group(action_path, radio_group, on_lmb_click):
            # omni.ui will toggle clicked item after this, so set everything in group to False
            for item_path in self._radio_groups[radio_group]:
                self._active_menus[item_path].checked = False

            if on_lmb_click:
                on_lmb_click()

        # get delegate for icons
        menu_hotkey_text = False
        menu_checkable = False
        for menu_entry in sorted(menus, key=lambda a: a.user["prebuilt_order"]):
            if menu_entry.ticked:
                menu_checkable = True
            if menu_entry.original_menu_item and menu_entry.original_menu_item.hotkey:
                menu_hotkey_text = True

        with self._main_menus[action_prefix]:
            # order menu using "prebuilt_order"
            for menu_entry in sorted(menus, key=lambda a: a.user["prebuilt_order"]):
                try:
                    item = None
                    menu_name = get_menu_name(menu_entry)
                    action_path = get_action_path(action_prefix, menu_entry.name)

                    on_lmb_click = None
                    if menu_entry.onclick_action and menu_entry.unclick_action:
                        on_lmb_click = lambda oca=menu_entry.onclick_action, uca=menu_entry.unclick_action: (
                            self._execute_action(oca),
                            self._execute_action(uca),
                        )
                    elif menu_entry.onclick_action:
                        on_lmb_click = lambda oca=menu_entry.onclick_action: self._execute_action(oca)
                    elif menu_entry.onclick_fn and menu_entry.unclick_fn:
                        on_lmb_click = lambda me=menu_entry: (
                            me.onclick_fn(),
                            me.unclick_fn(),
                        )
                    else:
                        on_lmb_click = menu_entry.onclick_fn

                    hotkey = None
                    if menu_entry.original_menu_item:
                        hotkey = menu_entry.original_menu_item.hotkey
                    enabled = menu_entry.enabled
                    ticked = menu_entry.ticked
                    radio_group = menu_entry.radio_group
                    value = menu_entry.ticked_value
                    visible = True
                    if menu_entry.enable_fn:
                        enabled = self.get_fn_result(menu_entry, "enable_fn")
                    if menu_entry.ticked_fn:
                        value = self.get_fn_result(menu_entry, "ticked_fn")
                    if menu_entry.show_fn:
                        visible = self.get_fn_result(menu_entry, "show_fn")

                    if menu_entry.name and menu_entry.sub_menu:
                        if menu_entry.sub_menu in prebuilt_menus_root:
                            self._visible_menus[action_prefix] = visible
                            visible = self._build_menu(
                                prebuilt_menus_root[menu_entry.sub_menu],
                                prebuilt_menus_root,
                                False,
                                menu_entry,
                                self.get_fn_result(menu_entry, "show_fn", None),
                                menu_checkable,
                                menu_hotkey_text,
                                menu_entry.glyph,
                            )
                            # clear last item as sub menu won't of tagged anything for this action_prefix menu
                            self._last_item[action_prefix] = None

                            if visible_override is not None:
                                visible = visible_override
                            visible_count += 1 if visible else 0
                            self._submenu_is_shown(menu_entry.sub_menu, visible, delegate, False)
                            if visible:
                                if action_prefix not in self._menu_count:
                                    self._menu_count[action_prefix] = 0
                                self._menu_count[action_prefix] += 1
                        continue
                    if menu_entry.header is not None and not menu_entry.name:
                        if action_prefix in self._last_item:
                            if isinstance(self._last_item[action_prefix], ui.Separator):
                                # last thing was a Separator, change the text to new value
                                self._last_item[action_prefix].text = menu_entry.header
                            else:
                                item = ui.Separator(menu_entry.header)
                        else:
                            item = ui.Separator(menu_entry.header)
                    elif menu_entry.name == "":
                        if action_prefix in self._last_item:
                            if action_prefix in self._last_item and not isinstance(
                                self._last_item[action_prefix], ui.Separator
                            ):
                                item = ui.Separator()
                        else:
                            item = ui.Separator()
                    else:
                        if menu_entry.header is not None:
                            if action_prefix in self._last_item:
                                if isinstance(self._last_item[action_prefix], ui.Separator):
                                    # last thing was a Separator, change the text to new value
                                    self._last_item[action_prefix].text = menu_entry.header
                                else:
                                    item = ui.Separator(menu_entry.header)
                            else:
                                item = ui.Separator(menu_entry.header)

                        if radio_group:
                            if radio_group not in self._radio_groups:
                                self._radio_groups[radio_group] = []

                            # hijack on_lmb_click so radio buttons can be cleared before calling click fn
                            menu_click_fn = on_lmb_click
                            on_lmb_click = lambda rg=radio_group, ap=action_path, c=menu_click_fn: execute_radio_group(
                                ap, rg, c
                            )

                        # create menu item
                        item = uiMenuItem(
                            menu_name,
                            triggered_fn=on_lmb_click if on_lmb_click else None,
                            checkable=ticked,
                            checked=value,
                            radio_group=radio_group,
                            enabled=enabled,
                            visible=visible,
                            style=menu_entry.user.get("user_style", {}),
                            delegate=delegate if delegate else self._icon_delegate,
                            glyph=menu_entry.glyph,
                            menu_checkable=menu_checkable,
                            menu_hotkey_text=menu_hotkey_text,
                            parent_menu=parent_menu,
                        )
                        if radio_group:
                            self._radio_groups[radio_group].append(action_path)

                        if has_delegate_func(delegate, "update_menu_item"):
                            delegate.update_menu_item(item, False)
                        self._active_menus[action_path] = item
                        self._menu_count[action_prefix] += 1

                        if hotkey:
                            item.hotkey_text = "  " + menu_entry.original_menu_item.hotkey_text
                            setup_hotkey = True
                            try:
                                import omni.kit.hotkeys.core  # noqa # pylint: disable=unused-import

                                # Always setup hotkey because hotkey may changed
                                setup_hotkey = True
                            except ImportError:  # pragma: no cover
                                if hasattr(menu_entry.original_menu_item, "_action_setting_sub_id"):
                                    setup_hotkey = False
                            if setup_hotkey:
                                hotkey_text = self._setup_hotkey(menu_entry.original_menu_item, action_path)
                                if hotkey_text is not None:
                                    item.hotkey_text = hotkey_text
                    if item:
                        self._last_item[action_prefix] = item
                        self._visible_menus[action_prefix] = visible
                        visible_count += 1 if visible else 0

                except Exception as e:  # pragma: no cover # pylint: disable=broad-except
                    import traceback

                    carb.log_error(f"Error {e} creating menu {menu_entry}")
                    traceback.print_exc(file=sys.stdout)

        return visible_count > 0

    def _execute_action(self, action: Tuple):
        if not action:
            return

        async_delay = True

        # check for MenuActionControl in action & remove
        actioncontrol_list = [MenuActionControl.NONE, MenuActionControl.NODELAY]
        if any(a in action for a in actioncontrol_list):
            if MenuActionControl.NODELAY in action:
                async_delay = False
            action = [item for item in action if item not in actioncontrol_list]

        try:
            import omni.kit.actions.core
            import omni.kit.app

            if async_delay:

                async def execute_action(action):
                    await omni.kit.app.get_app().next_update_async()
                    omni.kit.actions.core.execute_action(*action)

                # omni.ui can sometimes crash is menu callback does ui calls.
                # To avoid this, use async function with frame delay
                asyncio.ensure_future(execute_action(action))
            else:
                omni.kit.actions.core.execute_action(*action)
        except ModuleNotFoundError:  # pragma: no cover
            carb.log_warn("menu_action: error omni.kit.actions.core not loaded")
        except Exception as exc:  # pragma: no cover # pylint: disable=broad-except
            carb.log_warn(f"menu_action: error {exc}")

    def _setup_hotkey(self, menu_entry: MenuItemDescription, action_path: str) -> str:
        from functools import partial

        import omni.appwindow

        appwindow = omni.appwindow.get_default_app_window()
        if not appwindow:
            if not AppMenu.__logged_no_window:
                AppMenu.__logged_no_window = True
                carb.log_error("Hotkeys cannot be setup without a default window")
            return None

        def action_trigger(on_action_pressed_fn, on_action_release_fn, evt, *_):
            if evt.flags & carb.input.BUTTON_FLAG_PRESSED:
                if on_action_pressed_fn:
                    on_action_pressed_fn()
            elif on_action_release_fn:
                on_action_release_fn()

        if not menu_entry.hotkey:
            return None

        self._clear_hotkey(menu_entry)
        self._unregister_hotkey(menu_entry)

        _input = carb.input.acquire_input_interface()
        settings = carb.settings.get_settings()

        action_mapping_set_path = appwindow.get_action_mapping_set_path()
        action_mapping_set = _input.get_action_mapping_set_by_path(action_mapping_set_path)
        input_string = menu_entry.get_action_mapping_desc()
        menu_entry._action_setting_input_path = action_mapping_set_path + "/" + action_path + "/0"
        settings.set_default_string(menu_entry._action_setting_input_path, input_string)
        if menu_entry.onclick_action:
            try:
                from omni.kit.hotkeys.core import get_hotkey_registry

                if not get_hotkey_registry():
                    raise ImportError
                current_action_triggger = None
                menu_entry._action_path = action_path
                self._register_hotkey(menu_entry)
                menu_entry.add_on_hotkey_update_func(lambda me, a=action_path: self._setup_hotkey(me, a))
                if hasattr(menu_entry, "_pressed_hotkey"):
                    return menu_entry._pressed_hotkey.key_text if menu_entry._pressed_hotkey else ""
                if hasattr(menu_entry, "_released_hotkey"):
                    return menu_entry._released_hotkey.key_text if menu_entry._released_hotkey else ""
                return None
            except ImportError:  # pragma: no cover
                current_action_triggger = partial(
                    action_trigger,
                    lambda oca=menu_entry.onclick_action: self._execute_action(oca),
                    lambda uca=menu_entry.unclick_action: self._execute_action(uca),
                )

        else:
            current_action_triggger = partial(action_trigger, menu_entry.onclick_fn, menu_entry.unclick_fn)

        if current_action_triggger:
            menu_entry._action_setting_sub_id = _input.subscribe_to_action_events(
                action_mapping_set, action_path, current_action_triggger
            )
            menu_entry.add_on_delete_func(self._clear_hotkey)
            menu_entry.add_on_hotkey_update_func(lambda me, a=action_path: self._setup_hotkey(me, a))

            # menu needs to refresh when self._action_setting_input_path changes
            def hotkey_changed(
                changed_item: carb.dictionary.Item,
                change_event_type: carb.settings.ChangeEventType,
                weak_entry: weakref,
                action_path: str,
            ):
                import carb.input

                def set_hotkey_text(action_path, hotkey_text, active_menu_text):
                    menu_entry.hotkey_text = hotkey_text
                    if action_path in self._active_menus:
                        self._active_menus[action_path].hotkey_text = active_menu_text

                menu_entry = weak_entry()
                if not menu_entry:
                    return

                # "changed_item" was DESTROYED, so remove hotkey
                if change_event_type == carb.settings.ChangeEventType.DESTROYED:
                    set_hotkey_text(action_path, "", "")
                    return

                hotkey_mapping = self._dict.get(changed_item)
                if isinstance(hotkey_mapping, str):
                    set_hotkey_text(
                        action_path, hotkey_mapping.replace("Keyboard::", ""), "  " + menu_entry.hotkey_text
                    )
                else:
                    set_hotkey_text(action_path, "", "")

            menu_entry._action_setting_changed_sub = settings.subscribe_to_node_change_events(
                menu_entry._action_setting_input_path,
                lambda ci, ev, m=weakref.ref(menu_entry), a=action_path: hotkey_changed(ci, ev, m, a),
            )
        return None

    def _clear_hotkey(self, menu_entry):
        if hasattr(menu_entry, "_action_setting_sub_id"):
            try:
                _input = carb.input.acquire_input_interface()
                _input.unsubscribe_to_action_events(menu_entry._action_setting_sub_id)
                del menu_entry._action_setting_sub_id
                settings = carb.settings.get_settings()
                settings.unsubscribe_to_change_events(menu_entry._action_setting_changed_sub)
                del menu_entry._action_setting_changed_sub
                del menu_entry._action_setting_input_path
            except Exception:  # pragma: no cover # pylint: disable=broad-except
                pass

    def _register_hotkey(self, menu_entry: MenuItemDescription):
        try:
            from omni.kit.hotkeys.core import HotkeyFilter, KeyCombination, get_hotkey_registry

            hotkey_registry = get_hotkey_registry()
            if not hotkey_registry:
                raise ImportError
            hotkey_ext_id = "omni.kit.menu.utils"
            if menu_entry.hotkey_window:
                hotkey_filter = HotkeyFilter(windows=[menu_entry.hotkey_window])
            else:
                hotkey_filter = None
            if menu_entry.onclick_action:
                key = KeyCombination(menu_entry.hotkey[1], modifiers=menu_entry.hotkey[0])
                menu_entry._pressed_hotkey = hotkey_registry.register_hotkey(
                    hotkey_ext_id, key, menu_entry.onclick_action[0], menu_entry.onclick_action[1], filter=hotkey_filter
                )
                # If hotkey disabled, do not show hotkey text
                if menu_entry._pressed_hotkey is None:
                    menu_entry.hotkey_text = ""
                action_id = menu_entry.onclick_action[0] + "::" + menu_entry.onclick_action[1]
                self.__actions_map[action_id] = menu_entry
            if menu_entry.unclick_action:
                key = KeyCombination(menu_entry.hotkey[1], modifiers=menu_entry.hotkey[0], trigger_press=False)
                menu_entry._released_hotkey = hotkey_registry.register_hotkey(
                    hotkey_ext_id, key, menu_entry.unclick_action[0], menu_entry.unclick_action[1], filter=hotkey_filter
                )
                # If hotkey disabled, do not show hotkey text
                if menu_entry._released_hotkey is None:
                    menu_entry.hotkey_text = ""
                action_id = menu_entry.unclick_action[0] + "::" + menu_entry.unclick_action[1]
                self.__actions_map[action_id] = menu_entry
            menu_entry.add_on_delete_func(self._unregister_hotkey)
        except ImportError:  # pragma: no cover
            pass

    def _unregister_hotkey(self, menu_entry: MenuItemDescription):
        try:
            from omni.kit.hotkeys.core import get_hotkey_registry

            hotkey_registry = get_hotkey_registry()
            if hotkey_registry:
                if hasattr(menu_entry, "_pressed_hotkey") and menu_entry._pressed_hotkey:
                    action_id = menu_entry.onclick_action[0] + "::" + menu_entry.onclick_action[1]
                    self.__actions_map.pop(action_id)
                    hotkey_registry.deregister_hotkey(menu_entry._pressed_hotkey)
                    menu_entry._pressed_hotkey = None
                if hasattr(menu_entry, "_released_hotkey") and menu_entry._released_hotkey:
                    action_id = menu_entry.unclick_action[0] + "::" + menu_entry.unclick_action[1]
                    self.__actions_map.pop(action_id)
                    hotkey_registry.deregister_hotkey(menu_entry._released_hotkey)
                    menu_entry._released_hotkey = None
        except ImportError:  # pragma: no cover
            pass

    def _on_hotkey_changed(self, event: Event) -> None:
        action_id = event["action_ext_id"] + "::" + event["action_id"]
        menu_entry = self.__actions_map.get(action_id, None)
        if menu_entry:
            from omni.kit.hotkeys.core import HOTKEY_DEREGISTER_GLOBAL_EVENT

            # If hotkey deregistered, change hotkey text to empty string
            menu_entry.hotkey_text = "" if event.event_name == HOTKEY_DEREGISTER_GLOBAL_EVENT else event["key"]
            self.refresh_menu_items("", menu_entry._action_path)

    def _mainwindow_loaded(self):
        from omni.kit.mainwindow import get_main_window

        self._menu_bar = get_main_window().get_main_menu_bar()
        self.rebuild_menus()
        carb.log_info("omni.kit.mainwindow is now loaded. Menus are enabled")

    def __on_ext_changed(self, ext_id: str, *_):
        if ext_id.startswith("omni.kit.hotkeys.core"):
            self.rebuild_menus()
