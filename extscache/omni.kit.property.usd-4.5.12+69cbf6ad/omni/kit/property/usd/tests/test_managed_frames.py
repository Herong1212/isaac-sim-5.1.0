## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.undo
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


class ManagedFrames(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def test_managed_frames(self):
        to_select = "/World/Cylinder"

        # property window to front
        await ui_test.find("Property").focus()

        # reset managed frame state
        omni.kit.window.property.managed_frame.reset_collapsed_state()

        # select prim
        await select_prims([to_select])

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # toggle Collapsible Frames to close
        await ui_test.human_delay(10)

        # verify default state
        default_states = {"Materials on selected models": False, "Raw USD Properties": True}
        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            if w.widget.title in default_states:
                self.assertEqual(w.widget.collapsed, default_states[w.widget.title])

        # collapse all
        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            w.widget.collapsed = True
        await ui_test.human_delay(10)

        # select prim
        await select_prims([])
        await ui_test.human_delay(10)
        await select_prims([to_select])
        await ui_test.human_delay(10)

        # verify collapsed
        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            self.assertTrue(w.widget.collapsed)

        # expand all
        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            w.widget.collapsed = False
        await ui_test.human_delay(10)

        # select prim
        await select_prims([])
        await ui_test.human_delay(10)
        await select_prims([to_select])
        await ui_test.human_delay(10)

        # verify exapnded
        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            self.assertFalse(w.widget.collapsed)
