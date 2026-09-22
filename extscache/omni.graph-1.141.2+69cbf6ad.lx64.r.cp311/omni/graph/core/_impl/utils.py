"""
A collection of assorted utilities used by the OmniGraph scripts
"""

import os
import re
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import carb
import carb.settings
import numpy as np
import omni.graph.core as og
import OmniGraphSchema
from pxr import Gf, Sdf, Tf, Usd, Vt

from .object_lookup import ObjectLookup

# Moved to .settings
from .settings import Settings
from .type_aliases import Attribute_t, AttributeWithValue_t, Graph_t, Nodes_t

temporary_setting = Settings.temporary  # noqa:F401


# Special sentinel object to indicate that an argument in the _flatten_arguments function has no specified value.
# This is required because in some cases "None" is an acceptable value for such arguments so it cannot be used there.
class _UnspecifiedClass:
    pass


_Unspecified = _UnspecifiedClass()


# ==============================================================================================================
def _flatten_arguments(
    mandatory: List[Tuple[str, Any]] = None,
    optional: List[Tuple[str, Any]] = None,
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None,
) -> List[Any]:
    """Takes an argument list description and a set of supplied arguments and flattens them out into an explicit
    position-based set of arguments. This allows overrides for the argument values in either *args or **kwargs,
    raising an exception if any appear in both.

    This is a helper function for the pattern of having two very similar functions with slightly different argument
    lists calling into a shared implementation function. Here's an example of a function "jump()" with a parameter of
    "how_high" that can be overridden in the function call, and which will have a default value in the object
    constructor.

    .. code-block:: python

        class Toady:
            def __init__(self):
                self.__height_default = 1
                self.__height_unit = METRES
                self.jump = self.__jump_obj

            @classmethod
            def jump(cls, *args, **kwargs):
                return cls.__jump(args=args, kwargs=kwargs)

            def __jump_obj(self, *args, **kwargs):
                return self.__jump(how_high=self.__height_default, unit=self.__height_unit, args=args, kwargs=kwargs)

            @staticmethod
            def __jump(obj, how_high: int = None, unit: str = None, args=List[Any], kwargs=Dict[str, Any]):
                (how_high, unit) = _flatten_arguments(
                    mandatory=[("how_high", how_high)],
                    optional=[("unit", unit)],
                    args=args, kwargs=kwargs
                )
                print(f"Jumping {how_high} {unit}")

        # Legal calls to this function
        Toady.jump(how_high=123)
        Toady.jump(123)
        Toady.jump(123, unit=FEET)
        Toady.jump(how_high=123, unit=FEET)

        # The main difference in object-based calls is the ability to omit the "mandatory" parameter since
        # it's value will be retrieved from the object's defaults instead
        smithers = Toady()
        smithers.jump()
        smithers.jump(how_high=123)
        smithers.jump(123)
        smithers.jump(123, unit=FEET)
        smithers.jump(how_high=123, unit=FEET)
        smithers.jump(unit=FEET)

    The mandatory and optional arguments mimic Python function argument lists, where the mandatory ones have no
    defaults and the optional ones do. This is how a function call would translate to mandatory/optional specs:

    .. code-block:: python

        def sample(a: bool, b: str, c: int = 5)
        # mandatory = [("a", None), ("b", None)], optional = [("c", 5)]

    Here is a sequence that flattens the arguments to a function taking a mandatory argument "a" and an optional
    argument "b":

        _flatten_arguments(mandatory=[("a", None)], optional=[("b", True)], args, kwargs)
        # args=[], kwargs={} -> raise og.OmniGraphError(missing attribute)
        # args=[3], kwargs={} -> returns (3, True)

    Args:
        mandatory: List of (arg_name, default_arg_value) for every mandatory argument. The sentinel value "_Unspecified"
                   is used as the default_arg_value to indicate that no value was provided.
        optional: List of (arg_name, default_arg_value) for every optional argument. The sentinel value "_Unspecified"
                   is used as the default_arg_value to indicate that no value was provided.
        args: List of positional args to check
        kwargs: Dictionary of keyword args to check, modified in place with the net resulting argument set

    Raises:
        og.OmniGraphError if the arguments were internally redundant or inconsistent
    """
    if mandatory is None:
        mandatory = []
    if optional is None:
        optional = []
    all_keywords = [name for name, _ in mandatory + optional]
    final_args = [value for _, value in mandatory + optional]

    # Walk the keyword args
    mandatory_found = {key: not isinstance(value, _UnspecifiedClass) for key, value in mandatory}
    if kwargs:
        index = 0  # noqa: SIM113 Index needed across two loops
        for name, _ in mandatory:
            if name in kwargs:
                final_args[index] = kwargs[name]
                mandatory_found[name] = True
            index += 1
        for name, _ in optional:
            if name in kwargs:
                final_args[index] = kwargs[name]
            index += 1

    # Walk the positional args, converting to the matching kwarg and checking for duplication
    if args:
        for index, arg in enumerate(args):
            try:
                keyword = all_keywords[index]
                if keyword in mandatory_found:
                    mandatory_found[keyword] = True
            except IndexError as error:
                raise og.OmniGraphError(
                    f"Argument {index} has no corresponding attribute definition - {all_keywords}"
                ) from error
            if keyword in kwargs:
                raise og.OmniGraphError(f"'{keyword}' cannot be specified both in both args={args} and kwargs={kwargs}")
            final_args[index] = arg

    # Report if any mandatory args were missing
    if not all(mandatory_found.values()):
        missing = [mandatory_key for mandatory_key, found in mandatory_found.items() if not found]
        raise og.OmniGraphError(f"Missing mandatory argument(s) {missing}")

    return final_args


