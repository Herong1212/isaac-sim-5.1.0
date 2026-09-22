## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    build_sdf_asset_frame_dictonary,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from pxr import Sdf


class DragDropHDRIProperty(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "dome_light.usda"))
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    # After running each test
    async def tearDown(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def test_drag_drop_hdri_property(self):
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        to_select = ["/World/DomeLight"]

        # select prim
        await select_prims(to_select)

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # open all CollapsableFrames
        for frame in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            if frame.widget.title != "Raw USD Properties":
                frame.widget.scroll_here_y(0.5)
                frame.widget.collapsed = False
                await ui_test.human_delay()

        # prep content window for drag/drop
        texture_path = get_test_data_path(__name__, "textures/sunflowers.hdr")

        # NOTE: cannot keep using widget as they become stale as window refreshes due to set_value

        # do tests
        widget_table = await build_sdf_asset_frame_dictonary()
        for frame_name in widget_table.keys():
            if frame_name in ["Raw USD Properties", "Extra Properties"]:
                continue
            for field_name in widget_table[frame_name].keys():
                # NOTE: sdf_asset_ could be used more than once, if so skip
                if widget_table[frame_name][field_name] == 1:

                    def get_widget(frame, field):
                        return ui_test.find(f"Property//Frame/**/CollapsableFrame[*].title=='{frame}'").find(
                            f"**/StringField[*].identifier=='{field}'"
                        )

                    # scroll to widget
                    get_widget(frame_name, field_name).widget.scroll_here_y(0.5)
                    await ui_test.human_delay()

                    # reset for test
                    get_widget(frame_name, field_name).model.set_value("")

                    # drag/drop
                    async with ContentBrowserTestHelper() as content_browser_helper:
                        await content_browser_helper.drag_and_drop_tree_view(
                            texture_path, drag_target=get_widget(frame_name, field_name).center
                        )

                    # verify dragged item(s)
                    for prim_path in to_select:
                        prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
                        self.assertTrue(prim.IsValid())
                        attr = prim.GetAttribute(field_name[10:])
                        self.assertTrue(attr.IsValid())
                        asset_path = attr.Get()
                        self.assertTrue(asset_path is not None)
                        self.assertTrue(
                            asset_path.resolvedPath.replace("\\", "/").lower()
                            == texture_path.replace("\\", "/").lower()
                        )

                    # reset for next test
                    get_widget(frame_name, field_name).model.set_value("")
