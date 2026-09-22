# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestArea2DComponent"]

from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import XRSceneView
from omni.kit.xr.scene_view.utils import Area2DComponent, SceneViewUtils, WidgetComponent
from omni.kit.xr.scene_view.utils.composable_manipulator import ComposableManipulator
from omni.ui import color

from .base_sceneview_test import BaseSceneViewTest, _LabelWithBackground


class TestArea2DComponent(BaseSceneViewTest):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 0.5  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_unit_child_positions_and_origins_align(self):
        """Make sure Area2D components line up correctly"""

        sv_utils = SceneViewUtils(XRSceneView)
        with sv_utils.scene_view.scene:
            self._manipulator = ComposableManipulator()

        widget_component = WidgetComponent(
            _LabelWithBackground,
            widget_kwargs={"text": "VISUAL", "background": color(0.2)},
        )
        self._manipulator.add_component(widget_component)

        top_left = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.BOTTOM_RIGHT,
            widget_kwargs={"text": "TOP LEFT", "background": color(1.0, 0.0, 0.5)},
        )
        top = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.BOTTOM,
            widget_kwargs={"text": "TOP", "background": color(1.0, 0.0, 0.0)},
        )
        top_right = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.BOTTOM_LEFT,
            widget_kwargs={"text": "TOP RIGHT", "background": color(1.0, 0.4, 0.0)},
        )
        left = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.RIGHT,
            widget_kwargs={"text": "LEFT", "background": color(0.0, 0.0, 1.0)},
        )
        right = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.LEFT,
            widget_kwargs={"text": "RIGHT", "background": color(1.0, 0.8, 0.0)},
        )
        bottom_left = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.TOP_RIGHT,
            widget_kwargs={"text": "BOTTOM LEFT", "background": color(0.0, 1.0, 0.5)},
        )
        bottom = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.TOP,
            widget_kwargs={"text": "BOTTOM", "background": color(0.0, 1.0, 0.0)},
        )
        bottom_right = WidgetComponent(
            _LabelWithBackground,
            origin=Area2DComponent.TOP_LEFT,
            widget_kwargs={"text": "BOTTOM RIGHT", "background": color(0.5, 1.0, 0.0)},
        )

        widget_component.add_child(top_left, Area2DComponent.TOP_LEFT)
        widget_component.add_child(top, Area2DComponent.TOP)
        widget_component.add_child(top_right, Area2DComponent.TOP_RIGHT)
        widget_component.add_child(left, Area2DComponent.LEFT)
        widget_component.add_child(right, Area2DComponent.RIGHT)
        widget_component.add_child(bottom_left, Area2DComponent.BOTTOM_LEFT)
        widget_component.add_child(bottom, Area2DComponent.BOTTOM)
        widget_component.add_child(bottom_right, Area2DComponent.BOTTOM_RIGHT)

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                "area_2d_child_arrangement", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )
