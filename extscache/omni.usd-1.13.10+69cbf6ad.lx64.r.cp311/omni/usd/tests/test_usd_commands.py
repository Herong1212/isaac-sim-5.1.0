import os
from pathlib import Path
import carb
from unittest.mock import patch, PropertyMock
import omni.kit.test

import omni.kit.undo
import omni.kit.commands
import omni.timeline
import omni.usd
import omni.client
import omni.client.utils as clientutils

from pxr import Gf, Kind, Sdf, Usd, UsdGeom, UsdShade

CURRENT_PATH = Path(__file__).parent.joinpath("data").absolute().resolve()

FILE_PATH_ROOT = str(CURRENT_PATH.joinpath("material_root.usda")).replace("\\", "/")
FILE_PATH_SUB = str(CURRENT_PATH.joinpath("material_sub.usda")).replace("\\", "/")


def getStageDefaultPrimPath(stage):
    if stage.HasDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        return Sdf.Path.absoluteRootPath


class TestUsdCommands(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()
        omni.client.set_retries(*self.previous_retry_values)

    async def test_reference(self):
        stage = Usd.Stage.CreateInMemory()
        stage.DefinePrim("/world")

        layer = Sdf.Layer.CreateAnonymous()

        omni.kit.commands.execute(
            "AddReference",
            stage=stage,
            prim_path="/world",
            reference=Sdf.Reference(layer.identifier)
        )

        prim_spec = stage.GetRootLayer().GetPrimAtPath("/world")

        def layer_in_list(layer):
            return Sdf.Reference(layer.identifier) in prim_spec.referenceList.GetAddedOrExplicitItems()

        self.assertTrue(layer_in_list(layer))

        omni.kit.undo.undo()

        self.assertTrue(not layer_in_list(layer))

        omni.kit.undo.redo()

        self.assertTrue(layer_in_list(layer))

        omni.kit.commands.execute(
            "RemoveReference",
            stage=stage,
            prim_path="/world",
            reference=Sdf.Reference(layer.identifier)
        )

        self.assertTrue(not layer_in_list(layer))

        omni.kit.undo.undo()

        self.assertTrue(layer_in_list(layer))

        layer1 = Sdf.Layer.CreateAnonymous()

        omni.kit.commands.execute(
            "ReplaceReference",
            stage=stage,
            prim_path="/world",
            old_reference=Sdf.Reference(layer.identifier),
            new_reference=Sdf.Reference(layer1.identifier)
        )

        self.assertTrue(not layer_in_list(layer))
        self.assertTrue(layer_in_list(layer1))

        omni.kit.undo.undo()

        self.assertTrue(layer_in_list(layer))
        self.assertTrue(not layer_in_list(layer1))

    async def test_payload(self):
        stage = Usd.Stage.CreateInMemory()
        stage.DefinePrim("/world")

        layer = Sdf.Layer.CreateAnonymous()

        omni.kit.commands.execute(
            "AddPayload",
            stage=stage,
            prim_path="/world",
            payload=Sdf.Payload(layer.identifier)
        )

        prim_spec = stage.GetRootLayer().GetPrimAtPath("/world")

        def layer_in_list(layer):
            return Sdf.Payload(layer.identifier) in prim_spec.payloadList.GetAddedOrExplicitItems()

        self.assertTrue(layer_in_list(layer))

        omni.kit.undo.undo()

        self.assertTrue(not layer_in_list(layer))

        omni.kit.undo.redo()

        self.assertTrue(layer_in_list(layer))

        omni.kit.commands.execute(
            "RemovePayload",
            stage=stage,
            prim_path="/world",
            payload=Sdf.Payload(layer.identifier)
        )

        self.assertTrue(not layer_in_list(layer))

        omni.kit.undo.undo()

        self.assertTrue(layer_in_list(layer))

        layer1 = Sdf.Layer.CreateAnonymous()

        omni.kit.commands.execute(
            "ReplacePayload",
            stage=stage,
            prim_path="/world",
            old_payload=Sdf.Payload(layer.identifier),
            new_payload=Sdf.Payload(layer1.identifier)
        )

        self.assertTrue(not layer_in_list(layer))
        self.assertTrue(layer_in_list(layer1))

        omni.kit.undo.undo()

        self.assertTrue(layer_in_list(layer))
        self.assertTrue(not layer_in_list(layer1))

    async def test_create_prim(self):
        omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        def check_exist():
            prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
            self.assertTrue(prim)
            self.assertFalse(prim.IsA(UsdGeom.Mesh))
            self.assertTrue(prim.IsA(UsdGeom.Xformable))
            self.assertTrue(prim.IsA(UsdGeom.Sphere))
            self.assertFalse(prim.IsA(UsdGeom.Cylinder))
            model_api = Usd.ModelAPI(prim)
            kind = model_api.GetKind()
            self.assertFalse(kind == Kind.Tokens.model)

        def check_does_not_exist():
            self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))

        check_exist()

        # give hydra a frame before deleting to catch up so it doesn't spew coding error about not finding prim
        await omni.kit.app.get_app().next_update_async()
        omni.kit.undo.undo()
        check_does_not_exist()
        omni.kit.undo.redo()
        check_exist()
        omni.kit.undo.undo()
        check_does_not_exist()

    async def test_copy_prim(self):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)
        root_layer = stage.GetRootLayer()
        ref_stage = Usd.Stage.CreateInMemory()
        ref_layer = ref_stage.GetRootLayer()

        root_ref_cube = UsdGeom.Cube.Define(ref_stage, "/Cube")
        UsdGeom.Cube.Define(ref_stage, "/Cube/Cube2")
        ref_stage.SetDefaultPrim(root_ref_cube.GetPrim())

        layer_strong = Sdf.Layer.CreateAnonymous()
        layer_weak = Sdf.Layer.CreateAnonymous()
        layer_copy = Sdf.Layer.CreateAnonymous()

        root_layer.subLayerPaths = [layer_strong.identifier, layer_weak.identifier, layer_copy.identifier]

        with Usd.EditContext(stage, layer_weak):
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
            stage.DefinePrim("/RefCube").GetReferences().AddReference(ref_layer.identifier)

        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        prim_ref_leaf = stage.GetPrimAtPath("/RefCube/Cube2")
        self.assertTrue(prim)
        self.assertTrue(prim_ref_leaf)
        self.assertTrue(layer_weak.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
        self.assertFalse(layer_strong.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
        sphere = UsdGeom.Sphere(prim)

        # Create delta on strong layer
        with Usd.EditContext(stage, layer_strong):
            sphere.CreateRadiusAttr(1.234)

        radius = sphere.GetRadiusAttr().Get()
        self.assertTrue(radius == 1.234)

        def check(expected_path, expected_radius, assert_strong, assert_weak, assert_copy):
            nonlocal layer_strong
            nonlocal layer_weak
            nonlocal layer_copy
            assert_strong(layer_strong.GetPrimAtPath(expected_path))
            assert_weak(layer_weak.GetPrimAtPath(expected_path))
            assert_copy(layer_copy.GetPrimAtPath(expected_path))
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(expected_path))
            radius = sphere.GetRadiusAttr().Get()
            self.assertTrue(radius == expected_radius)

        # Test default copy behavior
        # Expected: default_prim_path.AppendChild("Sphere_01") created only on layer_copy. delta on layer_strong will be discarded.
        expected_path = default_prim_path.AppendChild("Sphere_01")
        carb.log_info("Test Duplicate")
        with Usd.EditContext(stage, layer_copy):
            omni.kit.commands.execute("CopyPrim", path_from=default_prim_path.AppendChild("Sphere").pathString)
            check(expected_path, 1.0, self.assertFalse, self.assertFalse, self.assertTrue)
            omni.kit.undo.undo()
            self.assertFalse(stage.GetPrimAtPath(expected_path))
            omni.kit.undo.redo()
            check(expected_path, 1.0, self.assertFalse, self.assertFalse, self.assertTrue)

        # Test copy all layers separately
        # Expected: default_prim_path.AppendChild("SphereAllLayer") created on layer_weak and layer_strong. Delta preserved in layer_strong.
        expected_path = default_prim_path.AppendChild("SphereAllLayers")
        carb.log_info("Test Duplicate - All Layers")
        with Usd.EditContext(stage, layer_copy):
            omni.kit.commands.execute(
                "CopyPrim",
                path_from=default_prim_path.AppendChild("Sphere").pathString,
                path_to=expected_path.pathString,
                duplicate_layers=True,
            )
            check(expected_path, 1.234, self.assertTrue, self.assertTrue, self.assertFalse)
            omni.kit.undo.undo()
            self.assertFalse(stage.GetPrimAtPath(expected_path))
            omni.kit.undo.redo()
            check(expected_path, 1.234, self.assertTrue, self.assertTrue, self.assertFalse)

        # Test copy all layers and collapse to one combined prim.
        # Expected: default_prim_path.AppendChild("SphereCollapsed") created on layer_copy. Delta combined into final result.
        expected_path = default_prim_path.AppendChild("SphereCollapsed")
        carb.log_info("Test Duplicate - Collapsed")
        with Usd.EditContext(stage, layer_copy):
            omni.kit.commands.execute(
                "CopyPrim",
                path_from=default_prim_path.AppendChild("Sphere").pathString,
                path_to=expected_path.pathString,
                combine_layers=True,
            )
            check(expected_path, 1.234, self.assertFalse, self.assertFalse, self.assertTrue)
            omni.kit.undo.undo()
            self.assertFalse(stage.GetPrimAtPath(expected_path))
            omni.kit.undo.redo()
            check(expected_path, 1.234, self.assertFalse, self.assertFalse, self.assertTrue)

        # Test collaps a child of a referenced prim.
        # Expected: /RefCube/Cube2_01 will not be created on layer_copy as its ancestor is a gprim.
        expected_path = "/RefCube/Cube2_01"
        self.assertFalse(stage.GetPrimAtPath(expected_path))
        with Usd.EditContext(stage, layer_copy):
            omni.kit.commands.execute("CopyPrim", path_from="/RefCube/Cube2", combine_layers=True)
            self.assertFalse(stage.GetPrimAtPath(expected_path))

        expected_path = "/Root/Cube2"
        self.assertFalse(stage.GetPrimAtPath(expected_path))
        with Usd.EditContext(stage, layer_copy):
            omni.kit.commands.execute(
                "CopyPrim", path_from="/RefCube/Cube2", path_to=expected_path, combine_layers=True
            )
            self.assertTrue(stage.GetPrimAtPath(expected_path))
            omni.kit.undo.undo()
            self.assertFalse(stage.GetPrimAtPath(expected_path))
            omni.kit.undo.redo()
            self.assertTrue(stage.GetPrimAtPath(expected_path))

    async def test_copy_prims(self):
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        stage = usd_context.get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)
        sublayer = Sdf.Layer.CreateAnonymous()
        root_layer = stage.GetRootLayer()
        root_layer.subLayerPaths.append(sublayer.identifier)

        with Usd.EditContext(stage, sublayer):
            omni.kit.commands.execute("CreatePrims", prim_types=["Sphere", "Cone", "Cube"])

        for combine_layers in [False, True]:
            for copy_to_introducing_layer in [False, True]:
                # Creates prims to sublayer to test copy to introducing layer.
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone")))
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube")))

                selected_paths_before = [
                    default_prim_path.AppendChild("Sphere").pathString,
                    default_prim_path.AppendChild("Cone").pathString,
                    default_prim_path.AppendChild("Cube").pathString,
                ]
                selection.set_selected_prim_paths(selected_paths_before, False)

                omni.kit.commands.execute(
                    "CopyPrims",
                    paths_from=selection.get_selected_prim_paths(),
                    combine_layers=combine_layers,
                    copy_to_introducing_layer=copy_to_introducing_layer,
                )

                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))

                # Copy to introducing layer only works if combine_layers is true
                if copy_to_introducing_layer:
                    target_layer = sublayer
                    false_layer = root_layer
                else:
                    target_layer = root_layer
                    false_layer = sublayer
                self.assertTrue(target_layer.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
                self.assertTrue(target_layer.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
                self.assertTrue(target_layer.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))
                self.assertFalse(false_layer.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
                self.assertFalse(false_layer.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
                self.assertFalse(false_layer.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))

                selected_paths_after = [
                    default_prim_path.AppendChild("Sphere_01").pathString,
                    default_prim_path.AppendChild("Cone_01").pathString,
                    default_prim_path.AppendChild("Cube_01").pathString,
                ]
                self.assertTrue(selection.get_selected_prim_paths() == selected_paths_after)

                omni.kit.undo.undo()

                self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
                self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
                self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))
                self.assertTrue(selection.get_selected_prim_paths() == selected_paths_before)

                omni.kit.undo.redo()

                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
                self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))
                self.assertTrue(selection.get_selected_prim_paths() == selected_paths_after)

                omni.kit.undo.undo()

    async def test_delete_prims_with_default_prim(self):
        """Test for OM-117571."""

        prim_path = Sdf.Path("/DefaultPrim")
        stage = omni.usd.get_context().get_stage()
        default_prim = stage.DefinePrim(prim_path, "Xform")
        stage.SetDefaultPrim(default_prim)

        omni.kit.commands.execute("DeletePrims", paths=[prim_path], destructive=False)
        self.assertFalse(stage.GetPrimAtPath(prim_path))

        omni.kit.undo.undo()
        self.assertTrue(stage.GetPrimAtPath(prim_path))
        self.assertEqual(stage.GetDefaultPrim().GetPath(), prim_path)

    async def test_delete_prims_with_multiple_sublayers(self):
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        session_layer = stage.GetSessionLayer()
        format = Sdf.FileFormat.FindByExtension(".usd")
        strong_layer = Sdf.Layer.New(format, "z:/fake-path/subfolder/test.usd")
        weak_layer = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(weak_layer.identifier)
        session_layer.subLayerPaths.append(strong_layer.identifier)

        test_prim_path = "/root/test"
        layer_list = [session_layer, strong_layer, root_layer, weak_layer]

        def delete_and_check(def_layer, current_layer, test_prim_path):
            has_prim_spec_before = not not current_layer.GetPrimAtPath(test_prim_path)
            with Usd.EditContext(stage, current_layer):
                omni.kit.commands.execute("DeletePrims", paths=[test_prim_path], destructive=False)
                usd_prim = stage.GetPrimAtPath(test_prim_path)
                if def_layer == current_layer or (
                    def_layer.anonymous and (not has_prim_spec_before or current_layer.anonymous)
                ):
                    self.assertFalse(usd_prim)
                else:
                    self.assertTrue(usd_prim)
                    self.assertFalse(usd_prim.IsActive())
                    def_prim_spec = def_layer.GetPrimAtPath(test_prim_path)
                    current_prim_spec = current_layer.GetPrimAtPath(test_prim_path)
                    if def_layer.anonymous:
                        self.assertFalse(def_prim_spec)
                        if not current_layer.anonymous and has_prim_spec_before:
                            self.assertTrue(current_prim_spec)
                            self.assertTrue(current_prim_spec.HasActive())
                            self.assertFalse(current_prim_spec.active)
                        else:
                            self.assertFalse(current_prim_spec)
                    else:
                        self.assertTrue(def_prim_spec)
                        self.assertFalse(def_prim_spec.HasActive())
                        self.assertTrue(current_prim_spec)
                        self.assertTrue(current_prim_spec.HasActive())
                        self.assertFalse(current_prim_spec.active)

            omni.kit.undo.undo()
            usd_prim = stage.GetPrimAtPath(test_prim_path)
            self.assertTrue(usd_prim)
            self.assertTrue(usd_prim.IsActive())
            prim_spec = def_layer.GetPrimAtPath(test_prim_path)
            self.assertTrue(prim_spec)
            self.assertFalse(prim_spec.HasActive())
            prim_spec = current_layer.GetPrimAtPath(test_prim_path)
            if has_prim_spec_before:
                self.assertTrue(prim_spec)
                self.assertFalse(prim_spec.HasActive())
            else:
                self.assertFalse(prim_spec)

        layer_list = [session_layer, strong_layer, root_layer, weak_layer]
        for def_layer in layer_list:
            with Usd.EditContext(stage, def_layer):
                stage.DefinePrim(test_prim_path, "Xform")

            for current_layer in layer_list:
                if current_layer != def_layer:
                    for has_delta_before in [False, True]:
                        if has_delta_before:
                            with Usd.EditContext(stage, current_layer):
                                stage.DefinePrim(test_prim_path)

                        delete_and_check(def_layer, current_layer, test_prim_path)
                        with Usd.EditContext(stage, current_layer):
                            stage.RemovePrim(test_prim_path)
                else:
                    delete_and_check(def_layer, current_layer, test_prim_path)

            with Usd.EditContext(stage, def_layer):
                stage.RemovePrim(test_prim_path)

    async def test_delete_prims(self):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        def check(assert_fn):
            nonlocal stage
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("Cylinder")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("Capsule")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("Camera")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("DistantLight")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("DomeLight")))
            assert_fn(stage.GetPrimAtPath(default_prim_path.AppendChild("SphereLight")))

        omni.kit.commands.execute(
            "CreatePrims",
            prim_types=[
                "Sphere",
                "Cube",
                "Cone",
                "Cylinder",
                "Capsule",
                "Camera",
                "DistantLight",
                "DomeLight",
                "SphereLight",
            ],
        )
        check(self.assertTrue)

        # give hydra a frame before deleting to catch up so it doesn't spew coding error about not finding prim
        await omni.kit.app.get_app().next_update_async()
        omni.kit.commands.execute(
            "DeletePrims",
            paths=[
                default_prim_path.AppendChild("Sphere").pathString,
                default_prim_path.AppendChild("Cube").pathString,
                default_prim_path.AppendChild("Cone").pathString,
                default_prim_path.AppendChild("Cylinder").pathString,
                default_prim_path.AppendChild("Capsule").pathString,
                default_prim_path.AppendChild("Camera").pathString,
                default_prim_path.AppendChild("DistantLight").pathString,
                default_prim_path.AppendChild("DomeLight").pathString,
                default_prim_path.AppendChild("SphereLight").pathString,
            ],
        )

        check(self.assertFalse)

        omni.kit.undo.undo()
        check(self.assertTrue)

        # give hydra a frame before deleting to catch up so it doesn't spew coding error about not finding prim
        await omni.kit.app.get_app().next_update_async()
        omni.kit.undo.redo()
        check(self.assertFalse)

    async def test_transform_instance_proxy(self):
        stage = omni.usd.get_context().get_stage()
        reference_layer = Sdf.Layer.CreateAnonymous()
        reference_stage = Usd.Stage.Open(reference_layer)
        default_prim = reference_stage.DefinePrim("/Root", "Xform")
        reference_stage.SetDefaultPrim(default_prim)
        instance_proxy_prim_path = "/Root/instance_proxy_cube"
        reference_stage.DefinePrim(instance_proxy_prim_path, "Cube")
        reference_prim = stage.DefinePrim("/Root")
        reference_prim.GetReferences().AddReference(reference_layer.identifier)

        reference_prim.SetInstanceable(True)
        reference_prim = stage.GetPrimAtPath(instance_proxy_prim_path)

        prim = stage.GetPrimAtPath(instance_proxy_prim_path)
        self.assertTrue(prim.IsInstanceProxy())
        omni.kit.commands.execute(
            "TransformMultiPrimsSRTCpp",
            count=1,
            paths=[str(instance_proxy_prim_path)],
            new_translations=[100.0, 100.0, 100.0],
            new_rotation_orders=[2, 1, 0],
            new_scales=[1.0, 1.0, 1.0],
            new_rotation_eulers=[0.0, 0.0, 0.0],
            old_translations=[0.0, 0.0, 0.0]
        )

        _, _, _, translation = omni.usd.get_local_transform_SRT(reference_prim)
        self.assertEqual(Gf.IsClose(translation, (0.0, 0.0, 0.0), 0.001), True, translation)
        stage.RemovePrim(instance_proxy_prim_path)

    async def test_transform_prim(self):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreatePrim", prim_type="Cube")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cube"))
        self.assertTrue(prim)

        xformable = UsdGeom.Xformable(prim)
        self.assertTrue(xformable.GetLocalTransformation() == Gf.Matrix4d(1.0))

        translate_mtx = Gf.Matrix4d()
        rotate_mtx = Gf.Matrix4d()
        scale_mtx = Gf.Matrix4d()

        translate_mtx.SetTranslate(Gf.Vec3d(1, 2, 3))
        rotation = Gf.Rotation(Gf.Vec3d(0, 1, 0), 60)
        rotate_mtx.SetRotate(rotation)
        scale_mtx = scale_mtx.SetScale(Gf.Vec3d(3, 2, 1))
        transform_matrix = scale_mtx * rotate_mtx * translate_mtx
        omni.kit.commands.execute(
            "TransformPrim", path=default_prim_path.AppendChild("Cube"), new_transform_matrix=transform_matrix
        )

        transform_matrix_1 = xformable.GetLocalTransformation()
        self.assertTrue(Gf.IsClose(transform_matrix, transform_matrix_1, 0.00001))

        translate_mtx.SetTranslate(Gf.Vec3d(3, 5, 2))
        rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), 60)
        rotate_mtx.SetRotate(rotation)
        scale_mtx = scale_mtx.SetScale(Gf.Vec3d(1, 3, 4))
        transform_matrix_2 = scale_mtx * rotate_mtx * translate_mtx
        omni.kit.commands.execute(
            "TransformPrim", path=default_prim_path.AppendChild("Cube"), new_transform_matrix=transform_matrix_2
        )

        transform_matrix_3 = xformable.GetLocalTransformation()
        self.assertTrue(Gf.IsClose(transform_matrix_2, transform_matrix_3, 0.00001))

        omni.kit.undo.undo()
        transform_matrix_4 = xformable.GetLocalTransformation()
        self.assertTrue(Gf.IsClose(transform_matrix_4, transform_matrix_1, 0.00001))

        omni.kit.undo.redo()
        transform_matrix_5 = xformable.GetLocalTransformation()
        self.assertTrue(Gf.IsClose(transform_matrix_3, transform_matrix_5, 0.00001))

        omni.kit.undo.undo()
        omni.kit.undo.undo()

        transform_matrix_6 = xformable.GetLocalTransformation()
        self.assertTrue(Gf.IsClose(transform_matrix_6, Gf.Matrix4d(1.0), 0.00001))

    async def _test_transform_prim_srt_impl(self, command: str):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreatePrim", prim_type="Cube", create_default_xform=False)
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cube"))
        self.assertTrue(prim)

        xformable = UsdGeom.Xformable(prim)
        self.assertTrue(xformable.GetLocalTransformation() == Gf.Matrix4d(1.0))

        translation = (1, 2, 3)
        rotation_euler = (0, 60, 0)
        scale = (3, 2, 1)
        omni.kit.commands.execute(
            command,
            path=default_prim_path.AppendChild("Cube").pathString,
            new_translation=translation,
            new_rotation_euler=rotation_euler,
            new_scale=scale,
        )

        scale_1, rotation_euler_1, _, translation_1 = omni.usd.get_local_transform_SRT(prim)
        self.assertTrue(
            Gf.IsClose(translation, translation_1, 0.00001), f"{translation} is not close to {translation_1}"
        )
        self.assertTrue(
            Gf.IsClose(rotation_euler, rotation_euler_1, 0.00001),
            f"{rotation_euler} is not close to {rotation_euler_1}",
        )
        self.assertTrue(Gf.IsClose(scale, scale_1, 0.00001), f"{scale} is not close to {scale_1}")

        translation_2 = (3, 5, 2)
        rotation_euler_2 = (60, 0, 0)
        scale_2 = (1, 3, 4)
        omni.kit.commands.execute(
            command,
            path=default_prim_path.AppendChild("Cube").pathString,
            new_translation=translation_2,
            new_rotation_euler=rotation_euler_2,
            new_scale=scale_2,
        )

        scale_3, rotation_euler_3, _, translation_3 = omni.usd.get_local_transform_SRT(prim)
        self.assertTrue(
            Gf.IsClose(translation_2, translation_3, 0.00001), f"{translation_2} is not close to {translation_3}"
        )
        self.assertTrue(
            Gf.IsClose(rotation_euler_2, rotation_euler_3, 0.00001),
            f"{rotation_euler_2} is not close to {rotation_euler_3}",
        )
        self.assertTrue(Gf.IsClose(scale_2, scale_3, 0.00001), f"{scale_2} is not close to {scale_3}")

        omni.kit.undo.undo()
        scale_4, rotation_euler_4, _, translation_4 = omni.usd.get_local_transform_SRT(prim)
        self.assertTrue(
            Gf.IsClose(translation_1, translation_4, 0.00001), f"{translation_1} is not close to {translation_4}"
        )
        self.assertTrue(
            Gf.IsClose(rotation_euler_1, rotation_euler_4, 0.00001),
            f"{rotation_euler_1} is not close to {rotation_euler_4}",
        )
        self.assertTrue(Gf.IsClose(scale_1, scale_4, 0.00001), f"{scale_1} is not close to {scale_4}")

        omni.kit.undo.redo()
        scale_5, rotation_euler_5, _, translation_5 = omni.usd.get_local_transform_SRT(prim)
        self.assertTrue(
            Gf.IsClose(translation_3, translation_5, 0.00001), f"{translation_3} is not close to {translation_5}"
        )
        self.assertTrue(
            Gf.IsClose(rotation_euler_3, rotation_euler_5, 0.00001),
            f"{rotation_euler_3} is not close to {rotation_euler_5}",
        )
        self.assertTrue(Gf.IsClose(scale_3, scale_5, 0.00001), f"{scale_3} is not close to {scale_5}")

        omni.kit.undo.undo()
        omni.kit.undo.undo()

        transform_matrix_6 = xformable.GetLocalTransformation()
        self.assertTrue(
            Gf.IsClose(transform_matrix_6, Gf.Matrix4d(1.0), 0.00001),
            f"{transform_matrix_6} is not close to {Gf.Matrix4d(1.0)}",
        )

        scale_6, rotation_euler_6, _, translation_6 = omni.usd.get_local_transform_SRT(prim)
        self.assertTrue(
            Gf.IsClose(Gf.Vec3d(0), translation_6, 0.00001), f"{Gf.Vec3d(0)} is not close to {translation_6}"
        )
        self.assertTrue(
            Gf.IsClose(Gf.Vec3f(0), rotation_euler_6, 0.00001), f"{Gf.Vec3f(0)} is not close to {rotation_euler_6}"
        )
        self.assertTrue(Gf.IsClose(Gf.Vec3f(1), scale_6, 0.00001), f"{Gf.Vec3f(1)} is not close to {scale_6}")

    async def test_transform_prim_srt(self):
        await self._test_transform_prim_srt_impl("TransformPrimSRT")

    async def test_transform_prim_srt_cpp(self):
        await self._test_transform_prim_srt_impl("TransformPrimSRTCpp")

    async def _test_transform_prim_srt_session_layer_impl(self, command: str):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        # create prim on root layer but override translate on session layer
        omni.kit.commands.execute("CreatePrim", prim_type="Cube")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cube"))
        self.assertTrue(prim)

        xformable = UsdGeom.Xformable(prim)
        self.assertTrue(xformable.GetLocalTransformation() == Gf.Matrix4d(1.0))

        translation = (0, 0, 0)
        xform_op = xformable.AddTranslateOp()
        xform_op.Set(translation)

        translation_1 = (1, 2, 3)
        session_layer = stage.GetSessionLayer()
        root_layer = stage.GetRootLayer()
        with Usd.EditContext(stage, session_layer):
            xform_op.Set(translation_1)

        translation_2 = (2, 3, 4)
        omni.kit.commands.execute(
            command,
            path=prim.GetPath().pathString,
            new_translation=translation_2,
        )

        t = xform_op.Get()
        self.assertTrue(Gf.IsClose(t, translation_2, 0.00001), f"{t} is not close to {translation_2}")

        session_attr_spec = session_layer.GetAttributeAtPath(xform_op.GetAttr().GetPath())
        t = session_attr_spec.default
        self.assertTrue(Gf.IsClose(t, translation_2, 0.00001), f"{t} is not close to {translation_2}")

        root_attr_spec = root_layer.GetAttributeAtPath(xform_op.GetAttr().GetPath())
        t = root_attr_spec.default
        self.assertTrue(Gf.IsClose(t, translation, 0.00001), f"{t} is not close to {translation}")

        # create prim on session layer and manipulate
        with Usd.EditContext(stage, session_layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Cube2")
            prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cube2"))
            self.assertTrue(prim)

            xformable = UsdGeom.Xformable(prim)
            self.assertTrue(xformable.GetLocalTransformation() == Gf.Matrix4d(1.0))

            xform_op = xformable.AddTranslateOp()
            xform_op.Set(translation)

            omni.kit.commands.execute(
                command,
                path=prim.GetPath().pathString,
                new_translation=translation_2,
            )

            t = xform_op.Get()
            self.assertTrue(Gf.IsClose(t, translation_2, 0.00001), f"{t} is not close to {translation_2}")

            session_attr_spec = session_layer.GetAttributeAtPath(xform_op.GetAttr().GetPath())
            t = session_attr_spec.default
            self.assertTrue(Gf.IsClose(t, translation_2, 0.00001), f"{t} is not close to {translation_2}")

            root_attr_spec = root_layer.GetAttributeAtPath(xform_op.GetAttr().GetPath())
            self.assertIsNone(root_attr_spec)

    async def test_transform_prim_srt_session_layer(self):
        await self._test_transform_prim_srt_session_layer_impl("TransformPrimSRT")

    async def test_transform_prim_srt_cpp_session_layer(self):
        await self._test_transform_prim_srt_session_layer_impl("TransformPrimSRTCpp")

    async def test_move_prim_without_destruction(self):
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        session_layer = stage.GetSessionLayer()
        format = Sdf.FileFormat.FindByExtension(".usd")
        strong_layer = Sdf.Layer.New(format, "z:/fake-path/subfolder/test.usd")
        weak_layer = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(weak_layer.identifier)
        session_layer.subLayerPaths.append(strong_layer.identifier)

        test_prim_path = "/root/test"
        test_prim_path_move_to = "/root/test2"
        layer_list = [session_layer, strong_layer, root_layer, weak_layer]

        def move_and_check(def_layer, current_layer, test_prim_path):
            has_prim_spec_before = not not current_layer.GetPrimAtPath(test_prim_path)
            with Usd.EditContext(stage, current_layer):
                omni.kit.commands.execute(
                    "MovePrim", path_from=test_prim_path, path_to=test_prim_path_move_to, destructive=False,
                    stage_or_context=stage
                )
                old_usd_prim = stage.GetPrimAtPath(test_prim_path)
                new_usd_prim = stage.GetPrimAtPath(test_prim_path_move_to)
                if def_layer == current_layer or (
                    def_layer.anonymous and (not has_prim_spec_before or current_layer.anonymous)
                ):
                    self.assertFalse(old_usd_prim)
                else:
                    old_prim_spec = current_layer.GetPrimAtPath(test_prim_path)
                    if def_layer.anonymous:
                        if not current_layer.anonymous and has_prim_spec_before:
                            self.assertTrue(old_prim_spec)
                            self.assertTrue(old_prim_spec.HasActive())
                            self.assertFalse(old_prim_spec.active)
                        else:
                            self.assertFalse(old_prim_spec)
                    else:
                        self.assertTrue(old_prim_spec)
                        self.assertTrue(old_prim_spec.HasActive())
                        self.assertFalse(old_prim_spec.active)
                self.assertTrue(new_usd_prim)

            omni.kit.undo.undo()
            old_usd_prim = stage.GetPrimAtPath(test_prim_path)
            new_usd_prim = stage.GetPrimAtPath(test_prim_path_move_to)
            self.assertTrue(old_usd_prim)
            self.assertTrue(old_usd_prim.IsActive())
            prim_spec = def_layer.GetPrimAtPath(test_prim_path)
            self.assertTrue(prim_spec)
            self.assertFalse(prim_spec.HasActive())
            prim_spec = current_layer.GetPrimAtPath(test_prim_path)
            if has_prim_spec_before:
                self.assertTrue(prim_spec)
                self.assertFalse(prim_spec.HasActive())
            else:
                self.assertFalse(prim_spec)
            self.assertFalse(new_usd_prim)

        layer_list = [session_layer, strong_layer, root_layer, weak_layer]
        for def_layer in layer_list:
            for current_layer in layer_list:
                with Usd.EditContext(stage, def_layer):
                    stage.DefinePrim(test_prim_path, "Xform")
                if current_layer != def_layer:
                    for has_delta_before in [False, True]:
                        if has_delta_before:
                            with Usd.EditContext(stage, current_layer):
                                stage.DefinePrim(test_prim_path)

                        move_and_check(def_layer, current_layer, test_prim_path)
                        with Usd.EditContext(stage, current_layer):
                            stage.RemovePrim(test_prim_path)
                            stage.RemovePrim(test_prim_path_move_to)
                else:
                    move_and_check(def_layer, current_layer, test_prim_path)
                    with Usd.EditContext(stage, current_layer):
                        stage.RemovePrim(test_prim_path)
                        stage.RemovePrim(test_prim_path_move_to)

            with Usd.EditContext(stage, def_layer):
                stage.RemovePrim(test_prim_path)
                stage.RemovePrim(test_prim_path_move_to)

    async def test_move_prim(self):
        async def test():
            stage = omni.usd.get_context().get_stage()
            default_prim_path = getStageDefaultPrimPath(stage)

            cube_path = default_prim_path.AppendChild("Cube")
            cube_new_path = default_prim_path.AppendChild("Cube_Renamed")
            cube_new_path2 = "/Cube"
            cube_translate = Gf.Vec3d(1, 0, 0)

            sphere_path = default_prim_path.AppendChild("Sphere")
            sphere_new_path = cube_new_path.AppendChild("Sphere_Moved")
            sphere_new_path2 = "/Sphere_02"
            sphere_translate = Gf.Vec3d(0, 1, 0)

            # /Stage/Cube
            omni.kit.commands.execute("CreatePrim", prim_type="Cube")
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)
            cube_xform_api = UsdGeom.XformCommonAPI(cube)
            cube_xform_api.SetTranslate(translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            sphere_xform_api = UsdGeom.XformCommonAPI(sphere)
            sphere_xform_api.SetTranslate(translation=sphere_translate)

            # Should raise a value error
            with self.assertRaises(ValueError):
                omni.kit.commands.execute(
                    "MovePrim", path_from=cube_path, path_to="123invalid", keep_world_transform=False,
                    stage_or_context=""
                )
            # OMPE-28550: MovePrim should raise a ValueError if the given stage is invalid
            invalid_stage = Usd.Stage.CreateInMemory()
            with self.assertRaises(ValueError):
                omni.kit.commands.execute(
                    "MovePrim", path_from=cube_path, path_to="123invalid", keep_world_transform=False,
                    stage_or_context=invalid_stage
                )

            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.commands.execute(
                "MovePrim", path_from=cube_path, path_to=cube_new_path, keep_world_transform=False,
                stage_or_context=omni.usd.get_context()
            )
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            cube = stage.GetPrimAtPath(cube_new_path)
            self.assertTrue(cube)

            # Cannot move gprim under a gprim
            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.commands.execute(
                "MovePrim", path_from=sphere_path, path_to=sphere_new_path, keep_world_transform=False
            )
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertFalse(sphere)
            omni.kit.undo.undo()

            # Create xform and move sphere under a xform
            # /Stage/Cube_Renamed
            # /Stage/root/Sphere
            xform_path = default_prim_path.AppendChild("root")
            xform = UsdGeom.Xform.Define(stage, xform_path)
            self.assertTrue(xform)
            xform_api = UsdGeom.XformCommonAPI(xform)
            xform_api.SetTranslate(translation=cube_translate)

            sphere_new_path = xform_path.AppendChild("Sphere")
            omni.kit.commands.execute(
                "MovePrim", path_from=sphere_path, path_to=sphere_new_path, keep_world_transform=False
            )
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)
            sphere_world_mtx = omni.usd.get_world_transform_matrix(sphere)
            self.assertTrue(sphere_world_mtx.GetRow3(3) == sphere_translate + cube_translate)

            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.undo.undo()

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.undo.undo()
            self.assertTrue(stage.GetPrimAtPath(cube_path))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))

            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.undo.redo()
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            self.assertTrue(stage.GetPrimAtPath(cube_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))

            # Test keep_world_transform
            # /Stage/Cube_Renamed
            # /Stage/Cube_Renamed/Sphere
            omni.kit.commands.execute(
                "MovePrim", path_from=sphere_path, path_to=sphere_new_path, keep_world_transform=True
            )
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)

            sphere_world_mtx = omni.usd.get_world_transform_matrix(sphere)
            self.assertTrue(sphere_world_mtx.GetRow3(3) == sphere_translate)

            omni.kit.undo.undo()

            # Test batched move
            batch_move = {}
            batch_move[cube_new_path] = cube_new_path2
            batch_move[sphere_path] = sphere_new_path2

            children_order = str(stage.GetPrimAtPath(default_prim_path).GetChildren())
            # /Stage
            # /Cube
            # /Sphere
            omni.kit.commands.execute("MovePrims", paths_to_move=batch_move, stage_or_context=omni.usd.get_context())
            omni.kit.undo.undo()
            omni.kit.commands.execute("MovePrims", paths_to_move=batch_move, stage_or_context=stage)
            omni.kit.undo.undo()
            omni.kit.commands.execute("MovePrims", paths_to_move=batch_move, stage_or_context="")
            self.assertTrue(stage.GetPrimAtPath(cube_new_path2))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_new_path2))

            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.undo.undo()
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            self.assertTrue(stage.GetPrimAtPath(cube_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(str(stage.GetPrimAtPath(default_prim_path).GetChildren()) == children_order)  # Check order

            # /Stage
            # /Cube
            # /Sphere
            omni.kit.undo.redo()
            self.assertTrue(stage.GetPrimAtPath(cube_new_path2))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_new_path2))

            # Tests for https://nvidia-omniverse.atlassian.net/browse/OM-21961
            # Create prim /reference and it references /cube
            reference_prim = stage.DefinePrim("/reference")
            reference_prim.GetReferences().AddInternalReference(cube_new_path2)

            omni.kit.commands.execute(
                "MovePrim", path_from=cube_new_path2, path_to=cube_new_path, keep_world_transform=False
            )
            self.assertFalse(stage.GetPrimAtPath(cube_new_path2))
            cube = stage.GetPrimAtPath(cube_new_path)
            self.assertTrue(cube)

            def get_reference_prims(prim):
                prim_paths = []
                for prim_spec in prim.GetPrimStack():
                    items = prim_spec.referenceList.prependedItems
                    for item in items:
                        if item.primPath:
                            prim_paths.append(item.primPath)

                return prim_paths

            prim_paths = get_reference_prims(reference_prim)
            # After move, the reference path should be changed also.
            self.assertTrue(len(prim_paths) == 1 and prim_paths[0] == cube_new_path)

            # /Stage
            # /Cube
            # /Sphere
            omni.kit.undo.undo()
            self.assertTrue(stage.GetPrimAtPath(cube_new_path2))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_new_path2))

            prim_paths = get_reference_prims(reference_prim)
            # After undo, the reference path should be changed back.
            self.assertTrue(len(prim_paths) == 1 and prim_paths[0] == cube_new_path2)

            # Create prim /reference2 and it references "../test/test.usd"</sphere>
            reference_prim2 = stage.DefinePrim("/reference2")
            # Add a non-existent external reference
            reference_prim2.GetReferences().AddReference("../test/test.usd", sphere_new_path2)

            omni.kit.commands.execute(
                "MovePrim", path_from=sphere_new_path2, path_to=sphere_new_path, keep_world_transform=False
            )
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path2))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)

            def get_reference_prims(prim):
                prim_paths = []
                for prim_spec in prim.GetPrimStack():
                    items = prim_spec.referenceList.prependedItems
                    for item in items:
                        if item.primPath:
                            prim_paths.append(item.primPath)

                return prim_paths

            prim_paths = get_reference_prims(reference_prim2)
            # After move, the reference path should not be changed since it points to an external USD
            self.assertTrue(len(prim_paths) == 1 and prim_paths[0] == sphere_new_path2)

            omni.kit.undo.undo()
            prim_paths = get_reference_prims(reference_prim2)
            # After undo, the reference path should not be changed also.
            self.assertTrue(len(prim_paths) == 1 and prim_paths[0] == sphere_new_path2)

        carb.log_info("Test Move/Rename")
        await test()

    async def test_rename_prim(self):
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        session_layer = stage.GetSessionLayer()
        format = Sdf.FileFormat.FindByExtension(".usd")
        strong_layer = Sdf.Layer.New(format, "z:/fake-path/subfolder/test.usd")
        weak_layer = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(weak_layer.identifier)
        session_layer.subLayerPaths.append(strong_layer.identifier)

        test_prim_path = "/root/test"
        test_new_name = "test2ÄßÖÜäöü测试"
        test_prim_path_move_to = Sdf.Path(test_prim_path).GetParentPath().AppendChild(test_new_name)
        layer_list = [session_layer, strong_layer, root_layer, weak_layer]

        def move_and_check(def_layer, current_layer, test_prim_path):
            has_prim_spec_before = not not current_layer.GetPrimAtPath(test_prim_path)
            with Usd.EditContext(stage, current_layer):
                omni.kit.commands.execute(
                    "RenamePrimCommand", prim_path=test_prim_path, new_name=test_new_name)
                old_usd_prim = stage.GetPrimAtPath(test_prim_path)
                new_usd_prim = stage.GetPrimAtPath(test_prim_path_move_to)
                if def_layer == current_layer or (
                    def_layer.anonymous and (not has_prim_spec_before or current_layer.anonymous)
                ):
                    self.assertFalse(old_usd_prim)
                else:
                    old_prim_spec = current_layer.GetPrimAtPath(test_prim_path)
                    if def_layer.anonymous:
                        if not current_layer.anonymous and has_prim_spec_before:
                            self.assertTrue(old_prim_spec)
                            self.assertTrue(old_prim_spec.HasActive())
                            self.assertFalse(old_prim_spec.active)
                        else:
                            self.assertFalse(old_prim_spec)
                    else:
                        self.assertTrue(old_prim_spec)
                        self.assertTrue(old_prim_spec.HasActive())
                        self.assertFalse(old_prim_spec.active)
                self.assertTrue(new_usd_prim)

            omni.kit.undo.undo()
            old_usd_prim = stage.GetPrimAtPath(test_prim_path)
            new_usd_prim = stage.GetPrimAtPath(test_prim_path_move_to)
            self.assertTrue(old_usd_prim)
            self.assertTrue(old_usd_prim.IsActive())
            prim_spec = def_layer.GetPrimAtPath(test_prim_path)
            self.assertTrue(prim_spec)
            self.assertFalse(prim_spec.HasActive())
            prim_spec = current_layer.GetPrimAtPath(test_prim_path)
            if has_prim_spec_before:
                self.assertTrue(prim_spec)
                self.assertFalse(prim_spec.HasActive())
            else:
                self.assertFalse(prim_spec)
            self.assertFalse(new_usd_prim)

        layer_list = [session_layer, strong_layer, root_layer, weak_layer]
        for def_layer in layer_list:
            for current_layer in layer_list:
                with Usd.EditContext(stage, def_layer):
                    stage.DefinePrim(test_prim_path, "Xform")
                if current_layer != def_layer:
                    for has_delta_before in [False, True]:
                        if has_delta_before:
                            with Usd.EditContext(stage, current_layer):
                                stage.DefinePrim(test_prim_path)

                        move_and_check(def_layer, current_layer, test_prim_path)
                        with Usd.EditContext(stage, current_layer):
                            stage.RemovePrim(test_prim_path)
                            stage.RemovePrim(test_prim_path_move_to)
                else:
                    move_and_check(def_layer, current_layer, test_prim_path)
                    with Usd.EditContext(stage, current_layer):
                        stage.RemovePrim(test_prim_path)
                        stage.RemovePrim(test_prim_path_move_to)

            with Usd.EditContext(stage, def_layer):
                stage.RemovePrim(test_prim_path)
                stage.RemovePrim(test_prim_path_move_to)

    async def test_move_non_xformable_prim(self):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])

        cube_path = default_prim_path.AppendChild("Cube")
        xform_path = default_prim_path.AppendChild("Xform")
        scope_path = default_prim_path.AppendChild("Scope")

        cube_translate = Gf.Vec3d(1, 0, 0)
        xform_translate = Gf.Vec3d(1, 1, 1)

        cube = UsdGeom.Cube.Define(stage, cube_path)
        xform = UsdGeom.Xform.Define(stage, xform_path)
        scope = UsdGeom.Scope.Define(stage, scope_path)

        cube_xform_api = UsdGeom.XformCommonAPI(cube.GetPrim())
        cube_xform_api.SetTranslate(translation=cube_translate)

        xform_xform_api = UsdGeom.XformCommonAPI(xform.GetPrim())
        xform_xform_api.SetTranslate(translation=xform_translate)

        cube_original_bound = bbox_cache.ComputeWorldBound(cube.GetPrim())

        def check_cube_bound(cube_path):
            nonlocal cube_original_bound
            nonlocal bbox_cache
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)

            bbox_cache.Clear()
            cube_bound = bbox_cache.ComputeWorldBound(cube.GetPrim())
            self.assertTrue(cube_bound == cube_original_bound)

        # Move /Scope tp /Xform/Scope
        scope_under_xform_path = xform_path.AppendChild("Scope")
        omni.kit.commands.execute(
            "MovePrim", path_from=scope_path, path_to=scope_under_xform_path, keep_world_transform=True
        )

        # Move /Cube to /Xform/Scope/Cube
        cube_under_scope_path = scope_under_xform_path.AppendChild("Cube")
        omni.kit.commands.execute(
            "MovePrim", path_from=cube_path, path_to=cube_under_scope_path, keep_world_transform=True
        )

        check_cube_bound(cube_under_scope_path)

        # Move /Xform/Scope to /Scope (didn't move Cube directly but its transform should stay the same)
        omni.kit.commands.execute(
            "MovePrim", path_from=scope_under_xform_path, path_to=scope_path, keep_world_transform=True
        )

        cube_under_scope_path = scope_path.AppendChild("Cube")
        check_cube_bound(cube_under_scope_path)

        omni.kit.undo.undo()

        cube_under_scope_path = scope_under_xform_path.AppendChild("Cube")
        check_cube_bound(cube_under_scope_path)

        omni.kit.undo.undo()
        check_cube_bound(cube_path)

        omni.kit.undo.redo()
        check_cube_bound(cube_under_scope_path)

        omni.kit.undo.redo()
        cube_under_scope_path = scope_path.AppendChild("Cube")
        check_cube_bound(cube_under_scope_path)

    async def test_toggle_visibility_selected(self):
        timeline = omni.timeline.get_timeline_interface()
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        stage = usd_context.get_stage()
        default_prim_path = Sdf.Path("/root")
        root_layer = stage.GetRootLayer()

        with Usd.EditContext(stage, root_layer):
            stage.DefinePrim("/root", "Xform")
            stage.DefinePrim("/root/Cube", "Cube")
            stage.DefinePrim("/root/Sphere", "Sphere")
            stage.DefinePrim("/root/Cone", "Cone")

        def test_visibility(paths, visible):
            for path in paths:
                prim = stage.GetPrimAtPath(path)
                imageable = UsdGeom.Imageable(prim)
                visibilityAttr = imageable.GetVisibilityAttr()
                timeSampled = visibilityAttr.GetNumTimeSamples() > 1
                currTime = timeline.get_current_time()
                if timeSampled:
                    self._currTimeCode = currTime * stage.GetTimeCodesPerSecond()
                else:
                    self._currTimeCode = Usd.TimeCode.Default()
                visibility = imageable.ComputeVisibility(self._currTimeCode)
                if visible:
                    self.assertFalse(visibility == UsdGeom.Tokens.invisible)
                else:
                    self.assertTrue(visibility == UsdGeom.Tokens.invisible)

        # if nothing selected, visiblity should not change.
        selection.clear_selected_prim_paths()
        paths = selection.get_selected_prim_paths()
        test_visibility(paths, True)
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths)
        paths = selection.get_selected_prim_paths()
        test_visibility(paths, True)
        self.assertTrue(len(paths) == 0)

        # select all the paths and there should be 3 selected.
        paths = [
            default_prim_path.AppendChild("Cube").pathString,
            default_prim_path.AppendChild("Sphere").pathString,
            default_prim_path.AppendChild("Cone").pathString
        ]
        selection.set_selected_prim_paths(paths, False)
        self.assertEqual(len(paths), 3)
        # toggle and test they are all hidden
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths)
        test_visibility(paths, False)
        # toggle again and test they are all visible again
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths)
        test_visibility(paths, True)
        omni.kit.undo.undo()
        test_visibility(paths, False)
        omni.kit.undo.redo()
        test_visibility(paths, True)

        # select one and it should be visible
        selection.set_selected_prim_paths([default_prim_path.AppendChild("Cube").pathString], False)
        test_visibility(paths, True)

        # toggle and test they are all hidden
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths)
        test_visibility(paths, False)
        # toggle again and test they are all visible again
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths)
        test_visibility(paths, True)

        omni.kit.undo.undo()
        test_visibility(paths, False)
        omni.kit.undo.redo()
        test_visibility(paths, True)

        # Select one of them and toggle visiblity
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths[0:1])
        test_visibility(paths[0:1], False)

        # Toggle all of them again should keep all prims visible as it toggles visibility according to the specified value
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths, visible=True)
        test_visibility(paths, True)

        # Select one of them and toggle visiblity
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths[0:1])
        test_visibility(paths[0:1], False)
        # Toggle all of them again should keep all prims invisible as it toggles visibility according to the specified value
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths, visible=False)
        test_visibility(paths, False)

        # Toggle all of them back to visible.
        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths, visible=True)
        test_visibility(paths, True)

        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=paths)
        test_visibility(paths, False)

        omni.kit.commands.execute("ToggleVisibilitySelectedPrims", selected_paths=["/root/Cube"])
        test_visibility(["/root/Cube"], True)
        test_visibility(["/root"], True)
        omni.kit.undo.undo()
        test_visibility(paths, False)

    async def test_set_material_strength(self):
        carb.log_info("Test SetMaterialStrengthCommand")
        stage = omni.usd.get_context().get_stage()

        mat = UsdShade.Material.Define(stage, "/mat")
        prim = stage.OverridePrim("/prim")

        omni.kit.commands.execute(
            "BindMaterial",
            prim_path=prim.GetPath(),
            material_path=mat.GetPrim().GetPath(),
            strength=UsdShade.Tokens.strongerThanDescendants,
        )
        binding_api = UsdShade.MaterialBindingAPI(prim)
        mat, rel = binding_api.ComputeBoundMaterial()

        self.assertTrue(mat)
        self.assertTrue(rel)

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.strongerThanDescendants)

        omni.kit.commands.execute("SetMaterialStrength", rel=rel, strength=UsdShade.Tokens.weakerThanDescendants)

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.weakerThanDescendants)

        omni.kit.undo.undo()

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.strongerThanDescendants)

        omni.kit.undo.redo()

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.weakerThanDescendants)

        omni.kit.commands.execute("SetMaterialStrength", rel=rel, strength=UsdShade.Tokens.strongerThanDescendants)

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.strongerThanDescendants)

        omni.kit.undo.undo()

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.weakerThanDescendants)

        omni.kit.undo.redo()

        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
        self.assertTrue(strength == UsdShade.Tokens.strongerThanDescendants)

    async def test_collection_material_assignment(self):
        stage = omni.usd.get_context().get_stage()

        mat = UsdShade.Material.Define(stage, "/mat")
        prim = stage.DefinePrim("/prim")
        # https://github.com/PixarAnimationStudios/USD/commit/e9d1109d41c1a8edde80cf3c3a0154fc06a6ff3c
        if hasattr(Usd.CollectionAPI, 'Apply'):
            test_collection = Usd.CollectionAPI.Apply(prim, "test_collection")
        else:
            test_collection = Usd.CollectionAPI.ApplyCollection(prim, "test_collection")

        coll_path = test_collection.GetCollectionPath()

        omni.kit.commands.execute(
            "BindMaterialCommand",
            prim_path=coll_path,
            material_path=mat.GetPrim().GetPath(),
            strength=UsdShade.Tokens.strongerThanDescendants,
        )
        material = None
        relationship = None
        binding_api = UsdShade.MaterialBindingAPI(prim)
        all_bindings = binding_api.GetCollectionBindings()
        for b in all_bindings:
            curr_collection = b.GetCollection()
            if curr_collection.GetName() == "test_collection":
                relationship = b.GetBindingRel()
                material = b.GetMaterial()

        self.assertTrue(mat.GetPath() == material.GetPath())
        self.assertTrue(relationship)

    async def test_multiple_collections_single_prim(self):
        """
        check assigning different materials to different collections on a single prim
        """
        stage = omni.usd.get_context().get_stage()

        mat1 = UsdShade.Material.Define(stage, "/mat1")
        mat2 = UsdShade.Material.Define(stage, "/mat2")
        materials = [mat1.GetPath(), mat2.GetPath()]
        prim = stage.DefinePrim("/prim")
        # https://github.com/PixarAnimationStudios/USD/commit/e9d1109d41c1a8edde80cf3c3a0154fc06a6ff3c
        if hasattr(Usd.CollectionAPI, 'Apply'):
            test_collection1 = Usd.CollectionAPI.Apply(prim, "test_collection1")
            test_collection2 = Usd.CollectionAPI.Apply(prim, "test_collection2")
        else:
            test_collection1 = Usd.CollectionAPI.ApplyCollection(prim, "test_collection1")
            test_collection2 = Usd.CollectionAPI.ApplyCollection(prim, "test_collection2")

        collections = [test_collection1.GetCollectionPath(), test_collection2.GetCollectionPath()]
        coll_path1 = test_collection1.GetCollectionPath()
        coll_path2 = test_collection2.GetCollectionPath()
        omni.kit.commands.execute(
            "BindMaterialCommand",
            prim_path=coll_path1,
            material_path=mat1.GetPrim().GetPath(),
            strength=UsdShade.Tokens.strongerThanDescendants,
        )
        omni.kit.commands.execute(
            "BindMaterialCommand",
            prim_path=coll_path2,
            material_path=mat2.GetPrim().GetPath(),
            strength=UsdShade.Tokens.strongerThanDescendants,
        )

        binding_api = UsdShade.MaterialBindingAPI(prim)
        all_bindings = binding_api.GetCollectionBindings()
        self.assertTrue(len(all_bindings) == 2)
        for b in all_bindings:
            curr_collection = b.GetCollection()
            self.assertTrue(curr_collection.GetCollectionPath() in collections)
            material = b.GetMaterial()
            self.assertTrue(material.GetPath() in materials)

    async def test_set_metadata(self):
        carb.log_info("Test ChangeMetadataInPrimsCommand")
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreatePrims", prim_types=["Sphere", "Cone", "Cube"])
        prim_paths = [
            default_prim_path.AppendChild("Cube"),
            default_prim_path.AppendChild("Sphere"),
            default_prim_path.AppendChild("Cone"),
        ]

        sphere_path = default_prim_path.AppendChild("Sphere")
        cone_path = default_prim_path.AppendChild("Cone")
        cube_path = default_prim_path.AppendChild("Cube")

        sphere_prim = stage.GetPrimAtPath(sphere_path)
        cone_prim = stage.GetPrimAtPath(cone_path)
        cube_prim = stage.GetPrimAtPath(cube_path)

        sphere_prim_model_api = Usd.ModelAPI(sphere_prim)
        cone_prim_model_api = Usd.ModelAPI(cone_prim)
        cube_prim_model_api = Usd.ModelAPI(cube_prim)

        sphere_kind = Kind.Tokens.component
        cone_kind = Kind.Tokens.subcomponent
        cube_kind = Kind.Tokens.component

        all_kind = Kind.Tokens.assembly

        omni.kit.commands.execute("ChangeMetadataInPrims", prim_paths=[sphere_path], key="kind", value=sphere_kind)
        omni.kit.commands.execute("ChangeMetadataInPrims", prim_paths=[cone_path], key="kind", value=cone_kind)
        omni.kit.commands.execute("ChangeMetadataInPrims", prim_paths=[cube_path], key="kind", value=cube_kind)

        self.assertTrue(sphere_prim_model_api.GetKind() == sphere_kind)
        self.assertTrue(cone_prim_model_api.GetKind() == cone_kind)
        self.assertTrue(cube_prim_model_api.GetKind() == cube_kind)

        omni.kit.commands.execute(
            "ChangeMetadataInPrims", prim_paths=[sphere_path, cone_path, cube_path], key="kind", value=all_kind
        )

        self.assertTrue(sphere_prim_model_api.GetKind() == all_kind)
        self.assertTrue(cone_prim_model_api.GetKind() == all_kind)
        self.assertTrue(cube_prim_model_api.GetKind() == all_kind)

        omni.kit.undo.undo()

        self.assertTrue(sphere_prim_model_api.GetKind() == sphere_kind)
        self.assertTrue(cone_prim_model_api.GetKind() == cone_kind)
        self.assertTrue(cube_prim_model_api.GetKind() == cube_kind)

        omni.kit.undo.redo()

        self.assertTrue(sphere_prim_model_api.GetKind() == all_kind)
        self.assertTrue(cone_prim_model_api.GetKind() == all_kind)
        self.assertTrue(cube_prim_model_api.GetKind() == all_kind)

    async def test_change_property(self):
        stage = omni.usd.get_context().get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreatePrim", prim_type="Cube")

        cube_path = default_prim_path.AppendChild("Cube")
        cube = stage.GetPrimAtPath(cube_path)
        self.assertTrue(cube is not None)

        size_attr = cube.GetAttribute("size")
        self.assertTrue(size_attr.Get() == 2.0)

        # test changing exisitng attr
        size_attr_path = cube_path.AppendProperty("size")
        args = {"prop_path": size_attr_path, "value": 10.0, "prev": None, "timecode": Usd.TimeCode.Default()}
        omni.kit.commands.execute("ChangeProperty", **args)

        self.assertTrue(size_attr.Get() == 10.0)

        omni.kit.undo.undo()
        self.assertTrue(size_attr.Get() == 2.0)

        omni.kit.undo.redo()
        self.assertTrue(size_attr.Get() == 10.0)

        # test clearing value
        args["value"] = None
        omni.kit.commands.execute("ChangeProperty", **args)

        self.assertTrue(not size_attr.HasAuthoredValue())

        omni.kit.undo.undo()
        self.assertTrue(size_attr.Get() == 10.0)

        omni.kit.undo.redo()
        self.assertTrue(not size_attr.HasAuthoredValue())

        # test changing non-exisitng attr
        my_attr_path = cube_path.AppendProperty("not_exist")
        args = {
            "prop_path": my_attr_path,
            "value": True,
            "prev": None,
            "timecode": Usd.TimeCode.Default(),
            "type_to_create_if_not_exist": Sdf.ValueTypeNames.Bool,
        }
        omni.kit.commands.execute("ChangeProperty", **args)

        my_attr = cube.GetAttribute("not_exist")
        self.assertTrue(my_attr is not None)
        self.assertTrue(my_attr.Get() == True)

        omni.kit.undo.undo()
        my_attr = cube.GetAttribute("not_exist")
        self.assertFalse(my_attr.IsValid())

        omni.kit.undo.redo()
        my_attr = cube.GetAttribute("not_exist")
        self.assertTrue(my_attr.IsValid())
        self.assertTrue(my_attr.Get() == True)

        # test changing non-existing attribute that does not get created
        fake_attr_path = cube_path.AppendProperty("another_fake")
        omni.kit.commands.execute("ChangeProperty", prop_path=fake_attr_path, value=0, prev=1)
        self.assertFalse(cube.GetAttribute("another_fake").IsValid())

        omni.kit.undo.undo()
        self.assertFalse(cube.GetAttribute("another_fake").IsValid())

        omni.kit.undo.redo()
        self.assertFalse(cube.GetAttribute("another_fake").IsValid())

    async def test_relationship_target(self):
        stage = omni.usd.get_context().get_stage()
        xform = UsdGeom.Xform.Define(stage, "/Xform")
        xform_rel = UsdGeom.Xform.Define(stage, "/XformRel")
        imageable = UsdGeom.Imageable(xform.GetPrim())
        rel = imageable.GetProxyPrimRel()

        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=xform_rel.GetPrim().GetPath())
        targets = rel.GetTargets()
        self.assertTrue(targets == [xform_rel.GetPrim().GetPath()])

        omni.kit.undo.undo()
        targets = rel.GetTargets()
        self.assertTrue(targets == [])

        omni.kit.undo.redo()
        targets = rel.GetTargets()
        self.assertTrue(targets == [xform_rel.GetPrim().GetPath()])

        omni.kit.commands.execute("RemoveRelationshipTarget", relationship=rel, target=xform_rel.GetPrim().GetPath())
        targets = rel.GetTargets()
        self.assertTrue(targets == [])

        omni.kit.undo.undo()
        targets = rel.GetTargets()
        self.assertTrue(targets == [xform_rel.GetPrim().GetPath()])

        omni.kit.undo.redo()
        targets = rel.GetTargets()
        self.assertTrue(targets == [])

    async def test_group_prims(self):
        async def test():
            stage = omni.usd.get_context().get_stage()
            default_prim_path = getStageDefaultPrimPath(stage)

            cube_path = default_prim_path.AppendChild("Cube")
            cube_translate = Gf.Vec3d(100, 0, 0)

            sphere_path = default_prim_path.AppendChild("Sphere")
            sphere_translate = Gf.Vec3d(0, 100, 0)

            cylinder_xform_path = default_prim_path.AppendChild("CylinderXform")
            cylinder_xform_translate = Gf.Vec3d(0, 0, 100)

            cylinder_path = cylinder_xform_path.AppendChild("Cylinder")
            cylinder_translate = Gf.Vec3d(0, 0, 100)

            scope_path = default_prim_path.AppendChild("Scope")

            # /Stage/Cube
            omni.kit.commands.execute("CreatePrim", prim_type="Cube")
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)
            cube_xform_api = UsdGeom.XformCommonAPI(cube)
            cube_xform_api.SetTranslate(translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            sphere_xform_api = UsdGeom.XformCommonAPI(sphere)
            sphere_xform_api.SetTranslate(translation=sphere_translate)

            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            prim = UsdGeom.Xform.Define(stage, cylinder_xform_path)
            cylinder_xform = prim.GetPrim()

            prim = UsdGeom.Cylinder.Define(stage, cylinder_path)
            cylinder = prim.GetPrim()

            cylinder_xform_api = UsdGeom.XformCommonAPI(cylinder_xform)
            cylinder_xform_api.SetTranslate(translation=cylinder_xform_translate)

            cylinder_api = UsdGeom.XformCommonAPI(cylinder)
            cylinder_api.SetTranslate(translation=cylinder_translate)


            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            # /Stage/Sceope
            # Non xformable prim
            omni.kit.commands.execute("CreatePrim", prim_type="Scope")

            # /Stage/Group/Cube
            # /Stage/Group/Sphere
            # /Stage/Group/Cylinder
            # /Stage/Group/Scope
            omni.kit.commands.execute("GroupPrims", prim_paths=[cube_path, sphere_path, cylinder_path, scope_path])
            group_prim_path = default_prim_path.AppendElementString("Group")
            group_prim = stage.GetPrimAtPath(group_prim_path)
            xform_vectors = UsdGeom.XformCommonAPI(group_prim).GetXformVectors(Usd.TimeCode.Default())
            _, _, _, pivot, _ = xform_vectors
            # Pivot is the center of the bound box
            self.assertEqual(pivot, Gf.Vec3f(50, 50, 100))
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_path))
            self.assertFalse(stage.GetPrimAtPath(scope_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_xform_path))
            cube_new_path = default_prim_path.AppendPath("Group/Cube")
            sphere_new_path = default_prim_path.AppendPath("Group/Sphere")
            cylinder_new_path = default_prim_path.AppendPath("Group/Cylinder")
            scope_new_path = default_prim_path.AppendPath("Group/Scope")
            cube = stage.GetPrimAtPath(cube_new_path)
            self.assertTrue(cube)
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)
            cylinder = stage.GetPrimAtPath(cylinder_new_path)
            self.assertTrue(cylinder)
            scope = stage.GetPrimAtPath(scope_new_path)
            self.assertTrue(scope)

            sphere_world_mtx = omni.usd.get_world_transform_matrix(sphere)
            self.assertTrue(sphere_world_mtx.GetRow3(3) == sphere_translate)

            cube_world_mtx = omni.usd.get_world_transform_matrix(cube)
            self.assertTrue(cube_world_mtx.GetRow3(3) == cube_translate)

            cylinder_world_mtx = omni.usd.get_world_transform_matrix(cylinder)
            self.assertTrue(cylinder_world_mtx.GetRow3(3) == cylinder_xform_translate + cylinder_translate)

            omni.kit.undo.undo()

            self.assertTrue(stage.GetPrimAtPath(cube_path))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_new_path))
            self.assertTrue(stage.GetPrimAtPath(scope_path))
            self.assertFalse(stage.GetPrimAtPath(scope_new_path))

            omni.kit.undo.redo()
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            self.assertTrue(stage.GetPrimAtPath(cube_new_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_new_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_new_path))
            self.assertFalse(stage.GetPrimAtPath(scope_path))
            self.assertTrue(stage.GetPrimAtPath(scope_new_path))

        await test()

    async def test_ungroup_prims(self):
        async def test():
            stage = omni.usd.get_context().get_stage()
            default_prim_path = getStageDefaultPrimPath(stage)

            cube_path = default_prim_path.AppendChild("Cube")
            cube_translate = Gf.Vec3d(100, 0, 0)

            sphere_path = default_prim_path.AppendChild("Sphere")
            sphere_translate = Gf.Vec3d(0, 100, 0)

            cylinder_xform_path = default_prim_path.AppendChild("CylinderXform")
            cylinder_xform_translate = Gf.Vec3d(0, 0, 100)

            cylinder_path = cylinder_xform_path.AppendChild("Cylinder")
            cylinder_translate = Gf.Vec3d(0, 0, 100)

            scope_path = default_prim_path.AppendChild("Scope")

            # /Stage/Cube
            omni.kit.commands.execute("CreatePrim", prim_type="Cube")
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)
            cube_xform_api = UsdGeom.XformCommonAPI(cube)
            cube_xform_api.SetTranslate(translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            sphere_xform_api = UsdGeom.XformCommonAPI(sphere)
            sphere_xform_api.SetTranslate(translation=sphere_translate)

            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            prim = UsdGeom.Xform.Define(stage, cylinder_xform_path)
            cylinder_xform = prim.GetPrim()

            prim = UsdGeom.Cylinder.Define(stage, cylinder_path)
            cylinder = prim.GetPrim()

            cylinder_xform_api = UsdGeom.XformCommonAPI(cylinder_xform)
            cylinder_xform_api.SetTranslate(translation=cylinder_xform_translate)

            cylinder_api = UsdGeom.XformCommonAPI(cylinder)
            cylinder_api.SetTranslate(translation=cylinder_translate)


            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            # /Stage/Scope
            # Non xformable prim
            omni.kit.commands.execute("CreatePrim", prim_type="Scope")

            # /Stage/Group/Cube
            # /Stage/Group/Sphere
            # /Stage/Group/Cylinder
            # /Stage/Group/Scope
            omni.kit.commands.execute("GroupPrims", prim_paths=[cube_path, sphere_path, cylinder_path, scope_path])
            group_prim_path = default_prim_path.AppendElementString("Group")
            group_prim = stage.GetPrimAtPath(group_prim_path)
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_path))
            self.assertFalse(stage.GetPrimAtPath(scope_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_xform_path))
            cube_new_path = default_prim_path.AppendPath("Group/Cube")
            sphere_new_path = default_prim_path.AppendPath("Group/Sphere")
            cylinder_new_path = default_prim_path.AppendPath("Group/Cylinder")
            scope_new_path = default_prim_path.AppendPath("Group/Scope")
            cube = stage.GetPrimAtPath(cube_new_path)
            self.assertTrue(cube)
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)
            cylinder = stage.GetPrimAtPath(cylinder_new_path)
            self.assertTrue(cylinder)
            scope = stage.GetPrimAtPath(scope_new_path)
            self.assertTrue(scope)
            cylinder_path = default_prim_path.AppendChild("Cylinder")

            omni.kit.commands.execute("UngroupPrims", prim_paths=[group_prim_path])

            self.assertTrue(stage.GetPrimAtPath(cube_path))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_new_path))
            self.assertTrue(stage.GetPrimAtPath(scope_path))
            self.assertFalse(stage.GetPrimAtPath(scope_new_path))

            omni.kit.undo.undo()
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            self.assertTrue(stage.GetPrimAtPath(cube_new_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_new_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_new_path))
            self.assertFalse(stage.GetPrimAtPath(scope_path))
            self.assertTrue(stage.GetPrimAtPath(scope_new_path))


            omni.kit.undo.redo()
            self.assertTrue(stage.GetPrimAtPath(cube_path))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(cylinder_path))
            self.assertFalse(stage.GetPrimAtPath(cylinder_new_path))
            self.assertTrue(stage.GetPrimAtPath(scope_path))
            self.assertFalse(stage.GetPrimAtPath(scope_new_path))

        await test()

    async def test_basic_instance(self):
        stage = omni.usd.get_context().get_stage()
        # create a cube
        omni.kit.commands.execute("CreatePrim", prim_type="Cube")
        await omni.kit.app.get_app().next_update_async()
        # create a parent xform
        omni.kit.commands.execute("GroupPrims", prim_paths=["/Cube"])
        await omni.kit.app.get_app().next_update_async()
        # create instances to mesh will fail
        omni.kit.commands.execute("CreateInstances", paths_from=["/Cube"])
        await omni.kit.app.get_app().next_update_async()
        instance = stage.GetPrimAtPath("/Cube_01")
        self.assertFalse(instance)
        omni.kit.commands.execute("CreateInstance", path_from="/Cube")
        await omni.kit.app.get_app().next_update_async()
        instance = stage.GetPrimAtPath("/Cube_01")
        self.assertFalse(instance)
        # create instance from the group
        omni.kit.commands.execute("CreateInstances", paths_from=["/Group"])
        await omni.kit.app.get_app().next_update_async()
        # check the instance is created successfully
        instance = stage.GetPrimAtPath("/Group_01")
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(instance.IsValid())
        # check the instance ops names are the same as the original prim
        # not adding extra suffix on top
        original = stage.GetPrimAtPath("/Group")
        xformable_original = UsdGeom.Xformable(original)
        xformable_instance = UsdGeom.Xformable(instance)
        ops_original = [op.GetName() for op in xformable_original.GetOrderedXformOps()]
        ops_instance = [op.GetName() for op in xformable_instance.GetOrderedXformOps()]
        self.assertEqual(ops_original, ops_instance)

        # Creates a material that's outside of /Group namespace, and bind to /Group
        stage.DefinePrim("/Material", "Material")
        rel = original.CreateRelationship("material:binding", False)
        rel.SetTargets(["/Material"])
        omni.kit.commands.execute("CreateInstances", paths_from=["/Group"])

        root_layer = stage.GetRootLayer()
        prop_spec = root_layer.GetPropertyAtPath("/Group_02.material:binding")
        self.assertTrue(prop_spec)
        self.assertTrue(prop_spec.GetInfo("targetPaths").HasItem(Sdf.Path('/Material')))

    async def test_nested_layer_removal_with_stage_update(self):
        stage = Usd.Stage.Open(FILE_PATH_ROOT)
        await omni.kit.app.get_app().next_update_async()
        # check the material prim is defined in the stage
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniPBR")
        self.assertTrue(material_prim.IsDefined())
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniGlass")
        self.assertTrue(material_prim.IsDefined())

        # remove the Looks folder from the `material_sub`subLayer
        # https://github.com/PixarAnimationStudios/USD/commit/0678ee81f3fad66d5ebd8dd03a0cf44a03999292
        if hasattr(Sdf.Layer, 'FindOrOpenRelativeToLayer'):
            sub_layer = Sdf.Layer.FindOrOpenRelativeToLayer(stage.GetRootLayer(), FILE_PATH_SUB)
        else:
            sub_layer = Sdf.FindOrOpenRelativeToLayer(stage.GetRootLayer(), FILE_PATH_SUB)
        with Usd.EditContext(stage, sub_layer):
            stage.RemovePrim("/World/Looks")
        await omni.kit.app.get_app().next_update_async()
        # check the material prim is not there anymore
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniPBR")
        self.assertFalse(material_prim.IsValid())
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniGlass")
        self.assertFalse(material_prim.IsValid())
        # check the cube from the root layer is still there
        scope_prim = stage.GetPrimAtPath("/World/Cube")
        self.assertTrue(scope_prim.IsValid())

    async def test_create_attribute(self):
        desired_value = 1.23456

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)
        prim = stage.DefinePrim(default_prim_path.AppendChild("Cube"), "Cube")
        omni.kit.commands.execute(
            "CreateUsdAttribute",
            prim=prim,
            attr_name="attr1",
            attr_type=Sdf.ValueTypeNames.Double,
            attr_value=desired_value,
        )

        attr = prim.GetAttribute("attr1")
        self.assertTrue(attr.IsValid())
        value = attr.Get()
        self.assertEqual(value, desired_value)

        omni.kit.undo.undo()

        self.assertFalse(prim.GetAttribute("attr1").IsValid())

        omni.kit.undo.redo()

        attr = prim.GetAttribute("attr1")
        self.assertIsNotNone(attr)
        value = attr.Get()
        self.assertEqual(value, desired_value)

        # Test for OM-114657
        with omni.kit.undo.group():
            prim_path = omni.usd.get_stage_next_free_path(
                stage,
                str(stage.GetPseudoRoot().GetPath().AppendPath("toto")),
                False
            )

            omni.kit.commands.execute(
                "CreatePrimCommand",
                prim_path=prim_path,
                prim_type="Xform",
                select_new_prim=False,
            )
            child_prim = stage.GetPrimAtPath(prim_path)

            omni.kit.commands.execute(
                "CreateUsdAttributeCommand",
                prim=child_prim,
                attr_name="hello",
                attr_type=Sdf.ValueTypeNames.Bool,
                attr_value=True,
            )

        omni.kit.undo.undo()
        self.assertFalse(stage.GetPrimAtPath(prim_path))

        omni.kit.undo.redo()
        self.assertTrue(stage.GetPrimAtPath(prim_path))

    async def test_create_attribute_path(self):
        desired_value = 1.23456

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)
        prim = stage.DefinePrim(default_prim_path.AppendChild("Cube"), "Cube")

        omni.kit.commands.execute(
            "CreateUsdAttributeOnPath",
            attr_path=prim.GetPath().AppendProperty("attr1"),
            attr_type=Sdf.ValueTypeNames.Double,
            attr_value=desired_value,
        )

        attr = prim.GetAttribute("attr1")
        self.assertTrue(attr.IsValid())
        value = attr.Get()
        self.assertEqual(value, desired_value)

        omni.kit.undo.undo()

        self.assertFalse(prim.GetAttribute("attr1").IsValid())

        omni.kit.undo.redo()

        attr = prim.GetAttribute("attr1")
        self.assertIsNotNone(attr)
        value = attr.Get()
        self.assertEqual(value, desired_value)

    async def test_remove_property(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        root_layer = stage.GetRootLayer()

        layer_2 = Sdf.Layer.CreateAnonymous()
        layer_1 = Sdf.Layer.CreateAnonymous()

        root_layer.subLayerPaths = [layer_2.identifier, layer_1.identifier]

        with Usd.EditContext(stage, layer_1):
            default_prim_path = getStageDefaultPrimPath(stage)
            prim = stage.DefinePrim(default_prim_path.AppendChild("Cube"), "Cube")
            attr = prim.CreateAttribute("attr1", Sdf.ValueTypeNames.Double)
            attr.Set(1.234)

        with Usd.EditContext(stage, layer_2):
            attr.Set(2.345)

        with Usd.EditContext(stage, root_layer):
            attr.Set(3.456)

        self.assertEqual(attr.Get(), 3.456)

        attr_path = attr.GetPath()

        def check_property_restored():
            spec2 = layer_2.GetAttributeAtPath(attr_path)
            spec1 = layer_1.GetAttributeAtPath(attr_path)
            spec_root = root_layer.GetAttributeAtPath(attr_path)

            self.assertIsNotNone(spec2)
            self.assertIsNotNone(spec1)
            self.assertIsNotNone(spec_root)

            self.assertEqual(spec2.default, 2.345)
            self.assertEqual(spec1.default, 1.234)
            self.assertEqual(spec_root.default, 3.456)

            attr = stage.GetAttributeAtPath(attr_path)
            self.assertTrue(attr.IsValid())
            self.assertEqual(attr.Get(), 3.456)

        # Test removing a property from all layers
        omni.kit.commands.execute("RemoveProperty", prop_path=attr_path)

        self.assertIsNone(layer_2.GetAttributeAtPath(attr_path))
        self.assertIsNone(layer_1.GetAttributeAtPath(attr_path))
        self.assertIsNone(root_layer.GetAttributeAtPath(attr_path))

        attr = stage.GetAttributeAtPath(attr_path)
        self.assertFalse(attr.IsValid())

        omni.kit.undo.undo()
        check_property_restored()
        omni.kit.undo.redo()

        self.assertIsNone(layer_2.GetAttributeAtPath(attr_path))
        self.assertIsNone(layer_1.GetAttributeAtPath(attr_path))
        self.assertIsNone(root_layer.GetAttributeAtPath(attr_path))

        attr = stage.GetAttributeAtPath(attr_path)
        self.assertFalse(attr.IsValid())
        omni.kit.undo.undo()
        check_property_restored()

        # Test removing a property from specific layers
        omni.kit.commands.execute("RemoveProperty", prop_path=attr_path, remove_from_layers=[root_layer, layer_2.identifier])
        spec2 = layer_2.GetAttributeAtPath(attr_path)
        spec1 = layer_1.GetAttributeAtPath(attr_path)
        spec_root = root_layer.GetAttributeAtPath(attr_path)
        self.assertIsNotNone(spec1)
        self.assertIsNone(spec2)
        self.assertIsNone(spec_root)
        self.assertEqual(spec1.default, 1.234)

        attr = stage.GetAttributeAtPath(attr_path)
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), 1.234)

        omni.kit.undo.undo()
        check_property_restored()
        omni.kit.undo.redo()

        spec2 = layer_2.GetAttributeAtPath(attr_path)
        spec1 = layer_1.GetAttributeAtPath(attr_path)
        spec_root = root_layer.GetAttributeAtPath(attr_path)
        self.assertIsNotNone(spec1)
        self.assertIsNone(spec2)
        self.assertIsNone(spec_root)
        self.assertEqual(spec1.default, 1.234)

    async def test_create_references_and_payloads(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        format = Sdf.FileFormat.FindByExtension(".usd")
        sublayer = Sdf.Layer.New(format, "z:/fake-path/subfolder/test.usd")

        reference_layer = Sdf.Layer.New(format, "z:/fake-path/subfolder/nestpath/test2.usd")
        reference_stage = Usd.Stage.Open(reference_layer)
        prim = reference_stage.DefinePrim("/root", "Xform")
        reference_stage.SetDefaultPrim(prim)
        UsdGeom.SetStageUpAxis(reference_stage, UsdGeom.Tokens.z)

        another_layer = Sdf.Layer.New(format, "p:/fake-path/subfolder/nestpath/test2.usd")
        local_layer = Sdf.Layer.New(format, "/fake-path/subfolder/nestpath/local.usd")  # local layer path on Linux
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        root_layer.subLayerPaths.append(sublayer.identifier)

        def create_reference_or_payload_and_check(stage, target_layer, asset_path, reference=True, rotate_ref=False):
            settings = carb.settings.get_settings()
            settings.set("/exts/omni.usd/commands/rotateOnCreatingReference", rotate_ref)

            target_url = omni.client.break_url(target_layer.identifier)
            asset_url = omni.client.break_url(asset_path)
            relative_url = clientutils.make_relative_url_if_possible(target_layer.identifier, asset_path)
            with Usd.EditContext(stage, target_layer):
                test_path = omni.usd.get_stage_next_free_path(stage, "/test", True)
                if reference:
                    command = "CreateReference"
                else:
                    command = "CreatePayload"
                omni.kit.commands.execute(
                    command, usd_context=usd_context, path_to=test_path, asset_path=asset_path
                )
                test_prim = stage.GetPrimAtPath(test_path)
                if reference:
                    reference_list = omni.usd.get_composed_references_from_prim(test_prim)
                else:
                    reference_list = omni.usd.get_composed_payloads_from_prim(test_prim)

                for (reference, layer) in reference_list:
                    self.assertTrue(clientutils.equal_urls(reference.assetPath, relative_url))
                    self.assertEqual(layer, target_layer)

                omni.kit.undo.undo()
                test_prim = stage.GetPrimAtPath(test_path)
                self.assertFalse(test_prim)

        for reference in [True, False]:
            for rotate_ref in [True, False]:
                create_reference_or_payload_and_check(stage, sublayer, reference_layer.identifier, reference, rotate_ref)
                create_reference_or_payload_and_check(stage, root_layer, reference_layer.identifier, reference, rotate_ref)
                create_reference_or_payload_and_check(stage, sublayer, another_layer.identifier, reference, rotate_ref)
                # Don't use omniverse to avoid trigger authentication
                create_reference_or_payload_and_check(
                    stage, sublayer, "fake-scheme://fake-url/invalid/path/test.usd", reference, rotate_ref
                )
                create_reference_or_payload_and_check(
                    stage, root_layer, "fake-scheme://fake-url/invalid/path/test.usd", reference, rotate_ref
                )

        # OMPE-9290: Test case where the current stage is non-local and the asset to reference is local
        # To avoid actually creating a test stage on server, here we fake the Sdf.Layer.identifier property so that
        #  it returns our fake non-local url even though the stage is local
        mock_layer = 'fake-scheme://fake-url/invalid/path/stage.usd'
        def mock_create_reference_or_payload_and_check(stage, target_layer, asset_path, reference=True):
            relative_url = clientutils.make_relative_url_if_possible(mock_layer, asset_path)
            with Usd.EditContext(stage, target_layer):
                test_path = omni.usd.get_stage_next_free_path(stage, "/test", True)
                if reference:
                    command = "CreateReference"
                else:
                    command = "CreatePayload"
                with patch("pxr.Sdf.Layer.identifier", new_callable=PropertyMock) as mock_layer_identifier:
                    mock_layer_identifier.return_value = mock_layer
                    omni.kit.commands.execute(
                        command, usd_context=usd_context, path_to=test_path, asset_path=asset_path
                    )
                test_prim = stage.GetPrimAtPath(test_path)
                if reference:
                    reference_list = omni.usd.get_composed_references_from_prim(test_prim)
                else:
                    reference_list = omni.usd.get_composed_payloads_from_prim(test_prim)

                for (reference, layer) in reference_list:
                    self.assertTrue(clientutils.equal_urls(reference.assetPath, relative_url))
                    self.assertEqual(layer, target_layer)
                    if clientutils.is_local_url(relative_url):
                        self.assertTrue(reference.assetPath.startswith('file:'))

                omni.kit.undo.undo()
                test_prim = stage.GetPrimAtPath(test_path)
                self.assertFalse(test_prim)

        # Test case where the current stage is non-local and the asset to reference is local
        for reference in [True, False]:
            mock_create_reference_or_payload_and_check(stage, root_layer, reference_layer.identifier, reference)
            mock_create_reference_or_payload_and_check(stage, root_layer, local_layer.identifier, reference)
            mock_create_reference_or_payload_and_check(stage, sublayer, another_layer.identifier, reference)
            # Don't use omniverse to avoid trigger authentication
            mock_create_reference_or_payload_and_check(
                stage, root_layer, "fake-scheme://fake-url/invalid/path/test.usd", reference
            )

    async def test_change_property_creation(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()
        xformable = UsdGeom.Xform.Define(stage, "/World/TestXform")

        omni.kit.commands.execute(
            "ChangePropertyCommand",
            prop_path=xformable.GetPath().AppendProperty("CustomAttribute3"),
            value=Gf.Vec3d(10, 10, 10),
            prev=None,
            type_to_create_if_not_exist=Sdf.ValueTypeNames.Vector3d,
        )

        attr = xformable.GetPrim().GetAttribute("CustomAttribute3")
        self.assertTrue(attr.IsValid())
        # 103 behavior defaults to custom as False, and Sdf.VariabilityVarying
        self.assertFalse(attr.IsCustom())
        self.assertEqual(attr.GetVariability(), Sdf.VariabilityVarying)
        self.assertEqual(attr.Get(), Gf.Vec3d(10, 10, 10))

        omni.kit.commands.execute(
            "ChangePropertyCommand",
            prop_path=xformable.GetPath().AppendProperty("CustomAttribute2"),
            value=Gf.Vec2f(20, 20),
            prev=None,
            type_to_create_if_not_exist=Sdf.ValueTypeNames.Float2,
            is_custom=True,
            variability=Sdf.VariabilityUniform,
        )

        attr = xformable.GetPrim().GetAttribute("CustomAttribute2")
        self.assertTrue(attr.IsValid())
        # 103 behavior defaults to custom as False, and Sdf.VariabilityVarying
        self.assertTrue(attr.IsCustom())
        self.assertEqual(attr.GetVariability(), Sdf.VariabilityUniform)
        self.assertEqual(attr.Get(), Gf.Vec2f(20, 20))

    async def test_mdl_material_commands(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        stage = usd_context.get_stage()
        looks_prim = stage.DefinePrim("/World/Looks", "Scope")
        stage.DefinePrim("/World/Looks/material", "Material")
        looks_prim.SetActive(False)

        omni.kit.commands.execute(
            "CreateMdlMaterialPrim",
            mtl_url="OmniPBR.mdl",
            mtl_name="OmniPBR",
            mtl_path="/World/Looks/material"
        )

        # Since looks is inactive, it will activate it and deactivate all of its children.
        prim = stage.GetPrimAtPath("/World/Looks/material")
        self.assertFalse(prim.IsActive())
        material_prim = stage.GetPrimAtPath("/World/Looks/material_01")
        self.assertTrue(material_prim)

        omni.kit.undo.undo()
        self.assertFalse(material_prim)

        omni.kit.commands.execute(
            "CreatePreviewSurfaceTextureMaterialPrim",
            mtl_path="/World/Looks/material1",
            select_new_prim=True
        )
        self.assertTrue(stage.GetPrimAtPath("/World/Looks/material1"))

        omni.kit.undo.undo()
        self.assertFalse(stage.GetPrimAtPath("/World/Looks/material1"))

    async def test_toggle_active_states(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        stage = usd_context.get_stage()
        level1_prim_paths = []
        level2_prim_paths = []

        def check_prim_active_state_and_existence(paths, active):
            stage = usd_context.get_stage()
            for path in paths:
                prim = stage.GetPrimAtPath(path)
                if active:
                    self.assertTrue(prim)
                    self.assertTrue(prim.IsActive())
                else:
                    self.assertTrue(not prim or not prim.IsActive())

        for i in range(10):
            path = Sdf.Path(f"/root{i}")
            prim = stage.DefinePrim(path, "Xform")
            level1_prim_paths.append(path)

            for j in range(10):
                child_path = path.AppendElementString(f"child{j}")
                prim = stage.DefinePrim(child_path, "Xform")
                level2_prim_paths.append(child_path)

        omni.kit.commands.execute("ToggleActivePrims", stage_or_context=stage, prim_paths=level1_prim_paths)
        check_prim_active_state_and_existence(level1_prim_paths, False)
        check_prim_active_state_and_existence(level2_prim_paths, False)
        omni.kit.undo.undo()
        check_prim_active_state_and_existence(level1_prim_paths, True)
        check_prim_active_state_and_existence(level2_prim_paths, True)

        omni.kit.commands.execute("ToggleActivePrims", stage_or_context=usd_context, prim_paths=level2_prim_paths)
        check_prim_active_state_and_existence(level1_prim_paths, True)
        check_prim_active_state_and_existence(level2_prim_paths, False)
        omni.kit.undo.undo()
        check_prim_active_state_and_existence(level1_prim_paths, True)
        check_prim_active_state_and_existence(level2_prim_paths, True)

        all_paths = level1_prim_paths + level2_prim_paths
        omni.kit.commands.execute("ToggleActivePrims", prim_paths=all_paths)
        check_prim_active_state_and_existence(level1_prim_paths, False)
        check_prim_active_state_and_existence(level2_prim_paths, False)
        omni.kit.undo.undo()
        check_prim_active_state_and_existence(level1_prim_paths, True)
        check_prim_active_state_and_existence(level2_prim_paths, True)

        # Do nothing as it specifies active state
        omni.kit.commands.execute("ToggleActivePrims", prim_paths=all_paths, active=True, stage_or_context="")
        check_prim_active_state_and_existence(level1_prim_paths, True)
        check_prim_active_state_and_existence(level2_prim_paths, True)

        omni.kit.commands.execute("ToggleActivePrims", prim_paths=all_paths, active=False, stage_or_context="")
        check_prim_active_state_and_existence(level1_prim_paths, False)
        check_prim_active_state_and_existence(level2_prim_paths, False)
        omni.kit.undo.undo()
        check_prim_active_state_and_existence(level1_prim_paths, True)
        check_prim_active_state_and_existence(level2_prim_paths, True)

    async def test_gprim_parenting(self):

        settings = carb.settings.get_settings()
        setting_key = "/persistent/app/stage/nestedGprimsAuthoring"
        restore_value = settings.get(setting_key)

        async def run_parenting_test(should_succeed: bool):
            settings.set(setting_key, should_succeed)

            usd_context = omni.usd.get_context()
            await usd_context.new_stage_async()
            stage = omni.usd.get_context().get_stage()

            UsdGeom.Cube.Define(stage, "/World/Cube_0")
            UsdGeom.Cube.Define(stage, "/World/Cube_1")

            # Only UsdGeom.Xform (no UsdGeom.Boundable, should always be allowed)
            UsdGeom.Xform.Define(stage, "/World/Xform_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_0/Xform_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_0/Xform_1")


            UsdGeom.Xform.Define(stage, "/World/Xform_1")
            UsdGeom.Xform.Define(stage, "/World/Xform_1/Xform_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_1/Xform_1")
            UsdGeom.Cube.Define(stage,  "/World/Xform_1/Xform_1/Cube_1")

            UsdGeom.Xform.Define(stage, "/World/Xform_2")
            UsdGeom.Cube.Define(stage,  "/World/Xform_2/Cube_1")

            UsdGeom.Xform.Define(stage, "/World/Xform_3")
            UsdGeom.Xform.Define(stage, "/World/Xform_3/Xform_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_3/Xform_1")
            UsdGeom.Cube.Define(stage,  "/World/Xform_3/Xform_1/Cube_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_3/Xform_2")

            UsdGeom.Xform.Define(stage, "/World/Xform_4")
            UsdGeom.Xform.Define(stage, "/World/Xform_4/Xform_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_4/Xform_1")
            UsdGeom.Cube.Define(stage,  "/World/Xform_4/Cube_0")

            UsdGeom.Xform.Define(stage, "/World/Xform_5")
            UsdGeom.Cube.Define(stage,  "/World/Xform_5/Cube_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_5/Xform_0")
            UsdGeom.Xform.Define(stage, "/World/Xform_5/Xform_1")

            # Define nested GPrim structure to test re-parent out of
            UsdGeom.Cube.Define(stage, "/World/Cube_2")
            UsdGeom.Cube.Define(stage, "/World/Cube_2/Cube_3")

            UsdGeom.Cube.Define(stage,  "/World/Cube_4")
            UsdGeom.Xform.Define(stage, "/World/Cube_4/Xform_6")
            UsdGeom.Xform.Define(stage, "/World/Cube_4/Xform_6/Xform_0")
            UsdGeom.Cube.Define(stage,  "/World/Cube_4/Xform_6/Cube_4")
            UsdGeom.Xform.Define(stage, "/World/Cube_4/Xform_6/Xform_1")

            # Only UsdGeom.Xform (no UsdGeom.Boundable, should always be allowed)
            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_0/Xform_1",
                path_to="/World/Cube_0/Xform_1",
            )
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), True)

            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_1/Xform_1",
                path_to="/World/Xform_1/Xform_0/Xform_1",
            )
            prim = stage.GetPrimAtPath("/World/Xform_1/Xform_0/Xform_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), True)
            prim = stage.GetPrimAtPath("/World/Xform_1/Xform_0/Xform_1/Cube_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), True)

            # Undo the above, which should still always be allowed
            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_1/Xform_0/Xform_1",
                path_to="/World/Xform_1/Xform_1",
            )
            prim = stage.GetPrimAtPath("/World/Xform_1/Xform_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), True)
            prim = stage.GetPrimAtPath("/World/Xform_1/Xform_1/Cube_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), True)

            # Only UsdGeom.Xform parented to GPrim (should also always be allowed)
            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_1",
                path_to="/World/Cube_0/Xform_1",
            )
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), True)

            # GPrim hiearchies, should allow or not allow based on setting
            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_2",
                path_to="/World/Cube_0/Xform_2",
            )
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_2")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), should_succeed)
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_2/Cube_1")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), should_succeed)

            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_3",
                path_to="/World/Cube_0/Xform_3",
            )
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_3")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), should_succeed)
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_3/Xform_1/Cube_0")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), should_succeed)

            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_4",
                path_to="/World/Cube_0/Xform_4",
            )
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_4")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), should_succeed)
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_4/Cube_0")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), should_succeed)

            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Xform_5",
                path_to="/World/Cube_0/Xform_5",
            )
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_5")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), should_succeed)
            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_5/Cube_0")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), should_succeed)

            # Test blocking of un-parenting of existing prims
            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Cube_2/Cube_3",
                path_to="/World/Cube_3",
            )
            prim = stage.GetPrimAtPath("/World/Cube_3")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), should_succeed)

            omni.kit.commands.execute("MovePrimCommand",
                path_from="/World/Cube_4/Xform_6",
                path_to="/World/Xform_6",
            )
            prim = stage.GetPrimAtPath("/World/Xform_6")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Xform), should_succeed)
            prim = stage.GetPrimAtPath("/World/Xform_6/Cube_4")
            self.assertEqual(bool(prim), should_succeed)
            self.assertEqual(bool(prim) and prim.IsA(UsdGeom.Cube), should_succeed)

        try:
            await run_parenting_test(True)
            await run_parenting_test(False)
        finally:
            settings.set(setting_key, restore_value)

    async def test_select_prims_command(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        prim_paths = ["/root", "/root1", "/root/child"]
        for path in prim_paths:
            stage.DefinePrim(path, "Xform")

        omni.kit.commands.execute(
            "SelectPrims",
            old_selected_paths=[],
            new_selected_paths=prim_paths
        )
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        selected_prim_paths = usd_context.get_selection().get_selected_prim_paths()
        self.assertEqual(set(selected_prim_paths), set(prim_paths))

        omni.kit.undo.undo()
        selected_prim_paths = usd_context.get_selection().get_selected_prim_paths()
        self.assertFalse(selected_prim_paths)

    async def test_frame_prims(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        prim_paths = ["/root", "/root1", "/root/child"]
        for path in prim_paths:
            stage.DefinePrim(path, "Xform")

        camera_prim = stage.DefinePrim("/camera", "Camera")
        omni.kit.commands.execute("FramePrims", prim_to_move="/camera")
        self.assertIsNotNone(camera_prim.GetPropertyAtPath("omni:kit:centerOfInterest"))

        omni.kit.undo.undo()
        self.assertFalse(camera_prim.GetPropertyAtPath("omni:kit:centerOfInterest"))

    async def test_create_default_xform(self):
        all_keys = [
            "/persistent/app/primCreation/PrimCreationWithDefaultXformOps",
            "/persistent/app/primCreation/DefaultXformOpType",
            "/persistent/app/primCreation/DefaultCameraRotationOrder",
            "/persistent/app/primCreation/DefaultRotationOrder",
        ]

        settings = carb.settings.get_settings()

        old_key_values = {}
        for key in all_keys:
            value = settings.get(key)
            if value is None:
                continue

            old_key_values[key] = key

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        try:
            default_rot_order = "XYZ"
            settings.set(all_keys[2], default_rot_order)
            settings.set(all_keys[3], default_rot_order)
            for create_default_xform in [False, True]:
                settings.set(all_keys[0], create_default_xform)
                for default_xform_op_type in [
                    "Transform",
                    "Scale, Orient, Translate",
                    "Scale, Rotate, Translate",
                ]:
                    settings.set(all_keys[1], default_xform_op_type)

                    prim = stage.DefinePrim("/test", "Xform")
                    omni.kit.commands.execute(
                        "CreateDefaultXformOnPrim",
                        prim_path=prim.GetPath(),
                        stage=stage
                    )

                    if not create_default_xform:
                        self.assertFalse(prim.GetProperty("xformOp:translate"))
                    else:
                        if default_xform_op_type == "Scale, Rotate, Translate":
                            self.assertTrue(prim.GetProperty("xformOp:translate"))
                            self.assertTrue(prim.GetProperty("xformOp:scale"))
                            self.assertTrue(prim.GetProperty("xformOp:rotateXYZ"))
                        elif default_xform_op_type == "Scale, Orient, Translate":
                            self.assertTrue(prim.GetProperty("xformOp:translate"))
                            self.assertTrue(prim.GetProperty("xformOp:scale"))
                            self.assertTrue(prim.GetProperty("xformOp:orient"))
                        else:
                            self.assertTrue(prim.GetProperty("xformOp:transform"))

                    omni.kit.undo.undo()
                    if default_xform_op_type == "Scale, Rotate, Translate":
                        self.assertFalse(prim.GetProperty("xformOp:translate"))
                        self.assertFalse(prim.GetProperty("xformOp:scale"))
                        self.assertFalse(prim.GetProperty("xformOp:rotateXYZ"))
                    elif default_xform_op_type == "Scale, Orient, Translate":
                        self.assertFalse(prim.GetProperty("xformOp:translate"))
                        self.assertFalse(prim.GetProperty("xformOp:scale"))
                        self.assertFalse(prim.GetProperty("xformOp:orient"))
                    else:
                        self.assertFalse(prim.GetProperty("xformOp:transform"))

                stage.RemovePrim("/test")
        finally:
            for key, value in old_key_values.items():
                settings.set(key, value)

    async def test_reference_resolve_api(self):
        material_group_path = "Group_Material"
        cube_group_A_path = "Group_Cube_A"
        cube_group_B_path = "Group_Cube_B"

        # Materials
        material_list = [
            "/World/Looks/OmniGlass",
            "/World/Looks/OmniPBR",
            "/World/Looks/OmniPBR_ClearCoat",
            "/World/Looks/OmniPBRBase"
        ]

        # Cube Groups
        cube_group_A = [
            "/World/Cube_00_A",
            "/World/Cube_01_A",
            "/World/Cube_02_A",
            "/World/Cube_03_A"
        ]
        cube_group_B = [
            "/World/Cube_00_B",
            "/World/Cube_01_B",
            "/World/Cube_02_B",
            "/World/Cube_03_B"
        ]

        usd_context = omni.usd.get_context()
        stage = None

        def open_stage():
            file_path = str(Path(__file__).parent.joinpath("data").joinpath("test_grouping.usda"))
            result = usd_context.open_stage(file_path)
            self.assertTrue(result)
            nonlocal stage
            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)

        def create_group(group_path:str):
            path = Sdf.Path.absoluteRootPath.AppendElementString(group_path)
            group_prim_path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, path, False))
            group_prim = UsdGeom.Xform.Define(stage, group_prim_path)
            Usd.ModelAPI(group_prim).SetKind(Kind.Tokens.group)
            return group_prim

        def move_and_resolve_prim(path_list, group_prim:UsdGeom.Xform, use_batch_api:bool):
            with Sdf.ChangeBlock():
                moved_paths = {}
                for prim_path_str in path_list:
                    prim_path = Sdf.Path(prim_path_str)
                    prim = stage.GetPrimAtPath(prim_path)
                    move_to = group_prim.GetPath().AppendElementString(prim_path.name)
                    layer = None
                    prim_stack = prim.GetPrimStack()
                    for prim_spec in prim_stack:
                        layer = prim_spec.layer
                        if layer.identifier not in moved_paths:
                            moved_paths[layer.identifier] = {"from":[], "to":[]}
                        moved_paths[layer.identifier]["from"].append(prim_path.pathString)
                        moved_paths[layer.identifier]["to"].append(move_to.pathString)

                    self.assertIsNotNone(layer)
                    # Move prim to under the Group prim
                    omni.kit.commands.execute("MovePrim", path_from=prim_path, path_to=move_to, resolve_reference=False)
                    if not use_batch_api:
                        omni.usd.resolve_prim_path_references(layer.identifier, prim_path.pathString, move_to.pathString)

                if use_batch_api:
                    for layer_identifier, paths in moved_paths.items():
                        omni.usd.resolve_prim_paths_references(layer_identifier, paths["from"], paths["to"])

        def validate_resolved_path(prim_path:str):
            prim = stage.GetPrimAtPath(prim_path)
            self.assertIsNotNone(prim)

            # Validate material binding reference
            targets = prim.GetRelationship("material:binding").GetTargets()
            current_prim_path = targets[0].pathString
            expected_prim_path = f"/{material_group_path}/{targets[0].name}"
            self.assertEqual(current_prim_path, expected_prim_path)

            # Validate proxyPrim reference
            targets = prim.GetRelationship("proxyPrim").GetTargets()
            current_prim_path = targets[0].pathString
            if "_A" in prim_path: # Cube Group A must have Group B proxyPrim
                expected_prim_path = f"/{cube_group_B_path}/{targets[0].name}"
                self.assertEqual(current_prim_path, expected_prim_path)
            elif "_B" in prim_path: # Cube Group B must have Group A proxyPrim
                expected_prim_path = f"/{cube_group_A_path}/{targets[0].name}"
                self.assertEqual(current_prim_path, expected_prim_path)
            else:
                never_reach_here = False
                self.assertTrue(never_reach_here) # if here, see test contents was changed or not.

        # Test1 start
        use_batch_api = False
        open_stage()

        # Grouping, it will move prim to other path and will resolve all reference path in the stage
        group = create_group(material_group_path)
        move_and_resolve_prim(material_list, group, use_batch_api)
        group = create_group(cube_group_A_path)
        move_and_resolve_prim(cube_group_A, group, use_batch_api)
        group = create_group(cube_group_B_path)
        move_and_resolve_prim(cube_group_B, group, use_batch_api)

        # Validation
        for index in range(4):
            validate_resolved_path(f"/{cube_group_A_path}/{Sdf.Path(cube_group_A[index]).name}")
            validate_resolved_path(f"/{cube_group_B_path}/{Sdf.Path(cube_group_B[index]).name}")

        # Test2 start
        use_batch_api = True
        open_stage()

        # Grouping, it will move prim to other path and will resolve all reference path in the stage
        group = create_group(material_group_path)
        move_and_resolve_prim(material_list, group, use_batch_api)
        group = create_group(cube_group_A_path)
        move_and_resolve_prim(cube_group_A, group, use_batch_api)
        group = create_group(cube_group_B_path)
        move_and_resolve_prim(cube_group_B, group, use_batch_api)

        # Validation
        for index in range(4):
            validate_resolved_path(f"/{cube_group_A_path}/{Sdf.Path(cube_group_A[index]).name}")
            validate_resolved_path(f"/{cube_group_B_path}/{Sdf.Path(cube_group_B[index]).name}")

    def __get_stage_default_prim_path(self, stage):
        if stage.HasDefaultPrim():
            return stage.GetDefaultPrim().GetPath()
        else:
            return Sdf.Path.absoluteRootPath

    async def test_toggle_payload_selected(self):
        carb.log_info("Test TogglePayLoadLoadSelectedPrimsCommand")
        await omni.usd.get_context().new_stage_async()
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        stage = usd_context.get_stage()
        default_prim_path = self.__get_stage_default_prim_path(stage)

        payload1 = Usd.Stage.CreateInMemory("payload1.usd")
        payload1.DefinePrim("/payload1/scope1", "Xform")
        payload1.DefinePrim("/payload1/scope1/xform", "Cube")

        payload2 = Usd.Stage.CreateInMemory("payload2.usd")
        payload2.DefinePrim("/payload2/scope2", "Xform")
        payload2.DefinePrim("/payload2/scope2/xform", "Cube")

        payload3 = Usd.Stage.CreateInMemory("payload3.usd")
        payload3.DefinePrim("/payload3/scope3", "Xform")
        payload3.DefinePrim("/payload3/scope3/xform", "Cube")

        payload4 = Usd.Stage.CreateInMemory("payload4.usd")
        payload4.DefinePrim("/payload4/scope4", "Xform")
        payload4.DefinePrim("/payload4/scope4/xform", "Cube")

        ps1 = stage.DefinePrim(default_prim_path.AppendChild("payload1"), "Xform")
        ps1.GetPayloads().AddPayload(
            Sdf.Payload(payload1.GetRootLayer().identifier, "/payload1"))
        ps2 = stage.DefinePrim(default_prim_path.AppendChild("payload2"), "Xform")
        ps2.GetPayloads().AddPayload(
            Sdf.Payload(payload2.GetRootLayer().identifier, "/payload2"))
        ps3 = stage.DefinePrim(default_prim_path.AppendChild("payload3"), "Xform")
        ps3.GetPayloads().AddPayload(
            Sdf.Payload(payload3.GetRootLayer().identifier, "/payload3"))
        ps4 = stage.DefinePrim(ps3.GetPath().AppendChild("payload4"), "Xform")
        ps4.GetPayloads().AddPayload(
            Sdf.Payload(payload4.GetRootLayer().identifier, "/payload4"))

        # unload everything
        stage.Unload()

        self.assertTrue(not ps1.IsLoaded())
        self.assertTrue(not ps2.IsLoaded())
        self.assertTrue(not ps3.IsLoaded())
        self.assertTrue(not ps4.IsLoaded())

        # if nothing selected, payload state should not change.
        selection.clear_selected_prim_paths()
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("TogglePayLoadLoadSelectedPrims", selected_paths=paths)
        self.assertTrue(not ps1.IsLoaded())
        self.assertTrue(not ps2.IsLoaded())
        self.assertTrue(not ps3.IsLoaded())
        self.assertTrue(not ps4.IsLoaded())

        # load payload1
        selection.set_selected_prim_paths(
            [
                ps1.GetPath().pathString
            ],
            False,
        )
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("TogglePayLoadLoadSelectedPrims", selected_paths=paths)
        self.assertTrue(ps1.IsLoaded())

        # unload payload1
        omni.kit.commands.execute("TogglePayLoadLoadSelectedPrims", selected_paths=paths)
        self.assertTrue(not ps1.IsLoaded())

        # load payload1, 2 and 3. 4 will load
        selection.set_selected_prim_paths(
            [
                ps1.GetPath().pathString,
                ps2.GetPath().pathString,
                ps3.GetPath().pathString,
            ],
            False,
        )
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("TogglePayLoadLoadSelectedPrims", selected_paths=paths)
        self.assertTrue(ps1.IsLoaded())
        self.assertTrue(ps2.IsLoaded())
        self.assertTrue(ps3.IsLoaded())
        self.assertTrue(ps4.IsLoaded())

        # unload 4
        selection.set_selected_prim_paths(
            [
                ps4.GetPath().pathString
            ],
            False,
        )
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("TogglePayLoadLoadSelectedPrims", selected_paths=paths)
        self.assertTrue(not ps4.IsLoaded())

        # undo
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())

        # redo
        omni.kit.undo.redo()
        self.assertTrue(not ps4.IsLoaded())

    async def test_set_payload_selected(self):
        carb.log_info("Test SetPayLoadLoadSelectedPrimsCommand")
        await omni.usd.get_context().new_stage_async()
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        stage = usd_context.get_stage()
        default_prim_path = self.__get_stage_default_prim_path(stage)

        payload1 = Usd.Stage.CreateInMemory("payload1.usd")
        payload1.DefinePrim("/payload1/scope1", "Xform")
        payload1.DefinePrim("/payload1/scope1/xform", "Cube")

        payload2 = Usd.Stage.CreateInMemory("payload2.usd")
        payload2.DefinePrim("/payload2/scope2", "Xform")
        payload2.DefinePrim("/payload2/scope2/xform", "Cube")

        payload3 = Usd.Stage.CreateInMemory("payload3.usd")
        payload3.DefinePrim("/payload3/scope3", "Xform")
        payload3.DefinePrim("/payload3/scope3/xform", "Cube")

        payload4 = Usd.Stage.CreateInMemory("payload4.usd")
        payload4.DefinePrim("/payload4/scope4", "Xform")
        payload4.DefinePrim("/payload4/scope4/xform", "Cube")

        ps1 = stage.DefinePrim(default_prim_path.AppendChild("payload1"), "Xform")
        ps1.GetPayloads().AddPayload(
            Sdf.Payload(payload1.GetRootLayer().identifier, "/payload1"))
        ps2 = stage.DefinePrim(default_prim_path.AppendChild("payload2"), "Xform")
        ps2.GetPayloads().AddPayload(
            Sdf.Payload(payload2.GetRootLayer().identifier, "/payload2"))
        ps3 = stage.DefinePrim(default_prim_path.AppendChild("payload3"), "Xform")
        ps3.GetPayloads().AddPayload(
            Sdf.Payload(payload3.GetRootLayer().identifier, "/payload3"))
        ps4 = stage.DefinePrim(ps3.GetPath().AppendChild("payload4"), "Xform")
        ps4.GetPayloads().AddPayload(
            Sdf.Payload(payload4.GetRootLayer().identifier, "/payload4"))

        # unload everything
        stage.Unload()

        self.assertTrue(not ps1.IsLoaded())
        self.assertTrue(not ps2.IsLoaded())
        self.assertTrue(not ps3.IsLoaded())
        self.assertTrue(not ps4.IsLoaded())

        # if nothing selected, payload state should not change.
        selection.clear_selected_prim_paths()
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)
        self.assertTrue(not ps1.IsLoaded())
        self.assertTrue(not ps2.IsLoaded())
        self.assertTrue(not ps3.IsLoaded())
        self.assertTrue(not ps4.IsLoaded())

        # load payload1
        selection.set_selected_prim_paths(
            [
                ps1.GetPath().pathString
            ],
            False,
        )
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)
        self.assertTrue(ps1.IsLoaded())
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)
        self.assertTrue(ps1.IsLoaded())

        # unload payload1
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)
        self.assertTrue(not ps1.IsLoaded())
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)
        self.assertTrue(not ps1.IsLoaded())

        # load payload1, 2 and 3. 4 will load
        selection.set_selected_prim_paths(
            [
                ps1.GetPath().pathString,
                ps2.GetPath().pathString,
                ps3.GetPath().pathString,
            ],
            False,
        )
        paths = selection.get_selected_prim_paths()
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)
        self.assertTrue(ps1.IsLoaded())
        self.assertTrue(ps2.IsLoaded())
        self.assertTrue(ps3.IsLoaded())
        self.assertTrue(ps4.IsLoaded())

        selection.set_selected_prim_paths(
            [
                ps4.GetPath().pathString
            ],
            False,
        )
        paths = selection.get_selected_prim_paths()
        # reload 4
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)
        self.assertTrue(ps4.IsLoaded())
        # unload 4
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)
        self.assertTrue(not ps4.IsLoaded())

        # undo
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())

        # redo
        omni.kit.undo.redo()
        self.assertTrue(not ps4.IsLoaded())

        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)
        self.assertTrue(not ps4.IsLoaded())
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)
        self.assertTrue(not ps4.IsLoaded())
        omni.kit.undo.undo()
        self.assertTrue(not ps4.IsLoaded())
        omni.kit.undo.redo()
        self.assertTrue(not ps4.IsLoaded())

        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)  # -1
        self.assertTrue(ps4.IsLoaded())
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)  # 0
        self.assertTrue(ps4.IsLoaded())
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())
        omni.kit.undo.redo()
        self.assertTrue(ps4.IsLoaded())

        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)  # 1
        self.assertTrue(not ps4.IsLoaded())  # 1
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())  # 0
        omni.kit.undo.redo()
        self.assertTrue(not ps4.IsLoaded())  # 1
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())  # 0

        # triple undo
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)  # 2
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)  # 3
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=False)  # 4
        omni.kit.commands.execute("SetPayLoadLoadSelectedPrims", selected_paths=paths, value=True)  # 5
        self.assertTrue(ps4.IsLoaded())  # 5
        omni.kit.undo.undo()
        self.assertTrue(not ps4.IsLoaded())  # 4
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())  # 3
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())  # 2

        # more undo
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())  # 0
        omni.kit.undo.undo()
        self.assertTrue(ps4.IsLoaded())  # -1

    async def test_simple_relative_reference(self):
        """Test that reproduces the user's exact issue using AddReference command with relative path."""        
        temp_dir = carb.tokens.get_tokens_interface().resolve("${temp}")
        # Create Root_Stage.usd and reference_asset.usd in same directory
        stage_path = os.path.join(temp_dir, "root_stage.usd").replace("\\", "/")
        ref_path = os.path.join(temp_dir, "reference_asset.usd").replace("\\", "/")
        
        # Create reference USD file with some content
        ref_stage = Usd.Stage.CreateNew(ref_path)
        ref_prim = ref_stage.DefinePrim("/TestPrim", "Xform")
        ref_stage.Save()
        del ref_stage
        
        # Create main stage with World/Xform prim
        main_stage = Usd.Stage.CreateNew(stage_path)
        world_prim = main_stage.DefinePrim("/World", "Xform")
        xform_prim = main_stage.DefinePrim("/World/Xform", "Xform")
        main_stage.Save()
        del main_stage
        
        # Open the stage in Kit (simulating user opening Root_Stage.usd)
        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(stage_path)
        
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        
        result = omni.kit.commands.execute('AddReference',
            stage=stage,
            prim_path=Sdf.Path('/World/Xform'),
            reference=Sdf.Reference('./reference_asset.usd'))
        
        # Check if the reference was actually added successfully
        prim = stage.GetPrimAtPath("/World/Xform")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        
        self.assertGreater(len(ref_and_layers), 0, "Reference should have been added")
        
        if ref_and_layers:
            ref_asset_path = ref_and_layers[0][0].assetPath
            
            # Test if USD can actually resolve this reference
            resolved_ref = stage.GetEditTarget().GetLayer().ComputeAbsolutePath(ref_asset_path)
            
            # Check if the resolved path exists
            stat_result, _ = omni.client.stat(resolved_ref)
            
            # This should fail if the bug exists
            self.assertEqual(stat_result, omni.client.Result.OK, 
                f"Reference file should be resolvable. "
                f"Original: {ref_path}, Relative: {ref_asset_path}, Resolved: {resolved_ref}")

