# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import json
import logging

import carb.dictionary

logger = logging.getLogger(__name__)


REGISTRY_FILENAME_LOCAL = "registry.json"
REGISTRY_FILENAME_REMOTE = "registry.gz"


class RegistryFile:
    def __init__(self, index_cache_path):
        self.path = f"{index_cache_path}/{REGISTRY_FILENAME_LOCAL}"

        data = {}
        try:
            with open(self.path, "r") as f:
                data = json.loads(f.read())
        except FileNotFoundError as e:
            carb.log_info(f"Local registry index not found: {self.path}. First time syncing.")

        self.set_data(data)

    def set_data(self, data):
        self._data = data
        self.files = self._data.get("files", {})

    def save(self):
        self._data["files"] = self.files
        with open(self.path, "w") as f:
            f.write(json.dumps(self._data, indent=4))
