"""Simulated searchable combobox class, used by MaterialListBoxWidget."""
__all__ = ['SearchModel', 'SearchWidget']

import asyncio
import omni.kit.app
import omni.ui as ui
from enum import IntFlag
from .treeview_model import Constant

class SearchModel(ui.AbstractValueModel):
    """Simulated searchable combobox model class, used by SearchWidget."""
    def __init__(self, modified_fn):
        """Initialize class function.

        Args:
            modified_fn (callable): function called when value changed.
        """
        super().__init__()
        self._modified_fn = modified_fn
        self.__str = ""

    def is_in_string(self, string :str):
        """Is `string` in SearchModel string, case insensitive.

        Args:
            string (str): string to compare against.

        Returns:
            (bool): True if Is `string` in SearchModel string else False.
        """
        if self.__str == "":
            return True
        return (self.__str.upper() in string.upper())

    def set_value(self, value):
        """Set SearchModel string.

        Args:
            value (str): new material name.
        """
        self.__str = str(value)
        self._value_changed()
        if self._modified_fn:
            self._modified_fn(self.__str)

    def get_value_as_string(self):
        """Gets material name as string.

        Returns:
            (str): material name.
        """
        return self.__str


class SearchWidget():
    """Simulated searchable combobox class, used by MaterialListBoxWidget."""
    class WidgetFlags(IntFlag):
        """build_ui_popup() options"""
        SHOW_OPEN_BUTTON = 0x01
        SHOW_GOTO_BUTTON = 0x02
        SHOW_ALL = SHOW_OPEN_BUTTON | SHOW_GOTO_BUTTON


    def __init__(self, theme: str, icon_path: str, modified_fn: callable=None):
        """Initialize class function.

        Args:
            theme (str): theme name, should be "NvidiaDark" or "NvidiaLight". Not wildly supported.
            icon_path (str): path to icons, if None then omni.kit.material.library/data/icons will be used.
            modified_fn (callable): modified_fn passed to SearchModel.
        """
        self._search_model = SearchModel(modified_fn=modified_fn)
        if not icon_path:
            icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"

        if theme == "NvidiaDark":
            BACKGROUND_COLOR = 0xFF555555
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFF333333
            SEARCH_BODY_COLOR = 0xFF2D2D2D
            SEARCH_PLACEHOLDER = 0xFF666666
            ERROR_TEXT_COLOR = 0xFF726FFF
            BUTTON_BACKGROUND_COLOR = 0xFF323434
            GENERAL_BACKGROUND_COLOR = 0xFF23201E
        else:
            BACKGROUND_COLOR = 0xFF545454
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFFACACAF
            SEARCH_BODY_COLOR = 0xFF2D2D2D
            SEARCH_PLACEHOLDER = 0xFF666666
            ERROR_TEXT_COLOR = 0xFF726FFF
            BUTTON_BACKGROUND_COLOR = 0xFF545454
            GENERAL_BACKGROUND_COLOR = 0xFF545454

        self._style = {
            # search_button
            "Button.Image::search_button": {
                "image_url": f"{icon_path}/search.svg",
                "background_color": SEARCH_BODY_COLOR,
                "margin": 0,
                "border_radius": 0.0,
            },
            "Button::search_button": {
                "margin": 0,
                "border_radius": 0.0,
            },

            "Field::search_button": {
                "background_color" : SEARCH_BODY_COLOR,
                "border_radius": 0.0,
            },

            # left_radius_style
            "Field::left_radius_style": {
                "border_radius": 4.0,
                "corner_flag": ui.CornerFlag.LEFT,
                "color": FIELD_TEXT_COLOR,
            },

            "Field::left_radius_style_error": {
                "border_radius": 4.0,
                "corner_flag": ui.CornerFlag.LEFT,
                "color": ERROR_TEXT_COLOR
            },

            # search placeholder
            "Label::search_placeholder": {
                "color": 0xFF666666,
                "border_radius": 0.0,
                "margin_width": 7.0,
            },

            # close/clear button
            "Button.Image::clear_popup": {
                "image_url": f"{icon_path}/close.svg",
            },

            "Button::clear_popup": {
                "background_color" : SEARCH_BODY_COLOR,
                "margin": 0,
                "border_radius": 0.0,
            },

            # clear button (different colors)
            "Button::clear_field":{
                "background_color": GENERAL_BACKGROUND_COLOR,
                "border_radius": 0.0,
            },
            "Button::clear_field:hovered": {
                "background_color": GENERAL_BACKGROUND_COLOR,
                "border_radius": 0.0,
            },
            "Button.Image::clear_field": {
                "image_url": f"{icon_path}/remove.svg"
            },
            "Button.Image::clear_field:hovered": {
                "image_url": f"{icon_path}/remove-hovered.svg"
            },

            # find button
            "Button::find": {
                "background_color": BUTTON_BACKGROUND_COLOR,
                "border_radius": 0.0,
            },
            "Button::find:hovered": {
                "background_color": 0xFF9E9E9E,
                "border_radius": 0.0,
            },
            "Button.Image::find": {
                "image_url": f"{icon_path}/find.svg",
            },

            # listbox button
            "Button.Image::listbox": {
                "color": 0xffcccccc,
                "image_url": f"{icon_path}/listbox.png",
                "alignment": ui.Alignment.CENTER,
            },
            "Button::listbox": {
                "background_color": 0xff292929,
                "border_radius": 3.5,
                "corner_flag": ui.CornerFlag.RIGHT,
            },
            "Button::listbox:hovered": {
                "background_color": 0xFF9E9E9E,
                "border_radius": 3.5,
                "corner_flag": ui.CornerFlag.RIGHT,
            },
        }

    def clean(self):
        """Clean up widget."""
        self._field = None
        self._search_clear = None

    def destroy(self):
        """Destroy class and cleanup."""
        self._field = None
        self._search_clear = None
        del self._search_model

    def update(self, filter_string: str):
        """Update placeholder string and clear button.

        Args:
            filter_string (str): current search string.
        """
        self._placeholder.visible = bool(filter_string == "")
        self._search_clear.enabled = not self._placeholder.visible

    def focus(self):
        """Focus search text."""
        async def focus(field):
            await omni.kit.app.get_app().next_update_async()
            field.focus_keyboard()

        asyncio.ensure_future(focus(self._field))

    def build_ui(self, width: float, search_size: float):
        """build_ui for search widget.

        Args:
            width (float): width of ui.StringField widget.
            search_size (float): size of widget
        """
        def clear_name(field):
            field.model.set_value("")
            field.focus_keyboard()

        with ui.HStack(width=0, height=search_size, style=self._style):
            ui.Button("", width=search_size, enabled=False, name="search_button")
            with ui.ZStack(width=0):
                with ui.HStack(width=0):
                    field = ui.StringField(model=self._search_model, width=width-46, name="search_button")
                    self._search_clear = ui.Button("", width=16, fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, image_width=8, enabled=False, clicked_fn=lambda f=field: clear_name(f), name="clear_popup")
                self._placeholder = ui.Label("Search....", name="search_placeholder")
                self._field = field
                self.focus()

    def set_placeholder_text(self, msg: str):
        """Set material placeholder name from string. This is the string displayed when material name is empty.

        Args:
            msg (str): text to use as placeholder.
        """
        self._placeholder.text = f"{msg}...."
        enabled = bool(msg == "Search")
        self._field.enabled = enabled
        self._field.focus_keyboard(enabled)

    def set_text(self, new_text: str):
        """Set material name from string.

        Args:
            new_text (str): New material name
        """
        if new_text == Constant.SDF_PATH_INVALID:
            new_text = "None"
        self._field.model.set_value(new_text)

    def get_text(self):
        """Get material name as string.

        Returns:
            (str) material name.
        """
        return self._field.model.get_value_as_string()

    def build_ui_popup(self, search_size :float, popup_text: str, index: int, update_fn: callable, widget_flags=WidgetFlags.SHOW_ALL, missing=False):
        """Build the UI for the listbox part of the widget.

        Args:
            search_size (float): widget size.
            popup_text (str): material name selected in combo box.
            index (int): default index of material name in combo box.
            update_fn (callable): callback called when ui.TextField string is cleared.
            widget_flags (WidgetFlags): Can be SHOW_OPEN_BUTTON and/or SHOW_GOTO_BUTTON or None.
            missing (bool): Material name is missing, text will be red.

        Returns:
                (ui.Widget) name field
                (ui.Widget) open button
                (ui.Widget) goto button
        """
        def clear_name(name_field):
            name_field.model.set_value("None")
            if update_fn:
                update_fn(name_field.model, None)

        goto_button = None
        open_button = None
        name_field = None
        style_name = "left_radius_style"

        if popup_text == Constant.SDF_PATH_INVALID:
            popup_text = "None"

        if missing:
            style_name = "left_radius_style_error"

        with ui.HStack(style=self._style, height=search_size):
            name_field = ui.StringField(enabled=False, name=style_name)
            name_field.model.set_value(popup_text)
            name_field.identifier = "combo_drop_target"

            if popup_text != "None" and " (inherited)" not in popup_text:
                ui.Button(
                    "",
                    width=20,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    clicked_fn=lambda f=name_field: clear_name(f),
                    name="clear_field",
                )

            if widget_flags & SearchWidget.WidgetFlags.SHOW_OPEN_BUTTON:
                open_button = ui.Button(
                    "",
                    width=19,
                    name="listbox",
                )
                open_button.identifier = "combo_open_button"

            if (widget_flags & SearchWidget.WidgetFlags.SHOW_GOTO_BUTTON) and index > 0 and not missing:
                goto_button = ui.Button(
                    "",
                    width=20,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    name="find",
                )
                goto_button.identifier = "goto_material_prim"
            self._field = name_field

        return name_field, open_button, goto_button
