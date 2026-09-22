# noqa: PLC0302
"""This module serves both as population for testing AutoNode definitions and for embedded documentation.

The pattern for each of the function definitions is:

.. code-block:: python

    def construct_autonode_ID():
        # begin-autonode-ID
        import omni.graph.core as og
        import omni.graph.core.types as ot

        @og.create_node_type(OPTIONAL_ARGS)
        def autonode_ID(INPUT_ARGS) -> OUTPUT_ARG_TYPE:
            '''Description of ID'''
            # COMPUTE OF OUTPUTS FROM INPUTS
            return True
        # end-autonode-ID

The "ID" above represents the type of AutoNode definition being documented/tested. The description includes not just
the description of what the compute does but also enough information to describe the salient points of the ID
definition.

The decorated functions all appear inside a function definition because simply importing a decorated function is enough
to construct the node type so by hiding them in a function they will not get constructed until the function is called.

The extra imports, while exceedingly redundant, ensure that the code between the begin-autonode-ID/end-autonode-ID
pairs stands alone and can be copy/pasted into the script editor if the user wants to try it out.

The return value is always a tuple where the first member is a string indicating the expected full node type name,
so that calling code can easily find it and deregister it, and the second member is a dictionary describing test
data in the same format as you would find in a .ogn file. i.e. a map of input value(s) to expected output value(s).
Two tests are used that have different outputs to minimize the chance that the values are correct by accident.
For those special cases where this is not practical, e.g. bundles, special test cases are manually constructed
elsewhere.
"""
# This is the list of test functions below that should be tested manually as they cannot be trivially tested with
# the pattern described above. It is mostly used by the testing script to confirm that all of the required tests
# have been supplied.
TEST_MANUALLY = [
    "construct_autonode_bundle",
    "construct_autonode_execution",
    "construct_autonode_output_bundles",
]


# The AutoNode meta-information returned from the construct functions. It consists of a 2-tuple:
#   - The unique name of the constructed node type
#   - A single tuple or list of tuples containing 2 dictionaries
#     - The first dictionary is input_name:value for all input attributes to be set as part of a test script
#     - The second dictionary is output_name:value for all exepected output attribute values when the inputs are set
_TestConfiguration = tuple[str, tuple[dict[str, any], dict[str, any]] | list[tuple[dict[str, any], dict[str, any]]]]


# ==============================================================================================================
def construct_autonode_trivial() -> _TestConfiguration:
    # begin-autonode-trivial
    import omni.graph.core as og

    @og.create_node_type
    def autonode_trivial():
        """This node type has no inputs or outputs and performs no computation. The arguments and return type
        could optionally be annotated for clarity as autonode_trivial(None) -> None.
        """
        return

    # end-autonode-trivial

    return ("omni.graph.autonode_trivial", ())


# ==============================================================================================================
def construct_autonode_decoration_ui_name() -> _TestConfiguration:
    # begin-autonode-decoration-ui-name
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type(ui_name="Fluffy Bunny")
    def autonode_decoration_ui_name() -> ot.string:
        """This node type has no inputs and returns the UI name of its node type as output. It demonstrates how the
        optional ui_name argument can be used on the decorator to modify the name of the node type as it
        will appear to the user.
        """
        # We know the name of the node type by construction
        node_type = og.get_node_type("omni.graph.autonode_decoration_ui_name")
        # Get the metadata containing the UI name - will always return "Fluffy Bunny"
        return node_type.get_metadata(og.MetadataKeys.UI_NAME)

    # end-autonode-decoration-ui-name

    return ("omni.graph.autonode_decoration_ui_name", ({}, {"out_0": "Fluffy Bunny"}))


# ==============================================================================================================
def construct_autonode_decoration_unique_name() -> _TestConfiguration:
    # begin-autonode-decoration-unique-name
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type(unique_name="omni.graph.autonode_unique_name")
    def autonode_decoration_unique_name() -> ot.string:
        """This node type has no inputs and returns the unique name of its node type as output. It demonstrates how the
        optional unique_name argument can be used on the decorator to modify the name of the node type as it
        is used for registration and identification.
        """
        # Look up the node type name using the supplied unique name rather than the one that would have been
        # automatically generated (omni.graph.autonode_decoration_unique_name)
        node_type = og.get_node_type("omni.graph.autonode_unique_name")
        return node_type.get_node_type() if node_type.is_valid() else ""

    # end-autonode-decoration-unique-name

    return ("omni.graph.autonode_unique_name", ({}, {"out_0": "omni.graph.autonode_unique_name"}))


# ==============================================================================================================
def construct_autonode_decoration_add_execution_pins() -> _TestConfiguration:
    # begin-autonode-decoration-add-execution-pins
    import inspect

    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type(add_execution_pins=True)
    def autonode_decoration_add_execution_pins() -> ot.int:
        """This node type has no inputs and returns the number of attributes it has of type "execution". It
        demonstrates how the optional add_execution_pins argument can be used on the decorator to automatically
        include both an input and an output execution pin so that the node type can be easily included in the
        Action Graph.
        """
        frame = inspect.currentframe().f_back
        node = frame.f_locals.get("node")
        # This will return 2, counting the automatically added input and output execution attributes
        return sum(1 for attr in node.get_attributes() if attr.get_resolved_type().role == og.AttributeRole.EXECUTION)

    # end-autonode-decoration-add-execution-pins

    return ("omni.graph.autonode_decoration_add_execution_pins", ({}, {"out_0": 2}))


# ==============================================================================================================
def construct_autonode_decoration_metadata() -> _TestConfiguration:
    # begin-autonode-decoration-metadata
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type(metadata={"Emperor": "Palpatine"})
    def autonode_decoration_metadata() -> ot.string:
        """This node type has no inputs and returns a string consisting of the value of the metadata
        whose name was specified in the decorator "metadata" argument. It demonstrates how the optional metadata
        argument can be used on the decorator to automatically add metadata to the node type definition.
        """
        # We know the name of the node type by construction
        node_type = og.get_node_type("omni.graph.autonode_decoration_metadata")
        # Return the metadata with the custom name we specified - will always return "Palpatine"
        return node_type.get_metadata("Emperor")

    # end-autonode-decoration-metadata

    return ("omni.graph.autonode_decoration_metadata", ({}, {"out_0": "Palpatine"}))


