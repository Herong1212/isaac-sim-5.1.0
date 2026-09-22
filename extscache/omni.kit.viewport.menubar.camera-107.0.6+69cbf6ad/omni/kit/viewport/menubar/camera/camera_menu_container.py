# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["CameraMenuContainer"]

import concurrent.futures
import functools
from functools import partial
from dataclasses import dataclass, fields, field
import traceback
from typing import Callable, Dict, List, Optional, Set, TYPE_CHECKING, Tuple
import weakref

import carb
from carb.eventdispatcher import get_eventdispatcher
import omni.ui as ui
import omni.usd
import omni.kit.commands
import omni.timeline
from omni.kit.async_engine import run_coroutine
from omni.kit.viewport.menubar.core import (
    ViewportMenuDelegate,
    SeparatorDelegate,
    ViewportMenuContainer,
    USDAttributeModel,
    USDFloatAttributeModel,
    menu_is_tearable,
    MenuDisplayStatus
)
from pxr import Sdf, Tf, Trace, Usd, UsdGeom

from .camera_list_delegate import CameraListDelegate
from .camera_widget_delegate_manager import CameraWidgetDelegateManager
from .commands import SetViewportCameraCommand
from .menu_item.lens import CameraLens
from .menu_item.focal_distance import CameraFocalDistance
from .menu_item.fstop import CameraFStop
from .menu_item.auto_exposure import CameraAutoExposure
from .menu_item.single_camera_menu_item import SingleCameraMenuItem, NoCameraMenuItem
from .menu_item.expand_menu_item import ExpandMenuItem
from .style import UI_STYLE
from .utils import SESSION_CAMERAS, get_camera_display


if TYPE_CHECKING:
    from .menu_item.single_camera_menu_item import SingleCameraMenuItemBase


CAMERA_LOCK_NAME = "omni:kit:cameraLock"
CAMERA_ACTIONS_MAP = {
    "omni.kit.viewport.actions::perspective_camera": "/OmniverseKit_Persp",
    "omni.kit.viewport.actions::top_camera": "/OmniverseKit_Top" ,
    "omni.kit.viewport.actions::front_camera": "/OmniverseKit_Front",
    "omni.kit.viewport.actions::right_camera": "/OmniverseKit_Right",
}


