# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.ui as ui

from enum import IntFlag
import asyncio


class SearchModel(ui.AbstractValueModel):
    def __init__(self, modified_fn):
        super().__init__()
        self._modified_fn = modified_fn
        self.__str = ""

    def is_in_string(self, string: str):
        if self.__str == "":
            return True
        return (self.__str.upper() in string.upper())

    def set_value(self, value):
        self.__str = str(value)
        self._value_changed()
        if self._modified_fn:
            self._modified_fn(self.__str)

    def get_value_as_string(self):
        return self.__str


class SearchWidget():
    class WidgetFlags(IntFlag):
        SHOW_OPEN_BUTTON = 0x01
        SHOW_GOTO_BUTTON = 0x02
        SHOW_ALL = SHOW_OPEN_BUTTON | SHOW_GOTO_BUTTON

    def __init__(self, theme: str, icon_path: str, modified_fn: callable = None):
        self._search_model = SearchModel(modified_fn=modified_fn)

        if theme == "NvidiaDark":
            SEARCH_BODY_COLOR = 0xFF2D2D2D
            BUTTON_BACKGROUND_COLOR = 0xFF323434
        else:
            SEARCH_BODY_COLOR = 0xFF2D2D2D
            BUTTON_BACKGROUND_COLOR = 0xFF545454

        self._style = {
            # search_button
            "Button.Image::search_button": {
                "image_url": f"{icon_path}/search.svg",
                "background_color": SEARCH_BODY_COLOR,
                "margin": 0,
            },
            "Button::search_button": {
                "margin": 0,
            },
            "Field::search_button": {
                "background_color": SEARCH_BODY_COLOR
            },
            "Field::search_button:hovered": {
                "background_color": SEARCH_BODY_COLOR
            },
            # search placeholder
            "Label::search_placeholder": {
                "color": 0xFF666666,
            },
            # remove button
            "Button.Image::remove": {"image_url": f"{icon_path}/remove.svg"},
            "Button.Image::remove:hovered": {"image_url": f"{icon_path}/remove-hovered.svg"},
            "Button::remove": {
                "background_color": SEARCH_BODY_COLOR,
                "margin": 0,
            },
            "Button::remove:hovered": {
                "background_color": SEARCH_BODY_COLOR,
            },
            # remove button popup (different colors)
            "Button::remove_popup": {
                "background_color": 0x00000000
            },
            "Button::remove_popup:hovered": {
                "background_color": 0x00000000
            },
            "Button.Image::remove_popup": {
                "image_url": f"{icon_path}/remove.svg"
            },
            "Button.Image::remove_popup:hovered": {
                "image_url": f"{icon_path}/remove-hovered.svg"
            },
            # find button
            "Button::find": {
                "background_color": BUTTON_BACKGROUND_COLOR
            },
            "Button.Image::find": {
                "image_url": f"{icon_path}/find.svg"
            },

            # listbox button
            "Button.Image::listbox": {
                "image_url": f"{icon_path}/listbox.svg"
            },
            "Button::listbox": {
                "background_color": 0xFF000000, "padding": 6
            },
        }

    def clear(self):
        self._field = None

    def update(self, string):
        self._placeholder.visible = bool(string == "")
        self._search_clear.enabled = not self._placeholder.visible

    def focus(self):
        async def focus(field):
            await omni.kit.app.get_app().next_update_async()
            field.focus_keyboard()

        asyncio.ensure_future(focus(self._field))

    def build_ui(self, width, search_size):
        def clear_name(field):
            field.model.set_value("")
            field.focus_keyboard()

        with ui.HStack(width=0, height=0, style=self._style):
            with ui.ZStack(width=0, height=0):
                with ui.HStack(width=0, height=0):
                    # searchable string field
                    field = ui.StringField(
                        model=self._search_model,
                        width=width - 46,
                        height=search_size, name="search_button"
                    )
                    # remove button
                    self._search_clear = ui.Button(
                        "",
                        width=search_size,
                        height=search_size,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        enabled=False,
                        clicked_fn=lambda f=field: clear_name(f), name="remove"
                    )
                self._placeholder = ui.Label("  Search....", height=search_size, name="search_placeholder")
                self._field = field
                self.focus()

    def set_placeholder_text(self, msg: str):
        self._placeholder.text = f"  {msg}...."
        enabled = bool(msg == "Search")
        self._field.enabled = enabled
        self._field.focus_keyboard(enabled)

    def set_text(self, new_text: str):
        self._field.model.set_value(new_text)

    def get_text(self):
        return self._field.model.get_value_as_string()

    def build_ui_popup(
        self,
        search_size: float,
        popup_text: str,
        index: int,
        update_fn: callable,
        widget_flags=WidgetFlags.SHOW_ALL
    ):
        def clear_name(name_field):
            name_field.model.set_value("None")
            if update_fn:
                update_fn(name_field.model, None)

        goto_button = None
        open_button = None
        name_field = None

        with ui.HStack(style=self._style):
            name_field = ui.StringField(height=search_size, enabled=False)
            name_field.model.set_value(popup_text)
            ui.Button(
                "",
                width=20,
                height=20,
                image_width=12,
                image_height=12,
                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                clicked_fn=lambda f=name_field: clear_name(f),
                name="remove_popup",
            )
            if widget_flags & SearchWidget.WidgetFlags.SHOW_OPEN_BUTTON:
                open_button = ui.Button(
                    "",
                    width=20,
                    height=20,
                    image_width=8,
                    image_height=8,
                    name="listbox",
                )
            if (widget_flags & SearchWidget.WidgetFlags.SHOW_GOTO_BUTTON) and index > 0:
                ui.Spacer(width=4)
                goto_button = ui.Button(
                    "",
                    width=20,
                    height=20,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    name="find",
                )
            self._field = name_field
            # we never need this in our code, but removing
            # the button breaks the interface horribly
            open_button.visible = False
        return name_field, open_button, goto_button
