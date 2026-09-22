"""This module provides a SearchWidget with a customizable searchable combobox and a SearchModel for managing search functionality in UI components."""

__all__ = ['SearchModel', 'SearchWidget']

import asyncio
import omni.kit.app
import omni.ui as ui
from enum import IntFlag


class SearchModel(ui.AbstractValueModel):
    """A model to support searching functionality in UI components.

    This class provides methods to set and retrieve search strings, and to determine if a given string is part of the current search string. It is designed to be used within UI components that require search capabilities, such as searchable combo boxes or lists.

    Args:
        modified_fn (callable): A function to be called when the search string is modified."""

    def __init__(self, modified_fn):
        """Initializes the SearchModel with a function to call when the model is modified."""
        super().__init__()
        self._modified_fn = modified_fn
        self.__str = ""

    def is_in_string(self, string: str):
        """Checks if the model's current string is a substring of the provided string.

        Args:
            string (str): The string to check against.

        Returns:
            bool: True if the model's string is a substring of `string`, False otherwise."""
        if self.__str == "":
            return True
        return self.__str.upper() in string.upper()

    def set_value(self, value):
        """Sets the value of the model and triggers the modified callback if it's provided.

        Args:
            value: The new value to set for the model."""
        self.__str = str(value)
        self._value_changed()
        if self._modified_fn:
            self._modified_fn(self.__str)

    def get_value_as_string(self):
        """Retrieves the current value of the model as a string.

        Returns:
            str: The current value of the model."""
        return self.__str


