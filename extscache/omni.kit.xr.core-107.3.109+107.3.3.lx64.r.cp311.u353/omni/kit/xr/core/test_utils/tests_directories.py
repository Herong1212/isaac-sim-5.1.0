# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported
import os
import pathlib
from functools import lru_cache
from typing import Optional, Union

import carb
import omni.kit.app


def get_xcr_recording_directory(module: Union[str, None] = None) -> pathlib.Path:
    """
    Get directory with XCR recordings for specific module.
    """

    return get_data_directory(module).joinpath("tests/xcr_recordings")


def get_golden_image_source_directory(module: Union[str, None] = None) -> pathlib.Path:
    """
    Get directory with golden images inside extension
    """

    return get_data_directory(module).joinpath("tests/golden_img")


def get_xcr_runtime_json() -> str:
    """
    Get path to .json file defining XCR Replay OpenXR runtime
    """

    return str(get_xcr_directory().joinpath("openxr_xcr_replay_runtime.json"))


def get_xcr_directory() -> pathlib.Path:
    """
    Get directory with XCR package inside build folder
    """

    platform_config_directory = pathlib.Path(carb.tokens.acquire_tokens_interface().resolve("${omni.kit.xr.core}"))
    return platform_config_directory.joinpath("bin").joinpath("xcr-runtime")


def get_data_directory(module: Union[str, None] = None) -> pathlib.Path:
    """
    Get data directory inside extension
    """

    if module is None:
        module = "omni.kit.xr.core"

    return pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(module)).joinpath(
        "data"
    )


def get_usd_directory(module: Union[str, None] = None) -> pathlib.Path:
    """
    Get directory with xr recordings inside extension
    """

    return get_data_directory(module).joinpath("tests/usd")


@lru_cache
def get_test_output_directory() -> pathlib.Path:
    """
    Get the test output directory
    """
    carb_settings = carb.settings.get_settings()
    test_output_path = carb_settings.get("exts/omni.kit.test/testOutputPath")
    return pathlib.Path(test_output_path)


def ensure_directory_exist(directory: str) -> None:
    """
    Ensures the directory exists
    """

    if not os.path.exists(directory):
        os.makedirs(directory)


@lru_cache
def get_test_ext_output_directory() -> pathlib.Path:
    """
    Get the test output directory
    """
    test_output_path = carb.settings.get_settings_interface().get_as_string("exts/omni.kit.test/testExtOutputPath")
    resolved_test_output_path = carb.tokens.acquire_tokens_interface().resolve(test_output_path)
    return pathlib.Path(resolved_test_output_path)