# ====================================================================================================
@dataclass
class TypedValue:
    """Class that encapsulates an arbitrary value with an explicit data type. This can be used when the
    data type is ambiguous due to the limited set of native Python data types. For example it can differentiate
    between a float and double whereas in Python they are the same thing.
    """

    value: Any = None
    """Value of the data"""
    type: og.Type = og.Type(og.BaseDataType.UNKNOWN)  # noqa: A003
    """Type of the data"""

    def __post_init__(self):
        """Ensure that type information is an og.Type"""
        self.type = ObjectLookup.attribute_type(self.type)

    def has_type(self) -> bool:
        """Checks if the data has a known type

        Returns:
            bool: True iff the data value has an explicit type (i.e. is not type UNKNOWN)
        """
        return self.type.base_type != og.BaseDataType.UNKNOWN

    def __len__(self) -> int:
        """Returns the length of the value so that length can be taken on a value or typed value equally.
        The length of a None value is 0, any non-list has length 1.
        """
        try:
            return len(self.value)
        except TypeError:
            return 0 if self.value is None else 1

    def set(self, *args, **kwargs):  # noqa: A003
        """Set the data to a specific value and/or type. The regular __init__ can be passed (VALUE, TYPE) in the
        simplest case; this is for more flexible setting.

        The argument types are flexible and support the following syntax

            - set(): Sets the data value to None and makes it an UNKNOWN type
            - set(Any): Sets the data value and makes it an UNKNOWN type
            - set(Any, str|og.Type): Sets the data value and defines an explicit type
            - set(value=Any): Sets the data value and makes it an UNKNOWN type
            - set(value=Any, type=str|og.Type): Sets the data value and defines an explicit type

        No attempt is made to match the type to the value - it is assumed that if it is specified, it is correct.

        Raises:
            OmniGraphError: if the argument combinations are not one of the above, or the type could not be parsed
        """
        # Check to make sure the arguments are a legal combination
        try:
            if not args:
                if "value" not in kwargs:
                    # Allow the edge case of "no data" to be a
                    if not kwargs:
                        self.value = None
                        self.type = og.Type(og.BaseDataType.UNKNOWN)
                        return
                    raise og.OmniGraphError("Keyword args must at least contain 'value'")
                self.value = kwargs["value"]
                if len(kwargs) == 2:
                    if "type" not in kwargs:
                        raise og.OmniGraphError("'type' not found")
                    self.type = ObjectLookup.attribute_type(kwargs["type"])
                elif len(kwargs) > 2:
                    raise og.OmniGraphError("Too many keyword arguments")
            elif len(args) < 3:
                if kwargs:
                    raise og.OmniGraphError("Cannot use both args and kwargs together")
                self.value = args[0]
                if len(args) == 2:
                    self.type = ObjectLookup.attribute_type(args[1])
            else:
                raise og.OmniGraphError("Too many unnamed arguments")
        except og.OmniGraphError as error:
            raise og.OmniGraphError(
                "Arguments must be one of (VALUE), (VALUE, TYPE), (value=VALUE), or (value=VALUE, type=TYPE) -"
                f" saw ({args}, {kwargs}) ({error})"
            )


