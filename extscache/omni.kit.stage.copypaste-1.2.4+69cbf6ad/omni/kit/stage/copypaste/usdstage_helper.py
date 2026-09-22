# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["UsdStageHelper"]

from typing import Optional

import omni.kit.app

from pxr import Usd
from pxr import UsdUtils


@omni.kit.app.deprecated("Import from omni.usd.commands instead.")
class UsdStageHelper:
    """DEPRECATED: Keeps the stage ID or returns the stage from the current context"""

    def __init__(self, stage: Usd.Stage):
        if stage:
            # Keep ID so the command doesn't prevent the stage from closing.
            self.__stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
        else:
            self.__stage_id = None

    def _get_stage(self) -> Optional[Usd.Stage]:
        if self.__stage_id:
            # Get the stage from ID
            cache = UsdUtils.StageCache.Get()
            stage = cache.Find(Usd.StageCache.Id.FromLongInt(self.__stage_id))
            return stage

        # Get the stage from the context
        import omni.usd

        return omni.usd.get_context().get_stage()
