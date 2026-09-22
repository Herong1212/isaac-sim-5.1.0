# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["USDMetadataModel"]

from typing import Any
from pxr import Sdf, Usd

import omni.kit.commands

from .usd_object_model import USDObjectModel


class USDMetadataModel(USDObjectModel):
    """A simple value model to watch the specified metadata."""

    def __init__(self, stage: Usd.Stage, path: Sdf.Path, md_key: str):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            path (Sdf.Path): Path in stage.
            md_key (str): Meta data key.
        """
        super().__init__(stage, path)
        self.__md_key = md_key

    def set_value(self, value: Any):
        """
        Set the value directly to USD.

        Args:
            value (Any): New value to set.
        """
        omni.kit.commands.execute('ChangeMetadataCommand', object_paths=[self.path], key=self.__md_key, value=value)

    def _get_value(self) -> Any:
        """Get the value directly from USD"""
        obj = self.stage.GetObjectAtPath(self.path) if self.stage else None
        return obj.GetMetadata(self.__md_key) if obj else None
