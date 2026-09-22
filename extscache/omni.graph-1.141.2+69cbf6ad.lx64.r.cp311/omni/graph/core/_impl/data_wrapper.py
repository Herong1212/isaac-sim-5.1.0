"""Contains support for wrapping Python objects around Fabric typed data

These patterns draw heavily on the interfaces used by numpy as that is what is provided when dealing with Python
data on the CPU. The intent is to make the data interface pattern as similar as possible to make dealing with it
more consistent, though not to try to replicate any of the numpy functionality - that is left up to the interpreter
of this data.

The data wrapper consists of a raw memory pointer and a set of type identification information that corresponds to the
types supported by Fabric (including those that will be supported in the foreseeable future).

One major way that the data typing differs from numpy is in the shape specification. While numpy insists that its
data be a matrix (i.e. a shape of (2,3) means a fully populated 2x3 matrix) this shape specification can include
different index counts in each level to accommodate gathered data.

To avoid ambiguity the gathered element sizes are placed in a tuple, even when it's only a single value.

e.g. 4x4 matrix = shape(4, 4)
     Array of 5 4x4 matrixes = shape(5, 4, 4)
     Two gathered 4x4 matrixes = shape((2,), 4, 4)
     Two gathered arrays of 5 and 6 4x4 matrixes = shape((5, 6), 4, 4)

Here's how the shapes correspond to the access patterns, where the values returned are either memory pointers to a
particular element or another DataWrapper which access the sub-array. The indexes in the shape are from largest
scope to smallest scope, so gathered size is first, then array size, then tuple size.

The index operator can be specified by one or more index values, traversing down multiple levels of the array hierarchy.
These two are equivalent, though the first is more efficient - wrapper[I, J, K], wrapper[I][J][K]

These are the shape types currently supported by Fabric, using float values as examples:

    None - "Item is a single value, not an array"

    (2,) - "An array of two elements"
          float[] of size 2
              index[I] is the Ith element of the array
          float[2]
              index[I] is the Ith tuple member

    ((2,)) - "A gathered set of two items"
            float with 2 gathered items
                index[I] is the Ith gathered item

    (2,3) - "An array of 2 arrays with 3 elements each"
            float[3][] of size 2
                item[I] = Ith float[3] in the array
                item[I, J] = Jth tuple member of the Ith float[3] in the array

    ((2,),3) - "An array of two arrays with 3 elements each"
              float[3] with 2 gathered items
                  item[I] = Ith gathered float[3]
                  item[I, J] = Jth tuple member of the Ith gathered float[3]

    ((3,4)) - "An array of 2 arrays, the first with 3 elements, the second with 4"
              float[] with gathered items of sizes 3 and 4
                  item[I] = Ith gathered array of floats
                  item[I, J] = Jth element of the Ith gathered float[]

    ((2,3),3) - "An array of 2 arrays of arrays with 3 elements, the first is an array of 2 arrays, the second is an
                array of 3 arrays"
                float[3][] with 2 gathered array items of length 2 and 3 respectively
                    item[I] = Ith gathered array of float[3]s
                    item[I, J] = Jth element of the Ith gathered array of float[3]s
                    item[I, J, K] = Kth tuple member of the Jth element of the Ith gathered array of float[3]s

There are also special cases for arrays, which are like tuples but have two index numbers for row and column. The matrix
types can only have 2, 3, or 4 as their tuple count, and must have a base data type of double.

    (2,2) - "A 2x2 matrix"
            matrixd[2]
                item[I] = Ith row of the matrix
                item[I, J] = Jth column of the Ith row of the matrix

    (3,2,2) - "An array of 2x2 matrixes"
              array of matrixd[2] with 3 gathered items
                  item[I] = Ith matrix array element
                  item[I, J] = Jth row of the Ith matrix array element
                  item[I, J, K] = Kth column of the Jth row of the Ith matrix array element

    ((3),2,2) - "An array of 2x2 matrixes"
                gathered matrixd[2] with 3 gathered items
                    item[I] = Ith gathered matrix
                    item[I, J] = Jth row of the Ith gathered matrix
                    item[I, J, K] = Kth column of the Jth row of the Ith gathered matrix

    ((2,3),2,2) - "An array of 2 arrays of 2x2 matrixes, the first with 2 elements, the second with 3 elements"
                  gathered matrixd[2][] with 2 gathered items consisting of an array of 2 matrixes and an array of
                  3 matrixes respectively
                      item[I] = Ith gathered matrix array
                      item[I, J] = Jth element of the Ith gathered matrix array
                      item[I, J, K] = Kth row of the Jth element of the Ith gathered matrix array
                      item[I, J, K, L] = Lth column of the Kth row of the Jth element of the Ith gathered matrix array

Note that while gathered arrays and regular arrays have the same access pattern they are conceptually different in that
a gathered array represents data from N different objects which a regular array represents N different values on the
same object.
"""

