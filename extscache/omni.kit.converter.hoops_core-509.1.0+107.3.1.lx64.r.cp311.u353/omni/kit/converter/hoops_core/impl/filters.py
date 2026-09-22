# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
from omni.kit.converter.common import ConverterFilterData

HOOPS_CORE_FILTER_DATA = [
    ConverterFilterData(
        "HOOPS Converter - CATIA V5",
        ["(.*\\.CATPart$)|(.*\\.CATProduct$)|(.*\\.CGR$)"],
        ["CATIA V5 Files (*.CATPart, *.CATProduct, *.CGR)"],
    ),
    ConverterFilterData("HOOPS Converter - IFC", ["(.*\\.ifc$)|(.*\\.ifczip$)"], ["IFC Files (*.ifc, *.ifczip)"]),
    ConverterFilterData("HOOPS Converter - NX", ["(.*\\.prt$)"], ["Siemens NX Files (*.prt)"]),
    ConverterFilterData(
        "HOOPS Converter - Parasolid",
        ["(.*\\.xmt$)|(.*\\.x_t$)|(.*\\.x_b$)|(.*\\.xmt_txt$)"],
        ["Parasolid Files (*.xmt, *.x_t, *.x_b, *.xmt_txt)"],
    ),
    ConverterFilterData(
        "HOOPS Converter - SolidWorks", ["(.*\\.sldprt$)|(.*\\.sldasm$)"], ["SolidWorks Files (*.sldprt, *.sldasm)"]
    ),
    ConverterFilterData("HOOPS Converter - STL", ["(.*\\.stl$)"], ["STL Files (*.stl)"]),
    ConverterFilterData(
        "HOOPS Converter - Autodesk Inventor", ["(.*\\.IPT$)|(.*\\.IAM$)"], ["Autodesk Inventor Files (*.IPT, *.IAM)"]
    ),
    ConverterFilterData("HOOPS Converter - CATIA V6 / 3DExperience", ["(.*\\.3DXML$)"], ["CATIA V6 Files (*.3DXML)"]),
    ConverterFilterData(
        "HOOPS Converter - AutoCAD 3D", ["(.*\\.DWG$)|(.*\\.DXF$)"], ["AutoCAD 3D Files (*.DWG, *.DXF)"]
    ),
    ConverterFilterData(
        "HOOPS Converter - Creo - Pro/E",
        ["(((.*\\.ASM)|(.*\\.PRT))(\\.[0-9]+)?)$"],
        ["Creo - Pro/E Files (*.ASM, *.PRT))"],
    ),
    ConverterFilterData("HOOPS Converter - Revit", ["(.*\\.RVT$)|(.*\\.RFA$)"], ["Revit Files (*.RVT, *.RFA)"]),
    ConverterFilterData(
        "HOOPS Converter - Solid Edge",
        ["(.*\\.ASM$)|(.*\\.PAR$)|(.*\\.PWD$)|(.*\\.PSM$)"],
        ["Solid Edge Files (*.ASM, *.PAR, *.PWD, *.PSM)"],
    ),
    ConverterFilterData(
        "HOOPS Converter - STEP",
        ["(.*\\.STEP$)|(.*\\.STP$)|(.*\\.IGES$)|(.*\\.IGS$)"],
        ["Step/Iges (*.STEP, *.STP, *.IGES, *.IGS)"],
    ),
    ConverterFilterData("HOOPS Converter - Rhino", ["(.*\\.3dm$)"], ["Rhino Files (*.3dm)"]),
    ConverterFilterData("HOOPS Converter - Collada", ["(.*\\.dae$)"], ["Collada Files (*.dae)"]),
    ConverterFilterData("HOOPS Converter - FBX", ["(.*\\.fbx$)"], ["FBX Files (*.fbx)"]),
    ConverterFilterData("HOOPS Converter - OBJ", ["(.*\\.obj$)"], ["OBJ Files (*.obj)"]),
    ConverterFilterData("HOOPS Converter - Autodesk 3DS", ["(.*\\.3ds$)"], ["3DS Files (*.3ds)"]),
    ConverterFilterData("HOOPS Converter - 3MF", ["(.*\\.3mf$)"], ["3MF Files (*.3mf)"]),
    ConverterFilterData("HOOPS Converter - GLTF", ["(.*\\.GLTF$)|(.*\\.GLB$)"], ["GLTF Files (*.GLTF, *.GLB)"]),
    ConverterFilterData("HOOPS Converter - ACIS", ["(.*\\.SAT$)|(.*\\.SAB$)"], ["ACIS Files (*.SAT, *.SAB)"]),
    ConverterFilterData("HOOPS Converter - JT", ["(.*\\.jt$)"], ["JT Files (*.jt)"]),
    ConverterFilterData("HOOPS Converter - DGN", ["(.*\\.DGN$)"], ["DGN Files (*.DGN)"]),
]
