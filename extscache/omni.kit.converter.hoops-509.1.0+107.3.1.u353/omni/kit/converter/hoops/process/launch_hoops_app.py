# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from omni.kit.converter.common import config_path_to_args
from omni.kit.converter.hoops_core import get_instance


def _convert(input_path, output_path, config_path):
    # call the HOOPS Core API
    async def convert_async():
        hoops_converter = get_instance()
        file_format_args = config_path_to_args(config_path)
        _, status = await hoops_converter.create_converter_task(input_path, output_path, file_format_args)
        if status.error_code == 0:
            carb.log_info(f"File conversion is successful")
        else:
            carb.log_error(f"File conversion failed: error_code {status.error_code}, error_msg {status.error_msg}")

    asyncio.run(convert_async())


def main():
    carb.log_info(f"Starting File Conversion")
    # Parse cmd args
    parser = argparse.ArgumentParser("HOOPS Converter Import")
    parser.add_argument("--config-path", type=str, help="Full Path to Converter Options JSON file.", required=True)
    parser.add_argument("--input-path", type=str, help="Full path to the input file", required=True)
    parser.add_argument("--output-path", type=str, help="Desired full path of the usd output file", required=True)

    args = parser.parse_args()
    _convert(args.input_path, args.output_path, args.config_path)


main()
