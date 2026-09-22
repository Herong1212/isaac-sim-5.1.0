"""Manage deprecation for Python features for common use

All deprecation functions can be accessed from the top module level.

The :py:class:`omni.graph.tools.DeprecateMessage` class provides a simple way of logging a message that will only
show up once per session.

The :py:class:`omni.graph.tools.DeprecatedClass` decorator provides a method to emit a deprecation message when the
deprecated class is accessed.

The :py:class:`omni.graph.tools.RenamedClass` decorator is a slightly more sophisticated method of deprecating a
class when the deprecation is simply a name change.

The :py:function:`omni.graph.tools.deprecated_function` decorator provides a method to emit a deprecation message
when the old function is called.

The :py:class:`omni.graph.tools.DeprecatedStringConstant` wrapper provides a method to emit a deprecation message
when a string constant has been removed from the API.

The :py:function:`omni.graph.tools.DeprecatedImport` decorator provides a method to emit a deprecation message
when an entire deprecated file is imported for use. This should not be used for imports that will be included
in the API for backward compatibility, nor should these files be moved as they must continue to exist at the
same import location in order to remain compatible.
"""

from __future__ import annotations

import functools
import inspect
import re
import traceback
from enum import Enum, auto
from typing import Optional, Set

# Allow use of this feature with and without access to the carb module (e.g. from inside a build)
try:
    from carb import log_warn, settings
except ImportError:
    settings = None

    def log_warn(msg: str):
        print(f"WARN: {msg}", flush=True)


__all__ = []


# ==============================================================================================================
class DeprecationError(Exception):
    """Exception to raise when a hard-deprecated import, class, or function is attempted to be used.
    Exists to provide a last bit of information to users who have been ignoring previous deprecation errors.
    """


# ==============================================================================================================
class DeprecationLevel(Enum):
    """Enum describing how deprecations should be treated"""

    WARNING = auto()
    """Calling deprecated code results in a warning message"""
    ERROR = auto()
    """Calling deprecated code results in an error message"""


