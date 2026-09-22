# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from functools import partial

import omni.ui as ui
import omni.usd
from omni.kit.property.usd.relationship import SelectionWatch
from omni.kit.widget.stage import StageWidget

from .core import VariantEditorCore


class StageWindowButton:
    _picker_core_instance = None

    def __init__(
        self,
        filter_by_text=False,
        filter_type_list=[],
        label="",
        on_select_fn=None,
        tooltip_fn=None,
        style=None,
        style_type_name_override="",
        targets_limit=1,
        width=90,
        fn_target_path=None,
    ):
        self.__add_button = None
        self.__filter_by_text = filter_by_text
        self.__label = None
        self.__on_select_fn = on_select_fn
        self.__selected_paths = []
        self.__stage_widget = None
        self.__filter_type_list = filter_type_list
        self.__stage_button = None
        self.__targets_limit = targets_limit
        self.__window = None
        self.__fn_target_path = fn_target_path
        if style is not None:
            self.__stage_button = ui.Button(
                label,
                clicked_fn=partial(self._on_click),
                tooltip_fn=tooltip_fn,
                style=style,
                style_type_name_override=style_type_name_override,
                width=width,
            )
        else:
            self.__stage_button = ui.Button(
                label,
                clicked_fn=partial(self._on_click),
                tooltip_fn=tooltip_fn,
                style_type_name_override=style_type_name_override,
                width=width,
            )
        if not self.__on_select_fn:
            self.enabled = False
        self.__selection_watcher = None

    def __del__(self):
        if self.__stage_widget:
            self.__stage_widget.open_stage(None)
            self.__stage_widget.destroy()
            self.__add_button = None
        self.__label = None
        self.__selected_paths = None
        self.__stage_widget = None
        self.__window = None
        self.__selection_watcher = None

    def _on_click(self):
        if not VariantEditorCore.get_instance().validate_variant_edit():
            return

        stage = omni.usd.get_context().get_stage()
        if self.__on_select_fn and (self.__targets_limit > 0) and stage:
            window_title = "Select Target Prim"
            if self.__targets_limit > 1:
                window_title = "Select Prims"
            self.__window = ui.Window(window_title, width=400, height=400, visible=True, flags=ui.WINDOW_FLAGS_MODAL)
            with self.__window.frame:
                with ui.VStack():
                    with ui.Frame():
                        self.__stage_widget = StageWidget(None, columns_enabled=["Type"])
                        self.__stage_widget.open_stage(stage)
                        if self.__fn_target_path:

                            def _is_descendant_prim(prim, fn_prefix=self.__fn_target_path):
                                prefix = fn_prefix()
                                # if prefix is None or an invalid string, fallback to True
                                return prim.GetPath().HasPrefix(fn_prefix()) if prefix else True

                            # register a filter to stage widget
                            self.__stage_widget._filter_by_lambda({"_is_descendant_prim": _is_descendant_prim}, True)
                        if self.__filter_by_text:
                            self.__stage_widget._filter_by_text(
                                VariantEditorCore.get_instance()._get_root_prim_path().pathString
                            )
                        self.__selection_watcher = SelectionWatch(
                            stage, partial(self.__on_selection_changed), self.__filter_type_list, None
                        )
                        self.__stage_widget.set_selection_watch(self.__selection_watcher)
                        self.__selection_watcher.reset(self.__targets_limit)
                    with ui.VStack(height=0, style={"Button.Label:disabled": {"color": 0xFF606060}}):
                        self.__label = ui.Label("Selected Path(s):\n\tNone")
                        self.__add_button = ui.Button("Select", height=10, clicked_fn=self.__on_select, enabled=False)

    def __on_select(self):
        self.__on_select_fn(self.__selected_paths)
        self.__window.visible = False

    def hide(self):
        if self.__window:
            self.__window.visible = False

    def show(self):
        if self.__window:
            self.__window.visible = True

    def __on_selection_changed(self, paths):
        self.__selected_paths = paths
        if self.__add_button:
            self.__add_button.enabled = len(self.__selected_paths) > 0
        if self.__label:
            text = "\n\t".join(paths)
            label_text = "Selected Path"
            if len(self.__selected_paths) > 1:
                label_text = "Selected Paths"
            if self.__targets_limit == 1:
                label_text += f" ({len(self.__selected_paths)}/{self.__targets_limit})"
            elif self.__targets_limit > 0:
                label_text += f" ({len(self.__selected_paths)})"
            label_text += f":\n\t{text if len(text) else 'None'}"
            self.__label.text = label_text

    @property
    def enabled(self):
        return self.__stage_button.enabled

    @enabled.setter
    def enabled(self, enabled):
        self.__stage_button.enabled = enabled


class RootSelector:
    _selector_core_instance = None

    def __init__(self, filter_type_list=[], on_select_fn=None, targets_limit=1):
        self.__add_button = None
        self.__label = None
        self.__on_select_fn = on_select_fn
        self.__selected_paths = []
        self.__stage_widget = None
        self.__filter_type_list = filter_type_list
        self.__stage_button = None
        self.__targets_limit = targets_limit
        self.__window = None

        # Startup
        stage = omni.usd.get_context().get_stage()
        window_title = "Select Target Prim"
        self.__window = ui.Window(window_title, width=400, height=400, visible=True, flags=ui.WINDOW_FLAGS_MODAL)
        with self.__window.frame:
            with ui.VStack():
                with ui.Frame():
                    self.__stage_widget = StageWidget(None, columns_enabled=["Type"])
                    self.__stage_widget.open_stage(stage)
                    self.__selection_watcher = SelectionWatch(
                        stage, partial(self.__on_selection_changed), self.__filter_type_list, None
                    )
                    self.__stage_widget.set_selection_watch(self.__selection_watcher)
                    self.__selection_watcher.reset(self.__targets_limit)
                with ui.VStack(height=0, style={"Button.Label:disabled": {"color": 0xFF606060}}):
                    self.__label = ui.Label("Selected Path(s):\n\tNone")
                    self.__add_button = ui.Button("Select", height=10, clicked_fn=self.__on_select, enabled=False)

    def __del__(self):  # pragma: no cover
        if self.__stage_widget:
            self.__stage_widget.open_stage(None)
            self.__stage_widget.destroy()
        self.__label = None
        self.__selected_paths = None
        self.__add_button = None
        self.__stage_widget = None
        self.__window = None
        self.__selection_watcher = None

    def __on_select(self):
        self.__on_select_fn(self.__selected_paths)
        self.__window.visible = False

    def __on_selection_changed(self, paths):
        self.__selected_paths = paths
        if self.__add_button:
            self.__add_button.enabled = len(self.__selected_paths) > 0
        if self.__label:
            text = "\n\t".join(paths)
            label_text = "Selected Path"
            if len(self.__selected_paths) > 1:
                label_text = "Selected Paths"
            if self.__targets_limit > 0:
                label_text += f" ({len(self.__selected_paths)}/{self.__targets_limit})"
            label_text += f":\n\t{text if len(text) else 'None'}"
            self.__label.text = label_text
