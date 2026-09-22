# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the BackdropGetter class to identify nodes within a specified backdrop in a graph widget."""


__all__ = ["BackdropGetter"]

from functools import lru_cache
from typing import Any, Callable, List, Optional

import carb.input

from .abstract_batch_position_getter import AbstractBatchPositionGetter
from .graph_model import GraphModel


@lru_cache()
def __get_input() -> carb.input.IInput:
    return carb.input.acquire_input_interface()


def _is_alt_down() -> bool:
    input = __get_input()
    return (
        input.get_keyboard_value(None, carb.input.KeyboardInput.LEFT_ALT)
        + input.get_keyboard_value(None, carb.input.KeyboardInput.RIGHT_ALT)
        > 0
    )


class BackdropGetter(AbstractBatchPositionGetter):
    """A class to identify nodes within a specified backdrop in a graph widget.

    Args:
        model (GraphModel): The graph model instance to work with.
        is_backdrop_fn (Callable[[Any], bool]): Function to determine if a node is a backdrop.
        graph_widget (Optional): The graph widget instance, if any."""

    def __init__(self, model: GraphModel, is_backdrop_fn: Callable[[Any], bool], graph_widget=None):
        """Initialize the BackdropGetter with the provided model and backdrop identification function."""
        super().__init__(model)
        # Callback to determine if the node is a backdrop
        self.__is_backdrop_fn = is_backdrop_fn
        self.__graph_widget = graph_widget

    def __call__(self, drive_item: Any) -> Optional[List[Any]]:
        # Get siblings and return

        MIN_OFFSET = 25  # Same value used in _create_backdrop_for_selected_nodes()

        # If user presses ALT while moving the backdrop, don't carry nodes with it.
        if _is_alt_down():
            return []

        model = self.model
        if model and self.__is_backdrop_fn(drive_item):
            position = model[drive_item].position
            size = model[drive_item].size
            if position and size:
                result = []

                for node in model.nodes:
                    node_position = model[node].position
                    if not node_position:
                        continue

                    # Add the node size offset to the extent
                    if self.__graph_widget:
                        widget = self.__graph_widget._graph_view._node_widgets[node]
                        s = (widget.computed_width, widget.computed_height)
                    else:
                        s = (0, 0)  # For backwards compatibility

                    # Check if the node is inside the backdrop
                    if (
                        node_position[0] < position[0]
                        or node_position[1] < position[1]
                        or node_position[0] + s[0] > position[0] + size[0] + MIN_OFFSET
                        or node_position[1] + s[1] > position[1] + size[1] + MIN_OFFSET
                    ):
                        continue

                    result.append(node)

                return result
