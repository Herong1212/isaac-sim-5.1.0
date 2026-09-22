"""
Contains the support class for managing attributes whose data is all types of numeric values

Exports:
    is_number
    is_number_or_list_of_numbers
    NumericAttributeManager
    values_in_range
"""

from __future__ import annotations

from typing import List, Union

from ..utils import ParseError
from .AttributeManager import AttributeManager, PropertySet
from .inf_nan import NanInfValues, repr_as_float, repr_value
from .parsing import KEY_ATTR_MAXIMUM, KEY_ATTR_MINIMUM


# ======================================================================
def is_number(value):
    """Return True if the value is a number, not including booleans"""
    if isinstance(value, float) or (isinstance(value, int) and not isinstance(value, bool)):
        return True
    return NanInfValues.as_float(value) is not None


# ======================================================================
def is_number_or_list_of_numbers(value, tuple_count: int):
    """Return True if the value is a number or a list of "tuple_count" numbers, not including booleans"""

    if tuple_count == 1:
        return is_number(value)

    if isinstance(value, (list, tuple)):
        if len(value) != tuple_count:
            return False
        return all(is_number(single_value) for single_value in value)

    return False


# ======================================================================
def _value_in_range(value, min_value: float | str | None, max_value: float | str | None):
    below_min = False
    if min_value is not None:
        if isinstance(min_value, str) and min_value.lower() == "-inf":
            below_min = isinstance(value, str) and value.lower() in ["nan", "snan"]
        elif isinstance(value, str):
            below_min = False
        else:
            below_min = value < min_value
        if below_min:
            return False

    above_max = False
    if max_value is not None:
        if isinstance(max_value, str) and max_value.lower() in ["inf", "+inf"]:
            above_max = isinstance(value, str) and value.lower() in ["nan", "snan"]
        elif isinstance(value, str):
            above_max = False
        else:
            above_max = value > max_value

    return not above_max


# ======================================================================
def values_in_range(value, min_value: float | tuple | str | None, max_value: float | tuple | str | None):
    """Return True if the value is a number or list of numbers in the range [min_value, max_value] or special values"""

    # The combinations of types for min/max range checks for value,min|max are:
    #    list|tuple, None : Ignore the restriction
    #    list|tuple, value : Confirm that every element of the list satisfies the constraint of value
    #    tuple, tuple: Confirm that sizes are the same and every element satisfies the matching element
    # Apply this recursively to handle matrix values and arrays of tuples. Other combinations are not allowed
    if isinstance(value, list):
        return all(values_in_range(single_value, min_value, max_value) for single_value in value)

    if isinstance(value, tuple):
        if isinstance(min_value, (tuple, list)):
            if len(value) != len(min_value):
                raise ValueError(f"Minimum {min_value} must be the same length as the value being checked {value}")
        else:
            min_value = [min_value] * len(value)
        if isinstance(max_value, (tuple, list)):
            if len(value) != len(max_value):
                raise ValueError(f"Maximum {max_value} must be the same length as the value being checked {value}")
        else:
            max_value = [max_value] * len(value)

        return all(
            values_in_range(single_value, single_min, single_max)
            for single_value, single_min, single_max in zip(value, min_value, max_value)
        )

    # Single values are compared directly
    return _value_in_range(value, min_value, max_value)


