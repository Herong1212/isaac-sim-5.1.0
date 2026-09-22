# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
"""Parameterize classes and functions."""

# Standard Library
from argparse import ArgumentParser, _ArgumentGroup
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third Party
import yaml
from docstring_parser import parse as parse_docstring
from pydantic import ConfigDict

# NVIDIA
from nvidia.srl.abc.srl import SRL
from nvidia.srl.basics.types import PathLike
from nvidia.srl.tools.misc import get_package_path
from nvidia.srl.tools.python_helper import (
    get_function_arg_names,
    get_inner_classes,
    get_nested_dict,
)
from nvidia.srl.types.base import PydanticModel


class Parameterize(SRL):
    """Base class that provides parameter functionality with Pydantic.

    Parameter precedence:
    - Command line option
    - Class initialization argument
    - Class initialization param file argument
    - Class default param file
    - Class default param value
    """

    # The path to the default params file. This path should be relative to the Python package's root
    # directory (note: not the repo's root directory, or an absolute path). This is because it is
    # expected that the default params file will be installed with the package.
    DEFAULT_PARAMS_FILE_PATH: Optional[PathLike] = None
    # The root dictionary in the params file that should have the values to initialize this set of
    # parameters.
    DEFAULT_PARAMS_DICT_ROOT: Optional[List[str]] = None

    class Params(PydanticModel):
        """Base parameter data class.

        Note:
            All child classes of `Parameterize` should have a subclass (nominally named `Params`)
            that inherits from this class.
        """

        model_config = ConfigDict(extra="allow")

    class ParamsClassCountError(Exception):
        """Exception that is thrown when the class has the incorrect number `Params` subclass."""

        def __init__(self, count: int):
            """Initialize a new `ParamsClassCountError` object.

            Args:
                count: Number of `Parameterize.Params` subclasses found.
            """
            msg = (
                "Incorrect number of `Parameterize.Params` subclasses found in"
                f" `{self.__class__.__name__}`.{count} found."
            )
            super().__init__(msg)

    def __init__(
        self,
        params_file_path: Optional[PathLike] = None,
        params_dict_root: Optional[List[str]] = None,
        params_use_defaults: bool = False,
        **kwargs: Any,
    ):
        """Initialize a new `Parametrize` object.

        Args:
            params_file_path: Path to parameter file. The parameters in this file have higher
                precedence than the parameters in default parameter file and the default class
                parameter values, but have less precedence than parameters pass as class
                initialization arguments and as command line options.
            params_dict_root: This specifies the root dictionary to use within the parameter file.
                It is specified as a list of dict keys, with the outer most key listed first.
            params_use_defaults: If true, the class default parameter values will be used, otherwise
                the parameters in the provided or default params file will be used.
        """
        # Extract out keyword arguments for params and SRL parent class
        params_keys = self.Params.model_fields.keys()
        params_kwargs = {key: kwargs.get(key) for key in params_keys if kwargs.get(key) is not None}

        # Check if the class defines a `Params` class, if so make sure it is only one, then set the
        # `params` attribute
        params_classes = get_inner_classes(self.__class__, Parameterize.Params)
        if len(params_classes) > 1:
            raise Parameterize.ParamsClassCountError(len(params_classes))

        if len(params_classes) == 1:
            # Get params from the params file
            params_from_file = {}
            if not params_use_defaults:
                params_from_file = self._get_params_from_file(
                    params_file_path=params_file_path, params_dict_root=params_dict_root
                )

            # Combine params from the file and the params provided as keyword arguments together,
            # with keyword arguments taking precedence.
            params = {**params_from_file, **params_kwargs}

            # Initialize `params` attribute
            params_cls = params_classes[0]
            self.params = params_cls(**params)

        # Extract out keyword arguments for SRL parent class
        srl_keys = get_function_arg_names(SRL.__init__)
        srl_kwargs = {key: kwargs.get(key) for key in srl_keys if kwargs.get(key) is not None}

        # Initialize SRL parent class
        super().__init__(**srl_kwargs)  # type: ignore

    @classmethod
    def _get_default_params_file_path(cls) -> Optional[Path]:
        params_file_path = None
        if cls.DEFAULT_PARAMS_FILE_PATH is None:
            return None

        if Path(cls.DEFAULT_PARAMS_FILE_PATH).is_absolute():
            params_file_path = Path(cls.DEFAULT_PARAMS_FILE_PATH)
        else:
            module_name = cls.__module__
            if "." in module_name:
                package_name = ".".join(module_name.split(".")[0:-1])
                pkg_path = get_package_path(package_name)
                params_file_path = pkg_path / cls.DEFAULT_PARAMS_FILE_PATH
            else:
                params_file_path = Path.cwd() / cls.DEFAULT_PARAMS_FILE_PATH

        if not params_file_path.exists():
            raise FileNotFoundError(f"File not found: {params_file_path}")

        return params_file_path

    def _get_params_from_file(
        self,
        params_file_path: Optional[PathLike] = None,
        params_dict_root: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if params_file_path is None:
            params_file_path = self._get_default_params_file_path()
        if params_file_path is None:
            return {}

        with open(params_file_path) as file:
            params = yaml.safe_load(file)
        if params_dict_root is None:
            params_dict_root = self.DEFAULT_PARAMS_DICT_ROOT
        if params_dict_root is not None:
            params = get_nested_dict(params, params_dict_root)

        return params

    @classmethod
    def add_argparse_args(
        cls, parser: ArgumentParser | _ArgumentGroup
    ) -> ArgumentParser | _ArgumentGroup:
        """Add class parameters as args to the given argparse parser."""
        # Get Params subclass
        params_classes = get_inner_classes(cls, Parameterize.Params)
        if len(params_classes) > 1 or len(params_classes) == 0:
            raise Parameterize.ParamsClassCountError(len(params_classes))
        params_class = params_classes[0]
        model_fields = params_class.model_fields  # type: ignore

        # Parse docstrings
        if params_class.__doc__ is not None:
            docstring = parse_docstring(params_class.__doc__)
            for param in docstring.params:
                if param.arg_name in model_fields.keys():
                    model_fields[param.arg_name].description = param.description

        # Add argument to parser
        for field_name, field_info in model_fields.items():
            field_name_snakecase = field_name.replace("_", "-")
            parser.add_argument(
                f"--{field_name_snakecase}", type=field_info.annotation, help=field_info.description
            )
        return parser
