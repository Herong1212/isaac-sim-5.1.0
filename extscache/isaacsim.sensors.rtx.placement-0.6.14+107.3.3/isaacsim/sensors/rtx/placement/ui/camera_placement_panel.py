import gc
import os

import carb
import omni.appwindow
import omni.ext
import omni.kit.commands
import omni.kit.ui
import omni.ui as ui
from omni.kit.commands.builtin.settings_commands import ChangeDraggableSettingCommand, ChangeSettingCommand
from omni.kit.widget.settings import SettingsWidgetBuilder, SettingType, create_setting_widget

omni.kit.commands.command.register(ChangeSettingCommand)
omni.kit.commands.command.register(ChangeDraggableSettingCommand)
from isaacsim.sensors.rtx.placement.settings import CameraPlacementSettings, GeneralSetting

from ..camera_placement.visualize_camera_placement import (
    show_all_selected_camera_coverage,
    clean_the_stage,
)
from isaacsim.sensors.rtx.placement.camera_placement.camera_placement_manager import (
    CameraPlacementManager,
)


# NOTE:: set to default value is closed to make the further develop process more easier.
# else all the value would be reset to default value whenever you change the code.
class CameraPlacementPanel:
    def __init__(self):
        self._frame = None
        self.generate_camera_placement = None
        self.show_coverage = None
        self.hide_visualization = None
        self._pruning_setting_collapsed = True
        self.x_min_widget = None
        self.x_max_widget = None
        self.y_min_widget = None
        self.y_max_widget = None

    def _build_ui(self):
        with self._frame:
            with ui.VStack(spacing=10):
                ui.Spacer(height=5)
                with ui.HStack(height=15, spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    camera_info_payload_label = ui.Label(
                        "Camera Placement Output Path", width=200, height=ui.Percent(1)
                    )
                    camera_info_payload_label.set_tooltip("Camera information would be store in this folder")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        camera_placement_output_folder_setting_path = CameraPlacementSettings.get_setting_path(
                            "camera_placement_output_folder_path"
                        )
                        camera_placement_output_widget, camera_placement_output_model = create_setting_widget(
                            camera_placement_output_folder_setting_path,
                            SettingType.STRING,
                            hard_range=False,
                            width=400,
                            height=ui.Percent(1),
                        )

                with ui.HStack(height=15, spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Spacer(width=20)
                    total_camera_label = ui.Label("Total Camera Number", width=200, height=ui.Percent(1))

                    total_camera_label.set_tooltip(
                        "Set the ideal total camera number when Required Camera Number is defined. Set negative value to deactivate this setting"
                    )
                    total_camera_number_setting_path = CameraPlacementSettings.get_setting_path("total_camera_number")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        total_camera_widget, total_camera_model = create_setting_widget(
                            total_camera_number_setting_path,
                            SettingType.INT,
                            hard_range=False,
                            width=100,
                            height=ui.Percent(1),
                        )

                def on_pruning_setting_collapse_changed(collapse: bool):
                    self._pruning_setting_collapsed = collapse

                basic_writer_collapse_frame = ui.CollapsableFrame(
                    "More", collapsed=self._pruning_setting_collapsed, height=15
                )
                basic_writer_collapse_frame.set_collapsed_changed_fn(on_pruning_setting_collapse_changed)

                with basic_writer_collapse_frame:
                    with ui.VStack(spacing=5):
                        with ui.HStack(height=10, spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Label("Camera Range Parameters", width=120, style={"color": 0xFF808080})
                            ui.Line(style={"color": 0xFF808080})

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            camera_height_range_label = ui.Label("Camera Height Range", width=200)
                            camera_height_range_label.set_tooltip("The range of the camera height.")
                            min_camera_height_setting_path = CameraPlacementSettings.get_setting_path(
                                "min_camera_height"
                            )
                            max_camera_height_setting_path = CameraPlacementSettings.get_setting_path(
                                "max_camera_height"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                min_camera_height_widget, min_camera_height_model = create_setting_widget(
                                    min_camera_height_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )
                                max_camera_height_widget, max_camera_height_model = create_setting_widget(
                                    max_camera_height_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            camera_distance_range_label = ui.Label("Camera Distance Range", width=200)
                            camera_distance_range_label.set_tooltip("The range of the camera distance.")
                            min_camera_distance_setting_path = CameraPlacementSettings.get_setting_path(
                                "min_camera_distance"
                            )
                            max_camera_distance_setting_path = CameraPlacementSettings.get_setting_path(
                                "max_camera_distance"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                min_camera_distance_widget, min_camera_distance_model = create_setting_widget(
                                    min_camera_distance_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )
                                max_camera_distance_widget, max_camera_distance_model = create_setting_widget(
                                    max_camera_distance_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            camera_look_down_angle_range_label = ui.Label("Camera Look Down Angle Range", width=200)
                            camera_look_down_angle_range_label.set_tooltip("The range of the camera look down angle.")
                            min_camera_look_down_angle_setting_path = CameraPlacementSettings.get_setting_path(
                                "min_camera_look_down_angle"
                            )
                            max_camera_look_down_angle_setting_path = CameraPlacementSettings.get_setting_path(
                                "max_camera_look_down_angle"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                (
                                    min_camera_look_down_angle_widget,
                                    min_camera_look_down_angle_model,
                                ) = create_setting_widget(
                                    min_camera_look_down_angle_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )
                                (
                                    max_camera_look_down_angle_widget,
                                    max_camera_look_down_angle_model,
                                ) = create_setting_widget(
                                    max_camera_look_down_angle_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )
                        with ui.HStack(height=10, spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Label("Stage Processing Parameters ", width=120, style={"color": 0xFF808080})
                            ui.Line(style={"color": 0xFF808080})

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            patch_size_label = ui.Label("Patch Size", width=200)
                            patch_size_label.set_tooltip("Determine the accuracy of the camera fov estimation")
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                patch_size_setting_path = CameraPlacementSettings.get_setting_path("patch_size")
                                patch_size_widget, patch_size_model = create_setting_widget(
                                    patch_size_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    alignment=ui.Alignment.LEFT_CENTER,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            patch_size_label = ui.Label("Ground Height", width=200)
                            patch_size_label.set_tooltip("The height of the ground")
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                ground_height_setting_path = GeneralSetting.get_setting_path("customized_floor_height")
                                ground_height_widget, ground_height_model = create_setting_widget(
                                    ground_height_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    alignment=ui.Alignment.LEFT_CENTER,
                                    width=100,
                                )
                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            patch_size_label = ui.Label("Stage Scope", width=200)
                            patch_size_label.set_tooltip("The scope of the ground on x and y axis, this value would be used only when navmesh is not available")
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                ground_height_setting_path = GeneralSetting.get_setting_path("customized_floor_height")
                                with ui.VStack(spacing=5):
                                    with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                                        ui.Label("X scope", width=100)
                                        self.x_min_widget = ui.FloatField(width=100, height=30)
                                        self.x_min_widget.model.set_value(0)
                                        self.x_max_widget = ui.FloatField(width=100, height=30)
                                        self.x_max_widget.model.set_value(0)
                                    with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                                        ui.Label("Y scope", width=100)
                                        self.y_min_widget = ui.FloatField(width=100, height=30)
                                        self.y_min_widget.model.set_value(0)
                                        self.y_max_widget = ui.FloatField(width=100, height=30)
                                        self.y_max_widget.model.set_value(0)

                        with ui.HStack(height=10, spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Label("Other Tuning Parameters", width=120, style={"color": 0xFF808080})
                            ui.Line(style={"color": 0xFF808080})

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            border_checking_index_label = ui.Label("Border Checking Index", width=200)
                            border_checking_index_label.set_tooltip("Index that control border checking")
                            border_checking_index_setting_path = CameraPlacementSettings.get_setting_path(
                                "border_checking_index"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                border_checking_index_widget, border_checking_index_model = create_setting_widget(
                                    border_checking_index_setting_path,
                                    SettingType.FLOAT,
                                    range_from=0,
                                    range_to=1,
                                    speed=0.01,
                                    hard_range=False,
                                    alignment=ui.Alignment.LEFT_CENTER,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            camera_on_navmesh_label = ui.Label("Camera On Navmesh", width=200)
                            camera_on_navmesh_label.set_tooltip("Does the camera need to be placed on navmesh.")
                            camera_on_navmesh_setting_path = CameraPlacementSettings.get_setting_path(
                                "camera_on_navmesh"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                camera_on_navmesh_widget, camera_on_navmesh_model = create_setting_widget(
                                    camera_on_navmesh_setting_path,
                                    SettingType.BOOL,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            min_coverage_increase_label = ui.Label("Minimum Coverage Increase", width=200)
                            min_coverage_increase_label.set_tooltip(
                                "Stop the camera generation if the coverage increment is smaller than this value. "
                            )
                            min_coverage_increase_setting_path = CameraPlacementSettings.get_setting_path(
                                "min_coverage_increase"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                min_coverage_increase_widget, min_coverage_increase_model = create_setting_widget(
                                    min_coverage_increase_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            min_view_distance_label = ui.Label("Minimum View Distance", width=200)
                            min_view_distance_label.set_tooltip(
                                "Stop the camera generation if the view distance is smaller than this value. "
                            )
                            min_view_distance_setting_path = CameraPlacementSettings.get_setting_path(
                                "min_view_distance"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                min_view_distance_widget, min_view_distance_model = create_setting_widget(
                                    min_view_distance_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            limit_fov_by_distance_label = ui.Label("Limit Fov by Distance", width=200)
                            limit_fov_by_distance_label.set_tooltip("Apply distance scope check when placing camera.")
                            limit_fov_by_distance_setting_path = CameraPlacementSettings.get_setting_path(
                                "limit_fov_by_distance"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                limit_fov_by_distance_widget, limit_fov_by_distance_model = create_setting_widget(
                                    limit_fov_by_distance_setting_path,
                                    SettingType.BOOL,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            coverage_density_label = ui.Label("Coverage Density", width=200)
                            coverage_density_label.set_tooltip(
                                "The least number of camera that coverage any point in the stage"
                            )
                            required_camera_per_patch_setting_path = CameraPlacementSettings.get_setting_path(
                                "required_camera_per_patch"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                (
                                    required_camera_per_patch_widget,
                                    required_camera_per_patch_model,
                                ) = create_setting_widget(
                                    required_camera_per_patch_setting_path,
                                    SettingType.INT,
                                    hard_range=False,
                                    width=100,
                                )

                        with ui.HStack(spacing=5, alignment=ui.Alignment.CENTER):
                            ui.Spacer(width=20)
                            target_coverage_ratio_label = ui.Label("Target Coverage Ratio", width=200)
                            target_coverage_ratio_label.set_tooltip(
                                " Fully coverage ratio of the accessible section in the stage."
                            )
                            target_coverage_ratio_setting_path = CameraPlacementSettings.get_setting_path(
                                "target_coverage_ratio"
                            )
                            with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                                target_coverage_ratio_widget, target_coverage_ratio_model = create_setting_widget(
                                    target_coverage_ratio_setting_path,
                                    SettingType.FLOAT,
                                    hard_range=False,
                                    width=100,
                                )

                with ui.HStack(height=15, spacing=5, alignment=ui.Alignment.CENTER):
                    self.generate_camera_placement = ui.Button("Place Cameras", width=200, alignment=ui.Alignment.LEFT)

                with ui.HStack(height=10, spacing=5, alignment=ui.Alignment.CENTER):
                    ui.Label("Visualization", width=120, style={"color": 0xFF808080})
                    ui.Line(style={"color": 0xFF808080})

                with ui.HStack(height=15, spacing=5, alignment=ui.Alignment.CENTER):

                    self.show_coverage = ui.Button(
                        "Show Selected Camera Coverage", width=250, alignment=ui.Alignment.CENTER
                    )
                    # button of generating top view image and debugging image.
                    self.generate_camera_placement.set_clicked_fn(self.start_camera_placement_fn)
                    self.show_coverage.set_tooltip("Show all selected cameras's fov in the stage. ")
                    self.show_coverage.set_clicked_fn(self.show_coverage_fn)
                    self.hide_visualization = ui.Button("Hide Coverage", width=200, alignment=ui.Alignment.CENTER)
                    self.hide_visualization.set_clicked_fn(self.hide_visualization_fn)

                ui.Spacer()
        return

    def build_ui_frame(self):
        if self._frame == None:
            self._frame = ui.CollapsableFrame(
                title="Camera Placement",
                height=20,
                collapsed=False,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )
            self._build_ui()

    def start_camera_placement_fn(self):
        """generate camera placement"""
        camera_placement_manager = CameraPlacementManager.get_instance()

        camera_placement_manager.place_camera_in_target_scope(target_scope=self.collect_stage_scope())

    def show_coverage_fn(self):
        """generate coverage fn"""

        show_all_selected_camera_coverage(target_scope=self.collect_stage_scope())

    def hide_visualization_fn(self):
        """generate clicked fn"""
        clean_the_stage()

    def collect_stage_scope(self):
        """collect the stage scope"""
        x_min = float(self.x_min_widget.model.get_value_as_float())
        x_max = float(self.x_max_widget.model.get_value_as_float())
        y_min = float(self.y_min_widget.model.get_value_as_float())
        y_max = float(self.y_max_widget.model.get_value_as_float())
        return [(x_min, x_max), (y_min, y_max)]
