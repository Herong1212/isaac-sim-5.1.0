# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from typing import Optional

import carb
import omni.client
import omni.kit.asset_converter
import omni.kit.converter.common.nvcf_common as nvcf_helpers
import pydantic
from fastapi import Depends, Header, Request, status
from fastapi.responses import JSONResponse
from omni.kit.converter.common.common import extract_zip_archive, is_asset_supported, validate_file_path
from omni.services.core import exceptions, routers
from pxr import Usd

from .. import _utils

__all__ = [
    "CustomBaseModel",
    "ProgressMonitor",
    "RequestRunModel",
]

# asset converter supported formats
SUPPORTED_FORMATS = [
    "(.*\\.fbx$)",
    "(.*\\.obj$)",
    "(.*\\.gltf$)",
    "(.*\\.*glb$)",
    "(.*\\.lxo$)",
    "(.*\\.md5$)",
    "(.*\\.stl$)",
    "(.*\\.bvh$)",
]

router = routers.ServiceAPIRouter()

ConverterContext = _utils.create_dynamic_model("ConverterContext", omni.kit.asset_converter.AssetConverterContext)


class CustomBaseModel(pydantic.BaseModel):
    @classmethod
    def validate(cls, value):
        """overwrite classmethod validate to log error and notify user when the payload is incorrect."""
        try:
            return super().validate(value)
        except pydantic.ValidationError as e:
            carb.log_error(f"Validation error in model {cls.__name__}: {e}")
            sample_input = '{ "import_path": "", "output_path": "", "converter_settings": {} }'
            raise exceptions.KitServicesBaseException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error in model, payload: {sample_input}",
            )


class RequestRunModel(CustomBaseModel):
    """Request Model for Asset Converter task

    Args:
        import_path (str): Full path to source asset (CAD File).
        output_path (str): Full path to the output file.
        converter_settings (dict): Converter context object, settings.
        archive_path (str): Archived input asset.
    """

    import_path: str = pydantic.Field(
        ..., title="The source asset.", description="Full path to source asset (CAD File)."
    )
    output_path: str = pydantic.Field(
        ..., title="The target asset.", description="Asset format is decided by the output path's extension."
    )
    converter_settings: ConverterContext
    archive_path: Optional[str] = pydantic.Field(
        "",
        title="Archive path",
        description="Optional path to `.zip`, `.tar`, or `.tar.gz` archive that contains the input file(s)",
    )


class RequestNVCFModel(CustomBaseModel):
    """Request Model for Asset Converter task

    Args:
        import_path (str): Full path to source asset (CAD File).
        output_path (str): Full path to the output file.
        converter_settings (dict): Converter context object, settings.
    """

    import_path: str = pydantic.Field(
        ..., title="The source asset.", description="Full path to source asset (CAD File)."
    )
    output_path: str = pydantic.Field(
        ..., title="The target asset.", description="Asset format is decided by the output path's extension."
    )
    converter_settings: ConverterContext


