import io
import json
from pathlib import PurePosixPath
from enum import IntFlag
from pxr import Gf, UsdGeom, Sdf
import carb
import omni.client
import omni.ext
import omni.kit.app
import yaml
import numpy as np
import os
from typing import Optional, Callable, Dict, Union
from pathlib import Path
import base64
from PIL import Image


class FileUtil:
    @staticmethod
    def get_parent_path(file_path):
        url = omni.client.break_url(file_path)
        parent_path = PurePosixPath(url.path).parent
        parent_url = omni.client.make_url(
            scheme=url.scheme,
            host=url.host,
            path=str(parent_path),
        )
        return parent_url.replace("file:/", "").replace("file:", "")

    @staticmethod
    def get_absolute_path(base_path, file_path):
        return (
            omni.client.utils.make_absolute_url_if_possible(base_path, file_path)
            .replace("file:/", "")
            .replace("file:", "")
        )

    @staticmethod
    def collect_files_in_nested_dict(
        root_folder: str,
        file_extension: str,
        subfolder_name: Optional[str] = None,
        file_name_checking_fn: Optional[Callable[[str, str], bool]] = None,
    ) -> Dict[str, Union[dict, str]]:
        """
        Collect files in a nested dictionary format from the given root folder,
        optionally filtering by subfolder name and file extension.

        Args:
            root_folder (str): The root folder path to start the search.
            file_extension (str): The file extension to filter files (e.g., ".txt").
            subfolder_name (str, optional): The name of the subfolder to filter files by. If None, collect from all subfolders.
            file_name_checking_fn (Callable[[str, str], bool], optional):
                A function that takes file name and file extension as input and
                returns True if the file should be included.

        Returns:
            Dict[str, Union[dict, str]]: A nested dictionary of files organized by matching subfolders (or all subfolders if subfolder_name is None).
        """
        result = {}

        for root, subdirs, files in os.walk(root_folder):
            # If subfolder_name is specified, skip folders that do not match
            if subfolder_name and os.path.basename(root) != subfolder_name:
                continue

            # Calculate the relative path from the root folder
            relative_path = os.path.relpath(root, root_folder)
            path_components = relative_path.split(os.sep) if relative_path != "." else []

            # Traverse the dictionary to get to the current level
            current_level = result
            for component in path_components:
                if component not in current_level:
                    current_level[component] = {}
                current_level = current_level[component]

            # Add files at the current directory level
            for file in files:
                if file.endswith(file_extension):
                    if file_name_checking_fn and not file_name_checking_fn(file, file_extension):
                        continue
                    file_path = os.path.join(root, file)
                    current_level[file] = file_path

        return result

    @staticmethod
    def delete_file(file_path):
        """
        Checks if a file exists at the target path and deletes it if it does.

        Args:
            file_path (str or Path): Path to the file to be checked and deleted.
        """
        file = Path(file_path)

        if file.exists() and file.is_file():
            try:
                file.unlink()  # Delete the file
                print(f"Deleted file: {file}")
            except Exception as e:
                print(f"error while deleting file {file}: {e}")
        else:
            print(f"File does not exist: {file}")

    @staticmethod
    def delete_folder(folder_path):
        """
        Deletes the specified folder and all its subfolders/files using pathlib.

        Args:
            folder_path (str or Path): Path to the folder to be deleted.
        """
        folder = Path(folder_path)

        if not folder.exists():
            print(f"The folder '{folder}' does not exist.")
            return

        try:
            # Recursively delete the folder and its contents
            for child in folder.iterdir():
                if child.is_dir():
                    FileUtil.delete_folder(child)  # Recursively delete subfolders
                else:
                    child.unlink()  # Delete file
            folder.rmdir()  # Delete the now-empty folder
            print(f"Deleted folder: {folder}")
        except Exception as e:
            print(f"Error while deleting {folder}: {e}")


