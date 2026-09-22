# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# Those tests work only when `omni.services.core` extension is enabled, otherwise skip those tests.
# Any other import error will be raised, not to skip actual errors:
try:
    from .test_local_client import *
    from .test_url_parsing import *
except ModuleNotFoundError as e:
    if e.name != "omni.services.core":
        raise e
