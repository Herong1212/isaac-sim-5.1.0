# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import os
from typing import Callable, List, Tuple

if hasattr(os, "add_dll_directory"):
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    dlldir = os.path.abspath(os.path.join(scriptdir, "../../bin"))
    if os.path.exists(dlldir):
        # this is run in the independent resolver configuration
        with os.add_dll_directory(dlldir):
            from ._omni_usd_resolver import *
    else:
        # that directory isn't present in the kit carb plugin
        # configuration, so just try to load it
        from ._omni_usd_resolver import *
else:
    from ._omni_usd_resolver import *
