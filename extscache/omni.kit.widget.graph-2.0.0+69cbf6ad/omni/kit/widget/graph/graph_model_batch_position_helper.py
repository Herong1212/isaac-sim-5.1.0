# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides a model to manage batch positions for items, supporting operations like multiselection, backdrop, and upstream positioning within a graphical interface."""


__all__ = ["GraphModelBatchPositionHelper"]

from .abstract_batch_position_getter import AbstractBatchPositionGetter
from typing import Any, Callable, Dict, List, Tuple, Union
import weakref


class GraphModelBatchPositionHelper:
    """A helper class for managing batch positions of graph items.

    This class is responsible for handling operations related to the positioning of multiple items as a batch within a
    graph interface. It supports functionalities such as multiselection, backdrop management, and positioning of upstream
    items. This class ensures that position-related actions are synchronized across all selected items, providing a
    consistent and expected behavior during user interactions such as dragging and editing the position of graph nodes.
    """

    def __init__(self):
        """Initializes the GraphModelBatchPositionHelper with default properties."""
        super().__init__()
        # Indicates that the method multiselection_set_position is called and
        # not finished. We need it because multiselection_set_position can be
        # called recursively
        self.__position_set_in_process = False
        # The same for multiselection_position_begin_edit
        self.__position_begin_edit_in_process = False
        # The same for multiselection_position_end_edit
        self.__position_end_edit_in_process = False

        # The node that drives position of many nodes. It's the node the user
        # actually drags.
        self.__current_drive_node = None
        # Other nodes in the selection
        self.__driven_nodes: List = []
        self.__position_difference: Dict[Any, Union[List, Tuple]] = {}

        # Functions to get the nodes that are moving
        self.__get_moving_items_fns = {}

        # Proxy is the isolation model. We need it to set the position of
        # input/output nodes.
        self.__batch_proxy = None
        self.batch_proxy = self

    @property
    def batch_proxy(self):
        """Gets the batch proxy which is used for converting calls to input/output nodes.

        Returns:
            The batch proxy object."""
        return self.__batch_proxy()

    @batch_proxy.setter
    def batch_proxy(self, value):
        """Sets a new batch proxy with weak reference to avoid circular references.

        Args:
            value: The new value for the batch proxy."""
        # Weak ref so we don't have circular references
        self.__batch_proxy = weakref.ref(value)

        for _, fn in self.__get_moving_items_fns.items():
            if isinstance(fn, AbstractBatchPositionGetter):
                fn.model = value

    def add_get_moving_items_fn(self, fn: Callable[[Any], List[Any]]):
        """Add the function that is called in batch_position_begin_edit to determine which items to move

        Args:
            fn: A callable that takes a single argument and returns a list of items to be moved."""

        def get_new_id(batch_position_fns: Dict[int, Callable]):
            if not batch_position_fns:
                return 0
            return max(batch_position_fns.keys()) + 1

        class Subscription:
            """The object that will remove the callback when destroyed"""

            def __init__(self, parent, id):
                self.__parent = weakref.ref(parent)
                self.__id = id

            def __del__(self):
                parent = self.__parent()
                if parent:
                    parent._remove_batch_position_fn(self.__id)

        id = get_new_id(self.__get_moving_items_fns)
        self.__get_moving_items_fns[id] = fn

    def _remove_get_moving_items_fn(self, id: int):
        self.__get_moving_items_fns.pop(id, None)

    def batch_set_position(self, position: List[float], item: Any = None):
        """Sets the position for all selected nodes.

        Should be called in the position setter to make sure the position setter is called for all the selected nodes.

        Args:
            position: The list of float values representing the new position.
            item: The item that is currently driving the position change, if any. Defaults to None."""

        if self.__position_set_in_process:
            return

        if self.__current_drive_node != item:
            # Somehow it's possible that batch_set_position is called for the
            # wrong node. We need to filter such cases. It happens rarely, but
            # when it happens, it leads to a crash because the node applies the
            # diff to itself infinitely.
            # TODO: investigate OM-58441 more
            return

        self.__position_set_in_process = True

        try:
            current_position = position
            if not current_position:
                # Can't do anything without knowing position
                return

            for node in self.__driven_nodes:
                diff = self.__position_difference.get(node, None)
                if diff:
                    self.batch_proxy[node].position = (
                        diff[0] + current_position[0],
                        diff[1] + current_position[1],
                    )

        # TODO: except
        finally:
            self.__position_set_in_process = False

    def batch_position_begin_edit(self, item: Any):
        """Begins a batch editing process, determining and preparing items for movement.

        Should be called from position_begin_edit to make sure position_begin_edit is called for all the selected nodes

        Args:
            item: The item for which the batch position editing is initiated."""

        def add_driven_nodes_recursive(node, visited_nodes=None):
            """
            Need a recursive function because there may be multiple backdrops selected that
            each have nodes to pull along.
            """
            if visited_nodes is None:
                visited_nodes = set()

            if node in visited_nodes:
                return []

            visited_nodes.add(node)

            driven_nodes = []
            for _, fn in self.__get_moving_items_fns.items():
                driven_nodes += fn(node) or []

            for next_node in driven_nodes:
                driven_nodes += add_driven_nodes_recursive(next_node, visited_nodes)

            return list(set(driven_nodes) - {self.__current_drive_node})

        if self.__position_begin_edit_in_process:
            return

        self.__position_begin_edit_in_process = True

        try:
            # The current node is the drive node.
            self.__current_drive_node = item
            self.__driven_nodes = add_driven_nodes_recursive(self.__current_drive_node)

            current_position = self.batch_proxy[self.__current_drive_node].position

            if not current_position:
                # Can't do anything without knowing position
                return

            for node in self.__driven_nodes:
                node_position = self.batch_proxy[node].position
                if node_position:
                    self.__position_difference[node] = (
                        node_position[0] - current_position[0],
                        node_position[1] - current_position[1],
                    )

                self.batch_proxy.position_begin_edit(node)

        # TODO: except
        finally:
            self.__position_begin_edit_in_process = False

    def batch_position_end_edit(self, item: Any):
        """Completes the batch editing process, finalizing the movement of items.

        Should be called from position_begin_edit to make sure position_begin_edit is called for all the selected nodes

        Args:
            item: The item for which the batch position editing is being completed."""

        if self.__position_end_edit_in_process:
            return

        self.__position_end_edit_in_process = True

        try:
            for node in self.__driven_nodes:
                self.batch_proxy.position_end_edit(node)

            # Clean up
            self.__driven_nodes = []
            self.__position_difference = {}
        # TODO: except
        finally:
            self.__position_end_edit_in_process = False
