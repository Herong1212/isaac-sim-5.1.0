# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
from pathlib import Path
import os.path
import tempfile
import omni.usd
from carb.eventdispatcher import get_eventdispatcher

from pxr import Usd, UsdGeom, Gf, Sdf


class TestSyncAPI(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        usd_context.set_pending_edit(False)

    async def tearDown(self):
        usd_context = omni.usd.get_context()
        await usd_context.close_stage_async()

    async def test_selection_api(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        test_prim_path = "/test/level1/level2/level3"
        test_prim_path2 = "/test2/level1/level2/level3"

        xform_prim = UsdGeom.Xform.Define(stage, test_prim_path)
        xform_prim2 = UsdGeom.Xform.Define(stage, test_prim_path2)

        selection = usd_context.get_selection()
        self.assertEqual(selection.get_selected_prim_paths(), [])
        selected_prims = [
            "/test", "/test2", "/test/level1/level2", "/test2/level1/level2/level3"
        ]
        selection.set_selected_prim_paths(selected_prims, True)
        self.assertEqual(selected_prims, selection.get_selected_prim_paths())

        for i in range(4):
            self.assertTrue(selection.is_prim_path_selected(selected_prims[i]))

        selection.clear_selected_prim_paths()
        self.assertEqual(selection.get_selected_prim_paths(), [])

        for i in range(3):
            selection.set_prim_path_selected(selected_prims[i], True, False, False, False)

        self.assertEqual(selected_prims[:3], selection.get_selected_prim_paths())
        for i in range(3):
            self.assertTrue(selection.is_prim_path_selected(selected_prims[i]))

        self.assertFalse(selection.is_prim_path_selected(selected_prims[3]))

        selection.set_prim_path_selected(selected_prims[2], False, False, False, False)
        self.assertEqual(selected_prims[:2], selection.get_selected_prim_paths())
        self.assertFalse(selection.is_prim_path_selected(selected_prims[2]))

        selection.set_prim_path_selected(selected_prims[2], True, False, True, False)
        self.assertEqual([selected_prims[2]], selection.get_selected_prim_paths())
        self.assertTrue(selection.is_prim_path_selected(selected_prims[2]))
        self.assertFalse(selection.is_prim_path_selected(selected_prims[0]))
        self.assertFalse(selection.is_prim_path_selected(selected_prims[1]))

    async def test_usd_sync_api(self):
        usd_context = omni.usd.get_context()
        test_prim_path = "/test_xform"
        original_prim_list = []

        # Test new_stage
        result = usd_context.new_stage()
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)

        # With load_set = LOAD_NONE
        result = usd_context.new_stage(omni.usd.UsdContextInitialLoadSet.LOAD_NONE)
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        self.assertEqual(stage.GetLoadRules(), Usd.StageLoadRules.LoadNone())

        # Test close_stage
        result = usd_context.close_stage()
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNone(stage)

        # Test open_stage
        file_path = str(Path(__file__).parent.joinpath("data").joinpath("test_scene.usda"))
        result = usd_context.open_stage(file_path)
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        original_prim_list = [prim.GetPath() for prim in stage.TraverseAll()]

        xform_prim = UsdGeom.Xform.Define(stage, test_prim_path)
        self.assertTrue(xform_prim.GetPrim().IsValid())

        # Test reopen_stage
        result = usd_context.reopen_stage()
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        xform_prim = stage.GetPrimAtPath(test_prim_path)
        self.assertFalse(xform_prim.GetPrim().IsValid())  # We didn't save, prim should be invalid
        prim_list = [prim.GetPath() for prim in stage.TraverseAll()]
        self.assertEqual(original_prim_list, prim_list)

        # Test save_as_stage
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            result = usd_context.save_as_stage(tmp_file_path)
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            prim_list = [prim.GetPath() for prim in stage.TraverseAll()]
            self.assertEqual(original_prim_list, prim_list)

            # make a new prim
            xform_prim = UsdGeom.Xform.Define(stage, test_prim_path)
            self.assertTrue(xform_prim.GetPrim().IsValid())

            # Test save_stage
            result = usd_context.save_stage()
            self.assertTrue(result)

            # reopen the newly saved file
            result = usd_context.reopen_stage()
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            xform_prim = stage.GetPrimAtPath(test_prim_path)
            self.assertTrue(xform_prim.GetPrim().IsValid())  # We saved, prim should be valid

            # Test export_as_stage
            tmp_file_path = os.path.join(tmpdirname, "tmp_export.usda")
            prim_list_before_export = [prim.GetPath() for prim in stage.TraverseAll()]

            result = usd_context.export_as_stage(tmp_file_path)
            self.assertTrue(result)

            # open exported file
            result = usd_context.open_stage(tmp_file_path)
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)

            prim_list = [prim.GetPath() for prim in stage.TraverseAll()]
            self.assertEqual(prim_list_before_export, prim_list)

        # OM-33357: Verify no crash when opening a stage whose identifier contains characters
        # that could be interpreted as string format specifiers.
        file_path = str(Path(__file__).parent.joinpath("data").joinpath("test_%20LowFBX.usda"))
        result = usd_context.open_stage(file_path)
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)

        # OM-33357: Verify re-saving to a different format doesn't trigger bug either
        usd_context.save_as_stage(os.path.join(tempfile.gettempdir(), "test_%20LowFBX.usdc"))

    async def wait(self, frames=3):
        for _ in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_pending_edits_api(self):
        usd_context = omni.usd.get_context()
        self.assertFalse(usd_context.has_pending_edit())

        usd_context.set_pending_edit(True)
        self.assertTrue(usd_context.has_pending_edit())

        usd_context.set_pending_edit(False)

        stage = usd_context.get_stage()
        stage.DefinePrim("/World/test_prim")

        self.assertTrue(usd_context.has_pending_edit())
        usd_context.set_pending_edit(False)

        dirty = False
        def on_dirty_changed(_):
            nonlocal dirty
            dirty = usd_context.has_pending_edit()

        # Make sure it could receive event
        stage_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.usd tests update",
            event_name=usd_context.stage_event_name(omni.usd.StageEventType.DIRTY_STATE_CHANGED),
            on_event=on_dirty_changed
        )

        stage.DefinePrim("/World/test_prim_2")
        await self.wait()
        self.assertTrue(dirty)

        usd_context.set_pending_edit(False)
        await self.wait()
        self.assertFalse(dirty)

        with tempfile.TemporaryDirectory() as tmpdirname:
            # Test with on-disk layer
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            sublayer = Sdf.Layer.CreateNew(tmp_file_path)
            sublayer.Save()

            # Insert on-disk layer to anonymous root will make stage dirty also.
            stage.GetRootLayer().subLayerPaths.insert(0, tmp_file_path)
            await self.wait()
            self.assertTrue(usd_context.has_pending_edit())

            # Clean up dirty status.
            usd_context.set_pending_edit(False)
            self.assertFalse(usd_context.has_pending_edit())

            # Change sublayer will make stage dirty also
            customData = sublayer.customLayerData
            customData['test'] = 1
            sublayer.customLayerData = customData
            self.assertTrue(sublayer.dirty)
            await self.wait()
            self.assertTrue(usd_context.has_pending_edit())

            # Clear pending state even if it has unsaved changes.
            usd_context.set_pending_edit(False)
            self.assertFalse(usd_context.has_pending_edit())

            # Test on-disk layer as root layer.
            await usd_context.open_stage_async(tmp_file_path)
            # It's possible that any extension will make the stage dirty
            # Saves stage to make sure it's total clean
            await usd_context.save_stage_async()
            self.assertFalse(usd_context.has_pending_edit())

            stage = usd_context.get_stage()
            stage.DefinePrim("/World/test_prim_2")
            self.assertTrue(usd_context.has_pending_edit())
            self.assertTrue(dirty)

            usd_context.set_pending_edit(False)
            self.assertFalse(usd_context.has_pending_edit())
            self.assertTrue(usd_context.get_stage().GetRootLayer().dirty)

            # At this time, sublayer is dirty, but whole stage state is not.
            # Try to edit it again will make pending_edit to be True again.
            stage.DefinePrim("/World/test_prim_3")
            self.assertTrue(usd_context.has_pending_edit())
            self.assertTrue(dirty)
