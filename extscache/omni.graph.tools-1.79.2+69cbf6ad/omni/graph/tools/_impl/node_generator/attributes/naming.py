"""This file contains support for the various utilities and constants used to manage attribute naming."""

from __future__ import annotations

import keyword
import re
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from ..keys import LanguageTypeValues
from ..utils import ParseError

# ==============================================================================================================
# Namespaces for attribute types
INPUT_NS = "inputs"
OUTPUT_NS = "outputs"
STATE_NS = "state"
ALL_NS = [INPUT_NS, OUTPUT_NS, STATE_NS]


# ==============================================================================================================
# Port type enum names corresponding to the namespaces
PORT_NAMES = {
    INPUT_NS: "og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT",
    OUTPUT_NS: "og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT",
    STATE_NS: "og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE",
}


# ==============================================================================================================
# Unique identifier of attribute types (corresponds to the C++ enum value for each type)
INPUT_GROUP = "ogn::kOgnInput"
OUTPUT_GROUP = "ogn::kOgnOutput"
STATE_GROUP = "ogn::kOgnState"

# Pattern for legal attribute names, not including the applied type-namespace prefix
# - starts with a letter or underscore
# - then an arbitrary number of alphanumerics, dots, or colons (colon is namespace separator)
RE_ATTRIBUTE_NAME = re.compile("^[A-Za-z_][A-Za-z0-9_:.]*$")
ATTR_NAME_REQUIREMENT = (
    "Attribute name must be a letter or underscore followed by letters, numbers, or"
    ' the special characters "_", ":", or "."'
)

# Requirements for user-friendly names. Only quotes are prohibited as they are problematic.
RE_ATTRIBUTE_UI_NAME = re.compile("^[^'\"]*$")
ATTR_UI_NAME_REQUIREMENT = "User-friendly attribute name cannot contain a quote"

# Problematic names for attributes, due to the way the automatic interfaces are generated
CPP_KEYWORDS = [
    "alignas",
    "alignof",
    "and",
    "and_eq",
    "asm",
    "atomic_cancel",
    "atomic_commit",
    "atomic_noexcept",
    "auto",
    "bitand",
    "bitor",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "char8_t",
    "char16_t",
    "char32_t",
    "class",
    "compl",
    "concept",
    "const",
    "consteval",
    "constexpr",
    "constinit",
    "const_cast",
    "continue",
    "co_await",
    "co_return",
    "co_yield",
    "decltype",
    "default",
    "delete",
    "do",
    "double",
    "dynamic_cast",
    "else",
    "enum",
    "explicit",
    "export",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "mutable",
    "namespace",
    "new",
    "noexcept",
    "not",
    "not_eq",
    "nullptr",
    "operator",
    "or",
    "or_eq",
    "private",
    "protected",
    "public",
    "reflexpr",
    "register",
    "reinterpret_cast",
    "requires",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "static_assert",
    "static_cast",
    "struct",
    "switch",
    "synchronized",
    "template",
    "this",
    "thread_local",
    "throw",
    "true",
    "try",
    "typedef",
    "typeid",
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    "wchar_t",
    "while",
    "xor",
    "xor_eq",
]
# Keywords that can be safely used since the context provides enough information to disambiguate, though there is no
# guarantee that will always be true so still issue a warning in these cases.
SAFE_CPP_KEYWORDS = [
    "atomic_cancel",
    "atomic_commit",
    "atomic_noexcept",
    "consteval",
    "constinit",
    "reflexpr",
    "requires",
]
PYTHON_KEYWORDS = keyword.kwlist


# ==============================================================================================================
def namespace_of_group(attribute_group: str) -> str:
    """Returns the namespace for the attributes of the given type"""
    if attribute_group == INPUT_GROUP:
        return INPUT_NS
    if attribute_group == OUTPUT_GROUP:
        return OUTPUT_NS
    if attribute_group == STATE_GROUP:
        return STATE_NS
    raise ParseError(f"Attribute with unknown type {attribute_group}")


