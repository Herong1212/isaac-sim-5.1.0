import os

import carb.settings
import omni.ui as ui
from omni.ui import color as cl
from .. import material_config_utils


class EditableListItem(ui.AbstractItem):
    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)


class EditableListItemDelegate(ui.AbstractItemDelegate):
    _ITEM_LABEL_STYLE = {
        "margin": 3,
        "font_size": 16.0,
        ":selected": {
            "color": cl("#333333")
        }
    }
    _DELETE_BUTTON_STYLE = {
        "margin": 2,
        "padding": 0,
        "": {
            "image_url": "",
            "alignment": ui.Alignment.CENTER,
            "background_color": 0x00000000
        },
        ":hovered": {
            "image_url": "resources/glyphs/trash.svg",
            "color": cl("#cccccc"),
            "background_color": 0x00000000
        },
        ":selected": {
            "image_url": "resources/glyphs/trash.svg",
            "color": cl("#cccccc"),
            "background_color": 0x00000000
        }
    }

    def build_widget(self, model, item, column_id, level, expanded):
        with ui.ZStack(height=20):
            value_model = model.get_item_value_model(item, column_id)

            if column_id == 0:
                # entry text
                label = ui.Label(value_model.as_string, style=self._ITEM_LABEL_STYLE)

                field = ui.StringField()
                field.model = value_model
                field.visible = False

                label.set_mouse_double_clicked_fn(
                    lambda x, y, b, m, f=field, l=label: self.on_label_double_click(b, f, l)
                )

            elif column_id == 1:
                # remove button
                with ui.HStack():
                    ui.Spacer()
                    button = ui.Button(width=20, style=self._DELETE_BUTTON_STYLE, identifier="material_config_delete")
                    button.set_clicked_fn(lambda i=item, m=model: self.on_button_clicked(i, m))
                    ui.Spacer(width=5)
            else:
                pass

    def on_label_double_click(self, mouse_button, field, label):
        if mouse_button != 0:
            return

        field.visible = True
        field.focus_keyboard()
        self.subscription = field.model.subscribe_end_edit_fn(
            lambda m, f=field, l=label: self.on_field_end_edit(m, f, l)
        )

    def on_field_end_edit(self, model, field, label):
        field.visible = False
        if model.as_string:  # avoid empty string
            label.text = model.as_string
        self.subscription = None

    def on_button_clicked(self, item, model):
        model.remove_item(item)


class EditableListModel(ui.AbstractItemModel):
    def __init__(
            self,
            item_class=EditableListItem,
            setting_path=None
        ):
        super().__init__()

        self._settings = carb.settings.get_settings()
        self._setting_path = setting_path
        self._item_class = item_class
        self._items = []
        self.populate_items()

    def populate_items(self):
        entries = self._settings.get(self._setting_path)

        if not entries:
            entries = []

        self._items.clear()
        for entry in entries:
            if not entry:
                continue
            self._items.append(self._item_class(entry))

        self._item_changed(None)

    def get_item_children(self, item):
        if item is not None:
            return []

        return self._items

    def get_item_value_model_count(self, item):
        return 2

    def get_item_value_model(self, item, column_id):
        if item and isinstance(item, self._item_class):
            if column_id == 0:
                return item.name_model
            else:
                return None

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

    def add_entry(self, text):
        self._items.insert(0, self._item_class(text))
        self._item_changed(None)

    def remove_item(self, item):
        self._items.remove(item)
        self._item_changed(None)

    def save_entries_to_settings(self):
        entries = [item.name_model.as_string for item in self._items]
        self._settings.set(self._setting_path, entries)

    def save_to_material_config_file(self):
        material_config_utils.save_live_config_to_file()


class EditableListWidget(ui.Widget):
    _ADD_BUTTON_STYLE = {
        "image_url": "resources/glyphs/plus.svg",
        "color": cl("#cccccc")
    }

    def __init__(
            self,
            model_class=EditableListModel,
            item_delegate_class=EditableListItemDelegate,
            setting_path=None,
            list_height=100
        ):
        super().__init__()

        self._model = model_class(setting_path=setting_path)
        self._delegate = item_delegate_class()

        # build UI
        with ui.VStack():
            with ui.HStack():
                # list widget
                with ui.ScrollingFrame(height=list_height):
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

                ui.Spacer(width=5)

                # "+" button
                self._add_new_entry_button = ui.Button(
                    width=20,
                    height=20,
                    style=self._ADD_BUTTON_STYLE,
                    clicked_fn=self.on_add_new_entry_button_clicked,
                    identifier="material_config_plus"
                )

            ui.Spacer(height=5)

            with ui.HStack():
                ui.Spacer()

                # save button
                self._save_button = ui.Button(
                    "Save",
                    width=100,
                    height=0,
                    clicked_fn=self.on_save_button_clicked,
                    identifier="material_config_save"
                )
                ui.Spacer(width=5)

                # reset button
                self._reset_button = ui.Button(
                    "Reset",
                    width=100,
                    height=0,
                    clicked_fn=self.on_reset_button_clicked,
                    identifier="material_config_reset"
                )
                ui.Spacer(width=25)

    def on_add_new_entry_button_clicked(self):
        self._view.clear_selection()
        self._model.add_entry("New Entry")

    def on_item_selection_changed(self, items):
        # not to allow multi-selection
        num_items = len(items)
        if num_items > 1:
            for i in range(1, num_items):
                self._view.toggle_selection(items[i])

    def on_save_button_clicked(self):
        self._model.save_entries_to_settings()

        config_file = material_config_utils.get_config_file_path()

        try:
            import omni.kit.notification_manager as nm

            if not os.path.exists(config_file):
                ok_button = nm.NotificationButtonInfo(
                    "OK",
                    on_complete=self._model.save_to_material_config_file
                )
                cancel_button = nm.NotificationButtonInfo(
                    "Cancel",
                    on_complete=None
                )
                nm.post_notification(
                    ("Material config file does not exist. Create?\n"
                    "(requires app restart to take the effect)\n\n"
                    f"{config_file}"),
                    status=nm.NotificationStatus.INFO,
                    button_infos=[ok_button, cancel_button],
                    hide_after_timeout=False
                )
            else:
                self._model.save_to_material_config_file()
                nm.post_notification(
                    ("Material config has been changed, please restart app to take the effect."),
                    status=nm.NotificationStatus.INFO,
                    hide_after_timeout=False
                )
        except ModuleNotFoundError:
            self._model.save_to_material_config_file()

        carb.log_info(f"Material config file saved: {config_file}")

    def on_reset_button_clicked(self):
        self._view.clear_selection()
        self._model.populate_items()
