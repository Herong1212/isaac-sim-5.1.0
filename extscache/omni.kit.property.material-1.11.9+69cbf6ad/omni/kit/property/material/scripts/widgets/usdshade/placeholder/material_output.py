# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pxr import Usd

from ..utils import get_display_group_for_render_context, get_sdr_shader_node_for_prim


class MaterialOutput:
    def __init__(self, prim: Usd.Prim, is_universal_context: bool):
        self._prim = prim
        self._shader_types = set()
        self._display_group_suffix = ""

        # If this output is connected to the universal context determine what the underlying type of the
        # shader that is connected: i.e. MDL, MaterialX etc.
        if is_universal_context:
            sdr_shader_node = get_sdr_shader_node_for_prim(self._prim)
            if sdr_shader_node:
                self._display_group_suffix = (
                    f" ({get_display_group_for_render_context(sdr_shader_node.GetSourceType())})"
                )

    @property
    def prim(self) -> Usd.Prim:
        return self._prim

    @property
    def display_group_prefix(self) -> str:
        shader_types = list(self._shader_types)
        shader_types.sort()
        prefix = ", ".join(shader_types)
        return f"{prefix}{self._display_group_suffix}"

    def add_shader_type(self, shader_type: str) -> None:
        self._shader_types.add(shader_type.capitalize())
