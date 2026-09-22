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
from typing import Dict

import omni.converter.dgn

__all__ = ["OdaDgnOptions"]


@dataclass
class OdaDgnOptions(omni.converter.dgn.Parameters):
    """
    DGN Converter settings class
    """

    def __init__(self):
        omni.converter.dgn.Parameters.__init__(self)
        self.progressLogging = True
        self.levelIncludes = ["*"]

        self.materialSelection = int(omni.converter.dgn.MaterialType.ePreviewSurface)
        self.materialType = omni.converter.dgn.MaterialType.ePreviewSurface

        # legacy options before Hungarian notations removal
        self.bInstancing = True
        self.sOptimizeConfig = ""
        self.bOptimize = True
        self.bConvertHidden = False
        self.bMergeMeshes = True
        self.bConvertCurves = False
        self.iUpAxis = 0
        self.dMetersPerUnit = 0.0
        self.dSurfaceTolerance = 0.2

        # update creator metadata to include extension and backend converter versions
        # to do: we also need to include the omni.kit.converter.cad bundle version
        # we're importing here to avoid circular imports because extension.py imports this class
        from .extension import get_instance

        creator = f"{get_instance().get_ext_name()} {get_instance().get_ext_version()} {self.creator}"
        self.creator = creator

    def _map_legacy_options(self):
        """
        Legacy options are still used in omni.kit.converter.common's CadConverterOptionsBuilder.
        So we need to map them to the new parameters.
        """
        self.instancing = self.bInstancing
        self.convertHidden = self.bConvertHidden
        self.mergeMeshes = self.bMergeMeshes
        self.surfaceTolerance = self.dSurfaceTolerance
        self.convertCurves = self.bConvertCurves
        self.instancingStyle = (
            omni.converter.dgn.InstancingStyle.eScenegraphInstancing
            if self.instancing
            else omni.converter.dgn.InstancingStyle.eNone
        )

    def parse(self, args: dict[str, str]):
        super().parseArgs(args)
        self._map_legacy_options()
        self.sOptimizeConfig = args.get("sOptimizeConfig")
        self.bOptimize = args.get("bOptimize", "true") == "true"

        self.bInstancing = args.get("bInstancing", "true") == "true"
        self.instancing = (
            args.get("instancing", "true") == "true"
            if args.get("instancing") != None
            else args.get("bInstancing", "true") == "true"
        )

        self.instancingStyle = (
            omni.converter.dgn.InstancingStyle.eScenegraphInstancing
            if self.instancing
            else omni.converter.dgn.InstancingStyle.eNone
        )

        self.bConvertHidden = args.get("bConvertHidden", "false") == "true"
        self.convertHidden = (
            args.get("convertHidden", "false") == "true"
            if args.get("convertHidden") != None
            else args.get("bConvertHidden", "false") == "true"
        )

        self.bMergeMeshes = args.get("bMergeMeshes", "true") == "true"
        self.mergeMeshes = (
            args.get("mergeMeshes", "true") == "true"
            if args.get("mergeMeshes") != None
            else args.get("bMergeMeshes", "true") == "true"
        )

        self.bConvertCurves = args.get("bConvertCurves", "false") == "true"
        self.convertCurves = (
            args.get("convertCurves", "false") == "true"
            if args.get("convertCurves") != None
            else args.get("bConvertCurves", "false") == "true"
        )
        self.iUpAxis = args.get("iUpAxis")
        self.dMetersPerUnit = args.get("dMetersPerUnit")
        self.progressLogging = (
            args.get("progressLogging", "true") == "true"
            if args.get("progressLogging") != None
            else args.get("bProgressLogging", "true") == "true"
        )

        if args.get("dSurfaceTolerance") != None:
            self.dSurfaceTolerance = float(args.get("dSurfaceTolerance"))
        if args.get("surfaceTolerance") != None:
            self.surfaceTolerance = float(args.get("surfaceTolerance"))

        # maps UI material selection to material type
        if self.materialSelection == 0:
            self.materialType = omni.converter.dgn.MaterialType.eNone
        elif self.materialSelection == 1:
            self.materialType = omni.converter.dgn.MaterialType.ePreviewSurface
        elif self.materialSelection == 2:
            self.materialType = omni.converter.dgn.MaterialType.ePreviewSurface_OmniPBR

        # materialType passed from args should take precedence over materialSelection from UI above
        if args.get("materialType", "1") == str(int(omni.converter.dgn.MaterialType.eNone)):
            self.materialType = omni.converter.dgn.MaterialType.eNone
        if args.get("materialType", "1") == str(int(omni.converter.dgn.MaterialType.ePreviewSurface)):
            self.materialType = omni.converter.dgn.MaterialType.ePreviewSurface
        if args.get("materialType", "1") == str(int(omni.converter.dgn.MaterialType.ePreviewSurface_OmniPBR)):
            self.materialType = omni.converter.dgn.MaterialType.ePreviewSurface_OmniPBR

    def toArgs(self) -> dict[str:str]:
        self._map_legacy_options()
        args = super().toArgs()
        args["instancing"] = str(self.instancing).lower()
        args["bInstancing"] = str(self.bInstancing).lower()
        args["convertHidden"] = str(self.convertHidden).lower()
        args["bConvertHidden"] = str(self.bConvertHidden).lower()
        args["mergeMeshes"] = str(self.mergeMeshes).lower()
        args["bMergeMeshes"] = str(self.bMergeMeshes).lower()
        args["convertCurves"] = str(self.convertCurves).lower()
        args["bConvertCurves"] = str(self.bConvertCurves).lower()
        args["progressLogging"] = str(self.progressLogging).lower()
        args["surfaceTolerance"] = str(self.surfaceTolerance)
        args["dSurfaceTolerance"] = str(self.dSurfaceTolerance)

        # maps UI material selection to material type
        args["materialType"] = str(self.materialSelection)

        # scene optimizer properties
        args["sOptimizeConfig"] = str(self.sOptimizeConfig).lower()
        args["bOptimize"] = str(self.bOptimize).lower()
        args["iUpAxis"] = str(self.iUpAxis).lower()
        args["dMetersPerUnit"] = str(self.dMetersPerUnit).lower()

        return args
