# The information bracketed here with begin/end describes the interface that is recommended for use with runtime
# attributes. The documentation uses these markers to perform a literal include of this code into the docs so that
# it can be the single source of truth. Note that the interface described here is not the complete set of functions
# functions available, merely the ones that make sense for the user to access when dealing with runtime attributes.
#
# begin-runtime-interface-description
"""
# A runtime attribute is one whose data type can only be determined at runtime, and which can potentially change
# from one evaluation to the next. These attributes can be found either as bundle members or as the extended
# attribute types "any" or "union".
#
# One way of getting this accessor class is by extracting a bundle member:
#
red_attribute = db.inputs.colorBundle.attribute_by_name(db.tokens.red)

# The other way is to access the data of an extended attribute type in the same way you'd access any other attribute
red_attribute = db.inputs.colorAtRuntime

# The wrapper class has access to the attribute description information, specifically the name and type
red_name = red_attribute.name
red_type = red_attribute.type

# Array attributes have a "size" property, which can also be set on output or state attributes
point_array = db.inputs.mesh.attribute_by_name(db.tokens.points)
deformed_point_array = db.outputs.mesh.attribute_by_name(db.tokens.points)
deformed_point_array.size = point_array.size

# Default value access is done through the value property, which is writable on output or state attributes
red_input = db.inputs.colorBundle.attribute_by_name(db.tokens.red)
red_output = db.outputs.colorBundle.attribute_by_name(db.tokens.red)
red_output.value = 1.0 - red_input.value

# By default the above functions operate in the same memory space as was defined by the bundle that contained the
# attribute. If you wish to be more explicit about where the memory lives you can access the specific versions of
# value properties that force either CPU or GPU memory space
if on_gpu:
    call_cuda_code(red_output.gpu_value, red_input.gpu_value)
else:
    red_output.cpu_value = 1.0 - red_input.cpu_value

# Lastly, on the rare occasion you need direct access to the attribute's ABI through the underlying type
# og.AttributeData you can access it through the abi property
my_attribute_data = red_attribute.abi
"""
from __future__ import annotations

from typing import Any

# end-runtime-interface-description
import omni.graph.core as og

from .attribute_values import WrappedArrayType
from .utils import non_const


# ================================================================================
class RuntimeAttribute:
    """----- FOR USE BY GENERATED CODE ONLY -----
    Accessor for an attribute whose data type can only be determined at runtime, and which can potentially change
    from one evaluation to the next. These attributes can be found either as bundle members or as the extended
    attribute types "any" or "union".
    """

    def __init__(
        self,
        attribute_data: og.AttributeData,
        context: og.GraphContext,
        read_only: bool,
        on_gpu: bool = None,
        gpu_ptr_kind: og.PtrToPtrKind = og.PtrToPtrKind.GPU,
    ):
        """Constructs a wrapper around the raw ABI attribute data object"""
        self.attribute_data = attribute_data
        self.read_only = read_only
        self.helper = og.AttributeDataValueHelper(attribute_data)
        self._on_gpu = False if on_gpu is None else on_gpu
        self.helper.gpu_ptr_kind = gpu_ptr_kind

    # ------------------------------------------------------------------------------------------
    def copy_data(self, other: RuntimeAttribute) -> bool:
        """Copies data from another attribute, returning True if the copy succeeded, else False

        Args:
            other: RuntimeAttribute from which data is to be copied

        Returns:
            bool: True if the copy succeeded
        """
        return self.attribute_data.copy_data(other.attribute_data)

    # ------------------------------------------------------------------------------------------
    @property
    def abi(self) -> og.AttributeData:
        """omni.graph.core.AttributeData: The ABI object representing the bundled attribute's data"""
        return self.attribute_data

    # ------------------------------------------------------------------------------------------
    @property
    def size(self) -> int:
        """int: The number of elements in the attribute (1 for regular data, elementCount for arrays)"""
        return self.attribute_data.size()

    @size.setter
    @non_const
    def size(self, new_size: int) -> int:
        """Set the array size for the element. Raises og.OmniGraphError if the data type is not an array"""
        if not self.attribute_data.resize(new_size):
            raise og.OmniGraphError(f"Not allowed to resize data that is not an array type - '{self.type}'")

    # ------------------------------------------------------------------------------------------
    @property
    def name(self) -> str:
        """str: Name of the attribute data. Can only be set on creation."""
        return self.attribute_data.get_name()

    # ------------------------------------------------------------------------------------------
    @property
    def type(self) -> og.Type:  # noqa: A003
        """omni.graph.core.Type: Attribute type of the attribute data. Can only be set on creation."""
        return self.attribute_data.get_type()

    # ------------------------------------------------------------------------------------------
    @property
    def value(self) -> Any:
        """Any: The value of an attributeData for reading"""
        wrapper_type = WrappedArrayType.RAW if self._on_gpu else WrappedArrayType.NUMPY
        return self.helper.get(
            on_gpu=self._on_gpu,
            return_type=wrapper_type if self.type.array_depth > 0 else None,
            reserved_element_count=None if self.type.array_depth == 0 else self.size,
        )

    @value.setter
    @non_const
    def value(self, new_value: Any):
        """Set the value of an attributeData"""
        if self.read_only:
            raise og.ReadOnlyError(f"Not allowed to set read-only attribute data {self.attribute_data.get_name()}")
        self.helper.set(new_value, on_gpu=self._on_gpu)

    # ------------------------------------------------------------------------------------------
    @property
    def gpu_value(self) -> Any:
        """Any: The value of an attributeData for reading, forcing it to be on the GPU"""
        return self.helper.get(
            on_gpu=True,
            return_type=WrappedArrayType.RAW if self.type.array_depth > 0 else None,
            reserved_element_count=None if self.type.array_depth == 0 else self.size,
        )

    @gpu_value.setter
    @non_const
    def gpu_value(self, new_value: Any):
        """Set the value of an attributeData, forcing it to be on the GPU"""
        if self.read_only:
            raise og.ReadOnlyError(f"Not allowed to set read-only attribute data {self.attribute_data.get_name()}")
        self.helper.set(new_value, on_gpu=True)

    # ------------------------------------------------------------------------------------------
    @property
    def cpu_value(self) -> Any:
        """Any: The value of an attributeData for reading, forcing it to be on the CPU"""
        return self.helper.get(
            on_gpu=False,
            reserved_element_count=None if self.type.array_depth == 0 else self.size,
        )

    @cpu_value.setter
    @non_const
    def cpu_value(self, new_value: Any):
        """Set the value of an attributeData, forcing it to be on the CPU"""
        if self.read_only:
            raise og.ReadOnlyError(f"Not allowed to set read-only attribute data {self.attribute_data.get_name()}")
        self.helper.set(new_value, on_gpu=False)

    # ------------------------------------------------------------------------------------------
    def array_value(self, *args, **kwargs) -> Any:
        """Set the value of an attributeData for writing, with preallocated element space.
        See AttributeDataValueHelper.get_array() for parameters. on_gpu is provided here

        Returns:
            Any: Value of the array data
        """
        return self.helper.get(*args, on_gpu=self._on_gpu, **kwargs)
