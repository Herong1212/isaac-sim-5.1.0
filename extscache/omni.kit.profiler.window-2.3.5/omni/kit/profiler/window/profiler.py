# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import concurrent.futures
import cProfile
import datetime
import importlib
import os
import threading
import time
from functools import lru_cache

import carb
import carb.profiler
import carb.settings
import carb.tokens
import omni.ext
import omni.kit.actions.core
import omni.kit.app
import omni.kit.menu.utils
import omni.ui as ui
from carb.input import KeyboardInput as Key
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.viewport.utility import get_active_viewport

try:
    from omni.kit.widget.settings import SettingType, create_setting_widget
    from omni.kit.widget.settings.settings_model import SettingModel
except:
    from omni.kit.settings import create_setting_widget, SettingType

import os

from pxr import Trace

from . import logger
from .capture_browser import CaptureBrowserWindow, TraceFile, is_external_build
from .profiler_utils import (
    create_label_checkbox,
    create_label_drag,
    create_label_slider,
    export_trace_to_nvdf,
    profile_startup,
)
from .style import PROFILER_WINDOW_STYLE

WINDOW_NAME = "Profiler"
PROFILER_MENU_GROUP = "Profiler"
PROFILER_START_MENU = "Start\\Stop"
PROFILER_STARTUP_MENU = "Profile Startup (Restart)"

_extension_instance = None


def _get_ts():
    return datetime.datetime.now().isoformat(timespec="seconds").replace(":", "-")


class PythonProfiler:
    def __init__(self):
        self.enabled = False
        self.checkbox = None



