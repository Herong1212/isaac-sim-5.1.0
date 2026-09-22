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

import omni.converter.hoops

__all__ = ["HoopsOptions"]


@dataclass
class HoopsOptions(omni.converter.hoops.Parameters):
    """
    Please defer to the hoopsExchangeCADConverterSpec base class for a list of all HoopsOptions converter settings
    """

    def __init__(self):
        """
        Initialize the Hoops Exchange Converter Parameters
        """
        omni.converter.hoops.Parameters.__init__(self)

        # legacy options before Hungarian notations removal
        self.bInstancing = True
        self.bConvertCurves = False
        self.sOptimizeConfig = ""
        self.bOptimize = True
        self.bConvertHidden = False
        self.bConvertMetadata = False
        self.iUpAxis = 0
        self.dMetersPerUnit = 0.0

        self.materialSelection = int(omni.converter.hoops.MaterialType.ePreviewSurface)
        self.materialType = omni.converter.hoops.MaterialType.ePreviewSurface

        # this flag is hardcoded to false due to a HOOPS SDK bug which generates invalid indices when the flag is enabled for some file formats
        # when the flag is true for some file format conversions. OMPE-33813
        self.accurateTessellation = False

        self.reportProgress = True

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
        self.convertMetadata = self.bConvertMetadata
        self.convertCurves = self.bConvertCurves

    def parse(self, args: dict[str, str]):
        self._map_legacy_options()
        super().parseArgs(args)

        self.bInstancing = args.get("bInstancing", "true") == "true"
        self.instancingStyle = (
            omni.converter.hoops.InstancingStyle.eInstanceableReference
            if self.bInstancing
            else omni.converter.hoops.InstancingStyle.eNone
        )

        self.instancing = (
            args.get("instancing", "true") == "true"
            if args.get("instancing") != None
            else args.get("bInstancing", "true") == "true"
        )

        self.bConvertHidden = args.get("bConvertHidden", "false") == "true"

        self.convertHidden = (
            args.get("convertHidden", "false") == "true"
            if args.get("convertHidden") != None
            else args.get("bConvertHidden", "false") == "true"
        )

        self.bConvertMetadata = args.get("bConvertMetadata", "false") == "true"

        self.convertMetadata = (
            args.get("convertMetadata", "false") == "true"
            if args.get("convertMetadata") != None
            else args.get("bConvertMetadata", "false") == "true"
        )

        self.reportProgress = (
            args.get("reportProgress", "true") == "true"
            if args.get("reportProgress") != None
            else args.get("bReportProgress", "true") == "true"
        )

        self.bConvertCurves = args.get("bConvertCurves", "false") == "true"

        self.convertCurves = (
            args.get("convertCurves", "false") == "true"
            if args.get("convertCurves") != None
            else args.get("bConvertCurves", "false") == "true"
        )

        self.sOptimizeConfig = args.get("sOptimizeConfig")
        self.bOptimize = args.get("bOptimize", "true") == "true"
        self.iUpAxis = args.get("iUpAxis")
        self.dMetersPerUnit = args.get("dMetersPerUnit")
        self.accurateTessellation = False

        # maps UI material selection to material type
        if self.materialSelection == 0:
            self.materialType = omni.converter.hoops.MaterialType.eNone
        elif self.materialSelection == 1:
            self.materialType = omni.converter.hoops.MaterialType.ePreviewSurface
        elif self.materialSelection == 2:
            self.materialType = omni.converter.hoops.MaterialType.ePreviewSurface_OmniPBR
        self.materialSelection = int(self.materialType)

        # materialType passed from args should take precedence over materialSelection from UI above
        if args.get("materialType", "1") == str(int(omni.converter.hoops.MaterialType.eNone)):
            self.materialType = omni.converter.hoops.MaterialType.eNone
        if args.get("materialType", "1") == str(int(omni.converter.hoops.MaterialType.ePreviewSurface)):
            self.materialType = omni.converter.hoops.MaterialType.ePreviewSurface
        if args.get("materialType", "1") == str(int(omni.converter.hoops.MaterialType.ePreviewSurface_OmniPBR)):
            self.materialType = omni.converter.hoops.MaterialType.ePreviewSurface_OmniPBR

    def toArgs(self) -> dict[str:str]:
        self._map_legacy_options()
        args = super().toArgs()
        args["instancingStyle"] = (
            str(int(omni.converter.hoops.InstancingStyle.eInstanceableReference))
            if self.bInstancing
            else str(int(omni.converter.hoops.InstancingStyle.eNone))
        )
        args["reportProgress"] = str(self.reportProgress).lower()
        args["bConvertCurves"] = str(self.bConvertCurves).lower()
        args["bConvertMetadata"] = str(self.bConvertMetadata).lower()
        args["bConvertHidden"] = str(self.bConvertHidden).lower()
        args["bInstancing"] = str(self.bInstancing).lower()
        args["accurateTessellation"] = "false"

        # maps UI material selection to material type
        args["materialType"] = str(self.materialSelection)

        # scene optimizer properties
        args["sOptimizeConfig"] = str(self.sOptimizeConfig).lower()
        args["bOptimize"] = str(self.bOptimize).lower()
        args["iUpAxis"] = str(self.iUpAxis).lower()
        args["dMetersPerUnit"] = str(self.dMetersPerUnit).lower()

        return args
