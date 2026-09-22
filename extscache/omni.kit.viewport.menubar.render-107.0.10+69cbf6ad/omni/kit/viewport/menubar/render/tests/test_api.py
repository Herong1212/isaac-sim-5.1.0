# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TestAPI']

import functools
from unittest.mock import patch, call
from omni.kit.test import AsyncTestCase
from omni.kit.viewport.menubar.render import get_instance as _get_menubar_extension
from omni.kit.viewport.menubar.render import SingleRenderMenuItem as _SingleRenderMenuItem
from omni.kit.viewport.menubar.render import SingleRenderMenuItemBase as _SingleRenderMenuItemBase
from omni.kit.viewport.menubar.render.renderer_menu_container import RendererMenuContainer as _RendererMenuContainer


class TestAPI(AsyncTestCase):
    async def test_get_instance(self):
        extension = _get_menubar_extension()
        self.assertIsNotNone(extension)

    async def test_register_custom_menu_item_type(self):
        def _single_render_menu_item(*args, **kwargs):
            class SingleRenderMenuItem(_SingleRenderMenuItemBase):
                pass

            return SingleRenderMenuItem(*args, **kwargs)

        extension = _get_menubar_extension()
        try:
            with patch.object(_RendererMenuContainer, "set_menu_item_type") as set_menu_item_type_mock:
                fn = functools.partial(_single_render_menu_item)
                extension.register_menu_item_type(
                    fn
                )

                self.assertEqual(1, set_menu_item_type_mock.call_count)
                self.assertEqual(call(fn), set_menu_item_type_mock.call_args)
        finally:
            extension.register_menu_item_type(None)

    async def test_register_regular_menu_item_type(self):
        def _single_render_menu_item(*args, **kwargs):
            return _SingleRenderMenuItem(*args, **kwargs)

        extension = _get_menubar_extension()
        try:
            with patch.object(_RendererMenuContainer, "set_menu_item_type") as set_menu_item_type_mock:
                fn = functools.partial(_single_render_menu_item)
                extension.register_menu_item_type(
                    fn
                )

                self.assertEqual(1, set_menu_item_type_mock.call_count)
                self.assertEqual(call(fn), set_menu_item_type_mock.call_args)
        finally:
            extension.register_menu_item_type(None)
