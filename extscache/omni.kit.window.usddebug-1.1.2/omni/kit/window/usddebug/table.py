import omni.ui as ui
from pxr import Tf

"""
Implements the Debug Symbol table
"""


class TableItem(ui.AbstractItem):
    def __init__(self, flag):
        super().__init__()
        self.name_model = ui.SimpleStringModel(flag)
        self.desc_model = ui.SimpleStringModel(Tf.Debug.GetDebugSymbolDescription(flag))


class TableModel(ui.AbstractItemModel):
    def __init__(self, entries):
        super().__init__()
        self._children = [TableItem(e) for e in entries]

    def get_item_children(self, item):
        if item is not None:
            return []
        return self._children

    def get_item_value_model_count(self, item):
        return 2

    def get_item_value_model(self, item, column_id):
        return item.name_model if column_id == 0 else item.desc_model

    def update_entries(self, entries):
        self._children = [TableItem(e) for e in entries]
        self._item_changed(None)


class TableDelegate(ui.AbstractItemDelegate):
    def __init__(self):
        super().__init__()
        self.border_color = 0xFF505050
        self.background_color = 0xFF444444

    def build_header(self, column_id):
        text = "Description" if column_id else "Debug Symbol"
        label = ui.Label(text, style={"font_size": 16, "margin": 10})
        if column_id:
            ui.Line(alignment=ui.Alignment.LEFT, style={"color": self.border_color})

    def build_widget(self, model, item, column_id, level, expanded):
        flag = model.get_item_value_model(item, column_id).as_string
        with ui.VStack():
            with ui.ZStack(height=ui.Pixel(25)):
                ui.Rectangle(style={"background_color": self.background_color})
                if column_id:
                    label = ui.Label(flag, style={"Label": {"margin_width": 10}}, elided_text=True)
                    ui.Line(alignment=ui.Alignment.LEFT, style={"color": self.border_color})
                else:
                    stack = ui.HStack(spacing=0)
                    with stack:
                        checkbox = ui.CheckBox(width=15, style={"font_size": 11, "margin_height": 7, "margin_width": 5})
                        enabled = Tf.Debug.IsDebugSymbolNameEnabled(flag)
                        checkbox.model.set_value(enabled)
                        label = ui.Label(flag.replace("_", " "), style={"Label": {"font_size": 14}})
                        checkbox.set_mouse_pressed_fn(lambda x, y, b, m: self.on_click(flag, checkbox))
                ui.Line(alignment=ui.Alignment.TOP, style={"color": self.border_color})

    def on_click(self, selected_flag, checkbox):
        new_value = not checkbox.model.get_value_as_bool()
        Tf.Debug.SetDebugSymbolsByName(selected_flag, new_value)
