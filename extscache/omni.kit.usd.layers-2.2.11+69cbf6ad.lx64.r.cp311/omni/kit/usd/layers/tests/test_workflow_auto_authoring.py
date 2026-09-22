import asyncio
from enum import auto
import carb
import os
import tempfile
import omni.kit.test
import omni.usd
import omni.client

from pxr import Sdf, Usd, UsdGeom, Gf
from omni.kit.usd.layers import get_layers, LayerUtils, get_layer_event_payload, LayerEventType, LayerEditMode


class TestAutoAuthoring(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()

    async def test_edit_mode_switch(self):
        layers = get_layers()
        auto_authoring = layers.get_auto_authoring()

        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.DEFAULT_LAYER_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        stage = self.usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        layers.set_edit_mode(LayerEditMode.NORMAL)
        self.assertEqual(layers.get_edit_mode(), LayerEditMode.NORMAL)
        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        self.assertTrue(auto_authoring.is_enabled())
        self.assertEqual(layers.get_edit_mode(), LayerEditMode.AUTO_AUTHORING)
        self.assertEqual(auto_authoring.get_default_layer(), root_layer.identifier)

        auto_authoring.set_default_layer(stage.GetSessionLayer().identifier)
        # It cannot set session layer as edit layer.
        self.assertEqual(auto_authoring.get_default_layer(), root_layer.identifier)

        layer0 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        auto_authoring.set_default_layer(layer0.identifier)
        self.assertEqual(auto_authoring.get_default_layer(), layer0.identifier)

        # Set invalid edit layer will switch it to root layer
        auto_authoring.set_default_layer("invalid_identifier.usd")
        self.assertEqual(auto_authoring.get_default_layer(), layer0.identifier)

        # Try to change edit target will fail
        LayerUtils.set_edit_target(stage, root_layer.identifier)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        edit_target_identifier = LayerUtils.get_edit_target(stage)
        self.assertNotEqual(LayerUtils.get_edit_target(stage), root_layer.identifier)
        self.assertIn("__DELTA_LAYER__", edit_target_identifier)

        # Switch from no deltas mode to authoring mode will keep the current edit layer as edit target.
        auto_authoring.set_default_layer(root_layer.identifier)
        payload = None
        auto_authoring.set_default_layer(layer0.identifier)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.DEFAULT_LAYER_CHANGED)
        self.assertEqual(layer0.identifier, auto_authoring.get_default_layer())
        layers.set_edit_mode(LayerEditMode.NORMAL)
        self.assertEqual(layers.get_edit_mode(), LayerEditMode.NORMAL)
        self.assertEqual(LayerUtils.get_edit_target(stage), layer0.identifier)

    async def _wait(self):
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    async def test_deltas_merge_under_auto_authoring_mode(self):
        layers = get_layers()
        auto_authoring = layers.get_auto_authoring()

        stage = self.usd_context.get_stage()
        root = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root.subLayerPaths.append(layer0.identifier)
        root.subLayerPaths.append(layer1.identifier)
        root.subLayerPaths.append(layer2.identifier)

        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        scale = Gf.Vec3f(1.0, 1.0, 1.0)

        layers.set_edit_mode(LayerEditMode.NORMAL)
        LayerUtils.set_edit_target(stage, layer1.identifier)
        cube_prim = UsdGeom.Cube.Define(stage, "/cube")
        UsdGeom.XformCommonAPI(cube_prim).SetTranslate(translation)
        UsdGeom.XformCommonAPI(cube_prim).SetRotate(rotation)
        UsdGeom.XformCommonAPI(cube_prim).SetScale(scale)

        LayerUtils.set_edit_target(stage, layer2.identifier)
        sphere_prim = UsdGeom.Sphere.Define(stage, "/sphere")
        UsdGeom.XformCommonAPI(sphere_prim).SetTranslate(translation)
        UsdGeom.XformCommonAPI(sphere_prim).SetRotate(rotation)
        UsdGeom.XformCommonAPI(sphere_prim).SetScale(scale)

        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        LayerUtils.set_edit_target(stage, layer0.identifier)
        # It needs to wait for at least one frame so that it will not allow to change edit target.
        await self._wait()
        auto_authoring.set_default_layer(layer0.identifier)
        translate = Gf.Vec3d(100.0, 100.0, 100.0)
        UsdGeom.XformCommonAPI(cube_prim).SetTranslate(translate)
        UsdGeom.XformCommonAPI(sphere_prim).SetTranslate(translate * 2)
        await self._wait()
        xform_vectors = UsdGeom.XformCommonAPI(cube_prim).GetXformVectors(Usd.TimeCode.Default())
        self.assertFalse(layer0.GetPrimAtPath(cube_prim.GetPath()))
        self.assertEqual(xform_vectors[0], translate)

        # Make sure the authoring is merged
        translate_property_path = cube_prim.GetPath().AppendProperty("xformOp:translate")
        translate_property = layer1.GetPropertyAtPath(translate_property_path)
        self.assertTrue(translate_property)
        self.assertEqual(translate_property.default, translate)

        xform_vectors = UsdGeom.XformCommonAPI(sphere_prim).GetXformVectors(Usd.TimeCode.Default())
        self.assertFalse(layer0.GetPrimAtPath(sphere_prim.GetPath()))
        self.assertEqual(xform_vectors[0], translate * 2)

        # Make sure the authoring is merged
        translate_property_path = sphere_prim.GetPath().AppendProperty("xformOp:translate")
        translate_property = layer2.GetPropertyAtPath(translate_property_path)
        self.assertTrue(translate_property)
        self.assertEqual(translate_property.default, translate * 2)

        # Switches to normal authoring mode and creates deltas there for cube
        layers.set_edit_mode(LayerEditMode.NORMAL)
        LayerUtils.set_edit_target(stage, layer0.identifier)
        translate = Gf.Vec3d(1000.0, 1000.0, 1000.0)
        UsdGeom.XformCommonAPI(cube_prim).SetTranslate(translate)
        xform_vectors = UsdGeom.XformCommonAPI(cube_prim).GetXformVectors(Usd.TimeCode.Default())
        self.assertTrue(layer0.GetPrimAtPath(cube_prim.GetPath()))
        self.assertEqual(xform_vectors[0], translate)

        # Then modify cube and sphere again, this time cube movement will go into layer0 instead
        # of where its defined, which sphere will still be in its define layer.
        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        auto_authoring.set_default_layer(layer0.identifier)
        translate = Gf.Vec3d(200.0, 200.0, 200.0)
        UsdGeom.XformCommonAPI(cube_prim).SetTranslate(translate)
        UsdGeom.XformCommonAPI(sphere_prim).SetTranslate(translate * 2)
        await self._wait()

        # Check layer 0
        xform_vectors = UsdGeom.XformCommonAPI(cube_prim).GetXformVectors(Usd.TimeCode.Default())
        self.assertTrue(layer0.GetPrimAtPath(cube_prim.GetPath()))
        self.assertEqual(xform_vectors[0], translate)

        # Make sure the authoring is merged
        translate_property_path = cube_prim.GetPath().AppendProperty("xformOp:translate")
        translate_property = layer0.GetPropertyAtPath(translate_property_path)
        self.assertTrue(translate_property)
        self.assertEqual(translate_property.default, translate)

        xform_vectors = UsdGeom.XformCommonAPI(sphere_prim).GetXformVectors(Usd.TimeCode.Default())
        self.assertFalse(layer0.GetPrimAtPath(sphere_prim.GetPath()))
        self.assertEqual(xform_vectors[0], translate * 2)

        # Make sure the authoring is merged
        translate_property_path = sphere_prim.GetPath().AppendProperty("xformOp:translate")
        translate_property = layer2.GetPropertyAtPath(translate_property_path)
        self.assertTrue(translate_property)
        self.assertEqual(translate_property.default, translate * 2)

    async def test_new_prim_create_under_auto_authoring_mode(self):
        layers = get_layers()
        auto_authoring = layers.get_auto_authoring()

        stage = self.usd_context.get_stage()
        root = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root.subLayerPaths.append(layer0.identifier)
        root.subLayerPaths.append(layer1.identifier)
        root.subLayerPaths.append(layer2.identifier)

        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        auto_authoring.set_default_layer(layer1.identifier)
        # Making sure that layer1 is not edit target at this moment.
        self.assertNotEqual(LayerUtils.get_edit_target(stage), layer1.identifier)

        all_cube_prims = []
        for i in range(1000):
            cube_path = f"/cube{i}"
            self.assertFalse(layer1.GetPrimAtPath(cube_path))
            cube_prim = UsdGeom.Cube.Define(stage, cube_path)
            # It's not in layer1 even after creation until it's moved in next frame.
            self.assertFalse(layer1.GetPrimAtPath(cube_path))
            self.assertTrue(cube_prim)
            all_cube_prims.append(cube_prim)

        # It needs to wait for prims move.
        await self._wait()

        for i in range(len(all_cube_prims)):
            cube_path = f"/cube{i}"
            cube_prim = all_cube_prims[i]
            prim_stack = cube_prim.GetPrim().GetPrimStack()
            # The first one is the auto authoring layer
            cube_prim_spec = layer1.GetPrimAtPath(cube_prim.GetPath())
            self.assertTrue(cube_prim_spec)
            self.assertTrue(cube_prim_spec.path, cube_path)
            self.assertTrue(cube_prim_spec)
            self.assertEqual(cube_prim_spec.specifier, Sdf.SpecifierDef)
            self.assertEqual(cube_prim_spec.typeName, "Cube")

    async def test_correct_merge_layer_of_spec(self):
        layers = get_layers()
        auto_authoring = layers.get_auto_authoring()

        stage = self.usd_context.get_stage()
        root = stage.GetRootLayer()
        session = stage.GetSessionLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        root.subLayerPaths.append(layer0.identifier)
        root.subLayerPaths.append(layer1.identifier)

        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        auto_authoring.set_default_layer(layer1.identifier)
        # Making sure that layer1 is not edit target at this moment.
        self.assertNotEqual(LayerUtils.get_edit_target(stage), layer1.identifier)

        cube_path = f"/cube0"
        with Usd.EditContext(stage, layer1):
            cube_prim = UsdGeom.Cube.Define(stage, cube_path)
            self.assertFalse(layer0.GetPrimAtPath(cube_path))
            self.assertTrue(cube_prim)

        # Authoring to auto authoring layer.
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(200.0, 200.0, 200.0))
        await self._wait()

        xform_vectors = UsdGeom.XformCommonAPI(cube_prim.GetPrim()).GetXformVectors(Usd.TimeCode.Default())
        self.assertEqual(xform_vectors[0], Gf.Vec3d(200.0, 200.0, 200.0))
        self.assertFalse(layer0.GetPrimAtPath(cube_path))
        self.assertFalse(root.GetPrimAtPath(cube_path))
        self.assertFalse(session.GetPrimAtPath(cube_path))

        # Switch to normal mode to make sure it's saved to layer1.
        layers.set_edit_mode(LayerEditMode.NORMAL)
        xform_vectors = UsdGeom.XformCommonAPI(cube_prim.GetPrim()).GetXformVectors(Usd.TimeCode.Default())
        self.assertEqual(xform_vectors[0], Gf.Vec3d(200.0, 200.0, 200.0))

        # Switch to auto authoring mode again and try to edit weaker layers under auto authoring layer.
        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)

        # Create a delta for cube_prim in layer 0
        with Usd.EditContext(stage, layer0):
            cube_prim.GetPrim().CreateAttribute("test_property", Sdf.ValueTypeNames.Bool, False).Set(False)

        # Edit the translate again and check if the translate will be merged to layer1 instead of layer0
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(400.0, 400.0, 400.0))
        await self._wait()

        xform_vectors = UsdGeom.XformCommonAPI(cube_prim.GetPrim()).GetXformVectors(Usd.TimeCode.Default())
        self.assertEqual(xform_vectors[0], Gf.Vec3d(400.0, 400.0, 400.0))

    async def test_whole_stage_refresh(self):
        stage = self.usd_context.get_stage()
        layers = get_layers()
        root = stage.GetRootLayer()
        session = stage.GetSessionLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        root.subLayerPaths.append(layer0.identifier)
        root.subLayerPaths.append(layer1.identifier)

        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)

        cube_path = f"/cube0"
        with Usd.EditContext(stage, layer1):
            cube_prim = UsdGeom.Cube.Define(stage, cube_path)
            self.assertFalse(layer0.GetPrimAtPath(cube_path))
            self.assertTrue(cube_prim)

            UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(100.0, 100.0, 100.0))

        identifier = session.subLayerPaths[0]
        auto_authoring_layer = Sdf.Find(identifier)
        self.assertTrue(auto_authoring_layer)
        self.assertTrue(len(auto_authoring_layer.rootPrims) == 0)

        # Creates a delta to auto authoring layer
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(200.0, 200.0, 200.0))
        await self._wait()
        self.assertTrue(len(auto_authoring_layer.rootPrims) > 0)

        # Remove layer to trigger whole stage refresh
        del root.subLayerPaths[1]
        await self._wait()

        # After that, the auto authoring layer will be cleared.
        self.assertTrue(len(auto_authoring_layer.rootPrims) == 0)

    async def test_weaker_layers_authoring(self):
        stage = self.usd_context.get_stage()
        layers = get_layers()
        auto_authoring = layers.get_auto_authoring()
        root = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        root.subLayerPaths.append(layer0.identifier)
        root.subLayerPaths.append(layer1.identifier)

        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        auto_authoring.set_default_layer(layer1.identifier)
        # Making sure that layer1 is not edit target at this moment.
        self.assertNotEqual(LayerUtils.get_edit_target(stage), layer1.identifier)

        cube_path = f"/cube0"
        with Usd.EditContext(stage, layer1):
            cube_prim = UsdGeom.Cube.Define(stage, cube_path)
            self.assertFalse(layer0.GetPrimAtPath(cube_path))
            self.assertTrue(cube_prim)

            UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(100.0, 100.0, 100.0))

        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(100.0, 100.0, 100.0))

        # Authoring to auto authoring layer.
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(200.0, 200.0, 200.0))
        await self._wait()

        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(200.0, 200.0, 200.0))
        self.assertFalse(layer0.GetPrimAtPath(cube_path))

        # Switch to normal mode to make sure it's saved back.
        layers.set_edit_mode(LayerEditMode.NORMAL)
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(200.0, 200.0, 200.0))

        # Switch to auto authoring mode again and try to edit weaker layers under auto authoring layer.
        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(400.0, 400.0, 400.0))
        await self._wait()

        # Edit weaker layers
        with Usd.EditContext(stage, layer0):
            UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(300.0, 300.0, 300.0))

        # Wait until it's merge back to auto authoring layer
        await self._wait()
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(300.0, 300.0, 300.0))

        # Edit weakest layer to make sure it will not be merged back to auto authoring layer
        # since layer0 is stronger.
        with Usd.EditContext(stage, layer1):
            UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(1000.0, 1000.0, 1000.0))
        await self._wait()
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(300.0, 300.0, 300.0))

    def _get_xform_translate(self, prim):
        xform_vectors = UsdGeom.XformCommonAPI(prim).GetXformVectors(Usd.TimeCode.Default())

        return xform_vectors[0]

    async def test_read_only_layer_edit(self):
        # Test for OM-35472
        stage = self.usd_context.get_stage()
        root = stage.GetRootLayer()
        layers = get_layers()
        layer0 = Sdf.Layer.CreateAnonymous()
        root.subLayerPaths.append(layer0.identifier)

        layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)

        with Usd.EditContext(stage, layer0):
            cube_prim = UsdGeom.Cube.Define(stage, "/world/cube")
            UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(1000.0, 1000.0, 1000.0))

        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(1000, 1000, 1000))

        LayerUtils.set_layer_lock_status(root, layer0.identifier, True)
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(100.0, 100.0, 100.0))
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(100, 100, 100))

        # It will return back to old value since it's read-only layer
        await self._wait()
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(1000, 1000, 1000))

        # Make sure it can be edited again
        LayerUtils.set_layer_lock_status(root, layer0.identifier, False)
        UsdGeom.XformCommonAPI(cube_prim.GetPrim()).SetTranslate(Gf.Vec3d(100.0, 100.0, 100.0))
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(100, 100, 100))

        await self._wait()
        self.assertEqual(self._get_xform_translate(cube_prim.GetPrim()), Gf.Vec3d(100, 100, 100))