class YamlFileUtil:
    def load_yaml(file_path):
        try:
            result, version, context = omni.client.read_file(file_path)
            if result == omni.client.Result.OK:
                carb.log_info(f"omni.client read yaml file {file_path} succeeds.")
                yaml_str = memoryview(context).tobytes().decode("utf-8")
                return yaml.safe_load(yaml_str)
            carb.log_warn(f"omni.client read yaml file {file_path} fails, result: {result}. Trying default read...")
            file = open(file_path, "r")
            yaml_data = yaml.safe_load(file)
            file.close()
            carb.log_info("Read yaml file succeeds.")
            return yaml_data
        except Exception as ex:
            carb.log_error(f"Read yaml file {file_path} fails, exception: {ex}.")
            return None

    def save_yaml(file_path, yaml_data):
        try:
            stream = io.StringIO("")
            yaml.dump(yaml_data, stream, sort_keys=False)
            result = omni.client.write_file(url=file_path, content=stream.getvalue().encode("utf-8"))
            if result == omni.client.Result.OK:
                carb.log_info(f"omni.client write yaml file {file_path} succeeds.")
                return True
            carb.log_warn(
                f"omni.client write yaml to file {file_path} fails, result: {result}. Trying default write..."
            )
            file = open(file_path, "w")
            yaml.dump(yaml_data, file, sort_keys=False)
            file.close()
            carb.log_info("Write yaml file succeeds.")
            return True
        except Exception as ex:
            carb.log_error(f"Write yaml file {file_path} fails, exception: {ex}.")
            return False


class TextFileUtil:
    @staticmethod
    def create_text_file(file_path, content_str=None):
        try:
            file = open(file_path, "w")
            file.seek(0)
            file.truncate()  # Remove previous content if it exists
            file.close()
            if content_str:
                return TextFileUtil.write_text_file(file_path, content_str)
            else:
                return True
        except IOError:
            return False

    @staticmethod
    def read_text_file(file_path):
        try:
            result, version, context = omni.client.read_file(file_path)
            if result == omni.client.Result.OK:
                carb.log_info(f"omni.client read text file {file_path} succeeds.")
                return memoryview(context).tobytes().decode("utf-8")
            carb.log_warn(f"omni.client read text file {file_path} fails, result: {result}. Trying default read...")
            file = open(file_path, "r")
            content = file.read()
            file.close()
            carb.log_info("Read text file succeeds.")
            return content
        except Exception as ex:
            carb.log_error(f"Read text file {file_path} fails, exception: {ex}.")
            return None

    @staticmethod
    def write_text_file(file_path, contentStr):
        try:
            if contentStr == None:
                carb.log_warn(f"Content is empty. Will not write to file {file_path}.")
                return False
            result = omni.client.write_file(file_path, contentStr.encode("utf-8"))
            if result == omni.client.Result.OK:
                carb.log_info(f"omni.client write text file {file_path} succeeds.")
                return True
            carb.log_warn(f"omni.client write text file {file_path} fails, result: {result}. Trying default write...")
            file = open(file_path, "w")
            file.writelines(contentStr)
            file.close()
            carb.log_info("Write text file succeeds.")
            return True
        except Exception as ex:
            carb.log_error(f"Write text file {file_path} fails, exception: {ex}.")
            return False

    @staticmethod
    def copy_text_file(source_file, target_file):
        content_str = TextFileUtil.read_text_file(source_file)
        if not TextFileUtil.create_text_file(target_file):
            return False
        return TextFileUtil.write_text_file(target_file, content_str)


