# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["AbstractViewportMenuItem", "AbstractViewportMenubarItem", "ViewportMenuModel", "register", "deregister", "get_items", "get_item", "push_to_scope", "pop_from_scope", "destroy"]

import abc
import weakref
from collections import defaultdict
from typing import Dict, List, Optional, Union

import carb
import omni.ui as ui

from .model.setting_model import SettingModelWithDefaultPath
from .style import DEFAULT_MENUBAR_NAME


class MenuDisplayStatus:
    """Menu item display status"""
    MIN = 0
    """Show menu item in min (for example, icon only without label)"""

    LABEL = 1
    """Show menu item with label"""

    EXPAND = 2
    """Show menu item with expand items"""

    MAX = 3
    """Show menu item with all elements"""


def singleton(class_):
    """A singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


class AbstractViewportMenuItem(ui.AbstractItem):
    """Represent a viewport menu item."""
    def __init__(
        self,
        name: str = "",
        visible_setting_path: Optional[str] = None,
        order_setting_path: Optional[str] = None,
        expand_setting_path: Optional[str] = None
    ):
        """
        Construct a viewport menu item.

        Keyword Args:
            name (str): Menu item name, defaults to "" to use self.
            visible_setting_path (Optional[str]): Setting path for visibility, defaults to None.
            order_setting_path (Optional[str]): Setting path for order, defaults to None. Order < 0 means in left of menubar. Order > 0 means in right of menubar.
            expand_setting_path (Optional[str]): Setting path for expand state, defaults to None.
        """
        self._name = name or str(self)
        if visible_setting_path:
            self.visible_model = SettingModelWithDefaultPath(visible_setting_path)
        else:
            self.visible_model = ui.SimpleBoolModel(True)

        if order_setting_path:
            self.order_model = SettingModelWithDefaultPath(order_setting_path)
        else:
            self.order_model = ui.SimpleIntModel(-1)

        if expand_setting_path:
            self.expand_model = SettingModelWithDefaultPath(expand_setting_path)
        else:
            self.expand_model = None

        # Put it to registry
        self._parent = register(self)

        self.clip_level = MenuDisplayStatus.MIN

        super().__init__()

    def destroy(self) -> None:
        """Remove from viewport menubar registry"""
        deregister(self)

    @property
    def name(self):
        """Item name"""
        return self._name

    @property
    def parent(self):
        """Parent item"""
        return self._parent

    def get_display_status(self, factory_args: dict) -> MenuDisplayStatus:
        """
        Menu item display status.

        Args:
            factory_args (dict): Argument related to viewport for this menu bar item.
        """
        return MenuDisplayStatus.MIN

    def get_require_size(self, factory_args: dict, expand: bool = False) -> float:
        """
        Required size for menu item.

        Args:
            factory_args (dict): Argument related to viewport for this menu bar item.

        keyword Args:
            expand (bool): True for menu item to expand. False for menu item in current display status.
        """
        return 0

    def expand(self, factory_args: dict) -> None:
        """
        Expand display of menu item.

        Args:
            factory_args (dict): Argument related to viewport for this menu bar item.
        """
        return

    def can_contract(self, factory_args: dict) -> bool:
        """
        If menu item could contract to smaller size, defaults to False.

        Args:
            factory_args (dict): Argument related to viewport for this menu bar item.
        """
        return False

    def contract(self, factory_args: dict) -> None:
        """
        Contract menu item to smaller size.

        Args:
            factory_args (dict): Argument related to viewport for this menu bar item.
        """
        return


class AbstractViewportMenubarItem(AbstractViewportMenuItem):
    """
    Represent a menubar.
    """
    @abc.abstractmethod
    def build_fn(self, menu_items: List[AbstractViewportMenuItem], factory_args: Dict) -> None:
        """
        Build menubar.

        Args:
            menu_items (List[AbstractViewportMenuItem]): Menu items to display on the menubar
            factory_args (dict): Argument related to viewport for this menu bar item.
        """
        return


@singleton
class ViewportMenuModel(ui.AbstractItemModel):
    def destroy(self):
        pass

    """General functions of ui.AbstractItemMode"""  # noqa PLW0105

    def get_item_children(self, parent_item: Union[AbstractViewportMenuItem, AbstractViewportMenubarItem, None] = None) -> List[AbstractViewportMenuItem]:
        if parent_item is None:
            # Retreive all menubar items
            items = get_items()
        elif isinstance(parent_item, AbstractViewportMenubarItem):
            # Retreive menu items for a menubar
            items = get_items(parent_item.name)
        else:
            items = []

        if items:
            items.sort(key=lambda item: item.order_model.as_int)
            return items
        return []

    def get_item_value_model_count(self, item: AbstractViewportMenuItem):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item: AbstractViewportMenuItem, column_id: int):
        if item and column_id == 0:
            return ui.SimpleStringModel(item.name)
        return ui.SimpleStringModel("")

    """Enable drag and drop"""  # noqa PLW0105

    def get_drag_mime_data(self, item):
        """Returns Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere"""
        # As we don't do Drag and Drop to the operating system, we return the string.
        return item.name

    def drop_accepted(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called to highlight target when drag and drop."""
        return isinstance(source, AbstractViewportMenuItem) and target_item

    def drop(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called when dropping something to the item."""
        if isinstance(source, AbstractViewportMenuItem):
            self._drop_item(target_item, source, drop_location)

    def _drop_item(self, target: AbstractViewportMenuItem, source: AbstractViewportMenuItem, drop_location=-1):
        items = self.get_item_children()
        source_index = items.index(source)
        target_index = items.index(target)

        if source_index > target_index:
            # Drop forward, source in front of target
            if target.order_model.as_int < 0:
                # Left, make order of source smaller than target
                source.order_model.set_value(target.order_model.as_int - 1)
                # Make sure other items in front of source has smaller order
                last = source
                for item in reversed(items[0 : target_index]):
                    if item.order_model.as_int >= last.order_model.as_int:
                        item.order_model.set_value(last.order_model.as_int - 1)
                        last = item
                    else:
                        break
            else:
                # Right, replace order of source with target
                source.order_model.set_value(target.order_model.as_int)
                # Make sure other items behind source (include target) bas bigger order
                last = source
                for item in items[target_index:]:
                    if item.order_model.as_int <= last.order_model.as_int:
                        item.order_model.set_value(last.order_model.as_int + 1)
                        last = item
                    else:
                        break
        else:
            # Drop backward, source behind of target
            if target.order_model.as_int < 0:
                # Left, replace order of source with target
                source.order_model.set_value(target.order_model.as_int)
                # Make sure items bwtween source and target has smaller order
                last = source
                for item in reversed(items[source_index + 1 : target_index + 1]):
                    if item.order_model.as_int >= last.order_model.as_int:
                        item.order_model.set_value(last.order_model.as_int - 1)
                        break
            else:
                # Right, make order of next items bigger
                source.order_model.set_value(target.order_model.as_int + 1)
                last = source
                for item in items[target_index + 1:]:
                    if item.order_model.as_int <= last.order_model.as_int:
                        item.order_model.set_value(last.order_model.as_int + 1)
                        last = item
                    else:
                        break

        self._item_changed(source)
        self._item_changed(None)


_parentname_to_name = defaultdict(list)
_name_to_menuitem: Dict[str, AbstractViewportMenuItem] = {}
_scope_stack: List[AbstractViewportMenuItem] = []


def register(menu_item: Union[AbstractViewportMenuItem, AbstractViewportMenubarItem]) -> "weakref.ProxyType[AbstractViewportMenuItem]":
    """
    Register the item in the storage. It keeps the item, so to destroy it,
    it's necessary to use `deregister` or `destroy`.

    It's called in the constructor of `ViewportMenuItem`, so once the item is
    created, it automatically registers here.

    Returns the proxy with the parent, so the child stores it and avoids
    circular reference.
    """
    # Name is the unique identifier
    name = menu_item.name

    # Get parent
    if _scope_stack:
        parent = _scope_stack[-1]
        parent_name = parent.name
    elif isinstance(menu_item, AbstractViewportMenubarItem):
        # For menubar, register to root by default
        parent = None
        parent_name = None
    elif isinstance(menu_item, AbstractViewportMenuItem):
        # For menu item, register to default menubar by default
        parent = get_item(DEFAULT_MENUBAR_NAME)
        parent_name = DEFAULT_MENUBAR_NAME
    else:
        parent = None
        parent_name = None

    carb.log_info(f"register {name}, order: {menu_item.order_model.as_int}, parent: {parent_name}")

    # Save it. We keep the object, it means we need to explicitly delete it when
    # shutdown.
    _parentname_to_name[parent_name].append(name)
    _name_to_menuitem[name] = menu_item

    if parent is None or isinstance(parent, AbstractViewportMenubarItem):
        # Now only care about root menus and menubar items
        ViewportMenuModel()._item_changed(parent)  # noqa PLW0212

    # Return parent proxy to avoid circular references.
    return weakref.proxy(parent) if parent else None


def deregister(menu_item: AbstractViewportMenuItem):
    """Remove item from the storage"""
    name = menu_item.name
    parent, parent_name = None, None
    # parent is weakref.proxy and underlying object may already not exists
    try:  # noqa: SIM105
        if menu_item.parent:
            parent = menu_item.parent
            parent_name = parent.name
    except ReferenceError:
        pass

    carb.log_info(f"deregister {name} from {parent_name}")

    if parent_name in _parentname_to_name and name in _parentname_to_name[parent_name]:
        _parentname_to_name[parent_name].remove(name)
    if name in _parentname_to_name:
        _parentname_to_name.pop(name)
    if name in _name_to_menuitem:
        _name_to_menuitem.pop(name)
    if parent is None or isinstance(parent, AbstractViewportMenubarItem):
        # Now only care about root menus and items in root menus
        # Here parent maybe a weakproxy, always use None instead
        ViewportMenuModel()._item_changed(None)  # noqa PLW0212


def get_items(parent_name: Optional[str] = None) -> List[AbstractViewportMenuItem]:
    """Get the list of items by parent name"""
    return [_name_to_menuitem[name] for name in _parentname_to_name[parent_name]]


def get_item(name: Optional[str] = None) -> AbstractViewportMenuItem:
    """Get the items by name"""
    return _name_to_menuitem.get(name, None)


def push_to_scope(menu_container: AbstractViewportMenuItem): # noqa:m F821
    """
    Called from `__enter__` when using `with` statement. Puts the container
    to the stack so the children know their parents.
    """
    _scope_stack.append(menu_container)


def pop_from_scope():
    """Called from `__exit__` when using `with` statement."""
    _scope_stack.pop()


def destroy():
    """Clear items"""
    _parentname_to_name.clear()
    _name_to_menuitem.clear()
    _scope_stack.clear()
