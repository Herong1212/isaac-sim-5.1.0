import carb
import carb.eventdispatcher
import omni.anim.navigation.core as nav
import omni.client
import omni.timeline
import omni.ui as ui
import omni.usd
from omni.kit.window.filepicker import FilePickerDialog
from omni.metropolis.utils.config_file.core import ConfigFile
from omni.metropolis.utils.ui_util import UIConfigFileUtil, UIFolderPickerUtil, UIStyleUtil, UIUtil

from ..config_file_defines import IncidentEventSection, IncidentGlobalSection
from ..config_file_loader import ConfigFileLoader
from ..incident_manager import IncidentManager

SAVE_TEXT = "Save"
UNSAVE_TEXT = "*Save"
SAVE_AS_TEXT = "Save As"
SET_UP_INCIDENT_TEXT = "Set Up Events"
RECORD_INCIDENT_TEXT = "Record Events"
STOP_RECORD_INCIDENT_TEXT = "Stop Record"


class ConfigPanel:
    """
    UI class that manages global section and buttons.
    - It uses ConfigFileLoader for config file load/save/access.
    - It uses IncidentManager for set up incidents and reports.
    """

    def __init__(self, config_file_loader: ConfigFileLoader, incident_manager: IncidentManager):
        self._config_file_loader = config_file_loader
        self._incident_manager = incident_manager
        self._report = self._incident_manager.get_incident_report()

        self._frame = None
        self._collapsable_frame = None
        self._folder_picker_stringfield = None
        self._folder_picker_btn = None
        self._folder_picker_goto_btn = None
        self._setup_btn = None
        self._save_btn = None
        self._save_as_btn = None
        self._record_btn = None
        self._seed_field = None
        self._report_picker_string_field = None
        self._report_picker_icon = None
        self._report_picker_goto_btn = None
        self._config_changed_sub = None
        self._config_saved_sub = None

        timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            lambda e: self._on_timeline_event(e)
        )
        self._stage_sub = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop(lambda e: self._on_stage_event(e))
        )

    def destroy(self):
        self._timeline_sub.unsubscribe()
        self._timeline_sub = None

        self._stage_sub.unsubscribe()
        self._stage_sub = None

        if self._config_changed_sub:
            self._config_changed_sub.reset()
            self._config_changed_sub = None

        if self._config_saved_sub:
            self._config_saved_sub.reset()
            self._config_saved_sub = None

        self._config_file_loader = None
        self._incident_manager = None
        self._report = None

    def build_ui_frame(self):
        if not self._frame:
            self._frame = ui.Frame()
            self._collapsable_frame = ui.CollapsableFrame(
                title="Global Settings",
                height=0,
                collapsed=False,
                style=UIStyleUtil.get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn=lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(
                    collapsed, title, "${omni.metropolis.utils}/data/ui_icons/Create Menu/icoEnvironments.svg"
                ),
            )
            self.build_ui()

    def build_ui(self):
        with self._frame:
            # Config File field path and buttons
            with ui.VStack(spacing=10, height=0):
                ui.Spacer(height=5)
                self._folder_picker_stringfield, self._folder_picker_btn, self._folder_picker_goto_btn = (
                    UIFolderPickerUtil.build_folder_picker(
                        label="Config File Path",
                        dialog_title="Select A Configuration File",
                        default_val="",
                        file_extension_type=UIFolderPickerUtil.FOLDER_PICKER_TYPE.YAML,
                        on_folder_picked=self._on_config_file_picked,
                    )
                )
                self._folder_picker_stringfield.model.add_end_edit_fn(self._on_config_file_path_edited)
                with ui.HStack(spacing=10):
                    self._setup_btn = ui.Button(
                        text=SET_UP_INCIDENT_TEXT, width=180, height=30, alignment=ui.Alignment.CENTER
                    )
                    self._setup_btn.set_clicked_fn(self._on_setup_btn)
                    self._save_btn = ui.Button(text=SAVE_TEXT, width=100, height=30, alignment=ui.Alignment.CENTER)
                    self._save_btn.set_clicked_fn(self._on_save_btn)
                    self._save_as_btn = ui.Button(
                        text=SAVE_AS_TEXT, width=100, height=30, alignment=ui.Alignment.CENTER
                    )
                    self._save_as_btn.set_clicked_fn(self._on_save_as_btn)
                    self._record_btn = ui.Button(
                        text=RECORD_INCIDENT_TEXT, width=180, height=30, alignment=ui.Alignment.CENTER
                    )
                    self._record_btn.set_clicked_fn(self._on_record_btn)
                ui.Spacer(height=5)
            # Global field display
            with self._collapsable_frame:
                with ui.VStack(spacing=10, height=0):
                    with ui.HStack(alignment=ui.Alignment.CENTER):
                        ui.Label("Seed", width=UIStyleUtil.UI_DISTANCE)
                        self._seed_field = ui.IntField(width=120)
                        self._seed_field.model.add_end_edit_fn(lambda m: self._on_seed_field_edited(self._seed_field))

                    self._report_picker_string_field, self._report_picker_icon, self._report_picker_goto_btn = (
                        UIFolderPickerUtil.build_folder_picker(
                            label="Report Directory",
                            dialog_title="Select A Directory",
                            default_val="",
                            file_extension_type=UIFolderPickerUtil.FOLDER_PICKER_TYPE,
                            on_folder_picked=self._on_report_dir_picked,
                        )
                    )
                    self._report_picker_string_field.model.add_end_edit_fn(self._on_report_dir_edited)
        # Register config file related callback for UI
        self._config_changed_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=self._config_file_loader.CONFIG_FILE_CHANGED_EVENT,
            on_event=lambda c: self._on_config_file_changed(),
        )
        self._config_saved_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=self._config_file_loader.CONFIG_FILE_SAVED_EVENT, on_event=lambda c: self.update_ui()
        )
        self.update_ui()

    def update_ui(self):
        config_file = self._config_file_loader.get_config_file()
        # If no config file or no global section in the config file, disable UIs expect config file path
        if not config_file:
            self._setup_btn.enabled = False
            self._save_btn.enabled = False
            self._save_as_btn.enabled = False
            self._record_btn.enabled = False

            self._save_btn.text = SAVE_TEXT
            self._record_btn.text = RECORD_INCIDENT_TEXT

            UIConfigFileUtil.set_property_to_ui(self._seed_field, None)

            self._report_picker_icon.enabled = False
            UIConfigFileUtil.set_property_to_ui(self._report_picker_string_field, None)
        # Else display UIs with global section values
        else:
            self._setup_btn.enabled = True
            self._save_btn.enabled = True
            self._save_as_btn.enabled = True
            self._record_btn.enabled = True

            self._save_btn.text = UNSAVE_TEXT if config_file.is_dirty() else SAVE_TEXT
            self._record_btn.text = RECORD_INCIDENT_TEXT

            seed_prop = config_file.get_property(IncidentGlobalSection.name, "seed")
            UIConfigFileUtil.set_property_to_ui(self._seed_field, seed_prop)

            self._report_picker_icon.enabled = True
            report_prop = config_file.get_property(IncidentGlobalSection.name, "report_dir")
            UIConfigFileUtil.set_property_to_ui(self._report_picker_string_field, report_prop)

    def _on_config_file_modified(self):
        text = SAVE_TEXT
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        if config_file and config_file.is_dirty():
            text = UNSAVE_TEXT
        self._save_btn.text = text

    def _on_config_file_changed(self):
        """Callback when config file is changed (load another, fail loading)"""
        # First register update callback for save btn
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        if config_file:
            config_file.register_update_func(lambda _: self._on_config_file_modified())
        self._folder_picker_stringfield.model.set_value(self._config_file_loader.get_config_file_path())
        # Update UI
        self.update_ui()

    def _on_seed_field_edited(self, model):
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        seed_prop = config_file.get_property(IncidentGlobalSection.name, "seed")
        UIConfigFileUtil.set_ui_to_property(self._seed_field, seed_prop)

    def _on_config_file_path_edited(self, model):
        self._config_file_loader.load_config_file(model.get_value_as_string())

    def _on_config_file_picked(self, filename, path):
        self._config_file_loader.load_config_file(f"{path}/{filename}")

    def _on_setup_btn(self):
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        if not config_file:
            return
        seed_prop = config_file.get_property(IncidentGlobalSection.name, "seed")
        event_section = config_file.get_section(IncidentEventSection.name)

        _inav = nav.acquire_interface()
        _inav.start_navmesh_baking_and_wait()
        self._incident_manager.setup_incidents_from_config_file(seed_prop.get_resolved_value(), event_section)

    def _on_record_btn(self):
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        if not config_file:
            self._record_btn.text = RECORD_INCIDENT_TEXT
            return
        if not self._report.is_recording():
            self._start_recording()
        else:
            self._end_recording()

    def _start_recording(self):
        # Check report path first
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        report_prop = config_file.get_property(IncidentGlobalSection.name, "report_dir")
        if report_prop.is_value_error():
            carb.log_error("Unable to start record due to invalid report file.")
            self._record_btn.text = RECORD_INCIDENT_TEXT
            return
        # Start recording
        self._report.start_recording(report_prop.get_resolved_value())
        # Start timeline
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        # Record btn text
        self._record_btn.text = STOP_RECORD_INCIDENT_TEXT

    def _end_recording(self):
        # End recording
        report = self._incident_manager.get_incident_report()
        report.end_recording()
        # Stop timeline
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        # Record btn text
        self._record_btn.text = RECORD_INCIDENT_TEXT

    def _on_report_dir_picked(self, filename, path):
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        report_prop = config_file.get_property(IncidentGlobalSection.name, "report_dir")
        report_prop.set_value(path)

    def _on_report_dir_edited(self, model):
        config_file: ConfigFile = self._config_file_loader.get_config_file()
        report_prop = config_file.get_property(IncidentGlobalSection.name, "report_dir")
        report_prop.set_value(model.get_value_as_string())

    def _on_save_btn(self):
        self._config_file_loader.save_config_file()

    def _on_save_as_btn(self):

        def on_selected(filename, path):
            if not filename:
                filename = "event_config.yaml"
            save_as_path = omni.client.combine_urls(path, filename)
            self._config_file_loader.save_as_config_file(save_as_path)
            file_picker.hide()

        def on_canceled(a, b):
            file_picker.hide()

        def filter_folder(item):
            if not item or item.is_folder:
                return True
            return False

        file_picker = FilePickerDialog(
            "Select Folder to Save As",
            allow_multi_selection=False,
            apply_button_label="Select",
            click_apply_handler=lambda a, b: on_selected(a, b),
            click_cancel_handler=lambda a, b: on_canceled(a, b),
            item_filter_fn=filter_folder,
            enable_versioning_pane=True,
        )

    def _on_timeline_event(self, e: carb.events.IEvent):
        config_file = self._config_file_loader.get_config_file()
        if not config_file:
            return
        # When timeline stops, stop recording if it is still running
        if e.type == omni.timeline.TimelineEventType.STOP.value:
            if self._report.is_recording():
                self._end_recording()

    def _on_stage_event(self, e: carb.events.IEvent):
        # Reset incident manager when stage changed
        if e.type == omni.usd.StageEventType.CLOSING.value:
            self._incident_manager.reset_incident_managers()
