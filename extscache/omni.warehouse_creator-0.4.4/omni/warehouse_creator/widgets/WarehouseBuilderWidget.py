import asyncio
import os
from functools import partial

import carb
import omni.ui as ui
from omni.kit.window.filepicker import FilePickerDialog
from omni.warehouse_creator.styles import get_style
from omni.warehouse_creator.utils import (
    get_default_asset_path,
    get_extension_folder,
    set_default_asset_path,
    validate_asset_path,
)
from omni.warehouse_creator.warehouse_creator import WarehouseBuilder
from omni.warehouse_creator.widgets.WarehouseColumnEditor import WarehouseColumnEditorWidget


class WarehouseBuilderWidget:
    def __init__(self, **kwargs):
        self._on_begin_edit_fn = kwargs.get("begin_edit_fn", None)
        self._on_finish_edit_fn = kwargs.get("finish_edit_fn", None)
        self.builder = WarehouseBuilder(
            finish_edit_fn=partial(
                self.on_finish_edit,
            )
        )
        with ui.VStack():
            with ui.CollapsableFrame("Instructions", height=0, width=ui.Fraction(1), collapsed=True):
                with ui.ScrollingFrame(
                    height=300,
                    width=ui.Fraction(1),
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                ):
                    with ui.VStack(spacing=15, height=0):
                        ui.Label(
                            "Warehouse Layout",
                            style={"font_size": 20, "color": 0xFF00B976},
                        )
                        ui.Spacer(height=1)
                        ui.Label(
                            "To start Building your warehouse, Click on the Build Warehouse Button.",
                            word_wrap=True,
                        )
                        ui.Label(
                            "This will enable you to draw your warehouse outline on the ground plane",
                            word_wrap=True,
                        )
                        ui.Label(
                            "Draw the warehouse by starting on a corner of the warehouse layout, and follow counter-clockwise clicking at the corners of the warehouse.",
                            word_wrap=True,
                        )
                        ui.Label(
                            "Outlines are always placed on the grid and rounded to the closest point, perpendicular to current outlines",
                            word_wrap=True,
                        )
                        ui.Label(
                            "To finish the warehouse construction place a point at the junction on the starting point. ",
                            word_wrap=True,
                        )
                        ui.Label(
                            "Tiles Style",
                            style={"font_size": 20, "color": 0xFF00B976},
                        )
                        ui.Spacer(height=1)
                        ui.Label(
                            "Select the tiles you want to change (To quickly select by clicking - change the select type to Component on the toolbar)",
                            word_wrap=True,
                        )
                        ui.Label(
                            "Go to the properties panel, and select the tile type you want to apply to the selected items",
                            word_wrap=True,
                        )
                        ui.Label(
                            "Columns",
                            style={"font_size": 20, "color": 0xFF00B976},
                        )
                        ui.Spacer(height=1)
                        ui.Label(
                            "Select the floor plan prim on the stage tree, then click on 'Edit Column Placement'",
                            word_wrap=True,
                        )
                        ui.Label(
                            "Pick the columns you want to show/hide on the viewport. You can select multiple with the mouse drag.",
                            word_wrap=True,
                        )
            ui.Spacer(height=10)
            with ui.CollapsableFrame("Dataset Source", height=0, collapsed=True):
                with ui.VStack():
                    with ui.HStack(spacing=2):
                        ui.Label("Path:", width=0)
                        self.str_field = ui.StringField(
                            name="",
                            height=0,
                            alignment=ui.Alignment.LEFT_CENTER,
                            width=ui.Fraction(1),
                            read_only=True,
                            style={"StringField::error": {"color": 0xFF333388}},
                        )
                        model = self.str_field.model
                        model.set_value(get_default_asset_path())

                        # model.add_value_changed_fn(partial(self.validate_path,))
                        def update_field(filename, path):
                            if self.validate_path(path):
                                model.set_value(path)

                        def open_folder_picker():
                            def on_selected(a, b):
                                update_field(a, b)
                                folder_picker.hide()

                            def on_canceled(a, b):
                                folder_picker.hide()

                            folder_picker = FilePickerDialog(
                                "Select Output Folder",
                                allow_multi_selection=False,
                                apply_button_label="Select Folder",
                                click_apply_handler=lambda a, b: on_selected(a, b),
                                click_cancel_handler=lambda a, b: on_canceled(a, b),
                            )

                        with ui.Frame(width=0):
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=open_folder_picker,
                                style=get_style()["IconButton.Image::FolderPicker"],
                            )
            ui.Spacer(height=10)
            with ui.ZStack(height=0):
                self.begin_edit_frame = ui.Frame(height=60)
                self.finish_edit_frame = ui.Frame()
                self.finish_edit_frame.visible = False

            with self.begin_edit_frame:
                self.begin_edit_btn = ui.Button(
                    "Build Warehouse",
                    clicked_fn=partial(
                        self.begin_edit,
                    ),
                    tooltip="Begin Buiding Warehouse",
                    style={
                        "background_color": 0xAA00B976,
                        ":hovered": {"background_color": 0x6600B976},
                    },
                )
            ui.Spacer(height=10)
            with self.finish_edit_frame:
                self.finish_edit_btn = ui.Button(
                    "Finish",
                    clicked_fn=partial(
                        self.finish_edit,
                    ),
                    tooltip="Finish Building the warehouse by connecting last created point to last with straight lines",
                )
            with ui.Frame(height=60):
                self.columns_widget = WarehouseColumnEditorWidget()

    def validate_path(self, path):
        result = validate_asset_path(path, self.builder.get_base_asset_names())
        if not result:
            carb.log_error("Selected folder does not contain the modular warehouse assets.")
            return False
        else:
            set_default_asset_path(path)
            asyncio.ensure_future(self.builder.get_assets_path())
            return True

    def shutdown(self):
        self.columns_widget.shutdown()

    def begin_edit(self, *args):
        self.begin_edit_frame.visible = False
        self.finish_edit_frame.visible = True
        self.builder.begin_edit()
        if self._on_begin_edit_fn:
            self._on_begin_edit_fn()

    def on_finish_edit(self, *args):
        self.begin_edit_frame.visible = True
        self.finish_edit_frame.visible = False
        if self._on_finish_edit_fn:
            self._on_finish_edit_fn()

    def finish_edit(self, *args):
        # TODO: close the warehouse  layout from current position on straight lines.
        self.builder.finish_edit()
