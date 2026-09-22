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

from omni.replicator.core.bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0

DEFAULT_BACKENDS = ["Disk", "S3"]


class DataWriteTelemetry:
    def __init__(self) -> None:
        self.telemetry = Schema_omni_replicator_extinfo_1_0()
        self.file_types = set([])
        self._recorded_backends = []

    def record_backend(self, backend_type, file_type):
        if backend_type not in self._recorded_backends:
            if backend_type not in DEFAULT_BACKENDS:
                self.telemetry.backend_sendEvent("Custom Backend")
            else:
                self.telemetry.backend_sendEvent(backend_type)
            self._recorded_backends.append(backend_type)

        self.file_types.add(file_type)

    def record_file_types(self):
        for t in list(self.file_types):
            self.telemetry.dispatcher_sendEvent(t)
        self.file_types.clear()


telemetry = DataWriteTelemetry()
