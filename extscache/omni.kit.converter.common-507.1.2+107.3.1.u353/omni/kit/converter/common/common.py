# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import json
import os
import re
import typing
import urllib.parse
import zipfile
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import List, NamedTuple, Optional

import carb
import carb.tokens
import omni.client
import omni.kit.app
from omni.scene.optimizer.core import ExecutionContext
from pxr import Usd, UsdGeom, UsdUtils

__all__ = [
    "ConverterStatus",
    "ConverterFilterData",
    "UsdSuffix",
    "run_scene_opt",
    "validate_file_path",
    "strip_file_regex",
    "is_asset_supported",
    "config_path_to_args",
    "dict_to_args",
]


def is_asset_supported(path: str, filters: typing.List[str]) -> bool:
    """If the asset is supported by the specified filters."""
    # remove checkpoint if any
    url = omni.client.break_url(path)
    if not url:
        return False

    for filter_regex in filters:
        regex = re.compile(filter_regex, re.IGNORECASE)
        if regex.match(url.path):
            return True

    return False


def validate_file_path(file_path: str) -> Optional[str]:
    """Utility to address file picker issue which is returning url-escaped versions of special chars.
    If a raw path and path does not exist, returns the escaped file path if it exists, otherise returns None.
    """
    # file picker is incorrectly passing local file paths with %20 instead of spaces.
    omni_url = omni.client.break_url(file_path)
    # we check that the path is a raw path, and if the file path doesn't resolve...
    if omni_url.is_raw and not os.path.isfile(file_path):
        # replace %20 with spaces and check that the file path exists and use that.
        unquote_file_path = urllib.parse.unquote(file_path)
        if os.path.isfile(unquote_file_path):
            return unquote_file_path
        else:
            return None
    return file_path


def strip_file_regex(input_path: Path, file_regex_patterns) -> str:
    """Strips the input_path regex from input_path file; else, returns stem

    Args:
        input_path (Path): input file path
        file_regex_patterns: regex patterns to strip from input_path

    Returns:
        str: name of file without suffix
    """

    # Use re.search to check if the pattern exists in the input path
    match = re.search(file_regex_patterns, input_path.name, flags=re.IGNORECASE)
    if match:
        stripped_path = re.sub(file_regex_patterns, "", input_path.name, flags=re.IGNORECASE)
    else:
        stripped_path = str(input_path.stem)

    return stripped_path