# ==============================================================================================================
# begin-deprecate-message
class DeprecateMessage:
    """Manager for deprecation messages, to make it efficient to prevent multiple logging of the same
    deprecation messages.

    The default settings for output is usually enough to help you find where deprecated code is referenced.
    If more information is desired these per-class variables can be set to reduce the filtering being done. The
    message should contains an action item for the user to upgrade from the deprecated functionality:

    .. code-block:: python

        DeprecateMessage.deprecated("Install the latest version instead")

        # Although it's not usually necessary the class can be tuned using these class variable

        SILENCE_LOG = False  # When set the output does not go to the console log; useful to disable for testing
        SHOW_STACK = True  # Report stack trace in the deprecation message - can be turned off if it is too verbose
        MAX_STACK_LEVELS = 3  # Maximum number of stack levels to report, after filtering

    You can use some Python features to handle simple deprecation cases directly such as:

    .. code-block:: python

        # Rename constant from A to B
        A = (DeprecateMessage("A has been renamed to B") and False) or B

        # Constant A will be removed
        A = (DeprecateMessage("A will be removed, use B instead) and False) or B
    """

    # end-deprecate-message
    # Deprecation messages already logged, remembered to avoid repeatedly spamming the same messages
    _MESSAGES_LOGGED = set()

    SILENCE_LOG = False
    """When set the output does not go to the console log; useful to disable for testing"""

    SHOW_STACK = True
    """Report stack trace in the deprecation message - can be turned off if it is too verbose"""

    MAX_STACK_LEVELS = 3
    """Maximum number of stack levels to report, after filtering"""

    # Pattern of stack trace elements to ignore since they are part of the collection mechanism
    _RE_IGNORE = re.compile("deprecate.py|bindings-python|importlib")

    # If Carbonite is not available use this local version of the setting to escalate deprecations to errors
    _DEPRECATIONS_ARE_ERRORS = False

    class NoLogging:
        """Context manager class to let you import a bunch of known deprecated functions without logging warnings.
        Typical use would be in providing backward compatibility in a module where submodules have moved.

            with DeprecateMessage.NoLogging():
                import .v1_0.my_old_function as my_old_function
        """

        def __init__(self, *args, **kwargs):
            self.__original_logging = None

        def __enter__(self):
            """Disable logging for the duration of the context"""
            self.__original_logging = DeprecateMessage.SILENCE_LOG
            DeprecateMessage.SILENCE_LOG = True

        def __exit__(self, exit_type, value, exit_traceback):
            """Restore the original logging state"""
            DeprecateMessage.SILENCE_LOG = self.__original_logging

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def messages_logged(cls) -> Set[str]:
        """Returns the set of messages that have been logged so far"""
        return cls._MESSAGES_LOGGED

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def clear_messages(cls):
        """Clear the logged messages so that they can be logged again"""
        cls._MESSAGES_LOGGED = set()

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def deprecations_are_errors(cls) -> bool:
        """Returns True if deprecations are currently being treated as errors"""
        if settings is None:
            return cls._DEPRECATIONS_ARE_ERRORS
        return settings.get_settings().get("/persistent/omnigraph/deprecationsAreErrors")

    @classmethod
    def set_deprecations_are_errors(cls, make_errors: bool):
        """Enable or disable treating deprecations as errors instead of warnings"""
        if settings is None:
            cls._DEPRECATIONS_ARE_ERRORS = make_errors
            return
        settings.get_settings().set("/persistent/omnigraph/deprecationsAreErrors", make_errors)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def deprecated(cls, message: str, deprecation_level: DeprecationLevel = None):
        """Log the deprecation message if it has not yet been logged, otherwise do nothing

        Args:
            message: Message to display; only displays once even if this is called many times
            deprecation_level: If specified, override the default level coming from deprecations_are_errors()

        Adds stack trace information if the class member SHOW_STACK is True.
        Skips the Carbonite logging if the class member SILENCE_LOG is True (mostly useful for testing when a
        warning is the expected result).
        """
        if message in cls._MESSAGES_LOGGED:
            return

        stack = ""
        try:
            try:
                full_stack = traceback.format_stack() if cls.SHOW_STACK else []
            except SyntaxError as error:
                full_stack = [f"Error encountered when retrieving call stack - {error}"]
            if full_stack:
                filtered_stack = filter(lambda stack: not cls._RE_IGNORE.search(stack), full_stack)
                stack = "\n" + "".join(list(filtered_stack)[-cls.MAX_STACK_LEVELS :])
        except SyntaxError as error:
            stack = f"Stack trace not accessible - {error}"

        if cls.deprecations_are_errors() or deprecation_level == DeprecationLevel.ERROR:
            raise DeprecationError(f"{message}{stack}")
        _ = cls.SILENCE_LOG or log_warn(f"{message}{stack}")
        cls._MESSAGES_LOGGED.add(message)


# ==============================================================================================================
# begin-deprecated-function
def deprecated_function(deprecation_message: str, is_property: bool = False):
    """Decorator to deprecate a function.

    Args:
        deprecation_message: A description of the action the user is to take to avoid the deprecated function.
        is_property: Set this True if the function is a property getter or setter.

    A deprecation message will only be shown once, the first time the deprecated function is called.

    .. code-block:: python

        @deprecated_function("After version 1.5.0 use og.newer_function() instead")
        def older_function():
            pass

    For property getters/setters use this decorator *after* the property decorator.

    .. code-block:: python

        @property
        @deprecated_function("use 'your_prop' instead.", is_property=True)
        def my_prop(self):
            return self.your_prop

        @my_prop.setter
        @deprecated_function("use 'your_prop' instead.", is_property=True)
        def my_prop(self, value):
            self.your_prop = value
    """

    # end-deprecated-function
    def decorator_deprecated(func):
        """Remember the message"""

        # The functools internal decorator lets the help functions drill down into the actual function when asked,
        # rather that
        @functools.wraps(func)
        def wrapper_deprecated(*args, **kwargs):
            func_str = f"'{func.__name__}'" if is_property else f"{func.__name__}()"
            DeprecateMessage.deprecated(f"{func_str} is deprecated: {deprecation_message}")
            return func(*args, **kwargs)

        return wrapper_deprecated

    return decorator_deprecated


