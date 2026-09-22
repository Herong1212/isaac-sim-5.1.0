# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Use these at your own risk, and forward-compatability is not supported

__all__ = ["XRAssetManager", "XRAssetPackageInfo"]

from typing import Optional, Tuple, Union

import carb

from ..._xrcore import XRAssetManager_Internal, XRAssetPackageInfo, XRToken

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRAssetManager class wrapper
# ================================================

# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRAssetManager:
    _singleton: "XRAssetManager"
    _singleton_deleted: bool

    def __init__(self):
        if hasattr(XRAssetManager, "_singleton"):
            carb.log_error("Do not instantiate XRAssetManager directly -- instead, use XRAssetManager.get_singleton()")

        self.__internal = XRAssetManager_Internal()

    def __eq__(self, other):
        if isinstance(other, XRAssetManager):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRAssetManager_Internal:
        return self.__internal

    @staticmethod
    # NOTE: if we move to Python 3.11, this should return Self instead of "XRAssetManager"
    def get_singleton() -> Optional["XRAssetManager"]:
        if hasattr(XRAssetManager, "_singleton_deleted"):
            return None

        if not hasattr(XRAssetManager, "_singleton"):
            carb.log_info("creating XRAssetManager singleton")
            XRAssetManager._singleton = XRAssetManager()

        return XRAssetManager._singleton

    @staticmethod
    def _delete_singleton() -> None:
        if hasattr(XRAssetManager, "_singleton"):
            carb.log_info("deleting XRAssetManager singleton")
            del XRAssetManager._singleton
            XRAssetManager._singleton_deleted = True

    def get_asset_package_list(self) -> Tuple[XRAssetPackageInfo]:
        """
        Get the list of xrasset packages available.

        Return:
            List of xrasset packages
        """
        return self.__internal.get_asset_package_list()

    def resolve_asset_path(self, asset_name: Union[str, XRToken]) -> str:
        """
        Resolve the asset path.

        Args:
            asset_name: the name of asset (package + internal path)

        Return:
            path to the asset
        """
        return self.__internal.resolve_asset_path(asset_name)
