# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
import omni.usd
from omni.kit.property.usd.relationship import SelectionWatch
from omni.kit.widget.stage import StageWidget
from pxr import Usd, Sdf
from typing import Callable, List, Optional
from functools import partial
import weakref
from ..anim_preview_model import AnimPreviewModel
from ..compatibility_utils import check_compatibility, is_anim_bound_to_skel, is_anim_compatible_with_skel


class AnimSkelPickerDialog:
    def __init__(
        self,
        anim_model: AnimPreviewModel,
        stage: Usd.Stage,
        on_select_fn: Callable[[List[Usd.Prim]], None],
        main_stage: Optional[Usd.Stage] = None,
        select_skeleton: bool = False
    ):
        self._SKELFILTER_DEFAULT = 1
        self._stage = stage
        self._on_select_fn = on_select_fn
        self._select_skeleton = select_skeleton

        if main_stage is None:
            self._main_stage = omni.usd.get_context().get_stage()
        else:
            self._main_stage = main_stage

        self._stages = []
        self._weak_stages = []
        self._stage_widgets = []
        self._selection_watches = []
        self._filter_type_list = []
        self._anim_model = weakref.ref(anim_model)
        self._filter_lambda_anim = anim_model.is_animation
        self._filter_lambda_skel = anim_model.is_skeleton
        self._filter_lambda_animskel = lambda p: anim_model.is_animation(p) or anim_model.is_skeleton(p)
        self._filter_lambdas = []
        # self._filter_lambda_narrow = filter_lambda_narrow  # TODO

        self._selected_paths = []

        self._anim_select = None
        self._skel_combo = None
        self._skel_filter_combo = None
        self._button = None
        self._selection_labels = []

        def on_window_visibility_changed(visible):
            if not visible:
                for stage_widget in self._stage_widgets:
                    stage_widget.open_stage(None)
            else:
                # Only attach the stage when picker is open. Otherwise the Tf notice listener in StageWidget kills perf
                for i, stage_widget in enumerate(self._stage_widgets):
                    stage_widget.open_stage(self._weak_stages[i]())

        title = "Select Animation and/or Skeleton to load"
        self._window = ui.Window(
            title,
            width=800,
            height=600,
            visible=False,
            flags=0,
            visibility_changed_fn=on_window_visibility_changed,
        )
        self._window.frame.set_build_fn(self._build_ui)

    def _get_load_state(self):
        if self._anim_select:
            load_anim = self._anim_select.model.get_value_as_bool()
        else:
            load_anim = True
        load_skel = self._select_skeleton
        load_skel_from_main = False
        if self._skel_combo:
            # 'No skeleton'
            if self._skel_combo.model.get_item_value_model().as_int == 0:
                load_skel = False
            # 'Load from this file'
            elif self._skel_combo.model.get_item_value_model().as_int == 1:
                load_skel = True
            else:
                load_skel = False
                load_skel_from_main = True
        return load_anim, load_skel, load_skel_from_main

    def _create_filters(self, load_anim, load_skel, load_skel_from_main):
        self._filter_lambdas = []

        filter_mode = self._SKELFILTER_DEFAULT
        if self._skel_filter_combo:
            filter_mode = self._skel_filter_combo.model.get_item_value_model().as_int

        anim_model = self._anim_model()
        if anim_model is None:
            self._filter_lambda_skel = lambda p: True
            self._filter_lambda_animskel = lambda p: True
        elif not load_anim:
            self._filter_lambda_animskel = anim_model.is_skeleton
            self._filter_lambda_skel = anim_model.is_skeleton
        elif filter_mode == 0:
            self._filter_lambda_animskel = lambda p: anim_model.is_animation(p) or anim_model.is_skeleton(p)
            self._filter_lambda_skel = anim_model.is_skeleton
        elif filter_mode == 1:
            self._filter_lambda_animskel = lambda p: anim_model.is_animation(p) or self._filter_compatible_skeletons(p)
            self._filter_lambda_skel = self._filter_compatible_skeletons
        elif filter_mode == 2:
            self._filter_lambda_animskel = lambda p: anim_model.is_animation(p) or self._filter_bound_skeletons(p)
            self._filter_lambda_skel = self._filter_bound_skeletons
        else:
            self._filter_lambda_animskel = lambda p: anim_model.is_animation(p) or self._filter_bound_and_compatible(p)
            self._filter_lambda_skel = self._filter_bound_and_compatible

        filter_file_stage = self._filter_lambda_animskel
        if load_skel and load_anim:
            filter_file_stage = self._filter_lambda_animskel
        elif load_anim:
            filter_file_stage = self._filter_lambda_anim
        else:
            filter_file_stage = self._filter_lambda_skel
        self._filter_lambdas.append(filter_file_stage)

        if load_skel_from_main:
            self._filter_lambdas.append(self._filter_lambda_skel)

    def _is_bound(self, skel_prim: Usd.Prim) -> bool:
        if self._selected_paths[0] is None or skel_prim.GetStage() != self._stage:
            return False
        for prim_path in self._selected_paths[0]:
            anim_prim = self._stage.GetPrimAtPath(prim_path)
            if is_anim_bound_to_skel(skel_prim, anim_prim):
                return True
        return False

    def _is_compatible(self, skel_prim: Usd.Prim) -> bool:
        if self._selected_paths[0] is None:
            return False
        for prim_path in self._selected_paths[0]:
            anim_prim = self._stage.GetPrimAtPath(prim_path)
            if is_anim_compatible_with_skel(skel_prim, anim_prim):
                return True
        return False

    def _filter_bound_skeletons(self, prim: Usd.Prim) -> bool:
        model = self._anim_model()
        if model is None or not model.is_skeleton(prim):
            return False
        return self._is_bound(prim)

    def _filter_compatible_skeletons(self, prim: Usd.Prim) -> bool:
        model = self._anim_model()
        if model is None or not model.is_skeleton(prim):
            return False
        return self._is_compatible(prim)

    def _filter_bound_and_compatible(self, prim: Usd.Prim) -> bool:
        model = self._anim_model()
        if model is None or not model.is_skeleton(prim):
            return False
        return self._is_bound(prim) and self._is_compatible(prim)

    def _apply_stage_settings(self):
        load_anim, load_skel, load_skel_from_main = self._get_load_state()

        for stage_widget in self._stage_widgets:
            stage_widget.destroy()

        self._stages = []
        self._weak_stages = []
        self._selection_watches = []
        self._stage_widgets = []
        self._selection_labels = []
        self._combo_content = ['No skeleton', 'Load from this file']
        self._filter_combo_content = ["All", "Compatible"]
        if load_anim:
            self._stages.append(self._stage)
            self._combo_content.append('Load from main stage')
        elif load_skel:
            self._stages.append(self._stage)
        if load_skel_from_main:
            self._stages.append(self._main_stage)
        else:
            self._filter_combo_content.append("Bound to animation")
            self._filter_combo_content.append("Compatible and bound")
        self._create_filters(load_anim, load_skel, load_skel_from_main)

        for s in self._stages:
            self._weak_stages.append(weakref.ref(s))
        self._selected_paths = [None, None]

        return load_anim, load_skel, load_skel_from_main

    def _build_ui(self):
        load_anim, load_skel, load_skel_from_main = self._apply_stage_settings()

        with self._window.frame:
            with ui.VStack():
                with ui.VStack(height=0):
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        with ui.HStack(alignment=ui.Alignment.LEFT_CENTER, width=0):
                            ui.Label("Load animations")
                            ui.Spacer(width=5)
                            select_anim = True
                            if self._anim_select:
                                select_anim = self._anim_select.model.get_value_as_bool()
                                self._anim_select.destroy()
                            self._anim_select = ui.CheckBox()
                            self._anim_select.model.set_value(select_anim)
                            self._anim_select.model.add_value_changed_fn(self._on_anim_select_changed)
                        with ui.HStack(alignment=ui.Alignment.LEFT_CENTER, width=0):
                            current = 1 if self._select_skeleton else 0
                            if self._skel_combo:
                                current = min(
                                    self._skel_combo.model.get_item_value_model().as_int,
                                    len(self._combo_content) - 1
                                )
                                self._skel_combo.destroy()
                            ui.Spacer(width=20)
                            ui.Label('Skeleton')
                            ui.Spacer(width=10)
                            self._skel_combo = ui.ComboBox(
                                False,
                                *self._combo_content,
                                width=150
                            )
                            self._skel_combo.model.get_item_value_model().set_value(current)
                            self._skel_combo.model.add_item_changed_fn(self._on_skel_combo_changed)
                        with ui.HStack(alignment=ui.Alignment.LEFT_CENTER, width=0):
                            if load_anim and (load_skel or load_skel_from_main):
                                current = self._SKELFILTER_DEFAULT
                                if self._skel_filter_combo:
                                    current = min(
                                        self._skel_filter_combo.model.get_item_value_model().as_int,
                                        len(self._filter_combo_content) - 1
                                    )
                                    self._skel_filter_combo.destroy()
                                ui.Spacer(width=20)
                                ui.Label('Display skeletons')
                                ui.Spacer(width=10)
                                self._skel_filter_combo = ui.ComboBox(
                                    False,
                                    *self._filter_combo_content,
                                    width=150
                                )
                                self._skel_filter_combo.model.get_item_value_model().set_value(current)
                                self._skel_filter_combo.model.add_item_changed_fn(self._on_skel_filter_combo_changed)
                            else:
                                if self._skel_filter_combo:
                                    self._skel_filter_combo.destroy()
                                ui.Pixel(1)
                    ui.Spacer(height=5)
                    ui.Line(height=5)
                    ui.Spacer(height=5)
                with ui.HStack():
                    for i, stage in enumerate(self._stages):
                        with ui.VStack():
                            stage_widget = StageWidget(None, columns_enabled=["Type"])
                            selection_watch = SelectionWatch(
                                stage=stage,
                                on_selection_changed_fn=partial(self._on_selection_changed, i),
                                filter_type_list=self._filter_type_list,
                                filter_lambda=self._filter_lambdas[i],
                            )
                            self._selection_watches.append(selection_watch)
                            stage_widget.set_selection_watch(selection_watch)
                            stage_widget.open_stage(self._weak_stages[i]())
                            stage_widget._filter_by_lambda({"preview_filter": self._filter_lambdas[i]}, True)
                            stage_widget._filter_by_type(self._filter_type_list, True)
                            stage_widget.update_filter_menu_state(self._filter_type_list)
                            self._stage_widgets.append(stage_widget)
                        if i + 1 < len(self._stages):
                            ui.Spacer(width=10)
                with ui.HStack(height=0):
                    with ui.HStack(height=0):
                        label = ui.Label("Selected Animation(s):\n\tNone")
                        self._selection_labels.append(label)
                    with ui.HStack(height=0):
                        label = ui.Label("Selected Skeleton(s):\n\tNone")
                        self._selection_labels.append(label)

                def on_select(weak_self):
                    weak_self = weak_self()
                    if not weak_self:
                        return

                    selected_prims = []
                    for i, selection in enumerate(weak_self._selected_paths):
                        stage = weak_self._stages[i] if len(weak_self._stages) > 1 and i < 2 else weak_self._stages[0]
                        if stage is not None and selection is not None and len(selection) > 0:
                            for path in selection:
                                selected_prim = stage.GetPrimAtPath(Sdf.Path(path))
                                if selected_prim.IsValid():
                                    selected_prims.append(selected_prim)

                    if weak_self._on_select_fn:
                        weak_self._on_select_fn(selected_prims)

                    weak_self._window.visible = False

                with ui.VStack(
                    height=0, style={"Button.Label:disabled": {"color": 0xFF606060}}
                ):
                    self._show_button = None

                    self._button = ui.Button(
                        "Load selection to the preview window",
                        height=10,
                        clicked_fn=partial(on_select, weak_self=weakref.ref(self)),
                        enabled=False
                    )

    def clean(self):
        self._window.set_visibility_changed_fn(None)
        self._window.destroy()
        self._window = None
        self._selection_watches = []
        for stage_widget in self._stage_widgets:
            stage_widget.open_stage(None)
            stage_widget.destroy()
        self._stage_widgets = []
        self._filter_type_list = None
        self._filter_lambdas = []
        self._filter_lambda_anim = None
        self._filter_lambda_skel = None
        self._selected_paths = []
        self._on_select_fn = None
        self._weak_stages = []
        for label in self._selection_labels:
            label.destroy()
        self._selection_labels = []
        if self._anim_select:
            self._anim_select.destroy()
            self._anim_select = None
        self._is_showing_all = True
        if self._skel_combo:
            self._skel_combo.destroy()
            self._skel_combo = None
        if self._skel_filter_combo:
            self._skel_filter_combo.destroy()
            self._skel_filter_combo = None
        if self._show_button:
            self._show_button.destroy()
        self._show_button = None
        self._button.destroy()
        self._button = None
        self._select_skeleton = False

    def show(self):
        self._window.visible = True

    def hide(self):
        self._window.visible = False

    def _on_selection_changed(self, i, paths):
        anim_model = self._anim_model()
        if not anim_model:
            return

        if i == 0:  # anim + skel, file contents
            for i in range(len(self._selected_paths)):
                self._selected_paths[i] = []
            for path in paths:
                prim = self._stage.GetPrimAtPath(path)
                if anim_model.is_animation(prim):
                    self._selected_paths[0].append(path)
                else:
                    self._selected_paths[1].append(path)
            if self._skel_filter_combo and self._skel_filter_combo.model.get_item_value_model().as_int > 0:
                self._on_skel_filter_combo_changed(self._skel_filter_combo.model, None)
        else:  # main stage view
            self._selected_paths[i] = paths

        if self._button:
            self._button.enabled = any(v is not None and len(v) > 0 for v in self._selected_paths)
        if len(self._selection_labels) > 0 and len(self._selected_paths) > 0:
            for i in range(len(self._selected_paths)):
                if self._selected_paths[i]:
                    text = "\n\t".join(self._selected_paths[i])
                else:
                    text = ""
                if 'Animation' in self._selection_labels[i].text:
                    label_text = "Selected Animation(s)"
                else:
                    label_text = "Selected Skeleton(s)"
                label_text += f":\n\t{text if len(text) else 'None'}"
                self._selection_labels[i].text = label_text

    def _on_anim_select_changed(self, model):
        self._window.frame.rebuild()

    def _on_skel_combo_changed(self, model, item):
        self._window.frame.rebuild()

    def _on_skel_filter_combo_changed(self, model, item):
        self._create_filters(*self._get_load_state())
        for i, stage_widget in enumerate(self._stage_widgets):
            stage_widget._filter_by_lambda({"preview_filter": None}, False)
            stage_widget._filter_by_lambda({"preview_filter": self._filter_lambdas[i]}, True)