# ======================================================================
class NumericAttributeManager(AttributeManager):
    """Support class for attributes with simple numeric types

    Attributes:
        minimum: Minimum allowable value of the numeric attribute. None means no minimum.
        maximum: Maximum allowable value of the numeric attribute. None means no maximum.
    """

    # Convenience types for determining numerical type information about these attributes with numerical_type()
    TYPE_OTHER = 0
    TYPE_INTEGER = 1
    TYPE_UNSIGNED_INTEGER = 2
    TYPE_DECIMAL = 3
    TYPE_FLOAT = 4
    TYPE_OBJECT_ID = 5

    # ----------------------------------------------------------------------
    def __init__(self, attribute_name: str, attribute_type_name: str):
        """Initialize the numeric attribute information

        Args:
            attribute_name: Name to use for this attribute
            attribute_type_name: Type of this attribute
        """
        super().__init__(attribute_name, attribute_type_name)
        self.minimum = None
        self.maximum = None
        self.needs_limits = False

    # ----------------------------------------------------------------------
    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_OTHER

    # ----------------------------------------------------------------------
    def cpp_element_value(self, value) -> str:
        """Ensure floating point elements have decimal values so that they are properly recognized."""
        if self.numerical_type() == self.TYPE_DECIMAL:
            if isinstance(value, str):
                if value.lower() in ["inf", "+inf"]:
                    self.needs_limits = True
                    return "std::numeric_limits<double>::infinity()"
                if value.lower() == "-inf":
                    self.needs_limits = True
                    return "-std::numeric_limits<double>::infinity()"
                if value.lower() == "nan":
                    self.needs_limits = True
                    return "std::numeric_limits<double>::quiet_NaN()"
                if value.lower() == "snan":
                    self.needs_limits = True
                    return "std::numeric_limits<double>::signaling_NaN()"
            return f"{value * 1.0}"
        if self.numerical_type() == self.TYPE_FLOAT:
            if isinstance(value, str):
                if value.lower() in ["inf", "+inf"]:
                    self.needs_limits = True
                    return "std::numeric_limits<float>::infinity()"
                if value.lower() == "-inf":
                    self.needs_limits = True
                    return "-std::numeric_limits<float>::infinity()"
                if value.lower() == "nan":
                    self.needs_limits = True
                    return "std::numeric_limits<float>::quiet_NaN()"
                if value.lower() == "snan":
                    self.needs_limits = True
                    return "std::numeric_limits<float>::signaling_NaN()"
            return f"{value * 1.0}f"
        return f"{int(value)}"

    # ----------------------------------------------------------------------
    def validate_value(self, value):
        """Validate that the given data is a matching numeric type, and in range when min/max are specified

        The parse_extra_properties() method should have been called before validating anything.

        Args:
            value: Data value to verify

        Raises:
            ParseError if the min/max range is not respected by the value
        """
        if not is_number_or_list_of_numbers(value, self.tuple_count):
            raise ParseError(f"Value {value} on a {self.ogn_type()} attribute is not a matching type")
        self.validate_numbers_in_range(value)

    # ----------------------------------------------------------------------
    def validate_numbers_in_range(self, value):
        """Validate that the given value is in the legal numeric range, if any are specified

        Args:
            value: Data value to verify

        Raises:
            ParseError if the min/max range is not respected by the value
        """
        # Convert single values to lists for uniform handling
        if self.tuple_count > 1:
            value = tuple(value)
        values = value if isinstance(value, list) else [value]
        if not values_in_range(values, self.minimum, self.maximum):
            raise ParseError(f"Value of {value} is not in the range [{self.minimum}, {self.maximum}")
        super().validate_value(value)

    # ----------------------------------------------------------------------
    def parse_extra_properties(self, property_set: dict) -> PropertySet:
        """Parse properties specific to numeric attribute types

        Args:
            property_set: (NAME, VALUE) for properties the attribute type might support

        Raises:
            ParseError: If any of the extra properties are invalid or not recognized
        """
        remaining_properties = self.parse_min_max_properties(property_set)
        unchecked_properties = super().parse_extra_properties(remaining_properties)
        return unchecked_properties

    # ----------------------------------------------------------------------
    def parse_min_max_properties(self, property_set: dict) -> PropertySet:
        """Check that the min and max property values in property_set are acceptable values (or not present).

        Args:
            property_set: (KEY:VALUE) set from which the min and max will be extracted

        Returns:
            The subset of property_set not checked by this method
        """
        unchecked_set = {}
        for property_name, property_value in property_set.items():
            if property_name in [KEY_ATTR_MINIMUM, KEY_ATTR_MAXIMUM]:
                try:
                    # Min/Max values are applied to all array members, but elements must be specified individually.
                    # The tuple is used to make sure the values are element-wise compared.
                    if isinstance(property_value, list):
                        property_value = tuple(property_value)
                        self.validate_value_nested(property_value, ())
                    else:
                        self.validate_value_nested(property_value, [])
                    setattr(self, property_name, property_value)
                except ParseError as error:
                    raise ParseError(f"Setting {property_name} on {self.name}") from error
            else:
                unchecked_set[property_name] = property_value
        return unchecked_set

    # ----------------------------------------------------------------------
    def cpp_includes(self) -> List[str]:
        """Numeric tuples can use the core 'tuple' class to provide some helpful support methods"""
        regular_includes = super().cpp_includes()
        if self.tuple_count > 1:
            regular_includes.append("omni/graph/core/tuple.h")
        if self.needs_limits:
            regular_includes.append("limits")
        return regular_includes

    # ----------------------------------------------------------------------
    def empty_base_value(self) -> Union[float, int]:
        """Returns an empty value of the current attribute type without tuples or arrays"""
        return 0.0 if self.numerical_type() in [self.TYPE_DECIMAL, self.TYPE_FLOAT] else 0

    # ----------------------------------------------------------------------
    def python_value(self, value):
        """Inf/Nan are treated specially, the rest are just plain numeric values"""
        return repr_as_float(value)

    # ----------------------------------------------------------------------
    def python_value_as_str(self, value):
        """Inf/Nan are treated specially, the rest are just plain numeric values"""
        return repr_value(value)

    # ----------------------------------------------------------------------
    def usd_element(self, element, bare: bool = False) -> str:
        """Handle the special case of inf/nan since they act differently here versus in string types"""
        if isinstance(element, str):
            # Makes use of the fact that even though Python printing of an inf/nan value is not a legal Python
            # value, it is in fact the corresponding legal USD value.
            if element.lower() in ["inf", "+inf"]:
                return float("Inf")
            if element.lower() == "-inf":
                return float("-Inf")
            if element.lower() in ["nan", "snan"]:
                return float("NaN")
            raise ParseError(f"USD string value for numerics can only be one of [inf, -inf, nan], saw '{element}'")

        return super().usd_element(element, bare)
