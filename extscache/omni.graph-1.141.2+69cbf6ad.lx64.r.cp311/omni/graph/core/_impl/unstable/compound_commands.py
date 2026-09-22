# =============================================================================================================================
# This submodule is work-in-progress and subject to change without notice
#  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __
# | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ /
# | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' /
# | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <
# | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \
#  \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_|


from typing import List, Optional, Tuple, Union

import carb
import omni.graph.core as og
import omni.graph.core._unstable as ogu
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.kit.commands
import omni.usd
import OmniGraphSchema
from pxr import Sdf

# Compound Node Types have multiple version of schema types
_LATEST_COMPOUND_SCHEMA = OmniGraphSchema.CompoundNodeType_1


# ------------------------------------------------------------------------------------------------------------
def _compose_node_type_qualified_name(name: Sdf.Path, namespace: Optional[str]) -> Tuple[str, str]:
    """Composes a node type qualified name from a prim path and namespace"""
    type_name = str(name.name)
    if namespace is None:
        namespace = str(OmniGraphSchema.Tokens.localNodes)
    namespace = namespace.rstrip(".")
    return (namespace, type_name)


# ------------------------------------------------------------------------------------------------------------
def _get_next_valid_node_type_name(folder: Sdf.Path, name: str, namespace: Optional[str]) -> Tuple[Sdf.Path, str]:
    """Returns a valid node type path and namespace"""
    base_name = name
    count = 0
    stage = omni.usd.get_context().get_stage()
    node_type_exists = None

    while True:
        prim_path = folder.AppendChild(name)
        (modified_namespace, name) = _compose_node_type_qualified_name(prim_path, namespace)
        if og.get_node_type(f"{modified_namespace}.{name}").is_valid():
            node_type_exists = f"{modified_namespace}.{name}"
        elif not stage.GetPrimAtPath(prim_path).IsValid():
            break
        count = count + 1
        name = f"{base_name}_{count:02d}"

    if node_type_exists is not None:
        carb.log_warn(
            f"Attempt to create duplicate node type {node_type_exists}. Registering as {modified_namespace}.{name} instead"
        )

    return (prim_path, modified_namespace)


# -------------------------------------------------------------------------------------------------------------
def _validate_type_str(type_name: str) -> bool:
    """Returns whether the supplied type is a proper ogn type, union or 'any' type"""
    if type_name == "any":
        return True
    if og.AttributeType.type_from_ogn_type_name(type_name).base_type != og.BaseDataType.UNKNOWN:
        return True
    if type_name in ogn.ATTRIBUTE_UNION_GROUPS:
        return True
    return False


# ------------------------------------------------------------------------------------------------------------
def _decode_type(ogn_type: Union[None, og.Type, List[og.Type], str]) -> Tuple[og.Type, str]:
    """
    Decodes the type information passed in:
    Returns:
        (og.Type, None) for a regular type
        (None, str) for a union type (str is a command separated list of types, including unions)
        (None, None) to indicate 'any' type
    """
    if ogn_type is None:
        return (None, None)

    if isinstance(ogn_type, og.Type):
        return (ogn_type, None)

    if isinstance(ogn_type, list):
        return (None, ",".join([t.get_ogn_type_name() for t in ogn_type]))

    if isinstance(ogn_type, str):
        # if it's an ogn type
        og_type = og.AttributeType.type_from_ogn_type_name(ogn_type)
        if og_type.base_type != og.BaseDataType.UNKNOWN:
            return (og_type, None)

        types = ogn_type.split(",")
        validated_types = []
        for type_str in types:
            val = type_str.strip().lower()
            if _validate_type_str(val):
                validated_types.append(val)
            else:
                raise og.OmniGraphError(f"Invalid ogn type {val} specified in Compound Node Type metadata.")

        return (None, ",".join(validated_types))

    return (None, None)


# ------------------------------------------------------------------------------------------------------------
def _has_bundle_type(ogn_type: Union[None, og.Type, List[og.Type], str]) -> bool:
    """Returns whether the given type list contains a bundle type"""
    if ogn_type is None:
        return False
    if isinstance(ogn_type, og.Type):
        return ogn_type.role == og.AttributeRole.BUNDLE
    if isinstance(ogn_type, list):
        return any(t.role == og.AttributeRole.BUNDLE for t in ogn_type)
    if isinstance(ogn_type, str):
        (og_type, type_str) = _decode_type(ogn_type)
        if og_type:
            return og_type.role == og.AttributeRole.BUNDLE
        if type_str:
            return "bundle" in type_str.split(",")
    return False


