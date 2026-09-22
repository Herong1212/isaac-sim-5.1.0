# Copyright (c) 2020-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from __future__ import annotations

__all__ = []

import asyncio
import os
from functools import partial
from typing import Any, Callable, Tuple

import carb.settings
import omni.client
import omni.ui as ui
import omni.usd
from pxr import Sdf

DEFAULT_FILE_EXTS = ("*.*", "All Files")


def show_asset_file_picker(
    title: str,
    assign_value_fn: Callable[[Any, str], None],
    model_weak,
    stage_weak,
    layer_weak=None,
    file_exts: Tuple[Tuple[str, str]] = None,
    frame=None,
    multi_selection: bool = False,
    on_selected_fn=None,
):
    """
    Show the asset file picker.

    Args:
        title (str): The title of the file picker.
        assign_value_fn (Callable[[Any, str], None]): The function to assign the value.
        model_weak (WeakRef): The weak reference to the model.
        stage_weak (WeakRef): The weak reference to the stage.
        layer_weak (WeakRef): The weak reference to the layer.
        file_exts (Tuple[Tuple[str, str]]): The file extensions.
    """
    model = model_weak()
    if not model:
        return

    navigate_to = None
    if hasattr(model, "get_resolved_path"):
        navigate_to = model.get_resolved_path()
        if navigate_to:
            navigate_to = (
                f"{omni.usd.correct_filename_case(os.path.dirname(navigate_to))}/{os.path.basename(navigate_to)}"
            )

    elif isinstance(model, ui.AbstractValueModel) and (
        not hasattr(model, "is_array_type") or not model.is_array_type()
    ):
        navigate_to = model.get_value_as_string()

    if navigate_to is None:
        stage = stage_weak()
        if stage and not stage.GetRootLayer().anonymous:
            # If asset path is empty, open the USD rootlayer folder
            # But only if filepicker didn't already have a folder remembered
            navigate_to = stage.GetRootLayer().identifier

    if layer_weak:
        layer = layer_weak()
        if layer:
            navigate_to = layer.ComputeAbsolutePath(navigate_to)

    if navigate_to:
        navigate_to = replace_query(navigate_to, None)

    try:
        from omni.kit.window.file_importer import get_file_importer

        file_importer = get_file_importer()
        if file_importer:
            file_exts = None

            if hasattr(model, "metadata"):
                custom_data = model.metadata.get(Sdf.PrimSpec.CustomDataKey, {})
                file_exts_dict = custom_data.get("fileExts", {})
                file_exts = tuple((key, value) for (key, value) in file_exts_dict.items())
            if not file_exts:
                file_exts = (DEFAULT_FILE_EXTS,)

            def on_import(model_weak, stage_weak, filename, dirname, selections=None):
                paths = selections.copy() if selections else []
                if not paths:
                    # fallback to filename
                    paths.append(omni.client.combine_urls(dirname, filename))

                # get_current_selections comes in random (?) order, it does not follow selection order. sort it so
                # at least the result is ordered alphabetically.
                paths.sort()

                if not multi_selection:
                    paths = paths[-1:]

                def on_selected(on_selected_fn, stage_weak, model_weak, assign_value_fn, frame, paths):
                    if on_selected_fn:
                        on_selected_fn(stage_weak, model_weak, "\n".join(paths), assign_value_fn, frame)

                check_paths_with_callback(
                    paths,
                    file_exts=file_exts,
                    callback=partial(on_selected, on_selected_fn, stage_weak, model_weak, assign_value_fn, frame),
                )

            file_importer.show_window(
                title=title,
                import_button_label="Select",
                import_handler=partial(on_import, model_weak, stage_weak),
                file_extension_types=file_exts,
                filename_url=navigate_to,
                hide_window_on_import=False,
            )
    except ModuleNotFoundError:
        pass


def check_paths_with_callback(paths, file_exts=(DEFAULT_FILE_EXTS,), callback=None):
    """
    Utility function that checks paths with callback if paths pass check.

    Args:
        paths (List[str]): The paths to check.
        file_exts (Tuple[Tuple[str, str]]): The file extensions.
        callback (Callable[[List[str]], None]): The callback to call if the paths pass the check.
    """

    async def check_paths(paths, callback=None):
        for path in paths:
            result, entry = await omni.client.stat_async(path)
            if result == omni.client.Result.OK:
                if (
                    file_exts
                    and file_exts != (DEFAULT_FILE_EXTS,)
                    and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN
                ):
                    carb.log_warn("Please select a file, not a folder!")
                    return
            else:
                carb.log_warn(f"Selected file {path} does not exist!")
                return

        try:
            from omni.kit.window.file_importer import get_file_importer

            # hide file importer if passed path validation
            file_importer = get_file_importer()
            if file_importer:
                file_importer.hide_window()
        except ModuleNotFoundError:
            pass

        if callback:
            callback(paths)

    asyncio.ensure_future(check_paths(paths, callback=callback))


def replace_query(url, new_query):
    """
    Replace the query of the URL.

    Args:
        url (str): The URL to replace the query of.
        new_query (str): The new query to replace the query of the URL with.

    Returns:
        str: The URL with the new query.
    """
    client_url = omni.client.break_url(url)
    return omni.client.make_url(
        scheme=client_url.scheme,
        user=client_url.user,
        host=client_url.host,
        port=client_url.port,
        path=client_url.path,
        query=new_query,
        fragment=client_url.fragment,
    )
