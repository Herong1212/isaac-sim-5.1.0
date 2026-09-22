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
import tempfile
import typing
from dataclasses import dataclass
from pathlib import Path

import carb
import pydantic
from fastapi import status
from omni.kit.converter.common import is_asset_supported, validate_file_path
from omni.services.core import exceptions, routers
from pxr import Usd

from .constants import Constants as constants
from .progress_facility import ProgressFacility
from .subprocess_convert import subprocess_convert

__all__ = [
    "RegisteredConverter",
    "ConverterRegistry",
    "ProgressFacility",
    "RegistryResponseModel",
    "ConverterResponseModel",
    "RequestRunModel",
]

router = routers.ServiceAPIRouter()


@dataclass
class RegisteredConverter:
    id: int
    filters: typing.List[str]  # Supported file formats
    convert_fn: typing.Callable[..., str]  # Converter entry point for each backend
    options_cls: type  # Converter Options Class for each backend


class ConverterRegistry:
    _registered_converters: typing.List[RegisteredConverter] = []
    _register_converter_id: int = 0

    @staticmethod
    def register_converter(filters: typing.List[str], convert_fn: typing.Callable[..., str], options_cls: type):
        """Register a frame build function."""
        ConverterRegistry._register_converter_id += 1
        carb.log_info(f"Registering converter {ConverterRegistry._register_converter_id}: for {filters}...")
        converter = RegisteredConverter(ConverterRegistry._register_converter_id, filters, convert_fn, options_cls)
        ConverterRegistry._registered_converters.insert(0, converter)
        return ConverterRegistry._register_converter_id

    @staticmethod
    def unregister_converter(converter_id: int):
        carb.log_info(f"Unregistering converter: {converter_id}...")
        """Un-Register a frame build function."""
        for converter in ConverterRegistry._registered_converters:
            if converter.id == converter_id:
                ConverterRegistry._registered_converters.remove(converter)

    @staticmethod
    def converters():
        """Returns a view of all the converters in the registry."""
        return ConverterRegistry._registered_converters.copy()

    @staticmethod
    def get_converter_for_file(file_in: str):
        """Get a converter for a given file."""
        for converter in ConverterRegistry.converters():
            # if its filters supports the imported file and this is the converter the user wants to use
            if is_asset_supported(file_in, converter.filters):
                return converter
        return None


class RegistryResponseModel(pydantic.BaseModel):
    status: int = pydantic.Field(..., title="Registry Status", description="Registry status response message.")
    comment: str = pydantic.Field(..., title="Comment", description="Additional information on the registry status.")


class ConverterResponseModel(pydantic.BaseModel):
    status: int = pydantic.Field(..., title="Converter status", description="Converter status response message.")
    comment: str = pydantic.Field(..., title="Comment", description="Additional information on the converter status.")


class RequestRunModel(pydantic.BaseModel):
    """Request Model for CAD Converter task

    Args:
        import_path (str): Full path to source asset (CAD File).
        output_path (str): Full path to the output directory for converted files.
        converter_options (dict): Converter options to use (optional).
        config_path (str): Full path to the user config JSON. (optional)
    """

    import_path: str = pydantic.Field(
        ..., title="Source Asset Path", description="Full path to source asset (CAD File)."
    )
    output_path: str = pydantic.Field(
        ..., title="Target Folder Path", description="Full path to the output directory for converted files."
    )
    converter_options: typing.Optional[dict] = pydantic.Field(
        {}, title="Converter Options", description="Dictionary representing the Converter options to use. (optional)"
    )
    config_path: typing.Optional[str] = pydantic.Field(
        "", title="User Config Path", description="Full path to the user config JSON. (optional)"
    )


@router.post(
    path="/process",
    summary="CAD Converter Service.",
    description="Convert CAD Files to USD.",
    response_model=ConverterResponseModel,
)
async def asset_convert(
    req: RequestRunModel,
    progress_facility: ProgressFacility = router.get_facility("progress"),
) -> ConverterResponseModel:

    if validate_file_path(req.import_path) is None:
        raise exceptions.KitServicesBaseException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File does not exist {req.import_path}",
        )

    # Unsupported output format
    if not Usd.Stage.IsSupportedFile(req.output_path):
        raise exceptions.KitServicesBaseException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Provided output_path isn't supported. {req.output_path}",
        )

    # if converter_options is provided from POST request, we save the dict to a temp file
    # and pass that file path to the subprocess to avoid potentially long command line argument
    # and string escaping
    config_path = req.config_path
    temp_config_path = None
    # if req.converter_options dict is not empty
    if req.converter_options:
        # create a temp config .json file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_config_path = temp_file.name
            with open(temp_config_path, "w") as config_file:
                json.dump(req.converter_options, config_file)

    ret = None
    if temp_config_path is None:
        ret = await subprocess_convert(req.import_path, req.output_path, config_path, progress_facility)
    else:
        ret = await subprocess_convert(req.import_path, req.output_path, temp_config_path, progress_facility)
        os.remove(temp_config_path)

    if ret:
        return ConverterResponseModel(
            status=status.HTTP_200_OK,
            comment=f"File {req.import_path} was successfully converted to {req.output_path}.",
        )
    else:
        msg = "Unexpected error - no output path returned!"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg,
        )
