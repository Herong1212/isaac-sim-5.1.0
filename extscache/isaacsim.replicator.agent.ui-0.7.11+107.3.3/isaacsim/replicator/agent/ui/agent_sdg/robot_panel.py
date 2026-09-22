import omni.ui as ui
from omni.ui import color as cl
from omni.metropolis.utils.ui_util import UIUtil
from omni.kit.widget.searchfield import SearchField
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.ui.agent_sdg.command_editor import CommandEditor
from isaacsim.replicator.agent.ui.ui_util import (
    GLOBAL_EVENTS,
    GLOBAL_VARIABLES,
    get_collapsable_frame_style,
    set_property_to_ui,
    set_ui_to_property,
    UI_DISTANCE,
    STRING_FIELD_WIDTH,
    update_navmesh_area_suggestions,
)


class RobotPanel:
    """
    Robot Panel in the AgentSDG window.
    - Display the 'robot' section in the config file format.
    - Make use of CommandSelection and CommandEditor for command displaying.
    """

    def __init__(self, events, variables):
        self._events = events
        self._variables = variables
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self.update_UI)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self.update_UI)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(self.update_UI)
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._frame = None
        self._carter_num_field = None
        self._iw_hub_num_field = None
        self._write_robot_data_cb = None
        self._command_editor = None

    def shutdown(self):
        self._command_editor.destroy()
        self._command_editor = None

    def update_UI(self):  # noqa
        self._frame.collapsed = self._sim_manager.get_config_file_section("robot") is None
        self.update_UI_enabled()
        # Robot UI fields
        set_property_to_ui(
            self._carter_num_field, self._sim_manager.get_config_file_property("robot", "nova_carter_num")
        )
        set_property_to_ui(self._iw_hub_num_field, self._sim_manager.get_config_file_property("robot", "iw_hub_num"))
        set_property_to_ui(self._write_robot_data_cb, self._sim_manager.get_config_file_property("robot", "write_data"))
        # Frame
        if self._sim_manager.get_config_file_section("robot") is not None and (
            self._carter_num_field.model.get_value_as_int() > 0 or self._iw_hub_num_field.model.get_value_as_int() > 0
        ):
            self._frame.collapsed = False
        else:
            self._frame.collapsed = True
        # Navmesh area
        set_property_to_ui(
            self._spawn_area_field, self._sim_manager.get_config_file_property("robot", "spawn_area")
        )
        set_property_to_ui(
            self._navigation_area_field, self._sim_manager.get_config_file_property("robot", "navigation_area")
        )

    def update_UI_enabled(self):
        section = self._sim_manager.get_config_file_section("robot")
        enabled = section is not None
        self._carter_num_field.enabled = enabled
        self._iw_hub_num_field.enabled = enabled
        self._write_robot_data_cb.enabled = enabled
        self._spawn_area_field.enabled = enabled
        self._navigation_area_field.enabled = enabled

    def build_ui_frame(self):
        if self._frame is None:
            self._frame = ui.CollapsableFrame(
                title="Robot",
                height=0,
                collapsed=True,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn = lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(collapsed, title,
                                                            "${omni.metropolis.utils}/data/ui_icons/Create Menu/icoRobots.svg")

            )
        self.build_ui()

    def build_ui(self):
        if self._command_editor is None:
            with self._frame:
                with ui.VStack(height=0, spacing=10):

                    UIUtil.add_separator("Robot Generation")
                    with ui.HStack():
                        ui.Label("Nova Carter Number", width=UI_DISTANCE)
                        self._carter_num_field = ui.IntField()
                        self._carter_num_field.model.add_value_changed_fn(
                            lambda m: set_ui_to_property(
                                self._carter_num_field,
                                self._sim_manager.get_config_file_property("robot", "nova_carter_num"),
                            )
                        )
                        ui.Spacer(width=50)
                        ui.Label("iw.hub Number", width=UI_DISTANCE)
                        self._iw_hub_num_field = ui.IntField()
                        self._iw_hub_num_field.model.add_value_changed_fn(
                            lambda m: set_ui_to_property(
                                self._iw_hub_num_field,
                                self._sim_manager.get_config_file_property("robot", "iw_hub_num"),
                            )
                        )
                    # Checkbox controlling
                    with ui.HStack():
                        ui.Label("Write Robot Camera Data", width=150)
                        self._write_robot_data_cb = ui.CheckBox()
                        self._write_robot_data_cb.model.add_value_changed_fn(
                            lambda m: set_ui_to_property(
                                self._write_robot_data_cb,
                                self._sim_manager.get_config_file_property("robot", "write_data"),
                            )
                        )

                    """Spawn Area and Navigation Area"""
                    with ui.HStack():
                        self._spawn_area_label = ui.Label("Spawn Area", width=UI_DISTANCE)
                        tooltip_str = (
                            "Spawn area name list.\nSupported spawn robots in specified navmesh area\n"
                        )
                        self._spawn_area_label.set_tooltip(tooltip_str)
                        self._spawn_area_field = SearchField(
                            on_search_fn=lambda m: set_ui_to_property(
                                self._spawn_area_field,
                                self._sim_manager.get_config_file_property("robot", "spawn_area"),
                            ),
                            # TODO: OMPE-44039 will allow the users to edit the hint text. Below is a workaround.
                            style={"SearchField.Hint": {"color": cl.transparent}},
                        )
                        # TODO: OMPE-44040 will allow the users to subscribe to mouse_pressed. Below is a workaround.
                        self._spawn_area_field._search_field.set_mouse_pressed_fn(
                            lambda x, y, btn, m: update_navmesh_area_suggestions(self._spawn_area_field)
                        )

                    UIUtil.add_separator("Robot Control")

                    with ui.HStack():
                        # Command modification UI
                        self.command_panel_vstack = ui.VStack(spacing=10)
                        if self._command_editor is None:
                            self._command_editor = CommandEditor(
                                self.command_panel_vstack, self._events, self._variables, agent_name="robot"
                            )

                    with ui.HStack():
                        self._navigation_area_label = ui.Label("Navigation Area", width=UI_DISTANCE)
                        tooltip_str = (
                            "Navigation area name list.\nSupported robots GoTo command to specified navmesh area\n"
                        )
                        self._navigation_area_label.set_tooltip(tooltip_str)
                        self._navigation_area_field = SearchField(
                            on_search_fn=lambda m: set_ui_to_property(
                                self._navigation_area_field,
                                self._sim_manager.get_config_file_property("robot", "navigation_area"),
                            ),
                            # TODO: OMPE-44039 will allow the users to edit this. Below is a workaround.
                            style={"SearchField.Hint": {"color": cl.transparent}},  # Hide the "search" text
                        )
                        # TODO: OMPE-44040 will allow the users to subscribe to mouse_pressed. Below is a workaround.
                        self._navigation_area_field._search_field.set_mouse_pressed_fn(
                            lambda x, y, btn, m: update_navmesh_area_suggestions(self._navigation_area_field)
                        )