# ====================================================================================================
ValueToSet_t = Union[Any, TypedValue]
"""Typing that identifies a value that may or may not have an explicit type defined."""

AttributeValue_t = Tuple[AttributeWithValue_t, ValueToSet_t]
"""Typing for an Attribute/Value Pair"""
AttributeValues_t = Union[AttributeValue_t, List[AttributeValue_t]]
"""Typing for a list of Attribute/Value Pairs"""


# ====================================================================================================
DBG_EVAL = os.getenv("OGN_DEBUG_EVAL") is not None
DBG = os.getenv("OGN_DEBUG") is not None


def dbg(message: str):  # pragma no cover
    """Print out a debugging message - use DBG and dbg() to selectively enable it"""
    print(f"DBG: {message}", flush=True)


def dbg_eval(message: str):  # pragma no cover
    """Print out a debugging message if DBG_EVAL is enabled"""
    return DBG_EVAL and dbg(message)


# ================================================================================
def list_dimensions(value) -> int:  # pragma no cover
    """Returns the dimension of the value type, assuming all entries have the same subdimension.
    0 = single values
    1 = [] and ()
    2 = [[]] [()] (()) ([])
    etc.
    """
    if not isinstance(value, (list, tuple)) or isinstance(value, str):
        return 0
    return 1 + list_dimensions(value[0]) if len(value) > 0 else 1


# ================================================================================
async def load_example_file(example_file_name: str):
    """Load the contents of the USD example file onto the stage
    Loading will be effectively synchronous when called as "await load_example_file(X)".
    In a testing environment we need to run one test at a time since there is no guarantee
    that tests can run concurrently, especially when loading files. This method encapsulates
    the logic necessary to load a test file using the omni.kit.asyncapi method and then wait
    for it to complete before returning.

    Args:
        example_file_name: Name of the example file to load - if an absolute path use it as-is

    Raises:
        ValueError: test file is not a valid USD file
    """
    # Delayed until here because the PYTHONPATH is not set the first time this file is imported
    import omni.usd

    if not Usd.Stage.IsSupportedFile(example_file_name):
        raise ValueError("Only USD files can be loaded with this method")

    if os.path.isabs(example_file_name):
        path_to_file = example_file_name
    else:
        path_to_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", example_file_name))

    usd_context = omni.usd.get_context()
    usd_context.disable_save_to_recent_files()
    with open(path_to_file, "r", encoding="utf-8") as example_fd:
        first_line = example_fd.readline()
        if first_line.startswith("version"):
            raise ValueError(f"Do a 'git lfs pull' to update the contents of {path_to_file}")
    (result, error) = await omni.usd.get_context().open_stage_async(path_to_file)
    usd_context.enable_save_to_recent_files()
    return (result, error)


