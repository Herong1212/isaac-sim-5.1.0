"""
Contains the support class for managing attributes whose data is values with specific interpretations
"""

from typing import List

from ..utils import ParseError
from .NumericAttributeManager import NumericAttributeManager


# ======================================================================
class RoleAttributeManager(NumericAttributeManager):
    """Base class for all attribute types that assume different names to tag their special roles"""

    # NUMPY array members types corresponding to the potential suffixes
    NUMPY_TYPES = {
        "d": "numpy.float64",
        "f": "numpy.float32",
        "h": "numpy.float16",
    }

    def __init__(self, attribute_name: str, attribute_type_name: str):
        """Initialize the role-based attribute information

        Args:
            attribute_name: Name to use for this attribute
            attribute_type_name: Unique name for this attribute type
        """
        super().__init__(attribute_name, attribute_type_name)
        if attribute_type_name not in self.roles():
            raise ParseError(f"Only {'|'.join(self.roles())} are legal - {attribute_type_name} is not")

    def suffix(self):
        """Returns the role suffix, for easy type construction"""
        return self.attribute_type_name[-1]

    def tuples_allowed(self) -> List[int]:
        """No tuples are currently supported for this type"""
        return []

    def ogn_base_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        return self.attribute_type_name

    def ogn_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        full_type = self.attribute_type_name
        if self.tuple_count > 1:
            full_type += f"[{self.tuple_count}]"
        full_type += "[]" * self.array_depth
        return full_type

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_DECIMAL if self.suffix() == "d" else NumericAttributeManager.TYPE_FLOAT

    @staticmethod
    def roles():
        """Return a list of valid role names for this type"""
        return []

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("float", self.NUMPY_TYPES[self.suffix()])
