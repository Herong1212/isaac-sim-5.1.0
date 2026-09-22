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
        from omni.replicator.core.ogn.OgnOnFrameDatabase import OgnOnFrameDatabase
        test_file_name = "OgnOnFrameTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnOnFrame")
        database = OgnOnFrameDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 2)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:interval"))
        attribute = test_node.get_attribute("inputs:interval")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.interval
        database.inputs.interval = db_value
        expected_value = 1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:maxExecs"))
        attribute = test_node.get_attribute("inputs:maxExecs")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.maxExecs
        database.inputs.maxExecs = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:renderProduct"))
        attribute = test_node.get_attribute("inputs:renderProduct")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.renderProduct
        database.inputs.renderProduct = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:rtSubframes"))
        attribute = test_node.get_attribute("inputs:rtSubframes")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.rtSubframes
        database.inputs.rtSubframes = db_value
        expected_value = 1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:run"))
        attribute = test_node.get_attribute("inputs:run")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.run
        database.inputs.run = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("outputs:execCounts"))
        attribute = test_node.get_attribute("outputs:execCounts")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.execCounts
        database.outputs.execCounts = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:execOut"))
        attribute = test_node.get_attribute("outputs:execOut")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.execOut
        database.outputs.execOut = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:frameNumber"))
        attribute = test_node.get_attribute("outputs:frameNumber")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.frameNumber
        database.outputs.frameNumber = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:referenceTimeDenominator"))
        attribute = test_node.get_attribute("outputs:referenceTimeDenominator")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.referenceTimeDenominator
        database.outputs.referenceTimeDenominator = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:referenceTimeNumerator"))
        attribute = test_node.get_attribute("outputs:referenceTimeNumerator")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.referenceTimeNumerator
        database.outputs.referenceTimeNumerator = db_value
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