from __future__ import annotations

import ctypes

import omni.graph.core as og

from .dtypes import Dtype

# These supported shape types correspond to the ones described above
DataWrapperShapeTypes = (
    None
    | int
    | tuple[int, int]
    | tuple[tuple[int, int]]
    | tuple[tuple[int, int], int]
    | tuple[int, int, int]
    | tuple[int, int, tuple[int, int]]
)


# ==============================================================================================================
class Device:
    """Device type for memory location of the data types"""

    def __init__(self, device_name: str):
        """Initialize the device with the given name"""
        self.__cpu = device_name.lower().find("cpu") == 0
        self.__cuda = device_name.lower().find("cuda") == 0

    def __str__(self) -> str:
        """Standardized device name"""
        return "cpu" if self.__cpu else "cuda" if self.__cuda else "unknown"

    @property
    def cpu(self) -> bool:
        """bool: Is the device a CPU?"""
        return self.__cpu

    @property
    def cuda(self) -> bool:
        """bool: Is the device a GPU programmed with CUDA?"""
        return self.__cuda


# ==============================================================================================================
def data_shape_from_type(attribute_type: og.Type, is_gathered: bool = False) -> tuple[Dtype, DataWrapperShapeTypes]:
    """Return the dtype,shape information that corresponds to the given attribute type.
    For easy testing gather sizes are set to 2 items and array sizes are set to 0 elements.
    e.g. a gathered bool[] would return a shape of ((0, 0))

    Args:
        attribute_type: Type from which to infer the shape
        is_gathered: Is the data shape for an array of the attribute type?

    Returns:
        (Dtype, DataWrapperShapeTypes): Data type and shape corresponding to the attribute type
    """
    dtype = None
    shape = None
    unmatched_shape = -1

    # --------------------------------------------------------------------------------------------------------------
    def matrix_shape(dtype_class) -> DataWrapperShapeTypes:
        """Get the information from a matched matrix type"""
        if attribute_type.tuple_count != dtype_class.tuple_count:
            return unmatched_shape
        if is_gathered:
            if attribute_type.array_depth == 0:
                shape = ((2,), dtype_class.matrix_dim, dtype_class.matrix_dim)
            else:
                shape = ((2, 2), dtype_class.matrix_dim, dtype_class.matrix_dim)
        else:
            if attribute_type.array_depth == 0:
                shape = (dtype_class.matrix_dim, dtype_class.matrix_dim)
            else:
                shape = (0, dtype_class.matrix_dim, dtype_class.matrix_dim)
        return shape

    # --------------------------------------------------------------------------------------------------------------
    def match_simple(dtype_class) -> DataWrapperShapeTypes:
        """Match types that are not matrixes"""
        if is_gathered:
            if attribute_type.array_depth == 0:
                if attribute_type.tuple_count == 1:
                    shape = (2,)
                else:
                    shape = ((2,), dtype_class.tuple_count)
            else:
                if attribute_type.tuple_count == 1:
                    shape = (2, 2)
                else:
                    shape = ((2, 2), dtype_class.tuple_count)
        else:
            if attribute_type.array_depth == 0:
                if attribute_type.tuple_count == 1:
                    shape = None
                else:
                    shape = (dtype_class.tuple_count,)
            else:
                if attribute_type.tuple_count == 1:
                    shape = (0,)
                else:
                    shape = (0, dtype_class.tuple_count)
        return shape

    for dtype_class in Dtype.__subclasses__():

        # This prevents double4 types from matching matrix2d types
        if attribute_type.is_matrix_type() != dtype_class.is_matrix_type():
            continue

        # Simple marker for an unmatched shape, needed since "None" is a valid match
        matched_shape = unmatched_shape
        if attribute_type.is_matrix_type():
            # Special case of matrix values where the tuple count is only one axis
            matched_shape = matrix_shape(dtype_class)

        elif (
            dtype_class.tuple_count == attribute_type.tuple_count and dtype_class.base_type == attribute_type.base_type
        ):
            matched_shape = match_simple(dtype_class)

        if matched_shape != unmatched_shape:
            if shape is not None:
                raise AttributeError(
                    f"More than one match found for {attribute_type} - {dtype}/{shape} and {dtype_class()}"
                )
            dtype = dtype_class()
            shape = matched_shape

    return (dtype, shape)


