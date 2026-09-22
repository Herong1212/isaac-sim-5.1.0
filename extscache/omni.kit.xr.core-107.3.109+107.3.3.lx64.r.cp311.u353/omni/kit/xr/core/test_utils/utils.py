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
from typing import Optional

import omni.kit.app


def get_test_name_and_file_name(test_image_name: str, test_file_name: Optional[str], type_name: str) -> str:
    # That should be a name of a method or class which invoked that function
    if not test_file_name:
        raise ValueError(f"cannot split {test_file_name=}")
    suffix_of_test_file_name = test_file_name.split(".")[-1]
    # To keep it unique and not override generated images
    test_name_and_file_name = f"{suffix_of_test_file_name}.{test_image_name}.{type_name}"

    return test_name_and_file_name


def get_ext_id_by_file_name(file_name: Optional[str]) -> str:
    """
    Return extension ID based on a name of the file inside that extension folder
    """

    full_ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(file_name)
    ext_id_without_version = full_ext_id.split("-")[0]

    return ext_id_without_version
