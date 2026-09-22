# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


# These scripts append more functions into C++ defined classes.
# We append classes rather then inherit from them so they can be used as inputs for the C++ classes as well

__all__ = ["XRSingleton", "XRSingletonType"]

from .xr_singleton import XRSingleton, XRSingletonType
