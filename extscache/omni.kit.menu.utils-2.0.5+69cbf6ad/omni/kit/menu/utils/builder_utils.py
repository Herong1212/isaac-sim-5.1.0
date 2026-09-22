"""
Definition of MenuItemDescription and other menu classes

"""

from typing import Callable, Optional, Tuple, Union

import carb
import omni.kit.app
from omni.kit.menu.core import has_delegate_func  # noqa # pylint: disable=unused-import


def get_menu_name(menu_entry):
    """
    gets menu name from menu_entry.name_fn or menu_entry.name
    """
    if menu_entry.name_fn:
        try:
            return f"{menu_entry.name_fn()}"
        except Exception as exc:  # pylint: disable=broad-except
            carb.log_warn(f"get_menu_name error:{str(exc)}")
    return f"{menu_entry.name}"


def get_action_path(action_prefix: str, menu_entry_name: str):
    """
    converts menu path into internal path
    """
    if not menu_entry_name:
        return action_prefix.replace(" ", "_").replace("/", "_").replace(".", "")
    return f"{action_prefix}/{menu_entry_name}".replace(" ", "_").replace("/", "_").replace(".", "")


def create_prebuild_entry(prebuilt_menus: dict, prefix_name: str, action_prefix: str):
    """
    internal function that creates a entry in prebuilt_menus dictionary
    """
    if action_prefix not in prebuilt_menus:
        # prefix_name cannot be "" as creating submenus with "" causes problems
        prebuilt_menus[action_prefix] = {}
        prebuilt_menus[action_prefix]["items"] = []
        prebuilt_menus[action_prefix]["prefix_name"] = prefix_name if prefix_name else "Empty"
        prebuilt_menus[action_prefix]["remapped"] = []
        prebuilt_menus[action_prefix]["action_prefix"] = action_prefix


class PrebuiltItemOrder:
    """
    Internal flags used by layout for item ordering
    """

    UNORDERED = 0x7FFFFFFF
    LAYOUT_ORDERED = 0x00000000
    LAYOUT_SUBMENU_SORTED = 0x00001000
    LAYOUT_ITEM_SORTED = 0x00002000


class MenuAlignment:
    """
    Menu alignment setting. Either left or right
    """

    DEFAULT = 0
    RIGHT = 1


class LayoutSourceSearch:
    """
    Controls how layouts search for the menu item paths, either everywhere or just in the local menu group
    """

    EVERYWHERE = 0
    LOCAL_ONLY = 1


