# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['IRegistryIndex', 'RegistryURLs']

from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import List
import carb.dictionary


@dataclass
class RegistryURLs:
    index: str # Root of the index (after the version part, e.g. C:/kit/default/3)
    archives: str # Path to store archives and metadata
    resources: str # Path to store hashed resources
    archives_alternatives: List[str] = None  # Support searching for archive in old version locations:
    index_file: str = "" # Remote index file URL


class IRegistryIndex(ABC):
    """Interface for registry index implementation.

    Index is a database of all packages in the registry. This interface allows to abstract it away and transition
    from V1 to V2 index layout.
    """
    @abstractmethod
    def get_urls(self) -> RegistryURLs:
        pass

    @abstractmethod
    def get_index_dict(self) -> carb.dictionary.Item:
        pass

    @abstractmethod
    def refresh_index(self):
        pass

    @abstractmethod
    def sync_index(self, resync=False):
        pass

    @abstractmethod
    def upload_resources(self, ext_id, ext_dict, **kwargs):
        pass

    @abstractmethod
    def add_to_index(self, ext_id, ext_dict):
        pass

    @abstractmethod
    def remove_from_index(self, ext_id, ext_dict):
        pass

    @abstractmethod
    def shutdown(self):
        pass

    @abstractmethod
    def apply_index_changes_batch(self) -> bool:
        pass

    @abstractmethod
    def get_package_dict(self, package_id: str) -> dict:
        pass
