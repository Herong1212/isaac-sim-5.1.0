# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# pylint: disable=missing-function-docstring, missing-class-docstring
import copy

import omni.usd
from omni.kit import ui_test
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, create_primspec_token
from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path, open_stage, select_prims
from omni.ui.tests.test_base import OmniUiTest
from pxr import UsdGeom, Vt


class ExampleAttributeWidget(UsdPropertiesWidget):
    def __init__(self):
        super().__init__(title="Example Properties", collapsed=False)

        # add 10 length array but only give 7 items, this results in 3 duplicates being added.
        cpt_tokens = Vt.TokenArray(
            10,
            (
                "pinhole",
                "pinholeOpenCV",
                "fisheyePolynomial",
                "fisheyeSpherical",
                "fisheyeKannalaBrandtK3",
                "fisheyeOpenCV",
                "fisheyeRadTanThinPrism",
                "omniDirectionalStereo",
                "generalizedProjection",
            ),
        )
        self.add_custom_schema_attribute(
            "cameraProjectionType",
            lambda p: p.IsA(UsdGeom.Mesh),
            None,
            "Projection Type",
            create_primspec_token(cpt_tokens, "pinhole"),
        )

    def on_new_payload(self, payload):
        if not payload or len(payload) == 0:
            return False

        if not super().on_new_payload(payload):
            return False

        used = []
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            if not prim or not (prim.IsA(UsdGeom.Xform) or prim.IsA(UsdGeom.Mesh)):
                return False
            if self.is_custom_schema_attribute_used(prim):
                used.append(None)
            used.append(prim)

        return used is not None

    def _customize_props_layout(self, props):
        from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutProperty

        self.add_custom_schema_attributes_to_props(props)

        # remove any unwanted props (all of the Xform & Mesh
        # attributes as we don't want to display them in the widget)
        for attr in copy.copy(props):
            if attr.attr_name not in ["cameraProjectionType"]:
                props.remove(attr)

        # custom UI attributes
        frame = CustomLayoutFrame(hide_extra=False)
        with frame:
            # Set layout order. this rearranges attributes in widget to the following order.
            CustomLayoutProperty("cameraProjectionType", "Camera Projection Type")

        return frame.apply(props)


class TestCustomValues(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", topleft_height=256, topleft_width=800.0)

        self._registered = False
        self._menu_items = []

        self._register_widget()

        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths([], False)
        await ui_test.human_delay()
        if self._registered:
            self._unregister_widget()

        await super().tearDown()

    def _register_widget(self):
        import omni.kit.window.property as property_window_ext

        property_window = property_window_ext.get_window()
        if property_window:
            property_window.register_widget("prim", "example_properties", ExampleAttributeWidget())
            self._registered = True

    def _unregister_widget(self):
        import omni.kit.window.property as property_window_ext

        property_window = property_window_ext.get_window()
        if property_window:
            property_window.unregister_widget("prim", "example_properties")
            self._registered = False

    async def test_custom_attribute_duplicate(self):
        await select_prims(["/World/Cone"])

        # test combo box, duplicate items should be tagged and unselectable.

        frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Example Properties'")
        combobox = frame.find("**/ComboBox[*].identifier=='token_cameraProjectionType'")
        items = [item.token for item in combobox.model.get_item_children(None)]

        # verify items
        self.assertEqual(
            items,
            [
                "pinhole",
                "pinholeOpenCV",
                "fisheyePolynomial",
                "fisheyeSpherical",
                "fisheyeKannalaBrandtK3",
                "fisheyeOpenCV",
                "fisheyeRadTanThinPrism",
                "omniDirectionalStereo",
                "generalizedProjection",
                "** DUPLICATE ** pinhole ** DUPLICATE **",
            ],
        )

        got_items = []
        for item in items:
            combobox.model.set_value(item)
            await ui_test.human_delay(10)
            got_items.append(combobox.model.get_value())

        # verify get_value items
        self.assertEqual(
            got_items,
            [
                "pinhole",
                "pinholeOpenCV",
                "fisheyePolynomial",
                "fisheyeSpherical",
                "fisheyeKannalaBrandtK3",
                "fisheyeOpenCV",
                "fisheyeRadTanThinPrism",
                "omniDirectionalStereo",
                "generalizedProjection",
                "generalizedProjection",
            ],
        )