# ==============================================================================================================
# begin-deprecated-import
def DeprecatedImport(deprecation_message: str):  # noqa: N802
    """Decorator to deprecate a specific file or module import. Usually the functionality has been deprecated and
    moved to a different file.

    Args:
        deprecation_message: String with the action the user is to perform to avoid the deprecated import

    Usage:

    .. code-block:: python

        '''This is the top line of the imported file'''
        import omni.graph.tools as ogt
        ogt.DeprecatedImport("Import 'omni.graph.tools as ogt' and use ogt.new_function() instead")

        # The rest of the file can be left as-is for best backward compatibility, or import non-deprecated versions
        # of objects from their new location to avoid duplication.
    """
    # end-deprecated-import
    this_module = inspect.currentframe().f_back.f_locals["__name__"]
    DeprecateMessage.deprecated(f"{this_module} is deprecated: {deprecation_message}")


# ==============================================================================================================
# begin-deprecated-string-constant
class DeprecatedStringConstant(str):
    """Class that lets you show a warning or error when attempting to use a deprecated string constant value.

    Usage:

    .. code-block:: python

        > # Original usage of a boolean setting
        > MY_SETTING = "/persistent/omnigraph/mySetting"
        > print(f"Value of {MY_SETTING} is {carb.settings.get_settings().get(MY_SETTING)}")
        Value of /persistent/omnigraph/mySetting is True

        > # Deprecation declaration
        > MY_SETTING = DeprecatedStringConstant("MY_SETTING", "UNUSED", "Please delete references to it.")
        > print(f"Value of {MY_SETTING} is {carb.settings.get_settings().get(MY_SETTING)}")
        ERROR: String constant 'MY_SETTING' can no longer be used. Please delete references to it.
        Value of UNUSED is False

    Note that the deprecation message only appears when the value is cast to a string, which is the majority of
    interesting cases. Any deprecation which needs to catch other manipulations of the string should use a different
    approach.
    """

    @staticmethod
    def _decorate_string_method(method) -> callable:
        def wrapper(self, *args, **kwargs) -> any:
            DeprecateMessage.deprecated(
                f"{self._name} is deprecated: {self._message}",  # pylint: disable=protected-access
                self._deprecation_level,  # pylint: disable=protected-access
            )
            return method(self, *args, **kwargs)

        return wrapper

    def __new__(cls, name: str, new_value: str | None, message: str, deprecation_level: DeprecationLevel = None):
        """Construct a string constant that will print a message if it is used
        Args:
            name: Name of the string constant. Should match what was formerly exported as part of the API
            new_value: The value to return if the string is requested
            message: Message to emit if the string is used
            deprecation_level: How serious the deprecation message should be. None means use the default
        """
        # end-deprecated-string-constant
        # Replace the standard str methods with a decorated version that generates a deprecation message when accessed.
        for member_name, fn in inspect.getmembers(cls, inspect.ismethoddescriptor):
            if member_name[2:-2] in ["eq", "format", "ge", "gt", "hash", "le", "lt", "ne", "repr", "sizeof", "str"]:
                setattr(cls, member_name, DeprecatedStringConstant._decorate_string_method(method=fn))
        return str.__new__(cls, new_value)

    def __init__(self, name: str, new_value: str | None, message: str, deprecation_level: DeprecationLevel = None):
        """Construct a string constant that will print a message if it is used
        Args:
            name: Name of the string constant. Should match what was formerly exported as part of the API
            new_value: The value to return if the string is requested
            message: Message to emit if the string is used
            deprecation_level: How serious the deprecation message should be. None means use the default
        """
        self._name = name
        self._message = message
        self._deprecation_level = deprecation_level
        super().__init__()


