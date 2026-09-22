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
import json
import os

import carb
import omni.client
import omni.kit.converter.jt_core
from omni.kit.converter.common import config_path_to_args


def _convert(input_path, output_path, config_path):
    # call the JT Core API
    async def convert_async():
        jt_converter = omni.kit.converter.jt_core.get_instance()
        file_format_args = config_path_to_args(config_path)
        _, status = await jt_converter.create_converter_task(input_path, output_path, file_format_args)
        if status.error_code == 0:
            carb.log_info(f"JT file Conversion is successful")
        else:
            carb.log_error(f"JT file Conversion failed: error_code {status.error_code}, error_msg {status.error_msg}")

    asyncio.run(convert_async())


def main():
    carb.log_info(f"Starting JT File Conversion")
    # Parse cmd args
    parser = argparse.ArgumentParser("JT Converter Import")
    parser.add_argument("--input-path", type=str, help="Full Path to input CAD file.", required=True)
    parser.add_argument("--output-path", type=str, help="Full Path to USD file output.", required=True)
    parser.add_argument("--config-path", type=str, help="Full Path to Converter Options JSON file.", required=True)

    args = parser.parse_args()
    _convert(args.input_path, args.output_path, args.config_path)


main()