# ==============================================================================================================
def attribute_name_in_namespace(attribute_name: str, namespace: str) -> str:
    """Returns the attribute_name with the namespace prepended - ignores if it is already there

    Handles the case of nested namespaces by prepending in those cases as well. Does not look for a degenerate
    case like the named namespace nested inside of a different one (e.g. change ("a:b:c", "b") to just "b:c")
    """
    (current_namespace, current_name) = split_attribute_name(attribute_name)
    # Prepend the namespace if there is none, or if there is an unmatching one
    if current_namespace is None:
        return f"{namespace}:{current_name}"
    if current_namespace != namespace:
        return f"{namespace}:{attribute_name}"
    return attribute_name


# ==============================================================================================================
def is_input_name(attribute_name: str) -> bool:
    """Returns True if the attribute_name lives in the input attribute namespace"""
    # Input namespace always appears at the top level so it's only necessary to check the prefix
    return attribute_name.startswith(f"{INPUT_NS}:")


# ==============================================================================================================
def is_output_name(attribute_name: str) -> bool:
    """Returns True if the attribute_name lives in the output attribute namespace"""
    # Output namespace always appears at the top level so it's only necessary to check the prefix
    return attribute_name.startswith(f"{OUTPUT_NS}:") or attribute_name.startswith(f"{OUTPUT_NS}_")


# ==============================================================================================================
def is_state_name(attribute_name: str) -> bool:
    """Returns True if the attribute_name lives in the state attribute namespace"""
    # State namespace always appears at the top level so it's only necessary to check the prefix
    return attribute_name.startswith(f"{STATE_NS}:")


# ==============================================================================================================
def split_attribute_name(attribute_name: str) -> Tuple[Optional[str], str]:
    """Returns the namespace and basename extracted from the full attribute name"""
    name_information = attribute_name.split(":")
    if len(name_information) < 2:
        return (None, attribute_name)
    if len(name_information) > 2:
        return (name_information[0], ":".join(name_information[1:]))

    return tuple(name_information)


# ==============================================================================================================
def attribute_name_without_port(attribute_name: str) -> str:
    """Returns the attribute name with its port namespace removed"""
    for prefix in [f"{OUTPUT_NS}:", f"{OUTPUT_NS}_", f"{INPUT_NS}:", f"{STATE_NS}:"]:
        if attribute_name.startswith(prefix):
            return attribute_name.replace(prefix, "")

    return attribute_name


# ==============================================================================================================
def attribute_name_as_python_property(attribute_name: str) -> str:
    """
    Returns the attribute name in a form suitable for a Python property, with the namespace stripped off and
    any ":" separators changed to "_"
    """
    if attribute_name.startswith(INPUT_NS):
        raw_name = attribute_name[len(INPUT_NS) + 1 :]
    elif attribute_name.startswith(OUTPUT_NS):
        raw_name = attribute_name[len(OUTPUT_NS) + 1 :]
    elif attribute_name.startswith(STATE_NS):
        raw_name = attribute_name[len(STATE_NS) + 1 :]
    else:
        raw_name = split_attribute_name(attribute_name)[1]
    return raw_name.replace(":", "_")


# ==============================================================================================================
def check_attribute_name(attribute_name: str, language_type: LanguageTypeValues = LanguageTypeValues.CPP):
    """Returns a pair of (namespace,base_name) is the attribute name is legal

    Raises:
        ParseError: Attribute name is not legally constructed
    """
    if not is_input_name(attribute_name) and not is_output_name(attribute_name) and not is_state_name(attribute_name):
        raise ParseError(f'Attribute "{attribute_name}" is not correctly namespaced as input, output, or state')
    (actual_namespace, base_name) = split_attribute_name(attribute_name)
    if not RE_ATTRIBUTE_NAME.match(base_name):
        raise ParseError(ATTR_NAME_REQUIREMENT)

    # For now attributes named for keywords will be forbidden, though we may in the future want a way to let
    # them function with modifications (e.g. instead of db.inputs.default have db.inputs._default)
    if language_type == LanguageTypeValues.CPP and base_name in CPP_KEYWORDS:
        if base_name not in SAFE_CPP_KEYWORDS:
            raise ParseError(f"Attribute name {attribute_name} cannot be a C++ keyword ('{base_name}')")
        print(f"WARNING: Attribute {attribute_name} is a C++ keyword ('{base_name}'), which may not always be safe")
    elif language_type == LanguageTypeValues.PYTHON and base_name in PYTHON_KEYWORDS:
        raise ParseError(f"Attribute {attribute_name} cannot be a Python keyword ('{base_name}')")

    return (actual_namespace, base_name)


