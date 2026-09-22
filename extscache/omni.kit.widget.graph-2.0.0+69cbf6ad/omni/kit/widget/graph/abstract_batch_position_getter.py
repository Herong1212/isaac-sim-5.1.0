# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines an abstract base class for determining positions of graph nodes in a batch within a UI."""


__all__ = ["AbstractBatchPositionGetter"]

from typing import Any, List, Optional
import weakref
import abc
from .graph_model import GraphModel


class AbstractBatchPositionGetter(abc.ABC):
    """Helper to get the nodes to move at the same time.

    This class is designed to be subclassed to implement specific strategies for determining
    the positions of a batch of nodes in a graph UI. It uses weak references to the graph model
    to avoid circular references and potential memory leaks.

    Args:
        model (GraphModel): The graph model associated with this position getter."""

    def __init__(self, model: GraphModel):
        """Initializes the AbstractBatchPositionGetter with a given graph model."""
        self.model = model

    @property
    def model(self):
        """Gets the graph model.

        Returns:
            A weak reference to the graph model."""
        return self.__model()

    @model.setter
    def model(self, value):
        """Sets the graph model with a weak reference.

        Args:
            value (GraphModel): The graph model to set."""
        self.__model = weakref.ref(value)

    @abc.abstractmethod
    def __call__(self, drive_item: Any) -> Optional[List[Any]]:
        pass
