# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .singleton import Singleton


@Singleton
class ShaderRegistry:
    def __init__(self):
        self._contexts = {}

    def Get(self, context):
        reg = self._contexts.get(context, None)

        if not reg:
            if context == "mdl":
                from .mdl_registry import MdlRegistry

                reg = MdlRegistry()
                self._contexts["mdl"] = reg

        return reg
