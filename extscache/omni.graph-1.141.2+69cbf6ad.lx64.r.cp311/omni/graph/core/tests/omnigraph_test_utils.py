# noqa: PLC0302
"""A set of utilities useful for testing OmniGraph.

Note that this file should not be imported directly, the API is in omni.graph.core.tests.

Available in this module are:
- omni.graph.core.tests.DataTypeHelper - a utility class to help iterate over all available data types
- omni.graph.core.tests.find_build_directory_above - find the root directory of the build
- omni.graph.core.tests.load_test_file - load a test file and wait for it to be ready
- omni.graph.core.tests.insert_sublayer - load a test file as a sublayer
- omni.graph.core.tests.dump_graph - conditionally call omni.graph.core.tests.print_current_graph
- omni.graph.core.tests.print_current_graph - print out the contents of the existing OmniGraphs
- omni.graph.core.tests.compare_lists - do an unordered comparison of two lists
- omni.graph.core.tests.verify_connections - confirm that a set of expected connections exists
- omni.graph.core.tests.verify_node_existence - confirm that a set of expected nodes exists
- omni.graph.core.tests.verify_values - confirm that a set of expected attribute values are correct
- omni.graph.core.tests.create_scope_node - create a Scope prim
- omni.graph.core.tests.create_cube - create a Cube prim
- omni.graph.core.tests.create_sphere - create a Sphere prim
- omni.graph.core.tests.create_cone - create a Cube prim
- omni.graph.core.tests.create_grid_mesh - Create a simple mesh consisting of a grid
- omni.graph.core.tests.create_input_and_output_grid_meshes - Create two meshes consisting of grids
"""
import inspect
import os
import unittest
from abc import ABC, abstractmethod
from contextlib import suppress
from dataclasses import dataclass
from math import isclose, isnan
from typing import Any, Dict, List, Optional, Tuple, Union

import carb
import numpy as np
import omni.graph.core as og
import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.usd
import OmniGraphSchemaTools
import usdrt.Sdf
from pxr import Sdf, Usd, UsdGeom

# If a node type version is unspecified then this is the value it gets.
# Keep in sync with kDefaultNodeTypeVersion in include/omni/graph/core/NodeTypeRegistrar.h
NODE_TYPE_VERSION_DEFAULT = 1


# ==============================================================================================================
class TestContextManager(ABC):
    """Definition of the context classes that can be temporarily enabled during tests.
    These can be passed in to the test_case_class() factory method to extend the capabilities it has that are
    hardcoded in this file by instantiating one of these classes and passing it through the extra_contexts= parameter.

    The __init__ gets called to instantiate the base class information required by the test case.
    The setUp() method gets called when the test case's setUp method is called (once for every test).
    The tearDown() method gets called when the test case's tearDown method is called (once for every test)
    """

    @abstractmethod
    def __init__(self):
        """Remember the setting name."""

    @abstractmethod
    async def setUp(self):
        """Called when the test case setUp() is called"""

    @abstractmethod
    async def tearDown(self):
        """Called when the test case tearDown() is called"""


# ==============================================================================================================
class SettingContext(TestContextManager):  # pragma: no cover
    """Helper class with an setUp and tearDown for modifying and restoring a carb setting"""

    def __init__(self, setting_name: str, temporary_value: any):
        """Remember the setting name."""
        super().__init__()
        self.__setting_name = setting_name
        self.__temporary_value = temporary_value
        self.__original_value = None

    async def setUp(self):
        """Save the current value of the setting and set it to the desired temporary value"""
        settings = carb.settings.get_settings()
        self.__original_value = settings.get(self.__setting_name)
        ogt.dbg(f"SETUP Setting: Change {self.__setting_name} from {self.__original_value} to {self.__temporary_value}")
        settings.set(self.__setting_name, self.__temporary_value)

    async def tearDown(self):
        """Restore the original value of the setting"""
        ogt.dbg(
            f"TEARDOWN Setting: Restore {self.__setting_name} to {self.__original_value} from {self.__temporary_value}"
        )
        carb.settings.get_settings().set(self.__setting_name, self.__original_value)


# ==============================================================================================================
class __ClearSceneContext(TestContextManager):
    """Helper class with an setUp and tearDown for potentially clearing the scene when a test is complete"""

    def __init__(self):  # noqa: PLW0246
        """Empty init is required since the parent is abstract"""
        super().__init__()

    async def setUp(self):
        """Nothing to do when setting up the test but the method is required"""
        ogt.dbg("SETUP ClearScene")

    async def tearDown(self):
        """If a clear was requested on tearDown do it now"""
        ogt.dbg("TEARDOWN ClearScene")
        await omni.usd.get_context().new_stage_async()


