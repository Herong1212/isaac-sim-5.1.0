import omni.ui as ui
from ..viewport_menu_model import ViewportMenuModel, AbstractViewportMenuItem
from ..menu_item.viewport_menubar_item import ViewportMenubar
from ..style import DEFAULT_MENUBAR_NAME

__all__ = ["PreferenceModel"]


class PreferenceModel(ui.AbstractItemModel):
    """
    Wrapper model for preference page.
    Only show default menubar in preference page. So using this wrapper to get menu items for default menubar only.
    """
    def __init__(self, model: ViewportMenuModel):
        self._model = model
        self.__sub_menubar_changed = self._model.subscribe_item_changed_fn(self.__on_menubar_changed)  # noqa: PLW0238
        super().__init__()

    def destroy(self):
        self.__sub_menubar_changed = None  # noqa: PLW0238

    def get_item_children(self, parent_item=None):
        if parent_item is None:
            for item in self._model.get_item_children():
                if item.name == DEFAULT_MENUBAR_NAME:
                    # Only show default menubar
                    return self._model.get_item_children(item)
        return []

    def get_item_value_model_count(self, item: AbstractViewportMenuItem):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item: AbstractViewportMenuItem, column_id: int):
        if item and column_id == 0:
            return ui.SimpleStringModel(item.name)
        return ui.SimpleStringModel("")

    # Enable drag and drop

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

        self._model._item_changed(source)  # noqa: PLW0212
        self._model._item_changed(None)  # noqa: PLW0212

        self._item_changed(source)
        self._item_changed(None)

    def __on_menubar_changed(self, model: ui.AbstractItemModel, item: ui.AbstractItem):
        # OM-77174: update preference treeview when
        # menubar item changed
        # Item is None means menubar item is removed
        if item is None or isinstance(item, ViewportMenubar):
            self._item_changed(None)
