# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pxr import UsdGeom

import omni.kit.test
import omni.usd
import omni.kit.clipboard
import omni.kit.ui_test as ui_test


class TestHotKey(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    async def _test_copy(self, prim_paths, text_to_compare):
        """Utility for testing copy."""
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        selection.set_selected_prim_paths(prim_paths, True)

        await ui_test.emulate_key_combo("CTRL+C")
        await ui_test.human_delay()

        text = omni.kit.clipboard.paste()
        # Linux line endings
        result = "\n".join(text.splitlines())
        self.assertEqual(result, text_to_compare)

    async def test_copy(self):
        """Testing CTRL+C for copy"""
        from .test_copypaste import sdf_prim_to_text
        UsdGeom.Sphere.Define(self.stage, "/Sphere01")
        UsdGeom.Sphere.Define(self.stage, "/Sphere02")

        await self._test_copy(["/Sphere01"], sdf_prim_to_text)

    async def test_paste(self):
        """Testing CTRL+V for paste"""
        UsdGeom.Sphere.Define(self.stage, "/Sphere01")
        omni.kit.clipboard.copy("dummy")

        # test that when invalid string is in the clipboard, paste doesn't do anything
        await ui_test.emulate_key_combo("CTRL+V")
        await ui_test.human_delay()
        self.assertEqual(len(self.stage.GetPseudoRoot().GetChildren()), 1)

        # select prim and copy
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        selection.set_selected_prim_paths(["/Sphere01"], True)

        await ui_test.emulate_key_combo("CTRL+C")
        await ui_test.human_delay()

        # test that prim is pasted
        await ui_test.emulate_key_combo("CTRL+V")
        await ui_test.human_delay()

        self.assertEqual(len(self.stage.GetPseudoRoot().GetChildren()), 2)
        # when pasted with a duplicated name, it will be suffixed with a number
        self.assertIsNotNone(self.stage.GetPrimAtPath("/Sphere01_01"))
