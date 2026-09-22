# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
import omni.usd
import unittest

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from pathlib import Path
from pxr import Usd, UsdGeom
import os
import asyncio


TEST_SERVER = "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.usd.fileformat.e57/sources/"


async def wait(count=30):
    for i in range(count):
        await omni.kit.app.get_app().next_update_async()

# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class Test(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_open(self):
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("bunnyDouble.e57"))
        self.assertTrue(os.path.exists(test_data_path))

        context = omni.usd.get_context()
        await context.open_stage_async(test_data_path)
        await wait()

        stage = context.get_stage()
        self.assertTrue(stage)

        xform_prim = stage.GetPrimAtPath("/data3D")
        self.assertTrue(xform_prim)

        prim = stage.GetPrimAtPath("/data3D/scan")
        self.assertTrue(prim)

    async def test_open_spherical(self):
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("pumpASpherical.e57"))
        self.assertTrue(os.path.exists(test_data_path))

        context = omni.usd.get_context()
        await context.open_stage_async(test_data_path)
        await wait(60)

        stage = context.get_stage()
        self.assertTrue(stage)

        xform_prim = stage.GetPrimAtPath("/data3D")
        self.assertTrue(xform_prim)

        prim = stage.GetPrimAtPath("/data3D/scan")
        self.assertTrue(prim)

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM")
    async def test_open_url(self):      # OM-93104
        context = omni.usd.get_context()
        await context.open_stage_async(TEST_SERVER + "bunnyDouble.e57")
        await wait()

        stage = context.get_stage()
        self.assertTrue(stage)

        xform_prim = stage.GetPrimAtPath("/data3D")
        self.assertTrue(xform_prim)

        prim = stage.GetPrimAtPath("/data3D/scan")
        self.assertTrue(prim)

    async def test_interpolation_type(self):    # OM-72158
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("bunnyDouble.e57"))
        self.assertTrue(os.path.exists(test_data_path))

        context = omni.usd.get_context()
        await context.open_stage_async(test_data_path)
        await wait()

        stage = context.get_stage()
        self.assertTrue(stage)

        prim = stage.GetPrimAtPath("/data3D/scan")
        self.assertTrue(prim)

        attr = UsdGeom.Points(prim).GetDisplayColorAttr()
        self.assertTrue(attr)
        self.assertTrue(attr.HasValue())
        self.assertTrue(attr.HasMetadata("interpolation"))

        self.assertEqual(attr.GetMetadata("interpolation"), "vertex")
