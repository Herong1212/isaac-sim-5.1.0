
from .visual_test_base import AnimationVisualTestBase
from pathlib import Path
import omni.ui as ui
import omni.kit.property.usd
import omni.timeline
import omni.anim.graph.core as ag
import carb.settings
import math
import time

from pxr import Usd, Gf, Sdf, UsdGeom, UsdSkel
import AnimGraphSchema

def convert(v):
    return carb.Float3(v[0], v[1], v[2])

def add(a, b):
    return carb.Float3(a[0] + b[0], a[1] + b[1], a[2] + b[2])

def sub(a, b):
    return carb.Float3(a[0] - b[0], a[1] - b[1], a[2] - b[2])

def length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def normalize(a, d):
    l = length(a)
    if l > 0.001:
        return carb.Float3(a[0] / l, a[1] / l, a[2] / l)
    else:
        return d

def scale(v, f):
    return carb.Float3(v[0] * f, v[1] * f, v[2] * f)

def lerp(a, b, t):
    return add(a, scale(sub(b, a), t))

def clamp(x, low, high):
    return max(min(x, high), low)

class AnimGraphVisualTests(AnimationVisualTestBase):
    '''
        Setup will set the
            1. self._GOLDEN_IMG_DIR
            2. self._MAP_DIR
            They will be served as the root folder of the golden image and USD map
    '''
    async def setUp(self):
        await super().setUp()
        extension_root_folder = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
        #Set the golden image dir it will be used in the do_visual_test function
        self._GOLDEN_IMG_DIR = extension_root_folder.joinpath("data/tests/golden")
        #Set the map dir. it will be used in the load_stage function
        self._MAP_DIR = extension_root_folder.joinpath("data/tests/usd")

    '''
    Load the AnimGraph test map from the omniverse server. Start playing and advance one frame.
    Do a screen capture and compare with the golden image.
    '''

    def get_characters(self):
        result = []
        context = omni.usd.get_context()
        if context:
            stage = context.get_stage()
            if stage is not None:
                for prim in Usd.PrimRange(stage.GetPseudoRoot()):
                    if prim.IsA(UsdSkel.Root) and prim.HasAPI(AnimGraphSchema.AnimationGraphAPI):
                        result.append(str(prim.GetPath()))
        return result

    async def plain_visual_test(self, map_name: str, golden_img_name: str, test_frame_count: int = 24, character_path: str = ""):
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        timeline.set_current_time(0.0)
        timeline.set_auto_update(False)
        timeline.set_fast_mode(True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        #Load the USD map, note: map_name should not start with /
        await self.load_stage(map_name=map_name)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()
        await self.setup_viewport_test()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        timeline.play()
        time = timeline.get_current_time()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        if character_path != "":
            character = ag.get_character(character_path)
        self.assertIsNot(character, None)
        for i in range(test_frame_count):
            timeline.forward_one_frame()
            time = timeline.get_current_time()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        # add extra wait before image capture to avoid affection from render result delay
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        time = timeline.get_current_time()
        await self.capture_and_compare_test(img_name=golden_img_name)
        time = timeline.get_current_time()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        timeline.set_auto_update(True)
        timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.restore()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    async def test_animation_graph_visual_01_play_animation(self):
        await self.plain_visual_test(
            map_name = "VisualTest/play_animation.usda",
            golden_img_name= "animation_graph_core_01_play_animation",
            test_frame_count = 24,
            character_path = "/World/Character"
            )

    async def test_animation_graph_visual_02_blend(self):
        await self.plain_visual_test(
            map_name = "VisualTest/blend.usda",
            golden_img_name= "animation_graph_core_02_blend",
            test_frame_count = 12,
            character_path = "/World/Character"
            )

    async def test_animation_graph_visual_03_mm_script(self):
        await self.plain_visual_test(
            map_name = "VisualTest/mm_script.usda",
            golden_img_name= "animation_graph_core_03_mm_script",
            test_frame_count = 24,
            character_path = "/World/Character"
            )

    async def test_animation_graph_visual_04_mm_path_point(self):
        await self.plain_visual_test(
            map_name = "VisualTest/mm_path_point.usda",
            golden_img_name= "animation_graph_core_04_mm_path_point",
            test_frame_count = 24,
            character_path = "/World/Character"
            )

    async def test_animation_graph_visual_05_blend_instancing(self):
        await self.plain_visual_test(
            map_name = "VisualTest/blend_instancing.usda",
            golden_img_name= "animation_graph_core_05_blend_instancing",
            test_frame_count = 24,
            character_path = "/World/Character_Left"
            )

    async def test_animation_graph_visual_06_filter(self):
        await self.plain_visual_test(
            map_name = "VisualTest/filter.usda",
            golden_img_name= "animation_graph_core_06_filter",
            test_frame_count = 24,
            character_path = "/World/Character"
            )

    async def test_animation_graph_visual_07_look_at_IK(self):
        await self.plain_visual_test(
            map_name = "VisualTest/look_at_ik.usda",
            golden_img_name= "animation_graph_core_07_look_at_ik",
            test_frame_count = 24,
            character_path = "/World/Character"
            )

    async def test_animation_graph_visual_08_state_machine(self):
        # TODO: this is not ideal, the action graph uses a delay to set the variable. We should control it in script as well to avoid discrepencies.
        await self.plain_visual_test(
            map_name = "VisualTest/state_machine.usda",
            golden_img_name= "animation_graph_core_08_state_machine",
            test_frame_count = 24,
            character_path = "/World/biped_demo"
            )

    async def test_animation_graph_visual_09_z_axis_up(self):
        await self.plain_visual_test(
            map_name = "VisualTest/z_axis_up.usda",
            golden_img_name= "animation_graph_core_09_z_axis_up",
            test_frame_count = 24,
            character_path = "/World/Characters/Tom/ManRoot/female_adult_police_01"
            )

    async def test_animation_graph_visual_10_external_graph(self):
        await self.plain_visual_test(
            map_name = "VisualTest/external_graph.usda",
            golden_img_name= "animation_graph_core_10_external_graph",
            test_frame_count = 24,
            character_path = "/World/Character"
            )

    #async def test_basic_hello_world(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Basic/hello-world.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    await self.setup_viewport_test()


    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    time = timeline.get_current_time()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Character")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        timeline.forward_one_frame()
    #        time = timeline.get_current_time()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    time = timeline.get_current_time()
    #    await self.capture_and_compare_test(img_name="animgraph_test_hello_world")
    #    time = timeline.get_current_time()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.set_auto_update(True)
    #    timeline.stop()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Basic/hello-world-zup.usda")
    #    stage = omni.usd.get_context().get_stage()
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Character")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_hello_world-zup")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_basic_blending(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Basic/blending.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script1")
    #    script.GetRelationship("target").ClearTargets(False)
    #    script = stage.GetPrimAtPath("/World/Script2")
    #    script.GetRelationship("target").ClearTargets(False)
    #    script = stage.GetPrimAtPath("/World/Script3")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Character1")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        character.set_variable("Test", 0.7)
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_blending")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_basic_filter(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Basic/filter.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Biped")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_filter")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_basic_blending_blendshape(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Basic/blending_blendshape.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/BehaviorScript")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/mark_head/OUTPUT")
    #    self.assertIsNot(character, None)
    #    for i in range(12):
    #        character.set_variable("BlendWeight", 0.7)
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_blending_blendshape")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_basic_statemachine(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Basic/state-machine.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Character")
    #    self.assertIsNot(character, None)
    #    character.set_variable("State", "Move")
    #    character.set_variable("Speed", 100.0)
    #    for i in range(12):
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_statemachine_move")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character.set_variable("State", "Action")
    #    for i in range(24):
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_statemachine_action")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_IK_full_body_ik(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="IK/full-body-ik.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Biped")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        positionLeft = stage.GetPrimAtPath("/World/TargetLeft").GetAttribute('xformOp:translate').Get()
    #        positionRight = stage.GetPrimAtPath("/World/TargetRight").GetAttribute('xformOp:translate').Get()
    #        character.set_variable("TargetLeft", convert(positionLeft))
    #        character.set_variable("TargetRight", convert(positionRight))
    #        character.set_variable("WeightLeft", 1.0)
    #        character.set_variable("WeightRight", 1.0)
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_full_body_ik")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_IK_look_at_ik(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="IK/look-at-ik.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Biped")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        character.set_variable("TargetPosition", carb.Float3(1000.0, 160.0, 500.0))
    #        character.set_variable("BlendWeight", 1.0)
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_look_at_ik")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_Locomotion_follow_path(self):
    #    def get_waypoints(character_prim):
    #        waypoints = character_prim.GetProperty('waypoints').GetTargets()
    #        positions = []
    #        for waypoint in waypoints:
    #            xform = character_prim.GetStage().GetPrimAtPath(waypoint)
    #            position = xform.GetAttribute('xformOp:translate').Get()
    #            positions.append(convert(position))
    #        return positions


    #    def get_character_position(character):
    #        t = carb.Float3(0, 0, 0)
    #        q = carb.Float4(0, 0, 0, 0)
    #        character.get_world_transform(t, q)
    #        return t

    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Locomotion/follow-path.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character_name = "/World/Biped"
    #    character = ag.get_character(character_name)
    #    character_prim = stage.GetPrimAtPath(character_name)
    #    self.assertIsNot(character, None)
    #    for i in range(48):
    #        # Retrieve waypoints from USD prim
    #        # rel waypoints = [ <A>, <B>, <C>, ...  ]
    #        waypoints = get_waypoints(character_prim)

    #        # Construct trajectory from waypoints.
    #        # This could be done during initialization, but doing
    #        # it here allows us to move the waypoints around during play mode.
    #        trajectory = ag.trajectory(waypoints, True)

    #        ## Display the generated trajectory curve
    #        #trajectory.debugDraw(0xFFFFFFFF, 20.0)

    #        # Retrieve the current position of the character
    #        current_position = get_character_position(character)

    #        # Find the nearest point on the trajectory curve w.r.t.  the
    #        # current character position
    #        distance_along_curve = trajectory.nearestPoint(current_position)
    #        nearest_point = trajectory.getPosition(distance_along_curve)

    #        # Calculate the direction along the trajectory curve at this point
    #        direction_along_curve = trajectory.getTangent(distance_along_curve)
    #        direction_along_curve = normalize(direction_along_curve,
    #        direction_along_curve)

    #        # Calculate the direction from the current character
    #        # position towards the nearest point on the trajectory curve
    #        direction_towards_curve = normalize(sub(nearest_point,
    #        current_position), direction_along_curve)

    #        # Interpolate between the direction towards the curve and the
    #        # direction along the curve
    #        # The interpolation factor is a function of the character's
    #        # distance to the curve
    #        # In other words, the further away the character is from the curve
    #        # the more we steer
    #        # orthorgonal towards the curve.  The closer the character is to
    #        # the curve the more we steer
    #        # along the actual intended trajectory curve.
    #        distance_to_curve = length(sub(nearest_point, current_position))
    #        factor = clamp(distance_to_curve / 130, 0.0, 1.0)
    #        movementDirection = lerp(direction_along_curve,
    #        direction_towards_curve, factor)

    #        ## Display both directions, the direction towards the curve and
    #        ## the direction along the curve
    #        #self.display_direction(nearest_point, direction_along_curve,
    #        #0xFFFF0000)
    #        #self.display_direction(current_position, direction_towards_curve,
    #        #0xFFFF0000)

    #        # Smoothly interpolate movement speed based on keyboard input
    #        weight = 1.0
    #        speed = weight * 1.0

    #        #
    #        # Now forward all calculated quantities to the animation graph
    #        #

    #        forwardDirection = carb.Float3(0.0, 0.0, 1.0)
    #        # Set the current desired state of the character
    #        if speed >= 0.15:
    #            forwardDirection = movementDirection
    #            character.set_variable("State", "Move")
    #        else:
    #            character.set_variable("State", "Idle")

    #        # Set the movement and forward direction
    #        character.set_variable("MovementDirection", scale(movementDirection, speed))
    #        character.set_variable("ForwardDirection", forwardDirection)

    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_follow_path")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()


    #async def test_Locomotion_motion_matching(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Locomotion/motion-matching.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Biped")
    #    self.assertIsNot(character, None)
    #    for i in range(24):
    #        analogSpeed = 1.0
    #        movementDirection = carb.Float3(0,0,1)
    #        forwardDirection = carb.Float3(1,0,0)
    #        # Transform input into camera relative movement direction
    #        if analogSpeed >= 0.15:     # gamepad deadzone threshold
    #            #self.display_direction(self.movementDirection, 0xFFFFFFFF)
    #            character.set_variable("State", "Move")
    #        else:
    #            character.set_variable("State", "Idle")

    #        # Set control variables in animation graph
    #        character.set_variable("MovementDirection", scale(movementDirection, analogSpeed * 1.0))
    #        character.set_variable("ForwardDirection", forwardDirection)
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_motion_matching")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_PoseProvider_pose_provider(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="PoseProvider/pose_provider.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    script = stage.GetPrimAtPath("/World/Script")
    #    script.GetRelationship("target").ClearTargets(False)
    #    await self.setup_viewport_test()

    #    stage.SetEndTimeCode(22)
    #    timeline.set_looping(True)

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    character = ag.get_character("/World/Character")
    #    self.assertIsNot(character, None)

    #    for i in range(36):
    #        previous_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()
    #        timeline.forward_one_frame()
    #        current_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()

    #        animprim = stage.GetPrimAtPath("/World/AnimationLibrary/RunFwdLoop")
    #        anim = UsdSkel.Animation(animprim)
    #        trans = anim.GetTranslationsAttr().Get(current_frame_code)
    #        quats = anim.GetRotationsAttr().Get(current_frame_code)
    #        scales = anim.GetScalesAttr().Get(current_frame_code)
    #        translist = [carb.Float3(i[0], i[1], i[2]) for i in trans ]
    #        translist[0] = carb.Float3(0.0, 0.0, 0.0)
    #        quatslist = [carb.Float4(i.imaginary[0], i.imaginary[1], i.imaginary[2], i.real) for i in quats ]
    #        quatslist[0] = carb.Float4(0.0, 0.0, 0.0, 1.0)
    #        scaleslist = [carb.Float3(i)  for i in scales ]
    #        character.set_transform_buffer("PoseProvider", len(trans), translist, quatslist, scaleslist)

    #        current_trans = trans[0]
    #        current_quat = quats[0]
    #        trans1 = anim.GetTranslationsAttr().Get(previous_frame_code)
    #        quats1 = anim.GetRotationsAttr().Get(previous_frame_code)
    #        previous_trans = trans1[0]
    #        previous_quat = quats1[0]

    #        inv_previous_quat = previous_quat.GetInverse()
    #        inv_previous_mat = Gf.Matrix4f()
    #        inv_previous_mat.SetRotateOnly(inv_previous_quat)

    #        delta_trans = current_trans - previous_trans
    #        delta_trans_carb = carb.Float3(delta_trans[0]* 0.01, delta_trans[1]*0.01, delta_trans[2]*0.01)
    #        delta_quat = inv_previous_quat * current_quat
    #        delta_quat_carb = carb.Float4(delta_quat.imaginary[0], delta_quat.imaginary[1], delta_quat.imaginary[2], delta_quat.real)
    #        character.set_transform_delta("PoseProvider", delta_trans_carb, delta_quat_carb)

    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_test_pose_provider")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_looping(False)
    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_Retargeting_retargeting(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Retargeting/retargeting.usda")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    for i in range(48):
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_retargeting")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #async def test_Retargeting_retargeting_hydra(self):
    #    timeline = omni.timeline.get_timeline_interface()
    #    timeline.stop()
    #    timeline.set_current_time(0.0)
    #    timeline.set_auto_update(False)
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    #Load the USD map, note: map_name should not start with /
    #    await self.load_stage(map_name="Retargeting/retargeting_hydra.usd")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    stage = omni.usd.get_context().get_stage()
    #    await self.setup_viewport_test()

    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    timeline.play()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    for i in range(48):
    #        timeline.forward_one_frame()
    #        await omni.kit.app.get_app().next_update_async()
    #        await omni.kit.app.get_app().next_update_async()

    #    # add extra wait before image capture to avoid affection from render result delay
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
    #    await self.capture_and_compare_test(img_name="animgraph_retargeting_hydra")
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    timeline.set_auto_update(True)
    #    timeline.stop()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()

    #    await self.restore()
    #    await omni.kit.app.get_app().next_update_async()
    #    await omni.kit.app.get_app().next_update_async()
