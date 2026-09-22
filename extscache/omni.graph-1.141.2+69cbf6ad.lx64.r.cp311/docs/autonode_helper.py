"""Helper file to isolate the AutoNode walkthrough examples so that they can be used in documentation
and tests can be written to ensure that they are functional as advertised.
"""

# begin-step1
import numpy as np
import omni.graph.core as og
import omni.graph.core.types as ot


def define_dot_product() -> str:
    """Calling this function creates a node type definition for the dot product. As the import is happening
    from a file a special prefix "og.RUNTIME_MODULE_NAME" is added to ensure the node type name is unique.
    This will be important to know when a node of this type is created later.
    Returns the fully qualified name of the new node type for easier use.
    """

    @og.create_node_type
    def autonode_dot(vector1: ot.vector3d, vector2: ot.vector3d) -> ot.double:
        """Computes the dot product of two vectors"""
        return np.dot(vector1, vector2)

    return f"{og.RUNTIME_MODULE_NAME}.autonode_dot"


# end-step1


# begin-step2
def create_graph(node_type_name: str) -> og.Node:
    """Create the sample graph with a node of the AutoNode type for use in the test"""
    (_, (test_node,), _, _) = og.Controller.edit(
        "/AutoNodeTestGraph", {og.Controller.Keys.CREATE_NODES: ("TestNode", node_type_name)}
    )
    return test_node


# end-step2


# begin-step3
def run_test() -> bool:
    """Tests the AutoNode node type we have defined above. Returns True if the test succeeded, False if not"""
    # Call the function that defines the node type
    node_type_name = define_dot_product()

    # Create a graph with a node of the new node type
    test_node = create_graph(node_type_name)

    # Set some input vectors whose dot product we know
    input1 = test_node.get_attribute("inputs:vector1")
    input2 = test_node.get_attribute("inputs:vector2")
    og.Controller(input1).set([1.0, 2.0, 3.0])
    og.Controller(input2).set([4.0, 5.0, 6.0])
    # Evaluate the graph so that the compute runs
    og.Controller.evaluate_sync()

    # Note the naming of the output attribute, with index starting at 0
    result = test_node.get_attribute("outputs:out_0")
    actual_result = og.Controller(result).get()

    # See if the computation produced the expected result
    success = np.allclose(actual_result, 32.0)

    # Deregister the node type so that it does not continue to exist after the test completes
    og.deregister_node_type(node_type_name)

    return success


# end-step3
