## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.kit.test
from omni.ui_scene import scene as sc
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
import carb
import omni.appwindow
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl

KIT_ROOT = Path(carb.tokens.get_tokens_interface().resolve("${kit}")).parent.parent.parent
CURRENT_PATH = Path(__file__).parent.joinpath("../../../data")


class TestWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = KIT_ROOT.joinpath("data/tests/omni.ui.tests")

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def _wait_updates(self, n_updates: int = 5):
        return await self.wait_n_updates(n_updates)

    async def test_general(self):
        """General ability to use widgets"""
        window = await self.create_test_window()

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                transform = sc.Matrix44.get_translation_matrix(0, 0, 0)
                transform *= sc.Matrix44.get_scale_matrix(0.4, 0.4, 0.4)

                with sc.Transform(transform=transform):
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        widget = sc.Widget(500, 500, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                        with widget.frame:
                            ui.Label("Hello world", style={"font_size": 100})

        await self._wait_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_resolution(self):
        """General ability to use widgets"""
        window = await self.create_test_window()

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                transform = sc.Matrix44.get_translation_matrix(0, 0, 0)
                transform *= sc.Matrix44.get_scale_matrix(0.4, 0.4, 0.4)

                with sc.Transform(transform=transform):
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        widget = sc.Widget(500, 500, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                        with widget.frame:
                            ui.Label("Hello world", style={"font_size": 100}, word_wrap=True)

        await self._wait_updates(6)

        widget.resolution_width = 250
        widget.resolution_height = 250

        await self._wait_updates(6)

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_transparency(self):
        """General ability to use widgets"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack():
                # Background
                ui.Rectangle(style={"background_color": ui.color(0.5, 0.5, 0.5)})

                # Camera matrices
                projection = [1e-2, 0, 0, 0]
                projection += [0, 1e-2, 0, 0]
                projection += [0, 0, 2e-7, 0]
                projection += [0, 0, 1, 1]
                view = sc.Matrix44.get_translation_matrix(0, 0, -5)

                scene_view = sc.SceneView(sc.CameraModel(projection, view))
                with scene_view.scene:
                    transform = sc.Matrix44.get_translation_matrix(0, 0, 0)
                    transform *= sc.Matrix44.get_scale_matrix(0.3, 0.3, 0.3)

                    with sc.Transform(transform=transform):
                        with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                            widget = sc.Widget(500, 500, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                            with widget.frame:
                                with ui.VStack():
                                    ui.Label("NVIDIA", style={"font_size": 100, "color": ui.color(1.0, 1.0, 1.0, 0.5)})
                                    ui.Label("NVIDIA", style={"font_size": 100, "color": ui.color(0.0, 0.0, 0.0, 0.5)})
                                    ui.Label("NVIDIA", style={"font_size": 100, "color": ui.color(1.0, 1.0, 1.0, 1.0)})

        await self._wait_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_click(self):
        """General ability to use mouse with widgets"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        was_clicked = [False]
        was_pressed = [False, False, False]
        was_released = [False, False, False]

        def click():
            was_clicked[0] = True

        def press(x, y, b, m):
            was_pressed[b] = True

        def release(x, y, b, m):
            was_released[b] = True

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                transform = sc.Matrix44.get_translation_matrix(0, 0, 0)
                transform *= sc.Matrix44.get_scale_matrix(0.4, 0.4, 0.4)

                with sc.Transform(transform=transform):
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        widget = sc.Widget(500, 500)
                        with widget.frame:
                            # Put the button to the center
                            with ui.VStack():
                                ui.Spacer()
                                with ui.HStack(height=0):
                                    ui.Spacer()
                                    ui.Button("Hello world", width=0, clicked_fn=click,
                                              mouse_pressed_fn=press, mouse_released_fn=release)
                                    ui.Spacer()
                                ui.Spacer()

        ref = ui_test.WidgetRef(scene_view, "")

        await self.wait_n_updates(2)

        # Click in the center
        await ui_test.emulate_mouse_move_and_click(ref.center)

        await self.wait_n_updates(2)

        self.assertTrue(was_clicked[0])
        self.assertTrue(was_pressed[0])
        self.assertTrue(was_released[0])
        self.assertFalse(was_pressed[1])
        self.assertFalse(was_released[1])
        self.assertFalse(was_pressed[2])
        self.assertFalse(was_released[2])

        # Right-click
        await ui_test.emulate_mouse_move_and_click(ref.center, right_click=True)

        await self.wait_n_updates(2)

        self.assertTrue(was_pressed[1])
        self.assertTrue(was_released[1])
        self.assertFalse(was_pressed[2])
        self.assertFalse(was_released[2])

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_keyboard(self):
        """General ability to use mouse with widgets"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            # Camera matrices
            projection = [1e-2 * 3, 0, 0, 0]
            projection += [0, 1e-2 * 3, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                transform = sc.Matrix44.get_translation_matrix(0, 0, 0)
                transform *= sc.Matrix44.get_scale_matrix(0.4, 0.4, 0.4)

                with sc.Transform(transform=transform):
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        widget = sc.Widget(500, 500)
                        with widget.frame:
                            # Put the button to the center
                            with ui.VStack():
                                ui.Spacer()
                                with ui.HStack(height=0):
                                    ui.Spacer()
                                    ui.StringField()
                                    ui.Spacer()
                                ui.Spacer()

        ref = ui_test.WidgetRef(scene_view, "")

        await self._wait_updates()

        # Click in the center
        await ui_test.emulate_mouse_move_and_click(ref.center)

        await self._wait_updates()

        await ui_test.emulate_char_press("NVIDIA Omniverse")

        await self._wait_updates()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_widget_color_not_leak(self):
        class Manipulator(sc.Manipulator):
            def on_build(self):
                with sc.Transform(scale_to=sc.Space.SCREEN):
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        widget = sc.Widget(
                            100, 100, update_policy=sc.Widget.UpdatePolicy.ALWAYS
                        )
                        sc.Arc(
                            radius=20,
                            wireframe=False,
                            thickness=2,
                            tesselation=16,
                            color=cl.red,
                        )
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, -2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)
            with sc.SceneView(sc.CameraModel(projection, view)).scene:
                Manipulator()

        await self._wait_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)
