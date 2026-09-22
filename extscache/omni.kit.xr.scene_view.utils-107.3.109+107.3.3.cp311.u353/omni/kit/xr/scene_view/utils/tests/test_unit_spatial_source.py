# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestSpatialSource"]

from typing import Any, Dict, Optional

import carb
import omni.ui.scene
from omni import ui
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.xr.scene_view.utils import WidgetComponent
from omni.kit.xr.scene_view.utils.spatial_source import SpatialSource
from omni.kit.xr.scene_view.utils.ui_container import UiContainer
from omni.ui import scene
from pxr import Gf

from .base_sceneview_test import BaseSceneViewTest


class _TestWidget(ui.Widget):
    def __init__(self, text: Optional[str] = None, style: Optional[Dict[str, Any]] = None):
        super().__init__()
        if text is None:
            text = "UI\nSpatial Source\nTest"

        if style is None:
            style = {"font_size": 48}

        self._text = text
        self._style = style
        self._build_ui()

    def _build_ui(self):
        self._widget = ui.VStack()
        with self._widget:
            ui.Label(self._text, style=self._style)


class TestSpatialSource(BaseSceneViewTest):
    async def test_unit_simple_transform_matrix_spatial_source(self):
        matrix_args = [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
            8.0,
            9.0,
            10.0,
            11.0,
            12.0,
            13.0,
            14.0,
            15.0,
        ]
        source_matrix = Gf.Matrix4f().Set(*matrix_args)
        spatial_source = SpatialSource.new_transform_matrix_source(source_matrix)
        transform = spatial_source.source.create_transform()

        for i in range(16):
            self.assertAlmostEqual(matrix_args[i], transform.transform[i])

    async def test_unit_simple_translation_spatial_source(self):
        source_vec = Gf.Vec3d(3, 7, 11)
        spatial_source = SpatialSource.new_translation_source(source_vec)
        transform = spatial_source.source.create_transform()

        ui_matrix: scene.Matrix44 = transform.transform
        x = ui_matrix[12]
        y = ui_matrix[13]
        z = ui_matrix[14]

        self.assertAlmostEqual(x, source_vec[0])
        self.assertAlmostEqual(y, source_vec[1])
        self.assertAlmostEqual(z, source_vec[2])

    async def test_unit_simple_look_at_camera_spatial_source(self):
        spatial_source = SpatialSource.new_look_at_camera_source()
        transform = spatial_source.source.create_transform()

        self.assertEqual(transform.look_at, scene.Transform.LookAt.CAMERA)

    async def test_unit_simple_primpath_spatial_source(self):

        path_string = "/World/source_prim"
        spatial_source = SpatialSource.new_prim_path_source(path_string)
        transform = spatial_source.source.create_transform()

        self.assertEqual(type(transform.basis), omni.kit.xr.scene_view.core.XRPrimPathTransformBasis)
