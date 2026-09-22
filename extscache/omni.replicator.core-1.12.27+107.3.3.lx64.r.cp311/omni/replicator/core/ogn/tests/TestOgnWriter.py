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
        from omni.replicator.core.ogn.OgnWriterDatabase import OgnWriterDatabase
        test_file_name = "OgnWriterTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnWriter")
        database = OgnWriterDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 2)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:dataStructure"))
        attribute = test_node.get_attribute("inputs:dataStructure")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.dataStructure
        database.inputs.dataStructure = db_value
        expected_value = "legacy"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:exec"))
        attribute = test_node.get_attribute("inputs:exec")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.exec
        database.inputs.exec = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:referenceTimeDenominator"))
        attribute = test_node.get_attribute("inputs:referenceTimeDenominator")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.referenceTimeDenominator
        database.inputs.referenceTimeDenominator = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:referenceTimeNumerator"))
        attribute = test_node.get_attribute("inputs:referenceTimeNumerator")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.referenceTimeNumerator
        database.inputs.referenceTimeNumerator = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:renderProducts"))
        attribute = test_node.get_attribute("inputs:renderProducts")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.renderProducts
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:writerId"))
        attribute = test_node.get_attribute("inputs:writerId")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.writerId
        database.inputs.writerId = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:writerName"))
        attribute = test_node.get_attribute("inputs:writerName")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.writerName
        database.inputs.writerName = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