# ==============================================================================================================
def construct_autonode_documented() -> _TestConfiguration:
    # begin-autonode-documented
    import numpy as np
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_documented(a: ot.point3d, b: ot.point3d) -> ot.vector3d:
        """This node type is an example of one where the intent of the attribute values is not easily apparent
        from their names. For that reason the documentation for what they are is embedded here in the function
        docstring. The function itself is calculating the normalized vector between two points. The attributes
        are documented explicitly here to provide more information to the user.
        Args:
            a: Point considered to be the origin of the vector
            b: Point considered to be the ending point of the vector
        Returns:
            out_0: Normalized vector from point a to point b
        """
        return (b - a) / np.linalg.norm(b - a)

    # end-autonode-documented

    return (
        "omni.graph.autonode_documented",
        [
            ({"a": np.array([0.0, 0.0, 5.0]), "b": np.array([3.0, 4.0, 5.0])}, {"out_0": np.array([0.6, 0.8, 0.0])}),
            ({"a": np.array([5.0, 3.0, 4.0]), "b": np.array([5.0, 0.0, 0.0])}, {"out_0": np.array([0.0, -0.6, -0.8])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_access_node() -> _TestConfiguration:
    # begin-autonode-access-node
    import inspect

    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_access_node() -> ot.string:
        """This node type is an example of how to use the inspect module to access the node that is evaluating
        this function as its compute. (The context could be accessed the same way.) The node type takes no
        inputs and returns as output the full path to the node being evaluated. It relies on some implementation
        details not changing but for the most part should be reliable.
        """
        frame = inspect.currentframe().f_back
        return frame.f_locals.get("node").get_prim_path()

    # end-autonode-access-node

    return (
        "omni.graph.autonode_access_node",
        [
            # Relies on knowing how the testing code creates nodes for testing
            ({}, {"out_0": "/TestGraph/TestNode"}),
        ],
    )


# ==============================================================================================================
def construct_autonode_logging() -> _TestConfiguration:
    # begin-autonode-logging
    import inspect

    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_logging(numerator: ot.double, denominator: ot.double) -> ot.double:
        """This node type is an example of how to use the inspect module to access the node that is evaluating
        this function in order to log error and warning messages. The function divides the first number by the
        second number, providing an error when the denominator is zero and a warning when both the numerator and
        denominators are zero, otherwise returning the first number divided by the second.
        """
        if denominator != 0.0:
            return numerator / denominator

        frame = inspect.currentframe().f_back
        node = frame.f_locals.get("node")
        if numerator == 0.0:
            node.log_compute_message(og.Severity.WARNING, "Indeterminate result from dividing 0 by 0")
        else:
            node.log_compute_message(og.Severity.WARNING, f"Infinite result from dividing {numerator} by 0")
        #
        # While you can also log an error by setting severity to og.Severity.ERROR, it is better to use an
        # exception so that the compute function will fail and no further computation will take place.
        # if numerator == 0.0:
        #     raise og.OmniGraphError("Indeterminate result from dividing 0 by 0")
        return 0.0

    # end-autonode-logging

    return (
        "omni.graph.autonode_logging",
        [
            ({"numerator": 1.0, "denominator": 2.0}, {"out_0": 0.5}),
            ({"numerator": 1.0, "denominator": 0.0}, {"out_0": 0.0}),
            ({"numerator": 0.0, "denominator": 0.0}, {"out_0": 0.0}),
        ],
    )


# ==============================================================================================================
def construct_autonode_per_node_data() -> _TestConfiguration:
    # begin-autonode-per-node-data
    import inspect

    import omni.graph.core as og
    import omni.graph.core.types as ot

    unique_id = 57
    per_node_data = {}

    @og.create_node_type
    def autonode_per_node_data(increment: ot.int) -> ot.int:
        """This node type is an example of how to use the inspect module to access the node that is evaluating
        this function in order to create per-node personal data. This particular example provides a monotonic ID
        that increases for each node created by maintaining a local per-node dictionary that uses the node's
        internal ID as a key.
        """
        nonlocal unique_id
        nonlocal per_node_data
        frame = inspect.currentframe().f_back
        node_id = frame.f_locals.get("node").node_id()
        if node_id not in per_node_data:
            per_node_data[node_id] = unique_id
            unique_id += increment
        return per_node_data[node_id]

    # end-autonode-per-node-data

    return (
        "omni.graph.autonode_per_node_data",
        [
            ({"increment": 1}, {"out_0": 57}),
        ],
    )


# ==============================================================================================================
def construct_autonode_output_bundles() -> _TestConfiguration:
    # begin-autonode-output-bundles
    import inspect

    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_output_bundles() -> ot.bundle:
        """This node type is an example of how to use the inspect module to access the node and context of evaluation
        in order to construct a bundle for use as an output value.
        """
        frame = inspect.currentframe().f_back
        node = frame.f_locals.get("node")
        context = frame.f_locals.get("context")
        new_bundle = og.BundleContents(context, node, "outputs_out_0", read_only=False, gpu_by_default=False)
        new_bundle.add_attributes([og.Type(og.BaseDataType.INT)], ["fizzbin"])

        return new_bundle

    # end-autonode-output-bundles

    return ("omni.graph.autonode_output_bundles", None)


# ==============================================================================================================
def construct_autonode_multi_simple() -> _TestConfiguration:
    # begin-autonode-multi-simple
    import statistics as st

    import numpy as np
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_multi_simple(values: ot.floatarray) -> tuple[ot.float, ot.float, ot.float]:
        """Takes in a list of floating point values and returns three outputs that are the mean, median,
        and mode of the values in the list. The outputs will be named "out_0", "out_1", and "out_2".
        """
        return (values.mean(), np.median(values), st.mode(values))

    # end-autonode-multi-simple

    return (
        "omni.graph.autonode_multi_simple",
        [
            ({"values": [0.0, 1.0, 2.0, 2.0, 5.0]}, {"out_0": 2.0, "out_1": 2.0, "out_2": 2.0}),
            ({"values": [0.0, 100.0, 7.0, 0.0, 3.0]}, {"out_0": 22.0, "out_1": 3.0, "out_2": 0.0}),
        ],
    )


# ==============================================================================================================
def construct_autonode_multi_tuple() -> _TestConfiguration:
    # begin-autonode-multi-tuple
    import numpy as np
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_multi_tuple(original: ot.matrix2d) -> tuple[ot.matrix2d, ot.matrix2d]:
        """Takes in a 2x2 matrix and returns two outputs that are the inverse and transpose of the matrix.
        Reports an error if the matrix is not invertible. Note that even though the data types themselves
        are tuples the return values will be correctly interpreted as being separate output attributes
        with each of the outputs itself being a tuple value. The outputs will be named "out_1" and "out_2".
        """
        try:
            return (original.transpose(), np.linalg.inv(original))
        except np.linalg.LinAlgError as error:
            raise og.OmniGraphError(f"Could not invert matrix {original}") from error

    # end-autonode-multi-tuple

    return (
        "omni.graph.autonode_multi_tuple",
        [
            (
                {"original": np.array([[1.0, 2.0], [3.0, 4.0]])},
                {"out_0": np.array([[1.0, 3.0], [2.0, 4.0]]), "out_1": np.array([[-2.0, 1.0], [1.5, -0.5]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_bool() -> _TestConfiguration:
    # begin-autonode-bool
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_bool(first_value: ot.bool, second_value: ot.bool) -> ot.boolean:
        """Takes in two boolean values and outputs the logical AND of them.
        The types of both inputs and the return value are Python booleans.
        Note that the return type name is the Warp-compatible "boolean", which is just a synonym for "bool".
        """
        return first_value and second_value

    # end-autonode-bool

    return (
        "omni.graph.autonode_bool",
        [
            ({"first_value": True, "second_value": True}, {"out_0": True}),
            ({"first_value": True, "second_value": False}, {"out_0": False}),
        ],
    )


# ==============================================================================================================
def construct_autonode_boolarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-boolarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_boolarray(first_value: ot.boolarray, second_value: ot.boolarray) -> ot.boolarray:
        """Takes in two arrays of boolean attributes and returns an array with the logical AND of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=bool) where "N" is the
        size of the array determined at runtime.
        """
        return first_value & second_value

    # end-autonode-boolarray

    return (
        "omni.graph.autonode_boolarray",
        [
            (
                {"first_value": np.array([True, False]), "second_value": np.array([True, True])},
                {"out_0": np.array([True, False])},
            ),
            (
                {"first_value": np.array([True, False]), "second_value": np.array([False, False])},
                {"out_0": np.array([False, False])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_bundle() -> _TestConfiguration:
    # begin-autonode-bundle
    import inspect

    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_bundle(bundle: ot.bundle, added: ot.int) -> ot.bundle:
        """Takes in a bundle value and outputs a bundle containing everything in the input bundle plus a count
        of "added" extra integer members named "added_0", "added_1", etc. Use the special value "added = 0" to
        indicate that the bundle should be cleared.
        The types of both inputs and the return value are og.BundleContents. When put into Fabric the bundle is
        stored as a data bucket and in USD it is represented as a target or reference to a prim when connected.

        Note how, since AutoNode definitions do not have direct access to the node, the inspect module must be
        used to get at it in order to construct an output bundle.
        """
        frame = inspect.currentframe().f_back
        node = frame.f_locals.get("node")
        context = frame.f_locals.get("context")
        result = og.BundleContents(context, node, "outputs_out_0", read_only=False, gpu_by_default=False)
        result.clear()
        if bundle.valid:
            result.bundle = bundle

        if added > 0:
            first_index = result.size
            for index in range(added):
                result.bundle.create_attribute(f"added_{index + first_index}", og.Type(og.BaseDataType.INT))

        return result

    # end-autonode-bundle

    return ("omni.graph.autonode_bundle", None)


# ==============================================================================================================
def construct_autonode_color3d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color3d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color3d(first_value: ot.color3d, second_value: ot.color3d) -> ot.color3d:
        """Takes in two colord[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float64). When put into
        Fabric the values are stored as 3 double-precision values. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color3d

    return (
        "omni.graph.autonode_color3d",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color3darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color3darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color3darray(first_value: ot.color3darray, second_value: ot.color3darray) -> ot.color3darray:
        """Takes in two arrays of color3d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color3darray

    return (
        "omni.graph.autonode_color3darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color3f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color3f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color3f(first_value: ot.color3f, second_value: ot.color3f) -> ot.color3f:
        """Takes in two colorf[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float32). When put into
        Fabric the values are stored as 3 single-precision values. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color3f

    return (
        "omni.graph.autonode_color3f",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color3farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color3farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color3farray(first_value: ot.color3farray, second_value: ot.color3farray) -> ot.color3farray:
        """Takes in two arrays of color3f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color3farray

    return (
        "omni.graph.autonode_color3farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color3h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color3h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color3h(first_value: ot.color3h, second_value: ot.color3h) -> ot.color3h:
        """Takes in two colorh[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float16). When put into
        Fabric the values are stored as 3 half-precision values. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color3h

    return (
        "omni.graph.autonode_color3h",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color3harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color3harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color3harray(first_value: ot.color3harray, second_value: ot.color3harray) -> ot.color3harray:
        """Takes in two arrays of color3h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color3harray

    return (
        "omni.graph.autonode_color3harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color4d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color4d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color4d(first_value: ot.color4d, second_value: ot.color4d) -> ot.color4d:
        """Takes in two color4d values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float64). When put into
        Fabric the values are stored as 4 double-precision values. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color4d

    return (
        "omni.graph.autonode_color4d",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color4darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color4darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color4darray(first_value: ot.color4darray, second_value: ot.color4darray) -> ot.color4darray:
        """Takes in two arrays of color4d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color4darray

    return (
        "omni.graph.autonode_color4darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color4f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color4f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color4f(first_value: ot.color4f, second_value: ot.color4f) -> ot.color4f:
        """Takes in two color4f values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float32). When put into
        Fabric the values are stored as 4 single-precision values. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color4f

    return (
        "omni.graph.autonode_color4f",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color4farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color4farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color4farray(first_value: ot.color4farray, second_value: ot.color4farray) -> ot.color4farray:
        """Takes in two arrays of color4f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color4farray

    return (
        "omni.graph.autonode_color4farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color4h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color4h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color4h(first_value: ot.color4h, second_value: ot.color4h) -> ot.color4h:
        """Takes in two color4h values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float16). When put into
        Fabric the values are stored as 4 half-precision values. The color role is applied to USD and OmniGraph types as
        an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color4h

    return (
        "omni.graph.autonode_color4h",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_color4harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-color4harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_color4harray(first_value: ot.color4harray, second_value: ot.color4harray) -> ot.color4harray:
        """Takes in two arrays of color4h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The color role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-color4harray

    return (
        "omni.graph.autonode_color4harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double() -> _TestConfiguration:
    # begin-autonode-double
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double(first_value: ot.double, second_value: ot.double) -> ot.float64:
        """Takes in two double precision values and outputs the sum of them.
        The types of both inputs and the return value are Python floats as Python does not distinguish between
        different precision levels. When put into Fabric and USD the values are stored as double.
        precision values.
        Note that the return type is the Warp-compatible "float64" which is a synonym for "double".
        """
        return first_value + second_value

    # end-autonode-double

    return (
        "omni.graph.autonode_double",
        [
            ({"first_value": 1.0, "second_value": 2.0}, {"out_0": 3.0}),
            ({"first_value": -1.0, "second_value": 3.0}, {"out_0": 2.0}),
        ],
    )


# ==============================================================================================================
def construct_autonode_doublearray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-doublearray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_doublearray(first_value: ot.doublearray, second_value: ot.doublearray) -> ot.doublearray:
        """Takes in two arrays of double attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-doublearray

    return (
        "omni.graph.autonode_doublearray",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([4.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([2.0, 2.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double2() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-double2
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double2(first_value: ot.double2, second_value: ot.double2) -> ot.double2:
        """Takes in two double[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.float64). When put into
        Fabric and USD the values are stored as two double-precision floating point values.
        """
        return first_value + second_value

    # end-autonode-double2

    return (
        "omni.graph.autonode_double2",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([2.0, 4.0])},
                {"out_0": np.array([3.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 6.0])},
                {"out_0": np.array([2.0, 4.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double2array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-double2array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double2array(first_value: ot.double2array, second_value: ot.double2array) -> ot.double2array:
        """Takes in two arrays of double2 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(2,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-double2array

    return (
        "omni.graph.autonode_double2array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0], [1.25, 2.25], [1.5, 2.5]]),
                    "second_value": np.array([[10.0, 20.0], [10.25, 20.25], [10.5, 20.5]]),
                },
                {"out_0": np.array([[11.0, 22.0], [11.5, 22.5], [12.0, 23.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0]]), "second_value": np.array([[3.0, 4.0]])},
                {"out_0": np.array([[2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double3() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-double3
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double3(first_value: ot.double3, second_value: ot.double3) -> ot.double3:
        """Takes in two double[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float64). When put into
        Fabric and USD the values are stored as three double-precision floating point values.
        """
        return first_value + second_value

    # end-autonode-double3

    return (
        "omni.graph.autonode_double3",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double3array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-double3array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double3array(first_value: ot.double3array, second_value: ot.double3array) -> ot.double3array:
        """Takes in two arrays of double3 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-double3array

    return (
        "omni.graph.autonode_double3array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double4() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-double4
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double4(first_value: ot.double4, second_value: ot.double4) -> ot.double4:
        """Takes in two double[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float64). When put into
        Fabric and USD the values are stored as four double-precision floating point values.
        """
        return first_value + second_value

    # end-autonode-double4

    return (
        "omni.graph.autonode_double4",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_double4array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-double4array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_double4array(first_value: ot.double4array, second_value: ot.double4array) -> ot.double4array:
        """Takes in two arrays of double4 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-double4array

    return (
        "omni.graph.autonode_double4array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_execution() -> _TestConfiguration:
    # begin-autonode-execution
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_execution(first_trigger: ot.execution, second_trigger: ot.execution) -> ot.execution:
        """Takes two execution pins and triggers the output only when both of them are enabled.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels. When put into Fabric and USD the values are stored as 32-bit precision
        integer values.
        """
        if first_trigger == og.ExecutionAttributeState.ENABLED and second_trigger == og.ExecutionAttributeState.ENABLED:
            return og.ExecutionAttributeState.ENABLED
        return og.ExecutionAttributeState.DISABLED

    # end-autonode-execution

    # The triggering requires more complex set up with an Action Graph and so must be done manually.
    return ("omni.graph.autonode_execution", None)


# ==============================================================================================================
def construct_autonode_float() -> _TestConfiguration:
    # begin-autonode-float
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float(first_value: ot.float, second_value: ot.float) -> ot.float32:
        """Takes in two single-precision floating point values and outputs the sum of them.
        The types of both inputs and the return value are Python floats as Python does not distinguish between
        different precision levels. When put into Fabric and USD the values are stored as single-precision
        floating point values.
        Note that the return type is the Warp-compatible "float32" which is a synonym for "float".
        """
        return first_value + second_value

    # end-autonode-float

    return (
        "omni.graph.autonode_float",
        [
            ({"first_value": 1.0, "second_value": 2.0}, {"out_0": 3.0}),
            ({"first_value": -1.0, "second_value": 3.0}, {"out_0": 2.0}),
        ],
    )


# ==============================================================================================================
def construct_autonode_floatarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-floatarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_floatarray(first_value: ot.floatarray, second_value: ot.floatarray) -> ot.floatarray:
        """Takes in two arrays of float attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-floatarray

    return (
        "omni.graph.autonode_floatarray",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([4.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([2.0, 2.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_float2() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-float2
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float2(first_value: ot.float2, second_value: ot.float2) -> ot.float2:
        """Takes in two float[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.float32). When put into
        Fabric and USD the values are stored as two single-precision floating point values.
        """
        return first_value + second_value

    # end-autonode-float2

    return (
        "omni.graph.autonode_float2",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([2.0, 4.0])},
                {"out_0": np.array([3.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 6.0])},
                {"out_0": np.array([2.0, 4.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_float2array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-float2array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float2array(first_value: ot.float2array, second_value: ot.float2array) -> ot.float2array:
        """Takes in two arrays of float2 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(2,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-float2array

    return (
        "omni.graph.autonode_float2array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0], [1.25, 2.25], [1.5, 2.5]]),
                    "second_value": np.array([[10.0, 20.0], [10.25, 20.25], [10.5, 20.5]]),
                },
                {"out_0": np.array([[11.0, 22.0], [11.5, 22.5], [12.0, 23.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0]]), "second_value": np.array([[3.0, 4.0]])},
                {"out_0": np.array([[2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_float3() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-float3
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float3(first_value: ot.float3, second_value: ot.float3) -> ot.float3:
        """Takes in two float[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float32). When put into
        Fabric and USD the values are stored as three single-precision floating point values.
        """
        return first_value + second_value

    # end-autonode-float3

    return (
        "omni.graph.autonode_float3",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_float3array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-float3array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float3array(first_value: ot.float3array, second_value: ot.float3array) -> ot.float3array:
        """Takes in two arrays of float3 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-float3array

    return (
        "omni.graph.autonode_float3array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_float4() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-float4
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float4(first_value: ot.float4, second_value: ot.float4) -> ot.float4:
        """Takes in two float[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float32). When put into
        Fabric and USD the values are stored as four single-precision floating point values.
        """
        return first_value + second_value

    # end-autonode-float4

    return (
        "omni.graph.autonode_float4",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_float4array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-float4array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_float4array(first_value: ot.float4array, second_value: ot.float4array) -> ot.float4array:
        """Takes in two arrays of float4 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-float4array

    return (
        "omni.graph.autonode_float4array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_frame4d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-frame4d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_frame4d(first_value: ot.frame4d, second_value: ot.frame4d) -> ot.frame4d:
        """Takes in two frame4d values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,4), dtype=numpy.float64). When put
        into Fabric the values are stored as a set of 16 double-precision values. USD uses the special frame4d type.
        """
        return first_value + second_value

    # end-autonode-frame4d

    input1a = np.random.rand(4, 4)
    input1b = np.random.rand(4, 4)
    result1 = input1a + input1b

    input2a = np.identity(4, dtype=np.float64)
    input2b = np.identity(4, dtype=np.float64)
    result2 = 2.0 * np.identity(4, dtype=np.float64)

    return (
        "omni.graph.autonode_frame4d",
        [
            ({"first_value": input1a, "second_value": input1b}, {"out_0": result1}),
            ({"first_value": input2a, "second_value": input2b}, {"out_0": result2}),
        ],
    )


# ==============================================================================================================
def construct_autonode_frame4darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-frame4darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_frame4darray(first_value: ot.frame4darray, second_value: ot.frame4darray) -> ot.frame4darray:
        """Takes in two frame4darray values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,4,N), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. When put into Fabric the values are stored as an array of sets
        of 16 double-precision values. USD stores it as the native frame4d[] type.
        """
        return first_value + second_value

    # end-autonode-frame4darray

    input1a = [np.random.rand(4, 4), np.random.rand(4, 4), np.random.rand(4, 4)]
    input1b = [np.random.rand(4, 4), np.random.rand(4, 4), np.random.rand(4, 4)]
    result1 = [a + b for a, b in zip(input1a, input1b)]

    input2a = [np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64)]
    input2b = [np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64)]
    result2 = [2.0 * np.identity(4, dtype=np.float64)] * 3

    return (
        "omni.graph.autonode_frame4darray",
        [
            ({"first_value": np.array(input1a), "second_value": np.array(input1b)}, {"out_0": np.array(result1)}),
            ({"first_value": np.array(input2a), "second_value": np.array(input2b)}, {"out_0": np.array(result2)}),
        ],
    )


# ==============================================================================================================
def construct_autonode_half() -> _TestConfiguration:
    # begin-autonode-half
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half(first_value: ot.half, second_value: ot.half) -> ot.float16:
        """Takes in two half-precision floating point values and outputs the sum of them.
        The types of both inputs and the return value are Python floats as Python does not distinguish between
        different precision levels. When put into Fabric and USD the values are stored as half
        precision floating point values.
        Note that the return type is the Warp-compatible "float16" which is a synonym for "half".
        """
        return first_value + second_value

    # end-autonode-half

    return (
        "omni.graph.autonode_half",
        [
            ({"first_value": 1.0, "second_value": 2.0}, {"out_0": 3.0}),
            ({"first_value": -1.0, "second_value": 3.0}, {"out_0": 2.0}),
        ],
    )


# ==============================================================================================================
def construct_autonode_halfarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-halfarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_halfarray(first_value: ot.halfarray, second_value: ot.halfarray) -> ot.halfarray:
        """Takes in two arrays of half attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-halfarray

    return (
        "omni.graph.autonode_halfarray",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([4.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([2.0, 2.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_half2() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-half2
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half2(first_value: ot.half2, second_value: ot.half2) -> ot.half2:
        """Takes in two half[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.float16). When put into
        Fabric and USD the values are stored as two 16-bit floating point values.
        """
        return first_value + second_value

    # end-autonode-half2

    return (
        "omni.graph.autonode_half2",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([2.0, 4.0])},
                {"out_0": np.array([3.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 6.0])},
                {"out_0": np.array([2.0, 4.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_half2array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-half2array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half2array(first_value: ot.half2array, second_value: ot.half2array) -> ot.half2array:
        """Takes in two arrays of half2 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(2,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-half2array

    return (
        "omni.graph.autonode_half2array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0], [1.25, 2.25], [1.5, 2.5]]),
                    "second_value": np.array([[10.0, 20.0], [10.25, 20.25], [10.5, 20.5]]),
                },
                {"out_0": np.array([[11.0, 22.0], [11.5, 22.5], [12.0, 23.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0]]), "second_value": np.array([[3.0, 4.0]])},
                {"out_0": np.array([[2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_half3() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-half3
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half3(first_value: ot.half3, second_value: ot.half3) -> ot.half3:
        """Takes in two half[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float16). When put into
        Fabric and USD the values are stored as three 16-bit floating point values.
        """
        return first_value + second_value

    # end-autonode-half3

    return (
        "omni.graph.autonode_half3",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_half3array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-half3array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half3array(first_value: ot.half3array, second_value: ot.half3array) -> ot.half3array:
        """Takes in two arrays of half3 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-half3array

    return (
        "omni.graph.autonode_half3array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_half4() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-half4
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half4(first_value: ot.half4, second_value: ot.half4) -> ot.half4:
        """Takes in two half[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float16). When put into
        Fabric and USD the values are stored as four 16-bit floating point values.
        """
        return first_value + second_value

    # end-autonode-half4

    return (
        "omni.graph.autonode_half4",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_half4array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-half4array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_half4array(first_value: ot.half4array, second_value: ot.half4array) -> ot.half4array:
        """Takes in two arrays of half4 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-half4array

    return (
        "omni.graph.autonode_half4array",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_int() -> _TestConfiguration:
    # begin-autonode-int
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int(first_value: ot.int, second_value: ot.int) -> ot.int32:
        """Takes in two 32-bit precision integer values and outputs the sum of them.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels. When put into Fabric and USD the values are stored as 32-bit precision
        integer values.
        Note that the return type is the Warp-compatible "int32" which is a synonym for "int".
        """
        return first_value + second_value

    # end-autonode-int

    return (
        "omni.graph.autonode_int",
        [
            ({"first_value": 1, "second_value": 2}, {"out_0": 3}),
            ({"first_value": -1, "second_value": 3}, {"out_0": 2}),
        ],
    )


# ==============================================================================================================
def construct_autonode_intarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-intarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_intarray(first_value: ot.intarray, second_value: ot.intarray) -> ot.intarray:
        """Takes in two arrays of integer attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.int32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-intarray

    return (
        "omni.graph.autonode_intarray",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([3, 4])}, {"out_0": np.array([4, 6])}),
            ({"first_value": np.array([-1, -2]), "second_value": np.array([3, 4])}, {"out_0": np.array([2, 2])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_int2() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int2
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int2(first_value: ot.int2, second_value: ot.int2) -> ot.int2:
        """Takes in two int[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.int32). When put into
        Fabric and USD the values are stored as two 32-bit integer values.
        """
        return first_value + second_value

    # end-autonode-int2

    return (
        "omni.graph.autonode_int2",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([2, 4])}, {"out_0": np.array([3, 6])}),
            ({"first_value": np.array([-1, -2]), "second_value": np.array([3, 6])}, {"out_0": np.array([2, 4])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_int2array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int2array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int2array(first_value: ot.int2array, second_value: ot.int2array) -> ot.int2array:
        """Takes in two arrays of int2 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(2,N,), dtype=numpy.int32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-int2array

    return (
        "omni.graph.autonode_int2array",
        [
            (
                {
                    "first_value": np.array([[1, 2], [3, 4], [5, 6]]),
                    "second_value": np.array([[10, 20], [30, 40], [50, 60]]),
                },
                {"out_0": np.array([[11, 22], [33, 44], [55, 66]])},
            ),
            ({"first_value": np.array([[-1, -2]]), "second_value": np.array([[3, 4]])}, {"out_0": np.array([[2, 2]])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_int3() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int3
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int3(first_value: ot.int3, second_value: ot.int3) -> ot.int3:
        """Takes in two int[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.int32). When put into
        Fabric and USD the values are stored as three 32-bit integer values.
        """
        return first_value + second_value

    # end-autonode-int3

    return (
        "omni.graph.autonode_int3",
        [
            ({"first_value": np.array([1, 2, 3]), "second_value": np.array([2, 4, 6])}, {"out_0": np.array([3, 6, 9])}),
            (
                {"first_value": np.array([-1, -2, -3]), "second_value": np.array([3, 6, 9])},
                {"out_0": np.array([2, 4, 6])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_int3array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int3array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int3array(first_value: ot.int3array, second_value: ot.int3array) -> ot.int3array:
        """Takes in two arrays of int3 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.int32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-int3array

    return (
        "omni.graph.autonode_int3array",
        [
            (
                {
                    "first_value": np.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]]),
                    "second_value": np.array([[10, 20, 30], [30, 40, 50], [50, 60, 70]]),
                },
                {"out_0": np.array([[11, 22, 33], [33, 44, 55], [55, 66, 77]])},
            ),
            (
                {"first_value": np.array([[-1, -2, -3]]), "second_value": np.array([[3, 4, 5]])},
                {"out_0": np.array([[2, 2, 2]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_int4() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int4
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int4(first_value: ot.int4, second_value: ot.int4) -> ot.int4:
        """Takes in two int[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.int32). When put into
        Fabric and USD the values are stored as two 32-bit integer values.
        """
        return first_value + second_value

    # end-autonode-int4

    return (
        "omni.graph.autonode_int4",
        [
            (
                {"first_value": np.array([1, 2, 3, 4]), "second_value": np.array([2, 4, 6, 8])},
                {"out_0": np.array([3, 6, 9, 12])},
            ),
            (
                {"first_value": np.array([-1, -2, -3, -4]), "second_value": np.array([3, 6, 9, 12])},
                {"out_0": np.array([2, 4, 6, 8])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_int4array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int4array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int4array(first_value: ot.int4array, second_value: ot.int4array) -> ot.int4array:
        """Takes in two arrays of int4 attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.int32) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-int4array

    return (
        "omni.graph.autonode_int4array",
        [
            (
                {
                    "first_value": np.array([[1, 2, 3, 4], [3, 4, 5, 6], [5, 6, 7, 8]]),
                    "second_value": np.array([[10, 20, 30, 40], [30, 40, 50, 60], [50, 60, 70, 80]]),
                },
                {"out_0": np.array([[11, 22, 33, 44], [33, 44, 55, 66], [55, 66, 77, 88]])},
            ),
            (
                {"first_value": np.array([[-1, -2, -3, -4]]), "second_value": np.array([[3, 4, 5, 6]])},
                {"out_0": np.array([[2, 2, 2, 2]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_int64() -> _TestConfiguration:
    # begin-autonode-int64
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int64(first_value: ot.int64, second_value: ot.int64) -> ot.int64:
        """Takes in two 64-bit precision integer values and outputs the sum of them.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels. When put into Fabric and USD the values are stored as 64-bit precision
        integer values.
        """
        return first_value + second_value

    # end-autonode-int64

    return (
        "omni.graph.autonode_int64",
        [
            ({"first_value": 1, "second_value": 2}, {"out_0": 3}),
            ({"first_value": -1, "second_value": 3}, {"out_0": 2}),
        ],
    )


# ==============================================================================================================
def construct_autonode_int64array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-int64array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_int64array(first_value: ot.int64array, second_value: ot.int64array) -> ot.int64array:
        """Takes in two arrays of 64-bit integer attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.int64) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-int64array

    return (
        "omni.graph.autonode_int64array",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([3, 4])}, {"out_0": np.array([4, 6])}),
            ({"first_value": np.array([-1, -2]), "second_value": np.array([3, 4])}, {"out_0": np.array([2, 2])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_matrix2d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-matrix2d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_matrix2d(first_value: ot.matrix2d, second_value: ot.matrix2d) -> ot.matrix2d:
        """Takes in two matrix2d values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(2,2), dtype=numpy.float64). When put
        into Fabric and USD the values are stored as a list of 4 double-precision values.
        """
        return first_value + second_value

    # end-autonode-matrix2d

    input1a = np.random.rand(2, 2)
    input1b = np.random.rand(2, 2)
    result1 = input1a + input1b

    input2a = np.identity(2, dtype=np.float64)
    input2b = np.identity(2, dtype=np.float64)
    result2 = 2.0 * np.identity(2, dtype=np.float64)

    return (
        "omni.graph.autonode_matrix2d",
        [
            ({"first_value": input1a, "second_value": input1b}, {"out_0": result1}),
            ({"first_value": input2a, "second_value": input2b}, {"out_0": result2}),
        ],
    )


# ==============================================================================================================
def construct_autonode_matrix2darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-matrix2darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_matrix2darray(first_value: ot.matrix2darray, second_value: ot.matrix2darray) -> ot.matrix2darray:
        """Takes in two matrix2darray values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,2,2), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.. When put into Fabric the values are stored as an array of sets
        of 9 double-precision values. USD stores it as the native matrix2d[] type.
        """
        return first_value + second_value

    # end-autonode-matrix2darray

    input1a = [np.random.rand(2, 2), np.random.rand(2, 2), np.random.rand(2, 2)]
    input1b = [np.random.rand(2, 2), np.random.rand(2, 2), np.random.rand(2, 2)]
    result1 = [a + b for a, b in zip(input1a, input1b)]

    input2a = [np.identity(2, dtype=np.float64), np.identity(2, dtype=np.float64), np.identity(2, dtype=np.float64)]
    input2b = [np.identity(2, dtype=np.float64), np.identity(2, dtype=np.float64), np.identity(2, dtype=np.float64)]
    result2 = [2.0 * np.identity(2, dtype=np.float64)] * 3

    return (
        "omni.graph.autonode_matrix2darray",
        [
            ({"first_value": np.array(input1a), "second_value": np.array(input1b)}, {"out_0": np.array(result1)}),
            ({"first_value": np.array(input2a), "second_value": np.array(input2b)}, {"out_0": np.array(result2)}),
        ],
    )


# ==============================================================================================================
def construct_autonode_matrix3d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-matrix3d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_matrix3d(first_value: ot.matrix3d, second_value: ot.matrix3d) -> ot.matrix3d:
        """Takes in two matrix3d values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,3), dtype=numpy.float64). When put
        into Fabric and USD the values are stored as a list of 9 double-precision values.
        """
        return first_value + second_value

    # end-autonode-matrix3d

    input1a = np.random.rand(3, 3)
    input1b = np.random.rand(3, 3)
    result1 = input1a + input1b

    input2a = np.identity(3, dtype=np.float64)
    input2b = np.identity(3, dtype=np.float64)
    result2 = 2.0 * np.identity(3, dtype=np.float64)

    return (
        "omni.graph.autonode_matrix3d",
        [
            ({"first_value": input1a, "second_value": input1b}, {"out_0": result1}),
            ({"first_value": input2a, "second_value": input2b}, {"out_0": result2}),
        ],
    )


# ==============================================================================================================
def construct_autonode_matrix3darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-matrix3darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_matrix3darray(first_value: ot.matrix3darray, second_value: ot.matrix3darray) -> ot.matrix3darray:
        """Takes in two matrix3darray values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,3,N), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.. When put into Fabric the values are stored as an array of sets
        of 9 double-precision values. USD stores it as the native matrix3d[] type.
        """
        return first_value + second_value

    # end-autonode-matrix3darray

    input1a = [np.random.rand(3, 3), np.random.rand(3, 3), np.random.rand(3, 3)]
    input1b = [np.random.rand(3, 3), np.random.rand(3, 3), np.random.rand(3, 3)]
    result1 = [a + b for a, b in zip(input1a, input1b)]

    input2a = [np.identity(3, dtype=np.float64), np.identity(3, dtype=np.float64), np.identity(3, dtype=np.float64)]
    input2b = [np.identity(3, dtype=np.float64), np.identity(3, dtype=np.float64), np.identity(3, dtype=np.float64)]
    result2 = [2.0 * np.identity(3, dtype=np.float64)] * 3

    return (
        "omni.graph.autonode_matrix3darray",
        [
            ({"first_value": np.array(input1a), "second_value": np.array(input1b)}, {"out_0": np.array(result1)}),
            ({"first_value": np.array(input2a), "second_value": np.array(input2b)}, {"out_0": np.array(result2)}),
        ],
    )


# ==============================================================================================================
def construct_autonode_matrix4d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-matrix4d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_matrix4d(first_value: ot.matrix4d, second_value: ot.matrix4d) -> ot.matrix4d:
        """Takes in two matrix4d values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,4), dtype=numpy.float64). When put
        into Fabric and USD the values are stored as a list of 9 double-precision values.
        """
        return first_value + second_value

    # end-autonode-matrix4d

    input1a = np.random.rand(4, 4)
    input1b = np.random.rand(4, 4)
    result1 = input1a + input1b

    input2a = np.identity(4, dtype=np.float64)
    input2b = np.identity(4, dtype=np.float64)
    result2 = 2.0 * np.identity(4, dtype=np.float64)

    return (
        "omni.graph.autonode_matrix4d",
        [
            ({"first_value": input1a, "second_value": input1b}, {"out_0": result1}),
            ({"first_value": input2a, "second_value": input2b}, {"out_0": result2}),
        ],
    )


# ==============================================================================================================
def construct_autonode_matrix4darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-matrix4darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_matrix4darray(first_value: ot.matrix4darray, second_value: ot.matrix4darray) -> ot.matrix4darray:
        """Takes in two matrix4darray values and outputs the sum of them.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,4,N), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.. When put into Fabric the values are stored as an array of sets
        of 16 double-precision values. USD stores it as the native matrix4d[] type.
        """
        return first_value + second_value

    # end-autonode-matrix4darray

    input1a = [np.random.rand(4, 4), np.random.rand(4, 4), np.random.rand(4, 4)]
    input1b = [np.random.rand(4, 4), np.random.rand(4, 4), np.random.rand(4, 4)]
    result1 = [a + b for a, b in zip(input1a, input1b)]

    input2a = [np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64)]
    input2b = [np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64), np.identity(4, dtype=np.float64)]
    result2 = [2.0 * np.identity(4, dtype=np.float64)] * 3

    return (
        "omni.graph.autonode_matrix4darray",
        [
            ({"first_value": np.array(input1a), "second_value": np.array(input1b)}, {"out_0": np.array(result1)}),
            ({"first_value": np.array(input2a), "second_value": np.array(input2b)}, {"out_0": np.array(result2)}),
        ],
    )


# ==============================================================================================================
def construct_autonode_normal3d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-normal3d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_normal3d(first_value: ot.normal3d, second_value: ot.normal3d) -> ot.normal3d:
        """Takes in two normald[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float64). When put into
        Fabric the values are stored as 3 double-precision values. The normal role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-normal3d

    return (
        "omni.graph.autonode_normal3d",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_normal3darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-normal3darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_normal3darray(first_value: ot.normal3darray, second_value: ot.normal3darray) -> ot.normal3darray:
        """Takes in two arrays of normal3d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The normal role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-normal3darray

    return (
        "omni.graph.autonode_normal3darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_normal3f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-normal3f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_normal3f(first_value: ot.normal3f, second_value: ot.normal3f) -> ot.normal3f:
        """Takes in two normalf[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float32). When put into
        Fabric the values are stored as 3 single-precision values. The normal role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-normal3f

    return (
        "omni.graph.autonode_normal3f",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_normal3farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-normal3farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_normal3farray(first_value: ot.normal3farray, second_value: ot.normal3farray) -> ot.normal3farray:
        """Takes in two arrays of normal3f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The normal role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-normal3farray

    return (
        "omni.graph.autonode_normal3farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_normal3h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-normal3h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_normal3h(first_value: ot.normal3h, second_value: ot.normal3h) -> ot.normal3h:
        """Takes in two normalh[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float16). When put into
        Fabric the values are stored as 3 half-precision values. The normal role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-normal3h

    return (
        "omni.graph.autonode_normal3h",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_normal3harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-normal3harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_normal3harray(first_value: ot.normal3harray, second_value: ot.normal3harray) -> ot.normal3harray:
        """Takes in two arrays of normal3h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The normal role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-normal3harray

    return (
        "omni.graph.autonode_normal3harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_objectid() -> _TestConfiguration:
    # begin-autonode-objectid
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_objectid(first_value: ot.objectid, second_value: ot.objectid) -> ot.objectid:
        """Takes in two objectId values and outputs the larger of them.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels or signs. When put into Fabric and USD the values are stored as 64-bit
        unsigned integer values.
        """
        return first_value if first_value > second_value else second_value

    # end-autonode-objectid

    return (
        "omni.graph.autonode_objectid",
        [
            ({"first_value": 1000, "second_value": 2000}, {"out_0": 2000}),
            ({"first_value": 2500, "second_value": 1500}, {"out_0": 2500}),
        ],
    )


# ==============================================================================================================
def construct_autonode_objectidarray() -> _TestConfiguration:
    # begin-autonode-objectidarray
    import numpy as np
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_objectidarray(first_value: ot.objectidarray, second_value: ot.objectidarray) -> ot.objectidarray:
        """Takes in two arrays of object IDs and returns an array containing the largest of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.uint64) where
        "N" is the size of the array determined at runtime.
        """
        return np.maximum(first_value, second_value)

    # end-autonode-objectidarray

    return (
        "omni.graph.autonode_objectidarray",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([3, 1])}, {"out_0": np.array([3, 2])}),
            ({"first_value": np.array([2, 3]), "second_value": np.array([4, 1])}, {"out_0": np.array([4, 3])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_point3d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-point3d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_point3d(first_value: ot.point3d, second_value: ot.point3d) -> ot.point3d:
        """Takes in two pointd[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float64). When put into
        Fabric the values are stored as 3 double-precision values. The point role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-point3d

    return (
        "omni.graph.autonode_point3d",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_point3darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-point3darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_point3darray(first_value: ot.point3darray, second_value: ot.point3darray) -> ot.point3darray:
        """Takes in two arrays of point3d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The point role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-point3darray

    return (
        "omni.graph.autonode_point3darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_point3f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-point3f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_point3f(first_value: ot.point3f, second_value: ot.point3f) -> ot.point3f:
        """Takes in two pointf[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float32). When put into
        Fabric the values are stored as 3 single-precision values. The point role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-point3f

    return (
        "omni.graph.autonode_point3f",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_point3farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-point3farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_point3farray(first_value: ot.point3farray, second_value: ot.point3farray) -> ot.point3farray:
        """Takes in two arrays of point3f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The point role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-point3farray

    return (
        "omni.graph.autonode_point3farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_point3h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-point3h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_point3h(first_value: ot.point3h, second_value: ot.point3h) -> ot.point3h:
        """Takes in two pointh[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float16). When put into
        Fabric the values are stored as 3 half-precision values. The point role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-point3h

    return (
        "omni.graph.autonode_point3h",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_point3harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-point3harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_point3harray(first_value: ot.point3harray, second_value: ot.point3harray) -> ot.point3harray:
        """Takes in two arrays of point3h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The point role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-point3harray

    return (
        "omni.graph.autonode_point3harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_quatd() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-quatd
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_quatd(first_value: ot.quatd, second_value: ot.quatd) -> ot.quatd:
        """Takes in two quatd[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float64). When put into
        Fabric the values are stored as 4 double-precision values. The quaternion role is applied to USD and OmniGraph
        types as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-quatd

    return (
        "omni.graph.autonode_quatd",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_quatdarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-quatdarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_quatdarray(first_value: ot.quatdarray, second_value: ot.quatdarray) -> ot.quatdarray:
        """Takes in two arrays of quatd attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The quaternion role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-quatdarray

    return (
        "omni.graph.autonode_quatdarray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_quatf() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-quatf
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_quatf(first_value: ot.quatf, second_value: ot.quatf) -> ot.quatf:
        """Takes in two quatf[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float32). When put into
        Fabric the values are stored as 4 single-precision values. The quaternion role is applied to USD and OmniGraph
        types as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-quatf

    return (
        "omni.graph.autonode_quatf",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_quatfarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-quatfarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_quatfarray(first_value: ot.quatfarray, second_value: ot.quatfarray) -> ot.quatfarray:
        """Takes in two arrays of quatf attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The quaternion role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-quatfarray

    return (
        "omni.graph.autonode_quatfarray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_quath() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-quath
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_quath(first_value: ot.quath, second_value: ot.quath) -> ot.quath:
        """Takes in two quath[4] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(4,), dtype=numpy.float16). When put into
        Fabric the values are stored as 4 half-precision values. The quaternion role is applied to USD and OmniGraph
        types as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-quath

    return (
        "omni.graph.autonode_quath",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0, 4.0]), "second_value": np.array([2.0, 4.0, 6.0, 8.0])},
                {"out_0": np.array([3.0, 6.0, 9.0, 12.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0, -4.0]), "second_value": np.array([3.0, 6.0, 9.0, 12.0])},
                {"out_0": np.array([2.0, 4.0, 6.0, 8.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_quatharray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-quatharray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_quatharray(first_value: ot.quatharray, second_value: ot.quatharray) -> ot.quatharray:
        """Takes in two arrays of quath attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(4,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The quaternion role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-quatharray

    return (
        "omni.graph.autonode_quatharray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0, 4.0], [1.25, 2.25, 3.25, 4.25]]),
                    "second_value": np.array([[10.0, 20.0, 30.0, 40.0], [10.25, 20.25, 30.25, 40.25]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0, 44.0], [11.5, 22.5, 33.5, 44.5]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0, -4.0]]), "second_value": np.array([[3.0, 4.0, 5.0, 6.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_string() -> _TestConfiguration:
    # begin-autonode-string
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_string(first_value: ot.string, second_value: ot.string) -> ot.string:
        """Takes in two string values and outputs the concatenated string.
        The types of both inputs and the return value are Python str. When put into Fabric the values are
        stored as uchar arrays with a length value. USD stores it as a native string type.
        """
        return first_value + second_value

    # end-autonode-string

    return (
        "omni.graph.autonode_string",
        [
            ({"first_value": "hello", "second_value": " world"}, {"out_0": "hello world"}),
        ],
    )


# ==============================================================================================================
def construct_autonode_target() -> _TestConfiguration:
    # begin-autonode-target
    import omni.graph.core as og
    import omni.graph.core.types as ot
    from usdrt import Sdf

    @og.create_node_type
    def autonode_target(target_values: ot.target) -> ot.target:
        """Takes in target values and outputs the targets resulting from appending "TestChild" to the target.
        The types of both inputs and the return value are list[usdrt.Sdf.Path]. Unlike most other array types this
        is represented as a list rather than a numpy array since the value type is not one supported by numpy.
        When put into Fabric the value is stored as an SdfPath token, while USD uses the native rel type.
        """
        return [target.AppendPath("Child") for target in target_values]

    # end-autonode-target

    return (
        "omni.graph.autonode_target",
        [
            (
                {"target_values": [Sdf.Path("/TestGraph/Prim1"), Sdf.Path("/TestGraph/Prim2")]},
                {"out_0": [Sdf.Path("/TestGraph/Prim1/Child"), Sdf.Path("/TestGraph/Prim2/Child")]},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord2d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord2d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord2d(first_value: ot.texcoord2d, second_value: ot.texcoord2d) -> ot.texcoord2d:
        """Takes in two texcoordd[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.float64). When put into
        Fabric the values are stored as 2 double-precision values. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord2d

    return (
        "omni.graph.autonode_texcoord2d",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([2.0, 4.0])},
                {"out_0": np.array([3.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 6.0])},
                {"out_0": np.array([2.0, 4.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord2darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord2darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord2darray(
        first_value: ot.texcoord2darray, second_value: ot.texcoord2darray
    ) -> ot.texcoord2darray:
        """Takes in two arrays of texcoord2d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord2darray

    return (
        "omni.graph.autonode_texcoord2darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0], [1.25, 2.25], [1.5, 2.5]]),
                    "second_value": np.array([[10.0, 20.0], [10.25, 20.25], [10.5, 20.5]]),
                },
                {"out_0": np.array([[11.0, 22.0], [11.5, 22.5], [12.0, 23.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0]]), "second_value": np.array([[3.0, 4.0]])},
                {"out_0": np.array([[2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord2f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord2f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord2f(first_value: ot.texcoord2f, second_value: ot.texcoord2f) -> ot.texcoord2f:
        """Takes in two texcoordf[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.float32). When put into
        Fabric the values are stored as 2 single-precision values. The texcoord role is applied to USD and OmniGraph
        types as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord2f

    return (
        "omni.graph.autonode_texcoord2f",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([2.0, 4.0])},
                {"out_0": np.array([3.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 6.0])},
                {"out_0": np.array([2.0, 4.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord2farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord2farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord2farray(
        first_value: ot.texcoord2farray, second_value: ot.texcoord2farray
    ) -> ot.texcoord2farray:
        """Takes in two arrays of texcoord2f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord2farray

    return (
        "omni.graph.autonode_texcoord2farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0], [1.25, 2.25], [1.5, 2.5]]),
                    "second_value": np.array([[10.0, 20.0], [10.25, 20.25], [10.5, 20.5]]),
                },
                {"out_0": np.array([[11.0, 22.0], [11.5, 22.5], [12.0, 23.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0]]), "second_value": np.array([[3.0, 4.0]])},
                {"out_0": np.array([[2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord2h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord2h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord2h(first_value: ot.texcoord2h, second_value: ot.texcoord2h) -> ot.texcoord2h:
        """Takes in two texcoordh[2] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(2,), dtype=numpy.float16). When put into
        Fabric the values are stored as 2 half-precision values. The texcoord role is applied to USD and OmniGraph
        types as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord2h

    return (
        "omni.graph.autonode_texcoord2h",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([2.0, 4.0])},
                {"out_0": np.array([3.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 6.0])},
                {"out_0": np.array([2.0, 4.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord2harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord2harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord2harray(
        first_value: ot.texcoord2harray, second_value: ot.texcoord2harray
    ) -> ot.texcoord2harray:
        """Takes in two arrays of texcoord2h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord2harray

    return (
        "omni.graph.autonode_texcoord2harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0], [1.25, 2.25], [1.5, 2.5]]),
                    "second_value": np.array([[10.0, 20.0], [10.25, 20.25], [10.5, 20.5]]),
                },
                {"out_0": np.array([[11.0, 22.0], [11.5, 22.5], [12.0, 23.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0]]), "second_value": np.array([[3.0, 4.0]])},
                {"out_0": np.array([[2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord3d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord3d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord3d(first_value: ot.texcoord3d, second_value: ot.texcoord3d) -> ot.texcoord3d:
        """Takes in two texcoordd[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float64). When put into
        Fabric the values are stored as 3 double-precision values. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord3d

    return (
        "omni.graph.autonode_texcoord3d",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord3darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord3darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord3darray(
        first_value: ot.texcoord3darray, second_value: ot.texcoord3darray
    ) -> ot.texcoord3darray:
        """Takes in two arrays of texcoord3d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord3darray

    return (
        "omni.graph.autonode_texcoord3darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord3f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord3f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord3f(first_value: ot.texcoord3f, second_value: ot.texcoord3f) -> ot.texcoord3f:
        """Takes in two texcoordf[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float32). When put into
        Fabric the values are stored as 3 single-precision values. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord3f

    return (
        "omni.graph.autonode_texcoord3f",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord3farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord3farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord3farray(
        first_value: ot.texcoord3farray, second_value: ot.texcoord3farray
    ) -> ot.texcoord3farray:
        """Takes in two arrays of texcoord3f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord3farray

    return (
        "omni.graph.autonode_texcoord3farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord3h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord3h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord3h(first_value: ot.texcoord3h, second_value: ot.texcoord3h) -> ot.texcoord3h:
        """Takes in two texcoordh[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float16). When put into
        Fabric the values are stored as 3 half-precision values. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord3h

    return (
        "omni.graph.autonode_texcoord3h",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_texcoord3harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-texcoord3harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_texcoord3harray(
        first_value: ot.texcoord3harray, second_value: ot.texcoord3harray
    ) -> ot.texcoord3harray:
        """Takes in two arrays of texcoord3h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The texcoord role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-texcoord3harray

    return (
        "omni.graph.autonode_texcoord3harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_timecode() -> _TestConfiguration:
    # begin-autonode-timecode
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_timecode(first_value: ot.timecode, second_value: ot.timecode) -> ot.timecode:
        """Takes in two timecodes outputs the sum of them.
        The types of both inputs and the return value are Python floats with the full precision required in order
        to represent the range of legal timecodes. When put into Fabric and USD the values are stored as a
        double-precision floating point value.
        """
        return first_value + second_value

    # end-autonode-timecode

    return (
        "omni.graph.autonode_timecode",
        [
            ({"first_value": 1.0, "second_value": 2.0}, {"out_0": 3.0}),
            ({"first_value": -1.0, "second_value": 3.0}, {"out_0": 2.0}),
        ],
    )


# ==============================================================================================================
def construct_autonode_timecodearray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-timecodearray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_timecodearray(first_value: ot.timecodearray, second_value: ot.timecodearray) -> ot.timecodearray:
        """Takes in two arrays of timecodes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-timecodearray

    return (
        "omni.graph.autonode_timecodearray",
        [
            (
                {"first_value": np.array([1.0, 2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([4.0, 6.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0]), "second_value": np.array([3.0, 4.0])},
                {"out_0": np.array([2.0, 2.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_token() -> _TestConfiguration:
    # begin-autonode-token
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_token(first_value: ot.token, second_value: ot.token) -> ot.token:
        """Takes in two tokenized strings and outputs the string resulting from concatenating them together.
        The types of both inputs and the return value are Python strs as Python does not have the concept of a
        unique tokenized string. When put into Fabric and USD the values are stored as a single
        64-bit unsigned integer that is a token .
        """
        return first_value + second_value

    # end-autonode-token

    return (
        "omni.graph.autonode_token",
        ({"first_value": "hello", "second_value": " world"}, {"out_0": "hello world"}),
    )


# ==============================================================================================================
def construct_autonode_tokenarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-tokenarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_tokenarray(first_value: ot.tokenarray, second_value: ot.tokenarray) -> ot.tokenarray:
        """Takes in two arrays of tokens and returns an array containing the concatenations of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype="<US") where "N" is
        the size of the array determined at runtime.
        """
        return np.array([x + y for x, y in zip(first_value, second_value)])

    # end-autonode-tokenarray

    return (
        "omni.graph.autonode_tokenarray",
        [
            (
                {"first_value": np.array(["hello", "whatcha"]), "second_value": np.array([" lamppost", " knowin"])},
                {"out_0": np.array(["hello lamppost", "whatcha knowin"])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_uchar() -> _TestConfiguration:
    # begin-autonode-uchar
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_uchar(first_value: ot.uchar, second_value: ot.uchar) -> ot.uint8:
        """Takes in two 8-bit precision unsigned integer values and outputs the sum of them.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels or signs. When put into Fabric and USD the values are stored as 8-bit
        precision unsigned integer values.
        Note that the return type is the Warp-compatible "uint8" which is a synonym for "uchar".
        """
        return first_value + second_value

    # end-autonode-uchar

    return (
        "omni.graph.autonode_uchar",
        [
            ({"first_value": 1, "second_value": 2}, {"out_0": 3}),
            ({"first_value": 10, "second_value": 20}, {"out_0": 30}),
        ],
    )


# ==============================================================================================================
def construct_autonode_uchararray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-uchararray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_uchararray(first_value: ot.uchararray, second_value: ot.uchararray) -> ot.uchararray:
        """Takes in two arrays of 8-bit unsigned integer attributes and returns an array containing the sum of each
        element. The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.uchar8) where
        "N" is the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-uchararray

    return (
        "omni.graph.autonode_uchararray",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([3, 4])}, {"out_0": np.array([4, 6])}),
            ({"first_value": np.array([0, 100]), "second_value": np.array([3, 4])}, {"out_0": np.array([3, 104])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_uint() -> _TestConfiguration:
    # begin-autonode-uint
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_uint(first_value: ot.uint, second_value: ot.uint) -> ot.uint:
        """Takes in two 32-bit precision unsigned integer values and outputs the sum of them.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels or signs. When put into Fabric and USD the values are stored as 32-bit
        precision unsigned integer values.
        """
        return first_value + second_value

    # end-autonode-uint

    return (
        "omni.graph.autonode_uint",
        [
            ({"first_value": 1, "second_value": 2}, {"out_0": 3}),
            ({"first_value": 10, "second_value": 20}, {"out_0": 30}),
        ],
    )


# ==============================================================================================================
def construct_autonode_uintarray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-uintarray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_uintarray(first_value: ot.uintarray, second_value: ot.uintarray) -> ot.uintarray:
        """Takes in two arrays of 32-bit unsigned integer attributes and returns an array containing the sum of each
        element. The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.uint32) where
        "N" is the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-uintarray

    return (
        "omni.graph.autonode_uintarray",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([3, 4])}, {"out_0": np.array([4, 6])}),
            ({"first_value": np.array([0, 100]), "second_value": np.array([3, 4])}, {"out_0": np.array([3, 104])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_uint64() -> _TestConfiguration:
    # begin-autonode-uint64
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_uint64(first_value: ot.uint64, second_value: ot.uint64) -> ot.uint64:
        """Takes in two 64-bit precision unsigned integer values and outputs the sum of them.
        The types of both inputs and the return value are Python ints as Python does not distinguish between
        different precision levels or signs. When put into Fabric and USD the values are stored as 64-bit
        precision unsigned integer values.
        """
        return first_value + second_value

    # end-autonode-uint64

    return (
        "omni.graph.autonode_uint64",
        [
            ({"first_value": 1, "second_value": 2}, {"out_0": 3}),
            ({"first_value": 10, "second_value": 20}, {"out_0": 30}),
        ],
    )


# ==============================================================================================================
def construct_autonode_uint64array() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-uint64array
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_uint64array(first_value: ot.uint64array, second_value: ot.uint64array) -> ot.uint64array:
        """Takes in two arrays of 8-bit unsigned integer attributes and returns an array containing the sum of each
        element. The types of both inputs and the return value are numpy.ndarray(shape=(N,), dtype=numpy.uint64) where
        "N" is the size of the array determined at runtime.
        """
        return first_value + second_value

    # end-autonode-uint64array

    return (
        "omni.graph.autonode_uint64array",
        [
            ({"first_value": np.array([1, 2]), "second_value": np.array([3, 4])}, {"out_0": np.array([4, 6])}),
            ({"first_value": np.array([0, 100]), "second_value": np.array([3, 4])}, {"out_0": np.array([3, 104])}),
        ],
    )


# ==============================================================================================================
def construct_autonode_vector3d() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-vector3d
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_vector3d(first_value: ot.vector3d, second_value: ot.vector3d) -> ot.vector3d:
        """Takes in two vectord[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float64). When put into
        Fabric the values are stored as 3 double-precision values. The vector role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-vector3d

    return (
        "omni.graph.autonode_vector3d",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_vector3darray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-vector3darray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_vector3darray(first_value: ot.vector3darray, second_value: ot.vector3darray) -> ot.vector3darray:
        """Takes in two arrays of vector3d attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float64) where "N" is
        the size of the array determined at runtime. The vector role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-vector3darray

    return (
        "omni.graph.autonode_vector3darray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_vector3f() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-vector3f
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_vector3f(first_value: ot.vector3f, second_value: ot.vector3f) -> ot.vector3f:
        """Takes in two vectorf[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float32). When put into
        Fabric the values are stored as 3 single-precision values. The vector role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-vector3f

    return (
        "omni.graph.autonode_vector3f",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_vector3farray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-vector3farray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_vector3farray(first_value: ot.vector3farray, second_value: ot.vector3farray) -> ot.vector3farray:
        """Takes in two arrays of vector3f attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float32) where "N" is
        the size of the array determined at runtime. The vector role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-vector3farray

    return (
        "omni.graph.autonode_vector3farray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_vector3h() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-vector3h
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_vector3h(first_value: ot.vector3h, second_value: ot.vector3h) -> ot.vector3h:
        """Takes in two vectorh[3] values and outputs the sum of them.
        The types of both inputs and the return value are numpy.array(shape=(3,), dtype=numpy.float16). When put into
        Fabric the values are stored as 3 half-precision values. The vector role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-vector3h

    return (
        "omni.graph.autonode_vector3h",
        [
            (
                {"first_value": np.array([1.0, 2.0, 3.0]), "second_value": np.array([2.0, 4.0, 6.0])},
                {"out_0": np.array([3.0, 6.0, 9.0])},
            ),
            (
                {"first_value": np.array([-1.0, -2.0, -3.0]), "second_value": np.array([3.0, 6.0, 9.0])},
                {"out_0": np.array([2.0, 4.0, 6.0])},
            ),
        ],
    )


# ==============================================================================================================
def construct_autonode_vector3harray() -> _TestConfiguration:
    import numpy as np

    # begin-autonode-vector3harray
    import omni.graph.core as og
    import omni.graph.core.types as ot

    @og.create_node_type
    def autonode_vector3harray(first_value: ot.vector3harray, second_value: ot.vector3harray) -> ot.vector3harray:
        """Takes in two arrays of vector3h attributes and returns an array containing the sum of each element.
        The types of both inputs and the return value are numpy.ndarray(shape=(3,N,), dtype=numpy.float16) where "N" is
        the size of the array determined at runtime. The vector role is applied to USD and OmniGraph types
        as an aid to interpreting the values.
        """
        return first_value + second_value

    # end-autonode-vector3harray

    return (
        "omni.graph.autonode_vector3harray",
        [
            (
                {
                    "first_value": np.array([[1.0, 2.0, 3.0], [1.25, 2.25, 3.25], [1.5, 2.5, 3.5]]),
                    "second_value": np.array([[10.0, 20.0, 30.0], [10.25, 20.25, 30.25], [10.5, 20.5, 30.5]]),
                },
                {"out_0": np.array([[11.0, 22.0, 33.0], [11.5, 22.5, 33.5], [12.0, 23.0, 34.0]])},
            ),
            (
                {"first_value": np.array([[-1.0, -2.0, -3.0]]), "second_value": np.array([[3.0, 4.0, 5.0]])},
                {"out_0": np.array([[2.0, 2.0, 2.0]])},
            ),
        ],
    )
