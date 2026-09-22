# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import carb.settings
import omni.kit.app
import omni.kit.test
import omni.kit.commands
import omni.kit.undo
import omni.usd
import usdrt.Usd
import usdrt.Sdf
import usdrt.UsdGeom
import usdrt.Gf
import usdrt.hierarchy
from pxr import Sdf
from ..scripts import utils


def getStageDefaultPrimPath(stage):
    if stage.GetDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        if isinstance(stage, usdrt.Usd.Stage):
            return usdrt.Sdf.Path.absoluteRootPath
        else:
            return Sdf.Path.absoluteRootPath


class TestCommands(omni.kit.test.AsyncTestCase):
    # inherits from async test case
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._settings = carb.settings.acquire_settings_interface()

        stage = self._get_stage()
        stage_id = stage.GetStageIdAsStageId()
        fabric_id = stage.GetFabricId()
        self._hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

    # inherits from async test case
    async def tearDown(self):
        self._settings = None
        await omni.usd.get_context().close_stage_async()

    def _get_stage(self):
        stage_id = omni.usd.get_context().get_stage_id()
        stage = usdrt.Usd.Stage.Attach(stage_id)
        return stage

    def set_xform_values(self, prim, translation=None, orientation=None, scale=None):
        translate_mtx = usdrt.Gf.Matrix4d()
        if translation is not None:
            translate_mtx.SetTranslate(translation)

        rot_mtx = usdrt.Gf.Matrix4d()
        if orientation is not None:
            rot_mtx.SetRotate(orientation)

        scale_mtx = usdrt.Gf.Matrix4d()
        if scale is not None:
            scale_mtx.SetScale(scale)
        else:
            scale_mtx.SetScale(usdrt.Gf.Vec3d(1, 1, 1))

        world_mtx = scale_mtx * rot_mtx * translate_mtx

        self._hier.set_world_xform(prim.GetPath(), world_mtx)

    # ============ SELECTION COMMAND ============

    # CPP Command
    async def test_cpp_command(self):
        TEST_PATH = "/fabric/commands/test"

        self.assertIsNone(self._settings.get(TEST_PATH))

        omni.kit.commands.execute("TestCppCommand")
        self.assertTrue(self._settings.get(TEST_PATH))

        omni.kit.undo.undo()
        self.assertFalse(self._settings.get(TEST_PATH))

    async def test_create_fabric_prim(self):
        omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")
        stage = self._get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        def check_exist():
            prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
            self.assertTrue(prim)
            self.assertFalse(prim.IsA(usdrt.UsdGeom.Mesh))
            self.assertTrue(prim.IsA(usdrt.UsdGeom.Xformable))
            self.assertTrue(prim.IsA(usdrt.UsdGeom.Sphere))
            self.assertFalse(prim.IsA(usdrt.UsdGeom.Cylinder))

        def check_does_not_exist():
            self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))

        check_exist()

        omni.kit.undo.undo()
        check_does_not_exist()
        omni.kit.undo.redo()
        check_exist()
        omni.kit.undo.undo()
        check_does_not_exist()

    async def test_copy_fabric_prim(self):
        stage = self._get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)
        omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")

        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)

        sphere = usdrt.UsdGeom.Sphere(prim)

        radius_attr = sphere.CreateRadiusAttr()
        radius_attr.Set(1.234)

        radius = sphere.GetRadiusAttr().Get()
        self.assertTrue(radius == 1.234)

        def check(expected_path, expected_radius):
            sphere = usdrt.UsdGeom.Sphere(stage.GetPrimAtPath(expected_path))
            radius = sphere.GetRadiusAttr().Get()
            self.assertTrue(radius == expected_radius)

        # Test default copy behavior
        expected_path = default_prim_path.AppendChild("Sphere_01")
        carb.log_info("Test Duplicate")
        omni.kit.commands.execute("CopyFabricPrim", path_from=default_prim_path.AppendChild("Sphere").pathString)
        check(expected_path, 1.234)
        omni.kit.undo.undo()
        self.assertFalse(stage.GetPrimAtPath(expected_path))
        omni.kit.undo.redo()
        check(expected_path, 1.234)

    async def test_copy_fabric_prims(self):
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        stage = self._get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreateFabricPrims", prim_types=["Sphere", "Cone", "Cube"])

        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone")))
        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube")))

        selected_paths_before = [
            default_prim_path.AppendChild("Sphere").pathString,
            default_prim_path.AppendChild("Cone").pathString,
            default_prim_path.AppendChild("Cube").pathString,
        ]
        selection.set_selected_prim_paths(selected_paths_before, False, omni.usd.Selection.SourceType.FABRIC)

        omni.kit.commands.execute(
            "CopyFabricPrims",
            paths_from=selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        )

        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))

        selected_paths_after = [
            default_prim_path.AppendChild("Sphere_01").pathString,
            default_prim_path.AppendChild("Cone_01").pathString,
            default_prim_path.AppendChild("Cube_01").pathString,
        ]

        self.assertTrue(selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC) == selected_paths_after)

        omni.kit.undo.undo()

        self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
        self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
        self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))
        self.assertTrue(selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC) == selected_paths_before)

        omni.kit.undo.redo()

        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere_01")))
        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone_01")))
        self.assertTrue(stage.GetPrimAtPath(default_prim_path.AppendChild("Cube_01")))
        self.assertTrue(selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC) == selected_paths_after)

        omni.kit.undo.undo()

    async def test_delete_fabric_prims(self):
        stage = self._get_stage()
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
            "CreateFabricPrims",
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

        omni.kit.commands.execute(
            "DeleteFabricPrims",
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

        omni.kit.undo.redo()
        check(self.assertFalse)

    async def test_transform_fabric_prim(self):
        stage = self._get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreateFabricPrim", prim_type="Cube")

        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cube"))
        self.assertTrue(prim)

        world_xform_mtx = self._hier.get_world_xform(prim.GetPath())

        self.assertTrue(world_xform_mtx == usdrt.Gf.Matrix4d(1.0))

        translate_mtx = usdrt.Gf.Matrix4d()
        rotate_mtx = usdrt.Gf.Matrix4d()
        scale_mtx = usdrt.Gf.Matrix4d()

        translate_mtx.SetTranslate(usdrt.Gf.Vec3d(1, 2, 3))
        rotation = usdrt.Gf.Rotation(usdrt.Gf.Vec3d(0, 1, 0), 60)
        rotate_mtx.SetRotate(rotation)
        scale_mtx = scale_mtx.SetScale(usdrt.Gf.Vec3d(3, 2, 1))
        transform_matrix = scale_mtx * rotate_mtx * translate_mtx
        omni.kit.commands.execute(
            "TransformFabricPrim",
            path=default_prim_path.AppendChild("Cube"),
            new_transform_matrix=transform_matrix,
            is_world_xform=True,
        )

        transform_matrix_1 = self._hier.get_local_xform(prim.GetPath())
        self.assertTrue(usdrt.Gf.IsClose(transform_matrix, transform_matrix_1, 0.00001))

        translate_mtx.SetTranslate(usdrt.Gf.Vec3d(3, 5, 2))
        rotation = usdrt.Gf.Rotation(usdrt.Gf.Vec3d(1, 0, 0), 60)
        rotate_mtx.SetRotate(rotation)
        scale_mtx = scale_mtx.SetScale(usdrt.Gf.Vec3d(1, 3, 4))
        transform_matrix_2 = scale_mtx * rotate_mtx * translate_mtx
        omni.kit.commands.execute(
            "TransformFabricPrim",
            path=default_prim_path.AppendChild("Cube"),
            new_transform_matrix=transform_matrix_2,
            is_world_xform=True,
        )

        transform_matrix_3 = self._hier.get_world_xform(prim.GetPath())
        self.assertTrue(usdrt.Gf.IsClose(transform_matrix_2, transform_matrix_3, 0.00001))

        omni.kit.undo.undo()
        transform_matrix_4 = self._hier.get_world_xform(prim.GetPath())
        self.assertTrue(usdrt.Gf.IsClose(transform_matrix_4, transform_matrix_1, 0.00001))

        omni.kit.undo.redo()
        transform_matrix_5 = self._hier.get_world_xform(prim.GetPath())
        self.assertTrue(usdrt.Gf.IsClose(transform_matrix_3, transform_matrix_5, 0.00001))

        omni.kit.undo.undo()
        omni.kit.undo.undo()

        transform_matrix_6 = self._hier.get_world_xform(prim.GetPath())
        self.assertTrue(usdrt.Gf.IsClose(transform_matrix_6, usdrt.Gf.Matrix4d(1.0), 0.00001))

    async def test_move_fabric_prim(self):
        async def test():
            stage = self._get_stage()
            default_prim_path = getStageDefaultPrimPath(stage)

            cube_path = default_prim_path.AppendChild("Cube")
            cube_new_path = default_prim_path.AppendChild("Cube_Renamed")
            cube_new_path2 = "/Cube"
            cube_translate = usdrt.Gf.Vec3d(1, 0, 0)

            sphere_path = default_prim_path.AppendChild("Sphere")
            sphere_new_path = cube_new_path.AppendChild("Sphere_Moved")
            sphere_new_path2 = "/Sphere_02"
            sphere_translate = usdrt.Gf.Vec3d(0, 1, 0)

            # /Stage/Cube
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Cube")
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)
            self.set_xform_values(cube, translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            self.set_xform_values(sphere, translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            self.set_xform_values(sphere, translation=sphere_translate)

            # Should raise a value error
            with self.assertRaises(ValueError):
                omni.kit.commands.execute(
                    "MoveFabricPrim", path_from=cube_path, path_to="123invalid", keep_world_transform=False,
                    stage_or_context=""
                )

            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.commands.execute(
                "MoveFabricPrim", path_from=cube_path, path_to=cube_new_path, keep_world_transform=False,
                stage_or_context=omni.usd.get_context()
            )
            self.assertFalse(stage.GetPrimAtPath(cube_path))
            cube = stage.GetPrimAtPath(cube_new_path)
            self.assertTrue(cube)

            # Cannot move gprim under a gprim
            # /Stage/Cube_Renamed
            # /Stage/Sphere
            omni.kit.commands.execute(
                "MoveFabricPrim", path_from=sphere_path, path_to=sphere_new_path, keep_world_transform=False
            )
            self.assertTrue(stage.GetPrimAtPath(sphere_path))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertFalse(sphere)
            omni.kit.undo.undo()

            # Create xform and move sphere under a xform
            # /Stage/Cube_Renamed
            # /Stage/root/Sphere
            xform_path = default_prim_path.AppendChild("root")
            xform = usdrt.UsdGeom.Xform.Define(stage, xform_path)
            self.assertTrue(xform)
            xform_prim = xform.GetPrim()
            self.set_xform_values(xform_prim, translation=cube_translate, orientation=usdrt.Gf.Quatd(), scale=usdrt.Gf.Vec3d(1,1,1))

            sphere_new_path = xform_path.AppendChild("Sphere")
            omni.kit.commands.execute(
                "MoveFabricPrim", path_from=sphere_path, path_to=sphere_new_path, keep_world_transform=False
            )
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)
            sphere_world_mtx = self._hier.get_world_xform(sphere.GetPath())
            # TODO: translation value is no correct because usdrt.Usd.PrimRange currently doesn't support Fabric only prims
            # self.assertTrue(sphere_world_mtx.GetRow3(3) == sphere_translate + cube_translate)

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
                "MoveFabricPrim", path_from=sphere_path, path_to=sphere_new_path, keep_world_transform=True
            )
            self.assertFalse(stage.GetPrimAtPath(sphere_path))
            sphere = stage.GetPrimAtPath(sphere_new_path)
            self.assertTrue(sphere)

            sphere_world_mtx = self._hier.get_world_xform(sphere.GetPath())
            # TODO: translation value is no correct because usdrt.Usd.PrimRange currently doesn't support Fabric only prims
            # self.assertTrue(sphere_world_mtx.GetRow3(3) == sphere_translate)

            omni.kit.undo.undo()

            # Test batched move
            batch_move = {}
            batch_move[cube_new_path] = cube_new_path2
            batch_move[sphere_path] = sphere_new_path2

            # /Stage
            # /Cube
            # /Sphere
            omni.kit.commands.execute("MoveFabricPrims", paths_to_move=batch_move, stage_or_context=omni.usd.get_context())
            omni.kit.undo.undo()
            omni.kit.commands.execute("MoveFabricPrims", paths_to_move=batch_move, stage_or_context=stage)
            omni.kit.undo.undo()
            omni.kit.commands.execute("MoveFabricPrims", paths_to_move=batch_move, stage_or_context="")
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

            # /Stage
            # /Cube
            # /Sphere
            omni.kit.undo.redo()
            self.assertTrue(stage.GetPrimAtPath(cube_new_path2))
            self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            self.assertTrue(stage.GetPrimAtPath(sphere_new_path2))

        carb.log_info("Test Move/Rename Fabric prims")
        await test()

    async def test_toggle_visibility_selected(self):
        context_name = "test_toggle_visibility_selected"
        usd_context = omni.usd.create_context(context_name)
        usd_context.new_stage()
        selection = usd_context.get_selection()
        stage_id = usd_context.get_stage_id()
        stage = usdrt.Usd.Stage.Attach(stage_id)

        default_prim_path = usdrt.Sdf.Path("/root")

        stage.DefinePrim("/root", "Xform")
        stage.DefinePrim("/root/Cube", "Cube")
        stage.DefinePrim("/root/Sphere", "Sphere")
        stage.DefinePrim("/root/Cone", "Cone")

        def test_visibility(paths, visible):
            paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
            for path in paths:
                prim = stage.GetPrimAtPath(path)
                visibility_attr = prim.GetAttribute("_worldVisibility")

                visibility = True
                if visibility_attr:
                    visibility = visibility_attr.Get()
                if visible:
                    self.assertTrue(visibility)
                else:
                    self.assertFalse(visibility)

        # if nothing selected, visiblity should not change.
        selection.clear_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, True)
        omni.kit.commands.execute("ToggleVisibilitySelectedFabricPrims", selected_paths=paths, stage=stage)
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, True)
        self.assertTrue(len(paths) == 0)

        # select all the paths and there should be 3 selected.
        selection.set_selected_prim_paths(
            [
                default_prim_path.AppendChild("Cube").pathString,
                default_prim_path.AppendChild("Sphere").pathString,
                default_prim_path.AppendChild("Cone").pathString,
            ],
            False,
            omni.usd.Selection.SourceType.FABRIC
        )

        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        self.assertEqual(len(paths), 3)
        # toggle and test they are all hidden
        omni.kit.commands.execute("ToggleVisibilitySelectedFabricPrims", selected_paths=paths, stage=stage)
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, False)
        # toggle again and test they are all visible again
        omni.kit.commands.execute("ToggleVisibilitySelectedFabricPrims", selected_paths=paths, stage=stage)
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, True)
        omni.kit.undo.undo()
        test_visibility(paths, False)
        omni.kit.undo.redo()
        test_visibility(paths, True)

        # select one and it should be visible
        selection.set_selected_prim_paths(
            [default_prim_path.AppendChild("Cube").pathString], False, omni.usd.Selection.SourceType.FABRIC
        )
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, True)

        # toggle and test they are all hidden
        omni.kit.commands.execute("ToggleVisibilitySelectedFabricPrims", selected_paths=paths, stage=stage)
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, False)
        # toggle again and test they are all visible again
        omni.kit.commands.execute(
            "ToggleVisibilitySelectedFabricPrims", selected_paths=paths, stage=stage
        )
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, True)

        omni.kit.undo.undo()
        test_visibility(paths, False)
        omni.kit.undo.redo()
        test_visibility(paths, True)

        omni.kit.commands.execute(
            "ToggleVisibilitySelectedFabricPrims", selected_paths=paths, stage=stage
        )
        paths = selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        test_visibility(paths, False)

        omni.kit.commands.execute(
            "ToggleVisibilitySelectedFabricPrims", selected_paths=["/root/Cube"], stage=stage
        )
        test_visibility(["/root/Cube"], True)
        test_visibility(["/root"], True)
        omni.kit.undo.undo()
        test_visibility(paths, False)
        test_visibility(["/root"], False)

        usd_context.close_stage()
        omni.usd.destroy_context(context_name)

    async def test_change_property(self):
        stage = self._get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        omni.kit.commands.execute("CreateFabricPrim", prim_type="Cube")

        cube_path = default_prim_path.AppendChild("Cube")
        cube = stage.GetPrimAtPath(cube_path)
        self.assertTrue(cube is not None)

        # fabric prim does not have any attribute by default
        size_attr = cube.CreateAttribute("size", usdrt.Sdf.ValueTypeNames.Float, False)
        size_attr.Set(2.0)
        size_attr = cube.GetAttribute("size")
        self.assertTrue(size_attr.Get() == 2.0)

        # test changing existing attr
        size_attr_path = cube_path.AppendProperty("size")
        args = {"prop_path": size_attr_path, "value": 10.0, "prev": None, "timecode": usdrt.Usd.TimeCode.Default()}
        omni.kit.commands.execute("ChangeFabricProperty", **args)

        self.assertTrue(size_attr.Get() == 10.0)

        omni.kit.undo.undo()
        self.assertTrue(size_attr.Get() == 2.0)

        omni.kit.undo.redo()
        self.assertTrue(size_attr.Get() == 10.0)

        # test changing non-exisitng attr
        my_attr_path = cube_path.AppendProperty("not_exist")
        args = {
            "prop_path": my_attr_path,
            "value": True,
            "prev": None,
            "timecode": usdrt.Usd.TimeCode.Default(),
            "type_to_create_if_not_exist": usdrt.Sdf.ValueTypeNames.Bool,
        }
        omni.kit.commands.execute("ChangeFabricProperty", **args)

        my_attr = cube.GetAttribute("not_exist")
        self.assertTrue(my_attr is not None)
        self.assertTrue(my_attr.Get() is True)

        omni.kit.undo.undo()
        my_attr = cube.GetAttribute("not_exist")
        self.assertFalse(my_attr.IsValid())

        omni.kit.undo.redo()
        my_attr = cube.GetAttribute("not_exist")
        self.assertTrue(my_attr.IsValid())
        self.assertTrue(my_attr.Get() is True)

        # test changing non-existing attribute that does not get created
        fake_attr_path = cube_path.AppendProperty("another_fake")
        omni.kit.commands.execute("ChangeFabricProperty", prop_path=fake_attr_path, value=0, prev=1)

        omni.kit.undo.undo()
        self.assertFalse(cube.GetAttribute("another_fake").IsValid())

        omni.kit.undo.redo()
        self.assertFalse(cube.GetAttribute("anoterh_fake").IsValid())

    async def test_change_property_creation(self):
        stage = self._get_stage()
        xformable = usdrt.UsdGeom.Xform.Define(stage, "/World/TestXform")
        xform_path = usdrt.Sdf.Path("/World/TestXform")

        omni.kit.commands.execute(
            "ChangeFabricPropertyCommand",
            prop_path=xform_path.AppendProperty("CustomAttribute3"),
            value=usdrt.Gf.Vec3d(10, 10, 10),
            prev=None,
            type_to_create_if_not_exist=usdrt.Sdf.ValueTypeNames.Vector3d
        )

        attr = xformable.GetPrim().GetAttribute("CustomAttribute3")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), usdrt.Gf.Vec3d(10, 10, 10))

        omni.kit.commands.execute(
            "ChangeFabricPropertyCommand",
            prop_path=xform_path.AppendProperty("CustomAttribute2"),
            value=usdrt.Gf.Vec2f(20, 20),
            prev=None,
            type_to_create_if_not_exist=usdrt.Sdf.ValueTypeNames.Float2,
            is_custom=True
        )

        attr = xformable.GetPrim().GetAttribute("CustomAttribute2")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), usdrt.Gf.Vec2f(20, 20))

    async def test_group_fabric_prims(self):
        async def test():
            stage = self._get_stage()
            default_prim_path = getStageDefaultPrimPath(stage)

            cube_path = default_prim_path.AppendChild("Cube")
            cube_translate = usdrt.Gf.Vec3d(100, 0, 0)

            sphere_path = default_prim_path.AppendChild("Sphere")
            sphere_translate = usdrt.Gf.Vec3d(0, 100, 0)

            cylinder_xform_path = default_prim_path.AppendChild("CylinderXform")
            cylinder_xform_translate = usdrt.Gf.Vec3d(0, 0, 100)

            cylinder_path = cylinder_xform_path.AppendChild("Cylinder")
            cylinder_translate = usdrt.Gf.Vec3d(0, 0, 100)

            scope_path = default_prim_path.AppendChild("Scope")

            # /Stage/Cube
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Cube")
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)
            # Set translate
            self.set_xform_values(cube, translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            self.set_xform_values(sphere, translation=sphere_translate)

            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            prim = usdrt.UsdGeom.Xform.Define(stage, cylinder_xform_path)
            cylinder_xform = prim.GetPrim()

            prim = usdrt.UsdGeom.Cylinder.Define(stage, cylinder_path)
            cylinder = prim.GetPrim()

            self.set_xform_values(
                cylinder_xform,
                translation=cylinder_xform_translate,
                orientation=usdrt.Gf.Quatd(),
                scale=usdrt.Gf.Vec3d(1,1,1)
            )
            self.set_xform_values(
                cylinder,
                translation=cylinder_translate,
                orientation=usdrt.Gf.Quatd(),
                scale=usdrt.Gf.Vec3d(1,1,1)
            )

            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            # /Stage/Sceope
            # Non xformable prim
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Scope")

            # /Stage/Group/Cube
            # /Stage/Group/Sphere
            # /Stage/Group/Cylinder
            # /Stage/Group/Scope
            omni.kit.commands.execute("GroupFabricPrims", prim_paths=[cube_path, sphere_path, cylinder_path, scope_path])
            group_prim_path = default_prim_path.AppendChild("Group")
            group_prim = stage.GetPrimAtPath(group_prim_path)

            # TODO: check group position, currently pivot may not be centralized for certain fabric prims due to extent attribute
            # self.assertEqual(pivot, usdrt.Gf.Vec3f(50, 50, 100))
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

            sphere_world_mtx = self._hier.get_world_xform(sphere.GetPath())
            # TODO: translation value is no correct because usdrt.Usd.PrimRange currently doesn't support Fabric only prims
            # self.assertTrue(sphere_world_mtx.GetRow3(3) == sphere_translate)

            cube_world_mtx = self._hier.get_world_xform(cube.GetPath())
            # TODO: translation value is no correct because usdrt.Usd.PrimRange currently doesn't support Fabric only prims
            # self.assertTrue(cube_world_mtx.GetRow3(3) == cube_translate)

            cylinder_world_mtx = self._hier.get_world_xform(cylinder.GetPath())
            # TODO: translation value is no correct because usdrt.Usd.PrimRange currently doesn't support Fabric only prims
            # self.assertTrue(cylinder_world_mtx.GetRow3(3) == cylinder_xform_translate + cylinder_translate)

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

    async def test_ungroup_fabric_prims(self):
        async def test():
            stage = self._get_stage()
            default_prim_path = getStageDefaultPrimPath(stage)

            cube_path = default_prim_path.AppendChild("Cube")
            cube_translate = usdrt.Gf.Vec3d(100, 0, 0)

            sphere_path = default_prim_path.AppendChild("Sphere")
            sphere_translate = usdrt.Gf.Vec3d(0, 100, 0)

            cylinder_xform_path = default_prim_path.AppendChild("CylinderXform")
            cylinder_xform_translate = usdrt.Gf.Vec3d(0, 0, 100)

            cylinder_path = cylinder_xform_path.AppendChild("Cylinder")
            cylinder_translate = usdrt.Gf.Vec3d(0, 0, 100)

            scope_path = default_prim_path.AppendChild("Scope")

            # /Stage/Cube
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Cube")
            cube = stage.GetPrimAtPath(cube_path)
            self.assertTrue(cube)
            self.set_xform_values(cube, translation=cube_translate)

            # /Stage/Cube
            # /Stage/Sphere
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")
            sphere = stage.GetPrimAtPath(sphere_path)
            self.assertTrue(sphere)
            self.set_xform_values(sphere, translation=sphere_translate)

            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            cylinder_xform = usdrt.UsdGeom.Xform.Define(stage, cylinder_xform_path)
            cylinder_xform_prim = cylinder_xform.GetPrim()
            self.set_xform_values(
                cylinder_xform_prim,
                translation=cylinder_xform_translate,
                orientation=usdrt.Gf.Quatd(),
                scale=usdrt.Gf.Vec3d(1,1,1)
            )

            cylinder = usdrt.UsdGeom.Cylinder.Define(stage, cylinder_path)
            cylinder_prim = cylinder.GetPrim()
            self.set_xform_values(
                cylinder_prim,
                translation=cylinder_translate,
                orientation=usdrt.Gf.Quatd(),
                scale=usdrt.Gf.Vec3d(1,1,1)
            )

            # /Stage/Cube
            # /Stage/Sphere
            # /Stage/CylinderXform/Cylinder
            # /Stage/Scope
            # Non xformable prim
            omni.kit.commands.execute("CreateFabricPrim", prim_type="Scope")

            # /Stage/Group/Cube
            # /Stage/Group/Sphere
            # /Stage/Group/Cylinder
            # /Stage/Group/Scope
            omni.kit.commands.execute("GroupFabricPrims", prim_paths=[cube_path, sphere_path, cylinder_path, scope_path])

            group_prim_path = default_prim_path.AppendChild("Group")
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

            # TODO: usdrt.Usd.Prim.GetChildren() currently doesn't work for Fabric only prims

            # omni.kit.commands.execute("UngroupFabricPrims", prim_paths=[group_prim_path])
            # self.assertTrue(stage.GetPrimAtPath(cube_path))
            # self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            # self.assertTrue(stage.GetPrimAtPath(sphere_path))
            # self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            # self.assertTrue(stage.GetPrimAtPath(cylinder_path))
            # self.assertFalse(stage.GetPrimAtPath(cylinder_new_path))
            # self.assertTrue(stage.GetPrimAtPath(scope_path))
            # self.assertFalse(stage.GetPrimAtPath(scope_new_path))

            # omni.kit.undo.undo()
            # self.assertFalse(stage.GetPrimAtPath(cube_path))
            # self.assertTrue(stage.GetPrimAtPath(cube_new_path))
            # self.assertFalse(stage.GetPrimAtPath(sphere_path))
            # self.assertTrue(stage.GetPrimAtPath(sphere_new_path))
            # self.assertFalse(stage.GetPrimAtPath(cylinder_path))
            # self.assertTrue(stage.GetPrimAtPath(cylinder_new_path))
            # self.assertFalse(stage.GetPrimAtPath(scope_path))
            # self.assertTrue(stage.GetPrimAtPath(scope_new_path))

            # omni.kit.undo.redo()
            # self.assertTrue(stage.GetPrimAtPath(cube_path))
            # self.assertFalse(stage.GetPrimAtPath(cube_new_path))
            # self.assertTrue(stage.GetPrimAtPath(sphere_path))
            # self.assertFalse(stage.GetPrimAtPath(sphere_new_path))
            # self.assertTrue(stage.GetPrimAtPath(cylinder_path))
            # self.assertFalse(stage.GetPrimAtPath(cylinder_new_path))
            # self.assertTrue(stage.GetPrimAtPath(scope_path))
            # self.assertFalse(stage.GetPrimAtPath(scope_new_path))

        await test()

    async def test_fabric_gprim_parenting(self):
        settings = carb.settings.get_settings()
        setting_key = "/persistent/app/stage/nestedGprimsAuthoring"
        restore_value = settings.get(setting_key)

        async def run_parenting_test(should_succeed: bool):
            settings.set(setting_key, should_succeed)
            usd_context = omni.usd.get_context()
            await usd_context.new_stage_async()
            stage = self._get_stage()

            usdrt.UsdGeom.Cube.Define(stage, "/World/Cube_0")
            usdrt.UsdGeom.Cube.Define(stage, "/World/Cube_1")

            # Only usdrt.UsdGeom.Xform (no UsdGeom.Boundable, should always be allowed)
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_0/Xform_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_0/Xform_1")

            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_1")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_1/Xform_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_1/Xform_1")
            usdrt.UsdGeom.Cube.Define(stage,  "/World/Xform_1/Xform_1/Cube_1")

            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_2")
            usdrt.UsdGeom.Cube.Define(stage,  "/World/Xform_2/Cube_1")

            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_3")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_3/Xform_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_3/Xform_1")
            usdrt.UsdGeom.Cube.Define(stage,  "/World/Xform_3/Xform_1/Cube_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_3/Xform_2")

            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_4")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_4/Xform_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_4/Xform_1")
            usdrt.UsdGeom.Cube.Define(stage,  "/World/Xform_4/Cube_0")

            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_5")
            usdrt.UsdGeom.Cube.Define(stage,  "/World/Xform_5/Cube_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_5/Xform_0")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Xform_5/Xform_1")

            # Define nested GPrim structure to test re-parent out of
            usdrt.UsdGeom.Cube.Define(stage, "/World/Cube_2")
            usdrt.UsdGeom.Cube.Define(stage, "/World/Cube_2/Cube_3")

            usdrt.UsdGeom.Cube.Define(stage,  "/World/Cube_4")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Cube_4/Xform_6")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Cube_4/Xform_6/Xform_0")
            usdrt.UsdGeom.Cube.Define(stage,  "/World/Cube_4/Xform_6/Cube_4")
            usdrt.UsdGeom.Xform.Define(stage, "/World/Cube_4/Xform_6/Xform_1")

            # Only usdrt.UsdGeom.Xform (no usdrt.UsdGeom.Boundable, should always be allowed)
            omni.kit.commands.execute("MoveFabricPrimCommand",
                path_from="/World/Xform_0/Xform_1",
                path_to="/World/Cube_0/Xform_1",
            )

            prim = stage.GetPrimAtPath("/World/Cube_0/Xform_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), True)

            omni.kit.commands.execute("MoveFabricPrimCommand",
                path_from="/World/Xform_1/Xform_1",
                path_to="/World/Xform_1/Xform_0/Xform_1",
            )
            prim = stage.GetPrimAtPath("/World/Xform_1/Xform_0/Xform_1")
            self.assertEqual(bool(prim), True)
            self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), True)

            # TODO: Get children currently doesn't work for Fabric only prims
            # prim = stage.GetPrimAtPath("/World/Xform_1/Xform_0/Xform_1/Cube_1")
            # self.assertEqual(bool(prim), True)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), True)

            # # Undo the above, which should still always be allowed
            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Xform_1/Xform_0/Xform_1",
            #     path_to="/World/Xform_1/Xform_1",
            # )
            # prim = stage.GetPrimAtPath("/World/Xform_1/Xform_1")
            # self.assertEqual(bool(prim), True)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), True)
            # prim = stage.GetPrimAtPath("/World/Xform_1/Xform_1/Cube_1")
            # self.assertEqual(bool(prim), True)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), True)

            # # Only UsdGeom.Xform parented to GPrim (should also always be allowed)
            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Xform_1",
            #     path_to="/World/Cube_0/Xform_1",
            # )
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_1")
            # self.assertEqual(bool(prim), True)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), True)

            # # GPrim hiearchies, should allow or not allow based on setting
            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Xform_2",
            #     path_to="/World/Cube_0/Xform_2",
            # )
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_2")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), should_succeed)
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_2/Cube_1")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), should_succeed)

            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Xform_3",
            #     path_to="/World/Cube_0/Xform_3",
            # )
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_3")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), should_succeed)
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_3/Xform_1/Cube_0")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), should_succeed)

            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Xform_4",
            #     path_to="/World/Cube_0/Xform_4",
            # )
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_4")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), should_succeed)
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_4/Cube_0")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), should_succeed)

            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Xform_5",
            #     path_to="/World/Cube_0/Xform_5",
            # )
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_5")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), should_succeed)
            # prim = stage.GetPrimAtPath("/World/Cube_0/Xform_5/Cube_0")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), should_succeed)

            # # Test blocking of un-parenting of existing prims
            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Cube_2/Cube_3",
            #     path_to="/World/Cube_3",
            # )
            # prim = stage.GetPrimAtPath("/World/Cube_3")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), should_succeed)

            # omni.kit.commands.execute("MoveFabricPrimCommand",
            #     path_from="/World/Cube_4/Xform_6",
            #     path_to="/World/Xform_6",
            # )
            # prim = stage.GetPrimAtPath("/World/Xform_6")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Xform), should_succeed)
            # prim = stage.GetPrimAtPath("/World/Xform_6/Cube_4")
            # self.assertEqual(bool(prim), should_succeed)
            # self.assertEqual(bool(prim) and prim.IsA(usdrt.UsdGeom.Cube), should_succeed)

        try:
            await run_parenting_test(True)
            await run_parenting_test(False)
        finally:
            settings.set(setting_key, restore_value)

    async def test_create_default_xform_on_fabric_prim(self):
        stage = self._get_stage()
        default_prim_path = getStageDefaultPrimPath(stage)

        # Test xform values for specific prims
        dome_light_path = default_prim_path.AppendChild("DomeLight")
        stage.DefinePrim(dome_light_path, "DomeLight")
        dome_light = stage.GetPrimAtPath(dome_light_path)

        self.assertTrue(dome_light)
        dome_light = stage.GetPrimAtPath(dome_light_path)

        omni.kit.commands.execute(
            "CreateDefaultXformOnFabricPrim",
            prim_path=dome_light_path,
            stage=stage
        )

        world_mtx = self._hier.get_world_xform(dome_light_path)
        rotation = world_mtx.ExtractRotation()

        angle = rotation.GetAngle()
        self.assertTrue(usdrt.Gf.IsClose(angle, 270.0, 0.00001))

        omni.kit.undo.undo()
        world_mtx = self._hier.get_world_xform(dome_light_path)
        self.assertTrue(usdrt.Gf.IsClose(world_mtx, usdrt.Gf.Matrix4d(1), 1e-5))

        omni.kit.undo.redo()
        world_mtx = self._hier.get_world_xform(dome_light_path)
        rotation = world_mtx.ExtractRotation()

        angle = rotation.GetAngle()
        self.assertTrue(usdrt.Gf.IsClose(angle, 270.0, 0.00001))
