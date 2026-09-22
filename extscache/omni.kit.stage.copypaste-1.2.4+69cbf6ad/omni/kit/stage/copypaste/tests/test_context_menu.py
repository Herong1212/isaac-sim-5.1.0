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
from omni.kit.test_suite.helpers import arrange_windows
import omni.kit.ui_test as ui_test


class TestContextMenu(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await arrange_windows("Stage", 800, 600)
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    def _find_prim_item(self, text):
        # TODO: not sure why there's two items with the same realpath in the stage window, for now pick the first one
        item = ui_test.find_all(f"Stage//Frame/**/Label[*].text=='{text}'")[0]
        self.assertTrue(item)
        return item

    async def test_copy_prim(self):
        """Test that copy prim context menu copies selected prims."""
        from .test_copypaste import sdf_prim_to_text
        UsdGeom.Sphere.Define(self.stage, "/Sphere01")
        await ui_test.human_delay(20)

        sphere = self._find_prim_item("Sphere01")
        await sphere.right_click()
        context_menu = await ui_test.get_context_menu()
        context_options = context_menu["_"]
        self.assertTrue("Copy Prim" in context_options)
        await ui_test.select_context_menu("Copy Prim")

        text = omni.kit.clipboard.paste()
        # Linux line endings
        result = "\n".join(text.splitlines())
        self.assertEqual(result, sdf_prim_to_text)

    async def test_paste_prim(self):
        """Test that paste prim context menu pastes copied prims."""
        from .test_copypaste import sdf_prim_to_text
        UsdGeom.Xform.Define(self.stage, "/root")
        await ui_test.human_delay(20)

        # prepare the clipboard with invalid content
        omni.kit.clipboard.copy("dummy")

        root = self._find_prim_item("root")
        await root.right_click()
        context_menu = await ui_test.get_context_menu()
        context_options = context_menu["_"]
        self.assertTrue("Paste Prim" in context_options)

        # test that pasting invalid content doesn't error
        await ui_test.select_context_menu("Paste Prim")
        self.assertFalse(self.stage.GetPrimAtPath("/root").GetChildren())

        # prepare valid clipboard content
        omni.kit.clipboard.copy(sdf_prim_to_text)
        # test that pasting valid content works as expected
        await root.right_click()
        await ui_test.select_context_menu("Paste Prim")
        self.assertEqual(len(self.stage.GetPrimAtPath("/root").GetChildren()), 1)
        self.assertIsNotNone(self.stage.GetPrimAtPath("/root/Sphere01"))
