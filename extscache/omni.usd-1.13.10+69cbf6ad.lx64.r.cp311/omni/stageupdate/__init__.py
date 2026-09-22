# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from ._stageupdate import *

# Cached editor instance pointer
def get_stage_update_interface(name: str='') -> StageUpdate:
    """Returns StageUpdate with the given name via cached :class:`omni.usd.IStageUpdate` interface"""

    if not hasattr(get_stage_update_interface, "iface"):
        get_stage_update_interface.iface = acquire_stage_update_interface()
    return get_stage_update_interface.iface.get_stage_update(name)
