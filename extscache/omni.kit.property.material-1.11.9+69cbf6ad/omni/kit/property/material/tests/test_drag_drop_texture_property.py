## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, build_sdf_asset_frame_dictonary
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from pxr import UsdShade

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class DragDropTextureProperty(MaterialPropertiesTestBase):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 64)

        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        scene_file_path = self._get_scene_path("bound_material.usda")
        await self._load_scene(scene_file_path)

    async def test_l1_drag_drop_texture_property(self):
        await self._select_prims(["/World/Looks/OmniHair/Shader"])

        texture_path = self._get_texture_path("granite_a_mask.png")

        # open all CollapsableFrames
        for frame in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            if frame.widget.title != "Raw USD Properties":
                frame.widget.scroll_here_y(0.5)
                frame.widget.collapsed = False
                await ui_test.human_delay()

        content_browser_helper = ContentBrowserTestHelper()

        processed_widgets = set()

        widget_table = await build_sdf_asset_frame_dictonary()
        for frame_name in widget_table.keys():
            for field_name in widget_table[frame_name].keys():
                if UsdShade.Tokens.inputs not in field_name:
                    continue

                # NOTE: sdf_asset_ could be used more than once, if so skip
                if widget_table[frame_name][field_name] == 1:
                    widget_ref = ui_test.find(f"Property//Frame/**/CollapsableFrame[*].title=='{frame_name}'").find(
                        f"**/StringField[*].identifier=='{field_name}'"
                    )
                    if widget_ref.realpath in processed_widgets:
                        continue

                    processed_widgets.add(widget_ref.realpath)

                    self.assertIsNotNone(widget_ref)

                    widget = widget_ref.widget
                    self.assertIsNotNone(widget)

                    model = widget.model
                    self.assertIsNotNone(model)

                    # scroll to widget
                    widget.scroll_here_y(0.5)
                    await ui_test.human_delay()

                    # reset for test
                    model.set_value("")

                    # drag/drop
                    await content_browser_helper.drag_and_drop_tree_view(texture_path, drag_target=widget_ref.center)
                    attribute = self._get_attribute_from_model(model)
                    asset_path = attribute.Get()

                    self.assertTrue(asset_path is not None)
                    self.assertTrue(
                        asset_path.resolvedPath.replace("\\", "/").lower() == texture_path.replace("\\", "/").lower()
                    )
