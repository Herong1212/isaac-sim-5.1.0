## Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_prims,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)


class TestLargeSelection(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd_variants/ThreeDollyVariantStage.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_large_selection(self):
        import omni.kit.commands

        await ui_test.find("Property").focus()

        # get stage
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # select all the prims
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        await select_prims(prim_list)
        await ui_test.human_delay(10)

        # click on show all
        await ui_test.find("Property//Frame/**/Button[*].identifier=='large_payload_show_all'").click()
        await ui_test.human_delay(10)

        # verify
        widgets = ui_test.find_all("Property//Frame/**/CollapsableFrame[*]")
        frame_names = [w.widget.title for w in widgets]
        self.assertEqual(frame_names, ["Raw USD Properties"])
