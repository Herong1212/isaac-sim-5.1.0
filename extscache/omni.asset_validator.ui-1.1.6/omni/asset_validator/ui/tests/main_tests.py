# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import carb
import omni.kit.test
from omni.asset_validator.ui import ApplicationModel, MainWidget
from omni.ui import Window


class MainWidgetTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.model = ApplicationModel.create()

    async def test_widget(self):
        window = Window("TestWindow")
        with window.frame:
            MainWidget(self.model)

    async def test_widget_with_capabilities(self):
        carb.settings.get_settings().set("exts/omni.asset_validator.ui/capabilities/enabled", True)
        window = Window("TestWindow")
        with window.frame:
            MainWidget(self.model)
