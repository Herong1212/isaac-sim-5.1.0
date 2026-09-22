import gc
import os

import carb
import omni.appwindow
import omni.ext
import omni.kit.commands
import omni.kit.ui
import omni.ui as ui
from omni.kit.commands.builtin.settings_commands import ChangeDraggableSettingCommand, ChangeSettingCommand

omni.kit.commands.command.register(ChangeSettingCommand)
omni.kit.commands.command.register(ChangeDraggableSettingCommand)

from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.widget.settings import SettingsWidgetBuilder, SettingType, create_setting_widget
from omni.kit.window.filepicker import FilePickerDialog
from isaacsim.sensors.rtx.placement.camera_calibration.camera_calibration_manager import (
    CameraCalibrationManager,
)
from isaacsim.sensors.rtx.placement.settings import CameraCalibrationSettings, GeneralSetting
from isaacsim.sensors.rtx.placement.camera_calibration.calibration_utils import (
    CalibrationDataProcessUtils,
)
from omni.metropolis.utils.ui_util import UIUtil


# NOTE:: set to default value is closed to make the further develop process more easier.
# else all the value would be reset to default value whenever you change the code.
class CameraCalibrationPanel:
    def __init__(self, view_port):
        self._frame = None
        self._filepicker = None
        self.image_path = None
        self.get_camera_button = None
        self.create_dot_button = None
        self.reset_seed_button = None
        self.view_port = view_port

    def _build_ui(self):
        with self._frame:
            with ui.VStack(spacing=20):
                with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    place_info_label = ui.Label("Place Info", width=200)
                    place_info_label.set_tooltip("Input place information")
                    place_info_setting_path = CameraCalibrationSettings.get_setting_path("place_info")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        place_widget, place_model = create_setting_widget(
                            place_info_setting_path,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                            width=400,
                        )
                    # place_model.set_value("")

                with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    scene_root_label = ui.Label("Scene Root Prim Path", width=200)
                    scene_root_label.set_tooltip(
                        "Enter the root node of the scene to calculate the top-down camera's position and rotation. This node serves as the reference point for what should the top-down camera's view include."
                    )
                    scene_bounding_box_path_setting_path = CameraCalibrationSettings.get_setting_path(
                        "scene_bounding_box_path"
                    )
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        scene_root_widget, scene_root_model = create_setting_widget(
                            scene_bounding_box_path_setting_path,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                            width=400,
                        )
                    # scene_bounding_box_model.set_value("")

                with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    floor_ceiling_height_label = ui.Label("Floor & Ceiling Height", width=200)
                    floor_ceiling_height_label.set_tooltip(
                        "Enter the floor and ceiling height of the scene, prim above the height would be clipping out from the topview camera."
                    )
                    customized_floor_height_setting_path = GeneralSetting.get_setting_path("customized_floor_height")

                    customized_ceiling_height_setting_path = GeneralSetting.get_setting_path(
                        "customized_ceiling_height"
                    )
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        floor_height_widget, floor_height_model = create_setting_widget(
                            customized_floor_height_setting_path,
                            SettingType.FLOAT,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                            width=200,
                        )
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        ceiling_height_widget, ceiling_height_model = create_setting_widget(
                            customized_ceiling_height_setting_path,
                            SettingType.FLOAT,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                            width=200,
                        )

                with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    with ui.HStack():
                        ui.Label("Top View Camera Path", width=150)
                        self.create_top_view_camera = ui.Button(
                            f"{UIUtil.get_plus_glyph()} Create", width=100, alignment=ui.Alignment.LEFT_CENTER
                        )
                        self.create_top_view_camera.set_clicked_fn(self._create_top_camera)

                        ui.Label("Path", alignment=ui.Alignment.CENTER, width=80)
                        top_view_camera_path_setting_path = CameraCalibrationSettings.get_setting_path(
                            "top_view_camera_path"
                        )
                        top_view_camera_path_widget, top_view_camera_path_model = create_setting_widget(
                            top_view_camera_path_setting_path,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.CENTER,
                            width=300,
                        )

                with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    raycast_density_label = ui.Label("Raycast Density", width=200)
                    raycast_density_label.set_tooltip(
                        "Adjust the density of raycasts emitted from the camera to visualize the Field of View (FOV). Higher values increase the number of raycasts, providing a more detailed representation."
                    )
                    raycast_seed_setting_path = CameraCalibrationSettings.get_setting_path("raycast_seed")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        raycast_seed_widget, raycast_seed_model = create_setting_widget(
                            raycast_seed_setting_path,
                            SettingType.INT,
                            range_from=0,
                            range_to=400,
                            speed=1,
                            hard_range=False,
                            width=100,
                        )

                with ui.HStack(spacing=5):
                    ui.Spacer(width=20)
                    edge_threshold_label = ui.Label("Minimum FOV Polygon Edge Length (meter)", width=200)
                    edge_threshold_label.set_tooltip(
                        "Specify the minimum length of edges in the polygon's contour. Edges shorter than this length will be ignored, and the vertices will be connected to the next point that meets this criteria."
                    )
                    ui.Spacer(width=100)
                    simplification_threshold_setting_path = CameraCalibrationSettings.get_setting_path(
                        "fov_contour_simplification_threshold"
                    )
                    contour_simplification_widget, contour_simplification_model = create_setting_widget(
                        simplification_threshold_setting_path,
                        SettingType.FLOAT,
                        range_from=0,
                        range_to=10,
                        speed=0.01,
                        hard_range=False,
                        width=200,
                        alignment=ui.Alignment.RIGHT_CENTER,
                    )

                with ui.HStack(spacing=5):
                    ui.Spacer(width=20)
                    hole_threshold_label = ui.Label("Minimum Area of FOV Polygon Hole to Ignore", width=200)
                    hole_threshold_label.set_tooltip(
                        "Specify the minimum area of holes in the FOV that should be ignored. Holes with an area smaller than this value will not be displayed."
                    )
                    ui.Spacer(width=100)
                    fov_area_filter_threshold_setting_path = CameraCalibrationSettings.get_setting_path(
                        "fov_area_filter_threshold"
                    )
                    hole_size_threshold_widget, hole_size_threshold_model = create_setting_widget(
                        fov_area_filter_threshold_setting_path,
                        SettingType.FLOAT,
                        range_from=0,
                        range_to=1000,
                        speed=0.01,
                        hard_range=False,
                        width=200,
                        alignment=ui.Alignment.RIGHT_CENTER,
                    )

                with ui.HStack(spacing=5):
                    ui.Spacer(width=20)
                    capture_camera_view_label = ui.Label("Create Camera View Images", width=200)
                    capture_camera_view_label.set_tooltip(
                        "Whether generate camera view image when generating top view image."
                    )
                    capture_camera_view_setting_path = CameraCalibrationSettings.get_setting_path(
                        "capture_camera_view_images_enabled"
                    )
                    capture_camera_view_widget, capture_camera_view_model = create_setting_widget(
                        capture_camera_view_setting_path,
                        SettingType.BOOL,
                        range_from=0,
                        range_to=0,
                        speed=0,
                        hard_range=False,
                    )

                with ui.HStack(spacing=5):
                    ui.Spacer(width=20)
                    show_fov_polygon_label = ui.Label("Show FOV Polygon", width=200)
                    show_fov_polygon_label.set_tooltip("Whether generate scene ui to show FOV polygon in the stage.")
                    show_fov_polygon_setting_path = CameraCalibrationSettings.get_setting_path(
                        "show_fov_polygon_enabled"
                    )
                    show_fov_polygon_widget, show_fov_polygon_model = create_setting_widget(
                        show_fov_polygon_setting_path,
                        SettingType.BOOL,
                        range_from=0,
                        range_to=0,
                        speed=0,
                        hard_range=False,
                    )

                with ui.HStack(spacing=5):
                    ui.Spacer(width=20)
                    output_folder_path_label = ui.Label("Output Folder Path", width=200)
                    output_folder_path_label.set_tooltip("Calibration tool would output files in this folder")
                    calibration_output_folder_path_setting_path = CameraCalibrationSettings.get_setting_path(
                        "camera_calibration_output_folder_path"
                    )
                    output_folder_widget, output_folder_model = create_setting_widget(
                        calibration_output_folder_path_setting_path,
                        SettingType.STRING,
                        range_from=0,
                        range_to=0,
                        speed=1,
                        hard_range=False,
                        width=400,
                    )
                    self.image_path = output_folder_model
                    ui.Spacer(width=10)

                    self._ui_kit_change_path = ui.Label(
                        f"{UIUtil.get_folder_glyph()}",
                        mouse_pressed_fn=lambda x, y, b, _: self._on_path_change_clicked(),
                    )

                with ui.HStack(spacing=10):
                    ui.Spacer(width=20)
                    self.create_dot_button = ui.Button("Create Dot Prims", width=200, alignment=ui.Alignment.CENTER)
                    self.generate_calibration = ui.Button(
                        "Generate Calibration File", width=200, alignment=ui.Alignment.CENTER
                    )
                    # button of generating top view image and debugging image.
                    self.generate_top_image = ui.Button(
                        "Generate Top View Image", width=200, alignment=ui.Alignment.CENTER
                    )

                    self.create_dot_button.set_clicked_fn(self._create_calibration_dot)
                    self.generate_calibration.set_clicked_fn(self._generate_calibration_info)
                    self.generate_top_image.set_clicked_fn(self._generate_top_view)

                ui.Spacer()
        return

    def build_ui_frame(self):
        if self._frame == None:
            self._frame = ui.CollapsableFrame(
                title="Camera Calibration",
                height=400,
                collapsed=False,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )
            self._build_ui()

    def _on_path_change_clicked(self):
        if self._filepicker is None:
            self._filepicker = FilePickerDialog(
                "Select Output Folder",
                apply_button_label="Select",
                item_filter_fn=lambda item: self._on_filepicker_filter_item(item),
                file_extension_options=[("*.png")],
                selection_changed_fn=lambda items: self._on_filepicker_selection_change(items),
                click_apply_handler=lambda filename, dirname: self._on_dir_pick(self._filepicker, filename, dirname),
            )
        self._filepicker.set_filebar_label_name("Command File Name: ")
        self._filepicker.refresh_current_directory()
        self._filepicker.show(self.image_path.get_value_as_string())

    def _on_filepicker_filter_item(self, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True

    def _on_filepicker_selection_change(self, items: [FileBrowserItem] = []):
        last_item = items[-1]
        self._filepicker_selected_folder = last_item.path

    def _on_dir_pick(self, dialog: FilePickerDialog, filename: str, dirname: str):
        dialog.hide()
        self.image_path.set_value(self._filepicker_selected_folder)

    def _create_top_camera(self):
        """create top view camera for the stage"""
        CameraCalibrationManager.get_instance().create_top_view_camera()

    def _create_calibration_dot(self):
        """call function to create calibration dots for each cameras"""
        CameraCalibrationManager.get_instance().generate_calibration_dot_prim()

    def _generate_top_view(self):
        """generate top view image data for the stage"""
        # check whether input camera path is valid
        if not CalibrationDataProcessUtils.check_camera_path_and_folder_path():
            carb.log_error("please provide valid camera path and folder path")
            return

        CameraCalibrationManager.get_instance().capture_camera_images()

    def _generate_calibration_info(self):
        """generate calibration information for each camera under ORA camera root prim"""
        if not CalibrationDataProcessUtils.check_camera_path_and_folder_path():
            carb.log_error("please provide valid camera path and folder path")
            return

        # check whether place info is input in a correct format
        if not CalibrationDataProcessUtils.check_place_info():
            carb.log_error("Cannot extract valid information from current Place Info")
            return

        CameraCalibrationManager.get_instance().generate_calibration()
