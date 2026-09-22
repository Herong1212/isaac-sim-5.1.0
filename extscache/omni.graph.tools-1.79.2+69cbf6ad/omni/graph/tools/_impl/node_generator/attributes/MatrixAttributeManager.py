"""
Contains the support class for managing attributes whose data is matrixes of numbers
"""

from contextlib import suppress
from typing import Any, List, Union

from ..utils import ParseError
from .AttributeManager import CppConfiguration, CudaConfiguration
from .inf_nan import repr_as_float, repr_value
from .NumericAttributeManager import is_number_or_list_of_numbers
from .RoleAttributeManager import RoleAttributeManager


class MatrixAttributeManager(RoleAttributeManager):
    """Support class for the attribute with role matrix (i.e. matrixd)
    Note that unlike other role classes the tuple values for a matrix indicate the row/column sizes, not the
    total number of values. So a matrixd[4] has 16 elements.
    """

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "matrixd[2]": CppConfiguration(
            "pxr::GfMatrix2d", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eMatrix"
        ),
        "matrixd[3]": CppConfiguration(
            "pxr::GfMatrix3d", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eMatrix"
        ),
        "matrixd[4]": CppConfiguration(
            "pxr::GfMatrix4d", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eMatrix"
        ),
    }
    CUDA_CONFIGURATION = {
        "matrixd[2]": CudaConfiguration("Matrix2d", include_files=["omni/graph/core/cuda/Matrix2d.h"], role="eMatrix"),
        "matrixd[3]": CudaConfiguration("Matrix3d", include_files=["omni/graph/core/cuda/Matrix3d.h"], role="eMatrix"),
        "matrixd[4]": CudaConfiguration("Matrix4d", include_files=["omni/graph/core/cuda/Matrix4d.h"], role="eMatrix"),
    }

    # ----------------------------------------------------------------------
    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: If True return as the data type used to set the value in USD attributes, else return Python values
        """
        values = [
            tuple(tuple(1.0 if i == j else 0.0 for i in range(self.tuple_count)) for j in range(self.tuple_count)),
            tuple(tuple(2.0 if i == j else 3.0 for i in range(self.tuple_count)) for j in range(self.tuple_count)),
        ]
        if for_usd:
            from pxr import Gf

            gf_type = getattr(Gf, f"Matrix{self.tuple_count}d")
            values = [gf_type(*self.flattened_value(values[0])), gf_type(*self.flattened_value(values[1]))]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    # ----------------------------------------------------------------------
    @staticmethod
    def roles():
        """Return a list of valid role names for this type"""
        return ["matrixd"]

    # ----------------------------------------------------------------------
    @classmethod
    def is_matrix_type(cls) -> bool:
        """This is obviously a matrix type"""
        return True

    # ----------------------------------------------------------------------
    @staticmethod
    def tuples_supported() -> List[int]:
        """This type can only have 2, 3 or 4 dimensions (squared for actual data count), not 1"""
        return [2, 3, 4]

    # ----------------------------------------------------------------------
    def tuple_argument(self):
        """Return a string with the declaration of a tuple count argument for constructors"""
        tuple_count_arg = "" if self.tuple_count < 2 else f", {self.tuple_count * self.tuple_count}"
        return tuple_count_arg

    # ----------------------------------------------------------------------
    def empty_value(self):
        """Having a 2d tuple count means the matrix needs a different shape for its empty values"""
        if self.array_depth == 1:
            return []
        # The empty matrix is the identity matrix, not all 0's as it is for other numeric types.
        identity = []
        for i in range(self.tuple_count):
            row = []
            for j in range(self.tuple_count):
                row.append(1.0 if j == i else 0.0)
            identity.append(row)
        return identity

    # ----------------------------------------------------------------------
    @staticmethod
    def flattened_value(value: Any) -> List[Any]:
        """Returns a flattened version of the 2d list, required by the Python bindings

        Args:
            value: A list of list of values or tuple of tuple of values representing a matrix
        """
        if isinstance(value, (list, tuple)):
            flattened_value = list(value)
            # The index error captures the empty list case, which flattens to itself
            with suppress(IndexError):
                if isinstance(flattened_value[0], (list, tuple)):
                    flattened_value = [item for sublist in flattened_value for item in sublist]
                else:
                    # The value is already flattened so just return it directly
                    return value
        else:
            raise ParseError(f"Value {value} should be a matrix")
        return flattened_value

    # ----------------------------------------------------------------------
    def square_tuple(self, value: Union[List[float], List[List[float]]]) -> List[float]:
        """Returns a square 2d list version of the passed in list, required for USD setting"""
        if len(value) == self.tuple_count:
            for element in value:
                if len(element) != self.tuple_count:
                    raise ParseError(
                        f"Value {value} should be a 2d or flattened matrix of dimension {self.tuple_count}"
                    )
            return tuple(tuple(element) for element in value)
        if len(value) == self.tuple_count * self.tuple_count:
            square = []
            for row in range(self.tuple_count):
                square.append(
                    tuple(
                        column for column in value[row * self.tuple_count : row * self.tuple_count + self.tuple_count]
                    )
                )
            return tuple(square)

        raise ParseError(f"Value {value} should be a 2d or flattened matrix of dimension {self.tuple_count}")

    # ----------------------------------------------------------------------
    def validate_numbers_in_range(self, value):
        """Validate that the given value is in the legal numeric range, if any are specified

        Args:
            value: Data value to verify, in flattened form

        Raises:
            ParseError if the min/max range is not respected by the value
        """
        # Convert single values to lists for uniform handling
        if self.minimum is not None:
            for single_value, minimum in zip(value, self.flattened_value(self.minimum)):
                if single_value < minimum:
                    raise ParseError(f"Value of {value} is less than the allowed minimum of {self.minimum}")
        if self.maximum is not None:
            for single_value, maximum in zip(value, self.flattened_value(self.maximum)):
                if single_value > maximum:
                    raise ParseError(f"Value of {value} is greater than the allowed maximum of {self.maximum}")

    # ----------------------------------------------------------------------
    def validate_value(self, value):
        """Raises a ParseError if the value is not a valid matrix value of the correct dimensions.
        Unlike other tuples the matrix types use a single tuple count to represent both dimensions of the data,
        so a matrix2d can be [[0.0, 0.0], [0.0, 0.0]] or [0.0, 0.0, 0.0, 0.0]
        """
        flattened_value = self.flattened_value(value)
        if not is_number_or_list_of_numbers(flattened_value, self.tuple_count * self.tuple_count):
            raise ParseError(f"Value {value} on a {self.ogn_type()} attribute is not a {self.tuple_count}d matrix")
        self.validate_numbers_in_range(flattened_value)

    # ----------------------------------------------------------------------
    def cpp_tuple_value(self, value) -> str:
        """Returns the string for the C++ representation of the single value passed in.
        Matrix values can be passed in either as flattened lists or as square 2d lists.
        The form passed in is assumed to be the one required for the constructor, except for the pxr::GfMatrixXd
        types, which require a flattened list but for historical reasons may not get it, so the list is flattened
        for them.
        """
        flattened_size = self.tuple_count * self.tuple_count
        if len(value) != self.tuple_count and len(value) != flattened_size:
            raise ParseError(f"Tuple count initializer expected matrix of size {self.tuple_count}, got `{value}`")

        # In the case of a flattened list the value is returned as a simple flattened list as well
        if len(value) == flattened_size:
            return f"{{{','.join([RoleAttributeManager.cpp_element_value(self, element) for element in value])}}}"

        expected_shape = [self.tuple_count] * self.tuple_count
        actual_shape = [len(row) for row in value]
        if expected_shape != actual_shape:
            raise ParseError(f"Matrix default must be size {self.tuple_count} x {self.tuple_count}, flat or square")

        if self.cpp_configuration().base_type_name.startswith("pxr"):
            # Backward compatibility for pxr::GfMatrix types - they should have flattened lists for construction
            # but before both types were accepted. Now the type in the file should correspond with the type needed
            # by the type's constructor.
            flattened_value = self.flattened_value(value)
            return f"{{{','.join([RoleAttributeManager.cpp_element_value(self, elem) for elem in flattened_value])}}}"

        row_values = []
        for row_element in value:
            row_values.append(
                f"{{{','.join([RoleAttributeManager.cpp_element_value(self, element) for element in row_element])}}}"
            )
        return f"{{{','.join(row for row in row_values)}}}"

    # ----------------------------------------------------------------------
    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.MATRIX"

    # ----------------------------------------------------------------------
    def python_value(self, value):
        """Returns the value for this attribute in a Python-compatible format.
        The Python bindings require the list be flattened so do that first.
        """
        if not value:
            return value
        if self.array_depth > 0:
            return [self.flattened_value(element) for element in value]
        return self.flattened_value(value)

    # ----------------------------------------------------------------------
    def python_value_as_str(self, value):
        """Inf/Nan are treated specially, the rest are just plain numeric values"""
        return repr_value(value)

    # ----------------------------------------------------------------------
    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return f"Matrix{self.suffix()}"

    # ----------------------------------------------------------------------
    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_arrays(f"matrix{self.tuple_count}{self.suffix()}")

    # ----------------------------------------------------------------------
    def usd_value(self, value):
        """The matrix values require two levels of parentheses so this override is necessary."""
        if value is None:
            return None
        if self.array_depth > 0:
            if not isinstance(value, (list, tuple)):
                raise ParseError(f"Expected list for USD array value on {self.name} - got {value}")
            array_output = []
            for element in value:
                array_output.append(repr_as_float(self.square_tuple(element)))
            return array_output

        return repr_as_float(self.square_tuple(value))
