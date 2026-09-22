import sys
import omni.kit.test
import omni.usd
import omni.client
import omni.client.utils as clientutils

from omni.kit.usd.layers import LayerUtils
from pxr import Sdf, Usd, UsdGeom, UsdShade, Vt, Tf


class TestLayerUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.__previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.usd_context = omni.usd.get_context()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()
        omni.client.set_retries(*self.__previous_retry_values)

    def check_sublayers(self, layer, expected_layer_identifiers):
        sublayers = layer.subLayerPaths
        self.assertTrue(len(sublayers) == len(expected_layer_identifiers), "Sublayers count does not match")

        sublayer_paths = []
        for sublayer_path in sublayers:
            sublayer_paths.append(sublayer_path)

        self.assertTrue(
            sublayer_paths == expected_layer_identifiers,
            f"Sublayers array does not match, got: {sublayer_paths}, expected: {expected_layer_identifiers}",
        )

    async def test_save_restore_edit_target(self):
        stage = Usd.Stage.CreateInMemory()
        format = Sdf.FileFormat.FindByExtension(".usd")
        sublayer = Sdf.Layer.New(format, "omniverse://__fake_omniverse_server__/test/test.usd")
        stage.GetRootLayer().subLayerPaths.append(sublayer.identifier)
        stage.SetEditTarget(Usd.EditTarget(sublayer))
        self.assertEqual(LayerUtils.get_edit_target(stage), sublayer.identifier)
        LayerUtils.save_authoring_layer_to_custom_data(stage)
        stage.SetEditTarget(Usd.EditTarget(stage.GetRootLayer()))
        self.assertEqual(LayerUtils.get_edit_target(stage), stage.GetRootLayer().identifier)
        LayerUtils.restore_authoring_layer_from_custom_data(stage)
        self.assertEqual(LayerUtils.get_edit_target(stage), sublayer.identifier)

    async def test_create_sublayer(self):
        layer = Sdf.Layer.CreateAnonymous()
        layer0 = LayerUtils.create_sublayer(layer, 0, "")
        layer1 = LayerUtils.create_sublayer(layer, 1, "")
        layer2 = LayerUtils.create_sublayer(layer, 2, "")
        self.check_sublayers(layer, [layer0.identifier, layer1.identifier, layer2.identifier])
        layer3 = LayerUtils.create_sublayer(layer, 3, "")
        self.check_sublayers(layer, [layer0.identifier, layer1.identifier, layer2.identifier, layer3.identifier])
        layer4 = LayerUtils.create_sublayer(layer, 3, "")
        self.check_sublayers(
            layer, [layer0.identifier, layer1.identifier, layer2.identifier, layer4.identifier, layer3.identifier]
        )
        layer5 = LayerUtils.create_sublayer(layer, -1, "")
        self.check_sublayers(
            layer,
            [
                layer0.identifier,
                layer1.identifier,
                layer2.identifier,
                layer4.identifier,
                layer3.identifier,
                layer5.identifier,
            ],
        )
        layer6 = LayerUtils.create_sublayer(layer, 100, "")
        self.check_sublayers(
            layer,
            [
                layer0.identifier,
                layer1.identifier,
                layer2.identifier,
                layer4.identifier,
                layer3.identifier,
                layer5.identifier,
                layer6.identifier,
            ],
        )
        layer7 = LayerUtils.create_sublayer(layer, -2, "")
        self.check_sublayers(
            layer,
            [
                layer0.identifier,
                layer1.identifier,
                layer2.identifier,
                layer4.identifier,
                layer3.identifier,
                layer5.identifier,
                layer6.identifier,
            ],
        )
        layer8 = LayerUtils.create_sublayer(layer, 0, "")
        self.check_sublayers(
            layer,
            [
                layer8.identifier,
                layer0.identifier,
                layer1.identifier,
                layer2.identifier,
                layer4.identifier,
                layer3.identifier,
                layer5.identifier,
                layer6.identifier,
            ],
        )

    async def test_insert_sublayer(self):
        layer = Sdf.Layer.CreateAnonymous()

        all_layers = []
        for i in range(9):
            all_layers.append(Sdf.Layer.CreateAnonymous())

        layer0 = LayerUtils.insert_sublayer(layer, 0, all_layers[0].identifier)
        layer1 = LayerUtils.insert_sublayer(layer, 1, all_layers[1].identifier)
        layer2 = LayerUtils.insert_sublayer(layer, 2, all_layers[2].identifier)
        self.check_sublayers(layer, [all_layers[0].identifier, all_layers[1].identifier, all_layers[2].identifier])
        layer3 = LayerUtils.insert_sublayer(layer, 3, all_layers[3].identifier)
        self.check_sublayers(
            layer,
            [all_layers[0].identifier, all_layers[1].identifier, all_layers[2].identifier, all_layers[3].identifier],
        )
        layer4 = LayerUtils.insert_sublayer(layer, 3, all_layers[4].identifier)
        self.check_sublayers(
            layer,
            [
                all_layers[0].identifier,
                all_layers[1].identifier,
                all_layers[2].identifier,
                all_layers[4].identifier,
                all_layers[3].identifier,
            ],
        )
        layer5 = LayerUtils.insert_sublayer(layer, -1, all_layers[5].identifier)
        self.check_sublayers(
            layer,
            [
                all_layers[0].identifier,
                all_layers[1].identifier,
                all_layers[2].identifier,
                all_layers[4].identifier,
                all_layers[3].identifier,
                all_layers[5].identifier,
            ],
        )
        layer6 = LayerUtils.insert_sublayer(layer, 100, all_layers[6].identifier)
        self.check_sublayers(
            layer,
            [
                all_layers[0].identifier,
                all_layers[1].identifier,
                all_layers[2].identifier,
                all_layers[4].identifier,
                all_layers[3].identifier,
                all_layers[5].identifier,
                all_layers[6].identifier,
            ],
        )
        layer7 = LayerUtils.insert_sublayer(layer, -2, all_layers[7].identifier)
        self.check_sublayers(
            layer,
            [
                all_layers[0].identifier,
                all_layers[1].identifier,
                all_layers[2].identifier,
                all_layers[4].identifier,
                all_layers[3].identifier,
                all_layers[5].identifier,
                all_layers[6].identifier,
            ],
        )
        layer8 = LayerUtils.insert_sublayer(layer, 0, all_layers[8].identifier)
        self.check_sublayers(
            layer,
            [
                all_layers[8].identifier,
                all_layers[0].identifier,
                all_layers[1].identifier,
                all_layers[2].identifier,
                all_layers[4].identifier,
                all_layers[3].identifier,
                all_layers[5].identifier,
                all_layers[6].identifier,
            ],
        )

    async def test_replace_sublayer(self):
        layer = Sdf.Layer.CreateAnonymous()

        all_layers = []
        for i in range(7):
            all_layers.append(Sdf.Layer.CreateAnonymous())

        layer0 = LayerUtils.insert_sublayer(layer, 0, all_layers[0].identifier)
        layer1 = LayerUtils.insert_sublayer(layer, 1, all_layers[1].identifier)
        layer2 = LayerUtils.insert_sublayer(layer, 2, all_layers[2].identifier)
        self.check_sublayers(layer, [all_layers[0].identifier, all_layers[1].identifier, all_layers[2].identifier])
        layer3 = LayerUtils.replace_sublayer(layer, 2, all_layers[3].identifier)
        self.check_sublayers(layer, [all_layers[0].identifier, all_layers[1].identifier, all_layers[3].identifier])
        layer4 = LayerUtils.replace_sublayer(layer, -1, all_layers[4].identifier)
        self.check_sublayers(layer, [all_layers[0].identifier, all_layers[1].identifier, all_layers[3].identifier])
        layer5 = LayerUtils.replace_sublayer(layer, 0, all_layers[5].identifier)
        self.check_sublayers(layer, [all_layers[5].identifier, all_layers[1].identifier, all_layers[3].identifier])
        layer6 = LayerUtils.replace_sublayer(layer, 100, all_layers[6].identifier)
        self.check_sublayers(layer, [all_layers[5].identifier, all_layers[1].identifier, all_layers[3].identifier])

    async def test_get_set_custom_name(self):
        layer = Sdf.Layer.CreateAnonymous()
        LayerUtils.set_custom_layer_name(layer, "name1")
        self.assertTrue(LayerUtils.get_custom_layer_name(layer) == "name1")
        LayerUtils.set_custom_layer_name(layer, "")
        self.assertEqual(LayerUtils.get_custom_layer_name(layer), layer.identifier)
        LayerUtils.set_custom_layer_name(layer, "name test with space")
        self.assertTrue(LayerUtils.get_custom_layer_name(layer) == "name test with space")

    def _create_material(self, stage, material_name, material_file_path):
        materials_group = UsdGeom.Scope.Define(stage, "/root/materials")
        material_path = materials_group.GetPath().AppendElementString(material_name)
        shader_path = material_path.AppendElementString(material_name)
        material = UsdShade.Material.Define(stage, material_path)
        shader = UsdShade.Shader.Define(stage, shader_path)

        shader.CreateOutput("out", Sdf.ValueTypeNames.Token)
        # https://github.com/PixarAnimationStudios/USD/commit/7944738df7891a6a1a00005b8f1d51c1805d1b61
        # https://groups.google.com/g/usd-interest/c/I7gY7LpNkjw/m/Zjm7gFVUBgAJ
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "out")
        shader.SetSourceAsset(material_file_path, "mdl")
        shader.SetSourceAssetSubIdentifier(material_name)
        shader.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)

        return material, shader

    async def test_resolve_paths(self):
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/a.usd")
        sublayer0 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd")
        # OMPE-44674: Add test case for asset path with different scheme.
        sublayer1 = Sdf.Layer.New(format, "dasset://test-ov-fake-server/fake/path/sublayers/sublayer1.usd")
        # OMPE-44674: Add test case for asset path with same scheme and different path.
        sublayer2 = Sdf.Layer.New(format, "omniverse://another-fake-server/sublayer2.usd")
        layer.subLayerPaths.insert(0, "./sublayers/sublayer0.usd")
        layer.subLayerPaths.insert(0, sublayer1.identifier)
        layer.subLayerPaths.insert(0, sublayer2.identifier)
        layer.subLayerOffsets[0] = Sdf.LayerOffset(2.0, 3.0)
        custom_data = layer.customLayerData
        custom_data["path"] = Sdf.AssetPath("../test_path.usd")
        layer.customLayerData = custom_data

        stage = Usd.Stage.Open(layer)
        mesh = UsdGeom.Mesh.Define(stage, "/root/test")
        test_prim = mesh.GetPrim()
        test_prim.GetReferences().AddReference("../b.usd")
        test_prim.GetPayloads().AddPayload("../c.usd")
        test_prim.CreateAttribute("Asset", Sdf.ValueTypeNames.Asset, False).Set("../d.usd")
        test_prim.CreateAttribute("AssetArray", Sdf.ValueTypeNames.AssetArray, False).Set(
            ["../e.usd", "../f.usd", "OmniPBR.mdl"]
        )
        # OMPE-43063: Add test case for asset path with %xx escape characters.
        test_prim.GetReferences().AddReference("../fake.usdz[scene.usd]</some/prim>")
        # OMPE-45438: Add test case for asset path with UTF-8 characters.
        test_prim.GetReferences().AddReference("../S%üßig%GBkeiten.usd")
        test_prim_spec = layer.GetPrimAtPath(test_prim.GetPath())
        test_prim_spec.customData["path"] = Sdf.AssetPath("../test.usd")

        omnipbr_mat, omnipbr_shader = self._create_material(stage, "omnipbr", "OmniPBR.mdl")
        external_mat, external_shader = self._create_material(stage, "external_mat", "../invalid_path/external_mat.mdl")

        # OM-42410: Paths without "./" are search paths
        searchpath_mat, searchpath_shader = self._create_material(stage, "searchpath_mat", "nvidia/searchpath_mat.mdl")

        material_binding = UsdShade.MaterialBindingAPI(test_prim)
        material_binding.Bind(omnipbr_mat)

        mesh = UsdGeom.Mesh.Define(stage, "/root/test2")
        test2_prim = mesh.GetPrim()
        material_binding = UsdShade.MaterialBindingAPI(test2_prim)
        material_binding.Bind(external_mat)

        mesh2 = UsdGeom.Mesh.Define(stage, "/root/test3")
        test3_prim = mesh2.GetPrim()
        material_binding = UsdShade.MaterialBindingAPI(test3_prim)
        material_binding.Bind(searchpath_mat)

        omni.usd.create_material_input(
            external_mat.GetPrim(),
            "diffuse_texture",
            Sdf.AssetPath("../invalid_path/invalid.png"),
            Sdf.ValueTypeNames.Asset,
        )

        if sys.platform.startswith('linux'):
            # OMPE-12316: Currently on linux there's issue with Sdf.Layer.computeAbsolutePath where linux local path
            # is not resolved as absolute path but relative. So here adding the file scheme prefix for now, until the
            # asset resolver issue is fixed.
            dummy_local_dir = "file:/dummy/local/"
        else:
            dummy_local_dir = "C:/dummy/local/"
        dummy_local_path = dummy_local_dir + "path.jpg"
        omni.usd.create_material_input(
            external_mat.GetPrim(),
            "normalmap_texture",
            Sdf.AssetPath(dummy_local_path),
            Sdf.ValueTypeNames.Asset,
        )

        # save to a target layer that is of common prefix as source layer
        target_layer = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/deep/level/a.usd")
        target_layer.TransferContent(layer)
        LayerUtils.resolve_paths(layer, target_layer, True, False, True)
        # Make sure that layer offset and scale are not changed.
        sublayer_offset = target_layer.subLayerOffsets[0]
        self.assertTrue(float(sublayer_offset.offset) == 2.0 and float(sublayer_offset.scale) == 3.0)
        string = target_layer.ExportToString()

        # FIXME: Search string directly instead of using USD API since it will cause unknown crashes.
        self.assertTrue(
            string.find("@../../sublayers/sublayer0.usd@") != -1,
            f"Sublayer repathing failed, expected: ../../sublayers/sublayer0.usd.",
        )

        self.assertTrue(string.find("@dasset://test-ov-fake-server/fake/path/sublayers/sublayer1.usd@") != -1, f"Sublayer repathing for paths with different scheme failed, expected: dasset://test-ov-fake-server/fake/path/sublayers/sublayer1.usd.")
        self.assertTrue(string.find("@omniverse://another-fake-server/sublayer2.usd@") != -1, f"Sublayer repathing for paths with same scheme but different path failed, expected: omniverse://another-fake-server/sublayer2.usd.")

        self.assertTrue(string.find("@../../../b.usd@") != -1, f"Reference is not resolved, expected: ../../../b.usd.")
        self.assertTrue(string.find("@../../../c.usd@") != -1, f"Payload is not resolved, expected: ../../../c.usd.")
        self.assertTrue(string.find("@../../../fake.usdz[scene.usd]</some/prim>@") != -1,
            f"Reference with %xx escape characters is not resolved, expected: ../../../fake.usdz[scene.usd]</some/prim>.")
        self.assertTrue(string.find("@../../../S%üßig%GBkeiten.usd@") != -1,
            f"Reference with UTF-8 characters is not resolved, expected: ../../../S%üßig%GBkeiten.usd.")

        self.assertTrue(
            string.find("@OmniPBR.mdl@") != -1,
            f"MDL from Core MDL Library should not be repathing, expected: OmniPBR.mdl.",
        )

        self.assertTrue(
            string.find("@../../../invalid_path/external_mat.mdl@") != -1,
            f"MDL repathing failed, expected: ../../../invalid_path/external_mat.mdl.",
        )

        self.assertTrue(
            string.find("@../../../invalid_path/invalid.png@") != -1,
            f"Material input repathing failed, expected: ../../../invalid_path/invalid.png.",
        )

        self.assertTrue(
            string.find(f"@{clientutils.make_file_url_if_possible(dummy_local_path)}@") != -1,
            f"Material input for local file path repathing failed, expected: {clientutils.make_file_url_if_possible(dummy_local_path)}.",
        )

        # Checks if all paths in target_path is re-pathing correctly.
        custom_data = target_layer.customLayerData
        self.assertTrue("path" in custom_data)
        self.assertEqual(custom_data["path"], "../../../test_path.usd")

        test_prim_spec = target_layer.GetPrimAtPath(test_prim.GetPath())
        self.assertTrue("path" in test_prim_spec.customData)
        self.assertEqual(test_prim_spec.customData["path"], "../../../test.usd")
        references = test_prim_spec.referenceList.prependedItems
        reference = references[0]
        self.assertEqual(reference.assetPath, "../../../b.usd")

        payloads = test_prim_spec.payloadList.prependedItems
        payload = payloads[0]
        self.assertEqual(payload.assetPath, "../../../c.usd")

        new_stage = Usd.Stage.Open(target_layer)
        test_prim = new_stage.GetPrimAtPath(test_prim.GetPath())

        attribute = test_prim.GetAttribute("Asset")
        self.assertEqual(attribute.GetTypeName(), Sdf.ValueTypeNames.Asset)
        path = attribute.Get().path
        self.assertEqual(path, "../../../d.usd")

        attribute = test_prim.GetAttribute("AssetArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.AssetArray)
        asset_array = attribute.Get()
        self.assertEqual
        (asset_array, Vt.StringArray(3, ("../../../e.usd", "../../../f.usd", "OmniPBR.mdl")))

        # MDL from core mdl library should stay untouched
        target_stage = Usd.Stage.Open(target_layer)
        target_omnipbr_shader = UsdShade.Shader.Get(target_stage, omnipbr_shader.GetPrim().GetPath())
        mdl = target_omnipbr_shader.GetSourceAsset("mdl")
        self.assertEqual(mdl.path, "OmniPBR.mdl")

        # MDL from external should be repathing to be relative to target layer.
        target_external_shader = UsdShade.Shader.Get(target_stage, external_shader.GetPrim().GetPath())
        mdl = target_external_shader.GetSourceAsset("mdl")
        self.assertEqual(mdl.path, "../../../invalid_path/external_mat.mdl")

        # MDL from search path should stay untouched.
        target_searchpath_shader = UsdShade.Shader.Get(target_stage, searchpath_shader.GetPrim().GetPath())
        mdl = target_searchpath_shader.GetSourceAsset("mdl")
        self.assertEqual(mdl.path, "nvidia/searchpath_mat.mdl")

        texture_input = target_external_shader.GetInput("diffuse_texture")
        path = texture_input.Get().path
        self.assertEqual(path, "../../../invalid_path/invalid.png")

        # OMPE-12316: test repath saving to a local target layer
        target_layer = Sdf.Layer.New(format, dummy_local_dir + "a.usd")
        target_layer.TransferContent(layer)
        LayerUtils.resolve_paths(layer, target_layer, True, False, True)
        # Make sure that layer offset and scale are not changed.
        sublayer_offset = target_layer.subLayerOffsets[0]
        self.assertTrue(float(sublayer_offset.offset) == 2.0 and float(sublayer_offset.scale) == 3.0)
        string = target_layer.ExportToString()

        # FIXME: Search string directly instead of using USD API since it will cause unknown crashes.
        self.assertTrue(
            string.find("@omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd@") != -1,
            f"Sublayer repathing failed, expected: omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd.",
        )

        self.assertTrue(string.find("@omniverse://test-ov-fake-server/fake/b.usd@") != -1, f"Reference is not resolved, expected: omniverse://test-ov-fake-server/fake/b.usd.")
        self.assertTrue(string.find("@omniverse://test-ov-fake-server/fake/c.usd@") != -1, f"Payload is not resolved, expected: omniverse://test-ov-fake-server/fake/c.usd.")

        self.assertTrue(
            string.find("@OmniPBR.mdl@") != -1,
            f"MDL from Core MDL Library should not be repathing, expected: OmniPBR.mdl.",
        )

        self.assertTrue(
            string.find("@omniverse://test-ov-fake-server/fake/invalid_path/external_mat.mdl@") != -1,
            f"MDL repathing failed, expected: omniverse://test-ov-fake-server/fake/invalid_path/external_mat.mdl.",
        )

        self.assertTrue(
            string.find("@omniverse://test-ov-fake-server/fake/invalid_path/invalid.png@") != -1,
            f"Material input repathing failed, expected: omniverse://test-ov-fake-server/fake/invalid_path/invalid.png.",
        )

        self.assertTrue(
            string.find(f"@./path.jpg@") != -1,
            f"Material input for local file path repathing failed, expected: ./path.jpg.",
        )

    async def test_resolve_local_paths(self):
        format = Sdf.FileFormat.FindByExtension(".usd")

        def test_local_path(layer_path, sublayer_path, target_layer_path, expected_sublayer_path):
            layer = Sdf.Layer.New(format, layer_path)
            Sdf.Layer.New(format, sublayer_path)
            layer.subLayerPaths.insert(0, sublayer_path)

            target_layer = Sdf.Layer.New(format, target_layer_path)
            target_layer.TransferContent(layer)
            LayerUtils.resolve_paths(layer, target_layer, True, False, True)
            string = target_layer.ExportToString()

            self.assertTrue(string.find(f"@{expected_sublayer_path}@") != -1, f"Sublayer repathing failed, expected: {expected_sublayer_path}.")

        
        if sys.platform.startswith('linux'):
            # Test case where two local urls, both without file scheme on different drives (Can't remove the file scheme prefix for linux yet,
            # because SdfLayer::ComputeAbsolutePath is still treating linux local path as relative path).
            layer_path = "file:/local/path/a.usd"
            sublayer_path = "file:/fake/path/sublayers/sublayer0.usd"
            target_layer_path = "file:/local/path/b.usd"

            test_local_path(layer_path, sublayer_path, target_layer_path, "../../fake/path/sublayers/sublayer0.usd")

            # Test case where two local urls are on the same drive
            layer_path = "file:/local/path/a.usd"
            sublayer_path = "file:/local/path/sublayers/sublayer0.usd"
            target_layer_path = "file:/local/path/b.usd"

            test_local_path(layer_path, sublayer_path, target_layer_path, "./sublayers/sublayer0.usd")

            return

        # Test case where two local urls, both without file scheme, on different drives.
        layer_path = "C:/fake/path/a.usd"
        sublayer_path = "D:/fake/path/sublayers/sublayer0.usd"
        target_layer_path = "C:/fake/path/b.usd"

        test_local_path(layer_path, sublayer_path, target_layer_path, sublayer_path)

        # Test case where two local urls, both without file scheme, on the same drive.
        layer_path = "C:/fake/path/a.usd"
        sublayer_path = "C:/fake/path/sublayers/sublayer0.usd"
        target_layer_path = "C:/fake/path/b.usd"

        test_local_path(layer_path, sublayer_path, target_layer_path, "./sublayers/sublayer0.usd")

        # Test case where two local urls, one with file scheme and the other without.
        layer_path = "C:/fake/path/a.usd"
        sublayer_path = "file:/D:/fake/path/sublayers/sublayer0.usd"
        target_layer_path = "C:/fake/path/b.usd"

        test_local_path(layer_path, sublayer_path, target_layer_path, "D:/fake/path/sublayers/sublayer0.usd")

        # Test case where two local urls, one with file scheme and the other without, on the same drive.
        layer_path = "C:/fake/path/a.usd"
        sublayer_path = "file:/C:/fake/path/sublayers/sublayer0.usd"
        target_layer_path = "C:/fake/path/b.usd"

        test_local_path(layer_path, sublayer_path, target_layer_path, "./sublayers/sublayer0.usd")

        # Test case where two local urls, both with file scheme, on different drives.
        layer_path = "file:/C:/fake/path/a.usd"
        sublayer_path = "file:/D:/fake/path/sublayers/sublayer0.usd"
        target_layer_path = "file:/C:/fake/path/b.usd"

        test_local_path(layer_path, sublayer_path, target_layer_path, "D:/fake/path/sublayers/sublayer0.usd")

        # Test case where two local urls, both with file scheme, on the same drive.
        layer_path = "file:/C:/fake/path/a.usd"
        sublayer_path = "file:/C:/fake/path/sublayers/sublayer0.usd"
        target_layer_path = "file:/C:/fake/path/b.usd"

        test_local_path(layer_path, sublayer_path, target_layer_path, "./sublayers/sublayer0.usd")


        

    def test_get_sublayer_position_in_parent(self):
        layer = Sdf.Layer.CreateAnonymous()
        layer0 = LayerUtils.create_sublayer(layer, 0, "")
        layer1 = LayerUtils.create_sublayer(layer, 1, "")
        layer2 = LayerUtils.create_sublayer(layer, 2, "")
        position = LayerUtils.get_sublayer_position_in_parent(layer.identifier, layer0.identifier)
        self.assertTrue(position == 0)

        position = LayerUtils.get_sublayer_position_in_parent(layer.identifier, layer1.identifier)
        self.assertTrue(position == 1)

        position = LayerUtils.get_sublayer_position_in_parent(layer.identifier, layer2.identifier)
        self.assertTrue(position == 2)

        position = LayerUtils.get_sublayer_position_in_parent(layer.identifier, "random")
        self.assertTrue(position == -1)

        position = LayerUtils.get_sublayer_position_in_parent(layer.identifier, "")
        self.assertTrue(position == -1)

    def test_get_set_layer_global_muteness(self):
        layer = Sdf.Layer.CreateAnonymous()
        LayerUtils.set_layer_global_muteness(layer, "c:/test/abcd/a.usd", True)
        self.assertTrue(LayerUtils.get_layer_global_muteness(layer, "c:/test/abcd/a.usd"))

        LayerUtils.set_layer_global_muteness(layer, "c:/random_string", True)
        self.assertTrue(LayerUtils.get_layer_global_muteness(layer, "c:/random_string"))

        LayerUtils.remove_layer_global_muteness(layer, "c:/random_string")
        self.assertFalse(LayerUtils.get_layer_global_muteness(layer, "c:/random_string"))

    def test_get_set_layer_lock_status(self):
        layer = Sdf.Layer.CreateAnonymous()
        LayerUtils.set_layer_lock_status(layer, "c:/test/abcd/a.usd", True)
        self.assertTrue(LayerUtils.get_layer_lock_status(layer, "c:/test/abcd/a.usd"))

        LayerUtils.set_layer_lock_status(layer, "c:/random_string", True)
        self.assertTrue(LayerUtils.get_layer_lock_status(layer, "c:/random_string"))

        LayerUtils.remove_layer_lock_status(layer, "c:/random_string")
        self.assertFalse(LayerUtils.get_layer_lock_status(layer, "c:/random_string"))

    def test_has_prim_spec(self):
        layer = Sdf.Layer.CreateAnonymous()
        stage = Usd.Stage.Open(layer)
        stage.DefinePrim("/Root/TestPrim")
        self.assertTrue(LayerUtils.has_prim_spec(layer.identifier, "/Root/TestPrim"))
        self.assertTrue(LayerUtils.has_prim_spec(layer.identifier, "/"))
        self.assertTrue(LayerUtils.has_prim_spec(layer.identifier, "/Root"))
        self.assertFalse(LayerUtils.has_prim_spec(layer.identifier, "/Root/TestPrim2"))
        self.assertFalse(LayerUtils.has_prim_spec(layer.identifier, ""))

    def test_get_sublayer_identifier(self):
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/a.usd")
        sublayer0 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd")
        layer.subLayerPaths.insert(0, "./sublayers/sublayer0.usd")
        identifier = LayerUtils.get_sublayer_identifier(layer.identifier, 0)
        self.assertTrue(sublayer0.identifier == identifier)

    def test_restore_muteness_from_custom_data(self):
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.CreateAnonymous()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        layer3 = Sdf.Layer.CreateAnonymous()
        layer4 = Sdf.Layer.CreateAnonymous()
        layer.subLayerPaths.append(layer0.identifier)
        layer.subLayerPaths.append(layer1.identifier)
        layer.subLayerPaths.append(layer2.identifier)
        layer.subLayerPaths.append(layer3.identifier)
        layer.subLayerPaths.append(layer4.identifier)
        LayerUtils.set_layer_global_muteness(layer, layer0.identifier, True)
        LayerUtils.set_layer_global_muteness(layer, layer1.identifier, False)
        LayerUtils.set_layer_global_muteness(layer, layer2.identifier, True)
        LayerUtils.set_layer_global_muteness(layer, layer3.identifier, False)
        LayerUtils.set_layer_global_muteness(layer, layer4.identifier, True)

        stage = Usd.Stage.Open(layer)
        LayerUtils.restore_muteness_from_custom_data(stage)
        self.assertTrue(stage.IsLayerMuted(layer0.identifier))
        self.assertFalse(stage.IsLayerMuted(layer1.identifier))
        self.assertTrue(stage.IsLayerMuted(layer2.identifier))
        self.assertFalse(stage.IsLayerMuted(layer3.identifier))
        self.assertTrue(stage.IsLayerMuted(layer4.identifier))

    def test_set_get_global_muteness(self):
        layer = Sdf.Layer.CreateAnonymous()
        LayerUtils.set_layer_global_muteness(layer, "test_identifier", True)
        LayerUtils.set_layer_global_muteness(layer, "", True)
        self.assertTrue(LayerUtils.get_layer_global_muteness(layer, "test_identifier"))
        self.assertFalse(LayerUtils.get_layer_global_muteness(layer, "test_identifier2"))
        self.assertFalse(LayerUtils.get_layer_global_muteness(layer, ""))

        LayerUtils.remove_layer_global_muteness(layer, "test_identifier")
        self.assertFalse(LayerUtils.get_layer_global_muteness(layer, "test_identifier"))

    def test_remove_sublayer(self):
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.CreateAnonymous()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        layer3 = Sdf.Layer.CreateAnonymous()
        layer4 = Sdf.Layer.CreateAnonymous()
        layer.subLayerPaths.append(layer0.identifier)
        layer.subLayerPaths.append(layer1.identifier)
        layer.subLayerPaths.append(layer2.identifier)
        layer.subLayerPaths.append(layer3.identifier)
        layer.subLayerPaths.append(layer4.identifier)

        LayerUtils.remove_sublayer(layer, 0)
        self.check_sublayers(layer, [layer1.identifier, layer2.identifier, layer3.identifier, layer4.identifier])

        # -1 means the last element.
        LayerUtils.remove_sublayer(layer, -1)
        self.check_sublayers(layer, [layer1.identifier, layer2.identifier, layer3.identifier])

        # Invalid index
        LayerUtils.remove_sublayer(layer, 100)
        self.check_sublayers(layer, [layer1.identifier, layer2.identifier, layer3.identifier])

        # Invalid index
        LayerUtils.remove_sublayer(layer, -2)
        self.check_sublayers(layer, [layer1.identifier, layer2.identifier, layer3.identifier])

        # clear it and try to remove an sublayer.
        layer.subLayerPaths = []
        LayerUtils.remove_sublayer(layer, 1)
        self.check_sublayers(layer, [])

    def test_remove_prim_spec(self):
        layer = Sdf.Layer.CreateAnonymous()
        stage = Usd.Stage.Open(layer)
        mesh = UsdGeom.Mesh.Define(stage, "/root/test")
        self.assertTrue(layer.GetPrimAtPath("/root/test"))

        LayerUtils.remove_prim_spec(layer, "/root/test")
        self.assertFalse(layer.GetPrimAtPath("/root/test"))

        self.assertTrue(layer.GetPrimAtPath("/root"))

        LayerUtils.remove_prim_spec(layer, "/root")
        self.assertFalse(layer.GetPrimAtPath("/root"))

    def test_get_all_sublayers(self):
        layer = Sdf.Layer.CreateAnonymous()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        layer3 = Sdf.Layer.CreateAnonymous()
        layer4 = Sdf.Layer.CreateAnonymous()
        layer5 = Sdf.Layer.CreateAnonymous()

        layer.subLayerPaths.append(layer0.identifier)
        layer.subLayerPaths.append(layer1.identifier)
        layer.subLayerPaths.append(layer2.identifier)
        layer.subLayerPaths.append(layer3.identifier)

        # Creates a circular reference: layer -> layer0 -> layer
        layer0.subLayerPaths.append(layer.identifier)

        layer3.subLayerPaths.append(layer4.identifier)
        layer4.subLayerPaths.append(layer5.identifier)

        stage = Usd.Stage.Open(layer)
        self.assertTrue(
            LayerUtils.get_all_sublayers(stage),
            [
                layer0.identifier,
                layer1.identifier,
                layer2.identifier,
                layer3.identifier,
                layer4.identifier,
                layer5.identifier,
            ],
        )

    def test_move_layer(self):
        layer = Sdf.Layer.CreateAnonymous()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        layer3 = Sdf.Layer.CreateAnonymous()
        layer4 = Sdf.Layer.CreateAnonymous()
        layer5 = Sdf.Layer.CreateAnonymous()

        layer.subLayerPaths.append(layer0.identifier)
        layer.subLayerPaths.append(layer1.identifier)
        layer.subLayerPaths.append(layer2.identifier)
        layer.subLayerPaths.append(layer3.identifier)

        # Creates a circular reference: layer -> layer0 -> layer
        layer0.subLayerPaths.append(layer.identifier)

        layer3.subLayerPaths.append(layer4.identifier)
        layer4.subLayerPaths.append(layer5.identifier)

        LayerUtils.move_layer(layer.identifier, 0, layer.identifier, 1, True)
        self.check_sublayers(layer, [layer1.identifier, layer0.identifier, layer2.identifier, layer3.identifier])

        # Move to the end
        LayerUtils.move_layer(layer.identifier, 0, layer.identifier, -1, True)
        self.check_sublayers(layer, [layer0.identifier, layer2.identifier, layer3.identifier, layer1.identifier])

        LayerUtils.move_layer(layer.identifier, 0, layer.identifier, 100, True)
        self.check_sublayers(layer, [layer2.identifier, layer3.identifier, layer1.identifier, layer0.identifier])

        # Invalid source
        LayerUtils.move_layer(layer.identifier, -1, layer.identifier, 0, True)
        self.check_sublayers(layer, [layer2.identifier, layer3.identifier, layer1.identifier, layer0.identifier])

        # Invalid target
        LayerUtils.move_layer(layer.identifier, 0, layer.identifier, -100, True)
        self.check_sublayers(layer, [layer2.identifier, layer3.identifier, layer1.identifier, layer0.identifier])

        # Move it to layer3 but not deletes it from source layer.
        LayerUtils.move_layer(layer.identifier, 0, layer3.identifier, 0, False)
        self.check_sublayers(layer, [layer2.identifier, layer3.identifier, layer1.identifier, layer0.identifier])
        self.check_sublayers(layer3, [layer2.identifier, layer4.identifier])

        LayerUtils.move_layer(layer.identifier, 0, layer1.identifier, 0, True)
        self.check_sublayers(layer, [layer3.identifier, layer1.identifier, layer0.identifier])
        self.check_sublayers(layer1, [layer2.identifier])

    def test_stitch_prim_specs(self):
        layer_content = """\
            #usda 1.0
            (
                subLayers = [
                    @omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd@,
                    @omniverse://test-ov-fake-server/fake/path/sublayers/sublayer1.usd@
                ]
            )

            def "root"
            {
                def "test_prim"
                {
                    int test = 1

                    def "test_prim2"
                    {
                        int test = 1
                    }
                }

                def "test_prim3"
                {
                    int test = 1
                }
            }
        """

        layer0_content = """\
            #usda 1.0

            over "root"
            {
                over "test_prim" (
                    prepend payload = @../invalid/payload1.usd@
                    prepend references = @../invalid/reference1.usd@
                )
                {
                    int test = 2

                    over "test_prim2" (
                        prepend payload = @../invalid/payload1.usd@
                        prepend references = @../invalid/reference1.usd@
                    )
                    {
                        int test = 2
                    }
                }

                over "test_prim3" (
                    prepend payload = @../invalid/payload1.usd@
                    prepend references = @../invalid/reference1.usd@
                )
                {
                    int test = 2
                }
            }
        """

        layer1_content = """\
            #usda 1.0
            (
                subLayers = [
                    @omniverse://test-ov-fake-server/fake/path/sublayers/level2/sublayer2.usd@
                ]
            )

            over "root"
            {
                over "test_prim" (
                    prepend payload = @../invalid/payload2.usd@
                    prepend references = @../invalid/reference2.usd@
                )
                {
                    asset[] AssetArray = [@1.usd@, @2.usd@, @OmniPBR.mdl@]
                    bool[] BoolArray = [0, 1]
                    float[] FloatArray = [1, 2, 3]
                    int[] IntArray = [1, 2, 3]
                    string[] StringArray = ["string1", "string2", "string3"]
                    int test = 3
                    asset test2 = @../../invalid/path.usd@
                    asset test3 = @OmniPBR.mdl@
                    token[] TokenArray = ["token1", "token2", "token3"]
                }
            }
        """

        layer2_content = """\
            #usda 1.0

            over "root"
            {
                over "test_prim" (
                    prepend payload = @../invalid/payload2.usd@
                    prepend references = @../invalid/reference2.usd@
                )
                {
                    asset[] AssetArray = [@3.usd@, @4.usd@, @OmniPBR.mdl@]
                    bool[] BoolArray = [1, 0]
                    float[] FloatArray = [3, 2, 1]
                    int[] IntArray = [3, 2, 1]
                    string[] StringArray = ["string3", "string2", "string1"]
                    int test = 3
                    asset test2 = @../../invalid/path.usd@
                    asset test3 = @OmniPBR.mdl@
                    asset test4 = @./invalid.mdl@
                    asset test5 = @nvidia/invalid.mdl@
                    token[] TokenArray = ["token3", "token2", "token1"]
                }
            }
        """

        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/a.usd")
        layer0 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer0.usd")
        layer1 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/sublayer1.usd")
        layer2 = Sdf.Layer.New(format, "omniverse://test-ov-fake-server/fake/path/sublayers/level2/sublayer2.usd")
        layer.ImportFromString(layer_content)
        layer0.ImportFromString(layer0_content)
        layer1.ImportFromString(layer1_content)
        layer2.ImportFromString(layer2_content)

        stage = Usd.Stage.Open(layer)
        result_layer = Sdf.Layer.CreateAnonymous()
        prim_paths = ["/root/test_prim", "/root/test_prim3"]
        with Sdf.ChangeBlock():
            for prim_path in prim_paths:
                omni.usd.stitch_prim_specs(stage, prim_path, result_layer)

        new_stage = Usd.Stage.Open(result_layer)
        prim = new_stage.GetPrimAtPath("/root/test_prim")
        prim_spec = result_layer.GetPrimAtPath("/root/test_prim")
        references = prim_spec.referenceList.prependedItems
        self.assertTrue(len(references), 3)
        self.assertEqual(references[0].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/reference1.usd")
        self.assertEqual(references[1].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/reference2.usd")
        self.assertEqual(
            references[2].assetPath, "omniverse://test-ov-fake-server/fake/path/sublayers/invalid/reference2.usd"
        )

        payloads = prim_spec.payloadList.prependedItems
        self.assertTrue(len(payloads), 3)
        self.assertEqual(payloads[0].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/payload1.usd")
        self.assertEqual(payloads[1].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/payload2.usd")
        self.assertEqual(
            payloads[2].assetPath, "omniverse://test-ov-fake-server/fake/path/sublayers/invalid/payload2.usd"
        )

        self.assertTrue(not not prim)
        attribute = prim.GetAttribute("test")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Int)
        self.assertTrue(attribute.Get() == 1)

        attribute = prim.GetAttribute("test2")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Asset)
        path = attribute.Get().path
        self.assertTrue(
            path == "omniverse://test-ov-fake-server/fake/invalid/path.usd", f"Path resolved is not correct: {path}."
        )

        attribute = prim.GetAttribute("test3")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Asset)
        path = attribute.Get().path
        # For path from core mdl library, it should not be re-mapping.
        self.assertTrue(path == "OmniPBR.mdl", f"Path resolved is not correct: {path}.")

        attribute = prim.GetAttribute("test4")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Asset)
        path = attribute.Get().path
        self.assertTrue(
            path == "omniverse://test-ov-fake-server/fake/path/sublayers/level2/invalid.mdl",
            f"Path resolved is not correct: {path}.",
        )

        # Search path should stay untouched.
        attribute = prim.GetAttribute("test5")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Asset)
        path = attribute.Get().path
        self.assertTrue(path == "nvidia/invalid.mdl", f"Path resolved is not correct: {path}.")

        attribute = prim.GetAttribute("BoolArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.BoolArray)
        bool_array = attribute.Get()
        self.assertTrue(len(bool_array) == 2)
        self.assertEqual(bool_array, Vt.BoolArray(2, (False, True)))

        attribute = prim.GetAttribute("IntArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.IntArray)
        int_array = attribute.Get()
        self.assertEqual(int_array, Vt.IntArray(3, (1, 2, 3)))

        attribute = prim.GetAttribute("FloatArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.FloatArray)
        float_array = attribute.Get()
        self.assertEqual(float_array, Vt.FloatArray(3, (1.0, 2.0, 3.0)))

        attribute = prim.GetAttribute("TokenArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.TokenArray)
        token_array = attribute.Get()
        self.assertEqual(token_array, Vt.TokenArray(3, ("token1", "token2", "token3")))

        attribute = prim.GetAttribute("StringArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.StringArray)
        string_array = attribute.Get()
        self.assertEqual(string_array, Vt.StringArray(3, ("string1", "string2", "string3")))

        attribute = prim.GetAttribute("AssetArray")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.AssetArray)
        asset_array = attribute.Get()
        self.assertEqual
        (
            asset_array,
            Vt.StringArray(
                3,
                (
                    "omniverse://test-ov-fake-server/fake/path/sublayers/1.usd",
                    "omniverse://test-ov-fake-server/fake/path/sublayers/2.usd",
                    "OmniPBR.mdl",
                ),
            ),
        )

        prim = new_stage.GetPrimAtPath("/root/test_prim/test_prim2")
        prim_spec = result_layer.GetPrimAtPath("/root/test_prim/test_prim2")
        references = prim_spec.referenceList.prependedItems
        self.assertTrue(len(references), 1)
        self.assertEqual(references[0].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/reference1.usd")

        payloads = prim_spec.payloadList.prependedItems
        self.assertTrue(len(payloads), 1)
        self.assertEqual(payloads[0].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/payload1.usd")

        self.assertTrue(not not prim)
        attribute = prim.GetAttribute("test")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Int)
        self.assertTrue(attribute.Get() == 1)

        prim = new_stage.GetPrimAtPath("/root/test_prim3")
        prim_spec = result_layer.GetPrimAtPath("/root/test_prim3")
        references = prim_spec.referenceList.prependedItems
        self.assertTrue(len(references), 1)
        self.assertEqual(references[0].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/reference1.usd")

        payloads = prim_spec.payloadList.prependedItems
        self.assertTrue(len(payloads), 1)
        self.assertEqual(payloads[0].assetPath, "omniverse://test-ov-fake-server/fake/path/invalid/payload1.usd")

        self.assertTrue(not not prim)
        attribute = prim.GetAttribute("test")
        self.assertTrue(attribute.GetTypeName() == Sdf.ValueTypeNames.Int)
        self.assertTrue(attribute.Get() == 1)
