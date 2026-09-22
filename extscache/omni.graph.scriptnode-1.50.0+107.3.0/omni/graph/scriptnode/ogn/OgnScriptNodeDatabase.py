r"""Support for simplified access to data on nodes of type omni.graph.scriptnode.ScriptNode

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This script node allows you to execute arbitrary Python code inside an OmniGraph.
The compute function is defined by you
at runtime and can be unique in every instance of a script node
that you create. Inside that function you can access the
database for the node, which is used for
getting and setting all attribute values that you define.

"""

import carb
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnScriptNodeDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.graph.scriptnode.ScriptNode

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.execIn
            inputs.script
            inputs.scriptPath
            inputs.usePath
        Outputs:
            outputs.execOut
        State:
            state.omni_initialized
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
        ('inputs:execIn', 'execution', 0, None, 'Signal to the graph that this node is ready to be executed.', {}, True, None, False, ''),
        ('inputs:script', 'string', 0, 'Inline Script', 'A string containing a Python script that may define code to be executed when the script node computes.\nSee the default and example scripts for more information.', {}, False, None, False, ''),
        ('inputs:scriptPath', 'token', 0, 'Script File Path', 'The path of a file containing a Python script that may define code to be executed when the script node computes.\nSee the default and example scripts for more info.', {ogn.MetadataKeys.UI_TYPE: 'filePath', 'fileExts': 'Python Scripts (*.py)'}, False, None, False, ''),
        ('inputs:usePath', 'bool', 0, 'Use Script File', "When true, the python script is read from the file specified in 'Script File Path' (*inputs:scriptPath*),\ninstead of the string in 'Inline Script' (*inputs:script*).", {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('outputs:execOut', 'execution', 0, None, 'Signal to the graph that execution can continue downstream.', {}, True, None, False, ''),
        ('state:omni_initialized', 'bool', 0, None, 'State attribute used to control when the script should be reloaded.\nThis should be set to false to trigger a reload of the script.', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.inputs.script = og.AttributeRole.TEXT
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"execIn", "script", "scriptPath", "usePath", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.execIn, self._attributes.script, self._attributes.scriptPath, self._attributes.usePath]
            self._batchedReadValues = [None, None, None, False]

        @property
        def execIn(self):
            return self._batchedReadValues[0]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[0] = value

        @property
        def script(self):
            return self._batchedReadValues[1]

        @script.setter
        def script(self, value):
            self._batchedReadValues[1] = value

        @property
        def scriptPath(self):
            return self._batchedReadValues[2]

        @scriptPath.setter
        def scriptPath(self, value):
            self._batchedReadValues[2] = value

        @property
        def usePath(self):
            return self._batchedReadValues[3]

        @usePath.setter
        def usePath(self, value):
            self._batchedReadValues[3] = value

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

        @property
        def omni_initialized(self):
            data_view = og.AttributeValueHelper(self._attributes.omni_initialized)
            return data_view.get()

        @omni_initialized.setter
        def omni_initialized(self, value):
            data_view = og.AttributeValueHelper(self._attributes.omni_initialized)
            data_view.set(value)

    def __init__(self, node):
        super().__init__(node)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
        self.inputs = OgnScriptNodeDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnScriptNodeDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnScriptNodeDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.graph.scriptnode.ScriptNode'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnScriptNodeDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnScriptNodeDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnScriptNodeDatabase(node)

            try:
                compute_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnScriptNodeDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnScriptNodeDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnScriptNodeDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnScriptNodeDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnScriptNodeDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnScriptNodeDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph.scriptnode")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Script Node")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "script")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This script node allows you to execute arbitrary Python code inside an OmniGraph.\nThe compute function is defined by you at runtime and can be unique in every instance of a script node\nthat you create. Inside that function you can access the database for the node, which is used for\ngetting and setting all attribute values that you define.\n")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                icon_path = carb.tokens.get_tokens_interface().resolve("${omni.graph.scriptnode}")
                icon_path = icon_path + '/' + "ogn/icons/omni.graph.scriptnode.ScriptNode.svg"
                node_type.set_metadata(ogn.MetadataKeys.ICON_PATH, icon_path)
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.set_data_access(og.eAccessLocation.E_USD, og.eAccessType.E_WRITE)
                OgnScriptNodeDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnScriptNodeDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnScriptNodeDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnScriptNodeDatabase.abi, 2)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.graph.scriptnode.ScriptNode")
