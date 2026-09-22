# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["ContainsMeshChecker"]

import omni.capabilities as cap
from omni.asset_validator.core import BaseRuleChecker, register_requirements
from pxr import Usd, UsdGeom


@register_requirements(cap.GeometryRequirements.VG_MESH_001)
class ContainsMeshChecker(BaseRuleChecker):
    """
    Validates that the stage contains at least one mesh.
    Warns if other geometry is also present.

    Implements VG_MESH_001
    """

    _MESH_NOT_FOUND_MESSAGE = "Stage does not contain any meshes."
    _OTHER_GEOMETRY_WARNING_MESSAGE = "Stage contains a mesh as required, but also other types of Gprims."

    def CheckStage(self, stage: Usd.Stage) -> None:

        def find_geometry_prims(stage: Usd.Stage) -> tuple[Usd.Prim | None, Usd.Prim | None]:
            """
            Traverses a USD stage to find at least one Mesh prim and one other
            type of geometry prim.

            Args:
                stage: The USD stage to traverse.

            Returns:
                A tuple containing the first found Mesh prim and the first found
                other geometry prim. Either can be None if not found.
            """
            mesh_prim = None
            other_geom_prim = None

            # Traverse all prims on the stage
            for prim in stage.Traverse():
                # If we haven't found a mesh yet, check if this prim is a mesh
                if not mesh_prim and prim.IsA(UsdGeom.Mesh):
                    mesh_prim = prim
                    continue  # Move to the next prim

                # If we haven't found other geometry yet, check if it's a Gprim
                # but specifically NOT a Mesh.
                if not other_geom_prim and prim.IsA(UsdGeom.Gprim) and not prim.IsA(UsdGeom.Mesh):
                    other_geom_prim = prim

                # Optimization: If we've found both, we can stop traversing
                if mesh_prim and other_geom_prim:
                    break

            return mesh_prim, other_geom_prim

        mesh_prim, other_geom_prim = find_geometry_prims(stage)

        if not mesh_prim:
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_MESH_001, message=self._MESH_NOT_FOUND_MESSAGE, at=stage
            )
        elif mesh_prim and other_geom_prim:
            self._AddWarning(
                requirement=cap.GeometryRequirements.VG_MESH_001,
                message=self._OTHER_GEOMETRY_WARNING_MESSAGE,
                at=other_geom_prim,
            )