def run_scene_opt(
    output_path: str,
    bOptimize: bool,
    bConvertHidden: bool,
    sOptimizeConfig: str = "",
    dMetersPerUnit: float = 0.0,
    iUpAxis: int = 0,
):
    """
    If the stage was successfully authored then execute the scene optimizer.
    """

    # we use Scene Optimizer to run the user's optimizer config, to generate UVs, or to remove hidden prims.
    if not sOptimizeConfig and not bOptimize and bConvertHidden and dMetersPerUnit == 0.0 and not iUpAxis == 0:
        return

    # TODO: We should probably check the conversion success rather than trusting that the ability to open the
    # Stage indicates success. This file path could already exist and we would edit it and save the changes.
    stage = Usd.Stage.Open(output_path)
    if stage:
        stage_cache = UsdUtils.StageCache().Get()

        # The Scene Optimizer execution context describes the stage to operate on.
        context = ExecutionContext()
        context.usdStageId = stage_cache.Insert(stage).ToLongInt()

        if sOptimizeConfig:
            omni.kit.commands.execute("SceneOptimizerJsonParser", context=context, args={"jsonFile": sOptimizeConfig})
        else:
            # TODO: Log a warning if Scene Optimization fails.
            if not bConvertHidden:
                # Gather hidden prims following DeleteHiddenPrimsOperation logic from Scene Optimizer
                # and call Scene Optimizer's deletePrims operation instead of 'DeletePrims' Kit command.
                # This is a workaround so we don't have to pass possibly risky destructive=True
                # to Kit's 'DeletePrims' command to get things working
                hidden_prim_paths = []
                it = iter(Usd.PrimRange.Stage(stage, Usd.PrimIsLoaded & ~Usd.PrimIsAbstract))

                for prim in Usd.PrimRange(stage.GetPseudoRoot()):
                    imageable = UsdGeom.Imageable(prim)
                    if imageable:
                        vis_attr = imageable.GetVisibilityAttr()
                        if vis_attr.Get() == UsdGeom.Tokens.invisible:
                            it.PruneChildren()
                            hidden_prim_paths.append(prim.GetPath().pathString)

                primPaths = str(hidden_prim_paths).replace("'", '"')
                operations = '[{"operation": "deletePrims", "primPaths": ' + primPaths + "}]"
                omni.kit.commands.execute("SceneOptimizerJsonParser", context=context, args={"jsonFile": operations})

            if bOptimize:
                # Default optimization is the generation of st texcoords where th 0-1 space represents a real world 1
                # meter surface area.
                operations = '[{"operation": "generateProjectionUVs", "projectionType": 4, "useWorldSpaceScales": true,  "scaleFactor": 1.0,  "scaleUnits": 1.0}]'
                omni.kit.commands.execute("SceneOptimizerJsonParser", context=context, args={"jsonFile": operations})

            if dMetersPerUnit:
                up_axis_token = UsdGeom.GetStageUpAxis(stage)
                up_axis = 1
                if up_axis_token == "Z":
                    up_axis = 2
                operations = (
                    '[{"operation": "editStageMetrics", "metersPerUnit": '
                    + str(dMetersPerUnit)
                    + ', "upAxis": '
                    + str(up_axis)
                    + " }]"
                )
                omni.kit.commands.execute("SceneOptimizerJsonParser", context=context, args={"jsonFile": operations})

            if iUpAxis:
                meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
                operations = (
                    '[{"operation": "editStageMetrics", "metersPerUnit": '
                    + str(meters_per_unit)
                    + ', "upAxis": '
                    + str(iUpAxis)
                    + " }]"
                )
                omni.kit.commands.execute("SceneOptimizerJsonParser", context=context, args={"jsonFile": operations})

        # Save the changes made to the Stage
        stage.Save()

        # Erase the stage from the stage cache to release the file handle
        stage_cache.Erase(stage_cache.GetId(stage))


def extract_zip_archive(archive_path: str) -> bool:
    """Extracts a ZIP file to the parent directory."""
    parent_folder = Path(archive_path).parent
    try:
        with zipfile.ZipFile(archive_path, "r") as zip_file:
            zip_file.extractall(parent_folder.as_posix())

        return True

    except (zipfile.BadZipFile, FileNotFoundError, OSError) as e:
        return False


def config_path_to_args(config_path: str) -> dict:
    """Convert values from a config file to FileFormatArgument"""
    file_format_args = {}
    if config_path and os.path.isfile(config_path):
        with open(config_path, "r") as f:
            data = json.load(f)
            # convert value to str for dict[str, str]
            for key, value in data.items():
                # converter expects bool strings in lower case
                if isinstance(value, bool):
                    file_format_args[key] = str(value).lower().replace("'", '"')
                else:
                    file_format_args[key] = str(value).replace("'", '"')
    return file_format_args


def dict_to_args(config_data: dict) -> dict:
    """Convert values from json object to FileFormatArgument"""
    file_format_args = {}
    for key, value in config_data.items():
        # converter expects bool strings in lower case
        if isinstance(value, bool):
            file_format_args[key] = str(value).lower().replace("'", '"')
        else:
            file_format_args[key] = str(value).replace("'", '"')
    return file_format_args


class ConverterStatus(NamedTuple):
    """
    Represents the conversion status
    """

    error_code: int = -1
    error_msg: str = ""


@dataclass
class ConverterFilterData:
    """
    Used to hold information about a CAD Converters supported file types
    """

    name: str
    """Name of the CAD Converter and the native application"""
    filter_regexes: List[str]
    """List of the supported file extensions"""
    filter_descriptions: List[str]
    """Description of the supported file extensions"""


class UsdSuffix(str, Enum):
    """Enums for USD Suffixes"""

    USD = "usd"  #: USD (Universal Scene Description) file format
    USDC = "usdc"  #: USD Crate File Format
    USDA = "usda"  #: USDA are human-readable and editable USD files
