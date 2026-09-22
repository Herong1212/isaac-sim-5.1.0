# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
"""Pydantic helper classes and functions."""

# Standard Library
from typing import Any, Dict, Optional

# Third Party
from pydantic import BaseModel


class PydanticModel(BaseModel):
    """Helper class that wraps ``Pydantic.BaseModel`` to provide pretty print functionality.

    Example:
        Here is an example `PydanticModel` with how it will look when printed out.

        .. code-block:: python

            class Foo(PydanticModel):
                a: int = 1
                b: float = 2.0
                c: str = "three"
            foo = Foo()
            print(foo)

        Output:

        .. code-block:: text

            a: 1
            b: 2.0
            c: three

        Standard Pydantic ``BaseModel`` does not support pretty printing and would look like this:

        .. code-block:: text

            a=1 b=2.0 c='three'
    """

    def _pretty_str(self, dict_obj: Optional[Dict[str, Any]] = None, indent: int = 0) -> str:
        # Start with the root object if not provided
        if dict_obj is None:
            dict_obj = self.model_dump()

        # Initialize result as a string
        result = ""
        for key, value in dict_obj.items():
            # Properly indent the key
            result += "    " * indent + f"{key}: "
            if isinstance(value, dict):  # Recursively print nested dictionaries
                result += "\n" + self._pretty_str(value, indent + 1)
            elif isinstance(value, list) and all(isinstance(x, dict) for x in value):
                result += "\n" + "\n".join(self._pretty_str(x, indent + 1) for x in value)
            else:  # For simple data types, just convert to string
                result += f"{value}\n"
        return result

    def __str__(self) -> str:
        return self._pretty_str()

    def __repr__(self) -> str:
        return self.__str__()
