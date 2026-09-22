# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, Dict, Optional

import omni.graph.core as og
import omni.ui as ui
from omni.graph.ui_nodes.ogn.OgnSetViewportModeDatabase import OgnSetViewportModeDatabase
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.ui import scene as sc

from . import UINodeCommon  # noqa: PLE0402
from .PickingManipulator import PickingManipulatorFactory  # noqa: PLE0402
from .ViewportClickManipulator import ViewportClickManipulatorFactory  # noqa: PLE0402
from .ViewportDragManipulator import ViewportDragManipulatorFactory  # noqa: PLE0402
from .ViewportHoverManipulator import ViewportHoverManipulatorFactory  # noqa: PLE0402
from .ViewportPressManipulator import ViewportPressManipulatorFactory  # noqa: PLE0402
from .ViewportScrollManipulator import ViewportScrollManipulatorFactory  # noqa: PLE0402

UI_FRAME_NAME = "omni.graph.SetViewportMode"
VIEWPORT_OVERLAY_NAME = "OG_overlay"
IS_LOCK_REQUIRED = True


class NoLock:  # pragma: no cover - this doesn't get used in normal usage
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class OgnSetViewportMode:
    @dataclass
    class ViewportState:
        viewport_click_manipulator: Optional[Any] = None
        viewport_press_manipulator: Optional[Any] = None
        viewport_drag_manipulator: Optional[Any] = None
        viewport_hover_manipulator: Optional[Any] = None
        viewport_scroll_manipulator: Optional[Any] = None
        picking_manipulator: Optional[Any] = None

    __viewport_states: Dict[str, ViewportState] = {}
    __do_it_lock: Optional[Any] = Lock() if IS_LOCK_REQUIRED else NoLock()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.execIn == og.ExecutionAttributeState.DISABLED:
            return False

        with OgnSetViewportMode.__do_it_lock:
            result = OgnSetViewportMode.__do_it(
                db.inputs.mode,
                db.inputs.viewport,
                db.abi_context,
                db.outputs,
                db.log_error,
                db.inputs.enableViewportMouseEvents,
                db.inputs.enablePicking,
                db.inputs.passClicksThru,
            )

        if result:
            if db.inputs.mode == 0:
                db.outputs.defaultMode = og.ExecutionAttributeState.ENABLED
                db.outputs.scriptedMode = og.ExecutionAttributeState.DISABLED
            elif db.inputs.mode == 1:
                db.outputs.defaultMode = og.ExecutionAttributeState.DISABLED
                db.outputs.scriptedMode = og.ExecutionAttributeState.ENABLED
            return True

        db.outputs.defaultMode = og.ExecutionAttributeState.DISABLED
        db.outputs.scriptedMode = og.ExecutionAttributeState.DISABLED
        return False

    @staticmethod
    def __do_it(
        mode: int,
        viewport_window_name: str,
        context: og.GraphContext,
        outputs: OgnSetViewportModeDatabase.ValuesForOutputs,
        log_fn: Optional[Callable],
        viewport_mouse_events_enabled: bool,
        picking_enabled: bool,
        pass_clicks_thru: bool,
    ) -> bool:
        # Validate the viewport window name
        if not viewport_window_name:
            if log_fn is not None:
                log_fn(f"Viewport window '{viewport_window_name}' not found")
            return False

        viewport_api, viewport_window = get_active_viewport_and_window(window_name=viewport_window_name)

        if viewport_window is None:
            if log_fn is not None:
                log_fn(f"Viewport window '{viewport_window_name}' not found")
            return False

        if hasattr(viewport_api, "legacy_window"):
            if log_fn is not None:
                log_fn(f"Legacy viewport window '{viewport_window_name}' not compatible with Set Viewport Mode")
            return False

        # Default mode
        if mode == 0:
            # Destroy the manipulators
            OgnSetViewportMode.__viewport_states[viewport_window_name] = OgnSetViewportMode.__viewport_states.get(
                viewport_window_name, OgnSetViewportMode.ViewportState()
            )
            viewport_state = OgnSetViewportMode.__viewport_states[viewport_window_name]
            OgnSetViewportMode.__destroy_manips(viewport_state)

            # Destroy the ui.ZStack and sc.SceneView if they exist
            frame = viewport_window.get_frame(UI_FRAME_NAME)

            frame_children = ui.Inspector.get_children(frame)
            if frame_children:
                widget_container = frame_children[0]

                widget_container_children = ui.Inspector.get_children(widget_container)
                if widget_container_children:
                    scene_view = widget_container_children[0]

                    viewport_api.remove_scene_view(scene_view)
                    scene_view.scene.clear()
                    scene_view.destroy()

                UINodeCommon.OgWidgetNode.deregister_widget(context, VIEWPORT_OVERLAY_NAME)
                widget_container.destroy()

            frame.clear()

            # Clear output widget path
            outputs.widgetPath = ""

        # Scripted mode
        elif mode == 1:
            # Create the ui.ZStack and sc.SceneView if they don't exist
            frame = viewport_window.get_frame(UI_FRAME_NAME)

            frame_children = ui.Inspector.get_children(frame)
            if frame_children:
                widget_container = frame_children[0]
            else:
                with frame:
                    widget_container = ui.ZStack(identifier=VIEWPORT_OVERLAY_NAME)
                    # Register the container widget so that graphs can access its properties, like size.
                    UINodeCommon.OgWidgetNode.register_widget(context, VIEWPORT_OVERLAY_NAME, widget_container)

            widget_container.content_clipping = not pass_clicks_thru
            widget_container_children = ui.Inspector.get_children(widget_container)
            if widget_container_children:
                scene_view = widget_container_children[0]
            else:
                with widget_container:
                    scene_view = sc.SceneView(child_windows_input=0)
                    viewport_api.add_scene_view(scene_view)

            # Destroy any existing manipulators and create the enabled manipulators
            OgnSetViewportMode.__viewport_states[viewport_window_name] = OgnSetViewportMode.__viewport_states.get(
                viewport_window_name, OgnSetViewportMode.ViewportState()
            )
            viewport_state = OgnSetViewportMode.__viewport_states[viewport_window_name]
            OgnSetViewportMode.__destroy_manips(viewport_state)

            with scene_view.scene:
                if viewport_mouse_events_enabled:
                    viewport_state.viewport_click_manipulator = ViewportClickManipulatorFactory(
                        {"viewport_api": viewport_api, "viewport_window_name": viewport_window_name}
                    )
                    viewport_state.viewport_press_manipulator = ViewportPressManipulatorFactory(
                        {"viewport_api": viewport_api, "viewport_window_name": viewport_window_name}
                    )
                    viewport_state.viewport_drag_manipulator = ViewportDragManipulatorFactory(
                        {"viewport_api": viewport_api, "viewport_window_name": viewport_window_name}
                    )
                    viewport_state.viewport_hover_manipulator = ViewportHoverManipulatorFactory(
                        {"viewport_api": viewport_api, "viewport_window_name": viewport_window_name}
                    )
                    viewport_state.viewport_scroll_manipulator = ViewportScrollManipulatorFactory(
                        {"viewport_api": viewport_api, "viewport_window_name": viewport_window_name}
                    )

                if picking_enabled:
                    viewport_state.picking_manipulator = PickingManipulatorFactory(
                        {"viewport_api": viewport_api, "viewport_window_name": viewport_window_name}
                    )

            # Set output widget path
            outputs.widgetPath = UINodeCommon.find_widget_path(widget_container, viewport_window)

        return True

    @staticmethod
    def __destroy_manips(viewport_state):
        if viewport_state.viewport_click_manipulator is not None:
            viewport_state.viewport_click_manipulator.destroy()
            viewport_state.viewport_click_manipulator = None

        if viewport_state.viewport_press_manipulator is not None:
            viewport_state.viewport_press_manipulator.destroy()
            viewport_state.viewport_press_manipulator = None

        if viewport_state.viewport_drag_manipulator is not None:
            viewport_state.viewport_drag_manipulator.destroy()
            viewport_state.viewport_drag_manipulator = None

        if viewport_state.viewport_hover_manipulator is not None:
            viewport_state.viewport_hover_manipulator.destroy()
            viewport_state.viewport_hover_manipulator = None

        if viewport_state.viewport_scroll_manipulator is not None:
            viewport_state.viewport_scroll_manipulator.destroy()
            viewport_state.viewport_scroll_manipulator = None

        if viewport_state.picking_manipulator is not None:
            viewport_state.picking_manipulator.destroy()
            viewport_state.picking_manipulator = None
