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

import time

from .. import annotators
from ..writers import Writer


class FPSWriter(Writer):
    """Record Writer FPS

    Writer that can be attached to record and print out writer FPS. Typically attached together with another writer.

    .. note::
        Writer does not write any data.

    """

    def __init__(self):
        self._last_frame_time = None
        self._times_per_frame = []
        self.annotators = [annotators.get("LdrColor", device="cuda")]

    def write(self, data):
        if self._last_frame_time is None:
            self._last_frame_time = time.time()
            return

        time_per_frame = time.time() - self._last_frame_time
        print(time_per_frame)
        self._times_per_frame.append(time_per_frame)
        self._last_frame_time = time.time()

    def on_final_frame(self):
        time_per_frame = sum(self._times_per_frame) / len(self._times_per_frame)
        print("COMPLETE")
        print(f"AVERAGE TIME PER FRAME: {time_per_frame}")
        print(f"AVERAGE FPS: {1. / time_per_frame}")
