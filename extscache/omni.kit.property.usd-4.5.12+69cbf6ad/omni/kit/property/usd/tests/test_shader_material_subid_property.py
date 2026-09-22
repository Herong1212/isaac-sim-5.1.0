## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
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
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from pxr import UsdShade


class ShaderMaterialSubidProperty(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_shader_material_subid_property(self):
        import omni.kit.commands

        await ui_test.find("Property").focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        to_select = ["/World/Cone", "/World/Cylinder", "/World/Cube", "/World/Sphere"]

        # bind OmniSurface_Plastic to prims
        omni.kit.commands.execute("BindMaterial", material_path="/World/Looks/OmniSurface_Plastic", prim_path=to_select)

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # select OmniSurface_Plastic shader
        await select_prims(["/World/Looks/OmniSurface_Plastic/Shader"])
        await ui_test.human_delay(50)

        # get OmniSurface_Plastic shader
        prim = stage.GetPrimAtPath("/World/Looks/OmniSurface_Plastic/Shader")
        shader = UsdShade.Shader(prim)

        # get subid widget
        property_widget = ui_test.find(
            "Property//Frame/**/ComboBox[*].identifier=='token_info:mdl:sourceAsset:subIdentifier'"
        )

        self.assertIsNotNone(property_widget)

        if property_widget.widget.enabled:
            model = property_widget.model
            items = model.get_item_children(None)

            # when the models value changes the entire frame/widget is rebuilt, which means
            # that we need to gather the widget and the model during each iteration of the following loop
            for item in items:
                property_widget = ui_test.find(
                    "Property//Frame/**/ComboBox[*].identifier=='token_info:mdl:sourceAsset:subIdentifier'"
                )
                self.assertIsNotNone(property_widget)

                model = property_widget.model
                self.assertIsNotNone(model)

                # change selection
                model.set_value(item.token)

                # wait for material to load & UI to refresh
                await wait_stage_loading()

                # verify shader value
                self.assertTrue(shader.GetSourceAssetSubIdentifier("mdl") == item.token)
