r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnMeshBoundsDecalPlacement

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

The position and rotation of a mesh for decal placement from mesh bounds.
"""

import numpy
import sys
import traceback
import usdrt

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnMeshBoundsDecalPlacementDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnMeshBoundsDecalPlacement

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.boundsVector
            inputs.execIn
            inputs.offset
            inputs.prims
            inputs.rotation
            inputs.scale
        Outputs:
            outputs.execOut
            outputs.rotation
            outputs.scale
            outputs.translate
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
        ('inputs:boundsVector', 'float3', 0, None, 'Normalized vector to determine translation and rotation in bounds.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0.0, 0.0, 0.0], False, ''),
        ('inputs:execIn', 'execution', 0, None, 'Input execution.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:offset', 'float', 0, None, 'How much to offset the final translation away from the bounds.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0.0, False, ''),
        ('inputs:prims', 'target', 0, None, 'Input prims to calculate bounds from.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:rotation', 'float3', 0, None, 'Additional rotation.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0.0, 0.0, 0.0], False, ''),
        ('inputs:scale', 'float3', 0, None, 'Scale to match bounds.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [0.0, 0.0, 0.0], False, ''),
        ('outputs:execOut', 'execution', 0, None, 'Output execution.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:rotation', 'float3', 0, None, 'The resulting local rotation (XYZ).', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:scale', 'float3', 0, None, 'The resulting local scale.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:translate', 'float3', 0, None, 'The resulting world translation.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.inputs.prims = og.AttributeRole.TARGET
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"boundsVector", "execIn", "offset", "rotation", "scale", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.boundsVector, self._attributes.execIn, self._attributes.offset, self._attributes.rotation, self._attributes.scale]
            self._batchedReadValues = [[0.0, 0.0, 0.0], None, 0.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

        @property
        def prims(self):
            data_view = og.AttributeValueHelper(self._attributes.prims)
            return data_view.get()

        @prims.setter
        def prims(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.prims)
            data_view = og.AttributeValueHelper(self._attributes.prims)
            data_view.set(value)
            self.prims_size = data_view.get_array_size()

        @property
        def boundsVector(self):
            return self._batchedReadValues[0]

        @boundsVector.setter
        def boundsVector(self, value):
            self._batchedReadValues[0] = value

        @property
        def execIn(self):
            return self._batchedReadValues[1]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[1] = value

        @property
        def offset(self):
            return self._batchedReadValues[2]

        @offset.setter
        def offset(self, value):
            self._batchedReadValues[2] = value

        @property
        def rotation(self):
            return self._batchedReadValues[3]

        @rotation.setter
        def rotation(self, value):
            self._batchedReadValues[3] = value

        @property
        def scale(self):
            return self._batchedReadValues[4]

        @scale.setter
        def scale(self, value):
            self._batchedReadValues[4] = value

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
        LOCAL_PROPERTY_NAMES = {"execOut", "rotation", "scale", "translate", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def execOut(self):
            value = self._batchedWriteValues.get(self._attributes.execOut)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.execOut)
                return data_view.get()

        @execOut.setter
        def execOut(self, value):
            self._batchedWriteValues[self._attributes.execOut] = value

        @property
        def rotation(self):
            value = self._batchedWriteValues.get(self._attributes.rotation)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.rotation)
                return data_view.get()

        @rotation.setter
        def rotation(self, value):
            self._batchedWriteValues[self._attributes.rotation] = value

        @property
        def scale(self):
            value = self._batchedWriteValues.get(self._attributes.scale)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.scale)
                return data_view.get()

        @scale.setter
        def scale(self, value):
            self._batchedWriteValues[self._attributes.scale] = value

        @property
        def translate(self):
            value = self._batchedWriteValues.get(self._attributes.translate)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.translate)
                return data_view.get()

        @translate.setter
        def translate(self, value):
            self._batchedWriteValues[self._attributes.translate] = value

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
        self.inputs = OgnMeshBoundsDecalPlacementDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnMeshBoundsDecalPlacementDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnMeshBoundsDecalPlacementDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnMeshBoundsDecalPlacement'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnMeshBoundsDecalPlacementDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnMeshBoundsDecalPlacementDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnMeshBoundsDecalPlacementDatabase(node)

            try:
                compute_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnMeshBoundsDecalPlacementDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnMeshBoundsDecalPlacementDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnMeshBoundsDecalPlacementDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnMeshBoundsDecalPlacementDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnMeshBoundsDecalPlacementDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Core,Core Replicator nodes")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "The position and rotation of a mesh for decal placement from mesh bounds.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnMeshBoundsDecalPlacementDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnMeshBoundsDecalPlacementDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnMeshBoundsDecalPlacementDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnMeshBoundsDecalPlacement")
