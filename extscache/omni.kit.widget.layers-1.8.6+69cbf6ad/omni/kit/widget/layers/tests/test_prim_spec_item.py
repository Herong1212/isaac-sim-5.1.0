import omni.kit.test
import os
import uuid
import omni.client

from omni.kit.usd.layers import LayerUtils
from omni.kit.widget.layers.layer_settings import LayerSettings
from omni.kit.widget.layers.prim_spec_item import PrimSpecSpecifier
from .base import TestLayerUIBase
from pxr import Sdf, UsdGeom


class TestLayerPrimSpecItemAPI(TestLayerUIBase):
    """Tests for layer model refresh reacted to usd stage changes."""

    async def setUp(self):
        await super().setUp()
        self.test_folder = omni.client.combine_urls(self.temp_dir, str(uuid.uuid1()))
        self.test_folder += "/"
        await omni.client.create_folder_async(self.test_folder)

        self.enable_missing_reference = LayerSettings().show_missing_reference
        LayerSettings().show_missing_reference = True
        self.stage = await self.prepare_empty_stage()

    async def tearDown(self):
        LayerSettings().show_missing_reference = self.enable_missing_reference
        await self.usd_context.close_stage_async()
        await omni.client.delete_async(self.test_folder)
        await super().tearDown()

    async def test_prim_spec_item_properties(self):
        temp_layer = Sdf.Layer.CreateAnonymous()
        typeless_prim = self.stage.DefinePrim("/test")
        cube_prim = self.stage.DefinePrim("/test/cube", "Cube")
        prim_with_reference = self.stage.DefinePrim("/test/reference", "Xform")
        prim_with_reference.GetReferences().AddReference(temp_layer.identifier)
        # Add invalid reference
        prim_with_reference.GetReferences().AddReference("../invalid_reference.usd")
        instanced_prim = self.stage.DefinePrim("/test/instanced", "Xform")
        instanced_prim.SetInstanceable(True)
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()

        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        self.assertEqual(len(root_layer_item.prim_specs), 1)
        typeless_prim_item = root_layer_item.prim_specs[0]
        self.assertEqual(len(typeless_prim_item.children), 3)
        cube_prim_item = typeless_prim_item.children[0]
        prim_with_reference_item = typeless_prim_item.children[1]
        instanced_prim_item = typeless_prim_item.children[2]
        self.check_prim_spec_regular_fields(
            typeless_prim_item, "test", "/test",
            children=["/test/cube", "/test/reference", "/test/instanced"],
            has_children=True
        )
        self.check_prim_spec_regular_fields(
            cube_prim_item, "cube", "/test/cube", type_name="Cube"
        )
        self.check_prim_spec_regular_fields(
            prim_with_reference_item, "reference", "/test/reference", type_name="Xform",
            specifier=PrimSpecSpecifier.DEF_WITH_REFERENCE,
            has_missing_reference=True
        )
        self.check_prim_spec_regular_fields(
            instanced_prim_item, "instanced", "/test/instanced", type_name="Xform",
            instanceable=True
        )

    async def test_prim_spec_item_filter(self):
        self.stage.DefinePrim("/test/filter/keyword1/keyword2")
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        self.assertEqual(len(root_layer_item.prim_specs), 1)

        test_prim = root_layer_item.prim_specs[0]
        filter_prim = test_prim.children[0]
        keyword1_prim = filter_prim.children[0]
        keyword2_prim = keyword1_prim.children[0]
        root_layer_item.prefilter("keyword1")
        self.assertTrue(layer_model.can_item_have_children(root_layer_item))
        self.assertTrue(test_prim.filtered)
        self.assertTrue(filter_prim.filtered)
        self.assertTrue(keyword1_prim.filtered)
        self.assertFalse(keyword2_prim.filtered)
