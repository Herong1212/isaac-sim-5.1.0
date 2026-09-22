"""Support for simplified access to data on nodes of type omni.graph.visualization.nodes.DrawScreenSpaceText

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Draw text at a prescribed position in the viewport
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnDrawScreenSpaceTextDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.graph.visualization.nodes.DrawScreenSpaceText

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.backgroundColor
            inputs.boxWidth
            inputs.execIn
            inputs.position
            inputs.size
            inputs.text
            inputs.textColor
        Outputs:
            outputs.execOut
    """

    # Imprint the generator and target ABI versions in the file for JIT generation
    GENERATOR_VERSION = (1, 79, 1)
    TARGET_VERSION = (2, 184, 0)

    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}

    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:backgroundColor', 'color4f', 0, 'Background Color', 'Background color', {ogn.MetadataKeys.DEFAULT: '[0.165, 0.157, 0.145, 0.8]'}, True, [0.165, 0.157, 0.145, 0.8], False, ''),
        ('inputs:boxWidth', 'int', 0, 'Text Max Width', 'Text box maximum width before wrapping (0 for no wrapping)', {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:execIn', 'execution', 0, 'In', 'Execution input', {}, True, None, False, ''),
        ('inputs:position', 'double2', 0, 'Screen Position (%)', 'Text position on the viewport (as a percentage of the viewport size)', {ogn.MetadataKeys.DEFAULT: '[50.0, 50.0]'}, True, [50.0, 50.0], False, ''),
        ('inputs:size', 'float', 0, 'Size', 'Text size', {ogn.MetadataKeys.DEFAULT: '14.0'}, True, 14.0, False, ''),
        ('inputs:text', 'string', 0, 'Text', 'Label text', {ogn.MetadataKeys.DEFAULT: '""'}, True, "", False, ''),
        ('inputs:textColor', 'color4f', 0, 'Text Color', 'Text color', {ogn.MetadataKeys.DEFAULT: '[0.95, 0.95, 0.95, 1.0]'}, True, [0.95, 0.95, 0.95, 1.0], False, ''),
        ('outputs:execOut', 'execution', 0, 'Out', 'Execution output', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.backgroundColor = og.AttributeRole.COLOR
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.inputs.text = og.AttributeRole.TEXT
        role_data.inputs.textColor = og.AttributeRole.COLOR
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"backgroundColor", "boxWidth", "execIn", "position", "size", "text", "textColor", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.backgroundColor, self._attributes.boxWidth, self._attributes.execIn, self._attributes.position, self._attributes.size, self._attributes.text, self._attributes.textColor]
            self._batchedReadValues = [[0.165, 0.157, 0.145, 0.8], 0, None, [50.0, 50.0], 14.0, "", [0.95, 0.95, 0.95, 1.0]]

        @property
        def backgroundColor(self):
            return self._batchedReadValues[0]

        @backgroundColor.setter
        def backgroundColor(self, value):
            self._batchedReadValues[0] = value

        @property
        def boxWidth(self):
            return self._batchedReadValues[1]

        @boxWidth.setter
        def boxWidth(self, value):
            self._batchedReadValues[1] = value

        @property
        def execIn(self):
            return self._batchedReadValues[2]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[2] = value

        @property
        def position(self):
            return self._batchedReadValues[3]

        @position.setter
        def position(self, value):
            self._batchedReadValues[3] = value

        @property
        def size(self):
            return self._batchedReadValues[4]

        @size.setter
        def size(self, value):
            self._batchedReadValues[4] = value

        @property
        def text(self):
            return self._batchedReadValues[5]

        @text.setter
        def text(self, value):
            self._batchedReadValues[5] = value

        @property
        def textColor(self):
            return self._batchedReadValues[6]

        @textColor.setter
        def textColor(self, value):
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
        self.inputs = OgnDrawScreenSpaceTextDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnDrawScreenSpaceTextDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnDrawScreenSpaceTextDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.graph.visualization.nodes.DrawScreenSpaceText'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnDrawScreenSpaceTextDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnDrawScreenSpaceTextDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnDrawScreenSpaceTextDatabase(node)

            try:
                compute_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnDrawScreenSpaceTextDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnDrawScreenSpaceTextDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnDrawScreenSpaceTextDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnDrawScreenSpaceTextDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnDrawScreenSpaceTextDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph.visualization.nodes")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Draw Screen Space Text (Beta)")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "debug")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Draw text at a prescribed position in the viewport")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnDrawScreenSpaceTextDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnDrawScreenSpaceTextDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnDrawScreenSpaceTextDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.graph.visualization.nodes.DrawScreenSpaceText")
