# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestSceneViewInteraction"]

from typing import Callable

from omni import ui
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import InputButtonMap, XRSceneView
from omni.kit.xr.scene_view.utils import WidgetComponent
from omni.kit.xr.scene_view.utils.manipulator_components.widget_component import UpdatePolicy
from omni.kit.xr.scene_view.utils.ui_container import UiContainer, UiInputMotion, UiInputToggle

from .base_sceneview_test import BaseSceneViewTest


class _TestWidget(ui.Widget):
    def __init__(self, on_click_fn: Callable[[], None] | None = None):
        super().__init__()

        ui.Button("Button", clicked_fn=on_click_fn)


class TestSceneViewInteraction(BaseSceneViewTest):
    async def test_integration_input_triggers_highlight(self):
        test_widget = WidgetComponent(_TestWidget, width=300, height=200, update_policy=UpdatePolicy.ALWAYS)
        ui_container = UiContainer(test_widget)
        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        assert type(ui_container.scene_view) is XRSceneView
        scene_view = ui_container.scene_view

        async with TestVRProfile(self):
            test_input = UiInputMotion([0, 0, 1], [0, 0, -1])
            test_input.push_input(scene_view)
            await self.wait_post_sync_async(3)  # wait a few frames so the UI can update

            await self.capture_and_compare_viewport_output_async(
                "input_triggers_highlight", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_integration_button_detects_click(self):
        self.disable_comparison()

        was_clicked = False

        def _on_click():
            nonlocal was_clicked
            was_clicked = True

        test_widget = WidgetComponent(
            _TestWidget,
            width=300,
            height=200,
            update_policy=UpdatePolicy.ALWAYS,
            widget_args=(_on_click,),
        )
        ui_container = UiContainer(test_widget)
        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        assert type(ui_container.scene_view) is XRSceneView
        scene_view = ui_container.scene_view

        async with TestVRProfile(self):
            test_input = UiInputMotion([0, 0, 1], [0, 0, -1])
            test_input.push_input(scene_view)
            await self.wait_post_sync_async(1)

            test_input = UiInputToggle(InputButtonMap.LeftButton, True)
            test_input.push_input(scene_view)
            await self.wait_post_sync_async(1)

            test_input = UiInputToggle(InputButtonMap.LeftButton, False)
            test_input.push_input(scene_view)
            await self.wait_post_sync_async(1)

        self.assertTrue(was_clicked)
