# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestWidgetComponent"]

from omni import ui
from omni.kit.xr.scene_view.core import XRSceneView
from omni.kit.xr.scene_view.utils import SceneViewUtils, WidgetComponent
from omni.kit.xr.scene_view.utils.composable_manipulator import ComposableManipulator

from .base_sceneview_test import BaseSceneViewTest


class TestWidgetComponent(BaseSceneViewTest):
    async def setUp(self):
        await super().setUp()
        self._sv_utils = SceneViewUtils(XRSceneView)

    async def tearDown(self):
        del self._sv_utils
        await super().tearDown()

    async def test_unit_initial_none_widget(self):
        """Initially, WidgetComponent's widget property will be None."""
        widget_component = WidgetComponent(ui.Widget)

        self.assertIsNone(widget_component.widget)
        self.assertIsNone(widget_component.scene_widget)

    async def test_unit_widget_gets_made(self):
        """After a scene update or two, WidgetComponent's widget property should have been created."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget)
            manipulator.add_component(widget_component)

        await self.wait_post_sync_async(4)

        self.assertIsNotNone(widget_component.widget)
        self.assertIsNotNone(widget_component.scene_widget)

    async def test_unit_correct_init_size(self):
        """The values for width and height should match those used for init arguments."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget, 123, 456)
            manipulator.add_component(widget_component)

        await self.wait_post_sync_async(3)

        self.assertAlmostEqual(widget_component.width, 123)
        self.assertAlmostEqual(widget_component.height, 456)

    async def test_unit_correct_init_resolution(self):
        """The UI resolution values should match the init arguments."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget, 123, 456, resolution_scale=2.0)
            manipulator.add_component(widget_component)

        await self.wait_post_sync_async(3)

        self.assertAlmostEqual(widget_component.scene_widget.resolution_width, 246)
        self.assertAlmostEqual(widget_component.scene_widget.resolution_height, 912)

    async def test_unit_set_size_after_create(self):
        """The width and height values should update if modified post-init."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget, 123, 456, resolution_scale=1.0)
            manipulator.add_component(widget_component)

        # Set new dims BEFORE scene part exists
        widget_component.width = 321
        widget_component.height = 654
        await self.wait_post_sync_async(3)

        self.assertAlmostEqual(widget_component.width, 321)
        self.assertAlmostEqual(widget_component.height, 654)

    async def test_unit_set_resolution_after_create(self):
        """The UI resolution values should update if modified post-init."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget, 123, 456, resolution_scale=1.0)
            manipulator.add_component(widget_component)

        # Set new dims BEFORE scene part exists
        widget_component.resolution_scale = 2.0
        await self.wait_post_sync_async(3)

        self.assertAlmostEqual(widget_component.scene_widget.resolution_width, 246)
        self.assertAlmostEqual(widget_component.scene_widget.resolution_height, 912)

    async def test_unit_set_size_after_shown(self):
        """Make sure that the initial size shows correctly as well as after resized."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget, 123, 456, resolution_scale=1.0)
            manipulator.add_component(widget_component)

        # Set new dims AFTER scene part exists
        await self.wait_post_sync_async(3)
        widget_component.width = 321
        widget_component.height = 654
        await self.wait_post_sync_async(3)

        self.assertAlmostEqual(widget_component.width, 321)
        self.assertAlmostEqual(widget_component.height, 654)

    async def test_unit_set_resolution_after_shown(self):
        """UI resolution should change according to the modified value."""
        with self._sv_utils.scene_view.scene:
            manipulator = ComposableManipulator()
            widget_component = WidgetComponent(ui.Widget, 123, 456, resolution_scale=1.0)
            manipulator.add_component(widget_component)

        # Set new dims AFTER scene part exists
        await self.wait_post_sync_async(3)
        widget_component.resolution_scale = 2.0
        await self.wait_post_sync_async(3)

        self.assertAlmostEqual(widget_component.scene_widget.resolution_width, 246)
        self.assertAlmostEqual(widget_component.scene_widget.resolution_height, 912)
