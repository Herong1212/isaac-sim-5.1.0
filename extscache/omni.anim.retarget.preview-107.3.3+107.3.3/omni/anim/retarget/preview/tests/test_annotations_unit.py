# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.undo
import omni.usd
import omni.timeline
import pathlib

from omni.anim.retarget.preview import Annotation, AnnotationSet, get_annotations, SourceModel
from omni.kit.test.async_unittest import LogErrorChecker
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading


EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class TestAnnotations(omni.kit.test.AsyncTestCase):
    fail_on_log_error = False

    async def setUp(self):
        self.context = omni.usd.get_context()
        self.assertIsNotNone(self.context)

        usd_path = TEST_DATA_PATH.absolute()
        test_file_path = str(usd_path.joinpath("annotation_tests.usda").absolute())
        await open_stage(test_file_path, self.context)
        self.stage = self.context.get_stage()
        self.assertIsNotNone(self.stage)

        self.anim_prim = self.stage.GetPrimAtPath('/World/animation')
        self.assertTrue(self.anim_prim.IsValid(), 'Could not find animation prim')
        self.empty_anim_prim = self.stage.GetPrimAtPath('/World/empty_animation')
        self.assertTrue(self.empty_anim_prim.IsValid(), 'Could not find animation prim')

        self.golden_annotations = [
            ('Walk', 0, 10, '/World/animation/Walk'),
            ('Walk', 20, 40, '/World/animation/Walk_01'),
            ('Wave', 20, 40, '/World/animation/Wave'),
            ('Idle', 25, 35, '/World/animation/Idle'),
            ('Run', 40, 50, '/World/animation/Run'),
        ]

        self.target_error_count = 0
        self.callback_call_count = 0

    async def tearDown(self):
        self.context.close_stage()
        self.stage = None
        self.context = None
        self.target_error_count = 0
        self.callback_call_count = 0

    async def test_01_create_and_set(self):
        ## Init
        tag = 'A tag'
        start = 42
        end = 159
        annotation = Annotation(tag=tag, start=start, end=end)
        self.assertEqual(annotation.tag, tag)
        self.assertEqual(annotation.start, start)
        self.assertEqual(annotation.end, end)
        self.assertEqual(annotation.length, end - start)
        self.assertIsNone(annotation.parent_path)

        ## Setters
        value_changed_sub = annotation.add_value_changed_fn(self._count_callbacks)
        new_tag = 'Another tag'
        new_start = 279
        new_end = 380
        annotation.tag = new_tag
        annotation.start = new_start
        annotation.end = new_end
        self.assertEqual(annotation.tag, new_tag)
        self.assertEqual(annotation.start, new_start)
        self.assertEqual(annotation.end, new_end)
        self.assertEqual(annotation.length, new_end - new_start)
        self.assertEqual(self.callback_call_count, 3)
        self.callback_call_count = 0  # reset

        ## Set values without USD syncback
        changed = annotation.set_values_without_usd_sync(tag=tag, start=start, end=end)
        # Value changed is not called, we get it as the return value
        self.assertEqual(self.callback_call_count, 0)
        self.assertTrue(changed)
        self.assertEqual(annotation.tag, tag)
        self.assertEqual(annotation.start, start)
        self.assertEqual(annotation.end, end)
        changed = annotation.set_values_without_usd_sync(tag=tag, start=start, end=end)
        self.assertFalse(changed)
        # Value changed is not called, we get it as the return value
        self.assertEqual(self.callback_call_count, 0)
        self.assertFalse(changed)

        ## Test the set_value, no USD syncback tests this time (those are in another test)
        changed = annotation.set_values(tag=new_tag, start=new_start, end=new_end)
        self.assertEqual(self.callback_call_count, 1)
        self.assertTrue(changed)
        self.assertEqual(annotation.tag, new_tag)
        self.assertEqual(annotation.start, new_start)
        self.assertEqual(annotation.end, new_end)
        changed = annotation.set_values(tag=new_tag, start=new_start, end=new_end)
        self.assertEqual(self.callback_call_count, 1)
        self.assertFalse(changed)

        ## Test UI models
        annotation.tag_model.set_value(tag)
        self.assertEqual(annotation.tag, tag)
        annotation.start_model.set_value(start)
        self.assertEqual(annotation.start, start)
        annotation.end_model.set_value(end)
        self.assertEqual(annotation.end, end)

        annotation.remove_value_changed_fn(value_changed_sub)

        ## Name is unique if prim path is different
        source1 = SourceModel()
        source1.set_source_path_in_stage('1')
        a1 = Annotation('Test', 0, 1, source1)

        source2 = SourceModel()
        source2.set_source_path_in_stage('2')
        a2 = Annotation(a1.tag, a1.start, a1.end, source2)

        self.assertNotEqual(a1.name, a2.name)

    async def test_02_parse_and_query(self):
        golden_annotations = self.golden_annotations

        ## Query all annotations
        annotations = get_annotations(self.anim_prim)
        self._verify_annotations(annotations, golden_annotations)

        ## Filter by tag
        annotations = get_annotations(self.anim_prim, tag='Walk')
        self._verify_annotations(annotations, [golden_annotations[0], golden_annotations[1]])
        annotations = get_annotations(self.anim_prim, tag='Run')
        self._verify_annotations(annotations, [golden_annotations[-1]])

        ## Filter by start and/or end time
        annotations = get_annotations(self.anim_prim, tag='Walk', start_time=0)
        self._verify_annotations(annotations, [golden_annotations[0]])
        annotations = get_annotations(self.anim_prim, tag='Walk', end_time=40)
        self._verify_annotations(annotations, [golden_annotations[1]])
        annotations = get_annotations(self.anim_prim, start_time=20, end_time=40)
        self._verify_annotations(annotations, [golden_annotations[1], golden_annotations[2]])
        annotations = get_annotations(self.anim_prim, start_time=20, end_time=40, exact_times=False)
        self._verify_annotations(annotations, [golden_annotations[1], golden_annotations[2], golden_annotations[3]])
        annotations = get_annotations(self.anim_prim, end_time=35, exact_times=False)
        self._verify_annotations(annotations, [golden_annotations[0], golden_annotations[3]])

        ## Prims with no annotation or invalid prims
        annotations = get_annotations(self.empty_anim_prim)
        self.assertEqual(len(annotations), 0)

        invalid_prim = self.stage.GetPrimAtPath('/World/this_prim_does_not_exist')
        annotations = get_annotations(invalid_prim)
        self.assertEqual(len(annotations), 0)

        ## Source
        source = SourceModel()
        source.set_source_path_in_stage(self.anim_prim.GetPath())
        source.set_source_url('c:/some_file.usd')  # exact value does not matter, we want to see if it is propagated
        annotations = get_annotations(self.anim_prim, source=source)
        self._verify_annotations(annotations, golden_annotations, source, self.anim_prim.GetPath())
        for annotation in annotations:
            self.assertEqual(str(annotation.parent_path), str(self.anim_prim.GetPath()))

    async def test_03_commands(self):
        golden_annotations = [
            ('Walk', 0, 10, '/World/empty_animation/Walk'),
            ('Walk', 20, 40, '/World/empty_animation/Walk_01'),
            ('Wave', 20, 40, '/World/empty_animation/Wave'),
            ('Idle', 25, 35, '/World/empty_animation/Idle'),
            ('Run', 40, 50, '/World/empty_animation/Run'),
        ]
        golden_annotations_without_source = [(a[0], a[1], a[2]) for a in golden_annotations]
        timeline_name = 'dummy_timeline'
        timeline = omni.timeline.get_timeline_interface(timeline_name)
        timeline.set_time_codes_per_second(24)
        timeline.set_end_time(10)
        timeline.set_start_time(0)
        await omni.kit.app.get_app().next_update_async()
        fps = timeline.get_time_codes_per_seconds()
        # convert to time codes
        timeline_start, timeline_end = timeline.get_start_time() * fps, timeline.get_end_time() * fps
        # Setup the log checker
        await omni.kit.app.get_app().next_update_async()  # Make sure log buffer pumped
        self.log_error_checker = LogErrorChecker()
        self.assertTrue(self.log_error_checker.get_error_count() == 0)
        self.target_error_count = 0

        ## Add single annotation
        self._verify_annotations(get_annotations(self.empty_anim_prim), [])

        default_tag = 'New annotation'
        omni.kit.commands.execute(
            'AnimationPreviewAddAnnotationCommand',
            path=self.empty_anim_prim.GetPath(),
            timeline_name=timeline_name,
            select_new_prim=True
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        new_path = '/World/empty_animation/New_annotation'
        golden = (default_tag, timeline_start, timeline_end, new_path)
        self._verify_annotations(get_annotations(self.empty_anim_prim), [golden])
        self.assertTrue(self.context.get_selection().is_prim_path_selected(new_path))
        omni.kit.undo.undo()
        self._verify_annotations(get_annotations(self.empty_anim_prim), [])

        start_time = 1
        end_time = 2
        tag = 'Run'
        omni.kit.commands.execute(
            'AnimationPreviewAddAnnotationCommand',
            path=self.empty_anim_prim.GetPath(),
            tag='Run',
            start_time=start_time,
            end_time=end_time,
            select_new_prim=False
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        new_path = '/World/empty_animation/Run'
        golden = (tag, start_time, end_time, new_path)
        self._verify_annotations(get_annotations(self.empty_anim_prim), [golden])
        self.assertFalse(self.context.get_selection().is_prim_path_selected(new_path))
        omni.kit.undo.undo()
        self._verify_annotations(get_annotations(self.empty_anim_prim), [])

        cmd_name = 'AnimationPreviewAddAnnotationCommand'
        path = self.empty_anim_prim.GetPath()
        # Invalid path type
        await self._assert_cmd_fail(1, cmd_name, path=0)
        # Invalid path
        await self._assert_cmd_fail(1, cmd_name, path='Does not exist')
        # Invalid prim: not an SkelAnim
        await self._assert_cmd_fail(1, cmd_name, path='/World/not_an_animation')
        # Invalid tag type
        await self._assert_cmd_fail(1, cmd_name, path=path, tag=0)
        # Invalid start time
        await self._assert_cmd_fail(1, cmd_name, path=path, start_time='5')
        # Invalid end time
        await self._assert_cmd_fail(1, cmd_name, path=path, end_time='5')
        # Invalid select_new_prim type (bool expected)
        await self._assert_cmd_fail(1, cmd_name, path=path, select_new_prim='off')
        # Invalid context name type (string expected)
        await self._assert_cmd_fail(1, cmd_name, path=path, context_name=self.context)
        # Non-existent context name
        await self._assert_cmd_fail(1, cmd_name, path=path, context_name='Does not exist')
        # Invalid timeline name type (string expected)
        await self._assert_cmd_fail(1, cmd_name, path=path, timeline_name=timeline)

        ## Add multiple annotations
        omni.kit.commands.execute(
            'AnimationPreviewAddAnnotationsCommand',
            path=self.empty_anim_prim.GetPath(),
            annotations=golden_annotations_without_source
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(get_annotations(self.empty_anim_prim), golden_annotations)
        omni.kit.undo.undo()
        self._verify_annotations(get_annotations(self.empty_anim_prim), [])

        cmd_name = 'AnimationPreviewAddAnnotationsCommand'
        path = self.empty_anim_prim.GetPath()
        # Invalid path type
        await self._assert_cmd_fail(1, cmd_name, path=0, annotations=golden_annotations_without_source)
        # Invalid annotations type
        await self._assert_cmd_fail(1, cmd_name, path=path, annotations=0)
        # Invalid type in annotations data
        invalid_annot_1 = [('valid', 0, 1, 'this tuple is longer than expected')]
        invalid_annot_2 = [('valid', 'invalid', 0), (0, 0, 'invalid')]
        await self._assert_cmd_fail(1, cmd_name, path=path, annotations=invalid_annot_1)
        await self._assert_cmd_fail(2, cmd_name, path=path, annotations=invalid_annot_2)

        ## Deletion
        golden_annotations = self.golden_annotations
        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath()
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(get_annotations(self.anim_prim), [])
        omni.kit.undo.undo()
        # Undoing a deletion may change the order of prims so we simply check their count.
        # self._verify_annotations(get_annotations(self.anim_prim), golden_annotations)
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            tag='Walk'
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[2],
                golden_annotations[3],
                golden_annotations[4],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            tag='Run'
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[0],
                golden_annotations[1],
                golden_annotations[2],
                golden_annotations[3],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            tag='Walk',
            start_time=0
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[1],
                golden_annotations[2],
                golden_annotations[3],
                golden_annotations[4],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            tag='Walk',
            end_time=40
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[0],
                golden_annotations[2],
                golden_annotations[3],
                golden_annotations[4],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            start_time=20,
            end_time=40
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[0],
                golden_annotations[3],
                golden_annotations[4],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            start_time=20,
            end_time=40,
            exact_times=False
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[0],
                golden_annotations[4],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))
        # Delete and re-insert, so order is maintained for the following tests
        self._restore(self.anim_prim, golden_annotations_without_source)

        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=self.anim_prim.GetPath(),
            end_time=35,
            exact_times=False
        )
        self.assertTrue(self.log_error_checker.get_error_count() == self.target_error_count)
        self._verify_annotations(
            get_annotations(self.anim_prim),
            [
                golden_annotations[1],
                golden_annotations[2],
                golden_annotations[4],
            ]
        )
        omni.kit.undo.undo()
        self.assertEqual(len(get_annotations(self.anim_prim)), len(golden_annotations))

        cmd_name = 'AnimationPreviewRemoveAnnotationsCommand'
        path = self.empty_anim_prim.GetPath()
        # Invalid path type
        await self._assert_cmd_fail(1, cmd_name, path=0)
        # Invalid path
        await self._assert_cmd_fail(1, cmd_name, path='Does not exist')
        # Invalid prim: not an SkelAnim
        await self._assert_cmd_fail(1, cmd_name, path='/World/not_an_animation')
        # Invalid tag type
        await self._assert_cmd_fail(1, cmd_name, path=path, tag=0)
        # Invalid start time
        await self._assert_cmd_fail(1, cmd_name, path=path, start_time='5')
        # Invalid end time
        await self._assert_cmd_fail(1, cmd_name, path=path, end_time='5')
        # Invalid exact_times type
        await self._assert_cmd_fail(1, cmd_name, path=path, exact_times='off')

        timeline = None
        omni.timeline.destroy_timeline(timeline_name)

        # shutdown the checker
        await omni.kit.app.get_app().next_update_async()
        self.log_error_checker.shutdown()

    async def test_04_usd_sync_back(self):
        annotations = get_annotations(self.anim_prim)
        annotation: Annotation = annotations[0]
        prim_path = annotation.source.source_path_in_stage
        annot_prim = self.stage.GetPrimAtPath(prim_path)
        self.assertTrue(annot_prim.IsValid())
        tag_attr = annot_prim.GetAttribute('tag')
        start_attr = annot_prim.GetAttribute('start')
        end_attr = annot_prim.GetAttribute('end')
        self.assertIsNotNone(tag_attr)
        self.assertIsNotNone(start_attr)
        self.assertIsNotNone(end_attr)

        # new_tag = 'Swim'
        # new_start = 42
        # new_end = 52
        # annotation.set_values(tag=new_tag, start=new_start, end=new_end)
        # self.assertEqual(tag_attr.Get(), new_tag)
        # self.assertEqual(start_attr.Get(), new_start)
        # self.assertEqual(end_attr.Get(), new_end)

        # new_tag = 'Write tests'
        # new_start = -197
        # new_end = 236
        # annotation.tag = new_tag
        # self.assertEqual(tag_attr.Get(), new_tag)
        # annotation.start = new_start
        # self.assertEqual(start_attr.Get(), new_start)
        # annotation.end = new_end
        # self.assertEqual(end_attr.Get(), new_end)

        # newer_tag = 'Fly'
        # newer_start = 1984
        # newer_end = 2100
        # annotation.set_values_without_usd_sync(tag=newer_tag, start=newer_start, end=newer_end)
        # # Changes are not visible in USD yet
        # self.assertEqual(tag_attr.Get(), new_tag)
        # self.assertEqual(start_attr.Get(), new_start)
        # self.assertEqual(end_attr.Get(), new_end)
        # # Sync to USD manually
        # annotation.write_to_usd()
        # self.assertEqual(tag_attr.Get(), newer_tag)
        # self.assertEqual(start_attr.Get(), newer_start)
        # self.assertEqual(end_attr.Get(), newer_end)

    async def test_05_annotation_set_api(self):
        parent_source = SourceModel()
        parent_source.set_source_path_in_stage(str(self.anim_prim.GetPath()))
        annotation_set = AnnotationSet(parent_anim=parent_source, time_codes_per_second=30)
        self.callback_call_count = 0
        annotation_sub = annotation_set.subscribe_value_changed_fn(self._count_callbacks)

        timeline = omni.timeline.get_timeline_interface()
        timeline.set_time_codes_per_second(10)
        timeline.set_end_time(10)
        timeline.set_start_time(0)
        await omni.kit.app.get_app().next_update_async()
        fps = timeline.get_time_codes_per_seconds()
        # convert to time codes
        timeline_start, timeline_end = timeline.get_start_time() * fps, timeline.get_end_time() * fps

        ## Empty initially
        self.assertTrue(annotation_set.is_empty())
        self.assertEqual(annotation_set.parent_anim, parent_source)

        ## Set annotations
        annotations = get_annotations(self.anim_prim)
        annotation_set.set_annotations(annotations)
        self.assertEqual(annotation_set.annotations, annotations)
        self.assertFalse(annotation_set.is_empty())
        self.assertEqual(self.callback_call_count, 1)
        self._assert_sorted(annotation_set.annotations)

        annotation_set.set_annotations([])
        self.assertTrue(annotation_set.is_empty())
        self.assertEqual(self.callback_call_count, 2)
        annotations = None

        ## Add and remove annotations
        self.callback_call_count = 0  # reset
        annotation = Annotation('Idle', 40, 50)
        annot_right = annotation
        annotation_set.add_annotation(annotation)
        self.assertEqual(annotation, annotation_set.annotations[0])
        self.assertFalse(annotation_set.is_empty())
        self.assertEqual(self.callback_call_count, 1)
        annotation = Annotation('Walk', 10, 20)
        annot_left = annotation
        annotation_set.add_annotation(annotation)
        self.assertTrue(annotation in annotation_set.annotations)
        self.assertEqual(self.callback_call_count, 2)
        self._assert_sorted(annotation_set.annotations)
        annotation = Annotation('Run', 25, 30)
        annot_mid = annotation
        annotation_set.add_annotation(annotation)
        self.assertTrue(annotation in annotation_set.annotations)
        self.assertEqual(self.callback_call_count, 3)
        self._assert_sorted(annotation_set.annotations)

        annotation = Annotation('To be removed', 0, 60)
        annotation_count = len(annotation_set.annotations)
        annotation_set.add_annotation(annotation)
        self.assertEqual(self.callback_call_count, 4)
        annotation_set.remove_annotation(annotation)
        self.assertEqual(annotation_count, len(annotation_set.annotations))
        self.assertFalse(annotation in annotation_set.annotations)
        self._assert_sorted(annotation_set.annotations)
        self.assertEqual(self.callback_call_count, 5)
        self.callback_call_count = 0

        ## Stretch
        annotation_set.stretch_left(annot_left, timeline_start)
        self.assertEqual(annot_left.start, 0)
        self.assertEqual(annot_left.end, 20)
        self._assert_sorted(annotation_set.annotations)

        annotation_set.stretch_left(annot_right, timeline_start)
        self.assertEqual(annot_right.start, 30)
        self.assertEqual(annot_right.end, 50)
        self._assert_sorted(annotation_set.annotations)

        annotation_set.stretch_right(annot_left, timeline_end)
        self.assertEqual(annot_left.start, 0)
        self.assertEqual(annot_left.end, 25)
        self._assert_sorted(annotation_set.annotations)

        annotation_set.stretch_right(annot_right, timeline_end)
        self.assertEqual(annot_right.start, 30)
        self.assertEqual(annot_right.end, 100)
        self._assert_sorted(annotation_set.annotations)

        annot_right.start, annot_right.end = 40, 50
        annot_left.start, annot_left.end = 10, 20
        annot_mid.start, annot_mid.end = 25, 30
        annotation_set.stretch_bounds(annot_left, timeline_start, timeline_end)
        self.assertEqual(annot_left.start, 0)
        self.assertEqual(annot_left.end, 25)
        self._assert_sorted(annotation_set.annotations)

        annotation_set.stretch_bounds(annot_right, timeline_start, timeline_end)
        self.assertEqual(annot_right.start, 30)
        self.assertEqual(annot_right.end, 100)
        self._assert_sorted(annotation_set.annotations)

        # This should not change
        annotation_set.stretch_bounds(annot_mid, timeline_start, timeline_end)
        self.assertEqual(annot_mid.start, 25)
        self.assertEqual(annot_mid.end, 30)
        self._assert_sorted(annotation_set.annotations)

        ## Fit
        annot_right.start, annot_right.end = 40, 60
        annot_left.start, annot_left.end = 10, 30
        annot_mid.start, annot_mid.end = 20, 50
        annotation_set.fit_left(annot_mid)
        self.assertEqual(annot_mid.start, 30)
        self.assertEqual(annot_mid.end, 50)
        self._assert_sorted(annotation_set.annotations)

        annotation_set.fit_right(annot_mid)
        self.assertEqual(annot_mid.start, 30)
        self.assertEqual(annot_mid.end, 40)
        self._assert_sorted(annotation_set.annotations)

        annot_mid.start, annot_mid.end = 20, 50
        annotation_set.fit_bounds(annot_mid)
        self.assertEqual(annot_mid.start, 30)
        self.assertEqual(annot_mid.end, 40)
        self._assert_sorted(annotation_set.annotations)

        ## Color
        annot_right.start, annot_right.end = 40, 60
        annot_left.start, annot_left.end = 10, 30
        annot_mid.start, annot_mid.end = 20, 50
        color_base = 0
        color_on_time = 1
        t = 25
        annotation_set.set_color(color_base=color_base, color_on_time_overlap=color_on_time, time=t)
        self.assertEqual(annot_right.color, color_base)
        self.assertEqual(annot_left.color, color_on_time)
        self.assertEqual(annot_mid.color, color_on_time)

        ## Tracks
        tracks = annotation_set.tracks
        self.assertEqual(tracks['1'], [annot_left, annot_right])
        self.assertEqual(tracks['2'], [annot_mid])
        annot_cover_all = Annotation('anything', 0, 100)
        annotation_set.add_annotation(annot_cover_all)
        tracks = annotation_set.tracks
        self.assertEqual(tracks['1'], [annot_cover_all])
        self.assertEqual(tracks['2'], [annot_left, annot_right])
        self.assertEqual(tracks['3'], [annot_mid])

        annotation_set.set_annotations([])
        self.assertEqual(len(annotation_set.tracks), 0)

        annotation_sub = None

    async def test_06_annotation_set_usd_sync(self):
        parent_source = SourceModel()
        parent_source.set_source_path_in_stage(self.anim_prim.GetPath())

        parent_source.set_source_path_in_stage(str(self.anim_prim.GetPath()))
        annotation_set = AnnotationSet(parent_anim=parent_source, time_codes_per_second=30)
        annotation_sub = annotation_set.subscribe_value_changed_fn(self._count_callbacks)

        annotations = get_annotations(self.anim_prim, source=parent_source)
        annotation_set.set_annotations(annotations)
        annotation_count_orig = len(self.golden_annotations)
        self.assertEqual(annotation_count_orig, len(annotation_set.annotations))
        self.callback_call_count = 0

        ## New annotation prim
        annotation = Annotation('Test', 0, 100)
        omni.kit.commands.execute(
            'AnimationPreviewAddAnnotationCommand',
            path=self.anim_prim.GetPath(),
            tag=annotation.tag,
            start_time=annotation.start,
            end_time=annotation.end
        )
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(annotation_count_orig + 1, len(annotation_set.annotations))
        self.assertGreater(self.callback_call_count, 0)
        found = False
        inserted_annotation = None
        for a in annotation_set.annotations:
            if annotation.tag == a.tag and annotation.start == a.start and annotation.end == a.end:
                found = True
                inserted_annotation: Annotation = a
        self.assertTrue(found)
        annot_prim_path = self.anim_prim.GetPath().AppendChild(annotation.tag)
        self.assertEqual(str(annot_prim_path), str(inserted_annotation.source.source_path_in_stage))
        # Only to test that destroy does not crash
        annotation.destroy()

        ## Change annotation prim attribute value
        self.callback_call_count = 0
        annot_prim = self.stage.GetPrimAtPath(annot_prim_path)
        new_tag = 'New tag'
        new_start = 10
        new_end = 20
        annot_prim.GetAttribute('tag').Set(new_tag)
        annot_prim.GetAttribute('start').Set(new_start)
        annot_prim.GetAttribute('end').Set(new_end)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(inserted_annotation.tag, new_tag)
        self.assertEqual(inserted_annotation.start, new_start)
        self.assertEqual(inserted_annotation.end, new_end)
        self.assertGreater(self.callback_call_count, 0)

        ## Rename annotation prim
        self.callback_call_count = 0
        new_annot_prim_path = self.anim_prim.GetPath().AppendChild('new_path')
        omni.kit.commands.execute('MovePrimCommand', path_from=annot_prim_path, path_to=new_annot_prim_path)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(str(new_annot_prim_path), str(inserted_annotation.source.source_path_in_stage))
        self.assertEqual(annotation_count_orig + 1, len(annotation_set.annotations))
        # Path change does not trigger a value changed callback
        self.assertEqual(self.callback_call_count, 0)

        ## Delete annotation prim
        omni.kit.commands.execute("DeletePrims", paths=[new_annot_prim_path])
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(annotation_count_orig, len(annotation_set.annotations))
        self.assertGreater(self.callback_call_count, 0)

        ## Rename parent
        new_anim_prim_path = '/World/new_path'
        omni.kit.commands.execute('MovePrimCommand', path_from=self.anim_prim.GetPath(), path_to=new_anim_prim_path)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(annotation_count_orig, len(annotation_set.annotations))
        for annotation in annotation_set.annotations:
            annotation: Annotation
            self.assertTrue(annotation.source.source_path_in_stage.startswith(new_anim_prim_path))

    def _verify_annotations(self, test_annotations, golden_annotations, source: SourceModel = None, parent_path=None):
        self.assertEqual(len(test_annotations), len(golden_annotations))
        for i in range(len(test_annotations)):
            test: Annotation = test_annotations[i]
            golden: Annotation = golden_annotations[i]
            self.assertEqual(test.tag, golden[0])
            self.assertEqual(test.start, golden[1])
            self.assertEqual(test.end, golden[2])
            self.assertEqual(test.source.source_path_in_stage, golden[3])
            if source is None:
                self.assertTrue(test.source.exists_in_source_stage)
                self.assertFalse(test.source.is_external)
            else:
                self.assertEqual(test.source.is_external, source.is_external)
                self.assertEqual(test.source.source_url, source.source_url)
                if parent_path is not None:
                    self.assertEqual(str(test.parent_path), parent_path)

    def _restore(self, prim, annotations):
        omni.kit.undo.begin_disabled()
        omni.kit.commands.execute(
            'AnimationPreviewRemoveAnnotationsCommand',
            path=prim.GetPath()
        )
        omni.kit.commands.execute(
            'AnimationPreviewAddAnnotationsCommand',
            path=prim.GetPath(),
            annotations=annotations
        )
        omni.kit.undo.end_disabled()

    async def _assert_cmd_fail(self, expected_error_count, command_name, **kwargs):
        (result, err) = omni.kit.commands.execute(command_name, **kwargs)
        await wait_stage_loading()
        self.assertFalse(err)
        self.target_error_count += expected_error_count
        self.assertEqual(self.log_error_checker.get_error_count(), self.target_error_count)

    def _count_callbacks(self, _):
        self.callback_call_count = self.callback_call_count + 1

    def _assert_sorted(self, annotations):
        # Check that annotations are sorted by start time
        for i in range(len(annotations) - 1):
            item_i = annotations[i]
            item_ip1 = annotations[i + 1]
            self.assertLessEqual(item_i.start, item_ip1.start)
