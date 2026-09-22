# pylint: disable=relative-beyond-top-level

__all__ = ["WindowColumnDelegate"]
import asyncio
from typing import Optional
from omni.kit.actions.window import AbstractActionItem, ActionExtItem, StringColumnDelegate
from omni.kit.widget.highlight_label import HighlightLabel
import omni.ui as ui
import omni.kit.app

from ..model.hotkeys_model import HotkeysModel, EmptyFilterWindowItem, AddWindowItem
from ..window.windows_picker import WindowsPicker
from ..style import VIEW_ROW_HEIGHT, HIGHLIGHT_LABEL_STYLE


class WindowColumnDelegate(StringColumnDelegate):
    """
    A simple delegate to display/add action in column.

    Kwargs:
        name (str): Column name.
        width (ui.Length): Column width. Default None means ui.Fraction(1).
    """
    def __init__(self, name: str, width: Optional[ui.Length] = None):
        width = ui.Fraction(1) if width is None else width
        super().__init__(name, width=width)
        self.__windows_picker: Optional[WindowsPicker] = None
        self.__auto_show_picker = False

    def build_widget(self, model: HotkeysModel, item: AbstractActionItem, level: int, expand: bool):
        if isinstance(item, AddWindowItem):
            container = ui.ZStack(width=self._width)
            with container:
                # Background rectangle to keep get hovered when button invisible
                ui.Rectangle(height=26, style_type_name_override="Button.Background")

                def __add_window_filter():
                    self.__auto_show_picker = True
                    model.add_window_filter()

                ui.Button(
                    "Add Window",
                    name="add",
                    image_width=20,
                    visible=True,
                    clicked_fn=__add_window_filter
                )
            return container
        if isinstance(item, EmptyFilterWindowItem):
            container = ui.HStack(width=self._width, height=VIEW_ROW_HEIGHT)
            with container:
                ui.Spacer(width=4)
                with ui.ZStack():
                    ui.Rectangle(style_type_name_override="DropDownArrow.background")
                    with ui.HStack():
                        if item.id:
                            action_label = ui.Label(item.id, name="", style_type_name_override="Action.Input")
                        else:
                            action_label = ui.Label("Select A Window", name="hint", style_type_name_override="Action.Input")
                        with ui.VStack(width=0):
                            ui.Spacer()
                            ui.Triangle(
                                width=20,
                                height=16,
                                alignment=ui.Alignment.CENTER_BOTTOM,
                                style_type_name_override="DropDownArrow",
                            )
                            ui.Spacer()
                ui.Spacer(width=4)
            container.set_mouse_released_fn(lambda x, y, b, f, m=model, i=item, c=container, l=action_label: self.__show_window_picker(m, i, c, l))  # noqa: E741
            if self.__auto_show_picker:
                self.__show_window_picker(model, item, container, action_label)
                self.__auto_show_picker = False
            return container
        if isinstance(item, ActionExtItem):
            container = ui.ZStack(height=VIEW_ROW_HEIGHT)
            with container:
                with ui.VStack():
                    ui.Spacer()
                    ui.Rectangle(height=26, style_type_name_override="ActionsView.Row.Background")
                    ui.Spacer()
                HighlightLabel(item.id, height=VIEW_ROW_HEIGHT, highlight=item.highlight, style=HIGHLIGHT_LABEL_STYLE)
            return container
        return None

    def __show_window_picker(self, model: HotkeysModel, item: EmptyFilterWindowItem, container: ui.Stack, label: ui.Label) -> None:
        if self.__windows_picker is not None:
            if self.__windows_picker.visible:
                # Just hide windows picker if it already visible
                self.__windows_picker.visible = False
                return
            self.__windows_picker = None

        # Refresh windows list every time
        def __on_window_selected(item, title):
            item = model.edit_hotkey_filter_item(item, window_title=title)
            label.text = title
            label.name = ""
            self.__windows_picker.visible = False

        async def __update_position():
            if container.computed_width == 0:
                await omni.kit.app.get_app().next_update_async()
            self.__windows_picker = WindowsPicker(width=container.computed_content_width, height=500, on_selected_fn=lambda t, i=item: __on_window_selected(i, t))
            self.__windows_picker.visible = True
            await omni.kit.app.get_app().next_update_async()
            self.__windows_picker.position_x = container.screen_position_x
            self.__windows_picker.position_y = container.screen_position_y + container.computed_height

        asyncio.ensure_future(__update_position())
