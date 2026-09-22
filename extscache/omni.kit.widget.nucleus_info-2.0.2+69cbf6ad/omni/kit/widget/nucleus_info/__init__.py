# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""
This module provides functions to check service availability and retrieve nucleus services both synchronously and asynchronously using the nucleus info extension.
"""


__all__ = [
    "is_service_available",
    "get_nucleus_services",
    "get_nucleus_services_async",
]

from .extension import NucleusInfoExtension, is_service_available, get_nucleus_services, get_nucleus_services_async
import omni.kit.app
