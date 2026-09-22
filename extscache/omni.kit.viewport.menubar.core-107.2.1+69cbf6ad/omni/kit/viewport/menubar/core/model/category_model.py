from typing import Callable, List, Optional

import omni.ui as ui

from .setting_model import SettingModel

__all__ = ["CategoryStatus", "BaseCategoryItem", "CategoryStateItem", "CategoryCustomItem", "CategoryCollectionItem", "SimpleCategoryModel"]


class CategoryStatus:
    """Status for a category menu"""

    EMPTY = "Category.None"
    """None of child items selected"""

    ALL = "Category.All"
    """All child items selected"""

    MIXED = "Category.Mixed"
    """Part of child items selected"""


class BaseCategoryItem(ui.AbstractItem):
    """
    Base category item.
    """
    def __init__(self, text: str):
        """
        Constructor.

        Args:
            text (str): Item text.
        """
        self.text = text
        super().__init__()


class CategoryStateItem(BaseCategoryItem):
    """A data item for category state (checked/unchecked)"""
    def __init__(self, text: str, value_model: ui.SimpleBoolModel = None, setting_path: Optional[str] = None, hotkey_text: str = "", show_hotkey_placeholder: bool = False):
        """
        Constructor.

        Args:
            text (str): Item text.
        Keyword Args:
            value_model (ui.SimpleBoolModel): Value model for item state, defaults to None.
            setting_path (str): Setting path for item state, defaults to None.
            hotkey_text (str): Hotkey text show in menu item, defaults to "".
            show_hotkey_placeholder (bool): Show placeholder for hotkey text, defaults to False. Used to align with other menu items which have hotkeys.
        """
        super().__init__(text)
        if value_model:
            self.value_model = value_model
        elif setting_path:
            self.value_model = SettingModel(setting_path)
        else:
            self.value_model = ui.SimpleBoolModel()
        self.hotkey_text = hotkey_text
        self.show_hotkey_placeholder = show_hotkey_placeholder

    @property
    def checked(self) -> bool:
        """Item checked state"""
        return self.value_model.as_bool

    @checked.setter
    def checked(self, value: bool) -> None:
        self.value_model.set_value(value)


class CategoryCustomItem(BaseCategoryItem):
    """A data item for user-defined category."""
    def __init__(self, text: str, build_fn: Callable[[None], None]):
        """
        Constructor.

        Args:
            text (str): Item text.

        Keyword Args:
            build_fn (Callable[[None], None]): Callback function to create menu item.
        """
        super().__init__(text)
        self.build_fn = build_fn


class CategoryCollectionItem(BaseCategoryItem):
    """Collection category item. It could includes a set of other category items.

    This item has 3 different states:
        CategoryStatus.ALL: All child items checked.
        CategoryStatus.EMPTY: None child items checked.
        CategoryStatus.MIXED: Some child items checked while others not.
    """
    def __init__(self, text: str, items: Optional[List[BaseCategoryItem]] = None, shown_changed_fn: Callable = None):
        """
        Constructor.

        Args:
            text (str): Item text.

        Keyword Args:
            items (Optional[List[BaseCategoryItem]]): List of child items, defaults to None.
            shown_changed_fn (Callable): Callback when item visibility changed, defaults to None.
        """
        super().__init__(text)
        self.children: List[CategoryStateItem] = []
        self._children_subs = []
        self.status_model = ui.SimpleStringModel(CategoryStatus.EMPTY)

        if items:
            for item in items:
                self.add_item(item)

        self.shown_changed_fn = shown_changed_fn

        self._on_child_changed(None)

        self._status_sub = self.status_model.subscribe_value_changed_fn(self._on_status_changed)

    def destroy(self) -> None:
        """Release resources"""
        for sub in self._children_subs:  # noqa: PLW0612
            sub = None  # noqa: F841
        self._status_sub = None

    def add_item(self, item: BaseCategoryItem):
        """
        Append child item.

        Args:
            item (BaseCategoryItem): Item to add as child.
        """
        self.children.append(item)
        if isinstance(item, CategoryStateItem):
            self._children_subs.append(item.value_model.subscribe_value_changed_fn(self._on_child_changed))
        elif isinstance(item, CategoryCollectionItem):
            self._children_subs.append(item.status_model.subscribe_value_changed_fn(self._on_child_changed))
        self._on_child_changed(None)

    @property
    def status(self) -> CategoryStatus:
        """Category status"""
        return self.status_model.as_string

    @status.setter
    def status(self, value: CategoryStatus) -> None:
        if self.status == value:
            return
        self.status_model.set_value(value)

    def _on_status_changed(self, model: ui.SimpleStringModel):
        # Update children status
        if self.status == CategoryStatus.EMPTY:
            for item in self.children:
                if isinstance(item, CategoryStateItem):
                    item.checked = False
                elif isinstance(item, CategoryCollectionItem):
                    item.status = CategoryStatus.EMPTY
        elif self.status == CategoryStatus.ALL:
            for item in self.children:
                if isinstance(item, CategoryStateItem):
                    item.checked = True
                elif isinstance(item, CategoryCollectionItem):
                    item.status = CategoryStatus.ALL

    def _on_child_changed(self, model: ui.SimpleStringModel):
        # Child changed, update status
        part_selected = False
        num_selected = 0
        num_children = len(self.children)

        for item in self.children:
            if isinstance(item, CategoryStateItem):
                if item.checked:
                    num_selected += 1
            elif isinstance(item, CategoryCollectionItem):
                if item.status == CategoryStatus.MIXED:
                    part_selected = True
                elif item.status == CategoryStatus.ALL:
                    num_selected += 1
            else:
                num_children -= 1  # unsupported item

        if num_children > 0 and num_selected == num_children:
            status = CategoryStatus.ALL
        elif part_selected or 0 < num_selected < num_children:
            status = CategoryStatus.MIXED
        else:
            status = CategoryStatus.EMPTY

        if status != self.status:
            self.status = status


class SimpleCategoryModel(ui.AbstractItemModel):
    """A data model for category items"""
    def __init__(self, text: str, items: Optional[List[BaseCategoryItem]] = None, root: CategoryCollectionItem = None):
        """
        Constructor.

        Args:
            text (str): Item text.

        Keyword Args:
            items (Optional[List[BaseCategoryItem]]): Category items, defaults to None.
            root (CategoryCollectionItem): Root category collection item, defaults to None.
        """
        self._root = root if root else CategoryCollectionItem(text)
        if items:
            for item in items:
                self._root.add_item(item)
        super().__init__()

    def destroy(self) -> None:
        """Release resources"""
        self._root.destroy()

    def get_item_children(self, item: Optional[BaseCategoryItem] = None) -> List[BaseCategoryItem]:
        """
        Returns all the children when the widget asks it.

        Keyword Args:
            item (Optional[BaseCategoryItem]): Parent item, defaults to None means to retrieve root items.
        """
        if item is None:
            return [self._root]
        if isinstance(item, CategoryCollectionItem):
            return item.children
        if isinstance(item, CategoryStateItem):
            return []
        return []

    def add_item(self, item: BaseCategoryItem, parent: BaseCategoryItem = None):
        """
        Add a new category item.

        Args:
            item (BaseCategoryItem): Category item to add.

        Keyword Args:
            parent (BaseCategoryItem): Parent category item, default to None to add as root.
        """
        if parent is None:
            self._root.add_item(item)
        else:
            parent.add_item(item)
