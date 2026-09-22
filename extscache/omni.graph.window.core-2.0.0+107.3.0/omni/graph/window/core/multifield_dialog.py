# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Any, Callable, List, Optional, Tuple, Type

import omni.ui as ui
from omni.kit.window.popup_dialog.dialog import AbstractDialog, PopupDialog
from omni.kit.window.popup_dialog.input_dialog import InputWidget


class MultiFieldDialog(PopupDialog):
    """
    A simple popup dialog with multiple input field and two buttons, OK and Cancel

    Keyword Args:
        title (str): Title of popup window.  Default 'input-dialog'.
        message (str): Message to display.
        width (int): The dialog list in pixels
        ok_handler: callback when ok button is pressed
        cancel_handler: callback when cancel button is pressed
        items: List of tuples representing each line in the dialog using
            (pre_label, input_cls, default_value, post_label) where:

            pre_label (str): Text displayed before input field. Can be None.
            input_cls (:obj:`omni.ui.AbstractField`): Type of input field specified by class name, e.g.
                :obj:`omni.ui.StringField`, :obj:`omni.ui.IntField`, :obj:`omni.ui.CheckBox`.
            default_value (Any): Default value of the input field. Must correspond to the default value for
            input_cls
            post_label (str): Text displayed after input field. Can be None.

            If 'items' is not supplied then a default containing Compound Name and Namespace fields will be used.

    """

    def __init__(
        self,
        width: int = 300,
        message: str = None,
        title: str = None,
        ok_handler: Callable[[AbstractDialog], None] = None,
        cancel_handler: Callable[[AbstractDialog], None] = None,
        ok_label: str = "Ok",
        cancel_label: str = "Cancel",
        items: List[Tuple[Optional[str], Type[ui.AbstractField], Any, Optional[str]]] = None,
    ):
        super().__init__(
            width=width,
            title=title,
            ok_handler=ok_handler,
            cancel_handler=cancel_handler,
            ok_label=ok_label,
            cancel_label=cancel_label,
            modal=True,
        )

        if items is None:
            items = [
                ("Compound Name", ui.StringField, "Compound", None),
                ("Namespace", ui.StringField, "local.nodes", None),
            ]

        with self._window.frame:
            self._widgets = []
            with ui.VStack():
                for pre_label, input_cls, default_value, post_label in items:
                    self._widgets.append(
                        InputWidget(
                            message=message,
                            input_cls=input_cls,
                            pre_label=pre_label,
                            post_label=post_label,
                            default_value=default_value,
                        )
                    )
                self._build_ok_cancel_buttons()
        self.hide()

    def get_values(self, index: Optional[int] = None) -> Any:
        """
        Returns the values of the widgets, either by index, or as a list
        """
        if self._widgets:
            if index is not None:
                return self._widgets[index].get_value()
            return [widget.get_value() for widget in self._widgets]
        return None

    def destroy(self):
        """Destructor"""
        if self._widgets:
            for widget in self._widgets:
                widget.destroy()
        self._widgets = None
        super().destroy()
