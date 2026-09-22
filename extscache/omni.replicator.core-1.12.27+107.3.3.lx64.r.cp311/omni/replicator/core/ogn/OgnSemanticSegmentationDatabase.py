r"""Support for simplified access to data on nodes of type omni.replicator.core.SemanticSegmentation

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This node outputs the semantic segmentation.
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnSemanticSegmentationDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.SemanticSegmentation

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.bufferSize
            inputs.colorize
            inputs.exec
            inputs.height
            inputs.ids
            inputs.instanceSegmentationCudaDeviceIndex
            inputs.instanceSegmentationPtr
            inputs.instanceSegmentationStrides
            inputs.labels
            inputs.mapping
            inputs.semanticFilterName
            inputs.semantics
            inputs.width
        Outputs:
            outputs._legacyIDs
            outputs.bufferSize
            outputs.cudaDeviceIndex
            outputs.dataPtr
            outputs.dataShape
            outputs.dataType
            outputs.exec
            outputs.height
            outputs.ids
            outputs.labels
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
        ('inputs:bufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:colorize', 'bool', 0, None, 'If true, convert semantic IDs into colors.', {ogn.MetadataKeys.DEFAULT: 'false', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, False, False, ''),
        ('inputs:exec', 'execution', 0, None, 'Trigger', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:height', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:ids', 'uint[]', 0, None, 'Unoccluded semantic u ids (or color, if `colorize` is set to True).', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [], False, ''),
        ('inputs:instanceSegmentationCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data) for instance segmentationSD', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('inputs:instanceSegmentationPtr', 'uint64', 0, None, 'Pointer to the raw instance segmetation data', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('inputs:instanceSegmentationStrides', 'int2', 0, None, 'Strides (in bytes) for InstanceSegmentationSD.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0, 0], False, ''),
        ('inputs:labels', 'token[]', 0, None, 'Prim path of the prim.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [], False, ''),
        ('inputs:mapping', 'string', 0, None, 'Optional mapping enforcing semantics to specific IDs or colors.', {ogn.MetadataKeys.DEFAULT: '"{}"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "{}", False, ''),
        ('inputs:semanticFilterName', 'token', 0, None, 'name of Semantic Filter to use', {ogn.MetadataKeys.DEFAULT: '""', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "", False, ''),
        ('inputs:semantics', 'token[]', 0, None, 'Semantic labels that correspond to the ids.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [], False, ''),
        ('inputs:width', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:_legacyIDs', 'bool', 0, None, 'If True, ids will be converted to strings for backwards compatibility', {ogn.MetadataKeys.DEFAULT: 'true', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, True, False, ''),
        ('outputs:bufferSize', 'uint', 0, None, 'Size (in bytes) of the buffer (0 if the input is a texture)', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:cudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, -1, False, ''),
        ('outputs:dataPtr', 'uint64', 0, None, 'Pointer to the raw data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0, False, ''),
        ('outputs:dataShape', 'int[]', 0, None, 'Desired dimensions of output array', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:dataType', 'token', 0, None, 'Defines the data type', {ogn.MetadataKeys.DEFAULT: '"uint8"', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, "uint8", False, ''),
        ('outputs:exec', 'execution', 0, None, 'Trigger', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:height', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:ids', 'uint[]', 0, None, 'Unoccluded semantic u ids (or color, if `colorize` is set to True).', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:labels', 'token[]', 0, None, 'Prim path of the prim.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:strides', 'int2', 0, None, 'Strides (in bytes).', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:width', 'uint', 0, None, 'Shape of the data', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.exec = og.AttributeRole.EXECUTION
        role_data.inputs.mapping = og.AttributeRole.TEXT
        role_data.outputs.exec = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"bufferSize", "colorize", "exec", "height", "instanceSegmentationCudaDeviceIndex", "instanceSegmentationPtr", "instanceSegmentationStrides", "mapping", "semanticFilterName", "width", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.bufferSize, self._attributes.colorize, self._attributes.exec, self._attributes.height, self._attributes.instanceSegmentationCudaDeviceIndex, self._attributes.instanceSegmentationPtr, self._attributes.instanceSegmentationStrides, self._attributes.mapping, self._attributes.semanticFilterName, self._attributes.width]
            self._batchedReadValues = [0, False, None, 0, -1, 0, [0, 0], "{}", "", 0]

        @property
        def ids(self):
            data_view = og.AttributeValueHelper(self._attributes.ids)
            return data_view.get()

        @ids.setter
        def ids(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.ids)
            data_view = og.AttributeValueHelper(self._attributes.ids)
            data_view.set(value)
            self.ids_size = data_view.get_array_size()

        @property
        def labels(self):
            data_view = og.AttributeValueHelper(self._attributes.labels)
            return data_view.get()

        @labels.setter
        def labels(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.labels)
            data_view = og.AttributeValueHelper(self._attributes.labels)
            data_view.set(value)
            self.labels_size = data_view.get_array_size()

        @property
        def semantics(self):
            data_view = og.AttributeValueHelper(self._attributes.semantics)
            return data_view.get()

        @semantics.setter
        def semantics(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.semantics)
            data_view = og.AttributeValueHelper(self._attributes.semantics)
            data_view.set(value)
            self.semantics_size = data_view.get_array_size()

        @property
        def bufferSize(self):
            return self._batchedReadValues[0]

        @bufferSize.setter
        def bufferSize(self, value):
            self._batchedReadValues[0] = value

        @property
        def colorize(self):
            return self._batchedReadValues[1]

        @colorize.setter
        def colorize(self, value):
            self._batchedReadValues[1] = value

        @property
        def exec(self):
            return self._batchedReadValues[2]

        @exec.setter
        def exec(self, value):
            self._batchedReadValues[2] = value

        @property
        def height(self):
            return self._batchedReadValues[3]

        @height.setter
        def height(self, value):
            self._batchedReadValues[3] = value

        @property
        def instanceSegmentationCudaDeviceIndex(self):
            return self._batchedReadValues[4]

        @instanceSegmentationCudaDeviceIndex.setter
        def instanceSegmentationCudaDeviceIndex(self, value):
            self._batchedReadValues[4] = value

        @property
        def instanceSegmentationPtr(self):
            return self._batchedReadValues[5]

        @instanceSegmentationPtr.setter
        def instanceSegmentationPtr(self, value):
            self._batchedReadValues[5] = value

        @property
        def instanceSegmentationStrides(self):
            return self._batchedReadValues[6]

        @instanceSegmentationStrides.setter
        def instanceSegmentationStrides(self, value):
            self._batchedReadValues[6] = value

        @property
        def mapping(self):
            return self._batchedReadValues[7]

        @mapping.setter
        def mapping(self, value):
            self._batchedReadValues[7] = value

        @property
        def semanticFilterName(self):
            return self._batchedReadValues[8]

        @semanticFilterName.setter
        def semanticFilterName(self, value):
            self._batchedReadValues[8] = value

        @property
        def width(self):
            return self._batchedReadValues[9]

        @width.setter
        def width(self, value):
            self._batchedReadValues[9] = value

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
        LOCAL_PROPERTY_NAMES = {"_legacyIDs", "bufferSize", "cudaDeviceIndex", "dataPtr", "dataType", "exec", "height", "strides", "width", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.dataShape_size = None
            self.ids_size = None
            self.labels_size = None
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
        def ids(self):
            data_view = og.AttributeValueHelper(self._attributes.ids)
            return data_view.get(reserved_element_count=self.ids_size)

        @ids.setter
        def ids(self, value):
            data_view = og.AttributeValueHelper(self._attributes.ids)
            data_view.set(value)
            self.ids_size = data_view.get_array_size()

        @property
        def labels(self):
            data_view = og.AttributeValueHelper(self._attributes.labels)
            return data_view.get(reserved_element_count=self.labels_size)

        @labels.setter
        def labels(self, value):
            data_view = og.AttributeValueHelper(self._attributes.labels)
            data_view.set(value)
            self.labels_size = data_view.get_array_size()

        @property
        def _legacyIDs(self):
            value = self._batchedWriteValues.get(self._attributes._legacyIDs)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes._legacyIDs)
                return data_view.get()

        @_legacyIDs.setter
        def _legacyIDs(self, value):
            self._batchedWriteValues[self._attributes._legacyIDs] = value

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
        self.inputs = OgnSemanticSegmentationDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnSemanticSegmentationDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnSemanticSegmentationDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.SemanticSegmentation'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnSemanticSegmentationDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnSemanticSegmentationDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnSemanticSegmentationDatabase(node)

            try:
                compute_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnSemanticSegmentationDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnSemanticSegmentationDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnSemanticSegmentationDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnSemanticSegmentationDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnSemanticSegmentationDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Annotators")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Annotators,Replicator annotator nodes.")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This node outputs the semantic segmentation.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnSemanticSegmentationDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnSemanticSegmentationDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnSemanticSegmentationDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.SemanticSegmentation")
