# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestUiContainer"]

import weakref
from typing import Any

from omni import ui
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.utils import WidgetComponent
from omni.kit.xr.scene_view.utils.spatial_source import SpatialSource
from omni.kit.xr.scene_view.utils.ui_container import UiContainer
from pxr import Gf

from .base_sceneview_test import BaseSceneViewTest


class _TestWidget(ui.Widget):
    def __init__(self, text: str | None = None, style: dict[str, Any] | None = None):
        super().__init__()
        if text is None:
            text = "UI\nContainer\nTest"

        if style is None:
            style = {"font_size": 48}

        self._text = text
        self._style = style
        self._build_ui()

    def _build_ui(self):
        self._widget = ui.VStack()
        with self._widget:
            ui.Label(self._text, style=self._style)


class TestUiContainer(BaseSceneViewTest):
    """
    Test operations around UiContainer. These tests do not "assume" that UiContainer works, and so do not use the
    BaseUiTest as a parent class.
    """

    async def test_unit_ui_container_deleted_when_dropped(self):  # pragma: no cover
        """
        Check to make sure that UiContainer is always released when no longer referenced.
        This could fail if something in the setup changes and creates a circular reference.
        """
        widget_component = WidgetComponent(_TestWidget)
        container = UiContainer(widget_component)
        del widget_component

        was_deleted = False

        def _handle_finalize(_ref):
            nonlocal was_deleted
            was_deleted = True

        container_weak_ref = weakref.ref(container, _handle_finalize)
        scene_view_weak_ref = weakref.ref(container.scene_view)

        await self.wait_materials_loaded_async()

        # A deleted UiContainer should always be finalized.
        del container
        await self.wait_post_sync_async(5)

        self.assertTrue(was_deleted)
        self.assertIsNone(container_weak_ref())
        self.assertIsNone(scene_view_weak_ref())

    async def test_unit_ui_container_components_not_leaked(self):
        """Check that all components of the UI container are dropped when the container cleans itself up"""
        widget_component = WidgetComponent(_TestWidget)
        container = UiContainer(widget_component)

        component_ref = weakref.ref(widget_component)
        container_ref = weakref.ref(container)
        manipulator_ref = weakref.ref(container.manipulator)
        model_ref = weakref.ref(container.manipulator.transform_model)

        await self.wait_materials_loaded_async()

        del widget_component
        del container

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        self.assertIsNone(component_ref())
        self.assertIsNone(container_ref())
        self.assertIsNone(manipulator_ref())
        self.assertIsNone(model_ref())

    async def test_unit_ui_container_created(self):
        component = WidgetComponent(_TestWidget)
        _ = UiContainer(component)

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                "ui_container_created", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_unit_ui_container_with_single_spatial_arg(self):
        component = WidgetComponent(_TestWidget)
        component.width = 250
        component.height = 200
        source = SpatialSource.new_translation_source(Gf.Vec3d(0, 50, 0))
        _ = UiContainer(component, space_stack=source)

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                "ui_container_single_translation_space", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_unit_ui_container_with_spatial_stack_list(self):
        component = WidgetComponent(_TestWidget)
        component.width = 250
        component.height = 200
        source1 = SpatialSource.new_translation_source(Gf.Vec3d(0, 50, 0))
        source2 = SpatialSource.new_look_at_camera_source()
        _ = UiContainer(component, space_stack=[source1, source2])

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        viewport_api = get_active_viewport()
        assert viewport_api is not None

        original_camera_path = viewport_api.camera_path

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                "ui_container_multi_translation_space", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            # TODO: There is a bug in kit causing an exception during tests when the profile is ended and gui layer is destroyed.
            # omni.kit.widget.viewport/omni/kit/widget/viewport/api.py > _conform_projection
            # Attempts to access the invalid "xr_camera". Normal runtime transitions cameras gracefully.
            # Workaround is to force the camera path to be a known valid camera.
            viewport_api.camera_path = original_camera_path
