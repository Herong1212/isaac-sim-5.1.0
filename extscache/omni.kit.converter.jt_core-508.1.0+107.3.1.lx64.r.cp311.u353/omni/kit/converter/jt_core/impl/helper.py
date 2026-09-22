# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import asyncio
import concurrent.futures
import os
from pathlib import Path
from threading import Thread
from typing import Tuple

import carb
import carb.tokens
import omni.client
import omni.converter.jtk
import omni.log
from omni.kit.converter.common import ConverterStatus, OmniClientWrapper, OmniUrl, run_scene_opt
from pxr import Usd

from .options import JTConverterOptions

__all__ = ["JtConverterHelper"]


class JtConverterHelper:
    """
    Can be used to make calls to the JT CAD Converter and for updating the USD stage
    """

    CONVERTER_EXT_NAME = "omni.kit.converter.jt_core"

    def __init__(self):
        """
        Initialize JT CAD Converter Helper class
        """
        self._loop = None
        self._thread = None
        self._node_type_counts = {}

    def destroy(self):
        """
        Clean up resources
        """
        pass

    def _log_result(self, error_code: int, error_msg: str):
        """
        We follow the result format used in the backend converter inside the core extension so converter delegate
        can extract result code and message in python subprocess the same way as the backend converter.
        """
        if error_code != 0:
            carb.log_error(error_msg)
        print(f"[omni.converter.jtk_progress]*end*{error_code}*{error_msg}")

    def get_node_type_counts(self):
        """
        Return a dict that contains counts for each node type
        """
        return self._node_type_counts

    def _start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start background asyncio loop

        :args:
            loop: `asyncio.AbstractEventLoop`
                Loop to run_forever
        """
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def _compute_node_type_counts(self, output_path):
        """
        Compute number of each node type
        """
        counter = {}
        stage = Usd.Stage.Open(output_path)
        if stage:
            traversal = iter(stage.Traverse())
            for prim in traversal:
                attr = prim.GetAttribute("omni:jt:nodeType")
                if not attr.IsAuthored():
                    continue
                node_type = attr.Get()

                # Increment the counter for this type.
                if node_type not in counter:
                    counter[node_type] = 0
                counter[node_type] += 1

                # To avoid double counting instanced prims we ignore descendants of any JtkInstance.
                # This is achieved by pruning the traversal.
                if node_type == "JtkInstance":
                    traversal.PruneChildren()
            stage = None
        return counter

    async def _convert_with_callback(self, converter, input_path, output_path, temp_output_path, args, cb):
        # Call omni.converter.jtk.convert
        if temp_output_path == "":
            cb(converter.convert(input_path, output_path, args))
        else:
            cb(converter.convert(input_path, temp_output_path, args))

    async def _convert_obj_async(
        self, input_path: str, output_path: str, temp_output_path: str, file_format_args: dict[str, str]
    ):
        """Asynchronously convert a jt file to usd"

        Args:
            input_path (str): Full path to the input file
            output_path (str): Full path to the output file
            file_format_args (dict[str,str]) : FileFormatArguments to pass to the converter
        """
        f = concurrent.futures.Future()

        def convert_cb(result):
            if not f.done():
                f.set_result(result)

        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            self._thread = Thread(target=self._start_background_loop, args=(self._loop,), daemon=True)
            self._thread.start()

        # Process the raw file format args applying mappings required to correctly call the converter
        options = JTConverterOptions()
        options.parse(file_format_args)

        # Create converter
        converter = omni.converter.jtk.Converter(options)
        asyncio.run_coroutine_threadsafe(
            self._convert_with_callback(converter, input_path, output_path, temp_output_path, {}, convert_cb),
            self._loop,
        )

        result = await asyncio.wrap_future(f)

        # exit early on conversion failure
        if result[0] != 0:
            return result

        if temp_output_path != "":
            copy_result = await OmniClientWrapper.copy(temp_output_path, output_path)
            try:
                os.remove(temp_output_path)
            except Exception as e:
                carb.log_warn(f"An error occurred while deleting temp file: " + str(e))
            if not copy_result:
                error_msg = f"Failed to copy to invalid output path {output_path}"
                return (-1, error_msg)

        self._node_type_counts = self._compute_node_type_counts(output_path)
        for key in self._node_type_counts:
            carb.log_info("Found {} {} nodes".format(self._node_type_counts[key], key))

        # Run Scene Optimizer
        run_scene_opt(
            output_path,
            options.bOptimize,
            options.bConvertHidden,
            options.sOptimizeConfig,
            options.dMetersPerUnit,
            options.iUpAxis,
        )

        return result

    async def create_import_task(
        self, input_path: str, output_path: str, file_format_args: dict[str, str]
    ) -> Tuple[str, ConverterStatus]:
        """Wraps the JT Converter so that it works with Nucleus files.

        Args:
            input_path (str): Full path to the jt input file
            output_path (str): Full path to the usd output file
            file_format_args (dict[str:str]): File Format Args to pass to converter.

        Returns:
            output_destination_url (str): Final output destination URL.
            result (bool): result of conversion #TODO return type
        """
        # there's a bug in the scheme passed in from upstream extension.. omniverse:/ should be omniverse://
        if output_path.startswith("omniverse:/") and not output_path.startswith("omniverse://"):
            output_path = "omniverse://" + output_path[len("omniverse:/") :]

        input_file_url = OmniUrl(input_path)
        export_url = OmniUrl(output_path)

        if not input_file_url.exists:
            self._log_result(-1, "Input file does not exist!")
            return "", ConverterStatus(-1, "Input file does not exist!")

        res, local_file_url = await input_file_url.get_local_file_async()

        # confirm local file exists; else return
        if res != omni.client.Result.OK:
            error_msg = f"Could not get local file: {local_file_url}. Reason: {res}"
            self._log_result(error_msg)
            return "", ConverterStatus(error_code=-1, error_msg=error_msg)

        temp_output_folder = None
        temp_output_local_path = ""
        if export_url.scheme == "omniverse":
            temp_output_folder = Path(carb.tokens.get_tokens_interface().resolve("${temp}/jt_converter/"))
            if not temp_output_folder.exists():
                temp_output_folder.mkdir(parents=True)

            output_file_name = Path(output_path).name
            temp_output_local_path = temp_output_folder / output_file_name
        elif export_url.scheme and export_url.scheme != "file":
            error_msg = f"Exporter path not supported : {output_path}"
            self._log_result(-1, error_msg)
            return "", ConverterStatus(-1, error_msg)

        output_destination_url = str(export_url)

        # need to create a folder at output path if running as a service
        output_directory = temp_output_folder or export_url.parent_url

        if not await OmniClientWrapper.exists(str(output_directory)):
            await OmniClientWrapper.create_folder(str(output_directory))

        omni.log.info(f"Converting {local_file_url} -> {str(output_destination_url)}...")

        error_code, error_message = await self._convert_obj_async(
            str(local_file_url), output_destination_url, str(temp_output_local_path), file_format_args
        )

        self._log_result(error_code, error_message)
        return str(output_destination_url), ConverterStatus(error_code, error_message)
