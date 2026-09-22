## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from omni.ui.tests.test_base import OmniUiTest
import omni.kit
import omni.ui as ui
import omni.kit.ui_test as ui_test


class TestQuickLayoutMenus(OmniUiTest):
    async def test_menus(self):
        menu_widget = ui_test.get_menubar()
        await menu_widget.find_menu("Window").click()
        await menu_widget.find_menu("Layout").click()
        await menu_widget.find_menu("Quick Save").click()
        await ui_test.human_delay(10)

        await menu_widget.find_menu("Window").click()
        await menu_widget.find_menu("Layout").click()
        await menu_widget.find_menu("Quick Load").click()
        await ui_test.human_delay(10)
