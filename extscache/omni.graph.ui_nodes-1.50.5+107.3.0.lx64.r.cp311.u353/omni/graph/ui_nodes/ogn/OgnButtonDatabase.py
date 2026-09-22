r"""Support for simplified access to data on nodes of type omni.graph.ui_nodes.Button

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Create a button widget on the Viewport
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnButtonDatabase(og.Database):  # pragma: no cover
    """Helper class providing simplified access to data on nodes of type omni.graph.ui_nodes.Button

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.create
            inputs.parentWidgetPath
            inputs.size
            inputs.startHidden
            inputs.style
            inputs.text
            inputs.widgetIdentifier
        Outputs:
            outputs.created
            outputs.widgetPath
    """

    # Imprint the generator and target ABI versions in the file for JIT generation
    GENERATOR_VERSION = (1, 79, 2)
    TARGET_VERSION = (2, 184, 2)

    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}

    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:create', 'execution', 0, 'Create', 'Input execution to create and show the widget', {}, True, None, False, ''),
        ('inputs:parentWidgetPath', 'token', 0, 'Parent Widget Path', 'The absolute path to the parent widget.', {}, True, "", False, ''),
        ('inputs:size', 'double2', 0, 'Size', 'The width and height of the created widget.\nValue of 0 means the created widget will be just large enough to fit everything.', {}, True, [0.0, 0.0], False, ''),
        ('inputs:startHidden', 'bool', 0, 'Start Hidden', 'Determines whether the button will initially be visible (False) or not (True).', {ogn.MetadataKeys.DEFAULT: 'false'}, False, False, False, ''),
        ('inputs:style', 'string', 0, None, 'Style to be applied to the button. This can later be changed with the WriteWidgetStyle node.', {}, False, None, False, ''),
        ('inputs:text', 'string', 0, 'Text', 'The text that is displayed on the button', {}, False, None, False, ''),
        ('inputs:widgetIdentifier', 'token', 0, 'Widget Identifier', 'An optional unique identifier for the widget.\nCan be used to refer to this widget in other places such as the OnWidgetClicked node.', {}, False, None, False, ''),
        ('outputs:created', 'execution', 0, 'Created', 'Executed when the widget is created', {}, True, None, False, ''),
        ('outputs:widgetPath', 'token', 0, 'Widget Path', 'The absolute path to the created widget', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.create = og.AttributeRole.EXECUTION
        role_data.inputs.style = og.AttributeRole.TEXT
        role_data.inputs.text = og.AttributeRole.TEXT
        role_data.outputs.created = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"create", "parentWidgetPath", "size", "startHidden", "style", "text", "widgetIdentifier", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.create, self._attributes.parentWidgetPath, self._attributes.size, self._attributes.startHidden, self._attributes.style, self._attributes.text, self._attributes.widgetIdentifier]
            self._batchedReadValues = [None, "", [0.0, 0.0], False, None, None, None]

        @property
        def create(self):
            return self._batchedReadValues[0]

        @create.setter
        def create(self, value):
            self._batchedReadValues[0] = value

        @property
        def parentWidgetPath(self):
            return self._batchedReadValues[1]

        @parentWidgetPath.setter
        def parentWidgetPath(self, value):
            self._batchedReadValues[1] = value

        @property
        def size(self):
            return self._batchedReadValues[2]

        @size.setter
        def size(self, value):
            self._batchedReadValues[2] = value

        @property
        def startHidden(self):
            return self._batchedReadValues[3]

        @startHidden.setter
        def startHidden(self, value):
            self._batchedReadValues[3] = value

        @property
        def style(self):
            return self._batchedReadValues[4]

        @style.setter
        def style(self, value):
            self._batchedReadValues[4] = value

        @property
        def text(self):
            return self._batchedReadValues[5]

        @text.setter
        def text(self, value):
            self._batchedReadValues[5] = value

        @property
        def widgetIdentifier(self):
            return self._batchedReadValues[6]

        @widgetIdentifier.setter
        def widgetIdentifier(self, value):
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
        LOCAL_PROPERTY_NAMES = {"created", "widgetPath", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def created(self):
            value = self._batchedWriteValues.get(self._attributes.created)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.created)
                return data_view.get()

        @created.setter
        def created(self, value):
            self._batchedWriteValues[self._attributes.created] = value

        @property
        def widgetPath(self):
            value = self._batchedWriteValues.get(self._attributes.widgetPath)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.widgetPath)
                return data_view.get()

        @widgetPath.setter
        def widgetPath(self, value):
            self._batchedWriteValues[self._attributes.widgetPath] = value

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
        self.inputs = OgnButtonDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnButtonDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnButtonDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.graph.ui_nodes.Button'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnButtonDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnButtonDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnButtonDatabase(node)

            try:
                compute_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnButtonDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnButtonDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnButtonDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnButtonDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnButtonDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnButtonDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph.ui_nodes")
                node_type.set_metadata(ogn.MetadataKeys.HIDDEN, "True")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Button (BETA)")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "internal:test")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Create a button widget on the Viewport")
                node_type.set_metadata(ogn.MetadataKeys.EXCLUSIONS, "tests")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnButtonDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnButtonDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnButtonDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnButtonDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.graph.ui_nodes.Button")
