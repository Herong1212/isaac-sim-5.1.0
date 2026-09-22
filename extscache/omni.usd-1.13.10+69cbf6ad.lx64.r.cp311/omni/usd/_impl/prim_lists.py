# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.usd
from pxr import Usd, UsdGeom, UsdLux


def get_geometry_standard_prim_list(usd_context=None):
    """Gets a list of pre-defined geometry types.

    Args:
        usd_context (omni.usd.UsdContext, optional): UsdContext for those geometries to be defined. Defaults to None.

    Returns:
        list: A list of pre-defined geometry types.
    """

    if not usd_context:
        usd_context = omni.usd.get_context()

    stage = usd_context.get_stage()
    if stage:
        meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    else:
        meters_per_unit = 0.01

    geom_base = 0.5 / meters_per_unit
    geom_base_double = geom_base * 2
    geom_base_half = geom_base / 2

    all_shapes = sorted([
        (
            "Cube",
            {
                UsdGeom.Tokens.size: geom_base_double,
                UsdGeom.Tokens.extent: [(-geom_base, -geom_base, -geom_base), (geom_base, geom_base, geom_base)],
            },
        ),
        (
            "Sphere",
            {
                UsdGeom.Tokens.radius: geom_base,
                UsdGeom.Tokens.extent: [(-geom_base, -geom_base, -geom_base), (geom_base, geom_base, geom_base)],
            },
        ),
        (
            "Cylinder",
            {
                UsdGeom.Tokens.radius: geom_base,
                UsdGeom.Tokens.height: geom_base_double,
                UsdGeom.Tokens.extent: [(-geom_base, -geom_base, -geom_base), (geom_base, geom_base, geom_base)],
            },
        ),
        (
            "Capsule",
            {
                UsdGeom.Tokens.radius: geom_base_half,
                UsdGeom.Tokens.height: geom_base,
                # Create extent with command dynamically since it's different in different up-axis.
            },
        ),
        (
            "Cone",
            {
                UsdGeom.Tokens.radius: geom_base,
                UsdGeom.Tokens.height: geom_base_double,
                UsdGeom.Tokens.extent: [(-geom_base, -geom_base, -geom_base), (geom_base, geom_base, geom_base)],
            },
        ),
    ])

    shape_attrs = {}
    for name, attrs in all_shapes:
        shape_attrs[name] = attrs

    return shape_attrs


def get_light_prim_list(usd_context=None):
    """Gets a list of pre-defined light types.

    Args:
        usd_context (omni.usd.UsdContext, optional): UsdContext for those lights to be defined. Defaults to None.

    Returns:
        list: A list of pre-defined light types.
    """
    if not usd_context:
        usd_context = omni.usd.get_context()

    stage = usd_context.get_stage()
    if stage:
        meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    else:
        meters_per_unit = 0.01

    geom_base = 0.5 / meters_per_unit
    geom_base_double = geom_base * 2

    # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
    if hasattr(UsdLux.Tokens, 'inputsIntensity'):
        return sorted([
            ("Distant Light", "DistantLight", {UsdLux.Tokens.inputsAngle: 1.0, UsdLux.Tokens.inputsIntensity: 3000}),
            ("Sphere Light", "SphereLight", {UsdLux.Tokens.inputsRadius: geom_base, UsdLux.Tokens.inputsIntensity: 30000}),
            (
                "Rect Light",
                "RectLight",
                {
                    UsdLux.Tokens.inputsWidth: geom_base_double,
                    UsdLux.Tokens.inputsHeight: geom_base_double,
                    UsdLux.Tokens.inputsIntensity: 15000,
                },
            ),
            ("Disk Light", "DiskLight", {UsdLux.Tokens.inputsRadius: geom_base, UsdLux.Tokens.inputsIntensity: 60000}),
            (
                "Cylinder Light",
                "CylinderLight",
                {UsdLux.Tokens.inputsLength: geom_base_double, UsdLux.Tokens.inputsRadius: 5, UsdLux.Tokens.inputsIntensity: 30000},
            ),
            (
                "Dome Light",
                "DomeLight",
                {UsdLux.Tokens.inputsIntensity: 1000, UsdLux.Tokens.inputsTextureFormat: UsdLux.Tokens.latlong},
            ),
        ])

    return sorted([
        ("Distant Light", "DistantLight", {UsdLux.Tokens.angle: 1.0, UsdLux.Tokens.intensity: 3000}),
        ("Sphere Light", "SphereLight", {UsdLux.Tokens.radius: geom_base, UsdLux.Tokens.intensity: 30000}),
        (
            "Rect Light",
            "RectLight",
            {
                UsdLux.Tokens.width: geom_base_double,
                UsdLux.Tokens.height: geom_base_double,
                UsdLux.Tokens.intensity: 15000,
            },
        ),
        ("Disk Light", "DiskLight", {UsdLux.Tokens.radius: geom_base, UsdLux.Tokens.intensity: 60000}),
        (
            "Cylinder Light",
            "CylinderLight",
            {UsdLux.Tokens.length: geom_base_double, UsdLux.Tokens.radius: 5, UsdLux.Tokens.intensity: 30000},
        ),
        (
            "Dome Light",
            "DomeLight",
            {UsdLux.Tokens.intensity: 1000, UsdLux.Tokens.textureFormat: UsdLux.Tokens.latlong},
        ),
    ])
