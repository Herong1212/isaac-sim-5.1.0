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

from typing import Any, Callable, Optional

import carb
import carb.events
import carb.settings
from pxr import Gf

# This file contains a series of event descriptions that are used
# for the event_handlers. The event handler code does check the type
# of event the user defined to be the input of the function and then
# binds a python class with that structure to the carb dictionary.

# This makes linting possible to ensure that the properties tested actually
# exist.


class XRSelectionEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__event: carb.events.IEvent = event
        self.__hand: str = event.payload["hand"]
        self.__selected_path: str = event.payload["selected_path"]
        self.__enclosing_model: str = event.payload["enclosing_model"]
        self.__hit_valid: bool = event.payload["hit_valid"]
        self.__hit_point: Gf.Vec3d = Gf.Vec3d(event.payload["hit_point"])
        self.__hit_normal: Gf.Vec3d = Gf.Vec3d(event.payload["hit_normal"])
        self.__button_changed: str = event.payload["button_changed"]

    @property
    def hand(self) -> str:
        return self.__hand

    @property
    def selected_path(self) -> str:
        return self.__selected_path

    @property
    def enclosing_model(self) -> str:
        return self.__enclosing_model

    @property
    def hit_valid(self) -> bool:
        return self.__hit_valid

    @property
    def hit_point(self) -> Gf.Vec3d:
        return self.__hit_point

    @property
    def hit_normal(self) -> Gf.Vec3d:
        return self.__hit_normal

    @property
    def button_changed(self) -> str:
        return self.__button_changed

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event

    def consume(self) -> None:
        # TODO: Need to request a way to read out consume flag
        # in carb::events. Writing it back in the payload is a
        # temp workaround
        self.__event.payload["consumed"] = True
        self.__event.consume()


class XRGuiLayerEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__gui_layer: str = event.payload["gui_layer"]
        self.__event: carb.events.IEvent = event

    @property
    def gui_layer(self) -> str:
        return self.__gui_layer

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRInputDeviceEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__input_device: str = event.payload["input_device"]
        self.__event: carb.events.IEvent = event

    @property
    def input_device(self) -> str:
        return self.__input_device

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRToolEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__tool: str = event.payload["tool"]
        self.__event: carb.events.IEvent = event

    @property
    def tool(self) -> str:
        return self.__tool

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRActionMapEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__action_map: str = event.payload["action_map"]
        self.__event: carb.events.IEvent = event

    @property
    def action_map(self) -> str:
        return self.__action_map

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRProfileEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__profile: str = event.payload["profile"]
        self.__event: carb.events.IEvent = event

    @property
    def profile(self) -> str:
        return self.__profile

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRProfileListEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__profiles: str = event.payload["profiles"]
        self.__event: carb.events.IEvent = event

    @property
    def profile(self) -> str:
        return self.__profiles

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRSystemEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__system: str = event.payload["system"]
        self.__event: carb.events.IEvent = event

    @property
    def system(self) -> str:
        return self.__system

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRSystemListEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__systems: str = event.payload["systems"]
        self.__event: carb.events.IEvent = event

    @property
    def systems(self) -> str:
        return self.__systems

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRTooltipEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__input_device: str = event.payload["input_device"]
        self.__input: str = event.payload["input"]
        self.__tooltip_button: Optional[str] = event.payload.get("tooltip_button", None)
        self.__tooltip_left: Optional[str] = event.payload.get("tooltip_left", None)
        self.__tooltip_right: Optional[str] = event.payload.get("tooltip_right", None)
        self.__tooltip_left_right: Optional[str] = event.payload.get("tooltip_left_right", None)
        self.__tooltip_up: Optional[str] = event.payload.get("tooltip_up", None)
        self.__tooltip_down: Optional[str] = event.payload.get("tooltip_down", None)
        self.__tooltip_up_down: Optional[str] = event.payload.get("tooltip_up_down", None)
        self.__event: carb.events.IEvent = event

    @property
    def input_device(self) -> str:
        return self.__input_device

    @property
    def input(self) -> str:
        return self.__input

    @property
    def tooltip_button(self) -> Optional[str]:
        return self.__tooltip_button

    @property
    def tooltip_left(self) -> Optional[str]:
        return self.__tooltip_left

    @property
    def tooltip_right(self) -> Optional[str]:
        return self.__tooltip_right

    @property
    def tooltip_left_right(self) -> Optional[str]:
        return self.__tooltip_left_right

    @property
    def tooltip_up(self) -> Optional[str]:
        return self.__tooltip_up

    @property
    def tooltip_down(self) -> Optional[str]:
        return self.__tooltip_down

    @property
    def tooltip_up_down(self) -> Optional[str]:
        return self.__tooltip_up_down

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


