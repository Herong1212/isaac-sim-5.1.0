# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")


class LayerIcons:
    """A singleton that scans the icon folder and returns the icon depending on the type"""
    _icons = {}

    @classmethod
    def get(cls, name, default=None):
        """Checks the icon cache and returns the icon if exists"""
        if not cls._icons:
            # Read all the svg files in the directory
            LayerIcons._icons = {icon.stem: icon for icon in ICON_PATH.glob("*.svg")}

        found = LayerIcons._icons.get(name)
        if not found and default:
            found = LayerIcons._icons.get(default)

        if found:
            return str(found)
