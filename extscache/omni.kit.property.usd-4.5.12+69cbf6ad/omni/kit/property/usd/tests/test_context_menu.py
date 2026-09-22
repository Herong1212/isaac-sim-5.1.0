## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
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


class USDContextMenu(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 128)
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)

    # After running each test
    async def tearDown(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await wait_stage_loading()

    async def test_usd_context_menu(self):
        await wait_stage_loading()

        # select prim
        await select_prims(["/World"])
        await ui_test.human_delay(10)

        # right click on Raw USD Properties header
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        await ui_test.human_delay(10)
        # context menu copy
        await ui_test.select_context_menu(
            'Copy All Property Values in "Raw USD Properties"', offset=ui_test.Vec2(10, 10)
        )

        # select prim
        await select_prims(["/World/Looks"])
        await ui_test.human_delay(10)

        # right click on Raw USD Properties header
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        await ui_test.human_delay(10)
        # context menu copy
        await ui_test.select_context_menu(
            'Paste All Property Values to "Raw USD Properties"', offset=ui_test.Vec2(10, 10)
        )

        # select prim
        await select_prims(["/World/Sphere"])
        await ui_test.human_delay(10)

        # disabled as randomly fails on CI...
        # right click on Raw USD Properties header
        # widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        # await widget.click(pos=widget.position+ui_test.Vec2(widget.widget.computed_content_width/2, 10), right_click=True)
        # await ui_test.human_delay(10)
        # context menu copy
        # await ui_test.select_context_menu("Reset All Property Values in \"Raw USD Properties\"", offset=ui_test.Vec2(10, 10))

    @unittest.skipUnless(omni.kit.test.gitlab.is_running_in_gitlab(), "Can fail locally")
    async def test_combobox_context_menu(self):
        await wait_stage_loading()

        # select prim
        await select_prims(["/World"])

        # right click on xformOpOrder
        frame_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        await frame_widget.find("**/StringField[*].identifier=='fallback_xformOpOrder'").click(right_click=True)
        await ui_test.human_delay(10)
        # context menu copy
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        # copy to clipboard
        omni.kit.clipboard.copy("invisible")

        # select prim
        await select_prims(["/World"])

        # right click on token_visibility
        frame_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        await frame_widget.find("**/ComboBox[*].identifier=='token_visibility'").click(right_click=True)
        await ui_test.human_delay(10)
        # context menu paste
        await ui_test.select_context_menu("Paste", offset=ui_test.Vec2(10, 10))

    @unittest.skipUnless(omni.kit.test.gitlab.is_running_in_gitlab(), "Can fail locally")
    async def test_combobox_context_menu_lock(self):
        await wait_stage_loading()

        # select prim
        await select_prims(["/World"])

        # copy to clipboard
        omni.kit.clipboard.copy("invisible")

        # select prim
        await select_prims(["/World"])

        # right click on token_visibility
        frame_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        await frame_widget.find("**/ComboBox[*].identifier=='token_visibility'").click(right_click=True)
        await ui_test.human_delay(10)
        # context menu lock
        await ui_test.select_context_menu("Locks/Lock", offset=ui_test.Vec2(10, 10))

        await frame_widget.find("**/ComboBox[*].identifier=='token_visibility'").click(right_click=True)
        await ui_test.human_delay(10)
        # context menu unlock
        await ui_test.select_context_menu("Locks/Unlock", offset=ui_test.Vec2(10, 10))
