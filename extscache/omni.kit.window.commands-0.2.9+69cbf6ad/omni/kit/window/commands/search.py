import inspect
from pathlib import Path

import carb.settings
import omni.ext
import omni.kit.app
from omni import ui


class SearchModel(ui.AbstractItemModel):
    """
    Represents the list of commands registered in Kit.
    It is used to make a single level tree appear like a simple list.
    """

    def __init__(self):
        super().__init__()
        self._commands = []

    def _clear_commands(self):
        self._commands = []

    def _commands_changed(self):
        self._item_changed(None)

    def _add_command(self, item):
        if item and isinstance(item, CommandItem):
            self._commands.append(item)

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is None:
            return self._commands

        return item.children

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return Columns.get_count()

    def get_item_value_model(self, item, column_id):
        """Return value model."""
        if item and isinstance(item, CommandItem):
            return Columns.get_model(item, column_id)


class SearchDelegate(ui.AbstractItemDelegate):
    def __init__(self):
        super().__init__()
        self._icon_path = Path(__file__).parent.parent.parent.parent.parent.joinpath("icons")
        self._style = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        # Read all the svg files in the directory
        self._icons = {icon.stem: icon for icon in self._icon_path.joinpath(self._style).glob("*.svg")}

    def build_widget(self, model, item, column_id, level, expanded):
        value_model = model.get_item_value_model(item, column_id)
        text = value_model.as_string
        ui.Label(text, style_type_name_override="TreeView.Item")

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
        label = Columns.get_label(column_id)
        ui.Label(label, height=30, width=20)


class CommandItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, command, ext_name):
        super().__init__()
        self.command_model = ui.SimpleStringModel(command.__name__)
        self.extension_model = ui.SimpleStringModel(ext_name)
        self.undo_model = ui.SimpleBoolModel(hasattr(command, "undo") and inspect.isfunction(command.undo))
        self.doc = command.__doc__ or (command.__init__ is not None and command.__init__.__doc__)
        self.children = []


class CommandChildItem(CommandItem):
    def __init__(self, arg):
        super().__init__(str(arg))
        self.children = []


class Columns:
    """
    Store UI info about the columns in one place so it's easier to keep in
    """

    class ColumnData:
        def __init__(self, label, column, width, attrib_name):
            self.label = label
            self.column = column
            self.width = width
            self.attrib_name = attrib_name

    Command = ColumnData("Command Class", 0, ui.Fraction(1), "command_model")
    Extension = ColumnData("Extension", 1, ui.Pixel(200), "extension_model")
    CanUndo = ColumnData("Can Undo", 2, ui.Pixel(80), "undo_model")
    ORDER = [Command, Extension, CanUndo]

    @classmethod
    def get_count(cls):
        return len(cls.ORDER)

    @classmethod
    def get_label(cls, index):
        return cls.ORDER[index].label

    @classmethod
    def get_model(cls, entry: CommandItem, index):
        return getattr(entry, cls.ORDER[index].attrib_name)
