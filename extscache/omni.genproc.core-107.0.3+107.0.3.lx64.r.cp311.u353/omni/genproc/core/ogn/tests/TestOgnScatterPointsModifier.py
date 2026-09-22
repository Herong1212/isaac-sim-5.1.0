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
        test_file_name = "OgnScatterPointsModifierTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_genproc_core_ScatterPointsModifier")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:active"))
        attribute = test_node.get_attribute("inputs:active")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:bundle"))
        attribute = test_node.get_attribute("inputs:bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:ids"))
        attribute = test_node.get_attribute("inputs:ids")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normals"))
        attribute = test_node.get_attribute("inputs:normals")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndices"))
        attribute = test_node.get_attribute("inputs:objectIndices")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:positions"))
        attribute = test_node.get_attribute("inputs:positions")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rotations"))
        attribute = test_node.get_attribute("inputs:rotations")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scales"))
        attribute = test_node.get_attribute("inputs:scales")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:tangents"))
        attribute = test_node.get_attribute("inputs:tangents")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs_bundle"))
        attribute = test_node.get_attribute("outputs_bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevActive"))
        attribute = test_node.get_attribute("state:prevActive")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevIds"))
        attribute = test_node.get_attribute("state:prevIds")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevNormals"))
        attribute = test_node.get_attribute("state:prevNormals")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndices"))
        attribute = test_node.get_attribute("state:prevObjectIndices")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevPositions"))
        attribute = test_node.get_attribute("state:prevPositions")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRotations"))
        attribute = test_node.get_attribute("state:prevRotations")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScales"))
        attribute = test_node.get_attribute("state:prevScales")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevTangents"))
        attribute = test_node.get_attribute("state:prevTangents")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:remappedIdsFrom"))
        attribute = test_node.get_attribute("state:remappedIdsFrom")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:remappedIdsTo"))
        attribute = test_node.get_attribute("state:remappedIdsTo")
        self.assertTrue(attribute.is_valid())
