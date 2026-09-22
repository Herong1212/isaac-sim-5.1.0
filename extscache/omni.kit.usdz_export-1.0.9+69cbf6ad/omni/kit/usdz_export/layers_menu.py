# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .utils import is_extension_loaded, copy, list_folder_async

from pxr import Sdf, Usd
from pathlib import Path
from zipfile import ZipFile
from functools import partial
from typing import Callable, List
from omni.kit.window.file_exporter import get_file_exporter
from omni.kit.widget.prompt import PromptManager

import carb
import omni.kit.usd.collect as collect
import omni.usd
import asyncio
import tempfile
import os
import omni.kit.app
import omni.kit.notification_manager as nm


def layers_available() -> bool:
    """Returns True if the extension "omni.kit.widget.layers" is loaded"""
    return is_extension_loaded("omni.kit.widget.layers")


async def usdz_export(identifier, export_path):
    """Export a layer to USDZ using a temporary directory for file collection and packaging.

    Args:
        identifier (str): Layer identifier to export.
        export_path (str): Destination path for the exported USDZ file.
    """
    try:
        target_out = export_path

        carb.log_info(f"Starting to export layer '{identifier}' to '{target_out}'")
        prompt = PromptManager.post_simple_prompt(
            "Please Wait", "Exporting to USDZ...", ok_button_info=None, modal=True
        )
        # Waits for prompt to be shown
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        layer = Sdf.Layer.FindOrOpen(identifier)
        if not layer:
            message = f"Failed to export layer {identifier} as it does not exist."
            carb.log_error(message)
            nm.post_notification(message, status=nm.NotificationStatus.WARNING)
            return

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            collect_path = tmp_path.joinpath("collected")

            split_ext = os.path.splitext(identifier)
            # Can't collect USDZ files because MDLs can't be resolved
            if split_ext[1] == ".usdz":
                input_usdz_temp_path = str(tmp_path.joinpath("temp_copy.usdz"))
                await copy(identifier, str(input_usdz_temp_path))
                with ZipFile(input_usdz_temp_path, "r") as zip_ref:
                    zip_ref.extractall(str(tmp_path))

                tmp_file_path = str(tmp_path.joinpath("main.usdc"))
                layer.Export(tmp_file_path)
                entry_layer_to_collect = tmp_file_path
            elif not omni.usd.is_usd_writable_filetype(identifier) or identifier.startswith("anon"):
                tmp_file_path = str(tmp_path.joinpath("main.usdc"))
                layer.Export(tmp_file_path)
                entry_layer_to_collect = tmp_file_path
            else:
                entry_layer_to_collect = identifier

            collector = collect.Collector(entry_layer_to_collect, str(collect_path), flat_collection=True)
            await collector.collect(None, None)

            # must create USDZ locally because the UsdUtils package cannot handle omniverse:// URIs
            absolute_paths, relative_paths = await list_folder_async(str(collect_path))
            local_out_path = collect_path.joinpath("local_out.usdz")

            # Create usdz package manually without using USD API as it cannot handle UDIM textures.
            batch = 0
            with ZipFile(str(local_out_path), "w") as zip_writer:
                for absolute_path, relative_path in zip(absolute_paths, relative_paths):
                    if os.path.basename(relative_path) == collect.COLLECT_MAPPING_FILE_NAME:
                        continue

                    try:
                        zip_writer.write(absolute_path, relative_path)
                    except Exception as e:
                        carb.log_warn(f"Failed to package file {absolute_path}: {str(e)}")
                        continue

                    if batch >= 5:
                        # Don't block main thread
                        batch = 0
                        await omni.kit.app.get_app().next_update_async()
                    else:
                        batch += 1
            layer = None
            await copy(str(local_out_path), target_out)
    except NotADirectoryError as e:
        carb.log_warn(f"Failed to remove tmp dir: {tmp_path}.")
    finally:
        prompt.visible = False
        prompt = None
        carb.log_info(f"Finished exporting layer '{identifier}' to '{target_out}'")


def export(objects):
    """Export the target layer to USDZ.

    Args:
        objects (dict): A dictionary containing selected layer item information.
    """

    def on_export(
        callback: Callable, flatten: bool, filename: str, dirname: str, extension: str = "", selections: List[str] = []
    ):
        nonlocal objects
        path = f"{dirname}{filename}{extension}"
        item = objects["item"]
        identifier = item().identifier
        asyncio.ensure_future(usdz_export(identifier, path))

    file_picker = get_file_exporter()
    file_picker.show_window(
        title="Export To USDZ",
        export_button_label="Export",
        export_handler=partial(on_export, None, False),
        file_extension_types=[(".usdz", "Zipped package")],
    )


class LayersMenu:
    """
    When this object is alive, Layers 2.0 has an additional action
    for exporting the layer to USDZ.
    """

    def __init__(self):
        import omni.kit.widget.layers as layers

        self.__menu_subscription = layers.ContextMenu.add_menu(
            [
                {"name": ""},
                {
                    "name": "Export USDZ",
                    "glyph": "menu_rename.svg",
                    "show_fn": [
                        layers.ContextMenu.is_layer_item,
                        layers.ContextMenu.is_not_missing_layer,
                        layers.ContextMenu.is_layer_not_locked_by_other,
                        layers.ContextMenu.is_layer_and_parent_unmuted,
                    ],
                    "onclick_fn": export,
                },
            ]
        )

    def destroy(self):
        """Remove the menu from Layers 2.0"""
        self.__menu_subscription = None
