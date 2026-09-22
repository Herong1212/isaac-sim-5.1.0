# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import argparse
import asyncio
import getpass
import os
import re
import uuid
from typing import Dict, List

import aiohttp
import carb
import omni.client

# Disable hang detection on omni.client
omni.client.set_hang_detection_time_ms(0)

# Supported file format by converter type
FILTER_DGN = {"DGN Converter": ["(.*\\.DGN$)"]}  # "DGN Converter"
FILTER_HOOPS = {
    "CAD Converter": [
        "(.*\\.CATDrawing$)|(.*\\.CATPart$)|(.*\\.CATProduct$)|(.*\\.CATShape$)|(.*\\.CGR$)",
        "(.*\\.ifc$)|(.*\\.ifczip$)",
        "(.*\\.prt$)",
        "(.*\\.xmt$)|(.*\\.x_t$)|(.*\\.x_b$)|(.*\\.xmt_txt$)",
        "(.*\\.sldprt$)|(.*\\.sldasm$)",
        "(.*\\.stl$)",
        "(.*\\.IPT$)|(.*\\.IAM$)",
        "(.*\\.3DXML$)",
        "(.*\\.DWG$)|(.*\\.DXF$)",
        "(.*\\.ASM$)|(.*\\.NEU$)|(.*\\.PRT$)|(.*\\.XAS$)|(.*\\.XPR$)",
        "(.*\\.RVT$)|(.*\\.RFA$)",
        "(.*\\.ASM$)|(.*\\.PAR$)|(.*\\.PWD$)|(.*\\.PSM$)",
        "(.*\\.STEP$)|(.*\\.STP$)|(.*\\.IGES$)|(.*\\.IGS$)",
    ]
}  # "CAD Converter"
FILTER_JT = {"JT Converter": ["(.*\\.jt$)"]}  # "JT Converter"
OUTPUT_FORMAT = ".usd"  # .usd/.usda/.usdc
SUPPORTED_FORMATS = [FILTER_DGN, FILTER_HOOPS, FILTER_JT]


def _is_supported(path: str, filters: List[str]) -> bool:
    """If the asset is supported by this importer."""
    # remove checkpoint if any
    url = omni.client.break_url(path)
    if not url:
        return False

    for filter_regex in filters:
        regex = re.compile(filter_regex, re.IGNORECASE)
        if regex.match(url.path):
            return True
    return False


def _get_converter_for_file_type(file_in: str) -> str:
    """Get a converter for a given file extension.
    Available converters: CAD Converter/DGN Converter/JT Converter"""
    converter = "CAD Converter"
    for filter in SUPPORTED_FORMATS:
        # Get filter regex and check if its filters supports the imported file
        if _is_supported(file_in, list(filter.values())[0]):
            converter = list(filter.keys())[0]
            return converter
    return None  # No compatible converter


def validate_head_files(heads_path: str) -> Dict[str, List[str]]:
    """Validate and group CAD files per converter."""
    path_dict = {"CAD Converter": [], "DGN Converter": [], "JT Converter": []}
    heads_file = open(heads_path)
    for head in heads_file.readlines():
        head = head.strip()
        converter_type = _get_converter_for_file_type(head)
        if converter_type:
            carb.log_info(f"Processing head file: {head}")
            path_dict[converter_type].append(head)
    heads_file.close()

    return path_dict


async def _run(heads_list: str, output_dir: str, converter_settings: Dict = None, farm_url: str = None) -> None:
    try:
        path_dict = validate_head_files(heads_list)
        for converter_name, valid_paths in path_dict.items():
            await _submit_to_farm(farm_url, valid_paths, output_dir, converter_settings)
    except Exception as exc:
        carb.log_error(str(exc))
    finally:
        omni.kit.app.get_app().post_quit()


async def _submit_to_farm(farm_url: str, paths: List[str], output_dir: str, settings: Dict) -> None:

    batch_id = str(uuid.uuid4())
    last_index = len(paths) - 1

    for idx, path in enumerate(paths):
        path_no_ext = path[: path.rfind(".")]
        output_path = path_no_ext + OUTPUT_FORMAT
        if output_dir:
            filename = os.path.basename(output_path)
            output_path = "/".join((output_dir, filename))

        data = {
            "user": getpass.getuser(),
            "task_type": "cad-converter",
            "task_args": {},
            "task_function": "convert.cad.process",
            "task_function_args": {"import_path": path, "output_path": output_path, "converter_settings": settings},
            "task_comment": f"Converting asset: {path}",
            "metadata": {"batches": {"last_index": last_index, "batch_id": batch_id, "index": idx}},
        }
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(f"{farm_url}/queue/management/tasks/submit", json=data):
                carb.log_info(f"Submitted path {path} to be converted to {output_path}")


def main():
    parser = argparse.ArgumentParser("Converter task submit")

    parser.add_argument("--heads-list", type=str, help="Text file containing head files for assemblies", required=True)

    parser.add_argument(
        "--output-dir", type=str, help="Output directory, where the converted assets will be written", required=True
    )

    parser.add_argument("--farm-url", type=str, help="FARM URL to submit converter tasks", required=True)

    args = parser.parse_args()
    heads_list = args.heads_list
    output_dir = args.output_dir
    farm_url = args.farm_url

    to_pop = ["heads_list", "output_dir", "farm_url"]
    converter_settings = vars(args)
    for key in to_pop:
        converter_settings.pop(key, None)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        _run(
            heads_list,
            output_dir,
            converter_settings=converter_settings,
            farm_url=farm_url,
        )
    )
    loop.run_until_complete(future)


main()  # Call as a script.
