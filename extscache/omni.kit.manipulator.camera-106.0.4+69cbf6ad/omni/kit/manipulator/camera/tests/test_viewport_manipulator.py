## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestViewportCamera']

import omni.kit.app
import omni.kit.ui_test as ui_test
from carb.input import MouseEventType, KeyboardEventType, KeyboardInput
from pxr import Gf, Sdf, UsdGeom

TEST_GUTTER = 10
TEST_WIDTH, TEST_HEIGHT = 500, 500
TEST_UI_CENTER = ui_test.Vec2(TEST_WIDTH / 2, TEST_HEIGHT / 2)
TEST_UI_LEFT = ui_test.Vec2(TEST_GUTTER, TEST_UI_CENTER.y)
TEST_UI_RIGHT = ui_test.Vec2(TEST_WIDTH - TEST_GUTTER, TEST_UI_CENTER.y)
TEST_UI_TOP = ui_test.Vec2(TEST_UI_CENTER.x, TEST_GUTTER)
TEST_UI_BOTTOM = ui_test.Vec2(TEST_UI_CENTER.x, TEST_HEIGHT - TEST_GUTTER)

class TestViewportCamera(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        from omni.kit.viewport.utility import get_active_viewport
        self.viewport = get_active_viewport()

        await self.viewport.usd_context.new_stage_async()
        self.stage = self.viewport.stage

        self.camera = UsdGeom.Xformable(self.stage.GetPrimAtPath(self.viewport.camera_path))
        # Disable locking to render results, as there are no render-results
        self.viewport.lock_to_render_result = False

        super().setUp()
        await self.wait_n_updates()

    # After running each test
    async def tearDown(self):
        super().tearDown()

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for _ in range(n_frames):
            await app.next_update_async()

    async def __do_mouse_interaction(self,
                                     mouse_down: MouseEventType,
                                     start: ui_test.Vec2,
                                     end: ui_test.Vec2,
                                     mouse_up: MouseEventType,
                                     modifier: KeyboardInput | None = None):
        if modifier:
            await ui_test.input.emulate_keyboard(KeyboardEventType.KEY_PRESS, modifier)
            await ui_test.human_delay()
        else:
            await self.wait_n_updates(10)

        await ui_test.input.emulate_mouse(MouseEventType.MOVE, start)
        await ui_test.input.emulate_mouse(mouse_down, start)
        await ui_test.input.emulate_mouse_slow_move(start, end)
        await ui_test.input.emulate_mouse(mouse_up, end)

        if modifier:
            await ui_test.input.emulate_keyboard(KeyboardEventType.KEY_RELEASE, modifier)
            await ui_test.human_delay()
        else:
            await self.wait_n_updates()

    def assertIsClose(self, a, b):
        self.assertTrue(Gf.IsClose(a, b, 0.1))

    def assertRotationIsClose(self, a, b):
        self.assertTrue(Gf.IsClose(a.GetReal(), b.GetReal(), 0.1))
        self.assertTrue(Gf.IsClose(a.GetImaginary(), b.GetImaginary(), 0.1))

    @property
    def camera_position(self):
        return self.camera.GetLocalTransformation(self.viewport.time).ExtractTranslation()

    @property
    def camera_rotation(self):
        return self.camera.GetLocalTransformation(self.viewport.time).ExtractRotation().GetQuaternion()

    async def test_viewport_scroll(self, is_locked: bool = False):
        """Test scrollwheel with a Viewport"""
        test_pos = [
            Gf.Vec3d(500, 500, 500),
            Gf.Vec3d(1007.76, 1007.76, 1007.76),
            Gf.Vec3d(555.97, 555.97, 555.97),
        ]
        if is_locked:
            test_pos = [test_pos[0]] * len(test_pos)

        await ui_test.input.emulate_mouse_move_and_click(TEST_UI_CENTER)
        self.assertIsClose(self.camera_position, test_pos[0])

        await ui_test.input.emulate_mouse_scroll(ui_test.Vec2(0, -2500))
        await self.wait_n_updates(100)
        self.assertIsClose(self.camera_position, test_pos[1])

        await ui_test.input.emulate_mouse_scroll(ui_test.Vec2(0, 1000))
        await self.wait_n_updates(100)
        self.assertIsClose(self.camera_position, test_pos[2])

    async def test_viewport_pan(self, is_locked: bool = False):
        """Test panning across a Viewport"""
        test_pos = [
            Gf.Vec3d(500, 500, 500),
            Gf.Vec3d(1189.86, 500, -189.86),
            Gf.Vec3d(699.14, 101.7, 699.14),
        ]
        if is_locked:
            test_pos = [test_pos[0]] * len(test_pos)

        self.assertIsClose(self.camera_position, test_pos[0])

        await self.__do_mouse_interaction(MouseEventType.MIDDLE_BUTTON_DOWN,
                                          TEST_UI_RIGHT, TEST_UI_LEFT,
                                          MouseEventType.MIDDLE_BUTTON_UP)
        self.assertIsClose(self.camera_position, test_pos[1])

        await self.__do_mouse_interaction(MouseEventType.MIDDLE_BUTTON_DOWN,
                                          TEST_UI_LEFT, TEST_UI_RIGHT,
                                          MouseEventType.MIDDLE_BUTTON_UP)
        self.assertIsClose(self.camera_position, test_pos[0])

        await self.__do_mouse_interaction(MouseEventType.MIDDLE_BUTTON_DOWN,
                                          TEST_UI_CENTER, TEST_UI_TOP,
                                          MouseEventType.MIDDLE_BUTTON_UP)
        self.assertIsClose(self.camera_position, test_pos[2])

        await self.__do_mouse_interaction(MouseEventType.MIDDLE_BUTTON_DOWN,
                                          TEST_UI_CENTER, TEST_UI_BOTTOM,
                                          MouseEventType.MIDDLE_BUTTON_UP)
        self.assertIsClose(self.camera_position, test_pos[0])


    async def test_viewport_look(self, is_locked: bool = False):
        """Test panning across a Viewport"""
        test_rot = [
            Gf.Quaternion(0.88, Gf.Vec3d(-0.27, 0.36, 0.11)),
            Gf.Quaternion(-0.33, Gf.Vec3d(0.10, 0.89,  0.28)),
            Gf.Quaternion(0.86, Gf.Vec3d(0.33, 0.35, -0.13)),
        ]
        if is_locked:
            test_rot = [test_rot[0]] * len(test_rot)

        self.assertRotationIsClose(self.camera_rotation, test_rot[0])

        await self.__do_mouse_interaction(MouseEventType.RIGHT_BUTTON_DOWN,
                                          TEST_UI_RIGHT, TEST_UI_LEFT,
                                          MouseEventType.RIGHT_BUTTON_UP)
        self.assertRotationIsClose(self.camera_rotation, test_rot[1])

        await self.__do_mouse_interaction(MouseEventType.RIGHT_BUTTON_DOWN,
                                          TEST_UI_LEFT, TEST_UI_RIGHT,
                                          MouseEventType.RIGHT_BUTTON_UP)
        self.assertRotationIsClose(self.camera_rotation, test_rot[0])

        await self.__do_mouse_interaction(MouseEventType.RIGHT_BUTTON_DOWN,
                                          TEST_UI_CENTER, TEST_UI_TOP,
                                          MouseEventType.RIGHT_BUTTON_UP)
        self.assertRotationIsClose(self.camera_rotation, test_rot[2])

        await self.__do_mouse_interaction(MouseEventType.RIGHT_BUTTON_DOWN,
                                          TEST_UI_CENTER, TEST_UI_BOTTOM,
                                          MouseEventType.RIGHT_BUTTON_UP)
        self.assertRotationIsClose(self.camera_rotation, test_rot[0])

    async def __test_viewport_orbit_modifer_not_working(self, is_locked: bool = False):
        """Test orbit across a Viewport"""
        test_rot = [
            Gf.Quaternion(0.88, Gf.Vec3d(-0.27, 0.36, 0.11)),
            Gf.Quaternion(-0.33, Gf.Vec3d(0.10, 0.89,  0.28)),
            Gf.Quaternion(0.86, Gf.Vec3d(0.33, 0.35, -0.13)),
        ]
        if is_locked:
            test_rot = [test_rot[0]] * len(test_rot)

        await ui_test.input.emulate_mouse_move_and_click(TEST_UI_CENTER)
        self.assertRotationIsClose(self.camera_rotation, test_rot[0])

        await self.__do_mouse_interaction(MouseEventType.LEFT_BUTTON_DOWN,
                                          TEST_UI_RIGHT, TEST_UI_LEFT,
                                          MouseEventType.LEFT_BUTTON_UP,
                                          KeyboardInput.LEFT_ALT)
        self.assertRotationIsClose(self.camera_rotation, test_rot[1])

        await self.__do_mouse_interaction(MouseEventType.LEFT_BUTTON_DOWN,
                                          TEST_UI_LEFT, TEST_UI_RIGHT,
                                          MouseEventType.LEFT_BUTTON_UP,
                                          KeyboardInput.LEFT_ALT)
        self.assertRotationIsClose(self.camera_rotation, test_rot[0])

        await self.__do_mouse_interaction(MouseEventType.LEFT_BUTTON_DOWN,
                                          TEST_UI_CENTER, TEST_UI_TOP,
                                          MouseEventType.LEFT_BUTTON_UP,
                                          KeyboardInput.LEFT_ALT)
        self.assertRotationIsClose(self.camera_rotation, test_rot[2])

        await self.__do_mouse_interaction(MouseEventType.LEFT_BUTTON_DOWN,
                                          TEST_UI_CENTER, TEST_UI_BOTTOM,
                                          MouseEventType.LEFT_BUTTON_UP,
                                          KeyboardInput.LEFT_ALT)
        self.assertRotationIsClose(self.camera_rotation, test_rot[0])


    async def test_viewport_lock(self):
        """Test the lock attribute blocks navigation"""
        self.camera.GetPrim().CreateAttribute("omni:kit:cameraLock", Sdf.ValueTypeNames.Bool, True).Set(True)
        await self.test_viewport_pan(is_locked=True)
        await self.test_viewport_look(is_locked=True)
        await self.test_viewport_scroll(is_locked=True)
