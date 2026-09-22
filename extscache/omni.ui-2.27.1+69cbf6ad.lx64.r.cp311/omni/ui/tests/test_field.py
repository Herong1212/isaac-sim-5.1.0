## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.ui as ui
import omni.kit.app
from .test_base import OmniUiTest


STYLE = {
    "Field": {
        "background_color": 0xFF000000,
        "color": 0xFFFFFFFF,
        "border_color": 0xFFFFFFFF,
        "background_selected_color": 0xFFFF6600,
        "border_width": 1,
        "border_radius": 0,
    }
}


class TestField(OmniUiTest):
    """Testing fields"""

    async def test_general(self):
        """Testing general properties of ui.StringField"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(height=0, style=STYLE, spacing=2):
                # Simple field
                ui.StringField()
                ui.StringField().model.set_value("Hello World")

        await self.finalize_test()

    async def test_focus(self):
        """Testing the ability to focus in ui.StringField"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(height=0, style=STYLE, spacing=2):
                # Simple field
                ui.StringField()
                field = ui.StringField()

        field.model.set_value("Hello World")
        field.focus_keyboard()

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_defocus(self):
        """Testing the ability to defocus in ui.StringField"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(height=0, style=STYLE, spacing=2):
                # Simple field
                ui.StringField()
                field = ui.StringField()

        field.model.set_value("Hello World")
        field.focus_keyboard()

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        field.focus_keyboard(False)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_change_when_editing(self):
        """Testing the ability to defocus in ui.StringField"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(height=0, style=STYLE, spacing=2):
                # Simple field
                ui.StringField()
                field = ui.StringField()

        field.model.set_value("Hello World")
        field.focus_keyboard()

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        field.model.set_value("Data Change")

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_multifield_resize(self):
        """Testing general properties of ui.StringField"""
        window = await self.create_test_window(256, 64)

        with window.frame:
            stack = ui.VStack(height=0, width=100, style=STYLE, spacing=2)
            with stack:
                # Simple field
                ui.MultiFloatField(1.0, 1.0, 1.0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        stack.width = ui.Fraction(1)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()
