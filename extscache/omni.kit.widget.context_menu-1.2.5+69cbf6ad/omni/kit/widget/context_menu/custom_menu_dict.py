import copy
import carb
import carb.events
from typing import Callable, List, Union, Tuple
from .singleton import Singleton

class ContextMenuEventType:
    """
    Event sent when menus are added or removed
    """
    ADDED = 0
    """New menu entry is added"""
    REMOVED = 1
    """Menu entry is removed"""


@Singleton
class _CustomMenuDict:
    """
    The singleton object that holds custom context menu which is private
    """

    def __init__(self) -> None:
        self.__custom_menu_dict = {}
        self.__counter = 0
        self.__event_stream = carb.events.get_events_interface().create_event_stream()

    def add_menu(self, menu: Union[str, list], index: str, extension_id: str) -> int:
        menu_id = self.__counter
        if not index in self.__custom_menu_dict:
            self.__custom_menu_dict[index] = {}
        if not extension_id in self.__custom_menu_dict[index]:
            self.__custom_menu_dict[index][extension_id] = {}

        self.__custom_menu_dict[index][extension_id][menu_id] = menu
        self.__counter += 1
        self.__event_stream.dispatch(ContextMenuEventType.ADDED, payload={"index": index, "extension_id": extension_id})
        return menu_id

    def remove_menu(self, menu_id: int, index: str, extension_id: str) -> None:
        # NOTE: removing a menu dictionary that does not exist is not valid
        if (
            index in self.__custom_menu_dict
            and extension_id in self.__custom_menu_dict[index]
            and menu_id in self.__custom_menu_dict[index][extension_id]
        ):
            del self.__custom_menu_dict[index][extension_id][menu_id]
            self.__event_stream.dispatch(ContextMenuEventType.REMOVED, payload={"index": index, "extension_id": extension_id})
            return
        carb.log_error(f"remove_menu index:{index} extension_id:{extension_id} doesn't exist.") # pragma: no cover

    def get_menu_dict(self, index: str, extension_id: str) -> List[dict]:
        # NOTE: getting a menu dictionary that does not exist is valid and will return empty list
        if index in self.__custom_menu_dict and extension_id in self.__custom_menu_dict[index]:
            return self._merge_submenus(list(self.__custom_menu_dict[index][extension_id].values()))
        return []

    ## merge submenus ##

    def _get_duplicate_item(self, compare_item: dict, item_list: list) -> bool:
        for item in item_list:
            if isinstance(compare_item["name"], str) and isinstance(item["name"], str):
                if item["name"] != "" and compare_item["name"] == item["name"]:
                    return item
            elif isinstance(compare_item["name"], dict) and isinstance(item["name"], dict):
                if compare_item["name"].keys() == item["name"].keys():
                    return item
        return None

    def _copy_item(self, item: dict):
        name = item.get("name")
        if name and isinstance(name, dict):
            result = {}
            for k, v in item.items():
                if k == "name":
                    result[k] = {ik: [self._copy_item(child) for child in iv] for ik, iv in v.items()}
                else:
                    result[k] = copy.copy(v)
            return result
        return copy.copy(item)

    def __merge_submenu(self, keys: list, main_item: dict, merge_item: dict) -> dict:
        for key in keys:
            if isinstance(main_item[key], str) and isinstance(merge_item[key], str):
                main_item[key] = main_item[key] + merge_item[key]
            elif isinstance(main_item[key], list) and isinstance(merge_item[key], list):
                for item in merge_item[key]:
                    duplicate_item = self._get_duplicate_item(item, main_item[key])
                    if duplicate_item:
                        dup_item_name = duplicate_item["name"]
                        if (not dup_item_name) or not (hasattr(dup_item_name, "keys")):
                            if dup_item_name != "":
                                carb.log_warn(f"_merge_submenu: failed to merge duplicate item {dup_item_name}")
                        else:
                            duplicate_item["name"] = self.__merge_submenu(
                                dup_item_name.keys(), self._copy_item(dup_item_name), item["name"]
                            )
                    else:
                        main_item[key].append(self._copy_item(item))
        return main_item

    def _merge_submenus(self, main_list: list) -> list:
        """ merge submenus into new dict without changing the original """
        new_list = []
        for item in main_list:
            duplicate_item = self._get_duplicate_item(item, new_list)
            if duplicate_item:
                dup_item_name = duplicate_item["name"]
                if (not dup_item_name) or not (hasattr(dup_item_name, "keys")):
                    if dup_item_name != "":
                        carb.log_warn(f"_merge_submenus: failed to merge duplicate item {dup_item_name}")
                else:
                    duplicate_item["name"] = self.__merge_submenu(
                        dup_item_name.keys(), self._copy_item(dup_item_name), item["name"]
                    )
            else:
                new_list.append(self._copy_item(item))
        return new_list

    def get_event_stream(self):
        return self.__event_stream


def add_menu(menu_dict, index: str = "MENU", extension_id: str = ""):
    """Add custom menu to any context_menu

    Examples
        menu = {"name": "Open in Material Editor", "onclick_fn": open_material}
        # add to all context menus
        self._my_custom_menu = omni.kit.context_menu.add_menu(menu, "MENU", "")
        # add to omni.kit.widget.stage context menu
        self._my_custom_menu = omni.kit.context_menu.add_menu(menu, "MENU", "omni.kit.widget.stage")

    Args:
        menu_dict: a dictionary containing menu settings. See ContextMenuExtension docs for information on values
        index: name of the menu EG. "MENU"
        extension_id: name of the target EG. "" or "omni.kit.widget.stage"

    NOTE: index and extension_id are extension arbitrary values. add_menu(menu, "MENU", "omni.kit.widget.stage") works
          as omni.kit.widget.stage retrieves custom context_menus with get_menu_dict("MENU", "omni.kit.widget.stage")
          Adding a menu to an extension that doesn't support context_menus would have no effect.

    Returns:
        (MenuSubscription): A MenuSubscription, keep a copy of this as the custom menu will be removed when `release()`
          is explicitly called or this is garbage collected.
    """

    class MenuSubscription:
        def __init__(self, menu_id):
            self.__id = menu_id

        def release(self):
            if self.__id is not None:
                _CustomMenuDict().remove_menu(self.__id, index, extension_id)
                self.__id = None

        def __del__(self):
            self.release()

    menu_id = _CustomMenuDict().add_menu(menu_dict, index, extension_id)
    return MenuSubscription(menu_id)


def get_menu_dict(index: str = "MENU", extension_id: str = "") -> List[dict]:
    """Get custom menus

    see add_menu for dictionary info

    Args:
        index (str): name of the menu
        extension_id (str): name of the target

    Returns:
        (list): a list of dictionaries containing custom menu settings. See ContextMenuExtension docs for information on values
    """
    return _CustomMenuDict().get_menu_dict(index, extension_id)

def merge_menus(menu_list: list) -> List[dict]:
    """Merge custom menus

    Args:
        menu_list (list): list of dictionaries

    Returns:
        (list): a list of dictionaries containing custom menu settings. See ContextMenuExtension docs for information on values
    """
    return _CustomMenuDict()._merge_submenus(menu_list)


def get_menu_event_stream():
    """
    Gets menu event stream.

    Returns:
        (IEventStream): Event stream.
    """
    return _CustomMenuDict().get_event_stream()