# ==============================================================================================================
def test_case_class(**kwargs) -> object:
    """ "Factory to return a base class to use for a test case configured with certain transient settings.

    The argument list is intentionally generic so that future changes can happen without impacting existing cases.
    The contexts will be invoked in the order specified below, with the extra_contexts being invoked in the order
    of the list passed in.

    Args:
        no_clear_on_finish (bool): If True then the scene will not be cleared after the test is complete
        extra_contexts (List[TestContextManager]): List of user-defined context managers to pass in
        deprecated (Tuple[str, DeprecationLevel]): Used to indicate this instantiation of the class has been deprecated
        base_class (object): Alternative base class for the test case, defaults to omni.kit.test.AsyncTestCase

    Return:
        Class object representing the base class for a test case with the given properties
    """
    # Check to see if an alternative base class was passed in
    base_class = omni.kit.test.AsyncTestCase
    with suppress(KeyError):
        base_class = kwargs["base_class"]

    # Issue the deprecation message if specified, but continue on
    deprecation = None
    with suppress(KeyError):
        deprecation = kwargs["deprecated"]

    # Create a container for classes that will manage the temporary setting changes
    custom_actions = []

    with suppress(KeyError):
        extra_contexts = kwargs["extra_contexts"]
        if not isinstance(extra_contexts, list):
            extra_contexts = [extra_contexts]
        for extra_context in extra_contexts:
            if not isinstance(extra_context, TestContextManager):
                raise ValueError(f"extra_contexts {extra_context} is not a TestContextManager")
            custom_actions.append(extra_context)

    if "no_clear_on_finish" not in kwargs or not kwargs["no_clear_on_finish"]:
        custom_actions.append(__ClearSceneContext())

    # --------------------------------------------------------------------------------------------------------------
    # Construct the customized test case base class object using the temporary setting and base class information
    class OmniGraphCustomTestCase(base_class):
        """A custom constructed test case base class that performs the prescribed setUp and tearDown actions.

        Members:
            __actions: List of actions to perform on setUp (calls action.setUp()) and tearDown (calls action.tearDown())
        """

        async def setUp(self):
            """Set up the test by saving and then setting up all of the action contexts"""
            super().setUp()

            if deprecation is not None:
                ogt.DeprecateMessage.deprecated(deprecation[0], deprecation[1])

            # Start with no test failures registered
            og.set_test_failure(False)

            # Always start with a clean slate as the settings may conflict with something in the scene
            await omni.usd.get_context().new_stage_async()
            await omni.kit.app.get_app().next_update_async()

            # Perform the custom action entries
            self.__action_contexts = custom_actions
            for action in self.__action_contexts:
                await action.setUp()

        async def tearDown(self):
            """Complete the test by tearing down all of the action contexts"""
            # Perform the custom action tearDowns
            for action in reversed(self.__action_contexts):
                await action.tearDown()
            super().tearDown()

    # Return the constructed class definition
    return OmniGraphCustomTestCase


OmniGraphTestCase = test_case_class()
"""Default test case base class used for most OmniGraph tests"""

OmniGraphTestCaseNoClear = test_case_class(no_clear_on_finish=True)
"""Test case class that leaves the stage as it was when the test completed"""