class SearchWidget:
    """A widget that provides a searchable combobox with customizable styles.

    Args:
        theme (str): The theme to apply to the combobox.
        icon_path (str): Path to the directory containing the icons.
        modified_fn (callable, optional): Function to call when search input is modified."""

    def __init__(self, theme: str, icon_path: str, modified_fn: callable = None):
        """A widget that provides a searchable combobox with customizable styles.

        Args:
            theme (str): The theme to apply to the combobox.
            icon_path (str): Path to the directory containing the icons.
            modified_fn (callable, optional): Function to call when search input is modified."""

        self._search_model = SearchModel(modified_fn=modified_fn)
        if not icon_path:
            icon_path = (
                f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
            )

        if theme == "NvidiaDark":
            SEARCH_BODY_COLOR = 0xFF2D2D2D
            SEARCH_PLACEHOLDER = 0xFF666666
            BUTTON_BACKGROUND_COLOR = 0xFF323434
            COMBO_BACKGROUND_COLOR = 0xFF92929
            GENERAL_BACKGROUND_COLOR = 0xFF24211F
        else:
            SEARCH_BODY_COLOR = 0xFF2D2D2D
            SEARCH_PLACEHOLDER = 0xFF666666
            BUTTON_BACKGROUND_COLOR = 0xFF545454
            COMBO_BACKGROUND_COLOR = 0xFF545454
            GENERAL_BACKGROUND_COLOR = 0xFF545454

        self._style = {
            # search_button
            "Button.Image::search_button": {
                "image_url": f"{icon_path}/search.svg",
                "background_color": SEARCH_BODY_COLOR,
                "margin": 0,
            },
            "Button::search_button": {"margin": 0},
            "Field::search_button": {"background_color": SEARCH_BODY_COLOR},
            "Field::search_button:hovered": {"background_color": SEARCH_BODY_COLOR},
            # search placeholder
            "Label::search_placeholder": {"color": SEARCH_PLACEHOLDER},
            # remove button
            "Button.Image::remove": {"image_url": f"{icon_path}/remove.svg"},
            "Button.Image::remove:hovered": {"image_url": f"{icon_path}/remove-hovered.svg"},
            "Button::remove": {"background_color": SEARCH_BODY_COLOR, "margin": 0},
            "Button::remove:hovered": {"background_color": SEARCH_BODY_COLOR, "margin": 0},
            # remove button popup (different colors)
            "Button::remove_popup": {"background_color": GENERAL_BACKGROUND_COLOR, "margin": 0},
            "Button::remove_popup:hovered": {"background_color": GENERAL_BACKGROUND_COLOR, "margin": 0},
            "Button.Image::remove_popup": {"image_url": f"{icon_path}/remove.svg"},
            "Button.Image::remove_popup:hovered": {"image_url": f"{icon_path}/remove-hovered.svg"},
            # find button
            "Button::find": {"background_color": BUTTON_BACKGROUND_COLOR},
            "Button.Image::find": {"image_url": f"{icon_path}/find.svg"},
            # listbox button
            "Button.Image::listbox": {"image_url": f"{icon_path}/listbox.svg"},
            "Button::listbox": {"background_color": COMBO_BACKGROUND_COLOR, "padding": 6, "margin": 0},
        }

    def clean(self):
        """Cleans up the SearchWidget and destroys models."""
        self._field = None
        self._search_field = None
        self._search_clear = None
        self._update_fn = None

    def destroy(self):
        """Destroys the SearchWidget widget."""
        self._field = None
        self._search_field = None
        self._search_clear = None
        self._update_fn = None
        del self._search_model

    def update(self, string):
        """Update search string."""
        self._placeholder.visible = bool(string == "")
        self._search_clear.enabled = not self._placeholder.visible

    def focus(self):
        """Focus caret on search string."""
        async def focus(field):
            await omni.kit.app.get_app().next_update_async()
            field.focus_keyboard()

        asyncio.ensure_future(focus(self._field))

    def build_ui(self, width, search_size):
        """Build UI for SearchWidget."""
        def clear_name(field):
            field.model.set_value("")
            field.focus_keyboard()

        with ui.HStack(width=0, height=0, style=self._style):
            ui.Button("", width=search_size, height=search_size, enabled=False, name="search_button")
            with ui.ZStack(width=0, height=0):
                with ui.HStack(width=0, height=0):
                    field = ui.StringField(
                        model=self._search_model, width=width - 46, height=search_size, name="search_button"
                    )
                    self._search_clear = ui.Button(
                        "",
                        width=search_size,
                        height=search_size,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        enabled=False,
                        clicked_fn=lambda f=field: clear_name(f),
                        name="remove",
                    )
                self._placeholder = ui.Label("  Search....", height=search_size, name="search_placeholder")
                self._field = field
                self.focus()

    def set_placeholder_text(self, msg: str):
        """Sets string when search field is empty."""
        self._placeholder.text = f"  {msg}...."
        enabled = bool(msg == "Search")
        self._field.enabled = enabled
        self._field.focus_keyboard(enabled)

    def set_text(self, new_text: str):
        """Sets selected item in items list."""
        changed = bool(self._search_field.model.get_value_as_string() != new_text)
        self._search_field.model.set_value(new_text)
        if changed and self._update_fn:
            self._update_fn(self._search_field.model)

    def get_text(self):
        """Gets selected item in items list."""
        return self._search_field.model.get_value_as_string()

    def build_ui_popup(self, search_size: float, default_value: str, popup_text: str, index: int, update_fn: callable):
        """Builds Combobox like widget when 'open' button is clicked."""
        def clear_name(name_field):
            name_field.model.set_value(default_value)
            if update_fn:
                update_fn(name_field.model)

        self._update_fn = update_fn
        open_button = None
        name_field = None

        with omni.ui.VStack(height=0, spacing=0, style={"margin_width": 0}):
            with ui.HStack(style=self._style):
                name_field = ui.StringField(height=search_size, enabled=False)
                name_field.model.set_value(popup_text)

                ui.Button(
                    "",
                    width=20,
                    height=20,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    clicked_fn=lambda f=name_field: clear_name(f),
                    name="remove_popup",
                )

                open_button = ui.Button("", width=20, height=20, image_width=8, name="listbox")

        self._search_field = name_field
        return name_field, open_button
