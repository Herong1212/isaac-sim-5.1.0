# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.test
import omni.timeline
import omni.usd
import omni.kit.undo
from pathlib import Path
from pxr import Gf, Sdf, Usd, UsdGeom


class TestRefinement(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_scene = str(Path(__file__).parent.joinpath("data").joinpath("test_refinement.usda"))

    async def setUp(self):
        result, err = await omni.usd.get_context().open_stage_async(self._test_scene, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        self.assertTrue(result)

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    async def test_clear_refinement_overrides(self):

        stage = omni.usd.get_context().get_stage()
        values = [
            ("/World/Sphere_00", "refinementEnableOverride", True,  "refinementLevel", 3),
            ("/World/Sphere_01", "refinementEnableOverride", False, "refinementLevel", 2),
            ("/World/Sphere_02", "refinementEnableOverride", True,  "refinementLevel", 4),
            ("/World/Sphere_03", "refinementEnableOverride", True,  "refinementLevel", 5),
            ("/World/Sphere_04", "refinementEnableOverride", True,  "refinementLevel", 1),
            ("/World/Sphere_05", "refinementEnableOverride", True,  "refinementLevel", 0),
            ("/World/Sphere_06", "refinementEnableOverride", True,  "refinementLevel", 3),
            ("/World/Sphere_07", "refinementEnableOverride", True,  "refinementLevel", 2),
            ("/World/Sphere_08", "refinementEnableOverride", False, "refinementLevel", 4),
            ("/World/Sphere_09", "refinementEnableOverride", True,  "refinementLevel", 1)
        ]

        def verify_default():
            for (prim_path, attr_name_1, expected_1, attr_name_2, expected_2) in values:
                prim = stage.GetPrimAtPath(prim_path)
                attr = prim.GetAttribute(attr_name_1)
                self.assertTrue(attr.IsValid())
                self.assertEqual(attr.Get(), expected_1)
                attr = prim.GetAttribute(attr_name_2)
                self.assertTrue(attr.IsValid())
                self.assertEqual(attr.Get(), expected_2)

        def verify_removed():
            for (prim_path, attr_name_1, expected_1, attr_name_2, expected_2) in values:
                prim = stage.GetPrimAtPath(prim_path)
                attr = prim.GetAttribute(attr_name_1)
                self.assertFalse(attr.IsValid())
                attr = prim.GetAttribute(attr_name_2)
                self.assertFalse(attr.IsValid())


        # verify default values
        verify_default()

        # clear values
        omni.kit.commands.execute("ClearRefinementOverrides")

        # verify removed values
        verify_removed()

        # undo
        omni.kit.undo.undo()

        # verify default values
        verify_default()

        # undo
        omni.kit.undo.redo()

        # verify removed values
        verify_removed()

        # undo
        omni.kit.undo.undo()

        # verify default values
        verify_default()
