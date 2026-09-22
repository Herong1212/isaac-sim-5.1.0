# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

# fmt: off
import asyncio
import os
from typing import List, Tuple

if hasattr(os, "add_dll_directory"):
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    dlldir = os.path.abspath(os.path.join(scriptdir, "../../.."))
    with os.add_dll_directory(dlldir):
        from ._omniclient import *
else:
    from ._omniclient import *

AUTH_ABORT = True

def set_result_if_not_done(f, result):
    if not f.done():
        f.set_result(result)



def get_server_info(url: str) -> Tuple[Result, ServerInfo]:
    """Blocking version of :py:func:`omni.client.get_server_info_with_callback`"""

    ret = None

    def get_server_info_cb(result, info):
        nonlocal ret
        ret = (result, info)

    request = get_server_info_with_callback(url=url, callback=get_server_info_cb)
    request.wait()
    return ret


async def get_server_info_async(url: str) -> Tuple[Result, ServerInfo]:
    """Asynchronous version of :py:func:`omni.client.get_server_info_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_server_info_cb(result, info):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, info))

    request = get_server_info_with_callback(url=url, callback=get_server_info_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def refresh_auth_token(url: str) -> Tuple[Result, str]:
    """Blocking version of :py:func:`omni.client.refresh_auth_token_with_callback`"""

    ret = None

    def refresh_auth_token_cb(result, auth_token):
        nonlocal ret
        ret = (result, auth_token)

    request = refresh_auth_token_with_callback(url=url, callback=refresh_auth_token_cb)
    request.wait()
    return ret


async def refresh_auth_token_async(url: str) -> Tuple[Result, str]:
    """Asynchronous version of :py:func:`omni.client.refresh_auth_token_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def refresh_auth_token_cb(result, auth_token):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, auth_token))

    request = refresh_auth_token_with_callback(url=url, callback=refresh_auth_token_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def list(url: str, include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Tuple[Result, Tuple[ListEntry]]:
    """Blocking version of :py:func:`omni.client.list_with_callback`"""

    ret = None

    def list_cb(result, entries):
        nonlocal ret
        ret = (result, entries)

    request = list_with_callback(url=url, include_deleted_option=include_deleted_option, callback=list_cb)
    request.wait()
    return ret


async def list_async(url: str, include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Tuple[Result, Tuple[ListEntry]]:
    """Asynchronous version of :py:func:`omni.client.list_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def list_cb(result, entries):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, entries))

    request = list_with_callback(url=url, include_deleted_option=include_deleted_option, callback=list_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def stat(url: str, include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Tuple[Result, ListEntry]:
    """Blocking version of :py:func:`omni.client.stat_with_callback`"""

    ret = None

    def stat_cb(result, entry):
        nonlocal ret
        ret = (result, entry)

    request = stat_with_callback(url=url, include_deleted_option=include_deleted_option, callback=stat_cb)
    request.wait()
    return ret


async def stat_async(url: str, include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Tuple[Result, ListEntry]:
    """Asynchronous version of :py:func:`omni.client.stat_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def stat_cb(result, entry):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, entry))

    request = stat_with_callback(url=url, include_deleted_option=include_deleted_option, callback=stat_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def resolve(url: str, search_urls: List[str]) -> Tuple[Result, ListEntry, str]:
    """Blocking version of :py:func:`omni.client.resolve_with_callback`"""

    ret = None

    def resolve_cb(result, entry, resolved_url):
        nonlocal ret
        ret = (result, entry, resolved_url)

    request = resolve_with_callback(url=url, search_urls=search_urls, callback=resolve_cb)
    request.wait()
    return ret


async def resolve_async(url: str, search_urls: List[str]) -> Tuple[Result, ListEntry, str]:
    """Asynchronous version of :py:func:`omni.client.resolve_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def resolve_cb(result, entry, resolved_url):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, entry, resolved_url))

    request = resolve_with_callback(url=url, search_urls=search_urls, callback=resolve_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def delete(url: str) -> Result:
    """Blocking version of :py:func:`omni.client.delete_with_callback`"""

    ret = None

    def delete_cb(result):
        nonlocal ret
        ret = result

    request = delete_with_callback(url=url, callback=delete_cb)
    request.wait()
    return ret


async def delete_async(url: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.delete_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def delete_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = delete_with_callback(url=url, callback=delete_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def delete_single(url: str) -> Result:
    """Blocking version of :py:func:`omni.client.delete_single_with_callback`"""

    ret = None

    def delete_single_cb(result):
        nonlocal ret
        ret = result

    request = delete_single_with_callback(url=url, callback=delete_single_cb)
    request.wait()
    return ret


async def delete_single_async(url: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.delete_single_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def delete_single_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = delete_single_with_callback(url=url, callback=delete_single_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def undelete(url: str) -> Result:
    """Blocking version of :py:func:`omni.client.undelete_with_callback`"""

    ret = None

    def undelete_cb(result):
        nonlocal ret
        ret = result

    request = undelete_with_callback(url=url, callback=undelete_cb)
    request.wait()
    return ret


async def undelete_async(url: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.undelete_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def undelete_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = undelete_with_callback(url=url, callback=undelete_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def obliterate(url: str, obliterate_checkpoints: bool) -> Result:
    """Blocking version of :py:func:`omni.client.obliterate_with_callback`"""

    ret = None

    def obliterate_cb(result):
        nonlocal ret
        ret = result

    request = obliterate_with_callback(url=url, obliterate_checkpoints=obliterate_checkpoints, callback=obliterate_cb)
    request.wait()
    return ret


async def obliterate_async(url: str, obliterate_checkpoints: bool) -> Result:
    """Asynchronous version of :py:func:`omni.client.obliterate_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def obliterate_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = obliterate_with_callback(url=url, obliterate_checkpoints=obliterate_checkpoints, callback=obliterate_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def create_folder(url: str) -> Result:
    """Blocking version of :py:func:`omni.client.create_folder_with_callback`"""

    ret = None

    def create_folder_cb(result):
        nonlocal ret
        ret = result

    request = create_folder_with_callback(url=url, callback=create_folder_cb)
    request.wait()
    return ret


async def create_folder_async(url: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.create_folder_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def create_folder_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = create_folder_with_callback(url=url, callback=create_folder_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def copy(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Result:
    """Blocking version of :py:func:`omni.client.copy_with_callback`"""

    ret = None

    def copy_cb(result):
        nonlocal ret
        ret = result

    request = copy_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=copy_cb)
    request.wait()
    return ret


async def copy_async(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Result:
    """Asynchronous version of :py:func:`omni.client.copy_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def copy_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = copy_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=copy_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def copy_file(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Result:
    """Blocking version of :py:func:`omni.client.copy_file_with_callback`"""

    ret = None

    def copy_file_cb(result):
        nonlocal ret
        ret = result

    request = copy_file_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=copy_file_cb)
    request.wait()
    return ret


async def copy_file_async(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Result:
    """Asynchronous version of :py:func:`omni.client.copy_file_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def copy_file_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = copy_file_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=copy_file_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def copy_folder(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Result:
    """Blocking version of :py:func:`omni.client.copy_folder_with_callback`"""

    ret = None

    def copy_folder_cb(result):
        nonlocal ret
        ret = result

    request = copy_folder_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=copy_folder_cb)
    request.wait()
    return ret


async def copy_folder_async(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Result:
    """Asynchronous version of :py:func:`omni.client.copy_folder_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def copy_folder_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = copy_folder_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=copy_folder_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def move(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Tuple[Result, bool]:
    """Blocking version of :py:func:`omni.client.move_with_callback`"""

    ret = None

    def move_cb(result, copied):
        nonlocal ret
        ret = (result, copied)

    request = move_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=move_cb)
    request.wait()
    return ret


async def move_async(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Tuple[Result, bool]:
    """Asynchronous version of :py:func:`omni.client.move_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def move_cb(result, copied):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, copied))

    request = move_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=move_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def move_file(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Tuple[Result, bool]:
    """Blocking version of :py:func:`omni.client.move_file_with_callback`"""

    ret = None

    def move_file_cb(result, copied):
        nonlocal ret
        ret = (result, copied)

    request = move_file_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=move_file_cb)
    request.wait()
    return ret


async def move_file_async(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Tuple[Result, bool]:
    """Asynchronous version of :py:func:`omni.client.move_file_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def move_file_cb(result, copied):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, copied))

    request = move_file_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=move_file_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def move_folder(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Tuple[Result, bool]:
    """Blocking version of :py:func:`omni.client.move_folder_with_callback`"""

    ret = None

    def move_folder_cb(result, copied):
        nonlocal ret
        ret = (result, copied)

    request = move_folder_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=move_folder_cb)
    request.wait()
    return ret


async def move_folder_async(src_url: str, dst_url: str, behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = "") -> Tuple[Result, bool]:
    """Asynchronous version of :py:func:`omni.client.move_folder_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def move_folder_cb(result, copied):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, copied))

    request = move_folder_with_callback(src_url=src_url, dst_url=dst_url, behavior=behavior, message=message, callback=move_folder_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_local_file(url: str, download: bool = True) -> Tuple[Result, str]:
    """Blocking version of :py:func:`omni.client.get_local_file_with_callback`"""

    ret = None

    def get_local_file_cb(result, local_file_path):
        nonlocal ret
        ret = (result, local_file_path)

    request = get_local_file_with_callback(url=url, download=download, callback=get_local_file_cb)
    request.wait()
    return ret


async def get_local_file_async(url: str, download: bool = True) -> Tuple[Result, str]:
    """Asynchronous version of :py:func:`omni.client.get_local_file_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_local_file_cb(result, local_file_path):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, local_file_path))

    request = get_local_file_with_callback(url=url, download=download, callback=get_local_file_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def open_cached_file(url: str, download: bool = True) -> Tuple[Result, int, str]:
    """Blocking version of :py:func:`omni.client.open_cached_file_with_callback`"""

    ret = None

    def open_cached_file_cb(result, handle, cache_path):
        nonlocal ret
        ret = (result, handle, cache_path)

    request = open_cached_file_with_callback(url=url, download=download, callback=open_cached_file_cb)
    request.wait()
    return ret


async def open_cached_file_async(url: str, download: bool = True) -> Tuple[Result, int, str]:
    """Asynchronous version of :py:func:`omni.client.open_cached_file_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def open_cached_file_cb(result, handle, cache_path):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, handle, cache_path))

    request = open_cached_file_with_callback(url=url, download=download, callback=open_cached_file_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def read_file(url: str) -> Tuple[Result, str, Content]:
    """Blocking version of :py:func:`omni.client.read_file_with_callback`"""

    ret = None

    def read_file_cb(result, version, content):
        nonlocal ret
        ret = (result, version, content)

    request = read_file_with_callback(url=url, callback=read_file_cb)
    request.wait()
    return ret


async def read_file_async(url: str) -> Tuple[Result, str, Content]:
    """Asynchronous version of :py:func:`omni.client.read_file_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def read_file_cb(result, version, content):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, version, content))

    request = read_file_with_callback(url=url, callback=read_file_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def create_with_hash(url: str, hash: str, overwrite: bool) -> Tuple[Result, str, str]:
    """Blocking version of :py:func:`omni.client.create_with_hash_with_callback`"""

    ret = None

    def create_with_hash_cb(result, version, hash):
        nonlocal ret
        ret = (result, version, hash)

    request = create_with_hash_with_callback(url=url, hash=hash, overwrite=overwrite, callback=create_with_hash_cb)
    request.wait()
    return ret


async def create_with_hash_async(url: str, hash: str, overwrite: bool) -> Tuple[Result, str, str]:
    """Asynchronous version of :py:func:`omni.client.create_with_hash_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def create_with_hash_cb(result, version, hash):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, version, hash))

    request = create_with_hash_with_callback(url=url, hash=hash, overwrite=overwrite, callback=create_with_hash_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def write_file(url: str, content: bytes, message: str = "") -> Result:
    """Blocking version of :py:func:`omni.client.write_file_with_callback`"""

    ret = None

    def write_file_cb(result):
        nonlocal ret
        ret = result

    request = write_file_with_callback(url=url, content=content, message=message, callback=write_file_cb)
    request.wait()
    return ret


async def write_file_async(url: str, content: bytes, message: str = "") -> Result:
    """Asynchronous version of :py:func:`omni.client.write_file_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def write_file_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = write_file_with_callback(url=url, content=content, message=message, callback=write_file_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def write_file_ex(url: str, content: bytes, message: str = "", skip_checkpoint: bool = False) -> Tuple[Result, WriteFileExInfo]:
    """Blocking version of :py:func:`omni.client.write_file_ex_with_callback`"""

    ret = None

    def write_file_ex_cb(result, extra_info):
        nonlocal ret
        ret = (result, extra_info)

    request = write_file_ex_with_callback(url=url, content=content, message=message, skip_checkpoint=skip_checkpoint, callback=write_file_ex_cb)
    request.wait()
    return ret


async def write_file_ex_async(url: str, content: bytes, message: str = "", skip_checkpoint: bool = False) -> Tuple[Result, WriteFileExInfo]:
    """Asynchronous version of :py:func:`omni.client.write_file_ex_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def write_file_ex_cb(result, extra_info):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, extra_info))

    request = write_file_ex_with_callback(url=url, content=content, message=message, skip_checkpoint=skip_checkpoint, callback=write_file_ex_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_acls(url: str) -> Tuple[Result, List[AclEntry]]:
    """Blocking version of :py:func:`omni.client.get_acls_with_callback`"""

    ret = None

    def get_acls_cb(result, acls):
        nonlocal ret
        ret = (result, acls)

    request = get_acls_with_callback(url=url, callback=get_acls_cb)
    request.wait()
    return ret


async def get_acls_async(url: str) -> Tuple[Result, List[AclEntry]]:
    """Asynchronous version of :py:func:`omni.client.get_acls_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_acls_cb(result, acls):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, acls))

    request = get_acls_with_callback(url=url, callback=get_acls_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def set_acls(url: str, acls: List[AclEntry]) -> Result:
    """Blocking version of :py:func:`omni.client.set_acls_with_callback`"""

    ret = None

    def set_acls_cb(result):
        nonlocal ret
        ret = result

    request = set_acls_with_callback(url=url, acls=acls, callback=set_acls_cb)
    request.wait()
    return ret


async def set_acls_async(url: str, acls: List[AclEntry]) -> Result:
    """Asynchronous version of :py:func:`omni.client.set_acls_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def set_acls_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = set_acls_with_callback(url=url, acls=acls, callback=set_acls_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def send_message(join_request_id: int, content: bytes) -> Result:
    """Blocking version of :py:func:`omni.client.send_message_with_callback`"""

    ret = None

    def send_message_cb(result):
        nonlocal ret
        ret = result

    request = send_message_with_callback(join_request_id=join_request_id, content=content, callback=send_message_cb)
    request.wait()
    return ret


async def send_message_async(join_request_id: int, content: bytes) -> Result:
    """Asynchronous version of :py:func:`omni.client.send_message_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def send_message_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = send_message_with_callback(join_request_id=join_request_id, content=content, callback=send_message_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def list_checkpoints(url: str) -> Tuple[Result, Tuple[ListEntry]]:
    """Blocking version of :py:func:`omni.client.list_checkpoints_with_callback`"""

    ret = None

    def list_checkpoints_cb(result, entries):
        nonlocal ret
        ret = (result, entries)

    request = list_checkpoints_with_callback(url=url, callback=list_checkpoints_cb)
    request.wait()
    return ret


async def list_checkpoints_async(url: str) -> Tuple[Result, Tuple[ListEntry]]:
    """Asynchronous version of :py:func:`omni.client.list_checkpoints_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def list_checkpoints_cb(result, entries):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, entries))

    request = list_checkpoints_with_callback(url=url, callback=list_checkpoints_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def create_checkpoint(url: str, comment: str, force: bool = False) -> Tuple[Result, str]:
    """Blocking version of :py:func:`omni.client.create_checkpoint_with_callback`"""

    ret = None

    def create_checkpoint_cb(result, query):
        nonlocal ret
        ret = (result, query)

    request = create_checkpoint_with_callback(url=url, comment=comment, force=force, callback=create_checkpoint_cb)
    request.wait()
    return ret


async def create_checkpoint_async(url: str, comment: str, force: bool = False) -> Tuple[Result, str]:
    """Asynchronous version of :py:func:`omni.client.create_checkpoint_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def create_checkpoint_cb(result, query):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, query))

    request = create_checkpoint_with_callback(url=url, comment=comment, force=force, callback=create_checkpoint_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_groups(url: str) -> Tuple[Result, List[str]]:
    """Blocking version of :py:func:`omni.client.get_groups_with_callback`"""

    ret = None

    def get_groups_cb(result, groups):
        nonlocal ret
        ret = (result, groups)

    request = get_groups_with_callback(url=url, callback=get_groups_cb)
    request.wait()
    return ret


async def get_groups_async(url: str) -> Tuple[Result, List[str]]:
    """Asynchronous version of :py:func:`omni.client.get_groups_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_groups_cb(result, groups):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, groups))

    request = get_groups_with_callback(url=url, callback=get_groups_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_group_users(url: str, group: str) -> Tuple[Result, List[str]]:
    """Blocking version of :py:func:`omni.client.get_group_users_with_callback`"""

    ret = None

    def get_group_users_cb(result, users):
        nonlocal ret
        ret = (result, users)

    request = get_group_users_with_callback(url=url, group=group, callback=get_group_users_cb)
    request.wait()
    return ret


async def get_group_users_async(url: str, group: str) -> Tuple[Result, List[str]]:
    """Asynchronous version of :py:func:`omni.client.get_group_users_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_group_users_cb(result, users):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, users))

    request = get_group_users_with_callback(url=url, group=group, callback=get_group_users_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def create_group(url: str, group: str) -> Result:
    """Blocking version of :py:func:`omni.client.create_group_with_callback`"""

    ret = None

    def create_group_cb(result):
        nonlocal ret
        ret = result

    request = create_group_with_callback(url=url, group=group, callback=create_group_cb)
    request.wait()
    return ret


async def create_group_async(url: str, group: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.create_group_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def create_group_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = create_group_with_callback(url=url, group=group, callback=create_group_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def rename_group(url: str, group: str, new_group: str) -> Result:
    """Blocking version of :py:func:`omni.client.rename_group_with_callback`"""

    ret = None

    def rename_group_cb(result):
        nonlocal ret
        ret = result

    request = rename_group_with_callback(url=url, group=group, new_group=new_group, callback=rename_group_cb)
    request.wait()
    return ret


async def rename_group_async(url: str, group: str, new_group: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.rename_group_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def rename_group_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = rename_group_with_callback(url=url, group=group, new_group=new_group, callback=rename_group_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def remove_group(url: str, group: str) -> Tuple[Result, int]:
    """Blocking version of :py:func:`omni.client.remove_group_with_callback`"""

    ret = None

    def remove_group_cb(result, change_count):
        nonlocal ret
        ret = (result, change_count)

    request = remove_group_with_callback(url=url, group=group, callback=remove_group_cb)
    request.wait()
    return ret


async def remove_group_async(url: str, group: str) -> Tuple[Result, int]:
    """Asynchronous version of :py:func:`omni.client.remove_group_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def remove_group_cb(result, change_count):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, change_count))

    request = remove_group_with_callback(url=url, group=group, callback=remove_group_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_users(url: str) -> Tuple[Result, List[str]]:
    """Blocking version of :py:func:`omni.client.get_users_with_callback`"""

    ret = None

    def get_users_cb(result, users):
        nonlocal ret
        ret = (result, users)

    request = get_users_with_callback(url=url, callback=get_users_cb)
    request.wait()
    return ret


async def get_users_async(url: str) -> Tuple[Result, List[str]]:
    """Asynchronous version of :py:func:`omni.client.get_users_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_users_cb(result, users):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, users))

    request = get_users_with_callback(url=url, callback=get_users_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_user_groups(url: str, user: str) -> Tuple[Result, List[str]]:
    """Blocking version of :py:func:`omni.client.get_user_groups_with_callback`"""

    ret = None

    def get_user_groups_cb(result, groups):
        nonlocal ret
        ret = (result, groups)

    request = get_user_groups_with_callback(url=url, user=user, callback=get_user_groups_cb)
    request.wait()
    return ret


async def get_user_groups_async(url: str, user: str) -> Tuple[Result, List[str]]:
    """Asynchronous version of :py:func:`omni.client.get_user_groups_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_user_groups_cb(result, groups):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, groups))

    request = get_user_groups_with_callback(url=url, user=user, callback=get_user_groups_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def add_user_to_group(url: str, user: str, group: str) -> Result:
    """Blocking version of :py:func:`omni.client.add_user_to_group_with_callback`"""

    ret = None

    def add_user_to_group_cb(result):
        nonlocal ret
        ret = result

    request = add_user_to_group_with_callback(url=url, user=user, group=group, callback=add_user_to_group_cb)
    request.wait()
    return ret


async def add_user_to_group_async(url: str, user: str, group: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.add_user_to_group_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def add_user_to_group_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = add_user_to_group_with_callback(url=url, user=user, group=group, callback=add_user_to_group_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def remove_user_from_group(url: str, user: str, group: str) -> Result:
    """Blocking version of :py:func:`omni.client.remove_user_from_group_with_callback`"""

    ret = None

    def remove_user_from_group_cb(result):
        nonlocal ret
        ret = result

    request = remove_user_from_group_with_callback(url=url, user=user, group=group, callback=remove_user_from_group_cb)
    request.wait()
    return ret


async def remove_user_from_group_async(url: str, user: str, group: str) -> Result:
    """Asynchronous version of :py:func:`omni.client.remove_user_from_group_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def remove_user_from_group_cb(result):
        loop.call_soon_threadsafe(set_result_if_not_done, f, result)

    request = remove_user_from_group_with_callback(url=url, user=user, group=group, callback=remove_user_from_group_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_hub_version() -> Tuple[Result, str]:
    """Blocking version of :py:func:`omni.client.get_hub_version_with_callback`"""

    ret = None

    def get_hub_version_cb(result, version):
        nonlocal ret
        ret = (result, version)

    request = get_hub_version_with_callback(callback=get_hub_version_cb)
    request.wait()
    return ret


async def get_hub_version_async() -> Tuple[Result, str]:
    """Asynchronous version of :py:func:`omni.client.get_hub_version_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_hub_version_cb(result, version):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, version))

    request = get_hub_version_with_callback(callback=get_hub_version_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise


def get_hub_http_uri() -> Tuple[Result, str]:
    """Blocking version of :py:func:`omni.client.get_hub_http_uri_with_callback`"""

    ret = None

    def get_hub_http_uri_cb(result, uri):
        nonlocal ret
        ret = (result, uri)

    request = get_hub_http_uri_with_callback(callback=get_hub_http_uri_cb)
    request.wait()
    return ret


async def get_hub_http_uri_async() -> Tuple[Result, str]:
    """Asynchronous version of :py:func:`omni.client.get_hub_http_uri_with_callback`"""

    loop = asyncio.get_event_loop()
    f = loop.create_future()

    def get_hub_http_uri_cb(result, uri):
        loop.call_soon_threadsafe(set_result_if_not_done, f, (result, uri))

    request = get_hub_http_uri_with_callback(callback=get_hub_http_uri_cb)
    try:
        ret = await f
        return ret
    except:
        request.stop()
        raise
