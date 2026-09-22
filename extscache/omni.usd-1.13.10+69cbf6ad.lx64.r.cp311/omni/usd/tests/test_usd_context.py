# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TestBBoxCache", "TestUsdContext"]

import carb
import omni.kit.app
import omni.kit.test
import omni.timeline
import omni.usd
import tempfile

from pathlib import Path
from pxr import Gf, Sdf, Usd, UsdGeom


class TestBBoxCache(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._usd_context = omni.usd.get_context()
        self._timeline = omni.timeline.get_timeline_interface()

    async def setUp(self):
        await self._usd_context.new_stage_async()

    async def tearDown(self):
        await self._usd_context.close_stage_async()

    async def test_compute_path_world_bounding_box(self):
        stage = self._usd_context.get_stage()

        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)

        # the "purpose" of the prims should all be "default"
        xform = stage.DefinePrim("/xform", "Xform")
        cube = stage.DefinePrim("/xform/cube", "Cube")
        cube_extent = UsdGeom.Boundable.ComputeExtentFromPlugins(UsdGeom.Boundable(cube), Usd.TimeCode.Default())
        cube_range = Gf.Range3d(Gf.Vec3d(cube_extent[0]), Gf.Vec3d(cube_extent[1]))

        xform_xform_api = UsdGeom.XformCommonAPI(xform)
        cube_xform_api = UsdGeom.XformCommonAPI(cube)

        def test_match(prim: Usd.Prim, expected_value: Gf.Range3d):
            epsilon = 1e-6
            usd_context_bound = self._usd_context.compute_path_world_bounding_box(prim.GetPath().pathString)
            bbox_cache_bound = bbox_cache.ComputeWorldBound(prim).ComputeAlignedRange()

            self.assertTrue(Gf.IsClose(Gf.Vec3d(*usd_context_bound[0]), bbox_cache_bound.GetMin(), epsilon))
            self.assertTrue(Gf.IsClose(Gf.Vec3d(*usd_context_bound[1]), bbox_cache_bound.GetMax(), epsilon))
            self.assertTrue(Gf.IsClose(expected_value.GetMin(), bbox_cache_bound.GetMin(), epsilon))
            self.assertTrue(Gf.IsClose(expected_value.GetMax(), bbox_cache_bound.GetMax(), epsilon))

        # Verify the initial state is correct:
        test_match(xform, cube_range)
        test_match(cube, cube_range)

        # TEST 1: Parent prim's transform affects child prim's world bound
        offset = Gf.Vec3d(10, 0, 0)
        xform_xform_api.SetTranslate(offset)

        bbox_cache.Clear()
        expected_bound = Gf.Range3d(cube_range.GetMin() + offset, cube_range.GetMax() + offset)

        test_match(xform, expected_bound)
        test_match(cube, expected_bound)

        # TEST 2: child prim's transform affect parent's world bound (if parent itself does not have an authored extent)
        xform_xform_api.SetTranslate((0, 0, 0))  # reset xform prim's translation

        cube_xform_api.SetTranslate(offset)

        bbox_cache.Clear()
        expected_bound = Gf.Range3d(cube_range.GetMin() + offset, cube_range.GetMax() + offset)

        test_match(xform, expected_bound)
        test_match(cube, expected_bound)

        # TEST 3: child prim's "extent" attribute affect parent's world bound (if parent itself does not have an authored extent)
        cube_xform_api.SetTranslate((0, 0, 0))  # reset cube prim's translation
        new_extent = [(-100, -100, -100), (100, 100, 100)]

        cube.GetPrim().GetAttribute("extent").Set(new_extent)

        bbox_cache.Clear()
        expected_bound = Gf.Range3d(*new_extent)

        test_match(xform, expected_bound)
        test_match(cube, expected_bound)

        # TEST 4: timecode change parent transform
        self._timeline.set_current_time(0.0)
        time_code = Usd.TimeCode(stage.GetTimeCodesPerSecond() * 2)
        xform_offset = (0, 10, 0)
        xform_xform_api.SetTranslate((0, 0, 0), Usd.TimeCode(0))
        xform_xform_api.SetTranslate(xform_offset, time_code)

        bbox_cache.Clear()

        # authored transform at new time should not affect current result
        test_match(xform, expected_bound)
        test_match(cube, expected_bound)

        self._timeline.set_current_time(2.0)

        # UsdContext has one frame of delay when setting current time
        # the bound won't match if not await.
        # Should this be considered as a bug or expected behavior?
        await omni.kit.app.get_app().next_update_async()

        bbox_cache.Clear()
        bbox_cache.SetTime(time_code)
        expected_bound = Gf.Range3d(*[Gf.Vec3d(ext) + xform_offset for ext in new_extent])

        test_match(xform, expected_bound)
        test_match(cube, expected_bound)

        # TEST 5: timecode change child extent
        self._timeline.set_current_time(0.0)
        bbox_cache.Clear()
        bbox_cache.SetTime(Usd.TimeCode.Default())
        await omni.kit.app.get_app().next_update_async()

        cube.GetPrim().GetAttribute("extent").Set(new_extent, Usd.TimeCode(0))

        new_extent_at_time = [(-200, -200, -200), (200, 200, 200)]
        cube.GetPrim().GetAttribute("extent").Set(new_extent_at_time, time_code)

        self._timeline.set_current_time(2.0)

        # UsdContext has one frame of delay when setting current time
        # the bound won't match if not await.
        # Should this be considered as a bug or expected behavior?
        await omni.kit.app.get_app().next_update_async()

        bbox_cache.Clear()
        bbox_cache.SetTime(time_code)

        expected_bound = Gf.Range3d(*[Gf.Vec3d(ext) + xform_offset for ext in new_extent_at_time])

        test_match(xform, expected_bound)
        test_match(cube, expected_bound)

        # Test compute_path_world_transform works with a UsdGeom.Camera as it can be in the UsdContext bbox cache
        # but has empty bounds (according to Usd) which is somewhat special in bbox-cache invalidation
        camera = stage.DefinePrim("/xform/camera", "Camera")
        world_xf = Gf.Matrix4d(*self._usd_context.compute_path_world_transform("/xform"))
        cam_xf = Gf.Matrix4d(*self._usd_context.compute_path_world_transform("/xform/camera"))
        self.assertTrue(Gf.IsClose(world_xf, cam_xf, 1e-5))

        cam_tr = Gf.Vec3d(100, 100, 1000)
        camera_xform_api = UsdGeom.XformCommonAPI(camera)
        camera_xform_api.SetTranslate(cam_tr)
        cam_xf = Gf.Matrix4d(*self._usd_context.compute_path_world_transform("/xform/camera"))
        self.assertTrue(Gf.IsClose(cam_xf, world_xf * Gf.Matrix4d().SetTranslate(cam_tr), 1e-5))