# ==============================================================================================================
class DataTypeHelper:  # pragma: no cover
    """
    Class providing utility methods to assist with the comprehensive data type tests.
    Example of how to walk all of the valid input attribute values:

        for attribute_type in DataTypeHelper.all_attribute_types():
            try:
                input_value = DataTypeHelper.test_input_value(attribute_type)
                process(input_value)
            except TypeError:
                pass  # Cannot process this type yet
    """

    _ATTR_TEST_DATA = None

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def all_test_data() -> Dict[str, List[Any]]:
        """Returns a dict mapping all available Sdf attribute type names and a pair of sample values of those types"""
        if DataTypeHelper._ATTR_TEST_DATA is None:
            # Lazily initialize since this data is not needed until tests request it
            test_data = {}
            for type_name in ogn.supported_attribute_type_names():
                attribute_type = og.AttributeType.type_from_ogn_type_name(type_name)
                sdf_type_name = og.AttributeType.sdf_type_name_from_type(attribute_type)
                if sdf_type_name is not None:
                    test_data[sdf_type_name] = ogn.get_attribute_manager_type(type_name).sample_values()
            DataTypeHelper._ATTR_TEST_DATA = test_data

        return DataTypeHelper._ATTR_TEST_DATA

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def all_attribute_types() -> List[str]:
        """Return the list of all supported attribute Sdf type names, including array versions"""
        return list(DataTypeHelper.all_test_data().keys())

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def test_input_value(attribute_type_name: str) -> Any:
        """
        :return: Test value on the input side of a node for the given attribute type
        :raise TypeError: If the attribute type is not yet supported
        """
        try:
            return DataTypeHelper.all_test_data()[attribute_type_name][0]  # noqa: PLE1136
        except KeyError as error:
            raise TypeError(f"Not yet supporting attribute type {attribute_type_name}") from error

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def test_output_value(attribute_type_name: str) -> any:
        """
        :return: Test value on the output side of a node for the given attribute type
        :raise TypeError: If the attribute type is not yet supported
        """
        try:
            return DataTypeHelper.all_test_data()[attribute_type_name][1]  # noqa: PLE1136
        except KeyError as error:
            raise TypeError(f"Not yet supporting attribute type {attribute_type_name}") from error

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def attribute_names(attribute_type_name: str, is_downstream_node: bool):
        """
        :param attribute_type_name: One of the available attribute types, including arrays of them (e.g. int and int[])
        :param is_downstream_node: True means it is one of the nodes accepting inputs, not computing anything itself
        :return: Pair of (INPUT_ATTRIBUTE_NAME, OUTPUT_ATTRIBUTE_NAME) used for the data test nodes
        """
        suffixes = ["from_input", "from_output"] if is_downstream_node else ["original", "computed"]
        return [f"a_{attribute_type_name.replace('[]','_array')}_{suffixes[i]}" for i in range(2)]


# --------------------------------------------------------------------------------------------------------------
def dump_graph(force_dump: bool = False):  # pragma: no cover
    """Utility to conditionally print the current contents of the scene and graph"""
    if ogt.OGN_DEBUG or force_dump:
        print_current_graph()
        print(omni.usd.get_context().get_stage().GetRootLayer().ExportToString())


# --------------------------------------------------------------------------------------------------------------
def find_build_directory_above(start_at: Optional[str] = None) -> str:  # pragma: no cover
    """Find the absolute path to the _build/ directory above the current one.
    If any of the folder up that path contains `dev/ogn` subfolder that is prioritized over `_build/`
    for shallow package support which don't have _build folder packaged at all.
    Using this method avoids the problems associated with following symlinks up a tree.
    :param start_at: Location at which to start looking; if None start at this script's location
    :raises ValueError: if there is no build directory above this file's directory
    :return: Path in which the _build/ directory was found
    """
    starting_file = __file__ if start_at is None else start_at
    build_directory = os.path.abspath(starting_file)
    (parent_directory, leaf_directory) = os.path.split(build_directory)
    while leaf_directory != "_build":
        if os.path.exists(f"{parent_directory}/dev/ogn"):
            return f"{parent_directory}/dev"
        build_directory = parent_directory
        (parent_directory, leaf_directory) = os.path.split(build_directory)
        if parent_directory == build_directory:
            raise ValueError(f"No _build/ directory above {starting_file}")
    return build_directory


# --------------------------------------------------------------------------------------------------------------
async def load_test_file(
    test_file_name: str, use_caller_subdirectory: bool = False
) -> Tuple[bool, str]:  # pragma: no cover
    """
    Load the contents of the USD test file onto the stage, synchronously, when called as "await load_test_file(X)".
    In a testing environment we need to run one test at a time since there is no guarantee
    that tests can run concurrently, especially when loading files. This method encapsulates
    the logic necessary to load a test file using the omni.kit.asyncapi method and then wait
    for it to complete before returning.

    Args:
        test_file_name: Name of the test file to load - if an absolute path use it as-is
        use_caller_subdirectory: If True, look in the data/ subdirectory of the caller's directory for the file
                                 otherwise it will look in the data/ subdirectory below this directory

    Returns:
        (LOAD_SUCCEEDED[bool], LOAD_ERROR[str])

    Raises:
        ValueError if the test file is not a valid USD file
    """
    if not Usd.Stage.IsSupportedFile(test_file_name):
        raise ValueError("Only USD files can be loaded with this method")

    if os.path.isabs(test_file_name):
        path_to_file = test_file_name
    elif use_caller_subdirectory:
        path_to_file = os.path.join(os.path.dirname(inspect.stack()[1][1]), "data", test_file_name)
    else:
        path_to_file = os.path.join(os.path.dirname(__file__), "data", test_file_name)
    # Unicode error might happen if the file is a .usd rather than .usda and it was already pulled so that case is okay
    with suppress(UnicodeDecodeError):
        with open(path_to_file, "r", encoding="utf-8") as test_fd:
            first_line = test_fd.readline()
            if first_line.startswith("version"):
                raise ValueError(f"Do a 'git lfs pull' to update the contents of {path_to_file}")

    usd_context = omni.usd.get_context()
    usd_context.disable_save_to_recent_files()
    (result, error) = await usd_context.open_stage_async(path_to_file)
    usd_context.enable_save_to_recent_files()
    dump_graph()
    await omni.kit.app.get_app().next_update_async()
    return (result, str(error))


