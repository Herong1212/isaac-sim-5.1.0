## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.ui.tests.test_base import OmniUiTest
from pxr import Vt


class TestBoolTypes(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64, 800)

    # After running each test
    async def tearDown(self):
        # de-select prims to prevent _delayed_dirty_handler exception
        await select_prims([])
        await wait_stage_loading()

    async def _load_and_select(self, shader_type: str):
        await ui_test.find("Property").focus()
        await open_stage(get_test_data_path(__name__, "usd/bools.usda"))

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # select prim
        await select_prims([f"/mtl_booleans/shader_{shader_type}"])
        await ui_test.human_delay(10)

    async def _array_test(self, shader_type: str, item_count: int):
        def get_widgets_and_model():
            frame_widget = ui_test.find("Property//Frame/**/.identifier=='boolean_per_channel_inputs:param'")
            self.assertIsNotNone(frame_widget)

            check_box_widgets = frame_widget.find_all("**/CheckBox[*]")
            self.assertIsNotNone(check_box_widgets)

            control_state_widget_ref = ui_test.find("Property//Frame/**/.identifier=='control_state_inputs:param'")
            self.assertIsNotNone(control_state_widget_ref)

            model = check_box_widgets[0].model
            self.assertIsNotNone(model)
            return (control_state_widget_ref, check_box_widgets, model)

        await self._load_and_select(shader_type)

        await self.wait_n_updates(3)
        (control_state_widget_ref, check_box_widgets, model) = get_widgets_and_model()

        # make sure default_value doesn't become stale when widget refreshes
        default_value = Vt.BoolArray(model.get_value())

        for i in range(item_count):
            await check_box_widgets[i].click()

        await self.wait_n_updates(3)
        (control_state_widget_ref, check_box_widgets, model) = get_widgets_and_model()

        await self.wait_n_updates(3)
        expected_value = [not v for v in default_value]

        (control_state_widget_ref, check_box_widgets, model) = get_widgets_and_model()
        self.assertEqual(model.get_value(), expected_value)

        await control_state_widget_ref.click()
        await self.wait_n_updates(3)

        # we need to retrieve model again because the widgets will have been destroyed due to the removal of the underlying attribute when the control state is reset.
        (control_state_widget_ref, check_box_widgets, model) = get_widgets_and_model()
        self.assertEqual(model.get_value(), default_value)

    async def test_bool_test(self):
        def get_widget_refs_and_model():
            # get widget and control state widget.
            param_widget_ref = ui_test.find("Property//Frame/**/.identifier=='bool_inputs:param'")
            self.assertIsNotNone(param_widget_ref)

            control_state_widget_ref = ui_test.find("Property//Frame/**/.identifier=='control_state_inputs:param'")
            self.assertIsNotNone(control_state_widget_ref)

            model = param_widget_ref.model
            self.assertIsNotNone(model)

            return (param_widget_ref, control_state_widget_ref, model)

        await self._load_and_select("bool")

        await self.wait_n_updates(3)
        (param_widget_ref, control_state_widget_ref, model) = get_widget_refs_and_model()

        default_value = model.get_value_as_bool()

        await param_widget_ref.click()
        await self.wait_n_updates(3)
        (param_widget_ref, control_state_widget_ref, model) = get_widget_refs_and_model()
        self.assertEqual(model.get_value_as_bool(), not default_value)

        await control_state_widget_ref.click()
        await self.wait_n_updates(3)

        # we need to retrieve model again because the widget will have been destroyed due to the removal of the underlying attribute when the control state is reset.
        (param_widget_ref, control_state_widget_ref, model) = get_widget_refs_and_model()
        self.assertEqual(model.get_value(), default_value)

    async def test_bool2_test(self):
        await self._array_test("bool2", 2)

    async def test_bool3_test(self):
        await self._array_test("bool3", 3)

    async def test_bool4_test(self):
        await self._array_test("bool4", 4)
