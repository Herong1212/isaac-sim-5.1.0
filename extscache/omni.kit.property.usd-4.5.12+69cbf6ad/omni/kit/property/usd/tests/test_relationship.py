## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
from pathlib import Path

import omni.kit.app
import omni.kit.test
import omni.kit.window.property.managed_frame
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_for_window,
    wait_stage_loading,
)
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf

from ..usd_property_widget_builder import UsdPropertiesWidgetBuilder


class PrimRelationship(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 224)
        await open_stage(get_test_data_path(__name__, "usd/relationship.usda"))
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)

    # After running each test
    async def tearDown(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await wait_stage_loading()

    async def handle_select_targets(self, prim_name):
        # handle assign dialog
        window_name = "Select Targets"
        await wait_for_window(window_name)

        # select prim
        stage_widget = ui_test.find(f"{window_name}//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{prim_name}'").click()
        await ui_test.human_delay()

        # click add
        await ui_test.find(f"{window_name}//Frame/**/Button[*].identifier=='select_button'").click()
        await ui_test.human_delay(50)

    async def test_relationship(self):
        def get_buttons():
            buttons = {}
            frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
            self.assertFalse(frame.widget.collapsed)
            for widget in frame.find_all("**/Button[*]"):
                buttons[widget.widget.identifier] = widget
            return buttons

        def remove_add_buttons():
            buttons = get_buttons()
            for w in buttons.copy():
                if (
                    w.endswith("add_relationships")
                    or w.startswith("sdf_browse_relationship")
                    or w.endswith("_proxyPrim")
                ):
                    del buttons[w]
            return buttons

        await ui_test.find("Property").focus()

        # select relationship prim
        await select_prims(["/World/Sphere_02"])

        # Raw USD Properties as relationship attribute is not part of any schema
        widgets = get_buttons()
        await widgets["sdf_relationship_Attr2[0].remove"].click()
        await ui_test.human_delay(50)

        # verify only "add_relationship"
        widgets = remove_add_buttons()
        self.assertEqual(list(widgets.keys()), ["sdf_relationship_Attr2[0].remove"])

        # "add_relationship"
        await get_buttons()["sdf_relationship_array_Attr2.add_relationships"].click()
        await self.handle_select_targets("/World/Sphere_01")

        # "add_relationship"
        await get_buttons()["sdf_relationship_array_Attr2.add_relationships"].click()
        await self.handle_select_targets("/World/Cube_01")

        # "add_relationship"
        await get_buttons()["sdf_relationship_array_Attr2.add_relationships"].click()
        await self.handle_select_targets("/World/Cube_02")

        # verify
        widgets = remove_add_buttons()
        self.assertEqual(
            list(widgets.keys()),
            [
                "sdf_relationship_Attr2[0].remove",
                "sdf_relationship_Attr2[1].remove",
                "sdf_relationship_Attr2[2].remove",
            ],
        )


class PrimRelationshipUI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = get_test_data_path(__name__, "golden_img")
        await open_stage(get_test_data_path(__name__, "usd/relationship.usda"))

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_relationship_limit(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        window = ui.Window("Relationship")

        await self.docked_test_window(
            window=window,
            width=450,
            height=700,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        await omni.kit.app.get_app().next_update_async()

        additional_widget_kwargs = {"targets_limit": 1}

        prim_rel_widget = None

        with window.frame:
            prim_rel_widget = UsdPropertiesWidgetBuilder.relationship_builder(
                stage,
                "test",
                {},
                [Sdf.Path("/World/Sphere_01")],
                additional_widget_kwargs=additional_widget_kwargs,
            )

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        add_button = ui_test.find(
            "Relationship//Frame/**/Button[*].identifier=='sdf_relationship_array_test.add_relationships'"
        )
        self.assertEqual(add_button.widget.enabled, False)

        await self.finalize_test(
            golden_img_dir=Path(self._golden_img_dir), golden_img_name="test_relationship_limit_ui.png", zero_mouse=True
        )

        if prim_rel_widget:
            del prim_rel_widget
