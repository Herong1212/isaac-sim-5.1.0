# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from typing import List, Dict, Callable
from collections import namedtuple
from .dialog import AbstractDialog, PopupDialog
from .options_dialog import OptionsWidget
from .style import get_style


class OptionsMenu(PopupDialog):
    """
    A simple checkbox menu with a set of options

    Keyword Args:
        title (str): Title of this menu. Default None.
        field_defs ([OptionsMenu.FieldDef]): List of FieldDefs. Default [].
        value_changed_fn (Callable): This callback is triggered on any value change.

    Note:
        OptionsMenu.FieldDef: 
            A namedtuple of (name, label, glyph, default) for describing the options field,
            e.g. OptionsDialog.FieldDef("option", "Option", None, True).

    """
    FieldDef = namedtuple("OptionsMenuFieldDef", "name label glyph default")

    def __init__(
        self,
        width: int=400,
        parent: ui.Widget=None,
        title: str=None,
        ok_handler: Callable[[AbstractDialog], None]=None,
        cancel_handler: Callable[[AbstractDialog], None]=None,
        ok_label: str="Ok",
        cancel_label: str="Cancel",
        field_defs: List[FieldDef]=None,
        value_changed_fn: Callable=None,
    ):
        self._widget = OptionsMenuWidget(title, field_defs, value_changed_fn, build_ui=False)
        super().__init__(
            width=width,
            title=title,
            ok_handler=ok_handler,
            cancel_handler=cancel_handler,
            ok_label=ok_label,
            cancel_label=cancel_label,
            hide_title_bar=True,
        )

    def get_values(self) -> dict:
        """
        Returns all values in a dictionary.

        Returns:
            dict

        """
        if self._widget:
            return self._widget.get_values()
        return {}

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
        return False

    def set_value(self, name: str, value: bool):
        """
        Sets the value of the named field.

        Args:
            name (str): Name of the field.
            value (bool): New value

        """
        if self._widget:
            self._widget.set_value(name, value)
        return None

    def reset_values(self):
        """Resets all values to their defaults."""
        if self._widget:
            self._widget.reset_values()
        return None

    def destroy(self):
        """Destructor"""
        if self._widget:
            self._widget.destroy()
        self._widget = None
        super().destroy()

    def _build_widgets(self):
        with self._window.frame:
            with ui.VStack():
                self._widget.build_ui()
        self.hide()

class OptionsMenuWidget:
    """
    A simple checkbox widget with a set of options. As opposed to the menu class, the widget can be combined 
    with other widget types in the same window.

    Keyword Args:
        title (str): Title of this menu. Default None.
        field_defs ([OptionsDialog.FieldDef]): List of FieldDefs. Default [].
        value_changed_fn (Callable): This callback is triggered on any value change.
        build_ui (bool): Build ui when created.

    Note:
        OptionsMenu.FieldDef: 
            A namedtuple of (name, label, glyph, default) for describing the options field,
            e.g. OptionsDialog.FieldDef("option", "Option", None, True).

    """
    def __init__(self,
        title: str = None,
        field_defs: List[OptionsMenu.FieldDef] = [],
        value_changed_fn: Callable = None,
        build_ui: bool = True,
    ):
        self._field_defs = field_defs
        self._field_models: Dict[str, ui.AbstractValueModel] = {}
        for field in field_defs:
            self._field_models[field.name] = ui.SimpleBoolModel(field.default)
        self._fields: Dict[str, ui.Widget] = {}
        self._title = title
        self._value_changed_fn = value_changed_fn
        if build_ui:
            self.build_ui()

    def build_ui(self):
        with ui.ZStack(height=0, style=get_style()):
            ui.Rectangle(style_type_name_override="BorderedBackground")
            with ui.VStack():
                with ui.ZStack(height=0):
                    ui.Rectangle(name="header", style_type_name_override="Background")
                    with ui.HStack(style_type_name_override="Menu.Header"):
                        if self._title:
                            ui.Label(self._title, width=0, name="title", style_type_name_override="Field.Label")
                        ui.Spacer()
                        label = ui.Label(
                            "Reset All", width=0, name="reset_all", style_type_name_override="Field.Label"
                        )
                        ui.Spacer(width=6)
                        label.set_mouse_pressed_fn(lambda x, y, b, _: self.reset_values())
                ui.Spacer(height=4)
                for field_def in self._field_defs:
                    with ui.HStack(height=20, style_type_name_override="Menu.Item"):
                        check_box = ui.CheckBox(model=self._field_models[field_def.name], width=20, style_type_name_override="Menu.CheckBox")
                        # check_box.model.set_value(field_def.default)
                        check_box.model.add_value_changed_fn(
                            lambda _, name=field_def.name: self._value_changed_fn(self, name)
                        )
                        ui.Spacer(width=2)
                        ui.Label(field_def.label, width=0, style_type_name_override="Field.Label")
                        self._fields[field_def.name] = check_box
                ui.Spacer(height=4)

    def get_value(self, name: str) -> bool:
        """
        Returns value of the named field.

        Args:
            name (str): Name of the field.

        Returns:
            bool

        """
        if name and name in self._field_models:
            model = self._field_models[name]
            return model.get_value_as_bool()
        return False

    def get_values(self) -> dict:
        """
        Returns all values in a dictionary.

        Returns:
            dict

        """
        options = {}
        for name, model in self._field_models.items():
            options[name] = model.get_value_as_bool()
        return options

    def set_value(self, name: str, value: bool):
        """
        Sets the value of the named field.

        Args:
            name (str): Name of the field.
            value (bool): New value

        """
        if name and name in self._field_models:
            model = self._field_models[name]
            model.set_value(value)

    def reset_values(self):
        """Resets all values to their defaults."""
        for field_def in self._field_defs:
            model = self._field_models[field_def.name]
            model.set_value(field_def.default)

    def destroy(self):
        """Destructor."""
        self._field_defs = None
        self._fields.clear()
        self._field_models.clear()
