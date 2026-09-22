"""
Contains the support class for managing attributes whose data is strings represented as tokens
"""

from .AttributeManager import CppConfiguration, CudaConfiguration
from .UInt64AttributeManager import UInt64AttributeManager


class ObjectIdAttributeManager(UInt64AttributeManager):
    """Support class for attributes of type objectId.
    The values passed around are the same as uint64, except that they are interpreted as references to objects
    in the scene from a managed object store. The mechanism for interpreting them differently is the metadata
    stored on the attribute.
    """

    OGN_TYPE = "objectId"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "objectId": CppConfiguration("uint64_t", cast_required=False, role="eObjectId"),
    }
    CUDA_CONFIGURATION = {
        "objectId": CudaConfiguration("uint64_t", cast_required=False),
    }

    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        if self.array_depth > 0:
            return "Array of unique identifiers of Python object types"
        return "Unique identifier for Python object types"

    def create_type_name(self) -> str:
        """When creating the attribute this special type name will set up the underlying metadata correctly"""
        return "objectId[]" if self.array_depth == 1 else "objectId"

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.OBJECT_ID"

    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.data_types module.
        The default uses the SDF type name but there isn't one for this type so hardcode the actual type.
        """
        return "omni.graph.core.types.objectid" + "array" * self.array_depth

    def sdf_type_name(self) -> str:
        """Object Id attributes have no pxr::SdfValueTypeName"""
