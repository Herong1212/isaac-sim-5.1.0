from typing import Optional

import omni.ui as ui


class LabelMenuDelegate(ui.MenuDelegate):
    """A menu delegate that creates a label within a viewport menubar."""
    def __init__(
        self,
        enabled: bool = True,
        width: Optional[ui.Length] = None,
        height: ui.Length = 26,
        alignment: ui.Alignment = ui.Alignment.LEFT
    ):
        """
        Constructor.

        Keyword Args:
            enable (bool):Delegate enabled state, defaults to True.
            width (ui.Length): Label width, defaults to None means ui.Fraction(1).
            height (ui.Length): Label height, defaults to 26 pixels.
            alignment (ui.Alignment): Label alignment, defaults to ui.Alignment.CENTER.
        """
        super().__init__(propagate=False)
        self.__enabled = enabled
        self.__height = height
        self.__width = width if width is not None else ui.Fraction(1)
        self.__alignment = alignment
        self.__frame: Optional[ui.Frame] = None

    def build_item(self, item: ui.MenuItem) -> None:
        """
        Build a label.

        Args:
            item (ui.MenuItem): Menu item.
        """
        self.__frame = ui.Frame(width=self.__width, height=self.__height, style_type_name_override="Menu.Item", enabled=self.__enabled)
        with self.__frame:
            ui.Label(item.text, style_type_name_override="Menu.Item.Label", alignment=self.__alignment)
