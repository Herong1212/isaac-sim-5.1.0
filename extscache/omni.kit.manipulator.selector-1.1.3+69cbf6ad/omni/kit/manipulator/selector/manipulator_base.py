# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
from abc import ABC, abstractmethod
from typing import List, Union

from pxr import Sdf, Usd

from .extension import get_manipulator_selector


class ManipulatorBase(ABC):
    """
    Base class for prim manipulator that works with ManipulatorSelector.
    Instead of subscribing to UsdStageEvent for selection change, manipulator should inherit this class and implements
    all abstractmethods to support choosing between multiple types of prim manipulators based on their order and enable
    criterions.

    The order of the manipulator is specified at carb.settings path `/persistent/exts/omni.kit.manipulator.selector/orders/<name>"`
    """

    def __init__(self, name: str, usd_context_name: str):
        """
        Constructor.

        Args:
            name (str): name of the manipulator. It must match the <name> in the setting path specifies order.
            usd_context_name (str): name of the UsdContext this manipulator operates on.
        """
        self._name = name
        self._selector = get_manipulator_selector(usd_context_name)

        self._register_task = None
        self._registered = None

        # do an async registration so that the child class __init__ has a chance to finish first.
        self._delayed_register()

    def destroy(self):
        if self._register_task and not self._register_task.done():
            self._register_task.cancel()
        self._register_task = None

        if self._registered:
            self._selector.unregister_manipulator_instance(self._name, self)
            self._registered = False

    def __del__(self):
        self.destroy()

    @abstractmethod
    def on_selection_changed(self, stage: Usd.Stage, selection: Union[List[Sdf.Path], None], *args, **kwargs) -> bool:
        """
        Function called when selection changes or types of prim manipulators are added or removed.

        Args:
            stage (Usd.Stage): the usd stage of which the selection change happens. It is the same as the stage of the
                               UsdContext this manipulator works on.
            selection (Union[List[Sdf.Path], None]): the list of selected prim paths. If it is None (different from []),
                                                     it means another manipulator with higher priority has handled the
                                                     selection and this manipulator should yield.

        Return:
            True if selected prim paths can be handled by this manipulator and subsequent manipulator with higher order
            should yield.
            False if selected prim paths can not be handled. Function should always return False if `selection` is None.
        """
        raise NotImplementedError("Derived class must implement on_selection_changed")
        return False

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """
        Returns if this manipulator is enabled.
        """
        raise NotImplementedError('Derived class must implement "enabled" getter')
        return False

    @enabled.setter
    @abstractmethod
    def enabled(self, value: bool):
        """
        Sets if this manipulator is enabled. A disabled manipulator should hide itself.
        """
        raise NotImplementedError('Derived class must implement "enabled" setter')

    def _delayed_register(self):
        async def register_manipulator():
            self._selector.register_manipulator_instance(self._name, self)
            self._registered = True

        self._register_task = asyncio.ensure_future(register_manipulator())
