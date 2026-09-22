# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni.kit.window.property.property_scheme_delegate import PropertySchemeDelegate

import NavSchema


class NavMeshAreaAPISchemeDelegate(PropertySchemeDelegate):
    def get_widgets(self, payload):
        widgets_to_build = []
        if self._should_enable_delegate(payload):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("navmesh_area_api")
            widgets_to_build.append("geometry")
            widgets_to_build.append("geometry_imageable")
        return widgets_to_build

    def get_unwanted_widgets(self, payload):
        unwanted_widgets_to_build = []
        unwanted_widgets_to_build.append("kind")
        return unwanted_widgets_to_build

    def _should_enable_delegate(self, payload):
        stage = payload.get_stage()
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if prim.HasAPI(NavSchema.NavMeshAreaAPI):
                        return True
            return False
        return False


class NavMeshExcludeAPISchemeDelegate(PropertySchemeDelegate):
    def get_widgets(self, payload):
        widgets_to_build = []
        if self._should_enable_delegate(payload):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("navmesh_exclude_api")
            widgets_to_build.append("geometry")
            widgets_to_build.append("geometry_imageable")
        return widgets_to_build

    def get_unwanted_widgets(self, payload):
        unwanted_widgets_to_build = []
        unwanted_widgets_to_build.append("kind")
        return unwanted_widgets_to_build

    def _should_enable_delegate(self, payload):
        stage = payload.get_stage()
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if prim.HasAPI(NavSchema.NavMeshExcludeAPI):
                        return True
            return False
        return False
