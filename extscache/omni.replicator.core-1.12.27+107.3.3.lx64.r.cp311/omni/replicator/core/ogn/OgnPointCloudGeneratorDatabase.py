r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnPointCloudGenerator

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This node generates pointcloud from rgb, normals, distance_to_camera and semantic sgementations.
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnPointCloudGeneratorDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnPointCloudGenerator

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.bufferSize
            inputs.camera3dPositionsCudaDeviceIndex
            inputs.camera3dPositionsPtr
            inputs.camera3dPositionsStrides
            inputs.cameraViewTransform
            inputs.exec
            inputs.height
            inputs.includeUnlabelled
            inputs.instanceSegmentationCudaDeviceIndex
            inputs.instanceSegmentationPtr
            inputs.instanceSegmentationStrides
            inputs.normalsCudaDeviceIndex
            inputs.normalsPtr
            inputs.normalsStrides
            inputs.rgbCudaDeviceIndex
            inputs.rgbPtr
            inputs.rgbStrides
            inputs.semanticSegmentationCudaDeviceIndex
            inputs.semanticSegmentationPtr
            inputs.semanticSegmentationStrides
            inputs.width
        Outputs:
            outputs.bufferSize
            outputs.cudaDeviceIndex
            outputs.dataPtr
            outputs.dataShape
            outputs.dataType
            outputs.exec
            outputs.height
            outputs.pointInstanceBufferSize
            outputs.pointInstanceCudaDeviceIndex
            outputs.pointInstanceDataShape
            outputs.pointInstanceDataType
            outputs.pointInstancePtr
            outputs.pointNormalsBufferSize
            outputs.pointNormalsCudaDeviceIndex
            outputs.pointNormalsDataShape
            outputs.pointNormalsDataType
            outputs.pointNormalsPtr
            outputs.pointRgbBufferSize
            outputs.pointRgbCudaDeviceIndex
            outputs.pointRgbDataShape
            outputs.pointRgbDataType
            outputs.pointRgbPtr
            outputs.pointSemanticBufferSize
            outputs.pointSemanticCudaDeviceIndex
            outputs.pointSemanticDataShape
            outputs.pointSemanticDataType
            outputs.pointSemanticPtr
            outputs.width
    """

    # Imprint the generator and target ABI versions in the file for JIT generation
    GENERATOR_VERSION = (1, 79, 2)
    TARGET_VERSION = (2, 184, 5)

    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}

    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:bufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:camera3dPositionsCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:camera3dPositionsPtr', 'uint64', 0, None, 'Pointer to the raw camera 3d position data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:camera3dPositionsStrides', 'int2', 0, None, 'Strides (in bytes) for Camera3dPosition.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:cameraViewTransform', 'matrix4d', 0, None, 'Camera view matrix', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
        ('inputs:exec', 'execution', 0, None, 'Trigger', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:height', 'uint', 0, None, 'Height', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:includeUnlabelled', 'bool', 0, None, 'If set to true, prim with no semantics will also be in output', {ogn.MetadataKeys.DEFAULT: 'false', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, False, False, ''),
        ('inputs:instanceSegmentationCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:instanceSegmentationPtr', 'uint64', 0, None, 'Pointer to the raw instance segmentation data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:instanceSegmentationStrides', 'int2', 0, None, 'Strides (in bytes) for instance segmentation.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:normalsCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:normalsPtr', 'uint64', 0, None, 'Pointer to the raw normals data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:normalsStrides', 'int2', 0, None, 'Strides (in bytes) for normals.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:rgbCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:rgbPtr', 'uint64', 0, None, 'Pointer to the raw rgb data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:rgbStrides', 'int2', 0, None, 'Strides (in bytes) for LdrColor.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:semanticSegmentationCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:semanticSegmentationPtr', 'uint64', 0, None, 'Pointer to the raw semantic segmentation data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:semanticSegmentationStrides', 'int2', 0, None, 'Strides (in bytes) for semanticSegmentation.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:width', 'uint', 0, None, 'Width', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:bufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:cudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:dataPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:dataShape', 'int[]', 0, None, 'Desired dimensions of output array', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:dataType', 'token', 0, None, 'Defines the data type', {ogn.MetadataKeys.DEFAULT: '"float32"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "float32", False, ''),
        ('outputs:exec', 'execution', 0, None, 'Trigger', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:height', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointInstanceBufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointInstanceCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:pointInstanceDataShape', 'int[]', 0, None, 'Desired dimensions of output array', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointInstanceDataType', 'token', 0, None, 'Defines the data type', {ogn.MetadataKeys.DEFAULT: '"uint32"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "uint32", False, ''),
        ('outputs:pointInstancePtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:pointNormalsBufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointNormalsCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:pointNormalsDataShape', 'int[]', 0, None, 'Desired dimensions of output array', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointNormalsDataType', 'token', 0, None, 'Defines the data type', {ogn.MetadataKeys.DEFAULT: '"float32"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "float32", False, ''),
        ('outputs:pointNormalsPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:pointRgbBufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointRgbCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:pointRgbDataShape', 'int[]', 0, None, 'Desired dimensions of output array', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointRgbDataType', 'token', 0, None, 'Defines the data type', {ogn.MetadataKeys.DEFAULT: '"uint8"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "uint8", False, ''),
        ('outputs:pointRgbPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:pointSemanticBufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointSemanticCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:pointSemanticDataShape', 'int[]', 0, None, 'Desired dimensions of output array', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:pointSemanticDataType', 'token', 0, None, 'Defines the data type', {ogn.MetadataKeys.DEFAULT: '"uint32"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "uint32", False, ''),
        ('outputs:pointSemanticPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:width', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.cameraViewTransform = og.AttributeRole.MATRIX
        role_data.inputs.exec = og.AttributeRole.EXECUTION
        role_data.outputs.exec = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"bufferSize", "camera3dPositionsCudaDeviceIndex", "camera3dPositionsPtr", "camera3dPositionsStrides", "cameraViewTransform", "exec", "height", "includeUnlabelled", "instanceSegmentationCudaDeviceIndex", "instanceSegmentationPtr", "instanceSegmentationStrides", "normalsCudaDeviceIndex", "normalsPtr", "normalsStrides", "rgbCudaDeviceIndex", "rgbPtr", "rgbStrides", "semanticSegmentationCudaDeviceIndex", "semanticSegmentationPtr", "semanticSegmentationStrides", "width", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.bufferSize, self._attributes.camera3dPositionsCudaDeviceIndex, self._attributes.camera3dPositionsPtr, self._attributes.camera3dPositionsStrides, self._attributes.cameraViewTransform, self._attributes.exec, self._attributes.height, self._attributes.includeUnlabelled, self._attributes.instanceSegmentationCudaDeviceIndex, self._attributes.instanceSegmentationPtr, self._attributes.instanceSegmentationStrides, self._attributes.normalsCudaDeviceIndex, self._attributes.normalsPtr, self._attributes.normalsStrides, self._attributes.rgbCudaDeviceIndex, self._attributes.rgbPtr, self._attributes.rgbStrides, self._attributes.semanticSegmentationCudaDeviceIndex, self._attributes.semanticSegmentationPtr, self._attributes.semanticSegmentationStrides, self._attributes.width]
            self._batchedReadValues = [0, -1, 0, [0, 0], [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], None, 0, False, -1, 0, [0, 0], -1, 0, [0, 0], -1, 0, [0, 0], -1, 0, [0, 0], 0]

        @property
        def bufferSize(self):
            return self._batchedReadValues[0]

        @bufferSize.setter
        def bufferSize(self, value):
            self._batchedReadValues[0] = value

        @property
        def camera3dPositionsCudaDeviceIndex(self):
            return self._batchedReadValues[1]

        @camera3dPositionsCudaDeviceIndex.setter
        def camera3dPositionsCudaDeviceIndex(self, value):
            self._batchedReadValues[1] = value

        @property
        def camera3dPositionsPtr(self):
            return self._batchedReadValues[2]

        @camera3dPositionsPtr.setter
        def camera3dPositionsPtr(self, value):
            self._batchedReadValues[2] = value

        @property
        def camera3dPositionsStrides(self):
            return self._batchedReadValues[3]

        @camera3dPositionsStrides.setter
        def camera3dPositionsStrides(self, value):
            self._batchedReadValues[3] = value

        @property
        def cameraViewTransform(self):
            return self._batchedReadValues[4]

        @cameraViewTransform.setter
        def cameraViewTransform(self, value):
            self._batchedReadValues[4] = value

        @property
        def exec(self):
            return self._batchedReadValues[5]

        @exec.setter
        def exec(self, value):
            self._batchedReadValues[5] = value

        @property
        def height(self):
            return self._batchedReadValues[6]

        @height.setter
        def height(self, value):
            self._batchedReadValues[6] = value

        @property
        def includeUnlabelled(self):
            return self._batchedReadValues[7]

        @includeUnlabelled.setter
        def includeUnlabelled(self, value):
            self._batchedReadValues[7] = value

        @property
        def instanceSegmentationCudaDeviceIndex(self):
            return self._batchedReadValues[8]

        @instanceSegmentationCudaDeviceIndex.setter
        def instanceSegmentationCudaDeviceIndex(self, value):
            self._batchedReadValues[8] = value

        @property
        def instanceSegmentationPtr(self):
            return self._batchedReadValues[9]

        @instanceSegmentationPtr.setter
        def instanceSegmentationPtr(self, value):
            self._batchedReadValues[9] = value

        @property
        def instanceSegmentationStrides(self):
            return self._batchedReadValues[10]

        @instanceSegmentationStrides.setter
        def instanceSegmentationStrides(self, value):
            self._batchedReadValues[10] = value

        @property
        def normalsCudaDeviceIndex(self):
            return self._batchedReadValues[11]

        @normalsCudaDeviceIndex.setter
        def normalsCudaDeviceIndex(self, value):
            self._batchedReadValues[11] = value

        @property
        def normalsPtr(self):
            return self._batchedReadValues[12]

        @normalsPtr.setter
        def normalsPtr(self, value):
            self._batchedReadValues[12] = value

        @property
        def normalsStrides(self):
            return self._batchedReadValues[13]

        @normalsStrides.setter
        def normalsStrides(self, value):
            self._batchedReadValues[13] = value

        @property
        def rgbCudaDeviceIndex(self):
            return self._batchedReadValues[14]

        @rgbCudaDeviceIndex.setter
        def rgbCudaDeviceIndex(self, value):
            self._batchedReadValues[14] = value

        @property
        def rgbPtr(self):
            return self._batchedReadValues[15]

        @rgbPtr.setter
        def rgbPtr(self, value):
            self._batchedReadValues[15] = value

        @property
        def rgbStrides(self):
            return self._batchedReadValues[16]

        @rgbStrides.setter
        def rgbStrides(self, value):
            self._batchedReadValues[16] = value

        @property
        def semanticSegmentationCudaDeviceIndex(self):
            return self._batchedReadValues[17]

        @semanticSegmentationCudaDeviceIndex.setter
        def semanticSegmentationCudaDeviceIndex(self, value):
            self._batchedReadValues[17] = value

        @property
        def semanticSegmentationPtr(self):
            return self._batchedReadValues[18]

        @semanticSegmentationPtr.setter
        def semanticSegmentationPtr(self, value):
            self._batchedReadValues[18] = value

        @property
        def semanticSegmentationStrides(self):
            return self._batchedReadValues[19]

        @semanticSegmentationStrides.setter
        def semanticSegmentationStrides(self, value):
            self._batchedReadValues[19] = value

        @property
        def width(self):
            return self._batchedReadValues[20]

        @width.setter
        def width(self, value):
            self._batchedReadValues[20] = value

        def __getattr__(self, item: str):
            if item in self.LOCAL_PROPERTY_NAMES:
                return object.__getattribute__(self, item)
            else:
                return super().__getattr__(item)

        def __setattr__(self, item: str, new_value):
            if item in self.LOCAL_PROPERTY_NAMES:
                object.__setattr__(self, item, new_value)
            else:
                super().__setattr__(item, new_value)

        def _prefetch(self):
            readAttributes = self._batchedReadAttributes
            newValues = _og._prefetch_input_attributes_data(readAttributes)
            if len(readAttributes) == len(newValues):
                self._batchedReadValues = newValues

    class ValuesForOutputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"bufferSize", "cudaDeviceIndex", "dataPtr", "dataType", "exec", "height", "pointInstanceBufferSize", "pointInstanceCudaDeviceIndex", "pointInstanceDataType", "pointInstancePtr", "pointNormalsBufferSize", "pointNormalsCudaDeviceIndex", "pointNormalsDataType", "pointNormalsPtr", "pointRgbBufferSize", "pointRgbCudaDeviceIndex", "pointRgbDataType", "pointRgbPtr", "pointSemanticBufferSize", "pointSemanticCudaDeviceIndex", "pointSemanticDataType", "pointSemanticPtr", "width", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.dataShape_size = None
            self.pointInstanceDataShape_size = None
            self.pointNormalsDataShape_size = None
            self.pointRgbDataShape_size = None
            self.pointSemanticDataShape_size = None
            self._batchedWriteValues = { }

        @property
        def dataShape(self):
            data_view = og.AttributeValueHelper(self._attributes.dataShape)
            return data_view.get(reserved_element_count=self.dataShape_size)

        @dataShape.setter
        def dataShape(self, value):
            data_view = og.AttributeValueHelper(self._attributes.dataShape)
            data_view.set(value)
            self.dataShape_size = data_view.get_array_size()

        @property
        def pointInstanceDataShape(self):
            data_view = og.AttributeValueHelper(self._attributes.pointInstanceDataShape)
            return data_view.get(reserved_element_count=self.pointInstanceDataShape_size)

        @pointInstanceDataShape.setter
        def pointInstanceDataShape(self, value):
            data_view = og.AttributeValueHelper(self._attributes.pointInstanceDataShape)
            data_view.set(value)
            self.pointInstanceDataShape_size = data_view.get_array_size()

        @property
        def pointNormalsDataShape(self):
            data_view = og.AttributeValueHelper(self._attributes.pointNormalsDataShape)
            return data_view.get(reserved_element_count=self.pointNormalsDataShape_size)

        @pointNormalsDataShape.setter
        def pointNormalsDataShape(self, value):
            data_view = og.AttributeValueHelper(self._attributes.pointNormalsDataShape)
            data_view.set(value)
            self.pointNormalsDataShape_size = data_view.get_array_size()

        @property
        def pointRgbDataShape(self):
            data_view = og.AttributeValueHelper(self._attributes.pointRgbDataShape)
            return data_view.get(reserved_element_count=self.pointRgbDataShape_size)

        @pointRgbDataShape.setter
        def pointRgbDataShape(self, value):
            data_view = og.AttributeValueHelper(self._attributes.pointRgbDataShape)
            data_view.set(value)
            self.pointRgbDataShape_size = data_view.get_array_size()

        @property
        def pointSemanticDataShape(self):
            data_view = og.AttributeValueHelper(self._attributes.pointSemanticDataShape)
            return data_view.get(reserved_element_count=self.pointSemanticDataShape_size)

        @pointSemanticDataShape.setter
        def pointSemanticDataShape(self, value):
            data_view = og.AttributeValueHelper(self._attributes.pointSemanticDataShape)
            data_view.set(value)
            self.pointSemanticDataShape_size = data_view.get_array_size()

        @property
        def bufferSize(self):
            value = self._batchedWriteValues.get(self._attributes.bufferSize)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.bufferSize)
                return data_view.get()

        @bufferSize.setter
        def bufferSize(self, value):
            self._batchedWriteValues[self._attributes.bufferSize] = value

        @property
        def cudaDeviceIndex(self):
            value = self._batchedWriteValues.get(self._attributes.cudaDeviceIndex)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.cudaDeviceIndex)
                return data_view.get()

        @cudaDeviceIndex.setter
        def cudaDeviceIndex(self, value):
            self._batchedWriteValues[self._attributes.cudaDeviceIndex] = value

        @property
        def dataPtr(self):
            value = self._batchedWriteValues.get(self._attributes.dataPtr)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.dataPtr)
                return data_view.get()

        @dataPtr.setter
        def dataPtr(self, value):
            self._batchedWriteValues[self._attributes.dataPtr] = value

        @property
        def dataType(self):
            value = self._batchedWriteValues.get(self._attributes.dataType)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.dataType)
                return data_view.get()

        @dataType.setter
        def dataType(self, value):
            self._batchedWriteValues[self._attributes.dataType] = value

        @property
        def exec(self):
            value = self._batchedWriteValues.get(self._attributes.exec)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.exec)
                return data_view.get()

        @exec.setter
        def exec(self, value):
            self._batchedWriteValues[self._attributes.exec] = value

        @property
        def height(self):
            value = self._batchedWriteValues.get(self._attributes.height)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.height)
                return data_view.get()

        @height.setter
        def height(self, value):
            self._batchedWriteValues[self._attributes.height] = value

        @property
        def pointInstanceBufferSize(self):
            value = self._batchedWriteValues.get(self._attributes.pointInstanceBufferSize)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointInstanceBufferSize)
                return data_view.get()

        @pointInstanceBufferSize.setter
        def pointInstanceBufferSize(self, value):
            self._batchedWriteValues[self._attributes.pointInstanceBufferSize] = value

        @property
        def pointInstanceCudaDeviceIndex(self):
            value = self._batchedWriteValues.get(self._attributes.pointInstanceCudaDeviceIndex)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointInstanceCudaDeviceIndex)
                return data_view.get()

        @pointInstanceCudaDeviceIndex.setter
        def pointInstanceCudaDeviceIndex(self, value):
            self._batchedWriteValues[self._attributes.pointInstanceCudaDeviceIndex] = value

        @property
        def pointInstanceDataType(self):
            value = self._batchedWriteValues.get(self._attributes.pointInstanceDataType)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointInstanceDataType)
                return data_view.get()

        @pointInstanceDataType.setter
        def pointInstanceDataType(self, value):
            self._batchedWriteValues[self._attributes.pointInstanceDataType] = value

        @property
        def pointInstancePtr(self):
            value = self._batchedWriteValues.get(self._attributes.pointInstancePtr)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointInstancePtr)
                return data_view.get()

        @pointInstancePtr.setter
        def pointInstancePtr(self, value):
            self._batchedWriteValues[self._attributes.pointInstancePtr] = value

        @property
        def pointNormalsBufferSize(self):
            value = self._batchedWriteValues.get(self._attributes.pointNormalsBufferSize)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointNormalsBufferSize)
                return data_view.get()

        @pointNormalsBufferSize.setter
        def pointNormalsBufferSize(self, value):
            self._batchedWriteValues[self._attributes.pointNormalsBufferSize] = value

        @property
        def pointNormalsCudaDeviceIndex(self):
            value = self._batchedWriteValues.get(self._attributes.pointNormalsCudaDeviceIndex)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointNormalsCudaDeviceIndex)
                return data_view.get()

        @pointNormalsCudaDeviceIndex.setter
        def pointNormalsCudaDeviceIndex(self, value):
            self._batchedWriteValues[self._attributes.pointNormalsCudaDeviceIndex] = value

        @property
        def pointNormalsDataType(self):
            value = self._batchedWriteValues.get(self._attributes.pointNormalsDataType)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointNormalsDataType)
                return data_view.get()

        @pointNormalsDataType.setter
        def pointNormalsDataType(self, value):
            self._batchedWriteValues[self._attributes.pointNormalsDataType] = value

        @property
        def pointNormalsPtr(self):
            value = self._batchedWriteValues.get(self._attributes.pointNormalsPtr)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointNormalsPtr)
                return data_view.get()

        @pointNormalsPtr.setter
        def pointNormalsPtr(self, value):
            self._batchedWriteValues[self._attributes.pointNormalsPtr] = value

        @property
        def pointRgbBufferSize(self):
            value = self._batchedWriteValues.get(self._attributes.pointRgbBufferSize)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointRgbBufferSize)
                return data_view.get()

        @pointRgbBufferSize.setter
        def pointRgbBufferSize(self, value):
            self._batchedWriteValues[self._attributes.pointRgbBufferSize] = value

        @property
        def pointRgbCudaDeviceIndex(self):
            value = self._batchedWriteValues.get(self._attributes.pointRgbCudaDeviceIndex)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointRgbCudaDeviceIndex)
                return data_view.get()

        @pointRgbCudaDeviceIndex.setter
        def pointRgbCudaDeviceIndex(self, value):
            self._batchedWriteValues[self._attributes.pointRgbCudaDeviceIndex] = value

        @property
        def pointRgbDataType(self):
            value = self._batchedWriteValues.get(self._attributes.pointRgbDataType)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointRgbDataType)
                return data_view.get()

        @pointRgbDataType.setter
        def pointRgbDataType(self, value):
            self._batchedWriteValues[self._attributes.pointRgbDataType] = value

        @property
        def pointRgbPtr(self):
            value = self._batchedWriteValues.get(self._attributes.pointRgbPtr)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointRgbPtr)
                return data_view.get()

        @pointRgbPtr.setter
        def pointRgbPtr(self, value):
            self._batchedWriteValues[self._attributes.pointRgbPtr] = value

        @property
        def pointSemanticBufferSize(self):
            value = self._batchedWriteValues.get(self._attributes.pointSemanticBufferSize)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointSemanticBufferSize)
                return data_view.get()

        @pointSemanticBufferSize.setter
        def pointSemanticBufferSize(self, value):
            self._batchedWriteValues[self._attributes.pointSemanticBufferSize] = value

        @property
        def pointSemanticCudaDeviceIndex(self):
            value = self._batchedWriteValues.get(self._attributes.pointSemanticCudaDeviceIndex)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointSemanticCudaDeviceIndex)
                return data_view.get()

        @pointSemanticCudaDeviceIndex.setter
        def pointSemanticCudaDeviceIndex(self, value):
            self._batchedWriteValues[self._attributes.pointSemanticCudaDeviceIndex] = value

        @property
        def pointSemanticDataType(self):
            value = self._batchedWriteValues.get(self._attributes.pointSemanticDataType)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointSemanticDataType)
                return data_view.get()

        @pointSemanticDataType.setter
        def pointSemanticDataType(self, value):
            self._batchedWriteValues[self._attributes.pointSemanticDataType] = value

        @property
        def pointSemanticPtr(self):
            value = self._batchedWriteValues.get(self._attributes.pointSemanticPtr)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.pointSemanticPtr)
                return data_view.get()

        @pointSemanticPtr.setter
        def pointSemanticPtr(self, value):
            self._batchedWriteValues[self._attributes.pointSemanticPtr] = value

        @property
        def width(self):
            value = self._batchedWriteValues.get(self._attributes.width)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.width)
                return data_view.get()

        @width.setter
        def width(self, value):
            self._batchedWriteValues[self._attributes.width] = value

        def __getattr__(self, item: str):
            if item in self.LOCAL_PROPERTY_NAMES:
                return object.__getattribute__(self, item)
            else:
                return super().__getattr__(item)

        def __setattr__(self, item: str, new_value):
            if item in self.LOCAL_PROPERTY_NAMES:
                object.__setattr__(self, item, new_value)
            else:
                super().__setattr__(item, new_value)

        def _commit(self):
            _og._commit_output_attributes_data(self._batchedWriteValues)
            self._batchedWriteValues = { }

    class ValuesForState(og.DynamicAttributeAccess):
        """Helper class that creates natural hierarchical access to state attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)

    def __init__(self, node):
        super().__init__(node)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
        self.inputs = OgnPointCloudGeneratorDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnPointCloudGeneratorDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnPointCloudGeneratorDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnPointCloudGenerator'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnPointCloudGeneratorDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnPointCloudGeneratorDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnPointCloudGeneratorDatabase(node)

            try:
                compute_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnPointCloudGeneratorDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnPointCloudGeneratorDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnPointCloudGeneratorDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnPointCloudGeneratorDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnPointCloudGeneratorDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Get Pointcloud Python")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Annotators")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Annotators,Replicator annotator nodes.")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This node generates pointcloud from rgb, normals, distance_to_camera and semantic sgementations.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnPointCloudGeneratorDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnPointCloudGeneratorDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnPointCloudGeneratorDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnPointCloudGenerator")
