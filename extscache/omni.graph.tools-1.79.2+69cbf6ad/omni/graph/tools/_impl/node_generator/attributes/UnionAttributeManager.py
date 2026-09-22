"""
Contains the support class for managing attributes whose data is 32 bit integers
"""

from typing import Dict, List

from ..utils import _EXTENDED_TYPE_UNION, ParseError, to_usd_docs
from .AnyAttributeManager import AnyAttributeManager
from .AttributeManager import AttributeManager

_INVALID_UNION_TYPES = ["bundle", "target", "execution"]


class UnionAttributeManager(AnyAttributeManager):
    """Support class for attributes of type union

    The union attribute type is different from all of the others in that it doesn't have a fixed data type, it is
    merely a placeholder for an attribute that accepts a variety of data types. It can be thought of as an "any"
    attribute with restrictions on exactly what kind of connections can be made. (e.g. if the union accepts float
    and double then it cannot accept a connection from a string attribute)

    Members:
        __types_accepted: Dictionary of {"typeName": AttributeManager} for all of the data types that this union
                          attribute can accept.
    """

    # This is just a keyword for the attribute manager, this doesn't appear in the type name directly
    OGN_TYPE = "union"

    def __init__(self, attribute_name: str, attribute_type_name: str, types_accepted: Dict[str, AttributeManager]):
        """Set up the empty attribute values for population from the JSON description

        Args:
            attribute_name: Unique name for this attribute
            attribute_type_name: Unique name for this attribute type
            types_accepted: Same type as member __types_accepted

        Raises:
            ParseError: If any of the accepted types are not legal
        """
        super().__init__(attribute_name, attribute_type_name)
        self.__types_accepted = types_accepted
        for type_name in types_accepted.keys():
            if type_name in _INVALID_UNION_TYPES:
                raise ParseError(f"'{type_name}' is not a permitted type when using extended types")

    def validate_value_structure(self, value_to_validate: any):
        """Validate the structure as much as possible"""
        # Ideally here the actual values would be verified against the allowed types but that's a pretty big
        # complication who's failures would ultimately get caught by the generated code anyway so for now just
        # confirm that input values have their types defined - outputs are assumed to be able to be anything.
        if isinstance(value_to_validate, dict) and ["type", "value"] == sorted(value_to_validate.keys()):
            return
        if not self.is_read_only():
            return
        raise ParseError(f"'Union' type attribute values have to be type/value dictionaries, got '{value_to_validate}'")

    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        return "One of the filtered set of Python data types, as resolved at runtime by connection or by value"

    def cpp_extended_type(self):
        """Returns the extended type identifier for C++ types"""
        return "kExtendedAttributeType_Union"

    def is_dynamic(self):
        """Returns True as "union" attributes are dynamic"""
        return True

    def ogn_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        type_information = sorted(self.__types_accepted.keys())
        if self.array_depth == 1:
            type_information = [type_information]
        return f"{type_information}"

    def ogn_root_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        type_information = sorted(self.__types_accepted.keys())
        if self.array_depth == 1:
            type_information = [type_information]
        return f"{type_information}"

    def cuda_type_name(self) -> str:
        return None

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return ",".join(sorted(self.__types_accepted.keys()))

    def python_extended_type(self):
        """Returns the extended type identifier and descriptor for Python attribute types"""
        return (_EXTENDED_TYPE_UNION, ",".join(sorted(self.__types_accepted.keys())))

    def usd_type_accepted_description(self) -> str:
        """Returns a string that will be the default value of the USD token, describing accepted types"""
        return f"union of {','.join(self.__types_accepted.keys())}"

    def emit_usd_declaration(self, out) -> List[str]:
        """Print a declaration for this attribute in USD

        Args:
            out: Output handler where the USD will be emitted
        """
        try:
            usd_name = self.usd_name()
            # Overriding default behavior of using self.usd_type_name()
            usd_type = "token"
        except ParseError:
            # Attributes without USD representations can be skipped
            return

        docs = to_usd_docs(self.description)

        default_value = self.usd_default_value()
        if out.indent(f"custom {usd_type} {usd_name}{default_value} ("):
            out.write(docs)
            out.exdent(")")
