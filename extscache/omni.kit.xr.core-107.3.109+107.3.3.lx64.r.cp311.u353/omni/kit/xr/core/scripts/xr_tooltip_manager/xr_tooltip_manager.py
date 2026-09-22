# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import Optional, Union

from ..xr_singleton import XRSingleton, XRSingletonType


class XRTooltip:
    def __init__(self, icon=None, text=None):
        self.__icon: Optional[str] = icon
        self.__text: Union[str, list[str], None] = text

    @property
    def icon(self) -> Optional[str]:
        return self.__icon

    @icon.setter
    def icon(self, value: Optional[str]) -> None:
        self.__icon = value

    @property
    def text(self) -> Union[str, list[str], None]:
        return self.__text

    @text.setter
    def text(self, value: Union[str, list[str], None]) -> None:
        self.__text = value


@XRSingleton()
class XRTooltipManager(XRSingletonType):
    """
    XRTooltipManager:

    Collection of all  tooltip settings
    """

    def __init__(self):
        self.__tooltips = {}

    def define_tooltip(self, tooltip_name: str, tooltip: XRTooltip) -> None:
        """
        Set a tooltip by name.
        """

        self.__tooltips[tooltip_name] = tooltip

    def get_tooltip(self, tooltip_name: str) -> XRTooltip:
        """
        Get tooltip by name.
        """

        return self.__tooltips[tooltip_name]
