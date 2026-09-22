import asyncio
import carb
import os
import tempfile
import omni.kit.test
import omni.usd
import omni.client

from pxr import Sdf, Usd, UsdGeom, Gf
from omni.kit.usd.layers import get_layers, LayerUtils, get_layer_event_payload, LayerEventType, LayerEditMode


class TestSpecsLinking(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()

    def __get_all_property_paths(self, prim):
        paths = []
        for p in prim.GetProperties():
            paths.append(str(p.GetPath()))

        return paths

    def __get_all_prim_childrens(self, prim, hierarchy=False):
        paths = [str(prim.GetPath())]
        paths.extend(self.__get_all_property_paths(prim))
        if hierarchy:
            for child in prim.GetAllPrimChildren():
                paths.append(str(child.GetPath()))
                paths.extend(self.__get_all_property_paths(child))

        return paths

    def __get_all_stage_paths(self, stage):
        paths = []
        for prim in stage.TraverseAll():
            paths.extend(self.__get_all_prim_childrens(prim))

        return paths

    async def test_link_specs(self):
        layers = get_layers()
        specs_linking = layers.get_specs_linking()

        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.SPECS_LINKING_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        layers.set_edit_mode(LayerEditMode.SPECS_LINKING)

        context = omni.usd.get_context()
        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        root_layer.subLayerPaths.append(layer2.identifier)

        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        all_spec_paths = set(self.__get_all_stage_paths(stage))

        # Invalid identifier or spec path will return empty result.
        paths = specs_linking.link_spec("/", "")
        self.assertEqual(len(paths), 0)
        self.assertIsNone(payload)

        paths = specs_linking.link_spec("", layer0.identifier)
        self.assertEqual(len(paths), 0)
        self.assertIsNone(payload)

        # Links root prim to layer0 without hierarchy, root prim cannot be linked.
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=False)
        self.assertEqual(len(paths), 0)
        self.assertIsNone(payload)

        # Links all prims in the prim tree.
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        self.assertEqual(set(paths), all_spec_paths)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LINKING_CHANGED)
        self.assertEqual(set([layer0.identifier]), set(payload.layer_spec_paths.keys()))
        self.assertEqual(set(payload.layer_spec_paths[layer0.identifier]), set(all_spec_paths))

        paths = specs_linking.get_spec_layer_links("/", hierarchy=False)
        self.assertEqual(len(paths), 0)

        paths = specs_linking.get_spec_layer_links("/", hierarchy=True)
        for path, value in paths.items():
            self.assertIn(path, all_spec_paths)
            self.assertEqual(len(value), 1)
            self.assertEqual(value[0], layer0.identifier)
            self.assertTrue(specs_linking.is_spec_linked(path, layer0.identifier))
            self.assertTrue(specs_linking.is_spec_linked(path))
            self.assertFalse(specs_linking.is_spec_linked(path, layer1.identifier))

        # Since it's prim is already linked, add properties will not change anything.
        root_translate_path = "/root.xformOp:translate"
        specs_linking.link_spec(root_translate_path, layer0.identifier)
        paths = specs_linking.get_spec_layer_links("/", hierarchy=True)
        for path, value in paths.items():
            self.assertIn(path, all_spec_paths)
            self.assertEqual(len(value), 1)
            self.assertEqual(value[0], layer0.identifier)
        self.assertTrue(specs_linking.is_spec_linked(root_translate_path, layer0.identifier))
        self.assertTrue(specs_linking.is_spec_linked(root_translate_path))
        self.assertFalse(specs_linking.is_spec_linked(root_translate_path, layer1.identifier))

        # Links translate
        specs_linking.unlink_all_specs()
        payload = None
        specs_linking.link_spec(root_translate_path, layer0.identifier, hierarchy=True)
        paths = specs_linking.get_all_spec_links()
        prims = ["/root.xformOp:translate"]
        for path, value in paths.items():
            self.assertIn(path, prims)
            self.assertEqual(len(value), 1)
            self.assertEqual(value[0], layer0.identifier)

        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LINKING_CHANGED)
        self.assertEqual(set([layer0.identifier]), set(payload.layer_spec_paths.keys()))
        self.assertEqual(set(payload.layer_spec_paths[layer0.identifier]), set(prims))

        specs_linking.link_spec(root_translate_path, layer1.identifier, hierarchy=True)
        paths = specs_linking.get_spec_layer_links(root_translate_path, hierarchy=True)
        self.assertIn(root_translate_path, paths)
        layers = paths[root_translate_path]
        self.assertEqual(set([layer0.identifier, layer1.identifier]), set(layers))

        # Links root translate to layer2 only.
        paths = specs_linking.get_spec_layer_links(root_translate_path, hierarchy=True)
        specs_linking.unlink_spec_from_all_layers(root_translate_path)
        paths = specs_linking.get_spec_layer_links(root_translate_path, hierarchy=True)
        specs_linking.link_spec(root_translate_path, layer2.identifier)
        paths = specs_linking.get_spec_layer_links(root_translate_path, hierarchy=True)
        self.assertIn(root_translate_path, paths)
        layers = paths[root_translate_path]
        self.assertEqual(set([layer2.identifier]), set(layers))

        specs_linking.unlink_all_specs()
        # Link all prims to layer 0
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)

        # Link /root/test0/l1 and all its descendants to both layer0 and layer1
        paths = specs_linking.link_spec("/root/test0/l1", layer1.identifier, hierarchy=True)
        links = specs_linking.get_all_spec_links()
        for path, layers in links.items():
            if path.startswith("/root/test0/l1"):
                self.assertEqual(set(layers), set([layer0.identifier, layer1.identifier]))
            else:
                self.assertEqual(set(layers), set([layer0.identifier]))

    async def test_unlink_spec(self):
        layers = get_layers()
        specs_linking = layers.get_specs_linking()

        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.SPECS_LINKING_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        context = omni.usd.get_context()
        layers.set_edit_mode(LayerEditMode.SPECS_LINKING)

        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)

        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        all_spec_paths = set(self.__get_all_stage_paths(stage))

        # Links root prim to layer0 with hierarchy.
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        self.assertEqual(set(paths), all_spec_paths)
        links = specs_linking.get_all_spec_links()
        self.assertEqual(set(links), all_spec_paths)

        # Unlink absolute root path without hierarchy will unlink nothing
        specs_linking.unlink_spec("/", layer0.identifier, hierarchy=False)
        links = specs_linking.get_all_spec_links()
        self.assertEqual(set(paths), all_spec_paths)

        # Unlink all
        unlinked_paths = specs_linking.unlink_spec("/", layer0.identifier, hierarchy=True)
        links = specs_linking.get_all_spec_links()
        self.assertEqual(set(unlinked_paths), all_spec_paths)
        self.assertEqual(len(links), 0)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LINKING_CHANGED)
        self.assertEqual(set([layer0.identifier]), set(payload.layer_spec_paths.keys()))
        self.assertEqual(set(payload.layer_spec_paths[layer0.identifier]), set(all_spec_paths))
        for path in unlinked_paths:
            self.assertFalse(specs_linking.is_spec_linked(path))
            self.assertFalse(specs_linking.is_spec_linked(path, layer0.identifier))

        # Unlinks a subset of paths
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        unlinked_paths = specs_linking.unlink_spec("/root/test0", layer0.identifier, hierarchy=True)
        links = specs_linking.get_all_spec_links()
        expected_unlinked_paths = all_spec_paths.difference(set(links))
        self.assertEqual(set(unlinked_paths), set(expected_unlinked_paths))

        # Unlinks single path
        unlinked_paths = specs_linking.unlink_spec("/root", layer0.identifier, hierarchy=False)
        new_links = specs_linking.get_all_spec_links()
        expected_unlinked_paths = set(links).difference(set(new_links))
        self.assertEqual(set(unlinked_paths), set(expected_unlinked_paths))

        # Unlinks specs from subset of layers.
        specs_linking.unlink_all_specs()
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        paths.extend(specs_linking.link_spec("/", layer1.identifier, hierarchy=True))
        unlinked_paths = specs_linking.unlink_spec("/", layer0.identifier, hierarchy=True)
        links = specs_linking.get_all_spec_links()
        self.assertEqual(set(paths), all_spec_paths)
        self.assertEqual(set(unlinked_paths), all_spec_paths)

        # Checks if only layer1's link is existed.
        for _, linked_layers in links.items():
            self.assertEqual(linked_layers, [layer1.identifier])

        # Unlinks all specs linked to specific layers
        specs_linking.unlink_all_specs()
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        paths.extend(specs_linking.link_spec("/", layer1.identifier, hierarchy=True))
        unlinked_paths = specs_linking.unlink_specs_to_layer(layer0.identifier)
        links = specs_linking.get_all_spec_links()
        self.assertEqual(set(paths), all_spec_paths)
        self.assertEqual(set(unlinked_paths), all_spec_paths)
        for _, linked_layers in links.items():
            self.assertEqual(linked_layers, [layer1.identifier])

        # Unlinks specific specs from all layers
        specs_linking.unlink_all_specs()
        paths = specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        paths.extend(specs_linking.link_spec("/", layer1.identifier, hierarchy=True))
        unlinked_paths = specs_linking.unlink_spec_from_all_layers("/root/test0", hierarchy=True)
        self.assertTrue(len(unlinked_paths) != 0)
        links = specs_linking.get_all_spec_links()
        self.assertTrue("/root/test0" not in links)
        expected_unlinked_paths = all_spec_paths.difference(set(links))
        self.assertEqual(set(unlinked_paths), set(expected_unlinked_paths))
    async def test_stage_edits_for_spec_links(self):
        layers = get_layers()
        specs_linking = layers.get_specs_linking()
        context = omni.usd.get_context()
        layers.set_edit_mode(LayerEditMode.SPECS_LINKING)

        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        root_layer.subLayerPaths.append(layer2.identifier)
        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        await omni.kit.app.get_app().next_update_async()
        specs_linking.link_spec("/", layer0.identifier, hierarchy=True)
        specs_linking.link_spec("/", layer1.identifier, hierarchy=True)

        # Create an attribute and make sure its edits are distributed to both layer0 and layer1
        prim = stage.GetPrimAtPath("/root/test0/l1")
        attr = prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
        attr.Set(1.0)
        await omni.kit.app.get_app().next_update_async()
        layer0_prim_spec = layer0.GetPrimAtPath("/root/test0/l1")
        layer1_prim_spec = layer1.GetPrimAtPath("/root/test0/l1")
        self.assertTrue(layer0_prim_spec)
        self.assertTrue(layer1_prim_spec)
        attr_spec0 = layer0.GetAttributeAtPath(attr.GetPath())
        attr_spec1 = layer1.GetAttributeAtPath(attr.GetPath())
        self.assertTrue(attr_spec0)
        self.assertTrue(attr_spec1)
        self.assertEqual(attr_spec0.default, 1.0)
        self.assertEqual(attr_spec1.default, 1.0)

        # Create an attribute and make sure its edits are distributed to layer0 only.
        # Unlink it from layer1 firstly to leave layer0 only.
        prim = stage.GetPrimAtPath("/root/test0/l1/l2")
        paths = specs_linking.unlink_spec(prim.GetPath(), layer1.identifier, hierarchy=False)
        attr = prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
        attr.Set(100.0)
        await omni.kit.app.get_app().next_update_async()
        layer0_prim_spec = layer0.GetPrimAtPath(prim.GetPath())
        layer1_prim_spec = layer1.GetPrimAtPath(prim.GetPath())
        self.assertTrue(layer0_prim_spec)
        self.assertFalse(layer1_prim_spec)
        attr_spec0 = layer0.GetAttributeAtPath(attr.GetPath())
        self.assertTrue(attr_spec0)
        self.assertEqual(attr_spec0.default, 100.0)

        # Link rotate attr to layer2 only, and lock translate attr.
        translate_attr = "/root/test0/l1/l2/l3.xformOp:translate"
        rotate_attr = "/root/test0/l1/l2/l3.xformOp:rotateXYZ"
        specs_linking.unlink_spec_from_all_layers(rotate_attr)
        specs_linking.link_spec(rotate_attr, layer2.identifier, hierarchy=False)
        xform_prim = stage.GetPrimAtPath("/root/test0/l1/l2/l3")
        common_api = UsdGeom.XformCommonAPI(xform_prim)
        common_api.SetRotate(Gf.Vec3f(200.0, 200.0, 200.0))
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        xform_vectors = common_api.GetXformVectors(Usd.TimeCode.Default())
        # Translate does not change and rotation is changed.
        self.assertEqual(xform_vectors[1], Gf.Vec3f(200.0, 200.0, 200.0))

        layer0_translate_attr = layer0.GetAttributeAtPath(translate_attr)
        layer1_translate_attr = layer1.GetAttributeAtPath(translate_attr)
        layer2_translate_attr = layer2.GetAttributeAtPath(translate_attr)
        root_layer_translate_attr = root_layer.GetAttributeAtPath(translate_attr)
        self.assertFalse(root_layer_translate_attr)
        self.assertFalse(layer0_translate_attr)
        self.assertFalse(layer1_translate_attr)
        self.assertFalse(layer2_translate_attr)
        layer0_rotation_attr = layer0.GetAttributeAtPath(rotate_attr)
        layer1_rotation_attr = layer1.GetAttributeAtPath(rotate_attr)
        layer2_rotation_attr = layer2.GetAttributeAtPath(rotate_attr)
        root_layer_rotation_attr = root_layer.GetAttributeAtPath(rotate_attr)
        self.assertFalse(layer0_rotation_attr)
        self.assertFalse(layer1_rotation_attr)
        self.assertTrue(layer2_rotation_attr)
        self.assertFalse(root_layer_rotation_attr)