class Profiler(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._window = None
        self._capture_browser_window = None
        self._button_live_update = None
        self._liveUpdate = True
        self._sort_by_time = False
        self._cpu_profiler_enabled = False
        self._cpu_profiler_autoenabled = False
        self._python_carb_profiler = PythonProfiler()
        self._python_cprofile = PythonProfiler()
        self._pxr_profiler_enabled = False
        self._profiler = None
        self._cprof = None
        self._profiler_gpu_names = None
        self._profiler_gpu_durations = None
        self._profiler_gpu_perfsdk_metrics = None
        self._progress_gpu_column = None
        self._progress_gpu_bars = []
        self._profiler_cpu_names = None
        self._profiler_cpu_durations = None
        self._progress_cpu_column = None
        self._progress_gpu_column_child_count = 0
        self._progress_cpu_column_child_count = 0
        self._progress_cpu_bars = []
        self._memStat = None
        self._gpu_index = 0
        self._max_gpu_indent = 2
        self._max_cpu_indent = 3
        self._min_duration_ms = 0.0
        self._cached_cpu_nodes = []
        self._cached_gpu_nodes = []
        self._average_timings = True
        self._averaging_period_secs = 1
        self._refresh_frame_count = 0
        self._ui_frame_count = 0
        self._memStat_enabled = True
        self._memStat_detail = False
        self._memStat_sort = False
        self._memStat_names = None
        self._memStat_sizes = None
        self._profiler_cpu = None
        self._capture_btn = None
        self._profile_monitor = None
        self._drag_gpu_index = None
        self._button_enable_tracy = None
        self._write_to_file_time = None
        self._tracy_present = False
        self._start_profiler = False
        self._prev_perfsdk_realtime_enabled = False
        self._perfsdk_realtime_enabled = False
        self._perfsdk_realtime_names = []
        self._menu_entry = []
        self._profiler_menu_entry = []
        self._settings = carb.settings.get_settings()
         # ui update times per second
        self._ui_update_rate = 5
        self._viewport_api = None
        self._engine_stats = None
        self._app = omni.kit.app.get_app_interface()
        self._update_sub = None
        self.__show_action_name = "show_profiler_window"
        self.__action_profiler = "profiler_start_stop"
        self.__action_profiler_startup = "profiler_startup"
        tokens = carb.tokens.get_tokens_interface()
        self._capture_trace_path = tokens.resolve(self._settings.get("/exts/omni.kit.profiler.window/capturePath"))
        if not os.path.exists(self._capture_trace_path):
            os.makedirs(self._capture_trace_path)

        self._capturing_until = 0
        try:
            self._profile_monitor = carb.profiler.acquire_profile_monitor_interface()
            self._profiler_cpu = carb.profiler.acquire_profiler_interface(plugin_name="carb.profiler-cpu.plugin")
            self._cpu_profiler_enabled = self._profiler_cpu.get_capture_mask() != 0
        except RuntimeError as e:
            logger.warning("RuntimeError %s", e)

        if self._settings:
            mask = self._settings.get_as_int("/app/profilerMask")
            if mask < 0:
                # since get_as_int() returns a signed value, and set_capture_mask() requires an unsigned value, and the
                # default value is all bits set (which python interprets as -1), we convert to a positive number here.
                mask = mask + 0x010000000000000000
            self._enabled_capture_mask = mask

            # Normally, these two defaults are set from C++ side. However, the change that included the defaults is after
            # 104.0. We set default to these two to ensure backward compatible with 104.0.
            self._settings.set_default("/profiler/perfsdkRealtimeMetrics/enabled", False)
            self._settings.set_default("/profiler/perfsdkReportGenerator/enabled", False)
        else:
            self._enabled_capture_mask = 0x0FFFFFFFFFFFFFFFF

    @lru_cache()
    def _late_init_once(self):
        # Only do it when we open window or press F5
        self._toggle_cpu_profiler(False)

    def on_startup(self, ext_id):
        self.__ext_id = ext_id

        omni.kit.actions.core.get_action_registry().register_action(
            self.__ext_id,
            self.__show_action_name,
            self._toggle_window,
            display_name=self.__show_action_name,
            description=self.__show_action_name,
            tag=self.__show_action_name,
        )
        # setup menu
        self._menu_entry = [
            MenuItemDescription(
                name=WINDOW_NAME,
                ticked=False,  # menu item is ticked
                ticked_fn=self._is_visible,  # gets called when the menu needs to get the state of the ticked menu
                appear_after="Render Settings",
                onclick_action=(ext_id, self.__show_action_name),
                hotkey=(0, Key.F8),
            )
        ]
        omni.kit.menu.utils.add_menu_items(self._menu_entry, name="Window")

        # Start/Stop menu and hotkey
        if not is_external_build():
            omni.kit.actions.core.get_action_registry().register_action(
                self.__ext_id,
                self.__action_profiler,
                lambda profiling=self._start_profiler: self._toggle_profiler(not profiling),
                display_name=self.__action_profiler,
                description=self.__action_profiler,
                tag=self.__action_profiler,
            )

            self._profiler_menu_entry = [
                MenuItemDescription(
                    name=PROFILER_START_MENU,
                    ticked=False,  # menu item is ticked
                    ticked_fn=lambda: self._capturing_until > 0,
                    onclick_action=(ext_id, self.__action_profiler),
                    hotkey=(0, Key.F5),
                )
            ]

            if self._settings.get("/exts/omni.kit.profiler.window/showProfileStartupMenu"):
                omni.kit.actions.core.get_action_registry().register_action(
                    self.__ext_id,
                    self.__action_profiler_startup,
                    lambda *args: profile_startup(self._capture_trace_path),
                    display_name=self.__action_profiler_startup,
                    description=self.__action_profiler_startup,
                    tag=self.__action_profiler_startup,
                )
                self._profiler_menu_entry.append(
                    MenuItemDescription(
                        name=PROFILER_STARTUP_MENU,
                        onclick_action=(ext_id, self.__action_profiler_startup),
                    )
                )
            omni.kit.menu.utils.add_menu_items(self._profiler_menu_entry, PROFILER_MENU_GROUP)
        global _extension_instance
        _extension_instance = self

    def _toggle_profiler(self, start):
        self._late_init_once()
        self._start_profiler = start
        if start:
            # Useful defaults: Tracy, 60 seconds autostop
            self._try_enable_tracy()
            if self._window and not self._window.visible:
                self._write_to_file_time.model.set_value(60)
        self._toggle_capture()

    def show_window(self, visible):
        if not self._window:
            if not visible:
                return
            window_flags = ui.WINDOW_FLAGS_NO_DOCKING
            self._window = ui.Window(WINDOW_NAME, width=800, height=600, flags=window_flags)
            self._window.frame.set_build_fn(self._build_profiler_ui)
            self._window.frame.set_style(PROFILER_WINDOW_STYLE)

        if visible:
            self._late_init_once()
        self._window.visible = visible

    def _toggle_window(self):
        if self._window and self._window.visible:
            self.show_window(False)
        else:
            self.show_window(True)

    def _is_visible(self):
        if self._window:
            return self._window.visible
        return False

    def _get_engine_stats(self):
        # If there is a Viewport attached, get the stats from its UsdContext and HydraEngine.
        if self._viewport_api is not None:
            usd_context_name, hydra_engine = self._viewport_api.usd_context_name, self._viewport_api.hydra_engine
        else:
            usd_context_name, hydra_engine = "", ""
        return omni.hydra.engine.stats.HydraEngineStats(usd_context_name, hydra_engine)

    def _try_enable_tracy(self):
        if is_external_build():
            return
        manager = omni.kit.app.get_app().get_extension_manager()
        if not manager.is_extension_enabled("omni.kit.profiler.tracy"):
            manager.set_extension_enabled_immediate("omni.kit.profiler.tracy", True)

        try:
            self._module_profiler_tracy = importlib.import_module("omni.kit.profiler.tracy")
            self._tracy_present = True

            if self._button_enable_tracy:
                self._button_enable_tracy.text = "Launch Tracy"
                self._button_enable_tracy.set_clicked_fn(lambda: self._module_profiler_tracy.launch_tracy())

        except ImportError:
            self._tracy_present = False

    def _on_late_startup(self):
        self._viewport_api = get_active_viewport()
        self._engine_stats = self._get_engine_stats()

    def on_shutdown(self):
        self._window = None
        if self._capture_browser_window:
            self._capture_browser_window.destroy()
            self._capture_browser_window = None
        self.memory_toggle = None
        self._update_sub = None

        # destroy action
        omni.kit.actions.core.get_action_registry().deregister_action(self.__ext_id, self.__show_action_name)
        omni.kit.actions.core.get_action_registry().deregister_action(self.__ext_id, self.__action_profiler)
        omni.kit.actions.core.get_action_registry().deregister_action(self.__ext_id, self.__action_profiler_startup)

        # destroy menu
        omni.kit.menu.utils.remove_menu_items(self._menu_entry, name="Window")
        omni.kit.menu.utils.remove_menu_items(self._profiler_menu_entry, PROFILER_MENU_GROUP)
        self._menu_entry = None
        self._profiler_menu_entry = None
        global _extension_instance
        _extension_instance = None

    def _has_perfsdk_functionality(self):
        if not self._engine_stats:
            self._engine_stats = self._get_engine_stats()
        if self._engine_stats is not None:
            return hasattr(self._engine_stats, "get_perfsdk_node_keys")
        return False

    def _get_perfsdk_node_keys(self):
        if not self._engine_stats:
            self._engine_stats = self._get_engine_stats()
        if hasattr(self._engine_stats, "get_available_perfsdk_node_keys"):
            return self._engine_stats.get_available_perfsdk_node_keys()
        if hasattr(self._engine_stats, "get_perfsdk_node_keys"):
            return self._engine_stats.get_perfsdk_node_keys()
        return []

    def _build_profiler_ui(self):
        with ui.VStack():
            self._build_profiler_enabled()
            self._build_trace_capture()
            self._build_gpu_profiler()
            self._build_profiler_depth()
            self._build_gpu_metrics()
            self._build_pixar_trace_enable()
            self._build_profiler_detail()
            self._build_memory_stat_control()
            self._build_memory_stat_header()
            self._build_memory_stat_detail()
        if not self._update_sub:
            self._update_sub = self._app.get_update_event_stream().create_subscription_to_pop(
                self._on_update, name="omni.kit.profiler.window progress"
            )

    def _build_profiler_enabled(self):
        with ui.HStack(height=0):
            self._cpu_profiler_cb = create_label_checkbox(
                "CPU Profiler",
                self._cpu_profiler_enabled,
                change_fn=None,
                tooltip="Enables/disables the CPU profiler (if available)",
            )
            self._cpu_profiler_cb.model.add_value_changed_fn(
                lambda model: self._toggle_cpu_profiler(model.get_value_as_bool())
            )

            def _refresh_python_profilers():
                self._python_carb_profiler.checkbox.enabled = not self._python_cprofile.enabled
                self._python_cprofile.checkbox.enabled = not self._python_carb_profiler.enabled

            def _on_python_carb_profiler_changed(model):
                self._python_carb_profiler.enabled = model.get_value_as_bool()
                _refresh_python_profilers()

            ui.Spacer(width=13)
            cb = create_label_checkbox(
                "Profile Python (carb.profiler)",
                self._python_carb_profiler.enabled,
                _on_python_carb_profiler_changed,
                "Enables/disables profiling python code with carb.profiler (slow)",
            )
            self._python_carb_profiler.checkbox = cb

            def _on_python_cprofile_profiler_changed(model):
                self._python_cprofile.enabled = model.get_value_as_bool()
                self._refresh_capture_btn()
                _refresh_python_profilers()

            ui.Spacer(width=13)
            cb = create_label_checkbox(
                "Profile Python (cProfile)",
                self._python_cprofile.enabled,
                _on_python_cprofile_profiler_changed,
                "Enables/disables profiling python code with python's cProfile",
            )
            self._python_cprofile.checkbox = cb

    def _build_trace_capture(self):
        with ui.HStack(height=0):
            # CPU Trace Capture Row
            if (
                self._settings.get_as_bool("/plugins/carb.profiler-cpu.plugin/saveProfile")
                and self._profiler_cpu is not None
            ):
                self._capturing_until = -1  # infinite

            self._write_to_file_time = create_label_slider(
                "Capture time (sec)",
                1,
                300,
                "The amount of time to capture a CPU profiler for",
            )
            self._write_to_file_time.model.set_value(3)
            ui.Spacer(width=8)
            self._capture_btn = ui.Button(
                "Capture",
                height=18,
                width=85,
                clicked_fn=lambda: self._toggle_capture(),
            )
            self._refresh_capture_btn()
            ui.Spacer(width=12)
            # Capture Browser button
            button_capture_browser = ui.Button(
                "Browse",
                height=18,
                width=85,
                clicked_fn=lambda: self._on_open_capture_browser(),
            )
            ui.Spacer(width=12)
            if not is_external_build():
                self._button_enable_tracy = ui.Button(
                    "Enable Tracy",
                    height=18,
                    width=85,
                    clicked_fn=lambda: self._try_enable_tracy(),
                )
        ui.Separator(height=0)

    def _build_gpu_profiler(self):
        with ui.HStack(height=0):
            # GPU Profiler Row
            model = SettingModel("/profiler/enabled")
            profiler_toggle = create_label_checkbox(
                "GPU Profiler",
                enabled=None,
                tooltip="Enables/disables the GPU profiler (if available)",
                model=model,
            )
            ui.Spacer(width=12)
            checkBox_sort = create_label_checkbox(
                "Sort by Time",
                self._sort_by_time,
                self._on_sort_fn,
                "Sort the GPU profiler by time",
            )
            ui.Spacer(width=12)
            drag_min_duration = create_label_drag(
                "Min Time (ms)",
                ui.FloatDrag,
                0,
                100.0,
                0.001,
                "Minimum time to display in the GPU profiler",
            )
            drag_min_duration.model.set_value(self._min_duration_ms)
            drag_min_duration.model.add_value_changed_fn(self._on_min_duration_fn)
            ui.Spacer(width=5)
            button_print_log = ui.Button(
                "Save to Logs",
                width=85,
                height=18,
                clicked_fn=self._on_print_log,
            )

    def _build_profiler_depth(self):
        with ui.HStack(height=0):
            # GPU Profiler Row (cont.)
            # Pause / Unpause button
            self._button_live_update = ui.Button(
                "Pause Updates",
                width=80,
                clicked_fn=lambda: self._on_live_update(),
            )
            ui.Spacer(width=12)

            drag_gpu_max_indent = create_label_drag(
                "GPU Depth",
                ui.IntDrag,
                0,
                16,
                1,
                "Maximum depth of the GPU profiler",
            )
            drag_gpu_max_indent.model.set_value(self._max_gpu_indent)
            drag_gpu_max_indent.model.add_value_changed_fn(self._on_max_gpu_indent_fn)

            drag_max_indent = create_label_drag(
                "CPU Depth",
                ui.IntDrag,
                0,
                16,
                1,
                "Maximum depth of the CPU profiler",
            )
            drag_max_indent.model.set_value(self._max_cpu_indent)
            drag_max_indent.model.add_value_changed_fn(self._on_max_cpu_indent_fn)

            self._drag_gpu_index = create_label_drag(
                "GPU",
                ui.IntDrag,
                0,
                15,
                1,
                "GPU index to profile",
            )
            self._drag_gpu_index.model.set_value(self._gpu_index)
            self._drag_gpu_index.model.add_value_changed_fn(self._on_gpu_index_fn)
            ui.Spacer(width=5)

            drag_averaging_period = create_label_drag(
                "Avg Timings (secs, enable)",
                ui.FloatDrag,
                0,
                10.0,
                0.001,
                "Averaging period for timings",
            )
            drag_averaging_period.model.set_value(self._averaging_period_secs)
            drag_averaging_period.model.add_value_changed_fn(self._on_averaging_period_fn)

            checkBox_average = create_label_checkbox(
                "",
                self._average_timings,
                self._on_average_timings_fn,
                "",
            )

    def _build_gpu_metrics(self):
        with ui.HStack(height=0):
            # PerfSdk realtime enable
            perfsdk_model = SettingModel("/profiler/perfsdkRealtimeMetrics/enabled")
            perfsdk_realtime = create_label_checkbox(
                "Show GPU Metrics",
                perfsdk_model.get_value_as_bool(),
                None,
                "Enables/disables PerfSDK profiler for displaying statistics of hard-to-detect bottlenecks such as PCIe",
            )
            perfsdk_realtime.model = perfsdk_model
            perfsdk_model.add_value_changed_fn(self._on_perfsdk_realtime_changed)

            ui.Spacer(width=4)
            perfsdk_realtime_interval_model = SettingModel(
                "/profiler/perfsdkRealtimeMetrics/samplingIntervalInMs", draggable=True
            )
            perfsdk_realtime_interval_ms = create_label_drag(
                "GPU Metrics Sample Interval (ms)",
                ui.FloatDrag,
                0.1,
                10000.0,
                0.001,
                "Adjust PerfSDK profiler sample interval",
            )
            perfsdk_realtime_interval_ms.model = perfsdk_realtime_interval_model
            perfsdk_realtime_interval_ms.tooltip = (
                "Adjust PerfSDK profiler sample interval.\n"
                "A sample interval that is too large will lead to imprecise results, while a sample interval\n"
                "that is too small may cause missing results due to a buffer overflow from too many samples.\n"
                "A good starting point is 0.1%% of frame time."
            )
            ui.Spacer(width=4)
            # PerfSdk report generator
            perfsdk_report_generator_model = SettingModel("/profiler/perfsdkReportGenerator/enabled")
            perfsdk_report_generator = create_label_checkbox(
                "Generate PerfSdk GPU Metrics report",
                perfsdk_report_generator_model.get_value_as_bool(),
                None,
                "Enables/disables generation of a report containing GPU counter values every certain number of frames",
            )
            perfsdk_report_generator.model = perfsdk_report_generator_model
            perfsdk_report_generator.tooltip = "Enables/disables generation of a report containing GPU counter values every certain number of frames. (if available)"

    def _build_pixar_trace_enable(self):
        with ui.HStack(height=0):
            # Pixar Trace Profiler
            tooltip = "Enables/disables the Pixar Trace profiler (prints to console and writes to pxr-trace.json)"
            self._pxr_profiler = create_label_checkbox(
                "Pixar Trace Profiler",
                self._pxr_profiler_enabled,
                self._on_pxr_profiler_changed,
                tooltip=tooltip,
            )

            tooltip = "UI update times per second"
            drag_ui_update_rate = create_label_drag(
                "UI update rate(sec)",
                ui.IntDrag,
                1,
                60,
                1,
                "UI update times per second",
            )
            drag_ui_update_rate.model.set_value(self._ui_update_rate)
            drag_ui_update_rate.model.add_value_changed_fn(self._on_ui_update_rate_fn)
        ui.Separator(height=0)

    def _build_profiler_header(self):
        with ui.HStack(height=0):
            # gpu columns consist of Name, Duraction (ms), Percentage, PerfSdk statistics
            gpu_columns_count = 3

            if self._perfsdk_realtime_enabled:
                self._perfsdk_realtime_names = self._get_perfsdk_node_keys()
                gpu_columns_count = gpu_columns_count + len(self._perfsdk_realtime_names)

            # timestamp and perfsdk header
            ui.Label("Name", width=90)
            ui.Spacer()
            if self._perfsdk_realtime_enabled:
                for perfsdk_metric_name in self._perfsdk_realtime_names:
                    ui.Label(perfsdk_metric_name, width=90)
            ui.Label("Duration (ms)", width=90)
            ui.Label("Percentage", width=90)
        ui.Separator(height=0)

    def _build_profiler_detail(self):
        with ui.VStack(height=0):
            self._build_profiler_header()
            self._build_gpu_detail()
            self._build_cpu_detail()

    def _build_color_label(self):
        return ui.Label("", width=90, style_type_name_override="Label.Green")

    def _build_gpu_detail(self):
        with ui.HStack(height=0):
            self._profiler_gpu_names = self._build_color_label()
            ui.Spacer()
            self._profiler_gpu_perfsdk_metrics = []
            if self._perfsdk_realtime_enabled:
                for perfsdk_metric_name in self._perfsdk_realtime_names:
                    perfsdk_metric_label = self._build_color_label()
                    self._profiler_gpu_perfsdk_metrics.append(perfsdk_metric_label)

            self._profiler_gpu_durations = self._build_color_label()
            self._progress_gpu_column = ui.VStack(spacing=0, width=90)

    def _build_cpu_detail(self):
        with ui.HStack(height=0):
            self._profiler_cpu_names = self._build_color_label()
            ui.Spacer()
            self._profiler_cpu_durations = self._build_color_label()
            self._progress_cpu_column = ui.VStack(spacing=0, width=90)
        ui.Separator(height=0)

    def _build_memory_stat_control(self):
        with ui.HStack(height=0):
            # Memory usage stat control
            self.memory_toggle = create_label_checkbox(
                "Memory Stats",
                self._memStat_enabled,
                self._on_memStats_toggle_fn,
                "Enables/disables the memory stats",
            )
            ui.Spacer(width=13)
            checkBox_detailedMemoryStats = create_label_checkbox(
                "Detailed Stats",
                self._memStat_detail,
                self._on_memStatsDetail_fn,
                "Enables/disables detailed memory stats",
            )
            ui.Spacer(width=13)
            checkBox_sortMemoryStats = create_label_checkbox(
                "Sort By Size",
                self._memStat_sort,
                self._on_memStatsSort_fn,
                "Sort memory stats by size",
            )

    def _build_memory_stat_header(self):
        with ui.HStack(height=0):
            # Memory usage stat header
            ui.Label("Memory Category", width=90)
            ui.Spacer()
            ui.Label("Size (MB)", width=90)
        ui.Separator(height=0)

    def _build_memory_stat_detail(self):
        with ui.HStack(height=0):
            # Memory usage stat detail
            self._memStat_names = self._build_color_label()
            ui.Spacer()
            self._memStat_sizes = self._build_color_label()

    def _build_progress_bars_gpu_ui(self, count):
        self._progress_gpu_column.clear()
        self._progress_gpu_bars = []
        self._progress_gpu_column_child_count = count
        progress_height = 12
        with self._progress_gpu_column:
            for i in range(count):
                progress_bar = ui.ProgressBar(width=ui.Pixel(60), height=ui.Pixel(progress_height))
                progress_bar.model.set_value(0.0)
                self._progress_gpu_bars.append(progress_bar)

    def _build_progress_bars_cpu_ui(self, count):
        self._progress_cpu_column.clear()
        self._progress_cpu_bars = []
        self._progress_cpu_column_child_count = count
        progress_height = 12  # self._profiler_cpu_names.get_font_size() - self._progress_cpu_column.child_spacing.y
        with self._progress_cpu_column:
            for i in range(count):
                progress_bar = ui.ProgressBar(width=ui.Pixel(60), height=ui.Pixel(progress_height))
                progress_bar.model.set_value(0.0)
                self._progress_cpu_bars.append(progress_bar)

    def _refresh_capture_btn(self):
        if not self._capture_btn:
            return
        self._capture_btn.enabled = (
            self._profiler_cpu is not None and self._cpu_profiler_enabled or self._python_cprofile.enabled
        )
        if self._capturing_until != 0:
            self._capture_btn.text = "Stop"
            self._capture_btn.tooltip = "Capturing until stopped"
        else:
            self._capture_btn.text = "Capture (F5)"
            self._capture_btn.tooltip = "Press to start capturing"

    def _refresh_capture_menu(self):
        if self._profiler_menu_entry:
            omni.kit.menu.utils.refresh_menu_items(PROFILER_MENU_GROUP)

    def _toggle_cpu_profiler(self, enabled):
        # enabled = model.get_value_as_bool()
        self._cpu_profiler_enabled = enabled
        self._refresh_capture_btn()
        if self._profiler_cpu is None:
            # OMPE-37601: if kit startup with "--/app/profilerBackend=tracy, the profiler cpu will not be initialized
            logger.warning("Profiler CPU is not initialized")
            return
        self._settings.set_bool("/plugins/carb.profiler-cpu.plugin/saveProfile", False)
        if enabled:
            self._profiler_cpu.set_capture_mask(self._enabled_capture_mask)
        else:
            self._profiler_cpu.set_capture_mask(0)

    def _write_pxr_trace_thread(self, f):
        # Slow blocking calls happen in another thread
        Trace.Reporter.globalReporter.ReportChromeTracingToFile("pxr-trace.json")  # chrome tracing report
        f.set_result(True)

    async def _write_pxr_trace_task(self):
        f = concurrent.futures.Future()

        # Create a background thread for the slow stuff
        thread = threading.Thread(target=self._write_pxr_trace_thread, args=(f,))
        thread.start()

        # Wait for the thread to finish
        await asyncio.wrap_future(f)

        # fix up the UI: enable the check box
        # OM-23538 TODO: UI feedback, e.g., popup window
        logger.info("Finshed writing pxr-trace.json")
        self._pxr_profiler.enabled = True

    def _on_perfsdk_realtime_changed(self, model):
        self._perfsdk_realtime_enabled = model.get_value_as_bool() and self._has_perfsdk_functionality()

    def _on_perfsdk_realtime_sampling_interval_changed(self, interval):
        self._settings.set_float("/profiler/perfsdkRealtimeMetrics/samplingIntervalInMs", interval)

    def _on_pxr_profiler_changed(self, model):
        enabled = model.get_value_as_bool()
        if enabled == self._pxr_profiler_enabled:
            return
        self._pxr_profiler_enabled = enabled
        if enabled:
            Trace.Reporter.globalReporter.ClearTree()
            Trace.Collector().enabled = True
        else:
            Trace.Collector().enabled = False
            Trace.Reporter.globalReporter.Report()  # aggregate report

            self._pxr_profiler.enabled = False

            # OM-23538 TODO: UI feedback, e.g., popup window
            logger.info("Writing to pxr-trace.json...")

            # For now, output aggregate report to terminal.
            # Longer-term, we can also draw a separate treeview for the aggregated report,
            # as well as offer an option to output aggregate or Chrome Tracing reports to files.
            asyncio.ensure_future(self._write_pxr_trace_task())

    def _on_ui_update_rate_fn(self, model):
        self._ui_update_rate = model.get_value_as_int()

    def _stop_capturing(self):
        self._capturing_until = 0
        self._settings.set("exts/omni.kit.profile_python/enable", False)
        self._settings.set_bool("/plugins/carb.profiler-cpu.plugin/saveProfile", False)
        self._refresh_capture_btn()
        self._refresh_capture_menu()

        file_path = self._settings.get("plugins/carb.profiler-cpu.plugin/filePath")

        if self._cpu_profiler_enabled:
            asyncio.ensure_future(self._export_trace(file_path))

        last_captures = []
        if self._cpu_profiler_enabled:
            last_captures.append(file_path)

        if self._cprof:
            self._cprof.disable()
            self._cprof.dump_stats(self._cprof_path)
            self._cprof = None
            last_captures.append(self._cprof_path)

        if not self._capture_browser_window:
            self._capture_browser_window = CaptureBrowserWindow(self._capture_trace_path)
        self._capture_browser_window.set_last_capture_paths(last_captures)

        if self._cpu_profiler_autoenabled:
            self._toggle_cpu_profiler(False)
            self._cpu_profiler_autoenabled = False

        print("profile capture: stop")

    async def _export_trace(self, file_path):
        tracefile = TraceFile(file_path)

        # export to nvdataflow?
        nvdf_endpoint = self._settings.get("exts/omni.kit.profiler.window/nvdf/endpoint")
        if nvdf_endpoint:
            tracefile.unzip()
            await export_trace_to_nvdf(tracefile.unzipped_path, nvdf_endpoint)

        # Auto launch in tracy?
        if self._tracy_present and not nvdf_endpoint:
            tracefile.launch_in_tracy()

    def _toggle_capture(self):
        if self._capturing_until == 0:
            if self._python_carb_profiler.enabled:
                manager = omni.kit.app.get_app().get_extension_manager()
                if not manager.is_extension_enabled("omni.kit.profile_python"):
                    manager.set_extension_enabled_immediate("omni.kit.profile_python", True)
            self._settings.set("exts/omni.kit.profile_python/enable", self._python_carb_profiler.enabled)

            print("profile capture: start")
            ts = _get_ts()

            if self._python_cprofile.enabled:
                self._cprof_path = self._capture_trace_path + f"/cProfile_{ts}.prof"
                self._cprof = cProfile.Profile()
                self._cprof.enable()
            else:
                if not self._cpu_profiler_enabled:
                    self._cpu_profiler_autoenabled = True
                    self._toggle_cpu_profiler(True)

            if self._cpu_profiler_enabled:
                self._settings.set_string(
                    "plugins/carb.profiler-cpu.plugin/filePath", self._capture_trace_path + f"/ct_{ts}.gz"
                )
                self._settings.set_bool("/plugins/carb.profiler-cpu.plugin/saveProfile", True)

            if self._write_to_file_time:
                self._capturing_until = time.monotonic() + self._write_to_file_time.model.get_value_as_int()
                self._capture_btn.text = "Stop"
                self._capture_btn.tooltip = (
                    "Time Remaining: " + str(self._write_to_file_time.model.get_value_as_int()) + "s"
                )
            else:
                self._capturing_until = time.monotonic() + 60

            self._refresh_capture_menu()
        else:
            self._stop_capturing()

    def _on_sort_fn(self, model):
        self._sort_by_time = model.get_value_as_bool()

    def _on_average_timings_fn(self, model):
        self._average_timings = model.get_value_as_bool()

    def _on_memStatsDetail_fn(self, model):
        self._memStat_detail = model.get_value_as_bool()

    def _on_memStats_toggle_fn(self, model):
        self._memStat_enabled = model.get_value_as_bool()

    def _on_memStatsSort_fn(self, model):
        self._memStat_sort = model.get_value_as_bool()

    def _on_gpu_index_fn(self, model):
        self._gpu_index = model.get_value_as_int()
        self._cached_gpu_nodes = []  # GPU index changed, clear the node cache

    def _on_max_gpu_indent_fn(self, model):
        self._max_gpu_indent = model.get_value_as_int()

    def _on_max_cpu_indent_fn(self, model):
        self._max_cpu_indent = model.get_value_as_int()

    def _on_min_duration_fn(self, model):
        self._min_duration_ms = model.get_value_as_float()

    def _on_averaging_period_fn(self, model):
        self._averaging_period_secs = model.get_value_as_float()

    def _on_print_log(self):
        names = self._profiler_gpu_names.text.split("\n")
        durations = self._profiler_gpu_durations.text.split("\n")
        full_log = "GPU Profiler (ms):\n"
        for time, name in zip(durations, names):
            full_log += time + "  " + name.replace("\t", " ") + "\n"  # replace tabs with space
        logger.info(full_log)

    def _on_live_update(self):
        self._liveUpdate = not self._liveUpdate
        if self._liveUpdate:
            self._button_live_update.text = "Pause Updates"
        else:
            self._button_live_update.text = "Resume Updates"

    def _on_open_capture_browser(self):
        if not self._capture_browser_window:
            self._capture_browser_window = CaptureBrowserWindow(self._capture_trace_path)
        self._capture_browser_window.show()

    def _update_multi_gpu_nodes(self):
        if not self._engine_stats:
            self._engine_stats = self._get_engine_stats()
        device_nodes = self._engine_stats.get_gpu_profiler_result()
        gpu_count = len(device_nodes)
        if (gpu_count - 1) != self._drag_gpu_index.max:
            self._drag_gpu_index.max = gpu_count  # DragUInt can't set both min and max to zero!

        if self._gpu_index < gpu_count:
            self._update_gpu_nodes(device_nodes[self._gpu_index])
        else:
            self._update_gpu_nodes([])

    def _format_perfsdk_metric(self, metric):
        if metric < 0:
            # Since metric cannot be negative, I use negative value to represent invalid
            # If the value is invalid, we print nothing
            return ""
        else:
            return "{:.1f}".format(metric)

    def _update_gpu_nodes(self, nodes):
        names = ""
        durations = ""
        total_time = 0.0
        perfsdk_metrics = [""] * len(self._perfsdk_realtime_names)

        # Sort nodes in descending order based on time if requested
        if self._sort_by_time == True:
            nodes = sorted(nodes, key=lambda node: node["duration"], reverse=True)

        # Smooth out timings if requested
        if self._average_timings == True:
            self._cached_gpu_nodes = self._average_node_times(nodes, self._cached_gpu_nodes)

        # Update the UI at a lower rate than the viewport
        if self._refresh_frame_count < self._ui_frame_count:
            return

        # To avoid the significant performance cost, batch labels and render in one column
        for node in nodes:
            if node["indent"] == 0:
                total_time += node["duration"]
            hidden = node["indent"] > self._max_gpu_indent or node["duration"] < self._min_duration_ms
            node["hidden"] = hidden
            if hidden:
                continue
            if self._sort_by_time == False:
                names += "\t" * node["indent"]
            if (node["query"] != 0) and (not node["name"]):
                names += "query-{}\n".format(node["query"])
            else:
                names += node["name"] + "\n"
            durations += "{:.3f}\n".format(node["duration"])
            if self._perfsdk_realtime_enabled:
                for i in range(len(self._perfsdk_realtime_names)):
                    metric_name = self._perfsdk_realtime_names[i]
                    if metric_name in node:
                        perfsdk_metrics[i] += self._format_perfsdk_metric(node[metric_name])
                    perfsdk_metrics[i] += "\n"

        # Total time row
        names += "\nTotal GPU-{} Time".format(self._gpu_index)
        durations += "\n{:.3f}\n".format(total_time)

        self._profiler_gpu_names.text = names
        self._profiler_gpu_durations.text = durations
        if self._perfsdk_realtime_enabled:
            for i in range(len(self._perfsdk_realtime_names)):
                self._profiler_gpu_perfsdk_metrics[i].text = perfsdk_metrics[i]

        # remove hidden nodes
        nodes = [x for x in nodes if x["hidden"] == False]

        node_count = len(nodes)
        if self._progress_gpu_column_child_count != node_count:
            self._build_progress_bars_gpu_ui(node_count)

        # update the existing progress bars
        for progress_bar, node in zip(self._progress_gpu_bars, nodes):
            percent = 0.0
            if total_time > 0.00001:
                percent = float(node["duration"]) / total_time
            progress_bar.model.set_value(percent)

    def _update_cpu_nodes(self):
        if self._profile_monitor is None:
            return

        events = self._profile_monitor.get_last_profile_events()
        thread = events.get_main_thread_id()
        nodes = events.get_profile_events(events.get_main_thread_id())
        names = ""
        durations = ""
        total_time = 0.0
        if not self._cpu_profiler_enabled:
            nodes = []
        # Sort nodes in descending order based on time if requested
        if self._sort_by_time == True:
            nodes = sorted(nodes, key=lambda node: node["duration"], reverse=True)

        # Smooth out timings if requested
        if self._average_timings == True:
            self._cached_cpu_nodes = self._average_node_times(nodes, self._cached_cpu_nodes)

        # Update the UI at a lower rate than the viewport
        if self._refresh_frame_count < self._ui_frame_count:
            return

        # To avoid the significant performance cost, batch labels and render in one column
        for node in nodes:
            if node["indent"] == 0:
                total_time += node["duration"]
            hidden = node["indent"] > self._max_cpu_indent or node["duration"] < self._min_duration_ms
            node["hidden"] = hidden
            if hidden:
                continue
            if self._sort_by_time == False:
                names += "\t" * node["indent"]
            names += node["name"] + "\n"
            durations += "{:.3f}\n".format(node["duration"])

        # Total time row
        names += "\nTotal CPU Time"
        durations += "\n{:.3f}\n".format(total_time)

        self._profiler_cpu_names.text = names
        self._profiler_cpu_durations.text = durations

        # remove hidden nodes
        nodes = [x for x in nodes if x["hidden"] == False]

        node_count = len(nodes)
        if self._progress_cpu_column_child_count != node_count:
            self._build_progress_bars_cpu_ui(node_count)

        # update the existing progress bars
        for progress_bar, node in zip(self._progress_cpu_bars, nodes):
            percent = 0.0
            if total_time > 0.00001:
                percent = float(node["duration"]) / total_time
            progress_bar.model.set_value(percent)

    def _update_memory_stats(self):
        # Update the UI at a lower rate than the viewport
        if self._refresh_frame_count < self._ui_frame_count:
            return
        # Memory stat update
        memStat_name = ""
        memStat_size = ""
        if not self._memStat_enabled:
            self._memStat_names.text = memStat_name
            self._memStat_sizes.text = memStat_size
            return

        memStat_nodes = omni.hydra.engine.stats.get_mem_stats(self._memStat_detail)
        # Sort nodes in descending order based on time if requested
        if self._memStat_sort == True:
            memStat_nodes = sorted(memStat_nodes, key=lambda node: node["size"], reverse=True)

        for node in memStat_nodes:
            memStat_name += node["category"] + "\n"
            memStat_size += "{}\n".format(node["size"])

        self._memStat_names.text = memStat_name
        self._memStat_sizes.text = memStat_size

    def _average_node_times(self, nodes, cached_nodes):
        if not self._viewport_api:
            return []

        fps = self._viewport_api.fps
        if (fps < 0.001) or (self._averaging_period_secs < 0.000001):
            return []

        updateCachedNodeStructure = True

        if (len(nodes) > 0) and (len(nodes) == len(cached_nodes)):

            # Verify cached node structure still matches the current frame one
            nodeStructuresMatch = True
            for i in range(len(nodes)):
                if nodes[i]["name"] != cached_nodes[i]["name"]:
                    nodeStructuresMatch = False
                    break

            # Average the timings over _averaging_period_secs via running weighted average
            if nodeStructuresMatch:
                frame_time_secs = 1.0 / fps
                a = min(1.0, frame_time_secs / self._averaging_period_secs)  # lerp coefficient

                for i in range(len(nodes)):
                    # Lerp - running weighted average
                    nodes[i]["duration"] = (1.0 - a) * cached_nodes[i]["duration"] + a * nodes[i]["duration"]
                    cached_nodes[i]["duration"] = nodes[i]["duration"]

                    for metric_name in self._perfsdk_realtime_names:
                        if metric_name in nodes[i] and metric_name in cached_nodes[i]:
                            new_val = nodes[i][metric_name]
                            cached_val = cached_nodes[i][metric_name]
                            # we should ignore cached value if the cached value is invalid (negative values = invalid perfsdk values)
                            s = a if cached_val >= 0 else 1.0
                            nodes[i][metric_name] = (1.0 - s) * cached_val + s * new_val
                            cached_nodes[i][metric_name] = nodes[i][metric_name]

                updateCachedNodeStructure = False

        # Node structure changed, update the cache with a copy of the current frame
        if updateCachedNodeStructure:
            cached_nodes = nodes

        return cached_nodes

    def _on_update(self, event):
        self._late_init_once()

        # node keys define how many columns we would have to display in the profiler.
        # With perfsdk, we have to check every frames if node keys are changed.
        # This is because after user enable perfsdk, it'd take a few _on_update before node keys are actually updated.
        if self._perfsdk_realtime_enabled:
            node_keys = self._get_perfsdk_node_keys()
            if self._perfsdk_realtime_names != node_keys:
                self._window.frame.rebuild()

        # If perfsdk realtime is enabled / disabled, we should insert / remove columns showing statistics from perfsdk.
        if self._prev_perfsdk_realtime_enabled != self._perfsdk_realtime_enabled:
            self._window.frame.rebuild()
            self._prev_perfsdk_realtime_enabled = self._perfsdk_realtime_enabled

        if not hasattr(self, "_late_startup_called"):
            self._on_late_startup()
            self._late_startup_called = True

        if self._capturing_until > 0:
            # apparently setting the text causes the button to not be clickable (or very difficult to click)
            # so only do this when the text changes
            new_text = "Time Remaining: {:.1f}s".format(self._capturing_until - time.monotonic())
            self._capture_btn.tooltip = new_text
            # if new_text != self._capture_btn.text:
            #    self._capture_btn.text = new_text

            if self._capturing_until < time.monotonic():
                self._stop_capturing()
        if not self._viewport_api:
            return
        self._refresh_frame_count += 1
        fps = 1/event.payload["dt"] if event.payload["dt"] > 0 else 60
        self._ui_frame_count = fps / self._ui_update_rate
        if self._liveUpdate:
            self._update_multi_gpu_nodes()
            self._update_cpu_nodes()
            self._update_memory_stats()
        if self._refresh_frame_count >= self._ui_frame_count:
            self._refresh_frame_count = 0



def get_instance():
    global _extension_instance
    return _extension_instance


def get_window():
    global _extension_instance
    if not _extension_instance._window:
        _extension_instance.show_window(True)
    return _extension_instance._window