# ================================================================================
def non_const(func):
    """Simple decorator that runs any member function only if the member is a writable type"""

    @wraps(func)
    def wrapper_non_const(self, *args, **kwargs):
        if self.read_only:
            raise og.OmniGraphError(f"{self.__class__.__name__}.{func.__name__} can only be called on writable objects")
        return func(self, *args, **kwargs)

    return wrapper_non_const


# ==============================================================================================================

# ----------------------------------------------------------------------------------
_usd_scaler_array_types = {
    # scaler array
    og.BaseDataType.BOOL: Vt.BoolArray,
    og.BaseDataType.DOUBLE: Vt.DoubleArray,
    og.BaseDataType.FLOAT: Vt.FloatArray,
    og.BaseDataType.HALF: Vt.HalfArray,
    og.BaseDataType.INT: Vt.IntArray,
    og.BaseDataType.INT64: Vt.Int64Array,
    og.BaseDataType.TOKEN: Vt.TokenArray,
    og.BaseDataType.UINT: Vt.UIntArray,
    og.BaseDataType.UINT64: Vt.UInt64Array,
    og.BaseDataType.UCHAR: Vt.UCharArray,
}

_usd_no_role_tuple_types = {
    (og.BaseDataType.DOUBLE, 2, 0): Gf.Vec2d,
    (og.BaseDataType.DOUBLE, 3, 0): Gf.Vec3d,
    (og.BaseDataType.DOUBLE, 4, 0): Gf.Vec4d,
    (og.BaseDataType.FLOAT, 2, 0): Gf.Vec2f,
    (og.BaseDataType.FLOAT, 3, 0): Gf.Vec3f,
    (og.BaseDataType.FLOAT, 4, 0): Gf.Vec4f,
    (og.BaseDataType.HALF, 2, 0): Gf.Vec2h,
    (og.BaseDataType.HALF, 3, 0): Gf.Vec3h,
    (og.BaseDataType.HALF, 4, 0): Gf.Vec4h,
    (og.BaseDataType.INT, 2, 0): Gf.Vec2i,
    (og.BaseDataType.INT, 3, 0): Gf.Vec3i,
    (og.BaseDataType.INT, 4, 0): Gf.Vec4i,
    (og.BaseDataType.DOUBLE, 2, 1): Vt.Vec2dArray,
    (og.BaseDataType.DOUBLE, 3, 1): Vt.Vec3dArray,
    (og.BaseDataType.DOUBLE, 4, 1): Vt.Vec4dArray,
    (og.BaseDataType.FLOAT, 2, 1): Vt.Vec2fArray,
    (og.BaseDataType.FLOAT, 3, 1): Vt.Vec3fArray,
    (og.BaseDataType.FLOAT, 4, 1): Vt.Vec4fArray,
    (og.BaseDataType.HALF, 2, 1): Vt.Vec2hArray,
    (og.BaseDataType.HALF, 3, 1): Vt.Vec3hArray,
    (og.BaseDataType.HALF, 4, 1): Vt.Vec4hArray,
    (og.BaseDataType.INT, 2, 1): Vt.Vec2iArray,
    (og.BaseDataType.INT, 3, 1): Vt.Vec3iArray,
    (og.BaseDataType.INT, 4, 1): Vt.Vec4iArray,
}


