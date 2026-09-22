# pylint: disable=unused-private-member, relative-beyond-top-level

__all__ = ["KeyResetHelper", "HotkeyColumnDelegate"]
import asyncio
from typing import Dict, List
from omni.kit.actions.window import AbstractActionItem, StringColumnDelegate
from omni.kit.hotkeys.core import KeyCombination, HOTKEY_CHANGED_GLOBAL_EVENT, HotkeyRegistry, get_hotkey_registry
from omni.kit.widget.highlight_label import HighlightLabel
import omni.ui as ui
import omni.kit.app
from carb.eventdispatcher import get_eventdispatcher, Event
from ..model.hotkeys_model import EmptyHotkeyItem, HotkeyDetailItem, HotkeysModel, AddWindowItem
from ..window.warning_window import WarningWindow, WarningMessage
from ..style import VIEW_ROW_HEIGHT, HIGHLIGHT_LABEL_STYLE, HIGHLIGHT_LABEL_STYLE_USER
from .reset_button import ResetButton, ResetHelper
from .key_editor import KeyEditor


class KeyResetHelper(ResetHelper):
    def __init__(self, model: HotkeysModel, item: HotkeyDetailItem, container: ui.Widget):
        self.__model = model
        self.__item = item
        self.__container = container

    def can_reset(self) -> bool:
        return self.__item.is_modified()

    def reset(self) -> bool:
        result = self.__model.restore_item_key(self.__item)
        if result != HotkeyRegistry.Result.OK:
            if result == HotkeyRegistry.Result.ERROR_KEY_DUPLICATED:
                key_combination = KeyCombination(self.__item.default_key_id)
                duplicated_key = get_hotkey_registry().get_hotkey_for_filter(key_combination, self.__item.hotkey.filter)
                action_display = duplicated_key.action.display_name if duplicated_key.action else "Unknown Action"
                warn_window = WarningWindow(
                    "Hotkey Conflict Warning",
                    messages=[
                        "The default for this action is ",
                        WarningMessage(f"'{key_combination.id}'", highlight=True),
                        "\n",
                        "It is already assigned to ",
                        WarningMessage(f"'{action_display}'", highlight=True),
                        '\n',
                        "Do you want to replace this existing hotkey with your new one?"
                    ],
                    buttons=[
                        ("Replace", lambda k=key_combination, n=self.__item, o=duplicated_key: self.__model.replace_item_key(k, n, o)),
                        ("Cancel", None)
                    ],
                )
            else:
                warn_window = WarningWindow("Unkown Error", [f"Error code: {result}"])
            warn_window.position_x = self.__container.screen_position_x + 4
            warn_window.position_y = self.__container.screen_position_y + self.__container.computed_height + 4
            return False
        return True

    def filter_payload(self, payload: Event) -> bool:
        hotkey = self.__item.hotkey
        if (
            payload["hotkey_ext_id"] == hotkey.hotkey_ext_id
            and payload["action_ext_id"] == hotkey.action_ext_id
            and payload["action_id"] == hotkey.action_id
        ):
            self._update_reset_button()
            return True

        return False


