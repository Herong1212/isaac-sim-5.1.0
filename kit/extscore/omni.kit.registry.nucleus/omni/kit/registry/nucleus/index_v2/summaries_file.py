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
import logging

import carb.dictionary

from ..utils.common import get_ext_fullname_version, new_dict_with_filter
from ..utils.semver import SemanticVersion
from ..registry_globals import RegistryGlobals
from .package_file import PACKAGE_FILE_KEYS, PackageFile


logger = logging.getLogger(__name__)


SUMMARIES_FILENAME_LOCAL = "summaries.json"
SUMMARIES_FILENAME_REMOTE = "summaries.gz"

SUMMARIES_FILE_KEYS = PACKAGE_FILE_KEYS + [
    "package/publish/buildNumber",
    "package/kitVersion",
    "package/title",
    "package/category",
    "package/authors",
    "package/repository",
    "package/keywords",
    "package/preview_image",
    "package/icon",
    "package/preview_image_remote",
    "package/icon_remote",
]

META_KEY = "#meta"


class SummariesFile:
    def __init__(self, index_cache_path):
        self._index_cache_path = index_cache_path
        self.path = f"{index_cache_path}/{SUMMARIES_FILENAME_LOCAL}"
        self.exts = {}

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write("{}")

        self.carb_dict = carb.dictionary.get_json_serializer().create_dictionary_from_file(self.path)
        if self.carb_dict is None:
            raise Exception(f"Failed to load summaries from {self.path}")

        # communicate back local cache path using an old #meta key, can be changed to be API in the future
        self._write_meta()

        # parse keys, map extension name to id (can be deferred until we add)
        self.keys = self.carb_dict.get_keys()
        for ext_id in self.keys:
            ext_name, ext_version = get_ext_fullname_version(ext_id)
            if ext_name in self.exts:
                logger.warning(
                    f"Duplicate extension version for {ext_name} ({ext_id} and {self.exts[ext_name]}) in {self.path}"
                )
            self.exts[ext_name] = ext_id

    def _write_meta(self):
        d = carb.dictionary.get_dictionary()
        meta = {}
        meta["local_cache_path"] = self._index_cache_path
        d.set(self.carb_dict, META_KEY, meta)

    def destroy(self, globals: RegistryGlobals):
        if self.carb_dict:
            globals.defer_destroy_index(self.carb_dict)
            self.carb_dict = None

    def apply_change(self, ext_id: str, ext_data: dict, add: bool, package_file: PackageFile) -> bool:
        ext_name, ext_version = get_ext_fullname_version(ext_id)

        d = carb.dictionary.get_dictionary()

        if ext_name in self.exts:
            other_ext_id = self.exts[ext_name]
            other_ext_name, other_ext_version = get_ext_fullname_version(other_ext_id)
            if SemanticVersion.parse(other_ext_version) > SemanticVersion.parse(ext_version):
                # newer already
                return False
            else:
                # delete prev
                item = d.get_item(self.carb_dict, other_ext_id)
                if item != None:
                    d.destroy_item(item)
                del self.exts[ext_name]

                # put next latest package (if any) to summaries if we are removing
                if not add:
                    latest_package_id = package_file.get_latest_package_id()
                    if latest_package_id:
                        self._add_ext(latest_package_id, package_file.get_package_dict(latest_package_id))
                    return True

        if add and ext_data:
            self._add_ext(ext_id, ext_data)

        return True

    def _add_ext(self, ext_id: str, ext_data: dict):
        ext_name, _ = get_ext_fullname_version(ext_id)
        d = carb.dictionary.get_dictionary()
        # only write defined keys to keep size small. Have not found other way to do python dict -> carb dict, but to use json
        temp_item = carb.dictionary.get_json_serializer().create_dictionary_from_string_buffer(json.dumps(ext_data))
        d.update(self.carb_dict, ext_id, temp_item, "", carb.dictionary.UpdateAction.OVERWRITE)
        d.destroy_item(temp_item)
        self.exts[ext_name] = ext_id

    def save(self):
        # remove meta not to store in file
        d = carb.dictionary.get_dictionary()
        meta = d.get_item(self.carb_dict, META_KEY)
        if meta != None:
            d.destroy_item(meta)
        # serialize
        carb.dictionary.get_json_serializer().save_file_from_dictionary(self.carb_dict, self.path, 0)
        # restore meta
        self._write_meta()
