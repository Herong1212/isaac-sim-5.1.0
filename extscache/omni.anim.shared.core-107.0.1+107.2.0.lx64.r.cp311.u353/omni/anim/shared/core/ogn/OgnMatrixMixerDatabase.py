"""Support for simplified access to data on nodes of type omni.anim.MatrixMixer

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Mix two matrices.
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnMatrixMixerDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.anim.MatrixMixer

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.alpha
            inputs.interpolate_rotation
            inputs.interpolate_scale
            inputs.interpolate_translation
            inputs.transform_a
            inputs.transform_b
        Outputs:
            outputs.transform
    """

    # Imprint the generator and target ABI versions in the file for JIT generation
    GENERATOR_VERSION = (1, 79, 1)
    TARGET_VERSION = (2, 184, 1)

    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}

    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:alpha', 'double', 0, None, 'Alpha blend value between transform_a and transform_b', {ogn.MetadataKeys.DEFAULT: '1.0'}, True, 1.0, False, ''),
        ('inputs:interpolate_rotation', 'bool', 0, None, 'Interpolate the rotation of transform_b', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:interpolate_scale', 'bool', 0, None, 'Interpolate the scale of transform_b', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:interpolate_translation', 'bool', 0, None, 'Interpolate the translation of transform_b', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:transform_a', 'matrix4d', 0, None, 'A transform matrix', {ogn.MetadataKeys.DEFAULT: '[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]'}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
        ('inputs:transform_b', 'matrix4d', 0, None, 'B transform matrix', {ogn.MetadataKeys.DEFAULT: '[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]'}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
        ('outputs:transform', 'matrix4d', 0, None, 'Output transform matrix', {ogn.MetadataKeys.DEFAULT: '[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]'}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.transform_a = og.AttributeRole.MATRIX
        role_data.inputs.transform_b = og.AttributeRole.MATRIX
        role_data.outputs.transform = og.AttributeRole.MATRIX
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"alpha", "interpolate_rotation", "interpolate_scale", "interpolate_translation", "transform_a", "transform_b", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.alpha, self._attributes.interpolate_rotation, self._attributes.interpolate_scale, self._attributes.interpolate_translation, self._attributes.transform_a, self._attributes.transform_b]
            self._batchedReadValues = [1.0, True, True, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]]

        @property
        def alpha(self):
            return self._batchedReadValues[0]

        @alpha.setter
        def alpha(self, value):
            self._batchedReadValues[0] = value

        @property
        def interpolate_rotation(self):
            return self._batchedReadValues[1]

        @interpolate_rotation.setter
        def interpolate_rotation(self, value):
            self._batchedReadValues[1] = value

        @property
        def interpolate_scale(self):
            return self._batchedReadValues[2]

        @interpolate_scale.setter
        def interpolate_scale(self, value):
            self._batchedReadValues[2] = value

        @property
        def interpolate_translation(self):
            return self._batchedReadValues[3]

        @interpolate_translation.setter
        def interpolate_translation(self, value):
            self._batchedReadValues[3] = value

        @property
        def transform_a(self):
            return self._batchedReadValues[4]

        @transform_a.setter
        def transform_a(self, value):
            self._batchedReadValues[4] = value

        @property
        def transform_b(self):
            return self._batchedReadValues[5]

        @transform_b.setter
        def transform_b(self, value):
            self._batchedReadValues[5] = value

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
        LOCAL_PROPERTY_NAMES = {"transform", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def transform(self):
            value = self._batchedWriteValues.get(self._attributes.transform)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.transform)
                return data_view.get()

        @transform.setter
        def transform(self, value):
            self._batchedWriteValues[self._attributes.transform] = value

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
        self.inputs = OgnMatrixMixerDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnMatrixMixerDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnMatrixMixerDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.anim.MatrixMixer'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnMatrixMixerDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnMatrixMixerDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnMatrixMixerDatabase(node)

            try:
                compute_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnMatrixMixerDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnMatrixMixerDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnMatrixMixerDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnMatrixMixerDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnMatrixMixerDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnMatrixMixerDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.anim.shared.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Matrix Mixer")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Mix two matrices.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnMatrixMixerDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnMatrixMixerDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnMatrixMixerDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnMatrixMixerDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.anim.MatrixMixer")
