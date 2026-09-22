# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List, Optional

import carb
import omni.graph.core as og
import omni.kit.app
import omni.ui as ui

from . import UINodeCommon


class OgnButton(UINodeCommon.OgWidgetNode):
    @staticmethod
    def compute(db) -> bool:
        if db.inputs.create != og.ExecutionAttributeState.DISABLED:
            start_hidden = db.inputs.startHidden
            text = db.inputs.text

            (size_x, size_y) = db.inputs.size
            if size_x < 0 or size_y < 0:
                db.log_error("The size of the widget cannot be negative!")
                return False

            parent_widget_path = db.inputs.parentWidgetPath
            if not parent_widget_path:
                db.log_error("No parentWidgetPath supplied.")
                return False

            parent_widget = UINodeCommon.find_widget_among_all_windows(parent_widget_path)
            if parent_widget is None:
                db.log_error("Could not find parent widget.")
                return False

            style = {}
            try:
                style = UINodeCommon.to_ui_style(db.inputs.style)
            except SyntaxError as err:
                db.log_error(f"'inputs:style': {err.msg}")
                return False

            widget_identifier = UINodeCommon.get_unique_widget_identifier(db)

            def on_button_clicked():
                widget = UINodeCommon.get_registered_widget(db.abi_context, widget_identifier)
                if not widget or not widget.enabled:
                    return
                message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
                event_name = "clicked_" + widget_identifier
                reg_event_name = UINodeCommon.registered_event_name(event_name)
                message_bus.push(reg_event_name)

            # Now create the button widget and register callbacks
            with parent_widget:
                button = ui.Button(
                    text, identifier=widget_identifier, width=size_x, height=size_y, visible=not start_hidden
                )
                button.set_clicked_fn(on_button_clicked)
                if style:
                    button.set_style(style)

            OgnButton.register_widget(db.abi_context, widget_identifier, button)
            db.outputs.created = og.ExecutionAttributeState.ENABLED
            db.outputs.widgetPath = UINodeCommon.find_widget_path(button)
            return True

        db.log_warning("Unexpected execution with no execution input enabled")
        return False

    @staticmethod
    def get_property_names(button: ui.Button, writeable: bool) -> Optional[List[str]]:
        props = super(OgnButton, OgnButton).get_property_names(button, writeable)
        if props is not None:
            if not isinstance(button, ui.Button):
                carb.log_warn(f"Attempt to retrieve property names from non-button object '{button}'.")
                return None

            props += [
                "image_height",  # ui.Length
                "image_url",  # str
                "image_width",  # ui.Length
                "spacing",  # float
                "text",  # str
            ]
        return props

    @staticmethod
    def resolve_output_property(button: ui.Button, property_name: str, attribute: og.Attribute):
        if not isinstance(button, ui.Button):
            raise og.OmniGraphError(f"Attempt to resolve property on non-button object '{button}'.")
        if property_name not in OgnButton.get_property_names(button, False):
            raise og.OmniGraphError(f"'{property_name}' is not a readable property of button '{button.identifier}'")
        super(OgnButton, OgnButton).resolve_output_property(button, property_name, attribute)

    @staticmethod
    def get_property_value(button: ui.Button, property_name: str, attribute: og.RuntimeAttribute):
        if not isinstance(button, ui.Button):
            raise og.OmniGraphError(
                f"Attempt to get value of property {property_name} on non-button object '{button}'."
            )
        if property_name not in OgnButton.get_property_names(button, False):
            raise og.OmniGraphError(f"'{property_name}' is not a readable property of button '{button.identifier}'")
        super(OgnButton, OgnButton).get_property_value(button, property_name, attribute)

    @staticmethod
    def set_property_value(button: ui.Button, property_name: str, attribute: og.RuntimeAttribute):
        if not isinstance(button, ui.Button):
            raise og.OmniGraphError(
                f"Attempt to set value of property {property_name} on non-button object '{button}'."
            )
        if property_name not in OgnButton.get_property_names(button, True):
            raise og.OmniGraphError(f"'{property_name}' is not a writeable property of button '{button.identifier}'")
        super(OgnButton, OgnButton).set_property_value(button, property_name, attribute)

    @staticmethod
    def get_style_element_names(button: ui.Button, writeable: bool) -> List[str]:
        element_names = super(OgnButton, OgnButton).get_style_element_names(button, writeable)
        if element_names is not None:  # noqa: SIM102
            if not isinstance(button, ui.Button):
                carb.log_warn(f"Attempt to retrieve style element names from non-button widget '{button}'.")
                return None

            # TBD
        return element_names

    @staticmethod
    def get_style_value(button: ui.Button, element_name: str, attribute: og.RuntimeAttribute) -> bool:
        if not isinstance(button, ui.Button):
            carb.log_warn(f"Attempt to get style element from non-button object '{button}'.")
            return False
        return super(OgnButton, OgnButton).get_style_value(button, element_name, attribute)

    @staticmethod
    def set_style_value(button: ui.Button, element_name: str, attribute: og.RuntimeAttribute) -> bool:
        if not isinstance(button, ui.Button):
            carb.log_warn(f"Attempt to set style element on non-button object '{button}'.")
            return False
        return super(OgnButton, OgnButton).set_style_value(button, element_name, attribute)
