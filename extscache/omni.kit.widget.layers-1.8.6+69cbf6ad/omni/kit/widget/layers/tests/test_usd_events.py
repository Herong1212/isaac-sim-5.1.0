import omni.kit.test
import os
import uuid
import omni.client
import omni.usd
import omni.kit.commands
import omni.kit.usd.layers as layers

from unittest.mock import patch
from stat import S_IREAD, S_IWRITE
from omni.kit.usd.layers import LayerUtils
from omni.kit.widget.layers.prim_spec_item import PrimSpecSpecifier
from .base import TestLayerUIBase
from pxr import Sdf, UsdGeom, Usd


class TestLayerUsdEvents(TestLayerUIBase):
    """Tests for layer model refresh reacted to usd stage changes."""

    async def setUp(self):
        await super().setUp()
        self.test_folder = omni.client.combine_urls(self.temp_dir, str(uuid.uuid1()))
        self.test_folder += "/"
        await omni.client.create_folder_async(self.test_folder)

        self.stage = await self.prepare_empty_stage()

    async def tearDown(self):
        await self.usd_context.close_stage_async()
        await omni.client.delete_async(self.test_folder)
        await super().tearDown()

    async def test_empty_stage(self):
        root_layer = self.stage.GetRootLayer()
        session_layer = self.stage.GetSessionLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        session_layer_item = layer_model.session_layer_item
        self.assertTrue(root_layer_item)
        self.assertTrue(session_layer_item)
        self.check_layer_regular_fields(
            root_layer_item, "Root Layer", root_layer.identifier,
            is_edit_target=True, reserved=True,
            from_session_layer=False, anonymous=True,
        )
        self.check_layer_regular_fields(
            session_layer_item, "Session Layer", session_layer.identifier,
            is_edit_target=False, reserved=True,
            from_session_layer=True, anonymous=True,
        )

    async def test_create_sublayers(self):
        root_layer = self.stage.GetRootLayer()
        session_layer = self.stage.GetSessionLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        session_layer_item = layer_model.session_layer_item

        _, identifiers_map = self.create_sublayers(root_layer, [2, 5, 4, 2])
        await self.app.next_update_async()
        await self.app.next_update_async()

        self.check_sublayer_tree(root_layer_item, identifiers_map)

        _, identifiers_map = self.create_sublayers(session_layer, [2, 5, 4, 2])
        await self.app.next_update_async()
        await self.app.next_update_async()

        self.check_sublayer_tree(session_layer_item, identifiers_map)

    async def test_edit_target_change(self):
        root_layer = self.stage.GetRootLayer()
        session_layer = self.stage.GetSessionLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        session_layer_item = layer_model.session_layer_item

        LayerUtils.set_edit_target(self.stage, session_layer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertTrue(session_layer_item.is_edit_target)
        self.assertFalse(root_layer_item.is_edit_target)

        LayerUtils.set_edit_target(self.stage, root_layer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertTrue(root_layer_item.is_edit_target)
        self.assertFalse(session_layer_item.is_edit_target)

    async def test_layer_misc_properties(self):
        root_layer = self.stage.GetRootLayer()
        root_layer.subLayerPaths.insert(0, "../invalid_path.usd")
        await self.app.next_update_async()
        await self.app.next_update_async()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        self.assertEqual(len(root_layer_item.sublayers), 1)

        missing_layer = root_layer_item.sublayers[0]
        self.check_layer_regular_fields(
            missing_layer, "invalid_path.usd", missing_layer.identifier,
            missing=True, anonymous=False, parent=root_layer_item
        )

        read_only_usd = omni.client.combine_urls(self.test_folder, "read_only.usd")
        read_only_layer = Sdf.Layer.CreateNew(read_only_usd)
        read_only_layer.Save()
        read_only_layer = None

        self.assertTrue(os.path.exists(read_only_usd))
        os.chmod(read_only_usd, S_IREAD)
        read_only_layer = Sdf.Layer.FindOrOpen(read_only_usd)
        root_layer.subLayerPaths.append(read_only_usd)
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        read_only_item = root_layer_item.sublayers[1]
        self.check_layer_regular_fields(
            read_only_item, "read_only.usd", read_only_layer.identifier,
            read_only=True, parent=root_layer_item, anonymous=False
        )
        # Change the write permission back so it could be removed.
        os.chmod(read_only_usd, S_IWRITE)
        dirty_layer_usd = omni.client.combine_urls(self.test_folder, "dirty_layer.usd")
        dirty_layer = Sdf.Layer.CreateNew(dirty_layer_usd)
        dirty_layer.Save()
        root_layer.subLayerPaths.append(dirty_layer_usd)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertTrue(len(root_layer_item.sublayers) == 3)

        dirty_layer_item = root_layer_item.sublayers[2]
        self.check_layer_regular_fields(
            dirty_layer_item, "dirty_layer.usd", dirty_layer.identifier,
            dirty=False, parent=root_layer_item, anonymous=False
        )

        # Change something
        customLayerData = dirty_layer.customLayerData
        customLayerData["test"] = 1
        dirty_layer.customLayerData = customLayerData
        await self.app.next_update_async()
        await self.app.next_update_async()

        self.check_layer_regular_fields(
            dirty_layer_item, "dirty_layer.usd", dirty_layer.identifier,
            dirty=True, parent=root_layer_item, anonymous=False
        )

    async def test_layer_local_mute_events(self):
        root_layer = self.stage.GetRootLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        sublayers_map, _ = self.create_sublayers(root_layer, [1, 1, 1])
        await self.app.next_update_async()
        await self.app.next_update_async()

        level_0_sublayer = sublayers_map[root_layer.identifier][0]
        level_1_sublayer = sublayers_map[level_0_sublayer.identifier][0]
        level_2_sublayer = sublayers_map[level_1_sublayer.identifier][0]
        level_0_item = root_layer_item.sublayers[0]
        level_1_item = level_0_item.sublayers[0]
        level_2_item = level_1_item.sublayers[0]

        self.stage.MuteLayer(level_2_sublayer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_2_item, level_2_sublayer.identifier, level_2_sublayer.identifier,
            parent=level_1_item, anonymous=True, muted=True, muted_or_parent_muted=True,
        )
        self.assertTrue(level_2_item.locally_muted)

        self.stage.UnmuteLayer(level_2_sublayer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_2_item, level_2_sublayer.identifier, level_2_sublayer.identifier,
            parent=level_1_item, anonymous=True, muted=False, muted_or_parent_muted=False
        )
        self.assertFalse(level_2_item.locally_muted)

        self.stage.MuteLayer(level_0_sublayer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_0_item, level_0_sublayer.identifier, level_0_sublayer.identifier,
            parent=root_layer_item, anonymous=True, muted=True, muted_or_parent_muted=True,
            sublayer_list=[level_1_sublayer.identifier]
        )
        self.check_layer_regular_fields(
            level_1_item, level_1_sublayer.identifier, level_1_sublayer.identifier,
            parent=level_0_item, anonymous=True, muted=False, muted_or_parent_muted=True,
            sublayer_list=[level_2_sublayer.identifier]
        )
        self.check_layer_regular_fields(
            level_2_item, level_2_sublayer.identifier, level_2_sublayer.identifier,
            parent=level_1_item, anonymous=True, muted=False, muted_or_parent_muted=True
        )

        self.stage.UnmuteLayer(level_0_sublayer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_1_item, level_1_sublayer.identifier, level_1_sublayer.identifier,
            parent=level_0_item, anonymous=True, muted=False, muted_or_parent_muted=False,
            sublayer_list=[level_2_sublayer.identifier]
        )
        self.check_layer_regular_fields(
            level_2_item, level_2_sublayer.identifier, level_2_sublayer.identifier,
            parent=level_1_item, anonymous=True, muted=False, muted_or_parent_muted=False
        )

    async def test_layer_global_mute_events(self):
        root_layer = self.stage.GetRootLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        layers_state = layers.get_layers().get_layers_state()
        layers_state.set_muteness_scope(True)

        sublayers_map, _ = self.create_sublayers(root_layer, [1])
        await self.app.next_update_async()
        await self.app.next_update_async()

        level_0_sublayer = sublayers_map[root_layer.identifier][0]
        level_0_item = root_layer_item.sublayers[0]

        self.stage.MuteLayer(level_0_sublayer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_0_item, level_0_sublayer.identifier, level_0_sublayer.identifier,
            parent=root_layer_item, anonymous=True, muted=True, muted_or_parent_muted=True,
        )
        self.assertTrue(level_0_item.globally_muted)

        self.stage.UnmuteLayer(level_0_sublayer.identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_0_item, level_0_sublayer.identifier, level_0_sublayer.identifier,
            parent=root_layer_item, anonymous=True, muted=False, muted_or_parent_muted=False,
        )
        self.assertFalse(level_0_item.globally_muted)

        LayerUtils.set_layer_global_muteness(root_layer, level_0_sublayer.identifier, True)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_0_item, level_0_sublayer.identifier, level_0_sublayer.identifier,
            parent=root_layer_item, anonymous=True, muted=True, muted_or_parent_muted=True,
        )
        self.assertTrue(level_0_item.globally_muted)

        LayerUtils.set_layer_global_muteness(root_layer, level_0_sublayer.identifier, False)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_layer_regular_fields(
            level_0_item, level_0_sublayer.identifier, level_0_sublayer.identifier,
            parent=root_layer_item, anonymous=True, muted=False, muted_or_parent_muted=False,
        )
        self.assertFalse(level_0_item.globally_muted)

    async def test_sublayer_edits(self):
        root_layer = self.stage.GetRootLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        _, identifiers_map = self.create_sublayers(root_layer, [3, 3, 3])
        await self.app.next_update_async()
        await self.app.next_update_async()

        level_0_sublayer0_identifier = identifiers_map[root_layer.identifier][0]
        level_0_sublayer1_identifier = identifiers_map[root_layer.identifier][1]
        level_0_sublayer2_identifier = identifiers_map[root_layer.identifier][2]

        # Layer refresh after remove.
        omni.kit.commands.execute("RemoveSublayer", layer_identifier=root_layer.identifier, sublayer_position=1)
        complete_sublayers = identifiers_map[root_layer.identifier][:]
        identifiers_map[root_layer.identifier] = [level_0_sublayer0_identifier, level_0_sublayer2_identifier]
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_sublayer_tree(root_layer_item, identifiers_map)
        omni.kit.undo.undo()
        await self.app.next_update_async()
        await self.app.next_update_async()
        identifiers_map[root_layer.identifier] = complete_sublayers
        self.check_sublayer_tree(root_layer_item, identifiers_map)

        # Layer refresh after create.
        # Create layer before second sublayer of root layer.
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=1,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
            layer_name="",
        )
        new_layer_identifier = self.stage.GetRootLayer().subLayerPaths[1]
        new_layer = Sdf.Layer.FindOrOpen(new_layer_identifier)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertTrue(root_layer_item.sublayers[1].identifier == new_layer_identifier)
        omni.kit.undo.undo()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_sublayer_tree(root_layer_item, identifiers_map)

        # Layer refresh after move.
        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=root_layer.identifier,
            from_sublayer_position=2,
            to_parent_layer_identifier=root_layer.identifier,
            to_sublayer_position=0,
            remove_source=True,
        )
        complete_sublayers = identifiers_map[root_layer.identifier][:]
        identifiers_map[root_layer.identifier] = [
            level_0_sublayer2_identifier,
            level_0_sublayer0_identifier,
            level_0_sublayer1_identifier
        ]
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_sublayer_tree(root_layer_item, identifiers_map)
        omni.kit.undo.undo()
        identifiers_map[root_layer.identifier] = complete_sublayers
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_sublayer_tree(root_layer_item, identifiers_map)

        # Layer refresh after replace.
        omni.kit.commands.execute(
            "ReplaceSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=1,
            new_layer_path=new_layer_identifier,
        )
        complete_sublayers = identifiers_map[root_layer.identifier][:]
        identifiers_map[root_layer.identifier] = [
            level_0_sublayer0_identifier,
            new_layer_identifier,
            level_0_sublayer2_identifier
        ]
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_sublayer_tree(root_layer_item, identifiers_map)
        omni.kit.undo.undo()
        identifiers_map[root_layer.identifier] = complete_sublayers
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_sublayer_tree(root_layer_item, identifiers_map)

    async def test_prim_specs_create(self):
        session_layer = self.stage.GetSessionLayer()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        session_layer_item = layer_model.session_layer_item

        prim_spec_paths = self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()

        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, prim_spec_paths)

        LayerUtils.set_edit_target(self.stage, session_layer.identifier)
        prim_spec_paths = self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()

        self.check_prim_spec_tree(session_layer_item.absolute_root_spec, prim_spec_paths)

    async def test_prim_specs_edits(self):
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        prim_spec_paths = self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()

        prim1_of_root = root_layer_item.prim_specs[1].path
        omni.kit.commands.execute(
            "RemovePrimSpec",
            layer_identifier=root_layer_item.identifier,
            prim_spec_path=prim1_of_root
        )
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()

        changed_prim_specs = prim_spec_paths.copy()
        for path in prim_spec_paths:
            if path.HasPrefix(prim1_of_root):
                changed_prim_specs.discard(path)

        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, changed_prim_specs)
        omni.kit.undo.undo()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, prim_spec_paths)

    async def test_layer_flush(self):
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        session_layer_item = layer_model.session_layer_item

        prim_spec_paths = self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, prim_spec_paths)

        session_layer_prim_spec_paths = self.get_all_prim_spec_paths(session_layer_item.absolute_root_spec)
        root_layer_item.layer.TransferContent(session_layer_item.layer)
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, session_layer_prim_spec_paths)

    async def test_prim_spec_type_name_change(self):
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        self.stage.DefinePrim("/test")
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertEqual(root_layer_item.prim_specs[0].path, Sdf.Path("/test"))
        self.assertEqual(root_layer_item.prim_specs[0].type_name, "")

        UsdGeom.Cube.Define(self.stage, root_layer_item.prim_specs[0].path)
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertEqual(root_layer_item.prim_specs[0].type_name, "Cube")

    async def test_parenting_prim_refresh(self):
        # Test for https://nvidia-omniverse.atlassian.net/browse/OM-34957

        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        # Creates 3 prims
        prim_spec_paths = list(self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [3]))
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, set(prim_spec_paths))

        # Moves first two prims as the children of the 3rd one.
        new_path0 = prim_spec_paths[2].AppendElementString(prim_spec_paths[0].name)
        new_path1 = prim_spec_paths[2].AppendElementString(prim_spec_paths[1].name)
        omni.kit.commands.execute("MovePrim", path_from=prim_spec_paths[0], path_to=new_path0)
        omni.kit.commands.execute("MovePrim", path_from=prim_spec_paths[1], path_to=new_path1)
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()

        self.assertEqual(len(root_layer_item.absolute_root_spec.children), 1)
        self.assertEqual(root_layer_item.absolute_root_spec.children[0].path, prim_spec_paths[2])
        self.assertEqual(len(root_layer_item.absolute_root_spec.children[0].children), 2)
        self.check_prim_spec_children(root_layer_item.absolute_root_spec.children[0], set([new_path0, new_path1]))

        omni.kit.undo.undo()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertEqual(len(root_layer_item.absolute_root_spec.children), 2)
        self.check_prim_spec_children(root_layer_item.absolute_root_spec, set(prim_spec_paths[1:3]))
        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, set([new_path0, prim_spec_paths[1], prim_spec_paths[2]]))

        omni.kit.undo.undo()
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, set(prim_spec_paths))

    @patch('omni.usd.is_usd_crate_file_version_supported')
    async def test_specifier_reference(self, mock_is_usd_crate_file_version_supported):
        # OMPE-37291: Mock crate file version check for non-existing crate file.
        mock_is_usd_crate_file_version_supported.return_value = True
        # Test for https://nvidia-omniverse.atlassian.net/browse/OM-34957

        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        layer_content = '''\
            #sdf 1.0

            def "test_prim" (
                prepend references = @../invalid/reference2.usd@
            )
            {
            }
        '''

        root_layer_item.layer.ImportFromString(layer_content)
        await self.app.next_update_async()
        await self.app.next_update_async()
        test_prim_spec = root_layer_item.absolute_root_spec.children[0]
        self.assertEqual(test_prim_spec.specifier, PrimSpecSpecifier.DEF_WITH_REFERENCE)

        stage = self.stage
        test_prim = stage.GetPrimAtPath("/test_prim")
        ref_and_layers = omni.usd.get_composed_references_from_prim(test_prim)
        for reference, layer in ref_and_layers:
            with Usd.EditContext(stage, layer):
                payload = Sdf.Payload(assetPath=reference.assetPath.replace("\\", "/"), primPath=reference.primPath, layerOffset=reference.layerOffset)
                omni.kit.commands.execute("RemoveReference", stage=stage, prim_path=test_prim.GetPath(), reference=reference)
                omni.kit.commands.execute("AddPayload", stage=stage, prim_path=test_prim.GetPath(), payload=payload)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertEqual(test_prim_spec.specifier, PrimSpecSpecifier.DEF_WITH_PAYLOAD)

        ref_and_layers = omni.usd.get_composed_payloads_from_prim(test_prim)
        for payload, layer in ref_and_layers:
            with Usd.EditContext(stage, layer):
                reference = Sdf.Reference(assetPath=payload.assetPath.replace("\\", "/"), primPath=payload.primPath, layerOffset=payload.layerOffset)
                omni.kit.commands.execute("RemovePayload", stage=stage, prim_path=test_prim.GetPath(), payload=payload)
                omni.kit.commands.execute("AddReference", stage=stage, prim_path=test_prim.GetPath(), reference=reference)
        await self.app.next_update_async()
        await self.app.next_update_async()
        self.assertEqual(test_prim_spec.specifier, PrimSpecSpecifier.DEF_WITH_REFERENCE)
