from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

from .utils import *
import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper

class AutoTypeConversionTest(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        await closeStage()

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # auto type conversions for function attachements of builtin types
    # this tests to conversion from:
    # - color to color (no conversion)
    # - float to color
    # - float3 to color
    # - bool to float
    # - int to float
    # Note, this is only an example but the algorithmn should by type agnostic
    async def test_builtins_working(self):
        await open_stage(get_usd_scene_path('autoTypeConversion/builtins_working.usda'))
        await omni.kit.app.get_app().next_update_async()

    # auto type conversions for function attachements of user defined type
    # this tests to conversion from:
    # - reexported enum to original enum (correct detection of the cast operator)
    # - reexported struct to original struct (correct detection of the cast operator)
    async def test_user_types_working(self):
        await open_stage(get_usd_scene_path('autoTypeConversion/user_types_working.usda'))
        await omni.kit.app.get_app().next_update_async()

    # auto type conversions for function attachements of builtin types
    # this tests the fallbacks for convertions that are expected to fail:
    # - float4 to color
    # Note, this is only an example but the algorithmn should by type agnostic
    async def test_builtins_expected_failures(self):
        await open_stage(get_usd_scene_path('autoTypeConversion/builtins_expected_failures.usda'))
        await omni.kit.app.get_app().next_update_async()

    # auto type conversions for function attachements of user defined type
    # this tests the fallbacks for convertions that are expected to fail:
    # - assignment of incompatible enums
    # - assign struct to color
    # - assign color to struct
    async def test_user_types_expected_failures(self):
        await open_stage(get_usd_scene_path('autoTypeConversion/user_types_expected_failures.usda'))
        await omni.kit.app.get_app().next_update_async()