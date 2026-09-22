"""Helpers for modifying the contents of a node"""

from typing import Any, Dict, List, Optional

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
from carb import log_info

from .object_lookup import ObjectLookup
from .type_aliases import Attribute_t, AttributeSpec_t, AttributeType_t, ExtendedAttribute_t, Node_t
from .utils import DBG, _flatten_arguments, _Unspecified


# ==============================================================================================================
class NodeController:
    """Helper class that provides a simple interface to modifying the contents of a node"""

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initializes the class with a particular configuration.
        The arguments are flexible so that classes can initialize only what they need for the calls they
        will be making. The argument is optional and there may be other arguments present that will be ignored

        Args:
            undoable (bool): If True the operations performed with this instance of the class are to be added to the
                             undo queue, else they are done immediately and forgotten
        """
        (self.__undoable,) = _flatten_arguments(
            optional=[("undoable", None)],
            args=args,
            kwargs=kwargs,
        )

        # Dual function methods that can be called either from an object or directly from the class
        self.create_attribute = self.__create_attribute_obj
        self.promote_attribute = self.__promote_attribute_obj
        self.remove_attribute = self.__remove_attribute_obj

    # ----------------------------------------------------------------------
    # begin-create-attribute-function
    @classmethod
    def create_attribute(obj, *args, **kwargs) -> Optional[og.Attribute]:  # noqa: N804, PLE0202, PLC0202
        """Create a new dynamic attribute on the node

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            node: Node on which to create the attribute (path or og.Node)
            attr_name: Name of the new attribute, either with or without the port namespace
            attr_type: Type of the new attribute, as an OGN type string or og.Type
            attr_port: Port type of the new attribute, default is og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            attr_default: The initial value to set on the attribute, default is None which means use the type's default
            attr_extended_type: The extended type of the attribute, default is
                                og.ExtendedAttributeType.REGULAR. If the extended type is
                                og.ExtendedAttributeType.UNION then this parameter will be a
                                2-tuple with the second element being a list or comma-separated string of union types
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten

        Returns:
            omni.graph.core.Attribute: The newly created attribute, None if there was a problem creating it
        """
        # end-create-attribute-function
        return obj.__create_attribute(obj, args=args, kwargs=kwargs)

    def __create_attribute_obj(self, *args, **kwargs) -> Optional[og.Attribute]:
        """Implements :py:meth:`.NodeController.create_attribute` when called as an object method"""
        return self.__create_attribute(self, undoable=self.__undoable, args=args, kwargs=kwargs)

    @staticmethod
    def __create_attribute(
        obj,
        node: Node_t = _Unspecified,
        attr_name: str = _Unspecified,
        attr_type: AttributeType_t = _Unspecified,
        attr_port: Optional[og.AttributePortType] = og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        attr_default: Optional[Any] = None,
        attr_extended_type: Optional[ExtendedAttribute_t] = og.ExtendedAttributeType.REGULAR,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> Optional[og.Attribute]:
        """Implements :py:meth:`.NodeController.create_attribute`"""
        (node, attr_name, attr_type, attr_port, attr_default, attr_extended_type, undoable) = _flatten_arguments(
            mandatory=[("node", node), ("attr_name", attr_name), ("attr_type", attr_type)],
            optional=[
                ("attr_port", attr_port),
                ("attr_default", attr_default),
                ("attr_extended_type", attr_extended_type),
                ("undoable", undoable),
            ],
            args=args,
            kwargs=kwargs,
        )

        omg_node = ObjectLookup.node(node)
        omg_attr_type = ObjectLookup.attribute_type(attr_type)
        if undoable:
            (_, success) = og.cmds.CreateAttr(
                node=omg_node,
                attr_name=attr_name,
                attr_type=omg_attr_type,
                attr_port=attr_port,
                attr_default=attr_default,
                attr_extended_type=attr_extended_type,
            )
        else:
            og.cmds.imm.CreateAttr(
                node=omg_node,
                attr_name=attr_name,
                attr_type=omg_attr_type,
                attr_port=attr_port,
                attr_default=attr_default,
                attr_extended_type=attr_extended_type,
            )
            success = True
        if not success:
            raise og.OmniGraphError("Could not create attribute - see warning log for details")

        # The command didn't return the new attribute so it has to be looked up in the node
        namespace = og.get_port_type_namespace(attr_port)
        if not attr_name.startswith(namespace):
            if (
                omg_attr_type.role == og.AttributeRole.BUNDLE
                and attr_port != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            ):
                separator = "_"
            else:
                separator = ":"
            attr_name = f"{namespace}{separator}{attr_name}"
        return omg_node.get_attribute(attr_name)

    # ----------------------------------------------------------------------
    # begin-remove-attribute-function
    @classmethod
    def remove_attribute(obj, *args, **kwargs) -> bool:  # noqa: N804,PLC0202,PLE0202
        """Removes an existing dynamic attribute from a node.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            attribute: Reference to the attribute to be removed
            node: If the attribute reference is a string the node is used to find the attribute to be removed
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten

        Raises:
            OmniGraphError: if the attribute was not found or could not be removed
        """
        # end-remove-attribute-function
        return obj.__remove_attribute(obj, args=args, kwargs=kwargs)

    def __remove_attribute_obj(self, *args, **kwargs) -> og.Graph:
        """Implements :py:meth:`.NodeController.remove_attribute` when called as an object method"""
        return self.__remove_attribute(self, undoable=self.__undoable, args=args, kwargs=kwargs)

    @staticmethod
    def __remove_attribute(
        obj,
        attribute: Attribute_t = _Unspecified,
        node: Node_t = None,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> bool:
        """Implements :py:meth:`.NodeController.remove_attribute`"""
        (attribute, node, undoable) = _flatten_arguments(
            mandatory=[("attribute", attribute)],
            optional=[("node", node), ("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )
        omg_attribute = ObjectLookup.attribute(attribute, node)
        if undoable:
            (_, success) = og.cmds.RemoveAttr(attribute=omg_attribute)
        else:
            og.cmds.imm.RemoveAttr(attribute=omg_attribute)
            success = True

        if not success:
            raise og.OmniGraphError("Could not remove attribute - see warning log for details")

        return success

    # ----------------------------------------------------------------------
    @classmethod
    def safe_node_name(cls, node_type_name: str, abbreviated: bool = False) -> str:
        """Returns a USD-safe node name derived from the node_type_name

        Args:
            node_type_name: Fully namespaced name of the node type (e.g. omni.graph.nodes.Clamp)
            abbreviated: If True then remove the namespace, else just make the separators into underscores

        Returns:
            str: A safe node name that roughly corresponds to the given node type name
        """
        if abbreviated:
            last_namespace = node_type_name.rfind(".")
            if last_namespace < 0:
                return node_type_name
            return node_type_name[last_namespace + 1 :]
        return node_type_name.replace(".", "_")

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def promote_attribute(obj, *args, **kwargs) -> og.Attribute:  # noqa: N804,PLC0202,PLE0202
        """Promotes an attribute on a node in a compound graph, making it accessable to the parenting compound node.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            src_spec: Specification of the attribute to be promoted
            name: The name of the promoted attribute. If not specified, the namespace prefix will be prepended based
            on src_spec.
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)
        Returns:
            og.Attribute: The attribute created on the compound node that connects to the attribute

        Raises:
            OmniGraphError: If attribute could not be found, the attribute does not belong to a compound, or the promoted
            name already exists
        """
        return obj.__promote_attribute(obj, args=args, kwargs=kwargs)

    def __promote_attribute_obj(self, *args, **kwargs) -> og.Attribute:
        """Implements :py:meth:`.NodeController.promote_attribute` when called as an object method"""
        return self.__promote_attribute(self, undoable=self.__undoable, args=args, kwargs=kwargs)

    @staticmethod
    def __promote_attribute(
        obj,
        attribute: AttributeSpec_t = _Unspecified,
        name: str = None,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> og.Attribute:
        """Implement :py:meth:`.NodeController._promote_attribute`"""
        (attribute, name, undoable) = _flatten_arguments(
            mandatory=[("attribute", attribute), ("name", name)],
            optional=[("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )
        msg = f"`{attribute}` -> `{name}`"
        _ = DBG and log_info(f"Promote Attribute {msg}")

        src = ObjectLookup.attribute(attribute)
        if (
            src.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            and src.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
        ):
            og.OmniGraphError(f"{attribute} only input or output ports can be promoted")

        src_graph = src.get_node().get_graph()
        if src_graph is None or not src_graph.is_valid() or not src_graph.is_compound_graph():
            raise og.OmniGraphError(
                f"{ObjectLookup.attribute_path(src)} is not part of a compound graph and cannot be promoted"
            )

        # TODO - check if this is a SUBGRAPH compound graph instance
        compound_node = src_graph.get_owning_compound_node()

        is_bundle = src.get_resolved_type().role == og.AttributeRole.BUNDLE

        # determine if it's an output or input, and validate the promoted name has the correct prefix
        port_type = og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        if (
            src.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
            or src.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1"
        ):
            port_type = og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT

        name = og.Attribute.ensure_port_type_in_name(name, port_type, is_bundle)
        base_name = og.Attribute.remove_port_type_from_name(name, is_bundle)

        if compound_node.get_attribute_exists(name):
            raise og.OmniGraphError(f"{name} already exists on {compound_node.get_prim_path()}")

        attr = None
        _ = DBG and log_info(f"   Promote Attribute {ObjectLookup.attribute_path(attribute)} as {name}")
        try:
            cmds = og._unstable.cmds if undoable else og._unstable.cmds.imm  # noqa PLW0202
            if port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                (success, attr) = cmds.CreateCompoundSubgraphInput(
                    compound_node=compound_node, input_name=base_name, connect_to=src
                )
            else:
                (success, attr) = cmds.CreateCompoundSubgraphOutput(
                    compound_node=compound_node, output_name=base_name, connect_from=src
                )
            if not success or (attr is None) or (not attr.is_valid()):
                raise og.OmniGraphError(f"Failed to promote {ObjectLookup.attribute_path(attribute)} as {name}")
        except og.OmniGraphError as error:
            raise og.OmniGraphError(f"Failed to connect {ObjectLookup.attribute_path(attribute)} as {name}") from error

        return attr
