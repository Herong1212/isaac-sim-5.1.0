# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable


class PropertyType(Enum):
    ATTRIBUTE = (auto(),)
    RELATIONSHIP = auto()


class AttributeAdapter(ABC):
    """
    Attribute Adapter
    """

    def __init__(self, attribute) -> None:
        self._attribute = attribute

    def __getattr__(self, attr):
        return getattr(self._attribute, attr)

    @property
    def attribute(self):
        return self._attribute

    @abstractmethod
    def GetPrim(self):  # noqa: N802
        raise NotImplementedError

    @abstractmethod
    def GetPropertyType(self):  # noqa: N802
        raise NotImplementedError


class PrimAdapter(ABC):  # noqa: B024
    """
    Prim Adapter
    """

    def __init__(self, prim) -> None:
        self._prim = prim

    def __getattr__(self, attr):
        return getattr(self._prim, attr)

    @property
    def prim(self):
        return self._prim


class StageAdapter(ABC):
    """
    Stage Adapter
    """

    def __init__(self, stage) -> None:
        self._stage = stage

    def __getattr__(self, attr):
        return getattr(self._stage, attr)

    @property
    def name(self) -> str:
        return ""

    @property
    def priority_read(self) -> int:
        return 0

    @property
    def priority_write(self) -> int:
        return 0

    @property
    def stage(self):
        return self._stage

    @property
    def usd_stage(self):
        return self._stage

    @abstractmethod
    def GetPrimAtPath(self, path):  # noqa: N802
        raise NotImplementedError

    @abstractmethod
    def GetAttributeAtPath(self, path):  # noqa: N802
        raise NotImplementedError

    @abstractmethod
    def CreateChangeTracker(self, attr_names: list, prim_paths: list, callback: Callable) -> Any:  # noqa: N802
        raise NotImplementedError

    @abstractmethod
    def convert_data(self, data, dst_adapter_name: str):
        raise NotImplementedError

    @abstractmethod
    def resolve_path_array(self, path, resolve_path: str, path_list, index):
        raise NotImplementedError

    @abstractmethod
    def get_notice_paths(self, stage, notice):
        raise NotImplementedError