# ==============================================================================================================
def attribute_value_as_usd(og_type: og.Type, value: Any, array_limit: Optional[int] = None) -> Any:
    """Returns the value, converted into a type suitable for setting through the USD API compatible with
    an attribute of the given type. It's assumed that anything passed in here has a valid USD attribute type;
    i.e. no extended attributes or bundles

    Args:
        og_type: The OG type of the given data
        value: The value read from the attribute
        array_limit: Arrays larger than this value will be truncated

    Returns:
        Any: The USD-compatible value
    """

    is_ndarray = isinstance(value, np.ndarray)

    if (og_type.array_depth > 0) and (array_limit is not None) and is_ndarray and (len(value) > array_limit):
        value = value[0:array_limit]

    # Handle the special cases with odd types first
    if og_type.role in [og.AttributeRole.FRAME, og.AttributeRole.MATRIX, og.AttributeRole.TRANSFORM]:
        dim = 2 if og_type.tuple_count == 4 else 3 if og_type.tuple_count == 9 else 4
        type_name = f"Matrix{dim}d"
        if og_type.array_depth > 0:
            return getattr(Vt, f"{type_name}Array").FromBuffer(
                np.array([np.array(element).reshape(dim, dim) for element in value])
            )
        return getattr(Gf, type_name)(np.array(value).reshape(dim, dim))

    if og_type.role == og.AttributeRole.TIMECODE:
        return Sdf.TimeCode(value) if og_type.array_depth == 0 else Sdf.TimeCodeArray(len(value), value)

    if og_type.role == og.AttributeRole.QUATERNION:
        quat_type = {
            og.BaseDataType.DOUBLE: [Gf.Quatd, Vt.QuatdArray],
            og.BaseDataType.FLOAT: [Gf.Quatf, Vt.QuatfArray],
            og.BaseDataType.HALF: [Gf.Quath, Vt.QuathArray],
        }
        (gf_type, vt_type) = quat_type[og_type.base_type]
        # Quaternions appear in memory and OGN as [i, j, k, r] but the Gf.Quat constructor expects [r, i, j, k] so
        # do the reordering for compatibility.
        if is_ndarray:
            py_array = value.tolist()
        else:
            py_array = value
        if og_type.array_depth > 0:
            return vt_type([gf_type(item[3], item[0], item[1], item[2]) for item in py_array])
        return gf_type(py_array[3], py_array[0], py_array[1], py_array[2])

    # relationships return a list of Sdf.Paths
    if og_type.base_type == og.BaseDataType.RELATIONSHIP:
        if not isinstance(value, list):
            value = [value]
        value = [Sdf.Path(str(x)) for x in value]
        return value

    with suppress(KeyError, AttributeError):
        if og_type.tuple_count > 1:
            usd_type = _usd_no_role_tuple_types[(og_type.base_type, og_type.tuple_count, og_type.array_depth)]
            if og_type.array_depth > 0:
                if is_ndarray:
                    value = usd_type.FromBuffer(value)
                else:
                    value = usd_type(value)
            else:
                if is_ndarray:
                    value = usd_type(*value.tolist())
                else:
                    value = usd_type(*value)
        elif og_type.array_depth > 0:
            # Special case string, path vs uchar[]
            if (og_type.base_type == og.BaseDataType.UCHAR) and (og_type.role != og.AttributeRole.NONE):
                return value
            vt_class = _usd_scaler_array_types[og_type.base_type]
            # OG returns token and token arrays as python str, List[str] instead of ndarray, so we
            # can't use FromBuffer for those.
            if is_ndarray:
                value = vt_class.FromBuffer(value)
            else:
                value = vt_class(value)
        return value

    return value


