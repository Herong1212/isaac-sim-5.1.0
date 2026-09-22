# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TestManipulatorCamera', 'TestFlightMode']


from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
from omni.ui import scene as sc
from omni.ui import color as cl
import carb
import omni.kit
import omni.kit.app

import omni.ui as ui
from pxr import Gf
from ..manipulator import CameraManipulatorBase, SceneViewCameraManipulator, adjust_center_of_interest
import omni.kit.ui_test as ui_test
from carb.input import MouseEventType, KeyboardEventType, KeyboardInput


CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.manipulator.camera}/data"))
TEST_WIDTH, TEST_HEIGHT = 500, 500
TEST_UI_CENTER = ui_test.Vec2(TEST_WIDTH / 2, TEST_HEIGHT / 2)

def _flatten_matrix(matrix: Gf.Matrix4d):
    return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
            matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
            matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
            matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]


class SimpleGrid():
    def __init__(self, lineCount: float = 100, lineStep: float = 10, thicknes: float = 1, color: ui.color = ui.color(0.25)):
        self.__transform = ui.scene.Transform()
        with self.__transform:
            for i in range(lineCount * 2 + 1):
                ui.scene.Line(
                    ((i - lineCount) * lineStep, 0, -lineCount * lineStep),
                    ((i - lineCount) * lineStep, 0, lineCount * lineStep),
                    color=color, thickness=thicknes,
                )
                ui.scene.Line(
                    (-lineCount * lineStep, 0, (i - lineCount) * lineStep),
                    (lineCount * lineStep, 0, (i - lineCount) * lineStep),
                    color=color, thickness=thicknes,
                )


class SimpleOrigin():
    def __init__(self, length: float = 5, thickness: float = 4):
        origin = (0, 0, 0)
        with ui.scene.Transform():
            ui.scene.Line(origin, (length, 0, 0), color=ui.color.red, thickness=thickness)
            ui.scene.Line(origin, (0, length, 0), color=ui.color.green, thickness=thickness)
            ui.scene.Line(origin, (0, 0, length), color=ui.color.blue, thickness=thickness)


# Create a few scenes with different camera-maniupulators (a general ui.scene manip and one that allows ortho-tumble )
class SimpleScene:
    def __init__(self, ortho: bool = False, custom: bool = False, *args, **kwargs):
        self.__scene_view = ui.scene.SceneView(*args, **kwargs)
        if ortho:
            view = [-1, 0, 0, 0, 0, 0, 0.9999999999999998, 0, 0, 0.9999999999999998, 0, 0, 0, 0, -1000, 1]
            projection = [0.008, 0, 0, 0, 0, 0.008, 0, 0, 0, 0, -2.000002000002e-06, 0, 0, 0, -1.000002000002, 1]
        else:
            view = [0.7071067811865476, -0.40557978767263897, 0.5792279653395693, 0, -2.775557561562892e-17, 0.8191520442889919, 0.5735764363510462, 0, -0.7071067811865477, -0.4055797876726389, 0.5792279653395692, 0, 6.838973831690966e-14, -3.996234471857009, -866.0161835150924, 1.0000000000000002]
            projection = [4.7602203407949375, 0, 0, 0, 0, 8.483787309173106, 0, 0, 0, 0, -1.000002000002, -1, 0, 0, -2.000002000002, 0]

        view = Gf.Matrix4d(*view)
        center_of_interest = [0, 0, -view.Transform((0, 0, 0)).GetLength()]
        with self.__scene_view.scene:
            self.items = [SimpleGrid(), ui.scene.Arc(100, axis=1, wireframe=True), SimpleOrigin()]
            with ui.scene.Transform(transform = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1000, 0, 1000, 1]):
                self.items.append(ui.scene.Arc(100, axis=1, wireframe=True, color=ui.color.green))
            with ui.scene.Transform(transform = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -260, 0, 260, 1]):
                self.items.append(ui.scene.Arc(100, axis=1, wireframe=True, color=ui.color.blue))

            if custom:
                self.items.append(CameraManipulatorBase())
            else:
                self.items.append(SceneViewCameraManipulator(center_of_interest))

        # Push the start values into the CameraManipulator
        self.setup_camera_model(self.items[-1].model, view, projection, center_of_interest, ortho)

    def setup_camera_model(self, cam_model, view, projection, center_of_interest, ortho):
        cam_model.set_floats('transform', _flatten_matrix(view.GetInverse()))
        cam_model.set_floats('projection', projection)
        cam_model.set_floats('center_of_interest', [0, 0, -view.Transform((0, 0, 0)).GetLength()])
        if ortho:
            cam_model.set_ints('orthographic', [ortho])

        # Setup up the subscription to the CameraModel so changes here get pushed to SceneView
        self.model_changed_sub = cam_model.subscribe_item_changed_fn(self.model_changed)
        # And push the view and projection into the SceneView.model
        cam_model._item_changed(cam_model.get_item('transform'))
        cam_model._item_changed(cam_model.get_item('projection'))

    def model_changed(self, model, item):
        if item == model.get_item('transform'):
            transform = Gf.Matrix4d(*model.get_as_floats(item))
            # Signal that this this is the final change block, adjust our center-of-interest then
            interaction_ended = model.get_as_ints('interaction_ended')
            if interaction_ended and interaction_ended[0]:
                transform = Gf.Matrix4d(*model.get_as_floats(item))
                # Adjust the center-of-interest if requested (zoom out in perspective does this)
                initial_transform = Gf.Matrix4d(*model.get_as_floats('initial_transform'))
                coi_start, coi_end = adjust_center_of_interest(model, initial_transform, transform)
                if coi_end:
                    model.set_floats('center_of_interest', [coi_end[0], coi_end[1], coi_end[2]])

            # Push the start values into the SceneView
            self.__scene_view.model.set_floats('view', _flatten_matrix(transform.GetInverse()))
        elif item == model.get_item('projection'):
            self.__scene_view.model.set_floats('projection', model.get_as_floats('projection'))

    @property
    def scene(self):
        return self.__scene_view.scene

    @property
    def model(self):
        return self.__scene_view.model


