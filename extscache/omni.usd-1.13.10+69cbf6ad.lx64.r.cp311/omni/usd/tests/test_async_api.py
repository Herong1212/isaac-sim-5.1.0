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
import omni.client.utils as clientutils
from carb.eventdispatcher import get_eventdispatcher

from pxr import Usd, UsdGeom, Gf, Sdf


class TestAsyncAPI(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_scene = str(Path(__file__).parent.joinpath("data").joinpath("test_scene.usda"))

    async def test_usd_async_api(self):
        usd_context = omni.usd.get_context()
        test_prim_path = "/test_xform"
        original_prim_list = []

        # Test new_stage_async, load_set = LOAD_ALL
        (result, err) = await usd_context.new_stage_async()
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)

        # Try to save the new stage and make sure Sdf.Path.absolutePath is not unloaded.
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp3.usda")

            await omni.usd.get_context().save_as_stage_async(tmp_file_path)
            stage = omni.usd.get_context().get_stage()
            for path, rule in stage.GetLoadRules().GetRules():
                if path == Sdf.Path.absoluteRootPath:
                    self.assertEqual(rule, Usd.StageLoadRules.AllRule)
                    break

            # New stage to release tmp file
            await usd_context.new_stage_async()

        # With load_set = LOAD_NONE
        (result, err) = await usd_context.new_stage_async(omni.usd.UsdContextInitialLoadSet.LOAD_NONE)
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        self.assertEqual(stage.GetLoadRules(), Usd.StageLoadRules.LoadNone())

        payload_prim = stage.DefinePrim("/root/payload", "Xform")
        payload_prim.GetPayloads().AddPayload(self._test_scene)
        self.assertTrue(Sdf.Path("/root/payload") not in set(stage.GetLoadSet()))
        stage.Load("/root/payload")
        self.assertTrue(Sdf.Path("/root/payload") in set(stage.GetLoadSet()))

        # Try to save the new stage and make sure Sdf.Path.absolutePath is still unloaded.
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp2.usda")

            await omni.usd.get_context().save_as_stage_async(tmp_file_path)
            stage = omni.usd.get_context().get_stage()
            self.assertEqual(set(stage.GetLoadSet()), set([Sdf.Path("/root/payload")]))

            for path, rule in stage.GetLoadRules().GetRules():
                if path == Sdf.Path.absoluteRootPath:
                    self.assertEqual(rule, Usd.StageLoadRules.NoneRule)
                    break

            # New stage to release tmp file
            await usd_context.new_stage_async()

        # Test close_stage_async
        (result, err) = await usd_context.close_stage_async()
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNone(stage)

        # Test open_stage_async
        (result, err) = await usd_context.open_stage_async(self._test_scene)
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        original_prim_list = [prim.GetPath() for prim in stage.TraverseAll()]

        xform_prim = UsdGeom.Xform.Define(stage, test_prim_path)
        self.assertTrue(xform_prim.GetPrim().IsValid())

        # Test reopen_stage_async
        (result, err) = await usd_context.reopen_stage_async()
        self.assertTrue(result)
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        xform_prim = stage.GetPrimAtPath(test_prim_path)
        self.assertFalse(xform_prim.GetPrim().IsValid())  # We didn't save, prim should be invalid
        prim_list = [prim.GetPath() for prim in stage.TraverseAll()]
        self.assertEqual(original_prim_list, prim_list)

        # Test save_as_stage_async
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            (result, err, saved_layers) = await usd_context.save_as_stage_async(tmp_file_path)
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            prim_list = [prim.GetPath() for prim in stage.TraverseAll()]
            self.assertEqual(original_prim_list, prim_list)

            # make a new prim
            xform_prim = UsdGeom.Xform.Define(stage, test_prim_path)
            self.assertTrue(xform_prim.GetPrim().IsValid())

            # Test save_stage_async
            (result, err, saved_layers) = await usd_context.save_stage_async()
            self.assertTrue(result)

            # reopen the newly saved file
            (result, err) = await usd_context.reopen_stage_async()
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            xform_prim = stage.GetPrimAtPath(test_prim_path)
            self.assertTrue(xform_prim.GetPrim().IsValid())  # We saved, prim should be valid

            # Save with sublayes
            all_sublayers = []
            for i in range(5):
                sublayer_file_path = os.path.join(tmpdirname, f"tmp{i}.usda")
                sublayer = Sdf.Layer.CreateNew(sublayer_file_path)
                all_sublayers.append(sublayer.identifier)
                sublayer.Save()
                self.assertFalse(sublayer.dirty)
                stage.GetRootLayer().subLayerPaths.append(sublayer.identifier)

                Sdf.CreatePrimInLayer(sublayer, "/test/sublayerPrim")

                self.assertTrue(sublayer.dirty)

            await usd_context.save_layers_async("", all_sublayers)

            for identifier in all_sublayers:
                sublayer = Sdf.Find(identifier)
                self.assertFalse(sublayer.dirty)
                self.assertTrue(sublayer.GetPrimAtPath("/test/sublayerPrim"))

            # reopen the newly saved file to check if sublayer is saved again.
            (result, err) = await usd_context.reopen_stage_async()
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            for identifier in all_sublayers:
                sublayer = Sdf.Find(identifier)
                self.assertFalse(sublayer.dirty)
                self.assertTrue(sublayer.GetPrimAtPath("/test/sublayerPrim"))

            # Test export_as_stage_async
            tmp_file_path = os.path.join(tmpdirname, "tmp_export.usda")
            prim_list_before_export = [prim.GetPath() for prim in stage.TraverseAll()]

            (result, err) = await usd_context.export_as_stage_async(tmp_file_path)
            self.assertTrue(result)

            # open exported file
            (result, err) = await usd_context.open_stage_async(tmp_file_path)
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)

            prim_list = [prim.GetPath() for prim in stage.TraverseAll()]
            self.assertEqual(prim_list_before_export, prim_list)

    async def test_hydra_context(self):
        context_name = "testcontext"

        event_count = 0
        def stage_event_cb(event):
            nonlocal event_count
            event_count += 1

        new_usd_context = omni.usd.create_context(context_name)
        self.assertIsNotNone(new_usd_context)

        stage_event_subscription = [
            get_eventdispatcher().observe_event(
                event_name=new_usd_context.stage_event_name(omni.usd.StageEventType(val)),
                on_event=stage_event_cb
            )
            for val in range(int(omni.usd.StageEventType.COUNT))
        ]
        self.assertIsNotNone(stage_event_subscription)

        await new_usd_context.open_stage_async(self._test_scene)

        self.assertGreater(event_count, 0)

        # test next_stage_event_async
        def dummy(*_):
            pass
        new_usd_context.reopen_stage_with_callback(dummy) # start a reload but don't wait for the event
        event, dict = await new_usd_context.next_stage_event_async()
        self.assertIsInstance(event, int)
        self.assertIsInstance(dict, type({}))

        omni.usd.destroy_context(context_name)

    async def test_save_as_with_layer_offsets(self):
        await omni.usd.get_context().new_stage_async()

        stage = omni.usd.get_context().get_stage()
        with tempfile.TemporaryDirectory() as tmpdirname:
            sublayer_path = os.path.join(tmpdirname, "sublayer.usda")
            layer = Sdf.Layer.CreateNew(sublayer_path)
            root_layer = stage.GetRootLayer()
            root_layer.subLayerPaths.append(layer.identifier)
            root_layer.subLayerOffsets[0] = Sdf.LayerOffset(2.0, 3.0)
            sublayer_offset = root_layer.subLayerOffsets[0]
            self.assertTrue(float(sublayer_offset.offset) == 2.0 and float(sublayer_offset.scale) == 3.0)

            for ext in [".usdc", ".usda", ".usd"]:
                new_stage_path = os.path.join(tmpdirname, "new_stage" + ext)
                await omni.usd.get_context().save_as_stage_async(new_stage_path)

                stage = omni.usd.get_context().get_stage()
                root_layer = stage.GetRootLayer()
                self.assertTrue(os.path.normpath(root_layer.identifier), os.path.normpath(new_stage_path))
                # Make sure offsets and scales are not changed
                sublayer_offset = root_layer.subLayerOffsets[0]
                self.assertTrue(float(sublayer_offset.offset) == 2.0 and float(sublayer_offset.scale) == 3.0)

            # Releases all to not hold handles to tmp folder.
            root_layer = None
            stage = None
            layer = None
            await omni.usd.get_context().new_stage_async()

    async def test_save_as_with_payloads_disabled(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        with tempfile.TemporaryDirectory() as tmpdirname:
            payload1 = os.path.join(tmpdirname, "payload1.usda")
            payload2 = os.path.join(tmpdirname, "payload2.usda")
            payload1_layer = Sdf.Layer.CreateNew(payload1)
            payload2_layer = Sdf.Layer.CreateNew(payload2)
            payload_stage = Usd.Stage.Open(payload1_layer)
            payload_stage.DefinePrim("/payload1/child", "Xform")
            payload_stage = Usd.Stage.Open(payload2_layer)
            payload_stage.DefinePrim("/payload2/child", "Xform")
            payload_stage = None

            payload1_prim = stage.DefinePrim("/root/payload1", "Xform")
            payload2_prim = stage.DefinePrim("/root/payload2", "Xform")
            payload1_prim.GetPayloads().AddPayload(payload1_layer.identifier)
            payload2_prim.GetPayloads().AddPayload(payload2_layer.identifier)
            stage.Unload("/root/payload2")

            self.assertEqual(set(stage.GetLoadSet()), set([Sdf.Path("/root/payload1")]))
            payload1_layer = None
            payload2_layer = None

            for extension in ["usda", "usd"]:
                new_stage_path = os.path.join(tmpdirname, f"new_stage_payloads_disabled.{extension}")
                await omni.usd.get_context().save_as_stage_async(new_stage_path)

                stage = omni.usd.get_context().get_stage()
                self.assertEqual(set(stage.GetLoadSet()), set([Sdf.Path("/root/payload1")]))

            # New stage to release layer references so temp files can be removed.
            await omni.usd.get_context().new_stage_async()

    async def test_save_as_with_target_opened(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        test_prim_path = "/test"
        stage.DefinePrim(test_prim_path, "Cube")

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            (result, err, saved_layers) = await usd_context.save_as_stage_async(tmp_file_path)
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            self.assertTrue(stage.GetPrimAtPath(test_prim_path))

            # OM-95979: Open target layer and hold its handle
            # to see if save-as can be done successfully to avoid
            # losing data.
            tmp_file_path = os.path.join(tmpdirname, "tmp2.usda")
            new_layer = Sdf.Layer.FindOrOpen(tmp_file_path)
            if new_layer:
                new_layer.Clear()
                new_layer.Save()
            else:
                new_layer = Sdf.Layer.CreateNew(tmp_file_path)

            (result, err, saved_layers) = await usd_context.save_as_stage_async(tmp_file_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(tmp_file_path))
            self.assertTrue(clientutils.equal_urls(tmp_file_path, usd_context.get_stage_url()))
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            self.assertTrue(stage.GetPrimAtPath(test_prim_path))

            stage = None
            await usd_context.close_stage_async()

    async def test_save_as_with_different_path_style(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        test_prim_path = "/test"
        stage.DefinePrim(test_prim_path, "Cube")

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            (result, err, saved_layers) = await usd_context.save_as_stage_async(tmp_file_path)
            self.assertTrue(result)
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)
            self.assertTrue(stage.GetPrimAtPath(test_prim_path))

            # OM-95979: Uses different path separator to ensure it does not influence
            # save functionality to treat them as different path.
            import platform

            if platform.system().lower() == "windows":
                tmp_file_path = os.path.join(tmpdirname, f"tmp2.usda")
                tmp_file_path = tmp_file_path.replace("\\", "/")
                (result, err, saved_layers) = await usd_context.save_as_stage_async(tmp_file_path)
                self.assertTrue(result)
                stage = usd_context.get_stage()
                self.assertIsNotNone(stage)
                self.assertTrue(stage.GetPrimAtPath(test_prim_path))

            stage = None
            await usd_context.close_stage_async()

    async def test_open_stage_with_session_layer(self):
        session_layer = Sdf.Layer.CreateAnonymous()
        spec = Sdf.CreatePrimInLayer(session_layer, "/test_prim_in_session_layer")

        with tempfile.TemporaryDirectory() as tmpdirname:
            stage_path = os.path.join(tmpdirname, "test_stage.usd")
            Sdf.Layer.CreateNew(stage_path)
            await omni.usd.get_context().open_stage_async(stage_path, session_layer_url=session_layer.identifier)

            stage = omni.usd.get_context().get_stage()
            self.assertEqual(stage.GetSessionLayer().identifier, session_layer.identifier)
            self.assertTrue(stage.GetSessionLayer().GetPrimAtPath(spec.path) is not None)

            stage = None
            session_layer = None
            await omni.usd.get_context().new_stage_async()
