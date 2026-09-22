import os
import sys
from unittest import skipIf

import omni.kit.app
import omni.kit.commands
import omni.kit.undo
import omni.usd
from omni.kit.sequencer.core import TrackTypes, sequencer_settings
from omni.kit.sequencer.usd import usd_sequencer
from omni.kit.test import AsyncTestCase
from pxr import Sdf, Tf, UsdGeom
import SequenceSchema

# TODO: SequencerCreateReferenceCommand
# TODO: SequencerSetTargetCommand : track with no target_rel (addrelationship), no target (clear relationship)
# TODO: SequencerClipSetAnimationCommand : anim with 0 length
# TODO: Test add_clip with no prim specified (instantiates with track prim) - handle when no track target.
# TODO: Test add_clip with no end_time specified
# TODO: move_track when wrapping

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ValueClipSamples")
ANIM_SKEL_WITH_CLIP = os.path.join(TEST_DATA_PATH, "UsdSkelWithClip", "skelcylinder_model.usda")
ANIM_SKEL_CLIP = os.path.join(TEST_DATA_PATH, "UsdSkelWithClip", "source", "skelcylinder_clip.usda")
NEW_PRIM_URL = os.path.join(TEST_DATA_PATH, "UsdSkelAsset", "skelcylinder.usda")


async def _add_reference(asset_url):
    stage = omni.usd.get_context().get_stage()
    prim_name = os.path.splitext(os.path.basename(asset_url))[0]
    prim_name = prim_name.partition(".")[0]
    anim_prim_path = f"/{prim_name}"
    path_to = Sdf.Path(omni.usd.get_stage_next_free_path(stage, anim_prim_path, True))
    res, _ = omni.kit.commands.execute(
        "CreateReferenceCommand", path_to=path_to, asset_path=asset_url, usd_context=omni.usd.get_context()
    )
    return res, path_to.pathString


