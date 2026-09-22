# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
from dataclasses import dataclass

import omni.converter.jtk
from omni.kit.converter.common import UsdSuffix

__all__ = ["JTConverterOptions", "UsdSuffix"]


@dataclass
class JTConverterOptions(omni.converter.jtk.Parameters):
    """
    JT converter settings base class.
    """

    # legacy options before Hungarian notations removal
    bInstancing: bool = True
    bOptimize: bool = True
    bConvertHidden: bool = False
    materialSelection = int(omni.converter.jtk.MaterialType.ePreviewSurface)
    sOptimizeConfig: str = ""
    iUpAxis: int = 0
    dMetersPerUnit: float = 0.0

    def __init__(self):
        omni.converter.jtk.Parameters.__init__(self)
        # use eOmit as default to align with our legacy convertHidden's default value false
        # using eOmit as default will also give us faster conversion time since hidden elements are skipped
        self.layerFilterStyle = omni.converter.jtk.LayerFilterStyle.eOmit
        self.materialType = omni.converter.jtk.MaterialType.ePreviewSurface

        # update creator metadata to include extension and backend converter versions
        # to do: we also need to include the omni.kit.converter.cad bundle version
        # we're importing here to avoid circular imports because extension.py imports this class
        from .extension import get_instance

        creator = f"{get_instance().get_ext_name()} {get_instance().get_ext_version()} {self.creator}"
        self.creator = creator

    def parse(self, args: dict[str, str]):
        omni.converter.jtk.Parameters.__init__(self, args)
        self.sOptimizeConfig = args.get("sOptimizeConfig")
        self.bOptimize = args.get("bOptimize", "true") == "true"
        self.bConvertHidden = args.get("bConvertHidden", "false") == "true"

        self.convertCurves = (
            args.get("convertCurves", "false") == "true"
            if args.get("convertCurves") != None
            else args.get("bConvertCurves", "false") == "true"
        )

        self.bInstancing = args.get("bInstancing", "true") == "true"
        self.instancingStyle = (
            omni.converter.jtk.InstancingStyle.eInstanceableReference
            if self.bInstancing
            else omni.converter.jtk.InstancingStyle.eNone
        )

        self.iUpAxis = args.get("iUpAxis")
        self.dMetersPerUnit = args.get("dMetersPerUnit")
        if self.bConvertHidden:
            self.layerFilterStyle = omni.converter.jtk.LayerFilterStyle.eHide
        else:
            self.layerFilterStyle = omni.converter.jtk.LayerFilterStyle.eOmit

        self.flatten = args.get("flatten", "false") == "true"

        if args.get("fallbackTessParamAngular") != None:
            self.fallbackTessParamAngular = float(args.get("fallbackTessParamAngular"))

        if args.get("fallbackTessParamChordal") != None:
            self.fallbackTessParamChordal = float(args.get("fallbackTessParamChordal"))

        if args.get("fallbackTessParamLength") != None:
            self.fallbackTessParamLength = float(args.get("fallbackTessParamLength"))

        if args.get("fallbackTessParamMaxAspect") != None:
            self.fallbackTessParamMaxAspect = float(args.get("fallbackTessParamMaxAspect"))

        if args.get("fallbackTessParamMinAngle") != None:
            self.fallbackTessParamMinAngle = float(args.get("fallbackTessParamMinAngle"))

        if args.get("fallbackTessParamHoleRemovalFraction") != None:
            self.fallbackTessParamHoleRemovalFraction = float(args.get("fallbackTessParamHoleRemovalFraction"))

        if args.get("fallbackTessParamMinEdgeLength") != None:
            self.fallbackTessParamMinEdgeLength = float(args.get("fallbackTessParamMinEdgeLength"))

        if args.get("fallbackTessParamTrimSuppress") != None:
            self.fallbackTessParamTrimSuppress = args.get("fallbackTessParamTrimSuppress", "false") == "true"

        if args.get("overrideTessellationGeometry") != None:
            self.overrideTessellationGeometry = args.get("overrideTessellationGeometry", "false") == "true"

        if args.get("overrideTessellationParameters") != None:
            self.overrideTessellationParameters = args.get("overrideTessellationParameters", "false") == "true"

        self.progressLogging = args.get("progressLogging", "true") == "true"

        # maps UI material selection to material type
        if self.materialSelection == 0:
            self.materialType = omni.converter.jtk.MaterialType.eNone
        elif self.materialSelection == 1:
            self.materialType = omni.converter.jtk.MaterialType.ePreviewSurface
        elif self.materialSelection == 2:
            self.materialType = omni.converter.jtk.MaterialType.ePreviewSurface_OmniPBR

        # materialType passed from args should take precedence over materialSelection from UI above
        if args.get("materialType", "1") == str(int(omni.converter.jtk.MaterialType.eNone)):
            self.materialType = omni.converter.jtk.MaterialType.eNone
        if args.get("materialType", "1") == str(int(omni.converter.jtk.MaterialType.ePreviewSurface)):
            self.materialType = omni.converter.jtk.MaterialType.ePreviewSurface
        if args.get("materialType", "1") == str(int(omni.converter.jtk.MaterialType.ePreviewSurface_OmniPBR)):
            self.materialType = omni.converter.jtk.MaterialType.ePreviewSurface_OmniPBR

    def toArgs(self) -> dict[str, str]:
        """Return dict[str, str] using Parameters.toArgs() with updated values from self"""
        self.progressLogging = True
        args = super().toArgs()
        args["instancingStyle"] = (
            str(int(omni.converter.jtk.InstancingStyle.eInstanceableReference))
            if self.bInstancing
            else str(int(omni.converter.jtk.InstancingStyle.eNone))
        )
        args["sOptimizeConfig"] = str(self.sOptimizeConfig).lower()
        args["bOptimize"] = str(self.bOptimize).lower()
        args["bConvertHidden"] = str(self.bConvertHidden).lower()
        args["iUpAxis"] = str(self.iUpAxis).lower()
        args["dMetersPerUnit"] = str(self.dMetersPerUnit).lower()
        if args["bConvertHidden"] == "true":
            args["layerFilterStyle"] = str(int(omni.converter.jtk.LayerFilterStyle.eHide))
        else:
            args["layerFilterStyle"] = str(int(omni.converter.jtk.LayerFilterStyle.eOmit))

        # maps UI material selection to material type
        args["materialType"] = str(self.materialSelection)
        return args
