## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
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


class MaterialWidgetRefreshOnBinding(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_material_widget_refresh_on_binding(self):
        widget_name = "Property//Frame/**/StringField[*].identifier=='combo_drop_target'"
        to_select = "/World/Cylinder"

        # property window to front
        await ui_test.find("Property").focus()

        # select prim
        await select_prims([to_select])

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # verify property_widget is correct
        self.assertEqual(ui_test.find(widget_name).model.get_value_as_string(), "/World/Looks/OmniPBR")

        # change material binding
        omni.kit.commands.execute(
            "BindMaterialCommand", prim_path=to_select, material_path="/World/Looks/OmniGlass", strength=None
        )

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # verify widget has been refreshed
        self.assertEqual(ui_test.find(widget_name).model.get_value_as_string(), "/World/Looks/OmniGlass")

        # change material binding back
        omni.kit.undo.undo()

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # verify widget has been refreshed
        self.assertEqual(ui_test.find(widget_name).model.get_value_as_string(), "/World/Looks/OmniPBR")
