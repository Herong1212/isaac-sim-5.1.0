from __future__ import annotations
import omni.core._core
import typing

__all__ = [
    "Float2",
    "IObject",
    "ITypeFactory",
    "Int2",
    "Result",
    "TypeFactoryLoadFlags",
    "UInt2",
    "create_type",
    "register_module"
]


class Float2():
    """
    Helper struct to represent a single 2-space vector of floating point values.  Each member of
     the struct can be accessed in multiple ways including an array and direct accessors known
     by multiple names.  Objects of this struct are guaranteed to be only as large as two
     32-bit floating point values.
    """
    def __eq__(self, arg0: Float2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    @typing.overload
    def __init__(self, x: float, y: float) -> None: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __str__(self) -> str: ...
    @property
    def h(self) -> float:
        """
        /< Provides access to the first data member as a height value.

        :type: float
        """
    @h.setter
    def h(self, arg0: float) -> None:
        """
        /< Provides access to the first data member as a height value.
        """
    @property
    def s(self) -> float:
        """
        /< Provides access to the first data member as an S texture coordinate.

        :type: float
        """
    @s.setter
    def s(self, arg0: float) -> None:
        """
        /< Provides access to the first data member as an S texture coordinate.
        """
    @property
    def t(self) -> float:
        """
        /< Provides access to the first data member as an T texture coordinate.

        :type: float
        """
    @t.setter
    def t(self, arg0: float) -> None:
        """
        /< Provides access to the first data member as an T texture coordinate.
        """
    @property
    def u(self) -> float:
        """
        /< Provides access to the first data member as a U texture coordinate.

        :type: float
        """
    @u.setter
    def u(self, arg0: float) -> None:
        """
        /< Provides access to the first data member as a U texture coordinate.
        """
    @property
    def v(self) -> float:
        """
        /< Provides access to the first data member as a V texture coordinate.

        :type: float
        """
    @v.setter
    def v(self, arg0: float) -> None:
        """
        /< Provides access to the first data member as a V texture coordinate.
        """
    @property
    def w(self) -> float:
        """
        /< Provides access to the first data member as a width value.

        :type: float
        """
    @w.setter
    def w(self, arg0: float) -> None:
        """
        /< Provides access to the first data member as a width value.
        """
    @property
    def x(self) -> float:
        """
        Provides access to the first data member as a Cartesian X coordinate. 

        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        """
        Provides access to the first data member as a Cartesian X coordinate. 
        """
    @property
    def y(self) -> float:
        """
        Provides access to the first data member as a Cartesian Y coordinate. 

        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        """
        Provides access to the first data member as a Cartesian Y coordinate. 
        """
    __hash__ = None
    pass
class ITypeFactory(_ITypeFactory, IObject):
    """
    A mapping from type id's to implementations.

    This object maps type id's to concrete implementations.  The type id's can represent interface ids or implementation
    ids.

    Register types with registerInterfaceImplementationsFromModule() and registerInterfaceImplementations().

    Instantiate types with omni::core::createType(). This is the primary way Omniverse applications are able to
    instantiate concrete implementations of @rstref{ABI-safe <abi-compatibility>} interfaces.  See
    omni::core::createType() for a helpful wrapper around omni::core::ITypeFactory::createType().

    In practice, there will be a single ITypeFactory active in the process space (accessible via
    omniGetTypeFactoryWithoutAcquire()).  However, @ref omni::core::ITypeFactory is not inherently a singleton, and as
    such multiple instantiations of the interface may exists.  This can be used to create private type trees.

    Unless otherwise noted, all methods in this interface are thread safe.
    """
    @typing.overload
    def __init__(self, arg0: IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def get_type_id_name(self, id: int) -> str: 
        """
        Maps a type id back to its type name.

        The memory returned is valid for the lifetime of ITypeFactory

        Returns nullptr if id has never been registered. Types that have been registered, and then unregistered, will
        still have a valid string returned from this method.

        This method is thread safe.
        """
    def register_interface_implementations_from_module(self, module_name: str, flags: int) -> int: 
        """
        Registers types from the given module.

        If the module is currently loaded, it will not be reloaded and kResultSuccess is returned.

        "omniModuleGetExports" returns a key/value database of the module's capabilities and the module's requirements.
        Some things to note about this database:

          - The module's requirements can be marked as optional.

          - The module's capabilities can be ignored by ITypeFactory.

        These properties allow ITypeFactory and the module to find an intersection of desired functionality in a data
        driven manner.  If one party's required needs are not met, the module fails to load (e.g. an appropriate
        omni::core::Result is returned).

        It is expected the module has entries in the key/value database describing the functions ITypeFactory should
        call during the loading process.  The most important of these entries is the one defined by
        OMNI_MODULE_ON_MODULE_LOAD(), which points to the function ITypeFactory should call to get a list of
        implementations in the module.  ITypeFactory invokes exports from the module in the following pattern:


        .. code-block:: text

          .------------------------------------------------------------------------------------------------------------.
          |                                               -> Time ->                                                   |
          |------------------------------------------------------------------------------------------------------------|
          | omniModuleGetExports | onLoad (req.) | onStarted (optional) | onCanUnload (optional) | onUnload (optional) |
          |                      |               | impl1->createFn      |                        |                     |
          |                      |               | impl2->createFn      |                        |                     |
          |                      |               | impl1->createFn      |                        |                     |
          \\------------------------------------------------------------------------------------------------------------/


        Above, functions in the same column can be called concurrently. It's up to the module to make sure such call
        patterns are thread safe within the module.

        onCanUnload and createFn can be called multiple times.  All other functions are called once during the lifecycle
        of a module.

        \\see omni/core/ModuleExports.h.
        \\see onModuleLoadFn
        \\see onModuleStartedFn
        \\see onModuleCanUnloadFn
        \\see onModuleUnloadFn


        The module can be explicitly unloaded with unregisterInterfaceImplementationsFromModule().

        Upon destruction of this ITypeFactory, unregisterInterfaceImplementationsFromModule is called for each loaded
        module.  If the ITypeFactory destructor's call to unregisterInterfaceImplementationsFromModule fails to safely
        unload a module (via the module's onModuleCanUnload and onModuleUnload), an attempt will be made to
        forcefully/unsafely unload the module.

        The given module name must not be nullptr.

        This method is thread safe. Modules can be loaded in parallel.

        \\returns Returns kResultSuccess if the module is loaded (either due to this function or a previous call).
        Otherwise, an error is returned.
        """
    def set_interface_defaults(self, interface_id: int, impl_id: int, module_name: str, impl_version: int) -> None: 
        """
        Sets the implementation matching constraints for the given interface id.

        See omni::core::ITypeFactory_abi::createType_abi() for how these constraints are used.

        moduleName can be nullptr.

        if implVersion is 0 and implId is an implementation id, the implementation with the highest version is chosen.

        This method is thread safe.
        """
    def unregister_interface_implementations_from_module(self, module_name: str) -> int: 
        """
        Unregisters all types registered from the given module.

        Unregistering a module may fail if the module does not belief it can safely be unloaded. This is determined by
        OMNI_MODULE_ON_MODULE_CAN_UNLOAD().

        If unregistration does succeed, the given module will be unloaded from the process space.

        Upon destruction of this ITypeFactory, unregisterInterfaceImplementationsFromModule is called for each loaded
        module.  If the ITypeFactory destructor's call to unregisterInterfaceImplementationsFromModule fails to safely
        unload a module (via the module's onModuleCanUnload and onModuleUnload), an attempt will be made to
        forcefully/unsafely unload the module.

        The given module name must not be nullptr.

        This method is thread safe.

        \\returns Returns kResultSuccess if the module wasn't already loaded or if this method successfully unloaded the
        module. Return an error code otherwise.
        """
    pass
class IObject():
    pass
class Int2():
    """
    Helper struct to represent a single 2-space vector of signed integers.  Each member of
     the struct can be accessed in multiple ways including an array and direct accessors known
     by multiple names.  Objects of this struct are guaranteed to be only as large as two
     32-bit signed integers.
    """
    def __eq__(self, arg0: Int2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    @typing.overload
    def __init__(self, x: int, y: int) -> None: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __str__(self) -> str: ...
    @property
    def h(self) -> int:
        """
        /< Provides access to the first data member as a height value.

        :type: int
        """
    @h.setter
    def h(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a height value.
        """
    @property
    def s(self) -> int:
        """
        /< Provides access to the first data member as an S texture coordinate.

        :type: int
        """
    @s.setter
    def s(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as an S texture coordinate.
        """
    @property
    def t(self) -> int:
        """
        /< Provides access to the first data member as an T texture coordinate.

        :type: int
        """
    @t.setter
    def t(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as an T texture coordinate.
        """
    @property
    def u(self) -> int:
        """
        /< Provides access to the first data member as a U texture coordinate.

        :type: int
        """
    @u.setter
    def u(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a U texture coordinate.
        """
    @property
    def v(self) -> int:
        """
        /< Provides access to the first data member as a V texture coordinate.

        :type: int
        """
    @v.setter
    def v(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a V texture coordinate.
        """
    @property
    def w(self) -> int:
        """
        /< Provides access to the first data member as a width value.

        :type: int
        """
    @w.setter
    def w(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a width value.
        """
    @property
    def x(self) -> int:
        """
        Provides access to the first data member as a Cartesian X coordinate. 

        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        """
        Provides access to the first data member as a Cartesian X coordinate. 
        """
    @property
    def y(self) -> int:
        """
        Provides access to the first data member as a Cartesian Y coordinate. 

        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        """
        Provides access to the first data member as a Cartesian Y coordinate. 
        """
    __hash__ = None
    pass
class Result():
    """
    Error code for the result of an operation.

    The numeric encoding for values follows Microsoft's
    <a
    href="https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/0642cb2f-2075-4469-918c-4441e69c548a">
    HRESULT</a> scheme. Many values are direct copies of those from the Windows API, such as ``kResultNotImplemented.``
    Codes which are NVIDIA-provided, will have the mask ``0xa4310000.`` This comes from setting the "customer bit" (bit
    at most-significant index 2) and having a "facility" (bits from index 5-15) of ``0b10000110001`` aka ``0x431`` (which
    is ``"NVDA"`` in Morse Code).

    Members:

      SUCCESS : Operation successful. No error occurred.

      NOT_IMPLEMENTED : The feature or method was not implemented. It might be at some point in the future.

      OPERATION_ABORTED : The operation was aborted.

      FAIL : The operation failed. * Decimal Value: -2147467259

      NOT_FOUND : The item was not found. * Decimal Value: -2147024894

      ACCESS_DENIED : Access has been denied for this operation.

      OUT_OF_MEMORY : A system is out of memory. This does not necessarily mean resident memory has been exhausted (although it can), as this code can be used to special conditions such as exhausting graphics memory or running out of a specific memory pool. It can also indicate that an allocation would have been too big and failed ahead of time.

      NOT_SUPPORTED : The operation is not supported. * Decimal Value: -2147024846

      INVALID_ARGUMENT : One or more of the arguments passed to a given function was invalid.

      INVALID_STATE : The system is in an invalid state to perform the operation. This is distinct from ``kResultInvalidOperation`` in that it covers situations like "system is not yet started" or "file is closed." * Decimal Value: -2147024892

      VERSION_CHECK_FAILURE : Version check failure. * Decimal Value: -2147024253

      VERSION_PARSE_ERROR : Failed to parse the version. * Decimal Value: -2147024119

      INSUFFICIENT_BUFFER : Insufficient buffer. * Decimal Value: -2147024774

      TRY_AGAIN : Try the operation again.

      INTERRUPTED : An operation was interrupted. An "interruption" happens in cases where the operation did not complete successfully due to an outside system (such as a timer) interrupting it. For example, a function ``Result wait_for(duration d)`` might give ``kResultSuccess`` when function returns because the duration expired and ``kResultInterrupted`` if the system is shutting down.

      NO_INTERFACE : Interface not implemented. * Decimal Value: -2147467262

      NULL_POINTER : Pointer is null.

      ALREADY_EXISTS : Object already exists.

      INVALID_OPERATION : The operation was not valid for the target. For example, attempting to perform a write operation on a read-only file would result in this error.

      NO_MORE_ITEMS : No more items to return. This is meant for things like reader queues when they have run out of data and will never have more data. For cases where something like an async queue being temporarily empty, use ``kResultTryAgain.``

      INVALID_INDEX : Invalid index.

      NOT_ENOUGH_DATA : Not enough data.

      TOO_MUCH_DATA : Too much data.

      INVALID_DATA_TYPE : Invalid data type. This is used in cases where a specific type of data is requested, but that is not the data which the receiver has.

      INVALID_DATA_SIZE : Invalid data size. This arises when the correct type of data is requested, but the requester believes the data size is different from the receiver. The cause of this is typically a version mismatch.

      TIMED_OUT : Timed out.

      WOULD_BLOCK : Would block.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ACCESS_DENIED: omni.core._core.Result # value = <Result.ACCESS_DENIED: -2147024891>
    ALREADY_EXISTS: omni.core._core.Result # value = <Result.ALREADY_EXISTS: -2147286960>
    FAIL: omni.core._core.Result # value = <Result.FAIL: -2147467259>
    INSUFFICIENT_BUFFER: omni.core._core.Result # value = <Result.INSUFFICIENT_BUFFER: -2147024774>
    INTERRUPTED: omni.core._core.Result # value = <Result.INTERRUPTED: -1540292607>
    INVALID_ARGUMENT: omni.core._core.Result # value = <Result.INVALID_ARGUMENT: -2147024809>
    INVALID_DATA_SIZE: omni.core._core.Result # value = <Result.INVALID_DATA_SIZE: -2144272372>
    INVALID_DATA_TYPE: omni.core._core.Result # value = <Result.INVALID_DATA_TYPE: -2144272373>
    INVALID_INDEX: omni.core._core.Result # value = <Result.INVALID_INDEX: -2146889720>
    INVALID_OPERATION: omni.core._core.Result # value = <Result.INVALID_OPERATION: -2147020579>
    INVALID_STATE: omni.core._core.Result # value = <Result.INVALID_STATE: -2147024892>
    NOT_ENOUGH_DATA: omni.core._core.Result # value = <Result.NOT_ENOUGH_DATA: -2144796415>
    NOT_FOUND: omni.core._core.Result # value = <Result.NOT_FOUND: -2147024894>
    NOT_IMPLEMENTED: omni.core._core.Result # value = <Result.NOT_IMPLEMENTED: -2147467263>
    NOT_SUPPORTED: omni.core._core.Result # value = <Result.NOT_SUPPORTED: -2147024846>
    NO_INTERFACE: omni.core._core.Result # value = <Result.NO_INTERFACE: -2147467262>
    NO_MORE_ITEMS: omni.core._core.Result # value = <Result.NO_MORE_ITEMS: -2146893782>
    NULL_POINTER: omni.core._core.Result # value = <Result.NULL_POINTER: -2147467261>
    OPERATION_ABORTED: omni.core._core.Result # value = <Result.OPERATION_ABORTED: -2147467260>
    OUT_OF_MEMORY: omni.core._core.Result # value = <Result.OUT_OF_MEMORY: -2147024882>
    SUCCESS: omni.core._core.Result # value = <Result.SUCCESS: 0>
    TIMED_OUT: omni.core._core.Result # value = <Result.TIMED_OUT: -1540282548>
    TOO_MUCH_DATA: omni.core._core.Result # value = <Result.TOO_MUCH_DATA: -2144796414>
    TRY_AGAIN: omni.core._core.Result # value = <Result.TRY_AGAIN: -2147020693>
    VERSION_CHECK_FAILURE: omni.core._core.Result # value = <Result.VERSION_CHECK_FAILURE: -2147024253>
    VERSION_PARSE_ERROR: omni.core._core.Result # value = <Result.VERSION_PARSE_ERROR: -2147024119>
    WOULD_BLOCK: omni.core._core.Result # value = <Result.WOULD_BLOCK: -1540282573>
    __members__: dict # value = {'SUCCESS': <Result.SUCCESS: 0>, 'NOT_IMPLEMENTED': <Result.NOT_IMPLEMENTED: -2147467263>, 'OPERATION_ABORTED': <Result.OPERATION_ABORTED: -2147467260>, 'FAIL': <Result.FAIL: -2147467259>, 'NOT_FOUND': <Result.NOT_FOUND: -2147024894>, 'ACCESS_DENIED': <Result.ACCESS_DENIED: -2147024891>, 'OUT_OF_MEMORY': <Result.OUT_OF_MEMORY: -2147024882>, 'NOT_SUPPORTED': <Result.NOT_SUPPORTED: -2147024846>, 'INVALID_ARGUMENT': <Result.INVALID_ARGUMENT: -2147024809>, 'INVALID_STATE': <Result.INVALID_STATE: -2147024892>, 'VERSION_CHECK_FAILURE': <Result.VERSION_CHECK_FAILURE: -2147024253>, 'VERSION_PARSE_ERROR': <Result.VERSION_PARSE_ERROR: -2147024119>, 'INSUFFICIENT_BUFFER': <Result.INSUFFICIENT_BUFFER: -2147024774>, 'TRY_AGAIN': <Result.TRY_AGAIN: -2147020693>, 'INTERRUPTED': <Result.INTERRUPTED: -1540292607>, 'NO_INTERFACE': <Result.NO_INTERFACE: -2147467262>, 'NULL_POINTER': <Result.NULL_POINTER: -2147467261>, 'ALREADY_EXISTS': <Result.ALREADY_EXISTS: -2147286960>, 'INVALID_OPERATION': <Result.INVALID_OPERATION: -2147020579>, 'NO_MORE_ITEMS': <Result.NO_MORE_ITEMS: -2146893782>, 'INVALID_INDEX': <Result.INVALID_INDEX: -2146889720>, 'NOT_ENOUGH_DATA': <Result.NOT_ENOUGH_DATA: -2144796415>, 'TOO_MUCH_DATA': <Result.TOO_MUCH_DATA: -2144796414>, 'INVALID_DATA_TYPE': <Result.INVALID_DATA_TYPE: -2144272373>, 'INVALID_DATA_SIZE': <Result.INVALID_DATA_SIZE: -2144272372>, 'TIMED_OUT': <Result.TIMED_OUT: -1540282548>, 'WOULD_BLOCK': <Result.WOULD_BLOCK: -1540282573>}
    pass
class TypeFactoryLoadFlags():
    """
    Base type for the flags used when registering plugins or implementations with the type
    factory.  These are used to modify how the plugin or implementation is registered.  No
    flags are currently defined.  These flags will all have the prefix ``fTypeFactoryFlag``.

    Members:

      NONE : Flag to indicate that no special change in behavior should be used when registering a plugin or implementation.
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    NONE: omni.core._core.TypeFactoryLoadFlags # value = <TypeFactoryLoadFlags.NONE: 0>
    __members__: dict # value = {'NONE': <TypeFactoryLoadFlags.NONE: 0>}
    pass
class UInt2():
    """
    Helper struct to represent a single 2-space vector of unsigned integers.  Each member
     of the struct can be accessed in multiple ways including an array and direct accessors
     known by multiple names.  Objects of this struct are guaranteed to be only as large as
     two 32-bit unsigned integers.
    """
    def __eq__(self, arg0: UInt2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    @typing.overload
    def __init__(self, x: int, y: int) -> None: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __str__(self) -> str: ...
    @property
    def h(self) -> int:
        """
        /< Provides access to the first data member as a height value.

        :type: int
        """
    @h.setter
    def h(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a height value.
        """
    @property
    def s(self) -> int:
        """
        /< Provides access to the first data member as an S texture coordinate.

        :type: int
        """
    @s.setter
    def s(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as an S texture coordinate.
        """
    @property
    def t(self) -> int:
        """
        /< Provides access to the first data member as an T texture coordinate.

        :type: int
        """
    @t.setter
    def t(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as an T texture coordinate.
        """
    @property
    def u(self) -> int:
        """
        /< Provides access to the first data member as a U texture coordinate.

        :type: int
        """
    @u.setter
    def u(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a U texture coordinate.
        """
    @property
    def v(self) -> int:
        """
        /< Provides access to the first data member as a V texture coordinate.

        :type: int
        """
    @v.setter
    def v(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a V texture coordinate.
        """
    @property
    def w(self) -> int:
        """
        /< Provides access to the first data member as a width value.

        :type: int
        """
    @w.setter
    def w(self, arg0: int) -> None:
        """
        /< Provides access to the first data member as a width value.
        """
    @property
    def x(self) -> int:
        """
        Provides access to the first data member as a Cartesian X coordinate. 

        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        """
        Provides access to the first data member as a Cartesian X coordinate. 
        """
    @property
    def y(self) -> int:
        """
        Provides access to the first data member as a Cartesian Y coordinate. 

        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        """
        Provides access to the first data member as a Cartesian Y coordinate. 
        """
    __hash__ = None
    pass
class _ITypeFactory(IObject):
    pass
def create_type(type_id: str, module_name: str = None, version: int = 0) -> IObject:
    pass
def register_module(module_name: str, flags: int = 0) -> int:
    pass