class XRInputDeviceGeneratorEvent:
    def __init__(self, event: carb.events.IEvent):
        self.__event_name: str = event.payload["event_name"]
        self.__event_type: str = event.payload["event_type"]
        self.__input: str = event.payload["input"]
        self.__input_device: str = event.payload["input_device"]
        self.__input_device_type: str = event.payload["input_device_type"]
        self.__dt: str = event.payload["dt"]
        self.__touch: Optional[str] = event.payload.get("touch", None)
        self.__click: Optional[str] = event.payload.get("click", None)
        self.__value: Optional[str] = event.payload.get("value", None)
        self.__x: Optional[str] = event.payload.get("x", None)
        self.__y: Optional[str] = event.payload.get("y", None)
        self.__event: carb.events.IEvent = event

    @property
    def event_name(self) -> str:
        return self.__event_name

    @property
    def event_type(self) -> str:
        return self.__event_type

    @property
    def input(self) -> str:
        return self.__input

    @property
    def input_device(self) -> str:
        return self.__input_device

    @property
    def input_device_type(self) -> str:
        return self.__input_device_type

    @property
    def dt(self) -> str:
        return self.__dt

    @property
    def touch(self) -> Optional[str]:
        return self.__touch

    @property
    def click(self) -> Optional[str]:
        return self.__click

    @property
    def value(self) -> Optional[str]:
        return self.__value

    @property
    def x(self) -> Optional[str]:
        return self.__x

    @property
    def y(self) -> Optional[str]:
        return self.__y

    @property
    def carb_event(self) -> carb.events.IEvent:
        return self.__event


def wrap_Event(event: carb.events.IEvent) -> carb.events.IEvent:
    return event


def wrap_XRGuiLayerEvent(event: carb.events.IEvent) -> XRGuiLayerEvent:
    return XRGuiLayerEvent(event)


def wrap_XRInputDeviceEvent(event: carb.events.IEvent) -> XRInputDeviceEvent:
    return XRInputDeviceEvent(event)


def wrap_XRToolEvent(event: carb.events.IEvent) -> XRToolEvent:
    return XRToolEvent(event)


def wrap_XRActionMapEvent(event: carb.events.IEvent) -> XRActionMapEvent:
    return XRActionMapEvent(event)


def wrap_XRProfileEvent(event: carb.events.IEvent) -> XRProfileEvent:
    return XRProfileEvent(event)


def wrap_XRProfileListEvent(event: carb.events.IEvent) -> XRProfileListEvent:
    return XRProfileListEvent(event)


def wrap_XRSystemEvent(event: carb.events.IEvent) -> XRSystemEvent:
    return XRSystemEvent(event)


def wrap_XRSystemListEvent(event: carb.events.IEvent) -> XRSystemListEvent:
    return XRSystemListEvent(event)


def wrap_XRInputDeviceGeneratorEvent(event: carb.events.IEvent) -> XRInputDeviceGeneratorEvent:
    return XRInputDeviceGeneratorEvent(event)


def wrap_XRTooltipEvent(event: carb.events.IEvent) -> XRTooltipEvent:
    return XRTooltipEvent(event)


def wrap_XRSelectionEvent(event: carb.events.IEvent) -> XRSelectionEvent:
    return XRSelectionEvent(event)


def get_event_wrapper(event_type) -> Callable[[carb.events.IEvent], Any]:
    """
    Wrap carb event class into a typed event
    """

    if event_type == str(XRInputDeviceGeneratorEvent):
        return wrap_XRInputDeviceGeneratorEvent
    elif event_type == str(XRGuiLayerEvent):
        return wrap_XRGuiLayerEvent
    elif event_type == str(XRInputDeviceEvent):
        return wrap_XRInputDeviceEvent
    elif event_type == str(XRToolEvent):
        return wrap_XRToolEvent
    elif event_type == str(XRActionMapEvent):
        return wrap_XRActionMapEvent
    elif event_type == str(XRProfileEvent):
        return wrap_XRProfileEvent
    elif event_type == str(XRProfileListEvent):
        return wrap_XRProfileListEvent
    elif event_type == str(XRSystemEvent):
        return wrap_XRSystemEvent
    elif event_type == str(XRSystemListEvent):
        return wrap_XRSystemListEvent
    elif event_type == str(XRTooltipEvent):
        return wrap_XRTooltipEvent
    elif event_type == str(XRSelectionEvent):
        return wrap_XRSelectionEvent
    else:
        return wrap_Event
