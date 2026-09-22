## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from pathlib import Path
from unittest.mock import patch
import carb

import os
import omni.kit.test
import omni.usd
import omni.client
import tempfile
import omni.client.utils as clientutils

from pxr import Sdf, Usd, UsdGeom, Gf, UsdShade

class TestUsdUtils(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_payload = str(Path(__file__).parent.joinpath("data").joinpath("test_payload.usda"))

    async def setUp(self):
        usd_context = omni.usd.get_context()
        omni.client.set_retries(0, 0, 0)
        await usd_context.new_stage_async()
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)

    async def tearDown(self):
        usd_context = omni.usd.get_context()

        if usd_context.get_stage():
            await usd_context.close_stage_async()
        omni.client.set_retries(*self.previous_retry_values)

    def test_is_usd_writable_filetype(self):
        for path, is_writable in [
            ("omniverse://test-server/test.usd", True),
            ("omniverse://test-server/test.usda", True),
            ("omniverse://test-server/test.usdc", True),
            ("omniverse://test-server/test.usdz", False),
            ("omniverse://test-server/test.usdg", False),
            ("omniverse://test-server/test.abc", False),
            ("omniverse://test-server/test.sdf", False),
            ("omniverse://test-server/test.drc", False),
            ("omniverse://test-server/test.txt", False),
            ("omniverse://test-server/test.usd?a=1", True),
            ("omniverse://test-server/test.usd?a=1#fragment", True),
            ("omniverse://test-server/test.usd.a=1#fragment", False),
            ("omniverse://test-server/test.txt?otherFile.usd?a=1", False),
            ("omniverse://test-server/invalid_path", False),
        ]:
            self.assertEqual(omni.usd.is_usd_writable_filetype(path),
                             is_writable)
            self.assertEqual(bool(omni.usd.writable_usd_re().match(path)),
                             is_writable)

    def test_is_usd_readable_filetype(self):
        for path, is_writable in [
            ("omniverse://test-server/test.usd", True),
            ("omniverse://test-server/test.usda", True),
            ("omniverse://test-server/test.usdc", True),
            ("omniverse://test-server/test.usdz", True),
            ("omniverse://test-server/test.usdg", False),
            ("omniverse://test-server/test.abc", True),
            ("omniverse://test-server/test.sdf", False),
            ("omniverse://test-server/test.drc", True),
            ("omniverse://test-server/test.txt", False),
            ("omniverse://test-server/test.abc?a=1", True),
            ("omniverse://test-server/test.abc?a=1#fragment", True),
            ("omniverse://test-server/test.abc.a=1#fragment", False),
            ("omniverse://test-server/test.txt?otherFile.abc?a=1", False),
            ("omniverse://test-server/invalid_path", False),
        ]:
            self.assertEqual(omni.usd.is_usd_readable_filetype(path),
                             is_writable)
            self.assertEqual(bool(omni.usd.readable_usd_re().match(path)),
                             is_writable)

    async def test_get_stage_next_free_path(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/World")
        prim_duplicate =stage.DefinePrim("/World_01")
        stage.SetDefaultPrim(prim)

        # Verifies it raises an exception on invalid path
        with self.assertRaises(ValueError):
            omni.usd.get_stage_next_free_path(stage, "1234567", False)

        # Verifies path without leading slash + not parent under default prim
        path = omni.usd.get_stage_next_free_path(stage, "World", False)
        self.assertEqual(path, "/World_02")

        # Verifies path with leading slash + not parent under default prim
        path = omni.usd.get_stage_next_free_path(stage, "/World", False)
        self.assertEqual(path, "/World_02")

        # Verifies path is not modified if source prim already exists
        # This handles the situation like this:
        # We already have a prim '/World/Path' and '/World/Path_01' now if we want to rename
        # '/World/Path_01' to '/World/Path', we should not change '/World/Path_01' to '/World/Path_02'
        # because '/World/Path_01' is already the desired path.
        path = omni.usd.get_stage_next_free_path(stage, "/World", False, source_prim=prim_duplicate)
        self.assertEqual(path, "/World_01")

        # Verifies path without leading slash + parent under default prim
        path = omni.usd.get_stage_next_free_path(stage, "World", True)
        self.assertEqual(path, "/World/World")

        # Verifies path with leading slash + parent under default prim
        path = omni.usd.get_stage_next_free_path(stage, "/World", True)
        self.assertEqual(path, "/World/World")

        # Verifies path without leading slash + parent under default prim
        path = omni.usd.get_stage_next_free_path(stage, "Path", True)
        self.assertEqual(path, "/World/Path")

        # Verifies path with leading slash + parent under default prim
        path = omni.usd.get_stage_next_free_path(stage, "/Path", True)
        self.assertEqual(path, "/World/Path")

        # Verifies path with leading slash matching default prim is not modified
        path = omni.usd.get_stage_next_free_path(stage, "World/Path", True)
        self.assertEqual(path, "/World/Path")

        # Verifies path without leading slash matching default prim is correct but not modified
        path = omni.usd.get_stage_next_free_path(stage, "/World/Path", True)
        self.assertEqual(path, "/World/Path")

    def _get_test_stage_with_references_and_payloads(self):
        layer_content = '''\
            #usda 1.0
        '''

        layer0_content = """\
            #usda 1.0

            over "root" (
                delete payload = [
                    @assets/Cube.usda@,
                    @assets/Capsule.usda@
                ]
                delete references = [
                    @assets/Cube.usda@,
                    @assets/Capsule.usda@
                ]
            )
            {
            }
        """

        layer1_content = """\
            #usda 1.0

            over "root" (
                append payload = [
                    @assets/Cylinder.usda@,
                    @assets/Capsule.usda@
                ]
                append references = [
                    @assets/Cylinder.usda@,
                    @assets/Capsule.usda@
                ]
            )
            {
            }
        """

        layer2_content = """\
            #usda 1.0

            over "root" (
                payload = [
                    @assets/Cube.usda@,
                    @assets/Sphere.usda@
                ]
                references = [
                    @assets/Cube.usda@,
                    @assets/Sphere.usda@
                ]
            )
            {
            }
        """

        layer3_content = """\
            #usda 1.0

            over "root" (
                prepend payload = [
                    @assets/Cone.usda@,
                ]
                prepend references = [
                    @assets/Cone.usda@,
                ]
            )
            {
            }
        """

        layer4_content = """\
            #usda 1.0

            def Xform "root" (
            )
            {
            }
        """

        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/a.usd")
        layer0 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd")
        layer1 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer1.usd")
        layer2 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer2.usd")
        layer3 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer3.usd")
        layer4 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer4.usd")
        layer.ImportFromString(layer_content)
        layer0.ImportFromString(layer0_content)
        layer1.ImportFromString(layer1_content)
        layer2.ImportFromString(layer2_content)
        layer3.ImportFromString(layer3_content)
        layer4.ImportFromString(layer4_content)
        layer.subLayerPaths.append(layer0.identifier)
        layer.subLayerPaths.append(layer1.identifier)
        layer.subLayerPaths.append(layer2.identifier)
        layer.subLayerPaths.append(layer3.identifier)
        layer.subLayerPaths.append(layer4.identifier)

        stage = Usd.Stage.Open(layer)

        ref_and_layer_map = {
            "assets/Cone.usda": layer3,
            "assets/Cube.usda": layer2,
            "assets/Sphere.usda": layer2,
            "assets/Cylinder.usda": layer1,
            "assets/Capsule.usda": layer1
        }

        layers = {
            "delete": layer0,
            "append": layer1,
            "explicit": layer2,
            "prepend": layer3
        }

        return stage, ref_and_layer_map, layers

    async def test_get_composed_references(self):
        stage, ref_and_layer_map, layers = self._get_test_stage_with_references_and_payloads()

        def verify(ref_and_layers, ref_paths):
            # same size
            self.assertTrue(len(ref_and_layers) == len(ref_paths))

            # same ref and layer and order:
            for i in range(len(ref_paths)):
                ref_path = ref_paths[i]
                info = ref_and_layers[i]
                self.assertTrue(info[0].assetPath == ref_path)
                golden_layer = ref_and_layer_map.get(info[0].assetPath, None)
                self.assertTrue(golden_layer is not None)
                self.assertTrue(info[1] is not None)
                self.assertTrue(info[1] == golden_layer)

        test_prim = stage.GetPrimAtPath("/root")
        references = omni.usd.get_composed_references_from_prim(test_prim)
        verify(references, ["assets/Sphere.usda", "assets/Cylinder.usda"])

        async def mute_and_test(layer_to_mute, ref_paths):
            stage.MuteLayer(layer_to_mute.identifier)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            references = omni.usd.get_composed_references_from_prim(test_prim)
            verify(references, ref_paths)

        # Mute delete layer, more references should be composed
        await mute_and_test(layers["delete"], ["assets/Cube.usda", "assets/Sphere.usda", "assets/Cylinder.usda", "assets/Capsule.usda"])

        # Mute append layer, reference should be removed
        await mute_and_test(layers["append"], ["assets/Cube.usda", "assets/Sphere.usda"])

        # Mute explicit layer, reference should be removed from explicit layer and prepend layer show up
        await mute_and_test(layers["explicit"], ["assets/Cone.usda"])

        # Mute prepend layer, reference should be empty
        await mute_and_test(layers["prepend"], [])

    async def test_get_composed_payloads(self):
        stage, payload_and_layer_map, layers = self._get_test_stage_with_references_and_payloads()

        def verify(ref_and_layers, ref_paths):
            # same size
            self.assertTrue(len(ref_and_layers) == len(ref_paths))

            # same ref and layer and order:
            for i in range(len(ref_paths)):
                ref_path = ref_paths[i]
                info = ref_and_layers[i]
                self.assertTrue(info[0].assetPath == ref_path)
                golden_layer = payload_and_layer_map.get(info[0].assetPath, None)
                self.assertTrue(golden_layer is not None)
                self.assertTrue(info[1] is not None)
                self.assertTrue(info[1] == golden_layer)

        test_prim = stage.GetPrimAtPath("/root")
        payloads = omni.usd.get_composed_payloads_from_prim(test_prim)
        verify(payloads, ["assets/Sphere.usda", "assets/Cylinder.usda"])

        async def mute_and_test(layer_to_mute, ref_paths):
            stage.MuteLayer(layer_to_mute.identifier)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            payloads = omni.usd.get_composed_payloads_from_prim(test_prim)
            verify(payloads, ref_paths)

        # Mute delete layer, more payloads should be composed
        await mute_and_test(layers["delete"], ["assets/Cube.usda", "assets/Sphere.usda", "assets/Cylinder.usda", "assets/Capsule.usda"])

        # Mute append layer, payload should be removed
        await mute_and_test(layers["append"], ["assets/Cube.usda", "assets/Sphere.usda"])

        # Mute explicit layer, payload should be removed from explicit layer and prepend layer show up
        await mute_and_test(layers["explicit"], ["assets/Cone.usda"])

        # Mute prepend layer, payload should be empty
        await mute_and_test(layers["prepend"], [])

    async def test_get_introducing_layer(self):
        root_layer = Sdf.Layer.CreateAnonymous()
        reference_layer = Sdf.Layer.CreateAnonymous()
        payload_layer = Sdf.Layer.CreateAnonymous()
        reference_of_reference_layer = Sdf.Layer.CreateAnonymous()
        stage = Usd.Stage.Open(reference_of_reference_layer)
        cube2_prim = UsdGeom.Cube.Define(stage, '/root/cube2')
        stage.SetDefaultPrim(cube2_prim.GetPrim().GetParent())
        stage = Usd.Stage.Open(reference_layer)
        cube_prim = UsdGeom.Cube.Define(stage, '/root/cube')
        stage.DefinePrim("/root/reference").GetReferences().AddReference(reference_of_reference_layer.identifier)
        stage.SetDefaultPrim(cube_prim.GetPrim().GetParent())
        stage = Usd.Stage.Open(payload_layer)
        sphere_prim = UsdGeom.Cube.Define(stage, '/root/sphere')
        stage.SetDefaultPrim(sphere_prim.GetPrim().GetParent())
        stage = Usd.Stage.Open(root_layer)
        root_prim = UsdGeom.Xform.Define(stage, "/root")
        root_prim.GetPrim().GetReferences().AddReference(reference_layer.identifier)
        root_prim.GetPrim().GetPayloads().AddPayload(payload_layer.identifier)
        self.assertEqual(omni.usd.get_introducing_layer(root_prim.GetPrim())[0], root_layer)

        cube_prim = stage.GetPrimAtPath("/root/cube")
        self.assertTrue(cube_prim)
        sphere_prim = stage.GetPrimAtPath("/root/cube")
        cube2_prim = stage.GetPrimAtPath("/root/reference/cube2")
        self.assertTrue(sphere_prim)
        UsdGeom.XformCommonAPI(cube_prim).SetTranslate(Gf.Vec3d(0.0, 0.0, 0.0))
        UsdGeom.XformCommonAPI(sphere_prim).SetTranslate(Gf.Vec3d(0.0, 0.0, 0.0))

        for prim in [cube_prim, sphere_prim, cube2_prim]:
            intro_layer, intro_prim_path = omni.usd.get_introducing_layer(prim)
            self.assertEqual(intro_layer, root_layer)
            self.assertEqual(intro_prim_path, root_prim.GetPath())

    async def test_load_payload(self):
        # LOAD_ALL
        (result, err) = await omni.usd.get_context().close_stage_async()
        self.assertTrue(result)

        (result, err) = await omni.usd.get_context().open_stage_async(
            self._test_payload, omni.usd.UsdContextInitialLoadSet.LOAD_ALL
        )
        self.assertTrue(result)

        stage = omni.usd.get_context().get_stage()
        world = stage.GetPrimAtPath("/World")
        # World should have children because we loaded all
        self.assertNotEqual(len(world.GetChildren()), 0)

        # LOAD_NONE
        (result, err) = await omni.usd.get_context().close_stage_async()
        self.assertTrue(result)

        (result, err) = await omni.usd.get_context().open_stage_async(
            self._test_payload, omni.usd.UsdContextInitialLoadSet.LOAD_NONE
        )
        self.assertTrue(result)

        stage = omni.usd.get_context().get_stage()
        world = stage.GetPrimAtPath("/World")
        # World should not have children because we loaded all
        self.assertEqual(len(world.GetChildren()), 0)

    async def test_duplicate(self):
        format = Sdf.FileFormat.FindByExtension(".usd")
        reference_layer = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/references/reference1.usd")
        stage1 = Usd.Stage.Open(reference_layer)
        xform = stage1.DefinePrim("/xform")
        stage1.SetDefaultPrim(xform)
        reference_path = xform.GetPath().AppendElementString("reference")
        reference1_prim = stage1.DefinePrim(reference_path)

        reference_layer2 = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/references/deep/reference2.usd")
        stage2 = Usd.Stage.Open(reference_layer2)
        cube = UsdGeom.Cube.Define(stage2, "/cube")
        # Creates another cube under the parent and defines its relationship so that
        # it can be used to check if the relationship is remapped after duplicate.
        cube2 = UsdGeom.Cube.Define(stage2, "/cube/test_cube")
        rel = cube2.GetPrim().CreateRelationship("test_relationship");
        rel.SetTargets(["/cube"])
        stage2.SetDefaultPrim(cube.GetPrim())
        reference1_prim.GetReferences().AddReference("./deep/reference2.usd")

        sublayer = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/sublayers/sublayer.usd")
        stage3 = Usd.Stage.Open(sublayer)
        xform = UsdGeom.Xform.Define(stage3, "/World/xform")
        stage3.SetDefaultPrim(xform.GetPrim().GetParent())
        xform.GetPrim().GetReferences().AddReference("../references/reference1.usd")

        root_layer = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/stage/root.usd")
        root_layer.subLayerPaths.append(sublayer.identifier)
        stage = Usd.Stage.Open(root_layer)

        def verify_references(prim, expected_reference_paths):
            references = omni.usd.get_composed_references_from_prim(prim)
            reference_paths = set()
            for ref_and_layer in references:
                reference, layer = ref_and_layer
                reference_paths.add(layer.ComputeAbsolutePath(reference.assetPath))

            self.assertEqual(reference_paths, set(expected_reference_paths))

        # Duplicates prim to the edit target
        for layer in [sublayer, root_layer]:
            with Usd.EditContext(stage, layer):
                duplicate_prim_path = omni.usd.get_stage_next_free_path(stage, "/World/xform", False)
                omni.usd.duplicate_prim(stage, "/World/xform", duplicate_prim_path, False)

                prim_spec = layer.GetPrimAtPath(duplicate_prim_path)
                self.assertTrue(prim_spec)

                prim = stage.GetPrimAtPath(duplicate_prim_path)
                self.assertTrue(prim)
                verify_references(prim, ["omniverse://invalid-fake-server/test_dir/references/reference1.usd"])

                prim = stage.GetPrimAtPath(Sdf.Path(duplicate_prim_path).AppendElementString("reference"))
                self.assertTrue(prim)
                verify_references(prim, ["omniverse://invalid-fake-server/test_dir/references/deep/reference2.usd"])

                # Duplicate prim from external reference layer
                duplicate_prim_path = omni.usd.get_stage_next_free_path(stage, "/World/xform/reference", False)
                omni.usd.duplicate_prim(stage, "/World/xform/reference", duplicate_prim_path, False)

                prim_spec = layer.GetPrimAtPath(duplicate_prim_path)
                self.assertTrue(prim_spec)

                # Check relationship to see if it's remapped also.
                test_cube_path = Sdf.Path(duplicate_prim_path).AppendElementString("test_cube")
                prim = stage.GetPrimAtPath(test_cube_path)
                self.assertTrue(prim)
                rel = prim.GetRelationship("test_relationship")
                targets = rel.GetTargets()
                self.assertEqual(len(targets), 1)
                self.assertTrue(str(targets[0]).startswith("/World/xform/reference"))

                prim = stage.GetPrimAtPath(duplicate_prim_path)
                self.assertTrue(prim)
                verify_references(prim, ["omniverse://invalid-fake-server/test_dir/references/deep/reference2.usd"])

        # Duplicate all layers
        with Usd.EditContext(stage, root_layer):
            prim = stage.GetPrimAtPath("/World/xform")
            prim.CreateAttribute("test_attribute", Sdf.ValueTypeNames.Bool)

            prim = stage.GetPrimAtPath("/World/xform/reference")
            prim.CreateAttribute("test_attribute", Sdf.ValueTypeNames.Bool)

        duplicate_prim_path = omni.usd.get_stage_next_free_path(stage, "/World/xform", False)
        omni.usd.duplicate_prim(stage, "/World/xform", duplicate_prim_path, True)
        prim_spec = sublayer.GetPrimAtPath(duplicate_prim_path)
        self.assertTrue(prim_spec)
        prim_spec = root_layer.GetPrimAtPath(duplicate_prim_path)
        self.assertTrue(prim_spec)

        prim = stage.GetPrimAtPath(duplicate_prim_path)
        self.assertTrue(prim)
        verify_references(prim, ["omniverse://invalid-fake-server/test_dir/references/reference1.usd"])

        prim = stage.GetPrimAtPath(Sdf.Path(duplicate_prim_path).AppendElementString("reference"))
        self.assertTrue(prim)
        verify_references(prim, ["omniverse://invalid-fake-server/test_dir/references/deep/reference2.usd"])

        # It has only one reference
        references = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(references), 1)
        self.assertEqual(references[0][1], reference_layer)

        # Duplicate prim from external reference layer
        duplicate_prim_path = omni.usd.get_stage_next_free_path(stage, "/World/xform/reference", False)
        omni.usd.duplicate_prim(stage, "/World/xform/reference", duplicate_prim_path, True)

        prim_spec = sublayer.GetPrimAtPath(duplicate_prim_path)
        self.assertTrue(prim_spec)
        prim_spec = root_layer.GetPrimAtPath(duplicate_prim_path)
        self.assertTrue(prim_spec)

        prim = stage.GetPrimAtPath(duplicate_prim_path)
        self.assertTrue(prim)
        verify_references(prim, ["omniverse://invalid-fake-server/test_dir/references/deep/reference2.usd"])

        references = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(references), 1)
        self.assertEqual(references[0][1], sublayer)

        # Bug test for OM-56561
        layer1_content = """\
#usda 1.0
(
    defaultPrim = "Xform"
)

def Xform "Xform"
{
    double3 xformOp:rotateXYZ = (0, 0, 0)
    double3 xformOp:scale = (1, 1, 1)
    double3 xformOp:translate = (0, 0, 0)
    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]

    def Cube "Cube"
    {
        float3[] extent = [(-50, -50, -50), (50, 50, 50)]
        double size = 100
        double3 xformOp:rotateXYZ = (0, 0, 0)
        double3 xformOp:scale = (1, 1, 1)
        double3 xformOp:translate = (0, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    }
}
        """

        layer2_content = """\
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def "test_cube" (
        instanceable = false
        prepend references = @./1.usd@
    )
    {
        double3 xformOp:rotateXYZ = (0, -0, 0)
        double3 xformOp:scale = (1, 1, 1)
        double3 xformOp:translate = (-233.219, 17.7878, -7.136)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    }
}
        """

        expected_string = """\
#usda 1.0

def Xform "test" (
    prepend references = @omniverse://invalid-fake-server/test_dir/2.usd@
)
{
    def "test_cube2" (
        instanceable = false
        prepend references = @./1.usd@
    )
    {
        double3 xformOp:rotateXYZ = (0, -0, 0)
        double3 xformOp:scale = (1, 1, 1)
        double3 xformOp:translate = (-233.219, 17.7878, -7.136)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    }
}
"""
        reference_layer = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/1.usd")
        reference_layer.ImportFromString(layer1_content)

        parent_reference_layer = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/2.usd")
        parent_reference_layer.ImportFromString(layer2_content)

        root_layer = Sdf.Layer.New(format, "omniverse://invalid-fake-server/test_dir/3.usd")
        stage = Usd.Stage.Open(root_layer)
        prim = stage.DefinePrim("/test", "Xform")
        prim.GetReferences().AddReference(parent_reference_layer.identifier)
        omni.usd.duplicate_prim(stage, "/test/test_cube", "/test/test_cube2", False)
        string = root_layer.ExportToString()
        self.assertEqual(string.strip(), expected_string.strip())

    async def test_get_usd_context_from_stage(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()
        self.assertTrue(omni.usd.get_context_from_stage(stage), usd_context)

        stage = Usd.Stage.CreateInMemory()
        await usd_context.attach_stage_async(stage)
        self.assertTrue(omni.usd.get_context_from_stage(stage), usd_context)

    async def _run_local_transform_SRT(self, cpp, pre, pivot):
        usd_context = omni.usd.get_context()

        stage = Usd.Stage.CreateInMemory()
        await usd_context.attach_stage_async(stage)

        rotate_ops = [
                UsdGeom.XformOp.TypeRotateZ,
                UsdGeom.XformOp.TypeRotateX,
                UsdGeom.XformOp.TypeRotateY,
                UsdGeom.XformOp.TypeRotateZYX,
                UsdGeom.XformOp.TypeRotateXYZ,
                UsdGeom.XformOp.TypeRotateXZY,
                UsdGeom.XformOp.TypeRotateYXZ,
                UsdGeom.XformOp.TypeRotateYZX,
                UsdGeom.XformOp.TypeRotateZXY,
                UsdGeom.XformOp.TypeOrient
                ]

        index = 0
        for rotate_op in rotate_ops:
            xform = UsdGeom.Xform.Define(stage, "/xform" + str(index))
            index = index + 1
            xformamble = UsdGeom.Xformable(xform.GetPrim())
            if pre:
                xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
                ur_scale = Gf.Vec3d(10, 10, 10)
                xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)
            xformamble.AddTranslateOp().Set((0, 0, 0))
            if pivot:
                xformamble.AddTranslateOp(opSuffix='pivot', isInverseOp=False).Set(Gf.Vec3d(0, 0, 0))
            ro = xformamble.AddXformOp(rotate_op)
            if rotate_op == UsdGeom.XformOp.TypeOrient:
                ro.Set(Gf.Quatd(1.0))
            elif rotate_op <= UsdGeom.XformOp.TypeRotateZ:
                ro.Set(0.0)
            else:
                ro.Set(Gf.Vec3d(0.0))
            xformamble.AddScaleOp().Set((1, 1, 1))
            if not pre:
                xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
                ur_scale = Gf.Vec3d(10, 10, 10)
                xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)
            if pivot:
                xformamble.AddTranslateOp(opSuffix='pivot', isInverseOp=True)

            if pivot:
                self.assertTrue(len(xform.GetOrderedXformOps()) == 7)
            else:
                self.assertTrue(len(xform.GetOrderedXformOps()) == 5)

            tolerance_epsilon = 1e-4
            (s, r, ro, t) = omni.usd.get_local_transform_SRT(xform)
            self.assertTrue(Gf.IsClose(ur_scale, s, tolerance_epsilon))
            self.assertTrue(abs(r[0] + 90.0) < tolerance_epsilon)

            if cpp:
                translation = (1, 2, 3)
                rotation_euler = (0, 0, 0)
                scale = (30, 20, 10)
                omni.kit.commands.execute(
                    "TransformPrimSRTCpp",
                    path=xform.GetPrim().GetPrimPath().pathString,
                    new_translation=translation,
                    new_rotation_euler=rotation_euler,
                    new_scale=scale,
                )
            else:
                translation = Gf.Vec3d(1, 2, 3)
                rotation_euler = Gf.Vec3d(0, 0, 0)
                scale = Gf.Vec3d(30, 20, 10)
                omni.kit.commands.execute(
                    "TransformPrimSRT",
                    path=xform.GetPrim().GetPrimPath().pathString,
                    new_translation=translation,
                    new_rotation_euler=rotation_euler,
                    new_scale=scale,
                )

            if pivot:
                if rotate_op <= UsdGeom.XformOp.TypeRotateZ:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 9)
                else:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 7)

                # Last op should be invertOp
                last_op = xform.GetOrderedXformOps()[-1]
                self.assertTrue(last_op.IsInverseOp())
            else:
                if rotate_op <= UsdGeom.XformOp.TypeRotateZ:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 7)
                else:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 5)
            mtx = xformamble.GetLocalTransformation()
            t = Gf.Transform(mtx)

            # ops = xform.GetOrderedXformOps()
            # for op in ops:
            #     print(op.GetOpName() + " value: " + str(op.Get()))
            # print("Full transform: " + str(t))

            self.assertTrue(Gf.IsClose(t.GetTranslation(), translation, tolerance_epsilon))
            self.assertTrue(Gf.IsClose(t.GetScale(), scale, tolerance_epsilon))
            eulers = t.GetRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
            self.assertTrue(Gf.IsClose(eulers, rotation_euler, tolerance_epsilon))

    async def test_local_transform_SRT_cpp_pre_suffix(self):
        await self._run_local_transform_SRT(True, True, False)

    async def test_local_transform_SRT_cpp_post_suffix(self):
        await self._run_local_transform_SRT(True, False, False)

    async def test_local_transform_SRT_python_pre_suffix(self):
        await self._run_local_transform_SRT(False, True, False)

    async def test_local_transform_SRT_python_post_suffix(self):
        await self._run_local_transform_SRT(False, False, False)

    async def test_local_transform_SRT_cpp_pre_suffix_pivot(self):
        await self._run_local_transform_SRT(True, True, True)

    async def test_local_transform_SRT_cpp_post_suffix_pivot(self):
        await self._run_local_transform_SRT(True, False, True)

    async def test_local_transform_SRT_python_pre_suffix_pivot(self):
        await self._run_local_transform_SRT(False, True, True)

    async def test_local_transform_SRT_python_post_suffix_pivot(self):
        await self._run_local_transform_SRT(False, False, True)

    async def _run_local_transform_SRT_full_matrix(self, cpp, pre):
        usd_context = omni.usd.get_context()

        stage = Usd.Stage.CreateInMemory()
        await usd_context.attach_stage_async(stage)

        xform = UsdGeom.Xform.Define(stage, "/xform")
        xformamble = UsdGeom.Xformable(xform.GetPrim())
        if pre:
            xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
            ur_scale = Gf.Vec3d(10, 10, 10)
            xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)
        xformamble.AddTransformOp()
        if not pre:
            xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
            ur_scale = Gf.Vec3d(10, 10, 10)
            xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)

        self.assertTrue(len(xform.GetOrderedXformOps()) == 3)

        tolerance_epsilon = 1e-4
        (s, r, ro, t) = omni.usd.get_local_transform_SRT(xform)
        self.assertTrue(Gf.IsClose(ur_scale, s, tolerance_epsilon))
        self.assertTrue(abs(r[0] + 90.0) < tolerance_epsilon)

        if cpp:
            translation = (1, 2, 3)
            rotation_euler = (0, 0, 0)
            scale = (30, 20, 10)
            omni.kit.commands.execute(
                "TransformPrimSRTCpp",
                path=xform.GetPrim().GetPrimPath().pathString,
                new_translation=translation,
                new_rotation_euler=rotation_euler,
                new_scale=scale,
            )
        else:
            translation = Gf.Vec3d(1, 2, 3)
            rotation_euler = Gf.Vec3d(0, 0, 0)
            scale = Gf.Vec3d(30, 20, 10)
            omni.kit.commands.execute(
                "TransformPrimSRT",
                path=xform.GetPrim().GetPrimPath().pathString,
                new_translation=translation,
                new_rotation_euler=rotation_euler,
                new_scale=scale,
            )

        self.assertTrue(len(xform.GetOrderedXformOps()) == 3)

        mtx = xformamble.GetLocalTransformation()
        t = Gf.Transform(mtx)

        # ops = xform.GetOrderedXformOps()
        # for op in ops:
        #     print(op.GetOpName() + " value: " + str(op.Get()))
        # print("Full transform: " + str(t))

        self.assertTrue(Gf.IsClose(t.GetTranslation(), translation, tolerance_epsilon))
        self.assertTrue(Gf.IsClose(t.GetScale(), scale, tolerance_epsilon))
        eulers = t.GetRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
        self.assertTrue(Gf.IsClose(eulers, rotation_euler, tolerance_epsilon))

    async def test_local_transform_SRT_cpp_post_suffix_full_matrix(self):
        await self._run_local_transform_SRT_full_matrix(True, False)

    async def test_local_transform_SRT_python_post_suffix_full_matrix(self):
        await self._run_local_transform_SRT_full_matrix(False, False)

    async def _run_local_transform_matrix(self, pre, pivot):
        usd_context = omni.usd.get_context()

        stage = Usd.Stage.CreateInMemory()
        await usd_context.attach_stage_async(stage)

        rotate_ops = [
                UsdGeom.XformOp.TypeRotateZ,
                UsdGeom.XformOp.TypeRotateX,
                UsdGeom.XformOp.TypeRotateY,
                UsdGeom.XformOp.TypeRotateZYX,
                UsdGeom.XformOp.TypeRotateXYZ,
                UsdGeom.XformOp.TypeRotateXZY,
                UsdGeom.XformOp.TypeRotateYXZ,
                UsdGeom.XformOp.TypeRotateYZX,
                UsdGeom.XformOp.TypeRotateZXY,
                UsdGeom.XformOp.TypeOrient
                ]

        index = 0
        for rotate_op in rotate_ops:
            xform = UsdGeom.Xform.Define(stage, "/xform" + str(index))
            index = index + 1
            xformamble = UsdGeom.Xformable(xform.GetPrim())
            if pre:
                xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
                ur_scale = Gf.Vec3d(10, 10, 10)
                xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)
            xformamble.AddTranslateOp().Set((0, 0, 0))
            if pivot:
                xformamble.AddTranslateOp(opSuffix='pivot', isInverseOp=False).Set(Gf.Vec3d(0, 0, 0))
            ro = xformamble.AddXformOp(rotate_op)
            if rotate_op == UsdGeom.XformOp.TypeOrient:
                ro.Set(Gf.Quatd(1.0))
            elif rotate_op <= UsdGeom.XformOp.TypeRotateZ:
                ro.Set(0.0)
            else:
                ro.Set(Gf.Vec3d(0.0))
            xformamble.AddScaleOp().Set((1, 1, 1))
            if not pre:
                xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
                ur_scale = Gf.Vec3d(10, 10, 10)
                xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)
            if pivot:
                xformamble.AddTranslateOp(opSuffix='pivot', isInverseOp=True)

            if pivot:
                self.assertTrue(len(xform.GetOrderedXformOps()) == 7)
            else:
                self.assertTrue(len(xform.GetOrderedXformOps()) == 5)

            tolerance_epsilon = 1e-4
            (s, r, ro, t) = omni.usd.get_local_transform_SRT(xform)
            self.assertTrue(Gf.IsClose(ur_scale, s, tolerance_epsilon))
            self.assertTrue(abs(r[0] + 90.0) < tolerance_epsilon)

            translation = (1, 2, 3)
            rotation_euler = (10, 20, 30)
            matrix = Gf.Matrix4d(1.0)
            matrix.SetTranslateOnly(translation)
            matrix.SetRotateOnly(Gf.Rotation(Gf.Vec3d.XAxis(), rotation_euler[0]) * Gf.Rotation(Gf.Vec3d.YAxis(), rotation_euler[1]) * Gf.Rotation(Gf.Vec3d.ZAxis(), rotation_euler[2]))
            t0 = Gf.Transform(matrix)
            omni.kit.commands.execute(
                "TransformPrim",
                path=xform.GetPrim().GetPrimPath().pathString,
                new_transform_matrix=matrix
            )

            if pivot:
                if rotate_op <= UsdGeom.XformOp.TypeRotateZ:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 9)
                else:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 7)

                # Last op should be invertOp
                last_op = xform.GetOrderedXformOps()[-1]
                self.assertTrue(last_op.IsInverseOp())
            else:
                if rotate_op <= UsdGeom.XformOp.TypeRotateZ:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 7)
                else:
                    self.assertTrue(len(xform.GetOrderedXformOps()) == 5)

            mtx = xformamble.GetLocalTransformation()
            t = Gf.Transform(mtx)

            # ops = xform.GetOrderedXformOps()
            # for op in ops:
            #     print(op.GetOpName() + " value: " + str(op.Get()))

            self.assertTrue(Gf.IsClose(t.GetTranslation(), translation, tolerance_epsilon))
            self.assertTrue(Gf.IsClose(t.GetScale(), t0.GetScale(), tolerance_epsilon))
            self.assertTrue(Gf.IsClose(t.GetRotation().GetQuaternion().GetImaginary(), t0.GetRotation().GetQuaternion().GetImaginary(), tolerance_epsilon))
            self.assertTrue(Gf.IsClose(t.GetRotation().GetQuaternion().GetReal(), t0.GetRotation().GetQuaternion().GetReal(), tolerance_epsilon))

    async def test_local_transform_matrix_post_suffix(self):
        await self._run_local_transform_matrix(False, False)

    async def test_local_transform_matrix_pre_suffix(self):
        await self._run_local_transform_matrix(True, False)

    async def test_local_transform_matrix_post_suffix_pivot(self):
        await self._run_local_transform_matrix(False, True)

    async def test_local_transform_matrix_pre_suffix_pivot(self):
        await self._run_local_transform_matrix(True, True)

    async def _run_local_transform_full_matrix(self, pre):
        usd_context = omni.usd.get_context()

        stage = Usd.Stage.CreateInMemory()
        await usd_context.attach_stage_async(stage)

        xform = UsdGeom.Xform.Define(stage, "/xform")
        xformamble = UsdGeom.Xformable(xform.GetPrim())
        if pre:
            xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
            ur_scale = Gf.Vec3d(10, 10, 10)
            xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)
        xformamble.AddTransformOp()
        if not pre:
            xformamble.AddRotateXOp(opSuffix='unitsResolve').Set((-90))
            ur_scale = Gf.Vec3d(10, 10, 10)
            xformamble.AddScaleOp(opSuffix='unitsResolve').Set(ur_scale)

        self.assertTrue(len(xform.GetOrderedXformOps()) == 3)

        tolerance_epsilon = 1e-4
        (s, r, ro, t) = omni.usd.get_local_transform_SRT(xform)
        self.assertTrue(Gf.IsClose(ur_scale, s, tolerance_epsilon))
        self.assertTrue(abs(r[0] + 90.0) < tolerance_epsilon)

        translation = (1, 2, 3)
        rotation_euler = (10, 20, 30)
        matrix = Gf.Matrix4d(1.0)
        matrix.SetTranslateOnly(translation)
        matrix.SetRotateOnly(Gf.Rotation(Gf.Vec3d.XAxis(), rotation_euler[0]) * Gf.Rotation(Gf.Vec3d.YAxis(), rotation_euler[1]) * Gf.Rotation(Gf.Vec3d.ZAxis(), rotation_euler[2]))
        t0 = Gf.Transform(matrix)
        omni.kit.commands.execute(
            "TransformPrim",
            path=xform.GetPrim().GetPrimPath().pathString,
            new_transform_matrix=matrix
        )

        self.assertTrue(len(xform.GetOrderedXformOps()) == 3)

        mtx = xformamble.GetLocalTransformation()
        t = Gf.Transform(mtx)

        # ops = xform.GetOrderedXformOps()
        # for op in ops:
        #     print(op.GetOpName() + " value: " + str(op.Get()))

        self.assertTrue(Gf.IsClose(t.GetTranslation(), translation, tolerance_epsilon))
        self.assertTrue(Gf.IsClose(t.GetScale(), t0.GetScale(), tolerance_epsilon))
        self.assertTrue(Gf.IsClose(t.GetRotation().GetQuaternion().GetImaginary(), t0.GetRotation().GetQuaternion().GetImaginary(), tolerance_epsilon))
        self.assertTrue(Gf.IsClose(t.GetRotation().GetQuaternion().GetReal(), t0.GetRotation().GetQuaternion().GetReal(), tolerance_epsilon))

    async def test_local_transform_matrix_post_suffix_full_matrix(self):
        await self._run_local_transform_full_matrix(False)

    async def test_usd_file_ext_utils(self):
        self.assertTrue(omni.usd.writable_usd_file_exts_str())
        self.assertTrue(omni.usd.writable_usd_file_exts())
        self.assertTrue(omni.usd.writable_usd_dotted_file_exts())
        self.assertTrue(omni.usd.writable_usd_files_desc())
        self.assertTrue(omni.usd.writable_usd_re())
        self.assertTrue(omni.usd.readable_usd_file_exts_str())
        self.assertTrue(omni.usd.readable_usd_file_exts())
        self.assertTrue(omni.usd.readable_usd_dotted_file_exts())
        self.assertFalse(omni.usd.is_usd_writable_filetype("test.unknown"))
        self.assertFalse(omni.usd.is_usd_writable_filetype(""))
        self.assertFalse(omni.usd.is_usd_writable_filetype(None))
        self.assertFalse(omni.usd.is_usd_writable_filetype("test.unknown"))
        self.assertFalse(omni.usd.is_usd_writable_filetype(""))
        self.assertFalse(omni.usd.is_usd_writable_filetype(None))

        for ext in omni.usd.writable_usd_dotted_file_exts():
            self.assertTrue(omni.usd.is_usd_writable_filetype(f"test{ext}"))

        for ext in omni.usd.readable_usd_dotted_file_exts():
            self.assertTrue(omni.usd.is_usd_readable_filetype(f"test{ext}"))

    async def test_get_prim_or_prop_utils(self):
        stage = Usd.Stage.CreateInMemory()
        prim = stage.DefinePrim("/test", "Xform")
        prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
        self.assertTrue(omni.usd.get_prim_at_path("/test", stage))
        self.assertFalse(omni.usd.get_prim_at_path("/test0", stage))
        self.assertFalse(omni.usd.get_prim_at_path("/test0"))
        self.assertTrue(omni.usd.get_prim_at_path("/test.custom", stage))
        self.assertFalse(omni.usd.get_prim_at_path("/test0.custom", stage))
        self.assertFalse(omni.usd.get_prim_at_path("/test0.custom"))

        prim = omni.usd.get_context().get_stage().DefinePrim("/test", "Xform")
        prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
        self.assertTrue(omni.usd.get_prim_at_path("/test"))
        self.assertTrue(omni.usd.get_prop_at_path("/test.custom"))

    async def test_set_or_clear_prop_val(self):
        stage = omni.usd.get_context().get_stage()
        layer = Sdf.Layer.CreateAnonymous()
        stage.GetSessionLayer().subLayerPaths.append(layer.identifier)

        prim = stage.DefinePrim("/test", "Xform")
        attr = prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
        self.assertFalse(omni.usd.get_prop_auto_target_session_layer(stage, attr.GetPath()))
        omni.usd.set_prop_val(attr, 1.0, auto_target_layer=False)
        self.assertEqual(attr.Get(), 1.0)

        with Usd.EditContext(stage, layer):
            omni.usd.set_prop_val(attr, 2.0, auto_target_layer=False)
        attr = prim.GetAttribute("custom")
        self.assertEqual(attr.Get(), 2.0)
        self.assertTrue(omni.usd.get_prop_auto_target_session_layer(stage, attr.GetPath()))

        # Root layer's value is shadowed
        omni.usd.set_prop_val(attr, 1.0, auto_target_layer=False)
        self.assertEqual(attr.Get(), 2.0)

        # Auto target layer can find strongest opinion automatically
        omni.usd.set_prop_val(attr, 3.0, auto_target_layer=True)
        self.assertEqual(attr.Get(), 3.0)

        omni.usd.clear_attr_val_at_time(attr, auto_target_layer=False)
        self.assertEqual(attr.Get(), 3.0)

        omni.usd.clear_attr_val_at_time(attr, auto_target_layer=True)
        self.assertEqual(attr.Get(), None)

        with Usd.EditContext(stage, stage.GetSessionLayer()):
            prim = stage.DefinePrim("/test", "Xform")
        self.assertTrue(omni.usd.get_prop_auto_target_session_layer(stage, "/test.custom"))

        self.assertFalse(omni.usd.is_path_valid("/test0"))
        self.assertTrue(omni.usd.is_path_valid("/test"))
        self.assertTrue(omni.usd.is_path_valid("/test.custom"))

        attr = prim.CreateAttribute("matrix", Sdf.ValueTypeNames.Matrix4d)
        omni.usd.set_prop_val(attr, Gf.Matrix4d(1.0))
        self.assertEqual(attr.Get(), Gf.Matrix4d(1.0))

        attr = prim.CreateAttribute("quath", Sdf.ValueTypeNames.Quath)
        omni.usd.set_prop_val(attr, Gf.Quath(1.0))
        omni.usd.set_attr_val(attr, Gf.Quath(1.0))
        self.assertEqual(attr.Get(), Gf.Quath(1.0))

        attr = prim.CreateAttribute("quatf", Sdf.ValueTypeNames.Quatf)
        omni.usd.set_prop_val(attr, Gf.Quatf(1.0))
        self.assertEqual(attr.Get(), Gf.Quatf(1.0))

        attr = prim.CreateAttribute("quatd", Sdf.ValueTypeNames.Quatd)
        omni.usd.set_prop_val(attr, Gf.Quatd(1.0))
        self.assertEqual(attr.Get(), Gf.Quatd(1.0))

        attr = prim.CreateAttribute("int2", Sdf.ValueTypeNames.Int2)
        omni.usd.set_prop_val(attr, (1, 1))
        self.assertEqual(attr.Get(), Gf.Vec2i(1))

    async def test_remove_property(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/test")
        for context in ["", stage]:
            for layer in stage.GetLayerStack():
                with Usd.EditContext(stage, layer):
                    prim.CreateAttribute("matrix", Sdf.ValueTypeNames.Matrix4d)

            omni.usd.remove_property("/test", "custom", context)
            self.assertFalse(prim.GetAttribute("custom"))

    async def test_material_input_creation(self):
        omni.kit.commands.execute(
            "CreateMdlMaterialPrim",
            mtl_url="OmniPBR.mdl",
            mtl_name="OmniPBR",
            mtl_path="/World/Looks/material"
        )
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/World/Looks/material")
        self.assertTrue(prim)

        attr = omni.usd.create_material_input(
            prim, "test", 1.0, Sdf.ValueTypeNames.Double,
            def_value="default", min_value=0.0, max_value=1.0, display_name="test",
            display_group="params", color_space="raw"
        )
        self.assertTrue(attr)

    async def test_layer_utils(self):
        usd_context = omni.usd.get_context()
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        custom_layer_data = root_layer.customLayerData

        self.assertFalse(omni.usd.is_layer_locked(usd_context, root_layer.identifier))
        locked_data = {
            "locked": {
                f"{root_layer.identifier}" : True
            }
        }
        custom_layer_data["omni_layer"] = locked_data

        root_layer.customLayerData = custom_layer_data
        self.assertTrue(omni.usd.is_layer_locked(usd_context, root_layer.identifier))

        with tempfile.TemporaryDirectory() as tmpdirname:
            layer_identifier0 = os.path.join(tmpdirname, "test0.usd")
            layer_identifier1 = os.path.join(tmpdirname, "test1.usd")
            layer0 = Sdf.Layer.CreateNew(layer_identifier0)
            layer1 = Sdf.Layer.CreateNew(layer_identifier1)
            layer0.Save()
            layer1.Save()

            stage.GetSessionLayer().subLayerPaths.append(layer0.identifier)
            stage.GetRootLayer().subLayerPaths.append(layer1.identifier)
            with Usd.EditContext(stage, layer0):
                stage.DefinePrim("/test")

            with Usd.EditContext(stage, layer1):
                stage.DefinePrim("/test0")

            layer0 = None
            layer1 = None
            dirty_layers = omni.usd.get_dirty_layers(stage)

            stage.GetSessionLayer().subLayerPaths.clear()
            stage.GetRootLayer().subLayerPaths.clear()

        # Layers under session layer should not be included.
        self.assertEqual(len(dirty_layers), 1)
        self.assertTrue(clientutils.equal_urls(dirty_layers[0], layer_identifier1))

    async def test_merge_layers(self):
        stage = omni.usd.get_context().get_stage()

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdirname:
            strong_layer_identifier = os.path.join(tmpdirname, "subdir/strong.usd")
            weak_layer_identifier = os.path.join(tmpdirname, "weak.usd")
            reference_identifier = os.path.join(tmpdirname, "reference.usd")
            strong_layer = Sdf.Layer.CreateNew(strong_layer_identifier)
            weak_layer = Sdf.Layer.CreateNew(weak_layer_identifier)
            reference_layer = Sdf.Layer.CreateNew(reference_identifier)
            strong_layer.Save()
            weak_layer.Save()
            reference_layer.Save()

            root_layer = stage.GetRootLayer()
            root_layer.subLayerPaths.append(strong_layer.identifier)
            root_layer.subLayerPaths.append(weak_layer.identifier)
            self.assertEqual(len(stage.GetRootLayer().subLayerPaths), 2)

            with Usd.EditContext(stage, strong_layer):
                prim = stage.DefinePrim("/reference", "Xform")
                prim.CreateAttribute("value", Sdf.ValueTypeNames.Int).Set(1)

            with Usd.EditContext(stage, weak_layer):
                prim = stage.DefinePrim("/reference", "Xform")
                prim.GetAttribute("value").Set(2)
                prim.GetReferences().AddReference("./reference.usd")

            # Merge from strong to weak
            omni.usd.merge_layers(weak_layer_identifier, strong_layer_identifier, False)
            prim = stage.GetPrimAtPath("/reference")
            refs_and_layers = omni.usd.get_composed_references_from_prim(prim)

            self.assertEqual(len(refs_and_layers), 1)
            ref_and_layer = refs_and_layers[0]

            # OMPE-11530: ensure path is resolved correctly after merge.
            self.assertEqual(ref_and_layer[0].assetPath, "./reference.usd")
            self.assertEqual(prim.GetAttribute("value").Get(), 1)

            # Releases resources to remove temp folder
            root_layer.subLayerPaths.clear()
            prim = None
            refs_and_layers = None
            root_layer = None
            strong_layer = None
            weak_layer = None
            reference_layer = None
            stage = None

            await omni.usd.get_context().close_stage_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

    async def create_and_destroy_engines(self, usd_context):
        carb.log_info("create_and_destroy_engines function started")

        config1 = omni.usd.HydraEngineCreationConfig()
        config1.flags = omni.usd.EngineCreationFlags.NONE
        config1.tickrate_in_hz = 60
        config1.device_mask = 1

        config2 = omni.usd.HydraEngineCreationConfig()
        config2.flags = omni.usd.EngineCreationFlags.NONE
        config2.tickrate_in_hz = 30
        config2.device_mask = 1

        config3 = omni.usd.HydraEngineCreationConfig()
        config3.flags = omni.usd.EngineCreationFlags.NONE
        config3.tickrate_in_hz = 0
        config3.device_mask = 1

        carb.log_info("creating hydra engines")
        engine_uid_1 = omni.usd.create_hydra_engine_with_config("rtx", usd_context, config1)
        engine_uid_2 = omni.usd.create_hydra_engine_with_config("rtx", usd_context, config2)
        engine_uid_3 = omni.usd.create_hydra_engine_with_config("rtx", usd_context, config3)
        carb.log_info("engine 1: " + str(engine_uid_1))
        carb.log_info("engine 2: " + str(engine_uid_2))
        carb.log_info("engine 3: " + str(engine_uid_3))

        # NOTE: This test currently only calls APIs, nothing is really created or destroyed
        # self.assertNotEqual(engine_uid_1, engine_uid_2)
        # self.assertNotEqual(engine_uid_2, engine_uid_3)

        carb.log_info("async wait 1 started")
        await self.wait_n_updates(6)
        carb.log_info("async wait 1 completed")

        list_of_names = usd_context.get_attached_hydra_engine_names()
        carb.log_info('Available names:')
        for name in list_of_names:
            carb.log_info(name)

        list_of_uids = usd_context.get_attached_hydra_engine_uids()
        carb.log_info('Available uids:')
        for uid in list_of_uids:
            carb.log_info(str(uid))

        for uid in list_of_uids:
            desc: omni.usd.HydraEngineDesc = usd_context.get_attached_hydra_engine_description(uid)
            carb.log_info("   ")
            carb.log_info(" engine " + str(desc.uid))
            carb.log_info("         type: " + desc.engine_type_name)
            carb.log_info("       thread: " + desc.thread_name)
            carb.log_info("        flags: " + str(desc.config.flags))
            carb.log_info("      tick_hz: " + str(desc.config.tickrate_in_hz))
            carb.log_info("  device_mask: " + str(desc.config.device_mask))
            carb.log_info("        index: " + str(desc.config.creation_index))

        await self.wait_n_updates(6)

        carb.log_info("destroying hydra engines")
        omni.usd.destroy_hydra_engine(engine_uid_3)
        omni.usd.destroy_hydra_engine(engine_uid_2)
        omni.usd.destroy_hydra_engine(engine_uid_1)
        carb.log_info("destroying completed")

        list_of_uids = usd_context.get_attached_hydra_engine_uids()
        carb.log_info('Available uids:')
        for uid in list_of_uids:
            carb.log_info(str(uid))

        for uid in list_of_uids:
            desc: omni.usd.HydraEngineDesc = usd_context.get_attached_hydra_engine_description(uid)
            carb.log_info("  ")
            carb.log_info(" engine " + str(desc.uid))
            carb.log_info("         type: " + desc.engine_type_name)
            carb.log_info("       thread: " + desc.thread_name)
            carb.log_info("        flags: " + str(desc.config.flags))
            carb.log_info("      tick_hz: " + str(desc.config.tickrate_in_hz))
            carb.log_info("  device_mask: " + str(desc.config.device_mask))
            carb.log_info("        index: " + str(desc.config.creation_index))

        carb.log_info("create_and_destroy_engines function completed")

    async def test_hydra_engine_management_apis(self):
        usd_context = omni.usd.get_context()
        for _ in range(2):
            await self.create_and_destroy_engines(usd_context)
            await self.wait_n_updates(6)

    async def test_is_usd_crate_file_supported(self):
        """Test that crate file version mismatch is detected, and crate file version check happens after asset path resolution."""
        # TODO: OMPE-52452 Add a simple test for relative crate file
        # (This is currently handled in test_usd_commands test_simple_relative_reference)
        #
        crate_file_path = str(Path(__file__).parent.joinpath("data").joinpath("crate_test.usd"))
        self.assertFalse(omni.usd.is_usd_crate_file_version_supported(crate_file_path))

        unresolved_path = "dummy:/path/to/crate/file.usd"
        self.assertFalse(omni.usd.is_usd_crate_file_version_supported(unresolved_path))

        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                layer_identifier = os.path.join(tmpdirname, "test.usd")
                layer = Sdf.Layer.CreateNew(layer_identifier)
                layer.Save()
                with patch('pxr.Ar.Resolver.Resolve') as mock_resolve:
                    mock_resolve.return_value = layer_identifier
                    self.assertTrue(omni.usd.is_usd_crate_file_version_supported(unresolved_path))
        except PermissionError:
            # Having weird permission error only on Windows. Passing if it's having issue removing temp file.
            pass