# --------------------------------------------------------------------------------------------------------------
async def insert_sublayer(test_file_name: str, use_caller_subdirectory: bool = False) -> bool:  # pragma: no cover
    """
    Inserts a sublayer from the given usd file into the current stage

    Args:
        test_file_name: Name of the test file to load - if an absolute path use it as-is
        use_caller_subdirectory: If True, look in the data/ subdirectory of the caller's directory for the file
                                 otherwise it will look in the data/ subdirectory below this directory

    Returns:
        True if the layer was loaded successfully, false otherwise
    """

    if os.path.isabs(test_file_name):
        path_to_file = test_file_name
    elif use_caller_subdirectory:
        path_to_file = os.path.join(os.path.dirname(inspect.stack()[1][1]), "data", test_file_name)
    else:
        path_to_file = os.path.join(os.path.dirname(__file__), "data", test_file_name)

    root_layer = omni.usd.get_context().get_stage().GetRootLayer()
    sublayer_position = len(root_layer.subLayerPaths)
    new_layer = Sdf.Layer.FindOrOpen(path_to_file)

    if new_layer:
        relative_path = omni.client.make_relative_url(root_layer.identifier, new_layer.identifier).replace("\\", "/")
        root_layer.subLayerPaths.insert(sublayer_position, relative_path)
    else:
        return False

    await omni.kit.app.get_app().next_update_async()
    return True


# --------------------------------------------------------------------------------------------------------------
def print_current_graph(
    show_attributes: bool = True, show_connections: bool = True, show_evaluation: bool = True
):  # pragma: no cover
    """
    Finds the current compute graph and prints out the nodes and attributes in it.

    Args:
        show_attributes: If True then include the attributes on the nodes
        show_connections: If True then include the connections between the nodes
        show_evaluation: If True then include the evaluation info for the graph
    """
    flags = []
    if show_attributes:
        flags.append("attributes")
    if show_connections:
        flags.append("connections")
    if show_evaluation:
        flags.append("evaluation")
    print(og.OmniGraphInspector().as_json(og.get_all_graphs()[0], flags=flags), flush=True)


# --------------------------------------------------------------------------------------------------------------
def compare_lists(expected_values: list, actual_values: list, comparing_what: str):
    """Compare the values in two lists, returning a relevant message if they are different, None if not"""
    extra_values = set(actual_values) - set(expected_values)
    missing_values = set(expected_values) - set(actual_values)

    if extra_values:
        return f"Unexpected {comparing_what} found - {extra_values}"

    if missing_values:
        return f"Expected {comparing_what} missing - {missing_values}"

    return None


