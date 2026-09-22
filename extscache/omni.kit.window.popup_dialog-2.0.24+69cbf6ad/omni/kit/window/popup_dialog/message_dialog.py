# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from typing import Callable, Optional
from .dialog import AbstractDialog, PopupDialog
from .style import get_style


class MessageDialog(PopupDialog):
    """
    This simplest of all popup dialogs displays a confirmation message before executing an action.
        
    Keyword Args:
        width (int): Width of popup window. Default 400.
        parent (:obj:'omni.ui.Widget'):OBSOLETE.
        message (str): The displayed message. Default ''.
        title (str): Title of popup window. Default None.
        ok_handler (Callable[[AbstractDialog], None]): Handler called when click ok button. Default None.
                    Function signature is: void ok_handler(AbstractDialog)
        cancel_handler (Callable[[AbstractDialog], None]): Handler called when click cancel button. Default None.
                    Function signature is: void ok_handler(AbstractDialog)
        ok_label (str): Label text for ok button. Default "Ok".
        cancel_label (str): Label text for cancel button. Default "Cancel".
        disable_okay_button (bool): If True, then don't display 'Ok' button. Default False.
        disable_cancel_button (bool): If True, then don't display 'Cancel' button. Default False.
        warning_message (Optional[str]): Warning message that will displayed in red with the warning glyph. Default None.
    """
    def __init__(
        self,
        width: int=400,
        parent: ui.Widget=None, # OBSOLETE
        message: str="",
        title: str=None,
        ok_handler: Callable[[AbstractDialog], None]=None,
        cancel_handler: Callable[[AbstractDialog], None]=None,
        ok_label: str="Ok",
        cancel_label: str="Cancel",
        disable_okay_button: bool=False,
        disable_cancel_button: bool=False,
        warning_message: Optional[str]=None,
    ):

        super().__init__(
            width=width,
            title=title,
            ok_handler=ok_handler,
            cancel_handler=cancel_handler,
            ok_label=ok_label,
            cancel_label=cancel_label,
            modal=True,
            warning_message=warning_message,
        )
        with self._window.frame:
            with ui.VStack():
                self._widget = MessageWidget(message)
                self._build_warning_message()
                self._build_ok_cancel_buttons(disable_okay_button=disable_okay_button, disable_cancel_button=disable_cancel_button)
        self.hide()

    def set_message(self, message: str):
        """
        Updates the message string.

        Args:
            message (str): The message string.

        """
        if self._widget:
            self._widget.set_message(message)

    def destroy(self):
        if self._widget:
            self._widget.destroy()
        self._widget = None
        super().destroy()


class MessageWidget:
    """
    This widget displays a custom message. As opposed to the dialog class, the widget can be combined 
    with other widget types in the same window.

    Keyword Args:
        message (str): The message string

    """
    def __init__(self, message: str = ""):
        self._message_label = None
        self._build_ui(message)

    def _build_ui(self, message: str):
        with ui.ZStack(style=get_style()):
            ui.Rectangle(style_type_name_override="Background")
            with ui.VStack(style_type_name_override="Dialog", spacing=6):
                with ui.HStack(height=0):
                    self._message_label = ui.Label(message, word_wrap=True, style_type_name_override="Message")

    def set_message(self, message: str):
        """
        Updates the message string.

        Args:
            message (str): The message string.

        """
        self._message_label.text = message

    def destroy(self):
        """Destructor."""
        self._message_label = None
