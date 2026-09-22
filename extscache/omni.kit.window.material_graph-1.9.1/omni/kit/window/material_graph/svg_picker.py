# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ATTRIBUTE_EMBEDDED_ICON", "SvgPicker"]

import asyncio
import functools
import os
import traceback
from pathlib import Path

import carb
import carb.tokens
import omni.client
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog
from pxr import Sdf, Usd

ATTRIBUTE_EMBEDDED_ICON = "ui:nodegraph:node:embeddedIcon"


def handle_exception(func):
    """
    Decorator to print exception in async functions
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


@handle_exception
async def _set_svg_icon(prim: Usd.Prim, path: str):
    """Opens SVG file and saves its content to the prim"""
    result, _, content = await omni.client.read_file_async(path)
    if result != omni.client.Result.OK:
        carb.log_error(f"[Material Graph] Can't read file {path}")
        return

    svg_data = memoryview(content).tobytes().decode("utf-8")

    # It's svg
    if prim.HasAttribute(ATTRIBUTE_EMBEDDED_ICON):
        attribute = prim.GetAttribute(ATTRIBUTE_EMBEDDED_ICON)
    else:
        attribute = prim.CreateAttribute(ATTRIBUTE_EMBEDDED_ICON, Sdf.ValueTypeNames.String, False)

    attribute.Set(svg_data)


class SvgPicker:
    def __init__(self):
        self._prim = None
        self._dialog = None

    def destroy(self):
        self._prim = None
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

    def set_icon(self, prim):
        self.destroy()

        self._prim = prim
        self._dialog = FilePickerDialog(
            "Open SVG",
            apply_button_label="Open",
            current_directory=self.__get_svg_dir(),
            click_apply_handler=self.__on_open,
            click_cancel_handler=self.__on_cancel,
            item_filter_options=["SVG Files (*.svg)", "All Files (*)"],
            item_filter_fn=self.__on_filter_item,
        )

    def __get_svg_dir(self) -> str:
        """Return the workspace file"""
        from .graph_extension import COMPOUND_DEFAULT_PATH

        token = carb.tokens.get_tokens_interface()
        dir = token.resolve(COMPOUND_DEFAULT_PATH)
        # FilePickerDialog needs the capital drive. In case it's linux, the
        # first letter will be / and it's still OK.
        dir = dir[:1].upper() + dir[1:]

        if not Path(dir).exists():
            os.mkdir(dir)

        return dir

    def __on_filter_item(self, prim: FileBrowserItem) -> bool:
        if not prim or prim.is_folder:
            return True
        if self._dialog.current_filter_option == 0:
            # Show only files with listed extensions
            if prim.path.endswith(".svg"):
                return True
            else:
                return False
        else:
            # Show All Files (*)
            return True

    def __on_cancel(self, filename: str, dir: str):
        self._dialog.hide()
        self._prim = None

    def __on_open(self, filename: str, dir: str):
        """Called when the user presses the Save button in the dialog"""
        path = omni.client.combine_urls(dir + "/", filename)

        asyncio.ensure_future(_set_svg_icon(self._prim, path))

        self._dialog.hide()
        self._prim = None
