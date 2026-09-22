import contextlib
import copy
import json
import logging
import os
import re
import time
import traceback
import yaml

import carb

from ..constants import EXTENSION_NAME, VERSION

# exception utilities


def error(msg: str):
    """Raise exception with message"""
    raise Exception(f"{msg}")  # noqa


@contextlib.contextmanager
def CHECK(desc: str, log: bool = False):  # noqa
    """Logs on success, raises an error if an exception is raised"""
    try:
        yield None
        if desc:
            logging.info(f"{EXTENSION_NAME} {desc} - SUCCESS")

    except Exception as e:  # noqa
        if log:
            logging.error(f"[{EXTENSION_NAME}] {desc} - FAILURE: {traceback.format_exc()}")
        error(f"{desc}, {e}")


def ensure_type(key, _dict, expected_type):
    """Raise an error if the value is not a specified type"""
    if not isinstance(_dict[key], expected_type):
        error(f"{key} is expected to have type {expected_type} but got {type(_dict[key])}")


# make sure key exists, return retrieved value
def ensured_retrieve(key, _dict, expected_type=None):
    if key not in _dict:
        error(f'"{key}" expected but not found')
    if expected_type is not None:
        ensure_type(key, _dict, expected_type)
    return _dict[key]


def ensured_retrieve_dict(key, _dict, typed_keys):
    sub_dict = ensured_retrieve(key, _dict, dict)
    for typed_key in typed_keys:
        ensured_retrieve(typed_key, sub_dict, typed_keys[typed_key])
    return sub_dict


# return retrieved value if key exists, otherwise return default
def tentative_retrieve(key, _dict, expected_type=None, default=None):
    if key not in _dict:
        return default
    if expected_type is not None:
        ensure_type(key, _dict, expected_type)
    return _dict[key]


# indexed values

# def resolve_mapped_string(string, mapping):
#     for r in re.findall(r'\$\[.*?\]', string):
#         key = r.strip("$[]")
#         if not key in mapping:
#             error(f"xformOp value {string} has unrecognized mapping variable {key}")
#         if not isinstance(mapping[key], (int, float)):
#             error(f"a numeric value is expected for the mapping variable {key}")
#         string = string.replace(r, str(mapping[key]))
#     return string

# def resolve_mapped_value_inner(value, mapping):
#     if isinstance(value, str):
#         return eval(resolve_mapped_string(value, mapping))
#     elif isinstance(value, (float, int)):
#         return value
#     else:
#         error(f"not supported xformOp value type: {type(value)}")

# def resolve_mapped_value(value, mapping):
#     if isinstance(value, list):
#         if len(value) > 0 and isinstance(value[0], list):
#             return [[resolve_mapped_value_inner(sub_value, mapping) for sub_value in row] for row in value]
#         else:
#             return [resolve_mapped_value_inner(sub_value, mapping) for sub_value in value]
#     else:
#         return resolve_mapped_value_inner(value, mapping)

# path resolution


class MacroStringPair:
    def __init__(self, macro_string, actual_string):
        self.macro_string = macro_string
        self.actual_string = actual_string

    def __repr__(self):
        return self.actual_string

    def __str__(self):
        return self.actual_string

    def __eq__(self, string):
        if not isinstance(string, str):
            error(f"str type is expected for comparison, got {type(string)}")
        return self.actual_string == string


# for string substitution
def replace_macro(string, config):
    # find strings enclosed in ${}
    macro_format = "${{}}"
    for r in re.findall(r"\$\{.*?\}", string):
        key = r.strip(macro_format)
        # ensure_key(key, config, "configuration file")
        macro_actual_value = ensured_retrieve(key, config, str)
        if isinstance(macro_actual_value, MacroStringPair):
            macro_actual_value = macro_actual_value.macro_string  # nested macro is not supported, to avoid loop nesting
        elif not isinstance(macro_actual_value, str):
            error("macro value must be str")
        string = string.replace(r, macro_actual_value)
    return string


def get_relative_paths_of_suffix(root_folder, suffix, is_full_path=False):
    relative_paths = []
    for root, _, files in os.walk(root_folder, topdown=False):
        for file in files:
            if file.endswith(suffix):
                full_path = os.path.join(root, file)
                if is_full_path:
                    relative_paths.append(full_path)
                else:
                    relative_paths.append(os.path.relpath(full_path, root_folder))
    return relative_paths


