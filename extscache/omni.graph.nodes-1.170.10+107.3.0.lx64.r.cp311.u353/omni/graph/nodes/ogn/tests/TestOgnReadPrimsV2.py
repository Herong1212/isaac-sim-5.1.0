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
        test_file_name = "OgnReadPrimsV2Template.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_ReadPrimsV2")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:_debugStamp"))
        attribute = test_node.get_attribute("inputs:_debugStamp")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:applySkelBinding"))
        attribute = test_node.get_attribute("inputs:applySkelBinding")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:attrNamesToImport"))
        attribute = test_node.get_attribute("inputs:attrNamesToImport")
        self.assertTrue(attribute.is_valid())
        expected_value = "*"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:computeBoundingBox"))
        attribute = test_node.get_attribute("inputs:computeBoundingBox")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:enableBundleChangeTracking"))
        attribute = test_node.get_attribute("inputs:enableBundleChangeTracking")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:enableChangeTracking"))
        attribute = test_node.get_attribute("inputs:enableChangeTracking")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pathPattern"))
        attribute = test_node.get_attribute("inputs:pathPattern")
        self.assertTrue(attribute.is_valid())
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:prims"))
        attribute = test_node.get_attribute("inputs:prims")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:typePattern"))
        attribute = test_node.get_attribute("inputs:typePattern")
        self.assertTrue(attribute.is_valid())
        expected_value = "*"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:usdTimecode"))
        attribute = test_node.get_attribute("inputs:usdTimecode")
        self.assertTrue(attribute.is_valid())
        expected_value = float("NaN")
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs_primsBundle"))
        attribute = test_node.get_attribute("outputs_primsBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:applySkelBinding"))
        attribute = test_node.get_attribute("state:applySkelBinding")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:attrNamesToImport"))
        attribute = test_node.get_attribute("state:attrNamesToImport")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:computeBoundingBox"))
        attribute = test_node.get_attribute("state:computeBoundingBox")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:enableBundleChangeTracking"))
        attribute = test_node.get_attribute("state:enableBundleChangeTracking")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:enableChangeTracking"))
        attribute = test_node.get_attribute("state:enableChangeTracking")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:pathPattern"))
        attribute = test_node.get_attribute("state:pathPattern")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:typePattern"))
        attribute = test_node.get_attribute("state:typePattern")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:usdTimecode"))
        attribute = test_node.get_attribute("state:usdTimecode")
        self.assertTrue(attribute.is_valid())
