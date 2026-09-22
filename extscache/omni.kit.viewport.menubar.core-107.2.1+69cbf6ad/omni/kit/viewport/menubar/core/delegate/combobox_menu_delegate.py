from typing import Optional

from omni import ui

from ..model.combobox_model import ComboBoxModel
from .abstract_widget_menu_delegate import AbstractWidgetMenuDelegate

__all__ = ["ComboBoxMenuDelegate"]


class ComboBoxMenuDelegate(AbstractWidgetMenuDelegate):
    """A menu delegate that creates combobox within a viewport menubar."""

    def __init__(
        self,
        model: Optional[ComboBoxModel] = None,
        height: ui.Length = 0,
        width: ui.Length = 300,
        enabled: bool = True,
        text: bool = True,
        icon_name: Optional[str] = None,
        icon_width: ui.Length = 30,
        icon_height: ui.Length = 30,
        tooltip: Optional[str] = None,
        use_in_menubar: bool = False,
        has_reset: bool = False,
    ):
        """
        Constructor.

        Keyword Args:
            model (Optional[ComboBoxModel]): Combobox data model, defaults to None.
            height (ui.Length): Delegate height, defaults to 0 means auto height.
            width (ui.Length): Delegate width, defaults to 300 pixels.
            enabled (bool): Delegate enabled state, defaults to True.
            text (bool): Show text before combobox, defaults to True.
            icon_name (Optional[str]): Name of additional icon to be displayed before text, defaults to None means no additional icon.
            icon_width (ui.Length): Width of additional icon. Only available when icon_name is valid, defaults to 30 pixels.
            icon_height (ui.Length): Height of additional icon. Only available when icon_name is valid, defaults to 30 pixels.
            tooltip (Optional[str]): Delegate tooltip, defaults to None means no tooltip.
            use_in_menubar (bool): Show delegate in menu bar, defaults to False.
            has_reset (bool): Show reset button, defaults to False.
        """
        super().__init__(
            model=model, height=height, width=width, enabled=enabled, has_reset=has_reset, use_in_menubar=use_in_menubar
        )
        self.__combo_width = 90
        self.__text = text
        self.__icon_name = icon_name
        self.__icon_width = icon_width
        self.__icon_height = icon_height
        self.__tooltip = tooltip

    def __del__(self):
        if self._model:
            self._model.destroy()
        self.destroy()

    def destroy(self) -> None:
        """Release resources."""
        # TODO: We don't have to destroy the model here. We should do it in the
        # object created the model. But since the model is not stored anywhere,
        # it's destroyed here.
        if self._model:
            self._model.destroy()
            self._model = None
        super().destroy()

    def build_widget(self, item: ui.MenuHelper) -> None:
        """
        Build combobox with optional icon and label.

        Args:
            item (ui.MenuHelper): Menu item.
        """
        if self.__icon_name:
            ui.ImageWithProvider(
                style_type_name_override="Menu.Item.Icon",
                tooltip=self.__tooltip,
                name=self.__icon_name,
                width=self.__icon_width,
                height=self.__icon_height,
            )
        if self.__text:
            ui.Label(item.text, style_type_name_override="Menu.Item.Label")
        with ui.VStack(width=self.__combo_width):
            ui.Spacer()
            ui.ComboBox(self._model, height=0)
            ui.Spacer()
