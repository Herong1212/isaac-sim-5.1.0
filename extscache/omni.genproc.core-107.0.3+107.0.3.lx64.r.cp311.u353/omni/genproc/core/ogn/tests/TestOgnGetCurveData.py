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
        test_file_name = "OgnGetCurveDataTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_genproc_core_GetCurveData")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:curvesBundle"))
        attribute = test_node.get_attribute("inputs:curvesBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:rampInterpolationsName"))
        attribute = test_node.get_attribute("inputs:rampInterpolationsName")
        self.assertTrue(attribute.is_valid())
        expected_value = "ramp_interpolations"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rampPositionsName"))
        attribute = test_node.get_attribute("inputs:rampPositionsName")
        self.assertTrue(attribute.is_valid())
        expected_value = "ramp_positions"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rampTagsName"))
        attribute = test_node.get_attribute("inputs:rampTagsName")
        self.assertTrue(attribute.is_valid())
        expected_value = "tags"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rampValuesName"))
        attribute = test_node.get_attribute("inputs:rampValuesName")
        self.assertTrue(attribute.is_valid())
        expected_value = "ramp_values"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:samplesPerSegment"))
        attribute = test_node.get_attribute("inputs:samplesPerSegment")
        self.assertTrue(attribute.is_valid())
        expected_value = 100
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:points"))
        attribute = test_node.get_attribute("outputs:points")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:tags"))
        attribute = test_node.get_attribute("outputs:tags")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:tangents"))
        attribute = test_node.get_attribute("outputs:tangents")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uValues"))
        attribute = test_node.get_attribute("outputs:uValues")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRampInterpolationsName"))
        attribute = test_node.get_attribute("state:prevRampInterpolationsName")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRampPositionsName"))
        attribute = test_node.get_attribute("state:prevRampPositionsName")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRampTagsName"))
        attribute = test_node.get_attribute("state:prevRampTagsName")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRampValuesName"))
        attribute = test_node.get_attribute("state:prevRampValuesName")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevSamplesPerSegment"))
        attribute = test_node.get_attribute("state:prevSamplesPerSegment")
        self.assertTrue(attribute.is_valid())
