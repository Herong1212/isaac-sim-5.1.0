# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio

import carb
import carb.settings
import omni.anim.navigation.core as nav
import omni.ui as ui
import omni.usd
import omni.kit.ui
import omni.timeline
from omni.kit.widget.settings import SettingsWidgetBuilder, SettingType, create_setting_widget
from omni.kit.window.preferences import PreferenceBuilder, get_page_list, select_page, show_preferences_window

from . import style
from .navmesh_geometry_widget import NavMeshGeometryWidget
from .navmesh_areas_widget import NavMeshAreasWidget
from .settings import NavMeshPreferencePage, NavMeshSettings
from typing import List

# respect the order. indexing will affect the logic of the combo box
NAVMESH_PARAM_TUNE_MODE_AUTO = "Automatic"  # auto, index=0, bool: True
NAVMESH_PARAM_TUNE_MODE_CUSTOM = "Custom"  # manual, index=1, bool: False

# order maps to boolean compatible with Pinocchio bool variables: manual: False (index=0), auto: True (index=1)
navmesh_tuning_options = [NAVMESH_PARAM_TUNE_MODE_CUSTOM, NAVMESH_PARAM_TUNE_MODE_AUTO]


class NavMeshWindow(ui.Window):
    def __init__(self):
        self._visibility_changed_listener = None

        super().__init__("NavMesh", width=450, height=0, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self.set_visibility_changed_fn(self._visibility_changed_fn)
        # dock it to the same space where Layers is docked, make it the first tab and the active tab.
        self.deferred_dock_in("Property", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self._loop = asyncio.get_event_loop()
        self._inav = nav.acquire_interface()
        self._progress: float = 0.0
        self._progress_sub = self._inav.get_navmesh_event_stream().create_subscription_to_pop(
            self._on_navmesh_event
        )
        self._settings = carb.settings.get_settings()
        self._current_frame = None
        self.frame.set_build_fn(self._build_layout)
        self._auto_rebake = self._settings.get_as_bool(NavMeshSettings.AUTO_REBAKE_SETTING_PATH)
        self._auto_rebake_model = ui.SimpleBoolModel(self._auto_rebake)
        self._auto_rebake_model.add_value_changed_fn(
            self._on_auto_rebake_changed
        )
        self._auto_rebake_delay = self._settings.get_as_int(NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH)
        self._auto_rebake_delay_model = ui.SimpleStringModel(self._format_auto_rebake_delay(self._auto_rebake_delay))
        self._auto_rebake_delay_model.add_end_edit_fn(self._on_auto_rebake_delay_edit)
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )

    def destroy(self):
        self._update_property = None
        self._progress_sub = None
        super().destroy()

    def _on_timeline_event(self, e: carb.events.IEvent):
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self._auto_rebake_checkbox.enabled = False
            self._bake_button.enabled = False
            self._bake_cancel_button.enabled = False
            self._delay_field.enabled = False
        elif e.type == int(omni.timeline.TimelineEventType.STOP):
            self._auto_rebake_checkbox.enabled = True
            self._bake_button.enabled = True
            self._bake_cancel_button.enabled = True
            self._delay_field.enabled = True

    def show_current_frame(self):
        self._show_frame(self._current_frame)

    def set_visibility_changed_listener(self, listener):
        self._visibility_changed_listener = listener

    def _on_auto_rebake_delay_mouse_pressed(self):
        if not self._timeline.is_playing():
            self._auto_rebake_delay = self._auto_rebake_delay_model.get_value_as_int()
            self._auto_rebake_delay_model.set_value(f"{self._auto_rebake_delay}")

    def _on_auto_rebake_delay_edit(self, model):
        rebake_delay = self._auto_rebake_delay_model.get_value_as_int()
        if rebake_delay < 1:
            self._auto_rebake_delay = 1
        else:
            self._auto_rebake_delay = rebake_delay
        self._auto_rebake_delay_model.set_value(self._format_auto_rebake_delay(self._auto_rebake_delay))
        self._settings.set_int(NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH, self._auto_rebake_delay)

    def _format_auto_rebake_delay(self, value: int) -> str:
        if value < 2:
            return f"{value} Second"
        else:
            return f"{value} Seconds"

    def _add_setting(
        self,
        setting_type: SettingType,
        name: str,
        path: str,
        range_from=0,
        range_to=0,
        speed=1,
        has_reset=True,
        tooltip="",
        hard_range=False,
        cleartext_path=None,
        suffix_text=None,
        group_prefix=""
    ):
        the_stack = ui.HStack(skip_draw_when_clipped=True)
        # stack identifier signature: "StackType_GroupName_SettingName"
        the_stack.identifier = "HStack_" + group_prefix.replace(" ", "_") + "_" + name.replace(" ", "_")

        with the_stack:
            SettingsWidgetBuilder._create_label(name, path if not cleartext_path else cleartext_path, tooltip)

            with ui.ZStack():
                widget, model = create_setting_widget(
                    path, setting_type, range_from, range_to, speed, hard_range=hard_range
                )
                if widget is not None:
                    # stack identifier signature: "GroupName_SettingName"
                    widget.identifier = "setting_" + group_prefix.replace(" ", "_") + "_" + name.replace(" ", "_")

                if suffix_text:
                    with ui.HStack(style=style.get_disabled_style()):
                        ui.Spacer()
                        ui.Label(suffix_text, width=0)
                        ui.Spacer(width=5)

            if has_reset:
                button = SettingsWidgetBuilder._build_reset_button(path)
                model.set_reset_button(button)

        return model

    def _show_frame(self, current_frame):
        self._current_frame = current_frame
        widget_list = [
            (self._geometry_button, self._geometry_frame),
            (self._areas_button, self._areas_frame),
            (self._bake_settings_button, self._bake_settings_frame)
        ]
        for (button, frame) in widget_list:
            active = bool(frame == current_frame)
            button.selected = active
            frame.visible = active

    def _on_preferences_mouse_pressed(self, x, y, button, modifier):
        self._prefs_menu = ui.Menu()
        with self._prefs_menu:
            ui.MenuItem("Edit Preferences", triggered_fn=lambda *_: self._on_edit_preferences(), identifier="edit_preferences")
            ui.MenuItem("Restore Defaults", triggered_fn=lambda *_: self._on_restore_default(), identifier="restore_defaults")
            self._prefs_menu.show_at(
                (int)(self._prefs_button.screen_position_x) - 100,
                (int)(self._prefs_button.screen_position_y + self._prefs_button.computed_content_height)
            )

    def _on_auto_rebake_changed(self, model):
        self._auto_rebake = model.get_value_as_bool()
        self._settings.set_bool(NavMeshSettings.AUTO_REBAKE_SETTING_PATH, self._auto_rebake)
        self._auto_bake_widget.visible = self._auto_rebake
        self._manual_bake_widget.visible = not self._auto_rebake

    def _build_bake_widget(self):
        with ui.HStack(height=20, margin=5):
            ui.Spacer(width=10)
            with ui.VStack(width=20):
                ui.Spacer()
                self._auto_rebake_checkbox = ui.CheckBox(
                    self._auto_rebake_model,
                    height=0,
                    width=20,
                    identifier="auto_bake"
                )
                ui.Spacer()
            ui.Label("Auto-Bake", width=60)
            ui.Spacer(width=20)
            self._auto_bake_widget = ui.HStack(width=ui.Percent(30), visible=self._auto_rebake)
            with self._auto_bake_widget:
                ui.Label("Delay", width=20)
                ui.Spacer(width=20)
                self._delay_field = ui.StringField(self._auto_rebake_delay_model, width=200, identifier="auto_bake_delay")
                self._delay_field.set_mouse_pressed_fn(lambda x, y, b, m: self._on_auto_rebake_delay_mouse_pressed())
            self._manual_bake_widget = ui.ZStack(width=ui.Percent(30), visible=not self._auto_rebake)
            with self._manual_bake_widget:
                ui.Spacer(width=40)
                self._bake_button = ui.Button(
                    "Bake",
                    width=250,
                    height=16,
                    clicked_fn=self._on_bake_clicked,
                    identifier="start_baking"
                )
                self._progress_bar = ui.ProgressBar(visible=False, width=200)
            ui.Spacer(width=20)
            self._bake_cancel_button = ui.Button(
                "Cancel Bake",
                width=110,
                height=20,
                clicked_fn=self._on_cancel_clicked,
                identifier="cancel_baking", visible=False
            )
            ui.Spacer()

    def _build_layout(self):
        # the unit of nvmesh setting is always cm
        UNIT_SPATIAL_STRING = "cm"
        UNIT_ANGULAR_STRING = "degrees"
        FLT_MAX = 3.40282e038
        button_style = style.get_button_style()
        button_width = 120

        with self.frame:
            self._scrollframe = ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED
            )
            with self._scrollframe:
                with ui.VStack(height=25):
                    # tab buttons
                    with ui.HStack():
                        ui.Spacer()
                        self._geometry_button = ui.Button(
                            "Geometry", style=button_style, width=button_width, identifier="geometry"
                        )
                        self._areas_button = ui.Button(
                            "Areas", style=button_style, width=button_width, identifier="areas"
                        )
                        self._bake_settings_button = ui.Button(
                            "Bake Settings", style=button_style, width=button_width, identifier="bake_settings"
                        )
                        ui.Spacer()
                        self._prefs_button = ui.Button(
                            image_url="resources/glyphs/settings.svg",
                            image_width=14,
                            image_height=14,
                            width=16,
                            spacing=10,
                            mouse_pressed_fn=self._on_preferences_mouse_pressed,
                            identifier="preferences"
                        )
                        ui.Spacer(width=20)
                    ui.Spacer(height=10)
                    self._build_bake_widget()
                    ui.Spacer(height=10)

                    # geometry section
                    self._geometry_frame = ui.HStack(height=0)
                    with self._geometry_frame:
                        with ui.VStack():
                            self._geometryWidget = NavMeshGeometryWidget()

                    # areas section
                    self._areas_frame = ui.HStack(height=0)
                    with self._areas_frame:
                        self._areasWidget = NavMeshAreasWidget()

                    self._bake_settings_frame = ui.HStack(height=0)
                    with self._bake_settings_frame:
                        with ui.VStack(height=0):
                            with ui.CollapsableFrame("Settings"):
                                with ui.VStack(height=10, spacing=5):
                                    ui.Spacer(height=5)
                                    group_prefix = "NavMeshBakeSettings"
                                    self._add_setting(
                                        setting_type=SettingType.FLOAT,
                                        name="Agent Min Height",
                                        group_prefix=group_prefix,
                                        path=NavMeshSettings.AGENT_MIN_HEIGHT_SETTING_PATH,
                                        cleartext_path="Agent Min Height",
                                        tooltip="The agent minimum height in centimeters",
                                        suffix_text=UNIT_SPATIAL_STRING,
                                    ).set_range(0, FLT_MAX)
                                    self._add_setting(
                                        setting_type=SettingType.FLOAT,
                                        name="Agent Min Radius",
                                        group_prefix=group_prefix,
                                        path=NavMeshSettings.AGENT_MIN_RADIUS_SETTING_PATH,
                                        cleartext_path="Agent Min Radius",
                                        tooltip="The agent minimum radius in centimeters",
                                        suffix_text=UNIT_SPATIAL_STRING,
                                    ).set_range(0, FLT_MAX)
                                    self._add_setting(
                                        setting_type=SettingType.FLOAT,
                                        name="Agent Max Radius",
                                        group_prefix=group_prefix,
                                        path=NavMeshSettings.AGENT_MAX_RADIUS_SETTING_PATH,
                                        cleartext_path="Agent Max Radius",
                                        tooltip="The agent maximum radius in centimeters",
                                        suffix_text=UNIT_SPATIAL_STRING,
                                    ).set_range(0, FLT_MAX)
                                    self._add_setting(
                                        setting_type=SettingType.FLOAT,
                                        name="Agent Max Step Height",
                                        group_prefix=group_prefix,
                                        path=NavMeshSettings.AGENT_MAX_STEP_HEIGHT_SETTING_PATH,
                                        cleartext_path="Agent Max Step Height",
                                        tooltip="The agent radius in centimeters",
                                        suffix_text=UNIT_SPATIAL_STRING,
                                    ).set_range(0, FLT_MAX)
                                    self._add_setting(
                                        setting_type=SettingType.FLOAT,
                                        name="Agent Max Floor Slope",
                                        group_prefix=group_prefix,
                                        path=NavMeshSettings.AGENT_MAX_FLOOR_SLOPE_SETTING_PATH,
                                        cleartext_path="Agent Max Floor Slope",
                                        tooltip="The max floor slope the agent can navigate in degrees",
                                        suffix_text=UNIT_ANGULAR_STRING,
                                    ).set_range(0, 90)
                                    self._add_setting(
                                        setting_type=SettingType.FLOAT,
                                        name="Agent Min Island Radius",
                                        group_prefix=group_prefix,
                                        path=NavMeshSettings.AGENT_MIN_ISLAND_RADIUS_SETTING_PATH,
                                        cleartext_path="Agent Min Island Radius",
                                        tooltip="The agent minimum radius of the island in centimeters",
                                        suffix_text=UNIT_SPATIAL_STRING,
                                    ).set_range(0, FLT_MAX)

                                    ui.Spacer()

        self._geometry_button.set_clicked_fn(lambda *_: self._show_frame(self._geometry_frame))
        self._areas_button.set_clicked_fn(lambda *_: self._show_frame(self._areas_frame))
        self._bake_settings_button.set_clicked_fn(lambda *_: self._show_frame(self._bake_settings_frame))
        if self._current_frame is None:
            self._current_frame = self._geometry_frame
        # refresh exclusion list when building layout
        if self._geometryWidget is not None:
            self._geometryWidget._refresh_exclusion_list()

        self._show_frame(self._current_frame)

    def _visibility_changed_fn(self, visible):
        if self._visibility_changed_listener:
            self._visibility_changed_listener(visible)

    def _on_bake_clicked(self):
        self._progress = 0.0
        self._inav.start_navmesh_baking()

    def _on_cancel_clicked(self):
        self._progress = 0.0
        self._inav.cancel_navmesh_baking()

    def _on_navmesh_event(self, evt: carb.events.IEvent):
        if evt.type == int(nav.EVENT_TYPE_NAVMESH_UPDATING):
            self._progress = evt.payload['progress']
            if self._progress < 1.0:
                self._bake_button.visible = False
                self._bake_cancel_button.visible = True
                self._progress_bar.visible = True
                self._progress_bar.model.set_value(self._progress)
            else:
                self._bake_cancel_button.visible = False
                self._progress_bar.visible = False
                self._bake_button.visible = True

    def _on_edit_preferences(self):
        self._prefs_menu.hide()
        pages = get_page_list()
        omni_page = [page for page in pages if page.get_title() == NavMeshPreferencePage.SETTING_PAGE_NAME]
        if len(omni_page) == 1:

            async def show_window_and_focus():
                select_page(omni_page[0])
                show_preferences_window()
                preferenceWindow = ui.Workspace.get_window(PreferenceBuilder.WINDOW_NAME)
                if preferenceWindow:
                    preferenceWindow.focus()

            asyncio.ensure_future(show_window_and_focus())

    def _on_restore_default(self):
        self._prefs_menu.hide()
        self._settings.set(
            NavMeshSettings.EXCLUDE_RIGID_BODIES_PATH,
            self._settings.get(NavMeshSettings.DEFAULT_EXCLUDE_RIGID_BODIES_PATH),
        )
        # baking
        self._settings.set(
            NavMeshSettings.AUTO_REBAKE_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AUTO_REBAKE_SETTING_PATH)
        )
        self._auto_rebake_model.set_value(self._settings.get_as_bool(NavMeshSettings.AUTO_REBAKE_SETTING_PATH))
        self._settings.set(
            NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AUTO_REBAKE_DELAY_SETTING_PATH)
        )
        self._auto_rebake_delay = self._settings.get_as_int(NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH)
        self._auto_rebake_delay_model.set_value(self._format_auto_rebake_delay(self._auto_rebake_delay))

        # bake setttings
        self._settings.set(
            NavMeshSettings.AGENT_MIN_HEIGHT_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AGENT_MIN_HEIGHT_SETTING_PATH)
        )
        self._settings.set(
            NavMeshSettings.AGENT_MAX_RADIUS_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AGENT_MAX_RADIUS_SETTING_PATH)
        )
        self._settings.set(
            NavMeshSettings.AGENT_MAX_STEP_HEIGHT_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AGENT_MAX_STEP_HEIGHT_SETTING_PATH)
        )
        self._settings.set(
            NavMeshSettings.AGENT_MAX_FLOOR_SLOPE_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AGENT_MAX_FLOOR_SLOPE_SETTING_PATH)
        )
        self._settings.set(
            NavMeshSettings.AUTO_REBAKE_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AUTO_REBAKE_SETTING_PATH)
        )
        self._settings.set(
            NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_AUTO_REBAKE_DELAY_SETTING_PATH)
        )

        # visualization
        self._settings.set(
            NavMeshSettings.VIZ_GEOM_ENABLE_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_VIZ_GEOM_ENABLE_SETTING_PATH),
        )
        self._settings.set(
            NavMeshSettings.VIZ_SURFACE_ENABLE_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_VIZ_SURFACE_ENABLE_SETTING_PATH),
        )
        self._settings.set(
            NavMeshSettings.VIZ_OUTLINE_ENABLE_SETTING_PATH, self._settings.get(NavMeshSettings.DEFAULT_VIZ_OUTLINE_ENABLE_SETTING_PATH),
        )
        if self._current_frame == self._areas_frame:
            self._areasWidget.model.reload()

    def add_exclusion(self, prim_paths: List[str]):
        if self._geometryWidget is not None:
            self._geometryWidget.add_to_exclusion_list(prim_paths)

    def remove_exclusion(self, prim_paths: List[str]):
        if self._geometryWidget is not None:
            self._geometryWidget.remove_from_exclusion_list(prim_paths)
