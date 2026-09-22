"""Support for validating the known runtime method overrides"""

import inspect
from collections import namedtuple
from types import NoneType

import omni.graph.core as og

# ==============================================================================================================
# Dictionary of method signatures for supported method types. The key is the name of the method, the value is a
# 2-tuple of expected return type annotation and expected argument annotations.

MethodSignature = namedtuple("MethodSignature", ["return_type", "arg_types"])

_SUPPORTED_METHOD_SIGNATURES = {
    "compute": MethodSignature(bool, [og.GraphContext, og.Node]),
    "initialize": MethodSignature(NoneType, [og.GraphContext, og.Node]),
    "release": MethodSignature(NoneType, [og.Node]),
}


# ==============================================================================================================
class MethodValidationError(Exception):
    """Exception raised for problems related to validation of method overrides in runtime node type definitions"""


# ==============================================================================================================
def supported_method_overrides() -> list[str]:
    """Returns the list of names of methods eligible to be overridden in create_node_type"""
    return list(_SUPPORTED_METHOD_SIGNATURES)


# ==============================================================================================================
def validate_method(method_name: str, method: callable) -> bool:
    """Check if the method name is supported that the method signature matches what is expected for runtime node types
    If the method has not annotations then only the argument count is validated.
    Args:
        method_name: Name of method being overridden on the node type
        method: Reference to the function supplying the method override
    Returns:
        True if the method name is on the supported list and the method signature matches, False if the method name
        is not in the supported list (with no validation performed on the signature) or the method has no type
        annotations to check.
    Raises:
        MethodValidationError: If the method name is supported and the method signature does not match the expected
    """
    if not callable(method):
        raise MethodValidationError(
            "Method overrides must be a dictionary mapping the name of the function (str) to the"
            f" callable implementation of that named function. One of the values ({method}) is not a function."
        )

    try:
        expected_signature = _SUPPORTED_METHOD_SIGNATURES[method_name]
    except KeyError:
        return False

    # Validate the return type
    signature = inspect.signature(method)
    if signature.return_annotation not in [inspect.Signature.empty, expected_signature.return_type]:
        raise MethodValidationError(
            f"Return annotation for {method_name} expected {expected_signature.return_type},"
            f" got {signature.return_annotation}"
        )

    # Validate the argument count
    expected_arg_count = len(expected_signature.arg_types)
    actual_arg_count = len(signature.parameters)
    if expected_arg_count != actual_arg_count:
        raise MethodValidationError(
            f"Method {method_name} has {actual_arg_count} arguments, {expected_arg_count} are required"
        )

    # Validate each individual argument type annotation
    for arg_num, (arg_name, arg_info) in enumerate(signature.parameters.items()):
        if arg_info.annotation not in [inspect.Signature.empty, expected_signature.arg_types[arg_num]]:
            raise MethodValidationError(
                f"Argument {arg_num} ({arg_name}) expected to be of type {expected_signature.arg_types[arg_num]}"
                f" but was found to be {arg_info.annotation}"
            )

    return True
