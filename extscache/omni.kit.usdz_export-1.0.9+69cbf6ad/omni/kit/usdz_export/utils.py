# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import omni.kit.app
import traceback
import carb
import omni.client


def is_extension_loaded(extansion_name: str) -> bool:
    """
    Returns True if the extension with the given name is loaded.
    """

    def is_ext(id: str, extension_name: str) -> bool:
        id_name = id.split("-")[0]
        return id_name == extension_name

    app = omni.kit.app.get_app_interface()
    ext_manager = app.get_extension_manager()
    extensions = ext_manager.get_extensions()

    loaded = next((ext for ext in extensions if is_ext(ext["id"], extansion_name) and ext["enabled"]), None)

    return not not loaded


async def copy(src_path: str, dest_path: str):
    carb.log_info(f"Copying from {src_path} to {dest_path}...")
    try:
        result = await omni.client.copy_async(src_path, dest_path, omni.client.CopyBehavior.OVERWRITE)
        if result != omni.client.Result.OK:
            carb.log_error(f"Cannot copy from {src_path} to {dest_path}, error code: {result}.")
            return False
        else:
            return True
    except Exception as e:
        traceback.print_exc()
        carb.log_error(str(e))

    return False


async def list_folder_async(folder_path):
    def compute_absolute_path(base_path, is_base_path_folder, path, is_path_folder):
        if is_base_path_folder and not base_path.endswith("/"):
            base_path += "/"

        if is_path_folder and not path.endswith("/"):
            path += "/"

        return omni.client.make_absolute_url_if_possible(base_path, path)

    absolute_paths = []
    relative_paths = []
    result, entry = await omni.client.stat_async(folder_path)
    if result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
        is_folder = True
    else:
        is_folder = False

    folder_path = omni.client.make_file_url_if_possible(folder_path)
    if not is_folder:
        absolute_paths = [folder_path]
        relative_paths = [os.path.basename(folder_path)]
    else:
        if not folder_path.endswith("/"):
            folder_path += "/"

        folder_queue = [folder_path]
        while len(folder_queue) > 0:
            folder = folder_queue.pop(0)
            (result, entries) = await omni.client.list_async(folder)
            if result != omni.client.Result.OK:
                break
            folders = set((e.relative_path for e in entries if e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN))
            for f in folders:
                folder_queue.append(compute_absolute_path(folder, True, f, False))
            files = set((e.relative_path for e in entries if not e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN))
            for file in files:
                absolute_path = compute_absolute_path(folder, True, file, False)
                absolute_paths.append(absolute_path)
                relative_path = omni.client.make_relative_url_if_possible(folder_path, absolute_path)
                relative_paths.append(relative_path)

    return absolute_paths, relative_paths