# --------------------------------------------------------------------------------------------------------------
def verify_connections(connections_expected: list):  # pragma: no cover
    """
    Confirm that the list of connections passed in exists in the compute graph, and are the only connections present.
    The argument is a list of pairs (SRC, DST) corresponding to the connection SRC -> DST
    """
    graph = og.get_all_graphs()[0]
    if not graph.is_valid():
        return "Compute graph has no valid contexts"
    ogt.dbg(f"Expecting {connections_expected}")

    # Collect connection information in both directions to verify they are the same
    upstream_connections_found = []
    downstream_connections_found = []

    comparison_errors = []

    nodes = graph.get_nodes()
    # Ignore the default nodes since they may change and this test doesn't care
    nodes_of_interest = [
        node
        for node in nodes
        if node.get_prim_path().find("/default") != 0
        and node.get_prim_path().find("/Omniverse") < 0
        and node.get_prim_path() != "/World"
        and node.get_prim_path() != "/"
    ]
    for node in nodes_of_interest:
        attributes_on_node = node.get_attributes()
        for attribute in attributes_on_node:
            this_attr = node.get_attribute(attribute.get_name())
            this_attr_name = f"{node.get_prim_path()}.{attribute.get_name()}"
            upstream_connections = this_attr.get_upstream_connections()
            if len(upstream_connections) > 0:
                for connection in upstream_connections:
                    upstream_attr_name = f"{connection.get_node().get_prim_path()}.{connection.get_name()}"
                    upstream_connections_found.append((upstream_attr_name, this_attr_name))

            downstream_connections = this_attr.get_downstream_connections()
            if len(downstream_connections) > 0:
                for connection in downstream_connections:
                    downstream_attr_name = f"{connection.get_node().get_prim_path()}.{connection.get_name()}"
                    downstream_connections_found.append((this_attr_name, downstream_attr_name))
    ogt.dbg(f"Upstream = {upstream_connections_found}")
    ogt.dbg(f"Downstream = {downstream_connections_found}")

    comparison_error = compare_lists(
        upstream_connections_found, downstream_connections_found, "upstream/downstream pair"
    )
    if comparison_error is not None:
        comparison_errors.append(comparison_error)
    comparison_error = compare_lists(connections_expected, downstream_connections_found, "connection")
    if comparison_error is not None:
        comparison_errors.append(comparison_error)

    return comparison_errors


# --------------------------------------------------------------------------------------------------------------
def verify_node_existence(primitives_expected: list):  # pragma: no cover
    """
    Confirm that the list of nodes passed in exists in the compute graph.

    Args:
        primitives_expected: List of node names expected in the graph.

    Returns:
        A list of errors found, empty list if none
    """
    graph = og.get_all_graphs()[0]
    if not graph.is_valid():
        return ["Compute graph has no valid contexts"]

    comparison_errors = []

    nodes = graph.get_nodes()
    # Get the current nodes in the world, ignoring the defaults since they may change and this test doesn't care
    primitives_found = [node.get_prim_path() for node in nodes if node.get_prim_path() in primitives_expected]
    comparison_error = compare_lists(primitives_expected, primitives_found, "compute graph primitives")
    if comparison_error is not None:
        comparison_errors.append(comparison_error)

    return comparison_errors


# --------------------------------------------------------------------------------------------------------------
def verify_values(expected_value, actual_value, error_message: str):  # pragma: no cover
    """Generic assert comparison which uses introspection to choose the correct method to compare the data values

    Args:
        expected_value: Value that was expected to be seen
        actual_value: Actual value that was seen
        error_message: Message describing the error if they do not match

    Raises:
        ValueError: With error message if the values do not match
    """
    ogt.dbg(f"Comparing {actual_value} with expected {expected_value} - error = '{error_message}'")

    def to_np_array(from_value: Union[List, Tuple, np.ndarray]) -> np.ndarray:
        """Returns the list of values as a flattened numpy array"""
        # TODO: The only reason this is flattened at the moment is because Python matrix values are incorrectly
        #       extracted as a flat array. They should maintain their data shape.
        return np.array(from_value).flatten()

    def is_close(first_value: float, second_value: float):
        """Raise a ValueError iff the single float values are not equal or floating-point close"""
        # Handle the NaN values first, which don't equal each other but should compare to equal for testing purposes
        if isnan(first_value) and isnan(second_value):
            return
        if isnan(first_value) or isnan(second_value):
            raise ValueError("NaN is only equal to other NaN values")
        # Default tolerance is 1e-9, which is a little tight for most simple uses
        if not isclose(first_value, second_value, rel_tol=1e-9):
            if not isclose(first_value, second_value, rel_tol=1e-5):
                raise ValueError
            ogt.dbg("The tolerance had to be loosened to make this pass")

    try:
        if isinstance(expected_value, (list, tuple, np.ndarray)):
            # Empty arrays are okay but only if both are empty. Using len() to handle both lists and numpy arrays
            if not len(expected_value) or not len(actual_value):  # noqa: PLC1802
                if not len(expected_value) and not len(actual_value):  # noqa: PLC1802
                    return
                raise ValueError
            # Path arrays are order dependant and can be set with either a string array or a path array.
            if isinstance(actual_value[0], usdrt.Sdf.Path):
                test_value = expected_value
                if isinstance(expected_value[0], str):
                    test_value = [usdrt.Sdf.Path(p) for p in expected_value]
                if actual_value != test_value:
                    raise ValueError
            # Lists of strings must be compared element-wise
            elif isinstance(expected_value[0], str):
                if set(actual_value) != set(expected_value):
                    raise ValueError
            # Numeric arrays can use numpy
            else:
                expected_array = to_np_array(expected_value)
                actual_array = to_np_array(actual_value)
                # If there are any NaN values then the array has to be checked element-by-element
                if any(np.isnan(expected_array)) and any(np.isnan(actual_array)):
                    for expected, actual in zip(expected_array, actual_array):
                        is_close(expected, actual)
                elif not np.allclose(expected_array, actual_array):
                    raise ValueError
        elif isinstance(actual_value, (float, np.float32, np.float64, np.half)):
            is_close(actual_value, expected_value)
        # Single element Path arrays can also be verified with a single value string or path
        elif isinstance(actual_value, list) and len(actual_value) == 1 and isinstance(actual_value[0], usdrt.Sdf.Path):
            test_value = expected_value
            if isinstance(expected_value, str):
                test_value = usdrt.Sdf.Path(expected_value)
            if actual_value[0] != test_value:
                raise ValueError
        else:
            if actual_value != expected_value:
                raise ValueError
    except ValueError as error:
        raise ValueError(
            f"{error_message}: Expected '{expected_value}' ({type(expected_value)}), "
            f"saw '{actual_value}' ({type(actual_value)})"
        ) from error


