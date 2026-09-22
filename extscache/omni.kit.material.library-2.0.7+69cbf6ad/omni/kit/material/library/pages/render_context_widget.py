from collections import OrderedDict

import os

import carb.settings
from omni.kit.window.preferences import PreferenceBuilder, PERSISTENT_SETTINGS_PREFIX, SettingType

import omni.ui as ui
from omni.ui import color as cl
from .. import material_config_utils


class RenderContextListItem(ui.AbstractItem):
    def __init__(self, value, display_name):
        super().__init__()
        self.value_model = ui.SimpleStringModel(value)
        self.name_model = ui.SimpleStringModel(display_name)


class RenderContextListItemDelegate(ui.AbstractItemDelegate):
    _ITEM_LABEL_STYLE = {
        "margin": 3,
        "font_size": 16.0,
        ":selected": {
            "color": cl("#333333")
        }
    }

    def build_widget(self, model, item, column_id, level, expanded):
        with ui.ZStack(height=20):
            value_model = model.get_item_value_model(item, column_id)
            label = ui.Label(value_model.as_string, style=self._ITEM_LABEL_STYLE)
            field = ui.StringField()
            field.model = value_model
            field.visible = False


class RenderContextListModel(ui.AbstractItemModel):
    SUPPORTED_CONTEXTS = OrderedDict([("mdl", "MDL"), ("mtlx", "MaterialX"), ("", "Default")])

    def __init__(self, message_fn):
        super().__init__()

        self._settings = carb.settings.get_settings()
        self._setting_path = PERSISTENT_SETTINGS_PREFIX + "/app/hydra/material/renderContexts"
        self._message_fn = message_fn
        self._item_class = RenderContextListItem
        self._items = []
        self.populate_items()

    def populate_items(self):
        entries = self._settings.get(self._setting_path)
        if not entries:
            entries = self.SUPPORTED_CONTEXTS
        else:
            if isinstance(entries, str):
                entries = [entries]

            for context in self.SUPPORTED_CONTEXTS.keys():
                if context not in entries:
                    entries.append(context)

        self._items = [self._item_class(entry, self.SUPPORTED_CONTEXTS[entry]) for entry in entries]
        self._item_changed(None)

    def get_item_children(self, item=None):
        return [] if (item is not None) else self._items

    def get_item_value_model_count(self, item):
        return 1

    def get_item_value_model(self, item, column_id):
        return item.name_model if (isinstance(item, self._item_class)) else None

    def get_drag_mime_data(self, item):
        return item.name_model.as_string

    def drop_accepted(self, target_item, source, drop_location=1):
        return not target_item and drop_location >= 0

    def drop(self, target_item, source, drop_location=-1):
        try:
            source_id = self._items.index(source)
        except ValueError:
            return

        if source_id == drop_location:
            return

        self._items.remove(source)

        if drop_location > len(self._items):
            self._items.append(source)
        else:
            if source_id < drop_location:
                drop_location = drop_location - 1

            self._items.insert(drop_location, source)

        self._item_changed(None)

        contexts = [item.value_model.as_string for item in self._items]
        self._settings.set_string_array(self._setting_path, contexts)
        self._message_fn("Material render context has been changed. You will need to reload your stage for this to take effect.")

class RenderContextWidget(ui.Widget):
    def __init__(self, message_fn):
        super().__init__()
        self._model = RenderContextListModel(message_fn)
        self._delegate = RenderContextListItemDelegate()

        # build UI
        with ui.ScrollingFrame(height=100):
            ui.Spacer(height=5)
            self._view = ui.TreeView(
                self._model,
                delegate=self._delegate,
                header_visible=False,
                root_visible=False,
                column_widths=[ui.Percent(95)],
                drop_between_items=True
            )
            self._view.set_selection_changed_fn(self.on_item_selection_changed)

    def on_item_selection_changed(self, items):
        # not to allow multi-selection
        num_items = len(items)
        if num_items > 1:
            for i in range(1, num_items):
                self._view.toggle_selection(items[i])


