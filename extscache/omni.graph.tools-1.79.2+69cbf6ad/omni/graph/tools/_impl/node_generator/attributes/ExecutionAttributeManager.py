"""
Contains the support class for managing attributes whose data is arrays interpreted as surface normals
"""

from typing import Any, List

from ..utils import ParseError, to_usd_docs
from .AttributeManager import CppConfiguration, CudaConfiguration
from .NumericAttributeManager import NumericAttributeManager, values_in_range
from .parsing import is_type_or_list_of_types
from .RoleAttributeManager import RoleAttributeManager


class ExecutionAttributeManager(RoleAttributeManager):
    """Support class for attributes of type execution

    These are uint and uint[] types with the internal Execution Role
    """

    OGN_TYPE = "execution"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {"execution": CppConfiguration("uint32_t", cast_required=False, role="eExecution")}
    CUDA_CONFIGURATION = {"execution": CudaConfiguration("int", cast_required=False, role="eExecution")}

    @staticmethod
    def roles():
        """Return a list of valid role names for this type"""
        return ["execution"]

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_UNSIGNED_INTEGER

    @staticmethod
    def array_depths_supported() -> List[int]:
        """Arrays of execution values doesn't make any sense"""
        return [0]

    @staticmethod
    def tuples_supported() -> List[int]:
        """Executions don't have tuples"""
        return [1]

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        # execution must be in the range of the enum ExecutionAttributeState
        values = [0, 1, 2]
        return [[value] for value in values] if for_usd else values

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid uint value"""
        if not is_type_or_list_of_types(value, int, self.tuple_count):
            raise ParseError(f"Value {value} on a uint[{self.tuple_count}] attribute is not a matching type")
        if not values_in_range(value, 0, 4294967295):
            raise ParseError(f"Value {value} on a uint[{self.tuple_count}] attribute is out of range")
        super().validate_value(value)

    def requires_default(self):
        """Execution attributes are transient by nature, we shouldn't really store them at all"""
        return False

    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        return "Execution pin value for Action graphs"

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.EXECUTION"

    def cuda_base_type_name(self) -> str:
        """Returns a string with the CUDA base type of the attribute data"""
        return "uint32_t"

    def sdf_type_name(self) -> str:
        """Execution attribs have no pxr::SdfValueTypeName"""

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "UInt"

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("int", "numpy.int32")

    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.data_types module.
        The default uses the SDF type name but there isn't one for this type so hardcode the actual type.
        """
        return "omni.graph.core.types.execution" + "array" * self.array_depth

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        # FIXME: This isn't accurate for execution case, the usd type is 'uint' but we are passing in 'execution' when
        # creating the attribute so that it can be recognized as a uint with eExecution role.
        # (see emit_usd_declaration())
        return "execution"

    def emit_usd_declaration(self, out) -> List[str]:
        """Print a declaration for this attribute in USD

        Args:
            out: Output handler where the USD will be emitted
        """
        try:
            usd_name = self.usd_name()
            # Overriding default behavior of using self.usd_type_name()
            usd_type = "uint"
        except ParseError:
            # Attributes without USD representations can be skipped
            return

        docs = to_usd_docs(self.description)

        default_value = self.usd_default_value()
        if out.indent(f"custom {usd_type} {usd_name}{default_value} ("):
            out.write(docs)
            out.exdent(")")
