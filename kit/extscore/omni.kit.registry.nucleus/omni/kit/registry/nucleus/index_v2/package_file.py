# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import json
import os

from ..utils.common import get_ext_fullname_version, new_dict_with_filter
from ..utils.semver import SemanticVersion


PACKAGE_FILE_KEYS = [
    "package/packageId",
    "package/id",
    "package/name",
    "package/version",
    "package/metadata",
    "package/archivePath",
    "package/archiveSubdir",
    "package/publish/date",
    "package/yanked",
    "core/order",
    "package/target",
    "dependencies",
]


class PackageFile:
    def __init__(self, path: str):
        self.path = path
        self._data = {}

        # create dirs if new
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            # parse from existing
            with open(path, "r") as f:
                for line in f.read().splitlines():
                    if not line:
                        break
                    package_id, data = line.split(" ", maxsplit=1)
                    self._data[package_id] = data

    def apply_change(self, package_id: str, ext_data: dict, add: bool) -> bool:
        if add:
            return self.add(package_id, ext_data)
        else:
            return self.remove(package_id)

    def add(self, package_id: str, ext_data: dict) -> bool:
        # prune
        ext_data = new_dict_with_filter(ext_data, PACKAGE_FILE_KEYS)

        self._data[package_id] = json.dumps(ext_data, indent=None)
        return True

    def remove(self, package_id: str) -> bool:
        if package_id not in self._data:
            return False

        del self._data[package_id]
        return True

    def get_package_dict(self, package_id: str) -> dict:
        data = self._data.get(package_id, None)
        return json.loads(data) if data else None

    def save(self):
        # Sort in reverse version order. So that highest versions go first (they are more likely to be used)

        def _sort_key(x):
            name, version = get_ext_fullname_version(x)
            return (name, SemanticVersion.parse(version))

        self._data = {
            key: self._data[key] for key in sorted(self._data.keys(), key=lambda x: _sort_key(x), reverse=True)
        }
        with open(self.path, "w") as f:
            for package_id, data in self._data.items():
                f.write(f"{package_id} {data}\n")

    def get_latest_package_id(self) -> str:
        if len(self._data) == 0:
            return None
        return next(iter(self._data))
