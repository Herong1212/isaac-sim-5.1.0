# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "TestResizeGesture",
    "TestRotationGesture",
    "TestScaleGesture",
    "TestTranslationGesture",
]

import abc
from typing import List

from carb import Float3
from carb.events import IEventStream
from omni import ui
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import InputButtonMap, InputType, XRSceneView
from omni.kit.xr.scene_view.utils import (
    Area2DComponent,
    Resize2DHandleComponent,
    RotationHandleComponent,
    ScaleHandleComponent,
    TranslationHandleComponent,
)
from omni.ui import color

from .base_sceneview_test import BaseUiTest


class _TestUI(ui.Widget):
    def __init__(self):
        super().__init__()

        with ui.Frame():
            with ui.ZStack():
                with ui.VStack():
                    with ui.HStack():
                        with ui.ZStack():
                            ui.Rectangle(style={"background_color": color(0.1, 0.6, 0.6)})
                            ui.Label("C", alignment=ui.Alignment.LEFT_TOP)
                        with ui.ZStack():
                            ui.Rectangle(style={"background_color": color(0.6, 0.1, 0.6)})
                            ui.Label("M", alignment=ui.Alignment.RIGHT_TOP)
                    with ui.HStack():
                        with ui.ZStack():
                            ui.Rectangle(style={"background_color": color(0.6, 0.6, 0.1)})
                            ui.Label("Y", alignment=ui.Alignment.LEFT_BOTTOM)
                        with ui.ZStack():
                            ui.Rectangle(style={"background_color": color(0.4, 0.4, 0.4)})
                            ui.Label("K", alignment=ui.Alignment.RIGHT_BOTTOM)
                with ui.VStack():
                    ui.Spacer(height=12)
                    with ui.HStack():
                        ui.Spacer(width=12)
                        ui.Button("Hi")
                        ui.Spacer(width=12)
                    ui.Spacer(height=12)


class InputEventMaker(abc.ABC):
    @abc.abstractmethod
    def push_input(self, stream: IEventStream) -> None:  # pragma: no cover
        ...


class MouseDownLeftEvent(InputEventMaker):
    def push_input(self, stream: IEventStream) -> None:
        stream.push(InputType.ToggleActivated.value, payload={"input_map": InputButtonMap.Button0.value})


class MouseUpLeftEvent(InputEventMaker):
    def push_input(self, stream: IEventStream) -> None:
        stream.push(InputType.ToggleDeactivated.value, payload={"input_map": InputButtonMap.Button0.value})


class WorldPositionEvent(InputEventMaker):
    def __init__(self, position: Float3, direction: Float3):
        self.__position = [i for i in position]
        self.__direction = [i for i in direction]

    def push_input(self, stream: IEventStream) -> None:
        stream.push(
            InputType.WorldSpaceMovement.value, payload={"origin": self.__position, "direction": self.__direction}
        )


class _GestureTestBase(BaseUiTest):
    WIDGET_TYPE = _TestUI

    async def _do_interaction_test(
        self,
        component: Area2DComponent,
        events_list: List[InputEventMaker],
        golden_image_name: str,
    ):
        self.widget_component.add_child(component, Area2DComponent.TOP)

        await self.wait_materials_loaded_async()
        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        scene_view = self.container.scene_view
        assert type(scene_view) is XRSceneView

        input_stream = scene_view.input_event_stream
        assert type(input_stream) is IEventStream

        async with TestVRProfile(self):
            for maker in events_list:
                maker.push_input(input_stream)
                await self.wait_post_sync_async(2)

            await self.capture_and_compare_viewport_output_async(
                golden_image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )
            await self.wait_post_sync_async()