class TestUsdContext(omni.kit.test.AsyncTestCase):
    async def test_external_stage_attached(self):
        """Test lifetime of a stage inserted into UsdUtils.StageCache outside of omni.usd.context"""
        from pxr import Usd, UsdUtils

        new_stage = Usd.Stage.CreateInMemory()
        usd_stage_cache = UsdUtils.StageCache.Get()
        usd_stage_cache.Insert(new_stage)
        new_stage_id = usd_stage_cache.GetId(new_stage)

        self.assertTrue(new_stage_id.IsValid())

        usd_context = omni.usd.get_context();
        usd_context.attach_stage_with_callback(new_stage_id.ToLongInt(), None)
        usd_context.close_stage()

        self.assertTrue(usd_stage_cache.Contains(new_stage_id))
        self.assertTrue(bool(new_stage))
        self.assertTrue(new_stage.GetPrimAtPath("/").IsValid())

        usd_stage_cache.Erase(new_stage)
        self.assertFalse(usd_stage_cache.Contains(new_stage_id))

    async def test_carb_event_observers(self):
        """Test the carb event observers have unique names when requested"""
        setting_name = "/app/events/qualifiedNames"
        settings = carb.settings.get_settings()
        initial_value = settings.get(setting_name)

        def iterate_observers():
            default_found, custom_found = False, False
            events = [f"runloop:main:{event}" for event in ("preUpdate", "update", "postUpdate")]
            for observer in carb.eventdispatcher.get_eventdispatcher().get_observers(events):
                name  = observer.name
                if name == "UsdContext hydraRender":
                    default_found = True
                elif name == "UsdContext hydraRender CustomContext":
                    custom_found = True
            return default_found, custom_found

        try:
            cur_value = initial_value
            for _ in range(2):
                if cur_value:
                    omni.usd.create_context(name="CustomContext")
                    default_found, custom_found = iterate_observers()
                    self.assertTrue(custom_found)
                else:
                    default_found, custom_found = iterate_observers()
                    self.assertFalse(custom_found)

                self.assertTrue(default_found)
                cur_value = not cur_value
                settings.set(setting_name, cur_value)
                await self.wait_n_updates()

        finally:
            settings.set(setting_name, initial_value)
