# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import inspect
import logging
import math
import os
from pathlib import Path
from typing import Awaitable, Callable, List

import carb
import carb.input
import carb.settings
import omni.kit.commands
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.undo
import omni.usd
from carb.input import MouseEventType
from omni.kit.manipulator.tool.snap import PRIM_SNAP_NAME, SURFACE_SNAP_NAME
from omni.kit.manipulator.tool.snap import settings_constants as snap_c
from omni.kit.manipulator.transform import Constants as transform_c
from omni.kit.test_helpers_gfx.compare_utils import ComparisonMetric, capture_and_compare
from omni.kit.ui_test import Vec2
from omni.kit.viewport.utility import get_active_viewport
from omni.ui.tests.test_base import OmniUiTest
from pxr import Gf, UsdGeom

from ..settings_constants import Constants as prim_c

CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.manipulator.prim.core}/data"))
OUTPUTS_DIR = Path(omni.kit.test.get_test_output_path()).resolve().absolute()

logger = logging.getLogger(__name__)


class TestTransform(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._context = omni.usd.get_context()
        self._selection = self._context.get_selection()
        self._settings = carb.settings.get_settings()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests").joinpath("golden")
        self._usd_scene_dir = CURRENT_PATH.absolute().resolve().joinpath("tests").joinpath("usd")
        self._window_width = self._settings.get("/app/window/width")
        self._window_height = self._settings.get("/app/window/height")
        self._human_delay_speed = 1
        if self._settings.get("/app/useFabricSceneDelegate"):
            self._human_delay_speed = 2
        # Load renderer before USD is loaded
        await self._context.new_stage_async()

    # After running each test
    async def tearDown(self):
        # Move and close the stage so selections are reset to avoid triggering ghost gestures.
        await ui_test.emulate_mouse_move(Vec2(0, 0))
        await ui_test.human_delay(5)
        await self._context.close_stage_async()

        self._golden_img_dir = None
        await super().tearDown()

    async def _snapshot(self, golden_img_name: str = "", threshold: float = 4e-5):
        await ui_test.human_delay()

        test_fn_name = ""
        for frame_info in inspect.stack():
            if os.path.samefile(frame_info[1], __file__):
                test_fn_name = frame_info[3]

        golden_img_name = f"{test_fn_name}.{golden_img_name}.png"

        # Because we're testing RTX renderered pixels, use a better threshold filter for differences
        diff = await capture_and_compare(
            golden_img_name,
            threshold=threshold,
            output_img_dir=OUTPUTS_DIR,
            golden_img_dir=self._golden_img_dir,
            metric=ComparisonMetric.MEAN_ERROR_SQUARED,
        )

        self.assertLessEqual(
            diff,
            threshold,
            f"The generated image {golden_img_name} has a difference of {diff}, but max difference is {threshold}",
        )

    async def _setup_global(
        self,
        op: str,
        enable_toolbar: bool = False,
        file_name: str = "test_scene.usda",
        prims_to_select=["/World/Cube", "/World/Xform", "/World/Xform/Cube_01"],
        placement=prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT,
    ):
        await self._setup(file_name, transform_c.TRANSFORM_MODE_GLOBAL, op, enable_toolbar, prims_to_select, placement)

    async def _setup_local(
        self,
        op: str,
        enable_toolbar: bool = False,
        file_name: str = "test_scene.usda",
        prims_to_select=["/World/Cube", "/World/Xform", "/World/Xform/Cube_01"],
        placement=prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT,
    ):
        await self._setup(file_name, transform_c.TRANSFORM_MODE_LOCAL, op, enable_toolbar, prims_to_select, placement)

    async def _setup(
        self,
        scene_file: str,
        mode: str,
        op: str,
        enable_toolbar: bool = False,
        prims_to_select=["/World/Cube", "/World/Xform", "/World/Xform/Cube_01"],
        placement=prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT,
    ):
        usd_path = self._usd_scene_dir.joinpath(scene_file)
        success, error = await self._context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        # move the mouse out of the way
        await ui_test.emulate_mouse_move(Vec2(0, 0))
        await ui_test.human_delay()

        viewport_api = get_active_viewport()
        await viewport_api.wait_for_rendered_frames(5)

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, placement)
        self._settings.set(transform_c.TRANSFORM_MOVE_MODE_SETTING, mode)
        self._settings.set(transform_c.TRANSFORM_ROTATE_MODE_SETTING, mode)
        self._settings.set(transform_c.TRANSFORM_OP_SETTING, op)
        self._settings.set("/app/viewport/snapEnabled", False)
        self._settings.set("/persistent/app/viewport/snapToSurface", False)
        self._settings.set("/exts/omni.kit.manipulator.prim.core/tools/enabled", enable_toolbar)

        self._selection.set_selected_prim_paths([], True)
        await ui_test.human_delay(human_delay_speed=10)
        self._selection.set_selected_prim_paths(prims_to_select, True)
        await ui_test.human_delay(human_delay_speed=10)

        # Save prims initial state to restore to.
        stage = self._context.get_stage()
        self._restore_transform = {}
        for prim_path in prims_to_select:
            xform_ops = []
            for xform_op in UsdGeom.Xformable(stage.GetPrimAtPath(prim_path)).GetOrderedXformOps():
                if not xform_op.IsInverseOp():
                    xform_ops.append((xform_op, xform_op.Get()))
            self._restore_transform[prim_path] = xform_ops

    async def _restore_initial_state(self):
        for xform_op_list in self._restore_transform.values():
            for xform_op_tuple in xform_op_list:
                xform_op, start_value = xform_op_tuple[0], xform_op_tuple[1]
                xform_op.Set(start_value)

    async def _emulate_mouse_drag_and_drop_multiple_waypoints(
        self,
        waypoints: List[Vec2],
        right_click=False,
        human_delay_speed: int = 4,
        num_steps: int = 8,
        on_before_drop: Callable[[int], Awaitable[None]] = None,
    ):
        """Emulate Mouse Drag & Drop. Click at start position and slowly move to end position."""
        logger.info(f"emulate_mouse_drag_and_drop poses: {waypoints} (right_click: {right_click})")

        count = len(waypoints)
        if count < 2:
            return

        await ui_test.input.emulate_mouse(MouseEventType.MOVE, waypoints[0])
        await ui_test.human_delay(human_delay_speed)
        await ui_test.input.emulate_mouse(
            MouseEventType.RIGHT_BUTTON_DOWN if right_click else MouseEventType.LEFT_BUTTON_DOWN
        )
        await ui_test.human_delay(human_delay_speed)
        for i in range(1, count):
            await ui_test.input.emulate_mouse_slow_move(
                waypoints[i - 1], waypoints[i], num_steps=num_steps, human_delay_speed=human_delay_speed
            )

        if on_before_drop:
            await ui_test.human_delay(human_delay_speed)
            await on_before_drop()

        await ui_test.input.emulate_mouse(
            MouseEventType.RIGHT_BUTTON_UP if right_click else MouseEventType.LEFT_BUTTON_UP
        )
        await ui_test.human_delay(human_delay_speed)

    ################################################################
    ################## test manipulator placement ##################
    ################################################################
    async def test_placement(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE)

        PLACEMENTS = {
            "placement_selection_center": prim_c.MANIPULATOR_PLACEMENT_SELECTION_CENTER,
            "placement_bbox_center": prim_c.MANIPULATOR_PLACEMENT_BBOX_CENTER,
            "placement_authored_pivot": prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT,
            "placement_bbox_base": prim_c.MANIPULATOR_PLACEMENT_BBOX_BASE,
        }

        for test_name, val in PLACEMENTS.items():
            self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, val)

            await ui_test.human_delay()
            await self._snapshot(test_name)

    async def test_tmp_placement(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=["/World/Xform/Cube_01", "/World/Cube"])

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_PICK_REF_PRIM)

        await ui_test.human_delay()
        await self._snapshot("pick_default")

        center = Vec2(self._window_width, self._window_height) / 2

        # pick the other prim as tmp pivot prim
        await ui_test.emulate_mouse_move_and_click(center)

        await ui_test.human_delay()
        await self._snapshot("pick")

        # move "/World/Cube", make sure the marker moves with it
        omni.kit.commands.execute("TransformPrimSRT", path="/World/Cube", new_translation=(0, 0, 300))
        await ui_test.human_delay(5)
        await self._snapshot("move")

        # move it back
        omni.kit.undo.undo()
        await ui_test.human_delay(5)

        # reset placement to last prim, the manipulator should go to last prim and marker disappears
        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT)

        await ui_test.human_delay()
        await self._snapshot("last_selected")

    async def test_bbox_placement_for_xform(self):
        await self._setup_global(
            transform_c.TRANSFORM_OP_MOVE,
            file_name="test_pivot_with_invalid_bbox.usda",
            prims_to_select=["/World/Xform"],
        )

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_BBOX_CENTER)
        await ui_test.human_delay()
        await self._snapshot("placement_bbox_center")

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_BBOX_BASE)
        await ui_test.human_delay()
        await self._snapshot("placement_bbox_base")

    ################################################################
    ####################### test translation #######################
    ################################################################

    ################## test manipulator move axis ##################
    async def test_move_global_axis(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE)
        await self._test_move_axis()

    async def test_move_local_axis(self):
        await self._setup_local(transform_c.TRANSFORM_OP_MOVE)
        await self._test_move_axis(180)

    async def _test_move_axis(self, angle_offset: float = 0, distance: float = 50):
        OFFSET = 50
        MOVEMENT = ["x", "y", "z"]

        center = Vec2(self._window_width, self._window_height) / 2

        for i, test_name in enumerate(MOVEMENT):
            await ui_test.human_delay()

            dir = Vec2(
                math.cos(math.radians(-i * 120 + 30 + angle_offset)),
                math.sin(math.radians(-i * 120 + 30 + angle_offset)),
            )
            try:
                await ui_test.emulate_mouse_drag_and_drop(center + dir * OFFSET, center + dir * (OFFSET + distance))
                await self._snapshot(f"{test_name}.{angle_offset}.{distance}")
            finally:
                await self._restore_initial_state()

    ################## test manipulator move plane ##################
    async def test_move_global_plane(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE)
        await self._test_move_plane()

    async def test_move_local_plane(self):
        await self._setup_local(transform_c.TRANSFORM_OP_MOVE)
        await self._test_move_plane(180)

    async def _test_move_plane(self, angle_offset: float = 0, distance=75):
        OFFSET = 50
        MOVEMENT = ["xz", "zy", "yx"]

        center = Vec2(self._window_width, self._window_height) / 2

        for i, test_name in enumerate(MOVEMENT):
            await ui_test.human_delay()

            dir = Vec2(
                math.cos(math.radians(-i * 120 + 90 + angle_offset)),
                math.sin(math.radians(-i * 120 + 90 + angle_offset)),
            )
            try:
                await ui_test.emulate_mouse_drag_and_drop(center + dir * OFFSET, center + dir * (OFFSET + distance))
                await self._snapshot(f"{test_name}.{angle_offset}.{distance}")
            finally:
                await self._restore_initial_state()

    ################## test manipulator move center ##################
    async def test_move_global_center(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE)
        await self._test_move_center()
        await self._test_move_center(
            modifier=carb.input.KeyboardInput.LEFT_ALT
        )  # with alt down, transform is not changed

    async def test_move_local_center(self):
        await self._setup_local(transform_c.TRANSFORM_OP_MOVE)
        await self._test_move_center()

    async def _test_move_center(self, dirs=[Vec2(50, 0)], modifier: carb.input.KeyboardInput = None):
        try:
            center = Vec2(self._window_width, self._window_height) / 2

            waypoints = [center]
            for dir in dirs:
                waypoints.append(center + dir)

            if modifier:
                await ui_test.input.emulate_keyboard(carb.input.KeyboardEventType.KEY_PRESS, modifier)
                await ui_test.human_delay()

            await self._emulate_mouse_drag_and_drop_multiple_waypoints(
                waypoints, human_delay_speed=self._human_delay_speed
            )

            if modifier:
                await ui_test.input.emulate_keyboard(carb.input.KeyboardEventType.KEY_RELEASE, modifier)
                await ui_test.human_delay()

            test_name = f"xyz.{len(dirs)}"
            if modifier:
                test_name += str(modifier).split(".")[-1]
            await self._snapshot(test_name)  # todo better hash name?
        finally:
            await self._restore_initial_state()

    # Test manipulator is placed correctly if the selected prim's parent is moved
    async def test_move_selected_parent(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=["/World/Xform/Cube_01"])
        stage = self._context.get_stage()
        parent_translate_attr = stage.GetAttributeAtPath("/World/Xform.xformOp:translate")
        try:
            parent_translate_attr.Set((0, 100, -100))
            await ui_test.human_delay(4)
            await self._snapshot()
        finally:
            await self._restore_initial_state()

    # Test manipulator is placed correctly if the selected prim is moved by USD update
    async def test_move_selected_self(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=["/World/Xform/Cube_01"])
        stage = self._context.get_stage()
        parent_translate_attr = stage.GetAttributeAtPath("/World/Xform/Cube_01.xformOp:translate")
        try:
            parent_translate_attr.Set((0, 100, -100))
            await ui_test.human_delay(4)
            await self._snapshot()
        finally:
            await self._restore_initial_state()

    ################################################################
    ######################## test rotation #########################
    ################################################################

    ################## test manipulator rotate arc ##################
    async def test_rotate_global_arc(self):
        await self._setup_global(transform_c.TRANSFORM_OP_ROTATE)
        await self._test_rotate_arc()

    # add a test to only select prims in the same hierarchy and pivot prim being the child
    # to cover the bug when consolidated prim path has one entry and is not the pivot prim
    async def test_rotate_global_arc_single_hierarchy(self):
        await self._setup_global(
            transform_c.TRANSFORM_OP_ROTATE, prims_to_select=["/World/Xform", "/World/Xform/Cube_01"]
        )
        await self._test_rotate_arc()

    async def test_rotate_local_arc(self):
        await self._setup_local(transform_c.TRANSFORM_OP_ROTATE)
        await self._test_rotate_arc(180)

    async def test_free_rotation_clamped(self):
        stored_human_delay = self._human_delay_speed
        self._human_delay_speed = 10
        await self._setup_global(transform_c.TRANSFORM_OP_ROTATE)
        self._settings.set(transform_c.FREE_ROTATION_TYPE_SETTING, transform_c.FREE_ROTATION_TYPE_CLAMPED)
        await self._test_move_center(dirs=[Vec2(100, 100)])
        self._human_delay_speed = stored_human_delay

    async def test_free_rotation_continuous(self):
        await self._setup_global(transform_c.TRANSFORM_OP_ROTATE)
        self._settings.set(transform_c.FREE_ROTATION_TYPE_SETTING, transform_c.FREE_ROTATION_TYPE_CONTINUOUS)
        await self._test_move_center(dirs=[Vec2(100, 100)])

    async def test_bbox_center_multi_prim_rotate_global(self):
        stored_human_delay = self._human_delay_speed
        self._human_delay_speed = 10
        await self._test_bbox_center_multi_prim_rotate(self._setup_global)
        self._human_delay_speed = stored_human_delay

    async def test_bbox_center_multi_prim_rotate_local(self):
        stored_human_delay = self._human_delay_speed
        self._human_delay_speed = 10
        await self._test_bbox_center_multi_prim_rotate(self._setup_local)
        self._human_delay_speed = stored_human_delay

    async def _test_bbox_center_multi_prim_rotate(self, test_fn):
        await test_fn(
            transform_c.TRANSFORM_OP_ROTATE,
            file_name="test_bbox_rotation.usda",
            prims_to_select=["/World/Cube", "/World/Cube_01", "/World/Cube_02"],
            placement=prim_c.MANIPULATOR_PLACEMENT_BBOX_CENTER,
        )
        await self._test_rotate_arc(post_snap=True)

    async def _test_rotate_arc(self, offset: float = 0, post_snap=False):
        OFFSET = 45
        MOVEMENT = ["x", "y", "z", "screen"]
        SEGMENT_COUNT = 12

        center = Vec2(self._window_width, self._window_height) / 2

        for i, test_name in enumerate(MOVEMENT):
            await ui_test.human_delay()

            waypoints = []

            step = 360 / SEGMENT_COUNT
            for wi in range(int(SEGMENT_COUNT * 1.5)):
                dir = Vec2(
                    math.cos(math.radians(-i * 120 - 30 + wi * step + offset)),
                    math.sin(math.radians(-i * 120 - 30 + wi * step + offset)),
                )
                waypoints.append(center + dir * (OFFSET if i < 3 else 80))

            try:

                async def before_drop():
                    await self._snapshot(test_name)

                await self._emulate_mouse_drag_and_drop_multiple_waypoints(
                    waypoints, on_before_drop=before_drop, human_delay_speed=self._human_delay_speed
                )

                if post_snap:
                    await ui_test.human_delay(human_delay_speed=4)
                    await self._snapshot(f"{test_name}.post")
            finally:
                await self._restore_initial_state()

    ################################################################
    ########################## test scale ##########################
    ################################################################

    # Given the complexity of multi-manipulating with non-uniform scale and potential shear from parents,
    # we reduce the test complexity using a simpler manipulating case.
    # Revisit when there's more complicated scaling needs.

    ################## test manipulator scale axis ##################
    async def test_scale_local_axis(self):
        await self._setup_local(transform_c.TRANSFORM_OP_SCALE)
        self._selection.set_selected_prim_paths(["/World/Xform/Cube_01"], True)
        await ui_test.human_delay()

        # test scale up
        await self._test_move_axis(180)

        # test scale down
        await self._test_move_axis(180, distance=-100)

    ################## test manipulator scale plane ##################
    async def test_scale_local_plane(self):
        await self._setup_local(transform_c.TRANSFORM_OP_SCALE)
        self._selection.set_selected_prim_paths(["/World/Xform/Cube_01"], True)
        await ui_test.human_delay()

        # test scale up
        await self._test_move_plane(180)

        # test scale down
        await self._test_move_plane(180, distance=-100)

    ################## test manipulator scale center ##################
    async def test_scale_local_center(self):
        await self._setup_local(transform_c.TRANSFORM_OP_SCALE)
        self._selection.set_selected_prim_paths(["/World/Xform/Cube_01"], True)
        await ui_test.human_delay()

        await self._test_move_center(dirs=[Vec2(0, -50)])

        await ui_test.human_delay()

        await self._test_move_center(dirs=[Vec2(0, -50), Vec2(0, 100)])

    ###### test manipulator scale center with float xformOps #########
    # OM-109231
    async def test_scale_local_center_float(self):
        await self._setup_local(transform_c.TRANSFORM_OP_SCALE, file_name="test_scene_float.usda")
        self._selection.set_selected_prim_paths(["/World/Xform/Cube_01"], True)
        await ui_test.human_delay()

        await self._test_move_center(dirs=[Vec2(0, -50)])

        await ui_test.human_delay()

        await self._test_move_center(dirs=[Vec2(0, -50), Vec2(0, 100)])

    ################################################################
    ################### test manipulator toolbar ###################
    ################################################################
    async def test_toolbar(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, True)

        await ui_test.human_delay(30)
        # move it slowly, otherwise it may not be able to click on the collapsable header and instead unselects the prim
        await ui_test.input.emulate_mouse_slow_move(Vec2(0, 0), Vec2(210, 345), num_steps=16, human_delay_speed=10)
        await ui_test.human_delay(5)
        await ui_test.emulate_mouse_click()
        await ui_test.human_delay(human_delay_speed=20)

        # expand the toolbar and take a snapshot to make sure the render/layout is correct.
        # if you changed the look of toolbar button or toolbar layout, update the golden image for this test.
        # added since OM-65012 for a broken button image
        await self._snapshot("visual")

        # Test the local/global button
        await ui_test.human_delay(30)
        await ui_test.emulate_mouse_move_and_click(Vec2(215, 365), human_delay_speed=20)
        self.assertEqual(self._settings.get(transform_c.TRANSFORM_MOVE_MODE_SETTING), transform_c.TRANSFORM_MODE_LOCAL)

        await ui_test.human_delay(30)
        await ui_test.emulate_mouse_move_and_click(Vec2(215, 365), human_delay_speed=20)
        self.assertEqual(self._settings.get(transform_c.TRANSFORM_MOVE_MODE_SETTING), transform_c.TRANSFORM_MODE_GLOBAL)

    ################################################################
    #################### test manipulator snap #####################
    ################################################################
    async def _run_snap_test(self, keep_spacing: bool):
        await self._setup_global(
            transform_c.TRANSFORM_OP_MOVE, True, "test_snap.usda", ["/World/Cube", "/World/Cube_01"]
        )
        stage = self._context.get_stage()

        cube_prim = stage.GetPrimAtPath("/World/Cube")
        cube01_prim = stage.GetPrimAtPath("/World/Cube_01")

        _, _, _, translate_cube_original = omni.usd.get_local_transform_SRT(cube_prim)
        _, _, _, translate_cube01_original = omni.usd.get_local_transform_SRT(cube01_prim)

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_SELECTION_CENTER)
        self._settings.set(snap_c.SNAP_PROVIDER_NAME_SETTING_PATH, [SURFACE_SNAP_NAME])
        self._settings.set(snap_c.CONFORM_TO_TARGET_SETTING_PATH, True)
        self._settings.set(snap_c.KEEP_SPACING_SETTING_PATH, keep_spacing)
        self._settings.set("/app/viewport/snapEnabled", True)

        center = Vec2(self._window_width, self._window_height) / 2

        await ui_test.human_delay()
        await ui_test.emulate_mouse_move(center, 10)

        await self._emulate_mouse_drag_and_drop_multiple_waypoints(
            [center, center / 1.5], human_delay_speed=1, num_steps=50
        )

        _, _, _, translate_cube = omni.usd.get_local_transform_SRT(cube_prim)
        _, _, _, translate_cube01 = omni.usd.get_local_transform_SRT(cube01_prim)

        self._settings.set("/app/viewport/snapEnabled", False)

        return translate_cube, translate_cube_original, translate_cube01, translate_cube01_original

    async def test_snap_keep_spacing(self):
        (
            translate_cube,
            translate_cube_original,
            translate_cube01,
            translate_cube01_original,
        ) = await self._run_snap_test(True)

        # Make sure start conditions aren't already on Plane
        self.assertFalse(Gf.IsClose(translate_cube_original[1], -100, 0.02))
        self.assertFalse(Gf.IsClose(translate_cube01_original[1], -100, 0.02))

        # Y position should be snapped to surface at -100 Y (within a tolerance for Storm)
        self.assertTrue(Gf.IsClose(translate_cube[1], -100, 0.02))
        self.assertTrue(Gf.IsClose(translate_cube01[1], -100, 0.02))

        # X and Z should be greater than original
        self.assertTrue(translate_cube[0] > translate_cube_original[0])
        self.assertTrue(translate_cube[2] > translate_cube_original[2])

        # X and Z should be greater than original
        self.assertTrue(translate_cube01[2] > translate_cube01_original[2])
        self.assertTrue(translate_cube01[0] > translate_cube01_original[0])

        # Workaround for testing on new Viewport, needs delay before running test_snap_no_keep_spacing test.
        self._selection.set_selected_prim_paths([], True)
        await ui_test.human_delay(10)

    async def test_snap_no_keep_spacing(self):
        (
            translate_cube,
            translate_cube_original,
            translate_cube01,
            translate_cube01_original,
        ) = await self._run_snap_test(False)

        self.assertFalse(Gf.IsClose(translate_cube_original[1], -100, 0.02))
        self.assertFalse(Gf.IsClose(translate_cube01_original[1], -100, 0.02))

        # cube and cube01 should be at same location since keep spacing is off
        self.assertTrue(Gf.IsClose(translate_cube, translate_cube01, 1e-6))

        # Y position should be snapped to surface at -100 Y
        self.assertTrue(Gf.IsClose(translate_cube[1], -100, 0.02))

        # X and Z should be greater than original
        self.assertTrue(translate_cube[0] > translate_cube_original[0])
        self.assertTrue(translate_cube[2] > translate_cube_original[2])

        # Workaround for testing on new Viewport, needs delay before running test_snap_no_keep_spacing test.
        self._selection.set_selected_prim_paths([], True)
        await ui_test.human_delay(10)

    async def test_snap_orient(self):
        try:
            import omni.kit.viewport_legacy

            # Don't test VP1. Prim snap only works with VP2
            return
        except ImportError:
            pass

        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=["/World/Cube"])
        stage = self._context.get_stage()

        cube_prim = stage.GetPrimAtPath("/World/Cube")
        cube01_prim = stage.GetPrimAtPath("/World/Xform/Cube_01")

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_SELECTION_CENTER)
        self._settings.set(snap_c.SNAP_PROVIDER_NAME_SETTING_PATH, [PRIM_SNAP_NAME])
        self._settings.set(snap_c.CONFORM_TO_TARGET_SETTING_PATH, True)
        self._settings.set(snap_c.KEEP_SPACING_SETTING_PATH, True)
        self._settings.set(snap_c.CONFORM_UP_AXIS_SETTING_PATH, "Stage")
        self._settings.set("/app/viewport/snapEnabled", True)

        start = Vec2(166, 296)
        end = Vec2(self._window_width, self._window_height) / 2

        await ui_test.human_delay()
        await ui_test.emulate_mouse_move(start, 10)
        await self._emulate_mouse_drag_and_drop_multiple_waypoints([start, end], human_delay_speed=1, num_steps=50)

        xform_cube = Gf.Matrix4d(*self._context.compute_path_world_transform("/World/Cube"))
        xform_cube_01 = Gf.Matrix4d(*self._context.compute_path_world_transform("/World/Xform/Cube_01"))

        self.assertTrue(Gf.IsClose(xform_cube.ExtractTranslation(), xform_cube_01.ExtractTranslation(), 1e-4))

        rotation_cube = xform_cube.GetOrthonormalized().ExtractRotationMatrix()
        rotation_cube_01 = xform_cube_01.GetOrthonormalized().ExtractRotationMatrix()

        self.assertTrue(Gf.IsClose(rotation_cube, rotation_cube_01, 1e-4))

        self._settings.set("/app/viewport/snapEnabled", False)

    ################################################################
    ##################### test prim with pivot #####################
    ################################################################
    async def _test_move_axis_one_dir(self, dir: Vec2 = Vec2(0, 1), distance: float = 50):
        OFFSET = 50

        center = Vec2(self._window_width, self._window_height) / 2

        try:
            await ui_test.emulate_mouse_drag_and_drop(center + dir * OFFSET, center + dir * (OFFSET + distance))
            await self._snapshot(f"{distance}")
        finally:
            await self._restore_initial_state()

    async def test_move_local_axis_with_pivot(self):
        # tests for when _should_keep_manipulator_orientation_unchanged is true
        await self._setup_local(
            transform_c.TRANSFORM_OP_MOVE, file_name="test_pivot.usda", prims_to_select=["/World/Cube"]
        )
        await self._test_move_axis_one_dir()

    async def test_scale_local_axis_with_pivot(self):
        # tests for when _should_keep_manipulator_orientation_unchanged is true
        await self._setup_local(
            transform_c.TRANSFORM_OP_SCALE, file_name="test_pivot.usda", prims_to_select=["/World/Cube"]
        )
        await self._test_move_axis_one_dir()

    ################################################################
    ##################### test remove xformOps #####################
    ################################################################
    async def test_remove_xform_ops_pivot(self):
        # remove the xformOps attributes, the manipulator position should update
        await self._setup_local(
            transform_c.TRANSFORM_OP_MOVE, file_name="test_remove_xformOps.usda", prims_to_select=["/World/Cube"]
        )

        stage = self._context.get_stage()
        cube_prim = stage.GetPrimAtPath("/World/Cube")

        attrs_to_remove = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
        for attr in attrs_to_remove:
            cube_prim.RemoveProperty(attr)

        await ui_test.human_delay(10)
        await self._snapshot()

    async def test_remove_xform_op_order_pivot(self):
        # remove the xformOpOrder attribute, the manipulator position should update
        await self._setup_local(
            transform_c.TRANSFORM_OP_MOVE, file_name="test_remove_xformOps.usda", prims_to_select=["/World/Cube"]
        )

        stage = self._context.get_stage()
        cube_prim = stage.GetPrimAtPath("/World/Cube")
        cube_prim.RemoveProperty("xformOpOrder")

        await ui_test.human_delay(10)
        await self._snapshot()

    ################################################################
    ################### test unknown op & modes ####################
    ################################################################
    async def test_unknown_move_mode(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=["/World/Xform/Cube_01"])
        await self._snapshot("pre-unknown-mode")
        self._settings.set(transform_c.TRANSFORM_MOVE_MODE_SETTING, "UNKNOWN")
        await self._snapshot("post-unknown-mode")
        self._settings.set(transform_c.TRANSFORM_MOVE_MODE_SETTING, transform_c.TRANSFORM_MODE_LOCAL)
        await self._snapshot("reset-known-mode")

    async def test_unknown_rotate_mode(self):
        await self._setup_global(transform_c.TRANSFORM_OP_ROTATE, prims_to_select=["/World/Xform/Cube_01"])
        await self._snapshot("pre-unknown-mode")
        self._settings.set(transform_c.TRANSFORM_ROTATE_MODE_SETTING, "UNKNOWN")
        await self._snapshot("post-unknown-mode")
        self._settings.set(transform_c.TRANSFORM_ROTATE_MODE_SETTING, transform_c.TRANSFORM_MODE_LOCAL)
        await self._snapshot("reset-known-mode")

    async def test_unknown_mode_enabled(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=[])
        await self._snapshot("known-mode-unselected")
        self._settings.set(transform_c.TRANSFORM_MOVE_MODE_SETTING, "UNKNOWN")
        await self._snapshot("unknown-mode-unselected")
        self._selection.set_selected_prim_paths(["/World/Xform/Cube_01"], True)
        await self._snapshot("unknown-mode-selected")
        self._settings.set(transform_c.TRANSFORM_MOVE_MODE_SETTING, transform_c.TRANSFORM_MODE_GLOBAL)
        await self._snapshot("known-mode-selected")

    async def test_unknown_op_enabled(self):
        await self._setup_global(transform_c.TRANSFORM_OP_MOVE, prims_to_select=[])
        await self._snapshot("move-op-unselected")
        self._settings.set(transform_c.TRANSFORM_OP_SETTING, "UNKNOWN")
        await self._snapshot("unknown-op-selected")
        self._selection.set_selected_prim_paths(["/World/Xform/Cube_01"], True)
        await self._snapshot("unknown-op-selected")
        self._settings.set(transform_c.TRANSFORM_OP_SETTING, transform_c.TRANSFORM_OP_ROTATE)
        await self._snapshot("rotate-op-selected")
