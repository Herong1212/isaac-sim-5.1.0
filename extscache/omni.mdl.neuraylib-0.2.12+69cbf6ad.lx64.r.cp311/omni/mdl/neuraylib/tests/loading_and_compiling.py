from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading
from unittest import skipIf

from .utils import *
import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper
import carb
import carb.settings

# OMPE-21612: some features are not available in legacy.hydra anymore
option = carb.settings.get_settings().get("exts/omni.mdl.neuraylib/tests/legacyHydra")
LEGACY_HYDRA: bool = True if (isinstance(option, bool) and option) else False

class LoadingAndCompilingTest(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        await closeStage()

    # base test case
    async def base_loading_and_compiling_test(self, stage: str):
        # open a simple scene with a mesh and a material assigned
        await open_stage(stage)
        await wait_stage_loading()
        # at the moment, don't do anything expect checking for errors in the logs

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # OMPE-16180: MDL backends produced wrong texture_isvalid functions with suffix
    async def test_tex_isvalid_3d(self):
        await self.base_loading_and_compiling_test(get_usd_scene_path('loading_tests/tex_isvalid_3d.usda'))

    # OMPE-15153: handle wrong resource consturctors with empty string, e.g., texture_2d("")
    async def test_tex_empty_string(self):
        await self.base_loading_and_compiling_test(get_usd_scene_path('loading_tests/wrong_empty_texture_path.usda'))

    # OMPE-15485: percent encoding of spaces. there wasn't a bug. test is added for completeness
    async def test_folder_with_spaces(self):
        await self.base_loading_and_compiling_test(get_usd_scene_path('loading_tests/folder_with_spaces.usda'))

    # OMPE-16695: add support for array parameters and corresponding overrides from USD
    @skipIf(LEGACY_HYDRA, "Skip Iray tests that are not supported anymore.")
    async def test_arrays_static_sized(self):
        await self.base_loading_and_compiling_test(get_usd_scene_path('arrays/array_examples_scene_static.usda'))

    @skipIf(LEGACY_HYDRA, "Skip Iray tests that are not supported anymore.")
    async def test_arrays_dynamic_sized(self):
        await self.base_loading_and_compiling_test(get_usd_scene_path('arrays/array_examples_scene_dynamic.usda'))