# ==============================================================================================================
def check_attribute_ui_name(attribute_ui_name: str):
    """Raises ParseError if the new user-friendly name was illegal, else returns the name itself"""
    if not RE_ATTRIBUTE_UI_NAME.match(attribute_ui_name):
        raise ParseError(ATTR_UI_NAME_REQUIREMENT)


# ==============================================================================================================
def assemble_attribute_type_name(
    type_name: str,
    tuple_count: int,
    array_depth: int,
    extra_info: Optional[Dict[str, Any]] = None,
):
    """Assemble a fully qualified attribute name from its constituent parts.

    Basically the reversal of split_attribute_type_name().
    This method does no validation; use management.py:validate_attribute_type_name for that

    Args:
        type_name: Base name of the attribute type
        tuple_count: Number of tuple elements in the attribute type
        array_depth: Levels of arrays in the attribute type
    """
    full_type = None
    if type_name == "union":
        full_type = list(extra_info.keys()) if extra_info else []
    else:
        full_type = type_name
        if tuple_count > 1:
            full_type += f"[{tuple_count}]"
        full_type += "[]" * array_depth
    return full_type


# ==============================================================================================================
# Results are cached to reduce overhead among similar names from different attributes and repeated calls for
# the same attributes.
@lru_cache(maxsize=100000)
def make_nice_name(raw_name: str, preserve_final_part: bool = False) -> str:
    """
    Takes a raw name and formats it for use as the corresponding nice name in the UI.

    o  (For attribute names) Standard namespaces ('inputs', 'outputs', 'state') are stripped off the front.
    o  (For attribute names) Any remaining namespaces are converted to words within the name.
    o  Underscores are converted to spaces.
    o  Mixed-case words are broken into separate words (e.g. 'primaryRGBColor' -> 'primary RGB Color').
    o  Words which are all lower-case are capitalized (e.g. 'primary' -> 'Primary').

    Args:
        raw_name: Name to be cleaned up
        preserve_final_part: If True then the portion of 'raw_name' after the last namespace is left as-is.
    """

    def _split_mixed_case(word: str) -> list[str]:
        """Split a mixed case word into individual words
        Lower-case followed by upper-case splits before first upper. E.g. 'usdPrim' -> 'usd Prim'
        Upper-case followed by lower-case splits before last upper. E.g: 'USDPrim' -> 'USD Prim'
        Combined example: abcDEFgHi -> abc DE Fg Hi
        Args:
            word: Raw word to be split
        Returns:
            List of the sub-words found within the original word
        """
        result = []
        sub_word = ""
        uppers = ""
        for c in word:
            if c.isupper():
                if not uppers and sub_word:
                    result += [sub_word]
                    sub_word = ""
                uppers += c
            else:
                if len(uppers) > 1:
                    result += [uppers[:-1]]
                sub_word += uppers[-1:] + c
                uppers = ""

        if sub_word:
            result += [sub_word]
        elif uppers:
            result += [uppers]
        return result

    # Split out namespaces
    parts = raw_name.split(":")
    # If the first namespace is one of our standard ones, get rid of it.
    if len(parts) > 1 and parts[0] in ("inputs", "outputs", "state"):
        parts = parts[1:]
    # If the user provided an explicit name then we shouldn't mess with that.
    final_part = None
    if preserve_final_part:
        final_part = parts[-1]
        parts = parts[:-1]
    parts_out = []
    for part in parts:
        words = part.replace("_", " ").split(" ")
        for word in words:
            if word.islower() or word.isupper():
                parts_out += [word]
            else:
                parts_out += _split_mixed_case(word)
    # Title-case any words which are all lower case.
    parts_out = [part.title() if part.islower() else part for part in parts_out]

    if final_part:
        parts_out += [final_part]

    return " ".join(parts_out)