def ensure_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def ensure_folder_recursive(path):
    child_stack = []
    while path != "/" and path != "" and not os.path.isdir(path):
        child_stack.append(os.path.basename(path))
        path = os.path.dirname(path)
    while child_stack:
        path = os.path.join(path, child_stack.pop())
        ensure_folder(path)


def resolve_string(s):
    if isinstance(s, MacroStringPair):
        return s.actual_string

    if not isinstance(s, str):
        error(f"{s} is not a str or MacroStringPair")
    return s


def resolve_mutable_name(name, is_mesh_name=True):
    splitter = "~~~"
    if splitter in name:
        if is_mesh_name:
            return name.split(splitter)[1]
        return name.split(splitter)[0]
    return name


# yaml


def read_yaml(yaml_path):
    with open(yaml_path) as yaml_file:
        return yaml.safe_load(yaml_file)


def read_description(yaml_path, exact_version=False):
    _dict = read_yaml(yaml_path)
    description = ensured_retrieve("isaacsim.replicator.object", _dict, dict)
    version = str(ensured_retrieve("version", description))
    if exact_version:
        if version != VERSION:
            error(f"incompatible version number: {version}, expecting {VERSION}")
    else:
        version_parts = version.split(".")
        expected_version_parts = VERSION.split(".")
        # Only check major version. We're okay with different minor and patch versions
        if version_parts[0] != expected_version_parts[0]:
            error(f"incompatible major version number: {version}, expecting {VERSION}")
    return description


# def read_yaml_recursive(yaml_path):
#     config = read_description(yaml_path)
#     while "parent_config" in config:
#         parent_config = read_description(f"{os.path.dirname(yaml_path)}/{config.pop('parent_config')}.yaml")
#         parent_config.update(config)
#         config = parent_config
#     return config


def write_yaml(data, yaml_path):
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)


# json


def read_json(path):
    with open(path) as infile:
        return json.load(infile)


def write_json(data, path, no_sort=None):
    with open(path, "w") as outfile:
        # sometimes we don't need to sort or indent
        if no_sort is not None and no_sort:
            json_data = json.dumps(data)
        else:
            json_data = json.dumps(data, sort_keys=True, indent=4)
        outfile.write(json_data)


# util


def disentangle(d):
    for key, value in d.items():
        d[key] = copy.deepcopy(value)


def to_array(mat):
    """For use converting numpy array/matrix to native python array/matrix"""
    return [[i for i in row] for row in mat]  # noqa


def get_base_name(path):
    return os.path.basename(path).split(".")[0]


def get_path_with_token(path):
    return carb.tokens.get_tokens_interface().resolve(path)


def get_tmp_dir():
    return get_path_with_token("${temp}")


default_log = f'{get_path_with_token("${cache}")}/isaacsim.replicator.object_debug_log.txt'


def CLEAR(path=default_log):  # noqa
    with open(path, "w") as _:
        pass


def LOG(*args, path=default_log):  # noqa
    with open(path, "a") as f:
        print(*args, file=f)


def global_message(msg):
    msg = f"{EXTENSION_NAME}: {msg}"
    print(msg)
    LOG(msg)
    logging.info(msg)


_timer = {"curr_time": 0.0, "elapsed_time": 0.0}


def timer_init():
    # global _timer
    _timer["curr_time"] = time.perf_counter()
    global_message(f"[METROPERF]: initial time {_timer['curr_time']}")


def timer(msg=""):
    # global _timer
    t = time.time()
    dt = t - _timer["curr_time"]
    _timer["curr_time"] = t
    _timer["elapsed_time"] += dt
    global_message(f"[METROPERF]: {msg}, elapsed time {_timer['elapsed_time']}, last duration {dt}")


@contextlib.contextmanager
def P(msg=""):  # noqa
    t = time.perf_counter()
    yield None
    global_message(f"{msg}: {time.perf_counter() - t:.3f}s")


@contextlib.contextmanager
def PROFILE(desc="[oro]"):  # noqa
    desc = "[oro] " + desc
    index = abs(hash(desc))
    carb.profiler.begin(index, desc)
    yield None
    carb.profiler.end(index)
