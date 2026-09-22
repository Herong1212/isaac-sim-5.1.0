# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["MeasurePayload"]

from typing import List, Optional
from uuid import uuid4

from pxr import Gf, Usd, Sdf
import omni.usd as ou

from ..common import (
    MeasureMode,
    UnitType,
    DisplayAxisSpace,
    Precision,
    LabelSize
)

class MeasurePayload:
    def __init__(self):
        # Core
        self.uuid: int = int(str(uuid4().int)[:8])
        # Metadata
        self.prim = None
        self.prim_paths: List[str] = []
        self.points: List[Gf.Vec3d] = []
        self.tool_mode: MeasureMode = MeasureMode.NONE
        self.tool_sub_mode: int = -1
        # Compute Data
        self.computed_points: List[Gf.Vec3d] = []
        self.primary_value: float = 0.0
        self.secondary_values: List[float] = []
        # User Properties
        self.name: str = ""
        self.visible: bool = True
        self.axis_display: DisplayAxisSpace = DisplayAxisSpace.NONE
        self.unit_type: UnitType = UnitType.CENTIMETERS
        self.precision: Precision = Precision.HUNDRETH
        self.label_size: LabelSize = LabelSize.MEDIUM
        self.label_color: Gf.Vec4f = Gf.Vec4f(0.0, 1.0, 1.0, 1.0)

    def __repr__(self) -> str:
        payload = {
            "uuid": self.uuid,
            "prim_paths": self.prim_paths,
            "points": self.points,
            "tool_mode": self.tool_mode,
            "tool_sub_mode": self.tool_sub_mode,
            "computed_points": self.computed_points,
            "primary_value": self.primary_value,
            "secondary_values": self.secondary_values,
            "name": self.name,
            "visible": self.visible,
            "axis_display": self.axis_display,
            "unit_type": self.unit_type,
            "precision": self.precision,
            "label_size": self.label_size,
            "label_color": self.label_color
        }
        return str(payload)

    def update_from_compute(self, data) -> None:
        self.computed_points = data.points
        self.primary_value = data.primary
        self.secondary_values = data.secondary

    @staticmethod
    def from_prim(prim: "Usd.Prim") -> Optional["MeasurePayload"]:
        if prim and prim.HasAttribute("measure:uuid"):
            payload: "MeasurePayload" = MeasurePayload()
            # Core
            payload.prim = prim
            payload.uuid = prim.GetAttribute("measure:uuid").Get()
            # Metadata
            payload.prim_paths = MeasurePayload.read_prim_paths(prim)

            if not prim.HasAttribute('measure:meta:local_points') and prim.HasAttribute('measure:meta:points'):
                world_points = prim.GetAttribute("measure:meta:points").Get()
                payload.points = MeasurePayload.world_to_local_points(world_points, payload.prim_paths)
            else:
                payload.points = prim.GetAttribute("measure:meta:local_points").Get()

            payload.tool_mode = MeasureMode(prim.GetAttribute("measure:meta:tool_mode").Get())
            payload.tool_sub_mode = prim.GetAttribute("measure:meta:tool_sub_mode").Get()
            # Compute Data
            payload.computed_points = prim.GetAttribute("measure:compute:points").Get()
            payload.primary_value = prim.GetAttribute("measure:compute:primary").Get()
            payload.secondary_values = prim.GetAttribute("measure:compute:secondary").Get()
            # User properties
            payload.name = prim.GetAttribute("measure:prop:name").Get()
            payload.visible = prim.GetAttribute("measure:prop:visible").Get()
            payload.axis_display = DisplayAxisSpace[prim.GetAttribute("measure:prop:axis_display").Get()]
            payload.unit_type = UnitType[prim.GetAttribute("measure:prop:unit").Get()]
            payload.precision = Precision[prim.GetAttribute("measure:prop:precision").Get()]
            payload.label_size = LabelSize[prim.GetAttribute("measure:prop:label_size").Get()]
            payload.label_color = prim.GetAttribute("measure:prop:label_color").Get()

            return payload

        return None

    @staticmethod
    def read_prim_paths(prim: Usd.Prim):
        if prim.HasAttribute("measure:meta:prim_paths"):
            MeasurePayload.convert_attribute_to_relationship(prim, "measure:meta:prim_paths")

        unique_paths = prim.GetRelationship("measure:meta:prim_paths").GetTargets()
        indices = prim.GetAttribute("measure:meta:prim_path_indieces").Get()

        return [unique_paths[index] for index in indices]

    @staticmethod
    def write_prim_paths(prim: Usd.Prim, prim_paths: List[Sdf.Path]):
        indexing_attr = prim.GetAttribute("measure:meta:prim_path_indieces")
        if not indexing_attr:
            indexing_attr = prim.CreateAttribute("measure:meta:prim_path_indieces", typeName=Sdf.ValueTypeNames.IntArray)

        relationship = prim.GetRelationship("measure:meta:prim_paths")
        if not relationship:
            relationship = prim.CreateRelationship("measure:meta:prim_paths", True)

        unique_paths = []
        for path in prim_paths:
            if not path in unique_paths:
                unique_paths.append(path)

        indices = [unique_paths.index(path) for path in prim_paths]

        if relationship.GetTargets() != unique_paths or indexing_attr.Get() != indices:
            relationship.SetTargets(unique_paths)
            indexing_attr.Set(indices)

    @staticmethod
    def convert_attribute_to_relationship(prim: Usd.Prim, attr_name: str):
        prim_paths = [Sdf.Path(path) for path in prim.GetAttribute(attr_name).Get()]
        prim.RemoveProperty(attr_name)
        MeasurePayload.write_prim_paths(prim, prim_paths)

    @staticmethod
    def world_to_local_points(points: List[Gf.Vec3d], paths: List[str]):
        local_points = []
        stage = ou.get_context().get_stage()
        for point, path in zip(points, paths):
            prim = stage.GetPrimAtPath(path)
            wtm = ou.get_world_transform_matrix(prim)
            local_points.append(wtm.GetInverse().Transform(point))
        return local_points
