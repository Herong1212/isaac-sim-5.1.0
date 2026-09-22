import os
import omni.kit.test
import omni.graph.core as og
import omni.graph.core.tests as ogts
from omni.graph.core.tests.omnigraph_test_utils import _TestGraphAndNode
from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_setup_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_verify_scene


class TestOgn(ogts.OmniGraphTestCase):

    async def test_data_access(self):
        test_file_name = "OgnExampleAdjacencyTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_examples_cpp_Adjacency")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:computeDistances"))
        attribute = test_node.get_attribute("inputs:computeDistances")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:computeNeighborCounts"))
        attribute = test_node.get_attribute("inputs:computeNeighborCounts")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:computeNeighborStarts"))
        attribute = test_node.get_attribute("inputs:computeNeighborStarts")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:computeNeighbors"))
        attribute = test_node.get_attribute("inputs:computeNeighbors")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:mesh"))
        attribute = test_node.get_attribute("inputs:mesh")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfDistancesOutputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfDistancesOutputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "distances"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfNeighborCountsOutputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfNeighborCountsOutputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "neighborCounts"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfNeighborStartsOutputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfNeighborStartsOutputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "neighborStarts"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfNeighborsOutputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfNeighborsOutputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "neighbors"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfPositionsInputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfPositionsInputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "points"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfVertexCountsInputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfVertexCountsInputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "faceVertexCounts"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:nameOfVertexIndicesInputAttribute"))
        attribute = test_node.get_attribute("inputs:nameOfVertexIndicesInputAttribute")
        self.assertTrue(attribute.is_valid())
        expected_value = "faceVertexIndices"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointCount"))
        attribute = test_node.get_attribute("inputs:pointCount")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:removeDuplicates"))
        attribute = test_node.get_attribute("inputs:removeDuplicates")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:treatEdgesAsOneWay"))
        attribute = test_node.get_attribute("inputs:treatEdgesAsOneWay")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:treatFacesAsCurves"))
        attribute = test_node.get_attribute("inputs:treatFacesAsCurves")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs_mesh"))
        attribute = test_node.get_attribute("outputs_mesh")
        self.assertTrue(attribute.is_valid())
