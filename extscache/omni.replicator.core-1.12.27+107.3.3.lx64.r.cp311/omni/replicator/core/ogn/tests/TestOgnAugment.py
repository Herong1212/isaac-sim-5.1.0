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
        from omni.replicator.core.ogn.OgnAugmentDatabase import OgnAugmentDatabase
        test_file_name = "OgnAugmentTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnAugment")
        database = OgnAugmentDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:augmentationFunctionName"))
        attribute = test_node.get_attribute("inputs:augmentationFunctionName")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.augmentationFunctionName
        database.inputs.augmentationFunctionName = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:augmentationScript"))
        attribute = test_node.get_attribute("inputs:augmentationScript")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.augmentationScript
        database.inputs.augmentationScript = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:bufferSize"))
        attribute = test_node.get_attribute("inputs:bufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.bufferSize
        database.inputs.bufferSize = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:cudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cudaDeviceIndex
        database.inputs.cudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:data"))
        attribute = test_node.get_attribute("inputs:data")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:dataOutShape"))
        attribute = test_node.get_attribute("inputs:dataOutShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.dataOutShape
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:dataPtr"))
        attribute = test_node.get_attribute("inputs:dataPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.dataPtr
        database.inputs.dataPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:dataShape"))
        attribute = test_node.get_attribute("inputs:dataShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.dataShape
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:dataType"))
        attribute = test_node.get_attribute("inputs:dataType")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.dataType
        database.inputs.dataType = db_value
        expected_value = "uint8"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:exec"))
        attribute = test_node.get_attribute("inputs:exec")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.exec
        database.inputs.exec = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:format"))
        attribute = test_node.get_attribute("inputs:format")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.format
        database.inputs.format = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:height"))
        attribute = test_node.get_attribute("inputs:height")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.height
        database.inputs.height = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:strides"))
        attribute = test_node.get_attribute("inputs:strides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.strides
        database.inputs.strides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:width"))
        attribute = test_node.get_attribute("inputs:width")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.width
        database.inputs.width = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("outputs:bufferSize"))
        attribute = test_node.get_attribute("outputs:bufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.bufferSize
        database.outputs.bufferSize = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:cudaDeviceIndex"))
        attribute = test_node.get_attribute("outputs:cudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.cudaDeviceIndex
        database.outputs.cudaDeviceIndex = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:dataPtr"))
        attribute = test_node.get_attribute("outputs:dataPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.dataPtr
        database.outputs.dataPtr = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:dataShape"))
        attribute = test_node.get_attribute("outputs:dataShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.dataShape

        self.assertTrue(test_node.get_attribute_exists("outputs:dataType"))
        attribute = test_node.get_attribute("outputs:dataType")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.dataType
        database.outputs.dataType = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:exec"))
        attribute = test_node.get_attribute("outputs:exec")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.exec
        database.outputs.exec = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:format"))
        attribute = test_node.get_attribute("outputs:format")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.format
        database.outputs.format = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:height"))
        attribute = test_node.get_attribute("outputs:height")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.height
        database.outputs.height = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:strides"))
        attribute = test_node.get_attribute("outputs:strides")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.strides
        database.outputs.strides = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:width"))
        attribute = test_node.get_attribute("outputs:width")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.width
        database.outputs.width = db_value

        self.assertTrue(test_node.get_attribute_exists("state:omni_initialized"))
        attribute = test_node.get_attribute("state:omni_initialized")
        self.assertTrue(attribute.is_valid())
        db_value = database.state.omni_initialized
        database.state.omni_initialized = db_value
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
