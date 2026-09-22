# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
import omni.kit.app
import asyncio

from typing import Callable, Any, Optional
from .dialog import AbstractDialog, PopupDialog, get_field_value
from .style import get_style


class InputDialog(PopupDialog):
    """
    A simple popup dialog with an input field and two buttons, OK and Cancel

    Keyword Args:
        width (int): Width of popup window. Default 400.
        parent (:obj:'omni.ui.Widget'):OBSOLETE.
        message (str): Message to display.
        title (str): Title of popup window.  Default None.
        ok_handler (Callable[[AbstractDialog], None]): Handler called when click ok button. Default None.
                    Function signature is: void ok_handler(AbstractDialog)
        cancel_handler (Callable[[AbstractDialog], None]): Handler called when click cancel button. Default None.
                    Function signature is: void ok_handler(AbstractDialog)
        ok_label (str): Label text for ok button. Default "Ok".
        cancel_label (str): Label text for cancel button. Default "Cancel".
        input_cls (omni.ui.AbstractField): Type of input field specified by class name, e.g.
            omni.ui.StringField, omni.ui.IntField, omni.ui.CheckBox. Default is omni.ui.StringField.
        pre_label (str): Text displayed before input field. Default None.
        post_label (str): Text displayed after input field. Default None.
        default_value (str): Default value of the input field.
        warning_message (Optional[str]): Warning message that will displayed in red with the warning glyph. Default None.

    """
    def __init__(
        self,
        width: int=400,
        parent: ui.Widget=None, # OBSOLETE
        message: str=None,
        title: str=None,
        ok_handler: Callable[[AbstractDialog], None]=None,
        cancel_handler: Callable[[AbstractDialog], None]=None,
        ok_label: str="Ok",
        cancel_label: str="Cancel",
        input_cls: ui.AbstractField=None,
        pre_label: str=None,
        post_label: str=None,
        default_value: str=None,
        warning_message: Optional[str]=None
    ):
        super().__init__(
            width=width,
            title=title,
            ok_handler=ok_handler,
            cancel_handler=cancel_handler,
            ok_label=ok_label,
            cancel_label=cancel_label,
            modal=True,
            warning_message=warning_message
        )
        with self._window.frame:
            with ui.VStack():
                self._build_warning_message()
                self._widget = InputWidget(
                    message=message,
                    input_cls=input_cls or ui.StringField,
                    pre_label=pre_label,
                    post_label=post_label,
                    default_value=default_value)
                self._build_ok_cancel_buttons()
        self.hide()

    def get_value(self) -> Any:
        """
        Returns field value.

        Returns:
            Any, e.g. one of [str, int, float, bool]

        """
        if self._widget:
            return self._widget.get_value()
        return None

    def destroy(self):
        """Destructor."""
        if self._widget:
            self._widget.destroy()
        self._widget = None
        super().destroy()


class InputWidget:
    """
    A simple widget with an input field. As opposed to the dialog class, the widget can be combined 
    with other widget types in the same window.

    Keyword Args:
        message (str): Message to display.
        input_cls (omni.ui.AbstractField): Class of the input field, e.g.
            omni.ui.StringField, omni.ui.IntField, omni.ui.CheckBox. Default is omni.ui.StringField.
        pre_label (str): Text displayed before input field. Default None.
        post_label (str): Text displayed after input field. Default None.
        default_value (str): Default value of the input field.

    """
    def __init__(self,
        message: str = None,
        input_cls: ui.AbstractField = None,
        pre_label: str = None,
        post_label: str = None,
        default_value: Any = None
    ):
        self._input = None
        self._build_ui(message, input_cls or ui.StringField, pre_label, post_label, default_value)

    def _build_ui(self,
        message: str,
        input_cls: ui.AbstractField,
        pre_label: str,
        post_label: str,
        default_value: Any,
    ):
        with ui.ZStack(style=get_style()):
            ui.Rectangle(style_type_name_override="Background")
            with ui.VStack(style_type_name_override="Dialog", spacing=6):
                if message:
                    ui.Label(message, height=20, word_wrap=True, style_type_name_override="Message")
                with ui.HStack(height=0):
                    input_width = 100
                    if pre_label:
                        ui.Label(pre_label, style_type_name_override="Field.Label", name="prefix")
                        input_width -= 30
                    if post_label:
                        input_width -= 30
                    self._input = input_cls(
                        width=ui.Percent(input_width), height=20, style_type_name_override="Input"
                    )
                    if default_value:
                        self._input.model.set_value(default_value)
                    # OM-95817: Wait a frame to make sure it focus correctly
                    async def focus_field():
                        await omni.kit.app.get_app().next_update_async()
                        if self._input:
                            self._input.focus_keyboard()
                    asyncio.ensure_future(focus_field())
                    if post_label:
                        ui.Label(post_label, style_type_name_override="Field.Label", name="postfix")

    def get_value(self) -> Any:
        """
        Returns value of input field.

        Returns:
            Any
        """
        if self._input:
            return get_field_value(self._input)
        return None

    def destroy(self):
        """Destructor."""
        self._input = None
        self._window = None