# ==============================================================================================================
def python_value_as_usd(og_type: og.Type, value: Any) -> Any:
    """Converts the given python value to the equivalent USD value

    Args:
        og_type: The OG type of the given data
        value: The pure python value (IE not USD or numpy)

    Returns:
        Any: The USD-compatible value
    """

    if og_type.role in [og.AttributeRole.FRAME, og.AttributeRole.MATRIX, og.AttributeRole.TRANSFORM]:
        dim = 2 if og_type.tuple_count == 4 else 3 if og_type.tuple_count == 9 else 4
        type_name = f"Matrix{dim}d"
        gf_type = getattr(Gf, type_name)
        if og_type.array_depth > 0:
            return getattr(Vt, f"{type_name}Array")([gf_type(item) for item in value])
        return gf_type(value)

    if og_type.role == og.AttributeRole.TIMECODE:
        return Sdf.TimeCode(float(value)) if og_type.array_depth == 0 else Sdf.TimeCodeArray(len(value), value)

    if og_type.role == og.AttributeRole.QUATERNION:
        quat_type = {
            og.BaseDataType.DOUBLE: [Gf.Quatd, Vt.QuatdArray],
            og.BaseDataType.FLOAT: [Gf.Quatf, Vt.QuatfArray],
            og.BaseDataType.HALF: [Gf.Quath, Vt.QuathArray],
        }
        (gf_type, vt_type) = quat_type[og_type.base_type]
        # Quaternions appear in memory and OGN as [i, j, k, r] but the Gf.Quat constructor expects [r, i, j, k] so
        # do the reordering for compatibility.
        if og_type.array_depth > 0:
            return vt_type([gf_type(item[3], item[0], item[1], item[2]) for item in value])
        return gf_type(value[3], value[0], value[1], value[2])

    with suppress(KeyError, AttributeError):
        if og_type.tuple_count > 1:
            usd_type = _usd_no_role_tuple_types[(og_type.base_type, og_type.tuple_count, og_type.array_depth)]
            if og_type.array_depth > 0:
                value = usd_type(value)
            else:
                value = usd_type(*value)
        elif og_type.array_depth > 0:
            # Special case string, path vs uchar[]
            if (og_type.base_type == og.BaseDataType.UCHAR) and (og_type.role != og.AttributeRole.NONE):
                return value
            vt_class = _usd_scaler_array_types[og_type.base_type]
            value = vt_class(value)
        return value

    return value


# ==============================================================================================================
def sync_to_usd(attribute: og.Attribute, value: Any):
    """This is necessary to update USD at the moment. Updating fabric and USD should be a feature that can
    be accessed at the low level for efficiency (e.g. in the IAttributeData interface).

    Args:
        attribute: Attribute to by synced to USD
        value: Value to be synced
    """
    # Delayed until here because the PYTHONPATH is not set the first time this file is imported
    import omni.usd

    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(attribute.get_node().get_prim_path())
    if prim.IsValid() and attribute.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
        try:
            # The Set method wants USD types for some attribute types so do the translation first
            attr_type = og.Controller.attribute_type(attribute)
            value = og.attribute_value_as_usd(attr_type, value)
            if attr_type.base_type == og.BaseDataType.RELATIONSHIP:
                prim.GetRelationship(attribute.get_name()).SetTargets(value)
            else:
                prim.GetAttribute(attribute.get_name()).Set(value)
        except Tf.ErrorException as error:
            carb.log_warn(f"Could not sync USD on attribute {attribute.get_name()} - {error}")
        except TypeError as error:
            # TODO: This occurs when the parameters to Set() don't match what USD expects. It could be fixed
            #       by special-casing every known mismatch but this section should be going away so it won't
            #       be done at this time. The current known failures are the quaternion types and arrays of the
            #       tuple-arrays (e.g. "quatd[4]", "double[3][]", "float[2][]", ...)
            carb.log_info(f"Could not set value on attribute {attribute.get_name()} - {error}")
        except Exception as error:  # pylint: disable=broad-except
            carb.log_warn(f"Unknown problem setting values - {error}")


# ==============================================================================================================
def remove_attributes_if(
    node: Nodes_t, attribute_filter_function: Optional[Callable[[og.Attribute], bool]] = None
) -> int:
    """Disconnects and removes the dynamic attributes on the given node which pass a given filter.

    Args:
        node: The node to remove attributes from
        attribute_filter_function: A function which returns True when given at prospective Attribute that should
                                   be removed. If None, all dynamic attributes will be removed.

    Returns:
        int: The number of attributes removed.
    """
    nodes = ObjectLookup.node(node)
    if not isinstance(nodes, list):
        nodes = [nodes]
    if not attribute_filter_function:
        attribute_filter_function = og.Attribute.is_dynamic

    attrs_to_remove = []
    for node_obj in nodes:
        attrs_to_remove += [attr for attr in node_obj.get_attributes() if attribute_filter_function(attr)]

    for attr in attrs_to_remove:
        og.cmds.DisconnectAllAttrs(attr=attr, modify_usd=True)

    for attr in attrs_to_remove:
        og.cmds.RemoveAttr(attribute=attr)

    return len(attrs_to_remove)


