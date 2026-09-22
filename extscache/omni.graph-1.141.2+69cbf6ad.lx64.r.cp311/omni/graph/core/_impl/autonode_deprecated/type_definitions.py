from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional, Tuple


# ================================================================================
class AutoNodeDefinitionWrapper(ABC):
    """Container for a single node representation consumed by the Ogn code generator.
    Class is abstract and meant to be overridden. A sufficient implementation overrides these methods:
    * get_ogn(self) -> Dict
    * get_node_impl(self)
    * get_unique_name(self) -> str
    * get_module_name(self) -> str
    """

    # --------------------------------------------------------------------------------
    @abstractmethod
    def get_ogn(self) -> Dict:
        """Get the Ogn dictionary representation of the node interface."""
        return {}

    # --------------------------------------------------------------------------------
    @abstractmethod
    def get_node_impl(self):
        """Returns the Ogn class implementing the node behavior. See omnigraph docuemntation on how to implement.
        A sufficient implementation contains a staticmethod with the function: compute(db)
        """

    # --------------------------------------------------------------------------------
    @abstractmethod
    def get_unique_name(self) -> str:
        """Get nodes unique name, to be saved as an accessor in the node database.

        Returns:
            the non-mangled unique name
        """
        return ""

    # --------------------------------------------------------------------------------
    @abstractmethod
    def get_module_name(self) -> str:
        """Get the module this autograph method was defined in.

        Returns:
            the module name
        """
        return ""


# ================================================================================
class AutoNodeDefinitionGenerator(ABC):
    """Defines an interface for generating a node definition"""

    _name = ""

    # --------------------------------------------------------------------------------
    @classmethod
    def name(cls):
        return cls._name

    # --------------------------------------------------------------------------------
    @classmethod
    @abstractmethod
    def generate_from_definitions(cls, new_type: type) -> Tuple[Iterable[AutoNodeDefinitionWrapper], Iterable[str]]:
        """This method scans the type new_type and outputs an AutoNodeDefinitionWrapper from it, representing the type,
        as well as a list of members it wishes to hide from the rest of the node extraction process.

        Args:
            new_type: the type to analyze by attribute

        Returns: a tuple of:
            Iterable[AutoNodeDefinitionWrapper] - an iterable of AutoNodeDefinitionWrapper - every node wrapper that is generated from this type.
            Iterable[str] - an iterable of all members covered by this handler that other handlers should ignore.
        """


class AutographDataWrapper:
    """Class to wrap around data being passed in the graph, to ensure a standard interface for passing data in the
    graph.  Accepts both reference and value types.
    """

    # --------------------------------------------------------------------------------
    def __init__(self, value) -> None:
        self._value = value
        self._type = type(value)
        if isinstance(self._type, AutographDataWrapper):
            raise KeyError("Attempted to wrap a datawrapper")

    # --------------------------------------------------------------------------------
    @property
    def value(self):
        """Returns the stored value without side effects"""
        return self._value

    # --------------------------------------------------------------------------------
    @property
    def type(self) -> type:  # noqa: A003
        """Returns the value type stored at initialization time without side effects"""
        return self._type


class AutographObjectStore:
    """Obejct store with simple put-pop interface."""

    # --------------------------------------------------------------------------------
    def __init__(self):
        self._store = {}

    # --------------------------------------------------------------------------------
    def pop(self, obj_id: int) -> AutographDataWrapper:
        """Attempts to return a value from the object store, and deletes it from the store.

        Args:
            obj_id: the object ID to be retrieved

        Returns:
            an AutographDataWrapper if successful

        Raises:
            KeyError if the object isn't there.
        """
        return self._store.pop(obj_id)

    # --------------------------------------------------------------------------------
    def put(self, obj_id: int, value: AutographDataWrapper) -> Optional[AutographDataWrapper]:
        """Places an object in the object store according to an object ID. If an object already exists in the data store
        with the same ID, it is popped.

        Args:
            obj_id: integer object ID for input object
            value: the actual object ID. Does not check for types.

        Returns:
            The previous object with the same ID stored in the object store, None otherwise.

        """
        swapped = self._store.get(obj_id, None)
        self._store[obj_id] = value
        return swapped


# ================================================================================
class TypeRegistry:
    """Main singleton for storing graph objects and generating and registering functions."""

    def __init__(self):
        self.class_to_methods = None
        self.func_name_to_func = None
        self.refs = None
        self.type_handlers = None
        self._impl_modules = None
        raise RuntimeError("Singleton class, use instance() instead")

    # --------------------------------------------------------------------------------
    def _initialize(self):

        self.class_to_methods: Dict[type, Dict[str, str]] = {}

        # Meant to make accessing functions easier
        self.func_name_to_func = {}

        # Meant to keep a pointer to an object, so it doesn't get garbage collected
        self.refs = AutographObjectStore()

        # Meant to handle types whene generating nodes
        self.type_handlers = set()

        # Stores omnigraph implementations
        self._impl_modules = {}

    # --------------------------------------------------------------------------------
    @classmethod
    def _reset(cls):
        """Resets all internal data strucutres. Does not unregister nodes."""
        cls.instance()._initialize()

    # --------------------------------------------------------------------------------
    @classmethod
    def instance(cls):
        """Retrieves the class instance for this singleton.

        Returns:
            Class instance
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls.__new__(cls)
            cls._instance._initialize()
        return cls._instance

    # --------------------------------------------------------------------------------
    @classmethod
    def get_func(cls, unique_name: str) -> Optional[AutoNodeDefinitionWrapper]:
        """Retrieves a function from the object store

        Attributes
            unique_name: function's qualified name. Name mangling is handled by this class

        Returns:
            Function Wrapper.

        """
        return cls.instance().func_name_to_func.get(unique_name, None)

    # --------------------------------------------------------------------------------
    @classmethod
    def add_to_graph(cls, obj) -> int:
        """Adds an object `obj` to the data store without checking for uniqueness of held object.
        Does check uniqueness of reference object.

        Attributes
            obj: Object to add to the data store.

        Returns:
            the object id.
        """
        wrapper = AutographDataWrapper(obj)
        obj_id = id(wrapper)
        cls.instance().refs.put(obj_id, wrapper)
        return obj_id

    # --------------------------------------------------------------------------------
    @classmethod
    def remove_from_graph(cls, obj_id: int) -> AutographDataWrapper:
        """Attempts to remove an object ID from the object store.

        Attributes
            obj_id: the object ID to be removed from the data store.

        Returns:
            the object stored if it was found, None otherwise.
        """
        return cls.instance().refs.pop(obj_id)