async def wait_human_delay(delay=1):
    await ui_test.human_delay(delay)


class TestManipulatorCamera(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def create_test_view(self, name: str, ortho: bool = False, custom: bool = False):
        window = await self.create_test_window(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)
        with window.frame:
            scene_view = SimpleScene(ortho, custom)
        return (window, scene_view)

    async def _test_perspective_camera(self):
        objects = await self.create_test_view('Perspective')
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name='test_perspective_camera.png')

    async def _test_orthographic_camera(self):
        objects = await self.create_test_view('Orthographic', True)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name='test_orthographic_camera.png')

    async def _test_custom_camera(self):
        objects = await self.create_test_view('Custom  Orthographic', True, True)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name='test_custom_camera.png')

    async def _test_mouse_across_screen(self, mouse_down, mouse_up):
        objects = await self.create_test_view('WASD Movement')

        mouse_begin = ui_test.Vec2(TEST_WIDTH / 2, TEST_UI_CENTER.y)
        mouse_end = ui_test.Vec2(TEST_WIDTH + TEST_WIDTH / 2, TEST_UI_CENTER.y)

        await ui_test.input.emulate_mouse(MouseEventType.MOVE, mouse_begin)
        await wait_human_delay()

        try:
            await ui_test.input.emulate_mouse(mouse_down, mouse_begin)
            await ui_test.input.emulate_mouse_slow_move(mouse_begin, mouse_end)
            await wait_human_delay()

        finally:
            await ui_test.input.emulate_mouse(mouse_up, mouse_end)
            await wait_human_delay()

        return objects

    async def test_pan_across_screen(self):
        """Test pan across X is a full move across NDC by default"""
        objects = await self._test_mouse_across_screen(MouseEventType.MIDDLE_BUTTON_DOWN, MouseEventType.MIDDLE_BUTTON_UP)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name='test_pan_across_screen.png')

    async def test_look_across_screen(self):
        """Test look rotation across X is 180 degrees by default"""
        objects = await self._test_mouse_across_screen(MouseEventType.RIGHT_BUTTON_DOWN, MouseEventType.RIGHT_BUTTON_UP)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name='test_look_across_screen.png')