# ------------------------------------------------------------------------------------------------------------
def _get_compound_node_type(node_type_id: Union[str, Sdf.Path]):
    compound = None
    node_type = og.get_node_type(str(node_type_id))
    if node_type.is_valid():
        compound = ogu.get_compound_node_type(node_type)
        if compound.is_valid():
            return compound

    raise og.OmniGraphError(f"Could not find compound node type {node_type_id}")


# ----------------------------------------------------------------------------------------------------------------------
class CreateCompoundNodeTypeCommand(omni.kit.commands.Command):
    """
    Create Compound Node Type **Command**. Creates a new empty node type

    Args:
        compound_name: The name of the node type to create. If a prim already exists, the next available prim name will be used
        graph_name: The name of the default graph to reference. if the graph doesn't exist, one will be created.
        namespace: The namespace to create for the node (e.g. local.nodes). If not supplied, will use the schema default
        folder: The prim to create the node under. If not supplied, the default folder is used. If the folder
                does not exist it will be created.
        evaluator_type: The associated evaluator, for example "push". Only used if a graph is created for this compound.
    """

    def __init__(
        self,
        compound_name: str = "compound",
        graph_name: str = "Graph",
        namespace: Optional[str] = None,
        folder: Optional[Sdf.Path] = None,
        evaluator_type: Optional[str] = None,
    ):
        self._compound_path = Sdf.Path()
        self._graph_path = Sdf.Path()
        self._applied = False
        self._created_folder = False
        self._compound_name = compound_name
        self._graph_name = graph_name
        self._namespace = namespace
        self._folder = folder or Sdf.Path(ogu.get_default_compound_node_type_folder())
        self._evaluator_type = evaluator_type if evaluator_type else ""

    def do(self):

        stage = omni.usd.get_context().get_stage()
        self._created_folder = not stage.GetPrimAtPath(self._folder)
        (self._compound_path, self._namespace) = _get_next_valid_node_type_name(
            self._folder, self._compound_name, self._namespace
        )
        schema_prim = None
        result = ogu.create_compound_node_type(
            self._compound_path.name, self._graph_name, self._namespace, str(self._folder), self._evaluator_type
        )
        self._created_folder = self._created_folder and bool(stage.GetPrimAtPath(self._folder))
        self._applied = self._created_folder
        if result.is_valid():
            self._applied = True
            schema_prim = _LATEST_COMPOUND_SCHEMA(stage.GetPrimAtPath(self._compound_path))

        return schema_prim

    def undo(self):
        if self._applied:
            # remove the top-most created prim
            paths = []
            if self._created_folder:
                paths.append(self._folder)
            else:
                paths.append(self._compound_path)

            delete_cmd = omni.usd.commands.DeletePrimsCommand(paths)
            delete_cmd.do()
            self._applied = False
            self._created_folder = None


# ==============================================================================================================
class CreateCompoundNodeTypeInput(omni.kit.commands.Command):
    """
    Creates a new input on a Compound Node Type
    Args:
        node_type Path to the Compound Node Type to create an attribute on, either namespace name or prim path
        input_name Name of the input attribute
        attribute_path The attribute in the compound graph to connect the node type input to
        default_type Optional default type of the path. This can be an og.Type, a list of og.Type (union) or
        a string representing the type, extended type (e.g. "any"), or ogn union type (e.g. "numerics")
    """

    def __init__(
        self,
        node_type: Union[str, Sdf.Path],
        input_name: str,
        attribute_path: Optional[Sdf.Path] = None,  # todo, this should support lists
        default_type: Union[None, og.Type, List[og.Type], str] = None,
    ):
        self._node_type = node_type
        self._input_name = input_name
        self._attribute_path = attribute_path
        self._applied = False
        self._default_type = default_type

    def do(self):
        compound = _get_compound_node_type(self._node_type)

        input_attr = None
        (og_type, ext_type) = _decode_type(self._default_type)

        if og_type is not None:
            input_attr = compound.add_input(self._input_name, og_type.get_ogn_type_name(), True)
        elif ext_type is not None:
            input_attr = compound.add_extended_input(
                self._input_name, ext_type, True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
            )
        else:
            input_attr = compound.add_extended_input(
                self._input_name, "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY
            )

        self._applied = input_attr is not None and input_attr.is_valid()
        if self._applied and self._attribute_path is not None:
            input_attr.connect_by_path(self._attribute_path)

    def undo(self):
        if self._applied:
            cmd = RemoveCompoundNodeTypeInput(self._node_type, self._input_name)
            cmd.do()
            self._applied = False


