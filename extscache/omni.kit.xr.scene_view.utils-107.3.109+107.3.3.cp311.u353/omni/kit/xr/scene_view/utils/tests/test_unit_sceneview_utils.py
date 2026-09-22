# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestSceneViewUtils"]

import weakref
from typing import Any, Dict, Optional

from omni import ui
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import XRSceneView
from omni.kit.xr.scene_view.utils import SceneViewUtils
from omni.kit.xr.scene_view.utils.manipulator_components.widget_component import WidgetComponent
from omni.kit.xr.scene_view.utils.spatial_source import SpatialSource
from omni.kit.xr.scene_view.utils.ui_container import UiContainer
from pxr import Gf

from .base_sceneview_test import BaseSceneViewTest


class _TestWidget(ui.Widget):
    def __init__(self, text: Optional[str] = None, style: Optional[Dict[str, Any]] = None):
        super().__init__()
        if text is None:
            text = "Test label"

        if style is None:
            style = {"font_size": 100}

        self._text = text
        self._style = style
        self._build_ui()

    def _build_ui(self):
        self._widget = ui.VStack()
        with self._widget:
            ui.Label(self._text, style=self._style)


class TestSceneViewUtils(BaseSceneViewTest):
    def _set_camera_for_test(self):
        # skip camera customization in this test set
        pass

    async def test_unit_scene_view_utils_memory(self):
        utils = SceneViewUtils(XRSceneView)

        weak_utils = weakref.ref(utils)
        weak_scene_view = weakref.ref(utils.scene_view)
        weak_scene = weakref.ref(utils.scene_view.scene)

        utils = None
        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        self.assertIsNone(weak_utils())
        self.assertIsNone(weak_scene_view())
        self.assertIsNone(weak_scene())

    async def test_unit_label_widget_usd(self):
        widget_component = WidgetComponent(_TestWidget, 600, 200)
        self._test_widget = UiContainer(widget_component)
        async with TestVRProfile(self):
            await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)
            await self.capture_and_compare_viewport_output_async(
                "label_widget", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_unit_custom_args_label_widget_usd(self):
        widget_component = WidgetComponent(_TestWidget, 600, 200, widget_args="...Custom text...")
        self._test_widget = UiContainer(widget_component)

        async with TestVRProfile(self):
            await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)
            await self.capture_and_compare_viewport_output_async(
                "custom_args_label", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_unit_scaled_label_widget_usd(self):
        widget_component = WidgetComponent(
            _TestWidget, 600, 200, widget_args="sCaLeD!", widget_kwargs={"style": {"font_size": 120}}
        )
        self._test_widget = UiContainer(widget_component, space_stack=SpatialSource.new_scale_source(Gf.Vec3d(1, 4, 1)))

        async with TestVRProfile(self):
            await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)
            await self.capture_and_compare_viewport_output_async(
                "scaled_label", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_unit_resolution_scale_label_widget_usd(self):
        widget_component = WidgetComponent(_TestWidget, 600, 200, widget_args="~hi-rez~", resolution_scale=5)
        self._test_widget = UiContainer(widget_component, space_stack=SpatialSource.new_scale_source(Gf.Vec3d(3, 3, 1)))

        async with TestVRProfile(self):
            await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)
            await self.capture_and_compare_viewport_output_async(
                "resolution_scale_label", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )
