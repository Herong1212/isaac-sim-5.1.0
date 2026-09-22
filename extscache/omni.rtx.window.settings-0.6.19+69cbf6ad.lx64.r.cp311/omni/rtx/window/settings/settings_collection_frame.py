__all__ = ["SettingsCollectionFrame"]

from typing import Any, Union

import carb.settings
import omni.kit.commands
import omni.rtx.window.settings
import omni.ui as ui
import rtx.settings
from omni.kit.widget.settings import (
    SettingsSearchableCombo,
    SettingsWidgetBuilder,
    SettingType,
    create_setting_widget,
    create_setting_widget_combo,
)


class FrameSessionState:
    """
    stre any state we would like to persist across the Session
    """

    frame_state = {}

    @classmethod
    def get_state(cls, frame_id: str, key: str) -> Any:
        if frame_id not in cls.frame_state:
            return None
        if key not in cls.frame_state[frame_id]:
            return None
        return cls.frame_state[frame_id][key]

    @classmethod
    def has_state(cls, frame_id: str, key: str) -> bool:
        if frame_id not in cls.frame_state:
            return False
        if key not in cls.frame_state[frame_id]:
            return False
        return True

    @classmethod
    def set_state(cls, frame_id: str, key: str, value: Any) -> None:
        if frame_id not in cls.frame_state:
            cls.frame_state[frame_id] = {}
        cls.frame_state[frame_id][key] = value


class SettingsCollectionFrame:

    parents = {}  # For later deletion of parents

    def __init__(self, frame_label: str, collapsed=True, parent=None) -> None:
        self.classNamespace = ".".join([self.__class__.__module__, self.__class__.__name__])
        self._settings = carb.settings.get_settings()
        self._collapsedState = collapsed
        self._setting_path = self._frame_setting_path()
        if FrameSessionState.has_state(self.classNamespace, "collapsed"):
            self._collapsedState = FrameSessionState.get_state(self.classNamespace, "collapsed")

        self._widget = ui.CollapsableFrame(
            frame_label,
            height=0,
            build_fn=self.build_ui,
            build_header_fn=self.build_header,
            skip_draw_when_clipped=True,
            collapsed=self._collapsedState,
        )
        self._widget.identifier = frame_label
        self._widget.set_collapsed_changed_fn(self.on_collapsed_changed)
        self.sub_widgets = []
        self.sub_models = []

        # store a reference to our parent to allow later destruction
        if parent:
            if parent in self.parents:
                self.parents[parent].append(self)
            else:
                self.parents[parent] = [self]

    def _frame_setting_path(self):
        """subclass can overtide that to get a checkbox in the frame"""
        return None

    def destroy(self):
        """
        We need to explicitly destroy widgets/models -  there's usually a number of circular ref
        between model and Widget which can be difficult to track down and keep widgets alive
        after the Frame is rebuilt
        """
        for w in self.sub_models:
            w.destroy()
        self.sub_models = []

        for w in self.sub_widgets:
            del w
        self.sub_widgets = []

        self._widget.set_collapsed_changed_fn(None)
        self._widget.set_build_fn(None)
        self._widget.clear()
        self._widget = None

    def _on_change(self, *_):
        self._rebuild()

    def on_collapsed_changed(self, collapsed):
        FrameSessionState.set_state(self.classNamespace, "collapsed", collapsed)

    def build_header(self, collapsed, title):
        triangle_alignment = ui.Alignment.RIGHT_CENTER
        triangle_width = 4
        triangle_height = 6
        if not collapsed:
            triangle_alignment = ui.Alignment.CENTER_BOTTOM
            triangle_width = 7
            triangle_height = 5

        with ui.HStack(height=20, style={"HStack": {"margin_height": 5}}):
            ui.Spacer(width=5)
            with ui.VStack(width=15):
                ui.Spacer()
                ui.Triangle(
                    alignment=triangle_alignment,
                    name="title",
                    width=triangle_width,
                    height=triangle_height,
                    # Using the style defined in style.py"
                    # style={"background_color": 0xFFCCCCCC},
                )
                ui.Spacer()

            ui.Label(title, name="title", width=0)
            ui.Spacer()
            if self._setting_path:
                with ui.VStack(width=20, content_clipping=True):
                    ui.Spacer(height=4)
                    widget, model = create_setting_widget(self._setting_path, SettingType.BOOL)
                    if widget and model:
                        widget.set_tooltip("Check to Activate")

                        def expand_frame(model, frame):
                            if frame:
                                frame.collapsed = not model.get_value_as_bool()

                        model.add_value_changed_fn(lambda m, frame=self._widget: expand_frame(m, frame))

                        ui.Spacer()

    def build_ui(self):
        with ui.VStack(height=0, spacing=5, style={"VStack": {"margin_width": 10}}):
            ui.Spacer(height=5)
            self._build_ui()
            ui.Spacer(height=5)

    def _rebuild(self):
        if self._widget:
            self._widget.rebuild()

    def _restore_defaults(self, path: str):
        omni.kit.commands.execute("RestoreDefaultSetting", path=path)

    def _add_setting(
        self,
        setting_type,
        name: str,
        path: str,
        range_from=0,
        range_to=0,
        speed=1,
        has_reset=True,
        tooltip="",
        hard_range=False,
        cleartext_path=None,
    ):
        the_stack = ui.HStack(skip_draw_when_clipped=True)
        the_stack.identifier = "HStack_" + name.replace(" ", "_")
        with the_stack:
            SettingsWidgetBuilder._create_label(name, path if not cleartext_path else cleartext_path, tooltip)
            widget, model = create_setting_widget(
                path, setting_type, range_from, range_to, speed, hard_range=hard_range
            )
            self.sub_widgets.append(widget)
            self.sub_models.append(model)
            if has_reset:
                button = SettingsWidgetBuilder._build_reset_button(path)
                model.set_reset_button(button)

        return widget

    def _add_internal_setting(
        self, setting_type, name: str, path: str, range_from=0, range_to=0, speed=1, has_reset=True, tooltip=""
    ):
        internal_path = rtx.settings.get_internal_setting_string(path)
        return self._add_setting(
            setting_type, name, internal_path, range_from, range_to, speed, has_reset, tooltip, cleartext_path=path
        )

    def _add_setting_combo(
        self,
        name: str,
        path: str,
        items: Union[list, dict],
        callback=None,
        has_reset=True,
        tooltip="",
        cleartext_path=None,
        allow_non_items: bool = False,
    ):
        the_stack = ui.HStack(skip_draw_when_clipped=True)
        the_stack.identifier = "HStack_" + name.replace(" ", "_")
        with the_stack:
            SettingsWidgetBuilder._create_label(name, path if not cleartext_path else cleartext_path, tooltip)
            widget, model = create_setting_widget_combo(path, items, allow_non_items=allow_non_items)
            self.sub_widgets.append(widget)
            self.sub_models.append(model)
            if has_reset:
                button = SettingsWidgetBuilder._build_reset_button(path)
                model.set_reset_button(button)
        return widget, model

    def _add_setting_searchable_combo(self, name: str, path: str, items: dict, default_item: str, tooltip=""):
        with ui.HStack():
            SettingsWidgetBuilder._create_label(name, path, tooltip)
            widget = SettingsSearchableCombo(path, items, default_item)
            self.sub_widgets.append(widget)

    def _add_internal_setting_combo(
        self, name: str, path: str, items: Union[list, dict], callback=None, has_reset=True, tooltip=""
    ):
        internal_path = rtx.settings.get_internal_setting_string(path)
        return self._add_setting_combo(name, internal_path, items, callback, has_reset, tooltip, cleartext_path=path)

    def _get_internal_setting(self, path: str):
        return self._settings.get(rtx.settings.get_internal_setting_string(path))

    def _subscribe_to_internal_setting_change(self, path: str):
        omni.kit.app.SettingChangeSubscription(rtx.settings.get_internal_setting_string(path), self._on_change)

    def _build_ui(self):
        """virtual function that will be called in the Collapsable frame"""
        pass
