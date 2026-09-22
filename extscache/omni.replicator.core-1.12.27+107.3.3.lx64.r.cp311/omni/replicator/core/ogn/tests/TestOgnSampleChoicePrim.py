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
        from omni.replicator.core.ogn.OgnSampleChoicePrimDatabase import OgnSampleChoicePrimDatabase
        test_file_name = "OgnSampleChoicePrimTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnSampleChoicePrim")
        database = OgnSampleChoicePrimDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:choices"))
        attribute = test_node.get_attribute("inputs:choices")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.choices

        self.assertTrue(test_node.get_attribute_exists("inputs:numSamples"))
        attribute = test_node.get_attribute("inputs:numSamples")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.numSamples
        database.inputs.numSamples = db_value
        expected_value = 1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:seed"))
        attribute = test_node.get_attribute("inputs:seed")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.seed
        database.inputs.seed = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:weights"))
        attribute = test_node.get_attribute("inputs:weights")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.weights
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:withReplacements"))
        attribute = test_node.get_attribute("inputs:withReplacements")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.withReplacements
        database.inputs.withReplacements = db_value
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("outputs:numSamples"))
        attribute = test_node.get_attribute("outputs:numSamples")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.numSamples
        database.outputs.numSamples = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:prims"))
        attribute = test_node.get_attribute("outputs:prims")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.prims

        self.assertTrue(test_node.get_attribute_exists("outputs:samples"))
        attribute = test_node.get_attribute("outputs:samples")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.samples
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
