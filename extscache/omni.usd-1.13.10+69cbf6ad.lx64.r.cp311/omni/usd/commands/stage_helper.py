# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pxr import Usd
from pxr import UsdUtils
from typing import Optional


class UsdStageHelper:
    """Keeps the stage ID or returns the stage from the current context"""

    def __init__(self, stage: Optional[Usd.Stage] = None, context_name : Optional[str] = None):
        self._set_stage(stage, context_name)

    def _set_stage(self, stage: Optional[Usd.Stage] = None, context_name : Optional[str] = None):
        """Save stage ID or context name"""
        if stage is not None:
            self.__stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
            self.__context_name = None
        elif context_name is not None:
            self.__stage_id = None
            self.__context_name = context_name
        else:
            self.__stage_id = None
            self.__context_name = ""

    def _get_context(self) -> Optional["omni.usd.context"]:
        import omni.usd

        if self.__context_name is not None:
            return omni.usd.get_context(self.__context_name)

        return omni.usd.get_context()

    def _get_stage(self) -> Optional[Usd.Stage]:
        """Get staved stage"""
        if self.__stage_id is not None:
            # Get the stage from ID
            cache = UsdUtils.StageCache.Get()
            stage = cache.Find(Usd.StageCache.Id.FromLongInt(self.__stage_id))
            return stage

        return self._get_context().get_stage()
