# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import omni.kit.test
import omni.ui as ui
from omni.asset_validator.ui import CapabilitiesModel, CapabilitiesWidget
from omni.kit import ui_test


class CapabilitiesModelTest(omni.kit.test.AsyncTestCase):

    async def test_init(self):
        model = CapabilitiesModel()
        self.assertGreater(len(model), 0)

        for capability in model:
            self.assertGreater(len(capability), 0)

    async def test_reset(self):
        model = CapabilitiesModel()
        # Set some requirements as selected
        for capability in model:
            for requirement in capability:
                if requirement.enabled:
                    requirement.selected = True

        # Reset should set all to False
        model.reset()
        for capability in model:
            for requirement in capability:
                if requirement.enabled:
                    self.assertFalse(requirement.selected)


class CapabilitiesWidgetTest(omni.kit.test.AsyncTestCase):

    async def test_widget(self):
        model = CapabilitiesModel()
        window = ui.Window(__name__)
        with window.frame:
            CapabilitiesWidget(model)

            await ui_test.human_delay()
            button = ui_test.find(f"{__name__}//Frame/VStack[0]/HStack[0]/Button[0]")
            await button.click()
            for capability in model:
                for requirement in capability:
                    if requirement.enabled:
                        self.assertTrue(requirement.selected)

            button = ui_test.find(f"{__name__}//Frame/VStack[0]/HStack[0]/Button[1]")
            await button.click()
            for capability in model:
                for requirement in capability:
                    if requirement.enabled:
                        self.assertFalse(requirement.selected)
