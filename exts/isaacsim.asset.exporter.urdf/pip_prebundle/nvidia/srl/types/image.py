# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Image related types."""

# Standard Library
from typing import Any, List, Optional, Tuple

# Third Party
import numpy as np
from pydantic import ValidationInfo, field_serializer, field_validator

# NVIDIA
from nvidia.srl.types.base import PydanticModel


class BoundingBoxData(PydanticModel):
    """2D bounding box.

    Specifies upper left corner and lower right corner of the box.
    """

    x0: float
    y0: float
    x1: float
    y1: float

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize a new `BoundingBoxData` class in different ways.

        * With four values: x0, y0, x1, y1
        * With a tuple or list of four values: (x0, y0, x1, y1)
        * With or with keyword arguments: x0=, y0=, x1=, y1=
        """
        if len(args) == 1:
            super(BoundingBoxData, self).__init__(  # type: ignore[call-arg]
                x0=args[0][0], y0=args[0][1], x1=args[0][2], y1=args[0][3]
            )
        elif len(args) == 4:
            x0, y0, x1, y1 = args[0], args[1], args[2], args[3]
            super(BoundingBoxData, self).__init__(  # type: ignore[call-arg]
                x0=x0, y0=y0, x1=x1, y1=y1
            )
        else:
            super(BoundingBoxData, self).__init__(**kwargs)

    @field_validator("x1")
    @classmethod
    def x1_greater_than_x0(cls, val: int, validation_info: ValidationInfo) -> int:
        """Validate that x0 < x1."""
        if "x0" in validation_info.data and val <= validation_info.data["x0"]:
            raise ValueError("Field `x1` must be greater than `x0`.")
        return val

    @field_validator("y1")
    @classmethod
    def y1_greater_than_y0(cls, val: int, validation_info: ValidationInfo) -> int:
        """Validate that y0 < y1."""
        if "y0" in validation_info.data and val <= validation_info.data["y0"]:
            raise ValueError("Field `y1` must be greater than `y0`")
        return val

    def as_tuple(self) -> Tuple[float, float, float, float]:
        """Return the bounding box as a tuple."""
        return (self.x0, self.y0, self.x1, self.y1)

    def as_list(self) -> List[float]:
        """Return the bounding box as a list."""
        return [self.x0, self.y0, self.x1, self.y1]


class ObjectDetectionData(PydanticModel):
    """The object detection data."""

    label: str
    bounding_box: BoundingBoxData
    confidence: Optional[float]


class SemanticSegmentationData(PydanticModel):
    """The semantic segmentation data."""

    labels: List[str]
    values: List[int]
    data: Any  # Placeholder for NumPy array validation
    scores: Optional[List[Optional[float]]] = None
    colors: Optional[List[Optional[Tuple[int, int, int]]]] = None

    @field_validator("values")
    @classmethod
    def validate_values(cls, val: Any, validation_info: ValidationInfo) -> List[int]:
        """Validate that `values` has the same length as `labels`."""
        if len(val) != len(validation_info.data["labels"]):
            raise ValueError("Field `values` must have the same length as `labels`.")
        return val

    @field_validator("data", mode="before")
    @classmethod
    def validate_data(cls, val: Any) -> np.ndarray:
        """Validate that `data` is a NumPy array with dtype int64."""
        # Ensure `data` is a NumPy array with dtype int64
        if isinstance(val, list):  # Convert list to NumPy array
            val = np.array(val, dtype=np.int64)
        if not isinstance(val, np.ndarray) or val.ndim != 2 or val.dtype != np.int64:
            raise ValueError("Field `data` must be a 2-dimensional NumPy array with dtype `int64`.")
        return val

    @field_validator("scores")
    @classmethod
    def validate_scores(cls, val: Any, validation_info: ValidationInfo) -> List[int]:
        """Validate that `scores` has the same length as `labels` if it is not None."""
        if val is not None and len(val) != len(validation_info.data["labels"]):
            raise ValueError("Field `scores` must have the same length as `labels`.")
        return val

    @field_validator("colors")
    @classmethod
    def validate_colors(cls, val: Any, validation_info: ValidationInfo) -> List[int]:
        """Validate that `colors` has the same length as `labels` if it is not None."""
        if val is not None and len(val) != len(validation_info.data["labels"]):
            raise ValueError("Field `colors` must have the same length as `labels`.")
        return val

    @field_serializer("data")
    def serialize_numpy_array(self, val: np.ndarray, _info: Any) -> List[Any]:
        """Convert ndarray to list and before serialization."""
        # NOTE (roflaherty): numpy >= 2.0.0 is known to cause mypy errors.
        return val.tolist()  # type: ignore[return-value]
