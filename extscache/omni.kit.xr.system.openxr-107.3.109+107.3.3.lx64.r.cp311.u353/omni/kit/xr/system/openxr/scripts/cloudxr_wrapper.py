# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Use these at your own risk, and forward-compatability is not supported

__all__ = ["get_cloudxr_runtime_version"]

from .._xr_openxr import get_cloudxr_runtime_version_internal


def get_cloudxr_runtime_version():
    """
    Get the runtime version (major, minor, patch) of the bundled CloudXR service.

    Returns:
        tuple: The runtime version (major, minor, patch) of the bundled CloudXR service.
    """

    # Memoize the result to avoid loading the library every time
    if not hasattr(get_cloudxr_runtime_version, "result"):
        get_cloudxr_runtime_version.result = get_cloudxr_runtime_version_internal()
    return get_cloudxr_runtime_version.result
