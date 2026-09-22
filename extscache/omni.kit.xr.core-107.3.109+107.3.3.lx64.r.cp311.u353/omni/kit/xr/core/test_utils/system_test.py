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

import omni.kit.app


async def run_system_test(test_case: omni.kit.test.AsyncTestCase, system_name: str, test_name: str) -> None:
    """
    Run a C++ test embedded inside the XRSystem

    Args:
        system_name:    name of the system
        test_name:      name of the test
    """

    try:
        omni.kit.xr.core.XRCore.get_singleton().test_system(system_name, test_name)
    except RuntimeError as e:
        test_case.fail(f"An error occurred while running test {system_name}:{test_name}:\n  {e}")