# ==============================================================================================================
def get_dtype_tuple_child(parent_type: Dtype) -> Dtype:
    """Return the Dtype that is the tuple child of the parent_type.
    e.g. if you pass in Float3 you should get Float back

    Args:
        parent_type: Dtype whose child is to be found

    Returns:
        Dtype: Type corresponding to the parent_type, but with a tuple_count of 1

    Raises:
        AttributeError: If the parent_type has no corresponding child
    """
    try:
        expected_tuple_count = parent_type.matrix_dim
    except AttributeError:
        expected_tuple_count = 1

    for dtype_class in Dtype.__subclasses__():
        if dtype_class.base_type == parent_type.base_type and dtype_class.tuple_count == expected_tuple_count:
            return dtype_class()

    raise AttributeError(
        f"No matching class found with base tyhpe {parent_type.base_type} and tuple count {expected_tuple_count}"
    )


# ==============================================================================================================
class DataWrapper:
    """Wrapper around typed memory data.

    This class provides no functionality for manipulating the data, only for inspecting it and extracting it for
    other code to manipulate it. e.g. you could extract CPU data as a numpy array and modify values, though you
    cannot change its size, or you could extract the pointer to the GPU data for passing in to a GPU-aware package
    like TensorFlow. External functions will perform these conversions.

    Attributes:
        memory: Address of the data in the memory space
        dtype: Data type information for the individual data elements
        shape: Array shape of the memory
        device: Device on which the memory is located.
        gpu_ptr_kind: Arrays of GPU pointers can either be on the GPU or the CPU, depending on where you want to
                      reference them. If the shape is an array and device is cuda then this tells where 'memory' lives
    """

    def __init__(
        self,
        memory: int,
        dtype: Dtype,
        shape: DataWrapperShapeTypes,
        device: Device,
        gpu_ptr_kind: og.PtrToPtrKind = og.PtrToPtrKind.NA,
    ):
        """Sets up the wrapper for the passed-in data.

        Args:
            memory: Integer containing the memory address of the data
            dtype: Data type of the referenced data
            shape: Array shape of the referenced data
            device: Device on which the memory is located.
            gpu_ptr_kind: Location of pointers that point to GPU arrays
        """
        self.memory = memory
        self.dtype = dtype
        self.shape = shape
        self.device = device
        self.gpu_ptr_kind = gpu_ptr_kind

        # Check to see if the shape is in a valid configuration
        is_tuple = self.dtype.tuple_count > 1
        if shape is None:
            if is_tuple:
                raise ValueError("tuple type must at least have the tuple count in the shape")
            return

        if not isinstance(shape, tuple):
            raise ValueError("Shape must be a tuple type matching the array configuration of the data type")

        first_dimension, *other_dimensions = shape

        if not isinstance(first_dimension, int):
            raise ValueError(f"First member of shape tuple must be an array count - not {shape}")
        if is_tuple:
            # Legal tuple shapes are (N) for simple tuples, (N, M) for tuple arrays and matrixes,
            # and (N, M, M) for matrix arrays
            if dtype.is_matrix_type():
                matrix_type_invalid = False
                if len(other_dimensions) == 1:
                    if (other_dimensions[-1] != first_dimension) or (first_dimension != dtype.matrix_dim):
                        matrix_type_invalid = True
                elif len(other_dimensions) == 2:
                    if (other_dimensions[-1] != other_dimensions[-2]) or (other_dimensions[-2] != dtype.matrix_dim):
                        matrix_type_invalid = True
                else:
                    matrix_type_invalid = True
                if matrix_type_invalid:
                    raise ValueError(
                        f"Matrix shape can only be (N, N) or (M, N, N) where N is the matrix dimension - not {shape}"
                    )
            else:
                tuple_type_invalid = False
                if len(other_dimensions) == 1:
                    tuple_type_invalid = other_dimensions[-1] != dtype.tuple_count
                elif not other_dimensions:
                    tuple_type_invalid = first_dimension != dtype.tuple_count
                else:
                    tuple_type_invalid = True
                if tuple_type_invalid:
                    raise ValueError(f"tuple shape can only be (N) or (M, N) where N is the tuple count - not {shape}")
        else:
            if other_dimensions:
                raise ValueError(f"Simple value shape can only be None or (N) - not {shape}")

    def __delitem__(self, index: int):
        """Raises ValueError as deleting items from the data is not allowed"""
        raise ValueError("This is just a memory wrapper. Deletion of array elements is not permitted here")

    def __setitem__(self, index: int, new_item: DataWrapper):
        """Raises ValueError as settings items on the data is not allowed"""
        raise ValueError("This is just a memory wrapper. Setting of array elements is not permitted here")

    def __getitem__(self, index: int) -> DataWrapper:
        """Returns the data referenced at the index.

        This means different things depending on the shape of the object.
        For gathered objects the index is taken to mean "the Nth gathered value", so the result will point to
        ungathered data.
        For ungathered objects the index is taken to mean "the Nth child of the first shape depth". For an array
        it will be the array element, for tuples it will be the tuple element, and for matrices it will be the
        row first, the column second.

        Args:
            index: Index within the array of the item to find

        Raises:
            ValueError: If the object is not an array type or the index is out of range
        """
        if isinstance(index, slice):
            raise ValueError("Slice indexing is not yet supported")

        if self.shape is None:
            raise ValueError("Cannot take the index of a non-array type")

        first_shape, *new_shape = self.shape
        new_shape = tuple(new_shape)

        # Gathered items are easier to handle as the underlying types don't change. An index into a gathered
        # array is the Nth array in the gathering.
        if isinstance(first_shape, tuple):
            if len(first_shape) == 1:
                if not 0 <= index < first_shape[0]:
                    raise ValueError(f"DataWrapper gathered element index {index} must be in [0, {first_shape[0]}]")
                # Gathered array of simple values
                new_memory = self.memory + self.dtype.size * index
            else:
                if not 0 <= index < len(first_shape):
                    raise ValueError(f"DataWrapper gathered element index {index} must be in [0, {len(first_shape)}]")
                # Gathered array of array values
                new_memory = self.memory + sum(size * self.dtype.size for size in first_shape[0:index])
                new_shape = (first_shape[index], *new_shape)
            return DataWrapper(new_memory, self.dtype, new_shape or None, self.device, self.gpu_ptr_kind)

        # Single shape dimension - a simple tuple, or a simple array (can't be a matrix at this point)
        if not new_shape:
            if not 0 <= index < first_shape:
                raise ValueError(f"DataWrapper element index {index} must be in [0, {first_shape}]")
            if self.dtype.tuple_count > 1:
                new_dtype = get_dtype_tuple_child(self.dtype)
                new_memory = self.memory + index * (self.dtype.size / self.dtype.tuple_count)
            else:
                new_dtype = self.dtype
                new_memory = self.memory + index * self.dtype.size

        # Single matrix
        elif self.dtype.is_matrix_type() and len(new_shape) == 1:
            if not 0 <= index < first_shape:
                raise ValueError(f"DataWrapper matrix row index {index} must be in [0, {first_shape}]")
            new_dtype = get_dtype_tuple_child(self.dtype)
            new_memory = self.memory + index * new_dtype.size

        # Array of something
        # TODO: A CPU pointer to a GPU array will not return the right thing here but there is no way to prevent it
        #       with the current type configuration.
        else:
            if self.dtype.tuple_count == 1:
                raise ValueError(f"Array depth of simple type is limited to 1 - started from {self.shape}")
            if not 0 <= index < first_shape:
                raise ValueError(f"DataWrapper array index {index} must be in [0, {first_shape}]")
            new_dtype = self.dtype
            if self.gpu_ptr_kind == og.PtrToPtrKind.GPU:
                new_memory = self.memory + index * self.dtype.size
            else:
                ptr_type = ctypes.POINTER(ctypes.c_size_t)
                ptr = ctypes.cast(self.memory, ptr_type)
                new_memory = ptr.contents.value + index * self.dtype.size

        return DataWrapper(new_memory, new_dtype, new_shape or None, self.device, self.gpu_ptr_kind)

    def is_array(self) -> bool:
        """Checks to see if the data wrapped type is an array

        Returns:
            bool: True iff the data shape indicates that it is an arbitrary sized array of some kind
        """
        if self.shape is None:
            return False

        first_shape, *new_shape = self.shape
        new_shape = tuple(new_shape)
        # tuples have a shape like ((N,),), tuple arrays are like ((N, M),)
        if isinstance(first_shape, tuple):
            return len(first_shape) > 1
        # Simple arrays have a shape like (N,)
        if not new_shape:
            return self.dtype.tuple_count == 1
        # Matrix values have a shape like (N, M), matrix arrays are like (N, M, K)
        if self.dtype.is_matrix_type() and len(new_shape) == 1:
            return False
        # Everything that is not an array has been eliminated
        return True

    def __str__(self) -> str:
        """Representation of the wrapper showing the contents"""
        gpu_type = "GPU" if (self.gpu_ptr_kind == og.PtrToPtrKind.GPU) and self.is_array() else "CPU"
        return f"{gpu_type} Memory: {hex(self.memory)}, type {self.dtype}, shape {self.shape}, device {self.device}"
