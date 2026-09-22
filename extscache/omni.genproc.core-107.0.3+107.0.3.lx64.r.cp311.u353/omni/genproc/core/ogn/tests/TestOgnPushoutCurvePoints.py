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
        test_file_name = "OgnPushoutCurvePointsTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_genproc_core_PushoutCurvePoints")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:collisionBundle"))
        attribute = test_node.get_attribute("inputs:collisionBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:collisionProxy"))
        attribute = test_node.get_attribute("inputs:collisionProxy")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:curvesBundle"))
        attribute = test_node.get_attribute("inputs:curvesBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:numberOfSegments"))
        attribute = test_node.get_attribute("inputs:numberOfSegments")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pushoutHorizontally"))
        attribute = test_node.get_attribute("inputs:pushoutHorizontally")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:samplesPerSegment"))
        attribute = test_node.get_attribute("inputs:samplesPerSegment")
        self.assertTrue(attribute.is_valid())
        expected_value = 20
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:upAxis"))
        attribute = test_node.get_attribute("inputs:upAxis")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 1, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:upAxisSource"))
        attribute = test_node.get_attribute("inputs:upAxisSource")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs_curvesBundle"))
        attribute = test_node.get_attribute("outputs_curvesBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs_pointsBundle"))
        attribute = test_node.get_attribute("outputs_pointsBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevCollisionProxy"))
        attribute = test_node.get_attribute("state:prevCollisionProxy")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevNumberOfSegments"))
        attribute = test_node.get_attribute("state:prevNumberOfSegments")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevPushoutHorizontally"))
        attribute = test_node.get_attribute("state:prevPushoutHorizontally")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevSamplesPerSegment"))
        attribute = test_node.get_attribute("state:prevSamplesPerSegment")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevUpAxis"))
        attribute = test_node.get_attribute("state:prevUpAxis")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevUpAxisSource"))
        attribute = test_node.get_attribute("state:prevUpAxisSource")
        self.assertTrue(attribute.is_valid())
