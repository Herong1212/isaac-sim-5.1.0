# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import os
from dataclasses import dataclass
from typing import *

import carb
import omni.usd
import omni.kit.app
import omni.kit.ui
import omni.ui as ui
import carb.input
import omni.appwindow
import omni.kit.notification_manager as nm
from omni.kit.helper.file_utils.asset_types import get_icon
from .anim_preview_widget import PlayMode, AnimPreviewWidget
from .dialog.stage_picker import StagePickerDialog
from .dialog.anim_skel_picker import AnimSkelPickerDialog
from .progress_window import ProgressWindow
from omni.kit.window.drop_support import ExternalDragDrop
from pxr import Ar, Gf, Pcp, Usd, UsdGeom, UsdSkel, Sdf
from .anim_preview_model import AnimPreviewModel, XFORM_OP_ROTATE_UNITSRESOLVE_ATTR, XFORM_OP_SCALE_UNITSRESOLVE_ATTR
from .file_loader import FileLoader
from .usd_helper import get_first_in_stage, is_skeleton

__all__ = ['AnimPreviewWindow']

MODULE_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
WINDOW_MENU = "Window/Animation/Animation Preview"
SETTINGS_SHOW_WINDOW = "/exts/omni.anim.retarget.preview/show_window"

SKELANIM_ICON = get_icon("a.skelanim.usd")
SKEL_ICON = get_icon("a.skel.usd")
FILE_ICON = get_icon("a.usd")


@dataclass
class SceneClipInfo:
    roots: List[Usd.Prim]
    clips: List[Usd.Prim]

    def has_skeleton(self, prim_name:str) -> bool:
        return bool(len([x for x in self.roots if x.GetName() == prim_name]))

    def has_clip(self, prim_name:str) -> bool:
        return bool(len([x for x in self.clips if x.GetName() == prim_name]))


def data_from_stage(stage:Usd.Stage) -> SceneClipInfo:
    result = SceneClipInfo([], [])

    if not bool(stage):
        # Extensions create windows before the stage context is available
        return result

    for prim in stage.Traverse():
        if prim.IsA(UsdSkel.Skeleton):
            result.roots.append(prim)
        elif prim.IsA(UsdSkel.Animation):
            result.clips.append(prim)

    def should_keep(prim:Usd.Prim) -> bool:
        parent = prim.GetParent()
        while parent and not parent.GetTypeName() == "BehaviorMotionLibrary":
            parent = parent.GetParent()
        return not bool(parent)

    ## remove anything with BehaviorMotionLibrary parents-- we
    ## don't want to be seeing that skeleton
    result.roots = list(filter(should_keep, result.roots))
    return result


