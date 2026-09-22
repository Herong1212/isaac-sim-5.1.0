"""This module provides a user interface for managing the collection of assets, allowing users to specify various collection options and initiate the collection process."""

import os
import omni.ui as ui
import omni.client

from .icons import Icons
from omni.kit.window.file_exporter import get_file_exporter


class CollectMainWindow:
    """A user interface window for managing the collection of assets.

    This class provides a main window interface for users to specify options for asset collection, including the file location and asset filtering preferences. The options are applied when the Start button is clicked, triggering the collection process.

    Args:
        collect_button_fn (callable, optional): Function to call when the Start button is clicked.
        cancel_button_fn (callable, optional): Function to call when the Cancel button is clicked."""

    def __init__(self, collect_button_fn=None, cancel_button_fn=None):
        self._collect_button_fn = collect_button_fn
        self._cancel_button_fn = cancel_button_fn
        self._collection_path_field = None
        self._build_content_ui()

    def destroy(self):
        self._collect_button_fn = None
        self._cancel_button_fn = None
        self._collection_path_field = None
        if self._cancel_button:
            self._cancel_button.set_clicked_fn(None)
            self._cancel_button = None
        if self._collect_button:
            self._collect_button.set_clicked_fn(None)
            self._collect_button = None
        if self._folder_button:
            self._folder_button.set_clicked_fn(None)
            self._folder_button = None
        self._window = None

    def set_collect_fn(self, collect_fn):
        self._collect_button_fn = collect_fn

    def set_cancel_fn(self, cancel_fn):
        self._cancel_button_fn = cancel_fn

    def _build_content_ui(self):
        self._window = ui.Window(
            "Collection Options", visible=False, height=0, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
        )

        self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        def _build_option_checkbox(text, default_value, identifier, tooltip=None):
            stack = ui.HStack(height=0, width=0)
            with stack:
                checkbox = ui.CheckBox(width=20, identifier=identifier, style={"font_size": 16})
                checkbox.model.set_value(default_value)
                ui.Label(text, alignment=ui.Alignment.LEFT)
                if tooltip:
                    stack.set_tooltip(tooltip)

            return checkbox

        style = {
            "Rectangle::hovering": {"background_color": 0x0, "border_radius": 2, "margin": 0, "padding": 0},
            "Rectangle::hovering:hovered": {"background_color": 0xFF9E9E9E},
            "Button.Image::folder": {"image_url": Icons().get("folder")},
            "Button.Image::folder:checked": {"image_url": Icons().get("folder")},
            "Button::folder": {"background_color": 0x0, "margin": 0},
            "Button::folder:checked": {"background_color": 0x0, "margin": 0},
            "Button::folder:pressed": {"background_color": 0x0, "margin": 0},
            "Button::folder:hovered": {"background_color": 0x0, "margin": 0},
        }

        self._window.width = 0
        with self._window.frame:
            with ui.HStack(height=0, style=style, width=0):
                ui.Spacer(width=40)
                with ui.VStack(spacing=10):
                    ui.Spacer(height=10)
                    # build collection path widgets
                    with ui.HStack(height=0):
                        ui.Label("Collection Path:  ", width=0)
                        with ui.VStack(height=0):
                            ui.Spacer(height=4)
                            self._collection_path_field = ui.StringField(
                                height=20, identifier="collect_path", width=ui.Fraction(1)
                            )
                            ui.Spacer(height=4)
                        ui.Spacer(width=5)
                        with ui.VStack(width=0):
                            ui.Spacer()
                            with ui.ZStack(width=20, height=20):
                                ui.Rectangle(name="hovering")
                                self._folder_button = ui.Button(
                                    name="folder", identifier="folder_button", width=24, height=24
                                )
                            self._folder_button.set_tooltip("Choose folder")
                            ui.Spacer()
                        ui.Spacer(width=2)
                        self._folder_button.set_clicked_fn(lambda: self._show_file_picker())

                    # build collection options
                    with ui.HStack(height=0, spacing=10):
                        self._usd_only_checkbox = _build_option_checkbox(
                            "USD Only",
                            False,
                            "usd_only_checkbox",
                            "Only USD files will be collected. Any materials bindings will be removed.",
                        )
                        self._material_only_checkbox = _build_option_checkbox(
                            "Material Only",
                            False,
                            "material_only_checkbox",
                            "Only MDL files and their depdendent textures will be collected.",
                        )
                        self._flat_collection_checkbox = _build_option_checkbox(
                            "Flat Collection",
                            False,
                            "flat_collection_checkbox",
                            "By default, it will keep the folder structure after collection. "
                            "After this option is enabled, assets will be collected into specified folders.",
                        )

                        self._default_prim_only_checkbox = _build_option_checkbox(
                            "Default Prim Only",
                            False,
                            "default_prim_only_checkbox",
                            "By default, it will collect all prims in the root usd file. "
                            "After this option is enabled, only assets under default prim will be collected.",
                        )

                        self._usda_to_usdc_checkbox = _build_option_checkbox(
                            "Convert USDA to USDC",
                            False,
                            "usda_to_usdc_checkbox",
                            "After this option is enabled, USDA files will be converted to USDC ones.",
                        )

                        # add value changed callback to enable flat collection settings combo
                        self._flat_collection_checkbox.model.add_value_changed_fn(self._on_flat_collection_toggled)

                        # add value changed callback to enable default prim options combo
                        self._default_prim_only_checkbox.model.add_value_changed_fn(self._on_default_prim_toggled)

                    # build flat collection texture options (visibility toggled by flat collection checkbox)
                    with ui.HStack(spacing=5):
                        tooltip = "Options for grouping for textures.\nTextures can be grouped under parent folders by MDL or USD, or flat in the same hierarchy."
                        self._flat_options_widgets = [
                            ui.Label("Flat Collection Texture Option: ", name="label", width=0, tooltip=tooltip),
                            ui.ComboBox(
                                0,
                                "Group By MDL",
                                "Group By USD",
                                "Flat",
                                height=10,
                                name="choices",
                                identifier="texture_option_combo",
                            ),
                        ]
                        for widget in self._flat_options_widgets:
                            widget.visible = False

                    # build default prim only options (visibility toggled by default prim only checkbox)
                    with ui.HStack(height=5):
                        tooltip = (
                            "Options for collecting default prims. By default, it only influences root layer.\n"
                            "REMINDER: When it's to collect default prim only for all layers, it's possible that\n"
                            "non-default prims in a layer that are referenced in others layers are invalid anymore after\n"
                            "the option is enabled since it removes all non-default prims in all layers no matter they are\n"
                            "referenced by any layers or not."
                        )

                        self._default_prim_options_widgets = [
                            ui.Label("Default Prim Only Option: ", width=0, tooltip=tooltip),
                            ui.ComboBox(
                                0,
                                "Root Layer Only",
                                "All Layers",
                                height=10,
                                name="choices",
                                identifier="default_prim_option_combo",
                            ),
                        ]
                        for widget in self._default_prim_options_widgets:
                            widget.visible = False

                    # build action buttons
                    with ui.HStack(height=0):
                        ui.Spacer()
                        self._collect_button = ui.Button("Start", width=120, height=0)
                        self._collect_button.set_clicked_fn(self._on_collect_button_clicked)
                        self._cancel_button = ui.Button("Cancel", width=120, height=0)
                        self._cancel_button.set_clicked_fn(self._on_cancel_button_clicked)
                        ui.Spacer()
                    ui.Spacer(height=20)
                ui.Spacer(width=40)

    def _on_collect_button_clicked(self):
        if self._collect_button_fn:
            collect_dir = self._collection_path_field.model.get_value_as_string()
            usd_only = self._usd_only_checkbox.model.get_value_as_bool()
            material_only = self._material_only_checkbox.model.get_value_as_bool()
            flat_collection = self._flat_collection_checkbox.model.get_value_as_bool()
            texture_option = self._flat_options_widgets[1].model.get_item_value_model().as_int
            default_prim_only = self._default_prim_only_checkbox.model.get_value_as_bool()
            usda_to_usdc = self._usda_to_usdc_checkbox.model.get_value_as_bool()
            default_prim_option = self._default_prim_options_widgets[1].model.get_item_value_model().as_int
            self._collect_button_fn(
                collect_dir,
                usd_only,
                flat_collection,
                material_only,
                texture_option,
                default_prim_only,
                default_prim_option,
                usda_to_usdc,
            )

        self._window.visible = False

    def _on_cancel_button_clicked(self):
        if self._cancel_button_fn:
            self._cancel_button_fn()

        self._window.visible = False

    def _show_file_picker(self):
        self._window.visible = False

        def _select_picked_folder_callback(filename: str, dirname: str, extension: str = "", selections=[]):
            path = omni.client.make_absolute_url_if_possible(dirname, filename)
            self._collection_path_field.model.set_value(path)
            self._window.visible = True

        def _cancel_picked_folder_callback(arg0, arg1):
            self._window.visible = True

        filters = [(".*", "All Files (*.*)")]
        path = self._collection_path_field.model.get_value_as_string()
        file_exporter = get_file_exporter()
        file_exporter.show_window(
            title="Select Collect Destination",
            export_button_label="Select",
            export_handler=_select_picked_folder_callback,
            filename_url=path,
            show_only_folders=True,
            click_cancel_handler=_cancel_picked_folder_callback,
            file_extension_types=filters,
        )

    def _on_flat_collection_toggled(self, model):
        for widget in self._flat_options_widgets:
            widget.visible = model.as_bool
        self._window.height = 0

    def _on_default_prim_toggled(self, model):
        for widget in self._default_prim_options_widgets:
            widget.visible = model.as_bool
        self._window.height = 0

    def show(self, export_folder=None):
        if export_folder:
            self._collection_path_field.model.set_value(export_folder)
        self._window.visible = True

    def hide(self):
        self._window.visible = False
