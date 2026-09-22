# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import re
from typing import List

import carb
import carb.tokens
import omni.client


async def get_subidentifier_from_mdl_async(mdl_file: str) -> List[str]:
    if not mdl_file:
        return []

    mdl_file = carb.tokens.get_tokens_interface().resolve(mdl_file)
    result, _, content = await omni.client.read_file_async(mdl_file)
    if result != omni.client.Result.OK:
        carb.log_error(f"get_subidentifier_from_material: Failed to read file {mdl_file}")
        return []

    re_material_in_mdl = re.compile(r"export\s+material\s+([^\s]+)\s*\(")
    mtl_list = []
    try:
        for line in memoryview(content).tobytes().decode("utf-8").splitlines():
            # get material names from MDL file
            for match in re.finditer(re_material_in_mdl, line):
                mtl_list.append(match.group(1))
    except UnicodeDecodeError:
        carb.log_error(f"Failed to parse {mdl_file}")

    return mtl_list
