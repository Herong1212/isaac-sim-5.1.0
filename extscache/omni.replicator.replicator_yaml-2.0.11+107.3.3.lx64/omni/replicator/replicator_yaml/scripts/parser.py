# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import collections.abc
import copy
import inspect
import os
import re
from typing import Dict, List

import carb
import omni.replicator.core as rep
import yaml
from yaml.composer import Composer
from yaml.constructor import Constructor
from yaml.loader import Loader
from yaml.nodes import ScalarNode
from yaml.resolver import BaseResolver

# Reserve non-replicator function name
SPECIAL_PARAM = ["with", "inputs", "property"]
LINE_PREFIX = "__line__"


class LineLoader(Loader):
    def __init__(self, stream):
        super(LineLoader, self).__init__(stream)

    def compose_node(self, parent, index):
        # the line number where the previous token has ended (plus empty lines)
        line = self.line
        node = Composer.compose_node(self, parent, index)
        node.__line__ = line + 1
        return node

    def construct_mapping(self, node, deep=False):
        node_pair_lst = node.value
        node_pair_lst_for_appending = []

        for key_node, value_node in node_pair_lst:
            shadow_key_node = ScalarNode(tag=BaseResolver.DEFAULT_SCALAR_TAG, value="__line__" + key_node.value)
            shadow_value_node = ScalarNode(tag=BaseResolver.DEFAULT_SCALAR_TAG, value=key_node.__line__)
            node_pair_lst_for_appending.append((shadow_key_node, shadow_value_node))

        node.value = node_pair_lst + node_pair_lst_for_appending
        mapping = Constructor.construct_mapping(self, node, deep=deep)
        return mapping


