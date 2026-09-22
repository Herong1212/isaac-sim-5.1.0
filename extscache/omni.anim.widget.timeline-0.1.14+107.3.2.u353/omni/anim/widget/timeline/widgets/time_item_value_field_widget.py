import carb
from omni import ui

from ..models import TimeDisplayValueModel, TimeStringInputModel, TimeValueModel

FIELD_BACKGROUND = 0xFF23211F
FIELD_TEXT_COLOR = 0xFFD5D5D5
FIELD_TEXT_COLOR_READ_ONLY = 0xFF5C5C5C


class TimeItemValueFieldWidget:
    def __init__(
        self,
        item_model: ui.AbstractItemModel,
        item: ui.AbstractItem,
        value_model: TimeValueModel,
        time_display_model: ui.SimpleStringModel,
        fps_model: ui.SimpleFloatModel,
        *args,
        **kwargs,
    ) -> None:
        """Time edit field."""
        self._item_model = item_model
        self._item = item
        self._value_model = value_model
        self._time_display_model = time_display_model

        self._field: ui.StringField = None
        self._begin_edit_subscription: carb.Subscription = None
        self._end_edit_subscription: carb.Subscription = None
        self._value_change_sub: carb.Subscription = None

        self._display_model = TimeDisplayValueModel(
            parent_model=self._value_model, time_display_model=self._time_display_model, fps_model=fps_model
        )
        self._display_value_change_sub = self._display_model.subscribe_value_changed_fn(self._display_value_changed)

        self._ui_frame = ui.Frame(build_fn=self._build_ui, style=self.style, *args, **kwargs)

        # Start editing when double clicked
        self._ui_frame.set_mouse_double_clicked_fn(self.on_double_click)

    def _build_ui(self):
        with self._ui_frame:
            self._stack = ui.ZStack()
            with self._stack:
                ui.Rectangle()
                self._label = ui.Label(self._display_model.as_string)

    @property
    def style(self):
        return {
            "Label": {
                "color": FIELD_TEXT_COLOR_READ_ONLY if self._value_model.read_only else FIELD_TEXT_COLOR,
                "margin_width": 5,
            },
            "Rectangle": {"background_color": FIELD_BACKGROUND},
        }

    def destroy(self):
        self._item_model = None
        self._item = None
        self._value_model = None
        self._time_display_model = None
        self._begin_edit_subscription = None
        self._end_edit_subscription = None
        self._value_change_sub = None
        self._display_model = None
        self._display_value_change_sub = None
        self._stack = None
        self._label = None
        self._field = None
        self._ui_frame.destroy()

    def on_double_click(
        self,
        x: float,
        y: float,
        button: int,
        key_mod: int,
    ):
        """Called when the user double-clicked the item in TreeView"""
        if button != 0:
            return

        if self._display_model.read_only:
            return

        input_value_model = TimeStringInputModel(self._display_model)
        with self._stack:
            self._field = ui.StringField(input_value_model)

        self._begin_edit_subscription = self._field.model.subscribe_begin_edit_fn(self._on_begin_edit)
        self._end_edit_subscription = self._field.model.subscribe_end_edit_fn(self._on_end_edit)
        self._value_change_sub = self._field.model.subscribe_value_changed_fn(self._on_value_change)
        self._field.visible = True
        self._field.focus_keyboard()

    def _on_begin_edit(self, value_model: TimeStringInputModel):
        self._item_model.begin_edit(self._item)

    def _on_value_change(
        self,
        value_model: TimeStringInputModel,
    ):
        if not value_model.is_valid:
            self._field.set_style({"border_width": 1, "border_color": 0xFF0000FF})
        else:
            self._field.set_style({})

    def _on_end_edit(
        self,
        value_model: TimeStringInputModel,
    ):
        """Called when the user is editing the item and pressed Enter or clicked outside of the item"""
        if value_model.is_valid:
            value_model.commit()
        self._item_model.end_edit(self._item)

        # Cleanup
        self._field.visible = False
        self._field.destroy()

        self._end_edit_subscription = None
        self._begin_edit_subscription = None
        self._value_change_sub = None

    def _display_value_changed(self, value_model: ui.AbstractValueModel):
        self._label.text = value_model.as_string
