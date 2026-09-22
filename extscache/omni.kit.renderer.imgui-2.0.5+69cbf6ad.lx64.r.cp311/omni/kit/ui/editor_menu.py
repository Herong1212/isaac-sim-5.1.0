import carb
import omni.kit.app
from typing import Callable, Union, Tuple

ACTION_TAG_PREFIX = "EMBridge_"
UNKNOWN_EXTENSION = "omni.kit.ui.editor_menu_bridge"

class EditorMenu():

    active_menus = {}
    window_handler = {}
    omni_kit_menu_utils_loaded = False

    def __init__(self):
        import omni.kit.app

        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks = []
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: EditorMenu.set_menu_loaded(True),
                on_disable_fn=lambda _: EditorMenu.set_menu_loaded(False),
                ext_name="omni.kit.menu.utils",
                hook_name="editor menu omni.kit.menu.utils listener",
            )
        )

    def __del__(self):
        self._hooks = []

    @staticmethod
    def print_depreciated_message(func: callable=None):
        log_deprecated = bool((carb.settings.get_settings().get_as_string("/exts/omni.kit.menu.utils/logDeprecated") or "true") == "true")
        if log_deprecated:
            omni.kit.app.log_deprecation(f"omni.kit.ui.get_editor_menu() is deprecated. Please update \"{EditorMenu.get_extension_from_stack(func)}\" to use omni.kit.menu.utils")

    @staticmethod
    def clean_menu_path(path):
        import re

        return re.sub(r"[^\x00-\x7F]+", "", path).lstrip()

    @staticmethod
    def set_menu_loaded(state: bool):
        EditorMenu.omni_kit_menu_utils_loaded = state


    class EditorMenuItem:
        def __init__(self, menu_path):
            self._menu_path = menu_path

        def __del__(self):
            carb.log_info(f"{self._menu_path} went out of scope and is being automatically removed from the menu system")
            EditorMenu.remove_item(self._menu_path)

    @staticmethod
    def get_action_name(menu_path):
        import re

        action = ACTION_TAG_PREFIX + re.sub(r'[^\x00-\x7F]','', menu_path).lower().strip().replace('/', '_').replace(' ', '_').replace('__', '_')
        return(action)

    @staticmethod
    def convert_to_new_menu(menu_path:str, menu_name: Union[str, list], on_click: Callable, toggle: bool, priority: int, value: bool, enabled: bool, original_svg_color: bool, extension_id):
        from omni.kit.menu.utils import MenuItemDescription

        action_name = EditorMenu.get_action_name(menu_path)
        if on_click:
            import omni.kit.actions.core

            omni.kit.actions.core.get_action_registry().register_action(
                extension_id,
                action_name,
                lambda: on_click(menu_path, EditorMenu.toggle_value(menu_path)),
                display_name=action_name,
                description=action_name,
                tag=action_name,
            )

        if isinstance(menu_name, list):
            menu_item = menu_name.pop(-1)
            sub_menu_item = MenuItemDescription(name=menu_item,
                                                enabled=enabled,
                                                ticked=toggle,
                                                ticked_value=value if toggle else None,
                                                onclick_action=(extension_id, action_name),
                                                original_svg_color=original_svg_color)
            sub_menu = [sub_menu_item]
            while(len(menu_name) > 0):
                menu_item = menu_name.pop(-1)
                menu = MenuItemDescription(name=menu_item, sub_menu=sub_menu, original_svg_color=original_svg_color)
                menu.priority=priority
                sub_menu = [menu]
            return menu, sub_menu_item
        else:
            menu = MenuItemDescription(name=menu_name,
                                       enabled=enabled,
                                       ticked=toggle,
                                       ticked_value=value if toggle else None,
                                       onclick_action=(extension_id, action_name),
                                       original_svg_color=original_svg_color)
            menu.priority=priority

        return menu, menu

    @staticmethod
    def split_menu_path(menu_path: str):
        menu_name = None
        menu_parts = menu_path.replace(r"\/", "@TEMPSLASH@").split("/")
        menu_title = menu_parts.pop(0)
        if len(menu_parts) > 1:
            menu_name = menu_parts
        elif menu_parts:
            menu_name = menu_parts[0]

        if menu_name:
            if isinstance(menu_name, list):
                menu_name = [name.replace("@TEMPSLASH@", "\\") for name in menu_name]
            else:
                menu_name = menu_name.replace("@TEMPSLASH@", "\\")
        if menu_title:
            menu_title = menu_title.replace("@TEMPSLASH@", "\\")
        return menu_title, menu_name

    @staticmethod
    def get_extension_from_stack(func: callable=None):
        import traceback
        import omni.kit.app

        if func and hasattr(func, "__module__"):
            ext_name = func.__module__
            if ext_name.endswith(".extension"):
                return ext_name[:-10]
            # its something like "functools" to find name via stack frames

        def is_extension(extension_id, packages):
            for package in packages:
                if package['name'] == extension_id:
                    return True
            return False

        manager = omni.kit.app.get_app().get_extension_manager()
        packages = manager.get_extension_packages()
        # get paths of frames
        frames = [f.filename.replace("\\", "/") for f in reversed(traceback.extract_stack()) if not any(i in f.filename for i in [
                "/kernel/",
                "::startup()",
                "omni.kit.renderer.imgui/omni/kit/ui/editor_menu.py"])]
        for frame in frames:
            # split path into parts & check if any are extensions
            parts = [p for p in reversed(frame.split("/")) if "." in p]
            for part in parts:
                # remove version info from extension name
                part_nover = part.split("-", 1)[0]
                if is_extension(part_nover, packages):
                    return part_nover

        return UNKNOWN_EXTENSION

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def add_item(menu_path: str, on_click: Callable=None, toggle: bool=False, priority: int=0, value: bool=False, enabled: bool=True, original_svg_color: bool=False, auto_release=True):
        EditorMenu.print_depreciated_message(on_click)
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for add_item({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return

        import omni.kit.menu.utils

        extension_id = EditorMenu.get_extension_from_stack(on_click)
        menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
        menu, menuitem = EditorMenu.convert_to_new_menu(menu_path, menu_name, on_click, toggle, priority, value, enabled, original_svg_color, extension_id)
        EditorMenu.active_menus[menu_path] = (menu, menuitem)
        omni.kit.menu.utils.add_menu_items([menu], menu_title)

        # disabled for fastShutdown as auto-release causes exceptions on shutdown, so editor_menus may leak as most are not removed
        if auto_release:
            return EditorMenu.EditorMenuItem(menu_path)

        return menu_path

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def set_on_click(menu_path: str, on_click: Callable=None):
        EditorMenu.print_depreciated_message(on_click)
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for set_on_click({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return

        import omni.kit.menu.utils

        extension_id = EditorMenu.get_extension_from_stack(on_click)
        action_name = EditorMenu.get_action_name(menu_path)
        if menu_path in EditorMenu.active_menus:
            import omni.kit.actions.core

            omni.kit.actions.core.get_action_registry().deregister_action(
                extension_id,
                action_name
            )

            if on_click:
                omni.kit.actions.core.get_action_registry().register_action(
                    extension_id,
                    action_name,
                    lambda: on_click(menu_path, EditorMenu.toggle_value(menu_path)),
                    display_name=action_name,
                    description=action_name,
                    tag=action_name,
                )

            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            omni.kit.menu.utils.remove_menu_items([menu], menu_title)
            menuitem.onclick_action = None
            if on_click:
                menuitem.onclick_action=(extension_id, action_name)
            omni.kit.menu.utils.add_menu_items([menu], menu_title)
            return None
        carb.log_warn(f"set_on_click menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    def remove_item(menu_path: str):
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for remove_item({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return

        import omni.kit.menu.utils
        import omni.kit.actions.core

        extension_id = EditorMenu.get_extension_from_stack()
        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            omni.kit.menu.utils.remove_menu_items([menu], menu_title)
            del EditorMenu.active_menus[menu_path]
            omni.kit.actions.core.get_action_registry().deregister_action(
                extension_id,
                EditorMenu.get_action_name(menu_path)
            )
            return None

        carb.log_warn(f"remove_item menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    def set_priority(menu_path: str, priority: int):
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for set_priority({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return

        import omni.kit.menu.utils

        menu_title_id, menu_name = EditorMenu.split_menu_path(menu_path)
        if menu_title_id and not menu_name:
            for menu_id in EditorMenu.active_menus:
                menu_title, menu_name = EditorMenu.split_menu_path(menu_id)
                if menu_title == menu_title_id:
                    menu, menuitem = EditorMenu.active_menus[menu_id]
                    omni.kit.menu.utils.remove_menu_items([menu], menu_title)
                    omni.kit.menu.utils.add_menu_items([menu], menu_title, priority)
            return

        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            omni.kit.menu.utils.remove_menu_items([menu], menu_title)
            menuitem.priority = priority
            omni.kit.menu.utils.add_menu_items([menu], menu_title)
            return
        carb.log_warn(f"set_priority menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def set_enabled(menu_path: str, enabled: bool):
        EditorMenu.print_depreciated_message()
        if not EditorMenu.omni_kit_menu_utils_loaded:
            return None

        import omni.kit.menu.utils

        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            menuitem.enabled = enabled
            return None
        carb.log_warn(f"set_enabled menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def set_hotkey(menu_path: str, modifier: int, key: int):
        EditorMenu.print_depreciated_message()
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for set_hotkey({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return None

        import omni.kit.menu.utils

        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            omni.kit.menu.utils.remove_menu_items([menu], menu_title)
            menuitem.set_hotkey((modifier, key))
            omni.kit.menu.utils.add_menu_items([menu], menu_title)
            return None
        carb.log_warn(f"set_hotkey menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def set_value(menu_path: str, value: bool):
        EditorMenu.print_depreciated_message()
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for set_value({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return None

        import omni.kit.menu.utils

        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            if menuitem.ticked_value != value:
                menuitem.ticked_value = value
                omni.kit.menu.utils.refresh_menu_items(menu_title)
            return None
        carb.log_warn(f"set_value menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def get_value(menu_path: str):
        EditorMenu.print_depreciated_message()
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for get_value({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return None

        if menu_path in EditorMenu.active_menus:
            menu, menuitem = EditorMenu.active_menus[menu_path]
            return menuitem.ticked_value
        carb.log_warn(f"get_value menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def toggle_value(menu_path: str):
        EditorMenu.print_depreciated_message()
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for toggle_value({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return None

        import omni.kit.menu.utils

        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            menuitem.ticked_value = not menuitem.ticked_value
            omni.kit.menu.utils.refresh_menu_items(menu_title)
            return menuitem.ticked_value
        carb.log_warn(f"toggle_value menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def has_item(menu_path: str):
        EditorMenu.print_depreciated_message()
        return (menu_path in EditorMenu.active_menus)

    @staticmethod
    def set_on_right_click(menu_path: str, on_click: Callable=None):
        carb.log_warn(f"EditorMenu.set_on_right_click(menu_path='{EditorMenu.clean_menu_path(menu_path)}', on_click={on_click}) not supported")
        return None

    @staticmethod
    def set_action(menu_path: str, action_mapping_path: str, action_name: str):
        carb.log_warn(f"EditorMenu.set_action(menu_path='{EditorMenu.clean_menu_path(menu_path)}', action_mapping_path='{action_mapping_path}', action_name='{action_name}') not supported")
        return None

    @staticmethod
    @omni.kit.app.deprecated("use omni.kit.menu.utils instead")
    def add_action_to_menu(
        menu_path: str,
        on_action: Callable,
        action_name: str = None,
        default_hotkey: Tuple[int, int] = None,
        on_rmb_click: Callable = None,
    ) -> None:
        EditorMenu.print_depreciated_message(on_action)
        if not EditorMenu.omni_kit_menu_utils_loaded:
            carb.log_warn(f"omni.kit.menu.utils not loaded for add_action_to_menu({EditorMenu.clean_menu_path(menu_path)}) - Extension needs dependency to omni.kit.menu.utils")
            return None

        import omni.kit.menu.utils
        from omni.kit.menu.utils import MenuActionControl


        if on_rmb_click:
            carb.log_warn(f"add_action_to_menu {EditorMenu.clean_menu_path(menu_path)} on_rmb_click not supported")

        extension_id = EditorMenu.get_extension_from_stack(on_action)
        if menu_path in EditorMenu.active_menus:
            menu_title, menu_name = EditorMenu.split_menu_path(menu_path)
            menu, menuitem = EditorMenu.active_menus[menu_path]
            omni.kit.menu.utils.remove_menu_items([menu], menu_title)

            action_name = EditorMenu.get_action_name(menu_path)
            if on_action:
                import omni.kit.actions.core

                omni.kit.actions.core.get_action_registry().deregister_action(
                    extension_id,
                    action_name
                )

                omni.kit.actions.core.get_action_registry().register_action(
                    extension_id,
                    action_name,
                    on_action,
                    display_name=action_name,
                    description=action_name,
                    tag=action_name,
                )

            menuitem.onclick_action=(extension_id, action_name)
            menuitem.set_hotkey(default_hotkey)
            omni.kit.menu.utils.add_menu_items([menu], menu_title)
            return None
        carb.log_warn(f"add_action_to_menu menu {EditorMenu.clean_menu_path(menu_path)} not found")
        return None
