# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from typing import List, Dict, Callable, Optional
from collections import namedtuple
from .dialog import AbstractDialog, PopupDialog
from .style import get_style, ICON_PATH


class OptionsDialog(PopupDialog):
    """
    A simple checkbox dialog with a set options and two buttons, OK and Cancel

    Keyword Args:
        width (int): Width of popup window. Default 400.
        parent (:obj:'omni.ui.Widget'):OBSOLETE.
        message (str): Message string.
        title (str): Title of popup window. Default None.
        ok_handler (Callable[[AbstractDialog], None]): Handler called when click ok button. Default None.
                    Function signature is: void ok_handler(AbstractDialog)
        cancel_handler (Callable[[AbstractDialog], None]): Handler called when click cancel button. Default None.
                    Function signature is: void ok_handler(AbstractDialog)
        ok_label (str): Label text for ok button. Default "Ok".
        cancel_label (str): Label text for cancel button. Default "Cancel".
        field_defs ([OptionsDialog.FieldDef]): List of FieldDefs. Default [].
        value_changed_fn (Callable): This callback is triggered on any value change.
        radio_group (bool): If True, then only one option can be selected at a time.

    Note:
        OptionsDialog.FieldDef: 
            A namedtuple of (name, label, default) for describing the options field,
            e.g. OptionsDialog.FieldDef("option", "Option", True).

    """
    FieldDef = namedtuple("OptionsDialogFieldDef", "name label default")

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
        field_defs: List[FieldDef]=None,
        value_changed_fn: Callable=None,
        radio_group: bool=False,
    ):
        super().__init__(
            width=width,
            title=title,
            ok_handler=ok_handler,
            cancel_handler=cancel_handler,
            ok_label=ok_label,
            cancel_label=cancel_label,
            hide_title_bar=True,
            modal=True
        )
        with self._window.frame:
            with ui.VStack():
                self._widget = OptionsWidget(message, field_defs, value_changed_fn, radio_group)
                self._build_ok_cancel_buttons()
        self.hide()

    def get_value(self, name: str) -> bool:
        """
        Returns value of the named field.

        Args:
            name (str): Name of the field.

        Returns:
            bool

        """
        if self._widget:
            return self._widget.get_value(name)
        return None

    def get_values(self) -> Dict:
        """
        Returns all values in a dictionary.

        Returns:
            Dict

        """
        if self._widget:
            return self._widget.get_values()
        return {}

    def get_choice(self) -> str:
        """
        Returns name of chosen option.

        Returns:
            str

        """
        if self._widget:
            return self._widget.get_choice()
        return None

    def destroy(self):
        if self._widget:
            self._widget.destroy()
        self._widget = None
        super().destroy()


class OptionsWidget:
    """
    A simple checkbox widget with a set options. As opposed to the dialog class, the widget can be combined 
    with other widget types in the same window.

    Keyword Args:
        message (str): Message string.
        field_defs ([OptionsDialog.FieldDef]): List of FieldDefs. Default [].
        value_changed_fn (Callable): This callback is triggered on any value change.
        radio_group (bool): If True, then only one option can be selected at a time.

    Note:
        OptionsDialog.FieldDef: 
            A namedtuple of (name, label, default) for describing the options field,
            e.g. OptionsDialog.FieldDef("option", "Option", True).

    """
    def __init__(self,
        message: str = None,
        field_defs: List[OptionsDialog.FieldDef] = [],
        value_changed_fn: Callable = None,
        radio_group: bool = False
    ):
        self._field_defs = field_defs
        self._radio_group = ui.RadioCollection() if radio_group else None
        self._fields: Dict[str, ui.Widget] = {}
        self._build_ui(message, field_defs, value_changed_fn, self._radio_group)

    def _build_ui(self, message: str, field_defs: List[OptionsDialog.FieldDef], value_changed_fn: Callable, radio_group: Optional[ui.RadioCollection]):
        with ui.ZStack(style=get_style()):
            ui.Rectangle(style_type_name_override="Background")
            with ui.VStack(style_type_name_override="Dialog", spacing=0):
                if message:
                    ui.Label(message, height=20, word_wrap=True, style_type_name_override="Message")
                for field_def in field_defs:
                    with ui.HStack():
                        ui.Spacer(width=30)
                        with ui.HStack(height=20, style_type_name_override="Options.Item"):
                            if radio_group:
                                icon_style = {
                                    "image_url": f"{ICON_PATH}/radio_off.svg",
                                    ":checked": {"image_url": f"{ICON_PATH}/radio_on.svg"},
                                }
                                field = ui.RadioButton(
                                    radio_collection=radio_group,
                                    width=26,
                                    height=26,
                                    style=icon_style,
                                    style_type_name_override="Options.RadioButton",
                                )
                            else:
                                field = ui.CheckBox(width=20, style_type_name_override="Options.CheckBox")
                                field.model.set_value(field_def.default)
                            ui.Spacer(width=2)
                            ui.Label(field_def.label, width=0, style_type_name_override="Field.Label")
                            self._fields[field_def.name] = field
                        ui.Spacer()
                #ui.Spacer(height=4)

    def get_values(self) -> dict:
        """
        Returns all values in a dictionary.

        Returns:
            dict

        """
        options = {}
        for name, field in self._fields.items():
            options[name] = field.checked if isinstance(field, ui.RadioButton) else field.model.get_value_as_bool()
        return options

    def get_value(self, name: str) -> bool:
        """
        Returns value of the named field.

        Args:
            name (str): Name of the field.

        Returns:
            bool

        """
        if name and name in self._fields:
            field = self._fields[name]
            return field.checked if isinstance(field, ui.RadioButton) else field.model.get_value_as_bool()
        return None

    def get_choice(self) -> str:
        """
        Returns name of chosen option.

        Returns:
            str

        """
        if self._radio_group:
            choice = self._radio_group.model.get_value_as_int()
            return self._field_defs[choice].name
        return None

    def destroy(self):
        """Destructor."""
        self._field_defs = None
        self._fields.clear()
        self._radio_group = None
