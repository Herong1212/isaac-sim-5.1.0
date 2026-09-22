import asyncio
import carb
import os
import tempfile
import omni.kit.test
import omni.usd
import omni.client

from pxr import Sdf, Usd, UsdGeom, Gf
from omni.kit.usd.layers import get_layers, LayerUtils, get_layer_event_payload, LayerEventType


class TestSpecsLocking(omni.kit.test.AsyncTestCase):

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

    async def test_lock_unlock_specs_and_events(self):
        layers = get_layers()
        specs_locking = layers.get_specs_locking()

        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.SPECS_LOCKING_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        context = omni.usd.get_context()
        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        UsdGeom.XformCommonAPI(asset_prim).SetTranslate(Gf.Vec3d(1.0))
        all_spec_paths = set(self.__get_all_stage_paths(stage))

        # Lock all
        locked_paths = specs_locking.lock_spec("/", hierarchy=True)
        self.assertEqual(set(locked_paths), set(all_spec_paths))
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LOCKING_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set(all_spec_paths))

        all_locked_paths = specs_locking.get_all_locked_specs()
        self.assertEqual(set(all_locked_paths), set(all_spec_paths))

        payload = None
        unlocked_paths = specs_locking.unlock_spec("/", hierarchy=True)
        self.assertEqual(set(unlocked_paths), set(locked_paths))
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LOCKING_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set(locked_paths))

        locked_paths = specs_locking.lock_spec("/root/test0", hierarchy=True)
        specs_locking.unlock_all_specs()
        all_unlocked_paths = specs_locking.get_all_locked_specs()
        self.assertEqual(len(all_unlocked_paths), 0)

        payload = None
        locked_paths = specs_locking.lock_spec("/root", hierarchy=False)
        self.assertEqual(locked_paths, ["/root"])
        self.assertTrue(specs_locking.is_spec_locked("/root"))
        self.assertFalse(specs_locking.is_spec_locked("/root/test0"))
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LOCKING_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set(["/root"]))

        payload = None
        specs_locking.unlock_all_specs()
        lock_single_attribute = asset_name + ".xformOp:translate"
        attributes = specs_locking.lock_spec(lock_single_attribute, False)
        self.assertEqual(set(attributes), set([lock_single_attribute]))
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SPECS_LOCKING_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([lock_single_attribute]))

    async def _try_to_edit_translate(self, xform_api, new_value, expected_value):
        xform_api.SetTranslate(new_value)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        xform_vectors = xform_api.GetXformVectors(Usd.TimeCode.Default())
        self.assertEqual(xform_vectors[0], expected_value)

    async def test_specs_locking_for_stage_edits(self):
        layers = get_layers()
        specs_locking = layers.get_specs_locking()

        context = omni.usd.get_context()
        root_layer = Sdf.Layer.CreateAnonymous()
        stage = Usd.Stage.Open(root_layer)
        # Initialize a prim and its translation
        asset_name = f"/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        xform_api = UsdGeom.XformCommonAPI(asset_prim)
        # It can be changed if it's not locked.
        await self._try_to_edit_translate(xform_api, Gf.Vec3d(1.0), Gf.Vec3d(1.0))

        await context.attach_stage_async(stage)

        layer0 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)

        locked_attribute = asset_name + ".xformOp:translate"
        attributes = specs_locking.lock_spec(locked_attribute, False)
        self.assertEqual(set(attributes), set([locked_attribute]))

        # Try to modify translate will return to state before it's locked.
        await self._try_to_edit_translate(xform_api, Gf.Vec3d(2.0), Gf.Vec3d(1.0))

        # Try to modify translate to other sublayers will return to it's previous state also.
        session_layer = stage.GetSessionLayer()
        with Usd.EditContext(stage, session_layer):
            await self._try_to_edit_translate(xform_api, Gf.Vec3d(2.0), Gf.Vec3d(1.0))
            self.assertFalse(session_layer.GetPrimAtPath(locked_attribute))
            self.assertFalse(session_layer.GetPrimAtPath(asset_name + ".xformOpOrder"))

        with Usd.EditContext(stage, layer0):
            await self._try_to_edit_translate(xform_api, Gf.Vec3d(2.0), Gf.Vec3d(1.0))
            self.assertFalse(session_layer.GetPrimAtPath(locked_attribute))
            self.assertFalse(session_layer.GetPrimAtPath(asset_name + ".xformOpOrder"))

        async def add_reference_and_check(prim, identifier, expected):
            prim.GetReferences().AddReference(identifier)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
            self.assertEqual(len(ref_and_layers), len(expected))
            identifiers = [item[0].assetPath for item in ref_and_layers]
            self.assertEqual(set(identifiers), set(expected))

        # Locks whole prim and try to add reference
        specs_locking.lock_spec(asset_name, True)
        layer1 = Sdf.Layer.CreateAnonymous()
        await add_reference_and_check(asset_prim, layer1.identifier, [])

        # Unlock and see
        attributes = specs_locking.unlock_spec(asset_name, False)
        await add_reference_and_check(asset_prim, layer1.identifier, [layer1.identifier])

        # Lock add and add another
        layer2 = Sdf.Layer.CreateAnonymous()
        attributes = specs_locking.lock_spec(asset_name, False)
        await add_reference_and_check(asset_prim, layer2.identifier, [layer1.identifier])
