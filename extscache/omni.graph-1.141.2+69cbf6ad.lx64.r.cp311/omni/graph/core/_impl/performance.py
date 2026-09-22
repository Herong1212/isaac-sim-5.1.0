"""Helpers for running performance tests on OmniGraph objects."""

import re
from contextlib import suppress
from typing import Dict, List

import carb
import carb.profiler
import omni.graph.core as og

# Regular expression matching event descriptions for node compute timing
RE_COMPUTE_EVENT = re.compile(r"(Py)?Compute\s+(.*)")


class OmniGraphPerformance:
    """Provides simple interfaces for measuring performance of OmniGraph.

    For simplicity, the collection is kept separate from the interpretation of the data. That way multiple
    collections can be made and summarized separately.

    Normal usage is something like this:
        p = og.OmniGraphPerformance()
        p.start_monitor()
        profile_task = asyncio.create_task(measure_results())
        p.end_monitor()

        async def measure_results():
            timing_task = p.measure_timing()
            await timing_task
            ids = timing_task.result()
            display(ids, p.average_node_evaluation_time())

    Internal Members:
        __capture_enabled: True when the profiler capturing is running
        __enabled_capture_mask: Profiler mask value to enable data capture, filtered for any settings
        __nodes_captured: Union of all nodes in the various capture sessions; for convenience when reporting
        __iprofiler: Interface for the profiler to collect CPU timing
        __iprofiler_monitor: Interface for the profiler loading of collecting timing data
        __old_capture_mask: Saved capture mask when the profiler is engaged (None when not running)
        __results: List of dictionaries with timing results
        __settings: Access to profiler settings
    """

    def __init__(self):
        """Set up the profiling interface objects, logging a warning if it doesn't exist.
        This allows the functions to silently fail, while still providing an alert to the user as to why their
        operations might not work as expected.
        """
        try:
            self.__iprofiler = carb.profiler.acquire_profiler_interface()
            self.__iprofiler_monitor = carb.profiler.acquire_profile_monitor_interface()
            self.__settings = carb.settings.get_settings()
            if self.__iprofiler is None:
                raise RuntimeError("Could not load the profiler interface")
            if self.__iprofiler_monitor is None:
                raise RuntimeError("Could not load the profiler monitor interface")
        except RuntimeError as error:
            carb.log_warn(f"RuntimeError {error} - data will not be collected")

        self.__results = []
        self.__nodes_captured = set()
        self.__old_capture_mask = None
        self.__capture_enabled = False

        if self.__settings:
            mask = self.__settings.get_as_int("/app/profilerMask")
            if mask < 0:
                # since get_as_int() returns a signed value, and set_capture_mask() requires an unsigned value, and the
                # default value is all bits set (which python interprets as -1), we convert to a positive number here.
                mask = mask + 0x010000000000000000
            self.__enabled_capture_mask = mask
        else:
            self.__enabled_capture_mask = 0x0FFFFFFFFFFFFFFFF

    # ----------------------------------------------------------------------
    def available(self) -> bool:
        """Returns true if the profiling capabilities are available"""
        return self.__iprofiler is not None and self.__iprofiler_monitor is not None and self.__capture_enabled

    # ----------------------------------------------------------------------
    def clear(self):
        """Clear out any timing data saved so far"""
        self.__results = []

    # ----------------------------------------------------------------------
    def memory_in_use(self) -> int:
        """Return the current number of bytes in use by Fabric"""
        return og.OmniGraphInspector().memory_use(og.get_compute_graph_contexts()[0])

    # ----------------------------------------------------------------------
    def start_monitor(self):
        """Set up the profiler for capturing - must be done before measuring timing"""
        if not self.__capture_enabled:
            self.__old_capture_mask = self.__iprofiler.get_capture_mask()
            self.__iprofiler.set_capture_mask(self.__enabled_capture_mask)
            self.__capture_enabled = True
        else:
            carb.log_warn("Tried to enable capture when it was already enabled")

    # ----------------------------------------------------------------------
    def end_monitor(self):
        """Set up the profiler to finish capturing"""
        if self.__old_capture_mask is None or not self.__capture_enabled:
            carb.log_warn("Tried to stop capture before starting")
        else:
            self.__iprofiler.set_capture_mask(self.__old_capture_mask)
        self.__old_capture_mask = None
        self.__capture_enabled = False

    # ----------------------------------------------------------------------
    async def measure_timing(self, iterations: int = 1) -> List[int]:
        """Add a set of evaluation timing information to the current data.
        You can either take multiple sets of timing here by setting the iterations value, or you can call this
        method multiple times when you make changes.

        Args:
            iterations: Number of times to measure the timing.

        Returns:
            List of IDs for the timing(s) taken.
        """
        if not self.available():
            return []

        self.clear()
        id_list = []
        for _run in range(iterations):
            id_list.append(len(self.__results))
            this_run = {}
            await og.Controller.evaluate()

            events = self.__iprofiler_monitor.get_last_profile_events()
            collected_data = events.get_profile_events(events.get_main_thread_id())
            for data in collected_data:
                node_match = RE_COMPUTE_EVENT.match(data["name"])
                if node_match:
                    node_name = node_match.group(2)
                    this_run[node_name] = getattr(this_run, node_name, 0.0) + data["duration"]
                    self.__nodes_captured.add(node_name)

            self.__results.append(this_run)

        return id_list

    # ----------------------------------------------------------------------
    def average_node_evaluation_time(self) -> Dict[str, float]:
        """Average out the node evaluation timing information for all runs for each node.

        Returns:
            Dictionary of NodePath:EvaluationTime for each node in the timing set.
        """
        if not self.available():
            return {}

        evaluation_times = {}
        for node_name in self.__nodes_captured:
            timing = 0.0
            count = 0
            for run in self.__results:
                with suppress(KeyError):
                    timing += run[node_name]
                    count += 1
            if count > 0:
                evaluation_times[node_name] = timing / float(count)

        return evaluation_times

    # ----------------------------------------------------------------------
    def average_event_time(self, event_regex: str) -> Dict[str, float]:
        """Average out the named event timing information for all runs for each node.

        Args:
            event_regex: Regular expression identifying the event specific to the type of node data being collected

        Returns:
            Dictionary of NodePath:EvaluationTime for each node in the timing set.
        """
        if not self.available():
            return {}

        evaluation_times = {}
        for node_name in self.__nodes_captured:
            timing = 0.0
            count = 0
            for run in self.__results:
                with suppress(KeyError):
                    timing += run[node_name]
                    count += 1
            if count > 0:
                evaluation_times[node_name] = timing / float(count)

        return evaluation_times