class JSONFileUtil:
    @staticmethod
    def load_from_file(file_path):
        try:
            result, version, context = omni.client.read_file(file_path)
            if result == omni.client.Result.OK:
                json_data = json.loads(memoryview(context).tobytes().decode("utf-8"))
                carb.log_info(f"omni.client read json file {file_path} succeeds.")
                return json_data
            carb.log_warn(f"omni.client read json file {file_path} fails, result: {result}. Trying default read...")
            file = open(file_path, "r")
            json_data = json.load(file)
            file.close()
            carb.log_info("Read json file succeeds.")
            return json_data
        except Exception as ex:
            carb.log_error(f"Read json file {file_path} fails, exception: {ex}.")
            return None

    @staticmethod
    def write_to_file(file_path, data):
        try:
            raw_data = json.dumps(data, indent="\t")
            result = omni.client.write_file(file_path, raw_data.encode("utf-8"))
            if result == omni.client.Result.OK:
                carb.log_info(f"omni.client write json file {file_path} succeeds.")
                return True
            carb.log_warn(f"omni.client write json file {file_path} fails, result: {result}. Trying default write...")
            file = open(file_path, "w")
            json.dump(data, file, indent="\t")
            file.close()
            carb.log_info("Write json file succeeds.")
            return True
        except Exception as ex:
            carb.log_error(f"Write json file {file_path} fails, exception: {ex}.")
            return False

    def convert_to_json_serializable(data):
        """
        Recursively convert data into a JSON-serializable format.
        """
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                # Convert enum keys to their names
                if isinstance(key, IntFlag):
                    key = key.name
                else:
                    key = str(key)
                new_dict[key] = JSONFileUtil.convert_to_json_serializable(value)
            return new_dict
        elif isinstance(data, list):
            return [JSONFileUtil.convert_to_json_serializable(item) for item in data]
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, Sdf.Path):
            return str(data)
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        else:
            # For any other type, try converting to string
            return str(data)

    @staticmethod
    def update_json_file(file_path, key_name, new_value):
        """
        Updates a JSON file with a new key-value pair. If the file does not exist,
        it creates a new one with the provided key and value.

        Args:
            file_path (str): Path to the JSON file.
            key_name (str): The key to add/update in the JSON file.
            new_value : The value associated with the key.

        Returns:
            None
        """
        # Check if the file exists
        if not os.path.exists(file_path):
            # Create a new JSON structure with the key and value
            data = {key_name: new_value}
        else:
            # Load existing data from the file
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    # If the file is empty or corrupted, start with an empty dict
                    data = {}

            # Update or add the new key-value pair
            data[key_name] = new_value

        # Write the updated data back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Data for '{key_name}' has been updated.")


class CommandFileUtil:
    """
    Class to hold utility functions for command file.
    Functions input includes config file path because command file can be relatvie to config file.
    """

    @staticmethod
    def load_command_file(config_file_path, command_file_path) -> list:
        command_path = FileUtil.get_absolute_path(config_file_path, command_file_path)
        commands_str = TextFileUtil.read_text_file(command_path)
        if not commands_str:
            return None
        else:
            return CommandFileUtil.parse_commands_str(commands_str)

    @staticmethod
    def save_command_file(config_file_path, command_file_path, commands_list) -> bool:
        command_path = FileUtil.get_absolute_path(config_file_path, command_file_path)
        command_str = CommandFileUtil.parse_commands_list(commands_list)
        return TextFileUtil.write_text_file(command_path, command_str)

    @staticmethod
    def parse_commands_list(commands_list: list) -> str:
        command_str = ""
        for cmd in commands_list:
            command_str += cmd
            command_str += "\n"
        return command_str

    @staticmethod
    def parse_commands_str(commands_str: str) -> list:
        return commands_str.splitlines()


class ImageFileUtil:
    """Helper functions to process Image files"""

    @staticmethod
    def load_and_encode_image(image_file_path: str) -> str | None:
        """generate base64 encoded image from image file"""
        if not os.path.isfile(image_file_path):
            carb.log_info(f"Invalid image path : {image_file_path} ")
            return None
        encoded_image = None
        with open(image_file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        # if the image fail to be encoded.
        if encoded_image is None:
            carb.log_info(f"Fail to encode image : {image_file_path} ")
            return None
        return encoded_image

    @staticmethod
    def encode_render_product_to_base64(render_product_data: np.ndarray) -> str | None:
        """
        Convert a numpy array (RGBA image from render product) into a base64-encoded image string.

        Args:
            render_product_data: A numpy array of shape (H, W, 4), RGBA format.

        Returns:
            Base64-encoded JPEG string or None if encoding fails.
        """
        if render_product_data is None:
            import carb

            carb.log_warn("Empty render product data provided for encoding.")
            return None

        try:
            # Convert RGBA to RGB and save to memory buffer
            rgb_image = Image.fromarray(render_product_data, "RGBA").convert("RGB")
            buffer = io.BytesIO()
            rgb_image.save(buffer, format="JPEG", quality=90)
            encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return encoded_image
        except Exception as e:
            import carb

            carb.log_error(f"[encode_render_product_to_base64] Failed to encode render image: {e}")
            return None
