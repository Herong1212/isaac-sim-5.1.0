import carb
import omni.kit.commands
import omni.ui as ui
import omni.usd
from omni.kit.window.filepicker import FilePickerDialog
from pxr import Usd, Sdf, Tf, UsdSkel
from .animation_graph_manager import AnimationGraphManager
from .node_graph import NodeGraphRoot
from .stage_picker_dialog import StagePickerDialog
from .utils import get_stage_default_prim_path
from pathlib import Path
from typing import Callable
from functools import partial
from enum import Enum, auto
import os
import queue
import weakref


class CreateAnimationGraphDialog:
    class _SkeletonSource(Enum):
        Invalid = auto()
        Stage = auto()
        Reference = auto()
        Payload = auto()

    def __init__(self, graph_manager: AnimationGraphManager):
        self._graph_manager = graph_manager

        def on_window_visibility_changed(weak_self, visible):
            weak_self = weak_self()
            if not weak_self:
                return
            if visible:
                return
            if self._stage_picker:
                self._stage_picker.hide()
            if self._file_picker:
                self._file_picker.hide()

        self._window = ui.Window(
            "Create Animation Graph",
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR,
            auto_resize=True,
            visible=False,
            visibility_changed_fn=partial(on_window_visibility_changed, weakref.ref(self))
        )

        self._usd_context = omni.usd.get_context()
        self._stage = None
        self._default_prim_path = None
        self._stage_picker = None
        self._file_picker = None
        self._on_create_graph_fn = None
        self._skeleton_source: CreateAnimationGraphDialog._SkeletonSource = \
            CreateAnimationGraphDialog._SkeletonSource.Invalid

        self._graph_path_widget = None
        self._select_skel_buttons = None
        self._skel_path_stack = None
        self._skel_path_widget = None
        self._asset_path_stack = None
        self._asset_type_label = None
        self._asset_path_widget = None
        self._asset_skel_path_widget = None
        self._remove_skel_button = None
        self._window.set_key_pressed_fn(self._on_key_pressed)
        self._window.frame.set_build_fn(self._build_frame)

    def destroy(self):
        self._window.destroy()
        self._window = None
        self._usd_context = None
        self._stage = None
        self._default_prim_path = None

        def destroy_widget(widget):
            if widget:
                widget.destroy()

        if self._stage_picker:
            self._stage_picker.clean()
        self._stage_picker = None
        destroy_widget(self._file_picker)
        self._file_picker = None

        self._on_create_graph_fn = None
        self._skeleton_source = None

        destroy_widget(self._graph_path_widget)
        destroy_widget(self._select_skel_buttons)
        destroy_widget(self._skel_path_stack)
        destroy_widget(self._skel_path_widget)
        destroy_widget(self._asset_path_stack)
        destroy_widget(self._asset_type_label)
        destroy_widget(self._asset_path_widget)
        destroy_widget(self._asset_skel_path_widget)
        destroy_widget(self._remove_skel_button)

        self._graph_path_widget = None
        self._select_skel_buttons = None
        self._skel_path_stack = None
        self._skel_path_widget = None
        self._asset_path_stack = None
        self._asset_type_label = None
        self._asset_path_widget = None
        self._asset_skel_path_widget = None
        self._remove_skel_button = None
        self._graph_manager = None

    def open(self, on_create_graph_fn: Callable[[Usd.Prim], None]):
        self._stage = self._usd_context.get_stage()
        self._default_prim_path = get_stage_default_prim_path(self._stage)

        def on_select_skeleton(weak_self, skeleton_prim):
            weak_self = weak_self()
            if not weak_self:
                return
            if not skeleton_prim:
                return
            weak_self._select_skel_buttons.visible = False
            weak_self._skel_path_stack.visible = True
            weak_self._remove_skel_button.visible = True
            weak_self._skel_path_widget.model.set_value(skeleton_prim.GetPath().pathString)
            weak_self._skeleton_source = weak_self._SkeletonSource.Stage

        if self._stage_picker:
            self._stage_picker.clean()

        self._stage_picker = StagePickerDialog(
            self._stage,
            partial(on_select_skeleton, weakref.ref(self)),
            "Select Skeleton",
            None,
            [UsdSkel.Skeleton]
        )
        self._on_create_graph_fn = on_create_graph_fn
        self._window.frame.rebuild()
        self._window.visible = True

    def _build_frame(self):
        pref_graph_path = f"{self._default_prim_path}/AnimationGraph" if self._stage.HasDefaultPrim() else "/AnimationGraph"
        with ui.VStack(
            width=400,
            height=0,
            spacing=5,
            name="top_level_stack",
            style={"VStack::top_level_stack": {"margin_height": 5}, "Button": {"margin": 0}},
        ):
            with ui.HStack(spacing=5):
                ui.Label("Path", width=0)
                self._graph_path_widget = ui.StringField()
                self._graph_path_widget.identifier = "animation_graph_path"
                self._graph_path_widget.model.set_value(
                    omni.usd.get_stage_next_free_path(
                        self._stage,
                        pref_graph_path,
                        False)
                )
                self._graph_path_widget.focus_keyboard()

            ui.Spacer(height=5)
            with ui.ZStack():
                ui.Rectangle(
                    style={"background_color": 0xff333333, "border_radius": 2.0, "padding": 0, "margin": 0}
                )
                with ui.VStack(
                    name="skel_group",
                    height=0,
                    spacing=5,
                    style={"VStack::skel_group": {"margin_width": 2, "margin_height": 5}}
                ):
                    with ui.HStack():
                        ui.Spacer(width=10)
                        ui.Label("Skeleton")
                    with ui.ZStack():
                        self._select_skel_buttons = ui.HStack(spacing=5)
                        with self._select_skel_buttons:
                            ui.Button("Select From Stage", clicked_fn=self._stage_picker.show)
                            ui.Button("Add Reference", clicked_fn=self._add_asset)
                        with ui.HStack(spacing=5):
                            with ui.ZStack():
                                self._skel_path_stack = ui.VStack(spacing=5, visible=False)
                                with self._skel_path_stack:
                                    with ui.HStack(spacing=5):
                                        ui.Label("Skeleton Path", width=0)
                                        self._skel_path_widget = ui.StringField(read_only=True)
                                self._asset_path_stack = ui.VStack(spacing=5, visible=False)
                                with self._asset_path_stack:
                                    with ui.HStack(spacing=5):
                                        ui.Label("Asset Path", width=0)
                                        self._asset_path_widget = ui.StringField(read_only=True)
                                    with ui.HStack(spacing=5):
                                        ui.Label("Asset Skeleton Path", width=0)
                                        self._asset_skel_path_widget = ui.StringField()
                            path = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(
                                __name__))

                            def on_remove_skel(weak_self):
                                weak_self = weak_self()
                                if not weak_self:
                                    return

                                weak_self._select_skel_buttons.visible = True
                                weak_self._skel_path_stack.visible = False
                                weak_self._asset_path_stack.visible = False
                                weak_self._remove_skel_button.visible = False
                                weak_self._skeleton_source = weak_self._SkeletonSource.Invalid

                            self._remove_skel_button = ui.Button(
                                style={
                                    "image_url": str(path.joinpath("icons").joinpath("remove.svg")),
                                    "margin": 0,
                                    "padding": 0
                                },
                                width=16,
                                clicked_fn=partial(on_remove_skel, weak_self=weakref.ref(self)),
                                visible=False
                            )

            ui.Spacer(height=5)
            with ui.HStack(spacing=5):
                ui.Button("Create", clicked_fn=self._create_graph)
                ui.Button("Cancel", clicked_fn=self._close_window)

    def _add_asset(self):
        def on_file_picked(weak_self, filename: str, dir_name: str):
            weak_self = weak_self()
            if not weak_self:
                return
            reference_path = ""
            if dir_name:
                reference_path = f"{dir_name}{filename}"
            elif filename:
                reference_path = filename

            weak_self._file_picker.hide()

            weak_self._select_skel_buttons.visible = False
            weak_self._asset_path_stack.visible = True
            weak_self._remove_skel_button.visible = True
            weak_self._skeleton_source = weak_self._SkeletonSource.Reference
            weak_self._asset_path_widget.model.set_value(reference_path)

            asset_layer = Sdf.Layer.FindOrOpen(reference_path)
            skeleton_prim_path = None
            if asset_layer.HasDefaultPrim():
                default_prim = asset_layer.GetPrimAtPath(Sdf.Path(f"/{asset_layer.defaultPrim}"))
                if default_prim:
                    specs_to_process = queue.SimpleQueue()
                    specs_to_process.put(default_prim)
                    while not specs_to_process.empty():
                        spec = specs_to_process.get()
                        if spec.typeName == "Skeleton":
                            skeleton_prim_path = spec.path
                            break

                        for child in spec.nameChildren:
                            specs_to_process.put(child)

            if skeleton_prim_path:
                weak_self._asset_skel_path_widget.model.set_value(skeleton_prim_path.pathString)
            else:
                weak_self._asset_skel_path_widget.model.set_value("<No Skeleton Found in Asset!>")

        if self._file_picker:
            self._file_picker.destroy()

        self._file_picker = FilePickerDialog(
            "Select File",
            allow_multi_selection=False,
            apply_button_label="Add Reference",
            click_apply_handler=partial(on_file_picked, weakref.ref(self)),
            item_filter_options=[omni.usd.readable_usd_files_desc()]
        )

        navigate_to = None
        if self._stage and not self._stage.GetRootLayer().anonymous:
            # If asset path is empty, open the USD rootlayer folder
            navigate_to = self._stage.GetRootLayer().identifier

        self._file_picker.show(path=navigate_to)

    def _close_window(self):
        self._window.visible = False

    def _create_graph(self):
        new_path_string = self._graph_path_widget.model.get_value_as_string()
        if not Sdf.Path.IsValidPathString(new_path_string):
            return

        widget_path = Sdf.Path(new_path_string)
        if not widget_path.IsPrimPath():
            return

        self._close_window()

        if not widget_path.IsAbsolutePath():
            widget_path = widget_path.MakeAbsolutePath(self._default_prim_path)

        graph_path = Sdf.Path(
            omni.usd.get_stage_next_free_path(
                self._stage,
                widget_path,
                False)
        )

        def create_asset(command_name):
            asset_path_string = self._asset_path_widget.model.get_value_as_string()
            name = os.path.splitext(Path(asset_path_string).name)[0]
            pref_asset_path = f"{self._default_prim_path}/{Tf.MakeValidIdentifier(name)}" if self._stage.HasDefaultPrim() else f"/{Tf.MakeValidIdentifier(name)}"
            prim_path = omni.usd.get_stage_next_free_path(
                self._stage,
                pref_asset_path,
                False
            )

            omni.kit.commands.execute(
                command_name,
                usd_context=self._usd_context,
                path_to=prim_path,
                asset_path=asset_path_string,
                instanceable=False
            )

            asset_skel_path_string = self._asset_skel_path_widget.model.get_value_as_string()
            if not Sdf.Path.IsValidPathString(asset_skel_path_string):
                return

            asset_skel_path = Sdf.Path(asset_skel_path_string)
            if not asset_skel_path.IsPrimPath():
                return

            return asset_skel_path.ReplacePrefix(asset_skel_path.GetPrefixes()[0], Sdf.Path(prim_path))

        skeleton_path = Sdf.Path.emptyPath
        if self._skeleton_source == self._SkeletonSource.Stage:
            skeleton_path = Sdf.Path(self._skel_path_widget.model.get_value_as_string())
        elif self._skeleton_source == self._SkeletonSource.Reference:
            skeleton_path = create_asset("CreateReference")

        callback_id = None

        def on_create_graph(node_graph: NodeGraphRoot):
            if self._graph_manager and callback_id is not None:
                self._graph_manager.remove_graph_create_callback(callback_id)

            if self._on_create_graph_fn:
                self._on_create_graph_fn(node_graph.prim)

        callback_id = self._graph_manager.add_graph_create_callback(on_create_graph)
        omni.kit.commands.execute("CreateAnimationGraphCommand", path=graph_path, skeleton_path=skeleton_path)

        graph_prim = self._stage.GetPrimAtPath(graph_path)
        if not graph_prim:
            self._graph_manager.remove_graph_create_callback(callback_id)

    def _on_key_pressed(self, key_index, key_mod, key_down):
        if key_index == int(carb.input.KeyboardInput.ENTER) and key_down:
            self._create_graph()
