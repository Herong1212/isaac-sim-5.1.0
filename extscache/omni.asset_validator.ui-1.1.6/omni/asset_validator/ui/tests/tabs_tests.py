# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass

import omni.kit.test
from omni.asset_validator.ui.tabs import TabBuilder, TabsWidget
from omni.kit import ui_test
from omni.ui import Window


@dataclass
class _TabBuilder(TabBuilder):
    name: str
    build_called: bool = False

    def get_name(self) -> str:
        return self.name

    def build_fn(self):
        self.build_called = True


class TabsWidgetTest(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        self.tab1 = _TabBuilder("Tab 1")
        self.tab2 = _TabBuilder("Tab 2")
        self.tab3 = _TabBuilder("Tab 3")
        self.tabs = [self.tab1, self.tab2, self.tab3]

    async def test_init(self):
        window = Window(__name__)
        with window.frame:
            widget = TabsWidget(self.tabs)
            await ui_test.human_delay()

            self.assertEqual(len(widget.tabs), 3)

    async def test_initial_tab_selection(self):
        window = Window(__name__)
        with window.frame:
            widget = TabsWidget(self.tabs)
            await ui_test.human_delay()

            self.assertTrue(widget.headers[0].selected)
            self.assertFalse(widget.headers[1].selected)
            self.assertFalse(widget.headers[2].selected)

    async def test_select_tab(self):
        window = Window(__name__)
        with window.frame:
            widget = TabsWidget(self.tabs)
            await ui_test.human_delay()

            widget.select_tab(1)
            self.assertFalse(widget.headers[0].selected)
            self.assertTrue(widget.headers[1].selected)
            self.assertFalse(widget.headers[2].selected)

    async def test_subscribe_value_changed_fn(self):
        window = Window(__name__)
        with window.frame:
            widget = TabsWidget(self.tabs)
            await ui_test.human_delay()

            value = None

            def on_value_changed(model):
                nonlocal value
                value = model.as_int

            subscription = widget.subscribe_value_changed_fn(on_value_changed)
            self.assertIsNotNone(subscription)

            widget.select_tab(1)
            self.assertEqual(value, 1)