class AnimPreviewWindow(ui.Window):
    def __init__(self, title: str, preview_context_name: str = '', window_width: int = 1280,
                 window_height: int = 720 + 20, flags: int = ui.WINDOW_FLAGS_NO_SCROLLBAR):
        """AnimPreviewWindow constructor
        Args:
            title (str): The name of the Window.
            preview_context_name (str): The name of a UsdContext this Viewport will be viewing.
            window_width(int): The width of the Window.
            window_height(int): The height of the Window.
            flags(int): ui.WINDOW flags to use for the Window.
            *vp_args, **vp_kw_args: Additional arguments to pass to the AnimPreviewWidget
        """

        self._model:AnimPreviewModel = AnimPreviewModel(preview_context_name)
        self.__file_loader:FileLoader = FileLoader(preview_context_name)

        settings = carb.settings.get_settings()
        settings.set_default_bool(SETTINGS_SHOW_WINDOW, False)
        show_window = settings.get_as_bool(SETTINGS_SHOW_WINDOW)

        super().__init__(title, width=window_width, height=window_height, flags=flags, visible=show_window)
        editor_menu = omni.kit.ui.get_editor_menu()
        self._menu = None
        if editor_menu:
            if editor_menu.has_item(WINDOW_MENU):
                omni.kit.ui.get_editor_menu().set_value(WINDOW_MENU, show_window)
            self._menu = editor_menu.add_item(WINDOW_MENU, self._on_menu_click, toggle=True, value=show_window)

        self.set_visibility_changed_fn(self._visibility_changed_fn)

        self.frame.set_build_fn(self._build_ui)
        # self.frame.height = ui.Percent(100)
        self.auto_resize = True

        appwindow = omni.appwindow.get_default_app_window()
        self.__mouse = appwindow.get_mouse()
        self.__input = carb.input.acquire_input_interface()

        self.frame.set_drop_fn(self._on_drop)
        self.frame.set_accept_drop_fn(self._accept_drop)
        self.frame.set_mouse_hovered_fn(self._mouse_hovered)

        self.__viewport_play_mode_old = None
        self._showing_notice = False

        # Handle drop from external application windows (e.g. file explorer)
        self.__external_dragdrop = ExternalDragDrop(window_name=title,
                                                    drag_drop_fn=self._on_external_drag_drop)

        self._model.register_animation_changed(self._refresh_hint_visibility)
        self._model.register_skeleton_changed(self._refresh_hint_visibility)

        self.deferred_dock_in("Property")

        self._preview_widget:AnimPreviewWidget = None
        self._anim_picker = None
        self._skeleton_picker = None
        self._progress_window = None
        self.__drop_loading = False
        self.__message_window = False
        self._hint_stack = None
        self.__dropping_url = None
        self.__show_file_load_picker = False
        self.__active_drop_target = None

        self._scrollframe = None

        self._scene_clip_info = None
        self._populate_scene_info()

    def __del__(self):
        self.destroy()

    def rebuild(self):
        self.frame.rebuild()

    @property
    def preview_widget(self) -> AnimPreviewWidget:
        return self._preview_widget

    @property
    def model(self) -> AnimPreviewModel:
        return self._model

    def destroy(self):
        if self._menu:
            omni.kit.ui.get_editor_menu().remove_item(WINDOW_MENU)
            self._menu = None
        if self.__message_window:
            self.__message_window.destroy()
        if self._preview_widget:
            self._preview_widget.destroy()
            self._preview_widget = None
        if self._anim_picker:
            self._anim_picker.clean()
            self._anim_picker = None
        if self._skeleton_picker:
            self._skeleton_picker.clean()
            self._skeleton_picker = None
        if self._progress_window:
            self._progress_window.clean()
            self._progress_window = None
        if self._model:
            self._model.destroy()
            self._model = None
        self.__dropping_url = None
        if self.__file_loader:
            self.__file_loader.destroy()
            self.__file_loader = None
        self.__external_dragdrop = None

        super().destroy()

    def _populate_scene_info(self):
        stage = omni.usd.get_context().get_stage()
        self._scene_clip_info = data_from_stage(stage)
        if self._preview_widget:
            self._preview_widget.update_from_stage(stage)
            self._preview_widget.update_selectors()
            self._preview_widget.rebuild()

    def _valid_anim_drop(self, url) -> bool:
        paths = str(url)
        path_list = paths.splitlines()

        anim_count = 0
        for path in path_list:
            if self._is_valid_animation(path):
                anim_count += 1
        if anim_count >= 1:
            return True

        return False

    def _valid_skel_drop(self, url) -> bool:
        paths = str(url)
        path_list = paths.splitlines()

        skel_count = 0
        for path in path_list:
            if self._is_valid_skeleton(path):
                skel_count += 1
        if skel_count >= 1:
            return True

        return False

    def _accept_drop(self, url):
        # NOTE: This is just to preserve the hovering functionality
        self.__dropping_url = url
        accept = True
        return accept

    def get_all_external_files(self, stage:Usd.Stage):
        result = []
        for prim in stage.Traverse():
            if prim.HasAuthoredPayloads() or prim.HasAuthoredReferences():
                arcs = [x for x in Usd.PrimCompositionQuery(prim).GetCompositionArcs()
                            if x.GetArcType() in (Pcp.ArcTypePayload,  Pcp.ArcTypeReference)]
                for arc in arcs:
                    result.append(os.path.abspath(str(arc.GetTargetLayer().resolvedPath)))

        return result

    def _add_file(self, path:str) -> bool:
        stage = omni.usd.get_context().get_stage()
        stage_up = UsdGeom.GetStageUpAxis(stage)
        meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage) or 0.01

        all_files = self.get_all_external_files(stage)

        if path in all_files:
            # We've already had this file payloaded in, so skip it
            carb.log_warn(f"-- File {path} already in scene.")
            return False

        drop_stage = Usd.Stage.Open(path)
        if not bool(drop_stage):
            carb.log_error(f"-- Dropped file not a valid stage: {drop_stage}")
            return False

        default_prim = drop_stage.GetDefaultPrim()
        drop_stage_up = UsdGeom.GetStageUpAxis(drop_stage)
        drop_meters_per_unit = UsdGeom.GetStageMetersPerUnit(drop_stage) or 0.01

        default_prim_base = str(default_prim.GetPath())
        default_prim_base = default_prim_base[1:] if default_prim_base[0] == "/" else default_prim_base
        root_prim = stage.GetPrimAtPath("/World")
        default_prim_name = default_prim_base[:]
        index = 1

        while bool(root_prim.GetPrimAtPath(default_prim_name)):
            default_prim_name = f"{default_prim_base}_{index:02d}"
            index += 1

        target_prim_path = root_prim.GetPath().AppendChild(default_prim_name)
        target_prim_xfo = UsdGeom.Xform.Define(stage, target_prim_path)
        target_prim = target_prim_xfo.GetPrim()
        references = target_prim.GetReferences()
        references.AddReference(drop_stage.GetRootLayer().realPath, default_prim.GetPath())

        if not stage_up == drop_stage_up:
            if not target_prim.HasAttribute(XFORM_OP_ROTATE_UNITSRESOLVE_ATTR):
                rotateX_op = target_prim_xfo.AddRotateXOp(opSuffix='unitsResolve')
            if drop_stage_up == UsdGeom.Tokens.z and stage_up == UsdGeom.Tokens.y:
                rotateX_op.Set(-90)
            elif drop_stage_up == UsdGeom.Tokens.y and stage_up == UsdGeom.Tokens.z:
                rotateX_op.Set(90)
            else:
                rotateX_op.Set(0)

        scale = drop_meters_per_unit/meters_per_unit
        if not Gf.IsClose(scale, 1.0, 1e-2):
            if not target_prim.HasAttribute(XFORM_OP_SCALE_UNITSRESOLVE_ATTR):
                scale_op = target_prim_xfo.AddScaleOp(opSuffix='unitsResolve')
            scale_op.Set(Gf.Vec3d(scale, scale, scale))

        drop_stage.Unload()
        del drop_stage

        # With the target prim dropped, process it.
        self._add_prim(stage, target_prim)

        return True

    def _add_prim(self, stage:Usd.Stage, prim:Usd.Prim) -> bool:
        if not bool(prim):
            carb.log_warn("-- Specified prim is not valid.")
            return False

        if prim.IsA(UsdSkel.Animation):
            return self._drop_anim_prim(stage, prim)
        elif prim.IsA(UsdSkel.Skeleton) or prim.IsA(UsdSkel.Root):
            return self._drop_skel_prim(stage, prim)
        else:
            # If someone drops the root prim and it's not one of the
            # above, Traverse() until you find the first child that's
            # one of the above, preferencing skeletons.
            for child in Usd.PrimRange(prim):
                if child.IsA(UsdSkel.Skeleton) or child.IsA(UsdSkel.Root):
                    return self._drop_skel_prim(stage, child)
                elif child.IsA(UsdSkel.Animation):
                    return self._drop_anim_prim(stage, child)

        return False

    def _is_supported_file(self, path:str) -> bool:
        return path.endswith((".usd", ".usda", ".usdc", ".usdz"))

    def _on_drop(self, url):
        resolver = Ar.GetResolver()
        stage = omni.usd.get_context().get_stage()

        paths_list = filter(lambda x: len(x.strip()) > 0, str(url).split("\n"))

        for path in paths_list:
            resolved = str(resolver.Resolve(path))
            if (resolved == os.path.abspath(path)) or "://" in resolved:
                self._add_file(resolved)
            else:
                prim = stage.GetPrimAtPath(path)
                if bool(prim):
                    self._add_prim(stage, prim)

        # TODO: this is probably called in too many places.
        self._restore_after_drag()

    def set_skel_prim(self, prim:str):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim)
        self._drop_skel_prim(stage, prim)

    def _drop_anim_prim(self, stage:Usd.Stage, prim:Usd.Prim) -> bool:
        path_str = str(prim.GetPrimPath())
        if self._is_valid_animation(path_str, stage):
            # This will always result in the last animation in the list actually being selected
            self._set_preview_anim(path_str, stage)
            if self._preview_widget:
                self._preview_widget.update_from_stage(stage)
                self._preview_widget._clip_prim_selector.set_value(path_str, run_callbacks=False)
                self._preview_widget.rebuild()
            self._hint_stack.visible = False
            return True
        return False

    def _drop_skel_prim(self, stage:Usd.Stage, prim:Usd.Prim):
        path_str = str(prim.GetPrimPath())
        if self._is_valid_skeleton(path_str, stage):
            self._model.set_preview_skeleton(path_str)
            if self._preview_widget:
                self._preview_widget.update_from_stage(stage)
                self._preview_widget._skeleton_prim_selector.set_value(path_str, run_callbacks=False)
                self._preview_widget.rebuild()
            return True
        return False

    def _drop_file(self, url, show_picker):
        paths = str(url)
        path_list = paths.splitlines()
        if self.__file_loader.is_supported_file(path_list[0]):
            if len(path_list) == 1:
                self.__show_file_load_picker = show_picker
                path = path_list[0]
                if self.__file_loader.is_supported_file(path):
                    if not self.__drop_loading:
                        self.__drop_loading = True
                        # TODO: move loading to window.
                        self._preview_widget.show_loading(True)
                        self.__file_loader.load_file_async(path, self._on_file_loaded)
            else:
                asyncio.ensure_future(self._load_files_batch(path_list))

    def _on_external_drag_drop(self, edd: ExternalDragDrop, payload: List[str]):
        if payload is not None and len(payload) > 0:
            file_path = payload[0]
            if self.__file_loader.is_supported_file(file_path):
                if not self.__drop_loading:
                    self.__drop_loading = True
                    self._preview_widget.show_loading(True)
                    self.__file_loader.load_file_async(file_path, self._on_file_loaded)

    def _is_valid_skeleton(self, path, stage=None) -> bool:
        """ Checks whether the prim at path exists in stage and is a supported skeleton animation
        """
        if stage is None:
            stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(path)

        if prim is None:
            return False

        # TODO: utility library
        if not self._model._is_valid_skeleton(prim, path):
            return False

        return True

    def _is_valid_animation(self, path, stage=None) -> bool:
        """ Checks whether the prim at path exists in stage and is a supported skeleton animation
        """
        if stage is None:
            stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(path)

        if prim is None:
            return False

        # TODO: utility library
        if not self._model.is_animation(prim):
            return False

        # TODO: Compatibility checks (maybe)

        return True

    def _on_batch_next_file_loaded(self, external_url: str, success: bool, root: str):
        # TODO: this should load skeletons
        stage = self.__file_loader.get_stage()

        try:
            prims = stage.Traverse()
        except:
            self.__bg_loading = False
            return
        anims = []
        for prim in prims:
            if self._model.is_animation(prim):
                anims.append(prim)

        for anim in anims:
            self._on_anim_selected(anim, external_url, False)

        self.__bg_loading = False

    async def _load_files_batch(self, path_list: List[str]):
        """ Loads multiple files in the background
        """
        if self.__drop_loading:
            return
        self.__drop_loading = True
        self._preview_widget.show_loading(True)

        if not self._progress_window:
            self._progress_window = ProgressWindow(title="Loading animations...", item_str='animation')
        self._progress_window.reset()
        self._progress_window.show()
        for i, path in enumerate(path_list):
            self._progress_window.set_current_item(f'({i+1}/{len(path_list)}) {path}')
            if self.__file_loader.is_supported_file(path):
                self.__bg_loading = True
                self.__file_loader.load_file_async(path, self._on_batch_next_file_loaded)
                while self.__bg_loading:
                    await omni.kit.app.get_app().next_update_async()
            self._progress_window.set_progress(float(i + 1) / len(path_list))
        self._progress_window.set_current_item('completed.')

        self._preview_widget.show_loading(False)
        self.__drop_loading = False

    def _on_file_loaded(self, external_url: str, success: bool, root: str):
        """ Called when a dropped file was successfully loaded
            We browse its contents, find skeleton animations, and show a selection window if indicated
        """
        self._preview_widget.show_loading(False)

        self.__drop_loading = False
        stage = self.__file_loader.get_stage()

        try:
            prims = stage.Traverse()
        except:
            return

        anims = []
        skeletons = []
        for prim in prims:
            if self._model.is_animation(prim):
                anims.append(prim)
            elif self._model.is_skeleton(prim):
                skeletons.append(prim)

        # Nothing to load.
        if len(anims) == 0 and len(skeletons) == 0:
            nm.post_notification(
                "The selected file has no skeleton animations or skeletons.",
                status=nm.NotificationStatus.WARNING,
            )
            return

        # When not showing the picker, load everything possible.
        if not self.__show_file_load_picker:
            all_loadable = anims + skeletons
            self._on_anim_skel_selected(all_loadable, external_url)
            return

        if len(anims) == 0:
            self._skeleton_picker = StagePickerDialog(
                stage,
                lambda p: self._on_skeleton_selected(p, None, stage, external_skel_url=external_url),
                "Select Skeleton (the file has no animations)",
                "Load Selection to the Animation Preview window",
                [],
                [],
                lambda p: self._model.is_skeleton(p)
            )
            self._skeleton_picker.show()
            return

        if self._anim_picker:
            self._anim_picker.clean()

        self._anim_picker = AnimSkelPickerDialog(
            anim_model=self.model,
            stage=stage,
            on_select_fn=lambda p: self._on_anim_skel_selected(p, external_url),
            main_stage=omni.usd.get_context().get_stage(),
            select_skeleton=False,
        )
        self._anim_picker.show()

    def _on_anim_skel_selected(self, prim_list, external_url: str = None, set_current: bool = True):
        """ Called when the user selected an animations and/or skeletons from the selection window
        """
        skeleton_prims = [prim for prim in prim_list if self.model.is_skeleton(prim)]
        # TODO: do not make the first ones current, only the last one
        for skeleton_prim in skeleton_prims:
            path = skeleton_prim.GetPath()
            stage = skeleton_prim.GetStage()
            self._model.set_preview_skeleton(path, stage, external_url)

        animation_prims = [prim for prim in prim_list if self.model.is_animation(prim)]
        for i in range(0, len(animation_prims) - 1):
            path = animation_prims[i].GetPath()
            stage = animation_prims[i].GetStage()
            self._model.set_preview_anim(path, stage, external_url, set_current=False)

        if len(animation_prims) > 0:
            path = animation_prims[-1].GetPath()
            stage = animation_prims[-1].GetStage()
            self._model.set_preview_anim(path, stage, external_url, set_current=True)

        self._refresh_hint_visibility()

    def _get_stage_and_prim(self, path:str) -> (Usd.Stage, Usd.Prim):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(path)
        return stage, prim

    def _skeleton_prim_selector_on_changed_cb(self, prim_name:str):
        if prim_name == "":
            if self._model.timeline.is_playing():
                self._model.pause()

            # We have to remove both here because if you don't, the
            # default skeleton comes in posed but not connected to the meshes.
            self._model.remove_skeletons()
            self._model.remove_animations()

            if self._preview_widget:
                self._preview_widget._skeleton_prim_selector.set_value("", run_callbacks=False)
                self._preview_widget._clip_prim_selector.set_value("", run_callbacks=False)
                self._preview_widget.rebuild()
                self._hint_stack.visible = True
            return

        stage, prim = self._get_stage_and_prim(str(prim_name))
        self._drop_skel_prim(stage, prim)

    def _clip_prim_selector_on_changed_cb(self, prim_name:str):
        if prim_name == "":
            if self._model.timeline.is_playing():
                self._model.pause()
            self._model.remove_animations()
            self._preview_widget.rebuild()
            return

        stage, prim = self._get_stage_and_prim(str(prim_name))
        self._drop_anim_prim(stage, prim)

    def _on_anim_selected(self, prim, external_url: str = None, set_current: bool = True):
        """ Called when the user selected an animation from the selection window (or it was automatically selected)
        """

        if not prim.IsValid():
            print('Invalid prim: ' + prim.GetPath())  # should not happen
            return
        stage = self.__file_loader.get_stage()
        path = prim.GetPath()
        if self._is_valid_animation(path, stage):
            self._set_preview_anim(path, stage, external_url, set_current)

        self._refresh_hint_visibility()

    def _on_skeleton_selected(self, skeleton_path, anim_path, stage, external_anim_url: str = None, external_skel_url: str = None):
        """ Called when the user selected a skeleton from the selection window
        """
        if anim_path is not None:
            self._model.set_preview_anim(anim_path, stage, external_anim_url)
        self._model.set_preview_skeleton(skeleton_path, stage, external_skel_url)

        self._refresh_hint_visibility()

    def _set_preview_anim(self, path: str, stage, external_url: str = None, set_current: bool = True):
        """ Sets the previewed animation
        Args:
            path (str): Path to the source animation prim
            stage: Source stage of the animation prim
            external_url: URL to the source file or None if the source is an open stage (e.g. the main)
        """
        # !TODO: handle failures?
        success = self._model.set_preview_anim(path, stage, external_url)
        self._refresh_hint_visibility()

    def _restore_after_drag(self):
        """ Restore state after drag and drop was ended
        """
        self._model.select_skeleton(False)
        self.__dropping_url = None
        if self.__viewport_play_mode_old is not None and self.__viewport_play_mode_old == PlayMode.PLAY:
            self._model.play()
            self.__viewport_play_mode_old = None

        if self.__active_drop_target:
            self.__active_drop_target.set_active(False)
            self.__active_drop_target = None

        self._refresh_hint_visibility()

    def _is_dragging(self) -> bool:
        """ Returns whether we are dragging something to the window
        """
        # NOTE: does not work for external drag and drop
        # NOTE: returns False when the mouse was first hovered over the window (_mouse_hovered)
        return self.__dropping_url is not None

    def _mouse_hovered(self, is_hovered: bool):
        """ Mouse hover callback
        """
        is_dragging = False
        if is_hovered:
            if self.__input.get_mouse_value(self.__mouse, carb.input.MouseInput.LEFT_BUTTON) > 0.5 and self._preview_widget:
                is_dragging = True
                self.__viewport_play_mode_old = self._preview_widget.play_mode
                if self.__viewport_play_mode_old == PlayMode.PLAY:
                    self._model.pause()
        else:
            self.__dropping_url = None
        if not is_dragging:
            self._restore_after_drag()

    def _on_menu_click(self, *args):
        self.visible = not self.visible

    def _visibility_changed_fn(self, visible):
        if not visible:
            self.model.reset_scene()
        omni.kit.ui.get_editor_menu().set_value(WINDOW_MENU, visible)

    def _refresh_hint_visibility(self, **kwargs):
        show_hint = not self._model.skeleton_prim
        if self._hint_stack is not None:
            self._hint_stack.visible = show_hint

    async def _delete_skel_source_cb(self):
        await omni.kit.app.get_app().next_update_async()
        self.rebuild()

    def _build_ui(self):
        icon_style = {"width": 24, "height":24, "margin":0, "padding": 0}

        self._scrollframe = ui.ScrollingFrame(
            width=ui.Percent(100),
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF
        )

        with self._scrollframe:
            with ui.ZStack():
                # Viewport and Buttons
                self._preview_widget = AnimPreviewWidget(parent=self, preview_model=self._model)

                # Because the viewport widget and timeline both use content_clipping, we need a separate_window to render on top.
                with ui.Frame(separate_window=1):
                    with ui.ZStack():
                        # Hint Text (display at start, when nothing's loaded)
                        self._hint_stack = ui.ZStack(visible=True)
                        with self._hint_stack:
                            ui.Rectangle(style={"background_color": 0x55000000})
                            with ui.VStack():
                                ui.Spacer()
                                with ui.HStack(height=24, margin=0, padding=0):
                                    with ui.HStack(style=icon_style):
                                        ui.Image(SKEL_ICON)
                                    ui.Label("Drag and drop Character\nor Animation to preview.", style={"font_size": 24, "alignment": ui.Alignment.CENTER})
                                    with ui.HStack(style=icon_style):
                                        ui.Image(SKELANIM_ICON)
                                ui.Spacer()
                            self._refresh_hint_visibility()

        self._restore_after_drag()

    @property
    def is_hint_stack_visible(self) -> bool:
        return self._hint_stack.visible
