# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""
NOTE: This is duplicated from Content Pipeline repo. We need to update the source if any changes are made here.
https://gitlab-master.nvidia.com/omniverse/content-pipeline/-/blob/main/source/extensions/omni.cip/omni/cip/common/vehicle_utils.py


Module containing utilities used for interfacing with SimReady vehicle assets.
"""
from collections import namedtuple
from enum import Enum, auto
from functools import cache
from typing import Any, Literal

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

DEFAULT_TIME = Usd.TimeCode.EarliestTime()

SimReadyAttrDesc = namedtuple("SimReadyAttrDesc", ["name", "types", "time_varying", "allowed_values"])


class SIMREADY:
    SIMREADY_PREFIX = "omni:simready:"

    # SimReady semantics
    SEMANTICS_WIKIDATA_LEGACY_ATTR_NAME = "semantic:wikidata_qcode:params:semanticData"
    SEMANTICS_WIKIDATA_NEW_ATTR_NAME = "semantics:labels:wikidata_qcode"

    # SimReady XODR
    XODR_PATH_ATTR_NAME = SIMREADY_PREFIX + "openDrive"
    XODR_JUNCTION_ID_ATTR_NAME = SIMREADY_PREFIX + "junctionID"
    XODR_CONTROL_ID_ATTR_NAME = SIMREADY_PREFIX + "controlID"
    XODR_SIGNAL_ID_ATTR_NAME = SIMREADY_PREFIX + "signalID"

    # SimReady lights
    LIGHT_ATTR_NAME = SIMREADY_PREFIX + "light"
    LIGHT_BEHAVIOR_ATTR_NAME = SIMREADY_PREFIX + "behaviors"
    SIGNAL_NAME_ATTR_NAME = SIMREADY_PREFIX + "signal"
    SIGNAL_ORDER_ATTR_NAME = SIMREADY_PREFIX + "signalOrder"
    SIGNAL_TYPE_ATTR_NAME = SIMREADY_PREFIX + "signalType"
    SIGNAL_INTENSITY_ATTR_NAME = SIGNAL_NAME_ATTR_NAME + ":intensityDomain"
    LIGHT_INTENSITY_ATTR_NAME = LIGHT_ATTR_NAME + ":intensityDomain"
    LIGHT_COLOR_ATTR_NAME = LIGHT_ATTR_NAME + ":color"
    LIGHT_DURATION_ATTR_NAME = LIGHT_ATTR_NAME + ":duration"

    # SimReady nonvisual attributes
    NONVISUAL_BASE_ATTR_NAME = SIMREADY_PREFIX + "nonvisual:base"
    NONVISUAL_COATING_ATTR_NAME = SIMREADY_PREFIX + "nonvisual:coating"
    NONVISUAL_ATTRIBUTES_ATTR_NAME = SIMREADY_PREFIX + "nonvisual:attributes"

    # SimReady vehicle attributes
    VEHICLE_ATTR_NAME = SIMREADY_PREFIX + "vehicle"
    VEHICLE_PIVOT_ATTR_NAME = VEHICLE_ATTR_NAME + ":pivot"
    VEHICLE_PARENT_ATTR_NAME = VEHICLE_ATTR_NAME + ":parent"
    VEHICLE_GROUP_ATTR_NAME = VEHICLE_ATTR_NAME + ":group"
    VEHICLE_SUBGROUP_ATTR_NAME = VEHICLE_ATTR_NAME + ":subgroup"
    VEHICLE_AXIS_ATTR_NAME = VEHICLE_ATTR_NAME + ":longitudinalAxis"
    VEHICLE_DRIVE_ATTR_NAME = VEHICLE_ATTR_NAME + ":drivetrain"
    VEHICLE_STEER_ATTR_NAME = VEHICLE_ATTR_NAME + ":steering"

    # SimReady task attributes
    TASKS_ATTR_NAME = SIMREADY_PREFIX + "tasks"
    TASKS_EFFECTOR_ATTR_NAME = TASKS_ATTR_NAME + ":effector"
    TASKS_GROUP_ATTR_NAME = TASKS_ATTR_NAME + ":group"

    # Vehicle attribute descriptions
    LIGHT_INTENSITY_ATTR_DESC = SimReadyAttrDesc(
        name=LIGHT_INTENSITY_ATTR_NAME,
        types=[Sdf.ValueTypeNames.Float2, Sdf.ValueTypeNames.Double2],
        time_varying=False,
        allowed_values=[],
    )
    LIGHT_COLOR_ATTR_DESC = SimReadyAttrDesc(
        name=LIGHT_COLOR_ATTR_NAME,
        types=[Sdf.ValueTypeNames.Color3f, Sdf.ValueTypeNames.Color3d],
        time_varying=False,
        allowed_values=[],
    )
    LIGHT_DURATION_ATTR_DESC = SimReadyAttrDesc(
        name=LIGHT_DURATION_ATTR_NAME,
        types=[Sdf.ValueTypeNames.Float],
        time_varying=False,
        allowed_values=[],
    )

    @classmethod
    def get_vehicle_attribute_descriptions(cls) -> list[SimReadyAttrDesc]:
        """Returns a list of SimReady vehicle attribute descriptions to ease batch processing
        of these attributes.
        """
        return [
            SimReadyAttrDesc(
                name=cls.LIGHT_ATTR_NAME, types=[Sdf.ValueTypeNames.TokenArray], time_varying=False, allowed_values=[]
            ),
            cls.LIGHT_INTENSITY_ATTR_DESC,
            cls.LIGHT_COLOR_ATTR_DESC,
            cls.LIGHT_DURATION_ATTR_DESC,
            SimReadyAttrDesc(
                name=cls.VEHICLE_ATTR_NAME, types=[Sdf.ValueTypeNames.Token], time_varying=False, allowed_values=[]
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_PIVOT_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=[],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_PARENT_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=[],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_GROUP_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=[],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_SUBGROUP_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=[],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_AXIS_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=["negX", "negY", "negZ", "posX", "posY", "posZ"],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_DRIVE_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=["4WD", "AWD", "FWD", "RWD"],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_PARENT_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=[],
            ),
            SimReadyAttrDesc(
                name=cls.VEHICLE_STEER_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                # Note that 'tank' is synonymous with 'none'.
                # This is handled through the dictionary mapping in SteerMethod.steering_map().
                allowed_values=["front", "back", "all", "none"],
            ),
            SimReadyAttrDesc(
                name=cls.TASKS_ATTR_NAME, types=[Sdf.ValueTypeNames.TokenArray], time_varying=False, allowed_values=[]
            ),
            SimReadyAttrDesc(
                name=cls.TASKS_EFFECTOR_ATTR_NAME,
                types=[Sdf.ValueTypeNames.Token],
                time_varying=False,
                allowed_values=["leftHand", "rightHand", "leftFoot", "rightFoot", "pelvis"],
            ),
            SimReadyAttrDesc(
                name=cls.TASKS_GROUP_ATTR_NAME, types=[Sdf.ValueTypeNames.String], time_varying=False, allowed_values=[]
            ),
        ]

    @classmethod
    def get_vehicle_light_attribute_descriptions(cls, light_group_name: str) -> list[SimReadyAttrDesc]:
        """Returns a list of SimReady vehicle attribute descriptions to ease batch processing
        of these attributes.
        """
        return [
            SimReadyAttrDesc(
                name=f"{cls.LIGHT_INTENSITY_ATTR_DESC.name}:{light_group_name}",
                types=cls.LIGHT_INTENSITY_ATTR_DESC.types,
                time_varying=cls.LIGHT_INTENSITY_ATTR_DESC.time_varying,
                allowed_values=cls.LIGHT_INTENSITY_ATTR_DESC.allowed_values,
            ),
            SimReadyAttrDesc(
                name=f"{cls.LIGHT_COLOR_ATTR_DESC.name}:{light_group_name}",
                types=cls.LIGHT_COLOR_ATTR_DESC.types,
                time_varying=cls.LIGHT_COLOR_ATTR_DESC.time_varying,
                allowed_values=cls.LIGHT_COLOR_ATTR_DESC.allowed_values,
            ),
            SimReadyAttrDesc(
                name=f"{cls.LIGHT_DURATION_ATTR_DESC.name}:{light_group_name}",
                types=cls.LIGHT_DURATION_ATTR_DESC.types,
                time_varying=cls.LIGHT_DURATION_ATTR_DESC.time_varying,
                allowed_values=cls.LIGHT_DURATION_ATTR_DESC.allowed_values,
            ),
        ]


class DriveMethod(Enum):
    """Methods of driving"""

    AWD = auto()
    FWD = auto()
    RWD = auto()

    @classmethod
    @cache
    def drive_map(cls):
        """Returns mapping of drive method strings to DriveMethod enum values."""
        return {
            "4wd": cls.AWD,
            "awd": cls.AWD,
            "fwd": cls.FWD,
            "rwd": cls.RWD,
        }


class SteerMethod(Enum):
    """Methods of steering"""

    FRONT = auto()
    REAR = auto()
    ALL = auto()
    NONE = auto()

    @classmethod
    @cache
    def steering_map(cls):
        """Returns mapping of steering method strings to SteerMethod enum values."""
        return {
            "front": cls.FRONT,
            "back": cls.REAR,
            "rear": cls.REAR,
            "all": cls.ALL,
            "none": cls.NONE,
            "tank": cls.NONE,  # 'tank' is synonymous with 'none'
        }


class SortMethod(Enum):
    """Methods of sorting components"""

    TRANSFORM = auto()
    CENTROID = auto()
    VOLUME = auto()
    LENGTH = auto()
    WIDTH = auto()
    HEIGHT = auto()
    PATH = auto()


class TagType(Enum):
    """Type of tagging in an vehicle"""

    SIMREADY = "simready"
    SEMANTIC = "semantic"


class CollectionMethod(Enum):
    """Method of collecting a component prim"""

    COLLECTION = auto()
    HIERARCHY = auto()
    PRIM = auto()
    LIGHT = auto()
    TASK = auto()


class VehicleType(Enum):
    """Type of vehicle"""

    VEHICLE = "vehicle"
    CAR = "car"
    TRUCK = "truck"
    EMERGENCY = "emergency vehicle"
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    SCOOTER = "scooter"
    SUV = "suv"
    BUS = "bus"


class VehicleLightType(Enum):
    """Type of vehicle light"""

    BRAKE = "brakeLights"
    EMERGENCY = "emergencyLights"
    FOG = "fogLights"
    HEAD = "headLights"
    HIGHBEAM = "highbeamLights"
    MARKER = "markerLights"
    NIGHT = "nightLights"
    PARKING = "parkingLights"
    PLATE = "plateLights"
    REVERSE = "reverseLights"
    RUNNING = "runningLights"
    SIGNAL = "signalLights"
    TAIL = "tailLights"


class VehicleUtils:

    WIKIDATA_TO_TYPE_MAP = {
        # vehicle
        "Q42889": "vehicle",
        "Q1420": "car",
        "Q43193": "truck",
        "Q1308737": "emergency vehicle",
        "Q11442": "bicycle",
        "Q34493": "motorcycle",
        "Q193234": "scooter",
        "Q5638": "bus",
        # body
        "Q731988": "body",
        # parts
        "Q60998096": "interior",
        "Q1276284": "door",
        "Q1142905": "trunk",
        "Q27206": "hood",
        "Q679300": "steering",
        "Q22706": "plate",
        "Q506095": "window",
        # wheel
        "Q446": "wheel",
        "Q1534839": "brake",
        # bicycle
        "Q1148375": "handlebars",
        "Q651103": "fork",
        "Q49717": "pedals",
        "Q305026": "pedal",
        # motorcycle
        "Q11885128": "handlebars",
        "Q377709": "fork",
        # suspension
        "Q272870": "suspension",
        "Q211251": "shock",
        "Q102836": "spring",
        "Q2039332": "strut",
        # lights
        "Q908406": "brakeLights",
        "Q1506699": "emergencyLights",
        "Q1751920": "fogLights",
        "Q869713": "headLights",
        "Q376517": "highbeamLights",
        "Q1426855": "runningLights",
        "Q1464545": "signalLights",
        "Q501192": "tailLights",
        "Q19978641": "reverseLights",
    }
    BASE_TYPE_MAP = {
        "vehicle": "body",
        "car": "body",
        "truck": "body",
        "emergency vehicle": "body",
        "bicycle": "body",
        "motorcycle": "body",
        "scooter": "body",
        "suv": "body",
        "bus": "body",
        "brakeLights": "light",
        "emergencyLights": "light",
        "fogLights": "light",
        "headLights": "light",
        "highbeamLights": "light",
        "markerLights": "light",
        "nightLights": "light",
        "parkingLights": "light",
        "plateLights": "light",
        "reverseLights": "light",
        "runningLights": "light",
        "signalLights": "light",
        "tailLights": "light",
        "trunk": "door",
        "hood": "door",
        "boot": "door",
        "bonnet": "door",
        "shock": "suspension",
        "strut": "suspension",
        "spring": "suspension",
        "arm": "suspension",
        "rod": "suspension",
        "bar": "suspension",
        "lower": "suspension",
        "lowerSuspension": "suspension",
        "lowerShock": "suspension",
        "lowerStrut": "suspension",
        "lowerArm": "suspension",
        "lowerRod": "suspension",
        "lowerBar": "suspension",
    }

    @classmethod
    def get_types_from_wikidata(cls, prim: Usd.Prim) -> list[str]:
        """Returns a list of vehicle semantic labels found on the prim"""
        types = []
        if (qcodes := prim.GetAttribute(SIMREADY.SEMANTICS_WIKIDATA_NEW_ATTR_NAME).Get()) is not None:
            for qcode in qcodes:
                if qcode in cls.WIKIDATA_TO_TYPE_MAP:
                    types.append(cls.WIKIDATA_TO_TYPE_MAP[qcode])
        elif (qcode := prim.GetAttribute(SIMREADY.SEMANTICS_WIKIDATA_LEGACY_ATTR_NAME).Get()) is not None:
            if qcode in cls.WIKIDATA_TO_TYPE_MAP:
                types.append(cls.WIKIDATA_TO_TYPE_MAP[qcode])
        return types

    @classmethod
    def get_light_types_from_wikidata(cls, prim: Usd.Prim) -> list[str]:
        """Returns light types from vehicle semantic labels found on the prim"""
        vehicle_light_types = [t.value for t in list(VehicleLightType)]
        return [t for t in cls.get_types_from_wikidata(prim) if t in vehicle_light_types]

    @classmethod
    def get_inherited_wikidata_types(cls, prim: Usd.Prim) -> list[str]:
        """Returns a list of vehicle semantic labels found on the prim or closest
        ancestors."""
        stage = prim.GetStage()
        types = []
        ancestors = prim.GetPath().GetAncestorsRange()
        for ancestor in ancestors:
            ancestor_prim = stage.GetPrimAtPath(ancestor)
            types.extend(cls.get_types_from_wikidata(ancestor_prim))
        return list(set(types))

    @classmethod
    def has_simready_tag(cls, prim: Usd.Prim) -> bool:
        """Returns True if prim has any valid SimReady tags"""
        tags = [
            SIMREADY.VEHICLE_ATTR_NAME,
            SIMREADY.LIGHT_ATTR_NAME,
            SIMREADY.TASKS_ATTR_NAME,
        ]
        return any([prim.HasProperty(t) for t in tags])

    @classmethod
    def is_ignored(cls, prim: Usd.Prim) -> bool:
        """Returns True if prim is an ignored type"""
        return (
            prim.IsA(UsdShade.Material) or prim.IsA(UsdShade.Shader) or prim.IsA(UsdGeom.Subset) or not prim.IsActive()
        )

    @classmethod
    def is_group(cls, prim: Usd.Prim) -> bool:
        """Returns True if prim is a scope or xform"""
        return prim.IsA(UsdGeom.Scope) or prim.IsA(UsdGeom.Xform)

    @classmethod
    def get_collections(cls, prim: Usd.Prim) -> list[str]:
        """Returns a list of CollectionAPI schemas"""
        all_schemas = prim.GetAppliedSchemas()
        coll_schemas = [s for s in all_schemas if s.startswith("CollectionAPI")]
        return coll_schemas

    @classmethod
    def is_collection(cls, prim: Usd.Prim) -> bool:
        """Returns True if prim is tagged and has collection schemas"""
        collection_tags = [SIMREADY.VEHICLE_ATTR_NAME, SIMREADY.LIGHT_ATTR_NAME]
        return cls.get_collections(prim) and cls.is_group(prim) and any([prim.HasProperty(t) for t in collection_tags])

    @classmethod
    def get_simready_tag(cls, prim: Usd.Prim, tag: str, prop_type=Sdf.ValueTypeNames.Token, fallback=None) -> Any:
        """Returns the value of the requested tag from the prim, if it exists.  Returns none if type is incorrect."""
        if (
            prim
            and prim.HasProperty(tag)
            and prim.GetAttribute(tag).GetTypeName() == prop_type
            and (value := prim.GetAttribute(tag).Get())
        ):
            return value
        return fallback

    @classmethod
    def get_vec_from_axis(
        cls, axis: Literal["posX", "posY", "posZ", "negX", "negY", "negZ"], fallback: Gf.Vec3d | None = None
    ) -> Gf.Vec3d:
        """Returns a GfVec3d axis from a token [posX, posY, posZ, negX, negY, negZ]."""
        axis_tokens = {
            "posX": Gf.Vec3d.XAxis(),
            "negX": -Gf.Vec3d.XAxis(),
            "posY": Gf.Vec3d.YAxis(),
            "negY": -Gf.Vec3d.YAxis(),
            "posZ": Gf.Vec3d.ZAxis(),
            "negZ": -Gf.Vec3d.ZAxis(),
        }
        return axis_tokens.get(axis, fallback)

    @classmethod
    def get_index_and_sign_from_axis(
        cls,
        axis: Literal["posX", "posY", "posZ", "negX", "negY", "negZ"],
        fallback_index: int | None = None,
        fallback_sign: int | None = None,
    ) -> tuple[int, int]:
        """Returns a tuple with the index and sign from a token [posX, posY, posZ, negX, negY, negZ]."""
        axis_tokens = {
            "posX": (0, 1),
            "negX": (0, -1),
            "posY": (1, 1),
            "negY": (1, -1),
            "posZ": (2, 1),
            "negZ": (2, -1),
        }
        return axis_tokens.get(axis, (fallback_index, fallback_sign))

    @classmethod
    def get_tagged_type(cls, prim: Usd.Prim, tag_type: TagType | None = None) -> tuple[str, str]:
        """Returns the base type and the sub type of a prim tagged with a tag type."""
        sub_type = None
        base_type = None
        if tag_type == TagType.SIMREADY:
            if tag := cls.get_simready_tag(prim, SIMREADY.VEHICLE_ATTR_NAME):
                sub_type = tag
                base_type = cls.BASE_TYPE_MAP.get(sub_type, sub_type)
            elif cls.get_simready_tag(prim, SIMREADY.LIGHT_ATTR_NAME, Sdf.ValueTypeNames.TokenArray):
                sub_type = "light"
                base_type = cls.BASE_TYPE_MAP.get(sub_type, sub_type)
            elif prim.IsA(UsdGeom.Xform) and cls.get_simready_tag(
                prim, SIMREADY.TASKS_ATTR_NAME, Sdf.ValueTypeNames.TokenArray
            ):
                base_type = sub_type = "task"
        elif tag_type == TagType.SEMANTIC:
            if wikidata_tags := cls.get_types_from_wikidata(prim):
                sub_type = wikidata_tags[0]
                base_type = cls.BASE_TYPE_MAP.get(sub_type, sub_type)

        return (base_type, sub_type)

    @classmethod
    def compute_world_bound(cls, prim: Usd.Prim) -> Gf.BBox3d:
        """Computes the world bounding box from the points attribute of a
        mesh, the center of a transform or falls back to the cached bound."""
        bbox_cache = UsdGeom.BBoxCache(DEFAULT_TIME, includedPurposes=[UsdGeom.Tokens.default_])
        bound = bbox_cache.ComputeWorldBound(prim)
        # Force bounding box into world space
        bbox_range = bound.ComputeAlignedBox()
        if bound.GetRange() == Gf.Range3d():
            if prim.IsA(UsdGeom.PointBased):
                bbox_range = Gf.Range3d()
                max_extents = bbox_range.GetMax()
                min_extents = bbox_range.GetMin()

                mesh = UsdGeom.Mesh(prim)
                mtx = mesh.ComputeLocalToWorldTransform(DEFAULT_TIME)
                pts = mesh.GetPointsAttr().Get()
                for pt in pts:
                    world_pt = mtx.Transform(pt)
                    for i in range(3):
                        if world_pt[i] <= min_extents[i]:
                            min_extents[i] = world_pt[i]
                        if world_pt[i] >= max_extents[i]:
                            max_extents[i] = world_pt[i]
                bbox_range.SetMin(min_extents)
                bbox_range.SetMax(max_extents)
            else:
                stage_scale = UsdGeom.GetStageMetersPerUnit(prim.GetStage())
                offset = Gf.Vec3d(stage_scale * 1e-3)
                xform = UsdGeom.Xformable(prim)
                transform = xform.ComputeLocalToWorldTransform(DEFAULT_TIME)
                center = transform.ExtractTranslation()
                bbox_range = Gf.Range3d(center - offset, center + offset)

        bound = Gf.BBox3d(bbox_range)
        return bound


class VehicleComponent:
    """A vehicle component representing a group of geometry with data.

    Inputs
        component_type: The component type. (ex. body, wheels)

    Attributes:
        type: The component type. (ex. body, wheels)
        subtype: A more specific type. (ex. spring)
        prim: The prim that created the component, if any.
        path: The concise relative path of the component.
        parent: The concise relative path of the hierarchical parent.
        transform: The world space transform.
        bound: The world space bounding box.
        data: The SimReady data stored on the component.
        subgroups: A list of subgroups that prims are added to.
        collections: A dictionary of prims arranged by subgroups.
    """

    def __init__(self, component_type: str, subtype: str | None = None):
        self.type = component_type
        self.subtype = subtype if subtype else component_type
        self.prim: Usd.Prim | None = None
        self.path: str | None = None
        self.parent: str | None = None
        self.transform: Gf.Matrix4d | None = None
        self.bound = Gf.BBox3d()
        self.data = {}
        self.collections: dict[str, list[Usd.Prim]] = {}

    @property
    def subgroups(self):
        return list(self.collections.keys())

    def _update_bound(self):
        """Updates the bounding box from the collection."""
        self.bound = Gf.BBox3d()
        for prims in self.collections.values():
            for prim in prims:
                bound = VehicleUtils.compute_world_bound(prim)
                self.bound = Gf.BBox3d.Combine(self.bound, bound)

    def get_semantic_tags(self, subgroup: str | None = None) -> list[str]:
        """Returns all semantic tags found on the component prims or on the
        prims in the specified subgroup."""
        if not subgroup:
            subgroups = self.subgroups
        elif subgroup not in self.collections:
            return []
        else:
            subgroups = [subgroup]

        all_tags = set()
        if self.prim:
            all_tags.update(VehicleUtils.get_inherited_wikidata_types(self.prim))
        for subgroup_name in subgroups:
            for prim in self.collections.get(subgroup_name, []):
                semantic_types = VehicleUtils.get_inherited_wikidata_types(prim)
                all_tags.update(semantic_types)
        return list(all_tags)

    def get_prims(self, subgroup: str | None = None) -> list[Usd.Prim]:
        """Returns all unique prims in the specified subgroup or in the component."""
        if not subgroup:
            subgroups = self.subgroups
        elif subgroup not in self.collections:
            return []
        else:
            subgroups = [subgroup]

        prims = set()
        for subgroup_name in subgroups:
            prims.update(self.collections.get(subgroup_name, []))
        return list(prims)

    def add_prim(self, prim: Usd.Prim, subgroup: str):
        """Adds a prim to a subgroup and updates the bound."""
        if subgroup not in self.collections:
            self.collections[subgroup] = []
        if prim not in self.collections[subgroup]:
            self.collections[subgroup].append(prim)
            self._update_bound()

    def add_prims(self, prims: list[Usd.Prim], subgroup: str):
        """Adds a prim to a subgroup and updates the bound."""
        if subgroup not in self.collections:
            self.collections[subgroup] = []
        add_prims = [p for p in prims if p not in self.collections[subgroup]]
        self.collections[subgroup].extend(add_prims)
        self._update_bound()

    def remove_prim(self, prim: Usd.Prim):
        """Removes a prim from any collection and updates the bound."""
        empty_subgroups = set()
        for subgroup in self.collections:
            if prim in self.collections[subgroup]:
                self.collections[subgroup].remove(prim)
            if not len(self.collections[subgroup]):
                empty_subgroups.add(subgroup)
        for subgroup in empty_subgroups:
            if subgroup in self.collections:
                del self.collections[subgroup]
        self._update_bound()

    def remove_prims(self, prims: list[Usd.Prim]):
        """Removes a list of prims any collection and updates the bound."""
        empty_subgroups = set()
        for subgroup in self.collections:
            for prim in prims:
                if prim in self.collections[subgroup]:
                    self.collections[subgroup].remove(prim)
            if not len(self.collections[subgroup]):
                empty_subgroups.add(subgroup)
        for subgroup in empty_subgroups:
            if subgroup in self.collections:
                del self.collections[subgroup]
        self._update_bound()


class VehicleCollection:
    """Defines a collection of vehicle components.  Components are referenced
    by a unique ID: a concise (short) relative prim path.

    Inputs
        vehicle_root: The root of the asset to collect
        tagging (optional): A string indicating the tagging type
        types (optional): A list of strings defining the vehicle type.

    Properties:
        data: Vehicle specific data. ex. make, model, year.
        types: Vehicle types from semantic data.
        drivetrain: The type of driving method are used in the vehicle.
        steering: The type of steering method used in the vehicle.
        bound: The computed vehicle bounding box.
        transform: The vehicle transform.
        longitudinal_axis: The longitudinal/forward axis of the vehicle.
        lateral_axis: The lateral/side axis of the vehicle.
        vertical_axis: The vertical/up axis of the vehicle.
        tagging: Stores the type of tagging used.
        components: A dictionary of components by their unique ID.
        component_prims: A dictionary of prims collection type.
        collection_types: A list of collection types
        collected_prims: A list of prims that have been collected.
        orphans: A list of geometry prims that have not been collected.
    """

    ALLOWED_FOR_AUTO_GROUP = [
        "brake",
        "door",
        "pedal",
        "plate",
        "suspension",
        "shock",
        "spring",
        "strut",
        "wheel",
        "window",
        "trunk",
        "hood",
        "boot",
        "bonnet",
    ]
    ALLOWED_FOR_AUTO_PARENT = [
        "brake",
        "door",
        "plate",
        "steering",
        "suspension",
        "shock",
        "spring",
        "strut",
        "window",
    ]
    ASSUMED_PARENT_TYPE_MAP = {
        "fork": "handlebars",
        "handlebars": "body",
        "kickstand": "body",
        "pedal": "pedals",
        "pedals": "body",
    }

    def __init__(self, vehicle_root: Usd.Prim, tagging: TagType | None = None, types: list[VehicleType] | None = None):
        self._vehicle_root = vehicle_root
        self._stage = self._vehicle_root.GetStage() if vehicle_root else None

        # TODO: Add data from layer
        self.data = {}
        self._populate_data(self._vehicle_root, self.data)
        self._drivetrain = DriveMethod.FWD
        self.update_drivetrain()
        self._steering = SteerMethod.FRONT
        self.update_steering()

        self.bound = Gf.BBox3d()
        self.transform = self._get_transform(vehicle_root)

        self._types: list[VehicleType] = []
        self.update_types(types)
        self._tagging: TagType = tagging if tagging else self._get_tagging_type()

        self._longitudinal_axis: Gf.Vec3d = Gf.Vec3d.XAxis()
        self._vertical_axis: Gf.Vec3d = Gf.Vec3d.ZAxis()
        self.update_axes()

        self.components: dict[str, VehicleComponent] = {}

        self._pivot_ids: dict[Usd.Prim, str] = {}
        self._tag_sub_types: dict[Usd.Prim, str] = {}
        self._tag_types: dict[Usd.Prim, str] = {}
        self._hierarchy_prims: dict[Usd.Prim, list[tuple[Usd.Prim, str]]] = {}
        self._light_parents: dict[Usd.Prim, str] = {}
        self._light_groups: dict[Usd.Prim, str] = {}
        self._task_parents: dict[Usd.Prim, str] = {}
        self._prim_groups: dict[Usd.Prim, str] = {}
        self._prim_parents: dict[Usd.Prim, str] = {}
        self.component_prims: dict[CollectionMethod, list[Usd.Prim]] = {}
        self._get_component_prims()

        self._group_prims: dict[str, list[Usd.Prim]] = {}
        self._group_bounds: dict[str, Gf.BBox3d] = {}

        self.collected_prims: list[Usd.Prim] = []
        self._populate_collections()
        self._populate_hierarchies()
        self._populate_prims()
        self._populate_lights()
        self._populate_tasks()
        self._populate_pivots()
        self._auto_transform_components()

        self.orphans: list[Usd.Prim] = []
        self._find_orphan_prims()

    @property
    def vehicle_root(self):
        return self._vehicle_root

    @property
    def drivetrain(self):
        return self._drivetrain

    @property
    def steering(self):
        return self._steering

    @property
    def types(self):
        return self._types

    @property
    def tagging(self):
        return self._tagging

    @property
    def longitudinal_axis(self):
        return self._longitudinal_axis

    @property
    def lateral_axis(self) -> Gf.Vec3d:
        return Gf.Cross(self._vertical_axis, self._longitudinal_axis)

    @property
    def vertical_axis(self):
        return self._vertical_axis

    @property
    def collection_types(self):
        return list(self.component_prims.keys())

    # Query Functions

    def get_component_ids(self) -> list[str]:
        """Returns the collection's component ids."""
        return sorted(self.components.keys())

    def get_component_types(self) -> list[str]:
        """Returns the collection's used types."""
        component_types = set()
        for component in self.components.values():
            component_types.add(component.type)
        return sorted(list(component_types))

    def get_component_subtypes(self) -> list[str]:
        """Returns the collection's used subtypes."""
        component_subtypes = set()
        for component in self.components.values():
            component_subtypes.add(component.subtype)
        return sorted(list(component_subtypes))

    def get_components(self, sort_by: SortMethod | None = None) -> list[VehicleComponent]:
        """Returns the collection's component ids."""
        return self.get_sorted_components(list(self.components.values()), sort_by)

    def get_component(self, comp_id: str) -> VehicleComponent:
        """Returns a component with a given id."""
        return self.components.get(comp_id, None)

    def get_component_by_path(self, path: Sdf.Path) -> VehicleComponent:
        """Returns a component by the prim path that defined it."""
        for comp in self.components.values():
            if path == comp.prim.GetPath():
                return comp
        return None

    def get_collected_component(self, prim: Usd.Prim) -> VehicleComponent:
        """Returns a component that includes a collected prim."""
        for comp in self.components.values():
            for subgroup in comp.collections:
                for collected_prim in comp.collections[subgroup]:
                    if prim == collected_prim:
                        return comp
        return None

    def get_sorted_components(
        self, components: list[VehicleComponent], sort_by: SortMethod | None = SortMethod.TRANSFORM
    ) -> list[VehicleComponent]:
        """Returns a sorted list of components.

        SortMethod:
            UNSORTED(None): The components are returned unchanged.
            PATH: The components are sorted by their id/path value.
            TRANSFORM: The components are sorted from their top-front-left to bottom-back-right transform.
            CENTROID: The components are sorted from their top-front-left to bottom-back-right bounding box centroid.
            LENGTH: The components are sorted from the smallest to largest bounding box length.
            WIDTH: The components are sorted from the smallest to largest bounding box width.
            HEIGHT: The components are sorted from the smallest to largest bounding box height.
            VOLUME: The components are sorted from the smallest to largest bounding box volume.
        """
        if not components:
            return []

        if sort_by is None:
            return components
        elif sort_by == SortMethod.PATH:
            return list(sorted(components, key=lambda c: c.path))
        elif sort_by == SortMethod.VOLUME:
            return list(sorted(components, key=lambda c: c.bound.GetVolume()))

        centers = []
        for component in components:
            center = Gf.Vec3d(0)
            if sort_by == SortMethod.TRANSFORM:
                center = component.transform.ExtractTranslation()
            elif sort_by == SortMethod.CENTROID:
                center = component.bound.ComputeCentroid()
            elif sort_by in [SortMethod.LENGTH, SortMethod.WIDTH, SortMethod.HEIGHT]:
                center = component.bound.GetRange().GetSize()

            long_pos = round(self.longitudinal_axis.GetDot(center), 3)
            lat_pos = round(self.lateral_axis.GetDot(center), 3)
            vert_pos = round(self.vertical_axis.GetDot(center), 3)
            centers.append((long_pos, lat_pos, vert_pos))

        if sort_by == SortMethod.LENGTH:
            return [c for c, _ in sorted(zip(components, centers), key=lambda x: abs(x[1][0]))]
        elif sort_by == SortMethod.WIDTH:
            return [c for c, _ in sorted(zip(components, centers), key=lambda x: abs(x[1][1]))]
        elif sort_by == SortMethod.HEIGHT:
            return [c for c, _ in sorted(zip(components, centers), key=lambda x: abs(x[1][2]))]
        else:
            return list(reversed([c for c, _ in sorted(zip(components, centers), key=lambda x: x[1])]))

    def get_components_of_type(self, comp_type: str, sort_by: SortMethod | None = None) -> list[VehicleComponent]:
        """Returns a list of components matching a specified type."""
        components = []
        for comp in self.components.values():
            if comp.type == comp_type:
                components.append(comp)
        return self.get_sorted_components(components, sort_by)

    def get_components_of_subtype(self, comp_subtype: str, sort_by: SortMethod | None = None) -> list[VehicleComponent]:
        """Returns a list of components matching a specified type."""
        components = []
        for comp in self.components.values():
            if comp.subtype == comp_subtype:
                components.append(comp)
        return self.get_sorted_components(components, sort_by)

    def get_child_components(self, parent_id: str, sort_by: SortMethod | None = None) -> list[VehicleComponent]:
        """Returns a list of child components from a specified id."""
        components = []
        for comp in self.components.values():
            if comp.parent == parent_id:
                components.append(comp)
        return self.get_sorted_components(components, sort_by)

    def get_parent_components(self, comp_id: str, sort_by: SortMethod | None = None) -> list[VehicleComponent]:
        """Returns the parent components of the given id."""
        comp_parents = []
        component = self.components.get(comp_id, None)
        if component:
            comp_parent_ids = []
            test_comp = component
            while test_comp.parent is not None:
                parent_id = test_comp.parent
                comp_parent_ids.append(parent_id)
                test_comp = self.components.get(parent_id, None)
                comp_parents.append(test_comp)
        return self.get_sorted_components(comp_parents, sort_by)

    def compute_combined_bounds(self, comp_id: str) -> Gf.BBox3d:
        """Returns the bound of the component and its children."""
        bound = Gf.BBox3d()
        component = self.components.get(comp_id, None)
        if component:
            bound = component.bound
            child_components = self.get_child_components(comp_id)
            for child_comp in child_components:
                bound = Gf.BBox3d.Combine(bound, child_comp.bound)
        return bound

    # Wheel Query Functions

    def compute_wheel_axles(self) -> list[list[VehicleComponent]]:
        """Sort wheel components into axle groups spatially."""
        wheel_components = self.get_components_of_type("wheel", SortMethod.TRANSFORM)
        if not wheel_components:
            return []

        wheel_idx = 1
        axle_idx = 0
        axles = [[wheel_components[0]]]
        prev_pos = wheel_components[0].transform.ExtractTranslation()
        prev_long_pos = self.longitudinal_axis.GetDot(prev_pos)
        while wheel_idx < len(wheel_components):
            component = wheel_components[wheel_idx]
            pos = component.transform.ExtractTranslation()
            long_pos = self.longitudinal_axis.GetDot(pos)
            if Gf.IsClose(
                long_pos, prev_long_pos, UsdGeom.LinearUnits.millimeters / UsdGeom.GetStageMetersPerUnit(self._stage)
            ):
                axles[axle_idx].append(component)
            else:
                axles.append([component])
                axle_idx += 1
            wheel_idx += 1
            prev_long_pos = long_pos
        return axles

    def compute_wheels_center(self) -> Gf.Vec3d:
        """Computes the center point of all wheels."""
        wheel_components = self.get_components_of_type("wheel")
        if not wheel_components:
            return Gf.Vec3d(0)

        center_sum = Gf.Vec3d(0)
        for component in wheel_components:
            center = component.transform.ExtractTranslation()
            long_pos = round(self.longitudinal_axis.GetDot(center), 3)
            lat_pos = round(self.lateral_axis.GetDot(center), 3)
            vert_pos = round(self.vertical_axis.GetDot(center), 3)
            center_sum += Gf.Vec3d(long_pos, lat_pos, vert_pos)

        return center_sum / len(wheel_components)

    # Edit Functions

    def add_prim(self, component: VehicleComponent, prim: Usd.Prim, subgroup: str):
        """Adds a prim to the specified component in a subgroup."""
        component.add_prim(prim, subgroup)
        self.bound = Gf.BBox3d.Combine(self.bound, component.bound)
        self.collected_prims.append(prim)

    def add_prims(self, component: VehicleComponent, prims: list[Usd.Prim], subgroup: str):
        """Adds a prim to the specified component in a subgroup."""
        component.add_prims(prims, subgroup)
        self.bound = Gf.BBox3d.Combine(self.bound, component.bound)
        self.collected_prims.extend(prims)

    def add_component(
        self,
        prim: Usd.Prim,
        component_id: str,
        prim_type: str,
        prim_sub_type: str | None = None,
        parent: str | None = None,
        prim_path: Sdf.Path = None,
        transform: Gf.Matrix4d = None,
    ) -> VehicleComponent:
        """Creates a new component."""

        if not prim_path:
            prim_path = prim.GetPath()
        if not transform:
            transform = self._get_transform(prim)

        if component_id not in self.components:
            component = VehicleComponent(prim_type, prim_sub_type)
            self.components[component_id] = component
            component.path = component_id
            component.prim = prim
            if prim.IsA(UsdGeom.Xform):
                component.transform = transform
            if parent:
                component.parent = parent
        else:
            component = self.components[component_id]

        self._populate_data(prim, component.data)
        return component

    def remove_prim(self, component: VehicleComponent, prim: Usd.Prim, update_bound=True):
        """Removes a prim from the specified component."""
        if prim in self.collected_prims:
            component.remove_prim(prim)
            self.collected_prims.remove(prim)
            if update_bound:
                self._compute_vehicle_bound()

    def remove_prims(self, component: VehicleComponent, prims: list[Usd.Prim]):
        """Removes a list of prims from the specified component."""
        for prim in prims:
            self.remove_prim(component, prim, update_bound=False)
        self._compute_vehicle_bound()

    def remove_component(self, component: VehicleComponent):
        """Removes a component from the collection"""
        child_components = self.get_child_components(component.path)
        if len(child_components):
            for child_comp in child_components:
                child_comp.parent = component.parent

        collected_prims = component.collections.values()
        for coll_prim in collected_prims:
            if coll_prim in self.collected_prims:
                self.collected_prims.remove(coll_prim)
            self.orphans.append(coll_prim)

        self._compute_vehicle_bound()

        component_id = component.path
        if component_id:
            del self.components[component_id]

        prim = component.prim
        if prim and prim.IsValid():
            for collection_type in self.component_prims:
                if prim in self.component_prims[collection_type]:
                    self.component_prims[collection_type].remove(prim)

            if prim in self._hierarchy_prims:
                del self._hierarchy_prims[prim]
            if prim in self._tag_sub_types:
                del self._tag_sub_types[prim]
            if prim in self._tag_types:
                del self._tag_types[prim]
            if prim in self._light_parents:
                del self._light_parents[prim]
            if prim in self._light_groups:
                del self._light_groups[prim]
            if prim in self._task_parents:
                del self._task_parents[prim]
            if prim in self._prim_groups:
                del self._prim_groups[prim]
            if prim in self._prim_parents:
                del self._prim_parents[prim]

    # Update Functions

    def update_drivetrain(self, drivetrain: DriveMethod | None = None):
        """Updates the drivetrain type for the asset."""
        if not self._stage or not self.vehicle_root:
            return

        if drivetrain:
            self._drivetrain = drivetrain
        else:
            for prim in Usd.PrimRange(self.vehicle_root):
                if drivetrain_token := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_DRIVE_ATTR_NAME):
                    self._drivetrain = DriveMethod.drive_map().get(drivetrain_token.lower(), DriveMethod.FWD)
                    return

            self._drivetrain = DriveMethod.FWD

    def update_steering(self, steering: SteerMethod | None = None):
        """Updates the steering type for the asset."""
        if not self.vehicle_root:
            return

        if steering:
            self._steering = steering
        else:
            for prim in Usd.PrimRange(self.vehicle_root):
                if steering_token := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_STEER_ATTR_NAME):
                    self._steering = SteerMethod.steering_map().get(steering_token.lower(), SteerMethod.FRONT)
                    return
            self._steering = SteerMethod.FRONT

    def update_types(self, types: list[VehicleType] | None = None):
        """Updates the vehicle type type for the asset."""
        if not self.vehicle_root:
            return

        if types:
            self._types = types
        else:
            out_types = set()
            known_types = [t.value for t in list(VehicleType)]
            for prim in Usd.PrimRange(self.vehicle_root):
                if VehicleUtils.is_ignored(prim):
                    continue

                if types := VehicleUtils.get_types_from_wikidata(prim):
                    vehicle_types = [t for t in types if t in known_types]
                    out_types.update(vehicle_types)

                self._types = [VehicleType(t) for t in out_types]

    def update_axes(self, longitudinal_axis: Gf.Vec3d | None = None):
        """Updates the axes of the asset."""
        if not self._stage or not self.vehicle_root:
            return

        if UsdGeom.GetStageUpAxis(self._stage) is UsdGeom.Tokens.z:
            self._vertical_axis = Gf.Vec3d.ZAxis()
        else:
            self._vertical_axis = Gf.Vec3d.YAxis()

        if longitudinal_axis:
            self._longitudinal_axis = longitudinal_axis
        else:
            for prim in Usd.PrimRange(self.vehicle_root):
                if long_axis_token := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_AXIS_ATTR_NAME):
                    self._longitudinal_axis = VehicleUtils.get_vec_from_axis(long_axis_token, Gf.Vec3d.XAxis())
                    return

            self._longitudinal_axis = Gf.Vec3d.XAxis()

    def update_transforms(self):
        """Recomputes the transforms in the collection."""
        if not self.vehicle_root:
            return

        self.transform = self._get_transform(self.vehicle_root)
        for component in self.components.values():
            prim = component.prim
            if prim and prim.IsA(UsdGeom.Xform):
                component.transform = self._get_transform(prim)
        self._populate_pivots()
        self.update_bounds()

    def update_bounds(self):
        """Recomputes the bounds in the collection."""
        if not self.vehicle_root:
            return

        for component in self.components.values():
            component._update_bound()
        self._compute_vehicle_bound()

    # Private Functions

    def _find_orphan_prims(self):
        """Finds uncollected prims in the collection."""
        self.orphans = []
        if not self.vehicle_root:
            return

        for prim in Usd.PrimRange(self.vehicle_root):
            is_ignored = VehicleUtils.is_ignored(prim)
            is_group = VehicleUtils.is_group(prim)
            if prim not in self.collected_prims and not is_ignored and not is_group:
                self.orphans.append(prim)

    def _populate_data(self, prim: Usd.Prim, data: dict):
        """Read SimReady data from a prim and set in provided dictionary."""
        if not prim:
            return

        for prop in prim.GetProperties():
            prop_name = prop.GetName()
            if prop_name == SIMREADY.VEHICLE_ATTR_NAME:
                continue
            if prop_name.startswith(SIMREADY.SIMREADY_PREFIX) and prop_name not in data:
                data_name = prop_name.removeprefix(SIMREADY.SIMREADY_PREFIX)
                if isinstance(prop, Usd.Attribute):
                    data[data_name] = prop.Get()
                else:
                    data[data_name] = prop.GetTargets()

    def _get_tagging_type(self) -> TagType:
        """Gets the tagging type from the asset."""
        if not self.vehicle_root:
            return None

        prim_range = Usd.PrimRange(self.vehicle_root)
        if any([not VehicleUtils.is_ignored(p) and VehicleUtils.has_simready_tag(p) for p in prim_range]):
            return TagType.SIMREADY
        else:
            return TagType.SEMANTIC

    def _get_transform(self, prim: Usd.Prim) -> Gf.Matrix4d:
        """Read the world transform of a prim."""
        mtx = None
        # TODO Take transform:pivot into account
        if prim and prim.IsA(UsdGeom.Xformable):
            xform = UsdGeom.Xformable(prim)
            mtx = xform.ComputeLocalToWorldTransform(DEFAULT_TIME)
        return mtx

    def _get_parent_path(self, prim: Usd.Prim) -> str:
        """Computes the ID of the closest ancestor."""
        ancestors = prim.GetParent().GetPath().GetAncestorsRange()
        for ancestor in ancestors:
            for component in self.components.values():
                if ancestor == component.prim.GetPath():
                    return component.path
        return None

    def _has_hierarchy_prims(self, root: Usd.Prim) -> bool:
        """Returns True if a hierarchy has un tagged prims and caches the prims."""
        (root_type, _) = VehicleUtils.get_tagged_type(root, self.tagging)
        root_is_group = VehicleUtils.is_group(root)
        root_is_ignored = VehicleUtils.is_ignored(root)
        if not root_is_group or not root.GetChildren() or root_is_ignored or root_type is None or root_type == "task":
            return False

        if root in self._hierarchy_prims:
            return True

        is_hierarchy = False
        root_path = root.GetPath()
        subgroups = {}
        if root_subgroup := VehicleUtils.get_simready_tag(root, SIMREADY.VEHICLE_SUBGROUP_ATTR_NAME):
            subgroups[root_path] = root_subgroup
        else:
            subgroups[root_path] = root_type

        prim_range_it = iter(Usd.PrimRange(root))
        for prim in prim_range_it:
            if prim == root or VehicleUtils.is_ignored(prim):
                continue

            (tagged_type, _) = VehicleUtils.get_tagged_type(prim, self.tagging)
            is_group = VehicleUtils.is_group(prim)
            prim_path = prim.GetPath()

            if child_subgroup := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_SUBGROUP_ATTR_NAME):
                subgroups[prim_path] = child_subgroup

            # Exclude other hierarchies and tasks
            if self._has_hierarchy_prims(prim) or tagged_type == "task":
                prim_range_it.PruneChildren()
                continue

            # Include all non-group un-tagged prims
            if not is_group and not tagged_type:
                ancestors = prim_path.GetAncestorsRange()
                subgroup_path = next(iter([p for p in ancestors if p in subgroups]), None)
                subgroup = subgroups.get(subgroup_path, root_type)
                self._hierarchy_prims.setdefault(root, []).append((prim, subgroup))
                is_hierarchy = True

        return is_hierarchy

    def _get_component_prims(self):
        """Searches for tagged component prims in the asset."""
        if not self.vehicle_root:
            return

        for prim in Usd.PrimRange(self.vehicle_root):
            if VehicleUtils.is_ignored(prim):
                continue

            if prim.IsA(UsdGeom.Xform) and (
                pivot_id := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_PIVOT_ATTR_NAME)
            ):
                self._pivot_ids[prim] = pivot_id

            (tag_type, tag_sub_type) = VehicleUtils.get_tagged_type(prim, self.tagging)
            if tag_type is None:
                continue

            self._tag_types[prim] = tag_type
            self._tag_sub_types[prim] = tag_sub_type

            is_collection = VehicleUtils.is_collection(prim)
            is_hierarchy = self._has_hierarchy_prims(prim)

            if is_collection and is_hierarchy:
                # This approach is taken to avoid supporting collections on individually tagged prims.
                self.component_prims.setdefault(CollectionMethod.COLLECTION, []).append(prim)
                self.component_prims.setdefault(CollectionMethod.HIERARCHY, []).append(prim)
            elif is_collection:
                self.component_prims.setdefault(CollectionMethod.COLLECTION, []).append(prim)
            elif is_hierarchy:
                self.component_prims.setdefault(CollectionMethod.HIERARCHY, []).append(prim)
            elif tag_type == "light":
                self.component_prims.setdefault(CollectionMethod.LIGHT, []).append(prim)
                if group_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_GROUP_ATTR_NAME):
                    self._light_groups[prim] = group_tag
                if parent_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_PARENT_ATTR_NAME):
                    self._light_parents[prim] = parent_tag
            elif tag_type == "task":
                self.component_prims.setdefault(CollectionMethod.TASK, []).append(prim)
                if parent_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_PARENT_ATTR_NAME):
                    self._task_parents[prim] = parent_tag
            elif not VehicleUtils.is_group(prim) or prim.IsInstanceable():
                self.component_prims.setdefault(CollectionMethod.PRIM, []).append(prim)
                if group_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_GROUP_ATTR_NAME):
                    self._prim_groups[prim] = group_tag
                if parent_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_PARENT_ATTR_NAME):
                    self._prim_parents[prim] = parent_tag

    def _compute_vehicle_bound(self):
        """Computes the vehicle bound from the union of all components."""
        self.bound = Gf.BBox3d()
        for component in self.components.values():
            self.bound = Gf.BBox3d.Combine(self.bound, component.bound)

    def _get_group_prims(self) -> dict[str, list[Usd.Prim]]:
        """Creates a dictionary of prims by their group."""
        if not len(self._group_prims):
            self._group_prims = {}
            for prim, group in self._prim_groups.items():
                if group not in self._group_prims:
                    self._group_prims[group] = []
                self._group_prims[group].append(prim)

        return self._group_prims

    def _get_group_bounds(self) -> dict[str, Gf.BBox3d]:
        """Creates a dictionary of bounds by their group."""
        if not len(self._group_prims):
            self._get_group_prims()

        if not len(self._group_bounds):
            self._group_bounds = {}
            for group in self._group_prims:
                group_bound = Gf.BBox3d()
                for prim in self._group_prims[group]:
                    bound = VehicleUtils.compute_world_bound(prim)
                    group_bound = Gf.BBox3d.Combine(group_bound, bound)
                self._group_bounds[group] = group_bound
        return self._group_bounds

    # Population Functions

    def _auto_group_prims(self, prims: list[Usd.Prim]):
        """Groups ungrouped prims based on their bounding box proximity."""
        ungrouped_prims = [p for p in prims if p not in self._prim_groups]
        type_prims = {}
        for prim in ungrouped_prims:
            prim_type = self._tag_sub_types[prim]
            parent_path = self._get_parent_path(prim)
            parent_component = self.components.get(parent_path)
            if prim_type in self.ALLOWED_FOR_AUTO_GROUP:
                if prim_type not in type_prims:
                    type_prims[prim_type] = []
                type_prims[prim_type].append(prim)
            elif parent_component and parent_component.type == prim_type:
                self._prim_groups[prim] = parent_path
            else:
                self._prim_groups[prim] = prim_type

        for prim_type in type_prims:
            # Compute bounds for each prim
            sorted_bounds = {}
            for prim in type_prims[prim_type]:
                sorted_bounds[prim] = VehicleUtils.compute_world_bound(prim)

            # Sort bounds by their volume, largest to smallest
            prim_groups = []
            bounds = []
            sorted_bounds = dict(reversed(sorted(sorted_bounds.items(), key=lambda b: b[1].GetVolume())))
            for prim, bound in sorted_bounds.items():
                bounds.append(bound)
                prim_groups.append([prim])

            # Check if each bound contains any of the other bounds
            for bound_idx, bound in enumerate(bounds):
                if bound is None:
                    continue

                found_indices = set()
                for search_idx, search_bound in enumerate(bounds):
                    if bound_idx == search_idx or search_bound is None:
                        continue
                    if bound.GetRange().Contains(search_bound.ComputeCentroid()):
                        found_indices.add(search_idx)

                for idx in found_indices:
                    bounds[bound_idx] = Gf.BBox3d.Combine(bound, bounds[idx])
                    bounds[idx] = None
                    prim_groups[bound_idx].extend(prim_groups[idx])
                    prim_groups[idx] = None

            # Create a dict to organize prims and their
            centers = {}
            prim_groups = dict((f"group_{i}", g) for i, g in enumerate(prim_groups) if g is not None)
            for i, bound in enumerate(bounds):
                if bound is None:
                    continue
                center = bound.ComputeCentroid()
                long_pos = round(self.longitudinal_axis.GetDot(center), 3)
                lat_pos = round(self.lateral_axis.GetDot(center), 3)
                centers[f"group_{i}"] = tuple([long_pos, lat_pos])

            # Assign numerical group id
            sorted_centers = dict(reversed(sorted(centers.items(), key=lambda c: c[1])))
            for group_idx, group_name in enumerate(sorted_centers.keys()):
                group_id = f"{prim_type}_{group_idx}"
                for prim in prim_groups[group_name]:
                    self._prim_groups[prim] = group_id

    def _auto_parent_prims(self, prims: list[Usd.Prim]):
        """Parents prims based on their bounding box proximity."""
        un_parented_prims = [p for p in prims if p not in self._prim_parents]
        if not un_parented_prims:
            return

        group_prims = self._get_group_prims()
        group_parent = {}
        group_type = {}
        group_parent_paths = {}
        for prim, group in self._prim_groups.items():
            # Store the first type
            if group not in group_type:
                group_type[group] = self._tag_sub_types[prim]

            # Store the first tagged parent for the group
            if prim in self._prim_parents:
                if group not in group_parent:
                    group_parent[group] = self._prim_parents[prim]

            # Store all of the ancestor paths for the group
            if parent := self._get_parent_path(prim):
                if group not in group_parent_paths:
                    group_parent_paths[group] = []
                group_parent_paths[group].append(parent)

        for group in group_prims:
            # All prims in the group share the same tagged parent
            if len(set(group_parent_paths.get(group, []))) == 1:
                group_parent[group] = group_parent_paths[group][0]
            # The type has an assumed parent type
            elif group_type[group] in self.ASSUMED_PARENT_TYPE_MAP:
                parent_type = self.ASSUMED_PARENT_TYPE_MAP[group_type[group]]
                if first_parent := next(iter([g for g in group_type if group_type[g] == parent_type]), None):
                    group_parent[group] = first_parent

            for prim in group_prims[group]:
                if group in group_parent:
                    self._prim_parents[prim] = group_parent[group]

        # Process smallest bound to largest
        group_bounds = self._get_group_bounds()
        un_parented_groups = [g for g in group_prims if g not in group_parent]
        sorted_group_bounds = dict(sorted(group_bounds.items(), key=lambda b: b[1].GetVolume()))
        for i, group in enumerate(sorted_group_bounds):
            if group_type[group] in self.ALLOWED_FOR_AUTO_PARENT and group in un_parented_groups:
                # Find the next biggest bound that the groups center is contained in
                group_center = group_bounds[group].ComputeCentroid()
                search_groups = list(sorted_group_bounds.keys())[(i + 1) :]
                for search_group in search_groups:
                    search_group_range = group_bounds[search_group].GetRange()
                    if search_group_range.Contains(group_center) and group not in group_parent:
                        # TODO: Find general solution about hard coded assumptions about dependencies
                        # Brakes should only be parented under wheels
                        if group_type[group] == "brake" and group_type[search_group] != "wheel":
                            continue
                        # Wheels should only have brake children
                        elif group_type[search_group] == "wheel" and group_type[group] != "brake":
                            continue

                        group_parent[group] = search_group
                        for prim in group_prims[group]:
                            self._prim_parents[prim] = search_group
                        break

                # If not found, fall back to the largest bound
                if group not in group_parent:
                    fallback_group = list(sorted_group_bounds.keys())[-1]
                    group_parent[group] = fallback_group
                    for prim in group_prims[group]:
                        self._prim_parents[prim] = fallback_group

    def _auto_transform_components(self):
        """Transforms components to their bounding box if none is set."""
        for component in self.components.values():
            if component.transform is None:
                component.transform = Gf.Matrix4d(1)
                if component.bound.GetRange() != Gf.Range3d():
                    center = component.bound.ComputeCentroid()
                    component.transform.SetTranslateOnly(center)

    def _populate_collections(self):
        """Populates components from collection groups"""
        collections = self.component_prims.get(CollectionMethod.COLLECTION, [])
        collection_paths = Sdf.Path.GetConciseRelativePaths([c.GetPath() for c in collections])
        remove = []
        for prim, path in zip(collections, collection_paths):
            collection_prims = {}
            for schema in VehicleUtils.get_collections(prim):
                subgroup = schema.split(":")[-1]
                collection = Usd.CollectionAPI.GetCollection(prim, subgroup)
                query = collection.ComputeMembershipQuery()
                schema_prims = collection.ComputeIncludedObjects(query, self._stage)
                prims = [
                    p
                    for p in schema_prims
                    if not VehicleUtils.is_ignored(p) and not VehicleUtils.is_group(p) and p not in self.collected_prims
                ]
                if prims:
                    collection_prims[subgroup] = prims

            if not len(collection_prims):
                remove.append(prim)
                continue

            prim_type = self._tag_types.get(prim)
            prim_sub_type = self._tag_sub_types.get(prim)

            if group_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_GROUP_ATTR_NAME):
                component_id = group_tag
            else:
                component_id = path.pathString

            if parent_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_PARENT_ATTR_NAME):
                parent = parent_tag
            else:
                parent = self._get_parent_path(prim)

            component = self.add_component(prim, component_id, prim_type, prim_sub_type=prim_sub_type, parent=parent)

            if prim_type == "light" and "light" not in component.data:
                component.data["light"] = VehicleUtils.get_light_types_from_wikidata(prim)

            for subgroup in collection_prims:
                self.add_prims(component, collection_prims[subgroup], subgroup)

        for prim in remove:
            self.component_prims[CollectionMethod.COLLECTION].remove(prim)

    def _populate_hierarchies(self):
        """Populates components from hierarchies"""
        hierarchies = self.component_prims.get(CollectionMethod.HIERARCHY, [])
        hierarchy_paths = Sdf.Path.GetConciseRelativePaths([h.GetPath() for h in hierarchies])
        remove = []
        for prim, path in zip(hierarchies, hierarchy_paths):
            children = [(p, s) for p, s in self._hierarchy_prims.get(prim, []) if p not in self.collected_prims]
            if not len(children):
                remove.append(prim)
                continue

            prim_type = self._tag_types.get(prim)
            prim_sub_type = self._tag_sub_types.get(prim)

            if group_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_GROUP_ATTR_NAME):
                component_id = group_tag
            elif prim_sub_type in [t.value for t in list(VehicleType)]:
                component_id = "body"
            else:
                component_id = path.pathString

            if parent_tag := VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_PARENT_ATTR_NAME):
                parent = parent_tag
            else:
                parent = self._get_parent_path(prim)

            component = self.add_component(prim, component_id, prim_type, prim_sub_type=prim_sub_type, parent=parent)

            if prim_type == "light" and "light" not in component.data:
                component.data["light"] = VehicleUtils.get_light_types_from_wikidata(prim)

            for child, subgroup in children:
                self.add_prim(component, child, subgroup)

        for prim in remove:
            self.component_prims[CollectionMethod.HIERARCHY].remove(prim)

    def _populate_prims(self):
        """Populates components from prims"""
        prims = self.component_prims.get(CollectionMethod.PRIM, [])
        self._auto_group_prims(prims)
        self._auto_parent_prims(prims)
        remove = []
        for prim in prims:
            if prim in self.collected_prims:
                remove.append(prim)
                continue

            prim_type = self._tag_types.get(prim)
            prim_sub_type = self._tag_sub_types.get(prim)

            component_id = self._prim_groups.get(prim, prim_type)
            parent = self._prim_parents.get(prim)
            component = self.add_component(prim, component_id, prim_type, prim_sub_type=prim_sub_type, parent=parent)

            subgroup = VehicleUtils.get_simready_tag(prim, SIMREADY.VEHICLE_SUBGROUP_ATTR_NAME, fallback=prim_type)

            self.add_prim(component, prim, subgroup)

        for prim in remove:
            self.component_prims[CollectionMethod.PRIM].remove(prim)

    def _populate_lights(self):
        """Populates components from lights"""
        lights = self.component_prims.get(CollectionMethod.LIGHT, [])

        # Search for light parents
        un_parented_lights = [lt for lt in lights if lt not in self._light_parents]
        light_centers = {}
        pivot_paths = dict([(p.GetPath(), g) for p, g in self._pivot_ids.items()])
        for light in un_parented_lights:
            parent = self._get_parent_path(light)
            if not parent:
                ancestors = light.GetParent().GetPath().GetAncestorsRange()
                pivot_path = next(iter([p for p in ancestors if p in pivot_paths]), None)
                parent = pivot_paths.get(pivot_path, None)

            if parent:
                self._light_parents[light] = parent
            else:
                bound = VehicleUtils.compute_world_bound(light)
                light_centers[light] = bound.ComputeCentroid()

        # If no parent found, search for spatial parents
        if light_centers:
            group_bounds = self._get_group_bounds()
            sorted_group_bounds = dict(sorted(group_bounds.items(), key=lambda b: b[1].GetVolume()))
            for group in sorted_group_bounds:
                group_range = group_bounds[group].GetRange()
                for light in light_centers:
                    light_center = light_centers[light]
                    if group_range.Contains(light_center) and light not in self._light_parents:
                        self._light_parents[light] = group

        remove = []
        for prim in lights:
            if prim in self.collected_prims:
                remove.append(prim)
                continue

            prim_type = self._tag_types.get(prim)
            prim_sub_type = self._tag_sub_types.get(prim)

            parent = self._light_parents.get(prim)
            if light_group := self._light_groups.get(prim):
                component_id = light_group
            else:
                component_id = prim_type
                if parent:
                    component_id = f"{parent}/{component_id}"

                if light_types := VehicleUtils.get_simready_tag(
                    prim, SIMREADY.LIGHT_ATTR_NAME, Sdf.ValueTypeNames.TokenArray
                ):
                    component_id += "_" + "_".join(light_types)
                elif light_types := VehicleUtils.get_light_types_from_wikidata(prim):
                    component_id += "_" + "_".join(light_types)

            component = self.add_component(prim, component_id, prim_type, prim_sub_type=prim_sub_type, parent=parent)
            self.add_prim(component, prim, prim_type)

            # Apply subtype as type if we didn't specify light types
            # This may happen when tagging type is semantic
            if "light" not in component.data:
                component.data["light"] = VehicleUtils.get_light_types_from_wikidata(prim)

        for prim in remove:
            self.component_prims[CollectionMethod.LIGHT].remove(prim)

    def _populate_tasks(self):
        """Populates components from tasks"""
        tasks = self.component_prims.get(CollectionMethod.TASK, [])

        # Search for parents
        un_parented_tasks = [t for t in tasks if t not in self._task_parents]
        task_centers = {}
        pivot_paths = dict([(p.GetPath(), g) for p, g in self._pivot_ids.items()])
        for task in un_parented_tasks:
            parent = self._get_parent_path(task)
            if not parent:
                ancestors = task.GetParent().GetPath().GetAncestorsRange()
                pivot_path = next(iter([p for p in ancestors if p in pivot_paths]), None)
                parent = pivot_paths.get(pivot_path, None)

            if parent:
                self._task_parents[task] = parent
            else:
                transform = self._get_transform(task)
                task_centers[task] = transform.ExtractTranslation()

        # If no parent found, search for spatial parents
        if task_centers:
            group_bounds = self._get_group_bounds()
            sorted_group_bounds = dict(sorted(group_bounds.items(), key=lambda b: b[1].GetVolume()))
            for group in sorted_group_bounds:
                group_range = group_bounds[group].GetRange()
                for task in task_centers:
                    task_center = task_centers[task]
                    if group_range.Contains(task_center) and task not in self._task_parents:
                        self._task_parents[task] = group

        remove = []
        for prim in tasks:
            if prim in self.collected_prims:
                remove.append(prim)
                continue

            prim_type = self._tag_types.get(prim)
            prim_sub_type = self._tag_sub_types.get(prim)

            component_id = prim_type
            if group := VehicleUtils.get_simready_tag(prim, SIMREADY.TASKS_GROUP_ATTR_NAME):
                component_id += "_" + group
            if tasks := VehicleUtils.get_simready_tag(prim, SIMREADY.TASKS_ATTR_NAME, Sdf.ValueTypeNames.TokenArray):
                component_id += "_" + "_".join(tasks)
            if effector := VehicleUtils.get_simready_tag(prim, SIMREADY.TASKS_EFFECTOR_ATTR_NAME):
                component_id += "_" + effector

            parent = self._task_parents.get(prim)
            component = self.add_component(prim, component_id, prim_type, prim_sub_type=prim_sub_type, parent=parent)
            self.add_prim(component, prim, prim_type)

        for prim in remove:
            self.component_prims[CollectionMethod.TASK].remove(prim)

    def _populate_pivots(self):
        """Applies data and transforms from the pivot to the specified component id."""
        for pivot in self._pivot_ids:
            comp_id = self._pivot_ids[pivot]
            component = self.components.get(comp_id)
            if component:
                self._populate_data(pivot, component.data)
                component.transform = self._get_transform(pivot)
