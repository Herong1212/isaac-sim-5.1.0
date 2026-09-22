
from .visual_test_base import SkelJointVisualTestBase
from pathlib import Path
import omni.ui as ui
import omni.kit.property.usd
import omni.timeline
import carb.settings
import math
import time

from pxr import Usd, Gf, Sdf, UsdGeom, UsdSkel


def convert(v):
    return carb.Float3(v[0], v[1], v[2])


def add(a, b):
    return carb.Float3(a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return carb.Float3(a[0] - b[0], a[1] - b[1], a[2] - b[2])


def length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def normalize(a, d):
    len_value = length(a)
    if len_value > 0.001:
        return carb.Float3(a[0] / len_value, a[1] / len_value, a[2] / len_value)
    else:
        return d


def scale(v, f):
    return carb.Float3(v[0] * f, v[1] * f, v[2] * f)


def lerp(a, b, t):
    return add(a, scale(sub(b, a), t))


def clamp(x, low, high):
    return max(min(x, high), low)


class SkelJointVisualTests(SkelJointVisualTestBase):
    '''
        Setup will set the
            1. self._GOLDEN_IMG_DIR
            2. self._MAP_DIR
            They will be served as the root folder of the golden image and USD map
    '''
    async def setUp(self):
        await super().setUp()
        extension_root_folder = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
        # Set the golden image dir it will be used in the do_visual_test function
        self._GOLDEN_IMG_DIR = extension_root_folder.joinpath("data/tests/golden")
        # Set the map dir. it will be used in the load_stage function
        self._MAP_DIR = extension_root_folder.joinpath("data/tests/usd")

    '''
    Load the AnimGraph test map from the omniverse server. Start playing and advance one frame.
    Do a screen capture and compare with the golden image.
    '''
    async def plain_visual_test(self, map_name: str, golden_img_name: str, test_frame_count: int = 24, skel_root_path: str = ""):
        #return #skip for Linux test failure for now
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        timeline.set_current_time(0.0)
        timeline.set_auto_update(False)
        timeline.set_fast_mode(True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # load the USD map, note: map_name should not start with /
        await self.load_stage(map_name=map_name)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.setup_viewport_test()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        for i in range(test_frame_count):
            timeline.forward_one_frame()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        settings = carb.settings.get_settings()
        settings.set_bool("persistent/app/viewport/Viewport/Viewport0/scene/skeletons/visible", True)

        # add extra wait before image capture to avoid affection from render result delay
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare_test(img_name=golden_img_name)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        timeline.set_auto_update(True)
        timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.restore()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    # async def test_skeljoint_visual_00_play(self):
    #     settings = carb.settings.get_settings()
    #     settings.set_bool("/persistent/omnihydra/useSkelAdapterBlendShape", False)
    #     await self.plain_visual_test(
    #         map_name="skelcylinder_ref.usda",
    #         golden_img_name="skeljoint_00_play_animation",
    #         test_frame_count=24,
    #         skel_root_path="/Root/group1"
    #     )

    # async def test_skeljoint_visual_01_move_skelroot(self):
    #     map_name = "skelcylinder_ref.usda"
    #     golden_img_name = "skeljoint_01_move_skelroot"
    #     skel_root_path = "/Root/group1"

    #     settings = carb.settings.get_settings()
    #     settings.set_bool("/persistent/omnihydra/useSkelAdapterBlendShape", False)

    #     timeline = omni.timeline.get_timeline_interface()
    #     timeline.stop()
    #     timeline.set_current_time(0.0)
    #     timeline.set_auto_update(False)
    #     timeline.set_fast_mode(True)
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()

    #     # load the USD map, note: map_name should not start with /
    #     await self.load_stage(map_name=map_name)
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()

    #     await self.setup_viewport_test()
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()

    #     timeline.play()
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()

    #     omni.kit.commands.execute(
    #         "TransformPrimSRT",
    #         path=skel_root_path,
    #         new_translation=(0.0, -5.0, 0.0),
    #         new_rotation_euler=(0, 0, 0),
    #         new_scale=(1, 1, 1),
    #     )

    #     # timeline.forward_one_frame()
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()

    #     settings.set_bool("persistent/app/viewport/Viewport/Viewport0/scene/skeletons/visible", True)
    #     # add extra wait before image capture to avoid affection from render result delay
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()
    #     await self.capture_and_compare_test(img_name=golden_img_name)
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()
    #     timeline.set_auto_update(True)
    #     timeline.stop()
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()

    #     await self.restore()
    #     await omni.kit.app.get_app().next_update_async()
    #     await omni.kit.app.get_app().next_update_async()
