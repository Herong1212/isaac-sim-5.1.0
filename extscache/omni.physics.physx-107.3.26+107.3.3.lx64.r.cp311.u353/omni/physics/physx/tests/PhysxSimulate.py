from omni.physics.core import get_physics_simulation_interface
import omni.kit.test
import carb
from pxr import Usd, UsdUtils, UsdPhysics, UsdGeom


class PhysxSimulate(omni.kit.test.AsyncTestCase):

    async def test_stage_update_attached_node(self):

        stage = Usd.Stage.CreateInMemory()
        cache = UsdUtils.StageCache.Get()
        cache.Insert(stage)
        stage_id = cache.GetId(stage).ToLongInt()

        cube_prim = UsdGeom.Cube.Define(stage, "/World/cube").GetPrim()
        UsdPhysics.RigidBodyAPI.Apply(cube_prim)
        UsdPhysics.CollisionAPI.Apply(cube_prim)

        get_physics_simulation_interface().attach_stage(stage_id)

        for _ in range(10):
            get_physics_simulation_interface().simulate(1.0/60.0, 1.0/60.0)
            get_physics_simulation_interface().fetch_results()

        translate_attr = cube_prim.GetAttribute("xformOp:translate")
        self.assertTrue(translate_attr)

        pos = translate_attr.Get()

        self.assertTrue(pos[1] < -10.0)

        get_physics_simulation_interface().detach_stage()

        cache.Erase(stage)

    async def test_simulate_zero_timestep(self):

        stage = Usd.Stage.CreateInMemory()
        cache = UsdUtils.StageCache.Get()
        cache.Insert(stage)
        stage_id = cache.GetId(stage).ToLongInt()

        cube_prim = UsdGeom.Cube.Define(stage, "/World/cube").GetPrim()
        UsdPhysics.RigidBodyAPI.Apply(cube_prim)
        UsdPhysics.CollisionAPI.Apply(cube_prim)

        get_physics_simulation_interface().attach_stage(stage_id)

        get_physics_simulation_interface().simulate(0.0, 0.0)
        get_physics_simulation_interface().fetch_results()

        translate_attr = cube_prim.GetAttribute("xformOp:translate")
        self.assertTrue(translate_attr)

        pos = translate_attr.Get()

        self.assertTrue(pos[1] == 0.0)

        get_physics_simulation_interface().detach_stage()

        cache.Erase(stage)