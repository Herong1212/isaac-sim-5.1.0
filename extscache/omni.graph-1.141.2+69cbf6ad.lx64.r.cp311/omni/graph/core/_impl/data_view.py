"""Helper class to access data values from the graph. Is also encapsulated in the all-purpose og.Helper class."""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import omni.graph.core as og

from .attribute_values import AttributeDataValueHelper, AttributeValueHelper, WrappedArrayType
from .errors import OmniGraphError
from .object_lookup import ObjectLookup
from .type_aliases import AttributeWithValue_t
from .utils import ValueToSet_t, _flatten_arguments, _Unspecified, is_in_compute


# ==============================================================================================================
class DataView:
    """Helper class for getting and setting attribute data values. The setting operation is undoable.

    Interfaces:
        force_usd_update
        get
        get_array_size
        gpu_ptr_kind
        set

    All of the interface functions can either be called from an instantiation of this object or from a class method
    of the same name with an added attribute parameter that tells where to get and set values.
    """

    __ALWAYS_UPDATE_USD = False
    """Global override to indicate that all calls to set() should force the update to USD"""

    # --------------------------------------------------------------------------------------------------------------
    # Context manager to temporarily enable forcing of USD updates, used as follows:
    #    with og.DataView.force_usd_update(True):
    #        do_something_requiring_usd_update()
    @classmethod
    @contextmanager
    def force_usd_update(cls, force_update: bool = True):
        original_update = cls.__ALWAYS_UPDATE_USD
        try:
            cls.__ALWAYS_UPDATE_USD = force_update
            yield
        finally:
            cls.__ALWAYS_UPDATE_USD = original_update

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def __get_value_helper(  # noqa: PLW0238
        cls, attribute: AttributeWithValue_t, instance=og.ACCORDING_TO_CONTEXT_GRAPH_INDEX
    ) -> AttributeDataValueHelper:
        """Returns a value manipulation helper that can get and set values on the given attribute or attributeData"""
        if isinstance(attribute, og.AttributeData):
            return AttributeDataValueHelper(attribute)
        return AttributeValueHelper(ObjectLookup.attribute(attribute), instance)

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initializes the data view class to prepare it for evaluting or setting an attribute value,
        The arguments are flexible so that you can either construct an object that will persist its settings across
        all method calls, or you can pass in overrides to the method calls to use instead. In the case of classmethod
        calls the values passed in will be the only ones used.

        The "attribute" value can be used by keyword or positionally. All other arguments must specify their keyword.

        .. code-block:: python

            og.Controller(update_usd=True)  # Good
            og.Controller("inputs:attr")  # Good
            og.Controller(update_usd=True, attribute="inputs:attr")  # Good
            og.Controller("inputs:attr", True)  # Bad

        Args:
             attribute: (AttributeWithValue_t) Description of an attribute object with data that can be accessed
             update_usd: (bool) Should the modification to the value immediately update the USD? Defaults to True
             undoable: (bool) Is the modification to the value undoable? Defaults to True
             on_gpu: (bool) Is the data being modified on the GPU? Defaults to True
             gpu_ptr_kind: (og.PtrToPtrKind) How should GPU array data be returned? Defaults to True
             instance: (int) When working with instantiated graphs, an index representing the instance
        """
        (
            self.__attribute,
            self.__update_usd,
            self.__undoable,
            self.__on_gpu,
            self.__gpu_ptr_kind,
            self.__instance,
        ) = _flatten_arguments(
            optional=[
                ("attribute", None),
                ("update_usd", self.__ALWAYS_UPDATE_USD),
                ("undoable", True),
                ("on_gpu", False),
                ("gpu_ptr_kind", og.PtrToPtrKind.GPU),
                ("instance", og.ACCORDING_TO_CONTEXT_GRAPH_INDEX),
            ],
            args=args,
            kwargs=kwargs,
        )

        # Dual function methods that can be called either from an object or directly from the class
        self.get = self.__get_obj
        self.get_array_size = self.__get_array_size_obj
        self.set = self.__set_obj

    # ----------------------------------------------------------------------------------------------------
    @property
    def gpu_ptr_kind(self) -> og.PtrToPtrKind:
        """PtrToPtrKind: The memory location of pointers to GPU arrays"""
        return self.__gpu_ptr_kind

    @gpu_ptr_kind.setter
    def gpu_ptr_kind(self, new_ptr_kind: og.PtrToPtrKind):
        """Sets the location of pointers to GPU arrays"""
        self.__gpu_ptr_kind = new_ptr_kind

    # ----------------------------------------------------------------------
    @classmethod
    def get(obj, *args, **kwargs) -> Any:  # noqa: N804,PLC0202,PLE0202
        """Returns the current value on the owned attribute.

        This function can be called either from the class or using an instantiated object. The first argument is
        mandatory, being either the class or object. All others are by keyword or by position and optional, defaulting
        to the value set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            attribute: Attribute whose value is to be retrieved. If used in an object context and a value was provided
                       in the constructor then this value overrides that value. It's mandatory, so if it was not
                       provided in the constructor or here then an error is raised.
            on_gpu: Is the value stored on the GPU?
            reserved_element_count: For array attributes, if not None then the array will pre-reserve this many elements
            return_type: For array attributes this specifies how the return data is to be wrapped.
            gpu_ptr_kind: Type of data to return for GPU arrays (only used if on_gpu=True)
            instance: When working with instantiated graphs, an index representing the instance

        Raises:
            OmniGraphError: If the current attribute is not valid or its value could not be retrieved
        """
        return obj.__get(obj, args=args, kwargs=kwargs)

    def __get_obj(self, *args, **kwargs) -> Any:
        """Implements :py:meth:`.DataView.get` when called as an object method"""
        return self.__get(
            self,
            attribute=self.__attribute,
            on_gpu=self.__on_gpu,
            gpu_ptr_kind=self.__gpu_ptr_kind,
            instance=self.__instance,
            args=args,
            kwargs=kwargs,
        )

    @staticmethod
    def __get(
        obj,
        attribute: AttributeWithValue_t = _Unspecified,
        on_gpu: bool = False,
        reserved_element_count: Optional[int] = None,
        return_type: Optional[WrappedArrayType] = None,
        gpu_ptr_kind: Optional[og.PtrToPtrKind] = None,
        instance=og.ACCORDING_TO_CONTEXT_GRAPH_INDEX,
        args: List[str] = None,
        kwargs: Dict[str, Any] = None,
    ) -> Any:
        """Implements :py:meth:`.DataView.get`"""
        (attribute, on_gpu, reserved_element_count, return_type, gpu_ptr_kind, instance) = _flatten_arguments(
            mandatory=[("attribute", attribute)],
            optional=[
                ("on_gpu", on_gpu),
                ("reserved_element_count", reserved_element_count),
                ("return_type", return_type),
                ("gpu_ptr_kind", gpu_ptr_kind),
                ("instance", instance),
            ],
            args=args,
            kwargs=kwargs,
        )
        helper = obj.__get_value_helper(attribute, instance)  # noqa: PLW0212
        if helper is None:
            raise OmniGraphError(f"Could not retrieve a value helper class for attribute {attribute}")
        if gpu_ptr_kind is not None:
            helper.gpu_ptr_kind = gpu_ptr_kind
        return helper.get(on_gpu=on_gpu, reserved_element_count=reserved_element_count, return_type=return_type)

    # ----------------------------------------------------------------------
    @classmethod
    def get_array_size(obj, *args, **kwargs) -> int:  # noqa: N804,PLC0202,PLE0202
        """Returns the current number of array elements on the owned attribute.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how get_array_size() was called
            attribute: Attribute whose size is to be retrieved. If used in an object context and a value was provided
                       in the constructor then this value overrides that value. It's mandatory, so if it was not
                       provided in the constructor or here then an error is raised.

        Raises:
            OmniGraphError: If the current attribute is not valid or is not an array type
        """
        return obj.__get_array_size(obj, args=args, kwargs=kwargs)

    def __get_array_size_obj(self, *args, **kwargs) -> Any:
        """Implements :py:meth:`.DataView.get_array_size` when called as an object method"""
        return self.__get_array_size(self, attribute=self.__attribute, args=args, kwargs=kwargs)

    @staticmethod
    def __get_array_size(
        obj,
        attribute: AttributeWithValue_t = None,
        args: List[str] = None,
        kwargs: Dict[str, Any] = None,
        instance=og.ACCORDING_TO_CONTEXT_GRAPH_INDEX,
    ) -> int:
        """Implements :py:meth:`.DataView.get_array_size`"""
        (attribute,) = _flatten_arguments(
            optional=[("attribute", attribute)],
            args=args,
            kwargs=kwargs,
        )
        helper = obj.__get_value_helper(attribute, instance)  # noqa: PLW0212
        if helper is None:
            raise OmniGraphError(f"Could not retrieve a value helper class for attribute {attribute}")
        return helper.get_array_size()

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def set(obj, *args, **kwargs) -> bool:  # noqa: N804,PLE0202,PLC0202, A003
        """Sets the current value on the owned attribute. This is an undoable action.

        This function can be called either from the class or using an instantiated object. Both the attribute and
        value argument are mandatory and will raise an error if omitted. The attribute value may optionally be set
        through the constructor instead, if this function is called from an object context. These arguments may be set
        positionally or by keyword. The remaining arguments are optional but must be specified by keyword only. In an
        object context the defaults will be taken from the constructor, else they will use the function defaults.

        .. code-block:: python

            og.Controller.set("inputs:attr", new_value)  # Good
            og.Controller("inputs:attr").set(new_value)  # Good
            og.Controller.set("inputs:attr")  # Bad - missing value
            og.Controller.set("inputs:attr", new_value, undoable=False)  # Good
            og.Controller("inputs:attr", undoable=False).set(new_value)  # Good

        Args:
            obj: Either cls or self depending on how the function was called
            attribute: Attribute whose value is to be set. If used in an object context and a value was provided
                       in the constructor then this value overrides that value. It's mandatory, so if it was not
                       provided in the constructor or here then an error is raised.
            value: The new value for the attribute. It's mandatory, so if it was not provided in the constructor or
                   here then an error is raised.
            on_gpu: Is the value stored on the GPU?
            update_usd: Should the value immediately propagate to USD?
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
            gpu_ptr_kind: Type of data to expect for GPU arrays (only used if on_gpu=True)

        Returns:
            bool: True if the value was set successfully

        Raises:
            OmniGraphError: If the current attribute is not valid or could not be set to the given value
        """
        return obj.__set(obj, args=args, kwargs=kwargs)

    def __set_obj(self, *args, **kwargs) -> bool:
        """Implements :py:meth:`.DataView.set` when called as an object method"""
        # Handle the special case of an args list that omits the attribute when it was constructed with an
        # existing attribute.
        if self.__attribute is not None and args and not isinstance(args[0], og.Attribute):
            args = [self.__attribute, *args]
        return self.__set(
            self,
            attribute=self.__attribute,
            on_gpu=self.__on_gpu,
            update_usd=self.__update_usd,
            gpu_ptr_kind=self.__gpu_ptr_kind,
            undoable=self.__undoable,
            args=args,
            kwargs=kwargs,
        )

    @staticmethod
    def __set(
        obj,
        attribute: AttributeWithValue_t = _Unspecified,
        value: ValueToSet_t = _Unspecified,
        on_gpu: bool = False,
        update_usd: bool = False,
        gpu_ptr_kind: Optional[og.PtrToPtrKind] = None,
        undoable: bool = True,
        args: List[str] = None,
        kwargs: Dict[str, Any] = None,
    ) -> bool:
        """Implements :py:meth:`DataView.set`"""
        (attribute, value, on_gpu, update_usd, gpu_ptr_kind, undoable) = _flatten_arguments(
            mandatory=[("attribute", attribute), ("value", value)],
            optional=[
                ("on_gpu", on_gpu),
                ("update_usd", update_usd),
                ("gpu_ptr_kind", gpu_ptr_kind),
                ("undoable", undoable),
            ],
            args=args,
            kwargs=kwargs,
        )
        if not isinstance(attribute, og.AttributeData):
            attribute = og.ObjectLookup.attribute(attribute)
        if is_in_compute() or not undoable:
            if isinstance(attribute, og.Attribute):
                og.cmds.imm.SetAttr(attribute, value, on_gpu, update_usd)
            else:
                og.cmds.imm.SetAttrData(attribute, value, on_gpu)
            success = True
        elif isinstance(attribute, og.Attribute):
            (success, _) = og.cmds.SetAttr(attr=attribute, value=value, on_gpu=on_gpu, update_usd=update_usd)
        else:
            (success, _) = og.cmds.SetAttrData(attribute_data=attribute, value=value, on_gpu=on_gpu)

        if not success:
            raise OmniGraphError(f"Failed to set value of '{value}' on attribute data '{attribute.get_name()}'")
        return success
