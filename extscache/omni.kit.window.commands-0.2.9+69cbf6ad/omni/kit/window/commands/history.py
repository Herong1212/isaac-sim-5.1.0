from pathlib import Path
import carb.settings
from omni import ui
import omni.kit.undo


class HistoryData:
    def __init__(self):
        self._data = omni.kit.undo.get_history()
        if len(self._data):
            self._curr = next(iter(self._data))
            self._last = next(reversed(self._data))
        else:
            self._curr = 0
            self._last = -1

    def is_not_empty(self):
        return self._curr <= self._last

    def get_next(self):
        self._curr += 1
        return self._data[self._curr - 1]

    def is_next_lower(self, level):
        return self._data[self._curr].level > level


class HistoryModel(ui.AbstractItemModel):
    def __init__(self):
        super().__init__()
        self._root = MainItem(None, HistoryData())

    def _commands_changed(self):
        self._root = MainItem(None, HistoryData())
        self._item_changed(None)

    def get_item_children(self, item):
        if item is None:
            return self._root.children

        return item.children

    def get_item_value_model_count(self, item):
        return 1

    def get_item_value_model(self, item, column_id):
        if column_id == 0:
            return item.name_model


class HistoryDelegate(ui.AbstractItemDelegate):
    def __init__(self):
        super().__init__()
        self._icon_path = Path(__file__).parent.parent.parent.parent.parent.joinpath("icons")
        self._style = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        # Read all the svg files in the directory
        self._icons = {icon.stem: icon for icon in self._icon_path.joinpath(self._style).glob("*.svg")}

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per column per item"""
        value_model = model.get_item_value_model(item, column_id)

        # call out commands that had errors
        text = value_model.as_string
        name = ""
        if hasattr(item, "_data") and hasattr(item._data, "error") and item._data.error:
            text = "[ERROR] " + text
            name = "error"

        ui.Label(text, name=name, style_type_name_override="TreeView.Item")

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        if column_id == 0:
            with ui.HStack(width=16 * (level + 2), height=0):
                ui.Spacer()
                if model.can_item_have_children(item):
                    # Draw the +/- icon
                    image_name = "Minus" if expanded else "Plus"
                    ui.Image(
                        str(self._icons.get(image_name)), width=10, height=10, style_type_name_override="TreeView.Item"
                    )
                    ui.Spacer(width=4)

    def build_header(self, column_id):
        pass


class MainItem(ui.AbstractItem):
    def __init__(self, command_data, history):
        super().__init__()
        self._data = command_data
        if command_data is None:
            self._create_root(history)
        else:
            self._create_node(history)

    def _create_root(self, history):
        self.children = []
        while history.is_not_empty():
            self.children.append(MainItem(history.get_next(), history))

    def _create_node(self, history):
        self.name_model = ui.SimpleStringModel(self._data.name)
        self.children = [ParamItem(arg, val) for arg, val in self._data.kwargs.items()]
        while history.is_not_empty() and history.is_next_lower(self._data.level):
            next_command = history.get_next()
            self.children.append(MainItem(next_command, history))


class ParamItem(ui.AbstractItem):
    def __init__(self, arg, val):
        super().__init__()
        self.name_model = ui.SimpleStringModel(str(arg) + "=" + str(val))
        self.children = []
