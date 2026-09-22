from typing import Callable, Dict, Optional

from omni import ui
from ..model.category_model import SimpleCategoryModel, CategoryStateItem, CategoryCollectionItem, CategoryCustomItem
from ..delegate.category_menu_delegate import CategoryMenuDelegate, CategoryStatus
from ..delegate.viewport_menu_delegate import ViewportMenuDelegate
from ..utils import menu_is_tearable
from .selectable_menu_item import SelectableMenuItem


__all__ = ["CategoryMenuCollection"]


class CategoryMenuCollection(ui.MenuItemCollection):
    """A menu collection for category items."""
    def __init__(
        self,
        model: SimpleCategoryModel,
        item: CategoryCollectionItem,
        identifier: Optional[str] = None,
        trigger_fns: Optional[Dict[str, Callable]] = None,
    ):
        """
        Constructor:

        Args:
            model (SimpleCategoryModel): Category data model.
            item (CategoryCollectionItem): Root category item in category model.

        Keyword Args:
            identifier (Optional[str]): Menu collection identifier, defaults to None.
            trigger_fns (Optional[Dict[str, Callable]]): Callbacks when menu item clicked, defaults to None.
        """

        # XXX: trigger_fns is a workaround for omni.kit.viewport.menubar.display
        # do not expect it will always exists!
        self.__trigger_fns: Optional[Dict[str, Callable]] = trigger_fns
        self.__identifier = identifier

        self._model = model
        self._item = item
        self._delegate = CategoryMenuDelegate(item.status, icon_clicked_fn=self._on_icon_clicked)
        self._sub = self._item.status_model.subscribe_value_changed_fn(self._on_status_changed)
        super().__init__(item.text, delegate=self._delegate,
                         on_build_fn=self._build_menu_items,
                         hide_on_click=False,
                         tearable=menu_is_tearable(identifier),
                         shown_changed_fn=item.shown_changed_fn)

    def destroy(self) -> None:
        """Release resources."""
        self._sub = None
        if self._item:
            self._item.destroy()
            self._item = None
        self.__trigger_fns = None
        super().destroy()

    def _build_menu_items(self):
        custom_items = []

        def attach_trigger_fn(item, name: str):
            if self.__trigger_fns and item and name:
                # Try to pull a triggered_fn from the ones provided
                trigger_fn = self.__trigger_fns.get(name)
                if trigger_fn:
                    item.set_triggered_fn(trigger_fn)

        show_separator = False
        for item in self._model.get_item_children(self._item):
            name: str = getattr(item, "text", "")
            if isinstance(item, CategoryStateItem):
                item = SelectableMenuItem(item.text, model=item.value_model, delegate=ViewportMenuDelegate(show_hotkey_placeholder=item.show_hotkey_placeholder), hotkey_text=item.hotkey_text)
                show_separator = True
            if isinstance(item, CategoryCollectionItem):
                item = CategoryMenuCollection(self._model, item)
                show_separator = True
            elif isinstance(item, CategoryCustomItem):
                item = custom_items.append(item)
            attach_trigger_fn(item, name)

        if custom_items:
            # Custom items have different states from other category items
            # Show a separator here if required
            if show_separator:
                ui.Separator()
            for item in custom_items:
                name: str = getattr(item, "text", "")
                item = item.build_fn()
                attach_trigger_fn(item, name)

    def _on_status_changed(self, model: ui.AbstractValueModel) -> None:
        self._delegate.status = self._item.status

    def _on_icon_clicked(self, x, y, button, modifiers) -> None:
        import carb
        if button != int(carb.input.MouseInput.LEFT_BUTTON):
            return

        # XXX: trigger_fns workaround to avoid status-model subscriptions firing multiple times.
        #
        # There is a checken-egg problem here, where if the trigger_fn is run first the it must know about
        # all-items current state to follow the all, empty, mixed model...but if run after then, the trigger_fn
        # has no idea of what item transitioned to what state. Opting to deal with the first issue as this is
        # only used for "Show By Type" where the bigger win is performance from batching all state transition into
        # one UsdStage Traversal.
        # But that means the status must be saved first, as triggered_fn may change child item state, which would affect
        # how the models urrent state is chosen when it is run afterward.

        cur_status = self._delegate.status
        if cur_status in (CategoryStatus.EMPTY, CategoryStatus.MIXED):
            cur_status = CategoryStatus.ALL
        else:
            cur_status = CategoryStatus.EMPTY

        if self.__trigger_fns:
            trigger_fn = self.__trigger_fns.get(self.__identifier)
            if trigger_fn:
                trigger_fn()

        self._item.status = cur_status
