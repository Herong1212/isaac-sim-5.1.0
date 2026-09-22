from pathlib import Path
import carb
import omni.timeline
import omni.usd
import omni.kit.test
import omni.kit.commands
import omni.kit.mesh.raycast
from pxr import Gf, UsdGeom


class RaycastTests(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        extension_root_folder = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )
        self._test_files = extension_root_folder.joinpath("data/usd")

        # Load the USD
        usd_context = omni.usd.get_context()
        test_file_path = self._test_files.joinpath("cube.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))

        await omni.kit.app.get_app().next_update_async()

        self._raycast = omni.kit.mesh.raycast.get_mesh_raycast_interface()
        self._raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        self._raycast.set_allowed_mesh_paths([])

    async def tearDown(self):
        omni.usd.get_context().close_stage()
        self._raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.SLOW, False)
        self._raycast = None

    def assertAlmostEqual_Float3(self, a: carb.Float3, b: carb.Float3):
        self.assertAlmostEqual(a[0], b[0], places=5)
        self.assertAlmostEqual(a[1], b[1], places=5)
        self.assertAlmostEqual(a[2], b[2], places=5)

    async def test_raycast(self):
        from_pos = Gf.Vec3d(100, 100, 100)
        dir = Gf.Vec3d(-1, -1, -1).GetNormalized()
        dist = 1000

        # closestRaycast
        hit_result = self._raycast.closestRaycast(from_pos, dir, dist)
        self.assertTrue(hit_result.meshIndex >= 0)
        self.assertAlmostEqual_Float3(hit_result.position, carb.Float3(50, 50, 50))
        self.assertAlmostEqual_Float3(hit_result.normal, carb.Float3(1, 0, 0))

        # invisible
        stage = omni.usd.get_context().get_stage()
        cube_prim = stage.GetPrimAtPath("/World/Cube")

        imageable = UsdGeom.Imageable(cube_prim)
        imageable.GetVisibilityAttr().Set(UsdGeom.Tokens.invisible)
        await omni.kit.app.get_app().next_update_async()

        hit_result = self._raycast.closestRaycast(from_pos, dir, dist)
        self.assertTrue(hit_result.meshIndex < 0)

        imageable.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)
        await omni.kit.app.get_app().next_update_async()

        # sphere raycast
        sphere_radius = 1
        overlap_result = self._raycast.spherecast(from_pos, dir, sphere_radius, dist)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(len(overlap_result) == 2)

        # overlap vertices
        center_pos = carb.Float3(50, 50, 50)
        vertices_result = self._raycast.overlap_vertices(center_pos, 10)
        self.assertTrue(len(vertices_result) == 1)
        prim_path = self._raycast.get_mesh_path_from_index(vertices_result[0].meshIndex)
        self.assertEqual(prim_path, "/World/Cube")

        # change prim on the fly
        omni.kit.commands.execute("DeletePrims", paths=[prim_path])
        omni.kit.commands.execute("CreatePrimCommand", prim_type="Sphere")
        await omni.kit.app.get_app().next_update_async()

        from_pos_2 = Gf.Vec3d(10, 0, 0)
        dir = Gf.Vec3d(-1, 0, 0)
        dist = 20
        hit_result_2 = self._raycast.closestRaycast(from_pos_2, dir, dist)
        self.assertTrue(hit_result_2.meshIndex >= 0)
        self.assertAlmostEqual_Float3(hit_result_2.position, carb.Float3(1, 0, 0))
        self.assertAlmostEqual_Float3(hit_result_2.normal, carb.Float3(1, 0, 0))

        # flood
        density = 10
        prim_path = self._raycast.get_mesh_path_from_index(hit_result_2.meshIndex)
        result = self._raycast.getFloodPoints(prim_path, density, False)
        self.assertEqual(len(result["positions"]), 125) # 125 = density * 4 * 3.14 * 1 * 1

    async def test_66407(self):
        # set invisible and remove a prim at the same frame
        timeline = omni.timeline.get_timeline_interface()
        stage = omni.usd.get_context().get_stage()
        timeline.play()
        await omni.kit.app.get_app().next_update_async()
        prim_path = "/test_crasher"
        cubeGeom = UsdGeom.Cube.Define(stage, prim_path)

        # This is somehow necessary to cause the bug
        imageable = UsdGeom.Imageable(cubeGeom)
        imageable.MakeInvisible()

        await omni.kit.app.get_app().next_update_async()
        from omni.usd.commands import DeletePrimsCommand
        DeletePrimsCommand([cubeGeom.GetPath()]).do()

    async def test_doubleside(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        result, path = omni.kit.commands.execute("CreateMeshPrim", prim_type="Disk")
        self.assertTrue(result)

        self._raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        await omni.kit.app.get_app().next_update_async()

        from_pos = Gf.Vec3d(0, -100, 0)
        dir = Gf.Vec3d(0, 1, 0).GetNormalized()
        dist = 1000

        hit_result = self._raycast.closestRaycast(from_pos, dir, dist)
        self.assertTrue(hit_result.meshIndex < 0)

        prim_disk = stage.GetPrimAtPath(path)
        prim_disk.GetAttribute("doubleSided").Set(True)
        await omni.kit.app.get_app().next_update_async()

        hit_result = self._raycast.closestRaycast(from_pos, dir, dist)
        self.assertTrue(hit_result.meshIndex >= 0)
