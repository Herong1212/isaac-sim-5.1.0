import carb
import omni.client
import isaacsim.storage.native.nucleus
from ..file_util import YamlFileUtil


class ConfigFileError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConfigFileUtil:

    @staticmethod
    def create_minimal_config_yaml(file_path, header, version, content=None):
        raw_yaml = {
            header: {
                "version": version,
            }
        }
        if content is not None:
            for k, v in content.items():
                raw_yaml[header][k] = v
        return YamlFileUtil.save_yaml(file_path, raw_yaml)

    @staticmethod
    def remove_header(raw_yaml, required_header):
        if required_header not in raw_yaml:
            carb.log_error(f"Yaml file does not contain '{required_header}' header.")
            return None
        return raw_yaml[required_header]

    @staticmethod
    def add_header(yaml_data, required_header):
        raw_yaml = {}
        raw_yaml[required_header] = yaml_data
        return raw_yaml

    @staticmethod
    def check_version(yaml_data, required_version):
        # Check if version attribute exists
        if "version" not in yaml_data:
            carb.log_error("version info is missing.")
            return False
        # Check if major version matches
        major = str(required_version).split(".")[0]
        yaml_major = str(yaml_data["version"]).split(".")[0]
        if major != yaml_major:
            carb.log_error("Invalid config file version. Version must match with the current extension version.")
            return False
        return True


class PropertyVerifyUtil:
    @staticmethod
    def verify_int_non_negative(name, value, log_error=True):
        if not (value >= 0):
            if log_error:
                carb.log_error(f"[{name}] value must be a non-negative number.")
            return False
        return True

    @staticmethod
    def verify_int_minus_one(name, value, log_error=True):
        if not (value >= -1):
            if log_error:
                carb.log_error(f"[{name}] value must be bigger than -1.")
            return False
        return True

    @staticmethod
    def verify_usd_path(name, value, log_error=True):
        if not (value.endswith(".usd") or value.endswith(".usda")):
            if log_error:
                carb.log_error(f"[{name}] value is not a valid USD file path.")
            return False
        return True

    @staticmethod
    def verify_text_path(name, value, log_error=True):
        if not value.endswith(".txt"):
            if log_error:
                carb.log_error(f"[{name}] value is not a valid TXT file path.")
            return False
        return True

    @staticmethod
    def verify_yaml_path(name, value, log_error=True):
        if not (value.endswith(".yaml") or value.endswith(".yml")):
            if log_error:
                carb.log_error(f"[{name}] value is not a valid YAML file path.")
            return False
        return True

    @staticmethod
    def verify_json_path(name, value, log_error=True):
        if not value.endswith(".json"):
            if log_error:
                carb.log_error(f"[{name}] value is not a valid JSON file path.")
            return False
        return True

    @staticmethod
    def verfiy_folder_path_exist(name, value, log_error=True):
        result, _ = omni.client.list(value)
        if result != omni.client.Result.OK:
            if log_error:
                carb.log_error(f"[{name}] value is not a valid directory.")
            return False
        return True

    @staticmethod
    def verify_path_exist(name, value, log_error=True):
        error_msg = f"[{name}] value is not a existing file path."
        try:
            result = isaacsim.storage.native.nucleus.is_file(value)
            if not result:
                if log_error:
                    carb.log_error(error_msg)
                return False
            else:
                return True
        except:
            if log_error:
                carb.log_error(error_msg)
            return False

    @staticmethod
    def verify_list(name, value, log_error=True):
        """Verify that the value is a list."""
        if not isinstance(value, list):
            if log_error:
                carb.log_error(f"[{name}] value must be a list, got {type(value)}.")
            return False

        return True
