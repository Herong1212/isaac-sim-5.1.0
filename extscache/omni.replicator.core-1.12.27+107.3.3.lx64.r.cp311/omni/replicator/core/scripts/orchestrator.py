# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=too-many-lines,protected-access

import asyncio
import builtins
import time
from collections import deque
from enum import Enum
from typing import Callable, List, Tuple

import carb
import carb.events
import carb.settings
import omni.graph.core as og
import omni.kit
import omni.kit.app
import omni.kit.async_engine
import omni.timeline
from omni.syntheticdata import SyntheticData
from pxr import Usd

from ..bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0
from .annotators import ANNOTATOR_EVENT
from .backends.dispatcher import BackendDispatch
from .named_nodes import NamedNodes
from .utils import GRAPH_PATH, get_reduced_ref_time, get_replicator_graph_exists, singleton, utils
from .writers import WRITER_EVENT, WriterRegistry

MAX_STEP_ATTEMPTS = 1000
WARMUP_FRAMES_DEFAULT = 0
FRAMES_TO_DISABLE_ASYNC_RENDERING = 0
DEFAULT_SUBFRAMES_REALTIME = 1
MAX_ASSET_LOADING_TIME = 30  # seconds
SETTINGS_PREFIX = "/exts/omni.replicator.core/"
ORCHESTRATOR_EVENT = "omni.replicator.core.orchestrator:orchestratorEvent"
NUM_FRAMES_ASYNC_RENDERING_DELAY = 5
SETTINGS_TO_SAVE = [
    "/rtx/externalFrameCounter",
    "/rtx-transient/resetPtAccumOnlyWhenExternalFrameCounterChanges",
    "/app/viewport/show",
    "/app/asyncRenderingLowLatency",
    "/app/viewport/grid/enabled",
    "/app/viewport/outline/enabled",
    "/app/viewport/show/lights",
    "/app/viewport/show/camera",
    "/rtx/pathtracing/spp",
    "/rtx/pathtracing/clampSpp",
    "/rtx/pathtracing/totalSpp",
    "/rtx/materialDb/syncLoads",
    "/rtx/hydra/materialSyncLoads",
    "/rtx/ecoMode/enabled",
    "/persistent/physics/visualizationDisplayColliders",
]
_orchestrator = None  # pylint: disable=invalid-name


class Status(Enum):
    STOPPED = 0
    STARTED = 1
    STARTING = 2
    LOADING = 3
    STOPPING = 4
    PAUSED = 5
    INITIALIZING = 6
    STEPPING = 7
    STEPPED = 8


