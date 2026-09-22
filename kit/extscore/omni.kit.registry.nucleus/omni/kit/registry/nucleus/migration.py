# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ext
import omni.kit.app
import omni.client
import carb.dictionary

from .utils.common import _print, get_ext_fullname_version, _get_setting
from .utils.semver import SemanticVersion
from .utils.omni_client_utils import omni_client_exists, omni_client_copy, omni_client_read_file

from .index_v1.index import RegistryIndexV1
from .index_v2.index import RegistryIndexV2


def migrate_v1_to_v2(index_v1: RegistryIndexV1, index_v2: RegistryIndexV2, overwrite: bool = False):
    _print(f"Migrating registry index from v1 to v2: {index_v1._urls.index} -> {index_v2._urls.index}")
    # v1 has a full index
    d = carb.dictionary.get_dictionary()
    index_dict_v1 = index_v1.get_index_dict()
    for package_id in index_dict_v1.get_keys():
        # skip #meta
        if package_id.startswith("#"):
            continue

        package_name, version = get_ext_fullname_version(package_id)
        try:
            SemanticVersion.parse(version)
        except ValueError as e:
            carb.log_error(f"Invalid version for package {package_id}. Not a semver. Error: {e}. Skipping...")
            continue

        if not index_v2.get_package_dict(package_id) or overwrite:
            _print(f"[migration] Adding package {package_id} to index: {index_v2._urls.index}")

            ext_dict = d.get_item(index_dict_v1, package_id)

            # reference archives in old location
            archive_remote = ext_dict.get("package/archivePath", "")
            if archive_remote.startswith("./"):
                archive_remote = "./../3/" + archive_remote[2:]
                d.set(ext_dict, "package/archivePath", archive_remote)

            # copy meta json files
            for possible_subpath in ["archives", f"archives/{package_name}"]:
                meta_json_v1 = f"{index_v1._urls.index}/{possible_subpath}/{package_id}.json"
                meta_json_v2 = f"{index_v2._urls.index}/archives/{package_name}/{package_id}.json"
                if omni_client_exists(meta_json_v1) and not omni_client_exists(meta_json_v2):
                    r = omni_client_copy(
                        meta_json_v1, meta_json_v2, reason="meta json copy", behavior=omni.client.CopyBehavior.OVERWRITE
                    )
                    _print(f"[migration] copied {meta_json_v1} -> {meta_json_v2} (copy result: {r})!")

            index_v2.add_to_index(package_id, ext_dict.get_dict())


def migrate_v2_to_v1(index_v2: RegistryIndexV2, index_v1: RegistryIndexV1, overwrite: bool = False):
    _print(f"Migrating registry index from v2 to v1: {index_v2._urls.index} -> {index_v1._urls.index}")

    d = carb.dictionary.get_dictionary()
    index_dict_v2 = index_v2.get_index_dict()
    all_package_ids = set()
    for package_id in index_dict_v2.get_keys():
        package_file = index_v2._index_sync.get_or_create_package_file(package_id)
        all_package_ids.update(package_file._data.keys())

    for package_id in all_package_ids:
        package_name, version = get_ext_fullname_version(package_id)
        d = carb.dictionary.get_dictionary()
        if not index_v1.get_package_dict(package_id) or overwrite:
            _print(f"[migration] Adding package {package_id} to index: {index_v1._urls.index}")

            # use meta json files as a source of ext_dict
            meta_json_v1 = f"{index_v1._urls.index}/archives/{package_name}/{package_id}.json"
            meta_json_v2 = f"{index_v2._urls.index}/archives/{package_name}/{package_id}.json"
            if not omni_client_exists(meta_json_v2):
                carb.log_error(f"Meta json file {meta_json_v2} does not exist. Skipping...")
                continue

            result, content = omni_client_read_file(meta_json_v2)
            content = memoryview(content).tobytes().decode("utf-8")
            ext_dict = carb.dictionary.get_json_serializer().create_dictionary_from_string_buffer(content)

            # reference archives in old location
            archive_remote = ext_dict.get("package/archivePath", "")
            if archive_remote.startswith("./"):
                archive_remote = "./../v2/" + archive_remote[2:]
                d.set(ext_dict, "package/archivePath", archive_remote)


            if not omni_client_exists(meta_json_v1):
                r = omni_client_copy(
                    meta_json_v2, meta_json_v1, reason="meta json copy", behavior=omni.client.CopyBehavior.OVERWRITE
                )
                _print(f"[migration] copied {meta_json_v2} -> {meta_json_v1} (copy result: {r})!")

            index_v1.add_to_index(package_id, ext_dict.get_dict())
