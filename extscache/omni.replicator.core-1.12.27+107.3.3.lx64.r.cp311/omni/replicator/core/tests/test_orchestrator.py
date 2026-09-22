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

import asyncio
import os
import random
import shutil
import sys
import unittest

import carb
import numpy as np
import omni.kit
import omni.kit.test
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core.functional import io_functions
from PIL import Image
from pxr import PhysxSchema, Sdf, Usd, UsdGeom, UsdPhysics

from .test_physics import setup_stage_physx_anim
from .utils import gitlab_output_image_comparison, tc_output_image_comparison

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

# Paths to the animated and physics-ready assets
PHYSICS_ASSET_URL = "data/objects/003_cracker_box_physics.usd"
ANIM_ASSET_URL = "data/objects/003_cracker_box.usd"

# -z velocities and start locations of the animated (left side) and physics (right side) assets (stage units/s)
ASSET_VELOCITIES = [0, 5, 10]
ASSET_X_MIRRORED_LOCATIONS = [(0.5, 0, 0.3), (0.3, 0, 0.3), (0.1, 0, 0.3)]

# Used to calculate how many frames to animate the assets to maintain the same velocity as the physics assets
ANIMATION_DURATION = 10


# Create a new stage with animated and physics-enabled assets with synchronized motion
async def setup_stage():
    # Create new stage
    await omni.usd.get_context().new_stage_async()
    await omni.kit.app.get_app().next_update_async()
    stage = omni.usd.get_context().get_stage()
    timeline = omni.timeline.get_timeline_interface()
    timeline.set_end_time(ANIMATION_DURATION)

    # Create lights
    dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
    dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(100.0)
    distant_light = stage.DefinePrim("/World/DistantLight", "DistantLight")
    if not distant_light.GetAttribute("xformOp:rotateXYZ"):
        UsdGeom.Xformable(distant_light).AddRotateXYZOp()
    distant_light.GetAttribute("xformOp:rotateXYZ").Set((-75, 0, 0))
    distant_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(2500)

    # Setup the physics assets with gravity disabled and the requested velocity
    assets_root_path = os.path.dirname(os.path.realpath(__file__))
    physics_asset_url = os.path.join(assets_root_path, PHYSICS_ASSET_URL)
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

    # Setup animated assets maintaining the same velocity as the physics asssets
    anim_asset_url = os.path.join(assets_root_path, ANIM_ASSET_URL)
    for loc, vel in zip(ASSET_X_MIRRORED_LOCATIONS, ASSET_VELOCITIES):
        start_loc = (-loc[0], loc[1], loc[2])
        prim = stage.DefinePrim(f"/World/anim_asset_{int(abs(vel))}", "Xform")
        prim.GetReferences().AddReference(anim_asset_url)
        if not prim.GetAttribute("xformOp:translate"):
            UsdGeom.Xformable(prim).AddTranslateOp()
        anim_distance = vel * ANIMATION_DURATION
        end_loc = (start_loc[0], start_loc[1], start_loc[2] - anim_distance)
        end_keyframe = timeline.get_time_codes_per_seconds() * ANIMATION_DURATION
        # Timesampled keyframe (animated) translation
        prim.GetAttribute("xformOp:translate").Set(start_loc, time=0)
        prim.GetAttribute("xformOp:translate").Set(end_loc, time=end_keyframe)


# Capture motion blur frames with the given delta time step and render mode
async def run_motion_blur_example_async(
    num_frames=2,
    custom_delta_time=None,
    pt_subsamples=8,
    pt_spp=64,
    pt_totalspp=64,
):
    # Create a new stage with the assets
    await setup_stage()
    stage = omni.usd.get_context().get_stage()
    timeline = omni.timeline.get_timeline_interface()

    # Set replicator settings (capture only on request and enable motion blur)
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)

    orig_rendermode = carb.settings.get_settings().get("/rtx/rendermode")
    carb.settings.get_settings().set("/rtx/rendermode", "PathTracing")

    # (int): Total number of samples for each rendered pixel, per frame.
    carb.settings.get_settings().set("/rtx/pathtracing/spp", pt_spp)
    # (int): Maximum number of samples to accumulate per pixel. When this count is reached the rendering stops until a scene or setting change is detected, restarting the rendering process. Set to 0 to remove this limit.
    carb.settings.get_settings().set("/rtx/pathtracing/totalSpp", pt_totalspp)
    carb.settings.get_settings().set("/rtx/pathtracing/optixDenoiser/enabled", 0)
    # Number of sub samples to render if in PathTracing render mode and motion blur is enabled.
    if not pt_subsamples:
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
    else:
        carb.settings.get_settings().set("/omni/replicator/pathTracedMotionBlurSubSamples", pt_subsamples)

    # Setup camera and writer
    camera = rep.create.camera(position=(0, 1.5, 0), look_at=(0, 0, 0), name="MotionBlurCam")
    render_product = rep.create.render_product(camera, (960, 540))
    rgb_anno = rep.annotators.get("rgb")
    rgb_anno.attach(render_product)

    # Use the physics scene to modify the physics FPS (if needed) to guarantee motion samples at any custom delta time
    physx_scene = None
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.Scene):
            physx_scene = PhysxSchema.PhysxSceneAPI.Apply(prim)
            break
    if physx_scene is None:
        physics_scene = UsdPhysics.Scene.Define(stage, "/PhysicsScene")
        physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/PhysicsScene"))

    # Check the target physics depending on the custom delta time and the render mode
    target_physics_fps = stage.GetTimeCodesPerSecond() if custom_delta_time is None else 1 / custom_delta_time
    if not pt_subsamples:
        target_physics_fps *= pt_totalspp // pt_spp
    else:
        target_physics_fps *= pt_subsamples

    # Check if the physics FPS needs to be increased to match the custom delta time
    orig_physics_fps = physx_scene.GetTimeStepsPerSecondAttr().Get()
    if target_physics_fps > orig_physics_fps:
        physx_scene.GetTimeStepsPerSecondAttr().Set(target_physics_fps)

    # Capture frames
    timeline.play()
    for i in range(num_frames):
        await rep.orchestrator.step_async(delta_time=custom_delta_time)
    timeline.pause()
    rgb = rgb_anno.get_data()

    # Restore the original physics FPS
    if target_physics_fps > orig_physics_fps:
        physx_scene.GetTimeStepsPerSecondAttr().Set(orig_physics_fps)

    # Switch back to the original rendering mode
    carb.settings.get_settings().set("/rtx/rendermode", orig_rendermode)

    return rgb