# ==============================================================================================================
def is_attribute_plain_data(attrib: Attribute_t) -> bool:
    """Is the given attribute numeric or string data?

    Args:
        attrib: The attribute in question

    Returns:
        bool: True if the given attribute is numeric or string data
    """
    a = ObjectLookup.attribute(attrib)
    tp = a.get_resolved_type()

    # ignore anything that we can't usefully expose or is potentially an error
    if tp.role in (
        og.AttributeRole.APPLIED_SCHEMA,
        og.AttributeRole.OBJECT_ID,
        og.AttributeRole.EXECUTION,
        og.AttributeRole.PRIM_TYPE_NAME,
        og.AttributeRole.UNKNOWN,
    ):
        return False

    if tp.base_type in (
        og.BaseDataType.RELATIONSHIP,
        og.BaseDataType.TAG,
        og.BaseDataType.ASSET,
        og.BaseDataType.CONNECTION,
        og.BaseDataType.UNKNOWN,
        og.BaseDataType.PRIM,
    ):
        return False

    # Skip known special attributes
    name = a.get_name()
    if name in ("UsdPrim", "IsTerminalNode", "Mesh", "node:type", "node:typeVersion"):
        return False

    return True


# =====================================================================
def graph_iterator(root: Optional[og.Graph] = None) -> og.Graph:
    """Generator function that provides the ability to walk through all graphs and their subgraphs in a manner similar
    to the os.walk function. The yield is the graph found at the current iteration step. It walks the graphs from the
    bottom up in a breadth-first way.

    Args:
        root: Starting graph - walk all graphs if None

    .. code-block:: python

        for graph in graph_iterator():
            print(f"Walking over graph at {graph.get_path_to_graph()}")

    Yields:
        omni.graph.core.Graph: Next graph in iteration
    """
    all_graphs = og.get_all_graphs() if root is None else [root]
    for root_graph in all_graphs:
        yield root_graph

        subgraphs = root_graph.get_subgraphs()
        if subgraphs:
            for subgraph in subgraphs:
                yield from graph_iterator(subgraph)


# ==============================================================================================================
@dataclass
class GraphSettings:
    """Container for the set of settings in a graph. This is a class instead of a tuple so that future
    additions to the settings do not break backward compatibility
    """

    evaluator_type: str = "push"
    """Type of evaluator to use by default on the graph"""
    file_format_version: Tuple[int, int] = (0, 0)
    """File format version used when creating the graph"""
    fabric_backing: str = og.GraphBackingType.GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY
    """Type of data backing the graph has"""
    pipeline_stage: str = og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION
    """Pipeline stage to which the graph belongs"""
    evaluation_mode: str = og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_STANDALONE
    """Default evaluation mode of the graph"""


