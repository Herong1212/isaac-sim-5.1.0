"""Getting and setting values for og.Attribute and og.AttributeData"""

from enum import Enum, auto
from typing import Any, Optional, Tuple

import numpy as np
import omni.graph.core as og
import omni.graph.tools as ogt

from .attribute_types import extract_attribute_type_information
from .data_wrapper import DataWrapper, Device, data_shape_from_type
from .type_aliases import AttributeType_t, AttributeWithValue_t
from .utils import ValueToSet_t, sync_to_usd


# ==============================================================================================================
class WrappedArrayType(Enum):
    """Enum for the type of array data returned from the get methods"""

    NUMPY = auto()
    """Array data is wrapped in numpy.ndarray"""
    RAW = auto()
    """Array data is wrapped in DataWrapper"""


# ==============================================================================================================
class AttributeDataValueHelper:
    """Class to manage getting and setting of omni.graph.core.AttributeData values.

    Note that this helper sets values directly and is not generally advised for use as it has no undo support.
    Instead you probably want to use Controller or DataView

    Attributes:
        _data: The interface to the attribute data
        _type: The attribute type of the data (delay loaded to allow for extended types needing resolution)
    """

    def __init__(self, data: AttributeWithValue_t, instance=og.ACCORDING_TO_CONTEXT_GRAPH_INDEX):
        """Create an accessor to get at AttributeData values

        Args:
            data: Object type whose data is to be accessed
            instance: Index of the graph from which the attribute's value is to be accessed

        Raises:
            og.OmniGraphTypeError: if 'data' did not reference a correct attribute type
        """
        if isinstance(data, og.Attribute):
            self._data = data.get_attribute_data(instance)
        else:
            if not isinstance(data, og.AttributeData):
                raise og.OmniGraphTypeError("Only og.Attribute and og.AttributeData can be passed in")
            self._data = data
        self._type = None

    # ----------------------------------------------------------------------------------------------------
    @property
    def is_valid(self) -> bool:
        """bool: Validity of the underlying API object"""
        return self._data is not None and self._data.is_valid()

    # ----------------------------------------------------------------------------------------------------
    @property
    def is_resolved(self) -> bool:
        """bool: Does the underlying attribute have a definite resolved type?"""
        # Without attribute information we have to assume the type has been resolved
        return True

    # ----------------------------------------------------------------------------------------------------
    def check_validity(self):
        """Check the validity of the data accessor

        Raises:
            og.OmniGraphError: if the data about to be accessed is invalid"""
        if not self.is_valid:
            if self.is_resolved:
                raise og.OmniGraphError("Attempted to access an invalid object")

            raise og.OmniGraphError("Tried to get the value from an unresolved attribute")

    # ----------------------------------------------------------------------------------------------------
    @property
    def gpu_ptr_kind(self) -> og.PtrToPtrKind:
        """PtrToPtrKind: The location of pointers to GPU arrays"""
        return self._data.gpu_ptr_kind

    @gpu_ptr_kind.setter
    def gpu_ptr_kind(self, new_ptr_kind: og.PtrToPtrKind):
        """Sets the location of pointers to GPU arrays"""
        self._data.gpu_ptr_kind = new_ptr_kind

    # ----------------------------------------------------------------------------------------------------
    @property
    def type(self) -> og.Type:  # noqa: A003
        """Type: the attribute type, extracting it from the data if it hasn't already been done"""
        if self._type is None:
            self._type = extract_attribute_type_information(self._data)
        return self._type

    # ----------------------------------------------------------------------------------------------------
    @property
    def attribute_data(self) -> og.AttributeData:
        """AttributeData: the attribute data this accessor is wrapping"""
        return self._data

    # ----------------------------------------------------------------------------------------------------
    def set(self, new_value: ValueToSet_t, on_gpu: bool = False):  # noqa: A003
        """
        Set the value of AttributeData

        Args:
            new_value: New value to be set on the attribute
            on_gpu: Should the value be stored on the GPU?

        Raises:
            og.OmniGraphTypeError: Raised if the data type of the attribute is not yet supported
        """
        self.check_validity()
        _ = ogt.OGN_DEBUG and ogt.dbg(f"{self.__class__}.set({self._data.get_name()} = {new_value} GPU({on_gpu}))")

        if (self.type.array_depth > 0 or self.type.base_type == og.BaseDataType.RELATIONSHIP) and isinstance(
            new_value, (list, np.ndarray)
        ):
            self.reserve_element_count(len(new_value))
            if len(new_value) == 0:
                return
        self._data.set(new_value, on_gpu=on_gpu)

    # ----------------------------------------------------------------------------------------------------
    def get(
        self,
        on_gpu: bool = False,
        reserved_element_count: Optional[int] = None,
        return_type: Optional[WrappedArrayType] = None,
    ) -> Any:
        """
        Get the value of this attribute data.

        Args:
            on_gpu: Is the value stored on the GPU?
            reserved_element_count: For array attributes, if not None then the array will pre-reserve this many elements
            return_type: For array attributes this specifies how the return data is to be wrapped

        Returns:
            Any: Value of the attribute data

        Raises:
            og.OmniGraphAttributeError: If reserved_element_count or return_type are defined but the attribute is not
            an array type
            og.OmniGraphTypeError: Raised if the data type is not yet supported or the attribute type is not resolved
        """
        self.check_validity()
        _ = ogt.OGN_DEBUG and ogt.dbg(
            f"AttributeDataValueHelper.get({self._data.get_name()} GPU({on_gpu})"
            f" RESERVED({reserved_element_count}) TYPE({return_type}))"
        )

        if self.type.array_depth > 0 or self.type.base_type == og.BaseDataType.RELATIONSHIP:
            writing = (
                reserved_element_count is not None and reserved_element_count > 0 and not self._data.is_read_only()
            )
            raw_data = self._data.get_array(
                on_gpu=on_gpu,
                get_for_write=writing,
                reserved_element_count=reserved_element_count if writing else 0,
            )
            if return_type is None:
                return_type = WrappedArrayType.RAW if on_gpu else WrappedArrayType.NUMPY

            if return_type == WrappedArrayType.NUMPY:
                if on_gpu:
                    raise og.OmniGraphTypeError("numpy data cannot be returned for GPU data")
                return raw_data
            if not on_gpu:
                raise og.OmniGraphTypeError("Only numpy data can be returned for CPU data")

            (memory_location, element_count) = raw_data
            (dtype, shape) = data_shape_from_type(self.type)
            # The array size was a placeholder; put the real size in
            _, *shape_info = shape
            shape = (element_count, *shape_info)
            return DataWrapper(memory_location, dtype, shape, Device("cuda"), self.gpu_ptr_kind)

        # While we could recover from these bad parameters we don't want to encourage their incorrect use
        if reserved_element_count is not None:
            raise og.OmniGraphAttributeError(
                f"Specified a reserved element count of {reserved_element_count} on"
                f" non-array attribute {self._data.get_name()}"
            )
        if return_type is not None:
            raise og.OmniGraphAttributeError(
                f"Return types like {return_type} are not legal on non-array attribute {self._data.get_name()}"
            )

        raw_data = self._data.get(on_gpu=on_gpu)

        if on_gpu:
            (dtype, shape) = data_shape_from_type(self.type)
            return DataWrapper(raw_data, dtype, shape, Device("cuda"), self.gpu_ptr_kind)

        return raw_data

    # ----------------------------------------------------------------------------------------------------
    def get_array_size(self) -> int:
        """
        Get the length of this attribute data's array.

        Returns:
            int: Length of the data array in Fabric

        Raises:
            og.OmniGraphAttributeError: If the array is not an array type
        """
        self.check_validity()
        _ = ogt.OGN_DEBUG and ogt.dbg(f"AttributeDataValueHelper.get_array_size({self._data.get_name()}")

        if self.type.array_depth == 0 and self.type.base_type != og.BaseDataType.RELATIONSHIP:
            raise og.OmniGraphAttributeError(
                f"Attempted to get array size of non-array attribute {self._data.get_name()}"
            )
        return self._data.size()

    # ----------------------------------------------------------------------------------------------------
    def reserve_element_count(self, new_element_count: int):
        """
        Set the length of this attribute data's array. It doesn't matter whether the data will be on the GPU or CPU,
        all this does is reserve the size number. When retrieving the data you will specify where it lives.

        Args:
            new_element_count: Number of array elements to reserve for the array

        Raises:
            og.OmniGraphAttributeError: If the array is not an array type
        """
        self.check_validity()
        _ = ogt.OGN_DEBUG and ogt.dbg(f"AttributeDataValueHelper.reserve_element_count({self._data.get_name()}")

        if self.type.array_depth == 0 and self.type.base_type != og.BaseDataType.RELATIONSHIP:
            raise og.OmniGraphAttributeError(
                f"Attempted to set array size of non-array attribute {self._data.get_name()}"
            )
        self._data.resize(new_element_count)

    # ----------------------------------------------------------------------------------------------------
    @ogt.deprecated_function("After version 1.5.0 use get() instead")
    def get_array(
        self,
        get_for_write: bool,
        reserved_element_count: int = 0,
        on_gpu: bool = False,
        return_type: Optional[WrappedArrayType] = None,
    ) -> Any:
        """Deprecated - use get()"""
        coded_count = reserved_element_count if get_for_write else None
        return self.get(on_gpu=on_gpu, reserved_element_count=coded_count, return_type=return_type)


