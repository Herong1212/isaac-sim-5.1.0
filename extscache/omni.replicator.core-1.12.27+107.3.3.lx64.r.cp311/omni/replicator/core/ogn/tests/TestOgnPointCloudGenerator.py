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
        from omni.replicator.core.ogn.OgnPointCloudGeneratorDatabase import OgnPointCloudGeneratorDatabase
        test_file_name = "OgnPointCloudGeneratorTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnPointCloudGenerator")
        database = OgnPointCloudGeneratorDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:bufferSize"))
        attribute = test_node.get_attribute("inputs:bufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.bufferSize
        database.inputs.bufferSize = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:camera3dPositionsCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:camera3dPositionsCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.camera3dPositionsCudaDeviceIndex
        database.inputs.camera3dPositionsCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:camera3dPositionsPtr"))
        attribute = test_node.get_attribute("inputs:camera3dPositionsPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.camera3dPositionsPtr
        database.inputs.camera3dPositionsPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:camera3dPositionsStrides"))
        attribute = test_node.get_attribute("inputs:camera3dPositionsStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.camera3dPositionsStrides
        database.inputs.camera3dPositionsStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraViewTransform"))
        attribute = test_node.get_attribute("inputs:cameraViewTransform")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraViewTransform
        database.inputs.cameraViewTransform = db_value
        expected_value = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:exec"))
        attribute = test_node.get_attribute("inputs:exec")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.exec
        database.inputs.exec = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:height"))
        attribute = test_node.get_attribute("inputs:height")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.height
        database.inputs.height = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:includeUnlabelled"))
        attribute = test_node.get_attribute("inputs:includeUnlabelled")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.includeUnlabelled
        database.inputs.includeUnlabelled = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationCudaDeviceIndex
        database.inputs.instanceSegmentationCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationPtr"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationPtr
        database.inputs.instanceSegmentationPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationStrides"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationStrides
        database.inputs.instanceSegmentationStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalsCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:normalsCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalsCudaDeviceIndex
        database.inputs.normalsCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalsPtr"))
        attribute = test_node.get_attribute("inputs:normalsPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalsPtr
        database.inputs.normalsPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalsStrides"))
        attribute = test_node.get_attribute("inputs:normalsStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normalsStrides
        database.inputs.normalsStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:rgbCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:rgbCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.rgbCudaDeviceIndex
        database.inputs.rgbCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:rgbPtr"))
        attribute = test_node.get_attribute("inputs:rgbPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.rgbPtr
        database.inputs.rgbPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:rgbStrides"))
        attribute = test_node.get_attribute("inputs:rgbStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.rgbStrides
        database.inputs.rgbStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:semanticSegmentationCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:semanticSegmentationCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.semanticSegmentationCudaDeviceIndex
        database.inputs.semanticSegmentationCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:semanticSegmentationPtr"))
        attribute = test_node.get_attribute("inputs:semanticSegmentationPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.semanticSegmentationPtr
        database.inputs.semanticSegmentationPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:semanticSegmentationStrides"))
        attribute = test_node.get_attribute("inputs:semanticSegmentationStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.semanticSegmentationStrides
        database.inputs.semanticSegmentationStrides = db_value
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

        self.assertTrue(test_node.get_attribute_exists("outputs:height"))
        attribute = test_node.get_attribute("outputs:height")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.height
        database.outputs.height = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointInstanceBufferSize"))
        attribute = test_node.get_attribute("outputs:pointInstanceBufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointInstanceBufferSize
        database.outputs.pointInstanceBufferSize = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointInstanceCudaDeviceIndex"))
        attribute = test_node.get_attribute("outputs:pointInstanceCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointInstanceCudaDeviceIndex
        database.outputs.pointInstanceCudaDeviceIndex = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointInstanceDataShape"))
        attribute = test_node.get_attribute("outputs:pointInstanceDataShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointInstanceDataShape

        self.assertTrue(test_node.get_attribute_exists("outputs:pointInstanceDataType"))
        attribute = test_node.get_attribute("outputs:pointInstanceDataType")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointInstanceDataType
        database.outputs.pointInstanceDataType = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointInstancePtr"))
        attribute = test_node.get_attribute("outputs:pointInstancePtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointInstancePtr
        database.outputs.pointInstancePtr = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointNormalsBufferSize"))
        attribute = test_node.get_attribute("outputs:pointNormalsBufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointNormalsBufferSize
        database.outputs.pointNormalsBufferSize = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointNormalsCudaDeviceIndex"))
        attribute = test_node.get_attribute("outputs:pointNormalsCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointNormalsCudaDeviceIndex
        database.outputs.pointNormalsCudaDeviceIndex = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointNormalsDataShape"))
        attribute = test_node.get_attribute("outputs:pointNormalsDataShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointNormalsDataShape

        self.assertTrue(test_node.get_attribute_exists("outputs:pointNormalsDataType"))
        attribute = test_node.get_attribute("outputs:pointNormalsDataType")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointNormalsDataType
        database.outputs.pointNormalsDataType = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointNormalsPtr"))
        attribute = test_node.get_attribute("outputs:pointNormalsPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointNormalsPtr
        database.outputs.pointNormalsPtr = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointRgbBufferSize"))
        attribute = test_node.get_attribute("outputs:pointRgbBufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointRgbBufferSize
        database.outputs.pointRgbBufferSize = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointRgbCudaDeviceIndex"))
        attribute = test_node.get_attribute("outputs:pointRgbCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointRgbCudaDeviceIndex
        database.outputs.pointRgbCudaDeviceIndex = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointRgbDataShape"))
        attribute = test_node.get_attribute("outputs:pointRgbDataShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointRgbDataShape

        self.assertTrue(test_node.get_attribute_exists("outputs:pointRgbDataType"))
        attribute = test_node.get_attribute("outputs:pointRgbDataType")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointRgbDataType
        database.outputs.pointRgbDataType = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointRgbPtr"))
        attribute = test_node.get_attribute("outputs:pointRgbPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointRgbPtr
        database.outputs.pointRgbPtr = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointSemanticBufferSize"))
        attribute = test_node.get_attribute("outputs:pointSemanticBufferSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointSemanticBufferSize
        database.outputs.pointSemanticBufferSize = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointSemanticCudaDeviceIndex"))
        attribute = test_node.get_attribute("outputs:pointSemanticCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointSemanticCudaDeviceIndex
        database.outputs.pointSemanticCudaDeviceIndex = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointSemanticDataShape"))
        attribute = test_node.get_attribute("outputs:pointSemanticDataShape")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointSemanticDataShape

        self.assertTrue(test_node.get_attribute_exists("outputs:pointSemanticDataType"))
        attribute = test_node.get_attribute("outputs:pointSemanticDataType")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointSemanticDataType
        database.outputs.pointSemanticDataType = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:pointSemanticPtr"))
        attribute = test_node.get_attribute("outputs:pointSemanticPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.pointSemanticPtr
        database.outputs.pointSemanticPtr = db_value

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
