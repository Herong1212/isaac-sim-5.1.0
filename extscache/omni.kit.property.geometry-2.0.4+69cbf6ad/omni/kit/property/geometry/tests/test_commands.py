## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.app
import omni.kit.commands
import omni.kit.test
from omni.kit.test_suite.helpers import get_test_data_path, open_stage
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf


class TestCommandWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await open_stage(get_test_data_path(__name__, "geometry_test.usda"))

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_command_prim_var(self):
        stage = omni.usd.get_context().get_stage()

        prim = stage.GetPrimAtPath("/World/Cube")
        attr = prim.GetAttribute("primvars:test_int")
        self.assertFalse(attr.IsValid())

        # create primvar as int
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_int",
            prim_type=Sdf.ValueTypeNames.Int,
            value=123456,
        )
        attr = prim.GetAttribute("primvars:test_int")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), 123456)

        # try and change using bool
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_int",
            prim_type=Sdf.ValueTypeNames.Bool,
            value=True,
        )
        attr = prim.GetAttribute("primvars:test_int")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), 123456)

        # change primvar
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_int",
            prim_type=Sdf.ValueTypeNames.Int,
            value=654321,
        )
        attr = prim.GetAttribute("primvars:test_int")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), 654321)

        # undo
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()

        # verify undo removed primvar
        attr = prim.GetAttribute("primvars:test_int")
        self.assertFalse(attr.IsValid())

        # create primvar as bool
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_bool",
            prim_type=Sdf.ValueTypeNames.Bool,
            value=True,
        )
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), True)

        # try and change using int
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_bool",
            prim_type=Sdf.ValueTypeNames.Int,
            value=123456,
        )
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), True)

        # change primvar
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_bool",
            prim_type=Sdf.ValueTypeNames.Bool,
            value=False,
        )
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), False)

        # undo
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()

        # verify undo removed primvar
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertFalse(attr.IsValid())

    async def test_command_toggle_prim_var(self):
        stage = omni.usd.get_context().get_stage()

        prim = stage.GetPrimAtPath("/World/Cube")
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertFalse(attr.IsValid())

        # create primvar as bool
        omni.kit.commands.execute("TogglePrimVarCommand", prim_path=["/World/Cube"], prim_name="test_bool")
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), True)

        # try and change using int
        omni.kit.commands.execute(
            "PrimVarCommand",
            prim_path=["/World/Cube"],
            prim_name="test_bool",
            prim_type=Sdf.ValueTypeNames.Int,
            value=123456,
        )
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), True)

        # change primvar
        omni.kit.commands.execute("TogglePrimVarCommand", prim_path=["/World/Cube"], prim_name="test_bool")
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), False)

        # undo
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()

        # verify undo removed primvar
        attr = prim.GetAttribute("primvars:test_bool")
        self.assertFalse(attr.IsValid())

    async def test_command_toggle_instanceable(self):
        stage = omni.usd.get_context().get_stage()

        prim = stage.GetPrimAtPath("/World/Cube")
        self.assertFalse(prim.IsInstanceable())

        # toggle instanceable
        omni.kit.commands.execute("ToggleInstanceableCommand", prim_path=["/World/Cube"])
        self.assertTrue(prim.IsInstanceable())

        # toggle instanceable
        omni.kit.commands.execute("ToggleInstanceableCommand", prim_path=["/World/Cube"])
        self.assertFalse(prim.IsInstanceable())

        # undo
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()

        # verify undo
        self.assertFalse(prim.IsInstanceable())
