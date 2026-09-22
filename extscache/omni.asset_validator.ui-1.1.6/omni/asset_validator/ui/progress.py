# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.ui import AbstractValueModel

__all__ = ["ProgressModel"]


class ProgressModel(AbstractValueModel):
    """
    A float model to represent progress.
    """

    def __init__(self):
        super().__init__()
        self._value: int = 0

    def set_value(self, value: float) -> None:
        if int(value * 100) != int(self._value * 100):
            self._value = value
            self._value_changed()

    def get_value_as_float(self) -> float:
        return self._value

    def get_value_as_string(self) -> str:
        if self._value == 0:
            return "Computing dependencies"
        else:
            return f"{int(self._value * 100)} %"
