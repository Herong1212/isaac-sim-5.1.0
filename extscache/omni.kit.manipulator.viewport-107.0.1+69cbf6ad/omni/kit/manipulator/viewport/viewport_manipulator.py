# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import inspect
from typing import Type

import carb


class ViewportManipulator:
    """
    ViewportManipulator is a generic wrapper class on top of normal Manipulator Object. It contains all "instances" of the
    Manipulators exist in each Viewports.

    When setting an attribute to the ViewportManipulator Object, it forwards the value to all instances.

    Do NOT initialize ViewportManipulator directly. Instead using ManipulatorFactory.create_manipulator(...) instead.
    It adds the functionality to automatically track viewport and create or destory "instance" of Manipulator into
    ViewportManipulator.
    """

    def __init__(self, manipulator_class: Type, **kwargs):
        self._manipulator_class = manipulator_class

        self._properties = {}
        signature = inspect.signature(manipulator_class.__init__)
        for arg, val in signature.parameters.items():
            if val.default is not inspect.Parameter.empty:
                self._properties[arg] = val.default

        self._properties.update(kwargs)

        for k, v in self._properties.items():
            setattr(self, k, v)

        self._instances = []

    def add_instance(self, instance):
        for k, v in self._properties.items():
            if hasattr(instance, k):
                setattr(instance, k, getattr(self, k))
            else:
                carb.log_verbose(f"{k} is not an attribute of {type(instance)}")

        self._instances.append(instance)

    def get_all_instances(self):
        return self._instances

    def clear_all_instances(self):
        self._instances.clear()

    @property
    def manipulator_class(self):
        return self._manipulator_class

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if hasattr(self, "_instances"):
            for instance in self._instances:
                if hasattr(instance, name):
                    setattr(instance, name, value)
                else:
                    carb.log_verbose(f"{name} is not an attribute of {type(instance)}")
