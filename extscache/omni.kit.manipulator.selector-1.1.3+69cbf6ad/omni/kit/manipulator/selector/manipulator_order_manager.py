# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Callable, Dict

import carb.settings

MANIPULATOR_ORDERS_SETTING_PATH = "/persistent/exts/omni.kit.manipulator.selector/orders"


class ManipulatorOrderManager:
    """  A manager class that manages the order of prim manipulators."""
    def __init__(self):
        """ Constructor. """
        self._on_orders_changed_fns_id = 0
        self._on_orders_changed_fns: Dict[Callable] = {}
        self._settings = carb.settings.get_settings()
        self._sub = self._settings.subscribe_to_tree_change_events(
            MANIPULATOR_ORDERS_SETTING_PATH, self._on_setting_changed
        )
        self._orders_dict: Dict[str, int] = {}
        self._refresh_orders()

    def destroy(self):
        " Destroys ManipulatorOrderManager's instance."
        if self._sub:
            self._settings.unsubscribe_to_change_events(self._sub)
            self._sub = None

    def __del__(self):
        self.destroy()

    @property
    def orders_dict(self) -> Dict[str, int]:
        """
        Get the order dictionary containing the manipulator orders.

        Returns:
            Dict[str, int]: A dictionary mapping manipulators' names to their orders.
        """
        return self._orders_dict

    def subscribe_to_orders_changed(self, fn: Callable) -> int:
        """
        Subscribes a function to be called when the manipulators' orders change.

        Args:
            fn (Callable): The function to be called when the manipulators' orders change.
                The funcion's signatrue is: void fn()

        Returns:
            int: A unique identifier for the change function.
        """
        self._on_orders_changed_fns_id += 1
        self._on_orders_changed_fns[self._on_orders_changed_fns_id] = fn
        return self._on_orders_changed_fns_id

    def unsubscribe_to_orders_changed(self, id: int):
        """
        Unsubscribes a function from being called when the manipulators' orders change.

        Args:
            id (int): The unique identifier of the function to be removed.
        """
        self._on_orders_changed_fns.pop(id, None)

    def _on_setting_changed(self, tree_item, changed_item, event_type):
        self._refresh_orders()

    def _refresh_orders(self):
        self._orders_dict = self._settings.get_settings_dictionary(MANIPULATOR_ORDERS_SETTING_PATH)

        for fn in self._on_orders_changed_fns.values():
            fn()