async def capture_with_motion_blur_and_pathtracing_async(duration=0.05, num_samples=8, spp=64):
    stage = omni.usd.get_context().get_stage()
    physx_scene = None
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.Scene):
            physx_scene = PhysxSchema.PhysxSceneAPI.Apply(prim)
            break
    if physx_scene is None:
        physics_scene = UsdPhysics.Scene.Define(stage, "/PhysicsScene")
        physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/PhysicsScene"))

    # For small step sizes the physics FPS needs to be temporarily increased to provide movements every syb sample
    orig_physics_fps = physx_scene.GetTimeStepsPerSecondAttr().Get()
    target_physics_fps = 1 / duration * num_samples
    if target_physics_fps > orig_physics_fps:
        physx_scene.GetTimeStepsPerSecondAttr().Set(target_physics_fps)

    carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
    carb.settings.get_settings().set("/omni/replicator/pathTracedMotionBlurSubSamples", num_samples)

    # Set the render mode to PathTracing
    prev_render_mode = carb.settings.get_settings().get("/rtx/rendermode")
    carb.settings.get_settings().set("/rtx/rendermode", "PathTracing")
    carb.settings.get_settings().set("/rtx/pathtracing/spp", spp)
    carb.settings.get_settings().set("/rtx/pathtracing/totalSpp", spp)
    carb.settings.get_settings().set("/rtx/pathtracing/clampSpp", spp)
    carb.settings.get_settings().set("/rtx/pathtracing/optixDenoiser/enabled", 0)

    # Capture the frame by advancing the simulation for the given duration and combining the sub samples
    await rep.orchestrator.step_async(delta_time=duration, pause_timeline=False)

    if target_physics_fps > orig_physics_fps:
        print(f"\t\t[SDG] Restoring physics FPS from {target_physics_fps} to {orig_physics_fps}")
        physx_scene.GetTimeStepsPerSecondAttr().Set(orig_physics_fps)

    carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", False)
    print(f"\t\t[SDG] Restoring render mode from 'PathTracing' to '{prev_render_mode}'")
    carb.settings.get_settings().set("/rtx/rendermode", prev_render_mode)


async def create_timeseries_cube_async(num_frames):
    stage = omni.usd.get_context().get_stage()
    timeline = omni.timeline.get_timeline_interface()

    cube = stage.DefinePrim("/World/Cube", "Cube")
    UsdGeom.Xformable(cube).AddTranslateOp()
    for i in range(num_frames):
        cube.GetAttribute("xformOp:translate").Set((i, i, i), time=i / timeline.get_time_codes_per_seconds())

    timeline.set_current_time(0)
    timeline.set_end_time(100)
    timeline.set_looping(False)
    await omni.kit.app.get_app().next_update_async()

    return cube


def get_translate_x(prim):
    timeline = omni.timeline.get_timeline_interface()
    return round(prim.GetAttribute("xformOp:translate").Get(timeline.get_current_time())[0])


class FrameCounterWriter(rep.Writer):
    def __init__(self):
        self.annotators = ["rgb"]
        self.counter = 0

    def write(self, data):
        self.counter += 1


