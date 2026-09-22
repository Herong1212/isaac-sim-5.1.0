# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from omni.ui import scene as sc
from typing import List, Sequence, Union


class SelectionShapeModel(sc.AbstractManipulatorModel):
    """A model to handle the selection region in a manipulator.

    This model manages the selection shapes such as rectangles and supports querying and
    setting their properties. It provides a way to interact with the selection shapes
    using named manipulator items and supports both integer and float values.

    Args:
        *args: Variable length argument list which will be forwarded to execute.
        **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the selection shape model with default values.

        This creates a set of manipulator items to store selection shape data.

        Args:
            *args: Variable length argument list which will be forwarded to execute.
            **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
        """
        super().__init__(*args, **kwargs)
        self.__items = {
            "ndc_start": (sc.AbstractManipulatorItem(), 2),
            "ndc_current": (sc.AbstractManipulatorItem(), 2),
            "ndc_rect": (sc.AbstractManipulatorItem(), 4),
            "mode": (sc.AbstractManipulatorItem(), 1),
            "live_update": (sc.AbstractManipulatorItem(), 1),
        }
        self.__ndc_ret_item = self.__items.get("ndc_rect")[0]
        self.__values = {item: [] for item, _ in self.__items.values()}

    def __validate_arguments(
        self, name: Union[str, sc.AbstractManipulatorItem], values: Sequence[Union[int, float]] = None
    ) -> sc.AbstractManipulatorItem:
        """Validates the arguments provided to other methods.

        Ensures that the provided name corresponds to a valid manipulator item
        and that the number of values matches the expected length.

        Args:
            name (Union[str, sc.AbstractManipulatorItem]): The name of the item or the item itself.
            values (Sequence[Union[int, float]], optional): A sequence of integers or floats to set for the item.

        Returns:
            sc.AbstractManipulatorItem: The validated manipulator item.

        Raises:
            KeyError: If the name is not recognized as an item.
            ValueError: If the number of provided values does not match the expected length.
        """
        if isinstance(name, sc.AbstractManipulatorItem):
            return name
        item, expected_len = self.__items.get(name, (None, None))
        if item is None:
            raise KeyError(f"SelectionShapeModel doesn't understand values of {name}")
        if values and len(values) != expected_len:
            raise ValueError(f"SelectionShapeModel {name} takes {expected_len} values, got {len(values)}")
        return item

    def get_item(self, name: str) -> sc.AbstractManipulatorItem():
        """Retrieves the manipulator item associated with the given name.

        Args:
            name (str): The name of the item to retrieve.

        Returns:
            sc.AbstractManipulatorItem: The corresponding manipulator item.
        """
        return self.__items.get(name, (None, None))[0]

    def set_ints(self, name: str, values: Sequence[int]):
        """Sets a sequence of integers for the specified item.

        Args:
            name (str): The name of the item to update.
            values (Sequence[int]): A sequence of integers to set for the item.
        """
        item = self.__validate_arguments(name, values)
        self.__values[item] = values

    def set_floats(self, name: str, values: Sequence[int]):
        """Sets a sequence of floats for the specified item.

        Args:
            name (str): The name of the item to update.
            values (Sequence[int]): A sequence of floats to set for the item.
        """
        item = self.__validate_arguments(name, values)
        self.__values[item] = values

    def get_as_ints(self, name: str) -> List[int]:
        """Gets the value of the specified item as a sequence of integers.

        Args:
            name (str): The name of the item to retrieve the value from.

        Returns:
            List[int]: The values of the item as a list of integers.
        """
        item = self.__validate_arguments(name)
        return self.__values[item]

    def get_as_floats(self, name: str) -> List[float]:
        """Gets the value of the specified item as a sequence of floats.

        If the item is 'ndc_rect', computes the rectangle's coordinates from 'ndc_start' and 'ndc_current'.

        Args:
            name (str): The name of the item to retrieve the value from.

        Returns:
            List[float]: The values of the item as a list of floats, or the computed rectangle coordinates.
        """
        item = self.__validate_arguments(name)
        if item == self.__ndc_ret_item:
            ndc_start, ndc_end = self.__values[self.get_item("ndc_start")], self.__values[self.get_item("ndc_current")]
            if not ndc_start:
                return []
            if not ndc_end:
                ndc_end = ndc_start
            min_x = min(ndc_start[0], ndc_end[0])
            max_x = max(ndc_start[0], ndc_end[0])
            min_y = min(ndc_start[1], ndc_end[1])
            max_y = max(ndc_start[1], ndc_end[1])
            return [min_x, min_y, max_x, max_y]

        return self.__values[item]
