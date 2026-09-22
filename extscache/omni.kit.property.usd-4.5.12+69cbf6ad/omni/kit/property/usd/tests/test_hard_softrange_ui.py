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
from pxr import Sdf


class HardSoftRangeUI(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64, 800)

    # After running each test
    async def tearDown(self):
        # de-select prims to prevent _delayed_dirty_handler exception
        await select_prims([])
        await wait_stage_loading()

    def _verify_hard_and_soft_range(self, drag_widgets, expected_hard_range, expected_soft_range):
        def verify_range(index, custom_data, key, expected):
            range_to_check = custom_data.get(key, None)
            self.assertIsNotNone(range_to_check)

            range_min = range_to_check.get("min", None)
            self.assertIsNotNone(range_min)
            range_min = list(range_min) if isinstance(range_min, tuple) else [range_min]
            self.assertAlmostEqual(range_min[index], expected[0])

            range_max = range_to_check.get("max", None)
            self.assertIsNotNone(range_max)
            range_max = list(range_max) if isinstance(range_max, tuple) else [range_max]
            self.assertAlmostEqual(range_max[index], expected[1])

        for index, widget_ref in enumerate(drag_widgets):
            model = widget_ref.model
            self.assertIsNotNone(model)

            custom_data = model.metadata.get(Sdf.AttributeSpec.CustomDataKey)
            self.assertIsNotNone(custom_data)

            verify_range(index, custom_data, "range", expected_hard_range)
            verify_range(index, custom_data, "soft_range", expected_soft_range)

    def _verify_values(self, type_size, expected):  # pragma: no cover
        for i in range(type_size):
            (drag_widgets, _) = self.__get_widgets()
            model = drag_widgets[i].model
            self.assertIsNotNone(model)
            self.assertAlmostEqual(model.get_value_as_float(), expected[i])

    async def _click_type(self, type_size, new_value):
        for i in range(type_size):
            (drag_widgets, _) = self.__get_widgets()
            await drag_widgets[i].input(str(new_value[i]))
            await self.wait_n_updates()

    def __get_widgets(self):
        frame = None
        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            if widget_ref.widget.title == "Inputs":
                frame = widget_ref
                break

        self.assertIsNotNone(frame)

        drag_widgets = frame.find_all("**/FloatDrag[*]")
        self.assertIsNotNone(drag_widgets)

        reset_widgets = frame.find_all("**/ImageWithProvider[*]")
        self.assertIsNotNone(reset_widgets)
        return (drag_widgets, reset_widgets)

    async def _test_range(self, input_type: str, type_size: int):
        await open_stage(get_test_data_path(__name__, "usd/soft_hard_range.usda"))
        await ui_test.find("Property").focus()

        # select prim
        await select_prims([f"/mtl_soft_hard_range/shader_{input_type}"])

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        (drag_widgets, reset_widgets) = self.__get_widgets()

        default_value = [0.5] * type_size
        expected_hard_range = [0.0, 2.0]
        expected_soft_range = [0.0, 1.0]

        self._verify_hard_and_soft_range(drag_widgets, expected_hard_range, expected_soft_range)

        # check default values
        self._verify_values(type_size, default_value)

        # test min clamping
        offset_low_value = [i - 13.7 for i in default_value]
        await self._click_type(type_size, offset_low_value)
        ## widgets are stale
        clamped_low = [expected_hard_range[0] for i in default_value]
        self._verify_values(type_size, clamped_low)

        # test max clamping
        offset_high_value = [i + 13.7 for i in default_value]
        await self._click_type(type_size, offset_high_value)
        ## widgets are stale
        clamped_high = [expected_hard_range[1] for i in default_value]
        self._verify_values(type_size, clamped_high)

        # click reset
        for i in range(type_size):
            (drag_widgets, reset_widgets) = self.__get_widgets()
            await reset_widgets[i].click()
        await self.wait_n_updates(3)

        # check default values
        self._verify_values(type_size, default_value)

    async def test_hard_softrange_float_ui(self):
        await self._test_range("float", 1)

    async def test_hard_softrange_float2_ui(self):
        await self._test_range("float2", 2)

    async def test_hard_softrange_float3_ui(self):
        await self._test_range("float3", 3)

    async def test_hard_softrange_float4_ui(self):
        await self._test_range("float4", 4)
