# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import doctest
import os
import unittest
from pathlib import Path

import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import usdrt
from pxr import PhysxSchema, Sdf, UsdGeom, UsdPhysics

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
PHYSICS_ASSET_URL = str(Path(TEST_DATA_DIR).joinpath("objects/003_cracker_box_physics.usd"))
ANIM_ASSET_URL = str(Path(TEST_DATA_DIR).joinpath("objects/003_cracker_box.usd"))
ASSET_VELOCITIES = [0, 5, 10]
ASSET_X_MIRRORED_LOCATIONS = [(0.5, 0, 0), (0.3, 0, 0), (0.1, 0, 0)]


async def setup_stage_physx_anim(
    material_wait_updates=0, anim_duration=10, timeline_fps=None, physics_fps=None, override_physx_dt=None
):
    # Create new stage
    await omni.usd.get_context().new_stage_async()
    await omni.kit.app.get_app().next_update_async()
    stage = omni.usd.get_context().get_stage()
    timeline = omni.timeline.get_timeline_interface()

    # Create lights
    dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
    dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(100.0)
    distant_light = stage.DefinePrim("/World/DistantLight", "DistantLight")
    if not distant_light.GetAttribute("xformOp:rotateXYZ"):
        UsdGeom.Xformable(distant_light).AddRotateXYZOp()
    distant_light.GetAttribute("xformOp:rotateXYZ").Set((-75, 0, 0))
    distant_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(2500)

    # Set custom timeline FPS if provided
    if timeline_fps is not None:
        timeline.set_time_codes_per_second(timeline_fps)
        timeline.commit()

    # need this for replicator app because the timeline is different from isaacsim (24 instead of 60 by default)
    elif timeline.get_time_codes_per_seconds() != 60:
        timeline.set_time_codes_per_second(60)
        timeline.commit()

    # Set custom physics FPS if provided
    if physics_fps is not None:
        physx_scene = None
        for prim in stage.Traverse():
            if prim.IsA(UsdPhysics.Scene):
                physx_scene = PhysxSchema.PhysxSceneAPI.Apply(prim)
                break
        if physx_scene is None:
            physics_scene = UsdPhysics.Scene.Define(stage, "/PhysicsScene")
            physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/PhysicsScene"))
        physx_scene.GetTimeStepsPerSecondAttr().Set(physics_fps)

    # Setup animated and physics assets
    # assets_root_path = get_assets_root_path()
    # physics_asset_url = assets_root_path + PHYSICS_ASSET_URL
    physics_asset_url = PHYSICS_ASSET_URL
    for loc, vel in zip(ASSET_X_MIRRORED_LOCATIONS, ASSET_VELOCITIES):
        prim = stage.DefinePrim(f"/World/physics_asset_{int(abs(vel))}", "Xform")
        prim.GetReferences().AddReference(physics_asset_url)
        if not prim.GetAttribute("xformOp:translate"):
            UsdGeom.Xformable(prim).AddTranslateOp()
        prim.GetAttribute("xformOp:translate").Set(loc)
        prim.GetAttribute("physxRigidBody:disableGravity").Set(True)
        prim.GetAttribute("physxRigidBody:angularDamping").Set(0.0)
        prim.GetAttribute("physxRigidBody:linearDamping").Set(0.0)
        prim.GetAttribute("physics:velocity").Set((0, 0, -vel))

    # anim_asset_url = assets_root_path + ANIM_ASSET_URL
    anim_asset_url = ANIM_ASSET_URL
    for loc, vel in zip(ASSET_X_MIRRORED_LOCATIONS, ASSET_VELOCITIES):
        start_loc = (-loc[0], loc[1], loc[2])
        prim = stage.DefinePrim(f"/World/anim_asset_{int(abs(vel))}", "Xform")
        prim.GetReferences().AddReference(anim_asset_url)
        if not prim.GetAttribute("xformOp:translate"):
            UsdGeom.Xformable(prim).AddTranslateOp()
        # Timesampled keyframe (animated) translation
        distance = vel * anim_duration
        end_keyframe = timeline.get_time_codes_per_seconds() * anim_duration
        end_loc = (start_loc[0], start_loc[1], start_loc[2] - distance)
        prim.GetAttribute("xformOp:translate").Set(start_loc, time=0)
        prim.GetAttribute("xformOp:translate").Set(end_loc, time=end_keyframe)

    # Setup replicator writer
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)

    # Update app to make sure materials are fully loaded
    for _ in range(material_wait_updates):
        await omni.kit.app.get_app().next_update_async()


