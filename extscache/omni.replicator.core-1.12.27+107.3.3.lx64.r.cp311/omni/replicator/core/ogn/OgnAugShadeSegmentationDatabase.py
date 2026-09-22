r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnAugShadeSegmentation

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This node randomizes the background using alpha channel.
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnAugShadeSegmentationDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnAugShadeSegmentation

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.exec
            inputs.format
            inputs.height
            inputs.lightSource
            inputs.normalBufferSize
            inputs.normalCudaDeviceIndex
            inputs.normalData
            inputs.normalDataPtr
            inputs.normalStrides
            inputs.segmentationBufferSize
            inputs.segmentationCudaDeviceIndex
            inputs.segmentationData
            inputs.segmentationDataPtr
            inputs.segmentationStrides
            inputs.useCandyColours
            inputs.width
        Outputs:
            outputs.bufferSize
            outputs.cudaDeviceIndex
            outputs.dataPtr
            outputs.exec
            outputs.format
            outputs.height
            outputs.strides
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
        ('inputs:exec', 'execution', 0, None, 'Trigger', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:format', 'uint64', 0, None, 'Format', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:height', 'uint', 0, None, 'Height', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:lightSource', 'float3', 0, None, 'Light source direction', {ogn.MetadataKeys.DEFAULT: '[0.0, 0.0, 1.0]', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0.0, 0.0, 1.0], False, ''),
        ('inputs:normalBufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:normalCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:normalData', 'uchar[]', 0, None, 'Buffer array data', {ogn.MetadataKeys.MEMORY_TYPE: 'cuda', ogn.MetadataKeys.DEFAULT: '[]', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [], False, ''),
        ('inputs:normalDataPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:normalStrides', 'int2', 0, None, 'Strides (in bytes) ([0,0] if the input is a buffer)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:segmentationBufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:segmentationCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:segmentationData', 'uchar[]', 0, None, 'Buffer array data', {ogn.MetadataKeys.MEMORY_TYPE: 'cuda', ogn.MetadataKeys.DEFAULT: '[]', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [], False, ''),
        ('inputs:segmentationDataPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:segmentationStrides', 'int2', 0, None, 'Strides (in bytes) ([0,0] if the input is a buffer)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:useCandyColours', 'bool', 0, None, 'If true, replace segmentation colours with random candy colours', {ogn.MetadataKeys.DEFAULT: 'false', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, False, False, ''),
        ('inputs:width', 'uint', 0, None, 'Width', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:bufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:cudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:dataPtr', 'uint64', 0, None, 'Pointer to the raw data (cuda device pointer or host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:exec', 'execution', 0, None, 'Trigger', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:format', 'uint', 0, None, 'Format', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:height', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:strides', 'int2', 0, None, 'Strides (in bytes) ([0,0] if the input is a buffer)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:width', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.exec = og.AttributeRole.EXECUTION
        role_data.outputs.exec = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"exec", "format", "height", "lightSource", "normalBufferSize", "normalCudaDeviceIndex", "normalDataPtr", "normalStrides", "segmentationBufferSize", "segmentationCudaDeviceIndex", "segmentationDataPtr", "segmentationStrides", "useCandyColours", "width", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.exec, self._attributes.format, self._attributes.height, self._attributes.lightSource, self._attributes.normalBufferSize, self._attributes.normalCudaDeviceIndex, self._attributes.normalDataPtr, self._attributes.normalStrides, self._attributes.segmentationBufferSize, self._attributes.segmentationCudaDeviceIndex, self._attributes.segmentationDataPtr, self._attributes.segmentationStrides, self._attributes.useCandyColours, self._attributes.width]
            self._batchedReadValues = [None, 0, 0, [0.0, 0.0, 1.0], 0, -1, 0, [0, 0], 0, -1, 0, [0, 0], False, 0]

        @property
        def normalData(self):
            data_view = og.AttributeValueHelper(self._attributes.normalData)
            data_view.gpu_ptr_kind = og.PtrToPtrKind.CPU
            return data_view.get(on_gpu=True)

        @normalData.setter
        def normalData(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.normalData)
            data_view = og.AttributeValueHelper(self._attributes.normalData)
            data_view.gpu_ptr_kind = og.PtrToPtrKind.CPU
            data_view.set(value, on_gpu=True)
            self.normalData_size = data_view.get_array_size()

        @property
        def segmentationData(self):
            data_view = og.AttributeValueHelper(self._attributes.segmentationData)
            data_view.gpu_ptr_kind = og.PtrToPtrKind.CPU
            return data_view.get(on_gpu=True)

        @segmentationData.setter
        def segmentationData(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.segmentationData)
            data_view = og.AttributeValueHelper(self._attributes.segmentationData)
            data_view.gpu_ptr_kind = og.PtrToPtrKind.CPU
            data_view.set(value, on_gpu=True)
            self.segmentationData_size = data_view.get_array_size()

        @property
        def exec(self):
            return self._batchedReadValues[0]

        @exec.setter
        def exec(self, value):
            self._batchedReadValues[0] = value

        @property
        def format(self):
            return self._batchedReadValues[1]

        @format.setter
        def format(self, value):
            self._batchedReadValues[1] = value

        @property
        def height(self):
            return self._batchedReadValues[2]

        @height.setter
        def height(self, value):
            self._batchedReadValues[2] = value

        @property
        def lightSource(self):
            return self._batchedReadValues[3]

        @lightSource.setter
        def lightSource(self, value):
            self._batchedReadValues[3] = value

        @property
        def normalBufferSize(self):
            return self._batchedReadValues[4]

        @normalBufferSize.setter
        def normalBufferSize(self, value):
            self._batchedReadValues[4] = value

        @property
        def normalCudaDeviceIndex(self):
            return self._batchedReadValues[5]

        @normalCudaDeviceIndex.setter
        def normalCudaDeviceIndex(self, value):
            self._batchedReadValues[5] = value

        @property
        def normalDataPtr(self):
            return self._batchedReadValues[6]

        @normalDataPtr.setter
        def normalDataPtr(self, value):
            self._batchedReadValues[6] = value

        @property
        def normalStrides(self):
            return self._batchedReadValues[7]

        @normalStrides.setter
        def normalStrides(self, value):
            self._batchedReadValues[7] = value

        @property
        def segmentationBufferSize(self):
            return self._batchedReadValues[8]

        @segmentationBufferSize.setter
        def segmentationBufferSize(self, value):
            self._batchedReadValues[8] = value

        @property
        def segmentationCudaDeviceIndex(self):
            return self._batchedReadValues[9]

        @segmentationCudaDeviceIndex.setter
        def segmentationCudaDeviceIndex(self, value):
            self._batchedReadValues[9] = value

        @property
        def segmentationDataPtr(self):
            return self._batchedReadValues[10]

        @segmentationDataPtr.setter
        def segmentationDataPtr(self, value):
            self._batchedReadValues[10] = value

        @property
        def segmentationStrides(self):
            return self._batchedReadValues[11]

        @segmentationStrides.setter
        def segmentationStrides(self, value):
            self._batchedReadValues[11] = value

        @property
        def useCandyColours(self):
            return self._batchedReadValues[12]

        @useCandyColours.setter
        def useCandyColours(self, value):
            self._batchedReadValues[12] = value

        @property
        def width(self):
            return self._batchedReadValues[13]

        @width.setter
        def width(self, value):
            self._batchedReadValues[13] = value

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
        LOCAL_PROPERTY_NAMES = {"bufferSize", "cudaDeviceIndex", "dataPtr", "exec", "format", "height", "strides", "width", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

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
        def format(self):
            value = self._batchedWriteValues.get(self._attributes.format)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.format)
                return data_view.get()

        @format.setter
        def format(self, value):
            self._batchedWriteValues[self._attributes.format] = value

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
        def strides(self):
            value = self._batchedWriteValues.get(self._attributes.strides)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.strides)
                return data_view.get()

        @strides.setter
        def strides(self, value):
            self._batchedWriteValues[self._attributes.strides] = value

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
        self.inputs = OgnAugShadeSegmentationDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnAugShadeSegmentationDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnAugShadeSegmentationDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnAugShadeSegmentation'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnAugShadeSegmentationDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnAugShadeSegmentationDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnAugShadeSegmentationDatabase(node)

            try:
                compute_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnAugShadeSegmentationDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnAugShadeSegmentationDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnAugShadeSegmentationDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnAugShadeSegmentationDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnAugShadeSegmentationDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator,OgnAugShadeSegmentation")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This node randomizes the background using alpha channel.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnAugShadeSegmentationDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnAugShadeSegmentationDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnAugShadeSegmentationDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnAugShadeSegmentation")
