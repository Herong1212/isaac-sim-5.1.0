# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import __main__
import carb
import omni.ui as ui
import omni.usd
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.widget.settings import SettingsWidgetBuilder, SettingType, create_setting_widget
from omni.kit.window.filepicker import FilePickerDialog

from ..settings import ReplicatorCaptionSettings

COLOR_BLACK = 0x0
BOUNDING_RADIUS = 1.5
UI_DISTANCE = 120
STRING_FIELD_WIDTH = 300


def get_collapsable_frame_style():
    return {
        "border_radius": BOUNDING_RADIUS * 2,
        "border_color": COLOR_BLACK,
        "border_width": 1,
        "padding": 6,
    }


class SelectAssetFolderPanel:
    """This is the panel that setting the stage info root folder"""

    def __init__(self):
        """initialize the buttons and frames"""
        self.parent_ui = None
        self.stage_info_folder_path_model = None
        self._ui_kit_change_path = None
        self.content_frame = None
        self._filepicker = None
        self.base_folder = omni.kit.ui.get_custom_glyph_code("${glyphs}/folder.svg")
        self.set_info_folder_button = None

    def shutdown(self):
        self.content_frame.clear()
        self.content_frame = None
        self.base_folder = None

    # def _build_content(self):
    #     """build the file picker and contents"""
    #     self.content_frame = ui.CollapsableFrame(
    #         title="Select Asset folder to add Caption",
    #         height=0,
    #         collapsed=True,
    #         style=get_collapsable_frame_style(),
    #         name="subFrame",
    #         horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
    #         vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
    #     )

    #     with self.content_frame:
    #         with ui.VStack(spacing=10):
    #             with ui.HStack(spacing=5):
    #                 ui.Label("Props Folder")
    #                 with ui.HStack(alignment=ui.Alignment.LEFT_CENTER, spacing=5):
    #                     default_dir = ""
    #                     # use the setting widget, so that the ui would get changed once the information are change in the setting value
    #                     output_widget, stage_info_root_folder_model = create_setting_widget(
    #                         ReplicatorCaptionSettings.STAGE_INFO_ROOT_PATH,
    #                         SettingType.STRING,
    #                         range_from=0,
    #                         range_to=0,
    #                         speed=1,
    #                         hard_range=False,
    #                     )

    #                     self.stage_info_folder_path_model = stage_info_root_folder_model

    #                     self._ui_kit_change_path = ui.Label(
    #                         f"{self.base_folder}",
    #                         mouse_pressed_fn=lambda x, y, b, _: self._on_path_change_clicked(),
    #                     )

    #                     # self.stage_info_folder_path_model.set_value("")

    #             ##TODO::this button is a debug button. I need to register an event to monitor the change of our output root folder setting
    #             self.set_info_folder_button = ui.Button("Select Asset Folder", width=200, aligment=ui.Alignment.RIGHT)
    #             self.set_info_folder_button.set_clicked_fn(self._change_asset_folders)

    # NOTE:: change asset folder
    def _change_asset_folders(self):
        """change the output root folder when user click the "load button"."""
        current_target_asset_folder_path = ReplicatorCaptionSettings.get_props_folder_path()
        carb.log_warn(
            "Message :: Isaac Replicator Caption's target asset folder has been changed to {target_folder}".format(
                target_folder=str(current_target_asset_folder_path)
            )
        )
        # please feel free to add any function triggered by this event.
        pass

    def _on_path_change_clicked(self):
        """When the path of asset folder get changed"""
        if self._filepicker is None:
            self._filepicker = FilePickerDialog(
                "Select Target Asset Folder",
                apply_button_label="Select",
                item_filter_fn=lambda item: self._on_filepicker_filter_item(item),
                file_extension_options=[("*.png")],
                selection_changed_fn=lambda items: self._on_filepicker_selection_change(items),
                click_apply_handler=lambda filename, dirname: self._on_dir_pick(self._filepicker, filename, dirname),
            )

        self._filepicker.set_filebar_label_name("Asset Folder: ")
        self._filepicker.refresh_current_directory()
        self._filepicker.show(self.stage_info_folder_path_model.get_value_as_string())

    def _on_filepicker_filter_item(self, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True
        # return item.path.endswith(".yaml")

    def _on_filepicker_selection_change(self, items: [FileBrowserItem] = []):
        last_item = items[-1]
        self._filepicker_selected_folder = last_item.path

    def _on_dir_pick(self, dialog: FilePickerDialog, filename: str, dirname: str):
        dialog.hide()
        self.stage_info_folder_path_model.set_value(self._filepicker_selected_folder)

    def _load_config_file(self, items: [FileBrowserItem] = []):
        last_item = items[-1]
        self._filepicker_selected_folder = last_item.path
