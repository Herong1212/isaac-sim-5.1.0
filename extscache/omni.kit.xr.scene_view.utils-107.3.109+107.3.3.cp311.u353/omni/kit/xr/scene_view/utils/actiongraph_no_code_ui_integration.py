# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

__all__ = ["ActionGraphNoCodeUiIntegration"]

import asyncio
import json
import sys
import traceback
from abc import ABC
from pydoc import locate
from typing import Any, Dict, List, Type

import carb.events
import omni
import omni.graph.core as og
import omni.graph.core.types as ot
from numpy import ndarray
from omni.kit.data2ui.core import DDView, OmniUiDelegate
from omni.kit.data2ui.usd import Data2UIUSDExtension
from omni.kit.data2ui.usd import Model as UsdModel
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.viewport.utility.camera_state import ViewportCameraState
from pxr import Gf, Usd, UsdGeom

from .manipulator_components import Area2DComponent, BaseTransformableComponent, WidgetComponent
from .spatial_source import SpatialSource
from .ui_container import UiContainer


class FrameWidget(omni.ui.Widget):
    def __init__(self, frame_prim, **kwargs):
        super().__init__(**kwargs)
        self._frame_prim = frame_prim
        self._build_ui()

    def _build_ui(self):
        self._frame = omni.ui.Frame()
        with self._frame:
            self._dd_view = DDView(UsdModel(self._frame_prim), OmniUiDelegate())