def handle_exception(func):
    """
    Decorator to print exception in async functions
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:  # noqa: PLW0718
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


def _show_camera_in_menu(prim: Usd.Prim):
    return prim and prim.IsA(UsdGeom.Camera) and not omni.usd.editor.is_hide_in_ui(prim)


class _CameraList:
    """The object that watches USD for the list of cameras"""

    def __init__(self, stage, callback):
        self.__stage: Usd.Stage = stage
        self.__callback: Callable[[], None] = callback
        self.__cameras: Set[Sdf.Path] = set()
        self.__listener = None
        self.__dirty = True
        self.__camera_filters = carb.settings.get_settings().get("/exts/omni.kit.viewport.menubar.camera/filters") or []

        self.__usdrt_stage = self.__get_usd_rt_stage(stage)
        self.__listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.__on_usd_changed, stage) if stage else None
        self.__dirty_prim_paths: Set[Sdf.Path] = set()
        self.__prim_changed_task: Optional[concurrent.futures.Future] = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__listener:
            self.__listener.Revoke()
            self.__listener = None
        if self.__prim_changed_task:
            self.__prim_changed_task.cancel()
            self.__prim_changed_task = None

    @property
    def is_dirty(self):
        return self.__dirty

    @property
    def camera_list(self) -> List[Sdf.Path]:
        # If it's called the first time, we just iterate the whole USD stage for cameras
        # Note the cast to bool is important in case self.__stage is not None, but also an invalid stage
        was_dirty, self.__dirty = self.__dirty, False
        has_stage = bool(self.__stage)
        if was_dirty and has_stage:
            self.__cameras: Set[Sdf.Path] = set()
            if self.__usdrt_stage:
                for prim_path in self.__usdrt_stage.GetPrimsWithTypeName("Camera"):
                    usd_prim = self.__stage.GetPrimAtPath(prim_path.GetString())
                    if _show_camera_in_menu(usd_prim) and self.__filter(usd_prim):
                        self.__cameras.add(usd_prim.GetPath())
            else:
                # If it's called the first time, we just iterate the whole USD stage for cameras
                # Note the cast to bool is important in case self.__stage is not None, but also an invalid stage
                predicate = Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded)
                for usd_prim in self.__stage.Traverse(predicate):
                    if _show_camera_in_menu(usd_prim) and self.__filter(usd_prim):
                        self.__cameras.add(usd_prim.GetPath())

        return self.__cameras

    def __filter(self, camera_prim: Usd.Prim) -> bool:
        path = camera_prim.GetPath().pathString
        return all(not path.startswith(filter_path) for filter_path in self.__camera_filters)

    @staticmethod
    def __get_usd_rt_stage(stage: Usd.Stage):
        if carb.settings.get_settings().get("/exts/omni.kit.viewport.menubar.camera/primQuery/useUsdRt"):
            try:
                from pxr import UsdUtils
                from usdrt import Usd as UsdRtUsd

                stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
                fabric_active_for_stage = UsdRtUsd.Stage.StageWithHistoryExists(stage_id)
                if fabric_active_for_stage:
                    return UsdRtUsd.Stage.Attach(stage_id)
            except ImportError:
                pass
        return None

    @Trace.TraceFunction
    def __on_usd_changed(self, notice: Tf.Notice, stage: Usd.Stage):
        """Called by Usd.Notice.ObjectsChanged"""
        if not bool(self.__stage) or stage != self.__stage:
            return

        dirty_prims_paths: List[Sdf.Path] = []

        for p in notice.GetResyncedPaths():
            if p.IsAbsoluteRootOrPrimPath():
                dirty_prims_paths.append(p)

        if not dirty_prims_paths:
            return

        self.__dirty_prim_paths.update(dirty_prims_paths)

        # Update in the next frame. We need it because we want to accumulate the affected prims
        if self.__prim_changed_task is None or self.__prim_changed_task.done():
            self.__prim_changed_task = run_coroutine(self.__delayed_prim_changed())

    @handle_exception
    @Trace.TraceFunction
    async def __delayed_prim_changed(self):
        """
        Create/remove dirty items that was collected from TfNotice. Can be
        called any time to pump changes.
        """
        # OMPE-54754: Because this is called async, the stage may have changed after the check in __on_usd_changed, so
        # here we should skip update if stage has changed; This fixes crash in UsdStage.GetPrimAtPath in line 192, an
        # example of such crash can be viewd at omnicrashes with uuid 92088195-c188-463a-9d87-11de0207ee1f
        if not bool(self.__stage) or omni.usd.get_context().get_stage() != self.__stage:
            return
        # Swap the dirty list to a local and reset the instance state
        dirty = False
        dirty_prim_paths, self.__dirty_prim_paths = self.__dirty_prim_paths, set()
        removed_camera, added_camera = None, None

        for path in dirty_prim_paths:
            prim = self.__stage.GetPrimAtPath(path)
            if _show_camera_in_menu(prim):
                # Changed or created
                self.__cameras.add(path)
                added_camera = path
                dirty = True
            else:
                # Removed or changed type
                try:
                    self.__cameras.remove(path)
                    removed_camera = path
                except KeyError:
                    pass
                dirty = True

        # For the case with one event that represents and removal and addition of a camera, pass it along as -hint-.
        # There could be fals-positives (a layer event where only one camera is gone and one added), but even in
        # that case hinting to the Viewport what to do (leave camera if removed camera was active) isn't horrible.
        if len(dirty_prim_paths) != 2 or (removed_camera is None) or (added_camera is None):
            removed_camera, added_camera = None, None

        if dirty:
            self.__dirty = True
            self.__callback(removed_camera, added_camera)

        self.__prim_changed_task = None


@dataclass
class MenuContext:
    root_menu: ui.Menu = None
    delegate: ui.MenuDelegate = None
    settings_menu: ui.Menu = None
    settings_container: ui.ZStack = None
    settings_width: int = 0
    expand_container: ui.ZStack = None
    expand_item: ExpandMenuItem = None
    expand_width: int = 0
    expand_model: ui.SimpleBoolModel = None
    saved_expand = False
    camera_collection: ui.MenuItemCollection = None
    camera_path: str = None

    selected_camera_item: ui.MenuItem = None
    camera_list: Optional[_CameraList] = None
    stage_sub: carb.Subscription = None
    stage_closing_sub: carb.Subscription = None
    expanded_sub: carb.Subscription = None
    render_settings_changed_sub: carb.Subscription = None
    lock_menu_sub: carb.Subscription = None

    settings_items: List[ui.MenuItem] = field(default_factory=list)
    camera_to_menu: Dict[Sdf.Path, Tuple[SingleCameraMenuItem, bool]] = field(default_factory=dict)

    def __init__(self, **kwargs):
        names = {f.name for f in fields(self)}
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
        if not hasattr(self, "settings_items"):
            self.settings_items = []
        if not hasattr(self, "camera_to_menu"):
            self.camera_to_menu = {}


class CameraMenuContainer(ViewportMenuContainer):
    """The menu with the list of cameras"""

    def __init__(self):
        super().__init__(
            name="Camera",
            delegate=None,
            visible_setting_path="/exts/omni.kit.viewport.menubar.camera/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.camera/order",
            expand_setting_path="/exts/omni.kit.viewport.menubar.camera/expand",
            style=UI_STYLE,
            actions_map=CAMERA_ACTIONS_MAP,
        )
        self.__menu_item_type = SingleCameraMenuItem
        self.__lock_models: Dict[Sdf.Path, USDAttributeModel] = {}
        self.__menu_context: Dict[int, MenuContext] = {}
        self._create_menu_item_fns: List[List[Callable[["viewport_context", ui.Menu], None]], int] = []  # noqa: F821
        self.register_menu_item(self._build_camera_collections, -100)
        self.register_menu_item(self._build_create_camera, -90)

        self.__custom_camera_widget_delegate_manager = CameraWidgetDelegateManager()
        self.__expanded_sub = None  # noqa: PLW0238
        self.__force_check_task_or_future = None  # noqa: PLW0238
        self.__hide_camera_settings_task_or_future = None  # noqa: PLW0238

    def set_menu_item_type(self, menu_item_type: Callable[..., "SingleCameraMenuItemBase"]):
        """
        Set the menu type for the default created camera

        Args:
            menu_item_type: callable that will create the menu item
        """
        if not menu_item_type:
            menu_item_type = SingleCameraMenuItem
        if self.__menu_item_type != menu_item_type:
            self.__menu_item_type = menu_item_type
            self.__full_invalidate()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.__lock_models = {}
        for context in self.__menu_context.values():
            context.expanded_sub = None
            context.lock_menu_sub = None
            if context.render_settings_changed_sub:
                context.render_settings_changed_sub.destroy()
                context.render_settings_changed_sub = None

        self.__custom_camera_widget_delegate_manager.destroy()

        super().destroy()

    def __full_invalidate(self):
        for context in self.__menu_context.values():
            context.root_menu.invalidate()
            context.settings_menu.invalidate()

    def get_display_status(self, factory_args: Dict) -> MenuDisplayStatus:
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        if context.expand_container.visible:
            return MenuDisplayStatus.EXPAND
        if context.delegate.text_visible:
            return MenuDisplayStatus.LABEL
        return MenuDisplayStatus.MIN

    def get_require_size(self, factory_args: Dict, expand: bool = False) -> float:
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        display_status = self.get_display_status(factory_args)
        if expand:
            if display_status == MenuDisplayStatus.EXPAND:
                return 0
            return context.settings_width + context.expand_width if display_status == MenuDisplayStatus.LABEL else context.delegate.text_size

        if display_status == MenuDisplayStatus.EXPAND:
            return 0 if context.expand_model.as_bool else context.settings_width
        return 0 if display_status == MenuDisplayStatus.LABEL else context.delegate.text_size

    def expand(self, factory_args: Dict) -> None:
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        if context.expand_container.visible:
            return
        if context.delegate.text_visible:
            context.expand_model.set_value(context.saved_expand)
            context.expand_container.visible = True
        else:
            context.delegate.text_visible = True
            if context.root_menu:
                context.root_menu.invalidate()

    def can_contract(self, factory_args: Dict) -> bool:
        display_status = self.get_display_status(factory_args)
        return display_status in (MenuDisplayStatus.LABEL, MenuDisplayStatus.EXPAND)

    def contract(self, factory_args: Dict) -> bool:
        viewport_api_id = factory_args['viewport_api'].id
        if viewport_api_id not in self.__menu_context:
            return False
        context = self.__menu_context[viewport_api_id]

        display_status = self.get_display_status(factory_args)
        if display_status == MenuDisplayStatus.EXPAND:
            context.saved_expand = context.expand_model.as_bool
            context.expand_model.set_value(False)
            context.expand_container.visible = False
            return True
        if display_status == MenuDisplayStatus.LABEL:
            context.delegate.text_visible = False
            if context.root_menu:
                context.root_menu.invalidate()
            return True
        return False

    def register_menu_item(self, create_menu_item_fn: Callable[["viewport_context", ui.Menu], None], order: int = 0):  # noqa: F821
        self._create_menu_item_fns.append((create_menu_item_fn, order))
        self.__full_invalidate()

    def deregister_menu_item(self, create_menu_item_fn: Callable[["viewport_context", ui.Menu], None]):  # noqa: F821
        found = [item for item in self._create_menu_item_fns if item[0] == create_menu_item_fn]
        if found:
            for item in found:
                self._create_menu_item_fns.remove(item)
            self.__full_invalidate()

    def build_fn(self, viewport_context: Dict):
        """Entry point for the menu bar"""
        viewport_api = viewport_context.get('viewport_api')
        viewport_api_id = viewport_api.id
        # Empty out any existing menu objects
        self.__menu_context[viewport_api_id] = MenuContext(
            delegate=CameraListDelegate(viewport_api, self.__custom_camera_widget_delegate_manager)
        )
        # Get a local reference to the new mapped value
        _menu_context = self.__menu_context[viewport_api_id]

        _menu_context.root_menu = ui.Menu(menu_compatibility=False, delegate=_menu_context.delegate, style=self._style)
        _menu_context.root_menu.set_on_build_fn(lambda *args, **kwargs: self._build_menu(viewport_context))

        # The Camera property widgets selection menu
        _menu_context.settings_container = ui.ZStack(width=0)
        with _menu_context.settings_container:
            ui.Rectangle(style_type_name_override="Menu.Item.Background")
            with ui.HStack(width=0):
                ui.Spacer(width=5)
                _menu_context.settings_menu = ui.Menu(menu_compatibility=False, direction=ui.Direction.LEFT_TO_RIGHT, style=self._style)
                _menu_context.settings_menu.set_on_build_fn(lambda *args, **kwargs: self._build_expand(viewport_context))
                ui.Spacer(width=5)

        def __on_settings_changed(vp_api_id):
            menu_context = self.__menu_context[vp_api_id]
            menu_context.settings_width = max(menu_context.settings_width, menu_context.settings_container.computed_content_width)

        _menu_context.settings_container.set_computed_content_size_changed_fn(partial(__on_settings_changed, viewport_api_id))

        # Delay a frame to hide camera settings if required to get settings width for contract/expand when startup
        _menu_context.expand_model = ui.SimpleBoolModel(self.expand_model.as_bool)

        async def __hide_camera_settings_async(menu_context):
            await omni.kit.app.get_app().next_update_async()
            menu_context.settings_container.visible = menu_context.expand_model.as_bool
        if not self.expand_model.as_bool:
            self.__hide_camera_settings_task_or_future = run_coroutine(__hide_camera_settings_async(_menu_context))  # noqa: PLW0238

        # Menu to expand/contract camera properties
        _menu_context.expand_container = ui.ZStack(width=0, height=0, style={"padding": 0, "margin": 0})
        with _menu_context.expand_container:
            with ui.Menu(menu_compatibility=False, direction=ui.Direction.LEFT_TO_RIGHT, style=self._style):
                _menu_context.expand_item = ExpandMenuItem(_menu_context.expand_model)

        def __on_expand_changed(*args, **kwargs):
            menu_context = self.__menu_context[viewport_api_id]
            menu_context.expand_width = max(menu_context.expand_width, menu_context.expand_container.computed_content_width)

        _menu_context.expand_container.set_computed_content_size_changed_fn(__on_expand_changed)

        def __on_toggle_expand(*args, **kwargs):
            menu_context = self.__menu_context[viewport_api_id]
            menu_context.settings_container.visible = menu_context.expand_model.as_bool
            menu_context.expand_item.checked = menu_context.expand_model.as_bool

            # Reset global expand status
            # Once at least one expanded, set global expanded
            # Otherwise, set global callpased
            self.__unsub_global_expand()
            if menu_context.expand_model.as_bool:
                self.expand_model.set_value(True)
            else:
                expand = False
                for menu_context in self.__menu_context.values():
                    if menu_context.expand_model.as_bool:
                        expand = True
                        break
                self.expand_model.set_value(expand)
            self.__sub_global_expand()

        _menu_context.expanded_sub = _menu_context.expand_model.subscribe_value_changed_fn(__on_toggle_expand)

        self.__sub_global_expand()

        # When stage opened, rebuild the root menu
        def on_stage_opened(_):
            camera_path = self.__ensure_valid_camera(viewport_api, viewport_api.camera_path)
            if camera_path:
                viewport_api.camera_path = camera_path
            menu_context = self.__menu_context.get(viewport_api_id)
            if menu_context:
                menu_context.root_menu.invalidate()
                menu_context.settings_menu.invalidate()

        _menu_context.stage_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.viewport.menubar.camera:camera_menu_container",
            event_name=viewport_api.usd_context.stage_event_name(omni.usd.StageEventType.OPENED),
            on_event=on_stage_opened
        )

        # OMPE-54754: On stage closing, we should clear _CameraList, this also cancels the __delayed_prim_changed task
        def on_stage_closing(_):
            menu_context = self.__menu_context.get(viewport_api_id, None)
            if menu_context and menu_context.camera_list:
                menu_context.camera_list.destroy()

        _menu_context.stage_closing_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.viewport.menubar.camera:camera_menu_container.stage_closing",
            event_name=viewport_api.usd_context.stage_event_name(omni.usd.StageEventType.CLOSING),
            on_event=on_stage_closing
        )
        # Clear out this reference to validate its not being held or used by any callback
        _menu_context = None

    def __render_settings_changed(self, camera_path: Sdf.Path, resolution: Tuple[int, int], viewport_api):
        # The Viewport may have switched to a new camera before out camera list was dirtied
        context = self.__menu_context[viewport_api.id]
        if context.camera_to_menu.get(camera_path) is None:
            # Rebuild but don't check camera validity; the Viewport is sending us the path it is rendering with
            self.__rebuild_cameras(viewport_api, False)
        self.__camera_changed(camera_path, viewport_api)

    def __camera_clicked(self, camera_path: Sdf.Path, viewport_api):
        context = self.__menu_context[viewport_api.id]
        if context.camera_path != camera_path:
            SetViewportCameraCommand(camera_path, viewport_api).do()
            return

        # Force the check state back on as it's being toggled off
        async def force_check(viewport_api_id):
            selected_cam_item = self.__menu_context[viewport_api_id].selected_camera_item
            if selected_cam_item and not selected_cam_item.checked:
                selected_cam_item.checked = True
        self.__force_check_task_or_future = run_coroutine(force_check(viewport_api.id))  # noqa: PLW0238

    def __camera_changed(self, camera_path: Sdf.Path, viewport_api):
        context = self.__menu_context[viewport_api.id]
        if context.camera_path == camera_path:
            cam_item = context.camera_to_menu.get(camera_path)
            if cam_item and not cam_item.checked:
                cam_item.checked = True
            return

        # Save the current state now
        context.camera_path = camera_path

        # Uncheck anything that is currently selected
        selected_cam_item = context.selected_camera_item
        if selected_cam_item:
            selected_cam_item.checked = False
            selected_cam_item = None

        # There is also chance the Camera was changed to an item that doesn't exist
        cam_item = context.camera_to_menu.get(camera_path)
        if cam_item:
            context.selected_camera_item = cam_item
            # And reset the check state on the new selection
            cam_item.checked = True

        # Update the root menu item
        if context.delegate:
            context.delegate.text = get_camera_display(camera_path, viewport_api.stage)

        # Toggle the cam collection marker accordingly
        context.camera_collection.checked = str(camera_path) not in SESSION_CAMERAS
        # Need to update the lock item to new camera
        self.__build_lock_item(viewport_api, camera_path)
        # Update the active Camera's property widgets by rebuilding them
        if context:
            context.settings_menu.invalidate()

    def __build_lock_item(self, viewport_api, camera_path: Sdf.Path):
        stage = viewport_api.stage
        # Lock menu sub is always destroyed
        context = self.__menu_context.get(viewport_api.id, None)
        context.lock_menu_sub = None

        # Possibly no path, so clear any state
        if not camera_path:
            self.__lock_models = {}
            if context and context.delegate:
                context.delegate.model = None
                context.delegate.camera_path = None
            return

        context.delegate.camera_path = camera_path
        lock_model = self.__get_lock_model(stage, camera_path)
        if context and context.delegate:
            context.delegate.model = lock_model
        if lock_model:
            context.lock_menu_sub = lock_model.subscribe_value_changed_fn(lambda m, api=viewport_api: self._on_lock_changed(m, api))

    def __get_lock_model(self, stage: Usd.Stage, camera_path: Sdf.Path):
        if camera_path not in self.__lock_models:
            if camera_path.pathString in ("/OmniverseKit_Persp", "/OmniverseKit_Front", "/OmniverseKit_Top", "/OmniverseKit_Right"):
                return None
            # Lock - Should probably use meta-data, but that needs to be added into allowed-metadata schema
            # self.__lock_models[camera_path] = USDMetadataModel(stage, camera_path, CAMERA_LOCK_NAME)
            self.__lock_models[camera_path] = USDAttributeModel(stage, camera_path, CAMERA_LOCK_NAME)
        return self.__lock_models.get(camera_path)

    def __get_session_camera_paths(self, stage: Usd.Stage):
        session_camera_paths = [Sdf.Path(path_str) for path_str in SESSION_CAMERAS]
        if stage:
            session_camera_paths = [path for path in session_camera_paths if stage.GetPrimAtPath(path)]
        return session_camera_paths

    def _build_cameras(self, viewport_api, session_cameras: bool, ui_shown: bool = False, force_build: bool = False):
        """Build the menu with the list of the cameras"""
        context = self.__menu_context.get(viewport_api.id, None)
        if (not session_cameras) and (not force_build):
            camera_collection = context.camera_collection
            if not camera_collection.shown and not camera_collection.teared:
                return

        if session_cameras:
            camera_list = self.__get_session_camera_paths(viewport_api.stage)
        elif context.camera_list.is_dirty:
            def sorting_key(sdf_path: Sdf.Path):
                # Sort based on parentPath/displayName which may lead to an invalid Sdf.Path durring AppendChild
                display_name = get_camera_display(sdf_path, viewport_api.stage)
                return f"{sdf_path.GetParentPath().pathString}/{display_name}".lower()
            camera_list = context.camera_list.camera_list
            camera_list = sorted(camera_list, key=sorting_key)
            camera_list = [path for path in camera_list if path.pathString not in SESSION_CAMERAS]
            context.camera_collection.clear()
        else:
            # If nothing changed, menu should be up-to-date
            return
        stage = viewport_api.stage

        # Check that the current camera path is valid
        current_camera = viewport_api.camera_path
        valid_camera_path = self.__ensure_valid_camera(viewport_api, current_camera)
        if valid_camera_path and (valid_camera_path != current_camera):
            current_camera = valid_camera_path
            viewport_api.camera_path = current_camera

        # Clear any selected selected_cam_item now, its going to be an invalid item soon
        if context and context.selected_camera_item:
            context.selected_camera_item.checked = False
            context.selected_camera_item = None

        class MenuParentContext:
            def __enter__(self, *args, **kwargs):
                return context.camera_collection.__enter__(*args, **kwargs) if not session_cameras else None

            def __exit__(self, *args, **kwargs):
                return context.camera_collection.__exit__(*args, **kwargs) if not session_cameras else None

        with MenuParentContext():
            if session_cameras or camera_list:

                # Show hotkey placeholder for menuitems if hotkey in any menuitem
                show_hotkey_placeholder = any(self._get_menu_item_hotkey_text(str(camera_path)) for camera_path in camera_list)

                for camera_path in camera_list:
                    checked = current_camera == camera_path

                    menu_item = self.__menu_item_type(
                        camera_path,
                        viewport_api,
                        self.__get_lock_model(stage, camera_path),
                        context.root_menu,
                        lambda camera_path=camera_path: self.__camera_clicked(camera_path, viewport_api),
                        self.__custom_camera_widget_delegate_manager,
                        hotkey_text=self._get_menu_item_hotkey_text(str(camera_path)),
                        show_hotkey_placeholder=show_hotkey_placeholder,
                    )
                    context.camera_to_menu[camera_path] = menu_item
                    if checked:
                        context.selected_camera_item = menu_item
            else:
                NoCameraMenuItem()

        # Call camera_changed for the case the camera menu has been invalidated
        context.camera_path = None
        self.__camera_changed(current_camera, viewport_api)

    def __rebuild_cameras(self, viewport_api, check_validity: bool = False, removed_camera: Sdf.Path = None, added_camera: Sdf.Path = None):
        context = self.__menu_context.get(viewport_api.id, None)
        camera_collection = context.camera_collection
        if camera_collection and (camera_collection.shown or camera_collection.teared):
            # Force a rebuild of the stage cameras now
            camera_collection.invalidate()
            camera_collection.clear()
            self._build_cameras(viewport_api, False, True, True)

        if not check_validity:
            return

        camera_path = viewport_api.camera_path
        # If there was a single re-synch event where this camera was removed, and a new one added, go to added
        valid_camera_path = self.__ensure_valid_camera(viewport_api, added_camera if removed_camera == camera_path else camera_path)
        if valid_camera_path and (valid_camera_path != camera_path):
            viewport_api.camera_path = valid_camera_path

    def __ensure_valid_camera(self, viewport_api, camera_path: Sdf.Path):
        stage = viewport_api.stage
        if not stage:
            return camera_path

        def validate_camera(camera_path):
            if camera_path:
                prim = stage.GetPrimAtPath(camera_path)
                # OM-59033: It does not need the followed camera to be shown in the camera list by checking
                # _show_camera_in_menu(prim) as follow user mode in live session needs this to switch
                # camera binding dynamically without adding the camera into camera list.
                if prim:
                    return Sdf.Path(camera_path)
            return None

        # Check if the camera_path is actually a valid camera_path
        camera_path = validate_camera(camera_path)
        if camera_path:
            return camera_path

        # Check if the info is held in the stage metadata.
        try:
            # Wrap in a try-catch so failure reading metadata does not cascade to caller.
            camera_path = validate_camera(stage.GetMetadataByDictKey('customLayerData', 'cameraSettings:boundCamera'))
            if camera_path:
                return camera_path
        except Tf.ErrorException as e:
            carb.log_error(f"Error reading Usd.Stage's boundCamera metadata {e}")

        # Fallback to implicit Perspective if possible (it is deterministic)
        camera_path = validate_camera('/OmniverseKit_Persp')
        if camera_path:
            return camera_path

        # Finally, try an pass the first valid camera in the list
        context = self.__menu_context[viewport_api.id]
        if context and context.camera_list:
            for known_camera in context.camera_list.camera_list:
                camera_path = validate_camera(known_camera)
                if camera_path:
                    return camera_path

        return None

    def _build_camera_collections(self, viewport_context, root: ui.Menu):
        viewport_api = viewport_context.get("viewport_api")
        context = self.__menu_context.get(viewport_api.id, None)
        if context.camera_list:
            context.camera_list.destroy()

        context.camera_list = _CameraList(viewport_api.stage, partial(self.__rebuild_cameras, viewport_api, True))

        # Clear out the Camera-path to MenuItem mapping
        context.camera_to_menu = {}

        # Verify current camera exists, changing it if it does not
        camera_path = viewport_api.camera_path
        valid_camera_path = self.__ensure_valid_camera(viewport_api, camera_path)
        if valid_camera_path and (valid_camera_path != camera_path):
            camera_path = valid_camera_path
            viewport_api.camera_path = camera_path

        # Order views
        session_cameras = self.__get_session_camera_paths(viewport_api.stage)

        tearable = menu_is_tearable("omni.kit.viewport.menubar.camera.Cameras")
        context.camera_collection = ui.MenuItemCollection(
            "Cameras",
            checkable=True,
            checked=camera_path not in session_cameras,
            delegate=ViewportMenuDelegate(),
            shown_changed_fn=partial(self._build_cameras, viewport_api, False),
            tearable=tearable,
            hide_on_click=False
        )

        def reset_checked():
            context.camera_collection.checked = str(viewport_api.camera_path) in SESSION_CAMERAS
        context.camera_collection.set_triggered_fn(reset_checked)

        # XXX: This isn't sticking from the usage in constructor
        context.camera_collection.tearable = tearable

        self._build_cameras(viewport_api, True)

        ui.Separator()

    def _build_create_camera(self, viewport_context, root: ui.Menu):
        viewport_api = viewport_context.get("viewport_api")
        ui.MenuItem(
            "Create from View",
            delegate=ViewportMenuDelegate(icon_name="Add"),
            triggered_fn=lambda *args, **kwargs: self._create_from_view(viewport_api),
            hide_on_click=False
        )

    def _build_menu(self, viewport_context):
        """Build the first level menu"""
        # Create a weak-reference to the active Camera menu; this will be passed to registered build functions
        viewport_api = viewport_context.get("viewport_api")
        context = self.__menu_context.get(viewport_api.id, None)
        cam_menu = weakref.proxy(context.root_menu)
        context.camera_path = viewport_api.camera_path

        # Need to watch for external changes to Viewport's camera, this is delivered in a render-settings change.
        if context.render_settings_changed_sub:
            context.render_settings_changed_sub.destroy()
            context.render_settings_changed_sub = None
        context.render_settings_changed_sub = viewport_api.subscribe_to_render_settings_change(self.__render_settings_changed)

        if context and context.delegate:
            context.delegate.model = None
            context.delegate.camera_path = None
        self.__lock_models = {}
        self.__build_lock_item(viewport_api, context.camera_path)

        # Active camera
        if context.camera_path:
            text = get_camera_display(context.camera_path, viewport_api.stage)
        else:
            text = self.name

        context.root_menu.text = text

        # Menu items
        self._create_menu_item_fns.sort(key=lambda item: item[1])
        for (create_fn, _) in self._create_menu_item_fns:
            create_fn(viewport_context, cam_menu)

            # The rest of the menu on the case someone wants to put custom stuff
            if self._children:
                for child in self._children:
                    child.build_fn(viewport_context)

    def _build_expand(self, viewport_context) -> None:
        # This menu has the number of widgets on the right side.
        # Check if the widgets are expanded
        viewport_api = viewport_context.get("viewport_api")
        context = self.__menu_context[viewport_api.id]
        stage = viewport_api.stage
        camera_path = viewport_api.camera_path
        context.settings_items = []
        if camera_path:
            locked = self.__lock_models[camera_path].as_bool if camera_path in self.__lock_models and self.__lock_models[camera_path] else False
            enabled = not locked

            context.settings_items.append(
                CameraLens(
                    USDFloatAttributeModel(stage, camera_path, "focalLength", draggable=True),
                    enabled=enabled,
                )
            )
            ui.MenuItem("", delegate=SeparatorDelegate())
            context.settings_items.append(
                CameraFocalDistance(
                    USDFloatAttributeModel(stage, camera_path, "focusDistance"),
                    viewport_context,
                    enabled=enabled,
                )
            )
            ui.MenuItem("", delegate=SeparatorDelegate())
            context.settings_items.append(
                CameraFStop(
                    USDFloatAttributeModel(stage, camera_path, "fStop"),
                    enabled=enabled,
                )
            )

            show_auto_exposure = carb.settings.get_settings().get("/exts/omni.kit.viewport.menubar.camera/showAutoExposure")
            if show_auto_exposure:
                ui.MenuItem("", delegate=SeparatorDelegate())
                context.settings_items.append(CameraAutoExposure(None, enabled=enabled))

        if camera_path in self.__lock_models and self.__lock_models[camera_path]:
            self._on_lock_changed(self.__lock_models[camera_path], viewport_api)

    def _create_from_view(self, viewport_api):
        omni.kit.commands.execute("DuplicateViewportCameraCommand", viewport_api=viewport_api)

    def _on_lock_changed(self, model: ui.AbstractValueModel, viewport_api) -> None:
        is_locked = model.as_bool
        settings_items = self.__menu_context[viewport_api.id].settings_items
        for setting in settings_items:
            setting.enabled = not is_locked

    def _on_menu_collection_triggered(self, menu: ui.MenuItemCollection, checked: bool):
        # Revert status here to keep checked status no changing when clicked
        menu.checked = not checked

    def __sub_global_expand(self):
        # Watch for the carb setting, for now treat it as global state and apply to all Viewports
        def __on_toggle_global_expand(*args, **kwargs):
            expanded = self.expand_model.as_bool
            for menu_context in self.__menu_context.values():
                menu_context.expand_model.set_value(expanded)

        self.__expanded_sub = self.expand_model.subscribe_value_changed_fn(__on_toggle_global_expand)  # noqa: PLW0238

    def __unsub_global_expand(self):
        self.__expanded_sub = None  # noqa: PLW0238
