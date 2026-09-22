# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import re
from enum import Enum

import carb
import omni.kit.app
import omni.kit.stagerecorder.core as recorder
import omni.kit.window.content_browser as content
import omni.stageupdate
import omni.timeline
import omni.ui as ui
import omni.usd
from omni.kit.widget.prompt import PromptButtonInfo, PromptManager
from pxr import Sdf, Usd, UsdGeom, UsdSkel

from .file_picker import FileBrowserSelectionType, FilePicker
from .prim_picker_dialog import PrimPickerDialog
from .prims import *

START_RECORDING_COMMAND = "StartRecording"
STOP_RECORDING_COMMAND = "StopRecording"

RECORDER_WIDTH = 550
RECORDER_HEIGHT_EXPANDED = 785
RECORDER_HEIGHT_COLLAPSED = 510
TREEVIEW_MIN_WIDTH = 498
TREEVIEW_MIN_HEIGHT = 281

INDICATOR_REFRESH_PERIOD = 0.125
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60

# Taken from class SMPTE_Timecode
# TODO: Reconcile all SMPTE Timecode functionality into a proper utility extension
SMPTE_PATTERN = re.compile(
    "^(?:(0?[0-9]|1[0-9]|2[0-3]):)?(?:(0?[0-9]|[0-5][0-9]):)(0?[0-9]|[0-5][0-9])(?:(\:|\.|\;)([0-9]*))?$"
)


class RecordDisplay(Enum):
    TIME = 0
    FRAMES = 1