class TestSequencerTrackCommandFailures(AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        _, sequence = omni.kit.commands.execute("SequencerCreateSequenceCommand")
        self.sequence_path = sequence.GetPrim().GetPath()
        await omni.kit.app.get_app().next_update_async()

    async def test_sequencer_track_create_command_undefined_type(self):
        _invalid_track_type = None
        with self.assertRaises(ValueError):
            res, ret_val = omni.kit.commands.execute(
                "SequencerTrackCreateCommand",
                sequence_path=self.sequence_path,
                track_name=None,
                track_type=_invalid_track_type,
            )
            self.assertFalse(res)
            self.assertIsNone(ret_val)

    async def test_sequencer_track_create_command_invalid_type(self):
        # TODO: OM-31526 sequencer defect: https://nvidia-omniverse.atlassian.net/browse/OM-31526
        _invalid_track_type = "foo"
        with self.assertRaises(ValueError):
            res, ret_val = omni.kit.commands.execute(
                "SequencerTrackCreateCommand",
                sequence_path=self.sequence_path,
                track_name=None,
                track_type=_invalid_track_type,
            )
            self.assertFalse(res)
            self.assertIsNone(ret_val)


class TestSequencerTrackCommands(AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        _, sequence = omni.kit.commands.execute("SequencerCreateSequenceCommand")
        self.sequence_path = sequence.GetPrim().GetPath()
        await omni.kit.app.get_app().next_update_async()

    async def test_sequencer_track_create_command_name_strings(self):
        """Make sure that name strings are made valid"""
        _unicode_track_name = "박우중"
        res, track = omni.kit.commands.execute(
            "SequencerTrackCreateCommand",
            sequence_path=self.sequence_path,
            track_name=_unicode_track_name,
            track_type=TrackTypes.SHOT,
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        self.assertEqual(track.GetPrim().GetName(), Tf.MakeValidIdentifier(_unicode_track_name))

        _bad_track_name = " 1 a name with spaces etc.."
        res, track = omni.kit.commands.execute(
            "SequencerTrackCreateCommand",
            sequence_path=self.sequence_path,
            track_name=_bad_track_name,
            track_type=TrackTypes.SHOT,
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        self.assertEqual(track.GetPrim().GetName(), Tf.MakeValidIdentifier(_bad_track_name))

    async def test_sequencer_track_create_command(self):
        """Test sequencer track create command"""
        stage = omni.usd.get_context().get_stage()

        for _track_type in TrackTypes:
            with self.subTest(_track_type=_track_type):
                res, track = omni.kit.commands.execute(
                    "SequencerTrackCreateCommand",
                    sequence_path=self.sequence_path,
                    track_name=_track_type,
                    track_type=_track_type,
                )
                await omni.kit.app.get_app().next_update_async()
                # give hydra a frame before deleting to catch up so it doesn't spew coding error about not finding prim

                self.assertTrue(res)
                prim = track.GetPrim()
                track_prim_path = prim.GetPath()
                track_type = track.GetTrackTypeAttr().Get()
                self.assertTrue(prim.IsA(SequenceSchema.Track))
                self.assertEqual(track_type, _track_type)

                omni.kit.undo.undo()
                await omni.kit.app.get_app().next_update_async()

                prim = stage.GetPrimAtPath(track_prim_path)
                self.assertFalse(prim)

                omni.kit.undo.redo()
                await omni.kit.app.get_app().next_update_async()

                prim = stage.GetPrimAtPath(track_prim_path)
                self.assertTrue(prim)
                self.assertTrue(prim.IsValid())

    async def test_sequencer_track_move_command(self):
        """Test sequencer move track command."""
        # NOTE: This moves the track index, not position in time. i.e. reordering tracks
        # TODO: Test case where move would put track to negative or beyond length or array.

        def get_track_index(track):
            """Get track index"""
            prim = track.GetPrim()
            parent = prim.GetParent()
            parent_prim = parent.GetPrim()
            children = parent_prim.GetChildren()
            index = children.index(prim)
            return index

        for i, _track_type in enumerate(TrackTypes):
            with self.subTest(_track_type=_track_type):
                track_names = [f"{_track_type}_0", f"{_track_type}_1"]
                n = i * 2
                # Create two tracks so we can reorder them etc.
                res, seq_track_1 = omni.kit.commands.execute(
                    "SequencerTrackCreateCommand",
                    sequence_path=self.sequence_path,
                    track_name=track_names[0],
                    track_type=_track_type,
                )
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                res, seq_track_2 = omni.kit.commands.execute(
                    "SequencerTrackCreateCommand",
                    sequence_path=self.sequence_path,
                    track_name=track_names[1],
                    track_type=_track_type,
                )
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                seq_tracks = [seq_track_1, seq_track_2]
                seq_track_paths = [track.GetPrim().GetPath().pathString for track in seq_tracks]
                # confirm track created
                self.assertEqual(len(seq_tracks), 2)
                # confirm track indicies
                self.assertEqual(n, get_track_index(seq_tracks[0]))
                self.assertEqual(n + 1, get_track_index(seq_tracks[1]))

                _move_vector = -1
                res = omni.kit.commands.execute(
                    "SequencerTrackMoveCommand", track_path=seq_track_paths[1], move_vector=_move_vector
                )
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertEqual(n, get_track_index(seq_tracks[1]))

                res = omni.kit.undo.undo()
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertEqual(n + 1, get_track_index(seq_tracks[1]))

                res = omni.kit.undo.redo()
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertEqual(n, get_track_index(seq_tracks[1]))

                res = omni.kit.undo.undo()
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertEqual(n + 1, get_track_index(seq_tracks[1]))

    async def test_sequencer_track_set_target_command(self):
        # SequencerSetTargetCommand
        track_type = "Asset"
        res, track = omni.kit.commands.execute(
            "SequencerTrackCreateCommand",
            sequence_path=self.sequence_path,
            track_name=track_type,
            track_type=track_type,
        )
        await omni.kit.app.get_app().next_update_async()

        # confirm track creation
        self.assertTrue(res)
        res, skel_anim_prim_path = await _add_reference(ANIM_SKEL_WITH_CLIP)
        track_prim = track.GetPrim()
        track_path = track.GetPath()
        target_rel = track_prim.GetRelationship("sequencer:trackTarget")
        self.assertFalse(target_rel.IsValid())
        res, _ = omni.kit.commands.execute(
            "SequencerSetTargetCommand",
            prim_path=track_path,
            target_prim=skel_anim_prim_path,
            relationship_name="sequencer:trackTarget",
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        target_rel = track_prim.GetRelationship("sequencer:trackTarget")
        self.assertTrue(target_rel.IsValid())
        targets = target_rel.GetTargets()
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0], skel_anim_prim_path)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        target_rel = track_prim.GetRelationship("sequencer:trackTarget")
        self.assertFalse(target_rel.IsValid())

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        target_rel = track_prim.GetRelationship("sequencer:trackTarget")
        self.assertTrue(target_rel.IsValid())
        targets = target_rel.GetTargets()
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0], skel_anim_prim_path)

    async def test_sequencer_track_visible_set_command(self):
        for _track_type in TrackTypes:
            with self.subTest(_track_type=_track_type):
                res, track = omni.kit.commands.execute(
                    "SequencerTrackCreateCommand",
                    sequence_path=self.sequence_path,
                    track_name=_track_type,
                    track_type=_track_type,
                )
                await omni.kit.app.get_app().next_update_async()

                # confirm track creation
                self.assertTrue(res)
                # check initial visibility

                # self.assertTrue(sequencer.get_track_is_visible(_track_type))
                track_path = track.GetPrim().GetPath().pathString
                self.assertTrue(track.ComputeVisibility())
                res, _ = omni.kit.commands.execute(
                    "SequencerTrackVisibleSetCommand", track_path=track_path, is_visible=False
                )
                self.assertTrue(res)
                self.assertEqual(track.ComputeVisibility(), UsdGeom.Tokens.invisible)

                res = omni.kit.undo.undo()
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertTrue(track.ComputeVisibility())

                res = omni.kit.undo.redo()
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertEqual(track.ComputeVisibility(), UsdGeom.Tokens.invisible)

                res = omni.kit.undo.undo()
                await omni.kit.app.get_app().next_update_async()

                self.assertTrue(res)
                self.assertTrue(track.ComputeVisibility())


class TestSequencerClipCreateCommands(AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetEndTimeCode(900)
        _, sequence = omni.kit.commands.execute("SequencerCreateSequenceCommand")
        await omni.kit.app.get_app().next_update_async()
        self.sequence_path = sequence.GetPrim().GetPath()
        self.tracks = {}
        for _track_type in TrackTypes:
            res, track = omni.kit.commands.execute(
                "SequencerTrackCreateCommand",
                sequence_path=self.sequence_path,
                track_name=_track_type,
                track_type=_track_type,
            )
            await omni.kit.app.get_app().next_update_async()

            self.assertTrue(res)
            self.tracks[_track_type] = track
        res, self.skel_anim_prim_path = await _add_reference(ANIM_SKEL_WITH_CLIP)
        self.assertTrue(res)
        await omni.kit.app.get_app().next_update_async()

    async def test_sequencer_clip_create_command(self):
        """Test sequencer clip create command"""
        stage = omni.usd.get_context().get_stage()
        clip_name = "Test_Clip"
        prim_path = self.skel_anim_prim_path
        clip_start = 2
        clip_end = 44
        select_prim = False
        selection_before = omni.usd.get_context().get_selection()
        asset_track = self.tracks["Asset"]
        asset_track_path = asset_track.GetPrim().GetPath().pathString

        res, clip = omni.kit.commands.execute(
            "SequencerClipCreateCommand",
            track_path=asset_track_path,
            clip_name=clip_name,
            prim_path=prim_path,
            clip_start=clip_start,
            clip_end=clip_end,
            select_prim=select_prim,
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        clip_prim = clip.GetPrim()
        clip_path = clip_prim.GetPath()

        self.assertTrue(clip_prim.IsA(SequenceSchema.AssetClip))
        start_time = clip.GetStartTimeAttr().Get()
        end_time = clip.GetEndTimeAttr().Get()
        self.assertEqual(start_time, clip_start)
        self.assertEqual(end_time, clip_end)

        rel = SequenceSchema.AssetClipBase(clip).GetAssetPrimRel()
        rel_targets = rel.GetTargets()
        self.assertEqual(len(rel_targets), 1)
        self.assertEqual(rel_targets[0], prim_path)

        self.assertEqual(clip_prim.GetName(), clip_name)

        # TODO: Test select_prim = True, or remove option because it is unused.
        selection_after = omni.usd.get_context().get_selection()
        self.assertEqual(selection_before, selection_after)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        prim = stage.GetPrimAtPath(clip_path)
        self.assertFalse(prim.IsValid())

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        prim = stage.GetPrimAtPath(clip_path)
        self.assertTrue(prim)

        rel = SequenceSchema.AssetClipBase(prim).GetAssetPrimRel()
        rel_targets = rel.GetTargets()
        self.assertEqual(len(rel_targets), 1)
        self.assertEqual(rel_targets[0], prim_path)

        # res = omni.kit.undo.undo()
        # self.assertTrue(res)
        # prim = stage.GetPrimAtPath(clip_path)
        # self.assertFalse(prim)


class TestSequencerClipCommands(AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        _, sequence = omni.kit.commands.execute("SequencerCreateSequenceCommand")
        await omni.kit.app.get_app().next_update_async()
        self.sequence_path = sequence.GetPrim().GetPath()
        self.track_name = "Asset Track"
        self.track_type = "Asset"
        # TODO: need to test different types of tracks...
        omni.kit.commands.execute("CreatePrimWithDefaultXformCommand", prim_type="Cube")
        await omni.kit.app.get_app().next_update_async()

        omni.kit.commands.execute("CreatePrimWithDefaultXformCommand", prim_type="Sphere")
        await omni.kit.app.get_app().next_update_async()

        res, track = omni.kit.commands.execute(
            "SequencerTrackCreateCommand",
            sequence_path=self.sequence_path,
            track_name=self.track_name,
            track_type=self.track_type,
        )
        await omni.kit.app.get_app().next_update_async()

        self.track = track
        self.track_path = self.track.GetPrim().GetPath().pathString

        prim_name = os.path.splitext(os.path.basename(ANIM_SKEL_WITH_CLIP))[0]
        self.prim_name = prim_name.partition(".")[0]
        res, self.anim_prim_path = await _add_reference(ANIM_SKEL_WITH_CLIP)
        self.assertTrue(res)
        await omni.kit.app.get_app().next_update_async()

    @skipIf(sys.platform.startswith("linux"), "Skip tests on linux to avoid hang on shutdown.")
    async def test_sequencer_clip_duplicate_command(self):
        stage = omni.usd.get_context().get_stage()
        clip_name = "Test_Clip"
        prim_path = "/Cube"
        clip_start = 2
        clip_end = 44
        select_prim = False

        res, orig_clip = omni.kit.commands.execute(
            "SequencerClipCreateCommand",
            track_path=self.track_path,
            clip_name=clip_name,
            prim_path=prim_path,
            clip_start=clip_start,
            clip_end=clip_end,
            select_prim=select_prim,
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        orig_clip_prim = orig_clip.GetPrim()
        orig_clip_path = orig_clip_prim.GetPath()
        self.assertTrue(orig_clip_prim.IsValid())

        res, clip = omni.kit.commands.execute(
            "SequencerClipDuplicateCommand", clip_id=orig_clip_path, inherit_translation=False
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        clip_prim = clip.GetPrim()
        clip_path = clip_prim.GetPath()
        self.assertTrue(clip_prim.IsA(SequenceSchema.AssetClip))

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        prim = stage.GetPrimAtPath(clip_path)
        self.assertFalse(prim)

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        prim = stage.GetPrimAtPath(clip_path)
        self.assertTrue(prim)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        prim = stage.GetPrimAtPath(clip_path)
        self.assertFalse(prim)

    async def test_sequencer_clip_update_time_commnand(self):
        clip_name = "Test_Clip"
        prim_path = "/Cube"
        clip_start = 2
        clip_end = 44
        select_prim = False

        res, clip = omni.kit.commands.execute(
            "SequencerClipCreateCommand",
            track_path=self.track_path,
            clip_name=clip_name,
            prim_path=prim_path,
            clip_start=clip_start,
            clip_end=clip_end,
            select_prim=select_prim,
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        clip_prim = clip.GetPrim()
        clip_path = clip_prim.GetPath()
        self.assertTrue(clip_prim.IsValid())

        new_clip_start = 3
        new_clip_end = 42

        res, _ = omni.kit.commands.execute(
            "SequencerClipUpdateTimeCommand", clip_id=clip_path, clip_start=new_clip_start, clip_end=new_clip_end
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        updated_start_time = clip.GetStartTimeAttr().Get()
        updated_end_time = clip.GetEndTimeAttr().Get()
        self.assertEqual(updated_start_time, new_clip_start)
        self.assertEqual(updated_end_time, new_clip_end)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        updated_start_time = clip.GetStartTimeAttr().Get()
        updated_end_time = clip.GetEndTimeAttr().Get()
        self.assertEqual(updated_start_time, clip_start)
        self.assertEqual(updated_end_time, clip_end)

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        updated_start_time = clip.GetStartTimeAttr().Get()
        updated_end_time = clip.GetEndTimeAttr().Get()
        self.assertEqual(updated_start_time, new_clip_start)
        self.assertEqual(updated_end_time, new_clip_end)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        updated_start_time = clip.GetStartTimeAttr().Get()
        updated_end_time = clip.GetEndTimeAttr().Get()
        self.assertEqual(updated_start_time, clip_start)
        self.assertEqual(updated_end_time, clip_end)


class TestSequencerClipSetProperties(AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        self.stage.SetEndTimeCode(600)

    async def setup_predicate(self):
        _, sequence = omni.kit.commands.execute("SequencerCreateSequenceCommand")
        await omni.kit.app.get_app().next_update_async()
        self.sequence_path = sequence.GetPrim().GetPath()
        res, self.skel_anim_prim_path = await _add_reference(ANIM_SKEL_WITH_CLIP)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        res, self.skel_clip_prim_path = await _add_reference(ANIM_SKEL_CLIP)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        self.skel_anim_prim_name = Sdf.Path(self.skel_anim_prim_path).name
        self.skel_clip_prim_name = Sdf.Path(self.skel_clip_prim_path).name
        self.skel_anim_prim = self.stage.GetPrimAtPath(self.skel_anim_prim_path)
        self.skel_clip_prim = self.stage.GetPrimAtPath(self.skel_clip_prim_path)

        self.track_name = self.skel_anim_prim_name

        res, self.track = omni.kit.commands.execute(
            "SequencerTrackCreateCommand",
            sequence_path=self.sequence_path,
            track_name=self.track_name,
            track_type="Asset",
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        track_path = self.track.GetPrim().GetPath().pathString

        clip_start = 0
        clip_end = 36

        res, self.clip = omni.kit.commands.execute(
            "SequencerClipCreateCommand",
            track_path=track_path,
            clip_name=self.skel_anim_prim_name,
            prim_path=self.skel_anim_prim_path,
            clip_start=clip_start,
            clip_end=clip_end,
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)

    async def test_sequencer_split_clip_cmd(self):
        await self.setup_predicate()
        usd_context = omni.usd.get_context()
        selection_before = omni.usd.get_context().get_selection()
        self.assertIsNotNone(self.clip)
        clip_path = self.clip.GetPath()
        res, _ = omni.kit.commands.execute(
            "SequencerClipUpdateTimeCommand", clip_id=clip_path, clip_start=0, clip_end=25
        )
        self.assertTrue(res)
        await omni.kit.app.get_app().next_update_async()

        looping_property_path = clip_path.AppendProperty("loop")
        omni.kit.commands.execute(
            "ChangePropertyCommand", prop_path=looping_property_path.pathString, value=True, prev=False
        )
        self.assertTrue(res)
        await omni.kit.app.get_app().next_update_async()

        self.clip.GetPlayStartAttr().Set(Sdf.TimeCode(1))
        self.clip.GetPlayEndAttr().Set(Sdf.TimeCode(120))

        res, new_clips = omni.kit.commands.execute(
            "SequencerClipSplitCommand", clip_paths=[clip_path.pathString], split_at_time=10
        )
        self.assertTrue(res)
        self.assertEqual(len(new_clips), 1)
        new_clip_path = new_clips[0].GetPath()
        new_clip_length = usd_sequencer.get_clip_length(new_clips[0])
        self.assertEqual(new_clip_length, 15)

        selection_after = usd_context.get_selection()
        self.assertListEqual(
            list(selection_after.get_selected_prim_paths()), ["/Sequence/skelcylinder_model/skelcylinder_model_01"]
        )

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        selection_after_undo = usd_context.get_selection()
        self.assertListEqual(
            list(selection_after_undo.get_selected_prim_paths()), ["/Sequence/skelcylinder_model/skelcylinder_model"]
        )

        new_clip_prim = self.stage.GetPrimAtPath(new_clip_path)
        self.assertFalse(new_clip_prim.IsValid())
        end_time = self.clip.GetEndTimeAttr().Get()
        self.assertEqual(end_time, 25)

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()

        new_clip_prim = self.stage.GetPrimAtPath(new_clip_path)
        self.assertTrue(new_clip_prim.IsValid())
        end_time = self.clip.GetEndTimeAttr().Get()
        self.assertEqual(end_time, 10)

    # test_sequencer_clip_use_selected_command (omni.kit.sequencer.core.tests.test_sequencer_commands.TestSequencerClipSetProperties)
    # Use selected prim as target command ... CRASH
    async def test_sequencer_clip_set_asset_prim_command(self):
        """Use selected prim as target command"""
        await self.setup_predicate()
        clip_prim = self.clip.GetPrim()
        clip_path = clip_prim.GetPath()
        res, new_prim_path = await _add_reference(NEW_PRIM_URL)
        _old_targets = usd_sequencer.get_clip_targets(self.clip)
        # track_name, clip_id, prim_path
        res, _ = omni.kit.commands.execute(
            "SequencerClipSetTargetCommand", clip_path=clip_path, asset_prim_path=new_prim_path
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        _new_targets = usd_sequencer.get_clip_targets(self.clip)
        self.assertNotEqual(_old_targets[0], _new_targets[0])
        self.assertEqual(_new_targets[0], new_prim_path)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        _new_targets = usd_sequencer.get_clip_targets(self.clip)
        self.assertNotEqual(_new_targets[0], new_prim_path)
        self.assertEqual(_new_targets[0], _old_targets[0])

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(res)
        _new_targets = usd_sequencer.get_clip_targets(self.clip)
        self.assertNotEqual(_old_targets[0], _new_targets[0])
        self.assertEqual(_new_targets[0], new_prim_path)

    @skipIf(sys.platform.startswith("linux"), "Skip tests on linux to avoid hang on shutdown.")
    async def test_sequencer_clip_set_animation_command(self):
        """Test 'Use Selected Prim As Animation' command."""
        await self.setup_predicate()
        clip_prim = self.clip.GetPrim()
        clip_path = clip_prim.GetPath()

        _old_animations = usd_sequencer.get_clip_animations(self.clip)
        self.assertFalse(_old_animations)

        res, _ = omni.kit.commands.execute(
            "SequencerClipUpdateTimeCommand", clip_id=clip_path, clip_start=6, clip_end=10
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        _old_start = self.clip.GetStartTimeAttr().Get().GetValue()
        self.assertEqual(_old_start, 6)
        _old_end = self.clip.GetEndTimeAttr().Get().GetValue()
        self.assertEqual(_old_end, 10)
        res, _ = omni.kit.commands.execute(
            "SequencerClipSetAnimationCommand",
            clip_path=clip_path,
            anim_prim_path=self.skel_clip_prim_path,
            update_clip_time=True,
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        _new_animations = usd_sequencer.get_clip_animations(self.clip)
        _new_anim_target = _new_animations[0]
        self.assertEqual(_new_anim_target, self.skel_clip_prim_path)

        clip_length = usd_sequencer.get_prim_available_length(self.skel_clip_prim)
        start_time = self.clip.GetStartTimeAttr().Get()
        self.assertEqual(start_time, _old_start)
        end_time = self.clip.GetEndTimeAttr().Get()
        self.assertEqual(end_time, _old_start + clip_length)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        self.assertFalse(usd_sequencer.get_clip_animations(self.clip))

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        _new_animations = usd_sequencer.get_clip_animations(self.clip)
        _new_anim_target = _new_animations[0]
        self.assertEqual(_new_anim_target, self.skel_clip_prim_path)

        # setting anim prim path to none clears the anim target
        res, _ = omni.kit.commands.execute(
            "SequencerClipSetAnimationCommand", clip_path=clip_path, anim_prim_path=None, update_clip_time=False
        )
        await omni.kit.app.get_app().next_update_async()
        _new_anim_target = usd_sequencer.get_clip_animations(self.clip)
        self.assertListEqual(_new_anim_target, [])


class TestSequencerSettingsCommands(AsyncTestCase):
    async def test_sequencer_settings_set_snap_to_frame_commnand(self):
        # SequencerSettingsSetSnapToFrameCommand snap_to_frame:bool
        # NOTE: Does this setting persist? Where?
        _previous_setting = sequencer_settings.snap_to_frame
        _new_setting = not _previous_setting
        res, _ = omni.kit.commands.execute("SequencerSettingsSetSnapToFrameCommand", on=_new_setting)
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        self.assertEqual(sequencer_settings.snap_to_frame, _new_setting)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        self.assertEqual(sequencer_settings.snap_to_frame, _previous_setting)

        res = omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        self.assertEqual(sequencer_settings.snap_to_frame, _new_setting)

        res = omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(res)
        self.assertEqual(sequencer_settings.snap_to_frame, _previous_setting)
