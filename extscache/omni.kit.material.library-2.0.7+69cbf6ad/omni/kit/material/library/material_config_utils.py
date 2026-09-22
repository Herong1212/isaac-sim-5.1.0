__all__ = []

import os
import pathlib
import copy

import toml

import carb
import carb.settings
import carb.tokens


SETTING_SEARCHPATHS_CUSTOM = "/materialConfig/searchPaths/custom"
SETTING_BUILTINALLOWLIST = "/materialConfig/materialGraph/builtInAllowList"
SETTING_BUILTINBLOCKLIST = "/materialConfig/materialGraph/builtInBlockList"
SETTING_USERALLOWLIST = "/materialConfig/materialGraph/userAllowList"
SETTING_USERBLOCKLIST = "/materialConfig/materialGraph/userBlockList"


def _key_value_to_dict(key, value):
    # "/path/to/key", <value> -> {"path": {"to": {"key": <value>}}}
    tokens = key.split('/')
    tokens = list(filter(None, tokens))  # filter empty strings

    dct = value
    for token in reversed(tokens):
        dct = {token: dct}

    return dct


def _merge_dict(dict1, dict2, overwrite_value=False):
    merged = copy.deepcopy(dict1)
    for k2, v2 in dict2.items():
        v1 = merged.get(k2)
        if isinstance(v1, dict) and isinstance(v2, dict):
            merged[k2] = _merge_dict(v1, v2, overwrite_value)
        elif isinstance(v1, (list, tuple)) and isinstance(v2, (list, tuple)):
            if overwrite_value:
                merged[k2] = v2
            else:
                merged[k2] = list(dict.fromkeys((list(v1) + list(v2))))  # dict for removing duplicates
        else:
            merged[k2] = copy.deepcopy(v2)

    return merged


def _get_default_config():
    # expose only settings used by user
    config = {
        "options": {
            "noStandardPath": False
        },
        "searchPaths": {
            "custom": []
        },
        "materialGraph": {
            "userAllowList": [],
            "userBlockList": []
        }
    }

    return config


def get_default_config_file_path():
    try:
        shared_dir = carb.tokens.get_tokens_interface().resolve("${shared_documents}")
    except Exception as e:
        carb.log_error(str(e))
        return ""

    config_file_path = pathlib.Path(shared_dir) / "material.config.toml"
    config_file_path = config_file_path.as_posix()

    return str(config_file_path)


def get_config_file_path():
    settings = carb.settings.get_settings()
    file_path = settings.get('/materialConfig/configFilePath')
    
    if not file_path or not os.path.exists(file_path):
        file_path = get_default_config_file_path()

    return file_path


def load_config_file(file_path):
    config = {}

    try:
        if os.path.exists(file_path):
            config = toml.load(file_path)
    except Exception as e:
        carb.log_error(str(e))

    return config


def save_config_file(config, file_path):
    if not config:
        carb.log_warn("save_config_file: no config to save")
        return False

    # this setting should not be saved in file
    config.pop("configFilePath", None)

    try:
        toml_str = toml.dumps(config)

        # least prettify format
        toml_str = toml_str.replace(",", ",\n")
        toml_str = toml_str.replace("[ ", "[\n ")

        with open(file_path, "w") as f:
            f.write(toml_str)

    except Exception as e:
        carb.log_error(str(e))
        return False

    return True


def get_config_from_carb_settings():
    try:
        default_config = _get_default_config()

        settings = carb.settings.get_settings()
        config = settings.get("/materialConfig")

        if (config is None) or (len(config) < 2):
            config = default_config
            settings.set_default("/materialConfig", config)
        else:
            config = _merge_dict(default_config, config)

    except Exception as e:
        carb.log_error(str(e))
        return {}
    
    return config


def save_carb_setting_to_config_file(carb_setting_key, config_key, is_paths=False, non_standard_path=None):
    try:
        # get value from carb setting
        settings = carb.settings.get_settings()
        value = settings.get(carb_setting_key)

        if is_paths:
            value = value.split(";") if value else []
            value = list(filter(None, value))  # remove empty strings

        # load config from file
        file_path = pathlib.Path(non_standard_path if non_standard_path else get_config_file_path())
        if not file_path.exists():
            file_path.touch()
        config = load_config_file(file_path)

        # deep merge configs
        new_config = _key_value_to_dict(config_key, value)
        merged_config = _merge_dict(config, new_config, True)

        # save config to file
        save_config_file(merged_config, file_path)

    except Exception as e:
        carb.log_error(str(e))
        return False

    return True


def save_live_config_to_file(non_standard_path=None):
    try:
        # get live material config from carb setting
        settings = carb.settings.get_settings()
        live_config = settings.get("/materialConfig")

        # save config to file
        file_path = pathlib.Path(non_standard_path if non_standard_path else get_config_file_path())
        save_config_file(live_config, file_path)
    except Exception as e:
        carb.log_error(str(e))
        return False

    return True