# ==============================================================================================================
# begin-deprecated-dict-constant
class DeprecatedDictConstant(dict):
    """Class that lets you show a warning or error when attempting to use a deprecated dict constant value.

    Usage:

    .. code-block:: python

        > # Original usage of a dictionary
        > MY_DICT = {"setting"": True}
        > print(f"Setting is {MY_DICT['setting']}")
        Setting is True

        > # Deprecation declaration
        > MY_DICT = DeprecatedDictConstant("MY_DICT", {}, "Please delete references to it.")
        > print(f"Setting is {MY_DICT['setting']}")
        ERROR: Dictionary constant 'MY_DICT' can no longer be used. Please delete references to it.
        KeyError: "setting"
    """

    @staticmethod
    def _decorate_dict_method(method) -> callable:
        def wrapper(self, *args, **kwargs) -> any:
            DeprecateMessage.deprecated(
                f"{self._name} is deprecated: {self._message}",  # pylint: disable=protected-access
                self._deprecation_level,  # pylint: disable=protected-access
            )
            return method(self, *args, **kwargs)

        return wrapper

    def __new__(cls, name: str, new_value: dict, message: str, deprecation_level: DeprecationLevel = None):
        """Construct a dictionary constant that will print a message if it is used
        Args:
            name: Name of the dictionary constant. Should match what was formerly exported as part of the API
            new_value: The value to return if the dictionary is requested
            message: Message to emit if the dictionary is used
            deprecation_level: How serious the deprecation message should be. None means use the default
        """
        # end-deprecated-dict-constant
        # Replace the standard str methods with a decorated version that generates a deprecation message when accessed.
        for member_name, fn in inspect.getmembers(cls, inspect.ismethoddescriptor):
            if member_name not in ["__class__", "__getattribute__", "__init__", "__new__", "__setattr__"]:
                setattr(cls, member_name, DeprecatedDictConstant._decorate_dict_method(method=fn))
        return dict.__new__(cls)

    def __init__(self, name: str, new_value: dict, message: str, deprecation_level: DeprecationLevel = None):
        """Construct a dictionary constant that will print a message if it is used
        Args:
            name: Name of the dictionary constant. Should match what was formerly exported as part of the API
            new_value: The value to return if the dictionary is requested
            message: Message to emit if the dictionary is used
            deprecation_level: How serious the deprecation message should be. None means use the default
        """
        self._name = name
        self._message = message
        self._deprecation_level = deprecation_level
        super().__init__(**new_value)


# ==============================================================================================================
# begin-deprecated-constant-object
def deprecated_constant_object(constant: any, deprecation_message: str, deprecation_level: DeprecationLevel = None):
    """Class that lets you show a warning or error when attempting to use a deprecated constant object.

    It only works for objects as it relies on overriding the __getattr__ function, which simple values like integers
    and floats do not have.

    Args:
        constant: The actual value of the constant as it was before deprecation
        deprecation_message: Additional message to provide the user with information of how to avoid using the constant
        deprecation_level: Optional ability to hardcode the deprecation level of this particular constant

    Usage:

    .. code-block:: python

        > # Original usage of a constant
        > RE_FIND_HOMER = re.compile(".*D'oh")
        > print(RE_FIND_HOMER.match("Don't have a cow man"))
        None

        > # Deprecation declaration
        > RE_FIND_HOMER = deprecated_constant(re.compile(".*D'oh"), "Please delete references to it.")
        > print(RE_FIND_HOMER.match("Don't have a cow man"))
        WARNING: Constant 'RE_FIND_HOMER' is deprecated. Please delete references to it.
        None
    """
    # end-deprecated-constant-object

    # The decorator works by wrapping the constant in a class
    class DeprecatedConstWrapper:
        def __getattr__(self, name) -> any:
            DeprecateMessage.deprecated(f"Constant {constant} is deprecated. {deprecation_message}", deprecation_level)
            return getattr(constant, name)

    return DeprecatedConstWrapper()


