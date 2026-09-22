# Copyright (c) 2020-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# pragma: no cover

import omni.client as client

import os.path
from os import stat_result
import pathlib
from typing import List, Tuple


def _stat(path: str) -> client.ListEntry:
    result, list_entry = client.stat(path)
    if result == client.Result.OK:
        return list_entry
    else:
        return None


def is_omni_path(path: str) -> bool:
    return path.startswith("omni") or path.startswith("http")


def join(left: str, right: str) -> str:
    if is_omni_path(left):
        if not left.endswith("/") and is_folder(left):
            left = left + "/"
        if right.startswith("/") and filename_from_path:
            right = right[1:]

        return client.combine_urls(left, right)
    else:
        return os.path.join(left, right)


def containing_folder(path: str) -> str:
    if is_omni_path(path):
        if is_file(path):
            return client.combine_urls(path, ".")
        if is_folder(path):
            if not path.endswith("/"):
                path = path + "/"
            return client.combine_urls(path, "..")
        return ""
    else:
        if is_file(path):
            return os.path.dirname(path) + os.path.sep
        if is_folder(path):
            if not path.endswith(os.path.sep):
                path = path + os.path.sep
            return os.path.normpath(path + "..")
        return ""


def filename_from_path(path: str) -> str:
    if is_omni_path(path):
        broke = client.break_url(path)
        only_path = broke.path
        basename = os.path.basename(only_path)
        return basename
    else:
        path_obj = pathlib.Path(path)
        return path_obj.name


def split_filename(filename: str) -> Tuple[str, str]:
    # It's safe to use os.path because we assume it's only the filename
    return os.path.splitext(filename)


def stat(path: str) -> stat_result:
    file_stat = _stat(path)
    if not file_stat:
        raise OSError

    return stat_result((0, 0, 0, 0, 0, 0, file_stat.size, 0, get_mtime(path), 0))


def isabs(path: str) -> bool:
    if is_omni_path(path):
        return True
    else:
        return os.path.isabs(path)


def exists(path: str) -> bool:
    if is_omni_path(path):
        stat = _stat(path)
        return stat is not None
    else:
        return os.path.exists(path)


def get_mtime(path: str) -> int:
    if is_omni_path(path):
        stat = _stat(path)
        if stat:
            return int(stat.modified_time.timestamp() * 1000)
        raise IOError
    else:
        if exists(path):
            return int(os.path.getmtime(path) * 1000)
        raise IOError


def get_size(path: str) -> int:
    if exists(path):
        if is_omni_path(path):
            stat = _stat(path)
            if stat:
                return stat.size
            return 0
        else:
            return os.path.getsize(path)
    else:
        return 0


def is_folder(path: str) -> bool:
    try:
        if is_omni_path(path):
            stat = _stat(path)
            if stat:
                return stat.flags & client.ItemFlags.CAN_HAVE_CHILDREN
            return False
        else:
            return os.path.isdir(path)
    except:
        return False


def is_file(path: str) -> bool:
    try:
        if is_omni_path(path):
            stat = _stat(path)
            if stat:
                return not (stat.flags & client.ItemFlags.CAN_HAVE_CHILDREN)
            return False
        else:
            return os.path.isfile(path)
    except:
        return False


def create_folder(path: str) -> None:
    if is_omni_path(path):
        if not path.endswith("/"):
            path = path + "/"
        client.create_folder(path)
    else:
        os.mkdir(path)


def read(path: str) -> bytearray:
    if is_omni_path(path):
        (result, _, content) = client.read_file(path)
        if result == client.Result.OK:
            data = memoryview(content).tobytes()
            if data:
                return data
            else:
                return ""
        else:
            raise OSError
    else:
        results = None
        with open(path, "rb") as f:
            results = f.read()
        return results


def write(path: str, data: bytearray) -> None:
    if is_omni_path(path):
        result = client.write_file(path, data)
        if result != client.Result.OK:
            raise OSError
    else:
        with open(path, "wb") as f:
            f.write(data)


def list_files(path: str) -> List[str]:
    if is_omni_path(path):
        file_list = []
        try:
            (result, entries) = client.list(path)
            if result != client.Result.OK:
                return file_list
            if entries:
                for p in entries:
                    file_list.append(p.relative_path)
        except Exception:
            raise OSError

        return file_list
    else:
        file_list = []
        with os.scandir(path) as entries:
            for entry in entries:
                file_list.append(entry.name)

        return file_list


def rename(path: str, new_name: str) -> None:
    if is_omni_path(path):
        client.copy(path, new_name)
        delete(path)
    else:
        os.rename(path, new_name)


def delete(path: str) -> None:
    if is_omni_path(path):
        client.delete(path)
    else:
        os.remove(path)


def read_str(path: str) -> str:
    try:
        result = read(path)
        return result.decode("utf-8")
    except OSError:
        return ""


def write_str(path: str, data: str):
    write(path, data.encode("utf-8"))
