"""
Contains the support class for managing attributes whose data is strings represented as tokens
"""

import json
from contextlib import suppress
from typing import Any, Dict, List

from ..utils import IndentedOutput, MetadataKeys, ParseError, check_token_name, to_cpp_str
from .AttributeManager import AttributeManager, CppConfiguration, CudaConfiguration
from .parsing import is_type_or_list_of_types


class TokenAttributeManager(AttributeManager):
    """Support class for attributes of type curated unique string.
    The values passed around are still strings, it is only the internal data type that is different
    from a regular string (NameToken instead of std::string)
    """

    OGN_TYPE = "token"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "token": CppConfiguration("NameToken", cast_required=False),
    }
    CUDA_CONFIGURATION = {
        "token": CudaConfiguration("NameToken", cast_required=False),
    }

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, attribute_name: str, attribute_type_name: str):
        """Initialize the token-based attribute information

        Args:
            attribute_name: Name to use for this attribute
            attribute_type_name: Unique name for this attribute type
        """
        super().__init__(attribute_name, attribute_type_name)
        self.__allowed_tokens = {}

    # --------------------------------------------------------------------------------------------------------------
    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = ["Ahsoka", "Tano"]
        if self.tuple_count > 1:
            values = [tuple(value + "x" * i for i in range(self.tuple_count)) for value in values]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def tuples_supported() -> List[int]:
        """Simple values are supported, no multiple tuples"""
        return [1]

    # --------------------------------------------------------------------------------------------------------------
    def get_allowed_tokens(self) -> Dict[str, str]:
        """Returns a dictionary of tokens allowed on this attribute type, raising a ParseError if they are not legal.
        This dictionary will be merged into the main node token dictionary, with duplicates removed. This is done
        separately from regular metadata and token parsing since it crosses both worlds with different requirements
        """
        allowed_tokens = {}
        raw_tokens = self.__allowed_tokens

        if isinstance(raw_tokens, str):
            token_list = raw_tokens.split(",")
            allowed_tokens = {check_token_name(token_name): token_name for token_name in token_list}
        elif isinstance(raw_tokens, list):
            allowed_tokens = {check_token_name(token): token for token in raw_tokens}
        elif isinstance(raw_tokens, dict):
            allowed_tokens = {check_token_name(token): value for token, value in raw_tokens.items()}
        else:
            raise ParseError(f"allowedTokens can only be a string, list, or dictionary - '{raw_tokens}'")

        return allowed_tokens

    # --------------------------------------------------------------------------------------------------------------
    def validate_default(self):
        """Check that the default is a legal value, making any implicit changes required to make it so if needed

        This has some extra functionality over the base class to handle the case where the default value was
        referencing the name of an allowed token
           "allowedTokens": {"ref": "This is a ref"},
           "default": "ref"

        Raises:
            ParseError: If the default was not a legal value
        """
        allowed_tokens = self.get_allowed_tokens()
        if allowed_tokens:

            def _check_for_token_replacement(value: str | list[str]) -> str:
                """Recursively check to replace a token name or list of names with their values"""
                if isinstance(value, list):
                    return [_check_for_token_replacement(member) for member in value]
                # allowed_tokens could be a string or a dictionary so both failures are caught
                with suppress(KeyError, TypeError):
                    return allowed_tokens[value]
                return value

            def _check_for_legal_token(value: str | list[str]) -> bool:
                """Recursively check that a value is one of the defined allowed tokens"""
                if isinstance(value, list):
                    return all(_check_for_legal_token(member) for member in value)
                if isinstance(allowed_tokens, str):
                    return allowed_tokens == value
                return any(value == token_value for token_value in allowed_tokens.values())

            self.default = _check_for_token_replacement(self.default)
            if not _check_for_legal_token(self.default):
                raise ParseError(
                    f"Token default '{self.default}' on {self.name} must be in the allowed set '{allowed_tokens}'"
                )

        super().validate_default()

    # --------------------------------------------------------------------------------------------------------------
    def parse_metadata(self, metadata: Dict[str, Any]):
        """Parse the metadata attached to the attribute type.
        Overrides to this method can add additional interpretation of special metadata.
        """
        super().parse_metadata(metadata)
        try:
            self.__allowed_tokens = self.metadata[MetadataKeys.ALLOWED_TOKENS]
        except KeyError:
            self.__allowed_tokens = {}
        with suppress(KeyError):
            if not self.__allowed_tokens and MetadataKeys.ALLOWED_TOKENS in metadata:
                raise ParseError(
                    f"{MetadataKeys.ALLOWED_TOKENS} can only be specified in one place, found top level "
                    f"{self.__allowed_tokens} and internal metadata definition "
                    f"{metadata[MetadataKeys.ALLOWED_TOKENS]}"
                )
            self.__allowed_tokens = metadata[MetadataKeys.ALLOWED_TOKENS]

        if self.__allowed_tokens:
            # The allowed tokens could be a dictionary, the keys of which would be lost if only the processed version
            # of the tokens was saved in the metadata so add in the raw data as well.
            self.metadata[MetadataKeys.ALLOWED_TOKENS_RAW] = json.dumps(self.__allowed_tokens)

    # --------------------------------------------------------------------------------------------------------------
    def cpp_default_initializer(self):
        """Default value setting is delayed so only set the array pointers to null if required."""
        return "nullptr, 0" if self.array_depth > 0 else None

    # --------------------------------------------------------------------------------------------------------------
    def cpp_pre_initialization(self, out: IndentedOutput):
        """If there is a default, output the code to initialize the token from the string default"""
        super().cpp_pre_initialization(out)
        if not self.default:
            return

        default_variable_name = f"{self.namespace}::{self.cpp_variable_name()}"
        refcount_variable_name = f"{self.namespace}_{self.cpp_variable_name()}_token"

        # There's a slight bit of ugliness happening here to avoid both memory leak and crash potentially caused by
        # the fact that tokens are reference counted. We have to store them locally as reference counted wrappers on
        # the raw token type, which means using a static variable to maintain the reference counts. That could be a
        # problem if the defaults are ever made editable and should be revisited in that case.
        if isinstance(self.default, list):
            out.write(f"static std::array<omni::fabric::Token, {len(self.default)}>")
            out.write(f" {refcount_variable_name} {{")
            default_strings = [to_cpp_str(value) for value in self.default]  # noqa: PLE1133
            out.write(", ".join([f"omni::fabric::Token({value})" for value in default_strings]))
            out.write("};")
            default_to_set = f"reinterpret_cast<NameToken const*>({refcount_variable_name}.data())"
            out.write(f"{default_variable_name}.setDefault({default_to_set}, {len(self.default)});")
        else:
            out.write(f"static omni::fabric::Token {refcount_variable_name} {{{to_cpp_str(self.default)}}};")
            out.write(f"{default_variable_name}.setDefault({refcount_variable_name}.asTokenC());")

    # --------------------------------------------------------------------------------------------------------------
    def cpp_element_value(self, value, remaining_depth: int = None):
        """String defaults must be quoted - use the json library to do it right"""
        return json.dumps(value) if value is not None else None

    # --------------------------------------------------------------------------------------------------------------
    def cuda_includes(self) -> List[str]:
        """Cuda cannot include iComputeGraph so it directly includes the handle definition file for token access"""
        includes = super().cuda_includes()
        includes.append("omni/graph/core/Handle.h")
        return includes

    # --------------------------------------------------------------------------------------------------------------
    def validate_value(self, value):
        """Raises a ParseError if value is not a valid string value"""
        if not is_type_or_list_of_types(value, str, self.tuple_count):
            raise ParseError(f"Value {value} on a token[{self.tuple_count}] attribute is not a matching type")
        super().validate_value(value)

    # --------------------------------------------------------------------------------------------------------------
    def python_value(self, value):
        """Token defaults must be quoted - use the json library to do it right"""
        return json.dumps(value) if value is not None else None

    # --------------------------------------------------------------------------------------------------------------
    def python_value_as_repr(self, value):
        """Returns the value of this attribute in a format that prints as something that can be assigned."""
        return json.dumps(value) if isinstance(value, str) else str(value)

    # --------------------------------------------------------------------------------------------------------------
    def python_value_as_str(self, value):
        """Returns the value of this attribute in a Python-compatible format, None for no default."""
        return str(value)

    # --------------------------------------------------------------------------------------------------------------
    def python_type_name(self):
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("str", "numpy.str")

    # --------------------------------------------------------------------------------------------------------------
    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "Token"

    # --------------------------------------------------------------------------------------------------------------
    def usd_type_name(self):
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("token")

    # --------------------------------------------------------------------------------------------------------------
    def empty_base_value(self) -> str:
        """Return the default for a token, which must include quotes"""
        return ""
