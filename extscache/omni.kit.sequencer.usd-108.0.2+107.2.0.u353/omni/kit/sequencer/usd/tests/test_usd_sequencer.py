from omni.kit.sequencer.usd.utils import AnimSection
import omni.kit.test
import omni.stageupdate
import omni.usd
from omni.kit.sequencer.usd import usd_sequencer
from pxr import Sdf, UsdGeom, Gf, Usd
import SequenceSchema


class TestUsdSequencer(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        stage.SetEndTimeCode(900)
        default_prim = stage.DefinePrim("/World", "XForm")
        stage.SetDefaultPrim(default_prim)
        await omni.kit.app.get_app().next_update_async()

    async def test_get_sequences(self):
        stage = omni.usd.get_context().get_stage()
        no_sequences = usd_sequencer.get_sequences()
        self.assertListEqual(no_sequences, [])

        sequence_path_1 = Sdf.Path("/SequenceTest")
        default_prim_path: Sdf.Path = stage.GetDefaultPrim().GetPath()
        sequence_path_2 = default_prim_path.AppendChild("SequenceTest_2")

        SequenceSchema.Sequence.Define(stage, sequence_path_1)
        sequence_paths = [seq.GetPath().pathString for seq in usd_sequencer.get_sequences()]
        self.assertListEqual(sequence_paths, [sequence_path_1.pathString])
        SequenceSchema.Sequence.Define(stage, sequence_path_2)
        sequence_paths = sorted([seq.GetPath().pathString for seq in usd_sequencer.get_sequences()])
        self.assertEqual(len(sequence_paths), 2)
        self.assertListEqual(sequence_paths, sorted([sequence_path_1.pathString, sequence_path_2.pathString]))

    async def test_get_sequence(self):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        no_sequence = usd_sequencer.get_sequence(stage)
        self.assertIsNone(no_sequence)

        default_prim_path: Sdf.Path = stage.GetDefaultPrim().GetPath()
        sequence_path_1 = Sdf.Path("/SequenceTest")
        SequenceSchema.Sequence.Define(stage, sequence_path_1)
        sequence = usd_sequencer.get_sequence(stage)
        self.assertIsNotNone(sequence)
        self.assertEqual(sequence.GetPath(), sequence_path_1.pathString)
        stage.RemovePrim(sequence_path_1)

        sequence_path_2 = default_prim_path.AppendChild("SequenceTest_2")
        SequenceSchema.Sequence.Define(stage, sequence_path_2)
        sequence = usd_sequencer.get_sequence(stage)
        self.assertIsNotNone(sequence)
        self.assertEqual(sequence.GetPath(), sequence_path_2.pathString)

    async def test_clip_source_time_util(self):
        stage = omni.usd.get_context().get_stage()
        sequence_path = Sdf.Path("/Sequence")
        track_path = sequence_path.AppendChild("Track")
        clip_path = track_path.AppendChild("Clip")
        xform_path = Sdf.Path("/Xform")

        cube = UsdGeom.Cube.Define(stage, xform_path)
        # attr_translate = cube.GetPrim().CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False)
        translate_op = cube.AddTranslateOp()
        translate_op.Set(time=1, value=Gf.Vec3d([0, 0, 0]))
        translate_op.Set(time=100, value=Gf.Vec3d([0, 10, 0]))

        sequence = SequenceSchema.Sequence.Define(stage, sequence_path)
        track = SequenceSchema.Track.Define(stage, track_path)
        clip = SequenceSchema.AssetClip.Define(stage, clip_path)
        clip.GetEndTimeAttr().Set(Sdf.TimeCode(200))
        clip.GetPlayStartAttr().Set(Sdf.TimeCode(0))
        clip.GetPlayEndAttr().Set(Sdf.TimeCode(100))
        usd_sequencer.set_clip_targets(clip, [xform_path])
        source_time = usd_sequencer.get_clip_source_time_from_parent_time(clip, 150)
        self.assertEqual(source_time.time, 100)
        self.assertEqual(source_time.infinity, AnimSection.POST_INFINITY)
        self.assertEqual(source_time.epsilon, 0)

        clip.GetLoopAttr().Set(True)
        source_time = usd_sequencer.get_clip_source_time_from_parent_time(clip, 150)
        self.assertEqual(source_time.time, 50)
        self.assertEqual(source_time.infinity, AnimSection.POST_INFINITY)
        self.assertEqual(source_time.epsilon, 0)

        clip.GetEndTimeAttr().Set(Sdf.TimeCode(400))
        clip.GetPlayRateAttr().Set(0.5)
        source_time = usd_sequencer.get_clip_source_time_from_parent_time(clip, 300)
        self.assertEqual(source_time.time, 100)
        self.assertEqual(source_time.infinity, AnimSection.POST_INFINITY)
        self.assertEqual(source_time.epsilon, 0)
