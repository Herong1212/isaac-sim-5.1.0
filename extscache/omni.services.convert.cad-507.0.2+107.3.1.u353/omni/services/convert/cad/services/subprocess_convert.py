# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import subprocess

import carb
import omni.kit.app
from fastapi import status
from omni.kit.converter.common import OmniClientWrapper
from omni.services.core import exceptions

from .constants import Constants as constants


def _check_format_supported(stdout_line: str, import_path: str):
    # Check for Format Supported information
    format_token = stdout_line.find("*Format_Supported*")
    if format_token != -1:
        tokens = stdout_line.split("*")
        # Validate the boolean value
        if "true" not in tokens[3].lower():
            carb.log_warn(f"File format not supported: {import_path}")
            # Raise an exception if the file format isn't supported
            raise exceptions.KitServicesBaseException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File format isn't supported: {import_path}",
            )


def _parse_convert_error_msg(stdout_line: str, import_path: str):
    # Check for any error messages
    convert_error_token = stdout_line.find("*convert_err_msg*")
    if convert_error_token != -1:
        _check_format_supported(stdout_line, import_path)


async def launch_kit_app(import_path: str, output_path: str, config_path: str, progress_facility) -> None:
    """
    Launches the application with the specified parameters.

    Parameters:
    - import_path (str): The path to the input CAD file.
    - output_path (str): The full path output USD file.
    - config_path (str): The path to the configuration file (JSON).
    - progress_facility: The facility for tracking progress.
    """

    # Get the full path to the Kit executable
    kit_folder_path = str(carb.tokens.get_tokens_interface().resolve("${kit}"))
    kit_ext = str(carb.tokens.get_tokens_interface().resolve("${exe_ext}"))
    kit_exe_path = f"{kit_folder_path}/kit{kit_ext}"

    # Find the extension install path to locate py script
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_enabled_extension_id(constants.APP_NAME)
    ext_path = manager.get_extension_path(ext_id)

    # Common args across converters.
    args = [kit_exe_path]
    # add the "--ext-folder" for the locally cached dgn_core in the container.
    args.extend(["--ext-folder", "/root/.local/share/ov/data/exts/v2"])
    for ext_folder in carb.settings.get_settings().get("/app/exts/folders"):
        args.extend(["--ext-folder", ext_folder])

    log_prefix = None
    if import_path.lower().endswith("dgn"):
        log_prefix = "[omni.converter.dgn_progress]"
        script_path = ext_path + constants.DGN_LAUNCH_SCRIPT_PATH
        args.extend(["--allow-root", "--enable", "omni.kit.converter.dgn_core", "--exec"])

    elif import_path.lower().endswith("jt"):
        log_prefix = "[omni.converter.jtk_progress]"
        script_path = ext_path + constants.JT_LAUNCH_SCRIPT_PATH
        args.extend(["--allow-root", "--enable", "omni.kit.converter.jt_core", "--exec"])

    else:
        log_prefix = "[omni.converter.hoops_progress]"
        script_path = ext_path + constants.HOOPS_LAUNCH_SCRIPT_PATH
        args.extend(["--allow-root", "--enable", "omni.kit.converter.hoops_core", "--exec"])

    core_args = [
        f'--input-path "{import_path}"',
        f'--output-path "{output_path}"',
        f'--config-path "{config_path}"',
    ]

    args += ["--/app/fastShutdown=1"]

    # Quote the script path to handle spaces properly
    quoted_script_path = f'"{script_path}"'
    args.extend([f'{quoted_script_path} {" ".join(core_args)}'])

    # pass --info to kit subprocess to pick up prints
    args += ["--info"]

    # Call the script that invokes kit with CAD Converter
    process = subprocess.Popen(args, stdout=subprocess.PIPE)

    # Set ProgressFacility from output.
    while process.poll() is None:
        stdout_line = process.stdout.readline().decode()
        # Process the stdout_line if needed - using as busy waiting...
        if stdout_line:
            # Check for any error messages
            _parse_convert_error_msg(stdout_line, import_path)

            if not stdout_line.startswith(log_prefix):
                continue
            stdout_line = stdout_line[len(log_prefix) :]
            carb.log_info(stdout_line)

            index = stdout_line.find("*prog*")
            # skip progress extraction if the line contains no such info
            if index == -1:
                continue

            tokens = stdout_line[index:].split("*")
            part_name = tokens[3].strip()
            progress = float(tokens[2]) / 100
            if hasattr(progress_facility, "set_progress"):
                progress_facility.set_progress(0, 1, progress=progress, status_message=part_name)

    return process.returncode


async def subprocess_convert(import_path: str, output_path: str, config_path: str, progress_facility) -> bool:
    """Set up and call a new process to convert files.

    Args:
        import_path (str): Full path to source asset (CAD File).
        output_path (str): Full path output USD file.
        config_path (str): Full path to the user config JSON.
        progress_facility (): Progress monitoring facility.
    """
    carb.log_info("Starting asset conversion...")

    # Call a new kit process and enable the target extension.
    return_code = await launch_kit_app(import_path, output_path, config_path, progress_facility)

    if return_code != 0:
        return False

    if not await OmniClientWrapper.exists(output_path):
        return False

    return True
