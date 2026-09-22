import inspect
from dataclasses import dataclass, field, is_dataclass
from enum import Enum
from math import radians
from typing import Any, List, Tuple, Type, TypeVar, get_type_hints

MAX_NUM_DETS = 2500


class RadarDetection:
    r_m = -1
    rv_ms = -1
    az_ang_rad = -1
    elev_ang_rad = -1
    rcs_dbsm = -1


class RadarPointCloud:
    frameId = -1
    sync_data = -1
    tasking_counter = -1
    sensor_id = -1
    scan_idx = -1
    timestamp_ns = -1
    cycle_cnt = -1
    max_range_m = -1
    min_vel_mps = -1
    max_vel_mps = -1
    min_az_rad = -1
    max_az_rad = -1
    min_el_rad = -1
    max_el_rad = -1
    num_detections = -1
    detections = []


@dataclass
class GmoFrameAtTime:
    timestampNs: int
    orientation: List[float]
    posM: List[float]


def get_value_from_enum(value_str: str, enum_type: Enum):
    enum_name_value_list = [(name, value) for name, value in vars(enum_type).items()]
    for name, value in enum_name_value_list:
        if name.startswith("_"):
            continue
        if name.lower() in str(value_str).lower():
            return value
    return None


class GmoCoordsType(Enum):
    CARTESIAN = 0
    SPHERICAL = 1  # x,y,z of BasicPoints contains: azimuth, elevation, distance
    NOT_APPLICABLE = 2  # Pixels?


class GmoFrameOfReference(Enum):
    SENSOR = 0
    WORLD = 1
    CUSTOM = 2
    PARENT = 3


class GmoMotionCompensationState(Enum):
    NONCOMPENSATED = 0
    COMPENSATED = 1
    NOT_APPLICABLE = 2


class GmoOutputType(Enum):
    POINTCLOUD = 0


@dataclass
class GmoRadarFrame:
    magicNumber: int

    majorVersion: int
    minorVersion: int
    patchVersion: int

    sizeInBytes: int
    numElements: int

    frameOfReference: GmoFrameOfReference
    motionCompensationState: GmoMotionCompensationState

    frameId: int
    timestampNs: int

    elementsCoordsType: GmoCoordsType
    outputType: GmoOutputType

    # frameEnd: _generic_model_output.FrameAtTime
    # frameStart: _generic_model_output.FrameAtTime

    sensorID: int
    scanIdx: int
    cycleCnt: int
    maxRangeM: float
    minVelMps: float
    maxVelMps: float
    minAzRad: float
    maxAzRad: float
    minElRad: float
    maxElRad: float

    timeOffSetNs: List[int] = field(default_factory=list)
    x: List[float] = field(default_factory=list)
    y: List[float] = field(default_factory=list)
    z: List[float] = field(default_factory=list)
    flags: List[int] = field(default_factory=list)
    scalar: List[float] = field(default_factory=list)

    rv_ms: List[float] = field(default_factory=list)

    @classmethod
    def from_readModelOutput(cls, other):
        fields = {f.name for f in cls.__dataclass_fields__.values()}
        kwargs = {}

        for fieldname in fields:
            if not hasattr(other, fieldname):
                continue

            value = getattr(other, fieldname)

            # If the type annotation from a dataclass field is an Enum, we need
            # to convert the value to the Enum type.
            annotation_type = cls.__annotations__[fieldname]
            if inspect.isclass(annotation_type):
                is_enum = issubclass(annotation_type, Enum)
                if is_enum:
                    value = get_value_from_enum(value, annotation_type)
                    kwargs[fieldname] = value
                    continue

            # Handle lists explicitly
            if isinstance(value, list):
                value = [x for x in value]

            kwargs[fieldname] = value

        return cls(**kwargs)

    def get_az_el_range(self) -> Tuple[List[float], List[float], List[float]]:

        if self.elementsCoordsType != GmoCoordsType.SPHERICAL:
            raise ValueError("This method is only valid for spherical coordinates")

        az_ang_rad = [radians(x) for x in self.x]
        elev_ang_rad = [radians(y) for y in self.y]
        r_m = [r for r in self.z]

        return az_ang_rad, elev_ang_rad, r_m
