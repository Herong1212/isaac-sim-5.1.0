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
        test_file_name = "OgnSdInstanceMappingTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_syntheticdata_SdInstanceMapping")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 2)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:exec"))
        attribute = test_node.get_attribute("inputs:exec")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:lazy"))
        attribute = test_node.get_attribute("inputs:lazy")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:renderResults"))
        attribute = test_node.get_attribute("inputs:renderResults")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:exec"))
        attribute = test_node.get_attribute("outputs:exec")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMInstanceSemanticMap"))
        attribute = test_node.get_attribute("outputs:sdIMInstanceSemanticMap")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMInstanceTokens"))
        attribute = test_node.get_attribute("outputs:sdIMInstanceTokens")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMLastUpdateTimeDenominator"))
        attribute = test_node.get_attribute("outputs:sdIMLastUpdateTimeDenominator")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMLastUpdateTimeNumerator"))
        attribute = test_node.get_attribute("outputs:sdIMLastUpdateTimeNumerator")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMMaxSemanticHierarchyDepth"))
        attribute = test_node.get_attribute("outputs:sdIMMaxSemanticHierarchyDepth")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMMinInstanceIndex"))
        attribute = test_node.get_attribute("outputs:sdIMMinInstanceIndex")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMMinSemanticIndex"))
        attribute = test_node.get_attribute("outputs:sdIMMinSemanticIndex")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMNumInstances"))
        attribute = test_node.get_attribute("outputs:sdIMNumInstances")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMNumSemanticTokens"))
        attribute = test_node.get_attribute("outputs:sdIMNumSemanticTokens")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMNumSemantics"))
        attribute = test_node.get_attribute("outputs:sdIMNumSemantics")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMSemanticLocalTransform"))
        attribute = test_node.get_attribute("outputs:sdIMSemanticLocalTransform")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMSemanticTokenMap"))
        attribute = test_node.get_attribute("outputs:sdIMSemanticTokenMap")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:sdIMSemanticWorldTransform"))
        attribute = test_node.get_attribute("outputs:sdIMSemanticWorldTransform")
        self.assertTrue(attribute.is_valid())
