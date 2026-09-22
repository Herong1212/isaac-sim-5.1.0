"""Support for validation of content"""

import inspect
from enum import Enum


# ==============================================================================================================
class _FunctionType(Enum):
    """Enumeration to make an easy tag type for function type definitions"""

    FUNCTION = "function"
    """Type is an untethered function"""
    STATIC = "staticmethod"
    """Type is a static method of a class"""
    CLASS = "classmethod"
    """Type is a class method (with cls) of a class"""
    INSTANCE = "instancemethod"
    """Type is an instance method (with self) of a class"""
    NOT_A_FUNCTION = "unknown"
    """Type is not a recognized function type"""


# ==============================================================================================================
def _get_pybind_function_type(func: any) -> _FunctionType:
    """Check to see if the object is a function type of some kind.

    The way to check if a function from a pybind interface is static or not is quite different from how you would
    check regular functions. The regular methods are instancemethod types, as expected, but the static methods are
    classified as builtin methods. The parent class is always PyCapsule so the assumption has to be made that anything
    passed in here already belongs to the interface being tested.

    Args:
        func (any): The object to inspect

    Returns:
        _FunctionType|None: The type of function @p func is or None if it is not a function
    """
    if not inspect.isroutine(func):
        return None

    function_type = type(func)
    if func.__name__ == func.__qualname__ or ".<locals>" in func.__qualname__:
        return _FunctionType.FUNCTION

    if function_type.__name__ == "builtin_function_or_method":
        return _FunctionType.STATIC

    if function_type.__name__ == "instancemethod":
        return _FunctionType.INSTANCE

    return _FunctionType.CLASS


# ==============================================================================================================
def validate_abi_interface(
    interface: any,
    instance_methods: list[str] = None,
    static_methods: list[str] = None,
    class_methods: list[str] = None,
    properties: list[str] = None,
    constants: list[tuple[str, any]] = None,
):
    """Validate an ABI interface's expected contents
    Args:
        interface (any): The interface object to validate
        instance_methods (list[str]): Names of interface members expected to be regular object functions
        static_methods (list[str]): Names of interface members expected to be static object functions
        class_methods (list[str]): Names of interface members expected to be class level functions
        properties (list[str]): Names of interface members expected to be object properties
        constants (list[str]): Names and types of interface members expected to be constant object values
    Raises:
        ValueError: if the interface was not consistent with the expected contents
    """
    # Convert members to forms easier to compare
    actual_members = {function_name for function_name in dir(interface) if not function_name.startswith("_")}
    expected_instance_method_names = set(instance_methods or [])
    expected_static_method_names = set(static_methods or [])
    expected_class_method_names = set(class_methods or [])
    expected_property_names = set(properties or [])
    expected_constant_definitions = set(constants or [])
    expected_members = (
        expected_instance_method_names.union(expected_property_names)
        .union(expected_static_method_names)
        .union(expected_class_method_names)
        .union(name for (name, _) in expected_constant_definitions)
    )
    unexpected = actual_members - expected_members
    not_found = expected_members - actual_members
    errors = []
    if unexpected:
        errors.append(f"Unexpected interface members found - {unexpected}")
    if not_found:
        errors.append(f"Expected interface members not found - {not_found}")

    def _validate_function_type(function_names: list[str], expected_type: _FunctionType):
        """Check that a list of function names have the given type, adding to 'errors' if not"""
        for function_name in function_names:
            function = getattr(interface, function_name, None)
            if not callable(function):
                errors.append(f"Expected function {function_name} was not a callable function, it was {type(function)}")
                return
            function_type = _get_pybind_function_type(function)
            if function_type != expected_type:
                errors.append(f"Expected function {function_name} to be {expected_type.value}, it was {function_type}")

    # Validate the expected functions
    _validate_function_type(expected_instance_method_names, _FunctionType.INSTANCE)
    _validate_function_type(expected_class_method_names, _FunctionType.CLASS)
    _validate_function_type(expected_static_method_names, _FunctionType.STATIC)

    # Validate the expected properties
    for property_name in expected_property_names:
        property_member = getattr(interface, property_name, None)
        if not isinstance(property_member, property):
            errors.append(f"Expected property {property_name} was not a property, it was {type(property_member)}")

    # The constants are already known to be present, now their types must be checked
    for constant_name, constant_type in expected_constant_definitions:
        constant_member = getattr(interface, constant_name, None)
        if not isinstance(constant_member, constant_type):
            errors.append(
                f"Expected constant {constant_name} to be type {constant_type}, it was {type(constant_member)}"
            )

    # Raise an exception if any errors were found
    if errors:
        formatted_errors = "\n    ".join(errors)
        raise ValueError(f"Errors with interface {interface}\n    {formatted_errors}")
