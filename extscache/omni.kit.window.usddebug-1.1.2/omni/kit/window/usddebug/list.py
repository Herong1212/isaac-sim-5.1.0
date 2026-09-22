import omni.ui as ui

"""
Implements list of strings using Model-View
"""


class ListItem(ui.AbstractItem):
    def __init__(self, text: str):
        super().__init__()
        self.sub_model = ui.SimpleStringModel(text)


class ListModel(ui.AbstractItemModel):
    def __init__(self, entries):
        super().__init__()
        self._children = [ListItem(e) for e in entries]

    def get_item_children(self, item):
        if item is not None:
            return []
        return self._children

    def get_item_value_model_count(self, item):
        return 1

    def get_item_value_model(self, item, id):
        return item.sub_model


class ListDelegate(ui.AbstractItemDelegate):
    def __init__(self, extension_instance):
        super().__init__()
        self._extension_instance = extension_instance

    def build_widget(self, model, item, column_id, level, expanded):
        stack = ui.VStack()
        with stack:
            value_model = model.get_item_value_model(item, column_id)
            label = ui.Label(
                value_model.as_string, style={"Label": {"margin_width": 10, "margin_height": 3, "font_size": 16}}
            )
            stack.set_mouse_pressed_fn(lambda x, y, b, m: self.on_click(label.text))

    def on_click(self, selected_option):
        self._extension_instance.select_prefix(selected_option)
