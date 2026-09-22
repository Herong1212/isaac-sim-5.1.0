# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TestManipulatorGamepad']

import omni.kit.test
from ..manipulator import CameraManipulatorBase, SceneViewCameraManipulator, adjust_center_of_interest

import omni.ui as ui
from omni.ui import scene as sc
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
import carb
from carb.input import GamepadInput

from pxr import Gf
from functools import partial

TEST_WIDTH, TEST_HEIGHT = 500, 500

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

    def __del__(self):
        self.destroy()

    def destroy(self):
        for item in self.items:
            if hasattr(item, 'destroy'):
                item.destroy()
        self.items = None

        if self.__scene_view:
            self.__scene_view.destroy()
            self.__scene_view = None

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
            self.model.set_floats('view', _flatten_matrix(transform.GetInverse()))
        elif item == model.get_item('projection'):
            self.model.set_floats('projection', model.get_as_floats('projection'))

    @property
    def scene(self):
        return self.__scene_view.scene

    @property
    def model(self):
        return self.__scene_view.model

    @property
    def camera_maipulator(self):
        return self.items[-1]


async def wait_human_delay(delay=1):
    await ui_test.human_delay(delay)

def get_translation(model):
    matrix = model.get_as_floats('view')
    return (matrix[12], matrix[13], matrix[14])