# ====================================================================================================
class AttributeValueHelper(AttributeDataValueHelper):
    """Class to manage getting and setting of Attribute values.
    You can also just use AttributeDataValueHelper directly.
    """

    def __init__(self, attribute: og.Attribute, instance=og.ACCORDING_TO_CONTEXT_GRAPH_INDEX):
        """Create a helper class to access Attribute values

        Args:
            attribute: Attribute whose value will be accessed
            instance: Index of the graph from which the attribute's value is to be accessed
        """
        super().__init__(attribute, instance)
        self.__attribute = attribute

    # ----------------------------------------------------------------------------------------------------
    @property
    def attribute(self) -> og.Attribute:
        """Attribute: the attribute this helper is wrapping"""
        return self.__attribute

    # ----------------------------------------------------------------------------------------------------
    @property
    def is_resolved(self) -> bool:
        """bool: Does the underlying attribute have a definite resolved type?"""
        return (
            self.__attribute is not None
            and self.__attribute.is_valid()
            and self.__attribute.get_resolved_type().base_type != og.BaseDataType.UNKNOWN
        )

    # ----------------------------------------------------------------------------------------------------
    @property
    def is_valid(self) -> bool:
        """bool: Validity of the underlying API object"""
        return self.__attribute is not None and self.__attribute.is_valid() and super().is_valid

    # ----------------------------------------------------------------------------------------------------
    @property
    def type(self) -> og.Type:  # noqa: A003
        """Type: the attribute type, extracting it from the data if it hasn't already been done"""
        if self._type is None:
            self._type = extract_attribute_type_information(self.__attribute)
        return self._type

    # ----------------------------------------------------------------------------------------------------
    def resolve_type(self, type_id: AttributeType_t):
        """Resolves the attribute type, usually before setting an explicit value.

        Args:
            type: Attribute type to which the attribute will be resolved.

        Raises:
            OmniGraphError: If the attribute could not (or should not) be resolved
        """
        if self.__attribute.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
            raise og.OmniGraphError(
                f"Attempted to resolve non-extended attribute {self.__attribute.get_name()} to {type_id}"
            )
        value_type = og.ObjectLookup.attribute_type(type_id)
        resolved_type = self.__attribute.get_resolved_type()

        # No need to do anything if the resolved type is already the desired one
        if value_type != resolved_type:
            self.__attribute.set_resolved_type(value_type)
            if value_type != self.attribute.get_resolved_type():
                raise og.OmniGraphTypeError(f"{self.__attribute.get_name()} cannot be set to {value_type}")

            # Resolving the type changes the data information so fix it up
            self._type = None
            self._data = self.__attribute.get_attribute_data()

    # ----------------------------------------------------------------------------------------------------
    def set(self, new_value: ValueToSet_t, on_gpu: bool = False, update_usd: bool = False):  # noqa: A003
        """
        Set the value of the attribute. This is overridden so that it can include an explicit type for the data,
        which can be used to resolve the attribute type (only valid for extended types)

        Args:
            new_value: New value to be set on the attribute
            on_gpu: Should the value be stored on the GPU?
            update_usd: Should the value be immediately propagated to USD?

        Raises:
            og.OmniGraphError: Raised if the data type of the attribute is not yet supported
        """
        _ = ogt.OGN_DEBUG and ogt.dbg(
            f"AttributeValueHelper.set({self.__attribute.get_name()} = {new_value} GPU({on_gpu}))"
        )

        def __get_type_and_value(value_information: ValueToSet_t) -> Optional[Tuple[Any, str]]:
            """Extracts type and value information from the data, or None if it's just a value with no type.
            Raises og.OmniGraphError if the dictionary or tuple types were not legal.
            Returns None if the value had no type encoding.
            """
            if isinstance(value_information, dict):
                if len(value_information) != 2 or "type" not in value_information or "value" not in value_information:
                    raise og.OmniGraphError(
                        f"Explicit type dictionary must contain 'type' and 'value' only - get {value_information}"
                    )
                return (value_information["value"], value_information["type"])
            if isinstance(value_information, og.TypedValue):
                return (value_information.value, value_information.type)
            return None

        # First set the resolved type, if setting a type was requested
        try:
            encoded_value = __get_type_and_value(new_value)
            if encoded_value is not None:
                (new_value, value_type_id) = encoded_value
                self.resolve_type(value_type_id)
        except og.OmniGraphError as error:
            raise og.OmniGraphTypeError() from error

        # This could have also called the parent class set() but that doesn't send out notifications to the graph
        # so it must handle it.
        self.check_validity()

        if (self.type.array_depth > 0 or self.type.base_type == og.BaseDataType.RELATIONSHIP) and isinstance(
            new_value, (list, np.ndarray)
        ):
            self.reserve_element_count(len(new_value))
            if len(new_value) == 0:
                return
        self.__attribute.set(new_value, on_gpu=on_gpu)

        if update_usd:
            # process any pending usd updates for extended attributes
            og._internal.flush_usd()  # noqa: PLW0212
            if self.__attribute.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
                # TODO: This is necessary to update USD at the moment. It would be more efficient if this were handled
                #       at the fabric level, or at least at the Attribute or AttributeData level.
                sync_to_usd(self.__attribute, new_value)
                # rerun to reflect any pending updates
                og._internal.flush_usd()  # noqa: PLW0212
