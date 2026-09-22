import omni.ui as ui


class SeparatorDelegate(ui.MenuDelegate):
    """ A menu delegate that creates separator between items within a viewport menubar"""

    def __init__(self):
        """Constructor"""
        self.__frame = None
        super().__init__()

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources"""
        return

    def build_item(self, item: ui.MenuItem) -> None:
        """
        Build a line as separator.

        Args:
            item (ui.MenuItem): Menu item.
        """
        self.__frame = ui.Frame(style_type_name_override="Menu.Item")
        with self.__frame:
            ui.Line(width=2, alignment=ui.Alignment.V_CENTER, style_type_name_override="Menu.Item.Separator")