# --------------------------------------------------------------------------------------------------------------
def create_scope_node(prim_name: str, attribute_data: Optional[Dict[str, Any]] = None) -> str:  # pragma: no cover
    """Create a Scope prim at the given path, populated with the attribute data.

    This prim is a good source for a bundle attribute connection for testing.

    Args:
        prim_name: Name to give the prim within the current stage
        attribute_data: Dictionary of attribute names and the value the attribute should have in the prim
            The key is the name of the attribute in the prim.
            The value is the attribute information as a tuple of (TYPE, ATTRIBUTE_VALUE)
                TYPE: OGN name of the base data type
                ATTRIBUTE_VALUE: Data stored in the attribute within the prim

    Returns:
        Full path to the prim within the current stage (usually the path passed in)
    """
    if attribute_data is None:
        attribute_data = {}
    stage = omni.usd.get_context().get_stage()
    prim_path = omni.usd.get_stage_next_free_path(stage, "/" + prim_name, True)
    prim = stage.DefinePrim(prim_path, "Scope")
    prim.CreateAttribute("node:type", Sdf.ValueTypeNames.Token).Set("Scope")
    return prim


# --------------------------------------------------------------------------------------------------------------
def create_cube(stage, prim_name: str, displayColor: tuple) -> Usd.Prim:  # noqa: N803  # pragma: no cover
    path = omni.usd.get_stage_next_free_path(stage, "/" + prim_name, True)
    prim = stage.DefinePrim(path, "Cube")
    prim.CreateAttribute("primvars:displayColor", Sdf.ValueTypeNames.Color3fArray).Set([displayColor])
    prim.CreateAttribute("size", Sdf.ValueTypeNames.Double).Set(1.0)
    return prim


# --------------------------------------------------------------------------------------------------------------
def create_sphere(stage, prim_name: str, displayColor: tuple) -> Usd.Prim:  # noqa: N803  # pragma: no cover
    path = omni.usd.get_stage_next_free_path(stage, "/" + prim_name, True)
    prim = stage.DefinePrim(path, "Sphere")
    prim.CreateAttribute("primvars:displayColor", Sdf.ValueTypeNames.Color3fArray).Set([displayColor])
    prim.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(1.0)
    return prim


# --------------------------------------------------------------------------------------------------------------
def create_cone(stage, prim_name: str, displayColor: tuple) -> Usd.Prim:  # noqa: N803  # pragma: no cover
    path = omni.usd.get_stage_next_free_path(stage, "/" + prim_name, True)
    prim = stage.DefinePrim(path, "Cone")
    prim.CreateAttribute("primvars:displayColor", Sdf.ValueTypeNames.Color3fArray).Set([displayColor])
    prim.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(1.0)
    prim.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(1.0)
    return prim


