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
        test_file_name = "CamTextureReadTaskNodeTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_sensors_nv_camera_CamTextureReadTaskNode")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:aov"))
        attribute = test_node.get_attribute("inputs:aov")
        self.assertTrue(attribute.is_valid())
        expected_value = "LDR"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:degreesX"))
        attribute = test_node.get_attribute("inputs:degreesX")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:degreesY"))
        attribute = test_node.get_attribute("inputs:degreesY")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:degreesZ"))
        attribute = test_node.get_attribute("inputs:degreesZ")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:disparityBaselineMM"))
        attribute = test_node.get_attribute("inputs:disparityBaselineMM")
        self.assertTrue(attribute.is_valid())
        expected_value = 55.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:disparityFarthestDistanceError"))
        attribute = test_node.get_attribute("inputs:disparityFarthestDistanceError")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.14
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:disparityFarthestRangeMM"))
        attribute = test_node.get_attribute("inputs:disparityFarthestRangeMM")
        self.assertTrue(attribute.is_valid())
        expected_value = 4000.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:disparityHorizontalFovDeg"))
        attribute = test_node.get_attribute("inputs:disparityHorizontalFovDeg")
        self.assertTrue(attribute.is_valid())
        expected_value = 65.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:disparityNearestDistanceError"))
        attribute = test_node.get_attribute("inputs:disparityNearestDistanceError")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.02
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:disparityNearestRangeMM"))
        attribute = test_node.get_attribute("inputs:disparityNearestRangeMM")
        self.assertTrue(attribute.is_valid())
        expected_value = 300.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:enableSyntheticDisparitySim"))
        attribute = test_node.get_attribute("inputs:enableSyntheticDisparitySim")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:gpu"))
        attribute = test_node.get_attribute("inputs:gpu")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:hydraTime"))
        attribute = test_node.get_attribute("inputs:hydraTime")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rp"))
        attribute = test_node.get_attribute("inputs:rp")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:simTime"))
        attribute = test_node.get_attribute("inputs:simTime")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:dest"))
        attribute = test_node.get_attribute("outputs:dest")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:gpu"))
        attribute = test_node.get_attribute("outputs:gpu")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:hydraTimeOut"))
        attribute = test_node.get_attribute("outputs:hydraTimeOut")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:rp"))
        attribute = test_node.get_attribute("outputs:rp")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:simTimeOut"))
        attribute = test_node.get_attribute("outputs:simTimeOut")
        self.assertTrue(attribute.is_valid())
