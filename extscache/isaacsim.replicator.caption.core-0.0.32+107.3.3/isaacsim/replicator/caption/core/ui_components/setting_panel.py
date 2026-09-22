# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import __main__
import asyncio
import carb
import omni.ui as ui
import omni.usd
from omni.kit.widget.settings import SettingType, create_setting_widget
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.metropolis.utils.ui_util import UIUtil
from pxr import Gf
from omni.metropolis.utils.ui_util import MinimalStringListModel
from ..settings import ReplicatorCaptionSettings
from ..stage_info_manager import StageInfoManager


COLOR_BLACK = 0x0
BOUNDING_RADIUS = 1.5
UI_DISTANCE = 120
STRING_FIELD_WIDTH = 300

# TODO (https://jirasw.nvidia.com/browse/METROPERF-923): Unify and canonicalize the style throughout IRC
def get_collapsable_frame_style():
    return {
        "border_radius": BOUNDING_RADIUS * 2,
        "border_color": COLOR_BLACK,
        "border_width": 1,
        "padding": 6,
    }


class CaptionSettingPanel:
    def __init__(self):
        self.parent_ui = None  # Initialize parent_ui reference
        self._root_prim_field = None
        self.content_frame = None
        self.generate_image = None  # this is the debug button to generate character information
        self.generate_character_info = None
        self.generate_environment_info = None
        self.cameras_prim_paths = []
        self.camera_combo_box = None
        self._load_stage_handle = None
        self._filepicker = None
        self._filepicker_selected_stage_path = None
        self.stage_path_model = ui.SimpleStringModel("")
        self._ui_kit_change_path = None
        self.base_folder = UIUtil.get_folder_glyph()
        self.brief_caption_model = ui.SimpleBoolModel(False)
        self.global_caption_model = ui.SimpleBoolModel(False)

    def shutdown(self):
        self.content_frame = None
        self.generate_image = None
        self.generate_character_info = None
        self.generate_environment_info = None
        self.cameras_prim_paths = None
        self.camera_combo_box = None
        self._load_stage_handle = None
        self._ui_kit_change_path = None
        self.base_folder = None
        self.stage_path_model = None
        self.brief_caption_model = None
        self.global_caption_model = None

    def _on_brief_caption_changed(self, model):
        """Callback for brief caption checkbox"""
        self._update_stage_info_manager()

    def _on_global_caption_changed(self, model):
        """Callback for global caption checkbox"""
        self._update_stage_info_manager()

    def _build_content(self):
        self.content_frame = ui.CollapsableFrame(
            title="Caption Settings",
            height=0,
            collapsed=True,
            style=get_collapsable_frame_style(),
            name="subFrame",
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )

        with self.content_frame:
            with ui.VStack(spacing=10):
                # set stage file path
                with ui.HStack(spacing=5):
                    stage_file_label = ui.Label("Stage USD Path")
                    stage_file_label.set_tooltip("Set the path of the stage USD file.")
                    stage_file_widget, self.stage_path_model = create_setting_widget(
                        ReplicatorCaptionSettings.STAGE_PATH,
                        SettingType.STRING,
                        hard_range=False,
                        alignment=ui.Alignment.LEFT_CENTER,
                    )
                    self.stage_path_model.set_value("")

                    self._ui_kit_change_path = ui.Label(
                        f"{self.base_folder}",
                        mouse_pressed_fn=lambda x, y, b, _: self._on_path_change_clicked(),
                    )

                # UI field that allow users to input target camera path
                with ui.HStack(spacing=5):
                    target_camera_label = ui.Label("Input Camera Prim Path")
                    selected_camera = ui.SimpleStringModel(
                        self.cameras_prim_paths[0]
                        if self.cameras_prim_paths is not None and self.cameras_prim_paths
                        else ""
                    )
                    carb.log_info(f"Selected camera: {selected_camera.get_value_as_string()}")
                    self.camera_combo_box = ui.ComboBox(
                        MinimalStringListModel(self.cameras_prim_paths), model=selected_camera, style={"font_size": 14}
                    )

                    def on_camera_selection_changed(model, item):
                        carb.log_info(f"Camera selection changed: {model}, {item}")
                        if hasattr(model, "_current_index"):
                            selected_index = model._current_index.get_value_as_int()
                            if selected_index >= 0 and selected_index < len(model._items):
                                selected_item = model._items[selected_index]
                                selected_path = selected_item.model.get_value_as_string()
                                # Update the setting value
                                carb.settings.get_settings().set(
                                    ReplicatorCaptionSettings.TARGET_CAMERA_PRIM_PATH, selected_path
                                )
                                carb.log_info(f"Selected camera: {selected_path}")

                    self.camera_combo_box.model.add_item_changed_fn(on_camera_selection_changed)

                # set output path
                with ui.HStack(spacing=5):
                    output_path_label = ui.Label("Output Path")
                    output_path_label.set_tooltip("Set the path of the output directory.")
                    output_path_widget, self.output_path_model = create_setting_widget(
                        ReplicatorCaptionSettings.CACHE_DATA_FOLDER,
                        SettingType.STRING,
                        hard_range=False,
                        alignment=ui.Alignment.LEFT_CENTER,
                    )
                    self.output_path_model.set_value(ReplicatorCaptionSettings.get_cache_folder_path())

                    self._ui_kit_change_output_path = ui.Label(
                        f"{self.base_folder}",
                        mouse_pressed_fn=lambda x, y, b, _: self._on_output_path_change_clicked(),
                    )

                # Add a button to refresh the camera paths
                # Add checkboxes at the top
                with ui.HStack(spacing=10):
                    brief_caption_checkbox = ui.CheckBox(
                        model=self.brief_caption_model,
                    )
                    brief_caption_checkbox.model.add_value_changed_fn(self._on_brief_caption_changed)
                    ui.Label("Brief Caption", style={"font_size": 14})
                    ui.Spacer(width=20)

                    global_caption_checkbox = ui.CheckBox(
                        model=self.global_caption_model,
                    )
                    global_caption_checkbox.model.add_value_changed_fn(self._on_global_caption_changed)
                    ui.Label("Full Caption", style={"font_size": 14})

                with ui.HStack(spacing=10):
                    self.load_scene_button = ui.Button("Load Scene", width=120, alignment=ui.Alignment.CENTER)
                    self.load_scene_button.set_tooltip("Load the scene from the stage USD file.")
                    self.load_scene_button.set_clicked_fn(self.load_scene_fn)

                    # add a button to generate scene graph with only visible object in target camera view
                    self.camera_view_only_button = ui.Button(
                        "Generate Scene Graph", width=180, alignment=ui.Alignment.CENTER
                    )
                    self.camera_view_only_button.set_tooltip(
                        "Generate the scene graph using only the objects visible within the selected camera's view."
                    )
                    self.camera_view_only_button.set_clicked_fn(self.camera_view_only_fn)

    def _on_output_path_change_clicked(self):
        """When the path of output folder get changed"""
        # Avoid opening multiple file picker (Not sure if gc will take care of it)
        if self._filepicker is not None:
            self._filepicker.hide()
            self._filepicker = None

        def on_selected(filename, path):
            if filename:  # If a file was selected instead of a folder
                carb.log_error("Please select a folder, not a file")
                return
            self.output_path_model.set_value(path)
            self._filepicker.hide()

        def filter_folder(item):
            if not item or item.is_folder:
                return True
            return False

        self._filepicker = FilePickerDialog(
            "Select Output Folder",
            allow_multi_selection=False,
            apply_button_label="Select Folder",
            click_apply_handler=lambda a, b: on_selected(a, b),
            click_cancel_handler=lambda a, b: self._filepicker.hide(),
            item_filter_fn=filter_folder,
            file_extension_options=[""],
            enable_versioning_pane=True,
        )

    def _on_path_change_clicked(self):
        """When the path of asset folder get changed"""
        if self._filepicker is None:
            self._filepicker = FilePickerDialog(
                "Select Stage USD File",
                apply_button_label="Select",
                item_filter_fn=lambda item: self._on_filepicker_filter_item(item),
                file_extension_options=[("*.usda;*.usd", "Universal Scene Description")],
                selection_changed_fn=lambda items: self._on_filepicker_selection_change(items),
                click_apply_handler=lambda filename, dirname: self._on_stage_pick(self._filepicker, filename, dirname),
            )

        self._filepicker.set_filebar_label_name("Stage USD File: ")
        self._filepicker.refresh_current_directory()
        self._filepicker.show(self.stage_path_model.get_value_as_string())

    def _on_filepicker_filter_item(self, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True
        return item.path.endswith(".usda") or item.path.endswith(".usd")

    def _on_filepicker_selection_change(self, items: [FileBrowserItem] = []):
        last_item = items[-1]
        self._filepicker_selected_stage_path = last_item.path

    def _on_stage_pick(self, dialog: FilePickerDialog, filename: str, dirname: str):
        dialog.hide()
        self.stage_path_model.set_value(self._filepicker_selected_stage_path)

    def load_scene_fn(self):
        """Load the scene from stage file"""
        stage_info_manager = StageInfoManager.get_instance()
        stage_info_manager.load_stage_from_path(self.stage_path_model.get_value_as_string())

        # Load scene done callback
        # This is done to ensure that the camera paths are updated after the scene is loaded
        # Stage loading is an async operation, so we need to wait for the stage to be loaded before updating the
        # camera paths. Otherwise, the camera paths will not be updated properly.
        def load_scene_from_stage_file_callback(event):
            if event.type == int(omni.usd.StageEventType.ASSETS_LOADED):
                # Release stage handle
                self._load_stage_handle = None
                self.cameras_prim_paths = stage_info_manager.get_cameras_prim_paths()
                self.camera_combo_box.model.set_item_children(self.cameras_prim_paths)

        # Subscribe stage event to ensure we query the camera paths after the stage is loaded
        self._load_stage_handle = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop(load_scene_from_stage_file_callback)
        )

    def camera_view_only_fn(self):
        """Generate the scene graph using only the objects visible within the selected camera's view"""

        stage_info_manager = StageInfoManager.get_instance()
        stage_info_manager.refresh_camera_path()
        self._update_stage_info_manager()

        async def update_captions():
            # Get the DataCollectionPanel instance first
            data_collection_panel = self.parent_ui
            if data_collection_panel and data_collection_panel.caption_results_panel:
                data_collection_panel.caption_results_panel.update_caption_results(None)
            await stage_info_manager.async_gather_node_info_from_camera_view()
            await stage_info_manager.async_generate_camera_scene_graph_stage()
            if data_collection_panel and data_collection_panel.caption_results_panel:
                data_collection_panel.caption_results_panel.update_caption_results(stage_info_manager.caption_results)

        asyncio.ensure_future(update_captions())

    def _update_stage_info_manager(self):
        """Update the stage info manager with current checkbox states"""
        output_folder_path = self.output_path_model.get_value_as_string()
        stage_info_manager = StageInfoManager.get_instance()
        stage_info_manager.caption_results = None
        self.output_path_model.set_value(output_folder_path)
        stage_info_manager.configs["isaacsim.replicator.caption.core"]["output_path"] = output_folder_path
        stage_info_manager.configs["isaacsim.replicator.caption.core"]["caption_configs"][
            "brief_caption"
        ] = self.brief_caption_model.get_value_as_bool()
        stage_info_manager.configs["isaacsim.replicator.caption.core"]["caption_configs"][
            "global_caption"
        ] = self.global_caption_model.get_value_as_bool()
        stage_info_manager.configs["isaacsim.replicator.caption.core"]["caption_configs"][
            "save_full_scene_graph"
        ] = self.global_caption_model.get_value_as_bool() or self.brief_caption_model.get_value_as_bool()
        stage_info_manager.configs["isaacsim.replicator.caption.core"]["caption_configs"][
            "save_pruned_scene_graph"
        ] = self.global_caption_model.get_value_as_bool() or self.brief_caption_model.get_value_as_bool()