# --------------------------------------------------------------------------------------------------------------
def get_graph_settings(graph: Graph_t) -> GraphSettings:
    """Return the current settings for the graph. This is just a copy of the settings. Changing it will not
    affect the graph's settings. To do that you must go through the graph ABI

    Args:
        graph: Graph for which the settings are to be retrieved

    Returns:
        omni.graph.core.GraphSettings: The settings currently on the graph
    """
    # Delayed until here because the PYTHONPATH is not set the first time this file is imported
    import omni.usd

    settings = GraphSettings()
    # The path to the settings prim is fixed
    graph_prim = omni.usd.get_context().get_stage().GetPrimAtPath(graph.get_path_to_graph())
    if not graph_prim.IsA(OmniGraphSchema.OmniGraph):
        carb.log_warn(f"Graph prim for {graph.get_path_to_graph()} not found - using default settings")
    else:
        graph_schema = OmniGraphSchema.OmniGraph(graph_prim)
        settings.evaluator_type = graph_schema.GetEvaluatorTypeAttr().Get()
        settings.file_format_version = graph_schema.GetFileFormatVersionAttr().Get()
        settings.fabric_backing = graph_schema.GetFabricCacheBackingAttr().Get()
        settings.pipeline_stage = graph_schema.GetPipelineStageAttr().Get()
        settings.evaluation_mode = graph_schema.GetEvaluationModeAttr().Get()
    return settings


_og_in_compute_count = 0


def _begin_in_compute():
    """
    Mark entry of OmniGraph runtime computation.
    Must be paired with a subsequent call to _end_in_compute()
    """
    global _og_in_compute_count
    _og_in_compute_count = _og_in_compute_count + 1


def _end_in_compute():
    """
    Mark exit of OmniGraph runtime computation.
    Must be paired with a prior call to _begin_in_compute()
    """
    global _og_in_compute_count
    if _og_in_compute_count > 0:
        _og_in_compute_count = _og_in_compute_count - 1
    else:
        carb.log_error("undo.end_disabled() called without matching prior call to undo.begin_disabled()")


@contextmanager
def in_compute():
    """Mark block of code executed at runtime. Optimizations can apply like setting values without undo support.

    This function is a context manager.

    Example:

    .. code-block:: python

        with omni.graph.in_compute():
            exec(state._code_object)

    Yields:
        None: Just used to mark a compute section
    """
    _begin_in_compute()
    try:
        yield
    finally:
        _end_in_compute()


def is_in_compute() -> bool:
    """Mark entry of OmniGraph runtime computation.

    Returns:
        bool: True if compute is currently underway
    """
    return _og_in_compute_count > 0


# ==============================================================================================================
_kit_version_re = re.compile(r"([0-9]+)(?:\.([0-9]+))?")


def get_kit_version() -> Tuple[int, int]:
    """
    Returns the currently running version of Kit as a tuple of (major, minor) numbers.

    Returns:
        (int, int): Major, minor version of Kit running, or (0, 0) if the Kit version could not be determined.
    """
    major = 0
    minor = 0
    version_str = carb.settings.get_settings().get("/app/extensions/target/kit")
    version_match = re.match(_kit_version_re, version_str)
    if version_match:
        major = int(version_match.groups()[0])
        if len(version_match.groups()) > 1:
            minor = int(version_match.groups()[1])
    return (major, minor)


# ==============================================================================================================
# Deprecated type information - use the values in typing.py (also in the omni.graph.core module)
# (The "noqa" silences the linter's complaint that the import is unused.)
from .v1_5_0.utils import ATTRIBUTE_TYPE_HINTS  # noqa
from .v1_5_0.utils import ATTRIBUTE_TYPE_OR_LIST  # noqa
from .v1_5_0.utils import ATTRIBUTE_TYPE_TYPE_HINTS  # noqa
from .v1_5_0.utils import ATTRIBUTE_VALUE_PAIR  # noqa
from .v1_5_0.utils import ATTRIBUTE_VALUE_PAIRS  # noqa
from .v1_5_0.utils import EXTENDED_ATTRIBUTE_TYPE_HINTS  # noqa
from .v1_5_0.utils import GRAPH_TYPE_HINTS  # noqa
from .v1_5_0.utils import GRAPH_TYPE_OR_LIST  # noqa
from .v1_5_0.utils import NODE_TYPE_HINTS  # noqa
from .v1_5_0.utils import NODE_TYPE_OR_LIST  # noqa
from .v1_5_0.utils import get_omnigraph  # noqa
from .v1_5_0.utils import l10n  # noqa