class ActionGraphNoCodeUiIntegration(ABC):
    __instance = None

    def __init__(self):
        assert ActionGraphNoCodeUiIntegration.__instance is None
        ActionGraphNoCodeUiIntegration.__instance = self

        # Create stage context menus to manually send and remove the No Code UI Frame Prims to the scene.
        send_menu_item = {
            "name": "Send No Code To Scene",
            "glyph": "frame.svg",
            "enabled_fn": lambda objects: Data2UIUSDExtension._menu_prim_is_frame(objects=objects),
            "show_fn": [lambda objects: Data2UIUSDExtension._menu_prim_is_frame(objects=objects)],
            "onclick_fn": lambda objects: self.send_to_scene(objects=objects),
        }

        remove_menu_item = {
            "name": "Remove No Code From Scene",
            "glyph": "frame.svg",
            "enabled_fn": lambda objects: self._can_remove_from_scene(objects=objects),
            "show_fn": [lambda objects: Data2UIUSDExtension._menu_prim_is_frame(objects=objects)],
            "onclick_fn": lambda objects: self.remove_from_scene(objects=objects),
        }

        self._stage_contextmenus = [
            omni.kit.context_menu.add_menu(item, "MENU", "omni.kit.widget.stage")
            for item in [send_menu_item, remove_menu_item]
        ]

        self._subs = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop_by_type(
                omni.usd.StageEventType.CLOSING,
                self._on_stage_closing,
                name="ActionGraphNoCodeUiIntegration On Stage Closing",
            )
        )

        self._task = None
        self._widget_containers: Dict[str, UiContainer] = {}

    def __del__(self):
        ActionGraphNoCodeUiIntegration.__instance = None

        self._stage_contextmenus.clear()

        if self._task:
            self._task.cancel()

        self._subs = None
        self._task = None
        self._widget_containers = {}

    def _on_stage_closing(self, ev: carb.events.IEvent) -> None:
        if self._task:
            self._task.cancel()

        self._task = None
        self._widget_containers = {}

    def send_to_scene(self, objects: dict, attributes: Dict[str, Any] = {}):
        _frame_prim = objects.get("hovered_prim", None)
        if not _frame_prim:
            return

        if not attributes:
            attributes = {}

        width = -1
        height = -1

        if _frame_prim.HasAttribute("omni:ui:Widget:width") and _frame_prim.HasAttribute("omni:ui:Widget:height"):
            width = _frame_prim.GetAttribute("omni:ui:Widget:width").Get()
            height = _frame_prim.GetAttribute("omni:ui:Widget:height").Get()

        # If user specified a set size, use it.
        if width > 0 and height > 0:
            try:
                self._create_ui_container(_frame_prim, width, height, attributes=attributes)
            except Exception as exp:
                carb.log_error("===================================================================")
                carb.log_error(str(exp))
                for line in traceback.format_exception(*sys.exc_info()):
                    carb.log_error(line)
                carb.log_error("===================================================================")
        # Else, we'll assume it was meant to be placed on the viewport, where we'll need to wait for a size.
        else:
            self._task = asyncio.ensure_future(
                self._create_ui_container_with_viewport_size(_frame_prim, attributes=attributes)
            )

    async def _create_ui_container_with_viewport_size(self, _frame_prim: Usd.Prim, attributes: Dict[str, Any]):
        if avw := omni.kit.viewport.utility.get_active_viewport_window(window_name="Viewport"):
            _frame = avw.get_frame("SceneViewUtils Frame")
            with _frame:
                # We need to wait a frame to for the ui frame to be drawn before the width and height are populated.
                await omni.kit.app.get_app().next_update_async()
                try:
                    self._create_ui_container(
                        _frame_prim, _frame.computed_width, _frame.computed_height, attributes=attributes
                    )
                except Exception as exp:
                    carb.log_error("===================================================================")
                    carb.log_error(str(exp))
                    for line in traceback.format_exception(*sys.exc_info()):
                        carb.log_error(line)
                    carb.log_error("===================================================================")

    def _create_ui_container(self, frame_prim: Usd.Prim, width: int, height: int, attributes: Dict[str, Any]):
        assert width > 0
        assert height > 0

        space_stack: List[SpatialSource] = self._get_space_stack_from_attributes(attributes)

        # If user didn't specify a transform, assume we will place the widget in front of the active camera.
        # This will be static UI meaning it does not move when camera moves.
        if len(space_stack) == 0:
            forward_distance = attributes["Camera.forward_offset"] if "Camera.forward_offset" in attributes else 1000
            world_transform = self._get_camera_forward_matrix(forward_distance)

            space_stack.append(SpatialSource.new_transform_matrix_source(world_transform))

        widget_component = WidgetComponent(
            FrameWidget,
            width,
            height,
            3,
            widget_kwargs={"frame_prim": frame_prim},
        )

        self._add_child_widgets(widget_component, attributes)

        self._widget_containers[str(frame_prim)] = UiContainer(
            widget_component,
            space_stack=space_stack,
        )

    def _can_remove_from_scene(self, objects: dict):
        prim_list = objects.get("prim_list", [])
        for prim in prim_list:
            if str(prim) not in self._widget_containers:
                return False

        return Data2UIUSDExtension._menu_prim_is_ui_prim(objects=objects)

    def remove_from_scene(self, objects: dict) -> bool:
        _frame_prim = objects.get("hovered_prim", None)
        if not _frame_prim:
            return False

        frame_path = str(_frame_prim)
        if frame_path not in self._widget_containers:
            return False

        self._widget_containers.pop(frame_path)
        return True

    def _get_space_stack_from_attributes(self, attributes: Dict[str, Any]) -> List[SpatialSource]:
        space_stack: List[SpatialSource] = []

        if "SpatialSource.new_prim_path_source" in attributes:
            space_stack.append(SpatialSource.new_prim_path_source(attributes["SpatialSource.new_prim_path_source"]))

        if "SpatialSource.new_look_at_camera_source" in attributes:
            space_stack.append(SpatialSource.new_look_at_camera_source())

        if "SpatialSource.new_transform_matrix_source" in attributes:
            space_stack.append(
                SpatialSource.new_transform_matrix_source(attributes["SpatialSource.new_transform_matrix_source"])
            )

        if "SpatialSource.new_translation_source" in attributes:
            space_stack.append(SpatialSource.new_translation_source(attributes["SpatialSource.new_translation_source"]))

        if "SpatialSource.new_rotation_source" in attributes:
            space_stack.append(SpatialSource.new_rotation_source(attributes["SpatialSource.new_rotation_source"]))

        if "SpatialSource.new_scale_source" in attributes:
            space_stack.append(SpatialSource.new_scale_source(attributes["SpatialSource.new_scale_source"]))

        return space_stack

    def _get_camera_forward_matrix(self, forward_distance: float) -> Gf.Matrix4d:
        viewport = get_active_viewport()
        viewport_cam_state = ViewportCameraState(camera_path=viewport.camera_path, viewport=viewport)
        world_transform = viewport_cam_state.usd_camera.ComputeLocalToWorldTransform(Usd.TimeCode.Default())

        pos = world_transform.ExtractTranslation()
        mat_no_scale = world_transform.RemoveScaleShear()

        if UsdGeom.GetStageUpAxis(omni.usd.get_context().get_stage()) == "Y":
            forward = mat_no_scale.GetRow3(2)
        else:
            forward = mat_no_scale.GetRow3(1)

        # Place the widget in front of the active camera.
        # N.B. Camera faces in "-Z"
        pos = pos + (forward * -forward_distance)

        world_transform.SetTranslateOnly(pos)
        return world_transform

    def _add_child_widgets(self, widget_component: WidgetComponent, attributes: Dict[str, Any]):
        for attr_name, attr_val in attributes.items():
            klass: Type[ActionGraphNoCodeUiIntegration] = locate(attr_name)  # type: ignore

            if not klass or not issubclass(klass, BaseTransformableComponent):
                continue

            if not isinstance(attr_val, str):
                continue

            args = json.loads(attr_val)
            # For any strings arguments, attempt to locate actual types corresponding to them.
            for arg_name, arg_val in args.items():
                if arg_val is not None and isinstance(arg_val, str):
                    args[arg_name] = locate(arg_val)

            # Special case: There is not a great place to retrieve the data driven parameter 'placement' used in add_child.
            # So we attempt to pull it from the args and remove it so it doesn't get used in the component constructor
            # or else we will get an exception.
            placement = Area2DComponent.CENTER
            if "placement" in args:
                placement = args["placement"]
                del args["placement"]

            transformable_component = klass(**args)
            widget_component.add_child(transformable_component, placement)

    def _parse_attributes(self, attributes: Dict[str, Any]):
        attr_name = "SpatialSource.new_prim_path_source"
        if attr_name in attributes:
            if not isinstance(attributes[attr_name], str):
                carb.log_warn(f"Culling {attr_name} not of type str.")
                del attributes[attr_name]

        attr_name = "SpatialSource.new_transform_matrix_source"
        if attr_name in attributes:
            if not isinstance(attributes[attr_name], ndarray) or attributes[attr_name].size != 16:
                carb.log_warn(f"Culling {attr_name} not of type Gf.Matrix4d.")
                del attributes[attr_name]
            attributes[attr_name] = Gf.Matrix4d(*attributes[attr_name].tolist())

        attr_name = "SpatialSource.new_translation_source"
        if attr_name in attributes:
            if not isinstance(attributes[attr_name], ndarray) or attributes[attr_name].size != 3:
                carb.log_warn(f"Culling {attr_name} not of type Gf.Vec3d.")
                del attributes[attr_name]
            attributes[attr_name] = Gf.Vec3d(*attributes[attr_name].tolist())

        attr_name = "SpatialSource.new_rotation_source"
        if attr_name in attributes:
            if not isinstance(attributes[attr_name], ndarray) or attributes[attr_name].size != 3:
                carb.log_warn(f"Culling {attr_name} not of type Gf.Vec3d.")
                del attributes[attr_name]
            attributes[attr_name] = Gf.Vec3d(*attributes[attr_name].tolist())

        attr_name = "SpatialSource.new_scale_source"
        if attr_name in attributes:
            if not isinstance(attributes[attr_name], ndarray) or attributes[attr_name].size != 3:
                carb.log_warn(f"Culling {attr_name} not of type Gf.Vec3d.")
                del attributes[attr_name]
            attributes[attr_name] = Gf.Vec3d(*attributes[attr_name].tolist())

        attr_name = "Camera.forward_offset"
        if attr_name in attributes:
            if not isinstance(attributes[attr_name], float):
                carb.log_warn(f"Culling {attr_name} not of type float.")
                del attributes[attr_name]
        pass

    @og.create_node_type
    def send_ui_to_scene(trigger: ot.execution, ui_frame_path: ot.string, parameters: ot.bundle) -> ot.execution:
        """
        Sends the No Code UI Frame to the scene.
        Args:
            @ui_frame_path: Path of the the No Code UI Frame Prim
            @parameters: Bundle with optional parameters
                @SpatialSource.new_prim_path_source(string): Attaches the UI to the specified Sdf.Path (as a string).
                @SpatialSource.new_look_at_camera_source(Any): Keeps the UI rotated towards the camera

                # If new_prim_path_source is set, the following will be an additive transformation.
                @SpatialSource.new_transform_matrix_source(Matrix4d): The matrix to transform the UI.
                @SpatialSource.new_translation_source(Vec3d): The translation to transform the UI.
                @SpatialSource.new_rotation_source(Vec3d): The rotation to transform the UI.
                @SpatialSource.new_scale_source(Vec3d): The scale to transform the UI.

                @Camera.forward_offset(float): If no SpatialSource set, the UI will be placed at the camera. This value specifies the distance in front of the camera to send the UI.
        """
        if not ActionGraphNoCodeUiIntegration.__instance:
            return og.ExecutionAttributeState.DISABLED

        stage = omni.usd.get_context().get_stage()
        frame_prim = stage.GetPrimAtPath(str(ui_frame_path))
        if not frame_prim:
            return og.ExecutionAttributeState.DISABLED

        objects = {"prim_list": [frame_prim]}
        if not Data2UIUSDExtension._menu_prim_is_frame(objects=objects):
            return og.ExecutionAttributeState.DISABLED

        objects = {"hovered_prim": frame_prim}

        attributes: Dict[str, Any] = {}
        for attr in parameters.attributes:
            attributes[attr.name] = attr.value

        ActionGraphNoCodeUiIntegration.__instance._parse_attributes(attributes)
        ActionGraphNoCodeUiIntegration.__instance.send_to_scene(objects=objects, attributes=attributes)
        return og.ExecutionAttributeState.ENABLED

    @og.create_node_type
    def remove_ui_from_scene(trigger: ot.execution, ui_frame_path: ot.string) -> ot.execution:
        """
        Removes the No Code UI corresponding to ui_frame_path from the scene.
        """
        if not ActionGraphNoCodeUiIntegration.__instance:
            return og.ExecutionAttributeState.DISABLED

        stage = omni.usd.get_context().get_stage()
        frame_prim = stage.GetPrimAtPath(ui_frame_path)
        if not frame_prim:
            return og.ExecutionAttributeState.DISABLED

        objects = {"hovered_prim": frame_prim}
        if ActionGraphNoCodeUiIntegration.__instance.remove_from_scene(objects):
            return og.ExecutionAttributeState.ENABLED
        else:
            return og.ExecutionAttributeState.DISABLED
