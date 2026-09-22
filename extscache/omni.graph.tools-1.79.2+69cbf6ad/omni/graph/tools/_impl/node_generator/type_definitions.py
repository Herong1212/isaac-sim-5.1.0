"""Handle the mapping of OGN types onto the various generated code types"""

import json
from contextlib import suppress
from io import TextIOWrapper
from pathlib import Path
from typing import IO, Dict, List, Tuple, Union

from .attributes.AttributeManager import CppConfiguration
from .attributes.management import get_attribute_manager_type
from .keys import NodeTypeKeys
from .utils import ParseError, is_comment


class __TypeDefinitions:
    """Use the function apply_type_definitions instead of directly instantiating this class"""

    def __init__(self, type_definitions: Union[str, IO, Dict, Path, None]):
        """Initialize the type definition maps based on a JSON definition

        Internal:
            __definitions: Dictionary of type information read from the definition description
        """
        try:
            self.__definitions = {}
            if type_definitions is None:
                pass
            elif isinstance(type_definitions, str):
                self.__definitions = json.loads(type_definitions)[NodeTypeKeys.TYPE_DEFINITIONS]
            elif isinstance(type_definitions, Dict):
                self.__definitions = type_definitions[NodeTypeKeys.TYPE_DEFINITIONS]
            elif isinstance(type_definitions, TextIOWrapper):
                self.__definitions = json.load(type_definitions)[NodeTypeKeys.TYPE_DEFINITIONS]
            elif isinstance(type_definitions, Path):
                with type_definitions.open("r") as fp:
                    self.__definitions = json.load(fp)[NodeTypeKeys.TYPE_DEFINITIONS]
            else:
                raise ParseError(f"Type definition type not handled - {type_definitions}")
        except OSError as error:
            raise ParseError(f"File error when parsing type definitions {type_definitions} - {error}") from None
        except json.decoder.JSONDecodeError as error:
            raise ParseError(f"Invalid JSON formatting in file {type_definitions} - {error}") from None

    # --------------------------------------------------------------------------------------------------------------
    def __apply_cpp_definitions(self, configuration_information: Dict[str, Tuple[str, List[str]]]):
        """Apply type definitions from the definition to the C++ types on the attribute managers

        Args:
            configuration_information: Dictionary whose keys are the names of attribute types and whose values are
            a tuple of the C++ data type name for that attribute type and a list of files to be included to use it
        """
        for attribute_type_name, attribute_type_configuration in configuration_information.items():
            # Empty configuration means leave it as-is
            if not attribute_type_configuration:
                continue

            if is_comment(attribute_type_name):
                continue

            # Take a single string to mean the type definition, with no extra includes required
            if isinstance(attribute_type_configuration, str):
                if attribute_type_configuration:
                    attribute_type_configuration = [attribute_type_configuration]
                else:
                    attribute_type_configuration = []

            attribute_manager = get_attribute_manager_type(attribute_type_name)
            if attribute_manager is None:
                raise ParseError(f"Could not find attribute manager type for configuration of {attribute_type_name}")

            # If there is a change it will have a type and include file list, else skip this one
            with suppress(AttributeError, KeyError):
                cast_type = attribute_type_configuration[0]
                include_files = [] if len(attribute_type_configuration) < 2 else attribute_type_configuration[1]
                if not isinstance(cast_type, str):
                    raise ParseError(
                        f"Cast type for attribute type {attribute_type_name} must be a string, not {cast_type}"
                    )
                if not isinstance(include_files, list):
                    raise ParseError(
                        f"Include files for attribute type {attribute_type_name} must be a list, not {include_files}"
                    )
                attribute_manager.override_cpp_configuration(cast_type, include_files, cast_required=False)
                attribute_manager.CPP_CONFIGURATION[attribute_manager.tuple_count] = CppConfiguration(
                    base_type_name=cast_type, include_files=include_files
                )

    # --------------------------------------------------------------------------------------------------------------
    def apply_definitions(self):
        """Apply any type definitions to the attribute manager to which they apply"""
        for language, configuration_information in self.__definitions.items():
            if language == "c++":
                self.__apply_cpp_definitions(configuration_information)
            elif not is_comment(language):
                raise ParseError(f"Configuration for language '{language}' is not supported")


# ==============================================================================================================
def apply_type_definitions(type_definitions: Union[str, IO, Dict, Path, None]):
    definitions = __TypeDefinitions(type_definitions)
    definitions.apply_definitions()
