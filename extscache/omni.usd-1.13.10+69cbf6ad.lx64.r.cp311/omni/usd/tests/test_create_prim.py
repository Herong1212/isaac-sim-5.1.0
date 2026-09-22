from cgitb import strong
from pathlib import Path
import carb
import omni.kit.test

import omni.kit.undo
import omni.kit.commands
import omni.timeline
import omni.usd
import omni.client
import omni.client.utils as clientutils

from pxr import Gf, Kind, Sdf, Usd, UsdGeom, UsdShade

class TestCreatePrimCommands(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    def assertAlmostEqualVec2f(self, a, b):
        self.assertAlmostEqual(a[0], b[0])
        self.assertAlmostEqual(a[1], b[1])

    async def test_create_prim_attr(self):
        settings = carb.settings.get_settings()
        stage = omni.usd.get_context().get_stage()

        # verify create created with no-attributes - Just get default values
        omni.kit.commands.execute("CreatePrim", prim_path="/Camera_defaults", prim_type="Camera", attributes={})
        prim = stage.GetPrimAtPath("/Camera_defaults")
        self.assertAlmostEqual(prim.GetAttribute("focalLength").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focalLength"))
        self.assertAlmostEqual(prim.GetAttribute("focusDistance").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focusDistance"))

        # verify create created with none-attributes - Don't get default values
        omni.kit.commands.execute("CreatePrim", prim_path="/Camera_none", prim_type="Camera", attributes=None)
        prim = stage.GetPrimAtPath("/Camera_none")
        self.assertNotEqual(prim.GetAttribute("focalLength").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focalLength"))
        self.assertNotEqual(prim.GetAttribute("focusDistance").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focusDistance"))

        # verify create created with attributes - Override default values
        omni.kit.commands.execute("CreatePrim", prim_path="/Camera_custom", prim_type="Camera", attributes={"focalLength": 10, "focusDistance": 32})
        prim = stage.GetPrimAtPath("/Camera_custom")
        self.assertAlmostEqual(prim.GetAttribute("focalLength").Get(), 10)
        self.assertAlmostEqual(prim.GetAttribute("focusDistance").Get(), 32)

    async def test_create_primxform_attr(self):
        settings = carb.settings.get_settings()
        stage = omni.usd.get_context().get_stage()

        # verify create created with no-attributes - Just get default values
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_path="/Camera_defaults", prim_type="Camera", attributes={})
        prim = stage.GetPrimAtPath("/Camera_defaults")
        self.assertAlmostEqual(prim.GetAttribute("focalLength").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focalLength"))
        self.assertAlmostEqual(prim.GetAttribute("focusDistance").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focusDistance"))

        # verify create created with none-attributes - Don't get default values
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_path="/Camera_none", prim_type="Camera", attributes=None)
        prim = stage.GetPrimAtPath("/Camera_none")
        self.assertNotEqual(prim.GetAttribute("focalLength").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focalLength"))
        self.assertNotEqual(prim.GetAttribute("focusDistance").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focusDistance"))

        # verify create created with attributes - Override default values
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_path="/Camera_custom", prim_type="Camera", attributes={"focalLength": 10, "focusDistance": 32})
        prim = stage.GetPrimAtPath("/Camera_custom")
        self.assertAlmostEqual(prim.GetAttribute("focalLength").Get(), 10)
        self.assertAlmostEqual(prim.GetAttribute("focusDistance").Get(), 32)

    async def test_create_ortho_prim_attr(self):
        settings = carb.settings.get_settings()
        stage = omni.usd.get_context().get_stage()

        # verify create created with no-attributes - Just get default values
        omni.kit.commands.execute("CreatePrim", prim_path="/Camera_defaults", prim_type="Camera", attributes={"projection": "orthographic"})
        prim = stage.GetPrimAtPath("/Camera_defaults")
        self.assertAlmostEqual(prim.GetAttribute("focalLength").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focalLength"))
        self.assertAlmostEqual(prim.GetAttribute("focusDistance").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focusDistance"))
        self.assertAlmostEqualVec2f(list(prim.GetAttribute("clippingRange").Get()), settings.get("persistent/app/primCreation/typedDefaults/orthoCamera/clippingRange"))

    async def test_create_ortho_primxform_attr(self):
        settings = carb.settings.get_settings()
        stage = omni.usd.get_context().get_stage()

        # verify create created with no-attributes - Just get default values
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_path="/Camera_defaults", prim_type="Camera", attributes={"projection": "orthographic"})
        prim = stage.GetPrimAtPath("/Camera_defaults")
        self.assertAlmostEqual(prim.GetAttribute("focalLength").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focalLength"))
        self.assertAlmostEqual(prim.GetAttribute("focusDistance").Get(), settings.get("persistent/app/primCreation/typedDefaults/camera/focusDistance"))
        self.assertAlmostEqualVec2f(list(prim.GetAttribute("clippingRange").Get()), settings.get("persistent/app/primCreation/typedDefaults/orthoCamera/clippingRange"))