class TestOgnPhysics(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        omni.timeline.get_timeline_interface().stop()
        for _ in range(100):
            await omni.kit.app.get_app().next_update_async()
        await omni.usd.get_context().new_stage_async()

    def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.physics)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    async def test_gravity(self):
        gravities = [10, 0.0, -10]
        for i, gravity in enumerate(gravities):
            rep.functional.physics.create_physics_scene(path=f"/PhysicsScene{i}", gravityMagnitude=gravity)
            stage = omni.usd.get_context().get_stage()
            scene_gravity = stage.GetPrimAtPath(f"/PhysicsScene{i}").GetAttribute("physics:gravityMagnitude").Get()
            self.assertAlmostEqual(scene_gravity, gravity)

    async def test_rigid_body_velocities(self):
        timeline_iface = omni.timeline.get_timeline_interface()

        async def step():
            timeline_iface.play()
            timeline_iface.commit()
            await rep.orchestrator.step_async()
            # Let usd update
            timeline_iface.pause()
            timeline_iface.commit()
            await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        timeline_iface.set_time_codes_per_second(1.0)
        await omni.kit.app.get_app().next_update_async()
        rep.functional.physics.create_physics_scene(gravityMagnitude=0.0, timeStepsPerSecond=240)

        with rep.create.cone(rep.distribution.uniform((-100, -100, -100), (100, 100, 100), seed=12), count=10):
            rep.physics.rigid_body(velocity=(100, 200, 300))

        def get_values(attribute):
            values = []
            replicator_prim = stage.GetPrimAtPath("/Replicator")
            for child in replicator_prim.GetChildren():
                if "Cone" in child.GetPrimPath().pathString:
                    values.append(child.GetAttribute(attribute).Get())
            return np.array(values)

        await step()

        pos_init = get_values("xformOp:translate")
        vel_init = get_values("physics:velocity")
        ang_vel_init = get_values("physics:angularVelocity")
        np.testing.assert_allclose(vel_init, np.array([[100.0, 200.0, 300.0]] * len(vel_init)), atol=0.1)
        np.testing.assert_allclose(ang_vel_init, np.zeros_like(vel_init), atol=0.1)

        # FIXME: Not behaving as expected
        # await step()
        # np.testing.assert_allclose(get_values("xformOp:translate") - pos_init, vel_init / 100, atol=0.1)

    async def test_rigid_body_nested(self):
        cube = rep.create.cube()

        stage = omni.usd.get_context().get_stage()

        cube_prim = stage.GetPrimAtPath("/Replicator/Cube_Xform/Cube")
        UsdPhysics.RigidBodyAPI.Apply(cube_prim)

        with cube:
            rep.physics.rigid_body(overwrite=True)

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim = stage.GetPrimAtPath("/Replicator/Cube_Xform")

        self.assertTrue(cube_xform_prim.HasAPI(UsdPhysics.RigidBodyAPI))
        self.assertFalse(cube_prim.HasAPI(UsdPhysics.RigidBodyAPI))

    async def test_physx_anim_timestep_match(self):
        async def setup_stage_and_replicator_async(
            material_wait_updates=0, anim_duration=10, timeline_fps=None, physics_fps=None
        ):
            # Create new stage
            await omni.usd.get_context().new_stage_async()
            stage = omni.usd.get_context().get_stage()
            timeline = omni.timeline.get_timeline_interface()

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM, test takes too long on CI")
    async def test_physx_anim_match(self):
        scenarios = [
            # (timeline_fps, physics_fps, num_frames, advance_with_timeline, delta_time)
            (None, None, 4, True, None),  # [0] NOTE: anim and physics move in sync (as expected)
            (None, None, 4, False, None),  # [1] NOTE: in sync, first frame is not advanced
            (None, None, 4, False, 1 / 60),  # [2]
            (None, None, 4, False, 1 / 30),  # [3]
            (None, None, 4, False, 1 / 120),  # [4] NOTE: physics update happen every 2nd frame
            (None, 120, 4, False, None),  # [5]
            (None, 120, 4, False, 1 / 60),  # [6]
            (None, 120, 4, False, 1 / 30),  # [7]
            (None, 120, 4, False, 1 / 120),  # [8]
            (120, 120, 4, False, None),  # [9]
            (120, 120, 4, False, 1 / 60),  # [10]
            (120, 120, 4, False, 1 / 30),  # [11]
            (120, 120, 4, False, 1 / 120),  # [12]
            (120, None, 4, False, None),  # [13] NOTE: physics update happen every 2nd frame
            (120, None, 4, False, 1 / 60),  # [14]
            (120, None, 4, False, 1 / 30),  # [15]
            (120, None, 4, False, 1 / 120),  # [16] NOTE: physics update happen every 2nd frame
        ]

        for i, scenario in enumerate(scenarios):
            timeline_fps = scenario[0]
            physics_fps = scenario[1]
            num_frames = scenario[2]
            advance_with_timeline = scenario[3]
            delta_time = scenario[4]
            delta_time_str = "None" if delta_time is None else f"{delta_time:.4f}"
            scenario_name = f"_{i}_out_timeline_fps_{timeline_fps}_physics_fps_{physics_fps}_delta_time_{delta_time_str}_num_frames_{num_frames}"
            await setup_stage_physx_anim(timeline_fps=timeline_fps, physics_fps=physics_fps)

            stage = omni.usd.get_context().get_stage()
            usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
            timeline = omni.timeline.get_timeline_interface()
            await omni.kit.app.get_app().next_update_async()

            physics_scene_paths = usdrt_stage.GetPrimsWithTypeName("PhysicsScene")
            if physics_scene_paths:
                physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath(str(physics_scene_paths[0])))

            anim_time_mult = None
            for i in range(num_frames):
                if advance_with_timeline:
                    timeline.forward_one_frame()
                    if i == 1:
                        anim_time_mult = timeline.get_current_time() * timeline.get_time_codes_per_seconds()

                    if anim_time_mult is not None:
                        timetick = (i + 1) * anim_time_mult
                    else:
                        timetick = i + 1
                    await omni.kit.app.get_app().next_update_async()
                    physx_asset_pos_10 = (
                        stage.GetPrimAtPath("/World/physics_asset_10").GetAttribute("xformOp:translate").Get()[2]
                    )
                    anim_asset_pos_10 = (
                        stage.GetPrimAtPath("/World/anim_asset_10").GetAttribute("xformOp:translate").Get(time=i + 1)[2]
                    )

                else:
                    timeline.play()
                    await rep.orchestrator.step_async(delta_time=delta_time)
                    if i == 1:
                        anim_time_mult = timeline.get_current_time() * timeline.get_time_codes_per_seconds()
                    if anim_time_mult is not None:
                        timetick = i * anim_time_mult
                    else:
                        timetick = i
                    physx_asset_pos_10 = (
                        stage.GetPrimAtPath("/World/physics_asset_10").GetAttribute("xformOp:translate").Get()[2]
                    )
                    anim_asset_pos_10 = (
                        stage.GetPrimAtPath("/World/anim_asset_10")
                        .GetAttribute("xformOp:translate")
                        .Get(time=timetick)[2]
                    )

                if i in [0, 2]:
                    self.assertTrue(np.abs(physx_asset_pos_10 - anim_asset_pos_10) < 0.001)

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM, test takes too long on CI")
    async def test_physx_anim_match_set_physx_dt(self):
        scenarios = [
            # (timeline_fps, physics_fps, num_frames, delta_time, physx_delta_time)
            (None, None, 4, 1 / 10, None),
            (None, None, 4, 1 / 10, 1 / 30),
            (None, None, 4, 1 / 10, 1 / 10),
            (None, 120, 4, 1 / 10, None),
            (None, 120, 4, 1 / 10, 1 / 30),
            (None, 120, 4, 1 / 10, 1 / 10),
            (120, 120, 4, 1 / 10, None),
            (120, 120, 4, 1 / 10, 1 / 30),
            (120, 120, 4, 1 / 10, 1 / 30),
            (120, None, 4, 1 / 10, None),
            (120, None, 4, 1 / 10, 1 / 30),
            (120, None, 4, 1 / 10, 1 / 30),
        ]

        for i, scenario in enumerate(scenarios):
            timeline_fps = scenario[0]
            physics_fps = scenario[1]
            num_frames = scenario[2]
            delta_time = scenario[3]
            override_physx_delta_time = scenario[4]
            delta_time_str = "None" if delta_time is None else f"{delta_time:.4f}"
            scenario_name = f"_{i}_out_timeline_fps_{timeline_fps}_physics_fps_{physics_fps}_delta_time_{delta_time_str}_num_frames_{num_frames}"
            await setup_stage_physx_anim(timeline_fps=timeline_fps, physics_fps=physics_fps)
            if override_physx_delta_time is not None:
                rep.settings.set_physx_timestep(override_physx_delta_time)

            stage = omni.usd.get_context().get_stage()
            usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
            timeline = omni.timeline.get_timeline_interface()
            await omni.kit.app.get_app().next_update_async()

            physics_scene_paths = usdrt_stage.GetPrimsWithTypeName("PhysicsScene")
            if physics_scene_paths:
                physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath(str(physics_scene_paths[0])))

            anim_time_mult = None
            for i in range(num_frames):

                timeline.play()
                await rep.orchestrator.step_async(delta_time=delta_time)
                if i == 1:
                    anim_time_mult = timeline.get_current_time() * timeline.get_time_codes_per_seconds()
                if anim_time_mult is not None:
                    timetick = i * anim_time_mult
                else:
                    timetick = i
                physx_asset_pos_10 = (
                    stage.GetPrimAtPath("/World/physics_asset_10").GetAttribute("xformOp:translate").Get()[2]
                )
                anim_asset_pos_10 = (
                    stage.GetPrimAtPath("/World/anim_asset_10").GetAttribute("xformOp:translate").Get(time=timetick)[2]
                )

                if i in [2]:
                    if override_physx_delta_time is None or override_physx_delta_time < 1.0 / 10:
                        self.assertTrue(np.abs(physx_asset_pos_10 - anim_asset_pos_10) > 0.001)
                    else:
                        self.assertTrue(np.abs(physx_asset_pos_10 - anim_asset_pos_10) < 0.001)

    async def test_offsets(self):
        # Ensure contact and rest offsets don't raise errors
        cube = rep.create.cube()
        with cube:
            rep.physics.collider(rest_offset=0.1, contact_offset=0.1)

        num_spheres = 15
        spheres = rep.create.sphere(count=num_spheres)
        with spheres:
            rep.physics.rigid_body(
                rest_offset=rep.distribution.uniform(10, 100),
                contact_offset=rep.distribution.uniform(100, 150),
            )

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        self.assertAlmostEqual(cube_prim.GetAttribute("physxCollision:restOffset").Get(), 0.1)
        self.assertAlmostEqual(cube_prim.GetAttribute("physxCollision:contactOffset").Get(), 0.1)

        sphere_prims = spheres.get_output_prims()["prims"]
        for sphere_prim in sphere_prims:
            self.assertGreater(sphere_prim.GetAttribute("physxCollision:restOffset").Get(), 10)
            self.assertGreater(100, sphere_prim.GetAttribute("physxCollision:restOffset").Get())
            self.assertGreater(sphere_prim.GetAttribute("physxCollision:contactOffset").Get(), 100)
            self.assertGreater(150, sphere_prim.GetAttribute("physxCollision:contactOffset").Get())

    async def test_physics_simulate(self):
        times = [1.0, 2.0]
        step_dt = 0.01
        starting_height = 0
        gravity = 9.81  # Earth (default)

        # Setup scene
        cubes = []
        for i in range(len(times)):
            rep.functional.physics.create_physics_scene(path=f"/PhysicsScene{i}")
            cube = rep.create.cube(position=(0, starting_height, 0))
            with cube:
                rep.physics.rigid_body(physics_scene=f"/PhysicsScene{i}")
            cubes.append(cube)

        # Simulate for each physics scene
        for i, time in enumerate(times):
            rep.physics.simulate(time=time, step_dt=step_dt, physics_scene=f"/PhysicsScene{i}")
        await omni.kit.app.get_app().next_update_async()

        for i, time in enumerate(times):
            expected_height = starting_height - 0.5 * gravity * time**2
            curr_height = cubes[i].get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Get()[1] / 100
            self.assertAlmostEqual(curr_height, expected_height, places=0)

        # Now simulate globally
        rep.physics.simulate(time=2.0, step_dt=step_dt)
        await omni.kit.app.get_app().next_update_async()

        for i, time in enumerate(times):
            expected_height = starting_height - 0.5 * gravity * (time + 2) ** 2
            curr_height = cubes[i].get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Get()[1] / 100
            self.assertAlmostEqual(curr_height, expected_height, places=0)

    async def test_mass_density_multiple(self):
        # Test that mass and density are correctly set for multiple prims
        cube = rep.create.cube(count=10)
        with cube:
            rep.physics.mass(mass=rep.distribution.uniform(0.1, 10), density=rep.distribution.uniform(100, 150))

        await omni.kit.app.get_app().next_update_async()

        cube_prims = cube.get_output_prims()["prims"]

        for cube_prim in cube_prims:
            self.assertGreater(cube_prim.GetAttribute("physics:mass").Get(), 0.1)
            self.assertGreater(10, cube_prim.GetAttribute("physics:mass").Get())
            self.assertGreater(cube_prim.GetAttribute("physics:density").Get(), 100)
            self.assertGreater(150, cube_prim.GetAttribute("physics:density").Get())
