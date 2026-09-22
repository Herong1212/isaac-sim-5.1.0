# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import omni.kit.app
import omni.kit.test
import omni.timeline
import omni.usd
import pathlib
import carb
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading
from pxr import Gf, Usd
from ..anim_preview_model import AnimPreviewModel, SkeletonGeometry


EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class TestPreviewModel(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._epsilon = 0.00001
        self.callback_call_count = 0
        self._asset_loaded = False
        self._asset_changed = False

        self.context = omni.usd.get_context()
        self.assertIsNotNone(self.context)

        usd_path = TEST_DATA_PATH.absolute()
        test_file_path = str(usd_path.joinpath("preview_test.usda").absolute())
        await open_stage(test_file_path, self.context)
        self.stage = self.context.get_stage()
        self.assertIsNotNone(self.stage)

    async def tearDown(self):
        self.context.close_stage()
        self.stage = None
        self.context = None

    async def test_create_model(self):
        ## Init with the default context
        model = AnimPreviewModel()
        self.assertEqual(model.context_name, '')
        self.assertEqual(model.timeline_name, '')
        self.assertIsNone(model.anim_source_model.get_current_source())
        self.assertIsNone(model.skel_source_model.get_current_source())
        self._assert_model_empty(model)

        ## Init with a new context
        context_name = 'preview_context'
        model = AnimPreviewModel(context_name)
        self.assertEqual(model.context_name, context_name)
        self.assertEqual(model.timeline_name, context_name)

        ## Load stage
        model.register_stage_loaded(self._count_callbacks)
        model.load_stage()
        await wait_stage_loading()

        self.assertEqual(self.callback_call_count, 1)
        # Check that we have root paths for animations and characters
        self.assertEqual(model.get_anim_root_path(), '/World/Animations/anim')
        self.assertEqual(model.get_skeleton_root_path(), '/World/Character/Root')
        self.assertIsNotNone(model.skel_source_model.get_current_source())
        self.assertEqual(
            model.skel_source_model.get_current_source().source_path_in_stage,
            '/World/Character/Root/Root'
        )
        self.assertEqual(
            model.skel_source_model.get_current_source().target_path_in_stage,
            '/World/Character/Root/Root'
        )

        model.unregister_stage_loaded(self._count_callbacks)
        model.load_stage()
        await wait_stage_loading()
        self.assertEqual(self.callback_call_count, 1)

        model.destroy()
        self._assert_model_empty(model)

    async def test_set_anim(self):
        context_name = 'preview_context'
        model = AnimPreviewModel(context_name)
        model.load_stage()
        await wait_stage_loading()
        # Animation prims for testing
        walk_prim = self.stage.GetPrimAtPath('/World/Animations/walk')
        wave_prim = self.stage.GetPrimAtPath('/World/Animations/wave')
        self.assertTrue(walk_prim.IsValid(), 'Could not find animation prim in the test usda file')
        self.assertTrue(wave_prim.IsValid(), 'Could not find animation prim in the test usda file')

        ## is_animation
        self.assertTrue(model.is_animation(walk_prim))
        self.assertFalse(None)
        self.assertFalse(model.is_animation(self.stage.GetPrimAtPath('prim_does_not_extist')))
        self.assertFalse(model.is_animation(self.stage.GetPrimAtPath('/World')))
        self.assertFalse(model.is_animation(self.stage.GetPrimAtPath('/World/DistantLight')))
        self.assertFalse(model.is_animation(self.stage.GetPrimAtPath('/World/Character')))

        ## Set preview animation: Invalid input
        success = model.set_preview_anim('prim_does_not_extist', self.stage)
        self.assertFalse(success)
        self.assertFalse(model.has_animation())
        success = model.set_preview_anim('/World/DistantLight', self.stage)
        self.assertFalse(success)
        self.assertFalse(model.has_animation())

        ## Set new valid animation
        self._reset_asset_state()
        self.assertFalse(model.timeline.is_playing())
        model.register_animation_changed(self._on_anim_changed)
        model.register_animation_loaded(self._on_anim_loaded)

        success = model.set_preview_anim(walk_prim.GetPath(), self.stage)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(success)
        self.assertTrue(model.has_animation())
        self.assertEqual(model.anim_source_model.get_current_source().source_path_in_stage, str(walk_prim.GetPath()))
        self.assertFalse(model.anim_source_model.get_current_source().is_external)
        self.assertTrue(model.timeline.is_playing())
        self.assertIsNotNone(model.annotation_model)
        self.assertTrue(model.annotation_model.is_empty())
        self.assertAlmostEqual(model.timeline.get_start_time(), 0.0, places=4)
        self.assertAlmostEqual(model.timeline.get_end_time(), 3.0 + 8.0 / 24.0, places=4)
        self.assertTrue(self._asset_loaded)
        self.assertTrue(self._asset_changed)
        anim_root_path_first = model.get_anim_root_path()

        ## Set the same animation again
        self._reset_asset_state()
        model.set_preview_anim(walk_prim.GetPath(), self.stage)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(model.anim_source_model.get_current_source().source_path_in_stage, str(walk_prim.GetPath()))
        self.assertFalse(self._asset_loaded)
        self.assertFalse(self._asset_changed)
        self.assertEqual(anim_root_path_first, model.get_anim_root_path())

        ## Add another animation with annotation
        self._reset_asset_state()
        test_url = 'test://test.usd'
        success = model.set_preview_anim(wave_prim.GetPath(), self.stage, external_url=test_url)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(success)
        self.assertTrue(model.has_animation())
        self.assertEqual(model.anim_source_model.get_current_source().source_path_in_stage, str(wave_prim.GetPath()))
        self.assertEqual(model.anim_source_model.get_current_source().source_url, test_url)
        self.assertTrue(model.anim_source_model.get_current_source().is_external)
        self.assertNotEqual(anim_root_path_first, model.get_anim_root_path())
        golden_annotations = [("Idle", 0, 8), ("Wave", 8, 58), ("Idle", 58, 76)]
        self.assertEqual(len(model.annotation_model.annotations), len(golden_annotations))
        for i, golden_annotation in enumerate(golden_annotations):
            test_annotation = model.annotation_model.annotations[i]
            self.assertEqual(golden_annotation[0], test_annotation.tag)
            self.assertEqual(golden_annotation[1], test_annotation.start)
            self.assertEqual(golden_annotation[2], test_annotation.end)
            self.assertAlmostEqual(model.timeline.get_start_time(), 0.0, places=4)
        self.assertAlmostEqual(model.timeline.get_end_time(), 3.0 + 4.0 / 24.0, places=4)
        self.assertTrue(self._asset_loaded)
        self.assertTrue(self._asset_changed)

        ## Switch back to the first animation
        self._reset_asset_state()
        success = model.set_preview_anim(walk_prim.GetPath(), self.stage)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(success)
        self.assertTrue(model.has_animation())
        self.assertEqual(model.anim_source_model.get_current_source().source_path_in_stage, str(walk_prim.GetPath()))
        self.assertTrue(model.annotation_model.is_empty())
        self.assertAlmostEqual(model.timeline.get_start_time(), 0.0, places=4)
        self.assertAlmostEqual(model.timeline.get_end_time(), 3.0 + 8.0 / 24.0, places=4)
        self.assertFalse(self._asset_loaded)
        self.assertTrue(self._asset_changed)
        self.assertEqual(anim_root_path_first, model.get_anim_root_path())

        ## Remove animations
        self._reset_asset_state()
        model.remove_animations()
        self.assertFalse(model.has_animation())
        self.assertFalse(self._asset_loaded)
        self.assertFalse(self._asset_changed)

        ## Do not load annotations, unsubscribe
        self._reset_asset_state()
        model.unregister_animation_changed(self._on_anim_changed)
        model.unregister_animation_loaded(self._on_anim_loaded)
        success = model.set_preview_anim(wave_prim.GetPath(), load_annotations=False)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(model.has_animation())
        self.assertTrue(model.annotation_model.is_empty())
        self.assertFalse(self._asset_loaded)
        self.assertFalse(self._asset_changed)

        ## Reset stage
        model.reset_scene()
        self.assertFalse(model.has_animation())

        model.destroy()
        self._assert_model_empty(model)

        self._on_anim_changed = None
        self._on_anim_loaded = None

    async def test_set_skeleton(self):
        context_name = 'preview_context'
        model = AnimPreviewModel(context_name)
        model.load_stage()
        await wait_stage_loading()
        # Skeleton prims for testing
        skelroot_prim = self.stage.GetPrimAtPath('/World/Character')
        skeleton_prim = self.stage.GetPrimAtPath('/World/Character/Root')
        self.assertTrue(skelroot_prim.IsValid(), 'Could not find skeleton prim in the test usda file')
        self.assertTrue(skeleton_prim.IsValid(), 'Could not find skeleton prim in the test usda file')

        # We already have a default skeleton
        self.assertEqual(len(model.get_skeleton_paths()), 1)

        ## is_skeleton
        self.assertTrue(model.is_skeleton(skeleton_prim))
        self.assertTrue(model.is_skeleton(skeleton_prim))
        self.assertFalse(None)
        self.assertFalse(model.is_skeleton(self.stage.GetPrimAtPath('prim_does_not_exist')))
        self.assertFalse(model.is_skeleton(self.stage.GetPrimAtPath('/World')))
        self.assertFalse(model.is_skeleton(self.stage.GetPrimAtPath('/World/DistantLight')))
        self.assertFalse(model.is_skeleton(self.stage.GetPrimAtPath('/World/Animations/walk')))

        ## Set preview skeleton: Invalid input
        success = model.set_preview_skeleton('prim_does_not_extist', self.stage)
        self.assertFalse(success)
        success = model.set_preview_skeleton('/World/DistantLight', self.stage)
        self.assertFalse(success)

        ## Set new valid SkeletonRoot
        self._reset_asset_state()
        model.register_skeleton_changed(self._on_skeleton_changed)
        model.register_skeleton_loaded(self._on_skeleton_loaded)

        success = model.set_preview_skeleton(skelroot_prim.GetPath(), self.stage)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        self.assertTrue(success)
        self.assertEqual(
            model.skel_source_model.get_current_source().source_path_in_stage,
            str(skelroot_prim.GetPath())
        )
        self.assertFalse(model.skel_source_model.get_current_source().is_external)
        self.assertTrue(self._asset_loaded)
        self.assertTrue(self._asset_changed)
        self.assertEqual(len(model.get_skeleton_paths()), 2)
        golden_bbox = [
            Gf.Vec3d(-92.4488296508789, 0, -8.280998229980469),
            Gf.Vec3d(92.44866943359375, 164.88621520996094, 11.115331649780273)
        ]
        self._assert_bbox(golden_bbox, model.get_skeleton_bbox())
        skel_root_path_first = model.get_skeleton_root_path()

        ## Add another supported skeleton, this time a Skeleton
        self._reset_asset_state()
        test_url = 'test://test.usd'
        success = model.set_preview_skeleton(skeleton_prim.GetPath(), self.stage, external_url=test_url)
        self.assertTrue(success)
        self.assertEqual(
            model.skel_source_model.get_current_source().source_path_in_stage,
            str(skeleton_prim.GetPath())
        )
        self.assertEqual(model.skel_source_model.get_current_source().source_url, test_url)
        self.assertTrue(model.skel_source_model.get_current_source().is_external)
        self.assertNotEqual(skel_root_path_first, model.get_skeleton_root_path())
        self.assertEqual(len(model.get_skeleton_paths()), 3)
        self.assertTrue(self._asset_loaded)
        self.assertTrue(self._asset_changed)

        ## Switch back to the first skeleton
        self._reset_asset_state()
        success = model.set_preview_skeleton(skelroot_prim.GetPath(), self.stage)
        self.assertTrue(success)
        self.assertEqual(
            model.skel_source_model.get_current_source().source_path_in_stage,
            str(skelroot_prim.GetPath())
        )
        self.assertFalse(self._asset_loaded)
        self.assertTrue(self._asset_changed)
        self.assertEqual(skel_root_path_first, model.get_skeleton_root_path())
        self.assertEqual(len(model.get_skeleton_paths()), 3)

        await wait_stage_loading()
        await omni.kit.app.get_app().next_update_async()

        ## Remove skeletons
        self._reset_asset_state()
        model.remove_skeletons()
        # the external skeleton will be keeped
        self.assertEqual(len(model.get_skeleton_paths()), 2)
        self.assertFalse(self._asset_loaded)
        # We do set the default skeleton so the changed event if fired.
        # We might as well change the code to not trigger this event.
        self.assertFalse(self._asset_changed)

        ## Unsubscribe
        self._reset_asset_state()
        model.unregister_skeleton_changed(self._on_skeleton_changed)
        model.unregister_skeleton_loaded(self._on_skeleton_loaded)
        success = model.set_preview_skeleton(skeleton_prim.GetPath(), self.stage)
        self.assertFalse(self._asset_loaded)
        self.assertFalse(self._asset_changed)

        ## Reset stage
        model.set_preview_skeleton(skelroot_prim.GetPath(), self.stage)
        model.reset_scene()

        # At this point the stage should have /World/Character/Root in it, but no actual character data
        self.assertEqual(len(model.get_skeleton_paths()), 1)

        model.destroy()
        self._assert_model_empty(model)

        self._on_skeleton_changed = None
        self._on_skeleton_loaded = None

    async def test_skeleton_geometry(self):
        context_name = 'preview_context'
        model = AnimPreviewModel(context_name)
        model.load_stage()
        await wait_stage_loading()

        skelgeom: SkeletonGeometry = model.skel_geometry
        golden_bbox = [
            Gf.Vec3d(-92.4488296508789, 0, -8.280998229980469),
            Gf.Vec3d(92.44866943359375, 164.88621520996094, 11.115331649780273)
        ]
        golden_center = Gf.Vec3d(-0.000080108642578125, 82.44310760498047, 1.4171667098999023)
        golden_center_offset = Gf.Vec3d(-0.000080108642578125, 82.44310760498047, 1.4171667098999023)
        golden_height = 164.88621520996094
        golden_up_axis = (0, 1, 0)

        model.timeline.stop()
        model.timeline.set_auto_update(False)

        self._assert_bbox(golden_bbox, skelgeom.bbox)
        self.assertTrue(Gf.IsClose(golden_center, skelgeom.center, self._epsilon))
        self.assertTrue(Gf.IsClose(golden_center_offset, skelgeom.center_offset, self._epsilon))
        self.assertTrue(Gf.IsClose(golden_height, skelgeom.height, self._epsilon))
        self.assertTrue(Gf.IsClose(golden_up_axis, skelgeom.up_axis, self._epsilon))

        walk_prim = self.stage.GetPrimAtPath('/World/Animations/walk')
        success = model.set_preview_anim(walk_prim.GetPath(), self.stage)
        for i in range(5):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(success)

        golden_centers = {
            0: Gf.Vec3d(5.26384162902832, 82.44310760498047, -145.14634037017822),
            10: Gf.Vec3d(3.891864776611328, 82.44310760498047, -108.22918033599854),
            30: Gf.Vec3d(-0.518359363079071, 82.44310760498047, -34.615986824035645),
        }
        golden_root_positions = {
            0: Gf.Vec3d(5.263921737670898, 0, -146.56350708007812),
            10: Gf.Vec3d(3.8919448852539062, 0, -109.64634704589844),
            30: Gf.Vec3d(-0.5182792544364929, 0, -36.03315353393555)
        }
        use_fabric = carb.settings.get_settings().get("/app/useFabricSceneDelegate")
        last_time_frame = 0
        for time_in_frames in golden_centers:
            print(time_in_frames)
            model.timeline.set_current_time(float(time_in_frames) / model.timeline.get_time_codes_per_seconds())
            await omni.kit.app.get_app().next_update_async()
            center = skelgeom.get_center(Usd.TimeCode(time_in_frames))
            root_pos = skelgeom.get_root_position(Usd.TimeCode(time_in_frames))

            if use_fabric:
                self.assertTrue(Gf.IsClose(golden_centers[last_time_frame], center, self._epsilon))
                self.assertTrue(Gf.IsClose(golden_root_positions[last_time_frame], root_pos, self._epsilon))
            else:
                self.assertTrue(Gf.IsClose(golden_centers[time_in_frames], center, self._epsilon))
                self.assertTrue(Gf.IsClose(golden_root_positions[time_in_frames], root_pos, self._epsilon))
            last_time_frame = time_in_frames

    def _count_callbacks(self, *args):
        self.callback_call_count = self.callback_call_count + 1

    def _on_anim_loaded(self, source_path, target_path, source_stage, external_url, annotations):
        self._asset_loaded = True

    def _on_anim_changed(self, source_path, target_path, external_url, annotations):
        self._asset_changed = True

    def _on_skeleton_loaded(self, source_path, target_path, source_stage):
        self._asset_loaded = True

    def _on_skeleton_changed(self, source_path, target_path):
        self._asset_changed = True

    def _reset_asset_state(self):
        self._asset_changed = False
        self._asset_loaded = False

    def _assert_model_empty(self, model: AnimPreviewModel):
        self.assertFalse(model.has_animation())
        self.assertIsNone(model.get_anim_root_path())
        self.assertIsNone(model.annotation_model)
        self.assertIsNone(model.get_skeleton_root_path())
        self.assertEqual(len(model.get_skeleton_paths()), 0)
        self.assertFalse(model.is_skeleton_selected)

    def _assert_bbox(self, golden_bbox, in_bbox: Gf.Range3d):
        self.assertTrue(Gf.IsClose(golden_bbox[0], in_bbox.GetMin(), self._epsilon))
        self.assertTrue(Gf.IsClose(golden_bbox[1], in_bbox.GetMax(), self._epsilon))
