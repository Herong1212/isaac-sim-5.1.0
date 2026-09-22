
from ..scripts.rig import RetargetRig
from ..scripts.extension import has_retarget_setup, auto_setup, auto_pose
from .visual_test_base import AnimationVisualTestBase
from pathlib import Path
import omni.ui as ui
import omni.kit.property.usd
import omni.timeline
import carb.settings
import math

from pxr import Gf, Sdf, Usd, UsdGeom, UsdSkel
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
    ln = length(a)
    if ln > 0.001:
        return carb.Float3(a[0] / ln, a[1] / ln, a[2] / ln)
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
        # set the golden image dir it will be used in the do_visual_test function
        self._GOLDEN_IMG_DIR = extension_root_folder.joinpath("data/tests/golden")
        # set the map dir. it will be used in the load_stage function
        self._MAP_DIR = extension_root_folder.joinpath("data/tests/usd")

    '''
    Load the AnimGraph test map from the omniverse server. Start playing and advance one frame.
    Do a screen capture and compare with the golden image.
    '''

    async def plain_visual_test(self, map_name: str, golden_img_name: str, test_frame_count: int = 24):
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        timeline.set_current_time(0.0)
        timeline.set_auto_update(False)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # load the USD map, note: map_name should not start with /
        await self.load_stage(map_name=map_name)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await self.setup_viewport_test()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        for i in range(test_frame_count):
            timeline.forward_one_frame()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        # add extra wait before image capture to avoid affection from render result delay
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare_test(img_name=golden_img_name, threshold=0.1)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        timeline.set_auto_update(True)
        timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.restore()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    async def running_test(self, test_frame_count: int = 24):
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        timeline.set_current_time(0.0)
        timeline.set_auto_update(False)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        for i in range(test_frame_count):
            timeline.forward_one_frame()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        timeline.set_auto_update(True)
        timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.restore()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    async def test_retarget_core_visual_01_retargeting_graph(self):
        await self.plain_visual_test(
            map_name="VisualTest/retargeting-graph.usda",
            golden_img_name="retarget_core_01_retargeting_graph",
            test_frame_count=24
        )

    async def test_retarget_core_visual_02_retargeting_clip(self):
        await self.plain_visual_test(
            map_name="VisualTest/retargeting-clip.usda",
            golden_img_name="retarget_core_02_retargeting_clip",
            test_frame_count=24
        )

    async def test_auto_setup(self):
        # load the USD map, note: map_name should not start with /
        await self.load_stage(map_name="VisualTest/retargeting-clip.usda")
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        skeleton_prim_path = "/World/Character_Target/ManRoot/Debra/Debra/Debra"
        skel_prim = stage.GetPrimAtPath(skeleton_prim_path)
        skeleton = None
        if skel_prim:
            skeleton = UsdSkel.Skeleton(skel_prim)
        else:
            # failed
            self.assertTrue("Invalid input skeleton" and False)

        # first get the keyword from rig file
        # we need keywords - we can move keywords to RigAutoMapManager
        rig = RetargetRig("Human")
        rig.set_skeleton(skeleton)

        # Clear retarget tag and pose
        rig.reset_tags()
        rig.reset_retarget_pose()

        # test hasretarget set up code to make sure it's false
        self.assertTrue("Failed to clear the tags" and not has_retarget_setup(skel_prim))

        # call auto set up and see if it passes visual test
        # first test only mapping file path with bind pose
        rig.auto_setup(True, False, False, False)
        await self.running_test(test_frame_count=24)

    async def test_auto_setup_no_mapping(self):
        # load the USD map, note: map_name should not start with /
        await self.load_stage(map_name="VisualTest/retargeting-clip.usda")
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        skeleton_prim_path = "/World/Character_Target/ManRoot/Debra/Debra/Debra"
        skel_prim = stage.GetPrimAtPath(skeleton_prim_path)
        skeleton = None
        if skel_prim:
            skeleton = UsdSkel.Skeleton(skel_prim)
        else:
            # failed
            self.assertTrue(f"Invalid input skeleton" and False)

        # first get the keyword from rig file
        # we need keywords - we can move keywords to RigAutoMapManager
        rig = RetargetRig("Human")
        rig.set_skeleton(skeleton)

        # Clear retarget tag and pose
        rig.reset_tags()
        rig.reset_retarget_pose()

        # test hasretarget set up code to make sure it's false
        self.assertTrue("Failed to clear the tags" and not has_retarget_setup(skel_prim))

        # call auto set up and see if it passes visual test
        # first test only mapping file path with bind pose
        rig.auto_setup(False, True, True, True)

        await self.running_test(test_frame_count=24)

    async def test_auto_setup_human(self):
        # load the USD map, note: map_name should not start with /
        await self.load_stage(map_name="VisualTest/retargeting-clip.usda")
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        skeleton_prim_path = "/World/Character_Source/Root"
        skel_prim = stage.GetPrimAtPath(skeleton_prim_path)
        skeleton = None
        if skel_prim:
            skeleton = UsdSkel.Skeleton(skel_prim)
        else:
            # failed
            self.assertTrue("Invalid input skeleton" and False)

        self.assertTrue(has_retarget_setup(skel_prim))

        # first get the keyword from rig file
        # we need keywords - we can move keywords to RigAutoMapManager
        rig = RetargetRig("Human")
        rig.set_skeleton(skeleton)

        # Clear retarget tag and pose
        rig.reset_tags()
        rig.reset_retarget_pose()

        self.assertTrue(not has_retarget_setup(skel_prim))
        # test hasretarget set up code to make sure it's false
        self.assertTrue("Failed to clear the tags" and not has_retarget_setup(skel_prim))

        # call auto set up and see if it passes visual test
        auto_setup("Human", skeleton_prim_path, True, True, True, True)

        await self.running_test(test_frame_count=24)

    async def test_auto_pose(self):
        # load the USD map, note: map_name should not start with /
        await self.load_stage(map_name="VisualTest/retargeting-clip.usda")
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        skeleton_prim_path1 = "/World/Character_Target/ManRoot/Debra/Debra/Debra"
        skeleton_prim_path2 = "/World/Character_Source/Root"

        auto_pose(skeleton_prim_path1, skeleton_prim_path2)

        await self.running_test(test_frame_count=24)

    async def test_rig_class(self):
        rig = RetargetRig("Human")
        success, _, _ = rig.get_reference_skeleton()
        self.assertTrue(success)

        success, _ = rig.get_reference_animations()
        self.assertTrue(success)

        rig.clear_select()
        defaultTags = rig.get_default_tags()

        for tag in defaultTags:
            self.assertTrue(not rig.get_selected(tag))
            self.assertTrue(rig.is_default_tag(tag))
