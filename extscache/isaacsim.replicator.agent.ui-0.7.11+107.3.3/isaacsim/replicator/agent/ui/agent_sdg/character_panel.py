import omni.ui as ui
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
    build_folder_picker,
    FOLDER_PICKER_TYPE,
    update_navmesh_area_suggestions,
)


class CharacterPanel:
    """
    Character Panel in the AgentSDG window.
    - Display the 'character' section in the config file format.
    - Make use of CommandSelection and CommandEditor for command displaying.
    """

    def __init__(self, events, variables):
        self._events = events
        self._variables = variables
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self.update_UI)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self.update_UI)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(self.update_UI)
        self._frame = None
        self._num_field = None
        self._filter_field = None
        self._spawn_area_field = None
        self._navigation_area_field = None
        self._command_editor = None
        self._asset_picker_field = None
        self._asset_picker_btn = None
        self._asset_picker_goto = None

    def shutdown(self):
        self._command_editor.destroy()
        self._command_editor = None

    def _on_asset_path_changed(self):
        set_ui_to_property(
            self._asset_picker_field, self._sim_manager.get_config_file_property("character", "asset_path")
        )
        # Filters should get updated when asset path changes
        self._filter_field.search_words = []

    def update_UI(self):  # noqa
        # Frame
        self._frame.collapsed = self._sim_manager.get_config_file_section("character") is None
        self.update_UI_enabled()
        # Character UI fields
        set_property_to_ui(
            self._asset_picker_field, self._sim_manager.get_config_file_property("character", "asset_path")
        )
        set_property_to_ui(self._num_field, self._sim_manager.get_config_file_property("character", "num"))
        # Filters
        set_property_to_ui(self._filter_field, self._sim_manager.get_config_file_property("character", "filters"))
        # Navmesh area
        set_property_to_ui(
            self._spawn_area_field, self._sim_manager.get_config_file_property("character", "spawn_area")
        )
        set_property_to_ui(
            self._navigation_area_field, self._sim_manager.get_config_file_property("character", "navigation_area")
        )

    def update_UI_enabled(self):  # noqa
        section = self._sim_manager.get_config_file_section("character")
        enabled = section is not None
        self._asset_picker_btn.enabled = enabled
        self._spawn_area_field.enabled = enabled
        self._filter_field.enabled = enabled
        self._navigation_area_field.enabled = enabled

    def update_filter_suggestions(self):
        labels = self._sim_manager.load_filters().keys()
        used_labels = self._filter_field.search_words
        self._filter_field.suggestions = [label for label in labels if label not in used_labels]

    def build_ui_frame(self):
        if self._frame is None:
            self._frame = ui.CollapsableFrame(
                title="Character",
                height=0,
                collapsed=False,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn = lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(collapsed, title,
                                                            "${omni.metropolis.utils}/data/ui_icons/Create Menu/icoCharacterTPoseA.svg")

            )
            self.build_ui()

    def build_ui(self):
        if self._command_editor is None:
            with self._frame:
                with ui.VStack(height=0, spacing=10):
                    UIUtil.add_separator("Character Generation")

                    # Character generation UI
                    self._asset_picker_field, self._asset_picker_btn, self._asset_picker_goto = build_folder_picker(
                        "Asset Path",
                        "Select A Characters Folder",
                        "",
                        FOLDER_PICKER_TYPE.FOLDER,
                        on_folder_picked=lambda a, b: self._on_asset_path_changed(),
                    )
                    self._asset_picker_field.model.add_end_edit_fn(lambda m: self._on_asset_path_changed())

                    """Character Number and Character Filter"""
                    with ui.HStack():
                        ui.Label("Character Number", width=UI_DISTANCE)
                        self._num_field = ui.IntField()
                        self._num_field.model.add_end_edit_fn(
                            lambda m: set_ui_to_property(
                                self._num_field, self._sim_manager.get_config_file_property("character", "num")
                            )
                        )

                    with ui.HStack():
                        ui.Label("Character Filter", width=UI_DISTANCE)
                        self._filter_field = SearchField(
                            on_search_fn=lambda m: set_ui_to_property(
                                self._filter_field, self._sim_manager.get_config_file_property("character", "filters")
                            ),
                            # TODO: OMPE-44039 will allow the users to edit the hint text. Below is a workaround.
                            style={"SearchField.Hint": {"color": ui.color.transparent}},
                        )
                        self._filter_field._search_field.set_mouse_pressed_fn(
                            lambda x, y, btn, m: self.update_filter_suggestions()
                        )

                    """Spawn Area and Navigation Area"""
                    with ui.HStack():
                        self._spawn_area_label = ui.Label("Spawn Area", width=UI_DISTANCE)
                        tooltip_str = (
                            "Spawn area name list.\nSupported spawn characters in specified navmesh area\n"
                        )
                        self._spawn_area_label.set_tooltip(tooltip_str)
                        self._spawn_area_field = SearchField(
                            on_search_fn=lambda m: set_ui_to_property(
                                self._spawn_area_field,
                                self._sim_manager.get_config_file_property("character", "spawn_area"),
                            ),
                            # TODO: OMPE-44039 will allow the users to edit the hint text. Below is a workaround.
                            style={"SearchField.Hint": {"color": ui.color.transparent}},
                        )
                        # TODO: OMPE-44040 will allow the users to subscribe to mouse_pressed. Below is a workaround.
                        self._spawn_area_field._search_field.set_mouse_pressed_fn(
                            lambda x, y, btn, m: update_navmesh_area_suggestions(self._spawn_area_field)
                        )

                    UIUtil.add_separator("Character Control")

                    with ui.HStack():
                        # Command modification UI
                        self.command_panel_vstack = ui.VStack(spacing=10)
                        if self._command_editor is None:
                            self._command_editor = CommandEditor(
                                self.command_panel_vstack, self._events, self._variables, agent_name="character"
                            )

                    with ui.HStack():
                        self._navigation_area_label = ui.Label("Navigation Area", width=UI_DISTANCE)
                        tooltip_str = (
                            "Navigation area name list.\n"
                            "Supported characters GoTo command to specified navmesh area\n"
                        )
                        self._navigation_area_label.set_tooltip(tooltip_str)
                        self._navigation_area_field = SearchField(
                            on_search_fn=lambda m: set_ui_to_property(
                                self._navigation_area_field,
                                self._sim_manager.get_config_file_property("character", "navigation_area"),
                            ),
                            # TODO: OMPE-44039 will allow the users to edit the hint text. Below is a workaround.
                            style={"SearchField.Hint": {"color": ui.color.transparent}},
                        )
                        # TODO: OMPE-44040 will allow the users to subscribe to mouse_pressed. Below is a workaround.
                        self._navigation_area_field._search_field.set_mouse_pressed_fn(
                            lambda x, y, btn, m: update_navmesh_area_suggestions(self._navigation_area_field)
                        )