class HotkeyColumnDelegate(StringColumnDelegate):
    """
    A simple delegate to display a editable hotkey in column.

    Kwargs:
        name (str): Column name.
        width (ui.Length): Column width. Default None means ui.Fraction(1).
    """
    def __init__(self, name: str, width: ui.Length = None):
        width = ui.Fraction(1) if width is None else width
        super().__init__(name, width=width)
        self.__reset_helpers: Dict[HotkeyDetailItem, KeyResetHelper] = {}
        self.__key_editors: Dict[HotkeyDetailItem, KeyEditor] = {}
        self.__edit_containers: Dict[HotkeyDetailItem, ui.HStack] = {}
        self.__last_selections: List[AbstractActionItem] = []

        self.__change_event_sub = get_eventdispatcher().observe_event(
            event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self.__on_hotkey_changed)

    def destroy(self):
        self.__reset_helpers = {}
        self.stop_key_capture()
        self.__key_editors = {}
        self.__change_event_sub = None

    def stop_key_capture(self):
        for item in self.__key_editors.values():
            item.visible = False

    def build_widget(self, model: HotkeysModel, item: AbstractActionItem, level: int, expand: bool):
        if isinstance(item, (HotkeyDetailItem, EmptyHotkeyItem)):
            is_empty_hotkey = isinstance(item, EmptyHotkeyItem)
            container = ui.ZStack()
            with container:
                tool_container = ui.HStack(visible=not is_empty_hotkey, content_clipping=True)
                with tool_container:
                    key_label = HighlightLabel(item.hotkey.key_text, highlight=item.highlight, style=HIGHLIGHT_LABEL_STYLE_USER if item.user_defined else HIGHLIGHT_LABEL_STYLE)
                    ui.Spacer()
                    edit_container = ui.HStack(width=0, visible=item in self.__last_selections)
                    with edit_container:
                        ui.Image(name="delete", width=20, mouse_pressed_fn=lambda x, y, b, f, m=model, i=item: self.__on_delete(m, i))
                        ui.Spacer(width=4)
                        edit_image = ui.Image(name="edit", width=20)
                    if isinstance(item, HotkeyDetailItem):
                        ui.Spacer(width=4)
                        self.__reset_helpers[item] = KeyResetHelper(model, item, container)
                        reset_button = ResetButton([self.__reset_helpers[item]])
                        self.__reset_helpers[item].set_reset_button(reset_button)
                    ui.Spacer(width=1)

                key_editor = KeyEditor(model, item, visible=is_empty_hotkey, on_edit_cancelled_fn=lambda v, k=key_label, t=tool_container: self.__on_key_cancelled(v, k, t))
                self.__key_editors[item] = key_editor
                self.__edit_containers[item] = edit_container

            tool_container.set_mouse_double_clicked_fn(lambda x, y, b, f, t=tool_container, k=key_editor: self.__show_key_editor(t, k))
            edit_image.set_mouse_pressed_fn(lambda x, y, b, f, t=tool_container, k=key_editor: self.__show_key_editor(t, k))
            return container
        if isinstance(item, AddWindowItem):
            return None

        container = ui.VStack(height=VIEW_ROW_HEIGHT)
        with container:
            ui.Spacer()
            ui.Rectangle(height=26, style_type_name_override="ActionsView.Row.Background")
            ui.Spacer()
        return container

    def on_selection_changed(self, selections: List[ui.AbstractItem]):
        for item in self.__last_selections:
            if item in self.__edit_containers and not self.__key_editors[item].visible:
                self.__edit_containers[item].visible = False
        for item in selections:
            if item in self.__edit_containers and not self.__key_editors[item].visible:
                self.__edit_containers[item].visible = True
        self.__last_selections = selections

    def on_hover_changed(self, item: ui.AbstractItem, hovered: bool) -> None:
        if not isinstance(item, HotkeyDetailItem):
            return

        if item in self.__edit_containers and not self.__key_editors[item].visible:
            self.__edit_containers[item].visible = hovered or item in self.__last_selections

    def __show_key_editor(self, tool_container: ui.HStack, key_editor: KeyEditor) -> None:

        async def __show_editor():
            # Wait a frame to not trigger show editor and drop down arrow at one click
            await omni.kit.app.get_app().next_update_async()
            key_editor.visible = True
            tool_container.visible = False

        asyncio.ensure_future(__show_editor())

    def __on_key_cancelled(self, value: str, key_label: ui.Label, tool_container: ui.HStack):
        key_label.text = value if value is not None else ""
        tool_container.visible = True

    def __on_delete(self, model: HotkeysModel, item: HotkeyDetailItem) -> None:
        model.delete_hotkey_item(item)

    def __on_hotkey_changed(self, event: Event):
        for helper in self.__reset_helpers.values():
            if helper.filter_payload(event):
                break