class TestManipulatorGamepad(OmniUiTest):
    async def create_test_view(self, name: str, custom=False, ortho: bool = False):
        window = await self.create_test_window(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)
        with window.frame:
            simple_scene = SimpleScene()
        return (window, simple_scene)

    async def test_gamepad_initilization(self):
        """Test gamepad controller setup and destrution via carb.input."""
        window, simple_scene = await self.create_test_view('Gamepad Movement')

        simple_scene.camera_maipulator.gamepad_enabled = False
        self.assertFalse(simple_scene.camera_maipulator.gamepad_enabled)

        simple_scene.camera_maipulator.gamepad_enabled = True
        self.assertTrue(simple_scene.camera_maipulator.gamepad_enabled)

        simple_scene.camera_maipulator.gamepad_enabled = False
        self.assertFalse(simple_scene.camera_maipulator.gamepad_enabled)

        simple_scene.destroy()

    async def test_gamepad_connection(self):
        """Test gamepad controller connection and disconnection doesn't throw"""
        window, simple_scene = await self.create_test_view('Gamepad Movement')

        simple_scene.camera_maipulator.gamepad_enabled = True
        self.assertTrue(simple_scene.camera_maipulator.gamepad_enabled)

        game_pad, game_pad_connected = None, False
        input_provider = carb.input.acquire_input_provider()
        try:
            game_pad = input_provider.create_gamepad("Fake Gamepad for test", "00000000-00000000-0000-0000")
            self.assertIsNotNone(game_pad)

            input_provider.set_gamepad_connected(game_pad, True)
            game_pad_connected = True
            await wait_human_delay(5)

            input_provider.set_gamepad_connected(game_pad, False)
            game_pad_connected = False
            await wait_human_delay(5)
        finally:
            if game_pad is not None:
                if game_pad_connected:
                    input_provider.set_gamepad_connected(game_pad, False)
                input_provider.destroy_gamepad(game_pad)

        simple_scene.destroy()

    async def test_gamepad_movement(self):
        """Test gamepad controller functionality"""
        window, simple_scene = await self.create_test_view('Gamepad Movement')
        self.assertIsNotNone(simple_scene.model)

        simple_scene.camera_maipulator.gamepad_enabled = True
        self.assertTrue(simple_scene.camera_maipulator.gamepad_enabled)

        game_pad, game_pad_connected = None, False
        input_provider = carb.input.acquire_input_provider()
        try:
            game_pad = input_provider.create_gamepad("Fake Gamepad for test", "00000000-00000000-0000-0000")
            self.assertIsNotNone(game_pad)

            input_provider.set_gamepad_connected(game_pad, True)
            game_pad_connected = True
            await wait_human_delay(5)

            def test_moved_left(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertGreater(tr_b[0], tr_a[0])
                self.assertTrue(Gf.IsClose(tr_a[1], tr_b[1], 1.0e-5))
                self.assertTrue(Gf.IsClose(tr_a[2], tr_b[2], 1.0e-5))

            def test_moved_right(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertLess(tr_b[0], tr_a[0])
                self.assertTrue(Gf.IsClose(tr_a[1], tr_b[1], 1.0e-5))
                self.assertTrue(Gf.IsClose(tr_a[2], tr_b[2], 1.0e-5))

            def test_moved_up(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertTrue(Gf.IsClose(tr_a[0], tr_b[0], 1.0e-5))
                self.assertGreater(tr_a[1], tr_b[1])
                self.assertTrue(Gf.IsClose(tr_a[2], tr_b[2], 1.0e-5))

            def test_moved_down(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertTrue(Gf.IsClose(tr_a[0], tr_b[0], 1.0e-5))
                self.assertLess(tr_a[1], tr_b[1])
                self.assertTrue(Gf.IsClose(tr_a[2], tr_b[2], 1.0e-5))

            def test_moved_forward(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertTrue(Gf.IsClose(tr_a[0], tr_b[0], 1.0e-5))
                self.assertTrue(Gf.IsClose(tr_a[1], tr_b[1], 1.0e-5))
                self.assertLess(tr_a[2], tr_b[2])

            def test_moved_backward(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertTrue(Gf.IsClose(tr_a[0], tr_b[0], 1.0e-5))
                self.assertTrue(Gf.IsClose(tr_a[1], tr_b[1], 1.0e-5))
                self.assertGreater(tr_a[2], tr_b[2])

            def test_no_move(m_a, m_b):
                tr_a = (m_a[12], m_a[13], m_a[14])
                tr_b = (m_b[12], m_b[13], m_b[14])
                self.assertTrue(Gf.IsClose(tr_a, tr_b, 1.0e-5))

            async def test_gamepad_input(input_dict, event_delay=15):
                prev_m = simple_scene.model.get_as_floats('view').copy()
                for input, test_fn in input_dict.items():
                    input_provider.buffer_gamepad_event(game_pad, input, 1.0)
                    await wait_human_delay(event_delay)
                    input_provider.buffer_gamepad_event(game_pad, input, 0.0)
                    await wait_human_delay(event_delay)
                    cur_m = simple_scene.model.get_as_floats('view').copy()
                    test_fn(prev_m, cur_m)
                    prev_m = cur_m

            await test_gamepad_input({
                GamepadInput.LEFT_STICK_LEFT: test_moved_left,
                GamepadInput.LEFT_STICK_RIGHT: test_moved_right,
                GamepadInput.LEFT_STICK_UP: test_moved_forward,
                GamepadInput.LEFT_STICK_DOWN: test_moved_backward
            })

            await test_gamepad_input({
                GamepadInput.DPAD_LEFT: test_moved_left,
                GamepadInput.DPAD_RIGHT: test_moved_right,
                GamepadInput.DPAD_UP: test_moved_forward,
                GamepadInput.DPAD_DOWN: test_moved_backward
            })

            await test_gamepad_input({
                GamepadInput.LEFT_TRIGGER: test_moved_down,
                GamepadInput.RIGHT_TRIGGER: test_moved_up,
            })

            await test_gamepad_input({
                GamepadInput.LEFT_SHOULDER: test_moved_left,
                GamepadInput.RIGHT_SHOULDER: test_moved_right,
            })

            def test_rot_x(is_greater: bool, m_a, m_b):
                rt_a = Gf.Matrix4d(*m_a).ExtractRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
                rt_b = Gf.Matrix4d(*m_b).ExtractRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
                self.assertEqual(rt_a[0] > rt_b[0], is_greater)
                self.assertTrue(Gf.IsClose(rt_a[1], rt_a[1], 1.0e-3))
                self.assertTrue(Gf.IsClose(rt_a[2], rt_a[2], 1.0e-3))

            def test_rot_y(is_greater: bool, m_a, m_b):
                rt_a = Gf.Matrix4d(*m_a).ExtractRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
                rt_b = Gf.Matrix4d(*m_b).ExtractRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
                self.assertTrue(Gf.IsClose(rt_a[0], rt_a[0], 1.0e-3))
                self.assertEqual(rt_a[1] > rt_b[1], is_greater)
                self.assertTrue(Gf.IsClose(rt_a[2], rt_a[2], 1.0e-3))

            await test_gamepad_input({
                GamepadInput.RIGHT_STICK_LEFT: partial(test_rot_y, True),
                GamepadInput.RIGHT_STICK_RIGHT: partial(test_rot_y, False),
                GamepadInput.RIGHT_STICK_UP: partial(test_rot_x, True),
                GamepadInput.RIGHT_STICK_DOWN: partial(test_rot_x, False),
            })

            # Test disabling flight-mode in the model would stop gamepad from doing anything
            simple_scene.items[-1].model.set_ints('disable_fly', [1])

            await test_gamepad_input({
                GamepadInput.LEFT_STICK_LEFT: test_no_move,
                GamepadInput.LEFT_STICK_RIGHT: test_no_move,
                GamepadInput.LEFT_STICK_UP: test_no_move,
                GamepadInput.LEFT_STICK_DOWN: test_no_move
            })

            await test_gamepad_input({
                GamepadInput.DPAD_LEFT: test_no_move,
                GamepadInput.DPAD_RIGHT: test_no_move,
                GamepadInput.DPAD_UP: test_no_move,
                GamepadInput.DPAD_DOWN: test_no_move
            })

            simple_scene.items[-1].model.set_ints('disable_fly', [0])

            await wait_human_delay(5)

        finally:
            if game_pad is not None:
                if game_pad_connected:
                    input_provider.set_gamepad_connected(game_pad, False)
                input_provider.destroy_gamepad(game_pad)

        simple_scene.destroy()
