## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import sys
import unittest

import omni.kit.app
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from pxr import Gf


class TransformContextMenu(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    @unittest.skipIf(sys.platform.startswith("linux"), "Pyperclip fails on some TeamCity agents")
    async def test_transform_context_menu(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        await wait_stage_loading()

        # get prim attributes
        torus_translate = stage.GetPrimAtPath("/World/Torus").GetAttribute("xformOp:translate")
        cone_translate = stage.GetPrimAtPath("/World/Cone").GetAttribute("xformOp:translate")
        torus_rotate = stage.GetPrimAtPath("/World/Torus").GetAttribute("xformOp:rotateXYZ")
        cone_rotate = stage.GetPrimAtPath("/World/Cone").GetAttribute("xformOp:rotateXYZ")
        torus_scale = stage.GetPrimAtPath("/World/Torus").GetAttribute("xformOp:scale")
        cone_scale = stage.GetPrimAtPath("/World/Cone").GetAttribute("xformOp:scale")

        # verify transforms different
        self.assertNotEqual(torus_translate.Get(), cone_translate.Get())
        self.assertNotEqual(torus_rotate.Get(), cone_rotate.Get())
        self.assertNotEqual(torus_scale.Get(), cone_scale.Get())

        # select torus
        await select_prims(["/World/Torus"])
        await ui_test.human_delay()

        # right click on transform header
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Transform'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        # context menu copy
        await ui_test.select_context_menu("Copy All Property Values in Transform", offset=ui_test.Vec2(10, 10))

        # select cone
        await select_prims(["/World/Cone"])
        await ui_test.human_delay()

        # right click on Transform header
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Transform'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        # context menu paste
        await ui_test.select_context_menu("Paste All Property Values to Transform", offset=ui_test.Vec2(10, 10))
        # verify transforms same
        self.assertEqual(torus_translate.Get(), cone_translate.Get())
        self.assertEqual(torus_rotate.Get(), cone_rotate.Get())
        self.assertEqual(torus_scale.Get(), cone_scale.Get())

        # select torus
        await select_prims(["/World/Torus"])
        await ui_test.human_delay()

        # right click on Transform header
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Transform'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        # context menu reset
        await ui_test.select_context_menu("Reset All Property Values in Transform", offset=ui_test.Vec2(10, 10))
        # verify transforms reset
        self.assertEqual(torus_translate.Get(), Gf.Vec3d(0, 0, 0))
        self.assertEqual(torus_rotate.Get(), Gf.Vec3d(0, 0, 0))
        self.assertEqual(torus_scale.Get(), Gf.Vec3d(1, 1, 1))
