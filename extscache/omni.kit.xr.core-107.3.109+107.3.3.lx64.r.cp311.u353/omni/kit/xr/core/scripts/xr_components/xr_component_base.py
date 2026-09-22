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

import sys
import traceback
from inspect import signature
from typing import Any, Callable, Optional, Union

import carb
import carb.events
import carb.settings
import omni.kit.app

from ..xr_class_wrappers import XRCore, XRToken
from ..xr_shutdown import XRShutdown
from ..xr_weak_method import XRWeakMethod
from .xr_events import get_event_wrapper


def printXRException(exp, exc_info) -> None:
    """
    Print exception error. This function parses the exception and the
    exception information to generate output with a description of where
    python code failed, including exception description and a stack trace.
    """

    carb.log_error("===================================================================")
    carb.log_error("Python Exception: ")
    carb.log_error(str(exp))
    for line in traceback.format_exception(*exc_info):
        carb.log_error(line)
    carb.log_error("===================================================================")


# XRComponentBase is the base class of the xr pieces in python. Each component is
# expected to be enabled with and event and disabled with a different event.
# Components are automatically registering to the event bus to check when they need
# to become active.
#
# This base class deals with registering callbacks in a safe manner so self is not
# bound into the callback and registers the activation and deactivation functions.
#
# The start/destroy pair is called when the component is initialized and destroyed
# The enable/disable pair is called to activate the component and deactivate the component.