def _get_time(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator


class OrchestratorError(Exception):
    """Base exception for errors raised by the orchestrator"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "An orchestrator error was encountered."
        super().__init__(msg)


class StatusCallback:
    """Status Callback object

    Provides methods to register and unregister a callback function called when orchestrator status changes.

    Attributes:
        callback: Callback function to be called when orchestrator status changes
    """

    def __init__(self, callback: Callable):
        self.callback = callback

    def register(self):
        """Register callback when orchestrator status is changed."""
        carb.log_info(f"Registering callback {self.callback}")
        _orchestrator._register_status_callback(self.callback)

    def unregister(self):
        """Unregister callback."""
        carb.log_info(f"Unregistering callback {self.callback}")
        _orchestrator._unregister_status_callback(self.callback)

    def __del__(self):
        self.unregister()


@singleton
class _Orchestrator:
    # Settings controlling writing
    _subframe = 0
    _frame = 0
    _sequence = 0
    _sim_times_to_write = deque(maxlen=10)
    _cached_settings = None
    _status_callbacks = []
    _writer_instances = {}
    _trigger_instances = {}

    def __init__(self):
        global _orchestrator  # pylint: disable=invalid-name
        _orchestrator = self
        self._telemetry = Schema_omni_replicator_extinfo_1_0()
        self._timeline = omni.timeline.get_timeline_interface()
        self._update_sub = None
        self._material_load_start = None
        self._status = Status.STOPPED
        self._step_delta_time = None
        self._is_loading = False
        self._cached_async_rendering = None
        self.reset()

    def _setup_subscribers(self):
        self.__status_cbs = [self._register_status_callback(self._on_status_change)]
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )
        self._observers = [
            # Placeholder for upcoming timeline event system update
            # carb.eventdispatcher.get_eventdispatcher().observe_event(
            #     observer_name="omni.replicator.orchestrator:timelineEventStop",
            #     event_name=omni.timeline.GLOBAL_EVENT_STOP,
            #     on_event=self._on_timeline_event,
            # ),
            # carb.eventdispatcher.get_eventdispatcher().observe_event(
            #     observer_name="omni.replicator.orchestrator:timelineEventPause",
            #     event_name=omni.timeline.GLOBAL_EVENT_PAUSE,
            #     on_event=self._on_timeline_event,
            # ),
            # carb.eventdispatcher.get_eventdispatcher().observe_event(
            #     observer_name="omni.replicator.orchestrator:timelineEventPlay",
            #     event_name=omni.timeline.GLOBAL_EVENT_PLAY,
            #     on_event=self._on_timeline_event,
            # ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.replicator.orchestrator:annotatorEvent",
                event_name=ANNOTATOR_EVENT,
                on_event=self._on_annotator_event,
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.replicator.orchestrator:writerEvent",
                event_name=WRITER_EVENT,
                on_event=self._on_writer_event,
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
                on_event=self.on_stage_event,
                observer_name="omni.replicator.core.orchestrator:stage_closed",
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOADING),
                on_event=self.on_stage_event,
                observer_name="omni.replicator.core.orchestrator:assets_loading",
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOADED),
                on_event=self.on_stage_event,
                observer_name="omni.replicator.core.orchestrator:assets_loaded",
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOAD_ABORTED),
                on_event=self.on_stage_event,
                observer_name="omni.replicator.core.orchestrator:assets_load_aborted",
            ),
        ]

    def on_stage_event(self, event: carb.events.IEvent):
        stage_event = omni.usd.get_context().stage_event_type(event.event_name)
        if stage_event == omni.usd.StageEventType.ASSETS_LOADING:
            self._is_loading = True
        elif stage_event in [
            omni.usd.StageEventType.ASSETS_LOADED,
            omni.usd.StageEventType.ASSETS_LOAD_ABORTED,
            omni.usd.StageEventType.CLOSED,
        ]:
            self._is_loading = False

    def shutdown(self):
        for observer in self._observers:
            observer.reset()
        self.stop()
        for status_cb in self.__status_cbs:
            self._unregister_status_callback(status_cb)
        self._timeline_sub = None

    def reset(self):
        self._status = Status.STOPPED
        self._num_frames = None
        self.reset_scenario()
        NamedNodes.reset()
        persistent_capture_on_play = carb.settings.get_settings().get_as_bool(
            "/persistent/omni/replicator/captureOnPlay"
        )
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", persistent_capture_on_play)

    def reset_scenario(self):
        self.stop()
        self._restore_settings()
        self._subframe = 0
        self._is_motion_blur_mode = False
        self._frame = 0
        self._sim_time = 0.0
        self._num_captured_frames = 0
        self._sequence = 0
        self._sim_times_to_write = deque(maxlen=10)
        self._next_rt_subframes = 1
        self._reset_writer_and_triggers(num_frames=self._num_frames)
        self._warn_once_total_spp = True
        self._warn_once_no_annotators = True
        self._cached_settings = None
        self._resume_play = False
        self._is_delayed_play = False
        self._step_delta_time = None

    def _on_status_change(self, new_status):
        if self.capture_on_play:
            if new_status == Status.STOPPED and not self._timeline.is_stopped():
                self._timeline.stop()
                self._timeline.commit()
            elif new_status == Status.STARTED:

                async def delayed_play():
                    await omni.kit.app.get_app().next_update_async()
                    # Delay play by one frame to capture frame time 0.0
                    if self.status not in [Status.STOPPED, Status.STOPPING]:
                        self._timeline.play()
                        self._is_delayed_play = False
                        # No need to commit timeline here

                if not self._timeline.is_playing():
                    self._is_delayed_play = True
                    omni.kit.async_engine.run_coroutine(delayed_play())
            elif new_status == Status.PAUSED and self._timeline.is_playing():
                self._timeline.pause()
                self._timeline.commit()
            elif new_status == Status.STOPPING and not self._timeline.is_stopped():
                self._timeline.stop()
                self._timeline.commit()

            # FIXME: This this not threadsafe
            # Applies pending timeline state changes and calls all callbacks
        if new_status == Status.STOPPED:
            WriterRegistry._on_final_frame()
            self._undo_motion_blur_settings()
            self._restore_settings()

    def _on_attached(self):
        if (
            self.capture_on_play
            and self._timeline.is_playing()
            and ((self.status not in [Status.STARTING, Status.STARTED, Status.STEPPING]) or not self._is_tick_graph())
        ):
            self._set_capture_settings()
            self._set_tick_graph()
            self.status = Status.STARTING

    def _on_annotator_event(self, event: carb.events.IEvent):
        if "attached" in event:
            self._on_attached()

    def _on_writer_event(self, event: carb.events.IEvent):
        if "attached" in event:
            self._on_attached()

    def _on_timeline_event(self, event: carb.events.IEvent):
        # NOTE: Timeline callbacks occur on the main thread
        # int(omni.timeline.TimelineEventType.PLAY) = 0
        # int(omni.timeline.TimelineEventType.PAUSE) = 1
        # int(omni.timeline.TimelineEventType.STOP) = 2
        event_type = omni.timeline.TimelineEventType(event.type)
        if event.type > 2:
            return

        if self.capture_on_play and get_replicator_graph_exists():
            if event_type == omni.timeline.TimelineEventType.PLAY:
                if self.status not in [Status.STARTING, Status.STARTED, Status.STEPPING]:
                    # If status indicates Replicator is already initialized, don't reset
                    if self.status not in [Status.PAUSED, Status.STEPPED]:
                        self.reset_scenario()
                    self.preview()  # Toggle triggers once
                    self._set_capture_settings()
                    self._set_tick_graph()
                    self.status = Status.STARTED
            elif event_type == omni.timeline.TimelineEventType.STOP:
                if self.status not in [Status.STOPPING, Status.STOPPED]:
                    self._restore_settings()
                    self.status = Status.STOPPING
            elif event_type == omni.timeline.TimelineEventType.PAUSE:
                # Force timeline and replicator to stop once reaches end of non-looping timeline
                if (
                    self._timeline.get_current_time() >= self._timeline.get_end_time()
                    and not self._timeline.is_looping()
                ):
                    self._timeline.stop()
                elif self.status != Status.PAUSED:
                    self.status = Status.PAUSED

    def set_sim_time(self, sim_time_numerator: int, sim_time_denominator: int):
        self._sim_time = get_reduced_ref_time(sim_time_numerator, sim_time_denominator)

    def _is_all_ended(self, end_sim_time: Tuple[int, int] = None):
        is_all_ended = _orchestrator._trigger_instances and all(
            not trigger["active"] for _, trigger in _orchestrator._trigger_instances.items()
        )
        if is_all_ended and _orchestrator.status == Status.STARTED:
            _orchestrator.status = Status.STOPPING
        return is_all_ended

    def _validate_pt_settings(self, render_mode, total_spp):
        if render_mode == "PathTracing" and (not total_spp or total_spp < 1):
            if self._warn_once_total_spp:
                carb.log_warn(
                    f"Total SPP set to {total_spp}, Replicator unable to run. To use Replicator, ensure "
                    "`/rtx/pathtracing/totalSpp` > 0"
                )
                self._warn_once_total_spp = False
            return False
        return True

    def _get_pt_subframes_per_frame(self) -> int:
        if not carb.settings.get_settings().get_as_int("/rtx/pathtracing/totalSpp"):
            carb.settings.get_settings().set_int("/rtx/pathtracing/totalSpp", 64)
            UserWarning("/rtx/pathtracing/totalSpp not defined, setting to default of 64.")
        if not carb.settings.get_settings().get_as_int("/rtx/pathtracing/spp"):
            carb.settings.get_settings().set_int("/rtx/pathtracing/spp", 1)
            UserWarning("/rtx/pathtracing/spp not defined, setting to default of 1.")

        render_mode = carb.settings.get_settings().get("/rtx/rendermode")
        total_spp = carb.settings.get_settings().get("/rtx/pathtracing/totalSpp")
        spp = carb.settings.get_settings().get("/rtx/pathtracing/spp")
        if render_mode == "PathTracing" and carb.settings.get_settings().get(
            "/omni/replicator/pathTracedMotionBlurSubSamples"
        ):
            return carb.settings.get_settings().get("/omni/replicator/pathTracedMotionBlurSubSamples")

        # Compute PT subframes for motion blur effect if pathTracedMotionBlurSubSamples is not set.
        return total_spp // max(1, spp)  # this gets huge for motion blur set to true

    def on_update(  # noqa C901
        self,
        *args,
    ):
        self._frame += 1

        fps = self._timeline.get_time_codes_per_seconds()
        render_mode = carb.settings.get_settings().get("/rtx/rendermode")
        total_spp = carb.settings.get_settings().get("/rtx/pathtracing/totalSpp")

        if not self._validate_pt_settings(render_mode, total_spp):
            self.stop()
            return

        pt_subframes = self._get_pt_subframes_per_frame()

        if self.status == Status.STOPPING:
            # Check if safe to stop
            sim_time = self._sim_times_to_write[-1] if self._sim_times_to_write else (1, -1)
            dispatcher = og.get_node_by_path("/Render/PostProcess/SDGPipeline/PostProcessDispatcher")

            if dispatcher:
                numerator = dispatcher.get_attribute("outputs:referenceTimeNumerator").get()
                denominator = dispatcher.get_attribute("outputs:referenceTimeDenominator").get()
                is_rendering_done = (
                    numerator == 0 or _get_time(numerator, denominator) > _get_time(*sim_time)
                    if denominator > 0.0
                    else True
                )
            else:
                is_rendering_done = True

            is_writing_done = BackendDispatch.is_done_writing()
            if is_writing_done and is_rendering_done:
                self.status = Status.STOPPED
            return

        # This ensures one frame is rendered before replicator is started
        if self.status == Status.STARTING:
            self.status = Status.STARTED
            return

        if self.status in [Status.STARTED, Status.STEPPING]:
            if not self._is_tick_graph():
                self._set_tick_graph()

            if og.Controller().node("/Orchestrator/OgnReadFabricTime"):
                read_time_node = og.Controller().node("/Orchestrator/OgnReadFabricTime")
                self.set_sim_time(
                    read_time_node.get_attribute("outputs:fabricFrameTimeNumerator").get(),
                    read_time_node.get_attribute("outputs:fabricFrameTimeDenominator").get(),
                )
                if self._sim_time == (-1, -1):
                    return
            else:
                self.stop()
                raise OrchestratorError("Unable to read simulation time, Replicator cannot run")

            if self._subframe == 0:
                # Set frame counter for PT motion blur (if using)
                carb.settings.get_settings().set_int("/rtx/externalFrameCounter", self._frame)
                # Add a frame to randomize
                carb.eventdispatcher.get_eventdispatcher().dispatch_event(
                    ORCHESTRATOR_EVENT, payload={"trigger": self._sim_time}
                )
                # Find any Replicator trigger and evaluate the graph
                if carb.settings.get_settings().get_as_bool(f"{SETTINGS_PREFIX}Orchestrator/enableEvalTriggers"):
                    replicator_triggers = utils._find_replicator_triggers()
                    utils._evaluate_graphs_from_nodes(replicator_triggers)
                # Force graph to evaluate trigger (both randomization and orchestration graphs)
                else:
                    if og.get_graph_by_path(GRAPH_PATH):
                        og.Controller().evaluate_sync(graph_id=GRAPH_PATH)
                    if og.get_graph_by_path("/WriterOrchestrator"):
                        og.Controller().evaluate_sync(graph_id="/WriterOrchestrator")

                # Check if generation is complete
                if self._is_all_ended() and self.status in [Status.STARTED, Status.STOPPING]:
                    return

            self._subframe += 1

            carb_rt_subframes = carb.settings.get_settings().get("/omni/replicator/RTSubframes")
            if not carb_rt_subframes:
                carb_rt_subframes = DEFAULT_SUBFRAMES_REALTIME
            rt_subframes = max(1, max(int(self._next_rt_subframes), carb_rt_subframes))

            # RT Subframes can be used when in PathTracing mode to workaround loading material issues
            if self._subframe < rt_subframes:
                if self._timeline.is_playing() or self._is_delayed_play:
                    self._resume_play = True
                    self._timeline.set_auto_update(False)
                    self._timeline.commit_silently()
                return

            # Reset next rt subframes to 1
            self._next_rt_subframes = 1

            is_motion_blur_enabled = carb.settings.get_settings().get_as_bool("/omni/replicator/captureMotionBlur")
            if is_motion_blur_enabled:
                self._set_motion_blur_settings()

            # If rendering motion blur in PT mode, render subframe
            if render_mode == "PathTracing" and self._subframe <= max(pt_subframes, rt_subframes):
                # If motion blur is enabled, step timeline before returning subframe
                if is_motion_blur_enabled:
                    target_time = self._timeline.get_current_time()
                    time_rate = self._step_delta_time if self._step_delta_time else 1.0 / fps
                    if self._num_captured_frames > 0:
                        target_time += time_rate / pt_subframes
                    self._timeline.set_current_time(target_time)
                    self._timeline.commit()
                elif self._timeline.is_playing() or self._is_delayed_play:
                    self._resume_play = True
                    self._timeline.set_auto_update(False)
                    self._timeline.commit_silently()

                # Only proceed if on the last subframe
                if self._subframe < max(pt_subframes, rt_subframes):
                    return

            # Advance timeline manually if delta time is present and not doing motion blur
            elif not (render_mode == "PathTracing" and is_motion_blur_enabled) and self._step_delta_time:
                target_time = self._timeline.get_current_time()
                if self._num_captured_frames > 0:
                    target_time += self._step_delta_time
                self._timeline.set_current_time(target_time)
                self._timeline.commit()

            # Reset next rt subframes to 1
            self._next_rt_subframes = 1

            # Add a frame to capture
            if len(self._sim_times_to_write) == 0 or self._sim_time != self._sim_times_to_write[-1]:
                self._sim_times_to_write.append(self._sim_time)
            carb.eventdispatcher.get_eventdispatcher().dispatch_event(
                ORCHESTRATOR_EVENT, payload={"capture": self._sim_time}
            )
            if carb.settings.get_settings().get("/omni/replicator/debug"):
                carb.log_info(f"Orchestrator-schedule sim time {self._sim_time}")
            self._num_captured_frames += 1
            self._subframe = 0
            self._is_all_ended()

            ogn_ref_time_gate_path = "/Render/PostProcess/SDGPipeline/DispatchSync"
            try:
                stage = omni.usd.get_context().get_stage()
                with Usd.EditContext(stage, stage.GetSessionLayer()):
                    ref_time_gate_node = og.Controller.node(ogn_ref_time_gate_path)
                    og.AttributeValueHelper(ref_time_gate_node.get_attribute("inputs:simTimesToWrite")).set(
                        self._sim_times_to_write, update_usd=True
                    )
            except og.OmniGraphError as err:
                if self._warn_once_no_annotators:
                    carb.log_info(f"Replicator running, but no annotator detected. {err}")
                    self._warn_once_no_annotators = False

            if self.status == Status.STEPPING:
                self.status = Status.STEPPED

            # If timeline was paused to render subframes, resume now
            if self._resume_play:
                self._resume_play = False
                self._timeline.set_auto_update(True)
                self._timeline.play()
                # No timeline commit - causes timeline to pause

            NamedNodes.collect_data(self._sim_time)

            has_reached_num_frames = self._num_frames is not None and self._num_captured_frames >= self._num_frames

            # Don't stop if replicator is Stepping
            if has_reached_num_frames and self.status == Status.STARTED:
                self.stop()

    async def _initialize_async(self):
        # Wait for stopping complete
        while self.status == Status.STOPPING:
            await omni.kit.app.get_app().next_update_async()

        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "initialize"})
        self._status = Status.INITIALIZING
        self._telemetry.orchestrator_sendEvent(omni.kit.app.get_app().get_time_since_start_ms(), "INITIALIZING")

        # Reset deque
        self._sim_times_to_write.clear()

        # Create dispatcher
        SyntheticData.Get().activate_node_template("DispatchSync")

        # Async rendering turned on can cause loaded event to fail to be sent (OMREQ-1202)
        if self._cached_settings is not None and "/app/asyncRendering" in self._cached_settings:
            cached_async_rendering = self._cached_settings["/app/asyncRendering"]
        else:
            cached_async_rendering = carb.settings.get_settings().get("/app/asyncRendering")
        carb.settings.get_settings().set("/app/asyncRendering", False)

        # Pause timeline
        is_auto_updating = self._timeline.is_auto_updating()
        self._timeline.set_auto_update(False)
        self._timeline.commit_silently()

        # Setup tick graph
        self._set_tick_graph()

        # Setup first frame
        await omni.kit.app.get_app().next_update_async()
        self.preview()
        await omni.kit.app.get_app().next_update_async()
        start_loading_time = time.time()
        min_time = start_loading_time + carb.settings.get_settings().get_as_float(f"{SETTINGS_PREFIX}initMinLoadTime")
        max_time = start_loading_time + self._max_loading_time
        while (self._is_loading and time.time() < max_time) or time.time() < min_time:
            await asyncio.sleep(0.01)
            await omni.kit.app.get_app().next_update_async()

        if time.time() > (start_loading_time + self._max_loading_time):
            msg = (
                "Maximum loading time reached while waiting for assets to load. Asset loading may not have completed."
                f"Maximum asset loading time can be configured by setting the `{SETTINGS_PREFIX}maxAssetLoadingTime` "
                "setting."
            )
            carb.log_warn(msg)

        # Restore async rendering state
        carb.settings.get_settings().set("/app/asyncRendering", cached_async_rendering)

        # Set capture setting, including specified async rendering state
        self._set_capture_settings()

        # This waits for async-rendering to be disabled
        frame_disable_async_rendering = 0
        while self.status != Status.STOPPED and frame_disable_async_rendering < FRAMES_TO_DISABLE_ASYNC_RENDERING:
            await omni.kit.app.get_app().next_update_async()
            frame_disable_async_rendering += 1

        if self.status == Status.STOPPED:
            carb.log_warn("Replicator initialization aborted")
            return

        for path in self._writer_instances:
            self._set_active_status("writer", path, True)
        for path in self._trigger_instances:
            self._set_active_status("trigger", path, True)

        self.is_starting = True
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "start"})

        # Resume timeline
        self._timeline.set_auto_update(is_auto_updating)
        self._timeline.commit_silently()

    def _initialize(self):
        _verify_is_standalone_workflow("_initialize")

        while self.status == Status.STOPPING:
            omni.kit.app.get_app().update()

        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "initialize"})
        self._status = Status.INITIALIZING
        self._telemetry.orchestrator_sendEvent(omni.kit.app.get_app().get_time_since_start_ms(), "INITIALIZING")

        # Reset deque
        self._sim_times_to_write.clear()

        # Create dispatcher
        SyntheticData.Get().activate_node_template("DispatchSync")

        # Async rendering turned on can cause loaded event to fail to be sent (OMREQ-1202)
        if self._cached_settings is not None and "/app/asyncRendering" in self._cached_settings:
            cached_async_rendering = self._cached_settings["/app/asyncRendering"]
        else:
            cached_async_rendering = carb.settings.get_settings().get("/app/asyncRendering")
        carb.settings.get_settings().set("/app/asyncRendering", False)

        # Pause timeline
        is_auto_updating = self._timeline.is_auto_updating()
        self._timeline.set_auto_update(False)
        self._timeline.commit_silently()

        # Setup tick graph
        self._set_tick_graph()

        # Run the graph once to load required assets/materials
        omni.kit.app.get_app().update()
        self.preview()
        omni.kit.app.get_app().update()
        start_loading_time = time.time()
        min_time = start_loading_time + carb.settings.get_settings().get_as_float(f"{SETTINGS_PREFIX}initMinLoadTime")
        max_time = start_loading_time + self._max_loading_time

        while (self._is_loading and time.time() < max_time) or time.time() < min_time:
            omni.kit.app.get_app().update()

        if time.time() > (start_loading_time + self._max_loading_time):
            msg = (
                "Maximum loading time reached while waiting for assets to load. Asset loading may not have completed."
                f"Maximum asset loading time can be configured by setting the `{SETTINGS_PREFIX}maxAssetLoadingTime` "
                "setting."
            )
            carb.log_warn(msg)

        # Restore async rendering state
        carb.settings.get_settings().set("/app/asyncRendering", cached_async_rendering)

        # Set capture settings
        self._set_capture_settings()

        # This waits for async-rendering to be disabled
        for _ in range(FRAMES_TO_DISABLE_ASYNC_RENDERING):
            omni.kit.app.get_app().update()

        if self.status == Status.STOPPED:
            carb.log_warn("Replicator initialization aborted")
            return

        for path in self._writer_instances:
            self._set_active_status("writer", path, True)
        for path in self._trigger_instances:
            self._set_active_status("trigger", path, True)

        self.is_starting = True
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "start"})

        # Resume timeline
        self._timeline.set_auto_update(is_auto_updating)
        self._timeline.commit_silently()

    @property
    def frames_to_preview(self):
        # DEPRECATED
        return 0

    @property
    def _max_loading_time(self):
        _settings = carb.settings.get_settings()
        return _settings.get_as_float(f"{SETTINGS_PREFIX}maxAssetLoadingTime") or MAX_ASSET_LOADING_TIME

    @property
    def next_rt_subframes(self):
        return self._next_rt_subframes

    @next_rt_subframes.setter
    def next_rt_subframes(self, value):
        carb_rt_subframes = carb.settings.get_settings().get("/omni/replicator/RTSubframes")
        if carb_rt_subframes is None:
            carb_rt_subframes = 1
        self._next_rt_subframes = max(1, max(int(value), carb_rt_subframes))

    @property
    def is_started(self):
        return self.status == Status.STARTED

    @is_started.setter
    def is_started(self, value: bool):
        if value:
            self.status = Status.STARTED
        else:
            self.status = Status.STOPPING

    @property
    def is_starting(self):
        return self.status == Status.STARTING

    @is_starting.setter
    def is_starting(self, value: bool):
        if value:
            self.status = Status.STARTING
        else:
            self.status = Status.STOPPING

    @property
    def capture_on_play(self):
        return bool(carb.settings.get_settings().get("/omni/replicator/captureOnPlay"))

    @capture_on_play.setter
    def capture_on_play(self, value: bool):
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", bool(value))

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if new_status == Status.STOPPING and not self._is_tick_graph():
            # No tick graph, can safely stop immediately
            new_status = Status.STOPPED

        if self.status != new_status:
            if carb.settings.get_settings().get("/omni/replicator/debug"):
                carb.log_info(f"Status changed: {self._status}->{new_status}")
            self._telemetry.orchestrator_sendEvent(
                omni.kit.app.get_app().get_time_since_start_ms(), str(new_status).replace("Status.", "")
            )
            self._status = new_status
            self._notify_status_observers(new_status)

    def _notify_status_observers(self, new_status):
        for callback in self._status_callbacks:
            callback(new_status)

    def _register_status_callback(self, callback):
        self._status_callbacks.append(callback)

    def _unregister_status_callback(self, callback):
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)

    def start(self, num_frames: int = None, start_timeline: bool = False):
        self._reset_writer_and_triggers(num_frames)
        if get_replicator_graph_exists():
            self.reset_scenario()
            if _check_is_standalone_workflow():
                self._initialize()
            else:
                omni.kit.async_engine.run_coroutine(self._initialize_async())
            while self.status != Status.STARTED and self.status == Status.STARTING:
                omni.kit.app.get_app().update()

            async def delayed_play():
                # Play after one frame
                await omni.kit.app.get_app().next_update_async()
                self._timeline.play()
                self._is_delayed_play = False

            if start_timeline:
                self._is_delayed_play = True
                omni.kit.async_engine.run_coroutine(delayed_play())

    async def start_async(self, num_frames: int = None, start_timeline: bool = False):
        self._reset_writer_and_triggers(num_frames)
        if get_replicator_graph_exists():
            self.reset_scenario()
            await self._initialize_async()
            while self.status != Status.STARTED and self.status == Status.STARTING:
                await omni.kit.app.get_app().next_update_async()

            async def delayed_play():
                # Play after one frame
                await omni.kit.app.get_app().next_update_async()
                self._timeline.play()
                self._is_delayed_play = False

            if start_timeline:
                self._is_delayed_play = True
                omni.kit.async_engine.run_coroutine(delayed_play())

    def resume(self):
        self.status = Status.STARTED

    def stop(self):
        """Note, non-async stop is best followed by ``wait_until_complete`` in a standalone workflow to
        guarantee full stop.
        """
        if self.status not in [Status.STOPPING, Status.STOPPED]:
            self.status = Status.STOPPING
            carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "stop"})

            async def on_stop():
                await self.wait_until_complete_async()
                self._restore_settings()

            omni.kit.async_engine.run_coroutine(on_stop())

    async def stop_async(self):
        self.status = Status.STOPPING
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "stop"})
        await self.wait_until_complete_async()
        self._restore_settings()

    def pause(self):
        self.status = Status.PAUSED

    def preview(self):
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "preview"})
        if og.get_graph_by_path(GRAPH_PATH):
            og.Controller().evaluate_sync(graph_id=GRAPH_PATH)

    async def preview_async(self):
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ORCHESTRATOR_EVENT, payload={"command": "preview"})
        await og.Controller().evaluate()
        await omni.kit.app.get_app().next_update_async()

    def _is_tick_graph(self):
        ctx = omni.usd.get_context()
        if ctx is None:
            return False
        stage = ctx.get_stage()
        if stage is None:
            return False
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            return bool(stage.GetPrimAtPath("/Orchestrator"))

    def _clear_tick_graph(self):
        if self._is_tick_graph():
            stage = omni.usd.get_context().get_stage()
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                stage.RemovePrim("/Orchestrator")

    def _subscribe_update(self):
        if _orchestrator._update_sub is None:
            _orchestrator._update_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
                order=0,
                event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
                on_event=_orchestrator.on_update,
                observer_name="omni.replicator.core.orchestrator:update",
            )

    def _unsubscribe_update(self):
        if _orchestrator._update_sub is not None:
            _orchestrator._update_sub.unsubscribe()

    def _set_tick_graph(self):
        # If orchestrator is disabled, no orchestrator "trigger" or "capture" events will be produced
        if not carb.settings.get_settings().get(f"{SETTINGS_PREFIX}Orchestrator/enabled"):
            return False

        stage = omni.usd.get_context().get_stage()
        if stage is None:
            return False
        session_layer = stage.GetSessionLayer()
        with Usd.EditContext(stage, session_layer):
            if not og.Controller().graph("/Orchestrator"):
                if carb.settings.get_settings().get("/omni/replicator/asyncRendering"):
                    self._unsubscribe_update()
                    og.Controller.edit(
                        {"graph_path": "/Orchestrator", "evaluator_name": "push"},
                        {
                            og.Controller.Keys.CREATE_NODES: [
                                ("OgnReadFabricTime", "omni.replicator.core.ReadFabricTime"),
                                ("OrchestratorUpdate", "omni.replicator.core.OgnUpdateOrchestrator"),
                            ],
                            og.Controller.Keys.CONNECT: [
                                (
                                    "OgnReadFabricTime.outputs:fabricFrameTimeNumerator",
                                    "OrchestratorUpdate.inputs:rationalTimeOfSimNumerator",
                                ),
                                (
                                    "OgnReadFabricTime.outputs:fabricFrameTimeDenominator",
                                    "OrchestratorUpdate.inputs:rationalTimeOfSimDenominator",
                                ),
                            ],
                        },
                    )
                else:
                    og.Controller.edit(
                        {"graph_path": "/Orchestrator", "evaluator_name": "push"},
                        {
                            og.Controller.Keys.CREATE_NODES: [
                                ("OgnReadFabricTime", "omni.replicator.core.ReadFabricTime"),
                            ],
                        },
                    )
                    self._subscribe_update()

                # Hide orchestrator prim
                stage.GetPrimAtPath("/Orchestrator").SetMetadata("hide_in_stage_window", 1)
        return True

    def _set_motion_blur_settings(self):
        if _orchestrator._is_motion_blur_mode:
            return
        _orchestrator._is_motion_blur_mode = True
        _settings = carb.settings.get_settings()
        if _settings.get("/rtx/rendermode") == "PathTracing":
            # Disable automatic time update in timeline so that orchestrator can control step
            self._timeline.set_auto_update(False)
            self._timeline.commit_silently()

            spp = _settings.get_as_int("/rtx/pathtracing/spp")
            _settings.set_int("/rtx/pathtracing/totalSpp", spp * _orchestrator._get_pt_subframes_per_frame())

            # Allow control of sample accumulation explicitly by simply changing the /rtx/externalFrameCounter value
            _settings.set_bool("/rtx-transient/resetPtAccumOnlyWhenExternalFrameCounterChanges", True)
        else:
            _settings.set_bool("/rtx/post/motionblur/enabled", True)

    def _undo_motion_blur_settings(self, pt_only: bool = False):
        if not _orchestrator._is_motion_blur_mode:
            return
        _orchestrator._is_motion_blur_mode = False
        _settings = carb.settings.get_settings()
        if _settings.get("/rtx/rendermode") == "PathTracing":
            # Disable automatic time update in timeline so that orchestrator can control step
            self._timeline.set_auto_update(True)
            self._timeline.commit_silently()

            if self._cached_settings:
                _settings.set_int("/rtx/pathtracing/spp", self._cached_settings.get("/rtx/pathtracing/spp", 1))
                _settings.set_int(
                    "/rtx/pathtracing/totalSpp", self._cached_settings.get("/rtx/pathtracing/totalSpp", 1)
                )

            # Allow control of sample accumulation explicitly by simply changing the /rtx/externalFrameCounter value
            _settings.set_bool("/rtx-transient/resetPtAccumOnlyWhenExternalFrameCounterChanges", False)
        elif not pt_only:
            _settings.set_bool("/rtx/post/motionblur/enabled", False)

    def _set_capture_settings(self):
        _settings = carb.settings.get_settings()

        # Cache settings
        # self._cached_settings = [_settings.create_dictionary_from_settings(sp) for sp in SETTINGS_TO_SAVE]
        if self._cached_settings is None:
            self._cached_settings = {sp: _settings.get(sp) for sp in SETTINGS_TO_SAVE if _settings.get(sp) is not None}

        if self._cached_async_rendering is None:
            self._cached_async_rendering = _settings.get("/app/asyncRendering")

        # Remove gizmos from RGB
        _settings.set("/app/viewport/grid/enabled", False)
        _settings.set("/app/viewport/outline/enabled", False)
        _settings.set("/app/viewport/show/lights", False)
        _settings.set("/app/viewport/show/camera", False)
        _settings.set("/persistent/physics/visualizationDisplayColliders", 0)

        # disable async rendering unless asyncRendering is specified
        async_rendering = bool(_settings.get("/omni/replicator/asyncRendering"))
        if _settings.get_as_bool("/app/asyncRendering") != async_rendering:
            _settings.set_bool("/app/asyncRendering", async_rendering)

        # Enable syncLoads in materialDB and Hydra.
        # This is needed to make sure texture updates finish before we start the rendering
        _settings.set("/rtx/materialDb/syncLoads", True)
        _settings.set("/rtx/hydra/materialSyncLoads", True)

        # Disable eco mode (want to keep accumulating samples)
        _settings.set("/rtx/ecoMode/enabled", False)

        # Rendering to some image buffers additionally require explicitly setting `set_capture_sync(True)`, on top of
        # disabling the `/app/asyncRendering` setting. This can otherwise cause images to hold corrupted buffer
        # information by erroneously assuming a complete image buffer is available when only a first partial subframe
        # has been renderer (as in the case of EXR):
        # _renderer.set_capture_sync(True)

        if _settings.get("/omni/replicator/captureMotionBlur"):
            self._set_motion_blur_settings()

        # This ensures the push graph is executed every frame
        self._timeline.set_play_every_frame(True)

        # Clear any prim selections
        _usd_context = omni.usd.get_context()
        _selection = _usd_context.get_selection()
        _selection.clear_selected_prim_paths()

    def _reset_writer_and_triggers(self, num_frames: int = None):
        self._writer_instances.clear()
        self._trigger_instances.clear()
        if num_frames is not None:
            self._num_frames = num_frames

    def _restore_settings(self):
        # As of 107.3.3, restoring async rendering True after destroying the annotator graph
        # leads to a hang. This is a workaround to restore async rendering after multiple
        # updates.
        async def _delayed_restore_async_rendering(self, cached_setting):
            # Need 5 updates to avoid hang
            for _ in range(NUM_FRAMES_ASYNC_RENDERING_DELAY):
                await omni.kit.app.get_app().next_update_async()
            # Restore only if still stopped
            if _orchestrator.status == Status.STOPPED:
                carb.settings.get_settings().set("/app/asyncRendering", cached_setting)
                self._cached_async_rendering = None

        if self._cached_async_rendering is not None:
            omni.kit.async_engine.run_coroutine(_delayed_restore_async_rendering(self, self._cached_async_rendering))

        _settings = carb.settings.get_settings()
        if self._cached_settings is not None:
            for settings_path, cached_setting in self._cached_settings.items():
                _settings.set(settings_path, cached_setting)
            self._cached_settings = None
        self._timeline.set_auto_update(True)
        self._timeline.commit_silently()

    def _initialize_call_count(self, instance_type, path):
        """Increment the call count of writer or trigger at path"""
        if instance_type not in ["writer", "trigger"]:
            raise ValueError("`instance_type` must be set to either ``writer`` or 'trigger`")

        if instance_type == "writer":
            self._writer_instances[str(path)] = {"call_count": 0, "active": True}
        elif instance_type == "trigger":
            self._trigger_instances[str(path)] = {"call_count": 0, "active": True}

    def _increment_call_count(self, instance_type, path):
        """Increment the call count of writer or trigger at path"""

        if instance_type == "writer":
            instance = self._writer_instances.setdefault(str(path), {"call_count": 0, "active": True})
        elif instance_type == "trigger":
            instance = self._trigger_instances.setdefault(str(path), {"call_count": 0, "active": True})
        else:
            raise ValueError("`instance_type` must be set to either `writer` or 'trigger`")
        instance["call_count"] += 1

    def _set_active_status(self, instance_type, path, status, end_sim_time: Tuple[int, int] = None):
        """Set active status of writer or trigger at path"""
        if instance_type == "writer":
            instance = self._writer_instances.setdefault(str(path), {"call_count": 0, "active": True})
        elif instance_type == "trigger":
            instance = self._trigger_instances.setdefault(str(path), {"call_count": 0, "active": True})
        else:
            raise ValueError("`instance_type` must be set to either `writer` or 'trigger`")
        instance["active"] = status

    @classmethod
    def _reset_sim_times_to_write(cls):
        cls._sim_times_to_write = deque(maxlen=1000)

    @staticmethod
    def wait_until_complete():
        """Wait until generation and dispatcher have completed (standalone workflow)

        Wait until generation is stopped and all queued writing jobs are completed.

        If status is "STEPPED", stop generation.
        """
        _verify_is_standalone_workflow("wait_until_complete")

        if _orchestrator.status == Status.STEPPED:
            stop()

        while _orchestrator.status not in [Status.STOPPING, Status.STOPPED]:
            omni.kit.app.get_app().update()

        # Wait until the dispatcher shows the last scheduled write frame
        if _orchestrator._sim_times_to_write:
            write_sim_time = (
                _get_time(*_orchestrator._sim_times_to_write[-1]) if _orchestrator._sim_times_to_write else 0.0
            )
            dispatcher = og.get_node_by_path("/Render/PostProcess/SDGPipeline/PostProcessDispatcher")
            if dispatcher:
                cur_time = _get_time(
                    dispatcher.get_attribute("outputs:referenceTimeNumerator").get(),
                    dispatcher.get_attribute("outputs:referenceTimeDenominator").get(),
                )
            else:
                cur_time = 0.0
            last_time = 0.0
            while (
                dispatcher
                and dispatcher.get_attribute("outputs:referenceTimeDenominator").get() > 0
                and dispatcher.get_attribute("outputs:referenceTimeNumerator").get() > 0
                and last_time < cur_time < write_sim_time
            ):
                omni.kit.app.get_app().update()
                if not dispatcher:
                    break
                last_time = cur_time
                cur_time = _get_time(
                    dispatcher.get_attribute("outputs:referenceTimeNumerator").get(),
                    dispatcher.get_attribute("outputs:referenceTimeDenominator").get(),
                )
        # Set status stopped and wait at one frame to allow for status to change from STOPPING->STOPPED
        _orchestrator.status = Status.STOPPED
        omni.kit.app.get_app().update()

        # This keeps the app responsive while jobs get completed
        while not BackendDispatch.is_done_writing():
            omni.kit.app.get_app().update()

        BackendDispatch.wait_until_done()

    @staticmethod
    async def wait_until_complete_async() -> None:
        """Wait until generation and dispatcher have completed

        Wait until generation is stopped and all queued writing jobs are completed.

        If status is "STEPPED", stop generation.
        """
        if _orchestrator.status == Status.STEPPED:
            await stop_async()

        while _orchestrator.status not in [Status.STOPPING, Status.STOPPED]:
            await omni.kit.app.get_app().next_update_async()

        # Wait until the dispatcher shows the last scheduled write frame
        if _orchestrator._sim_times_to_write:
            if _orchestrator._sim_times_to_write:
                write_sim_time = _get_time(*_orchestrator._sim_times_to_write[-1])
            else:
                write_sim_time = 0.0
            dispatcher = og.get_node_by_path("/Render/PostProcess/SDGPipeline/PostProcessDispatcher")
            if dispatcher:
                cur_time = _get_time(
                    dispatcher.get_attribute("outputs:referenceTimeNumerator").get(),
                    dispatcher.get_attribute("outputs:referenceTimeDenominator").get(),
                )
            else:
                cur_time = 0.0
            last_time = 0.0
            while (
                dispatcher
                and dispatcher.get_attribute("outputs:referenceTimeDenominator").get() > 0
                and dispatcher.get_attribute("outputs:referenceTimeNumerator").get() > 0
                and last_time < cur_time < write_sim_time
            ):
                await omni.kit.app.get_app().next_update_async()
                if not dispatcher:
                    break
                last_time = cur_time
                cur_time = _get_time(
                    dispatcher.get_attribute("outputs:referenceTimeNumerator").get(),
                    dispatcher.get_attribute("outputs:referenceTimeDenominator").get(),
                )

        # Set status stopped and wait at one frame to allow for status to change from STOPPING->STOPPED
        _orchestrator.status = Status.STOPPED
        await omni.kit.app.get_app().next_update_async()

        # This keeps the app responsive while jobs get completed
        # Waiting for all queued writing jobs to be completed.
        while not BackendDispatch.is_done_writing():
            await omni.kit.app.get_app().next_update_async()

        BackendDispatch.wait_until_done()


def run(num_frames: int = None, start_timeline: bool = False) -> None:
    """Run the replicator scenario

    Submit the ``Start`` command to replicator without waiting for its status to change to ``Started``.

    Args:
        num_frames: Optionally specify the maximum number of frames to capture. Note that ``num_frames`` does not
            override the number of frames specified in triggers defined in the scene.
        start_timeline: Optionally start the timeline when Replicator starts.
    """
    carb.log_info("Replicator Start")
    _orchestrator.start(num_frames, start_timeline)


async def run_async(num_frames: int = None, start_timeline: bool = False) -> None:
    """Run the replicator scenario and wait for orchestrator to start

    Submit the ``Start`` command to replicator and wait for its status to change to ``Started``.

    Args:
        num_frames: Optionally specify the maximum number of frames to capture. Note that ``num_frames`` does not
            override the number of frames specified in triggers defined in the scene.
        start_timeline: Optionally start the timeline when Replicator starts.
    """
    carb.log_info("Replicator Start Async")
    await _orchestrator.start_async(num_frames, start_timeline)

    # Wait for replicator to start
    while not get_is_started():
        await omni.kit.app.get_app().next_update_async()


def stop() -> None:
    """Stop the replicator scenario

    Submit the ``Stop`` command to replicator without waiting for its status to change to ``Stopped``.
    """
    carb.log_info("Replicator Stop")
    _orchestrator.stop()


async def stop_async() -> None:
    """Stop the replicator scenario and wait until Replicator is stopped

    Submit the ``Stop`` command to replicator and wait for its status to change to ``Stopped``.
    """
    carb.log_info("Replicator Stop Async")
    await _orchestrator.stop_async()


def resume() -> None:
    """Resume a paused replicator scenario

    Submit the ``Resume`` command to replicator without waiting for its status to change to ``Started``.
    """
    # TODO: check if paused
    carb.log_info("Replicator Resume")
    _orchestrator.resume()


def pause() -> None:
    """Pause a running replicator scenario

    Submit the ``Pause`` command to replicator without waiting for its status to change to ``Paused``.
    """
    carb.log_info("Replicator Pause")
    _orchestrator.pause()


def preview() -> None:
    """Run the replicator scenario for a single iteration

    Submit the ``Preview`` command to replicator without waiting for a frame to be previewed.
    Writers are disabled during preview.
    """
    carb.log_info("Replicator Preview")
    _orchestrator.preview()


async def preview_async() -> None:
    """Run the replicator scenario for a single iteration

    Submit the ``Preview`` command to replicator and wait for a frame to be previewed.
    Writers are disabled during preview.
    """
    carb.log_info("Replicator Preview Async")
    await _orchestrator.preview_async()


def wait_until_complete() -> None:
    """Wait until generation is complete (standalone workflow)

    Synchronous function: only use from standalone workflow (controlling Kit app from python).
    Blocks execution until synthetic data generation has completed.
    """
    _verify_is_standalone_workflow("wait_until_complete")
    _orchestrator.wait_until_complete()


async def wait_until_complete_async() -> None:
    """Wait until generation is complete

    Blocks execution until synthetic data generation has completed.
    """
    await _orchestrator.wait_until_complete_async()


async def run_until_complete_async(num_frames: int = None, start_timeline: bool = False) -> None:
    """Run the replicator scenario until stopped
    Generation ends when all triggers have reached their end condition or when a stop event is published.

    Args:
        num_frames: Optionally specify the maximum number of frames to capture. Note that ``num_frames`` does not
            override the number of frames specified in triggers defined in the scene.
        start_timeline: Optionally start the timeline when Replicator starts.
    """
    await run_async(num_frames, start_timeline)

    # Wait for replicator to finish
    # wait for stop so that step_async/pause calls do not register as completion
    while not get_is_stopped():
        await omni.kit.app.get_app().next_update_async()

    await wait_until_complete_async()


def run_until_complete(num_frames: int = None, start_timeline: bool = False) -> None:
    """Run the replicator scenario until stopped (standalone workflow)

    Synchronous function: only use from standalone workflow (controlling Kit app from python).
    Generation ends when all triggers have reached their end condition or when a stop event is published.

    Args:
        num_frames: Optionally specify the maximum number of frames to capture. Note that ``num_frames`` does not
            override the number of frames specified in triggers defined in the scene.
    """
    _verify_is_standalone_workflow("run_until_complete")

    run(num_frames, start_timeline)

    # Wait for replicator to start (warmup period to load materials)
    while not get_is_started():
        omni.kit.app.get_app().update()

    # Wait for replicator to finish
    while get_is_started():
        omni.kit.app.get_app().update()

    wait_until_complete()


def _check_is_standalone_workflow() -> None:
    # LAUNCHED_FROM_TERMINAL means it's running within Kit
    if not hasattr(builtins, "ISAAC_LAUNCHED_FROM_TERMINAL"):
        # If not in Isaac app, not in standalone mode
        return False
    return not builtins.ISAAC_LAUNCHED_FROM_TERMINAL


def _verify_is_standalone_workflow(fn_name: str) -> None:
    if not _check_is_standalone_workflow():
        raise OrchestratorError(
            f"Synchronous call to `{fn_name}` can only be performed in a standalone workflow and may not be made from "
            f"within Kit. Please use the async function `{fn_name}_async`."
        )


async def _next_render_update_async() -> float:
    """Wait for next render update of Omniverse Kit. Returns SWH Frame Number"""

    future = asyncio.Future()

    def on_event(event: carb.events.IEvent):
        if not future.done():
            future.set_result(event.payload)

    # Need assignment to avoid hang
    _sub = carb.eventdispatcher.get_eventdispatcher().observe_event(  # noqa: F841
        order=0,
        event_name=omni.usd.get_context().stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME),
        on_event=on_event,
        observer_name="omni.replicator.core.extension:update",
    )
    return await future


async def step_async(
    rt_subframes: int = -1, pause_timeline: bool = True, delta_time: float = None, wait_for_render: bool = True
) -> None:
    """Step one frame

    If Replicator is not yet started, an initialization step is first taken to ensure the necessary settings are set
    for data capture. The renderer will then render as many subframes as required by current settings and schedule a
    frame to be captured by any active annotators and writers.

    Args:
        rt_subframes: Specify the number of subframes to render. During subframe generation, the simulation is paused.
            This is often beneficial when large scene changes occur to reduce rendering artifacts or to allow materials
            to fully load. This setting is enabled for both RTX Real-Time and Path Tracing render modes. Values must be
            greater than ``0``.
        pause_timeline: If ``True``, pause timeline after step. Defaults to ``True``.
        delta_time: The amount of time that timeline advances for each step call. When delta_time == None, default
            timeline rate will be used. When delta_time == 0.0, timeline will not advance. When delta_time > 0.0,
            timeline will advance by the custom delta_time.
        wait_for_render: If ``True``, wait for a render to complete. Set to ``True`` whenever it is necessary for the
            annotation/writer data match the current simulation state. Defaults to ``True``.
    """
    carb.log_info("Replicator Step")

    # If replicator is stopping, abort step
    if _orchestrator.status == Status.STOPPING:
        carb.log_warn("Replicator is in the process of stopping, step skipped.")
        await omni.kit.app.get_app().next_update_async()
        return

    if _orchestrator.status == Status.STOPPED:
        await _orchestrator._initialize_async()

    if not _orchestrator._is_tick_graph():
        _orchestrator._set_tick_graph()

    is_timeline_auto_updating = _orchestrator._timeline.is_auto_updating()

    # Disable automatic time update when delta_time is not None in timeline so that orchestrator can control step
    # Disable automatic time update for first frame (Status.STARTING) to capture time 0.0
    if delta_time is not None or _orchestrator.status == Status.STARTING:
        _orchestrator._timeline.set_auto_update(False)
        if _orchestrator._step_delta_time and delta_time > _orchestrator._step_delta_time:
            carb.log_warn(
                "Physx tstep is smaller than the user specified delta time, so physx will lag behind. Suggest updating "
                "the physx tstep with rep.settings.set_physx_timestep(...) to equal or be greater than the delta time."
            )

    else:
        _orchestrator._timeline.set_auto_update(is_timeline_auto_updating)
    _orchestrator._timeline.commit_silently()
    _orchestrator._step_delta_time = delta_time

    # If not first frame (STARTING) and capture on play, step forward one frame
    do_motion_blur = carb.settings.get_settings().get_as_bool("/omni/replicator/captureMotionBlur")
    if (
        _orchestrator.status != Status.STARTING
        and carb.settings.get_settings().get("/omni/replicator/captureOnPlay")
        and (
            _orchestrator._timeline.is_auto_updating() or do_motion_blur
        )  # Unless motion blur is enabled, we don't need to update the timeline
    ):
        _orchestrator.status = Status.STEPPING
        _orchestrator._timeline.play()

    # Support for pause timeline feature
    if _orchestrator._resume_play:
        _orchestrator._resume_play = False
        _orchestrator._timeline.play()
        _orchestrator._timeline.commit_silently()

    if rt_subframes > 0:
        _orchestrator.next_rt_subframes = rt_subframes

    # Step one frame (may render multiple subframes)
    _orchestrator.status = Status.STEPPING
    attempts = 0
    cur_sim_time = _get_time(*_orchestrator._sim_times_to_write[-1]) if _orchestrator._sim_times_to_write else 0
    while not _orchestrator._sim_times_to_write or (
        _orchestrator.status == Status.STEPPING
        and cur_sim_time == _get_time(*_orchestrator._sim_times_to_write[-1])
        and attempts < MAX_STEP_ATTEMPTS
    ):
        attempts += 1
        await omni.kit.app.get_app().next_update_async()

    if attempts >= MAX_STEP_ATTEMPTS:
        carb.log_error("Error while stepping, orchestrator failed to schedule a new frame.")

    # Wait for a render
    if wait_for_render:
        write_sim_time = _get_time(*_orchestrator._sim_times_to_write[-1]) if _orchestrator._sim_times_to_write else 0.0
        dispatcher = og.get_node_by_path("/Render/PostProcess/SDGPipeline/PostProcessDispatcher")

        # Pause
        _orchestrator._timeline.set_auto_update(False)
        _orchestrator._timeline.commit_silently()

        while (
            dispatcher
            and _get_time(
                dispatcher.get_attribute("outputs:referenceTimeNumerator").get(),
                dispatcher.get_attribute("outputs:referenceTimeDenominator").get(),
            )
            < write_sim_time
        ):
            await _next_render_update_async()

    # Restore auto-updating status
    _orchestrator._timeline.set_auto_update(is_timeline_auto_updating)
    _orchestrator._timeline.commit_silently()
    # PT only, changing motion blur setting in RT causes issue in 106.2
    _orchestrator._undo_motion_blur_settings(pt_only=True)

    if pause_timeline:
        _orchestrator._resume_play = _orchestrator._timeline.is_playing()  # only set resume flag if timeline is playing
        _orchestrator._timeline.pause()
        _orchestrator._timeline.commit_silently()


def step(
    rt_subframes: int = -1, pause_timeline: bool = True, delta_time: float = None, wait_for_render: bool = True
) -> None:
    """Step one frame (standalone workflow)

    Synchronous step function: only use from standalone workflow (controlling Kit app from python).
    If Replicator is not yet started, an initialization step is first taken to ensure the necessary settings are set
    for data capture. The renderer will then render as many subframes as required by current settings and schedule a
    frame to be captured by any active annotators and writers.

    Args:
        rt_subframes: Specify the number of subframes to render. During subframe generation, the simulation is paused.
            This is often beneficial when large scene changes occur to reduce rendering artifacts or to allow materials
            to fully load. This setting is enabled for both RTX Real-Time and Path Tracing render modes. Values must be
            greater than ``0``.
        pause_timeline: If ``True``, pause timeline after step. Defaults to ``True``.
        delta_time: The amount of time that timeline advances for each step call. When delta_time == None, default
            timeline rate will be used. When delta_time == 0.0, timeline will not advance. When delta_time > 0.0,
            timeline will advance by the custom delta_time.
        wait_for_render: If ``True``, wait for a render to complete. Set to ``True`` whenever it is necessary for the
            annotation/writer data match the current simulation state. Defaults to ``True``.
    """
    carb.log_info("Replicator Step")

    _verify_is_standalone_workflow("step")

    # If replicator is stopping, abort step
    if _orchestrator.status == Status.STOPPING:
        carb.log_warn("Replicator is in the process of stopping, step skipped.")
        omni.kit.app.get_app().update()
        return

    if _orchestrator.status == Status.STOPPED:
        _orchestrator._initialize()

    if not _orchestrator._is_tick_graph():
        _orchestrator._set_tick_graph()

    is_timeline_auto_updating = _orchestrator._timeline.is_auto_updating()

    # Disable automatic time update when delta_time is not None in timeline so that orchestrator can control step
    # Disable automatic time update for first frame (Status.STARTING) to capture time 0.0
    if delta_time is not None or _orchestrator.status == Status.STARTING:
        _orchestrator._timeline.set_auto_update(False)
        if _orchestrator._step_delta_time and delta_time > _orchestrator._step_delta_time:
            carb.log_warn(
                "Physx tstep is smaller than the user specified delta time, so physx will lag behind. Suggest updating "
                "the physx tstep with rep.settings.set_physx_timestep(...) to equal or be greater than the delta time."
            )

    else:
        _orchestrator._timeline.set_auto_update(is_timeline_auto_updating)
    _orchestrator._timeline.commit_silently()
    _orchestrator._step_delta_time = delta_time

    # If not first frame (STARTING) and capture on play, step forward one frame
    do_motion_blur = carb.settings.get_settings().get_as_bool("/omni/replicator/captureMotionBlur")
    if (
        _orchestrator.status != Status.STARTING
        and carb.settings.get_settings().get("/omni/replicator/captureOnPlay")
        and (
            _orchestrator._timeline.is_auto_updating() or do_motion_blur
        )  # Unless motion blur is enabled, we don't need to update the timeline
    ):
        _orchestrator.status = Status.STEPPING
        _orchestrator._timeline.play()

    # Support for pause timeline feature
    if _orchestrator._resume_play:
        _orchestrator._resume_play = False
        _orchestrator._timeline.play()
        _orchestrator._timeline.commit_silently()

    if rt_subframes > 0:
        _orchestrator.next_rt_subframes = rt_subframes

    # Step one frame (may render multiple subframes)
    _orchestrator.status = Status.STEPPING
    attempts = 0
    cur_sim_time = _get_time(*_orchestrator._sim_times_to_write[-1]) if _orchestrator._sim_times_to_write else 0
    while not _orchestrator._sim_times_to_write or (
        _orchestrator.status == Status.STEPPING
        and cur_sim_time == _get_time(*_orchestrator._sim_times_to_write[-1])
        and attempts < MAX_STEP_ATTEMPTS
    ):
        attempts += 1
        omni.kit.app.get_app().update()

    if attempts >= MAX_STEP_ATTEMPTS:
        carb.log_error("Error while stepping, orchestrator failed to schedule a new frame.")

    # Wait for a render
    if wait_for_render:
        write_sim_time = _get_time(*_orchestrator._sim_times_to_write[-1]) if _orchestrator._sim_times_to_write else 0.0
        dispatcher = og.get_node_by_path("/Render/PostProcess/SDGPipeline/PostProcessDispatcher")

        # Pause
        _orchestrator._timeline.set_auto_update(False)
        _orchestrator._timeline.commit_silently()

        while (
            dispatcher
            and _get_time(
                dispatcher.get_attribute("outputs:referenceTimeNumerator").get(),
                dispatcher.get_attribute("outputs:referenceTimeDenominator").get(),
            )
            < write_sim_time
        ):
            omni.kit.app.get_app().update()

    # Restore auto-updating status
    _orchestrator._timeline.set_auto_update(is_timeline_auto_updating)
    _orchestrator._timeline.commit_silently()
    # PT only, changing motion blur setting in RT causes issue in 106.2
    _orchestrator._undo_motion_blur_settings(pt_only=True)

    if pause_timeline:
        _orchestrator._resume_play = _orchestrator._timeline.is_playing()  # only set resume flag if timeline is playing
        _orchestrator._timeline.pause()
        _orchestrator._timeline.commit_silently()


def register_status_callback(callback: Callable) -> StatusCallback:
    """Register a callback on orchestrator status changed.

    Register a callback and return a StatusCallback object that automatically unregisters callback when destroyed.

    Args:
        callback: Callback function that will be called whenever orchestrator status changes

    Returns:
        StatusCallback object which will automatically unregister callback when destroyed

    Example:
        >>> import omni.replicator.core as rep
        >>> def my_callback(status):
        ...     print(f"Orchestrator Status: {status}")
        >>> # register callback
        >>> my_callback = rep.orchestrator.register_status_callback(my_callback)
        >>> my_callback2 = rep.orchestrator.register_status_callback(my_callback)
        >>> # unregister callback manually
        >>> my_callback.unregister()
        >>> # unregister callback automatically
        >>> del(my_callback)
    """
    status_callback = StatusCallback(callback)
    status_callback.register()

    return status_callback


def get_is_started() -> bool:
    """Return ``True`` if Replicator is Started."""
    return _orchestrator.status == Status.STARTED


def get_is_paused() -> bool:
    """Return ``True`` if Replicator is Paused."""
    return _orchestrator.status == Status.PAUSED


def get_status() -> Status:
    """Return Replicator status"""
    return _orchestrator.status


def get_is_stopped() -> bool:
    """Return ``True`` if Replicator is Stopped."""
    return _orchestrator.status == Status.STOPPED


def _release_trigger(trigger_path):
    if trigger_path in _orchestrator._trigger_instances:
        _orchestrator._trigger_instances.pop(trigger_path)


def get_sim_times_to_write() -> List:
    """Get list of simulation times scheduled to be written"""
    return _orchestrator._sim_times_to_write


def _add_named_node(name, node):
    NamedNodes.add(name, node)


def _get_distribution_values(reference_time: Tuple[int, int]) -> dict:
    return NamedNodes._get_distribution_values(reference_time)


def _get_trigger_values(reference_time: Tuple[int, int]) -> dict:
    return NamedNodes._get_trigger_values(reference_time)


def _get_named_node_values(reference_time: Tuple[int, int]) -> dict:
    return NamedNodes._get_named_node_values(reference_time)


def set_next_rt_subframes(rt_subframes: int) -> None:
    """Specify the number of subframes to render

    Specify the number of subframes to render. During subframe generation, the simulation is paused.
    This is often beneficial when large scene changes occur to reduce rendering artifacts or to allow materials
    to fully load. This setting is enabled for both RTX Real-Time and Path Tracing render modes. Values must be
    greater than ``0``.

    Args:
        rt_subframes: Number of subframes to render for the next frame. Resets on every frame.
    """
    _orchestrator.next_rt_subframes = rt_subframes


def set_minimum_next_rt_subframes(rt_subframes: int) -> None:
    """Specify the minimum number of subframes to render

    Specify the minimum number of subframes to render. During subframe generation, the simulation is paused.
    This is often beneficial when large scene changes occur to reduce rendering artifacts or to allow materials
    to fully load. This setting is enabled for both RTX Real-Time and Path Tracing render modes. Values must be
    greater than ``0``.

    Args:
        rt_subframes: Minimum number of subframes to render for the next frame. Resets on every frame.
    """
    if rt_subframes > _orchestrator.next_rt_subframes:
        _orchestrator.next_rt_subframes = rt_subframes


def set_capture_on_play(value: bool) -> None:
    """Set Replicator to capture on timeline playing.

    When capture on play is enabled, timeline operations (ie. Play, Stop, Pause) will trigger the corresponding
    Replicator commands.

    Args:
        value (bool): If ``True``, Replicator will engage when timeline is playing to capture frames.
    """
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", value)
