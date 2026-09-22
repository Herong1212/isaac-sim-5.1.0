from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

from .utils import *
import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper


class UsdzTest(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        await closeStage()

    # base test case for usdz support
    async def base_usdz_test(self, stage: str):
        # open a simple scene with a mesh and a material assigned
        await open_stage(stage)
        await wait_stage_loading()
        # at the moment, don't do anything expect checking for errors in the logs

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    async def test_textured_local(self):
        await self.base_usdz_test(get_usdz_scene_path('textured.usdz'))

    async def test_textured_nucleus(self):
        await self.base_usdz_test('omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usdz/textured.usdz')

    async def test_with_imports_local(self):
        await self.base_usdz_test(get_usdz_scene_path('with_import.usdz'))

    async def test_with_imports_nucleus(self):
        await self.base_usdz_test('omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usdz/with_import.usdz')

    # TODO this is a bug in the usdz export
    async def test_missing_body_resource_local(self):
        await self.base_usdz_test(get_usdz_scene_path('missing_body_resource.usdz'))

    # TODO limitation
    async def test_tiled_resources_local(self):
        await self.base_usdz_test(get_usdz_scene_path('udim.usdz'))