class XRComponentBase:

    def __init__(self, name: str):

        xr_core: Optional[XRCore] = XRCore.get_singleton()
        if not xr_core:
            raise Exception("Cannot find XRCore")

        self.__xr_core: XRCore = xr_core
        self.__settings = carb.settings.get_settings()
        self.__enabled = False
        self.__profile_name = self.__xr_core.get_current_profile_name()

        self.__name = name

        if self.__settings.get("/xr/persistence/enabled") is True:
            self.__persistence_prefix = "/persistent/xr"
        else:
            self.__persistence_prefix = "/xr"

        XRShutdown.assert_object_deletion_upon_shutdown(self)

    def start(self, event_name: str, enabled: bool = True) -> None:
        """ "
        This function registers callbacks that are executed when this component is
        enabled.
        """

        self.__event_name: str = event_name

        if enabled:
            self.__subscriptions = [
                self.register_message_bus_event_handler(event_name + ".enable", self.on_enable_callback),
                self.register_message_bus_event_handler(event_name + ".disable", self.on_disable_callback),
                self.register_message_bus_event_handler(event_name + ".update", self.on_update),
                self.register_message_bus_event_handler("xr_profile.change", self.on_profile_update_callback),
            ]

            try:
                self.on_start()
            except Exception as exp:
                printXRException(exp, sys.exc_info())

    def __del__(self):

        if self.__enabled is True:
            try:
                self.on_disable()
            except Exception as exp:
                printXRException(exp, sys.exc_info())

        try:
            self.on_destroy()
        except Exception as exp:
            printXRException(exp, sys.exc_info())

        self.__subscriptions = []

    def get_name(self) -> str:
        """
        Name of this component.
        """

        return self.__name

    def get_event_name(self) -> str:
        """
        Name of the event that this component is connected to
        for enable, disable and update
        """

        return self.__event_name

    def on_enable_callback(self) -> None:
        """
        Function called when component is enabled.
        """

        self.__enabled = True
        self.__profile_name = self.get_xr_core().get_current_profile_name()

        try:
            self.on_enable()
        except Exception as exp:
            printXRException(exp, sys.exc_info())

    def on_disable_callback(self) -> None:
        """
        Function called when component is disabled.
        """

        self.__enabled = False

        try:
            self.on_disable()
        except Exception as exp:
            printXRException(exp, sys.exc_info())

    def on_profile_update_callback(self) -> None:
        """
        Function called when profile is changed.
        """

        self.__profile_name = self.get_xr_core().get_current_profile_name()
        try:
            self.on_profile_update(self.__profile_name)
        except Exception as exp:
            printXRException(exp, sys.exc_info())

    def is_enabled(self) -> bool:
        """
        Check if component is enabled.
        """

        return self.__enabled

    def on_destroy(self) -> None:
        """
        This function is called when the component is destroyed.
        """

        pass

    def on_start(self) -> None:
        """
        This function is called when the component is started.
        """

        pass

    def on_enable(self) -> None:
        """
        This function is called when the component is enabled.
        """

        pass

    def on_disable(self) -> None:
        """
        This function is called when the component is disabled.
        """

        pass

    def on_update(self) -> None:
        """
        This function is called each frame when component is active
        """

        pass

    def on_profile_update(self, profile_name: str) -> None:
        """
        Update the profile
        """

        pass

    def get_xr_core(self) -> XRCore:
        """
        Convenience function for getting the XRCore singleton.

        Return:
            singleton of XRCore class
        """

        return self.__xr_core

    def get_settings(self) -> carb.settings.ISettings:
        """
        Convenience function for getting the settings singleton.
        """

        return self.__settings

    def get_persistent_profile_setting_path(self, setting_name: str) -> str:
        """
        This function returns the persistent settings path to the profile.

        Args:
            setting_name:  name of the setting

        Return:
                Settings path to location of persistent parameters
        """

        return self.__persistence_prefix + "/profile/" + self.__profile_name + "/" + setting_name

    def get_non_persistent_profile_setting_path(self, setting_name: str) -> str:
        """
        This function returns the non-persistent settings path to the profile.

        Args:
            setting_name:  name of the setting

        Return:
            Settings path to location of persistent parameters
        """

        return "/xr/profile/" + self.__profile_name + "/" + setting_name

    def get_scene_persistent_profile_setting_path(self, setting_name: str) -> str:
        """
        This function returns the scene-persistent settings path to the profile.

        Args:
            setting_name:  name of the setting

        Return:
            Settings path to location of persistent parameter
        """

        return "/xrstage/profile/" + self.__profile_name + "/" + setting_name

    def register_setting_event_handler(
        self, setting_name: str, callback: Union[Callable[..., None], Callable[..., Any]]
    ) -> carb.settings.SubscriptionId:
        """
        Register callback to an event when a setting is changed

        Args:
            setting_path:     name of the setting
            callback:         function to call

        Return:
            subscription
        """

        callback_internal = callback
        if hasattr(callback_internal, "__self__"):
            callback_internal = XRWeakMethod(callback_internal)

        return omni.kit.app.SettingChangeSubscription(setting_name, lambda *_: callback_internal())

    def register_message_bus_event_handler(
        self, event_name: str, callback: Union[Callable[..., None], Callable[..., Any]], order=0
    ) -> carb.events.ISubscription:
        """
        Register callback to an event from the message bus.

        Args:
            event_name:    name of the event
            callback:      function to call
            order:         where in the stack does the event handler need to be (default = 0)

        Return:
            subscription
        """

        message_bus = self.get_xr_core().get_message_bus()
        message_type = carb.events.type_from_string(event_name)

        has_event = False
        parameters = list(signature(callback).parameters.values())

        if len(parameters) >= 1:
            has_event = True
            event_wrapper = get_event_wrapper(str(parameters[0].annotation))

        callback_internal = callback
        if hasattr(callback_internal, "__self__"):
            callback_internal = XRWeakMethod(callback_internal)

        if has_event:

            def callback_wrapper(event) -> None:
                try:
                    callback_internal(event_wrapper(event))
                except Exception as exp:
                    printXRException(exp, sys.exc_info())

        else:

            def callback_wrapper(event) -> None:
                try:
                    callback_internal()
                except Exception as exp:
                    printXRException(exp, sys.exc_info())

        return message_bus.create_subscription_to_pop_by_type(
            message_type, callback_wrapper, name="xr_event_handler:" + event_name, order=order
        )

    def dispatch_message_bus_event(self, message_name: Union[str, XRToken], payload: Any = {}) -> None:
        """
        Dispatch a message on the event bus.

        Args:
            message_name:    name of the message
            payload:         optional dictionary with payload for the event
        """

        message_type = carb.events.type_from_string(str(message_name))
        XRCore.get_singleton().get_message_bus().dispatch(message_type, payload=payload)

    def translate_usd_name_to_event_name(self, usd_name: str) -> str:
        """
        Translate a usd name like (like /user/hand/left) into
        a form without slashes for message bus events.

        Args:
            usd_name:   name of an object

        Return:
            name in event
        """

        result = usd_name.replace("/", "_")
        if len(result) > 0 and result[0] == "_":
            result = result[1:]

        return result
