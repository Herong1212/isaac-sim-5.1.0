# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import omni.kit.test
import omni.ui as ui
from omni.asset_validator.ui import FeaturesModel, FeaturesWidget
from omni.kit import ui_test


class FeaturesModelTest(omni.kit.test.AsyncTestCase):

    async def test_init(self):
        model = FeaturesModel()
        self.assertGreater(len(model), 0)

        for feature in model:
            self.assertGreater(len(feature), 0)

    async def test_reset(self):
        model = FeaturesModel()
        # Set some requirements as selected
        for feature in model:
            for requirement in feature:
                if requirement.enabled:
                    requirement.selected = True

        # Reset should set all to False
        model.reset()
        for feature in model:
            for requirement in feature:
                if requirement.enabled:
                    self.assertFalse(requirement.selected)


class FeaturesWidgetTest(omni.kit.test.AsyncTestCase):

    async def test_widget(self):
        model = FeaturesModel()
        window = ui.Window("TestWindow")
        with window.frame:
            FeaturesWidget(model)

        await ui_test.human_delay()
        button = ui_test.find("TestWindow//Frame/VStack[0]/HStack[0]/Button[0]")
        await button.click()
        for feature in model:
            for requirement in feature:
                if requirement.enabled:
                    self.assertTrue(requirement.selected)

        button = ui_test.find("TestWindow//Frame/VStack[0]/HStack[0]/Button[1]")
        await button.click()
        for feature in model:
            for requirement in feature:
                if requirement.enabled:
                    self.assertFalse(requirement.selected)
