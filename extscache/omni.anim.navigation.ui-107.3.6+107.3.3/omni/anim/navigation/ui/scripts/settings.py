# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb.settings
import omni.ui as ui
from omni.anim.navigation.core import NavMeshSettings
from omni.kit.widget.settings import SettingType
from omni.kit.window.preferences import PreferenceBuilder
import omni.usd
from pxr import UsdGeom
from .utils import open_cache_dir, clear_cache
from . import style


class NavPathSettings:
    TRANSFORM_MOVE_MODE_SETTING = "/app/transform/moveMode"
    TRANSFORM_ROTATE_MODE_SETTING = "/app/transform/rotateMode"
    TRANSFORM_MODE_GLOBAL = "global"
    TRANSFORM_MODE_LOCAL = "local"
    TRANSFORM_OP_SETTING = "/app/transform/operation"
    TRANSFORM_OP_SELECT = "select"
    TRANSFORM_OP_MOVE = "move"
    TRANSFORM_OP_ROTATE = "rotate"
    TRANSFORM_OP_SCALE = "scale"

    MANIPULATOR_PLACEMENT_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/placement"
    MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT = "Last Prim Pivot"
    MANIPULATOR_PLACEMENT_SELECTION_CENTER = "Selection Center"
    MANIPULATOR_PLACEMENT_BBOX_CENTER = "Bounding Box Center"
    MANIPULATOR_SCALE_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/scaleMultiplier"

    FREE_ROTATION_TYPE_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/freeRotationType"
    FREE_ROTATION_TYPE_CLAMPED = "Clamped"
    FREE_ROTATION_TYPE_CONTINUOUS = "Continuous"


class NavMeshPreferencePage(PreferenceBuilder):
    SETTING_PAGE_NAME = "Navigation"

    def __init__(self):
        super().__init__(NavMeshPreferencePage.SETTING_PAGE_NAME)
        self._settings = carb.settings.get_settings()

    def destroy(self):
        self._settings = None

    def build(self):
        FLT_MAX = 3.40282e038
        UNIT_SPATIAL_STRING = "cm"
        UNIT_ANGULAR_STRING = "degrees"
        step_float = 0.1

        with ui.VStack(height=0):
            with self.add_frame("NavMesh Geometry"):
                with ui.VStack():
                    self._create_setting_widget_with_suffix(
                        "Auto-Exclude Rigid Bodies",
                        NavMeshSettings.DEFAULT_EXCLUDE_RIGID_BODIES_PATH,
                        SettingType.BOOL
                    )
            ui.Spacer(height=10)
            with self.add_frame("NavMesh Auto-Bake"):
                with ui.VStack():
                    self._create_setting_widget_with_suffix(
                        "Auto-Bake Enabled",
                        NavMeshSettings.DEFAULT_AUTO_REBAKE_SETTING_PATH,
                        SettingType.BOOL
                    )
                    self._create_setting_widget_with_suffix(
                        "Auto-Bake Delay (Seconds)",
                        NavMeshSettings.DEFAULT_AUTO_REBAKE_DELAY_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float
                    )
                    ui.Spacer()
            ui.Spacer(height=10)
            with self.add_frame("NavMesh Bake Settings"):
                with ui.VStack():
                    self._create_setting_widget_with_suffix(
                        "Agent Min Height",
                        NavMeshSettings.DEFAULT_AGENT_MIN_HEIGHT_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float,
                        suffix_text=UNIT_SPATIAL_STRING
                    ).model.set_range(0, FLT_MAX)
                    self._create_setting_widget_with_suffix(
                        "Agent Min Radius",
                        NavMeshSettings.DEFAULT_AGENT_MIN_RADIUS_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float,
                        suffix_text=UNIT_SPATIAL_STRING
                    ).model.set_range(0, FLT_MAX)
                    self._create_setting_widget_with_suffix(
                        "Agent Max Radius",
                        NavMeshSettings.DEFAULT_AGENT_MAX_RADIUS_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float,
                        suffix_text=UNIT_SPATIAL_STRING
                    ).model.set_range(0, FLT_MAX)
                    self._create_setting_widget_with_suffix(
                        "Agent Max Step Height",
                        NavMeshSettings.DEFAULT_AGENT_MAX_STEP_HEIGHT_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float,
                        suffix_text=UNIT_SPATIAL_STRING
                    ).model.set_range(0, FLT_MAX)
                    self._create_setting_widget_with_suffix(
                        "Agent Max Floor Slope",
                        NavMeshSettings.DEFAULT_AGENT_MAX_FLOOR_SLOPE_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float,
                        suffix_text=UNIT_ANGULAR_STRING
                    ).model.set_range(0, 90)
                    self._create_setting_widget_with_suffix(
                        "Agent Min Island Radius",
                        NavMeshSettings.DEFAULT_AGENT_MIN_ISLAND_RADIUS_SETTING_PATH,
                        SettingType.FLOAT,
                        step=step_float,
                        suffix_text=UNIT_SPATIAL_STRING
                    ).model.set_range(0, FLT_MAX)
                    ui.Spacer()
            ui.Spacer(height=10)
            with self.add_frame("NavMesh Visualization"):
                with ui.VStack():
                    self._create_setting_widget_with_suffix(
                        "Outline Border Only",
                        NavMeshSettings.DEFAULT_VIZ_OUTLINE_BORDER_ONLY_SETTING_PATH,
                        SettingType.BOOL
                    )
            ui.Spacer(height=10)
            with self.add_frame("NavMesh Advanced"):
                with ui.VStack():
                    self._create_setting_widget_with_suffix(
                        "Max Vertices Per Tile",
                        NavMeshSettings.MAX_VERTICES_PER_TILE_SETTING_PATH,
                        SettingType.INT,
                        range_from=0,
                        range_to=10000000
                    )
                    self._create_setting_widget_with_suffix(
                        "Cache Enabled",
                        NavMeshSettings.CACHE_ENABLED_SETTING_PATH,
                        SettingType.BOOL
                    )
                    with ui.HStack():
                        ui.Spacer(width=ui.Percent(50))
                        ui.Button("Clear Cache", clicked_fn=self._on_clear_cache_clicked, identifier="clear_cache")
                        ui.Spacer(width=20)
                        ui.Button("Open Cache Folder", clicked_fn=self._on_open_cache_dir_clicked, identifier="open_cache_folder")
                        ui.Spacer()
                    ui.Spacer()

    def _create_setting_widget_with_suffix(self, *args, suffix_text: str = None, **kwargs):
        with ui.VStack():
            with ui.ZStack():
                ret = self.create_setting_widget(*args, **kwargs)
                if suffix_text:
                    with ui.HStack(style=style.get_disabled_style()):
                        ui.Spacer()
                        ui.Label(suffix_text, width=0)
                        ui.Spacer(width=5)
            ui.Spacer(height=5)
            return ret

    def _on_clear_cache_clicked(self):
        clear_cache()

    def _on_open_cache_dir_clicked(self):
        open_cache_dir()
