# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import carb
import requests

# The functions in this file are modified copies of the ones in the sample repo.
# https://github.com/NVIDIA/nv-cloud-function-helpers/blob/main/nv_cloud_function_helpers/nvcf_container/helpers.py


def _uppercase_dict_keys(d: dict) -> dict:
    """
    Converts all keys in a dictionary to upper case
    :param d: the target dictionary
    :return: key value pairs in upper case
    """
    return {k.upper(): v for k, v in d.items()}


def get_request_id(request_parameters: dict) -> str:
    """
    Get the reqId of the invocation (NVCF-REQID) from the function invocation message
    :param request_parameters: a dict of the parameters passed to the function
    :return: request id string
    """
    request_parameters = _uppercase_dict_keys(request_parameters)
    return request_parameters.get("NVCF-REQID", "")


def get_input_path(request_parameters: dict) -> str:
    """
    Gets the storage location (file path) where large input assets sent to the function (NVCF-ASSET-DIR)
    from the function invocation message
    :param request_parameters: a dict of the parameters passed to the function
    :return: asset input path string
    """
    request_parameters = _uppercase_dict_keys(request_parameters)
    request_id = get_request_id(request_parameters)
    input_assets_path_base = request_parameters.get("NVCF-ASSET-DIR", f"/var/inf/inputAssets/{request_id}")
    return input_assets_path_base


def get_asset_ids(request_parameters: dict) -> list:
    """
    Get the asset_ids of the invocation (NVCF-FUNCTION-ASSET-IDS) from the function invocation message
    :param request_parameters: a dict of the parameters passed to the function
    :return: list of asset ids
    """
    request_parameters = _uppercase_dict_keys(request_parameters)
    s = request_parameters.get("NVCF-FUNCTION-ASSET-IDS", "")
    ids = s.split(",")
    return ids


def get_service_api_key() -> str:
    """
    Get the NGC Service API Key from environment variable
    :return: NGC Service API Key
    """
    if "NGC-SERVICE-KEY" in os.environ:
        return os.environ.get("NGC-SERVICE-KEY")
    else:
        carb.log_error("NGC-SERVICE-KEY not found")


def get_large_output_directory(request_parameters: dict) -> str:
    """
    Get the large output directory from the function invocation message
    :param request_parameters: a dict of the parameters passed to the function
    :return: accept-encoding string
    """
    request_parameters = _uppercase_dict_keys(request_parameters)
    return request_parameters.get("NVCF-LARGE-OUTPUT-DIR", "")


def get_upload_presigned_url(api_key: str, description: str):
    """
    Get presigned URL to upload the converted file to.
    :param api_key: NGC API Key
    :param description: File description
    :return: presigned uploadUrl and assetId
    """
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json", "Content-Type": "application/json"}

    # https://openusd.org/release/spec_usdz.html#mime-type
    data = {"contentType": "application/vnd.usdz+zip", "description": description}
    response = requests.post("https://api.nvcf.nvidia.com/v2/nvcf/assets", headers=headers, data=json.dumps(data))

    response_data = response.json()
    upload_url = response_data.get("uploadUrl")
    asset_id = response_data.get("assetId")

    if response.status_code == 200:
        return upload_url, asset_id
    else:
        return None, None


def upload_output_file(url: str, output_path: str, description: str):
    """
    Upload converted file to presigned URL
    :param url: Presigned URL to upload file to
    :param output_path: output file path
    :param description: output file description
    """
    headers = {"Content-Type": "application/vnd.usdz+zip", "x-amz-meta-nvcf-asset-description": description}
    with open(output_path, "rb") as file:
        response = requests.put(url, headers=headers, data=file)

        return response.status_code == 200


def get_download_presigned_url(api_key: str, asset_id: str):
    """
    Get presigned URL to download the file
    :param api_key: NGC API Key
    :asset_id: ID of the asset to download
    """
    url = f"https://api.nvcf.nvidia.com/v2/nvcf/assets/{asset_id}/content-redirect"
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json", "Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    response_data = response.json()
    presigned_url = response_data.get("presignedUrl")

    if response.status_code == 200:
        return presigned_url
    else:
        return None
