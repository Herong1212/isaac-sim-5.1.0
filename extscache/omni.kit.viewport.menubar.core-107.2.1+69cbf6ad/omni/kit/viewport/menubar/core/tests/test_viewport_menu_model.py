# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TestViewportMenuModel']


from omni.kit.test import AsyncTestCase

from omni.kit.viewport.menubar.core import ViewportMenuSpacer, ViewportMenubar

from ..viewport_menu_model import ViewportMenuModel

from .left_example_menu_container import LeftExampleMenuContainer
from .right_example_menu_container import RightExampleMenuContainer
from .example_button import ButtonExample


class ViewportBottomBar(ViewportMenubar):
    def __init__(self):
        super().__init__("BOTTOM_BAR")

    def build_fn(self, menu_items, factory):
        pass


class TestViewportMenuModel(AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    def get_setting_path(self, setting):
        return f'/app/test/omni.kit.viewport.menubar.core/test_root/{setting}'

    async def test_model(self):
        model = ViewportMenuModel()
        self.assertEqual(model.get_item_value_model_count(None), 1)

        bottom_bar = ViewportBottomBar()

        left_menu = LeftExampleMenuContainer()
        right_menu = RightExampleMenuContainer()
        button_menu = ButtonExample()

        menubar_items = model.get_item_children(None)
        # One default menubar + bottom bar
        self.assertEqual(len(menubar_items), 2)
        self.assertEqual(menubar_items[1].name, bottom_bar.name)

        default_bar_item = menubar_items[0]
        bottom_bar_item = menubar_items[1]

        items = model.get_item_children(menubar_items[0])
        # Actually there are 4 items (left+button+spacer+right) in default bat
        self.assertEqual(len(items), 4)
        self.assertEqual(items[0].name, left_menu.name)
        self.assertEqual(items[1].name, button_menu.name)
        self.assertTrue(isinstance(items[2], ViewportMenuSpacer))
        self.assertEqual(items[3].name, right_menu.name)

        self.assertEqual(model.get_drag_mime_data(bottom_bar_item), bottom_bar.name)

        drop_accepted = model.drop_accepted(bottom_bar_item, default_bar_item)
        self.assertTrue(drop_accepted)

        drop_accepted = model.drop_accepted(None, default_bar_item)
        self.assertFalse(drop_accepted)

        # Drop default to behind bottom bar
        model.drop(bottom_bar_item, default_bar_item)
        menubar_items = model.get_item_children(None)
        self.assertEqual(menubar_items[0], bottom_bar_item)
        self.assertEqual(menubar_items[1], default_bar_item)

        # Drop default to in front of bottom bar
        model.drop(bottom_bar_item, default_bar_item)
        menubar_items = model.get_item_children(None)
        self.assertEqual(menubar_items[0], default_bar_item)
        self.assertEqual(menubar_items[1], bottom_bar_item)