class TestResizeGesture(_GestureTestBase):
    async def test_integration_make_resize_rect_component(self):
        handle_component = Resize2DHandleComponent(self.widget_component, 100, 100, Area2DComponent.BOTTOM)
        self.widget_component.add_child(handle_component, Area2DComponent.TOP)

        await self.wait_post_sync_async(3)

        self.assertIsNotNone(handle_component.transform)

    async def test_integration_resize_with_component(self):
        # NOTE: This test has been very unreliable, and I haven't figured out why yet. I HAVE checked that the prim
        # is visible (and thus the UI definitely exists) before the inputs are being handled, and also that the inputs
        # are being send and received and updated correctly.
        #
        # Maybe the camera isn't updating reliably?
        #
        # Seems to be more reliable when run as part of the main series of tests, but that could also just be
        # an illusion of luck... ):

        handle_component = Resize2DHandleComponent(self.widget_component, 100, 100, Area2DComponent.BOTTOM)
        events_list = [
            WorldPositionEvent(Float3(0, 150, 1), Float3(0, 0, -1)),
            MouseDownLeftEvent(),
            WorldPositionEvent(Float3(75, 150, 1), Float3(0, 0, -1)),
            WorldPositionEvent(Float3(85, 185, 1), Float3(0, 0, -1)),
            MouseUpLeftEvent(),
        ]

        await self._do_interaction_test(handle_component, events_list, "resize_with_gesture_component")


class TestRotationGesture(_GestureTestBase):
    async def test_integration_make_rotation_rect_component(self):
        handle_component = RotationHandleComponent(100, 100, Area2DComponent.BOTTOM)
        self.widget_component.add_child(handle_component, Area2DComponent.TOP)

        await self.wait_post_sync_async(3)

        self.assertIsNotNone(handle_component.transform)

    async def test_integration_rotate_with_component(self):
        handle_component = RotationHandleComponent(100, 100, Area2DComponent.BOTTOM)
        events_list = [
            WorldPositionEvent(Float3(0, 150, 1), Float3(0, 0, -1)),
            MouseDownLeftEvent(),
            WorldPositionEvent(Float3(45, 150, 1), Float3(0, 0, -1)),
            WorldPositionEvent(Float3(80, 115, 1), Float3(0, 0, -1)),
            MouseUpLeftEvent(),
        ]

        await self._do_interaction_test(handle_component, events_list, "rotate_with_gesture_component")


class TestScaleGesture(_GestureTestBase):
    async def test_integration_make_scale_rect_component(self):
        handle_component = ScaleHandleComponent(100, 100, Area2DComponent.BOTTOM)
        self.widget_component.add_child(handle_component, Area2DComponent.TOP)

        await self.wait_post_sync_async(3)

        self.assertIsNotNone(handle_component.transform)

    async def test_integration_scale_with_component(self):
        handle_component = ScaleHandleComponent(100, 100, Area2DComponent.BOTTOM)
        events_list = [
            WorldPositionEvent(Float3(0, 150, 1), Float3(0, 0, -1)),
            MouseDownLeftEvent(),
            WorldPositionEvent(Float3(50, 150, 1), Float3(0, 0, -1)),
            WorldPositionEvent(Float3(55, 185, 1), Float3(0, 0, -1)),
            MouseUpLeftEvent(),
        ]

        await self._do_interaction_test(handle_component, events_list, "scale_with_gesture_component")


class TestTranslationGesture(_GestureTestBase):
    async def test_integration_make_translation_rect_component(self):
        handle_component = TranslationHandleComponent(100, 100, Area2DComponent.BOTTOM)
        self.widget_component.add_child(handle_component, Area2DComponent.TOP)

        await self.wait_post_sync_async(3)

        self.assertIsNotNone(handle_component.transform)

    async def test_integration_move_with_component(self):
        handle_component = TranslationHandleComponent(100, 100, Area2DComponent.BOTTOM)
        events_list = [
            WorldPositionEvent(Float3(0, 150, 1), Float3(0, 0, -1)),
            MouseDownLeftEvent(),
            WorldPositionEvent(Float3(50, 150, 1), Float3(0, 0, -1)),
            WorldPositionEvent(Float3(55, 185, 1), Float3(0, 0, -1)),
            MouseUpLeftEvent(),
        ]

        await self._do_interaction_test(handle_component, events_list, "move_with_gesture_component")