class RecordWindow(ui.Window):
    def __init__(self, ext_id, plugin):
        super().__init__(
            "Stage Recorder", width=RECORDER_WIDTH, height=RECORDER_HEIGHT_EXPANDED, raster_policy=ui.RasterPolicy.NEVER
        )
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        self._icon_path = os.path.join(ext_path, "icons")
        self._plugin = plugin

        timeline_event_stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_event_sub = timeline_event_stream.create_subscription_to_pop(
            self._on_timeline_event,
            name="record timeline event",
        )

        self._usd_context = omni.usd.get_context()
        self._stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event,
            name="record stage event",
        )

        update_event_stream = omni.kit.app.get_app().get_update_event_stream()
        self._update_event_sub = update_event_stream.create_subscription_to_pop(
            self._on_update_event,
            name="record update event",
        )

        self._file_picker = None

        self._init_var()
        self._rebuild_window()
        self._populate_frame_range()

        self.set_visibility_changed_fn(self._visiblity_changed_fn)
        self._post_do_start_callback_id = omni.kit.commands.register_callback(
            START_RECORDING_COMMAND, omni.kit.commands.POST_DO_CALLBACK, self.update_authoring_widget
        )
        self._post_do_stop_callback_id = omni.kit.commands.register_callback(
            STOP_RECORDING_COMMAND, omni.kit.commands.POST_DO_CALLBACK, self.update_authoring_widget
        )
        self._post_undo_start_callback_id = omni.kit.commands.register_callback(
            START_RECORDING_COMMAND, omni.kit.commands.POST_UNDO_CALLBACK, self.update_authoring_widget
        )
        self._stage_update = omni.stageupdate.get_stage_update_interface()
        self._stage_subscription = self._stage_update.create_stage_update_node(
            "StageRecorderWindow", on_prim_add_fn=self._on_prim_created, on_prim_remove_fn=self._on_prim_removed
        )

    def destroy(self):
        self.set_visibility_changed_fn(None)
        self._stage_subscription = None
        omni.kit.commands.unregister_callback(self._post_do_start_callback_id)
        omni.kit.commands.unregister_callback(self._post_do_stop_callback_id)
        omni.kit.commands.unregister_callback(self._post_undo_start_callback_id)
        if self._prim_list_treeview:
            self._prim_list_treeview.set_selection_changed_fn(None)
        if self._file_picker:
            self._file_picker.set_custom_fn(None, None)
        if self._prim_list_treeview:
            self._prim_list_treeview.set_hover_changed_fn(None)
        if self._folder_button:
            self._folder_button.set_clicked_fn(None)
        if self._find_button:
            self._find_button.set_clicked_fn(None)
        if self._collapsable_frame:
            self._collapsable_frame.set_collapsed_changed_fn(None)
        self.hide()
        self._timeline_event_sub = None
        self._stage_event_sub = None
        self._update_event_sub = None
        self._plugin = None
        self._destroy_prim_picker()
        super().destroy()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def _visiblity_changed_fn(self, visible):
        if not visible:
            self._hide_prim_picker()

    def _hide_prim_picker(self):
        if self._prim_picker:
            self._prim_picker.hide()

    def _destroy_prim_picker(self):
        self._hide_prim_picker()
        if self._prim_picker:
            self._prim_picker.clean()
        self._prim_picker = None

    def _init_var(self):
        # Indicator refresh counter in seconds
        self._indicator_refresh_time = 0

        # record Target
        self._prim_list = PrimListModel()
        self._prim_list_delegate = PrimListDelegate(self._icon_path)
        self._prim_list_treeview = None
        self._add_prim_button = None
        self._add_selection_button = None
        self._prim_picker = None

        # record state related
        self._record_button = None
        self._record_timecode = 0
        self._record_time_indicator = None
        self._record_display_combobox = None
        self._record_display = RecordDisplay.FRAMES

        # record range
        self._start_frame_field = None
        self._end_frame_field = None
        self._record_range_checkbox = None
        self._record_start_frame = 0
        self._record_end_frame = 0
        self._record_frame_range = False

        # pre-roll
        self._start_preroll_field = None
        self._record_preroll_checkbox = None
        self._record_preroll_frame = 0
        self._record_preroll = False

        # record take Name
        self._folder_field = None
        self._folder_button = None
        self._find_button = None
        self._takename_field = None
        self._increment_combobox = None
        self._recordto_combobox = None
        self._timemode_checkbox = None
        self._record_folder = ""
        stage = self._usd_context.get_stage()
        if stage:
            root_layer = stage.GetRootLayer()
            if root_layer and not root_layer.IsAnonymousLayerIdentifier(root_layer.identifier):
                self._record_folder = os.path.dirname(root_layer.realPath)
        self._record_take_name = ""
        self._record_increment_name = True
        self._record_recordto = recorder.RecordTo.FILE
        self._record_apply_root_anim = True

        self._root_checkbox = None
        self._record_live_mode = False
        self._max_fps_combobox = None

        self._collapsable_frame = None

    def _get_max_fps(self, index):
        fps_list = ["24.00", "29.97", "30.00", "60.00", "120.00"]
        return fps_list[index]

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self._on_stage_change()
        if event.type == int(omni.usd.StageEventType.CLOSED):
            self._on_stage_change()

    def _on_stage_change(self):
        self._record_timecode = 0
        self._plugin.stop_recording(True)
        self._prim_list.clear_all()
        self._destroy_prim_picker()
        self._update_record_name()
        self._update_record_time_mode()
        self._update_record_button()
        self._toggle_authoring_widget()
        # self._populate_frame_range()

    def _add_all_paths(self, paths):
        contains_same = False
        for path in paths:
            if self._prim_list.contains_an_equal_of(path):
                contains_same = True

        if contains_same:
            PromptManager.post_simple_prompt(
                "Prim(s) already in list",
                "Pre-existing items skipped.",
            )

        for path in paths:
            if not self._prim_list.contains_an_equal_of(path):
                self._prim_list.add_subtree(path)

    def _add_unique_paths(self, paths):
        for path in paths:
            if not self._prim_list.contains_an_equal_or_ancestors_of(path):
                self._prim_list.remove_descendants_of(path)
                self._prim_list.add_subtree(path)

    def _try_add_unique_paths(self, paths):
        paths = Sdf.Path.RemoveDescendentPaths(paths)

        contains_descendants = False
        for path in paths:
            if self._prim_list.contains_descendants_of(path):
                contains_descendants = True
                break

        if contains_descendants:
            PromptManager.post_simple_prompt(
                "Child prim(s) already in list",
                "Pre-existing items will be replaced.",
                ok_button_info=PromptButtonInfo("Confirm", lambda: self._add_unique_paths(paths)),
                cancel_button_info=PromptButtonInfo("Cancel", lambda: None),
            )
        else:
            contains_an_equal_or_ancestors = False
            for path in paths:
                if self._prim_list.contains_an_equal_or_ancestors_of(path):
                    contains_an_equal_or_ancestors = True
                    break

            if contains_an_equal_or_ancestors:
                PromptManager.post_simple_prompt(
                    "Prim(s) already in list",
                    "Pre-existing items skipped.",
                )

            self._add_unique_paths(paths)

    def _check_add_paths(self, paths):
        if self._prim_list.allow_duplicates():
            self._add_all_paths(paths)
        else:
            self._try_add_unique_paths(paths)

    def _drop_accept(self, url):
        stage = self._usd_context.get_stage()
        return url and Sdf.Path(url) and stage and stage.GetPrimAtPath(url)

    def _drop(self, event):
        paths = event.mime_data.split("\n")
        if paths:
            self._check_add_paths(paths)

    def _on_add_prim(self, prim):
        if prim:
            paths = [prim.GetPath()]
            self._check_add_paths(paths)

    def _on_add_selection(self):
        selection = self._usd_context.get_selection()
        if selection:
            paths = selection.get_selected_prim_paths()
            self._check_add_paths(paths)

    def _on_prim_selection_changed(self, items):
        self._prim_list_treeview.selection = []

    def _on_prim_created(self, path):
        self._prim_list.activate_all_for_prefix(path, True)

    def _on_prim_removed(self, path):
        self._prim_list.activate_item_by_path(path, False)

    def _update_record_frame_range(self):
        self._start_frame_field.model.set_value(self._get_record_time_string(self._record_start_frame))
        self._end_frame_field.model.set_value(self._get_record_time_string(self._record_end_frame))
        self._record_range_checkbox.model.set_value(self._record_frame_range)
        self._start_frame_field.enabled = self._record_frame_range
        self._end_frame_field.enabled = self._record_frame_range

    def _on_timeline_event(self, event):
        if event.type == int(omni.timeline.TimelineEventType.PAUSE) and self._plugin.is_recording():
            timeline = omni.timeline.get_timeline_interface()
            if not self._record_live_mode and timeline.get_current_time() == self._get_recording_end_time():
                self._stop_record()
                self._update_record_button()

    def _get_record_time_string(self, record_frame):
        nearest_frame = round(record_frame)
        if self._record_display == RecordDisplay.FRAMES:
            return f"{nearest_frame}"
        else:
            # TODO: consider caching fps
            timeline = omni.timeline.get_timeline_interface()
            fps = timeline.get_time_codes_per_seconds()
            frame = nearest_frame % fps
            div = int(nearest_frame / fps)
            second = div % SECONDS_PER_MINUTE
            div = int(div / SECONDS_PER_MINUTE)
            minute = div % MINUTES_PER_HOUR
            hour = int(div / MINUTES_PER_HOUR)
            return f"{hour:02.0f}:{minute:02.0f}:{second:02.0f}:{frame:02.0f}"

    def _parse_timecode(self, input):
        if self._record_display == RecordDisplay.FRAMES:
            return 0 if not input else int(input)
        else:
            # Taken from class SMPTE_Timecode
            # TODO: Reconcile all SMPTE Timecode functionality into a proper utility extension
            match = re.match(SMPTE_PATTERN, input)
            if not match:
                return 0
            hours_str, minutes_str, seconds_str, frame_separator, frames_str = match.groups()
            hours, minutes, seconds, frames = 0, 0, 0, 0
            if hours_str:
                hours = int(hours_str)
            if minutes_str:
                minutes = int(minutes_str)
            if seconds_str:
                seconds = int(seconds_str)
            if frames_str:
                frames = int(frames_str)

            # TODO: consider caching fps
            timeline = omni.timeline.get_timeline_interface()
            fps = timeline.get_time_codes_per_seconds()
            hour_frames = hours * MINUTES_PER_HOUR * SECONDS_PER_MINUTE * fps
            minute_frames = minutes * SECONDS_PER_MINUTE * fps
            seconds_frames = seconds * fps
            return hour_frames + minute_frames + seconds_frames + frames

    def _on_update_event(self, event):
        self._indicator_refresh_time += event.payload["dt"]
        if self._indicator_refresh_time > INDICATOR_REFRESH_PERIOD:
            self._prim_list.remove_stale_items()
            self._indicator_refresh_time = 0
            if self._plugin.is_recording():
                self._record_timecode = self._plugin.get_recording_time_code()
            self._record_time_indicator.text = self._get_record_time_string(self._record_timecode)
            if self._plugin.is_max_recording_exceeded():
                carb.log_warn("Maximum recording length exceeded. Stopping recording.")
                self._stop_and_update()
                self._indicator_refresh_time = -INDICATOR_REFRESH_PERIOD

    def _get_recording_start_time(self):
        # TODO: avoid duplication between here and _get_recording_start_frame
        # TODO: consider storing start/end in seconds not frames so that we never divide by fps, only multiply
        timeline = omni.timeline.get_timeline_interface()
        if self._record_frame_range:
            fps = timeline.get_time_codes_per_seconds()
            return self._record_start_frame / fps
        else:
            return timeline.get_start_time()

    def _get_recording_start_frame(self):
        if self._record_frame_range:
            return self._record_start_frame
        else:
            timeline = omni.timeline.get_timeline_interface()
            fps = timeline.get_time_codes_per_seconds()
            return int(fps * timeline.get_start_time())

    def _get_recording_end_time(self):
        # TODO: avoid duplication between here and _get_recording_end_frame
        # TODO: consider storing start/end in seconds not frames so that we never divide by fps, only multiply
        timeline = omni.timeline.get_timeline_interface()
        if self._record_frame_range:
            fps = timeline.get_time_codes_per_seconds()
            return self._record_end_frame / fps
        else:
            return timeline.get_end_time()

    def _get_recording_end_frame(self):
        if self._record_frame_range:
            return self._record_end_frame
        else:
            timeline = omni.timeline.get_timeline_interface()
            fps = timeline.get_time_codes_per_seconds()
            return int(fps * timeline.get_end_time())

    def _populate_frame_range(self):
        timeline = omni.timeline.get_timeline_interface()
        if timeline and timeline.get_start_time() >= 0:
            fps = timeline.get_time_codes_per_seconds()
            self._record_start_frame = fps * timeline.get_start_time()
            self._record_end_frame = fps * timeline.get_end_time()
            self._update_record_frame_range()

    def _update_record_preroll(self):
        self._start_preroll_field.model.set_value(self._get_record_time_string(self._record_preroll_frame))
        self._record_preroll_checkbox.model.set_value(self._record_preroll)
        self._start_preroll_field.enabled = self._record_preroll

    def _update_record_name(self):
        self._folder_field.model.set_value(self._record_folder)
        self._takename_field.model.set_value(self._record_take_name)
        self._increment_combobox.model.get_item_value_model().set_value(0 if self._record_increment_name else 1)
        self._recordto_combobox.model.get_item_value_model().set_value(int(self._record_recordto))
        self._root_checkbox.model.set_value(self._record_apply_root_anim)

    def _update_record_time_mode(self):
        self._timemode_checkbox.model.set_value(self._record_live_mode)

    def _update_record_button(self):
        is_recording = self._plugin.is_recording()
        if is_recording:
            self._record_button.image_url = f"{self._icon_path}/rec-lit.png"
        else:
            self._record_button.image_url = f"{self._icon_path}/rec-unlit.png"

    def update_authoring_widget(self, info):
        self._update_record_button()
        self._toggle_authoring_widget()

    def _toggle_authoring_widget(self):
        enable = not self._plugin.is_recording()
        self._record_display_combobox.enabled = enable
        self._folder_field.enabled = enable
        self._folder_button.enabled = enable
        self._find_button.enabled = enable
        self._takename_field.enabled = enable
        self._increment_combobox.enabled = enable
        self._recordto_combobox.enabled = enable
        self._root_checkbox.enabled = enable
        self._timemode_checkbox.enabled = enable
        self._start_frame_field.enabled = enable and self._record_frame_range
        self._end_frame_field.enabled = enable and self._record_frame_range
        self._record_range_checkbox.enabled = enable
        self._start_preroll_field.enabled = enable and self._record_preroll
        self._record_preroll_checkbox.enabled = enable
        self._add_prim_button.enabled = enable
        self._add_selection_button.enabled = enable
        self._max_fps_combobox.enabled = enable and self._record_live_mode

    def _on_file_selected(self, path):
        current_dir = os.path.dirname(path)
        current_filename = os.path.basename(path)
        self._folder_field.model.set_value(current_dir)
        if current_filename != "":
            self._takename_field.model.set_value(current_filename)

    def _show_file_picker(self):
        if not self._file_picker:
            self._file_picker = FilePicker(
                "Select File",
                "Select",
                FileBrowserSelectionType.ALL,
                [("^.*\\.(usd([a-z])?|abc)$", ".usd|.usda (USD Files)")],
            )
            self._file_picker.set_custom_fn(self._on_file_selected, None)

        current_directory = self._folder_field.model.get_value_as_string()
        current_filename = self._takename_field.model.get_value_as_string()
        if not os.path.exists(current_directory):
            stage = self._usd_context.get_stage()
            if stage:
                root_layer = stage.GetRootLayer()
                if root_layer and not root_layer.IsAnonymousLayerIdentifier(root_layer.identifier):
                    current_directory = os.path.dirname(root_layer.realPath)
        if os.path.exists(current_directory):
            self._file_picker.set_current_directory(current_directory)
            self._file_picker.set_current_filename(current_filename)
        self._file_picker.show_dialog()

    def _locate_file(self):
        current_directory = self._folder_field.model.get_value_as_string()
        current_filename = self._takename_field.model.get_value_as_string()
        path = os.path.join(current_directory, current_filename)
        if not os.path.exists(path):
            path = current_directory
        content.get_content_window().navigate_to(path)

    def _can_start_record(self):
        if self._prim_list.is_empty():
            return False
        # elif self._record_recordto == recorder.RecordTo.STAGE:
        #    return True
        else:
            current_directory = self._folder_field.model.get_value_as_string()
            current_filename = self._takename_field.model.get_value_as_string()
            return bool(current_directory) and bool(current_filename)

    def _start_record(self):
        self._record_timecode = self._plugin.get_recording_time_code()
        # TODO: Consider improving interop with prim list model
        if self._can_start_record():
            index = self._max_fps_combobox.model.get_item_value_model().get_value_as_int()
            timeline = omni.timeline.get_timeline_interface()
            fps = float(self._get_max_fps(index)) if self._record_live_mode else timeline.get_time_codes_per_seconds()

            time_mode = recorder.TimeMode.LIVE if self._record_live_mode else recorder.TimeMode.WORLD_TIME
            if not self._plugin.validate_recording_frame_range(
                time_mode, self._record_frame_range, self._record_start_frame, self._record_end_frame
            ):
                PromptManager.post_simple_prompt(
                    "Recording range exceeds maximum",
                    f"Please use a duration less than {self._plugin.get_max_recording_hours()} hours.",
                )
            elif not self._plugin.validate_recording_preroll(self._record_preroll, self._record_preroll_frame):
                PromptManager.post_simple_prompt(
                    "Recording pre-roll exceeds maximum",
                    f"Please use a duration less than {self._plugin.get_max_recording_hours()} hours.",
                )
            else:
                omni.kit.commands.execute(
                    START_RECORDING_COMMAND,
                    target_paths=self._prim_list.get_target_paths(),
                    live_mode=self._record_live_mode,
                    use_frame_range=self._record_frame_range,
                    start_frame=self._record_start_frame,
                    end_frame=self._record_end_frame,
                    use_preroll=self._record_preroll,
                    preroll_frame=self._record_preroll_frame,
                    record_to=self._record_recordto.name,
                    take_name=self._record_take_name,
                    record_folder=self._record_folder,
                    increment_name=self._record_increment_name,
                    apply_root_anim=self._record_apply_root_anim,
                    fps=fps,
                )

    def _stop_record(self):
        result = omni.kit.commands.execute(STOP_RECORDING_COMMAND)
        self._record_timecode = self._plugin.get_recording_time_code()
        if len(result) > 1:
            if result[1] == recorder.RecordingReturnCode.NO_CHANGES_DETECTED:
                PromptManager.post_simple_prompt(
                    "No change(s) detected",
                    "Output is empty.",
                )
            elif result[1] == recorder.RecordingReturnCode.RECORDING_OVERRIDDEN:
                PromptManager.post_simple_prompt(
                    "Output potentially overridden",
                    "The layer containing the captured data may be overridden by the current authoring layer.",
                )

    def _stop_and_update(self):
        if not self._record_live_mode:
            timeline = omni.timeline.get_timeline_interface()
            timeline.pause()
        self._stop_record()
        self._update_record_button()

    def _on_record_clicked(self):
        if self._plugin.is_recording():
            self._stop_and_update()
        else:
            timeline = omni.timeline.get_timeline_interface()
            if self._can_start_record() and not self._record_live_mode:
                # TODO: consider starting from current time instead of start time (hard to know what user would want here)
                timeline.set_current_time(self._get_recording_start_time())
                timeline.play(
                    start_timecode=self._get_recording_start_frame(),
                    end_timecode=self._get_recording_end_frame(),
                    looping=False,
                )
            self._start_record()
            self._update_record_button()

    def _rebuild_window(self):
        self._record_timecode = 0
        self.frame.clear()
        self._destroy_prim_picker()

        with self.frame:
            with ui.VStack(spacing=10):
                ui.Spacer(height=2)

                # Section 1: Prims to be recorded and start/stop recording
                with ui.ZStack():
                    # Enforce minimum dimensions using ZStack and Spacer
                    ui.Spacer(width=TREEVIEW_MIN_WIDTH, height=TREEVIEW_MIN_HEIGHT)
                    with ui.HStack(spacing=2):
                        ui.Spacer(width=20)
                        with ui.ScrollingFrame(
                            width=ui.Fraction(1),
                            height=ui.Fraction(1),
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                            style_type_name_override="TreeView",
                        ):
                            self._prim_list_treeview = ui.TreeView(
                                self._prim_list,
                                delegate=self._prim_list_delegate,
                                root_visible=False,
                                header_visible=True,
                                column_widths=self._prim_list_delegate.get_column_widths(),
                                selection_changed_fn=self._on_prim_selection_changed,
                                style={"TreeView": {"margin": 4, "background_selected_color": 0x0}},
                                name="prim_list",
                            )
                            self._prim_list_treeview.set_hover_changed_fn(
                                lambda item, hovered: item.hover_model.set_value(hovered)
                            )
                            self._prim_list_treeview.set_accept_drop_fn(self._drop_accept)
                            self._prim_list_treeview.set_drop_fn(self._drop)
                        ui.Spacer(width=20)

                with ui.VStack(height=0, spacing=10):
                    with ui.HStack(spacing=2, width=0):
                        style = {
                            "Button": {
                                "background_color": 0x0,
                                "padding": 0,
                                "margin": 0,
                            },
                        }
                        ui.Spacer(width=22)
                        with ui.VStack(height=0, spacing=5):
                            self._add_selection_button = ui.Button(
                                width=0,
                                style=style,
                                clicked_fn=lambda: self._on_add_selection(),
                                image_url=f"{self._icon_path}/add-selection.png",
                                image_width=72,
                                image_height=76,
                                name="add_selection",
                            )
                            ui.Label("Add Selection", width=72, alignment=ui.Alignment.CENTER)
                        ui.Spacer(width=5)
                        with ui.VStack(height=0, spacing=5):

                            def on_add_prim_clicked():
                                if not self._prim_picker:
                                    stage = self._usd_context.get_stage()
                                    self._prim_picker = PrimPickerDialog(
                                        stage=stage,
                                        on_select_fn=lambda prim: self._on_add_prim(prim),
                                        title="Add Prim",
                                        select_button_text="Add",
                                    )
                                self._prim_picker.show()

                            self._add_prim_button = ui.Button(
                                width=0,
                                style=style,
                                clicked_fn=lambda: on_add_prim_clicked(),
                                image_url=f"{self._icon_path}/add-prim.png",
                                image_width=72,
                                image_height=76,
                                name="add_prim",
                            )
                            ui.Label("Add Prim", width=72, alignment=ui.Alignment.CENTER)
                        ui.Spacer(width=215)
                        with ui.VStack(height=0):
                            with ui.HStack(spacing=5):
                                ui.Spacer(width=15)
                                self._record_button = ui.Button(
                                    width=0,
                                    style=style,
                                    clicked_fn=lambda: self._on_record_clicked(),
                                    image_width=80,
                                    image_height=80,
                                    name="rec",
                                )
                                self._update_record_button()
                            with ui.HStack():
                                self._record_time_indicator = ui.Label(
                                    "0",
                                    width=90,
                                    style={"font_size": 22},
                                    alignment=ui.Alignment.RIGHT,
                                    name="record_time",
                                )
                                style = {
                                    "ComboBox": {
                                        "background_color": 0xFF454545,
                                    },
                                }
                                self._record_display_combobox = ui.ComboBox(
                                    1,
                                    "Display In Time",
                                    "Display In Frames",
                                    width=0,
                                    style=style,
                                    tooltip="Toggle display units",
                                    name="display_units",
                                )

                    ui.Spacer(height=3)

                with ui.HStack(spacing=5):
                    ui.Spacer(width=20)

                    def build_checked_header(collapsed, title):
                        triangle_alignment = ui.Alignment.RIGHT_CENTER
                        triangle_width = 6
                        triangle_height = 12
                        if not collapsed:
                            triangle_alignment = ui.Alignment.CENTER_BOTTOM
                            triangle_width = 12
                            triangle_height = 7

                        with ui.HStack(style={"HStack": {"margin_width": 15, "margin_height": 5}}):
                            with ui.VStack(width=20):
                                ui.Spacer()
                                ui.Triangle(
                                    alignment=triangle_alignment,
                                    width=triangle_width,
                                    height=triangle_height,
                                    style={"background_color": 0xFF888888},
                                )
                                ui.Spacer()

                            ui.Label(title, style={"color": 0xFF888888}, width=140)
                            ui.Line(style={"color": 0xFF888888}, width=335)

                    style = {
                        "CollapsableFrame": {
                            "background_color": 0x0,
                            "secondary_color": 0x0,
                            "padding": 0,
                            "margin": 0,
                        },
                    }

                    self._collapsable_frame = ui.CollapsableFrame(
                        "RECORDING OPTIONS", style=style, build_header_fn=build_checked_header
                    )

                    def on_collapsed_changed(collapsed):
                        # TODO: Consider a better way (see Damien/Victor)
                        self.height = RECORDER_HEIGHT_COLLAPSED if collapsed else RECORDER_HEIGHT_EXPANDED

                    self._collapsable_frame.set_collapsed_changed_fn(on_collapsed_changed)

                    with self._collapsable_frame:
                        with ui.VStack(height=0, spacing=10):

                            ui.Spacer(height=1)

                            # Section 2: Where to record to
                            with ui.HStack(spacing=5):
                                ui.Label("Take Name", width=70)
                                ui.Spacer(width=10)
                                self._takename_field = ui.StringField(
                                    width=280,
                                    name="take_name",
                                    tooltip="Name for the recorded data (.usd assumed)",
                                )
                                ui.Spacer(width=2)
                                self._increment_combobox = ui.ComboBox(
                                    0,
                                    "Multi-Take",
                                    "Overwrite File",
                                    width=113,
                                    tooltip="Multi-Take will append a sequence number to the file name.",
                                    name="increment",
                                )

                            with ui.HStack(spacing=5):
                                ui.Label("Record to", width=70)
                                ui.Spacer(width=10)
                                self._recordto_combobox = ui.ComboBox(
                                    0,
                                    "File",
                                    "New Layer",
                                    width=405,
                                    tooltip="Send to file/layer using specified take name and folder path.",
                                    name="recordto",
                                )

                            with ui.HStack(spacing=5):
                                ui.Label("Path", width=70)
                                ui.Spacer(width=10)
                                self._folder_field = ui.StringField(name="record_folder", width=354, height=20)
                                with ui.HStack(spacing=0):
                                    style = {
                                        "image_url": f"{self._icon_path}/small_folder.png",
                                        "Button": {"background_color": 0x0},
                                    }
                                    self._folder_button = ui.Button(
                                        style=style,
                                        width=0,
                                        image_width=14,
                                        image_height=12,
                                        tooltip="Select recording folder",
                                    )
                                    style = {
                                        "image_url": f"{self._icon_path}/find.png",
                                        "Button": {"background_color": 0x0},
                                    }
                                    self._find_button = ui.Button(
                                        style=style, width=0, image_width=14, image_height=12, tooltip="Locate folder"
                                    )

                            with ui.HStack(spacing=5, width=0):
                                ui.Label("Custom Range", width=110, alignment=ui.Alignment.TOP)
                                self._record_range_checkbox = ui.CheckBox(width=10, name="use_custom_range")
                                ui.Spacer(width=101)
                                ui.Label("Start", width=30)
                                self._start_frame_field = ui.StringField(width=87, name="custom_range_start")
                                ui.Spacer(width=5)
                                ui.Label("End", width=25)
                                self._end_frame_field = ui.StringField(width=87, name="custom_range_end")
                                ui.Spacer(width=5)
                                self._update_record_frame_range()

                                def _start_frame_changed(model):
                                    self._record_start_frame = self._parse_timecode(model.as_string)

                                self._start_frame_field.model.add_value_changed_fn(_start_frame_changed)

                                def _end_frame_changed(model):
                                    self._record_end_frame = self._parse_timecode(model.as_string)

                                self._end_frame_field.model.add_value_changed_fn(_end_frame_changed)

                                def _record_frame_changed(model):
                                    self._record_frame_range = model.as_bool
                                    self._start_frame_field.enabled = self._record_frame_range
                                    self._end_frame_field.enabled = self._record_frame_range

                                self._record_range_checkbox.model.add_value_changed_fn(_record_frame_changed)

                            with ui.HStack(spacing=5, width=0):
                                ui.Label("Add Pre-Roll", width=110, alignment=ui.Alignment.TOP)
                                self._record_preroll_checkbox = ui.CheckBox(width=10, name="use_pre_roll")
                                ui.Spacer(width=101)
                                ui.Label("Start", width=30)
                                self._start_preroll_field = ui.StringField(width=87, name="pre_roll_start")
                                self._update_record_preroll()

                                def _preroll_frame_changed(model):
                                    self._record_preroll_frame = self._parse_timecode(model.as_string)

                                self._start_preroll_field.model.add_value_changed_fn(_preroll_frame_changed)

                                def _record_preroll_changed(model):
                                    self._record_preroll = model.as_bool
                                    self._start_preroll_field.enabled = self._record_preroll

                                self._record_preroll_checkbox.model.add_value_changed_fn(_record_preroll_changed)

                            ui.Spacer(height=2)

                            with ui.HStack(spacing=5):
                                ui.Line(style={"color": 0xFF888888}, width=495)

                            ui.Spacer(height=5)

                            # Section 3: Settings for when recording
                            with ui.HStack(spacing=5):
                                ui.Label("Live Mode", width=205)
                                self._timemode_checkbox = ui.CheckBox(
                                    width=10,
                                    name="live_mode",
                                    tooltip="Live mode records any changes made by the user (e.g. moving a Prim).",
                                )
                                ui.Spacer(width=88)
                                ui.Label("Max FPS", width=56)
                                self._max_fps_combobox = ui.ComboBox(
                                    1,
                                    self._get_max_fps(0),
                                    self._get_max_fps(1),
                                    self._get_max_fps(2),
                                    self._get_max_fps(3),
                                    self._get_max_fps(4),
                                    width=112,
                                    tooltip="Maximum capture rate for Live Mode.",
                                    style={"ComboBox:disabled": {"color": 0xFF444444}},
                                    name="max_fps",
                                )
                                self._max_fps_combobox.enabled = self._record_live_mode

                            with ui.HStack(spacing=5):
                                ui.Label("Bake Root Motion (USDSkel only)", width=205)
                                self._root_checkbox = ui.CheckBox(
                                    width=10,
                                    name="bake_root_motion",
                                    tooltip="Only record skelanimation, convert related xform animation to root joint pose, and discard anything unrelated.",
                                )

                            ui.Spacer(height=10)

                self._update_record_name()
                self._update_record_time_mode()

                def record_display_change(item_model, notsure):
                    value = item_model.get_item_value_model().get_value_as_int()
                    self._record_display = RecordDisplay(value)
                    self._update_record_frame_range()
                    self._update_record_preroll()

                self._record_display_combobox.model.add_item_changed_fn(record_display_change)

                def folder_changed(model):
                    self._record_folder = model.as_string

                self._folder_field.model.add_value_changed_fn(folder_changed)

                def takename_change(model):
                    self._record_take_name = model.as_string

                self._takename_field.model.add_value_changed_fn(takename_change)
                self._folder_button.set_clicked_fn(self._show_file_picker)
                self._find_button.set_clicked_fn(self._locate_file)

                def increment_change(item_model, notsure):
                    # 0: Multi-Take, 1: Overwrite File
                    # TODO: Fix this!
                    value = item_model.get_item_value_model().get_value_as_int()
                    self._record_increment_name = value == 0

                self._increment_combobox.model.add_item_changed_fn(increment_change)

                def recordto_change(item_model, notsure):
                    value = item_model.get_item_value_model().get_value_as_int()
                    self._record_recordto = recorder.RecordTo(value)

                self._recordto_combobox.model.add_item_changed_fn(recordto_change)

                def root_change(model):
                    self._record_apply_root_anim = model.as_bool

                self._root_checkbox.model.add_value_changed_fn(root_change)

                def timemode_change(model):
                    self._record_live_mode = model.as_bool
                    self._max_fps_combobox.enabled = self._record_live_mode

                self._timemode_checkbox.model.add_value_changed_fn(timemode_change)
