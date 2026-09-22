## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from omni.ui.tests.test_base import OmniUiTest
from omni.ui.tests.compare_utils import capture_and_compare
from omni.kit.ui_test.input import emulate_mouse, emulate_mouse_slow_move, human_delay
from omni.kit.ui_test import Vec2

from omni.ui import scene as sc
import omni.ui as ui

import omni.appwindow
import omni.kit.app

import carb
from carb.input import MouseEventType

from pxr import Gf
from pathlib import Path


async def emulate_mouse_drag_and_drop(start_pos, end_pos, right_click=False, human_delay_speed: int = 4, end_with_up: bool = True):
    """Emulate Mouse Drag & Drop. Click at start position and slowly move to end position."""
    await emulate_mouse(MouseEventType.MOVE, start_pos)
    await emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN if right_click else MouseEventType.LEFT_BUTTON_DOWN)
    await human_delay(human_delay_speed)
    await emulate_mouse_slow_move(start_pos, end_pos, human_delay_speed=human_delay_speed)
    if end_with_up:
        await emulate_mouse(MouseEventType.RIGHT_BUTTON_UP if right_click else MouseEventType.LEFT_BUTTON_UP)
        await human_delay(human_delay_speed)


def _flatten_matrix(matrix: Gf.Matrix4d):
    return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
            matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
            matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
            matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]


class TestOmniUiScene(OmniUiTest):
    DATA_PATH = None

    async def setUp(self, ext_id: str = None):
        await super().setUp()
        self.__width, self.__height = None, None
        # If no extension-id, assume standard xxx.xxx.xxx.tests.current_test
        if ext_id is None:
            ext_id = '.'.join(self.__module__.split('.')[0:-2])
        TestOmniUiScene.DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${" + ext_id + "}")).absolute().resolve()
        self.__golden_img_dir = TestOmniUiScene.DATA_PATH.joinpath("data", "tests")

    # After running each test
    async def tearDown(self):
        self.__golden_img_dir = None
        await super().tearDown()

    async def setup_test_area_and_input(self, title: str, width: int = 256, height: int = 256):
        self.__width, self.__height = width, height
        await self.create_test_area(width=width, height=height)
        app_window = omni.appwindow.get_default_app_window()
        app_window.set_input_blocking_state(carb.input.DeviceType.MOUSE, False)
        return ui.Window(title=title, width=width, height=height,
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR  | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE)
        
    async def create_ortho_scene_view(self, title='test', width = 256, height = 256, ortho_size = 100, z_pos = -5):
        window = await self.setup_test_area_and_input(title, width, height)

        with window.frame:
            # Camera matrices
            projection = self.ortho_projection()
            view = sc.Matrix44.get_translation_matrix(0, 0, z_pos)
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.STRETCH, model=sc.CameraModel(projection, view))

            return window, scene_view

    async def create_perspective_scene_view(self, title='test', width = 256, height = 256, field_of_view = 25, distance = 100):
        window = await self.setup_test_area_and_input(title, width, height)

        with window.frame:
            # Camera matrices
            projection = self.perspective_projection(field_of_view)
            eye = Gf.Vec3d(distance, distance, distance)
            target = Gf.Vec3d(0, 0, 0)
            forward = (target - eye).GetNormalized()
            up = Gf.Vec3d(0, 0, 1).GetComplement(forward)
            view = _flatten_matrix(Gf.Matrix4d().SetLookAt(eye, target, up))
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.STRETCH, model=sc.CameraModel(projection, view))

            return window, scene_view

    async def finish_scene_ui_test(self, wait_frames = 15):
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()

        return await self.finalize_test(golden_img_dir=self.__golden_img_dir)

    def ortho_projection(self, ortho_size: float = 100, aspect_ratio: float = None, near: float = 0.001, far: float = 10000):
        if aspect_ratio is None:
            aspect_ratio = self.__width / self.__height

        if aspect_ratio > 1:
            ortho_half_height = ortho_size * 0.5
            ortho_half_width = ortho_half_height * aspect_ratio
        else:
            ortho_half_width = ortho_size * 0.5
            ortho_half_height = ortho_half_width * aspect_ratio
    
        frustum = Gf.Frustum()
        frustum.SetOrthographic(-ortho_half_width, ortho_half_width, -ortho_half_height, ortho_half_height, near, far)
        return _flatten_matrix(frustum.ComputeProjectionMatrix())

    def perspective_projection(self, field_of_view: float = 20, aspect_ratio: float = None, near: float = 0.001, far: float = 10000):
        if aspect_ratio is None:
            aspect_ratio = self.__width / self.__height

        frustum = Gf.Frustum()
        frustum.SetPerspective(field_of_view / aspect_ratio, aspect_ratio, near, far)
        return _flatten_matrix(frustum.ComputeProjectionMatrix())


    @property
    def golden_img_dir(self):
        return self.__golden_img_dir

    @property
    def human_delay(self):
        return 4

    async def wait_frames(self, frames: int = 15):
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

    async def end_mouse(self):
        await emulate_mouse(MouseEventType.LEFT_BUTTON_UP)
        await human_delay(self.human_delay)

    async def mouse_dragging_test(self, test_name, start_pos, end_pos):
        threshold = 10
        start_pos = Vec2(start_pos[0], start_pos[1])
        end_pos = Vec2(end_pos[0], end_pos[1])
        # Do a drag operation
        await emulate_mouse_drag_and_drop(start_pos, end_pos, human_delay_speed = self.human_delay, end_with_up=False)
        # Capture while mouse is down
        diff1 = await capture_and_compare(f'{test_name}_drag.png', threshold, self.golden_img_dir)
        # End the drag
        await self.end_mouse()
        # And cature again with mouse up
        diff2 = await capture_and_compare(f'{test_name}_done.png', threshold, self.golden_img_dir)

        if diff1 != 0:
            carb.log_warn(f"[{test_name}_drag.png] the generated image has difference {diff1}")
        if diff2 != 0:
            carb.log_warn(f"[{test_name}_done.png] the generated image has difference {diff2}")


        self.assertTrue(
            (diff1 is not None and diff1 < threshold),
            msg=f"The image for test '{test_name}_drag.png' doesn't match the golden one. Difference of {diff1} is is not less than threshold of {threshold}.",
        )
        self.assertTrue(
            (diff2 is not None and diff2 < threshold),
            msg=f"The image for test '{test_name}_done.png' doesn't match the golden one. Difference of {diff2} is is not less than threshold of {threshold}.",
        )