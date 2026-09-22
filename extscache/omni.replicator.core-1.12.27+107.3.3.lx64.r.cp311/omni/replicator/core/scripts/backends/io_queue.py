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

import atexit
import threading
import time
from collections import deque
from functools import partial
from typing import Callable

import carb

from .telemetry import telemetry

QUEUE_SIZE = 1000
NUM_THREADS = 4
NUM_THREADS_SETTING = "/omni/replicator/backend/writeThreads"
NUM_THREADS_SETTING_OLD = "/omni/replicator/render/write_threads"  # kept for backwards compatibility
QUEUE_SIZE_SETTING = "/omni/replicator/backend/queueSize"


class _DataWriteQueue:
    def __init__(self):
        self.q = None
        self.threads = []

    def _initialize(self):
        self.__setting_subs = []
        atexit.register(self.destroy)
        settings_iface = carb.settings.get_settings()

        # Setting number of IO threads
        self.num_worker_threads = settings_iface.get_as_int(NUM_THREADS_SETTING)  # check with new setting
        if not self.num_worker_threads:
            self.num_worker_threads = settings_iface.get_as_int(NUM_THREADS_SETTING_OLD)  # check with old setting
        if not self.num_worker_threads:
            carb.log_info(
                f"No backend number of threads setting found at `{NUM_THREADS_SETTING}`, defaulting to {NUM_THREADS} threads."
            )
            self.num_worker_threads = NUM_THREADS
        self.__setting_subs.append(
            settings_iface.subscribe_to_node_change_events(NUM_THREADS_SETTING, self._on_num_threads_setting_change)
        )

        # Setting max queue size
        self.max_queue_size = settings_iface.get(QUEUE_SIZE_SETTING)
        if not self.max_queue_size:
            carb.log_info(
                f"No backend queue size setting found at `{QUEUE_SIZE_SETTING}`, defaulting to {QUEUE_SIZE} threads."
            )
            self.max_queue_size = QUEUE_SIZE
        self.__setting_subs.append(
            settings_iface.subscribe_to_node_change_events(QUEUE_SIZE_SETTING, self._on_queue_size_setting_change)
        )

        self._has_warned_max_queue = False
        self.q = deque()
        self.start_threads()
        self._unfinished_tasks = deque()

    def _on_num_threads_setting_change(self, new_value, event):
        new_value = carb.settings.get_settings().get_as_int(NUM_THREADS_SETTING)
        if new_value < 1:
            carb.log_error(
                f"Minimum number of threads is 1, received {new_value}. Thread count remains at {self.num_worker_threads}"
            )
            return
        carb.log_warn(f"Changing number of backend write threads to `{new_value}`")
        self.num_worker_threads = new_value
        self.wait_until_done()
        self.threads = []
        self.start_threads()

    def _on_queue_size_setting_change(self, new_value, event) -> None:
        new_value = carb.settings.get_settings().get_as_int(QUEUE_SIZE_SETTING)
        if new_value < 1:
            carb.log_error(
                f"Minimum queue size is 1, received {new_value}. Queue size remains at {self.max_queue_size}"
            )
            return
        carb.log_warn(f"Changing backend queue size to `{new_value}`")
        self.max_queue_size = new_value

    def wait_if_max_queue_size(self) -> None:
        """Wait if maximum queue size is reached

        Block further data generation until queue size falls back below
        maximum limit.
        """
        if self.q is None:
            return
        if len(self.q) > self.max_queue_size:
            time.sleep(0.1)
            if not self._has_warned_max_queue:
                carb.log_warn("Throttling generation due to I/O bottleneck.")
                self._has_warned_max_queue = True

    def start_threads(self) -> None:
        """Start threads"""
        if self.q is None:
            self._initialize()
        # Start worker threads
        for _ in range(self.num_worker_threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.threads.append(t)

    def is_done_writing(self) -> bool:
        """If the queue is empty, return ``True``"""
        if self.q is None:
            return True
        return len(self.q) == 0 and len(self._unfinished_tasks) == 0

    def wait_until_done(self) -> None:
        """Wait until data queue is fully processed

        Blocks execution until ``is_done_writing() == True``.
        """
        if self.q is None:
            return

        carb.profiler.begin(126, f"Data Queue - wait_until_done")
        if not self.is_done_writing():
            carb.log_info(f"Finish writing data: {len(self.q) + len(self._unfinished_tasks)} tasks remaining...")

        # wait until all jobs are done
        while not self.is_done_writing():
            time.sleep(0.1)

        if self.is_done_writing():
            carb.log_info("All data I/O tasks complete.")
        carb.profiler.end(126)

    def destroy(self) -> None:
        """Destroy threads"""
        self.wait_until_done()

        if self.q is not None:
            carb.log_info("Tearing down DataWriteQueue threads...")

            # Stop workers
            for _ in range(self.num_worker_threads):
                self.q.append(None)
            for t in self.threads:
                t.join()

            carb.log_info("Done tearing down DataWriteQueue threads.")

        settings_iface = carb.settings.get_settings()
        for setting_sub in self.__setting_subs:
            settings_iface.unsubscribe_to_change_events(setting_sub)

    def do_work(self, payload: Callable) -> None:
        # Resolve partials
        for idx in range(len(payload.args)):
            if isinstance(payload.args[idx], partial):
                payload.args[idx] = payload.args[idx]()
        for key in payload.keywords:
            if isinstance(payload.keywords[key], partial):
                payload.keywords[key] = payload.keywords[key]()

        payload()

    def worker(self) -> None:
        while True:
            if len(self.q) == 0:
                carb.profiler.begin(232, "backend worker sleep")
                time.sleep(0.01)
                carb.profiler.end(232)
                continue
            payload = self.q.popleft()
            self._unfinished_tasks.append(True)
            if payload is None:
                break
            try:
                carb.profiler.begin(233, "backend worker payload")
                self.do_work(payload)
                carb.profiler.end(233)
            except Exception as e:
                carb.log_error(payload)
                carb.log_error("Error detected during Omni.Replicator.backend worker write\n")
                carb.log_error(e)
            self._unfinished_tasks.pop()

    def put(self, task: Callable) -> None:
        if self.q is None:
            self._initialize()
        self.q.append(task)


data_queue = _DataWriteQueue()


def is_done_writing() -> bool:
    """If the queue is empty, return ``True``"""
    if data_queue.is_done_writing():
        telemetry.record_file_types()
        return True
    else:
        return False


@staticmethod
def wait_until_done() -> None:
    """Wait until data queue is fully processed

    Blocks execution until ``is_done_writing() == True``.
    """
    data_queue.wait_until_done()


@staticmethod
def set_max_queue_size(value: int) -> None:
    """Set maximum queue size

    On systems with more available memory, increasing the queue size can
    reduce instances where I/O bottlenecks data generation.
    """
    data_queue.max_queue_size = int(value)