# ==============================================================================================================
class RemoveCompoundNodeTypeInput(omni.kit.commands.Command):
    """
    Removes an input attribute from a Compound Node Type
    Args:
        node_type: Path to the Compound Node Type to remove the input attribute on
        input_name: The name of the attribute to remove.
    """

    def __init__(self, node_type: Union[Sdf.Path, str], input_name: str):
        self._node_type = node_type
        self._input_name = input_name
        self._link_path = None
        self._applied = False

    def do(self):

        compound = _get_compound_node_type(self._node_type)
        input_attr = compound.find_input(self._input_name)

        if not input_attr.is_valid():
            return  # raise?

        connections = input_attr.get_connections()
        self._link_path = connections[0] if connections else None
        compound.remove_input_by_name(self._input_name)
        self._applied = True

    def undo(self):
        if self._applied:
            cmd = CreateCompoundNodeTypeInput(self._node_type, self._input_name, self._link_path)
            cmd.do()
            self._applied = False


# ==============================================================================================================
class CreateCompoundNodeTypeOutput(omni.kit.commands.Command):
    """
    Creates a new output on a Compound Node Type
    Args:
        node_type: Path to the Compound Node Type to create an attribute on.
        output_name: Name of the output attribute.
        attribute_path: The attribute in the compound graph to connect the node type output to.
        default_type: Optional default type of the path. This can be an og.Type, a list of og.Type (union) or
        a string representing the type, extended type (e.g. "any"), or ogn union type (e.g. "numerics")
    """

    def __init__(
        self,
        node_type: Union[Sdf.Path, str],
        output_name: str,
        attribute_path: Optional[Sdf.Path] = None,
        default_type: Union[None, og.Type, List[og.Type], str] = None,
    ):
        self._node_type = node_type
        self._output_name = output_name
        self._attribute_path = attribute_path
        self._applied = False
        self._default_type = default_type

    def do(self):
        if _has_bundle_type(self._default_type):
            raise og.OmniGraphError("Bundles are not yet supported as node type outputs")

        compound = _get_compound_node_type(self._node_type)
        output = None
        (og_type, ext_type) = _decode_type(self._default_type)

        if og_type is not None:
            output = compound.add_output(self._output_name, og_type.get_ogn_type_name(), True)
        elif ext_type is not None:
            output = compound.add_extended_output(
                self._output_name, ext_type, True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
            )
        else:
            output = compound.add_extended_output(
                self._output_name, "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY
            )

        self._applied = output is not None and output.is_valid()
        if self._applied and self._attribute_path is not None:
            output.connect_by_path(self._attribute_path)

    def undo(self):
        if self._applied:
            cmd = RemoveCompoundNodeTypeOutput(self._node_type, self._output_name)
            cmd.do()
            self._applied = False


# ==============================================================================================================
class RemoveCompoundNodeTypeOutput(omni.kit.commands.Command):
    """
    Removes an output attribute from a Compound Node Type
    Args:
        node_type: Path to the Compound Node Type to remove the output attribute on
        output_name: The name of the attribute to remove.
    """

    def __init__(self, node_type: Union[Sdf.Path, str], output_name: str):
        self._node_type = node_type
        self._output_name = output_name
        self._link_path = None
        self._applied = False

    def do(self):
        compound = _get_compound_node_type(self._node_type)
        output = compound.find_output(self._output_name)

        if not output.is_valid():
            return  # raise?

        connections = output.get_connections()
        self._link_path = connections[0] if connections else None
        compound.remove_output_by_name(self._output_name)
        self._applied = True

    def undo(self):
        if self._applied:
            cmd = CreateCompoundNodeTypeOutput(self._node_type, self._output_name, self._link_path)
            cmd.do()
            self._applied = False
