# pylint: disable=relative-beyond-top-level

__all__ = ["ActionColumnDelegate"]
import asyncio
from typing import Optional
from omni.kit.actions.window import AbstractActionItem, ActionExtItem, StringColumnDelegate, ActionsPicker
from omni.kit.widget.highlight_label import HighlightLabel
import omni.ui as ui
import omni.kit.app

from ..model.hotkeys_model import HotkeyDetailItem, HotkeysModel, EmptyHotkeyItem
from ..model.hotkey_item import AbstractFilterItem, AddWindowItem, FilterContextItem, FilterWindowItem
from ..window.warning_window import WarningWindow
from ..style import HIGHLIGHT_LABEL_STYLE, HIGHLIGHT_LABEL_STYLE_USER


class ActionColumnDelegate(StringColumnDelegate):
    """
    A simple delegate to display/add action in column.

    Kwargs:
        name (str): Column name.
        width (ui.Length): Column width. Default ui.Fraction(1).
    """
    def __init__(self, name: str, width: ui.Length = None):
        width = ui.Fraction(1) if width is None else width
        super().__init__(name, width=width)
        self.__actions_picker: Optional[ActionsPicker] = None
        self.__auto_show_picker = False

    def build_widget(self, model: HotkeysModel, item: AbstractActionItem, level: int, expand: bool):
        if isinstance(item, AddWindowItem):
            return None
        if isinstance(item, HotkeyDetailItem):
            if item.hotkey.action:
                label = HighlightLabel(item.hotkey.action.display_name, highlight=item.highlight, style=HIGHLIGHT_LABEL_STYLE_USER if item.user_defined else HIGHLIGHT_LABEL_STYLE)
                label.widget.set_tooltip(f"{item.hotkey.action_text}\n{item.hotkey.action.description}")
                return label.widget
            return ui.Label(item.hotkey.action_text, name="warning", style_type_name_override="ActionsView.Item.Text")
        if isinstance(item, ActionExtItem):
            container = ui.ZStack()
            with container:
                # Background rectangle
                with ui.VStack():
                    ui.Spacer()
                    ui.Rectangle(height=26, style_type_name_override="ActionsView.Row.Background")
                    ui.Spacer()
                filter_type = "Global"
                if isinstance(item, FilterWindowItem):
                    filter_type = "Window"
                elif isinstance(item, FilterContextItem):
                    filter_type = "Context"
                button = ui.Button(
                    f"Add New {filter_type} Hotkey",
                    name="add",
                    image_width=20,
                    visible=True,
                )
                button.set_clicked_fn(lambda m=model, i=item, b=button: self.__add_action(m, i, b))
            return container
        if isinstance(item, EmptyHotkeyItem):
            container = ui.ZStack()
            with container:
                ui.Rectangle(style_type_name_override="DropDownArrow.background")
                with ui.HStack():
                    action_label = ui.Label("Select An Action", name="hint", style_type_name_override="Action.Input")
                    with ui.VStack(width=0):
                        ui.Spacer()
                        ui.Triangle(
                            width=20,
                            height=16,
                            alignment=ui.Alignment.CENTER_BOTTOM,
                            style_type_name_override="DropDownArrow",
                        )
                        ui.Spacer()
            container.set_mouse_released_fn(lambda x, y, b, f, m=model, c=container, l=action_label: self.__show_action_picker(m, c, l))  # noqa: E741
        if self.__auto_show_picker:
            self.__show_action_picker(model, container, action_label)
            self.__auto_show_picker = False

        return container

    def __add_action(self, model: HotkeysModel, item: AbstractFilterItem, button: ui.Button):
        if isinstance(item, FilterContextItem):
            if not item.id:
                warn_window = WarningWindow("Context required", ["Please select a context first before adding new context hotkey!"])
                warn_window.position_x = button.screen_position_x + 4
                warn_window.position_y = button.screen_position_y
                return
        elif isinstance(item, FilterWindowItem) and not item.id:
            warn_window = WarningWindow("Window required", ["Please select a window first before adding new window hotkey!"])
            warn_window.position_x = button.screen_position_x + 4
            warn_window.position_y = button.screen_position_y
            return

        async def __add_action_async():
            await omni.kit.app.get_app().next_update_async()
            self.__auto_show_picker = True
            model.add_empty_hotkey(item)

        asyncio.ensure_future(__add_action_async())

    def __show_action_picker(self, model: HotkeysModel, container: ui.Stack, label: ui.Label) -> None:
        if self.__actions_picker is not None:
            if self.__actions_picker.visible:
                # Just hide actions picker if it already visible
                self.__actions_picker.visible = False
                return
            self.__actions_picker = None

        # Refresh actions list every time
        def __on_action_selected(action):
            item = model.save_empty_action(action)
            label.text = item.action_display
            label.name = ""
            self.__actions_picker.visible = False

        async def __update_position():
            if container.computed_width == 0:
                await omni.kit.app.get_app().next_update_async()
            self.__actions_picker = ActionsPicker(width=container.computed_width, height=500, on_selected_fn=__on_action_selected)
            self.__actions_picker.visible = True

            self.__actions_picker.position_x = container.screen_position_x
            self.__actions_picker.position_y = container.screen_position_y + container.computed_height

        asyncio.ensure_future(__update_position())
