# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import ValuesView

from pxr import Usd, UsdShade

from ..utils import get_display_group_for_render_context
from .material_output import MaterialOutput


class MaterialContext:
    def __init__(self, render_context: str):
        self._render_context = render_context
        self._outputs = {}
        self._display_group_prefix = render_context
        self._is_universal_context = render_context == UsdShade.Tokens.universalRenderContext

        if self._is_universal_context:
            self._display_group_prefix = "Default"

        else:
            self._display_group_prefix = get_display_group_for_render_context(render_context)

    @property
    def render_context(self) -> str:
        return self._render_context

    @property
    def display_group_prefix(self) -> str:
        return self._display_group_prefix

    @property
    def outputs(self) -> ValuesView[MaterialOutput]:
        return self._outputs.values()

    def add_output(self, shader_type: str, prim: Usd.Prim) -> None:
        prim_path = prim.GetPath()

        if prim_path not in self._outputs:
            self._outputs[prim_path] = MaterialOutput(prim, self._is_universal_context)

        self._outputs[prim_path].add_shader_type(shader_type)
