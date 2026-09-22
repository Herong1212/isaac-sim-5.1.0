r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnDecal

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Mesh decal node
"""

import numpy
import sys
import traceback

import carb
import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnDecalDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnDecal

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.clip_depth
            inputs.clip_height
            inputs.clip_width
            inputs.clip_xform
            inputs.execIn
            inputs.mesh
            inputs.offset_depth
            inputs.offset_normal
        Outputs:
            outputs.execOut
            outputs.mesh
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
        ('inputs:clip_depth', 'float', 0, None, 'Depth along the z-axis of the clip volume', {ogn.MetadataKeys.DEFAULT: '100.0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 100.0, False, ''),
        ('inputs:clip_height', 'float', 0, None, 'Height along the y-axis of the clip volume', {ogn.MetadataKeys.DEFAULT: '100.0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 100.0, False, ''),
        ('inputs:clip_width', 'float', 0, None, 'Width along the x-axis of the clip volume', {ogn.MetadataKeys.DEFAULT: '100.0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 100.0, False, ''),
        ('inputs:clip_xform', 'matrix4d', 0, None, 'Collider mesh', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
        ('inputs:execIn', 'execution', 0, None, 'Input execution.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:mesh', 'bundle', 0, None, 'Cloth geometry', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('inputs:offset_depth', 'float', 0, None, '', {ogn.MetadataKeys.DEFAULT: '0.0', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0.0, False, ''),
        ('inputs:offset_normal', 'float', 0, None, '', {ogn.MetadataKeys.DEFAULT: '0.1', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, 0.1, False, ''),
        ('outputs:execOut', 'execution', 0, None, 'Output execution.', {ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
        ('outputs:mesh', 'bundle', 0, None, 'Decal mesh geometry', {ogn.MetadataKeys.MEMORY_TYPE: 'cpu', ogn.MetadataKeys.CUDA_POINTERS: 'cpu'}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.clip_xform = og.AttributeRole.MATRIX
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.inputs.mesh = og.AttributeRole.BUNDLE
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        role_data.outputs.mesh = og.AttributeRole.BUNDLE
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"clip_depth", "clip_height", "clip_width", "clip_xform", "execIn", "offset_depth", "offset_normal", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.__bundles = og.BundleContainer(context, node, attributes, [], read_only=True, gpu_ptr_kinds={})
            self._batchedReadAttributes = [self._attributes.clip_depth, self._attributes.clip_height, self._attributes.clip_width, self._attributes.clip_xform, self._attributes.execIn, self._attributes.offset_depth, self._attributes.offset_normal]
            self._batchedReadValues = [100.0, 100.0, 100.0, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], None, 0.0, 0.1]

        @property
        def mesh(self) -> og.BundleContents:
            """Get the bundle wrapper class for the attribute inputs.mesh"""
            return self.__bundles.mesh

        @property
        def clip_depth(self):
            return self._batchedReadValues[0]

        @clip_depth.setter
        def clip_depth(self, value):
            self._batchedReadValues[0] = value

        @property
        def clip_height(self):
            return self._batchedReadValues[1]

        @clip_height.setter
        def clip_height(self, value):
            self._batchedReadValues[1] = value

        @property
        def clip_width(self):
            return self._batchedReadValues[2]

        @clip_width.setter
        def clip_width(self, value):
            self._batchedReadValues[2] = value

        @property
        def clip_xform(self):
            return self._batchedReadValues[3]

        @clip_xform.setter
        def clip_xform(self, value):
            self._batchedReadValues[3] = value

        @property
        def execIn(self):
            return self._batchedReadValues[4]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[4] = value

        @property
        def offset_depth(self):
            return self._batchedReadValues[5]

        @offset_depth.setter
        def offset_depth(self, value):
            self._batchedReadValues[5] = value

        @property
        def offset_normal(self):
            return self._batchedReadValues[6]

        @offset_normal.setter
        def offset_normal(self, value):
            self._batchedReadValues[6] = value

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
        LOCAL_PROPERTY_NAMES = {"execOut", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.__bundles = og.BundleContainer(context, node, attributes, [], read_only=False, gpu_ptr_kinds={})
            self._batchedWriteValues = { }

        @property
        def mesh(self) -> og.BundleContents:
            """Get the bundle wrapper class for the attribute outputs.mesh"""
            return self.__bundles.mesh

        @mesh.setter
        def mesh(self, bundle: og.BundleContents):
            """Overwrite the bundle attribute outputs.mesh with a new bundle"""
            if not isinstance(bundle, og.BundleContents):
                carb.log_error("Only bundle attributes can be assigned to another bundle attribute")
            self.__bundles.mesh.bundle = bundle

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
        self.inputs = OgnDecalDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnDecalDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnDecalDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnDecal'

        @staticmethod
        def compute(context, node):
            def database_valid():
                if not db.inputs.mesh.valid:
                    db.log_warning('Required bundle inputs.mesh is invalid or not connected, compute skipped')
                    return False
                if not db.outputs.mesh.valid:
                    db.log_error('Required bundle outputs.mesh is invalid, compute skipped')
                    return False
                return True
            try:
                per_node_data = OgnDecalDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnDecalDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnDecalDatabase(node)

            try:
                compute_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnDecalDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnDecalDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnDecalDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnDecalDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnDecalDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnDecalDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Mesh decal node")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnDecalDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnDecalDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnDecalDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnDecalDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnDecal")
