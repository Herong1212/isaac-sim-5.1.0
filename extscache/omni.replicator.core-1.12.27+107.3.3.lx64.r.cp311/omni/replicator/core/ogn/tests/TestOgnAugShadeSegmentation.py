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
        from omni.replicator.core.ogn.OgnAugShadeSegmentationDatabase import OgnAugShadeSegmentationDatabase
        test_file_name = "OgnAugShadeSegmentationTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnAugShadeSegmentation")
        database = OgnAugShadeSegmentationDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


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

        self.assertTrue(test_node.get_attribute_exists("inputs:lightSource"))
        attribute = test_node.get_attribute("inputs:lightSource")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.lightSource
        database.inputs.lightSource = db_value
        expected_value = [0.0, 0.0, 1.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalBufferSize"))
        attribute = test_node.get_attribute("inputs:normalBufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalBufferSize
        database.inputs.normalBufferSize = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:normalCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalCudaDeviceIndex
        database.inputs.normalCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalData"))
        attribute = test_node.get_attribute("inputs:normalData")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalDataPtr"))
        attribute = test_node.get_attribute("inputs:normalDataPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalDataPtr
        database.inputs.normalDataPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalStrides"))
        attribute = test_node.get_attribute("inputs:normalStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalStrides
        database.inputs.normalStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:segmentationBufferSize"))
        attribute = test_node.get_attribute("inputs:segmentationBufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.segmentationBufferSize
        database.inputs.segmentationBufferSize = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:segmentationCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:segmentationCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.segmentationCudaDeviceIndex
        database.inputs.segmentationCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:segmentationData"))
        attribute = test_node.get_attribute("inputs:segmentationData")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:segmentationDataPtr"))
        attribute = test_node.get_attribute("inputs:segmentationDataPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.segmentationDataPtr
        database.inputs.segmentationDataPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:segmentationStrides"))
        attribute = test_node.get_attribute("inputs:segmentationStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.segmentationStrides
        database.inputs.segmentationStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:useCandyColours"))
        attribute = test_node.get_attribute("inputs:useCandyColours")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.useCandyColours
        database.inputs.useCandyColours = db_value
        expected_value = False
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
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
