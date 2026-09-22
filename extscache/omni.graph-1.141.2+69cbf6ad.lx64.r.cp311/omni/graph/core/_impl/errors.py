"""Implementation details for internal OmniGraph error types"""

import traceback
from typing import Optional

from .object_lookup import ObjectLookup
from .type_aliases import Attribute_t


# ======================================================================
class OmniGraphError(Exception):
    """Exception to raise when there is an error in an OmniGraph operation"""

    SHOW_STACK_TRACE = False

    @classmethod
    def set_show_stack_trace(cls, enable_traces: bool):
        """Turn on or off display of stack traces when an OmniGraphError is raised

        Args:
            enable_traces: Turn on or off the stack traces when raising the error
        """
        cls.SHOW_STACK_TRACE = enable_traces

    def __init__(self, *args, **kwargs) -> str:
        """Returns the exception text, with stack trace information added if requested"""
        if OmniGraphError.SHOW_STACK_TRACE:
            self.__stack_trace = "\n" + "\n".join(traceback.format_stack(limit=5)[:-1])
        else:
            self.__stack_trace = ""
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"OmniGraphError: {super().__str__()}{self.__stack_trace}"


# ======================================================================
class OmniGraphValueError(OmniGraphError, ValueError):
    """Exception to raise when an OmniGraph operation encountered an illegal value"""


# ======================================================================
class OmniGraphTypeError(OmniGraphError, TypeError):
    """Exception to raise when an OmniGraph operation encountered an unrecognized or illegal type"""


# ======================================================================
class OmniGraphAttributeError(OmniGraphError, AttributeError):
    """Exception to raise when an OmniGraph operation encountered an unrecognized or illegal attribute value"""


# ======================================================================
class ReadOnlyError(OmniGraphError):
    """Exception to raise when there is a write operation on a read-only attribute (i.e. an input)"""

    def __init__(self, attribute: Attribute_t, message: Optional[str] = None):
        """Set up the attribute information for the operation"""
        super().__init__(message)
        self.__attribute = ObjectLookup.attribute(attribute)
        self.__message = message

    def __str__(self) -> str:
        """Returns the string representing the exception"""
        if self.__message:
            return f"{self.__message} (on {self.__attribute.get_name()})"
        return f"{self.__attribute.get_name()}"
