# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
import omni.ui as ui


class CreateAttributePopupDialog:
    """The popup dialog for creating new dynamic attribute on the script node"""

    def __init__(self, create_new_attribute_callback, require_port_type: og.AttributePortType):
        """Build the dialog
        Args:
            create_new_attribute_callback: The callback to invoke when user confirms selection
            require_port_type: What port type is being created
        """
        self.create_new_attribute_callback = create_new_attribute_callback
        self.all_supported_types = []
        self.all_displayed_types = []
        self.window = None
        self.attribute_name_field = None
        self.scrolling_frame = None
        self.selected_type_button = None
        self.error_message_label = None

        self.all_supported_types = self.get_all_supported_types()
        self.all_displayed_types = self.all_supported_types
        self.require_port_type = require_port_type
        self.build_popup_dialog()

    def get_all_supported_types(self):
        """Get a list of types that can be added"""
        types = []
        for attr_type in ogn.supported_attribute_type_names():
            if attr_type in ("any", "transform", "bundle", "execution", "path") or (attr_type[:9] == "transform"):
                continue
            types.append(attr_type)
        return types

    def build_scrolling_frame(self):
        """Build the scrolling frame underneath the search bar"""

        def _on_type_selected(button):
            if self.selected_type_button is not None:
                self.selected_type_button.checked = False
            self.selected_type_button = button
            self.selected_type_button.checked = True

        self.scrolling_frame.clear()
        with self.scrolling_frame:
            with ui.VStack():
                for displayed_type in self.all_displayed_types:
                    button = ui.Button(displayed_type, height=20)
                    button.set_clicked_fn(partial(_on_type_selected, button))

    def build_popup_dialog(self):
        def filter_types_by_prefix(text):
            """Callback executed when the user presses enter in the search bar"""
            if text is None:
                self.all_displayed_types = self.all_supported_types
            else:
                text = text[0]
                self.all_displayed_types = [
                    displayed_type for displayed_type in self.all_supported_types if displayed_type[: len(text)] == text
                ]
            self.build_scrolling_frame()
            self.selected_type_button = None

        def on_create_new_attribute():
            """Callback executed when the user creates a new dynamic attribute"""
            if not self.attribute_name_field.model.get_value_as_string():
                self.error_message_label.text = "Error: Attribute name cannot be empty"
                return

            if not self.attribute_name_field.model.get_value_as_string()[0].isalpha():
                self.error_message_label.text = "Error: The first character of attribute name must be a letter"
                return

            if self.selected_type_button is None:
                self.error_message_label.text = "Error: You must select a type for the new attribute"
                return

            attrib_name = self.attribute_name_field.model.get_value_as_string()
            attrib_port_type = self.require_port_type
            attrib_type_name = self.selected_type_button.text
            attrib_type = og.AttributeType.type_from_ogn_type_name(attrib_type_name)
            self.create_new_attribute_callback(attrib_name, attrib_port_type, attrib_type, None, None)

            self.window.visible = False

        def on_cancel_clicked():
            self.window.visible = False

        match self.require_port_type:
            case og.AttributePortType.OUTPUT:
                title = "Output"
            case og.AttributePortType.INPUT:
                title = "Input"
            case og.AttributePortType.STATE:
                title = "State"
            case _:
                raise AssertionError()

        window_flags = ui.WINDOW_FLAGS_NO_RESIZE
        self.window = ui.Window(
            f"Create {title}",
            width=400,
            height=0,
            padding_x=15,
            padding_y=15,
            flags=window_flags,
        )
        input_field_width = ui.Percent(60)

        with self.window.frame:
            with ui.VStack(spacing=10):
                # Attribute name string field
                with ui.HStack(height=0):
                    ui.Label("Attribute Name: ")
                    self.attribute_name_field = ui.StringField(width=input_field_width, height=20)

                # Attribute type search bar
                with ui.HStack(height=0):
                    ui.Label("Attribute Type: ", alignment=ui.Alignment.LEFT_TOP)
                    with ui.VStack(width=input_field_width):
                        # Search bar
                        try:
                            from omni.kit.widget.searchfield import SearchField

                            SearchField(
                                show_tokens=False, subscribe_edit_changed=True, on_search_fn=filter_types_by_prefix
                            )
                        except ImportError:
                            # skip the search bar if the module cannot be imported
                            pass
                        # List of attribute types
                        self.scrolling_frame = ui.ScrollingFrame(
                            height=150,
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                            style_type_name_override="TreeView",
                        )
                        self.build_scrolling_frame()

                # OK button to confirm selection
                with ui.HStack(height=0):
                    ui.Spacer()
                    with ui.HStack(width=input_field_width, height=20):
                        ui.Button(
                            "OK",
                            clicked_fn=on_create_new_attribute,
                        )
                        ui.Button(
                            "Cancel",
                            clicked_fn=on_cancel_clicked,
                        )

                # Some empty space to display error messages if needed
                self.error_message_label = ui.Label(
                    " ", height=20, alignment=ui.Alignment.H_CENTER, style={"color": 0xFF0000FF}
                )