# ==============================================================================================================
# begin-deprecated-class
def DeprecatedClass(deprecation_message: str = None) -> object:  # noqa: N802
    """Decorator to deprecate a class.

    Args:
        deprecation_message: A string to describe the action the user is to take to avoid the deprecated class. If None
                             then a generic message will be provided. A deprecation message will be shown only once, the
                             first time the deprecated class is accessed.

    .. code-block:: python

        @DeprecatedClass("After version 1.5.0 use og.NewerClass instead")
        class OlderClass:
            STATIC_VALUE = 1

        obj = OlderClass()  # Gives a deprecation warning
        value = OlderClass.STATIC_VALUE  # This also works for static class members and methods
    """
    # end-deprecated-class

    # The way the decorator works is by creating an inner _WrappedClass that inherits everything from the deprecated
    # class and then replaces static/class members and the __init__ function with a wrapper that prints a deprecation
    # message and then forwards the request to the deprecated class.

    def deprecated_class_decorator(cls, deprecated_class_name: str = None):
        deprecated_class_name = cls.__name__ if deprecated_class_name is None else deprecated_class_name

        class _WrappedClass(cls):
            def __init__(self, *args, **kwargs):
                self.__deprecation_message = f"Accessing {{}} on deprecated class {deprecated_class_name}"
                if deprecation_message is not None and not inspect.isclass(deprecation_message):
                    self.__deprecation_message = deprecation_message + f" ({self.__deprecation_message})"

                def add_deprecation_message(func, message):
                    def wrapper(*args, **kwargs):
                        DeprecateMessage.deprecated(message.format(func.__name__))
                        return func(*args, **kwargs)

                    return wrapper

                for name, member in vars(cls).items():
                    if isinstance(member, (classmethod, staticmethod)) or name == "__init__":
                        setattr(_WrappedClass, name, add_deprecation_message(member, self.__deprecation_message))

                    # Static class members are emulated as properties of the wrapped class with deprecation messages
                    # in the setters and getters of the property, and the actual values stored as internal copies
                    # of the actual class member. So the class transformation behaves something like this:
                    #
                    #    class Old:
                    #        VALUE = 1
                    #
                    #    class New(Old):
                    #        def __init__(self, *args, **kwargs):
                    #            __VALUE = 1
                    #            super().__init__(self, *args, **kwargs)
                    #        @property
                    #        def VALUE(self):
                    #            return self.__VALUE
                    #        @VALUE.setter
                    #        def VALUE(self, new_value):
                    #            self.__VALUE = new_value
                    #
                    elif not name.startswith("__") and not isinstance(member, property) and not callable(member):
                        internal_name = f"___{name}"

                        def _getter(self, _name=name, _internal_name=internal_name):
                            DeprecateMessage.deprecated(self.__deprecation_message.format(_name))
                            return getattr(self, _internal_name)

                        def _setter(self, value, _name=name, _internal_name=internal_name):
                            DeprecateMessage.deprecated(self.__deprecation_message.format(_name))
                            setattr(self, _internal_name, value)

                        setattr(_WrappedClass, internal_name, getattr(cls, name))
                        setattr(_WrappedClass, name, property(fget=_getter, fset=_setter))

            def __call__(self, *args, **kwargs):
                """This handles the case of a deprecated class being instantiated"""
                DeprecateMessage.deprecated(self.__deprecation_message.format("__init__"))
                return cls(*args, **kwargs)

        return _WrappedClass()

    # Having two ways of returning the values lets the decorator be used both with and without a message argument
    if inspect.isclass(deprecation_message):
        return deprecated_class_decorator(deprecation_message)
    return deprecated_class_decorator


# ==============================================================================================================
# begin-renamed-class
def RenamedClass(cls, old_class_name: str, rename_message: Optional[str] = None) -> object:  # noqa: N802
    """Syntactic sugar to provide a class deprecation that is a simple renaming, where all of the functions in
    the old class are still present in backwards compatible form in the new class.

    Args:
        old_class_name: The name of the class that was renamed
        rename_message: Message to give the user if the old class name is used. A generic message will be
                        provided if this is None.

    Usage:

    .. code-block:: python

        MyDeprecatedClass = RenamedClass(MyNewClass, "MyDeprecatedClass")
        obj = MyDeprecatedClass()  # Gives a deprecation warning
        obj = MyNewClass()  # Works fine - both calls return the same type of object

        # This also works for static class members and methods
        value = MyDeprecatedClass.VALUE  # Gives a deprecation warning
        value = MyDeprecatedClass.class_method()  # Gives a deprecation warning
        value = MyDeprecatedClass.static_method()  # Gives a deprecation warning
    """
    # end-renamed-class
    if rename_message is None:
        rename_message = f"Use class {cls.__name__} instead"
    return DeprecatedClass(rename_message)(cls, old_class_name)
