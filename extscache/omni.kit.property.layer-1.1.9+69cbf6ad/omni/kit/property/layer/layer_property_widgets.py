# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides widgets for displaying and interacting with USD layer paths and metadata within a property UI."""


__all__ = ["LayerPathWidget", "LayerMetaWiget"]

import os

import carb
import omni.client
import omni.kit.window.content_browser as content
import omni.ui as ui
import omni.usd
from omni.kit.usd.layers import LayerEventType, get_layer_event_payload, get_layers
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_HEIGHT, SimplePropertyWidget

from .file_picker import FileBrowserSelectionType, FilePicker
from .layer_property_models import LayerMetaModel, LayerPathModel, LayerWorldAxisModel
from .types import LayerMetaName, LayerMetaType


class LayerPathWidget(SimplePropertyWidget):
    """A widget for displaying and interacting with the file path of a USD layer.

    This widget provides an interface for users to view, select, and change the file path of a USD layer. It includes functionality to open a file picker dialog, navigate to the selected file, and update the path based on user input. The widget also supports displaying whether the current layer is missing and allows for finding and replacing layer paths.

    Args:
        icon_path (str): The file system path to the directory containing the icons used in the widget."""

    def __init__(self, icon_path):
        """Initializes the LayerPathWidget with necessary setup."""
        super().__init__(title="Layer Path", collapsed=False)
        self._icon_path = icon_path
        self._file_picker = None
        self._layer_path_field = False
        self._layer_path_model = None
        self._checkpoint_combobox = None
        self._any_item_visible = False

    def destroy(self):
        """Cleans up resources, specifically the file picker if it was created."""
        if self._file_picker:
            self._file_picker.destroy()

    def _show_file_picker(self):
        if not self._file_picker:
            self._file_picker = FilePicker(
                "Select File",
                "Select",
                FileBrowserSelectionType.FILE_ONLY,
                [(omni.usd.writable_usd_re(), omni.usd.writable_usd_files_desc())],
            )
            self._file_picker.set_custom_fn(self._on_file_selected, None)

        if self._layer_path_field:
            value = self._layer_path_field.model.get_value_as_string()
            current_dir = os.path.dirname(value)
            self._file_picker.set_current_directory(current_dir)
        self._file_picker.show_dialog()

    def _on_file_selected(self, path):
        if self._layer_path_field:
            self._layer_path_field.model.replace_layer(path)

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (Dict): The new payload to be handled by the widget.

        Returns:
            bool: True if the payload is not None, False otherwise."""
        if not super().on_new_payload(payload, ignore_large_selection=True):
            return False
        return payload is not None

    def build_items(self):
        """Constructs the UI elements for the layer path widget."""
        layer_item = self._payload
        if layer_item and layer_item():
            with ui.VStack(height=0, spacing=5):
                with ui.HStack():
                    self._layer_path_model = LayerPathModel(layer_item)
                    read_only = bool(self._layer_path_model.is_reserved_layer())
                    self._layer_path_field = ui.StringField(
                        name="models", model=self._layer_path_model, read_only=read_only
                    )

                    if layer_item().missing:
                        self._layer_path_field.set_style({"color": 0xFF6F72FF})

                    style = {"image_url": str(self._icon_path.joinpath("small_folder.png"))}
                    if not read_only:
                        ui.Spacer(width=3)
                        open_button = ui.Button(style=style, width=20, tooltip="Open")
                        open_button.set_clicked_fn(self._show_file_picker)

                    if not self._layer_path_model.anonymous():
                        ui.Spacer(width=3)
                        style["image_url"] = str(self._icon_path.joinpath("find.png"))
                        find_button = ui.Button(style=style, width=20, tooltip="Find")

                        def find_button_fn():
                            path = self._layer_path_field.model.get_value_as_string()
                            # Remove checkpoint and branch so navigate_to works
                            client_url = omni.client.break_url(path)
                            path = omni.client.make_url(
                                scheme=client_url.scheme,
                                user=client_url.user,
                                host=client_url.host,
                                port=client_url.port,
                                path=client_url.path,
                                query=None,
                                fragment=client_url.fragment,
                            )
                            content.get_content_window().navigate_to(path)

                        find_button.set_clicked_fn(find_button_fn)

                if not self._layer_path_model.anonymous() and self._filter.matches("Checkpoint"):
                    self._build_checkpoint_ui(layer_item().identifier)
                    self._any_item_visible = True
        else:
            selected_info_name = "(nothing selected)"
            ui.StringField(name="layer_path", height=LABEL_HEIGHT, enabled=False).model.set_value(selected_info_name)

    def _build_checkpoint_ui(self, absolute_layer_path):
        try:
            # Use checkpoint widget in the drop down menu for more detailed information
            from omni.kit.widget.versioning.checkpoint_combobox import CheckpointCombobox

            with ui.HStack(spacing=HORIZONTAL_SPACING):
                self.add_label("Checkpoint")

                def on_selection_changed(selection):
                    if selection:
                        self._layer_path_model.replace_layer(selection.get_full_url())

                self._checkpoint_combobox = CheckpointCombobox(absolute_layer_path, on_selection_changed)
            return
        except ImportError as e:
            # If the widget is not available, create a simple combo box instead
            carb.log_warn(f"Checkpoint widget in Layer Path widget is not available due to: {e}")


class LayerMetaWiget(SimplePropertyWidget):
    """A widget for displaying and interacting with the metadata of a layer in a USD scene.

    This widget provides a UI component within the application to view and modify metadata associated with a specific layer. It dynamically updates its content based on the layer selected by the user and listens for changes in the layer's metadata to refresh its display.

    Args:
        icon_path (str): The file path to the icon used by the widget."""

    def __init__(self, icon_path):
        """Initializes the LayerMetaWiget with a specified icon path."""
        super().__init__(title="Layer Metadata", collapsed=False)
        self._icon_path = icon_path
        self._models = {}
        self._meta_change_listener = None
        self._any_item_visible = False

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (Dict): The new payload to be handled by the widget.

        Returns:
            bool: True if the payload is not None, False otherwise."""
        if not super().on_new_payload(payload):
            return False
        return payload is not None

    def reset(self):
        """Resets the widget to its initial state, clearing any metadata change listeners and models."""
        super().reset()
        self._meta_change_listener = None
        self._models = {}

    def _on_meta_changed(self, event: carb.events.IEvent):
        payload = get_layer_event_payload(event)
        if payload and payload.event_type == LayerEventType.INFO_CHANGED:
            layer_item = self._payload
            if layer_item and layer_item() and layer_item().layer:
                layer_item = layer_item()
                if layer_item.identifier in payload.layer_info_data:
                    info_tokens = payload.layer_info_data.get(layer_item.identifier, [])
                    for token in info_tokens:
                        model = self._models.get(token, None)
                        if model:
                            model.on_value_changed()

        if payload.event_type == LayerEventType.SUBLAYERS_CHANGED:
            self.request_rebuild()

    def build_items(self):
        """Builds the UI items for the widget based on the current payload."""
        layer_item = self._payload
        if layer_item and layer_item() and layer_item().layer:
            usd_context = layer_item().usd_context
            layers = get_layers(usd_context)
            event_stream = layers.get_event_stream()
            self._meta_change_listener = event_stream.create_subscription_to_pop(
                self._on_meta_changed, name="Layers Property Window"
            )

            model = LayerWorldAxisModel(layer_item)
            self._models[model.get_usd_token_name()] = model
            if self._filter.matches("World Axis"):
                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    self.add_label("World Axis")
                    ui.ComboBox(model, name="choices")
                self._any_item_visible = True

            for index in range(LayerMetaType.NUM_PROPERTIES):
                model = LayerMetaModel(layer_item, index)
                if model.get_value_as_string() is not None:
                    self.add_item_with_model(LayerMetaName[index], model, True)
                    self._models[model.get_usd_token_name()] = model
