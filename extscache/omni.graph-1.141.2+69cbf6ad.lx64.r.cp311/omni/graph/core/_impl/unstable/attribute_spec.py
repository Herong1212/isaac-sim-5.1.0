"""This is a specification for the structural elements of an attribute.
The definition is in the internal namespace for now as there may be changes required soon in order to support
Warp data types natively so the design is unstable and should not be exposed yet. It is primarily used for
AutoNode definitions.

It's implemented as a dataclass for now as its instantiation happens entirely in one place, and the automatically
generated niceties such as the equality operator will come in handy.
"""

from dataclasses import dataclass

import omni.graph.core as og  # For Python binding types


@dataclass
class AttributeSpec:
    name: str
    """Base name of the attribute, not including the port namespace"""
    port_type: og.AttributePortType
    """Port type of the attribute - input, output, or state"""
    type_name: str
    """Data type of the attribute. Uses a string for now to keep the options open on what the representation is"""
    description: str = "[No description provided]"
    """Description of the attribute. Should be detailed enough that the user will understand how to use it."""
    ui_name: str = None
    """UI name of the attribute. This is how the user will see it in the GUI."""
    default: any = None
    """Optional default value of the attribute, for those attribute types that support it."""
    min_value: any = None
    """Minimum value of the attribute, for those attribute types that support it"""
    max_value: any = None
    """Maximum value of the attribute, for those attribute types that support it"""
    metadata: dict[str, str] = None
    """User-defined metadata to store on the attribute"""

    def full_name(self):
        """Convenience function to build and return the fully qualified attribute name based on the spec"""
        return og.Attribute.ensure_port_type_in_name(
            self.name, port_type=self.port_type, is_bundle=(self.type_name == "bundle")
        )
