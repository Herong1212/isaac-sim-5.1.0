"""Collection of class definitions that provide wrappers for AutoNode functionality"""

from abc import ABC, abstractmethod
from typing import Iterable


# ================================================================================
class AutoNodeDefinitionWrapper(ABC):
    """Container for a single node representation consumed by the Ogn code generator.
    Class is abstract and meant to be overridden. A sufficient implementation overrides these methods:
    * get_ogn(self) -> Dict
    * get_node_impl(self)
    * get_unique_name(self) -> str
    * get_module_name(self) -> str
    """

    # --------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def get_ogn(self) -> dict:
        """Get the Ogn dictionary representation of the node interface."""
        return {}

    # --------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def get_node_impl(self) -> object:
        """Gets the implementation class for the node type. See OmniGraph documentation for details
        on exactly what goes into this class.
        Returns:
            Class implementing the node behavior, which mainly comprises a static `compute(db)` method
        """

    # --------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def get_unique_name(self) -> str:
        """Get nodes unique name, to be saved as an accessor in the node database.
        Returns:
            the non-mangled unique name
        """
        return ""

    # --------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def get_module_name(self) -> str:
        """Get the Python module where this AutoNode definition should appear.
        Returns:
            The name of the Python module in which the AutoNode method this class wraps was defined
        """
        return ""


# ================================================================================
class AutoNodeDefinitionGenerator(ABC):  # pragma: no cover   Unsupported code
    """Defines an interface for generating a node definition"""

    _NAME = ""

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def name(cls):
        return cls._NAME

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    @abstractmethod
    def generate_from_definitions(cls, new_type: type) -> tuple[Iterable[AutoNodeDefinitionWrapper], Iterable[str]]:
        """This method scans the type new_type and outputs an AutoNodeDefinitionWrapper from it, representing the type,
        as well as a list of members it wishes to hide from the rest of the node extraction process.

        Args:
            new_type: the type to analyze by attribute

        Returns: a tuple of:
            Iterable[AutoNodeDefinitionWrapper] - an iterable of AutoNodeDefinitionWrapper - every node wrapper that is generated from this type.
            Iterable[str] - an iterable of all members covered by this handler that other handlers should ignore.
        """


# ==============================================================================================================
class AutoNodeDataWrapper:  # pragma: no cover   Unsupported code
    """Class to wrap around data being passed in the graph, to ensure a standard interface for passing data in the
    graph.  Accepts both reference and value types.
    """

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, value) -> None:
        self._value = value
        self._type = type(value)
        if isinstance(self._type, AutoNodeDataWrapper):
            raise KeyError("Attempted to wrap a datawrapper")

    # --------------------------------------------------------------------------------------------------------------
    @property
    def value(self):
        """Returns the stored value without side effects"""
        return self._value

    # --------------------------------------------------------------------------------------------------------------
    @property
    def type(self) -> type:  # noqa: A003
        """Returns the value type stored at initialization time without side effects"""
        return self._type


# ==============================================================================================================
class AutoNodeObjectStore:  # pragma: no cover   Unsupported code
    """Object store with simple put-pop interface."""

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self._store = {}

    # --------------------------------------------------------------------------------------------------------------
    def pop(self, obj_id: int) -> AutoNodeDataWrapper:
        """Attempts to return a value from the object store, and deletes it from the store.

        Args:
            obj_id: the object ID to be retrieved

        Returns:
            An AutoNodeDataWrapper that was placed in the store with the given obj_id

        Raises:
            KeyError if the object isn't there.
        """
        return self._store.pop(obj_id)

    # --------------------------------------------------------------------------------
    def put(self, obj_id: int, value: AutoNodeDataWrapper) -> AutoNodeDataWrapper | None:
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
