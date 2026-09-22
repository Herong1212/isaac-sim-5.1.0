# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
import carb.input
import omni.ui as ui

from typing import Callable, Union, Optional

from .style import get_style

class AbstractDialog:
    pass


class PopupDialog(AbstractDialog):
    """ Base class for a simple popup dialog with two primary buttons, OK and Cancel."""

    WINDOW_FLAGS = ui.WINDOW_FLAGS_NO_RESIZE
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_POPUP
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_NO_SCROLLBAR

    def __init__(
        self,
        width: int=400,
        parent: ui.Widget=None, # OBSOLETE
        title: str=None,
        ok_handler: Callable[[AbstractDialog], None]=None,
        cancel_handler: Callable[[AbstractDialog], None]=None,
        ok_label: str="Ok",
        cancel_label: str="Cancel",
        hide_title_bar: bool=False,
        modal: bool=False,
        warning_message: Optional[str]=None,
    ):
        """
        Inherited args from the base class.

        Keyword Args:
            width (int): Window width. Default 400.
            title (str): Title to display. Default None.
            ok_handler (Callable): Function to invoke when Ok button clicked. Function signature:
                void okay_handler(dialog: PopupDialog)
            cancel_handler (Callable):  Function to invoke when Cancel button clicked. Function
                signature: void cancel_handler(dialog: PopupDialog)
            ok_label (str): Alternative text to display on 'Accept' button. Default 'Ok'.
            cancel_label (str): Alternative text to display on 'Cancel' button. Default 'Cancel'.
            warning_message (Optional[str]): Warning message that will displayed in red with the warning glyph. Default None.
            parent (omni.ui.Widget): OBSOLETE.

        """
        super().__init__()
        self._title = title
        self._click_okay_handler = ok_handler
        self._click_cancel_handler = cancel_handler
        self._okay_label = ok_label
        self._okay_button = None
        self._cancel_label = cancel_label
        self._cancel_button = None
        self._warning_message = warning_message
        self._modal = modal
        self._width = width
        self._hide_title_bar = hide_title_bar

        self._key_functions = {
            int(carb.input.KeyboardInput.ENTER): self._on_okay,
            int(carb.input.KeyboardInput.ESCAPE): self._on_cancel
        }
        self._build_window()

    def __del__(self):
        self.destroy()

    def show(self, offset_x: int = 0, offset_y: int = 0, parent: ui.Widget = None, recreate_window: bool = False):
        """
        Shows this dialog, optionally offset from the parent widget, if any.

        Keyword Args:
            offset_x (int): X offset. Default 0.
            offset_y (int): Y offset. Default 0.
            parent (ui.Widget): Offset from this parent widget. Default None.
            recreate_window (bool): Recreate popup window. Default False.

        """
        if recreate_window:
            # OM-42020: Always recreate window.
            # Recreate to follow the parent window type (external window or main window) to make position right
            # TODO: Only recreate when parent window external status changed. But there is no such notification now.
            self._window = None
            self._build_window()

        if parent:
            self._window.position_x = parent.screen_position_x + offset_x
            self._window.position_y = parent.screen_position_y + offset_y
        elif offset_x != 0 or offset_y != 0:
            self._window.position_x = offset_x
            self._window.position_y = offset_y

        self._window.set_key_pressed_fn(self._on_key_pressed)
        self._window.visible = True

    def hide(self):
        """Hides this dialog."""
        self._window.visible = False

    @property
    def position_x(self):
        """
        Get position x of the dialog window.
        
        Returns:
            int
        """
        return self._window.position_x

    @property
    def position_y(self):
        """
        Get position y of the dialog window.
        
        Returns:
            int
        """
        return self._window.position_y

    @property
    def window(self):
        """
        Get the dialog window widget.
        
        Returns:
            :obj:'omni.ui.window'
        """
        return self._window
    
    def _build_window(self):
        window_flags = self.WINDOW_FLAGS
        if not self._title or self._hide_title_bar:
            window_flags |= ui.WINDOW_FLAGS_NO_TITLE_BAR
        if self._modal:
            window_flags |= ui.WINDOW_FLAGS_MODAL
        self._window = ui.Window(self._title or "", width=self._width, height=0, flags=window_flags)

        self._build_widgets()

    def _build_widgets(self):
        pass

    def _cancel_handler(self, dialog):
        self.hide()

    def _ok_handler(self, dialog):
        pass

    def _build_ok_cancel_buttons(self, disable_okay_button: bool = False, disable_cancel_button: bool = False):
        if disable_okay_button and disable_cancel_button:
            return

        with ui.HStack(height=20, spacing=4):
            ui.Spacer()
            if not disable_okay_button:
                self._okay_button = ui.Button(self._okay_label, width=100, clicked_fn=self._on_okay)
            if not disable_cancel_button:
                self._cancel_button = ui.Button(self._cancel_label, width=100, clicked_fn=self._on_cancel)
            ui.Spacer()

    def _build_warning_message(self, glyph_width=50, glyph_height=100):
        if not self._warning_message:
            return

        with ui.ZStack(style=get_style(), height=0):
            with ui.HStack(style={"margin": 15}):
                ui.Image(
                    "resources/glyphs/Warning_Log.svg",
                    width=glyph_width,
                    height=glyph_height,
                    alignment=ui.Alignment.CENTER
                )
                ui.Label(self._warning_message, word_wrap=True, style_type_name_override="Message")
            ui.Rectangle(style_type_name_override="Rectangle.Warning")

    def _on_okay(self):
        if self._click_okay_handler:
            self._click_okay_handler(self)

    def _on_cancel(self):
        if self._click_cancel_handler:
            self._click_cancel_handler(self)
        else:
            self.hide()

    def _on_key_pressed(self, key, mod, pressed):
        if not pressed:
            return
        func = self._key_functions.get(key)
        if func and mod in (0, ui.Widget.FLAG_WANT_CAPTURE_KEYBOARD):
            func()

    def set_okay_clicked_fn(self, ok_handler: Callable[[AbstractDialog], None]):
        """
        Sets function to invoke when Okay button is clicked.

        Args:
            ok_handler (Callable): Callback with signature: void okay_handler(dialog: PopupDialog)

        """
        self._click_okay_handler = ok_handler

    def set_cancel_clicked_fn(self, cancel_handler: Callable[[AbstractDialog], None]):
        """
        Sets function to invoke when Cancel button is clicked.

        Args:
            cancel_handler (Callable): Callback with signature: void cancel_handler(dialog: PopupDialog)

        """
        self._click_cancel_handler = cancel_handler

    def destroy(self):
        """ Destructor """
        self._window = None
        self._click_okay_handler = None
        self._click_cancel_handler = None
        self._key_functions = None
        self._okay_button = None
        self._cancel_button = None


def get_field_value(field: ui.AbstractField) -> Union[str, int, float, bool]:
    """
    Returns value of the given field.

    Args:
        field (:obj:'ui.AbstractField'): Name of the field.

    Returns:
        Union[str, int, float, bool]
    """
    
    if not field:
        return None
    if isinstance(field, ui.StringField):
        return field.model.get_value_as_string()
    elif type(field) in [ui.IntField, ui.IntDrag, ui.IntSlider]:
        return field.model.get_value_as_int()
    elif type(field) in [ui.FloatField, ui.FloatDrag, ui.FloatSlider]:
        return field.model.get_value_as_float()
    elif isinstance(field, ui.CheckBox):
        return field.model.get_value_as_bool()
    else:
        # TODO: Retrieve values for MultiField
        return None