# --------------------------------------------------------------------------------------------------------------
def create_grid_mesh(stage, path, counts=(32, 32), domain=(620, 620, 20), display_color=(1, 1, 1)):  # pragma: no cover
    mesh = UsdGeom.Mesh.Define(stage, path)
    mesh.CreateDoubleSidedAttr().Set(True)
    num_vertices = counts[0] * counts[1]
    num_triangles = (counts[0] - 1) * (counts[1] - 1)
    mesh.CreateFaceVertexCountsAttr().Set([3] * num_triangles * 2)
    face_vertex_indices = [0] * num_triangles * 6
    for i in range(counts[0] - 1):
        for j in range(counts[1] - 1):
            a = i * counts[0] + j
            b = a + 1
            c = a + counts[0]
            d = c + 1
            k = (i * (counts[0] - 1) + j) * 6
            face_vertex_indices[k : k + 6] = [a, b, d, a, d, c]
    mesh.CreateFaceVertexIndicesAttr().Set(face_vertex_indices)
    points = [(0, 0, 0)] * num_vertices
    for i in range(counts[0]):
        for j in range(counts[1]):
            points[i * counts[0] + j] = (i * domain[0] / (counts[0] - 1), j * domain[1] / (counts[1] - 1), domain[2])
    mesh.CreatePointsAttr().Set(points)
    mesh.CreateDisplayColorPrimvar().Set([display_color])
    return mesh


# --------------------------------------------------------------------------------------------------------------
def create_input_and_output_grid_meshes(stage):  # pragma: no cover
    input_grid = create_grid_mesh(stage, "/defaultPrim/inputGrid", display_color=(0.2784314, 0.64705884, 1))
    output_grid = create_grid_mesh(stage, "/defaultPrim/outputGrid", display_color=(0.784314, 0.64705884, 0.1))
    return (input_grid, output_grid)


# ==============================================================================================================
# Below here is support for generated tests
#
@dataclass
class _TestGraphAndNode:
    """Helper class to pass graph and node around in test utility methods below"""

    graph: og.Graph = None
    node: og.Node = None


# -----------------------------------------------------------------------------------------------------------
async def _test_clear_scene(
    tc: unittest.TestCase, test_run: Dict[str, Dict[str, Any]], reset_stage=True
):  # pragma: no cover
    """Clear the scene if test run requires it

    Note that this method is only ever used for tests that did not specify a
    specific test scene.

    Args:
        tc: Unit test case executing this method. Used to raise errors
        test_run: Dictionary consisting of a dictionary of dictionaries.
            The key is a path to the node in the test scene (empty if no test scene is
            specified), and the value contains up to the following four sub-lists and
            dictionary:
            - values for input attributes, set before the test starts
            - values for output attributes, checked after the test finishes
            - initial values for state attributes, set before the test starts
            - final values for state attributes, checked after the test finishes
            - setup to be used for populating the scene via controller
            For complete implementation see generate_user_test_data.
        reset_stage: If there is no setup argument, this will create a new stage when true.
            Set this to false to avoid accessive stage resets, which can slow down testing.
    """
    setup = test_run.get("setup", None)
    if setup or ((setup is None) and reset_stage):
        await omni.usd.get_context().new_stage_async()


