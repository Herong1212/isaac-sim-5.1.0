import omni.kit.test
import omni.usd
import omni.kit.app

import omni.kit.primitive.mesh
import omni.kit.commands
import omni.kit.actions.core

from pathlib import Path
from pxr import Gf, Kind, Sdf, Usd, UsdGeom, UsdShade


EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


# NOTE: those tests belong to omni.kit.primitive.mesh extension.
class TestMeshPrims(omni.kit.test.AsyncTestCase):

    async def test_tessellation_params(self):
        test_data = {
            "Cube": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1, "w_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2, "w_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 400, "u_verts_scale": 2, "v_verts_scale": 2, "w_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1, "w_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2, "w_patches": 2
                    },
                },
            ],
            "Cone": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1, "w_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2, "w_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 400, "u_verts_scale": 2, "v_verts_scale": 2, "w_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1, "w_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2, "w_patches": 2
                    },
                },
            ],
            "Cylinder": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1, "w_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2, "w_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 400, "u_verts_scale": 2, "v_verts_scale": 2, "w_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1, "w_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2, "w_patches": 2
                    },
                },
            ],
            "Disk": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2
                    },
                },
            ],
            "Plane": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2
                    },
                },
            ],
            "Sphere": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2
                    },
                },
            ],
            "Torus": [
                {
                    "params": {"half_scale": 100, "u_verts_scale": 2, "v_verts_scale": 1},
                },
                {
                    "params": {"half_scale": 200, "u_verts_scale": 2, "v_verts_scale": 2},
                },
                {
                    "params": {
                        "half_scale": 100, "u_verts_scale": 1, "v_verts_scale": 1,
                        "u_patches": 2, "v_patches": 2
                    },
                },
            ],
        }

        golden_file = TEST_DATA_PATH.joinpath("golden.usd")
        golden_stage = Usd.Stage.Open(str(golden_file))
        self.assertTrue(golden_stage)

        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        for prim_type, test_cases in test_data.items():
            for test_case in test_cases:
                params = test_case["params"]
                result, path = omni.kit.commands.execute(
                    "CreateMeshPrim", prim_type=prim_type, above_ground=True, **params
                )
                self.assertTrue(result)

                mesh_prim = stage.GetPrimAtPath(path)
                self.assertTrue(mesh_prim)

                golden_prim = golden_stage.GetPrimAtPath(path)
                self.assertTrue(golden_prim)

                property_names = mesh_prim.GetPropertyNames()
                golden_property_names = golden_prim.GetPropertyNames()
                self.assertEqual(property_names, golden_property_names)

                path = Sdf.Path(path)
                for property_name in property_names:
                    property_path = path.AppendProperty(property_name)
                    prop = mesh_prim.GetPropertyAtPath(property_path)
                    golden_prop = golden_prim.GetPropertyAtPath(property_path)
                    # Skips relationship
                    if hasattr(prop, "GetTypeName"):
                        self.assertTrue(prop.GetTypeName(), golden_prop.GetTypeName())
                        self.assertEqual(prop.Get(), golden_prop.Get())


    async def test_mesh_prims(self):
        """Test all mesh generator prims."""
        for y_axis in [True, False]:
            await omni.usd.get_context().new_stage_async()
            stage = omni.usd.get_context().get_stage()
            axis = UsdGeom.Tokens.y if y_axis else UsdGeom.Tokens.z
            UsdGeom.SetStageUpAxis(stage, axis)
            for prim_type in omni.kit.primitive.mesh.get_geometry_mesh_prim_list():
                result, path = omni.kit.commands.execute("CreateMeshPrim", prim_type=prim_type, above_ground=True)
                self.assertTrue(result)

                def check_exist():
                    prim = stage.GetPrimAtPath(path)
                    attr = prim.GetAttribute(UsdGeom.Tokens.extent)
                    self.assertTrue(attr and attr.Get())
                    self.assertTrue(prim)
                    self.assertTrue(prim.IsA(UsdGeom.Mesh))
                    self.assertTrue(prim.IsA(UsdGeom.Xformable))
                    mesh_prim = UsdGeom.Mesh(prim)
                    points = mesh_prim.GetPointsAttr().Get()
                    face_indices = mesh_prim.GetFaceVertexIndicesAttr().Get()
                    normals = mesh_prim.GetNormalsAttr().Get()
                    face_counts = mesh_prim.GetFaceVertexCountsAttr().Get()
                    total = 0
                    for face_count in face_counts:
                        total += face_count
                    unique_indices = set(face_indices)
                    self.assertTrue(len(points) == len(unique_indices))
                    self.assertTrue(total == len(normals))
                    self.assertTrue(total == len(face_indices))

                def check_does_not_exist():
                    self.assertFalse(stage.GetPrimAtPath(path))

                check_exist()
                omni.kit.undo.undo()
                check_does_not_exist()
                omni.kit.undo.redo()
                check_exist()
                omni.kit.undo.undo()
                check_does_not_exist()

    async def test_meshes_creation_from_menu(self):
        import omni.kit.ui_test as ui_test

        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()

        for prim_type in omni.kit.primitive.mesh.get_geometry_mesh_prim_list():
            await ui_test.menu_click(f"Create/Mesh/{prim_type.capitalize()}")
            path = f"/{prim_type}"

            def check_exist():
                prim = stage.GetPrimAtPath(path)
                self.assertTrue(prim)

            def check_does_not_exist():
                self.assertFalse(stage.GetPrimAtPath(path))

            check_exist()
            omni.kit.undo.undo()
            check_does_not_exist()
            omni.kit.undo.redo()
            check_exist()
            omni.kit.undo.undo()
            check_does_not_exist()

    async def test_mesh_settings(self):
        import omni.kit.ui_test as ui_test

        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()

        await ui_test.menu_click("Create/Mesh/Settings")

        window = ui_test.find("Mesh Generation Settings")
        self.assertTrue(window)
        await window.focus()

        primitive_type_combobox = window.find("**/ComboBox[*].name=='primitive_type'")
        self.assertTrue(primitive_type_combobox)
        create_button = window.find("**/Button[*].name=='create'")
        self.assertTrue(create_button)
        model = primitive_type_combobox.model
        value_model = model.get_item_value_model()
        for i, prim_type in enumerate(omni.kit.primitive.mesh.get_geometry_mesh_prim_list()):
            value_model.set_value(i)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            await create_button.click()

            path = f"/{prim_type}"
            self.assertTrue(stage.GetPrimAtPath(path))

    async def test_actions(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()

        for prim_type in omni.kit.primitive.mesh.get_geometry_mesh_prim_list():
            omni.kit.actions.core.execute_action(
                "omni.kit.primitive.mesh",
                f"create_mesh_prim_{prim_type.lower()}"
            )

            path = f"/{prim_type}"

            def check_exist():
                prim = stage.GetPrimAtPath(path)
                self.assertTrue(prim)

            def check_does_not_exist():
                self.assertFalse(stage.GetPrimAtPath(path))

            check_exist()
            omni.kit.undo.undo()
            check_does_not_exist()
            omni.kit.undo.redo()
            check_exist()
            omni.kit.undo.undo()
            check_does_not_exist()

        result, path = omni.kit.commands.execute(
            "CreateMeshPrim", prim_type=prim_type, above_ground=True,
            object_origin=Gf.Vec3f(100.0, 100.0, 100.0)
        )

        self.assertTrue(result)
        prim = stage.GetPrimAtPath(path)
        self.assertTrue(prim)

        xformable_prim = UsdGeom.Xformable(prim)
        world_xform = xformable_prim.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        position = world_xform.ExtractTranslation()
        self.assertTrue(Gf.IsClose(Gf.Vec3d(100.0, 100.0, 100.0), position, 1e-06))