@router.post(
    path="/process_nvcf",
    summary="Asset Converter Service for NVCF.",
    description="Convert between supported CAD formats.",
)
async def asset_convert(
    req: RequestNVCFModel,
    request: Request = None,
    metrics=router.get_facility("metrics"),
):
    carb.log_info(f"Collecting NVCF headers.")
    headers = request.headers
    request_parameters_dict = nvcf_helpers._uppercase_dict_keys(headers)
    # value in NVCF-REQID (automatically assigned by NVCF)
    request_id = nvcf_helpers.get_request_id(request_parameters_dict)
    # value in `NVCF-ASSET-DIR`
    input_path = nvcf_helpers.get_input_path(request_parameters_dict)
    # values in `NVCF-FUNCTION-ASSET-IDS`
    asset_ids = nvcf_helpers.get_asset_ids(request_parameters_dict)
    archive_path = os.path.join(input_path, asset_ids[0])
    # value in `NVCF-LARGE-OUTPUT-DIR`
    large_output_dir = nvcf_helpers.get_large_output_directory(request_parameters_dict)
    # construct an output path in the large output dir to write the output USD file.
    output_path = os.path.join(large_output_dir, req.output_path)

    carb.log_info(f"Validating inputs for request: {request_id}.")
    # Validate archive path exists.
    if validate_file_path(archive_path) is None or not os.path.isfile(archive_path):
        msg = f"Archive path does not exist! Recieved: {archive_path}"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=msg)

    # Validate input file format is supported by converter.
    if not is_asset_supported(req.import_path, SUPPORTED_FORMATS):
        msg = f"Input file format is not supported! Recieved: {req.import_path}"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)

    # Unsupported output format.
    if not Usd.Stage.IsSupportedFile(output_path):
        msg = f"Output file is not supported! Supported formats: `.usd`, `.usda`, '.usdc'"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)

    # Extract archive that should contain the CAD files without a top level folder.
    # NOTE: we assume this is a zip file, i.e. the client uploads a zip file.
    if not extract_zip_archive(archive_path):
        msg = f"Failed to extract from archive {archive_path}! Only .zip files are supported at this time!"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)

    # Construct full path to point at the head file.
    # NOTE: req.import_path is a relative path to the head file.
    head_file = os.path.join(input_path, req.import_path)
    if validate_file_path(head_file) is None:
        msg = f"Head file does not exist! Recieved: {head_file}"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=msg)

    carb.log_info(f"Starting asset conversion, path: {head_file}")

    process_time = metrics.summaries(
        "convert_asset_time", "Time taken to convert given asset", labelnames=("input_file", "output_file")
    )
    progress_callback = ProgressMonitor()
    try:
        task = omni.kit.asset_converter.get_instance().create_converter_task(
            head_file, output_path, progress_callback.progress, req.converter_settings
        )

        with process_time.labels(input_file=req.import_path, output_file=output_path).time():
            success = await task.wait_until_finished()
            if not success:
                detailed_status_code = task.get_status()
                detailed_status_error_string = task.get_detailed_error()
                raise exceptions.KitServicesBaseException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to convert {req.import_path}. Error: {detailed_status_code}, {detailed_status_error_string}",
                )

        # Validate output path exists.
        if not os.path.isfile(output_path):
            msg = f"Output path does not exist! Failed to write: {output_path}"
            carb.log_error(msg)
            raise exceptions.KitServicesBaseException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=msg)

        carb.log_info(f"Asset {req.import_path} is converterted!")

        # upload to storage and return download presigned URL and asset ID to user
        api_key = nvcf_helpers.get_service_api_key()
        upload_presigned_url, asset_id = nvcf_helpers.get_upload_presigned_url(api_key, req.output_path)
        if upload_presigned_url == None:
            carb.log_error(f"Failed to generate storage presigned URL.")
            raise exceptions.KitServicesBaseException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate storage presigned URL.",
            )

        upload_success = nvcf_helpers.upload_output_file(upload_presigned_url, output_path, req.output_path)
        if not upload_success:
            carb.log_error(f"Failed to upload result to storage.")
            raise exceptions.KitServicesBaseException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to upload result to storage.",
            )
        download_url = nvcf_helpers.get_download_presigned_url(api_key, asset_id)
        if download_url == None:
            carb.log_error(f"Failed to generate download presigned URL.")
            raise exceptions.KitServicesBaseException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate download presigned URL.",
            )

        # delete output file from server so that NVCF doesn't return a zip response
        os.remove(output_path)

        content = {
            "status": status.HTTP_200_OK,
            "asset_id": asset_id,
            "description": req.output_path,
            "download_url": download_url,
        }

        return JSONResponse(content=content)

    except Exception as exc:
        carb.log_error(f"Failed to convert {req.import_path}. Error: {str(type(exc))} {str(exc)}")
        raise exceptions.KitServicesBaseException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert {req.import_path}. Error: {str(type(exc))} {str(exc)}",
        )


@router.post(
    path="/process",
    summary="Asset Converter Service.",
    description="Convert between supported CAD formats.",
)
async def asset_convert(
    req: RequestRunModel,
    metrics=router.get_facility("metrics"),
):
    carb.log_info("Validating inputs.")
    # Validate input path exists.
    if validate_file_path(req.import_path) is None:
        msg = f"Input file path does not exist! Recieved: {req.import_path}"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=msg)

    # Validate input file format is supported by converter.
    if not is_asset_supported(req.import_path, SUPPORTED_FORMATS):
        msg = f"Input file format is not supported! Recieved: {req.import_path}"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)

    # Unsupported output format.
    if not Usd.Stage.IsSupportedFile(req.output_path):
        msg = f"Output file is not supported! Supported formats: `.usd`, `.usda`, '.usdc'"
        carb.log_error(msg)
        raise exceptions.KitServicesBaseException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)

    # Extract archive to get unmanged import_path in order to work with NVCF asset management
    if req.archive_path:
        if _utils.unpack_archive(req.archive_path):
            carb.log_info(f"Archive {req.archive_path} extracted!")
        else:
            msg = f"Failed to extract from archive {req.archive_path}! Supported formats: `.zip`, `.tar`, `.tar.gz`"
            carb.log_error(msg)
            raise exceptions.KitServicesBaseException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)

    carb.log_info(f"Starting asset conversion, path: {req.import_path}")

    process_time = metrics.summaries(
        "convert_asset_time", "Time taken to convert given asset", labelnames=("input_file", "output_file")
    )
    progress_callback = ProgressMonitor()
    try:
        task = omni.kit.asset_converter.get_instance().create_converter_task(
            req.import_path, req.output_path, progress_callback.progress, req.converter_settings
        )

        with process_time.labels(input_file=req.import_path, output_file=req.output_path).time():
            success = await task.wait_until_finished()
            if not success:
                detailed_status_code = task.get_status()
                detailed_status_error_string = task.get_detailed_error()
                raise exceptions.KitServicesBaseException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to convert {req.import_path}. Error: {detailed_status_code}, {detailed_status_error_string}",
                )

        carb.log_info(f"Asset {req.import_path} is converterted!")
        return {"status": "finished"}

    except Exception as exc:
        carb.log_error(f"Failed to convert {req.import_path}. Error: {str(type(exc))} {str(exc)}")
        raise exceptions.KitServicesBaseException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert {req.import_path}. Error: {str(type(exc))} {str(exc)}",
        )


class ProgressMonitor:

    def progress(self, step, total_steps):
        carb.log_info(f"step {step} of {total_steps} finished.")
