# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import os
from pathlib import Path

import carb
import carb.tokens
import omni.client
import omni.converter.dgn
import omni.log
from omni.kit.converter.common import ConverterStatus, OmniClientWrapper, OmniUrl, run_scene_opt
from pxr import Tf

from .options import OdaDgnOptions

__all__ = ["DgnConverterCoreHelper"]

DEFAULT_TEMP_FOLDER_SETTING = "/ext/omni.kit.converter.dgn_core/default_temp"


class DgnConverterCoreHelper:
    """
    Can be used to make calls to the DGN CAD Converter and for updating the USD stage
    """

    CONVERTER_EXT_NAME = "omni.kit.converter.dgn_core"

    def __init__(self):
        """
        Initialize DGN Converter Helper class
        """
        pass

    def destroy(self):
        pass

    def _log_result(self, error_code: int, error_msg: str):
        """
        We follow the result format used in the backend converter inside the core extension so converter delegate
        can extract result code and message in python subprocess the same way as the backend converter.
        """
        if error_code != 0:
            carb.log_error(error_msg)
        print(f"[omni.converter.dgn_progress]*end*{error_code}*{error_msg}")

    async def _create_import_task(self, input_path: str, output_path: str, file_format_args: dict[str, str]):
        """Convert DGN file to USD

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

        host_dir = os.path.dirname(output_path)

        input_file_url = OmniUrl(input_path)
        res, local_file_url = await input_file_url.get_local_file_async()

        # confirm local file exists; else return
        if res != omni.client.Result.OK:
            error_msg = f"Could not get local file: {local_file_url}. Reason: {res}"
            self._log_result(-1, error_msg)
            return "", ConverterStatus(-1, error_msg)

        export_folder_url = OmniUrl(host_dir)
        temp_output_folder = None
        temp_output_local_path = None
        if export_folder_url.scheme == "omniverse":
            carb.log_info(f"export_folder_url.scheme : {export_folder_url.scheme}")
            temp_output_folder = Path(carb.tokens.get_tokens_interface().resolve("${temp}/cad_converter/"))
            if not temp_output_folder.exists():
                temp_output_folder.mkdir(parents=True)

            output_file_name = Path(output_path).name
            temp_output_local_path = temp_output_folder / output_file_name
        elif export_folder_url.scheme and export_folder_url.scheme != "file":
            error_msg = f"Exporter path not supported : {host_dir}"
            self._log_result(-1, error_msg)
            return "", ConverterStatus(-1, error_msg)

        output_directory = temp_output_folder or Path(host_dir)
        if not await OmniClientWrapper.exists(str(output_directory)):
            await OmniClientWrapper.create_folder(str(output_directory))

        options = OdaDgnOptions()
        options.parse(file_format_args)
        converter = omni.converter.dgn.Converter(options)

        error_code = -1
        error_msg = None
        if temp_output_local_path is None:
            error_code, error_msg = converter.convert(str(local_file_url), output_path, {})
        else:
            error_code, error_msg = converter.convert(str(local_file_url), str(temp_output_local_path), {})
            if error_code == 0:
                copy_result = await OmniClientWrapper.copy(str(temp_output_local_path), output_path)
                temp_output_local_path.unlink()
                if not copy_result:
                    error_msg = f"Failed to copy to invalid output path {output_path}"
                    self._log_result(-1, error_msg)
                    return "", ConverterStatus(-1, error_msg)

        if error_code != 0:
            self._log_result(-1, error_msg)
            return "", ConverterStatus(error_code, error_msg)

        # Run Scene Optimizer
        run_scene_opt(
            output_path,
            options.bOptimize,
            options.convertHidden,
            options.sOptimizeConfig,
            options.dMetersPerUnit,
            options.iUpAxis,
        )
        self._log_result(0, "")
        return output_path, ConverterStatus(0, "")