class MenuItemDescription:
    """
    Class for creation of menu items

    - "name" is name shown on menu. (if name is "" then a menu spacer is added. Can be combined with show_fn)
    - "glyph" is icon shown on menu, full paths are allowed
    - "header" is None or string value & will add separator above item
    - "appear_after" is name of menu item to insert after. Used for appending menus, can be a list or string
    - "enabled" is True/False, True when item enabled
    - "ticked" menu item is ticked when True
    - "ticked_fn" function or list of functions used to decide if menu item is ticked
    - "ticked_value" is value used to decide if menu item is ticked
    - "radio_group" is name of group of ticked-radio buttons, setting one in group will clear the others
    - "sub_menu" is sub menu to this menu
    - "hotkey" is hotkey values for menu item
    - "name_fn" is function to get menu name
    - "show_fn" function or list of functions used to decide if menu item is shown. All functions must return True to show
    - "enable_fn" function or list of functions used to decide if menu item is enabled. All functions must return True to be enabled
    - "onclick_action" action called when user clicks menu item
    - "unclick_action" action called when user release's button on menu item
    - "onclick_fn" function called when user clicks menu item (deprecated)
    - "unclick_fn" function called when user releases click on menu item (deprecated)
    - "onclick_right_fn" function called when user right clicks menu item (deprecated)
    - "original_svg_color" isn't used (deprecated)
    - "user" is user dictionary that is passed to menu. NOTE: values will be added to this dictionary
    - *hotkey_window* is title of window where hotkey to be triggered
    """

    MAX_DEPTH = 16

    def __init__(
        self,
        name: str = "",
        glyph: str = "",
        header: Optional[str] = None,
        appear_after: Union[list, str] = "",
        enabled: bool = True,
        ticked: bool = False,
        ticked_value: Optional[bool] = None,
        radio_group: Optional[str] = "",
        sub_menu=None,
        hotkey: Tuple[int, int] = None,
        name_fn: Callable = None,
        show_fn: Callable = None,
        enable_fn: Callable = None,
        ticked_fn: Callable = None,
        onclick_action: Tuple = None,
        unclick_action: Tuple = None,
        onclick_fn: Callable = None,  # deprecated
        unclick_fn: Callable = None,  # deprecated
        onclick_right_fn: Callable = None,  # deprecated
        original_svg_color: bool = False,  # deprecated - only used for editor_menu
        original_menu_item=None,  # private for hotkey processing
        user=None,
        hotkey_window: Optional[str] = None,
    ):
        self._on_delete_funcs = []
        self._on_hotkey_update_funcs = []
        # don't allow unnamed submenus as causes Menu problems
        if name == "" and sub_menu:
            self.name = "SubMenu"
        else:
            self.name = name
        self.glyph = glyph
        self.header = header
        self.appear_after = appear_after
        self.ticked = bool(ticked or ticked_value is not None or ticked_fn is not None)
        self.ticked_value = ticked_value
        self.radio_group = radio_group
        self.enabled = enabled
        self.sub_menu = sub_menu
        self.name_fn = name_fn
        self.show_fn = show_fn
        self.enable_fn = enable_fn
        self.ticked_fn = ticked_fn
        self.onclick_action = onclick_action
        self.unclick_action = unclick_action
        self.set_hotkey(hotkey)
        self.hotkey_window = hotkey_window
        self.original_menu_item = original_menu_item
        self.user = user.copy() if user else {}

        # Deprecated
        self.original_svg_color = original_svg_color
        self.onclick_fn = onclick_fn
        self.unclick_fn = unclick_fn
        self.onclick_right_fn = onclick_right_fn

        log_deprecated = (
            carb.settings.get_settings().get_as_string("/exts/omni.kit.menu.utils/logDeprecated") or "true"
        ) == "true"
        if log_deprecated and "shown_deprecated_warning" not in self.user:

            def deprecated_msg(fn_name, func):
                if func and getattr(func, "__module__", None):
                    omni.kit.app.log_deprecation(
                        f'Menu item "{name}" from {func.__module__} uses {fn_name} which is deprecated'
                    )
                else:
                    omni.kit.app.log_deprecation(f'Menu item "{name}" uses {fn_name} which is deprecated')

            if onclick_fn or unclick_fn or onclick_right_fn or original_svg_color:
                omni.kit.app.log_deprecation(f"********************* MenuItemDescription {name} *********************")
                self.user["shown_deprecated_warning"] = True
            if onclick_fn:
                deprecated_msg("onclick_fn", onclick_fn)
            if unclick_fn:
                deprecated_msg("unclick_fn", unclick_fn)
            if onclick_right_fn:
                deprecated_msg("onclick_right_fn", onclick_right_fn)
            if original_svg_color:
                deprecated_msg("original_svg_color", None)

    def add_on_delete_func(self, on_delete_fn: callable):
        self._on_delete_funcs.append(on_delete_fn)

    def remove_on_delete_func(self, on_delete_fn: callable):
        try:
            self._on_delete_funcs.remove(on_delete_fn)
        except Exception as exc:  # pylint: disable=broad-except
            carb.log_warn(f"omni.kit.menu.utils remove_on_delete_func failed {str(exc)}")

    def add_on_hotkey_update_func(self, hotkey_update_fn: callable):
        self._on_hotkey_update_funcs.append(hotkey_update_fn)

    def remove_on_hotkey_update_func(self, hotkey_update_fn: callable):
        try:
            self._on_hotkey_update_funcs.remove(hotkey_update_fn)
        except Exception as exc:  # pylint: disable=broad-except
            carb.log_warn(f"omni.kit.menu.utils remove_on_hotkey_update_func failed {str(exc)}")

    def set_hotkey(self, hotkey):
        self.hotkey = None
        self.hotkey_text = ""
        if hotkey:
            self.hotkey = hotkey
            self.hotkey_text = self.get_action_mapping_desc().replace("Keyboard::", "")

        for on_hotkey_update_fn in self._on_hotkey_update_funcs:
            on_hotkey_update_fn(self)

    def get_action_mapping_desc(self):
        if isinstance(self.hotkey, carb.input.GamepadInput):
            return carb.input.get_string_from_action_mapping_desc(self.hotkey)
        return carb.input.get_string_from_action_mapping_desc(self.hotkey[1], self.hotkey[0])

    def has_action(self):
        return bool(self.onclick_fn or self.onclick_action or self.unclick_fn or self.unclick_action)

    def destroy(self, recurse: bool = True):
        if recurse and self.sub_menu:
            for menu in self.sub_menu:
                menu.destroy()

        self.original_menu_item = None

        if hasattr(self, "_on_delete_funcs"):
            for on_delete_fn in self._on_delete_funcs:
                on_delete_fn(self)
            del self._on_delete_funcs

        if hasattr(self, "_on_hotkey_update_funcs"):
            del self._on_hotkey_update_funcs

    def __del__(self):
        self.destroy(recurse=False)

    def __repr__(self):
        if self.user:
            if self.sub_menu:
                return f"<{self.__class__.__name__} name:'{self.name}' user:{self.user} sub_menu:{repr(self.sub_menu)}>"
            return f"<{self.__class__.__name__} name:'{self.name}' user:{self.user}>"

        if self.sub_menu:
            return f"<{self.__class__.__name__} name:'{self.name}' sub_menu:{repr(self.sub_menu)}>"
        return f"<{self.__class__.__name__} name:'{self.name}'>"

    def __copy__(self):
        # as hotkeys are removed on copied item delete, hotkeys are accessed via original_menu_item as these are not deleted until the menu is removed
        def get_original(item):
            original = item.original_menu_item
            if original:
                while original.original_menu_item and original.original_menu_item.original_menu_item:
                    original = original.original_menu_item
                return original
            return item

        sub_menu = self.sub_menu
        if sub_menu:

            def copy_sub_menu(sub_menu, new_sub_menu, max_depth=MenuItemDescription.MAX_DEPTH):
                if max_depth == 0:
                    carb.log_warn(f"Recursive sub_menu {sub_menu} aborting copy")
                    return

                for sub_item in sub_menu:
                    item = MenuItemDescription(
                        name=sub_item.name,
                        glyph=sub_item.glyph,
                        header=sub_item.header,
                        appear_after=sub_item.appear_after,
                        enabled=sub_item.enabled,
                        ticked=sub_item.ticked,
                        ticked_value=sub_item.ticked_value,
                        radio_group=sub_item.radio_group,
                        sub_menu=None,
                        hotkey=None,
                        name_fn=sub_item.name_fn,
                        show_fn=sub_item.show_fn,
                        enable_fn=sub_item.enable_fn,
                        ticked_fn=sub_item.ticked_fn,
                        onclick_action=sub_item.onclick_action,
                        unclick_action=sub_item.unclick_action,
                        onclick_fn=sub_item.onclick_fn,
                        unclick_fn=sub_item.unclick_fn,
                        onclick_right_fn=sub_item.onclick_right_fn,
                        original_svg_color=sub_item.original_svg_color,
                        original_menu_item=get_original(sub_item),
                        user=sub_item.user,
                    )

                    new_sub_menu.append(item)
                    if sub_item.sub_menu:
                        item.sub_menu = []
                        copy_sub_menu(sub_item.sub_menu, item.sub_menu, max_depth - 1)

            if isinstance(sub_menu, list):
                new_sub_menu = []
                copy_sub_menu(sub_menu, new_sub_menu)
                sub_menu = new_sub_menu

        return MenuItemDescription(
            name=self.name,
            glyph=self.glyph,
            header=self.header,
            appear_after=self.appear_after,
            enabled=self.enabled,
            ticked=self.ticked,
            ticked_value=self.ticked_value,
            radio_group=self.radio_group,
            sub_menu=sub_menu,
            hotkey=None,
            name_fn=self.name_fn,
            show_fn=self.show_fn,
            enable_fn=self.enable_fn,
            ticked_fn=self.ticked_fn,
            onclick_action=self.onclick_action,
            unclick_action=self.unclick_action,
            onclick_fn=self.onclick_fn,
            unclick_fn=self.unclick_fn,
            onclick_right_fn=self.onclick_right_fn,
            original_svg_color=self.original_svg_color,
            original_menu_item=get_original(self),
            user=self.user,
        )

    def json_enc(self):
        values = {
            "name": self.name,
            "glyph": self.glyph,
            "header": self.header,
            "enabled": self.enabled,
            "sub_menu": self.sub_menu,
            "hotkey": self.hotkey,
            "name_fn": self.name_fn,
            "show_fn": self.show_fn,
            "enable_fn": self.enable_fn,
            "onclick_action": self.onclick_action,
            "unclick_action": self.unclick_action,
            "onclick_fn": self.onclick_fn,
            "unclick_fn": self.unclick_fn,
            "onclick_right_fn": self.onclick_right_fn,
            "original_svg_color": self.original_svg_color,
            "user": self.user,
        }

        if self.ticked:
            values["ticked"] = self.ticked
            values["ticked_value"] = self.ticked_value
            values["ticked_fn"] = self.ticked_fn
            values["radio_group"] = self.radio_group

        if self.appear_after:
            values["appear_after"] = self.appear_after

        return {k: v for k, v in values.items() if v is not None}

    # Make a dict like interface for MenuItemDescription so it can be used as an entry for omni.kit.context_menu
    # overrides [] and get for read-only access
    def __getitem__(self, key, default_value=None):
        return getattr(self, key, default_value)

    def __contains__(self, key):
        return self.__getitem__(key) is not None

    def get(self, key, default_value=None):
        return getattr(self, key, default_value)