class ParserError(Exception):
    """Base exception for errors raised by parser"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A parser error was encountered."
        super().__init__(msg)


class Parser:
    """For parsing the input parameterization to ReplicatorYAML."""

    def __init__(self, yaml_path: str, root_dir: str = None, nucleus_server: str = "omniverse://localhost"):
        """Construct Parser. Parse input file.

        Args:
            yaml_path: File path to the yaml file.
            root_dir: Root directory to resolve relative path.
            nucleus_server: nucleus server to resolve nucleus file path. Default: omniverse://localhost
        """

        self.yaml_path = yaml_path
        if root_dir is not None:
            self.root_dir = root_dir  # Root dir to resolve relative path.
        else:
            self.root_dir = os.path.dirname(os.path.realpath(__file__))

        if nucleus_server is None:
            self.nucleus_server = "omniverse://localhost"
        else:
            self.nucleus_server = nucleus_server

        self.params = self.parse_input_yaml(yaml_path)

        self.raw_params = self.params.copy()

        if "file_root_dir" in self.params:
            self.root_dir = self.params["file_root_dir"]
            del self.params["file_root_dir"]

        self.solve_inheritance(self.params)

        if "nucleus_server" in self.params:
            self.nucleus_server = self.params["nucleus_server"]
            del self.params["nucleus_server"]

        self.resolve_path_params(self.params)

    def solve_inheritance(
        self,
        params,
        parent_file_inherited_params: List[Dict] = [],
        in_file_inherited_params: Dict = {},
        parent_to_curr_mapping={},
    ):
        """Solve the inheritance of current params.
        Args:
            params: params to resolve inheritance.
            parent_file_inherited_params: inherited params to refer to.
            in_file_inherited_params: inherited params in the current yaml file.
            parent_to_curr_mapping:
            in_file_inheritance: whether to solve in file inheritance. Only set to true when first parsed a new yaml file.
        """

        def update_nested_dict(dict1, dict2):
            """Nested update dict1 with the items in dict2"""
            for k, v in dict2.items():
                if isinstance(v, collections.abc.Mapping):
                    dict1[k] = update_nested_dict(dict1.get(k, {}), v)
                else:
                    dict1[k] = v
            return dict1

        def solve_inheritance_reference(params: Dict, inherited_params: List[Dict]):
            """Solve for inheritance if the params hold variable defined in inherited files."""
            for key, val in params.items():
                if isinstance(val, str):
                    for inherited_param in inherited_params:
                        if val in inherited_param:
                            params[key] = inherited_param[val]
                            break
                elif isinstance(val, dict):
                    solve_inheritance_reference(val, inherited_params)

        def extract_group_params(params: Dict, flatten_group_params=None):
            """Extract and flatten nested group params for easier inheritance."""
            if not flatten_group_params:
                flatten_group_params = {}

            for key, value in params.items():
                if "." in key and not key.startswith("with"):
                    continue

                # skip line number keys
                if LINE_PREFIX in key:
                    continue

                flatten_group_params[key] = value

                if isinstance(value, dict):
                    extract_group_params(value, flatten_group_params)

            return flatten_group_params

        def replace_parent_reference(parent_func_signature, parent_to_curr_group_name):
            """Replace parent function signature's reference to current group name."""
            if not parent_to_curr_group_name:
                return parent_func_signature
            replaced_func_signature = {}

            for key, val in parent_func_signature.items():
                if key.startswith("with"):
                    with_context = key.split(".")[1]
                    if with_context in parent_to_curr_group_name:
                        new_key = "with." + parent_to_curr_group_name[with_context]
                    else:
                        new_key = key
                else:
                    new_key = key

                if isinstance(val, str) and val in parent_to_curr_group_name:
                    new_val = parent_to_curr_group_name[val]
                elif isinstance(val, dict):
                    new_val = replace_parent_reference(val, parent_to_curr_group_name)
                else:
                    new_val = val

                replaced_func_signature[new_key] = new_val

            return replaced_func_signature

        if not in_file_inherited_params:
            in_file_inherited_params = extract_group_params(params)

        # Parse inherited yaml files
        if "profiles" in params and not parent_file_inherited_params:
            # Resolve profiles' relative path if needed.
            resolved_paths = []
            for profile_path in params["profiles"]["value"]:
                if not (profile_path.startswith("/") or re.match("^[a-zA-Z]:\\\\", profile_path) is not None):
                    resolved_paths.append(os.path.join(self.root_dir, profile_path))
            params["profiles"] = resolved_paths
            inherited_params = self.parse_inherited_yaml(params["profiles"])

            # Solve the inheritance for inherited params first
            parent_file_inherited_params = []
            for inherited_param in inherited_params:
                self.solve_inheritance(inherited_param)
                parent_file_inherited_params.append(extract_group_params(inherited_param))

        # Handles inheritance for params, combining func parameters.
        for group_name, func_signature in params.items():
            if isinstance(func_signature, dict):
                if "inherit" in func_signature.keys():
                    parent_group_name = func_signature["inherit"]
                    parent_to_curr_mapping[parent_group_name] = group_name

                    found_inheritance = False
                    for inherited_param in parent_file_inherited_params:
                        if parent_group_name in inherited_param:
                            found_inheritance = True
                            parent_func_signature = inherited_param[parent_group_name]

                            parent_func_signature = replace_parent_reference(
                                parent_func_signature, parent_to_curr_mapping
                            )
                            update_nested_dict(func_signature, parent_func_signature)
                            break

                    # Keep find inheritance in in_file_inherited_params
                    if not found_inheritance:
                        if parent_group_name in in_file_inherited_params:
                            found_inheritance = True
                            parent_func_signature = in_file_inherited_params[parent_group_name]

                            parent_func_signature = replace_parent_reference(
                                parent_func_signature, parent_to_curr_mapping
                            )
                            update_nested_dict(func_signature, parent_func_signature)

                    if not found_inheritance:
                        line_num = func_signature[LINE_PREFIX + "inherit"]
                        raise ParserError(
                            f"Error parsing {self.yaml_path}, line {line_num}: \n\t> {line_num}\nCannot found inheritance both from other files and in file."
                        )

                else:
                    # recursivly update the dict for the rest of the func_signature
                    self.solve_inheritance(
                        func_signature, parent_file_inherited_params, in_file_inherited_params, parent_to_curr_mapping
                    )

        # Iterate through dict values and see if the value refers to a group in inherited params.
        solve_inheritance_reference(params, parent_file_inherited_params)

        self.clear_inheritance(params)

    def resolve_path_params(self, params):
        """Resolve relative path params."""
        for key, val in params.items():
            if isinstance(val, dict):
                if "property" in val.keys():
                    if val["property"] == "nucleus_path":
                        if isinstance(val["value"], list):
                            paths = [os.path.join(self.nucleus_server, v) for v in val["value"]]
                        else:
                            paths = os.path.join(self.nucleus_server, val["value"])
                        params[key] = paths
                    elif val["property"] == "file_path":
                        if isinstance(val["value"], list):
                            paths = [os.path.join(self.root_dir, v) for v in val["value"]]
                        else:
                            paths = os.path.join(self.root_dir, val["value"])
                        params[key] = paths
                else:
                    self.resolve_path_params(val)
            else:
                continue

    def clear_inheritance(self, params):
        """Clear inheritance after solving the inheritance."""
        if "profiles" in params:
            del params["profiles"]

        for group_name, func_signature in params.items():
            if isinstance(func_signature, dict):
                if "inherit" in func_signature.keys():
                    del func_signature["inherit"]

                # delete inherited corresponding line num
                if LINE_PREFIX + "inherit" in func_signature.keys():
                    del func_signature[LINE_PREFIX + "inherit"]
                self.clear_inheritance(func_signature)

    def eval_parsed_params(self):
        params = self.params.copy()
        evaled_functions = {}
        register_function_holders = {}  # Mapping from group name to list of function holders.
        register_func_keys = []
        for group_name, func_signature in params.items():
            if isinstance(func_signature, dict):
                func_name = list(func_signature.keys())[0]
                if func_name == "randomizer.register":
                    register_func_name = list(func_signature[func_name].keys())[0]
                    register_func_signature = func_signature[func_name][register_func_name]
                    register_function_holders[register_func_name] = register_func_signature
                    # Append register func keys
                    register_func_keys.append(group_name)

        # Remove register function from params.
        for func_key in register_func_keys:
            params.pop(func_key, None)

        # Register functions
        for register_func_name, func_signatures in register_function_holders.items():
            self.register_function(register_func_name, func_signatures)

        for group_name, group_val in params.items():
            if LINE_PREFIX in group_name:
                continue
            if isinstance(group_val, list):
                evaled_vals = []
                for list_elem in group_val:
                    if isinstance(list_elem, dict) and "." in list(list_elem.keys())[0]:
                        nested_func_name = list(list_elem.keys())[0]
                        nested_func_args = list_elem[nested_func_name]
                        evaled_vals.append(
                            self._eval_rep_function(None, nested_func_name, nested_func_args, evaled_functions)
                        )
                    else:
                        evaled_vals.append(list_elem)
                evaled_functions[group_name] = evaled_vals
            elif isinstance(group_val, dict):
                func_name = list(group_val.keys())[0]
                func_args = group_val[func_name]
                line_key = LINE_PREFIX + func_name
                try:
                    func_line_num = group_val[line_key]
                    del group_val[line_key]
                except KeyError as e:
                    # func_line_num is N/A if the group is inherited
                    func_line_num = None

                self._eval_rep_function(group_name, func_name, func_args, evaled_functions, func_line_num)
            else:
                raise NotImplementedError(f"Only dict and list type will be accepted for now, but got {group_val}")

        return evaled_functions

    def parse_input_yaml(self, yaml_path):
        """Parse all input parameter files.

        Args:
            yaml_path: path to the yaml file.

        Return: Parsed content from the yaml file.
        """
        if not isinstance(yaml_path, str):
            raise ValueError(
                f"Invalid yaml_path value provided: {yaml_path} of type {type(yaml_path)}. Expected string."
            )
        if yaml_path.startswith("/") or re.match("^[a-zA-Z]:\\\\", yaml_path) is not None:
            yaml_path = yaml_path
        else:
            yaml_path = os.path.join(self.root_dir, yaml_path)

        carb.log_info("Parsing and checking input parameterization.")

        loader = LineLoader(open(yaml_path).read())
        params = loader.get_single_data()

        carb.log_info("Finishing parsing the yaml file.")

        return params

    def _eval_rep_function(self, group_name: str, func_name, func_args: dict, evaled_items, func_line_num: int = 0):
        """Evaluate replicator function given name and args, recursively."""
        if func_name.startswith("with"):
            if func_name.count(".") != 1:
                raise ParserError(
                    f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t> {func_line_num}\nwith statement found but syntax is not correct."
                )
            try:
                context = evaled_items[func_name.split(".")[1]]
            except KeyError as e:
                raise ParserError(
                    f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t> {func_line_num}\n{func_name.split('.')[1]} is not defined."
                )

            with context:
                for in_with_func_name, in_with_func_args in func_args.items():
                    if LINE_PREFIX in in_with_func_name:
                        continue
                    if "." not in in_with_func_name:  # It is a group name, not function name
                        curr_group_name = in_with_func_name
                        curr_func_name = list(in_with_func_args.keys())[0]
                        curr_func_args = in_with_func_args[curr_func_name]

                        # func_number is not present if in inherited group or custom function
                        curr_func_num = None
                        if LINE_PREFIX + in_with_func_name in func_args:
                            curr_func_num = func_args[LINE_PREFIX + in_with_func_name]

                        self._eval_rep_function(
                            curr_group_name, curr_func_name, curr_func_args, evaled_items, curr_func_num
                        )
                    else:
                        # func_number is not present if in inherited group or custom function
                        curr_func_num = None
                        if LINE_PREFIX + in_with_func_name in func_args:
                            curr_func_num = func_args[LINE_PREFIX + in_with_func_name]

                        self._eval_rep_function(None, in_with_func_name, in_with_func_args, evaled_items, curr_func_num)
        else:
            func_names = func_name.split(".")
            call_func = rep
            combined_name = call_func.__name__
            while func_names:
                func_name = func_names.pop(0)
                try:
                    call_func = getattr(call_func, func_name)
                    combined_name = inspect.getmodule(call_func).__name__ + "." + func_name
                except AttributeError as e:
                    if func_name in evaled_items:
                        call_func = getattr(evaled_items[func_name], func_names.pop(0))
                    else:
                        raise ParserError(
                            f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t > {func_line_num}\nFunction {combined_name + '.' + func_name} does not exist."
                        )

            updated_args = {}

            if func_args:  # func_args can be None
                if not isinstance(func_args, dict):
                    raise ParserError(
                        f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t> {func_line_num}\nExpected key value pairs but got {func_args}."
                    )
                for arg_name, arg_value in func_args.items():
                    if isinstance(arg_value, str) and arg_value in evaled_items:
                        arg_value = evaled_items[arg_value]
                    elif isinstance(arg_value, dict) and "." in list(arg_value.keys())[0]:
                        if len(arg_value.keys()) > 2:  # key + the special __line__ key
                            raise ParserError(
                                f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t > {func_line_num}\nExpect a nested function input as a dict for arg {arg_name} but got more than one key in dict {arg_value}."
                            )

                        nested_func_name = list(arg_value.keys())[0]
                        nested_func_args = arg_value[nested_func_name]
                        # func_number is not present if in inherited group or custom function
                        nested_func_line_num = None
                        if LINE_PREFIX + nested_func_name in func_args[arg_name]:
                            nested_func_line_num = func_args[arg_name][LINE_PREFIX + nested_func_name]

                        arg_value = self._eval_rep_function(
                            None, nested_func_name, nested_func_args, evaled_items, nested_func_line_num
                        )
                    elif isinstance(arg_value, list):
                        list_arg_values = []
                        for list_elem in arg_value:
                            if isinstance(list_elem, dict) and "." in list(list_elem.keys())[0]:
                                nested_func_name = list(list_elem.keys())[0]
                                nested_func_args = list_elem[nested_func_name]

                                # func_number is not present if in inherited group or custom function
                                nested_func_line_num = None
                                if LINE_PREFIX + nested_func_name in list_elem:
                                    nested_func_line_num = list_elem[LINE_PREFIX + nested_func_name]

                                list_arg_values.append(
                                    self._eval_rep_function(
                                        None, nested_func_name, nested_func_args, evaled_items, nested_func_line_num
                                    )
                                )
                            elif isinstance(list_elem, str) and list_elem in evaled_items:
                                list_arg_values.append(evaled_items[list_elem])
                            else:
                                list_arg_values.append(list_elem)
                        arg_value = list_arg_values

                    updated_args[arg_name] = arg_value

            # Validate the args are correct with respect the to be called function
            expected_func_signature = inspect.signature(call_func).parameters.copy()

            for arg_name in updated_args.keys():
                if LINE_PREFIX in arg_name:
                    # Special key
                    continue
                if arg_name not in expected_func_signature and "kwargs" not in expected_func_signature:
                    # func_number is not present if in inherited group or custom function
                    func_line_num = None
                    if LINE_PREFIX + arg_name in func_args:
                        func_line_num = func_args[LINE_PREFIX + arg_name]

                    raise ParserError(
                        f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t> {func_line_num}\n{combined_name} got an unexpected keyword argument {arg_name}."
                    )
                elif arg_name in expected_func_signature:
                    expected_func_signature.pop(arg_name)

            # Valid to see if the rest arguments has default value.
            for expected_arg_name, expected_arg_param in expected_func_signature.items():
                if expected_arg_param.default is expected_arg_param.empty and expected_arg_name != "kwargs":
                    raise ParserError(
                        f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t> {func_line_num}\nArg {expected_arg_name} of function {combined_name} is not an optional arg but no value is provided."
                    )

            self.delete_line_recur(updated_args)
            try:
                evaled_value = call_func(**updated_args)
            except Exception as e:
                raise ParserError(
                    f"Error parsing {self.yaml_path}, line {func_line_num}: \n\t> {func_line_num}\nError calling function {combined_name} with args {updated_args}."
                )

            if group_name:
                evaled_items[group_name] = evaled_value

            return evaled_value

    def register_function(self, function_name: str, func_signatures) -> None:
        """Special function for registering custom replicator function.

        Args:
            function_name: Function name to register
            func_signatures: list of FunctionHolder that contains all the function calls of the function_name to be registered.
        """
        # Register function has a special arg input

        input_args = {}
        group_args = {}
        all_other_args = {}

        for arg_name, arg_val in func_signatures.items():
            if arg_name == "inputs":
                for input_arg_name, input_default_arg_Val in arg_val.items():
                    if input_arg_name.startswith(LINE_PREFIX):
                        continue
                    input_args[input_arg_name] = input_default_arg_Val
            elif "." not in arg_name:  # Indicates not a function, but a group name.
                group_args[arg_name] = arg_val
            else:
                all_other_args[arg_name] = arg_val

        self.delete_line_recur(group_args)
        self.delete_line_recur(all_other_args)

        def custom_function(**kwargs):
            for arg_name in kwargs:

                if arg_name not in input_args:

                    raise ValueError(f"Input arg name {arg_name} not in {input_args.keys()}.")

            # Deep copy default args and change the value into kwargs'
            actual_args = copy.deepcopy(input_args)

            for arg_name in kwargs:
                actual_args[arg_name] = kwargs[arg_name]

            evaled_groups = actual_args

            for (
                group_name,
                group_func_signature,
            ) in group_args.items():  # Eval group first, so it can be accessed in other places

                func_name = list(group_func_signature.keys())[0]
                func_args = group_func_signature[func_name]
                self._eval_rep_function(group_name, func_name, func_args, evaled_groups)

            for func_name, func_args in all_other_args.items():
                self._eval_rep_function(None, func_name, func_args, evaled_groups)

        rep.randomizer.register(custom_function, fn_name=function_name)

    def parse_inherited_yaml(self, inherited_yaml_files: list):
        """Parse inherited yaml files."""
        if not isinstance(inherited_yaml_files, list):
            raise ValueError(f"Expecte interited yaml file to be a list of strings, but got {inherited_yaml_files}")

        inherited_params = []
        for yaml_file in inherited_yaml_files:
            with open(yaml_file, "r") as f:
                inherited_params.append(yaml.safe_load(f))

        return inherited_params

    def delete_line_recur(self, args):
        """Delete the line number key of the args recursively."""
        line_keys = []
        for key in args.keys():
            if LINE_PREFIX in key:
                line_keys.append(key)

        for line_key in line_keys:
            del args[line_key]

        for key, value in args.items():
            if isinstance(value, dict):
                self.delete_line_recur(value)


def parse(yaml_path: str, root_dir: str = None, nucleus_server: str = "omniverse://localhost"):
    """Parse input file.

    Args:
        yaml_path: File path to the yaml file.
        root_dir: Root directory to resolve relative path.
        nucleus_server: nucleus server to resolve nucleus file path. Default: omniverse://localhost
    """
    parser = Parser(yaml_path=yaml_path, root_dir=root_dir, nucleus_server=nucleus_server)
    parser.eval_parsed_params()
