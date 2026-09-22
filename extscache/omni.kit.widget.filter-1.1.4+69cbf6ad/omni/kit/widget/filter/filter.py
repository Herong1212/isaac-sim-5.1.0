import asyncio
from typing import Optional, Dict, List

from omni.kit.widget.options_menu import OptionsMenu, OptionsModel, OptionItem
import omni.ui as ui

from .style import UI_STYLE


TIME_HOLD_SHOW_MENU = 0.08


class FilterModel(OptionsModel):
    """
    Filter model.
    """
    def __init__(self, option_items: List[OptionItem]):
        super().__init__("Filter", option_items)


class FilterButton:
    """
    A filter button with an associated popup menu.

    Kwargs:
        option_items (List[OptionItem]): Option items.
        width (ui.Length): Button width. Default ui.Pixel(24).
        height (ui.Length): Button height. Default ui.Pixel(24).
        hide_on_click (bool): Hide popup menu if menu item clicked. Default False.
        menu_width (ui.Length): Width of popup menu item. Default ui.Fraction(1).
        style (dict): External widget style. Default empty.
    """

    def __init__(
        self,
        option_items: List[OptionItem],
        width: ui.Length = ui.Pixel(24),
        height: ui.Length = ui.Pixel(24),
        hide_on_click: bool = False,
        menu_width: ui.Length = ui.Fraction(1),
        carot_size: ui.Length = ui.Pixel(3),
        style: Dict = {},
    ):
        self._options_model = FilterModel(option_items)
        self._width = width
        self._height = height
        self._hide_on_click = hide_on_click
        self._menu_width = menu_width
        self._carot_size = carot_size
        self._style = UI_STYLE.copy()
        self._style.update(style)

        self._options_menu: Optional[OptionsMenu] = None
        self._ignore_next_mouse_release = False
        self._show_menu_task = None
        self._saved_options: Dict[OptionItem, bool] = {}

        self._build_ui()

    def destroy(self) -> None:
        self.__sub = None
        self._options_model.destroy()
        self._options_model = None
        if self._options_menu:
            self._options_menu.destroy()
            self._options_menu = None

    @property
    def model(self) -> FilterModel:
        """Model for filter options"""
        return self._options_model

    @property
    def button(self) -> ui.Button:
        """Filter button widget"""
        return self._button

    def _build_ui(self) -> None:
        self._container = ui.ZStack(width=0, height=0, style=self._style)
        with self._container:
            self._button = ui.Button(
                width=self._width,
                height=self._height,
                checked=self._options_model.dirty,
                style_type_name_override="FilterButton",
                # clicked_fn=lambda: self._show_options_menu(),
                mouse_pressed_fn=lambda x, y, b, a: self._on_mouse_pressed(b),
                mouse_released_fn=lambda x, y, b, a: self._on_mouse_released(b),
                mouse_double_clicked_fn=lambda x, y, b, a: self._on_mouse_double_clicked(b),
                identifier="filter"
            )

            with ui.VStack():
                with ui.HStack():
                    ui.Spacer()
                    with ui.VStack(width=self._carot_size):
                        ui.Spacer()
                        ui.Triangle(
                            width=self._carot_size,
                            height=self._carot_size,
                            alignment=ui.Alignment.RIGHT_TOP,
                            style_type_name_override="FilterButton.Carot",
                        )
                    ui.Spacer(width=2)
                ui.Spacer(height=2)

        self.__sub = self._options_model.subscribe_item_changed_fn(self._on_item_changed)

    def _on_mouse_pressed(self, btn) -> None:
        # If options menu already show, just hide
        self._ignore_next_mouse_release = False
        if self._options_menu and self._options_menu.shown:
            self._ignore_next_mouse_release = True
        else:
            self._ignore_next_mouse_release = False
        return

    def _on_mouse_released(self, btn) -> None:
        if self._ignore_next_mouse_release:
            return

        if btn == 1 or btn == 0:
            # Schedule a task so double click will interrupt
            self._show_menu_task = asyncio.ensure_future(self._schedule_show_menu())
        elif btn == 2:
            # Middle button
            self._toggle_filter()
        return

    def _on_mouse_double_clicked(self, btn) -> None:
        self._ignore_next_mouse_release = True
        if self._show_menu_task:
            self._show_menu_task.cancel()
        self._toggle_filter()

    def _show_options_menu(self):
        if self._options_menu is None:
            self._options_menu = OptionsMenu(self._options_model, hide_on_click=self._hide_on_click, width=self._menu_width)
        self._options_menu.show_by_widget(self._button)

    async def _schedule_show_menu(self, ):
        await asyncio.sleep(TIME_HOLD_SHOW_MENU)
        self._show_options_menu()
        self._show_menu_task = None
        self._ignore_next_mouse_release = True

    def _toggle_filter(self):
        if self._container.selected:
            for item in self._options_model.get_item_children():
                if hasattr(item, "value"):
                    self._saved_options[item] = item.value
            self._options_model.reset()
        else:
            for item, value in self._saved_options.items():
                item.value = value

    def _on_item_changed(self, model: OptionsModel, item: OptionItem) -> None:
        self._container.selected = model.dirty
