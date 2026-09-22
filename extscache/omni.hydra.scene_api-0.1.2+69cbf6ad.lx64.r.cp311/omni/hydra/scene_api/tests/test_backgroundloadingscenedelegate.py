## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.kit.test
from omni.hydra.scene_api import *

import omni.kit.app
import omni.kit.commands
import omni.kit.undo
from omni.rtx.tests import RtxTest, testSettings, postLoadTestSettings
from pxr import Gf, Usd, UsdGeom

import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
USD_DIR = EXTENSION_FOLDER_PATH.joinpath("omni/hydra/scene_api/tests/data/usd")
GOLDEN_DIR = EXTENSION_FOLDER_PATH.joinpath("omni/hydra/scene_api/tests/data/golden")


class TestBackgroundLoadingSceneDelegate(RtxTest):
    """
    An RtxTest that verifies we can load several scene delegates and they are
    all rendered.
    """

    # override resolution
    WINDOW_SIZE = (512, 512)

    # override diff threshold. Seeing some lighting diffs on teamcity that trip the
    # default threshold. All we care about is whether the item loaded, so we can have
    # a pretty flexible threshold. The default is 1e-5 currently.
    THRESHOLD = 1e-4

    async def setUp(self):
        await super().setUp()
        self.set_settings(testSettings)
        # Create a main stage in the usd_context. This is to be like a normal run,
        # where there would be a stage. We'll also put a light on it.
        omni.usd.get_context().new_stage()
        self.add_dir_light()
        await omni.kit.app.get_app().next_update_async()  # Wait stage loading
        self.set_settings(postLoadTestSettings)

    async def _pause(self):
        await omni.rtx.tests.test_common.wait_for_update(self.ctx, 5)  # Wait 5 frames before capture.

    async def test_addAndRemove(self):
        path = USD_DIR.joinpath('wonky-cylinder.usda')
        x = add_background_loading_hydra_scene_delegate('testDelegate', str(path))
        self.assertTrue(x, f'Failed to add stage {path}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="added_cylinder.png")
        x = remove_hydra_scene_delegate('testDelegate')
        self.assertTrue(x, f'Failed to remove delegate {path}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="removed_cylinder.png")

    async def test_addSameTwice(self):
        path = USD_DIR.joinpath('bunny.obj.usda')
        x = add_background_loading_hydra_scene_delegate('testDelegate', str(path))
        self.assertTrue(x, f'Failed to add stage {path}')
        x = add_background_loading_hydra_scene_delegate('testDelegate', str(path))
        self.assertFalse(x, f'second add with the same name should fail')
        x = remove_hydra_scene_delegate('testDelegate')
        self.assertTrue(x, f'Failed to remove delegate {path}')

    async def test_add_grid(self):
        path00 = USD_DIR.joinpath('cylinder00.usda')
        path01 = USD_DIR.joinpath('cylinder01.usda')
        path10 = USD_DIR.joinpath('cylinder10.usda')
        path11 = USD_DIR.joinpath('cylinder11.usda')
        x = add_background_loading_hydra_scene_delegate('cylinder00', str(path00))
        self.assertTrue(x, f'Failed to add stage {path00}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="added_cylinder00.png")
        x = add_background_loading_hydra_scene_delegate('cylinder01', str(path01))
        self.assertTrue(x, f'Failed to add stage {path01}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="added_cylinder01.png")
        x = add_background_loading_hydra_scene_delegate('cylinder10', str(path10))
        self.assertTrue(x, f'Failed to add stage {path10}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="added_cylinder10.png")
        x = add_background_loading_hydra_scene_delegate('cylinder11', str(path11))
        self.assertTrue(x, f'Failed to add stage {path11}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="added_cylinder11.png")
        x = remove_hydra_scene_delegate('cylinder00')
        self.assertTrue(x, f'Failed to remove delegate {path00}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="removed_cylinder00.png")
        x = remove_hydra_scene_delegate('cylinder01')
        self.assertTrue(x, f'Failed to remove delegate {path01}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="removed_cylinder01.png")
        x = remove_hydra_scene_delegate('cylinder10')
        self.assertTrue(x, f'Failed to remove delegate {path10}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="removed_cylinder10.png")
        x = remove_hydra_scene_delegate('cylinder11')
        self.assertTrue(x, f'Failed to remove delegate {path11}')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="removed_cylinder11.png")

    async def test_parallel_load(self):
        path00 = USD_DIR.joinpath('cylinder00.usda')
        path01 = USD_DIR.joinpath('cylinder01.usda')
        path10 = USD_DIR.joinpath('cylinder10.usda')
        path11 = USD_DIR.joinpath('cylinder11.usda')
        add_background_loading_hydra_scene_delegate('cylinder00', str(path00))
        add_background_loading_hydra_scene_delegate('cylinder01', str(path01))
        add_background_loading_hydra_scene_delegate('cylinder10', str(path10))
        add_background_loading_hydra_scene_delegate('cylinder11', str(path11))
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="parallel_load.png", threshold=1e-4)
        x = remove_hydra_scene_delegate('cylinder00')
        x = remove_hydra_scene_delegate('cylinder01')
        x = remove_hydra_scene_delegate('cylinder10')
        x = remove_hydra_scene_delegate('cylinder11')
        await self._pause()
        await self.screenshot_and_diff(GOLDEN_DIR, output_subdir="omni.hydra.scene_api",
                                       golden_img_name="parallel_unload.png")

    def _convert_mat(self, xf):
        """Convert a Gf.Matrix4d into an array of row values"""
        row0 = xf.GetRow(0)
        row1 = xf.GetRow(1)
        row2 = xf.GetRow(2)
        row3 = xf.GetRow(3)
        return [
            row0[0], row0[1], row0[2], row0[3],
            row1[0], row1[1], row1[2], row1[3],
            row2[0], row2[1], row2[2], row2[3],
            row3[0], row3[1], row3[2], row3[3],
        ]

    async def test_set_root_transform(self):
        path00 = USD_DIR.joinpath("cylinder00.usda")
        path01 = USD_DIR.joinpath("cylinder01.usda")
        add_background_loading_hydra_scene_delegate("cylinder00", str(path00))
        add_background_loading_hydra_scene_delegate("cylinder01", str(path01))
        # initial state
        await self._pause()
        await self.screenshot_and_diff(
            GOLDEN_DIR, output_subdir="omni.hydra.scene_api", golden_img_name="transform_initial.png", threshold=1e-4
        )
        # move one cylinder over
        xf = Gf.Matrix4d(1).SetTranslate(Gf.Vec3d(300, 200, 0))
        x = set_scene_delegate_root_transform("cylinder00", self._convert_mat(xf))
        self.assertTrue(x, f"Expected to set xform on cylinder00")
        await self._pause()
        await self.screenshot_and_diff(
            GOLDEN_DIR, output_subdir="omni.hydra.scene_api", golden_img_name="transform_move.png", threshold=1e-4
        )
        # rotate and scale one cylinder, move the other a second time
        xf = Gf.Matrix4d(1).SetScale(Gf.Vec3d(2.5, 2.5, 2.5)).SetRotateOnly(Gf.Rotation(Gf.Vec3d(0, 1, 0), 45.0))
        x = set_scene_delegate_root_transform("cylinder01", self._convert_mat(xf))
        self.assertTrue(x, f"Expected to set xform on cylinder01")
        xf = Gf.Matrix4d(1).SetTranslate(Gf.Vec3d(0, 0, 300))
        x = set_scene_delegate_root_transform("cylinder00", self._convert_mat(xf))
        self.assertTrue(x, f"Expected to set xform on cylinder00")
        await self._pause()
        await self.screenshot_and_diff(
            GOLDEN_DIR,
            output_subdir="omni.hydra.scene_api",
            golden_img_name="transform_scale_rotate_move.png",
            threshold=1e-4,
        )
        # cleanup
        x = remove_hydra_scene_delegate("cylinder00")
        x = remove_hydra_scene_delegate("cylinder01")
        await self._pause()
        await self.screenshot_and_diff(
            GOLDEN_DIR, output_subdir="omni.hydra.scene_api", golden_img_name="transform_unload.png"
        )

    async def test_set_bounding_box(self):
        path = USD_DIR.joinpath("bbox.usda")
        add_background_loading_hydra_scene_delegate("bbox", str(path))
        set_scene_delegate_root_transform("bbox", (1.,0.,0.,0., 0.,1.,0.,0., 0.,0.,1.,0., 100.,0.,0.,0.))
        await self._pause()
        bbox = compute_scene_delegate_world_bounding_box("bbox")
        compare_to = [50, -50, -50, 150, 50, 50, 100, 0, 0, 100, 100, 100]
        for i in range(len(compare_to)):
            self.assertEqual(compare_to[i], round(bbox[i]))
