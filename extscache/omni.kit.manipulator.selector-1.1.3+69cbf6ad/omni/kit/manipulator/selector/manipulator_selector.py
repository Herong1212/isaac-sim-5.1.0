# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Set

from carb.eventdispatcher import get_eventdispatcher
import carb.settings
import omni.usd
from pxr import Sdf

if TYPE_CHECKING:
    from .manipulator_base import ManipulatorBase, ManipulatorOrderManager


class ManipulatorSelector:
    """
    Manages the selection and ordering of manipulators in a USD context. It will auto
    enable/disable each prim manipulator when selection changed.
    """
    def __init__(self, order_manager: ManipulatorOrderManager, usd_context_name: str):
        """
        Initialize the ManipulatorSelector.

        Args:
            order_manager (:obj:'ManipulatorOrderManager'): Manager for manipulator orders.
            usd_context_name (str): Name of the USD context.
        """
        self._order_manager = order_manager

        self._usd_context_name = usd_context_name
        self._manipulators: Dict[str, Set[ManipulatorBase]] = {}
        self._usd_context = omni.usd.get_context(usd_context_name)

        self._stage_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.manipulator.selector:manipulator_selector",
            event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED),
            on_event=lambda _: self._on_selection_changed()
        )

        self._order_sub = self._order_manager.subscribe_to_orders_changed(self._on_orders_changed)
        self._refresh()

    def destroy(self):
        """ Clean up resources used by the ManipulatorSelector."""
        self._stage_event_sub = None
        if self._order_sub:
            self._order_manager.unsubscribe_to_orders_changed(self._order_sub)
            self._order_sub = None

    def __del__(self):
        self.destroy()

    def register_manipulator_instance(self, name: str, manipulator: ManipulatorBase):
        """
        Register a prim manipulator instance.

        Args:
            name (str): Name of the manipulator.
            manipulator (:obj:'ManipulatorBase'): Manipulator instance.
        """
        needs_sort = False
        if name not in self._manipulators:
            self._manipulators[name] = set()
            needs_sort = True

        self._manipulators[name].add(manipulator)

        if needs_sort:
            self._sort()

        self._refresh()

    def unregister_manipulator_instance(self, name: str, manipulator: ManipulatorBase):
        """
        Unregister a manipulator instance.

        Args:
            name (str): Name of the manipulator.
            manipulator (:obj:'ManipulatorBase'): Manipulator instance.
        """
        manipulator_set = self._manipulators.get(name, set())
        manipulator_set.remove(manipulator)

        self._refresh()

    def _sort(self) -> bool:
        orders_dict = self._order_manager.orders_dict

        # sort by order
        sorted_manipulators = dict(sorted(self._manipulators.items(), key=lambda item: orders_dict.get(item[0], 0)))

        # compare keys to check order difference (direct dicts compare are equal if their content is same but in
        # different order)
        if sorted_manipulators != self._manipulators or list(sorted_manipulators.keys()) != list(
            self._manipulators.keys()
        ):
            self._manipulators = sorted_manipulators
            return True
        return False

    def _refresh(self):
        if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._on_selection_changed()

    def _on_selection_changed(self):
        selection = self._usd_context.get_selection().get_selected_prim_paths(omni.usd.Selection.SourceType.USD)
        selection_all = self._usd_context.get_selection().get_selected_prim_paths(omni.usd.Selection.SourceType.ALL)
        selection_sdf = [Sdf.Path(path) for path in selection]
        for _, manipulators in self._manipulators.items():
            handled = False
            for manipulator in manipulators:
                res = None
                if hasattr(manipulator, 'support_fabric'):
                    selection_mixed_sdf = [Sdf.Path(path) for path in selection_all] if selection_sdf is not None else None
                    res = manipulator.on_selection_changed(self._usd_context.get_stage(), selection_mixed_sdf)
                else:
                    res = manipulator.on_selection_changed(self._usd_context.get_stage(), selection_sdf)
                if res:
                    manipulator.enabled = True
                    handled = True
                else:
                    manipulator.enabled = False
            if handled:
                # Set selection_sdf to None to signal subsequent manipulator the selection has been handled
                # This is different from being empty []
                selection_sdf = None

    def _on_orders_changed(self):
        if self._sort():
            self._refresh()
