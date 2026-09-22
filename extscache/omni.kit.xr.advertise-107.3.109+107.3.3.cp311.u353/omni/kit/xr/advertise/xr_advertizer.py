# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import enum
import logging
from typing import Iterable

import carb
import carb.settings
import omni.ext
from omni.kit.xr.core import XRCore, XRCoreEventType
from omni.services.transport.server.zeroconf import ZeroConf

logger = logging.getLogger(__name__)


class XRAdvertizer:
    """
    XRAdvertizer
    """

    def __init__(self):
        # Subscribe to XR enable/disable events to refresh the menu so the "Save" items are properly enabled/disabled
        self.__subs = {}

        self.__subs["xr_enable_zeroconf"] = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.xr_enabled, self.startZeroconf)
        )
        self.__subs["xr_disable_zeroconf"] = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.xr_disabled, self.stopZeroconf)
        )

        # this string has to be the same both here and in the iOS and other clients; don't change it casually
        self.serviceType = "_xrstream-001._udp"
        # port doesn't actually matter at all at the moment
        self.servicePort = 8001
        self.__zeroconf = ZeroConf()
        self.__enabled = False

    def set_profile_name(self, name: str):
        self.__profile_name = name

    def get_profile_name(self) -> str:
        return self.__profile_name

    def is_enabled(self) -> bool:
        return self.__enabled

    def startZeroconf(self, ev):
        if XRCore.get_singleton().get_current_profile_name() == self.__profile_name:
            logger.debug("XRAdvertizer.startZeroconf")
            self.__zeroconf.add(self.serviceType, self.servicePort)
            self.__enabled = True

    def stopZeroconf(self, ev):
        if self.__enabled is True:
            logger.debug("XRAdvertizer.stopZeroconf")
            self.__zeroconf.remove(self.serviceType, self.servicePort)
            self.__enabled = False

    def destroy(self) -> None:
        """
        Helper function to explicitly destroy the Zeroconf manager.
        This function removes all subscriptions.
        """

        if self.__enabled is True:
            self.__zeroconf.remove(self.serviceType, self.servicePort)

        self.__subs = {}