class TestOrchestrator(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)
        self.out_dir = os.path.join(carb.tokens.get_tokens_interface().resolve("${temp}"), "test_orchestrator")
        self.golden_dir = os.path.join(TEST_DATA_DIR, "golden")
        self._syncloads = carb.settings.get_settings().get("/rtx/materialDb/syncLoads")

    async def tearDown(self) -> None:
        carb.settings.get_settings().set("/rtx/materialDb/syncLoads", self._syncloads)
        carb.settings.get_settings().set("/app/asyncRendering", True)
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", False)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_looping(True)
        timeline.stop()
        timeline.commit()  # FIXME: Not threadsafe
        rep.orchestrator.set_capture_on_play(False)
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)
        await omni.usd.get_context().new_stage_async()

    async def test_step_fail(self):
        with self.assertRaises(rep.orchestrator.OrchestratorError):
            with rep.create.cube():
                rep.modify.pose(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)))
            rep.orchestrator.step()

    async def test_run_until_complete_fail(self):
        with self.assertRaises(rep.orchestrator.OrchestratorError):
            with rep.create.cube():
                rep.modify.pose(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)))
            rep.orchestrator.run_until_complete()

    async def test_step_next_rt_subframes(self):
        RT_SUBFRAMES = 5
        cube = rep.create.cube()
        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(rep.distribution.uniform((10, 10, 10), (15, 15, 15)))

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        asyncio.ensure_future(rep.orchestrator.step_async(rt_subframes=RT_SUBFRAMES))
        await omni.kit.app.get_app().next_update_async()

        # Assert at least RT_SUBFRAMES are rendered before frame is updated
        for _ in range(RT_SUBFRAMES):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(writer.counter, 0)

        # Wait for frame to reach post process graph
        while writer.counter == 0:
            await omni.kit.app.get_app().next_update_async()

        asyncio.ensure_future(rep.orchestrator.step_async(rt_subframes=RT_SUBFRAMES))
        for _ in range(RT_SUBFRAMES):
            self.assertEqual(writer.counter, 1)
            await omni.kit.app.get_app().next_update_async()

        # Wait for frame to reach post process graph
        while writer.counter == 1:
            await omni.kit.app.get_app().next_update_async()

    async def test_rt_subframe_simulation_playing(self):
        """Test orchestrator stepping with subframes while simulation is playing

        Ensure that RT subframes correctly pause a playing timeline
        """
        timeline = omni.timeline.get_timeline_interface()

        cube = await create_timeseries_cube_async(100)

        with rep.trigger.on_frame():
            pass

        timeline.play()
        timeline.commit()  # FIXME: Not threadsafe
        random.seed(1234)
        for i in range(0, 10):
            await rep.orchestrator.step_async(rt_subframes=random.randint(1, 20))
            self.assertEqual(get_translate_x(cube), i)

    async def test_rt_subframe_simulation_playing_physics(self):
        """Test orchestrator stepping with subframes while simulation is playing

        Ensure that RT subframes correctly pause a playing timeline
        """
        timeline = omni.timeline.get_timeline_interface()

        rep.functional.physics.create_physics_scene()
        await omni.kit.app.get_app().next_update_async()

        cube = rep.create.cube(position=(0, 100, 0))
        with cube:
            rep.physics.rigid_body()

        with rep.trigger.on_frame(interval=3, rt_subframes=10):
            pass

        rep.orchestrator.set_capture_on_play(True)
        await rep.orchestrator.run_async()

        stage = omni.usd.get_context().get_stage()
        cube_prim = stage.GetPrimAtPath("/Replicator/Cube_Xform")

        def get_translate_y(prim):
            return prim.GetAttribute("xformOp:translate").Get()[1]

        cur_pos = None
        for _ in range(3):
            await omni.kit.app.get_app().next_update_async()
            if cur_pos:
                self.assertNotEqual(get_translate_y(cube_prim), cur_pos)
            cur_pos = get_translate_y(cube_prim)

        # render subframes (paused)
        cur_pos = None
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
            if cur_pos:
                self.assertEqual(get_translate_y(cube_prim), cur_pos)
            cur_pos = get_translate_y(cube_prim)

        for _ in range(3):
            cur_pos = get_translate_y(cube_prim)
            await omni.kit.app.get_app().next_update_async()
            self.assertNotEqual(get_translate_y(cube_prim), cur_pos)

    async def test_start_async(self):
        self.assertEqual(rep.orchestrator.get_is_started(), False, "Orchestrator is already started")
        rep.create.sphere()
        await rep.orchestrator.run_async()
        self.assertEqual(
            rep.orchestrator.get_is_started(),
            True,
            f"Orchestrator did not start, status is `{rep.orchestrator.get_status()}`",
        )

    async def test_stop_async(self):
        rep.create.sphere()  # Need a replicator component to start
        await rep.orchestrator.run_async()
        self.assertEqual(
            rep.orchestrator.get_is_started(),
            True,
            f"Orchestrator did not start, status is `{rep.orchestrator.get_status()}`",
        )
        self.assertEqual(rep.orchestrator.get_is_stopped(), False, "Orchestrator is already stopped")
        await rep.orchestrator.stop_async()
        self.assertEqual(
            rep.orchestrator.get_is_stopped(),
            True,
            f"Orchestrator did not stop, status is `{rep.orchestrator.get_status()}`",
        )

    async def test_preview_async(self):
        sequence = [(2.0, 2.0, 2), (3.0, 3.0, 3.0), (4.0, 4.0, 4.0)]
        with rep.trigger.on_time():
            rep.create.sphere(scale=rep.distribution.sequence(sequence, name="preview_test", seed=123))

        stage = omni.usd.get_context().get_stage()
        sphere = stage.GetPrimAtPath("/Replicator/Sphere_Xform")

        for i in range(len(sequence)):
            await rep.orchestrator.preview_async()
            sphere_scale = sphere.GetAttribute("xformOp:scale").Get()
            self.assertEqual(sphere_scale, sequence[i])

    async def test_num_frames(self):
        num_frames = 5

        camera = rep.create.camera()
        rp = rep.create.render_product(camera, (256, 256))

        out_path = os.path.join(self.out_dir, "num_frames")
        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir=out_path, rgb=True)
        writer.attach(rp)

        with rep.trigger.on_frame():
            rep.create.cone(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)))

        await rep.orchestrator.run_until_complete_async(num_frames)

        num_files_generated = len(os.listdir(out_path))
        self.assertEqual(num_files_generated, num_frames + 1)  # + 1 to account for metadata file

    async def test_num_frames_1_capture_on_play(self):
        num_frames = 1

        camera = rep.create.camera()
        rp = rep.create.render_product(camera, (256, 256))
        rep.orchestrator.set_capture_on_play(True)

        out_path = os.path.join(self.out_dir, "num_frames")
        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir=out_path, rgb=True)
        writer.attach(rp)

        with rep.trigger.on_frame():
            rep.create.cone(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)))

        await rep.orchestrator.run_async(num_frames)
        await rep.orchestrator.wait_until_complete_async()

        num_files_generated = len(os.listdir(out_path))
        self.assertEqual(num_files_generated, num_frames + 1)  # + 1 to account for metadata file

    async def test_num_frames_capture_on_play_replay(self):
        num_frames = 5

        camera = rep.create.camera()
        rp = rep.create.render_product(camera, (256, 256))

        out_path = os.path.join(self.out_dir, "num_frames")
        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir=out_path, rgb=True)
        writer.attach(rp)

        rep.orchestrator.set_capture_on_play(True)

        with rep.trigger.on_frame():
            rep.create.cone(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)))

        await rep.orchestrator.run_until_complete_async(num_frames)

        num_files_generated = len(os.listdir(out_path))
        self.assertEqual(num_files_generated, num_frames + 1)  # + 1 to account for metadata file

        # Using "Play"
        carb.settings.get_settings().set(
            "/app/asyncRendering", False
        )  # HACK Frame fails to reach SdOnNewFrame when setting is set
        omni.timeline.get_timeline_interface().play()
        omni.timeline.get_timeline_interface().commit()
        await rep.orchestrator.wait_until_complete_async()

        num_files_generated = len(os.listdir(out_path))
        self.assertEqual(
            num_files_generated, (num_frames * 2 + 1), "Failed replay with play"
        )  # + 1 to account for metadata file

        # Using "run"
        await rep.orchestrator.run_async()
        await rep.orchestrator.wait_until_complete_async()

        num_files_generated = len(os.listdir(out_path))
        self.assertEqual(
            num_files_generated, (num_frames * 3 + 1), "Failed replay with run"
        )  # + 1 to account for metadata file

    async def test_num_frames_bounded(self):
        num_frames = 5
        bound = 3

        camera = rep.create.camera()
        rp = rep.create.render_product(camera, (256, 256))

        out_path = os.path.join(self.out_dir, "num_frames")
        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir=out_path, rgb=True)
        writer.attach(rp)

        with rep.trigger.on_frame(max_execs=bound):
            rep.create.cone(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)))

        await rep.orchestrator.run_until_complete_async(num_frames)

        num_files_generated = len(os.listdir(out_path))
        self.assertEqual(num_files_generated, bound + 1)  # + 1 to account for metadata file

    async def test_status_callback(self):
        rep.create.sphere()
        current_status = {"status": None}

        def status_callback(status, current_status):
            current_status["status"] = status

        # Register callback
        my_callback = rep.orchestrator.register_status_callback(lambda x, y=current_status: status_callback(x, y))

        await rep.orchestrator.run_async()
        self.assertEqual(
            current_status["status"],
            rep.orchestrator.Status.STARTED,
            f"Expected `Status.STARTED`, got `{current_status}`",
        )

        await rep.orchestrator.stop_async()
        self.assertEqual(
            current_status["status"],
            rep.orchestrator.Status.STOPPED,
            f"Expected `Status.STOPPED`, got `{current_status}`",
        )

        # Unregister callback
        del my_callback
        await rep.orchestrator.run_async()
        self.assertEqual(
            current_status["status"],
            rep.orchestrator.Status.STOPPED,
            f"Expected `Status.STOPPED`, got `{current_status}`",
        )

    async def test_zero_fps(self):
        stage = omni.usd.get_context().get_stage()
        timeline = omni.timeline.get_timeline_interface()

        timeline.set_time_codes_per_second(0.0)

        # Should not hang
        await rep.orchestrator.step_async()

        timeline.play()

    async def test_on_final_frame(self):
        num_frames = 5

        class TestWriter(rep.writers.Writer):
            def __init__(self, out_dir):
                self.out_dir = os.path.join(out_dir, "final_frame_test")
                self.backend = rep.BackendDispatch(output_dir=self.out_dir)
                self.annotators = ["rgb"]
                self.frame_id = 0
                self.num_out = 0
                self.final_seed_called = False

            def write(self, data):
                self.backend.schedule(io_functions.write_image, data=data["rgb"], path=f"img_{self.frame_id}.png")
                self.frame_id += 1

            def on_final_frame(self):
                if self.final_seed_called:
                    # Fail test if this is called twice
                    self.num_out = -1
                import time

                time.sleep(0.5)
                self.num_out = len(os.listdir(self.out_dir))
                self.final_seed_called = True

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = TestWriter(self.out_dir)
        writer.attach(rp)

        with rep.trigger.on_frame(max_execs=num_frames):
            pass

        await rep.orchestrator.run_until_complete_async()

        self.assertEqual(
            writer.num_out, num_frames + 1, f"`on_final_frames` saw {writer.num_out} files, expected {num_frames + 1}"
        )

    async def test_capture_on_timeline_play(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        await omni.kit.app.get_app().next_update_async()
        timeline.play()
        timeline.commit()  # FIXME: Not threadsafe
        while rep.orchestrator.get_status() != rep.orchestrator.Status.STARTED:
            await omni.kit.app.get_app().next_update_async()

        for i in range(1, 12):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(get_translate_x(cube), i, f"Timeseries cube is at {get_translate_x(cube)}, expected {i}")

        rep.orchestrator.stop()

        await rep.orchestrator.wait_until_complete_async()
        stopped_frames = 11
        self.assertEqual(
            writer.counter, stopped_frames, f"Writer counted {writer.counter} frames, expected {stopped_frames}"
        )

    async def test_capture_on_play_timeline_stop(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        timeline.play()
        timeline.commit()  # FIXME: Not threadsafe
        while rep.orchestrator.get_status() != rep.orchestrator.Status.STARTED:
            await omni.kit.app.get_app().next_update_async()

        for i in range(1, 6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(get_translate_x(cube), i)

        timeline.stop()
        timeline.commit()  # FIXME: Not threadsafe

        stopped_pos = get_translate_x(cube)
        # Now timeline should not increase
        for i in range(1, 6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube),
                stopped_pos,
                f"Timeseries cube is at {get_translate_x(cube)}, expected {stopped_pos}",
            )

        stopped_frames = 5
        self.assertEqual(
            writer.counter, stopped_frames, f"Writer counted {writer.counter} frames, expected {stopped_frames}"
        )

    async def test_capture_on_play_timeline_pause(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        timeline.play()
        timeline.commit()  # FIXME: Not threadsafe
        while rep.orchestrator.get_status() != rep.orchestrator.Status.STARTED:
            await omni.kit.app.get_app().next_update_async()

        for i in range(1, 6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube), i, f"Play: Timeseries cube is at {get_translate_x(cube)}, expected {i}"
            )

        timeline.pause()
        timeline.commit()  # FIXME: Not threadsafe

        paused_pos = get_translate_x(cube)
        paused_frames = 5
        # Now timeline should not increase
        for i in range(1, 6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube),
                paused_pos,
                f"Pause: Timeseries cube is at {get_translate_x(cube)}, expected {paused_pos}",
            )

        self.assertEqual(
            writer.counter, paused_frames, f"Play: Writer counted {writer.counter} frames, expected {paused_frames}"
        )

        timeline.play()
        timeline.commit()  # FIXME: Not threadsafe

        # Now timeline should resume
        for i in range(6, 12):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube), i, f"Resume: Timeseries cube is at {get_translate_x(cube)}, expected {i}"
            )

        rep.orchestrator.stop()

        await rep.orchestrator.wait_until_complete_async()
        stopped_frames = 11
        self.assertEqual(
            writer.counter, stopped_frames, f"Resume: Writer counted {writer.counter} frames, expected {stopped_frames}"
        )

    async def test_capture_on_replicator_play(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        await omni.kit.app.get_app().next_update_async()
        rep.orchestrator.run()
        while rep.orchestrator.get_status() != rep.orchestrator.Status.STARTED:
            await omni.kit.app.get_app().next_update_async()

        for i in range(12):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(get_translate_x(cube), i, f"Timeseries cube is at {get_translate_x(cube)}, expected {i}")

        rep.orchestrator.stop()

        await rep.orchestrator.wait_until_complete_async()
        stopped_frames = 12
        self.assertEqual(
            writer.counter, stopped_frames, f"Writer counted {writer.counter} frames, expected {stopped_frames}"
        )

    async def test_capture_on_replicator_step(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        for i in range(6):
            await rep.orchestrator.step_async()
            self.assertEqual(get_translate_x(cube), i, f"Timeseries cube is at {get_translate_x(cube)}, expected {i}")
            self.assertFalse(timeline.is_playing(), "Timeline is playing, expected it to be paused")

        paused_frames = 6
        self.assertEqual(
            writer.counter, paused_frames, f"Writer counted {writer.counter} frames, expected {paused_frames}"
        )

        rep.orchestrator.resume()

        # Now timeline should resume
        for i in range(5, 10):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube), i, f"Resume: Timeseries cube is at {get_translate_x(cube)}, expected {i}"
            )

        rep.orchestrator.stop()

        await rep.orchestrator.wait_until_complete_async()
        stopped_frames = 11
        self.assertEqual(
            writer.counter, stopped_frames, f"Resume: Writer counted {writer.counter} frames, expected {stopped_frames}"
        )

    async def test_capture_on_replicator_timeline_stop(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        rep.orchestrator.run()
        while rep.orchestrator.get_status() != rep.orchestrator.Status.STARTED:
            await omni.kit.app.get_app().next_update_async()

        for i in range(6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(round(get_translate_x(cube)), i)

        rep.orchestrator.stop()

        stopped_pos = get_translate_x(cube)
        # Now timeline should not increase
        for i in range(6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube),
                stopped_pos,
                f"Timeseries cube is at {get_translate_x(cube)}, expected {stopped_pos}",
            )

    async def test_capture_on_play_replicator_pause(self):
        """Test orchestrator does not interfere with FPS when playing and capturing
        without auto timeline updates
        """
        rep.orchestrator.set_capture_on_play(True)

        cube = await create_timeseries_cube_async(12)

        rp = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
        writer = FrameCounterWriter()
        writer.attach(rp)

        rep.orchestrator.run()
        while rep.orchestrator.get_status() != rep.orchestrator.Status.STARTED:
            await omni.kit.app.get_app().next_update_async()

        # First update captures frame 0.0
        for i in range(6):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube), i, f"Play: Timeseries cube is at {get_translate_x(cube)}, expected {i}"
            )

        rep.orchestrator.pause()

        paused_pos = get_translate_x(cube)
        paused_frames = 6
        # Now timeline should not increase
        for i in range(5):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube),
                paused_pos,
                f"Pause: Timeseries cube is at {get_translate_x(cube)}, expected {paused_pos}",
            )

        self.assertEqual(
            writer.counter, paused_frames, f"Play: Writer counted {writer.counter} frames, expected {paused_frames}"
        )

        rep.orchestrator.resume()

        # Now timeline should resume
        for i in range(5, 10):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                get_translate_x(cube), i, f"Resume: Timeseries cube is at {get_translate_x(cube)}, expected {i}"
            )

        rep.orchestrator.stop()

        await rep.orchestrator.wait_until_complete_async()
        stopped_frames = 11
        self.assertEqual(
            writer.counter, stopped_frames, f"Resume: Writer counted {writer.counter} frames, expected {stopped_frames}"
        )

    async def test_orchestrator_play_interference(self):
        settings = carb.settings.get_settings()
        settings.set("/rtx/materialDb/syncLoads", False)
        await omni.usd.get_context().new_stage_async()
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        await omni.kit.app.get_app().next_update_async()

        self.assertFalse(
            settings.get("/rtx/materialDb/syncLoads"),
            "Capture settings are set, expected capture settings NOT set.",
        )
        self.assertFalse(
            rep.orchestrator.get_is_started(), "Replicator is running. Expected replicator to remain Stopped."
        )

    async def test_orchestrator_play_capture_anno(self):
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        anno = rep.annotators.get("rgb")
        anno.attach(rp)
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        await omni.kit.app.get_app().next_update_async()

        settings = carb.settings.get_settings()
        self.assertTrue(
            settings.get("/rtx/materialDb/syncLoads"),
            "Capture settings are not set, expected capture settings set.",
        )
        self.assertTrue(rep.orchestrator.get_is_started(), "Replicator is stopped. Expected replicator to be running.")

    async def test_orchestrator_play_capture_rand(self):
        with rep.trigger.on_frame():
            rep.create.cone()
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        await omni.kit.app.get_app().next_update_async()

        settings = carb.settings.get_settings()
        self.assertTrue(
            settings.get("/rtx/materialDb/syncLoads"),
            "Capture settings are not set, expected capture settings set.",
        )
        self.assertTrue(rep.orchestrator.get_is_started(), "Replicator is stopped. Expected replicator to be running.")

    async def test_pt_motion_blur(self):
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        stage = omni.usd.get_context().get_stage()
        cube = stage.DefinePrim("/Cube", "Cube")
        cube.GetAttribute("size").Set(100)
        UsdGeom.Xformable(cube).AddTranslateOp()
        cube.GetAttribute("xformOp:translate").Set((-200, 0, 200), 0.0)
        cube.GetAttribute("xformOp:translate").Set((200, 0, -200), 12.0)
        timeline_iface.set_end_time(0.5)

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        rgb = rgb_anno.get_data()

        golden = np.array(Image.open(os.path.join(self.golden_dir, "pt_motionblur.png")))
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 1.1)

    async def test_pt_no_motion_blur(self):
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/rtx/rendermode", "PathTracing")
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", False)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        stage = omni.usd.get_context().get_stage()
        cube = stage.DefinePrim("/Cube", "Cube")
        cube.GetAttribute("size").Set(100)
        UsdGeom.Xformable(cube).AddTranslateOp()
        cube.GetAttribute("xformOp:translate").Set((-200, 0, 200), 0.0)
        cube.GetAttribute("xformOp:translate").Set((200, 0, -200), 12.0)
        timeline_iface.set_end_time(0.5)

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        rgb = rgb_anno.get_data()
        golden = np.array(Image.open(os.path.join(self.golden_dir, "no_motionblur.png")))
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 1.1)

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM, test takes too long on CI")
    async def test_pt_no_motion_blur_clampSpp_fixcrash(self):
        # to check fix for ISIM-1180

        carb.settings.get_settings().set("/rtx/rendermode", "PathTracing")
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", False)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")

        camera = rep.create.camera(name=f"Camera_default_camera", position=(0, 0, 0), rotation=(0, 0, 0))
        rp = rep.create.render_product(camera, (3840, 2160))
        await rep.orchestrator.step_async()

    async def test_pt_motion_blur_delta_time_large(self):
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        stage = omni.usd.get_context().get_stage()
        cube = rep.create.cube()

        with cube:
            rep.physics.rigid_body()

        with rep.trigger.on_time(interval=0.125, max_execs=1):
            pass

        await rep.orchestrator.step_async(delta_time=1)
        await rep.orchestrator.step_async(delta_time=1)
        rgb = rgb_anno.get_data()

        golden = np.array(
            Image.open(os.path.join(self.golden_dir, "pt_motionblur_delta_time_large.png"))
        )  # Physics should step because delta time is larger than physx's step time
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 1.1)

    async def test_pt_motion_blur_user_settings_1(self):
        # test when /pathTracedMotionBlurSubSamples is not set and the spp and totalSpp are user defined
        # should subframes per frame should be totalSpp / spp
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        carb.settings.get_settings().set("/rtx/pathtracing/spp", 6)
        carb.settings.get_settings().set("/rtx/pathtracing/totalSpp", 72)

        cube = rep.create.cube()

        with cube:
            rep.physics.rigid_body()

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async(
            delta_time=0.5
        )  # this is capped based on the totalSpp/spp 72/6, so making it higher than 0.5 doesn't make a difference
        await rep.orchestrator.step_async(delta_time=0.5)

        # subframes per frame should be 12 provide totalSpp=72, spp=6.
        rgb = rgb_anno.get_data()

        golden = np.array(
            Image.open(os.path.join(self.golden_dir, "pt_motionblur_usersettings_1.png"))
        )  # Physics should step because delta time is larger than physx's step time
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 0.6)

    async def test_pt_motion_blur_user_settings_2(self):
        # test if you have /pathTracedMotionBlurSubSamples defined, spp stays the same, totalSpp is overwritted by
        # spp * /pathTracedMotionBlurSubSamples
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().set("/omni/replicator/pathTracedMotionBlurSubSamples", 18)
        carb.settings.get_settings().set("/rtx/pathtracing/spp", 6)
        carb.settings.get_settings().set("/rtx/pathtracing/totalSpp", 72)

        cube = rep.create.cube()

        with cube:
            rep.physics.rigid_body()

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async(
            delta_time=1.0
        )  # this is capped based on the totalSpp/spp 144/6, so making it higher than 1.0 doesn't make a difference
        await rep.orchestrator.step_async(delta_time=1.0)

        # subframes per frame should be 18 provide pathTracedMotionBlurSubSamples=18, totalSpp=72, spp=6.
        rgb = rgb_anno.get_data()

        golden = np.array(
            Image.open(os.path.join(self.golden_dir, "pt_motionblur_usersettings_2.png"))
        )  # Physics should step because delta time is larger than physx's step time
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 0.6)

    async def test_pt_motion_blur_spp_quality(self):
        # created based on JIRA ISIM-974 to ensure user can control quality of image via setting spp
        motion_blur_step_duration = [None]
        for custom_delta_time in motion_blur_step_duration:
            repsubsamps = [3]
            pt_spp_totalspps = [[1, 1], [4, 4]]  # 416 fails totalSpp 408 is OK
            for repsubsamp in repsubsamps:
                for pt_spp_totalspp in pt_spp_totalspps:
                    rgb_arr = await run_motion_blur_example_async(
                        custom_delta_time=custom_delta_time,
                        pt_subsamples=repsubsamp,
                        pt_spp=pt_spp_totalspp[0],
                        pt_totalspp=pt_spp_totalspp[1],
                    )
                    im_name = (
                        f"pt_motionblur_{repsubsamp}repsubsamp_{pt_spp_totalspp[0]}spp_{pt_spp_totalspp[1]}totalspp.png"
                    )

                    golden = np.array(
                        Image.open(os.path.join(self.golden_dir, im_name))
                    )  # Physics should step because delta time is larger than physx's step time
                    std_dev = np.sqrt(np.square(rgb_arr - golden).astype(float).mean())
                    # self.assertLess(std_dev, 1.1, f"Data does not match golden file {im_name}.")

    async def test_pt_motion_blur_repsubsamps(self):
        # created based on JIRA ISIM-974 to ensure user can control number of images stitched per frame (i.e. subsamples)
        motion_blur_step_duration = [None]
        for custom_delta_time in motion_blur_step_duration:
            repsubsamps = [3, 6]
            pt_spp_totalspps = [[4, 4]]  # 416 fails totalSpp 408 is OK
            for repsubsamp in repsubsamps:
                for pt_spp_totalspp in pt_spp_totalspps:
                    rgb_arr = await run_motion_blur_example_async(
                        custom_delta_time=custom_delta_time,
                        pt_subsamples=repsubsamp,
                        pt_spp=pt_spp_totalspp[0],
                        pt_totalspp=pt_spp_totalspp[1],
                    )
                    im_name = (
                        f"pt_motionblur_{repsubsamp}repsubsamp_{pt_spp_totalspp[0]}spp_{pt_spp_totalspp[1]}totalspp.png"
                    )

                    golden = np.array(
                        Image.open(os.path.join(self.golden_dir, im_name))
                    )  # Physics should step because delta time is larger than physx's step time
                    std_dev = np.sqrt(np.square(rgb_arr - golden).astype(float).mean())
                    self.assertLess(std_dev, 3.0, f"Data does not match golden file {im_name}.")

    async def test_pt_motion_blur_repsubsamps_2(self):
        # created based on JIRA ISIM-974 to ensure user can control number of images stitched per frame (i.e. subsamples)
        # ensures that the subsamples is computed from spp+total spp if user doesn't define it otherwise
        motion_blur_step_duration = [None]
        for custom_delta_time in motion_blur_step_duration:
            repsubsamps = [None, 3]
            pt_spp_totalspps = [[4, 16]]  # 416 fails totalSpp 408 is OK
            for repsubsamp in repsubsamps:
                for pt_spp_totalspp in pt_spp_totalspps:
                    rgb_arr = await run_motion_blur_example_async(
                        custom_delta_time=custom_delta_time,
                        pt_subsamples=repsubsamp,
                        pt_spp=pt_spp_totalspp[0],
                        pt_totalspp=pt_spp_totalspp[1],
                    )
                    im_name = (
                        f"pt_motionblur_{repsubsamp}repsubsamp_{pt_spp_totalspp[0]}spp_{pt_spp_totalspp[1]}totalspp.png"
                    )

                    golden = np.array(
                        Image.open(os.path.join(self.golden_dir, im_name))
                    )  # Physics should step because delta time is larger than physx's step time
                    std_dev = np.sqrt(np.square(rgb_arr - golden).astype(float).mean())
                    self.assertLess(std_dev, 3.0, f"Data does not match golden file {im_name}.")

    async def test_pt_motion_blur_to_rt_perframe(self):
        # created based on JIRA ISIM-972 to ensure user can switch back and forth per frame between pathtracing+motion blur and raytracing
        # Capture motion blur by combining the number of pathtraced subframes samples simulated for the given duration

        scenarios = [
            # (timeline_fps, physics_fps, num_frames, delta_time)
            (None, None, 4, 1 / 60),
        ]

        for i, scenario in enumerate(scenarios):
            timeline_fps, physics_fps, num_frames, delta_time = scenario
            await setup_stage_physx_anim(timeline_fps=timeline_fps, physics_fps=physics_fps)

            # Setup replicator writer
            carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)

            camera = rep.create.camera(position=(0, 1.5, -0.3), look_at=(0, 0, -0.3), name="MotionBlurCam")
            render_product = rep.create.render_product(camera, (960, 540))
            rgb_anno = rep.annotators.get("rgb")
            rgb_anno.attach(render_product)

            # Run a few updates to make sure all materials are fully loaded for capture
            for i in range(10):
                await omni.kit.app.get_app().next_update_async()
                await asyncio.sleep(0.05)

            stage = omni.usd.get_context().get_stage()
            timeline = omni.timeline.get_timeline_interface()
            for prim in stage.Traverse():
                if prim.IsA(UsdPhysics.Scene):
                    physx_scene = PhysxSchema.PhysxSceneAPI.Apply(prim)
                    break

            await rep.orchestrator.preview_async()
            for idx in range(num_frames):
                timeline.play()
                if idx % 2 == 0:
                    await capture_with_motion_blur_and_pathtracing_async(duration=0.025, num_samples=8, spp=16)
                else:
                    await rep.orchestrator.step_async(delta_time=delta_time)
                timeline.pause()
                rgb_arr = rgb_anno.get_data()
                im_name = f"pt_motionblur_to_rt_perframe_{idx}.png"

                golden = np.array(
                    Image.open(os.path.join(self.golden_dir, im_name))
                )  # Physics should step because delta time is larger than physx's step time
                std_dev = np.sqrt(np.square(rgb_arr - golden).astype(float).mean())
                self.assertLess(std_dev, 2.5, f"Data does not match golden file {im_name}.")

    async def test_pt_motion_blur_delta_time_small(self):
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        stage = omni.usd.get_context().get_stage()
        cube = rep.create.cube()

        with cube:
            rep.physics.rigid_body()

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async(delta_time=0.05)
        await rep.orchestrator.step_async(delta_time=0.05)
        rgb = rgb_anno.get_data()

        golden = np.array(
            Image.open(os.path.join(self.golden_dir, "pt_motionblur_delta_time_small.png"))
        )  # Physics should not step because delta time is smaller than physx's step time
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 1.1)

    async def test_pt_motion_blur_subsamples(self):
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        carb.settings.get_settings().set("/omni/replicator/pathTracedMotionBlurSubSamples", 16)
        carb.settings.get_settings().set("/rtx/pathtracing/totalSpp", 1)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_pathtraced(samples_per_pixel=64)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        stage = omni.usd.get_context().get_stage()
        cube = rep.create.cube()

        with cube:
            rep.physics.rigid_body()

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async(delta_time=0.25)
        await rep.orchestrator.step_async(delta_time=0.25)
        await rep.orchestrator.step_async(delta_time=0.25)
        await rep.orchestrator.step_async(delta_time=0.25)
        rgb = rgb_anno.get_data()

        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")

        golden = np.array(
            Image.open(os.path.join(self.golden_dir, "pt_motionblur_subsamples.png"))
        )  # Physics should step because MotionBlurSubSamples is smaller.
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 1.1)

    async def test_rt_motion_blur(self):
        timeline = omni.timeline.get_timeline_interface()
        rep.orchestrator.set_capture_on_play(True)
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        await omni.kit.app.get_app().next_update_async()
        rep.settings.set_render_rtx_realtime()
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        stage = omni.usd.get_context().get_stage()
        cube = stage.DefinePrim("/Cube", "Cube")
        cube.GetAttribute("size").Set(200)
        UsdGeom.Xformable(cube).AddTranslateOp()
        cube.GetAttribute("xformOp:translate").Set((-200, 0, 200), 0.0)
        cube.GetAttribute("xformOp:translate").Set((200, 0, -200), 12.0)
        timeline_iface.set_end_time(0.5)

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        rgb = rgb_anno.get_data()
        golden_file_path = os.path.join(self.golden_dir, "rt_motionblur.png")
        golden = np.array(Image.open(golden_file_path))
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        if std_dev > 1.005:
            # Uncomment for local debugging
            # Image.fromarray(rgb).save(os.path.join(os.path.dirname(__file__), "testoutput_rt_motionblur.png"))
            if omni.kit.test.utils.is_running_in_teamcity():
                tc_output_image_comparison("rt_motionblur", golden_file_path, self.out_dir, rgb)
            if omni.kit.test.utils.is_running_in_gitlab():
                gitlab_output_image_comparison("rt_motionblur", golden_file_path, image_data=rgb)
        self.assertLess(std_dev, 1.005)

        t1 = timeline.get_current_time()
        await rep.orchestrator.step_async(delta_time=1 / 60.0)
        await rep.orchestrator.step_async(delta_time=1 / 60.0)
        t2 = timeline.get_current_time()
        self.assertTrue(np.abs(t2 - t1 - 1.0 / 30) < 0.001)

    async def test_rt_no_motion_blur(self):
        rep.orchestrator.set_capture_on_play(True)
        rgb_anno = rep.annotators.get("rgb")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        rgb_anno.attach(rp)

        rep.create.light(light_type="distant", rotation=(315, 0, 0))
        rep.settings.set_render_rtx_realtime()
        rep.settings.carb_settings("/rtx/sceneDb/ambientLightIntensity", 0.0)
        timeline_iface = omni.timeline.acquire_timeline_interface()
        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", False)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")
        stage = omni.usd.get_context().get_stage()
        cube = stage.DefinePrim("/Cube", "Cube")
        cube.GetAttribute("size").Set(100)
        UsdGeom.Xformable(cube).AddTranslateOp()
        cube.GetAttribute("xformOp:translate").Set((-200, 0, 200), 0.0)
        cube.GetAttribute("xformOp:translate").Set((200, 0, -200), 12.0)
        timeline_iface.set_end_time(0.5)

        with rep.trigger.on_time(interval=0.5, max_execs=1):
            pass

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        rgb = rgb_anno.get_data()
        golden = np.array(Image.open(os.path.join(self.golden_dir, "no_motionblur.png")))
        std_dev = np.sqrt(np.square(rgb - golden).astype(float).mean())
        self.assertLess(std_dev, 1.1)

    async def test_pt_motion_blur_timeline_advance(self):
        # created based on JIRA ISIM-973 fixes
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()
        timeline = omni.timeline.get_timeline_interface()
        # Add a distant light to the empty stage
        distant_light = stage.DefinePrim("/World/Lights/DistantLight", "DistantLight")
        distant_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(400.0)
        if not distant_light.HasAttribute("xformOp:rotateXYZ"):
            UsdGeom.Xformable(distant_light).AddRotateXYZOp()
        distant_light.GetAttribute("xformOp:rotateXYZ").Set((0, 60, 0))

        carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)
        carb.settings.get_settings().destroy_item("/omni/replicator/pathTracedMotionBlurSubSamples")

        # NOTE: timeline works path tracing is commented out
        rep.settings.set_render_pathtraced(32)

        if not timeline.is_playing():
            timeline.play()
        # NOTE: timeline works if step is commented out
        await rep.orchestrator.step_async(pause_timeline=False)
        if not timeline.is_playing():
            timeline.play()
        for i in range(10):
            last_time = timeline.get_current_time()
            await omni.kit.app.get_app().next_update_async()
            self.assertTrue(timeline.get_current_time() - last_time > 0.01)
            # print(f"\t [{i}] time: {timeline.get_current_time():.2f}")

        if not timeline.is_playing():
            timeline.play()
        # NOTE: timeline works if step is commented out
        await rep.orchestrator.step_async(pause_timeline=False)
        if not timeline.is_playing():
            timeline.play()
        for i in range(10):
            last_time = timeline.get_current_time()
            await omni.kit.app.get_app().next_update_async()
            # print(f"\t [{i}] time: {timeline.get_current_time():.2f}")
            self.assertTrue(timeline.get_current_time() - last_time > 0.01)

    async def test_run_and_wait_async(self):
        NUM_FRAMES = 10
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        cube = rep.create.cube(position=(0, 0, 0))
        with rep.trigger.on_frame(max_execs=NUM_FRAMES):
            with cube:
                rep.randomizer.rotation()
        await rep.orchestrator.run_async()
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_run_and_wait_capture_on_play_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", True)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        cube = rep.create.cube(position=(0, 0, 0))
        with rep.trigger.on_frame(max_execs=NUM_FRAMES):
            with cube:
                rep.randomizer.rotation()
        await rep.orchestrator.run_async()
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_run_and_wait_capture_on_play_num_frames_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", True)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        await rep.orchestrator.run_async(num_frames=NUM_FRAMES)
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_run_and_wait_num_frames_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        await rep.orchestrator.run_async(num_frames=NUM_FRAMES)
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

        writer.detach()
        rp.destroy()

        await rep.orchestrator.wait_until_complete_async()

    async def test_run_until_complete_num_frames_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        await rep.orchestrator.run_until_complete_async(num_frames=NUM_FRAMES)

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_run_until_complete_capture_on_play_num_frames_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", True)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        await rep.orchestrator.run_until_complete_async(num_frames=NUM_FRAMES)

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_step_and_wait_num_frames_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        for _ in range(NUM_FRAMES):
            await rep.orchestrator.step_async()
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_step_and_wait_capture_on_play_num_frames_async(self):
        NUM_FRAMES = 20
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", True)
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = FrameCounterWriter()
        writer.attach([rp])
        for _ in range(NUM_FRAMES):
            await rep.orchestrator.step_async()
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(writer.counter, NUM_FRAMES, f"Writer recorded {writer.counter} frames out of {NUM_FRAMES}.")

    async def test_step_delta_time(self):
        # Test that step will step the amount of delta time specified.
        async def run_delta_time_step_async(play_timeline=False, delta_times=[]):
            await omni.usd.get_context().new_stage_async()
            carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
            timeline = omni.timeline.get_timeline_interface()
            timeline.set_end_time(1000.0)
            timeline.set_looping(False)
            # Weird quirk, new stage only resets the timeline to 0.0 if timeline is paused, not when it's stopped
            timeline.set_current_time(0.0)
            timeline.stop()
            timeline.commit_silently()

            if play_timeline:
                timeline.play()

            default_step_size = 1 / timeline.get_time_codes_per_seconds()

            expected_time = 0.0
            for i, delta_time in enumerate(delta_times):
                if delta_time is not None:
                    expected_time += delta_time
                elif i > 0 and play_timeline:
                    expected_time += default_step_size
                await rep.orchestrator.step_async(delta_time=delta_time)
                self.assertAlmostEqual(timeline.get_current_time(), expected_time, places=3)

        delta_times = [0.0, 0.0, 0.001, 0.001, 1.0, 0.0, 0.0, 24.0, 6.0, 12.1]
        await run_delta_time_step_async(play_timeline=False, delta_times=delta_times)
        await run_delta_time_step_async(play_timeline=True, delta_times=delta_times)

        delta_times = [None, None, 0.0, 0.0, 0.001, 0.001, 1.0, 0.0, 0.0, 24.0, 6.0, 12.1, None, None]
        await run_delta_time_step_async(play_timeline=False, delta_times=delta_times)
        await run_delta_time_step_async(play_timeline=True, delta_times=delta_times)

    async def test_step_pause_timeline(self):
        with rep.trigger.on_frame():
            rep.create.cube()

        timeline = omni.timeline.get_timeline_interface()
        timeline.set_time_codes_per_second(1)
        timeline.set_end_time(1000)
        timeline.stop()

        await rep.orchestrator.step_async(pause_timeline=True)
        self.assertFalse(timeline.is_playing(), "Expected timeline to not be playing, but it is.")
        self.assertAlmostEqual(timeline.get_current_time(), 0.0)

        # Repeat to ensure timeline isn't resumed
        await rep.orchestrator.step_async(pause_timeline=True)
        self.assertFalse(timeline.is_playing(), "Expected timeline to not be playing, but it is.")
        self.assertAlmostEqual(timeline.get_current_time(), 0.0)

        timeline.play()

        await rep.orchestrator.step_async(pause_timeline=False)
        self.assertTrue(timeline.is_playing(), "Expected timeline to continue playing, but it is not.")
        self.assertAlmostEqual(timeline.get_current_time(), 1.0)

        await rep.orchestrator.step_async(pause_timeline=True)
        self.assertFalse(timeline.is_playing(), "Expected timeline to not be playing, but it is.")
        self.assertAlmostEqual(timeline.get_current_time(), 2.0)

    async def test_pt_single_frame_render(self):
        cube = rep.create.cube()
        orc = rep.orchestrator._orchestrator

        rep.settings.set_render_pathtraced(4)
        carb.settings.get_settings().set("/rtx/pathtracing/spp", 4)

        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(position=(100, 0, 0))

        self.assertEqual(orc._get_pt_subframes_per_frame(), 1)

        await rep.orchestrator.run_async()
        await omni.kit.app.get_app().next_update_async()

        cur_time_to_write = orc._sim_times_to_write[0]
        cur_time = cur_time_to_write[0] * 30 // cur_time_to_write[1]

        await omni.kit.app.get_app().next_update_async()

        new_time_to_write = orc._sim_times_to_write[1]
        new_time = new_time_to_write[0] * 30 // new_time_to_write[1]

        self.assertAlmostEqual(new_time, cur_time + 1)

    async def test_multi_run_pt(self):
        # OMPE-32546 - Replicator sets totalSPP to 1 when running through multiple iterations
        spp = 2
        rep.settings.set_render_pathtraced(spp)
        for _ in range(2):
            rep.orchestrator.run()
            await rep.orchestrator.step_async()
            self.assertEqual(carb.settings.get_settings().get("/rtx/pathtracing/totalSpp"), spp)

    async def test_delta_time_capture_on_play(self):
        rep.orchestrator.set_capture_on_play(True)
        timeline = omni.timeline.get_timeline_interface()

        self.assertAlmostEqual(timeline.get_current_time(), 0.0)
        await rep.orchestrator.step_async(delta_time=0.0)
        self.assertAlmostEqual(timeline.get_current_time(), 0.0)
        await rep.orchestrator.step_async(delta_time=0.0)
        self.assertAlmostEqual(timeline.get_current_time(), 0.0)
        await rep.orchestrator.step_async(delta_time=0.0)
        self.assertAlmostEqual(timeline.get_current_time(), 0.0)
        await rep.orchestrator.step_async(delta_time=0.1)
        self.assertAlmostEqual(timeline.get_current_time(), 0.1)
        await rep.orchestrator.step_async(delta_time=0.4)
        self.assertAlmostEqual(timeline.get_current_time(), 0.5)

    async def test_all_frames_generated_timeline_play(self):
        num_frames = 2
        rep.orchestrator.set_capture_on_play(False)
        rep.create.light()
        rep.create.cube()

        render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        basic_writer = rep.writers.get("BasicWriter")
        basic_writer.initialize(output_dir=self.out_dir, rgb=True)

        # One less frame written
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        await omni.kit.app.get_app().next_update_async()
        timeline.pause()

        # Ensure this works if writer attached after timeline is played
        basic_writer.attach(render_product)

        for _ in range(num_frames):
            await rep.orchestrator.step_async()
        await rep.orchestrator.wait_until_complete_async()

        self.assertEqual(len(os.listdir(self.out_dir)), num_frames + 1)  # 5 frames + 1 for the metadata file

    async def test_attach_writer_after_timeline_play(self):
        rep.orchestrator.set_capture_on_play(False)
        rep.create.cube()

        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        timeline.commit_silently()

        render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir=self.out_dir, rgb=True)
        writer.attach(render_product)

        num_warmup_steps = 3
        num_steps = 2

        for _ in range(num_warmup_steps):
            await omni.kit.app.get_app().next_update_async()

        # Expect no files written
        await rep.orchestrator.wait_until_complete_async()
        self.assertEqual(len(os.listdir(self.out_dir)), 0)

        for _ in range(num_steps):
            await rep.orchestrator.step_async()

        # Expect 3 RGB images and 1 metadata file
        await rep.orchestrator.wait_until_complete_async()
        self.assertEqual(len(os.listdir(self.out_dir)), num_steps + 1)

    async def test_capture_on_play_timeline_pause_writer_attached(self):
        """Ensure that with a writer attached, the timeline remains paused. (NVB-5373123)"""
        rep.orchestrator.set_capture_on_play(True)
        writer = FrameCounterWriter()
        writer.attach(rep.create.render_product("/OmniverseKit_Persp", (512, 512)))

        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        timeline.commit()
        self.assertEqual(timeline.is_playing(), True, "Timeline should be playing.")
        await omni.kit.app.get_app().next_update_async()
        timeline.pause()
        timeline.commit()

        self.assertEqual(timeline.is_playing(), False, "Timeline should be paused, but is playing.")

        # Ensure timeline remains paused
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(timeline.is_playing(), False, f"Timeline should be paused, but is playing at step {i}.")

        # Ensure writer recorded just one frame
        self.assertEqual(writer.counter, 1)

    async def test_no_root_deltas(self):
        """Ensure no root deltas are created when replicator is running"""
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        anno = rep.annotators.get("rgb")
        anno.attach(rp)
        await rep.orchestrator.step_async()

        # Check that no root deltas are created
        stage = omni.usd.get_context().get_stage()
        self.assertFalse(stage.GetRootLayer().GetPrimAtPath("/Render/PostProcess/SDGPipeline/DispatchSync"))
        self.assertTrue(stage.GetSessionLayer().GetPrimAtPath("/Render/PostProcess/SDGPipeline/DispatchSync"))

    async def test_async_rendering_restore(self):
        """Ensure async rendering is restored correctly when Replicator is re-started"""
        with rep.trigger.on_frame(max_execs=3):
            pass

        await rep.orchestrator.run_until_complete_async()

        # async rendering restore is delayed to prevent hang
        self.assertFalse(carb.settings.get_settings().get("/app/asyncRendering"))

        # Run immediately again
        await rep.orchestrator.run_until_complete_async()

        # Wait NUM_FRAMES_ASYNC_RENDERING_DELAY frames
        for _ in range(rep.orchestrator.NUM_FRAMES_ASYNC_RENDERING_DELAY):
            await omni.kit.app.get_app().next_update_async()

        # After NUM_FRAMES_ASYNC_RENDERING_DELAY frames, async rendering should be restored
        self.assertTrue(carb.settings.get_settings().get("/app/asyncRendering"))
