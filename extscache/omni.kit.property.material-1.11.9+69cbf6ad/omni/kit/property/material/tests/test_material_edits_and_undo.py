## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.usd
from omni.kit import ui_test
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.test_suite.helpers import arrange_windows
from pxr import Sdf, UsdShade
from usdrt import Sdf as RtSdf

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialEditsAndUndo(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows(topleft_window="Property", topleft_height=64, topleft_width=800.0)
        await self.wait_n_updates(3)

        # create material and select corresponding shader prim.
        material_prim_path = "/OmniPBR"
        omni.kit.commands.execute(
            "CreateMdlMaterialPrim", mtl_url="OmniPBR.mdl", mtl_name="OmniPBR", mtl_path=material_prim_path
        )

        shader_prim_path = f"{material_prim_path}/Shader"
        await self._select_prims([shader_prim_path])

        self._all_widget_refs = []
        self._identifiers_already_processed = []
        self._build_widget_list()
        self._identifiers_to_process = [widget_ref.widget.identifier for widget_ref in self._all_widget_refs]

    def _build_widget_list(self):
        """
        Populate the list of all widgets, filtering by:
            1. Widgets that are for UsdShade input parameters
            2. Widgets that we have already processed: self._identifiers_already_processed
        """

        self._all_widget_refs.clear()
        found = ui_test.find_all("Property//Frame/**/.identifier!=''")
        self.assertNotEqual(found, [])

        for widget_ref in found:
            if not hasattr(widget_ref.widget, "model"):
                continue

            identifier = widget_ref.widget.identifier
            if identifier.startswith("colorspace"):
                continue

            if (UsdShade.Tokens.inputs in identifier) and (identifier not in self._identifiers_already_processed):
                self._all_widget_refs.append(widget_ref)

    def _find_by_identifier(self, identifier: str) -> ui_test.WidgetRef:
        """
        Repopulate list of all widgets.
        This needs to be done because of the enable_if logic in the widget code.
        Changing a widgets value may result in other widgets to be shown/hidden.
        So anytime we change a value on a widget we need to regenerate the 'self._all_widget_refs' list.
        """

        self._build_widget_list()

        res = None
        for widget_ref in self._all_widget_refs:
            if widget_ref.widget.identifier == identifier:
                res = widget_ref
                break

        self.assertIsNotNone(res)
        return res

    async def test_material_edits_and_undo(self):
        # There are two parts to a test:
        #     1. Set widget to 'new_value' and verify the underlying attribute and the widget model have both been updated.
        #     2. Undo, verify the underlying attribute and the widget have both been updated to contain 'old_value'

        while self._all_widget_refs:
            widget_ref = self._all_widget_refs.pop()
            widget = widget_ref.widget
            identifier = widget.identifier

            # we don't are about this widget so skip
            if identifier not in self._identifiers_to_process:
                continue

            self._identifiers_to_process.remove(identifier)

            def get_new_model(identifier: str) -> UsdAttributeModel:
                # we need to get the widget and model again because
                # changing the value on a model/attribute may have caused the enable_if logic
                # to redraw the widget.
                widget_ref = self._find_by_identifier(identifier)
                widget = widget_ref.widget
                self.assertIsNotNone(widget)
                model = widget.model
                self.assertIsNotNone(model)
                return model

            identifier = widget.identifier
            model = widget.model
            self.assertIsNotNone(model)

            # get old value
            old_value = model.get_value()
            self.assertIsNotNone(old_value)

            # create the new value
            new_value = None
            if isinstance(old_value, bool):
                new_value = not old_value

            elif isinstance(old_value, (Sdf.AssetPath, RtSdf.AssetPath)):
                new_value = "testpath/abc.png"

            elif isinstance(old_value, float):
                new_value = 0.1234

            else:
                new_value = old_value + 1

            self.assertIsNotNone(new_value)

            # Step 1: Set new value and verify
            model.set_value(new_value)
            await self.wait_n_updates(3)

            comparison_func = self.assertEqual
            if isinstance(old_value, float):
                comparison_func = lambda a, b: self.assertAlmostEqual(a, b, places=4)

            # get model as widgets may have been redrawn
            model = get_new_model(identifier)
            attribute = self._get_attribute_from_model(model)

            attribute_value = attribute.Get()
            comparison_func(attribute_value, new_value)

            model_value = model.get_value()
            comparison_func(model_value, new_value)

            # Step 2: Undo and verify
            omni.kit.undo.undo()
            await self.wait_n_updates(3)

            # get model as widgets may have been redrawn
            model = get_new_model(identifier)

            attribute_value = attribute.Get()
            # check against None because at some point we will want to completely remove the attribute from the
            # stage if it's value has been set to its default.
            self.assertTrue(attribute_value in [old_value, None])

            model_value = model.get_value()
            if isinstance(model_value, RtSdf.AssetPath):  # pragma: no cover
                model_value = model_value.path

            comparison_func(model_value, old_value)

            self._identifiers_already_processed.append(identifier)
