from typing import Optional, Dict, List

from omni.kit.widget.options_menu import OptionsMenu, OptionsModel, OptionItem
import omni.ui as ui

from .style import UI_STYLE


class OptionsButton:
    """A button that includes a popup menu for options.

    Args:
        option_items (List[OptionItem]): Option items.
        width (ui.Length): Button width. Default ui.Pixel(24).
        height (ui.Length): Button height. Default ui.Pixel(24).
        hide_on_click (bool): Hide popup menu if menu item clicked. Default False.
        menu_width (ui.Length): Width of popup menu item. Default ui.Fraction(1).
        style (dict): External widget style. Default empty."""

    def __init__(
        self,
        option_items: List[OptionItem],
        width: ui.Length = ui.Pixel(24),
        height: ui.Length = ui.Pixel(24),
        hide_on_click: bool = False,
        menu_width: ui.Length = ui.Fraction(1),
        style: Dict = {},
    ):
        """Constructor for OptionsButton."""
        self._options_model = OptionsModel("Options", option_items)
        self._width = width
        self._height = height
        self._hide_on_click = hide_on_click
        self._menu_width = menu_width
        self._style = UI_STYLE.copy()
        self._style.update(style)

        self._options_menu: Optional[OptionsMenu] = None
        self._ignore_next_mouse_release = False

        self._build_ui()

    def destroy(self) -> None:
        """Clears models and destroys the options menu."""
        self._options_model.destroy()
        self._options_model = None
        if self._options_menu:
            self._options_menu.destroy()
            self._options_menu = None

    @property
    def model(self) -> OptionsModel:
        """Gets the OptionsModel associated with the button.

        Returns:
            OptionsModel: The model used for options."""
        return self._options_model

    @property
    def button(self) -> ui.Button:
        """Gets the ui.Button used as the options button.

        Returns:
            ui.Button: The button widget."""
        return self._button

    def _build_ui(self) -> None:
        self._button = ui.Button(
            width=self._width,
            height=self._height,
            style_type_name_override="OptionsButton",
            style=self._style,
            mouse_pressed_fn=lambda x, y, b, a: self._on_mouse_pressed(b),
            mouse_released_fn=lambda x, y, b, a: self._on_mouse_released(b),
            identifier="settings_icon",
            name="options",
        )

    def _on_mouse_pressed(self, btn) -> None:
        # If options menu already show, just hide
        self._ignore_next_mouse_release = self._options_menu and self._options_menu.shown

    def _on_mouse_released(self, btn) -> None:
        if self._ignore_next_mouse_release:
            return

        self._show_options_menu()

    def _show_options_menu(self):
        if self._options_menu is None:
            self._options_menu = OptionsMenu(
                self._options_model, hide_on_click=self._hide_on_click, width=self._menu_width
            )
        self._options_menu.show_by_widget(self._button)