class TestFlightMode(OmniUiTest):
    async def create_test_view(self, name: str, custom=False, ortho: bool = False):
        window = await self.create_test_window(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)
        with window.frame:
            simple_scene = SimpleScene()
        return (window, simple_scene)

    def get_translation(self, model):
        matrix = model.view
        return (matrix[12], matrix[13], matrix[14])

    async def do_key_press(self, key: KeyboardInput, operation = None):
        try:
            await ui_test.input.emulate_keyboard(KeyboardEventType.KEY_PRESS, key)
            await wait_human_delay()
            if operation:
                operation()
        finally:
            await ui_test.input.emulate_keyboard(KeyboardEventType.KEY_RELEASE, key)
            await wait_human_delay()

    async def test_movement(self):
        """Test flight movement via WASD keyboard."""
        window, simple_scene = await self.create_test_view('WASD Movement')
        model = simple_scene.model

        await ui_test.input.emulate_mouse(MouseEventType.MOVE, TEST_UI_CENTER)
        await wait_human_delay()
        start_pos = self.get_translation(model)

        try:
            await ui_test.input.emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN, TEST_UI_CENTER)
            await wait_human_delay()

            await self.do_key_press(KeyboardInput.W)
            after_w = self.get_translation(model)
            # W should have moved Z forward
            self.assertAlmostEqual(after_w[0], start_pos[0], places=5)
            self.assertAlmostEqual(after_w[1], start_pos[1], places=5)
            self.assertTrue(after_w[2] > start_pos[2])

            await self.do_key_press(KeyboardInput.A)
            after_wa = self.get_translation(model)
            # A should have moved X left
            self.assertTrue(after_wa[0] > after_w[0])
            self.assertAlmostEqual(after_wa[1], after_w[1], places=5)
            self.assertAlmostEqual(after_wa[2], after_w[2], places=5)

            await self.do_key_press(KeyboardInput.S)
            after_was = self.get_translation(model)
            # S should have moved Z back
            self.assertAlmostEqual(after_was[0], after_wa[0], places=5)
            self.assertAlmostEqual(after_was[1], after_wa[1], places=5)
            self.assertTrue(after_was[2] < after_wa[2])

            await self.do_key_press(KeyboardInput.D)
            after_wasd = self.get_translation(model)
            # D should have moved X right
            self.assertTrue(after_wasd[0] < after_was[0])
            self.assertAlmostEqual(after_wasd[1], after_was[1], places=5)
            self.assertAlmostEqual(after_wasd[2], after_was[2], places=5)

            # Test disabling flight-mode in the model would stop keyboard from doing anything
            before_wasd = self.get_translation(model)
            simple_scene.items[-1].model.set_ints('disable_fly', [1])

            await self.do_key_press(KeyboardInput.W)
            await self.do_key_press(KeyboardInput.A)
            await self.do_key_press(KeyboardInput.S)
            await self.do_key_press(KeyboardInput.D)
            await wait_human_delay()

            after_wasd = self.get_translation(model)
            simple_scene.items[-1].model.set_ints('disable_fly', [0])

            self.assertTrue(Gf.IsClose(before_wasd, after_wasd, 1e-5))

        finally:
            await ui_test.input.emulate_mouse(MouseEventType.RIGHT_BUTTON_UP)
            await wait_human_delay()

    async def _test_speed_modifier(self, value_a, value_b):
        vel_key = '/persistent/app/viewport/camMoveVelocity'
        mod_amount_key = '/exts/omni.kit.manipulator.camera/flightMode/keyModifierAmount'
        settings = carb.settings.get_settings()

        window, simple_scene = await self.create_test_view('WASD Movement')
        model = simple_scene.model

        settings.set(vel_key, 5)
        await ui_test.input.emulate_mouse(MouseEventType.MOVE, TEST_UI_CENTER)
        await wait_human_delay()

        def compare_velocity(velocity):
            vel_value = settings.get(vel_key)
            self.assertEqual(vel_value, velocity)

        try:
            compare_velocity(5)

            await ui_test.input.emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN, TEST_UI_CENTER)
            # By default Shift should double speed
            await self.do_key_press(KeyboardInput.LEFT_SHIFT, lambda: compare_velocity(value_a))
            # By default Shift should halve speed
            await self.do_key_press(KeyboardInput.LEFT_CONTROL, lambda: compare_velocity(value_b))
            await ui_test.input.emulate_mouse(MouseEventType.RIGHT_BUTTON_UP)
            await wait_human_delay()

            compare_velocity(5)

        finally:
            settings.set(vel_key, 5)
            settings.set(mod_amount_key, 2)

            await ui_test.input.emulate_mouse(MouseEventType.RIGHT_BUTTON_UP)
            await wait_human_delay()


    async def test_speed_modifier_a(self):
        """Test default flight speed adjustement: 2x"""
        await self._test_speed_modifier(10, 2.5)

    async def test_speed_modifier_b(self):
        """Test custom flight speed adjustement: 4x"""
        carb.settings.get_settings().set('/exts/omni.kit.manipulator.camera/flightMode/keyModifierAmount', 4)
        await self._test_speed_modifier(20, 1.25)

    async def test_speed_modifier_c(self):
        """Test custom flight speed adjustement: 0x"""
        # Test when set to 0
        carb.settings.get_settings().set('/exts/omni.kit.manipulator.camera/flightMode/keyModifierAmount', 0)
        await self._test_speed_modifier(5, 5)
