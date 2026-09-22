from typing import List, Optional

import carb.events
import omni.kit.app
import omni.kit.widget.context_menu
import omni.ui as ui


class LogItem(ui.AbstractItem):
    def __init__(self, text_type, text):
        """
        Represent a log event.
        """
        self._text_type = text_type
        self.text = text
        self.value_model = ui.SimpleStringModel(text)
        super().__init__()

    @property
    def text_type(self) -> str:
        """Text of log type"""
        match self._text_type:
            case omni.kit.app.GLOBAL_EVENT_SCRIPT_COMMAND_IMMEDIATE:
                return "command"
            case omni.kit.app.GLOBAL_EVENT_SCRIPT_STDOUT_IMMEDIATE:
                return "information"
            case omni.kit.app.GLOBAL_EVENT_SCRIPT_STDERR_IMMEDIATE:
                return "error"
        return ""


class LogModel(ui.AbstractItemModel):
    def __init__(self):
        self._items: List[LogItem] = []

        self._on_log_error = None

        self._sub_logs = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=event_name,
                observer_name=f"[ext: omni.kit.window.script_editor] ScriptEvent for {event_name}",
                on_event=self._on_event,
            ) for event_name in [omni.kit.app.GLOBAL_EVENT_SCRIPT_COMMAND_IMMEDIATE, omni.kit.app.GLOBAL_EVENT_SCRIPT_STDOUT_IMMEDIATE, omni.kit.app.GLOBAL_EVENT_SCRIPT_STDERR_IMMEDIATE]
        ]

        super().__init__()

    def destroy(self) -> None:
        self._sub_logs.clear()
        self._sub_logs = None

    def set_on_log_error(self, on_log_error) -> None:
        self._on_log_error = on_log_error

    def clear(self) -> None:
        self._items.clear()
        self._item_changed(None)

    def get_item_value_model_count(self, item) -> int:
        return 1

    def get_item_value_model(self, item: LogItem, column_id: int) -> ui.AbstractValueModel:
        return item.value_model

    def get_item_children(self, item: Optional[LogItem] = None) -> List[LogItem]:
        return self._items if item is None else []

    def _on_event(self, event: carb.eventdispatcher.Event) -> None:
        item = LogItem(event.event_name, event.get("text"))
        self._items.append(item)
        if item.text_type == "error":
            if self._on_log_error:
                self._on_log_error(item)
        self._item_changed(None)


class LogDelegate(ui.AbstractItemDelegate):
    def __init__(self):
        super().__init__()

    def build_widget(self, model: LogModel, item: LogItem, column_id: int, level: int, expanded: bool) -> None:
        ui.Label(
            item.text,
            height=0,
            skip_draw_when_clipped=True,
            name=item.text_type,
            style_type_name_override="LogView.Item.Text",
        )


class LogView:
    def __init__(self, **kwargs):
        self._delegate = LogDelegate()
        self._log_model = LogModel()
        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            style_type_name_override="LogView",
            mouse_pressed_fn=self._on_mouse_pressed,
            **kwargs,
        ) as self._scrolling_frame:
            self._treeview = ui.TreeView(
                self._log_model,
                delegate=self._delegate,
                root_visible=False,
                header_visible=False,
                enabled=False,
                style_type_name_override="LogView",
            )

    def destroy(self) -> None:
        omni.kit.widget.context_menu.get_instance().close_menu()

    @property
    def model(self) -> LogModel:
        return self._log_model
    
    @property
    def latest_log(self) -> str:
        log_items = self._log_model.get_item_children()
        return log_items[-1].text if log_items else ""

    def scroll_to_end(self) -> None:
        self._scrolling_frame.scroll_y = self._scrolling_frame.scroll_y_max

    def refresh_ui(self) -> None:
        self._treeview.dirty_widgets()

    def _on_mouse_pressed(self, x, y, btn, flag) -> None:
        if btn == 1:
            # Right click
            omni.kit.widget.context_menu.get_instance().show_context_menu(
                "Script Editor Log View",
                {},
                [
                    {
                        "name": "Clear",
                        "onclick_fn": lambda _: self._clear_log(),
                    },
                ],
            )

    def _clear_log(self) -> None:
        self._log_model.clear()