# --------------------------------------------------------------------------------------------------------------
async def _test_setup_scene(  # pragma: no cover
    tc: unittest.TestCase,
    controller: og.Controller,
    test_graph_name: str,
    test_node_name: str,
    test_node_type: str,
    test_run: Dict[str, Dict[str, Any]],
    last_test_info: _TestGraphAndNode,
    instance_count=0,
) -> _TestGraphAndNode:
    """Setup the scene based on given test run dictionary

    Note that this method is only ever used for tests that did not specify a
    specific test scene.

    Args:
        tc: Unit test case executing this method. Used to raise errors
        controller: Controller object to use when constructing the scene (e.g. may have undo support disabled)
        test_graph_name: Graph name to use when constructing the scene
        test_node_name: Node name to use when constructing the scene without "setup" explicitly provided in test_run
        test_node_type: Node type to use when constructing the scene without "setup" explicitly provided in test_run
        test_run: Dictionary consisting of a dictionary of dictionaries.
            The key is a path to the node in the test scene (empty if no test scene is
            specified), and the value contains up to the following four sub-lists and
            dictionary:
            - values for input attributes, set before the test starts
            - values for output attributes, checked after the test finishes
            - initial values for state attributes, set before the test starts
            - final values for state attributes, checked after the test finishes
            - setup to be used for populating the scene via controller
            For complete implementation see generate_user_test_data.
        last_test_info: When executing multiple tests cases for the same node, this represents graph and node used in previous run
        instance_count: number of instances to create associated to this graph, in order to test vectorized compute

    Returns:
        Graph and node to use in current execution of the test
    """
    test_info = last_test_info

    setup = test_run.get("setup", None)
    if setup:
        (test_info.graph, test_nodes, _, _) = controller.edit(test_graph_name, setup)
        tc.assertTrue(test_nodes)
        test_info.node = test_nodes[0]
    elif (setup is None) or (test_info.graph is None) or (test_info.node is None):
        test_info.graph = controller.create_graph(test_graph_name)
        test_info.graph.set_auto_instancing_allowed(False)
        test_info.node = controller.create_node((test_node_name, test_info.graph), test_node_type)

    tc.assertTrue(test_info.graph is not None and test_info.graph.is_valid(), "Test graph invalid")
    tc.assertTrue(test_info.node is not None and test_info.node.is_valid(), "Test node invalid")
    test_info.graph.set_auto_instancing_allowed(False)
    await controller.evaluate(test_info.graph)

    inputs = test_run[""].get("inputs", [])
    state_set = test_run[""].get("state_set", [])

    values_to_set = inputs + state_set
    if values_to_set:
        for attribute_name, attribute_value, _ in values_to_set:
            controller.set(attribute=(attribute_name, test_info.node), value=attribute_value)

    # create some instance prims, and apply the graph on it
    if instance_count != 0:
        stage = omni.usd.get_context().get_stage()
        for i in range(instance_count):
            prim_name = f"/World/Test_Instance_Prim_{i}"
            stage.DefinePrim(prim_name)
            OmniGraphSchemaTools.applyOmniGraphAPI(stage, prim_name, test_graph_name)

    return test_info


# --------------------------------------------------------------------------------------------------------------
def _test_verify_scene(  # pragma: no cover
    tc: unittest.TestCase,
    controller: og.Controller,
    test_run: Dict[str, Dict[str, Any]],
    test_info: _TestGraphAndNode,
    error_msg: str,
    instance_count=0,
    node_path: str = "",
):
    """Verify the scene state based on given test run dictionary

    Args:
        tc: Unit test case executing this method. Used to raise errors
        controller: Controller object to use when constructing the scene (e.g. may have undo support disabled)
        test_run: Dictionary consisting of a dictionary of dictionaries.
            The key is a path to the node in the test scene (empty if no test scene is
            specified), and the value contains up to the following four sub-lists and
            dictionary:
            - values for input attributes, set before the test starts
            - values for output attributes, checked after the test finishes
            - initial values for state attributes, set before the test starts
            - final values for state attributes, checked after the test finishes
            - setup to be used for populating the scene via controller
            For complete implementation see generate_user_test_data.
        error_msg: Customized error message to use as a prefix for all unit test errors detected within this method
        instance_count: Number of instances associated to this graph that needs to be verified
        node_path: Path to the node in the test scene (blank by default/if a test scene was not specified).
    """
    outputs = test_run[node_path].get("outputs", [])
    state_get = test_run[node_path].get("state_get", [])

    for attribute_name, expected_value, on_gpu in outputs + state_get:
        # Skip explicit checks against data on the gpu.
        if on_gpu:
            continue

        if test_info:
            test_attribute = controller.attribute(attribute_name, test_info.node)
        elif node_path != "":
            test_attribute = controller.attribute(attribute_name, controller.node(node_path))
        expected_type = None
        if isinstance(expected_value, dict):
            expected_type = expected_value["type"]
            expected_value = expected_value["value"]

        if instance_count != 0:
            for i in range(instance_count):
                actual_output = controller.get(attribute=test_attribute, instance=i)
                verify_values(
                    expected_value,
                    actual_output,
                    f"{error_msg}: {attribute_name} attribute value error on instance {i}",
                )
        else:
            actual_output = controller.get(attribute=test_attribute)
            verify_values(expected_value, actual_output, f"{error_msg}: {attribute_name} attribute value error")
        if expected_type:
            tp = og.AttributeType.type_from_ogn_type_name(expected_type)
            actual_type = test_attribute.get_resolved_type()
            if tp != actual_type:
                raise ValueError(
                    f"{error_msg} - {attribute_name}: Expected {expected_type}, saw {actual_type.get_ogn_type_name()}"
                )


# ==============================================================================================================
#   _____   ______  _____   _____   ______  _____         _______  ______  _____
#  |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
#  | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
#  | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
#  | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
#  |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
#
