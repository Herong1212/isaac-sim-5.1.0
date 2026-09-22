"""Collection of class definitions that provide wrappers for AutoNode functionality"""

import logging

logger = logging.getLogger("AutoNode")


# ==============================================================================================================
class FunctionRegistrationError(Exception):
    """Exception type raised when there is a problem with the FunctionRegistry operation"""


# ==============================================================================================================
class FunctionRegistry:  # pragma: no cover    Unsupported code
    """Main class for registering AutoNode functions. Everything is a class method, operating similarly to a singleton

    The main mapping consists of a simple string to callable dictionary. Extra convenience features are layered
    on top, which is why this is a full class instead of just a dictionary.

    Attributes:
        _function_registry: The dictionary of fully qualified function name to the callable function object.
    """

    _function_registry = {}

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def get_function(cls, unique_name: str) -> callable:
        """Retrieves a function from the object store
        Args:
            unique_name: Function's fully qualified name.
        Returns:
            Function registered with the given name, or None if a function with that name has not been registered yet.
        """
        return cls._function_registry.get(unique_name, None)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def register_function(cls, unique_name: str, func: callable) -> None:
        """Creates an entry in the registry from the fully qualified name to the function.
        Args:
            unique_name: function's qualified name - the name by which it can be looked up.
            func: function reference. Weak Ref generation is handled by this method.
        Raises:
            FunctionRegistrationError: If a function of the given name already exists in the registry
        """
        logger.debug("Registering function %s as %s", unique_name, func)
        if unique_name in cls._function_registry:
            raise FunctionRegistrationError(
                f"{unique_name} already has a mapping to {cls._function_registry[unique_name]}."
                f" A second mapping to {func} is not allowed."
            )
        cls._function_registry[unique_name] = func

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def deregister_function(cls, func: callable) -> None:
        """Removes an entry in the registry for the given function.
        Args:
            func: function reference. Weak Ref generation is handled by this method.
        Raises:
            FunctionRegistrationError: If the function was not found in the registry.
        """
        logger.debug("Deregistering function %s", func)
        for unique_name, named_function in cls._function_registry.items():
            if named_function != func:
                continue
            del cls._function_registry[unique_name]
            return

        raise FunctionRegistrationError(f"The function {func} was not found in the registry.")

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def deregister_function_by_name(cls, unique_name: str) -> None:
        """Removes an entry in the registry for the given function name.
        Args:
            unique_name: function's qualified name - the name by which it can be looked up.
        Raises:
            FunctionRegistrationError: If a function with the given name was not found in the registry.
        """
        logger.debug("Deregistering function named %s", unique_name)
        if unique_name not in cls._function_registry:
            raise FunctionRegistrationError(f"No function with the name {unique_name} found in the function registry.")
        del cls._function_registry[unique_name]

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def get_functions_in_module(cls, module_name: str) -> dict[str, callable]:
        """Find registered functions that were registered under a given module name.
        Module names are assumed to be path-unique, so that checking the start of the fully qualified name is enough
        information to be sure the functon belongs to that module. Name is by prefix only - no regex matching is done.
        Args:
            module_name: Name of module to check for function registrations. Does not have to be top-level. Pass in
            an empty string to get the list of all functions registered.
        Returns:
            Dictionary of name to function object for all matching functions.
        """
        module_pattern = f"{module_name}."
        return {
            name: named_function
            for name, named_function in cls._function_registry.items()
            if name.startswith(module_pattern)
        }
