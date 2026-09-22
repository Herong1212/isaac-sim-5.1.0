## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
import omni.kit.app
import omni.kit.test
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


class PropertyPathAddMenu(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_property_path_add(self, retry_count=0):
        try:
            await ui_test.find("Content").focus()

            stage_window = ui_test.find("Stage")
            await stage_window.focus()

            usd_context = omni.usd.get_context()
            stage = usd_context.get_stage()
            await wait_stage_loading()

            # select cone
            await select_prims(["/World/Cone"])
            await ui_test.human_delay()

            # click "Add"
            add_widget = [w for w in ui_test.find_all("Property//Frame/**/Button[*]") if w.widget.text.endswith("Add")][
                0
            ]
            await add_widget.click()
            # select Attribute from menu
            await ui_test.select_context_menu("Attribute", offset=ui_test.Vec2(10, 10))

            # use "Add Attribute..." window
            await wait_for_window("Add Attribute...")

            # select settings in window
            for w in ui_test.find_all("Add Attribute...//Frame/**"):
                if isinstance(w.widget, omni.ui.StringField):
                    await w.input("MyTestAttribute")
                elif isinstance(w.widget, omni.ui.ComboBox):
                    items = w.widget.model.get_item_children(None)
                    if len(items) == 2:
                        w.widget.model.get_item_value_model(None, 0).set_value(1)
                    else:
                        bool_index = [
                            index
                            for index, i in enumerate(w.widget.model.get_item_children(None))
                            if i.value_type_name == "bool"
                            if i.value_type_name == "bool"
                        ][0]
                        w.widget.model.get_item_value_model(None, 0).set_value(bool_index)

            # click "Add"
            await ui_test.find("Add Attribute...//Frame/**/Button[*].text=='Add'").click()
            await ui_test.human_delay(10)

            # verify attribute correct type
            attr = stage.GetPrimAtPath("/World/Cone").GetAttribute("MyTestAttribute")
            self.assertEqual(attr.GetTypeName().cppTypeName, "bool")
        except Exception as ex:
            if retry_count < 5:
                await ui_test.human_delay(50)
                print("retrying test_property_path_add...")
                return await self.test_property_path_add(retry_count + 1)
            raise ex
