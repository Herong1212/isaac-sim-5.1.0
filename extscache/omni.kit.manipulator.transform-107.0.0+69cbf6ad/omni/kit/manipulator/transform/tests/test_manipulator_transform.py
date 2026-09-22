## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from functools import lru_cache
from carb.input import MouseEventType
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
from omni.ui import scene as sc
from omni.ui import color as cl
import carb
import omni.kit
import omni.kit.app
from omni.kit.ui_test import emulate_mouse_move, Vec2
import omni.ui as ui
import omni.appwindow
import carb.windowing

from ..manipulator import TransformManipulator
from ..manipulator import Axis
from ..simple_transform_model import SimpleRotateChangedGesture
from ..simple_transform_model import SimpleScaleChangedGesture
from ..simple_transform_model import SimpleTranslateChangedGesture
from ..types import Operation


CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.manipulator.transform}/data"))


class TestTransform(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def test_transform(self):
        window = await self.create_test_window(width=512, height=256)

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, -2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            # Selected point
            self._selected_item = None

            def _on_point_clicked(shape):
                """Called when the user clicks the point"""
                self._selected_item = shape

                pos = self._selected_item.positions[0]
                model = self._manipulator.model
                model.set_floats(model.get_item("translate"), [pos[0], pos[1], pos[2]])

            def _on_item_changed(model, item):
                """
                Called when the user moves the manipulator. We need to move
                the point here.
                """
                if self._selected_item is not None:
                    if item.operation == Operation.TRANSLATE:
                        self._selected_item.positions = model.get_as_floats(item)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                # The manipulator
                self._manipulator = TransformManipulator(
                    size=1,
                    axes=Axis.ALL & ~Axis.Z & ~Axis.SCREEN,
                    gestures=[
                        SimpleTranslateChangedGesture(),
                        SimpleRotateChangedGesture(),
                        SimpleScaleChangedGesture(),
                    ],
                )

                self._sub = \
                    self._manipulator.model.subscribe_item_changed_fn(_on_item_changed)

                # 5 points
                select = sc.ClickGesture(_on_point_clicked)
                sc.Points([[-5, 5, 0]], colors=[ui.color.white], sizes=[10], gesture=select)
                sc.Points([[5, 5, 0]], colors=[ui.color.white], sizes=[10], gesture=select)
                sc.Points([[5, -5, 0]], colors=[ui.color.white], sizes=[10], gesture=select)
                sc.Points([[-5, -5, 0]], colors=[ui.color.white], sizes=[10], gesture=select)
                self._selected_item = sc.Points(
                    [[0, 0, 0]], colors=[ui.color.white], sizes=[10], gesture=select
                )

        for _ in range(30):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_hovering(self):
        app_window = omni.appwindow.get_default_app_window()
        dpi_scale = ui.Workspace.get_dpi_scale()

        window = await self.create_test_window()

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            # Selected point
            self._selected_item = None

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                # The manipulator
                self._manipulator = TransformManipulator(
                    size=1,
                    axes=Axis.ALL & ~Axis.Z & ~Axis.SCREEN,
                )

        await omni.kit.app.get_app().next_update_async()

        # Get NDC position of World-space point
        transformed = scene_view.scene.transform_space(sc.Space.WORLD, sc.Space.NDC, (30, 0, 0))
        # Convert it to the Screen space
        transformed = [transformed[0] * 0.5 + 0.5, transformed[1] * 0.5 + 0.5]

        # Unblock mouse
        app_window.set_input_blocking_state(carb.input.DeviceType.MOUSE, False)
        # Go to the computed position
        x = (window.frame.computed_width * transformed[0] + window.frame.screen_position_x)
        y = (window.frame.computed_height * transformed[1] + window.frame.screen_position_y)
        await emulate_mouse_move(Vec2(x, y))

        for i in range(5):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)
