# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
import omni.kit.app
import omni.usd

from pxr import Usd, UsdGeom, Gf, Sdf


class TestNoGPUStartup(omni.kit.test.AsyncTestCase):

    async def check_no_gpu_extensions(self):
        # Check that the GPU extensions are not enabled
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        enabled_exts = {ext["name"] for ext in ext_manager.get_extensions() if ext["enabled"]}
        self.assertNotIn("omni.gpu_foundation", enabled_exts)
        self.assertNotIn("omni.gpucompute.plugins", enabled_exts)
        self.assertNotIn("omni.rtx.shadercache.d3d12", enabled_exts)
        self.assertNotIn("omni.rtx.shadercache.vulkan", enabled_exts)
        self.assertNotIn("carb.windowing.plugins", enabled_exts)

    def startup_gpu_foundation(self):
        import omni.gpu_foundation_factory

        foundation_factory = omni.gpu_foundation_factory.get_gpu_foundation_factory_interface()
        foundation_factory.startup_gpu_foundation()

    async def check_new_usd_stage(self):
        NUM_EDITS = 5
        WAITS_BEFORE_EDITS = 3

        def index_to_axis(i: int):
            return tuple(int(i == a) for a in range(3))


        def edit_scene(frame: int, spheres):
            for i, sphere in enumerate(spheres):
                axis = Gf.Vec3d(index_to_axis(i))
                UsdGeom.XformCommonAPI(sphere).SetTranslate(axis * frame)


        def create_sphere_scene(usd_context: omni.usd.UsdContext):
            stage = usd_context.get_stage()
            stage.DefinePrim("/World", "Xform")
            spheres = (UsdGeom.Sphere.Define(stage, f"/World/Sphere{axis}").GetPrim() for axis in ("X", "Y", "Z"))
            for i, sphere in enumerate(spheres):
                sphere.GetAttribute("radius").Set(20)
                sphere.CreateAttribute("primvars:displayColor", Sdf.ValueTypeNames.Color3fArray).Set([index_to_axis(i)])

            return spheres

        app = omni.kit.app.get_app()

        # Create new usd stage with spheres,edit it, and close it
        # (it shouldn't produce any errors or crash)
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        spheres = create_sphere_scene(usd_context)
        for i in range(NUM_EDITS):
            edit_scene(i, spheres)
            for _ in range(WAITS_BEFORE_EDITS):
                await app.next_update_async()

        await usd_context.close_stage_async()

    async def startup_gpu_extensions(self):
        engine_name = "pxr"
        usd_context = omni.usd.get_context()
        ext_manager = omni.kit.app.get_app().get_extension_manager()

        # omni.gpucompute.plugins requires omni.gpu_foundation too, so enable it
        # and start it up manually
        ext_manager.set_extension_enabled_immediate("omni.gpu_foundation", True)
        self.startup_gpu_foundation()

        ext_manager.set_extension_enabled_immediate("carb.windowing.plugins", True)
        ext_manager.set_extension_enabled_immediate("omni.gpucompute.plugins", True)

        # Enable the hydra engine and add it to the USD context
        ext_manager.set_extension_enabled_immediate(f"omni.hydra.{engine_name}", True)
        omni.usd.create_hydra_engine(engine_name, usd_context)

    async def test_no_gpu_extensions(self):
        await self.check_no_gpu_extensions()

        # GPU extensions can be defer enabled, try that:
        await self.startup_gpu_extensions()
        await self.check_new_usd_stage()
